# Reproducibility report: Cross-tissue immune cell analysis reveals tissue-specific features in humans

- DOI: 10.1126/science.abl5197
- Code: `fe357564a6625d3b1732a022fd39f18e55696e80`
- Generated: 2026-09-06T22:50:28+00:00

## Summary verdict: **reproduced**

4 of 4 claims within tolerance.

## Per-claim table

| id | figure | metric | claimed | obtained | tolerance | verdict | cause | extraction | evidence |
|---|---|---|---|---|---|---|---|---|---|
| T1 | n/a - committed notebook output, not a paper figure | T1_n_cell_types | 98 | 98 | absolute 0 | reproduced | n/a | manual | `work/dominguezconde-2022-celltypist/results.json` |
| T2 | n/a - committed notebook output | T2_n_features | 6639 | 6639 | absolute 0 | reproduced | n/a | manual | `work/dominguezconde-2022-celltypist/results.json` |
| T3 | n/a - committed notebook output | T3_n_features_used | 5645 | 5645 | absolute 0 | reproduced | n/a | manual | `work/dominguezconde-2022-celltypist/results.json` |
| T4 | n/a - committed notebook output | T4_n_genes_input | 18950 | 18950 | absolute 0 | reproduced | n/a | manual | `work/dominguezconde-2022-celltypist/results.json` |

## Environment delta

None: every pinned component matched.

## Data provenance

| id | uri | bytes | sha256 verified | fetched |
|---|---|---|---|---|
| demo_cells | https://celltypist.cog.sanger.ac.uk/Notebook_demo_data/demo_2000_cells.h5ad | 35730948 | True | 2026-09-06T22:50:18+00:00 |
| model_immune_all_low_v2 | https://celltypist.cog.sanger.ac.uk/models/Pan_Immune_CellTypist/v2/Immune_All_Low.pkl | 2824990 | True | 2026-09-06T22:50:19+00:00 |

## Deviations log

- `celltypist --update-models` is skipped. The model is fetched instead by an explicit versioned URL, https://celltypist.cog.sanger.ac.uk/models/Pan_Immune_CellTypist/v2/Immune_All_Low.pkl, and hashed like any other input (data[].model_immune_all_low_v2).
 (why: --update-models resolves through https://celltypist.cog.sanger.ac.uk/models/models.json, which is mutable and unversioned (last-modified 2026-03-16, nine months after the code froze on 2025-06-25) and is checksum-free in celltypist/models.py. Fetching the versioned URL directly makes the model bytes pinnable and hashable. No file under the clone is touched; only our fetch step changes.
; approved by Michael Wolfe, repro-lab maintainer (not the celltypist authors; approved 2026-09-06 before the harness run; neither change touches the paper's code), 2026-09-06)
- celltypist is installed from the clone at the pinned commit fe357564a6625d3b1732a022fd39f18e55696e80, rather than by the repo Dockerfile's unversioned `pip install celltypist`.
 (why: The repo's Dockerfile (579 bytes at fe357564) pins nothing, so `pip install celltypist` would resolve to whatever version PyPI serves on the build day - not necessarily the code this manifest's claims were read from. Installing the pinned SHA keeps the code under test identical to the code cited in claims[].source. Dependency versions remain unpinned, as the project leaves them.
; approved by Michael Wolfe, repro-lab maintainer (not the celltypist authors; approved 2026-09-06 before the harness run; neither change touches the paper's code), 2026-09-06)

## Time and cost

- Wall time: 0.15 min
- Agent tokens: 0
- Estimated cost: USD 0.0
