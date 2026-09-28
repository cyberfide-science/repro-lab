#!/usr/bin/env python3
"""Run Exomiser 14.0.1 phenotype-only on every case and score it with malco (pheval.llm@bd7146d).

Lives in repro-lab, not in any clone; edits nothing in the Exomiser or pheval.llm clones.

  cases    copy each case's phenopacket byte-for-byte from the hash-verified tarball to
           /work/cases/case-<row>.json (file names use the cases.tsv row, never the phenopacket id),
           checking each copy's sha256 against the tarball member.
  analyse  run the cases in batches of 25 rows (row order), one `--batch` file and one JVM per batch,
           JVMS batches at a time, writing to container-local /work/raw. After a batch, each
           case-<row>.json is hashed into raw_json.sha256,
           reduced to its disease items (items/case-<row>.tsv.gz: gene_index, gene_symbol, disease_id,
           score, in JSON order) and deleted, except rows 0001-0020, moved whole to the mounted raw/ as
           an audit sample.
  score    build each case's differential from its item list and score it; also ground o1-preview under
           the substituted condition for EX4. Writes /work/out/results.csv and per_case.tsv.

Field selection (step 2), the same fields pheval_exomiser 0.4.13's
post_process/post_process_results_format.py::extract_disease_results_from_json reads (pheval-exomiser is
not installed: it requires oaklib<0.6.0, malco's lock pins 0.6.21): for each gene entry in JSON order, each
element of priorityResults.HIPHIVE_PRIORITY.diseaseMatches in order: disease_id = element.model.diseaseId,
score = element.score with null read as 0.0 (fill_null(0.0)); a null disease id is dropped (drop_nulls());
a gene without HIPHIVE_PRIORITY contributes nothing.

Differential (steps 3-6): deduplicate by disease_id keeping the highest score; order by score descending,
then sha256(disease_id as UTF-8) ascending (the pre-registered tie rule); rank = 1-based position.
ORPHA:n items are mapped to the Mondo term whose skos:exactMatch is ORDO:n (the pinned Mondo writes
Orphanet's identifiers with the ORDO: prefix, expanded to http://www.orpha.net/ORDO/Orphanet_, the same
IRI as ORPHA:n); unmapped items stay in place and score 0 (passed to malco as "N/A"). Every item is
scored with malco's score(), i.e. score_grounded_result with a copy of the authors' caches;
is_correct = score > 0. A case with no item is "not found" and stays in the denominator.

Tie band (evidence): with s* the highest Exomiser score among correct items, optimistic rank = 1 + items
scoring above s*; pessimistic rank = items above s* + incorrect items scoring exactly s* + 1.
exomiser_max_tie_size is the largest number of items sharing one score in any case's differential.
"""
import csv, gzip, hashlib, io, json, os, shutil, subprocess, sys, tarfile, time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

CASES_TSV = "/work/cases.tsv"
DATA, OUT, EXO = "/work/data", "/work/out", "/work/exo"
AUDIT, ITEMS, RAW_SHA = f"{EXO}/raw", f"{EXO}/items", f"{EXO}/raw_json.sha256"
RAW = "/work/raw"  # container-local: Exomiser writes here; only audit rows are moved to the mounted AUDIT dir
CASE_DIR, BATCH_DIR = "/work/cases", "/work/batches"
CLI = "/work/exomiser-cli-14.0.1"
OPTIONS = "/work/output-options.yml"
BATCH_SIZE, JVMS, XMX, AUDIT_ROWS = 25, 4, "3g", 20
NA = [("N/A", "No grounding found")]


def read_cases():
    rows = list(csv.DictReader(open(CASES_TSV, encoding="utf-8", newline=""), delimiter="\t",
                               quoting=csv.QUOTE_NONE))
    if [r["row"] for r in rows] != [f"{i:04d}" for i in range(1, len(rows) + 1)]:
        sys.exit("[score_exomiser] cases.tsv rows are not 0001..N in order; stopping")
    return rows


# ---------------------------------------------------------------- cases
def cmd_cases():
    rows = read_cases()
    by_ppkt = {r["phenopacket_id"]: r["row"] for r in rows}
    os.makedirs(CASE_DIR, exist_ok=True)
    done = {}
    with tarfile.open(f"{DATA}/phenopackets.tar.gz", "r:gz") as t:
        for m in t:
            base = os.path.basename(m.name)
            if not m.isfile() or not base.endswith(".json") or base.startswith("._"):
                continue
            raw = t.extractfile(m).read()
            row = by_ppkt.get(json.loads(raw)["id"])
            if row is None:
                continue
            if row in done:
                sys.exit(f"[cases] two phenopackets resolve to row {row}; stopping")
            dest = f"{CASE_DIR}/case-{row}.json"
            with open(dest, "wb") as f:
                f.write(raw)
            if hashlib.sha256(open(dest, "rb").read()).hexdigest() != hashlib.sha256(raw).hexdigest():
                sys.exit(f"[cases] copy of row {row} does not match its tarball member; stopping")
            done[row] = m.name
    missing = [r["row"] for r in rows if r["row"] not in done]
    if missing:
        sys.exit(f"[cases] no phenopacket for rows {missing}; stopping")
    print(f"[cases] {len(done)} phenopackets copied to case-<row>.json, each sha256 equal to its tarball member")


# ---------------------------------------------------------------- analyse
def read_items(path):
    items = []
    for gi, g in enumerate(json.load(open(path, encoding="utf-8"))):
        hp = (g.get("priorityResults") or {}).get("HIPHIVE_PRIORITY")
        if not hp:
            continue
        for m in hp.get("diseaseMatches") or []:
            d = (m.get("model") or {}).get("diseaseId")
            if d is None:
                continue
            items.append((gi, g.get("geneSymbol") or "", d, 0.0 if m.get("score") is None else float(m["score"])))
    return items


def reduce_case(row, sha_out):
    src = f"{RAW}/case-{row}.json"
    if not os.path.exists(src):
        sys.exit(f"[analyse] no output for row {row}; stopping")
    h = hashlib.sha256()
    with open(src, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    items = read_items(src)
    buf = io.StringIO()
    buf.write("gene_index\tgene_symbol\tdisease_id\tscore\n")
    for gi, sym, d, s in items:
        buf.write(f"{gi}\t{sym}\t{d}\t{s!r}\n")
    with gzip.GzipFile(f"{ITEMS}/case-{row}.tsv.gz", "wb", mtime=0) as f:
        f.write(buf.getvalue().encode("utf-8"))
    sha_out.write(f"{h.hexdigest()}  case-{row}.json\n")
    if int(row) > AUDIT_ROWS:
        os.remove(src)
    else:
        shutil.move(src, f"{AUDIT}/case-{row}.json")


def batches_of(rows):
    return [rows[i:i + BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]


def cmd_reduce(k):
    """Reduce one finished batch; one process per batch, so JSON parsing runs in parallel across batches."""
    b = batches_of([r["row"] for r in read_cases()])[k]
    with open(f"{BATCH_DIR}/batch-{k:03d}.sha256", "w", encoding="utf-8", newline="\n") as sha_out:
        for row in b:
            reduce_case(row, sha_out)


def cmd_analyse():
    rows = [r["row"] for r in read_cases()]
    for d in (BATCH_DIR, RAW, AUDIT, ITEMS):
        os.makedirs(d, exist_ok=True)
    batches = batches_of(rows)
    for k, b in enumerate(batches):
        with open(f"{BATCH_DIR}/batch-{k:03d}.txt", "w", encoding="ascii", newline="\n") as f:
            for row in b:
                f.write(f"--sample {CASE_DIR}/case-{row}.json --preset phenotype-only --output {OPTIONS} "
                        f"--output-format JSON --output-directory {RAW} --output-filename case-{row}\n")
    t0 = time.time()
    print(f"[analyse] {len(rows)} cases in {len(batches)} batches of {BATCH_SIZE}; {JVMS} JVMs at a time, -Xmx{XMX}",
          flush=True)

    def run(k):
        b, tb = batches[k], time.time()
        log = f"{BATCH_DIR}/batch-{k:03d}.log"
        with open(log, "w") as lf:
            rc = subprocess.run(["java", f"-Xmx{XMX}", "-jar", f"{CLI}/exomiser-cli-14.0.1.jar",
                                 "--batch", f"{BATCH_DIR}/batch-{k:03d}.txt"], cwd=CLI, stdout=lf,
                                stderr=subprocess.STDOUT).returncode
        if rc != 0:
            print(open(log, encoding="utf-8", errors="replace").read()[-4000:], flush=True)
            raise SystemExit(f"[analyse] batch {k:03d} (rows {b[0]}-{b[-1]}) exited {rc}; stopping")
        if subprocess.run([sys.executable, __file__, "reduce", str(k)]).returncode != 0:
            raise SystemExit(f"[analyse] reducing batch {k:03d} failed; stopping")
        print(f"[analyse] batch {k + 1}/{len(batches)} rows {b[0]}-{b[-1]}: {time.time() - tb:.0f} s "
              f"(elapsed {(time.time() - t0) / 60:.1f} min)", flush=True)

    with ThreadPoolExecutor(max_workers=JVMS) as ex:
        list(ex.map(run, range(len(batches))))
    have = sorted(f for f in os.listdir(ITEMS))
    want = [f"case-{r}.tsv.gz" for r in rows]
    if have != want:
        sys.exit(f"[analyse] items/ does not hold exactly one list per row: extra {sorted(set(have) - set(want))[:5]}, "
                 f"missing {sorted(set(want) - set(have))[:5]}; stopping")
    kept = sorted(os.listdir(AUDIT))
    if kept != [f"case-{r}.json" for r in rows[:AUDIT_ROWS]] or os.listdir(RAW):
        sys.exit(f"[analyse] raw/ should hold rows 0001-{AUDIT_ROWS:04d} only, holds {kept[:5]}...; stopping")
    lines = sorted((line for k in range(len(batches))
                    for line in open(f"{BATCH_DIR}/batch-{k:03d}.sha256", encoding="utf-8").read().splitlines()),
                   key=lambda line: line.split()[1])
    if len(lines) != len(rows):
        sys.exit(f"[analyse] raw_json.sha256 has {len(lines)} lines for {len(rows)} rows; stopping")
    with open(RAW_SHA, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(l + "\n" for l in lines))
    print(f"[analyse] done in {(time.time() - t0) / 60:.1f} min: {len(have)} item lists, {len(kept)} audit JSON kept",
          flush=True)


# ---------------------------------------------------------------- score
_annotator = None


def _init_worker():
    global _annotator
    from oaklib import get_adapter
    _annotator = get_adapter("sqlite:obo:mondo")


def _ground(response):
    from malco.process.cleaning import split_diagnosis_from_header
    from malco.process.grounding import ground_diagnosis_text_to_mondo
    return ground_diagnosis_text_to_mondo(_annotator, split_diagnosis_from_header(response),
                                          verbose=False, use_ontogpt_grounding=False)


def tie_key(item):
    d, s = item
    return (-s, hashlib.sha256(d.encode("utf-8")).hexdigest())


def differential(row):
    best = {}
    with gzip.open(f"{ITEMS}/case-{row}.tsv.gz", "rt", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            s = float(r["score"])
            if r["disease_id"] not in best or s > best[r["disease_id"]]:
                best[r["disease_id"]] = s
    return sorted(best.items(), key=tie_key)


def first_correct(scored):
    for pos, item in enumerate(scored or [], start=1):
        if item["is_correct"]:
            return pos
    return None


def o1_subst(prompt_ids):
    """o1-preview's first-correct rank per prompt id under the substituted condition, as reese-2026-rescore
    computes it: OAK whole-line exact match, then the hash-verified Opus table for lines OAK cannot ground."""
    import pandas as pd
    from malco.process.scoring import score
    result = [json.loads(l) for l in open("/work/run/gpt-01-preview.jsonl", encoding="utf-8") if l.strip()]
    table = {r["name"]: r for r in csv.DictReader(open(f"{DATA}/opus-mondo-map.tsv", encoding="utf-8",
                                                          newline=""), delimiter="\t", quoting=csv.QUOTE_NONE)}
    with Pool(os.cpu_count(), initializer=_init_worker) as pool:
        floor = pool.map(_ground, [r["response"] for r in result], chunksize=8)
    subst, missing = [], set()
    for g in floor:
        s = []
        for line, grounded in g:
            if grounded == NA:
                t = table.get(line)
                if t is None:
                    missing.add(line)
                elif t["effective_mondo_id"] != "no match":
                    grounded = [(t["effective_mondo_id"], t["opus_mondo_label"])]
            s.append((line, grounded))
        subst.append(s)
    if missing:
        sys.exit(f"[score] {len(missing)} o1-preview line(s) missing from the Opus table; stopping")
    df = score(pd.DataFrame({"id": [r["id"] for r in result], "gold": [r["gold"] for r in result],
                             "grounding": subst}))
    ranks = dict(zip(df["id"], (first_correct(s) for s in df["scored"])))
    if set(ranks) != set(prompt_ids):
        sys.exit("[score] o1-preview ids differ from cases.tsv prompt ids; stopping")
    return ranks


def cmd_score():
    import sqlite3
    import pandas as pd
    from oaklib import get_adapter
    from malco.process.scoring import score

    cases = read_cases()
    denominator = sum(1 for _ in open(f"{DATA}/correct_results.tsv", encoding="utf-8"))
    db = get_adapter("sqlite:obo:mondo").engine.url.database
    ordo = {}
    for subj, obj in sqlite3.connect(db).execute(
            "SELECT subject, object FROM statements WHERE predicate = 'skos:exactMatch' "
            "AND subject LIKE 'MONDO:%' AND object LIKE 'ORDO:%'"):
        ordo.setdefault(obj, set()).add(subj)
    if any(len(v) > 1 for v in ordo.values()):
        sys.exit("[score] an ORDO id has more than one Mondo exactMatch; the mapping rule does not cover it")

    diffs, groundings, unmapped = [], [], 0
    for c in cases:
        d = differential(c["row"])
        diffs.append(d)
        g = []
        for did, _ in d:
            if did.startswith(("ORPHA:", "Orphanet:")):
                m = ordo.get("ORDO:" + did.split(":", 1)[1])
                if m is None:
                    unmapped += 1
                    g.append((did, NA))
                else:
                    g.append((did, [(next(iter(m)), "")]))
            else:
                g.append((did, [(did, "")]))
        groundings.append(g)
    print(f"[score] {len(cases)} differentials, {sum(len(d) for d in diffs)} items; scoring with malco", flush=True)
    df = score(pd.DataFrame({"id": [c["prompt_id"] for c in cases],
                             "gold": [{"disease_id": c["gold_id"]} for c in cases],
                             "grounding": groundings}))

    per_case, pos, opt, pess, in_tie, max_tie, no_result = [], [], [], [], 0, 0, 0
    for c, d, scored in zip(cases, diffs, df["scored"]):
        correct = [it["is_correct"] for it in (scored or [])]
        if len(correct) != len(d):
            sys.exit(f"[score] row {c['row']}: {len(correct)} scored items for {len(d)} differential items")
        no_result += not d
        counts = {}
        for _, s in d:
            counts[s] = counts.get(s, 0) + 1
        max_tie = max([max_tie] + list(counts.values()))
        p = first_correct(scored)
        if p is None:
            o = q = None
        else:
            s_star = max(s for (_, s), ok in zip(d, correct) if ok)
            above = sum(1 for _, s in d if s > s_star)
            wrong_at = sum(1 for (_, s), ok in zip(d, correct) if s == s_star and not ok)
            o, q = above + 1, above + wrong_at + 1
            in_tie += wrong_at > 0
        pos.append(p), opt.append(o), pess.append(q)
        per_case.append((c, p, o, q, d[0][0] if d else "", len(d)))

    o1 = o1_subst([c["prompt_id"] for c in cases])
    o1_top1 = sum(1 for r in o1.values() if r == 1)

    def n(ranks, k):
        return sum(1 for r in ranks if r is not None and r <= k)

    rows = []
    for key, ranks in (("", pos), ("_opt", opt), ("_pess", pess)):
        rows += [(f"EX1_exomiser_top1_frac{key}", n(ranks, 1) / denominator),
                 (f"EX2_exomiser_top3_frac{key}", n(ranks, 3) / denominator),
                 (f"EX3_exomiser_top10_frac{key}", n(ranks, 10) / denominator)]
    rows += [("EX4_exomiser_top1_gt_o1_subst_top1", "true" if n(pos, 1) > o1_top1 else "false"),
             ("denominator_cases", denominator), ("scored_cases", len(cases))]
    for key, ranks in (("", pos), ("_opt", opt), ("_pess", pess)):
        rows += [(f"exomiser_n_top{k}{key}", n(ranks, k)) for k in (1, 3, 10)]
    rows += [("exomiser_mrr", sum(1 / r for r in pos if r) / denominator),
             ("exomiser_cases_no_result", no_result), ("exomiser_orpha_items_unmapped", unmapped),
             ("o1_subst_n_top1", o1_top1),
             ("exomiser_cases_correct_in_tie", in_tie), ("exomiser_max_tie_size", max_tie)]
    with open(f"{OUT}/results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["key", "value"])
        for k, v in rows:
            w.writerow([k, repr(v) if isinstance(v, float) else v])
    with open(f"{OUT}/per_case.tsv", "w", newline="", encoding="utf-8") as f:
        f.write("row\tid\tgold_id\texomiser_first_correct_rank\texomiser_rank_opt\texomiser_rank_pess\t"
                "exomiser_top_item\texomiser_n_items\to1_subst_first_correct_rank\n")
        for c, p, o, q, top, ni in per_case:
            f.write(f"{c['row']}\t{c['prompt_id']}\t{c['gold_id']}\t{p or ''}\t{o or ''}\t{q or ''}\t{top}\t{ni}\t"
                    f"{o1[c['prompt_id']] or ''}\n")
    print(f"[score] Exomiser top1/3/10 {[n(pos, k) for k in (1, 3, 10)]} (opt {[n(opt, k) for k in (1, 3, 10)]}, "
          f"pess {[n(pess, k) for k in (1, 3, 10)]}); o1-preview subst top1 {o1_top1}; over {denominator}")


if __name__ == "__main__":
    cmds = {"cases": cmd_cases, "analyse": cmd_analyse, "score": cmd_score}
    if len(sys.argv) == 3 and sys.argv[1] == "reduce":
        cmd_reduce(int(sys.argv[2]))
    elif len(sys.argv) == 2 and sys.argv[1] in cmds:
        cmds[sys.argv[1]]()
    else:
        sys.exit(f"usage: score_exomiser.py {{{'|'.join(cmds)}}} | reduce <batch>")
