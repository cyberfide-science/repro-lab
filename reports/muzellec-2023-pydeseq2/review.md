# Reviewer findings: `muzellec-2023-pydeseq2`

Reviewed against `harness/prompts/reviewer.md`, rules 1–8 and the tone rules. Path mapping per `harness/README.md` ("The prompts" table). Evidence files read: `reports/muzellec-2023-pydeseq2/report.json`, `reports/muzellec-2023-pydeseq2/report.md`, `targets/muzellec-2023-pydeseq2/repro-target.yaml`, `work/muzellec-2023-pydeseq2/results.json`, `work/muzellec-2023-pydeseq2/env_actual.json`, `work/muzellec-2023-pydeseq2/provenance.json`, `work/muzellec-2023-pydeseq2/run_log.json`, `work/muzellec-2023-pydeseq2/logs/container_run.log`, plus `targets/muzellec-2023-pydeseq2/Dockerfile`, `run.sh`, `extract_results.py`.

## Rule 1 / rule 2 trace: every sentence in `report.md` that states a number, verdict, version, hash or date

Each line below is accepted; the file and key it traces to is quoted.

| `report.md` line | Sentence / cell | Traces to |
|---|---|---|
| 1 | title "PyDESeq2: a python package for bulk RNA-seq differential expression analysis" | `report.json` `paper.title`; `repro-target.yaml` `paper.title` |
| 3 | "DOI: 10.1093/bioinformatics/btad547" | `report.json` `paper.doi`; `repro-target.yaml` `paper.doi` |
| 4 | "Code: `4426e4db990db1c511de3b1b9b7a514989663dad`" | `report.json` `paper.code_sha`; `work/.../run_log.json` `code_sha`; `logs/container_run.log` line 1 `== git HEAD: 4426e4db990db1c511de3b1b9b7a514989663dad`; `repro-target.yaml` `code[0].commit` |
| 5 | "Generated: 2026-09-06T22:18:04+00:00" | `report.json` `generated_at` |
| 7 | "Summary verdict: **reproduced**" | `report.json` `verdict` |
| 9 | "4 of 4 claims within tolerance." | `report.json` `claims[]` — length 4, each `claims[i].verdict == "reproduced"` |
| 15 | P1 claimed `0.632812315254828` | `report.json` `claims[0].claimed`; `repro-target.yaml` `claims[P1].value` |
| 15 | P1 obtained `0.632812476644658` | `report.json` `claims[0].obtained`; `work/.../results.json` `metrics.P1_log2FoldChange_gene1`; `logs/container_run.log` line 21 |
| 15 | P1 metric `P1_log2FoldChange_gene1` | `repro-target.yaml` `harness.claim_keys.P1` (documented mapping, `docs/CONVENTIONS.md`) |
| 15 | P1 tolerance `relative 0.02` | `repro-target.yaml` `claims[P1].tolerance` = 0.02, `tolerance_type` = relative; `report.json` `claims[0].tolerance` / `tolerance_type` |
| 15 | P1 verdict `reproduced`, extraction `manual` | `report.json` `claims[0].verdict`, `claims[0].extraction`; `repro-target.yaml` `claims[P1].extraction: manual` |
| 16 | P2 claimed `-2.78368` | `report.json` `claims[1].claimed`; `repro-target.yaml` `claims[P2].value: -2.783680` (numerically identical; see finding F1) |
| 16 | P2 obtained `-2.783684562340294` | `report.json` `claims[1].obtained`; `work/.../results.json` `metrics.P2_log10_padj_gene2`; `logs/container_run.log` line 22 |
| 16 | P2 tolerance `absolute 0.3` | `repro-target.yaml` `claims[P2].tolerance: 0.3`, `tolerance_type: absolute`; `report.json` `claims[1]` same |
| 17 | P3 claimed `1.22898093726827` | `report.json` `claims[2].claimed`; `repro-target.yaml` `claims[P3].value` |
| 17 | P3 obtained `1.228980937268269` | `report.json` `claims[2].obtained`; `work/.../results.json` `metrics.P3_size_factor_sample1`; `logs/container_run.log` line 23 |
| 17 | P3 tolerance `relative 0.02` | `repro-target.yaml` `claims[P3].tolerance` / `tolerance_type`; `report.json` `claims[2]` same |
| 18 | P4 claimed `['gene5', 'gene2', 'gene4']` | `report.json` `claims[3].claimed` = `["gene5","gene2","gene4"]`; `repro-target.yaml` `claims[P4].value: [gene5, gene2, gene4]` (see finding F2) |
| 18 | P4 obtained `gene5;gene2;gene4` | `report.json` `claims[3].obtained`; `work/.../results.json` `metrics.P4_top3_genes_by_abs_stat`; `logs/container_run.log` line 24 |
| 18 | P4 tolerance `rank_order 0` | `repro-target.yaml` `claims[P4].tolerance: 0`, `tolerance_type: rank-order`; `report.json` `claims[3].tolerance_type: "rank_order"` — the documented `rank-order`→`rank_order` spelling mapping (`docs/CONVENTIONS.md`, `harness/README.md` stage 5), tolerance unchanged |
| 22 | "None: every pinned component matched." | `report.json` `environment_delta: []`; `work/.../env_actual.json` `delta: []` (see finding F3) |
| 28 | synthetic_counts uri / `3919` / `True` / `2026-09-06T22:17:05+00:00` | `report.json` `data_provenance[0].uri`/`bytes`/`verified`/`fetched_at`; `work/.../provenance.json` [0] same keys; `repro-target.yaml` `data[0].uri`, `size_bytes: 3919` |
| 29 | synthetic_metadata uri / `1915` / `True` / `2026-09-06T22:17:05+00:00` | `report.json` `data_provenance[1]` same keys; `work/.../provenance.json` [1]; `repro-target.yaml` `data[1].uri`, `size_bytes: 1915` |
| 33 | "Deviations log — None." | `report.json` `deviations: []`; `repro-target.yaml` `deviations: []` |
| 37 | "Wall time: 0.95 min" | `report.json` `cost.wall_minutes`; consistent with `work/.../run_log.json` `stages[0].seconds: 56.99` and `started_at` 22:17:06 → `finished_at` 22:18:03 |
| 38 | "Agent tokens: 0" | `report.json` `cost.agent_tokens` (see finding F4) |
| 39 | "Estimated cost: USD 0.0" | `report.json` `cost.usd_estimate` (see finding F4) |

No sentence in `report.md` failed to trace. No number appears in `report.md` that is absent from `report.json`, `work/muzellec-2023-pydeseq2/results.json`, `work/muzellec-2023-pydeseq2/provenance.json` or `targets/muzellec-2023-pydeseq2/repro-target.yaml`. Nothing is recomputed or re-rounded in prose.

## Rules 3–8

- **Rule 3 (tolerances unchanged):** pass. P1 `0.02`/relative, P2 `0.3`/absolute, P3 `0.02`/relative, P4 `0`/rank-order in `targets/muzellec-2023-pydeseq2/repro-target.yaml` `claims[]` are carried into `reports/muzellec-2023-pydeseq2/report.json` `claims[].tolerance` / `tolerance_type` with no numeric change. The only difference is the documented `rank-order` → `rank_order` spelling.
- **Rule 4 (cause_category on not_reproduced):** vacuously satisfied. No claim in `report.json` `claims[].verdict` is `not_reproduced`; all four carry `cause_category: "n/a"`.
- **Rule 5 (digitized labelling):** vacuously satisfied. `repro-target.yaml` `claims[].extraction` is `manual` for P1–P4; `report.md` line 13 has an `extraction` column and lines 15–18 show `manual` for each. No claim is `digitized`.
- **Rule 6 (deviations / unlisted steps):** pass, with note F5. `logs/container_run.log` shows only the two commands the manifest declares in `stages[]` — line 3 `== pytest tests/` (`stages[reference_suite].cmd`) and line 6 `== extract_results.py` (`stages[extract].cmd`) — driven by the single host stage `container_run` in `harness.stages[]`, whose argv matches `run_log.json` `stages[0].cmd`. No step appears in the log that changes the method.
- **Rule 7 (manifest predates the run):** pass. `git log -1 --format=%cI -- targets/muzellec-2023-pydeseq2/repro-target.yaml` → `2026-09-06T18:11:10-04:00` = `2026-09-06T22:11:10Z`. `work/muzellec-2023-pydeseq2/results.json` mtime `2026-09-06 18:18:03 -0400` = `22:18:03Z`. `report.json` `generated_at` = `2026-09-06T22:18:04+00:00`. Manifest commit precedes both by about seven minutes.
- **Rule 8 (paper-level verdict):** pass. All four entries of `report.json` `claims[].verdict` are `reproduced`, so `verdict: "reproduced"` is the required value.
- **Tone rules:** pass. `report.md` contains no claim that the paper or the authors are wrong, no speculation about author intent, and no adjective about the paper's quality. There is no discrepancy sentence to phrase, since no claim is out of tolerance.

## Findings

**F1 — note**
Sentence/field: `report.md` line 16, P2 `claimed` cell, `-2.78368`.
Expected in: `targets/muzellec-2023-pydeseq2/repro-target.yaml` `claims[P2].value`, which reads `-2.783680`.
Found instead: `reports/muzellec-2023-pydeseq2/report.json` `claims[1].claimed` = `-2.78368`, the same number with the trailing zero dropped by JSON float serialisation. The value is numerically identical to the manifest and is not a re-rounding, so this is not a rule 2 violation; recorded only so a reader comparing the two files character-by-character is not surprised.

**F2 — note**
Sentence/field: `report.md` line 18, P4 `claimed` cell, `['gene5', 'gene2', 'gene4']`.
Expected in: `report.json` `claims[3].claimed`, which is the JSON array `["gene5","gene2","gene4"]` (from `repro-target.yaml` `claims[P4].value`).
Found instead: the same three elements in the same order rendered as a Python list literal with single quotes. Content and order are unchanged, so the rank-order claim is still checkable from the report; the rendering is inconsistent with the `obtained` cell on the same row, which uses the results-file form `gene5;gene2;gene4`.

**F3 — note**
Sentence/field: `report.md` line 22, "None: every pinned component matched."
Expected in: `report.json` `environment_delta` and `work/muzellec-2023-pydeseq2/env_actual.json` `delta`.
Found instead: both are `[]`, so the sentence traces and is not false. The wording is nonetheless broader than the evidence: `repro-target.yaml` `environment.python: "3.11"` is a floor, not a pin (`harness/README.md`: "The manifest's `environment.python` is a floor"), and the version actually run — `env_actual.json` `python: "3.12.14"`, corroborated by `logs/container_run.log` line 2 `== python: Python 3.12.14` — appears nowhere in `report.md`. The image id `sha256:f2226316d67088b598abb0a28a48410d4015c9edb983497424b48decd4a26402` and base digest `python@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea` from `env_actual.json` are likewise absent from `report.md`. A reader of the report alone cannot tell which Python or which image produced the numbers.

**F4 — note**
Sentence/field: `report.md` lines 38–39, "Agent tokens: 0" and "Estimated cost: USD 0.0".
Expected in: `report.json` `cost.agent_tokens` and `cost.usd_estimate`.
Found instead: both are present and are `0` / `0.0`, so the lines trace. `harness/README.md` ("Cost") states that "A zero here means 'not measured by an agent wrapper', not 'free'", and `report.md` carries the zeros without that qualification. As written, an unqualified "Estimated cost: USD 0.0" can be read as a measurement rather than an absence of one.

**F5 — note**
Sentence/field: rule 6 check against `targets/muzellec-2023-pydeseq2/run.sh` and `logs/container_run.log`.
Expected in: `repro-target.yaml` `stages[]`, which lists exactly two in-container commands (`reference_suite`, `extract`).
Found instead: `run.sh` lines 6, 7, 12 and 14 also execute `git rev-parse HEAD`, `python --version`, `cat /work/out/results.csv` and `git status --porcelain`. These are read-only provenance echoes that do not alter the method, and the first of them is required by the harness contract (`harness/README.md`: the `== git HEAD:` line is the code SHA the report carries), so none of them is a deviation needing an `approved_by` entry and `deviations: []` remains correct. Recorded so the gap between `stages[]` and the script's line count is explicit.

**F6 — note**
Sentence/field: `logs/container_run.log` line 25, "== git status --porcelain inside the clone after the run (empty means untouched):".
Expected in: the log, an empty `git status --porcelain` output demonstrating the clone was not edited.
Found instead: the header is immediately followed at lines 26–48 by the pydeseq2 progress output ("Fitting size factors...", etc.), which is stderr flushed after the buffered stdout. The `git status` result is therefore not separable from the surrounding text, and the log does not cleanly evidence the untouched-clone check. `report.md` makes no untouched-clone assertion, so no sentence in the report is affected; this is a note about the strength of the evidence file, not about the report text. Interleaving stdout and stderr, or writing the `git status` output to its own file under `out/`, would make the check readable.

No **block** findings. No **fix** findings.

APPROVED
