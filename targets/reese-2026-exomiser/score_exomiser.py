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
  score    build each case's differential from its item list and score the minimal item set (below);
           also ground o1-preview under the substituted condition for EX4. Writes /work/out/results.csv and
           per_case.tsv (ranks above 10 written as >10).
  verify   (build-time check, not part of run.sh) minimal against full scoring on 40 rows; writes a table.

Minimal scoring. Items x_1..x_n in tie-rule order. Step A: score x_1, x_2, ... and stop at the first
correct item (rank R) or after x_10. Step B: with g = the score of x_R, or of x_10 if none of the first ten is
correct, score every other item scoring exactly g. This fixes [R <= k], [O <= k] and [P <= k] for
k in {1, 3, 10} exactly as full scoring would: items scoring above g all precede x_R (or x_10) and were
scored in Step A, and the whole tie group at g is scored. When no correct item scores g and none is in the
first ten, every correct item scores below x_10, so every rank is above 10. Ranks above 10 are not
computed, so MRR is truncated at 10 (exomiser_mrr_at10).

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
IRI as ORPHA:n); unmapped items stay in place and score 0. Each scored item is
scored with malco's score_grounded_result (see the score section);
is_correct = score > 0. A case with no item is "not found" and stays in the denominator.

Tie band (evidence): with s* the highest Exomiser score among correct items, optimistic rank = 1 + items
scoring above s*; pessimistic rank = items above s* + incorrect items scoring exactly s* + 1.
exomiser_max_tie_size is the largest number of items sharing one score in any case's differential.
"""
import csv, gzip, hashlib, io, json, os, shutil, subprocess, sys, tarfile, threading, time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

CASES_TSV = "/work/cases.tsv"
DATA, OUT, EXO = "/work/data", "/work/out", "/work/wk"
AUDIT, ITEMS, RAW_SHA = f"{EXO}/raw", f"{EXO}/items", f"{EXO}/raw_json.sha256"
RAW = "/work/raw"  # container-local: Exomiser writes here; only audit rows are moved to the mounted AUDIT dir
CASE_DIR, BATCH_DIR = "/work/cases", "/work/batches"
CLI = "/work/exomiser-cli-14.0.1"
OPTIONS = "/work/output-options.yml"
BATCH_SIZE, JVMS, XMX, AUDIT_ROWS = 25, 4, "3g", 20
REDUCERS = 2  # concurrent JSON reductions; each holds one case JSON (up to about 0.3 GB) as text
SCORERS = int(os.environ.get("SCORERS", "12"))  # scoring processes, about 0.5 GiB each (one Mondo adapter): 12 fit in --memory 16g
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
def iter_genes(path, block=1 << 24):
    """The elements of the top-level JSON array, decoded one at a time with json.JSONDecoder.raw_decode from
    a buffer refilled in 16 MiB blocks, so a case output (up to about 0.9 GB) is never held whole, as text
    or as objects. Every element is a JSON object, so a buffer cut inside one cannot decode early. Yields
    exactly the elements json.load(path) would return (checked on the audit rows)."""
    dec = json.JSONDecoder()
    with open(path, encoding="utf-8") as f:
        buf, eof = f.read(block), False
        i = buf.index("[") + 1
        while True:
            while i < len(buf) and buf[i] in " \t\r\n,":
                i += 1
            if i == len(buf):
                if eof:
                    raise ValueError(f"{path}: JSON array not closed")
                more = f.read(block)
                buf, i, eof = more, 0, not more
                continue
            if buf[i] == "]":
                return
            try:
                obj, j = dec.raw_decode(buf, i)
            except json.JSONDecodeError:
                if eof:
                    raise
                more = f.read(block)
                buf, i, eof = buf[i:] + more, 0, not more
                continue
            yield obj
            i = j


def read_items(path):
    items = []
    for gi, g in enumerate(iter_genes(path)):
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
    t0, reducers = time.time(), threading.BoundedSemaphore(REDUCERS)
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
        with reducers:  # at most REDUCERS reductions at once, beside the JVMs, inside --memory 16g
            rc = subprocess.run([sys.executable, __file__, "reduce", str(k)]).returncode
        if rc != 0:
            raise SystemExit(f"[analyse] reducing batch {k:03d} failed (exit {rc}); stopping")
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
# Every correctness decision is malco's own score_grounded_result(prediction, gold, mondo, cache) > 0, called
# directly in worker processes (one Mondo adapter each). The cache passed is malco's per-term OMIM-mapping
# cache (gold-independent); a (prediction, gold) memo avoids repeating a pair. An unmapped ORPHA item and an
# o1-preview "N/A" item are incorrect without a call: malco's score_grounded_result gives such an id 0.0
# (it has no OMIM mapping and no descendants but itself).
_mondo = _terms = None
_pairs = {}


def _init_scorer():
    global _mondo, _terms
    from cachetools import LRUCache
    from oaklib import get_adapter
    _mondo = get_adapter("sqlite:obo:mondo")
    _terms = LRUCache(maxsize=2 ** 22)
    _terms.hits = _terms.misses = 0


def _correct(pred, gold, work):
    if pred is None or pred == "N/A":
        return False
    k = (pred, gold)
    if k not in _pairs:
        from malco.process.mondo_score_utils import score_grounded_result
        _pairs[k] = score_grounded_result(pred, gold, _mondo, _terms) > 0
        work[0] += 1
    return _pairs[k]


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


def load_ordo():
    import sqlite3
    from oaklib import get_adapter
    db = get_adapter("sqlite:obo:mondo").engine.url.database
    ordo = {}
    for subj, obj in sqlite3.connect(db).execute(
            "SELECT subject, object FROM statements WHERE predicate = 'skos:exactMatch' "
            "AND subject LIKE 'MONDO:%' AND object LIKE 'ORDO:%'"):
        ordo.setdefault(obj, set()).add(subj)
    if any(len(v) > 1 for v in ordo.values()):
        sys.exit("[score] an ORDO id has more than one Mondo exactMatch; the mapping rule does not cover it")
    return {k: next(iter(v)) for k, v in ordo.items()}


def predictions(d, ordo):
    """The id malco scores for each differential item: the item itself, or, for ORPHA:n / Orphanet:n, the
    Mondo term whose skos:exactMatch is ORDO:n (None when there is none)."""
    out = []
    for did, _ in d:
        if did.startswith(("ORPHA:", "Orphanet:")):
            out.append(ordo.get("ORDO:" + did.split(":", 1)[1]))
        else:
            out.append(did)
    return out


def ranks_from(d, ok, s_star):
    """Optimistic and pessimistic ranks given the score s* of the best correct item; ok[i] is known for
    every item scoring exactly s*."""
    above = sum(1 for _, s in d if s > s_star)
    wrong_at = sum(1 for i, (_, s) in enumerate(d) if s == s_star and not ok[i])
    return above + 1, above + wrong_at + 1, wrong_at


def minimal(args):
    """Steps A and B for one case. Returns R (<= 10, else None), O and P (exact when a correct item at the
    deciding score was found, else None: not in the top 10), the tie-group size at g, and the pairs scored."""
    row, gold, d, preds = args
    work, ok = [0], {}
    R = None
    for i in range(min(10, len(d))):                      # Step A
        ok[i] = _correct(preds[i], gold, work)
        if ok[i]:
            R = i + 1
            break
    if R is None and len(d) <= 10:
        return row, None, None, None, None, 0, work[0]
    g = d[R - 1][1] if R else d[9][1]                    # Step B
    group = [i for i, (_, s) in enumerate(d) if s == g]
    for i in group:
        if i not in ok:
            ok[i] = _correct(preds[i], gold, work)
    if not any(ok[i] for i in group):
        return row, R, None, None, None, len(group), work[0]
    O, P, wrong_at = ranks_from(d, ok, g)
    return row, R, O, P, wrong_at, len(group), work[0]


def _pair(pair):
    """One (prediction, gold) pair through malco's score_grounded_result (verification only)."""
    return pair, _correct(pair[0], pair[1], [0])


def full(job, verdict):
    """Every item of one case scored (verification only); verdict maps (prediction, gold) to correctness."""
    row, gold, d, preds = job
    ok = {i: (p is not None and verdict[(p, gold)]) for i, p in enumerate(preds)}
    hits = [i for i in range(len(d)) if ok[i]]
    if not hits:
        return row, None, None, None
    s_star = d[hits[0]][1]
    O, P, _ = ranks_from(d, ok, s_star)
    return row, hits[0] + 1, O, P


def o1_first(args):
    """o1-preview's first-correct position in its flattened item list (malco's rank), or None."""
    items, gold = args
    work = [0]
    for pos, pred in enumerate(items, start=1):
        if _correct(pred, gold, work):
            return pos
    return None


def _ground(response):
    global _mondo
    if _mondo is None:
        _init_scorer()
    from malco.process.cleaning import split_diagnosis_from_header
    from malco.process.grounding import ground_diagnosis_text_to_mondo
    return ground_diagnosis_text_to_mondo(_mondo, split_diagnosis_from_header(response),
                                          verbose=False, use_ontogpt_grounding=False)


def o1_subst(cases):
    """o1-preview's first-correct rank per prompt id under the substituted condition, as reese-2026-rescore
    builds it: OAK whole-line exact match, then the hash-verified Opus table for lines OAK cannot ground."""
    result = [json.loads(l) for l in open("/work/run/gpt-01-preview.jsonl", encoding="utf-8") if l.strip()]
    table = {r["name"]: r for r in csv.DictReader(open(f"{DATA}/opus-mondo-map.tsv", encoding="utf-8",
                                                          newline=""), delimiter="\t", quoting=csv.QUOTE_NONE)}
    with Pool(SCORERS, initializer=_init_scorer) as pool:
        floor = pool.map(_ground, [r["response"] for r in result], chunksize=8)
        jobs, missing = [], set()
        for r, g in zip(result, floor):
            items = []
            for line, grounded in g:
                if grounded == NA:
                    t = table.get(line)
                    if t is None:
                        missing.add(line)
                    elif t["effective_mondo_id"] != "no match":
                        grounded = [(t["effective_mondo_id"], t["opus_mondo_label"])]
                items += [i for i, _ in grounded]
            jobs.append((items, r["gold"]["disease_id"]))
        if missing:
            sys.exit(f"[score] {len(missing)} o1-preview line(s) missing from the Opus table; stopping")
        ranks = dict(zip((r["id"] for r in result), pool.map(o1_first, jobs, chunksize=8)))
    if set(ranks) != {c["prompt_id"] for c in cases}:
        sys.exit("[score] o1-preview ids differ from cases.tsv prompt ids; stopping")
    return ranks


def score_jobs(cases, ordo):
    jobs, max_tie, mapped, unmapped, no_result = [], 0, 0, 0, 0
    for c in cases:
        d = differential(c["row"])
        preds = predictions(d, ordo)
        orpha = [p for (did, _), p in zip(d, preds) if did.startswith(("ORPHA:", "Orphanet:"))]
        mapped += sum(1 for p in orpha if p)
        unmapped += sum(1 for p in orpha if not p)
        no_result += not d
        counts = {}
        for _, s in d:
            counts[s] = counts.get(s, 0) + 1
        max_tie = max([max_tie] + list(counts.values()))
        jobs.append((c["row"], c["gold_id"], d, preds))
    return jobs, max_tie, mapped, unmapped, no_result


def cap(x):
    return ">10" if x is None or x > 10 else str(x)


def cmd_score():
    cases = read_cases()
    denominator = sum(1 for _ in open(f"{DATA}/correct_results.tsv", encoding="utf-8"))
    ordo = load_ordo()
    t0 = time.time()
    jobs, max_tie, mapped, unmapped, no_result = score_jobs(cases, ordo)
    example = next(((did, p) for _, _, d, preds in jobs for (did, _), p in zip(d, preds)
                    if did.startswith("ORPHA:") and p), None)
    print(f"[score] {len(cases)} differentials, {sum(len(j[2]) for j in jobs)} items; ORPHA items mapped "
          f"{mapped}, unmapped {unmapped}; example {example[0]} -> {example[1]}", flush=True)
    order = sorted(range(len(jobs)), key=lambda i: (jobs[i][1], jobs[i][0]))  # group by gold for the caches
    with Pool(SCORERS, initializer=_init_scorer) as pool:
        got = {r[0]: r for r in pool.imap_unordered(minimal, [jobs[i] for i in order], chunksize=4)}
    res = [got[c["row"]] for c in cases]
    n_pairs = sum(r[6] for r in res)
    print(f"[score] minimal scoring: {n_pairs} (item, gold) pairs in {(time.time() - t0) / 60:.1f} min", flush=True)
    pos = [r[1] for r in res]
    opt = [r[2] for r in res]
    pess = [r[3] for r in res]
    in_tie = sum(1 for r in res if r[4])

    o1 = o1_subst(cases)
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
    rows += [("exomiser_mrr_at10", sum(1 / r for r in pos if r and r <= 10) / denominator),
             ("exomiser_cases_no_result", no_result), ("exomiser_orpha_items_mapped", mapped),
             ("exomiser_orpha_items_unmapped", unmapped), ("exomiser_n_scored_pairs", n_pairs),
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
        for c, r, j in zip(cases, res, jobs):
            d = j[2]
            f.write(f"{c['row']}\t{c['prompt_id']}\t{c['gold_id']}\t{cap(r[1])}\t{cap(r[2])}\t{cap(r[3])}\t"
                    f"{d[0][0] if d else ''}\t{len(d)}\t{o1[c['prompt_id']] or ''}\n")
    print(f"[score] Exomiser top1/3/10 {[n(pos, k) for k in (1, 3, 10)]} (opt {[n(opt, k) for k in (1, 3, 10)]}, "
          f"pess {[n(pess, k) for k in (1, 3, 10)]}); o1-preview subst top1 {o1_top1}; over {denominator}")


def cmd_verify(out_path):
    """Pre-registered check of minimal against full scoring: rows 0001-0020 plus the 20 other rows with the
    largest tie group at g (ties by row number). R, O and P capped at 10 must agree on all 40 rows."""
    cases = read_cases()
    ordo = load_ordo()
    t0 = time.time()
    jobs, *_ = score_jobs(cases, ordo)
    by_row = {j[0]: j for j in jobs}
    with Pool(SCORERS, initializer=_init_scorer) as pool:
        order = sorted(range(len(jobs)), key=lambda i: (jobs[i][1], jobs[i][0]))
        mins = {r[0]: r for r in pool.imap_unordered(minimal, [jobs[i] for i in order], chunksize=4)}
        t_min = time.time() - t0
        audit = [c["row"] for c in cases[:AUDIT_ROWS]]
        rest = sorted((r for r in mins if r not in audit), key=lambda r: (-(mins[r][5] or 0), r))[:20]
        sample = audit + rest
        # Full scoring: every distinct (prediction, gold) pair of the sample rows, spread over the workers
        # (sorted by prediction, so a worker's term cache is reused), then each row's ranks from the verdicts.
        pairs = sorted({(p, by_row[r][1]) for r in sample for p in by_row[r][3] if p is not None})
        verdict = dict(pool.imap_unordered(_pair, pairs, chunksize=64))
    fulls = {r: full(by_row[r], verdict) for r in sample}
    lines, agree = [], 0
    lines.append("| row | set | tie group at g | minimal R / O / P | full R / O / P | agree |")
    lines.append("|---|---|---|---|---|---|")
    for r in sample:
        m, f = mins[r], fulls[r]
        a = (cap(m[1]), cap(m[2]), cap(m[3])) == (cap(f[1]), cap(f[2]), cap(f[3]))
        agree += a
        lines.append(f"| {r} | {'audit' if r in audit else 'largest tie'} | {m[5] if m[5] is not None else '-'} | "
                     f"{cap(m[1])} / {cap(m[2])} / {cap(m[3])} | {cap(f[1])} / {cap(f[2])} / {cap(f[3])} | "
                     f"{'yes' if a else 'NO'} |")
    summary = (f"minimal scoring of all {len(jobs)} cases: {sum(m[6] for m in mins.values())} (item, gold) pairs "
               f"in {t_min / 60:.1f} min on {SCORERS} processes; full scoring of the {len(sample)} sample "
               f"rows: {len(pairs)} distinct pairs; agreement {agree} of {len(sample)}")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fo:
        fo.write(summary + "\n\n" + "\n".join(lines) + "\n")
    print("[verify] " + summary, flush=True)
    if agree != len(sample):
        sys.exit("[verify] minimal and full scoring disagree; stopping")


if __name__ == "__main__":
    cmds = {"cases": cmd_cases, "analyse": cmd_analyse, "score": cmd_score}
    if len(sys.argv) == 3 and sys.argv[1] == "reduce":
        cmd_reduce(int(sys.argv[2]))
    elif len(sys.argv) == 3 and sys.argv[1] == "verify":
        cmd_verify(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] in cmds:
        cmds[sys.argv[1]]()
    else:
        sys.exit(f"usage: score_exomiser.py {{{'|'.join(cmds)}}} | reduce <batch>")
