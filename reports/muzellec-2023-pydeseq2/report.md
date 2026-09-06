# Reproducibility report: PyDESeq2: a python package for bulk RNA-seq differential expression analysis

- DOI: 10.1093/bioinformatics/btad547
- Code: `4426e4db990db1c511de3b1b9b7a514989663dad`
- Generated: 2026-09-06T22:18:04+00:00

## Summary verdict: **reproduced**

4 of 4 claims within tolerance.

## Per-claim table

| id | figure | metric | claimed | obtained | tolerance | verdict | cause | extraction | evidence |
|---|---|---|---|---|---|---|---|---|---|
| P1 | n/a - reference output committed in the repo, not a paper figure | P1_log2FoldChange_gene1 | 0.632812315254828 | 0.632812476644658 | relative 0.02 | reproduced | n/a | manual | `work/muzellec-2023-pydeseq2/results.json` |
| P2 | n/a - reference output committed in the repo | P2_log10_padj_gene2 | -2.78368 | -2.783684562340294 | absolute 0.3 | reproduced | n/a | manual | `work/muzellec-2023-pydeseq2/results.json` |
| P3 | n/a - reference output committed in the repo | P3_size_factor_sample1 | 1.22898093726827 | 1.228980937268269 | relative 0.02 | reproduced | n/a | manual | `work/muzellec-2023-pydeseq2/results.json` |
| P4 | n/a - reference output committed in the repo | P4_top3_genes_by_abs_stat | ['gene5', 'gene2', 'gene4'] | gene5;gene2;gene4 | rank_order 0 | reproduced | n/a | manual | `work/muzellec-2023-pydeseq2/results.json` |

## Environment delta

None: every pinned component matched.

## Data provenance

| id | uri | bytes | sha256 verified | fetched |
|---|---|---|---|---|
| synthetic_counts | https://raw.githubusercontent.com/owkin/PyDESeq2/4426e4db990db1c511de3b1b9b7a514989663dad/datasets/synthetic/test_counts.csv | 3919 | True | 2026-09-06T22:17:05+00:00 |
| synthetic_metadata | https://raw.githubusercontent.com/owkin/PyDESeq2/4426e4db990db1c511de3b1b9b7a514989663dad/datasets/synthetic/test_metadata.csv | 1915 | True | 2026-09-06T22:17:05+00:00 |

## Deviations log

None.

## Time and cost

- Wall time: 0.95 min
- Agent tokens: 0
- Estimated cost: USD 0.0
