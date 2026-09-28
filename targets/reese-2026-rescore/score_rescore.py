#!/usr/bin/env python3
"""Score o1-preview's answers with malco (pheval.llm@bd7146d) under two grounding conditions.

Lives in repro-lab, not in the clone; calls malco's own functions and edits nothing in the clone.
  (a) floor: ground_diagnosis_text_to_mondo(..., use_ontogpt_grounding=False) - OAK whole-line exact match.
  (b) subst: as (a), then every line whose OAK result is [("N/A", "No grounding found")] is looked up,
      by its exact string, in the hash-verified Claude Opus 5.5 table; a validated Mondo ID becomes one
      item, "no match" stays N/A. A line missing from the table is a hard stop.
Both are scored with malco's score() (run from /work/run, which holds a copy of the authors' caches).
First-correct rank follows malco's summarize(): the 1-based position of the first item with
is_correct in the flattened item list. Writes /work/out/results.csv (key,value) and per_case.tsv.

Grounding runs in a multiprocessing.Pool of os.cpu_count() workers, as malco's own evaluate step does,
with one OAK adapter per worker (malco's create_single_standardised_results opens one per response).
ground_diagnosis_text_to_mondo is called unchanged, once per response; results come back in input order.
RESCORE_SLICE=<n> (timing runs only, never set in a scored run) scores the first n responses in id order.
"""
import csv, hashlib, json, os, sys
from multiprocessing import Pool

import pandas as pd
from oaklib import get_adapter
from malco.process.cleaning import split_diagnosis_from_header
from malco.process.grounding import ground_diagnosis_text_to_mondo
from malco.process.scoring import score

DATA, OUT = "/work/data", "/work/out"
NA = [("N/A", "No grounding found")]


def load_table(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8", newline=""), delimiter="\t", quoting=csv.QUOTE_NONE))
    table = {r["name"]: r for r in rows}
    if len(table) != len(rows):
        sys.exit("[score_rescore] the Opus table has a duplicated name; stopping")
    resolved = [r for r in rows if r["oak_resolved"] == "true"]
    rate = sum(r["agrees"] == "true" for r in resolved) / len(resolved)
    return table, rate


_annotator = None


def _init_worker():
    global _annotator
    _annotator = get_adapter("sqlite:obo:mondo")


def _ground(response):
    return ground_diagnosis_text_to_mondo(_annotator, split_diagnosis_from_header(response),
                                          verbose=False, use_ontogpt_grounding=False)


def first_correct(scored):
    for pos, item in enumerate(scored or [], start=1):
        if item["is_correct"]:
            return pos
    return None


def main():
    lines = open("/work/run/gpt-01-preview.jsonl", encoding="utf-8").read().splitlines()  # unzipped by run.sh
    result = [json.loads(l) for l in lines if l.strip()]
    if os.environ.get("RESCORE_SLICE"):  # timing only
        result = sorted(result, key=lambda r: r["id"])[:int(os.environ["RESCORE_SLICE"])]
        print(f"[score_rescore] RESCORE_SLICE: timing run on {len(result)} responses; not a scored run")
    denominator = sum(1 for _ in open(os.path.join(DATA, "correct_results.tsv"), encoding="utf-8"))
    table_path = os.path.join(DATA, "opus-mondo-map.tsv")
    table, agreement = load_table(table_path)

    with Pool(os.cpu_count(), initializer=_init_worker) as pool:
        floor = pool.map(_ground, [r["response"] for r in result], chunksize=8)
    print(f"[score_rescore] grounded {len(floor)} responses with {os.cpu_count()} workers")
    subst, hits, missing = [], 0, set()
    for g in floor:
        s = []
        for line, grounded in g:
            if grounded == NA:
                t = table.get(line)
                if t is None:
                    missing.add(line)
                elif t["effective_mondo_id"] != "no match":
                    grounded = [(t["effective_mondo_id"], t["opus_mondo_label"])]
                    hits += 1
            s.append((line, grounded))
        subst.append(s)
    if missing:
        sys.exit(f"[score_rescore] {len(missing)} answer line(s) missing from the Opus table; the input differs "
                 f"from the one the table was built from. First: {sorted(missing)[:3]!r}")

    base = {"id": [r["id"] for r in result], "gold": [r["gold"] for r in result]}
    df_floor = score(pd.DataFrame({**base, "grounding": floor}))
    df_subst = score(pd.DataFrame({**base, "grounding": subst}))

    rf = [first_correct(s) for s in df_floor["scored"]]
    rs = [first_correct(s) for s in df_subst["scored"]]
    items = lambda gs: [i for g in gs for _, lst in g for i in lst]

    def counts(ranks):
        return [sum(1 for x in ranks if x is not None and x <= k) for k in (1, 3, 10)]

    fl, sb = counts(rf), counts(rs)
    mrr = lambda ranks: sum(1 / x for x in ranks if x) / denominator
    h = hashlib.sha256(open(table_path, "rb").read()).hexdigest()
    rows = [
        ("RS1_o1_top1_frac_floor", fl[0] / denominator), ("RS2_o1_top3_frac_floor", fl[1] / denominator),
        ("RS3_o1_top10_frac_floor", fl[2] / denominator),
        ("RS4_o1_top1_frac_subst", sb[0] / denominator), ("RS5_o1_top3_frac_subst", sb[1] / denominator),
        ("RS6_o1_top10_frac_subst", sb[2] / denominator),
        ("denominator_cases", denominator), ("scored_cases", len(result)),
        ("o1_floor_n_top1", fl[0]), ("o1_floor_n_top3", fl[1]), ("o1_floor_n_top10", fl[2]),
        ("o1_subst_n_top1", sb[0]), ("o1_subst_n_top3", sb[1]), ("o1_subst_n_top10", sb[2]),
        ("o1_floor_mrr", mrr(rf)), ("o1_subst_mrr", mrr(rs)),
        ("o1_items_total", len(items(floor))),
        ("o1_floor_items_na", sum(1 for i in items(floor) if i[0] == "N/A")),
        ("o1_subst_items_na", sum(1 for i in items(subst) if i[0] == "N/A")),
        ("o1_subst_table_hits", hits),
        ("opus_map_sha256", h), ("opus_map_agreement_rate", agreement),
    ]
    with open(os.path.join(OUT, "results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["key", "value"])
        for k, v in rows:
            w.writerow([k, repr(v) if isinstance(v, float) else v])
    with open(os.path.join(OUT, "per_case.tsv"), "w", newline="", encoding="utf-8") as f:
        f.write("id\tgold_id\tn_items\tfloor_first_correct_rank\tsubst_first_correct_rank\n")
        for r, g, a, b in zip(result, floor, rf, rs):
            n = sum(len(lst) for _, lst in g)
            f.write(f"{r['id']}\t{r['gold']['disease_id']}\t{n}\t{a or ''}\t{b or ''}\n")
    print(f"[score_rescore] floor top1/3/10 {fl}, subst top1/3/10 {sb}, over {denominator}")


if __name__ == "__main__":
    main()
