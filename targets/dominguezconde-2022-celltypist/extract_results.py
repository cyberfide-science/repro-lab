#!/usr/bin/env python3
"""Write the four claim metrics of repro-target.yaml to a key,value CSV.

Lives in repro-lab, NOT in the celltypist clone. T1 and T2 are read through
celltypist's public API from the pinned model file. T3 and T4 are parsed out of
the annotate stage's own stdout, captured by run.sh; no number is retyped.
"""
import argparse, csv, re

import celltypist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--annotate-log", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    m = celltypist.models.Model.load(a.model)
    log = open(a.annotate_log, encoding="utf-8", errors="replace").read()
    used = re.search(r"(\d+) features used for prediction", log)
    genes = re.search(r"Input data has \d+ cells and (\d+) genes", log)
    if not used or not genes:
        raise SystemExit("annotate log does not carry the two printed counts")

    rows = [
        ("T1_n_cell_types", len(m.cell_types)),
        ("T2_n_features", len(m.features)),
        ("T3_n_features_used", int(used.group(1))),
        ("T4_n_genes_input", int(genes.group(1))),
    ]
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value"])
        for k, v in rows:
            w.writerow([k, v])


if __name__ == "__main__":
    main()
