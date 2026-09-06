#!/usr/bin/env python3
"""Write the four claim metrics of repro-target.yaml to a key,value CSV.

Lives in repro-lab, NOT in the PyDESeq2 clone. Calls only pydeseq2's documented
public API on the repo's shipped synthetic data, in the same sequence the
project's own tests/test_pydeseq2.py uses against r_test_res.csv:
DeseqDataSet(design="~condition").deseq2(), then DeseqStats(contrast B vs A).
"""
import argparse
import csv
import math

from pydeseq2.dds import DeseqDataSet
from pydeseq2.default_inference import DefaultInference
from pydeseq2.ds import DeseqStats
from pydeseq2.utils import load_example_data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    counts_df = load_example_data(modality="raw_counts", dataset="synthetic", debug=False)
    metadata = load_example_data(modality="metadata", dataset="synthetic", debug=False)

    inference = DefaultInference(n_cpus=1)
    dds = DeseqDataSet(
        counts=counts_df, metadata=metadata, design="~condition", inference=inference
    )
    dds.deseq2()
    ds = DeseqStats(dds, contrast=["condition", "B", "A"], inference=inference)
    ds.summary()
    res = ds.results_df

    top3 = res["stat"].abs().sort_values(ascending=False).index[:3].tolist()
    rows = [
        ("P1_log2FoldChange_gene1", res.loc["gene1", "log2FoldChange"]),
        ("P2_log10_padj_gene2", math.log10(res.loc["gene2", "padj"])),
        ("P3_size_factor_sample1", dds.obs.loc["sample1", "size_factors"]),
        ("P4_top3_genes_by_abs_stat", ";".join(top3)),
    ]
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "value"])
        for k, v in rows:
            w.writerow([k, repr(float(v)) if not isinstance(v, str) else v])


if __name__ == "__main__":
    main()
