#!/usr/bin/env python3
"""One-time build of the Claude Opus 5.5 disease-name -> Mondo table.

Not a harness stage; the scored runs never call it. Three subcommands:

  names     (rescore image, --network none) distinct cleaned answer lines of o1-preview, produced by
            malco's own split_diagnosis_from_header + ground_diagnosis_text_to_mondo line loop
            (clean_diagnosis_line, headers_to_avoid), sorted by Python str order, deduplicated exactly.
  query     (host, the user's Claude Code OAuth login; no API key) one `claude -p` call per chunk of 50
            names, fixed argv, names on stdin. Keeps every chunk's stdin and every attempt's raw JSON
            under the work directory and lists their sha256 in grounding/chunks.sha256.
  validate  (rescore image, --network none, pinned Mondo) checks chunks.sha256, applies the validity
            rule and the OAK agreement check, writes opus-mondo-map.tsv and opus-mondo-map.meta.json.

The script itself uses the standard library only; `names` and `validate` import malco/oaklib from the
rescore image. Every subprocess is an argv list with no shell.
"""
import argparse, hashlib, json, os, re, subprocess, sys, zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

MODEL = "claude-opus-5-5"
EFFORT = "medium"
CHUNK = 50
MAX_ATTEMPTS = 3
GATE = 0.90
RESPONSES_MEMBER = "all_models_responses/gpt-01-preview.jsonl"
HERE = os.path.dirname(os.path.abspath(__file__))


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_names(path):
    with open(path, encoding="utf-8", newline="\n") as f:
        return f.read().split("\n")[:-1]


def chunk_names(names, k):
    return names[CHUNK * k: CHUNK * k + CHUNK]


def n_chunks(names):
    return (len(names) + CHUNK - 1) // CHUNK


# ---------------------------------------------------------------- names (container)
def cmd_names(a):
    from malco.process.cleaning import split_diagnosis_from_header
    from malco.process.grounding import ground_diagnosis_text_to_mondo

    class NoMatch:  # an annotator that never matches: malco's loop then yields every kept clean line
        def annotate_text(self, text, configuration=None):
            return iter(())

    with zipfile.ZipFile(a.responses_zip) as z:
        lines = z.read(RESPONSES_MEMBER).decode("utf-8").splitlines()
    names, n_lines = set(), 0
    for raw in lines:
        if not raw.strip():
            continue
        r = json.loads(raw)
        text = split_diagnosis_from_header(r["response"])
        for clean_line, _ in ground_diagnosis_text_to_mondo(NoMatch(), text, verbose=False,
                                                              use_ontogpt_grounding=False):
            names.add(clean_line)
            n_lines += 1
    for n in names:
        if "\n" in n or "\r" in n:
            sys.exit(f"[names] a cleaned line contains a line break: {n!r}")
    out = sorted(names)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(n + "\n" for n in out))
    print(f"[names] {n_lines} answer lines, {len(out)} distinct -> {a.out} (sha256 {sha256_file(a.out)})")


# ---------------------------------------------------------------- query (host)
def schema_check(obj, names):
    """Structure of grounding/schema.json, checked here too (the CLI's --json-schema is the first check),
    plus the echo rule: exactly the chunk's names, in order."""
    if not isinstance(obj, dict) or set(obj) != {"rows"} or not isinstance(obj["rows"], list):
        return "top level is not {rows: [...]}"
    for i, r in enumerate(obj["rows"]):
        if not isinstance(r, dict) or set(r) != {"name", "mondo_id", "mondo_label"}:
            return f"row {i}: keys are not name, mondo_id, mondo_label"
        if not all(isinstance(r[k], str) for k in r):
            return f"row {i}: a value is not a string"
        if not re.fullmatch(r"MONDO:[0-9]{7}|no match", r["mondo_id"]):
            return f"row {i}: mondo_id {r['mondo_id']!r} does not match the pattern"
    echoed = [r["name"] for r in obj["rows"]]
    if echoed != names:
        return f"echoed names differ from the chunk's names ({len(echoed)} rows for {len(names)} names)"
    return None


def structured(cli_out):
    """The structured object from the CLI's JSON output: `structured_output` if present, else the
    `result` string parsed as JSON. Returns (obj, where) or (None, reason)."""
    try:
        j = json.loads(cli_out)
    except ValueError as e:
        return None, f"CLI output is not JSON ({e})"
    if not isinstance(j, dict):
        return None, "CLI output is not a JSON object"
    if j.get("is_error"):
        return None, f"CLI reported an error: {str(j.get('result'))[:200]}"
    if isinstance(j.get("structured_output"), dict):
        return j["structured_output"], "structured_output"
    try:
        obj = json.loads(j.get("result", ""))
        return obj, "result"
    except (TypeError, ValueError):
        return None, "no structured_output and result is not JSON"


def models_and_usage(cli_out):
    try:
        j = json.loads(cli_out)
    except ValueError:
        return [], None
    models = sorted((j.get("modelUsage") or {}).keys()) if isinstance(j, dict) else []
    u = j.get("usage") if isinstance(j, dict) else None
    usage = None
    if isinstance(u, dict) and "input_tokens" in u and "output_tokens" in u:
        usage = {k: u[k] for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                                    "cache_read_input_tokens") if isinstance(u.get(k), int)}
    return models, usage


def argv_for(prompt, schema):
    return ["claude", "-p", "--model", MODEL, "--effort", EFFORT, "--output-format", "json",
            "--json-schema", schema, "--system-prompt", prompt,
            "--tools", "", "--safe-mode", "--no-session-persistence"]


def run_chunk(k, names, work, prompt, schema, timeout):
    stem = os.path.join(work, f"chunk-{k:03d}")
    mine = chunk_names(names, k)
    stdin = "".join(n + "\n" for n in mine)
    with open(stem + ".in.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write(stdin)
    rec = {"chunk": k, "n_names": len(mine), "attempts": [], "accepted": None}
    for m in range(1, MAX_ATTEMPTS + 1):
        out_path = f"{stem}.try-{m}.out.json"
        att = {"attempt": m, "file": os.path.basename(out_path)}
        if os.path.exists(out_path):  # an attempt kept from an interrupted query run is evaluated, not repeated
            att["reused"] = True
        else:
            att["started_utc"] = now()
            try:
                r = subprocess.run(argv_for(prompt, schema), input=stdin.encode("utf-8"), cwd=work,
                                   capture_output=True, timeout=timeout)
                out, att["returncode"] = r.stdout, r.returncode
                if r.stderr:
                    with open(f"{stem}.try-{m}.stderr.txt", "wb") as f:
                        f.write(r.stderr)
            except subprocess.TimeoutExpired as e:
                out, att["returncode"] = (e.stdout or b""), "timeout"
            with open(out_path, "wb") as f:
                f.write(out)
            att["ended_utc"] = now()
        cli_out = open(out_path, encoding="utf-8", errors="replace").read()
        att["models"], att["usage"] = models_and_usage(cli_out)
        obj, where = structured(cli_out)
        problem = where if obj is None else schema_check(obj, mine)
        att["structured_from"] = where if obj is not None else None
        att["problem"] = problem
        rec["attempts"].append(att)
        print(f"[query] chunk {k:03d} attempt {m}: {'accepted' if problem is None else 'rejected: ' + problem}",
              flush=True)
        if problem is None:
            rec["accepted"] = m
            break
    return rec


def write_chunks_sha256(work, log, dest):
    lines = []
    for rec in sorted(log["chunks"].values(), key=lambda r: r["chunk"]):
        stem = f"chunk-{rec['chunk']:03d}"
        lines.append(f"{sha256_file(os.path.join(work, stem + '.in.txt'))}  {stem}.in.txt  input")
        for att in rec["attempts"]:
            role = "accepted" if rec["accepted"] == att["attempt"] else "rejected"
            lines.append(f"{sha256_file(os.path.join(work, att['file']))}  {att['file']}  {role}")
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(l + "\n" for l in lines))


def cmd_query(a):
    if "ANTHROPIC_API_KEY" in os.environ:
        sys.exit("[query] ANTHROPIC_API_KEY is set in this environment; Claude Code would prefer it over the "
                 "OAuth login. Unset it and rerun. This step never uses an API key.")
    names = read_names(a.names)
    work = os.path.abspath(a.workdir)
    os.makedirs(work, exist_ok=True)
    if os.path.exists(os.path.join(work, "CLAUDE.md")):
        sys.exit("[query] the working directory holds a CLAUDE.md; it must not")
    prompt = open(os.path.join(HERE, "prompt.md"), encoding="utf-8").read()
    schema = open(os.path.join(HERE, "schema.json"), encoding="utf-8").read()
    json.loads(schema)
    log_path = os.path.join(work, "query-log.json")
    log = json.load(open(log_path, encoding="utf-8")) if os.path.exists(log_path) else {
        "chunks": {}, "claude_code_version": [], "date_utc": {"start": now(), "end": None}}
    ver = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    if ver not in log["claude_code_version"]:
        log["claude_code_version"].append(ver)
    total = n_chunks(names)
    todo = [k for k in (a.chunks if a.chunks is not None else range(total))
            if not (str(k) in log["chunks"] and log["chunks"][str(k)]["accepted"])]
    print(f"[query] {len(names)} names, {total} chunks of {CHUNK}; running {len(todo)}; {ver}", flush=True)
    failed = []
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for rec in ex.map(lambda k: run_chunk(k, names, work, prompt, schema, a.timeout), todo):
            log["chunks"][str(rec["chunk"])] = rec
            if not rec["accepted"]:
                failed.append(rec["chunk"])
            json.dump(log, open(log_path, "w", encoding="utf-8", newline="\n"), indent=1)
    log["date_utc"]["end"] = now()
    json.dump(log, open(log_path, "w", encoding="utf-8", newline="\n"), indent=1)
    write_chunks_sha256(work, log, os.path.join(HERE, "chunks.sha256"))
    wrong = sorted({m for r in log["chunks"].values() for t in r["attempts"] for m in t["models"]} - {MODEL})
    if wrong:
        sys.exit(f"[query] the CLI reported model(s) {wrong}, not {MODEL}; stopping")
    if failed:
        sys.exit(f"[query] chunk(s) {failed} failed all {MAX_ATTEMPTS} attempts; stopping")
    print(f"[query] done; grounding/chunks.sha256 written", flush=True)


# ---------------------------------------------------------------- validate (container)
def cmd_validate(a):
    from oaklib import get_adapter
    from malco.process.grounding import perform_oak_grounding

    names = read_names(a.names)
    work = a.workdir
    log = json.load(open(os.path.join(work, "query-log.json"), encoding="utf-8"))
    total = n_chunks(names)
    if sorted(int(k) for k in log["chunks"]) != list(range(total)):
        sys.exit(f"[validate] query-log.json does not cover chunks 0..{total - 1}")
    listed = {}
    for line in open(os.path.join(HERE, "chunks.sha256"), encoding="utf-8"):
        h, fname, role = line.split()
        listed[fname] = (h, role)
    for fname, (h, _) in listed.items():
        p = os.path.join(work, fname)
        if not os.path.exists(p) or sha256_file(p) != h:
            sys.exit(f"[validate] hash check failed for {fname}; refusing to build the table")
    print(f"[validate] chunks.sha256: {len(listed)} files, all hashes match")

    rows = []
    for k in range(total):
        rec = log["chunks"][str(k)]
        stem = f"chunk-{k:03d}"
        if open(os.path.join(work, stem + ".in.txt"), encoding="utf-8", newline="\n").read() != \
                "".join(n + "\n" for n in chunk_names(names, k)):
            sys.exit(f"[validate] {stem}.in.txt is not chunk {k} of names.txt")
        acc = f"{stem}.try-{rec['accepted']}.out.json"
        if listed.get(acc, (None, None))[1] != "accepted":
            sys.exit(f"[validate] {acc} is not listed as accepted in chunks.sha256")
        obj, _ = structured(open(os.path.join(work, acc), encoding="utf-8").read())
        problem = None if obj is None else schema_check(obj, chunk_names(names, k))
        if obj is None or problem:
            sys.exit(f"[validate] accepted output {acc} does not pass the acceptance rule: {problem}")
        rows.extend(obj["rows"])

    mondo = get_adapter("sqlite:obo:mondo")
    table, n_valid, n_oak, n_agree = [], 0, 0, 0
    for r in rows:
        mid, mlabel = r["mondo_id"], r["mondo_label"]
        valid = False
        if mid != "no match":
            label = mondo.label(mid)
            meta = mondo.entity_metadata_map(mid) if label is not None else {}
            deprecated = any(str(v).lower() == "true" for v in meta.get("owl:deprecated", []))
            aliases = {s.strip().casefold() for s in list(mondo.entity_aliases(mid) or []) + [label or ""] if s}
            valid = label is not None and not deprecated and mlabel.strip().casefold() in aliases
        eff = mid if valid else "no match"
        oak = perform_oak_grounding(mondo, r["name"], exact_match=True, verbose=False, include_list=["MONDO:"])
        oak_ids = sorted({i for i, _ in oak if i != "N/A"})
        agrees = bool(oak_ids) and eff in oak_ids
        n_valid += valid
        n_oak += bool(oak_ids)
        n_agree += agrees
        table.append([r["name"], mid, mlabel, str(valid).lower(), eff, ";".join(oak_ids),
                      str(bool(oak_ids)).lower(), str(agrees).lower() if oak_ids else ""])
    rate = n_agree / n_oak if n_oak else None
    with open(a.out_tsv, "w", encoding="utf-8", newline="\n") as f:
        f.write("name\topus_mondo_id\topus_mondo_label\tvalid\teffective_mondo_id\toak_ids\toak_resolved\tagrees\n")
        for t in table:
            if any("\t" in c or "\n" in c for c in t):
                sys.exit(f"[validate] a field contains a tab or line break: {t!r}")
            f.write("\t".join(t) + "\n")

    atts = [t for r in log["chunks"].values() for t in r["attempts"]]
    models = sorted({m for t in atts for m in t["models"]})
    usages = [t["usage"] for t in atts]
    usage = ({"input_tokens": sum(u["input_tokens"] for u in usages),
              "output_tokens": sum(u["output_tokens"] for u in usages),
              "counted_over": "accepted and rejected attempts"}
             if usages and all(u for u in usages) else
             {"value": None, "reason": "the CLI's JSON output did not report usage for every attempt"})
    import sqlite3
    ver_iri = [row[0] for row in sqlite3.connect(mondo.engine.url.database).execute(
        "SELECT object FROM statements WHERE predicate = 'owl:versionIRI'")]
    meta = {
        "model_requested": MODEL,
        "model_reported": {"per_chunk": {k: sorted({m for t in log["chunks"][k]["attempts"] for m in t["models"]})
                                         for k in sorted(log["chunks"], key=int)},
                           "distinct": models} if models else
                          {"value": None, "reason": "the CLI's JSON output reported no model id"},
        "claude_code_version": log["claude_code_version"],
        "auth": "Claude Code OAuth login (no API key)",
        "argv": argv_for("<grounding/prompt.md>", "<grounding/schema.json>") + ["(stdin: chunk names, one per line)"],
        "prompt_sha256": sha256_file(os.path.join(HERE, "prompt.md")),
        "schema_sha256": sha256_file(os.path.join(HERE, "schema.json")),
        "names_sha256": sha256_file(a.names),
        "effort": EFFORT,
        "temperature": "not settable on this model",
        "chunk_size": CHUNK,
        "n_chunks": total,
        "n_attempts_total": len(atts),
        "n_retried_chunks": sum(1 for r in log["chunks"].values() if len(r["attempts"]) > 1),
        "date_utc": log["date_utc"],
        "usage": usage,
        "mondo_version": ver_iri,
        "n_names": len(names),
        "n_valid": n_valid,
        "n_invalid": len(names) - n_valid,
        "n_oak_resolved": n_oak,
        "n_agree": n_agree,
        "agreement_rate": rate,
        "gate": GATE,
        "gate_passed": rate is not None and rate >= GATE,
    }
    if models and models != [MODEL]:
        sys.exit(f"[validate] model_reported {models} differs from {MODEL}; stopping")
    json.dump(meta, open(a.out_meta, "w", encoding="utf-8", newline="\n"), indent=2)
    print(f"[validate] {len(names)} names, {n_valid} valid, {n_oak} OAK-resolved, {n_agree} agree; "
          f"agreement_rate {rate} (gate {GATE}): {'PASSED' if meta['gate_passed'] else 'FAILED'}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("names")
    p.add_argument("--responses-zip", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("query")
    p.add_argument("--names", required=True)
    p.add_argument("--workdir", required=True)
    p.add_argument("--chunks", type=int, nargs="*", help="chunk indices to run (default: all)")
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--timeout", type=int, default=1200)
    p = sub.add_parser("validate")
    p.add_argument("--names", required=True)
    p.add_argument("--workdir", required=True)
    p.add_argument("--out-tsv", required=True)
    p.add_argument("--out-meta", required=True)
    a = ap.parse_args()
    {"names": cmd_names, "query": cmd_query, "validate": cmd_validate}[a.cmd](a)


if __name__ == "__main__":
    main()
