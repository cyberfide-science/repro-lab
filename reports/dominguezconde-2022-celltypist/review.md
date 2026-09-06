# Reviewer findings — `dominguezconde-2022-celltypist`

Reviewed against `harness/prompts/reviewer.md`, using the path mapping in `harness/README.md`. Read-only; nothing in the repository was modified.

## Rule 1 / rule 2 — sentence-by-sentence traceability of `reports/dominguezconde-2022-celltypist/report.md`

Every sentence carrying a number, verdict, version, hash or date, with the file and key it traces to. Accepted unless a finding below says otherwise.

| Line in report.md | Traces to |
|---|---|
| `# Reproducibility report: Cross-tissue immune cell analysis reveals tissue-specific features in humans` | `report.json` key `paper.title` = "Cross-tissue immune cell analysis reveals tissue-specific features in humans"; originates in `targets/dominguezconde-2022-celltypist/repro-target.yaml` key `paper.title`. Accepted. |
| `- DOI: 10.1126/science.abl5197` | `report.json` key `paper.doi` = `"10.1126/science.abl5197"`; manifest key `paper.doi`. Accepted. |
| `- Code: \`fe357564a6625d3b1732a022fd39f18e55696e80\`` | `report.json` key `paper.code_sha`; `work/dominguezconde-2022-celltypist/run_log.json` key `code_sha` = `"fe357564a6625d3b1732a022fd39f18e55696e80"`, itself read from the container's own first stdout line in `work/dominguezconde-2022-celltypist/logs/container_run.log`: `== git HEAD: fe357564a6625d3b1732a022fd39f18e55696e80`. Equals manifest key `code[0].commit`. Accepted. |
| `- Generated: 2026-09-06T22:18:26+00:00` | `report.json` key `generated_at` = `"2026-09-06T22:18:26+00:00"`. Accepted. |
| `## Summary verdict: **reproduced**` | `report.json` key `verdict` = `"reproduced"`. Accepted; see rule 8 below. |
| `4 of 4 claims within tolerance.` | `report.json` key `claims[]`, length 4, each with `verdict` = `"reproduced"`. Accepted. |
| Table row `T1 … 98 | 98 | absolute 0 | reproduced | n/a | manual` | claimed: `report.json` `claims[0].claimed` = 98 ← manifest `claims[0].value: 98`. obtained: `report.json` `claims[0].obtained` = 98 ← `work/dominguezconde-2022-celltypist/results.json` key `metrics.T1_n_cell_types` = 98 ← `out/dominguezconde-2022-celltypist/results.csv` row `T1_n_cell_types,98`, echoed in `logs/container_run.log`. tolerance: `claims[0].tolerance` = 0, `tolerance_type` = `"absolute"` ← manifest `claims[0].tolerance: 0`, `tolerance_type: absolute`. extraction: `claims[0].extraction` = `"manual"` ← manifest `claims[0].extraction: manual`. Accepted. |
| Table row `T2 … 6639 | 6639 | absolute 0 | reproduced | n/a | manual` | `report.json` `claims[1].claimed` = 6639 ← manifest `claims[1].value: 6639`; `claims[1].obtained` = 6639 ← `results.json` key `metrics.T2_n_features` = 6639 ← `results.csv` row `T2_n_features,6639`. Tolerance `0` / `absolute` ← manifest `claims[1].tolerance`, `claims[1].tolerance_type`. Accepted. |
| Table row `T3 … 5645 | 5645 | absolute 0 | reproduced | n/a | manual` | `report.json` `claims[2].claimed` = 5645 ← manifest `claims[2].value: 5645`; `claims[2].obtained` = 5645 ← `results.json` key `metrics.T3_n_features_used` = 5645 ← `results.csv` row `T3_n_features_used,5645`, and in `logs/container_run.log` the annotate stage's own line `🧬 5645 features used for prediction`. Tolerance `0` / `absolute` ← manifest. Accepted. |
| Table row `T4 … 18950 | 18950 | absolute 0 | reproduced | n/a | manual` | `report.json` `claims[3].claimed` = 18950 ← manifest `claims[3].value: 18950`; `claims[3].obtained` = 18950 ← `results.json` key `metrics.T4_n_genes_input` = 18950 ← `results.csv` row `T4_n_genes_input,18950`, and in `logs/container_run.log`: `🔬 Input data has 2000 cells and 18950 genes`. Tolerance `0` / `absolute` ← manifest. Accepted. |
| Evidence column, all four rows: `work/dominguezconde-2022-celltypist/results.json` | `report.json` `claims[*].evidence_path`; the file exists on disk with the four metrics named above. Accepted. |
| `## Environment delta` → `None: every pinned component matched.` | `report.json` key `environment_delta` = `[]`; `work/dominguezconde-2022-celltypist/env_actual.json` key `delta` = `[]`, compared against `targets/dominguezconde-2022-celltypist/env-resolved.txt` per key `pip_freeze_compared_with`. The code-SHA arm of the same check also produced no entry: `run_log.json` `code_sha` equals manifest `code[0].commit`. Accepted as to the number; see finding 2 as to the wording. |
| Provenance row `demo_cells | https://celltypist.cog.sanger.ac.uk/Notebook_demo_data/demo_2000_cells.h5ad | 35730948 | True | 2026-09-06T22:18:16+00:00` | `work/dominguezconde-2022-celltypist/provenance.json` entry `id: demo_cells`, keys `uri`, `bytes` = 35730948, `verified` = true, `fetched_at` = `"2026-09-06T22:18:16+00:00"`, with `sha256_expected` = `sha256_actual` = `167d038d57bc7aee2854f12c3337cc1f58846f4ae7382745639a0957831bae9b`, matching manifest `data[0].sha256` and `data[0].size_bytes: 35730948`. Accepted. |
| Provenance row `model_immune_all_low_v2 | …/models/Pan_Immune_CellTypist/v2/Immune_All_Low.pkl | 2824990 | True | 2026-09-06T22:18:17+00:00` | `provenance.json` entry `id: model_immune_all_low_v2`, keys `uri`, `bytes` = 2824990, `verified` = true, `fetched_at`, `sha256_expected` = `sha256_actual` = `290874d35dac039d4c9218c343fde4aac1077709b72a331ce7266f6828c36502`, matching manifest `data[1].sha256` and `data[1].size_bytes: 2824990`. Accepted. |
| Deviations bullet 1, including the dates `2026-03-16`, `2025-06-25` and the approval date `2026-09-06` | `report.json` `deviations[0].what` / `.why` / `.approved_by` / `.date`, copied verbatim from manifest `deviations[0]`. The `2026-03-16` and `2025-06-25` dates originate in manifest `environment.notes` and `code[0]` comment. Accepted as traced text; see finding 3 on the approver string. |
| Deviations bullet 2, including `fe357564a6625d3b1732a022fd39f18e55696e80` and `579 bytes` | `report.json` `deviations[1].what` / `.why` / `.approved_by` / `.date`, copied verbatim from manifest `deviations[1]`; the `579 bytes` figure originates in manifest `environment.notes` and `selection.C3.justification`. Accepted as traced text; see finding 3. |
| `- Wall time: 0.133 min` | `report.json` key `cost.wall_minutes` = 0.133, computed by `harness/diff_claims.py` from `run_log.json` keys `started_at` = `"2026-09-06T22:18:17+00:00"` and `finished_at` = `"2026-09-06T22:18:25+00:00"`. Accepted; see finding 5 for the related stage figure. |
| `- Agent tokens: 0` and `- Estimated cost: USD 0.0` | `report.json` keys `cost.agent_tokens` = 0 and `cost.usd_estimate` = 0.0. Accepted; see finding 6. |

No sentence in `report.md` carries a number, verdict, version, hash or date that I could not trace. No number is rounded or restated differently from its source.

## Rule 3 — tolerances against the manifest

Accepted. `report.json` `claims[0..3].tolerance` are `0, 0, 0, 0` and `claims[0..3].tolerance_type` are `absolute, absolute, absolute, absolute`; `targets/dominguezconde-2022-celltypist/repro-target.yaml` `claims[0..3].tolerance` are `0, 0, 0, 0` and `claims[0..3].tolerance_type` are `absolute, absolute, absolute, absolute`. Unchanged, all four. The `metric` field is the `harness.claim_keys` value (`T1: T1_n_cell_types`, `T2: T2_n_features`, `T3: T3_n_features_used`, `T4: T4_n_genes_input`) rather than the manifest's prose `metric`, which is the documented mapping in `harness/README.md` stage 5; treated as unchanged. See finding 1.

## Rule 4 — cause categories

Not applicable and correctly so. No claim in `report.json` has `verdict` = `not_reproduced`; all four carry `cause_category` = `"n/a"`. No `undiagnosed` claim exists, so the report has nothing to say in that word.

## Rule 5 — digitized extraction

Not applicable. `repro-target.yaml` `claims[0..3].extraction` are all `manual`; `report.json` `claims[*].extraction` are all `"manual"`, and the report.md per-claim table's extraction column reads `manual` on all four rows. No claim is digitized.

## Rule 7 — manifest predates the run

Accepted. `git log -1 --format=%cI -- targets/dominguezconde-2022-celltypist/repro-target.yaml` returns `2026-09-06T18:11:10-04:00`, i.e. `2026-09-06T22:11:10Z`. The mtime of `work/dominguezconde-2022-celltypist/results.json` is `2026-09-06 22:18:25.752342+00:00`, and `report.json` key `generated_at` is `2026-09-06T22:18:26+00:00`. The manifest commit precedes the results file by 7 min 15 s and `generated_at` by 7 min 16 s. `targets/dominguezconde-2022-celltypist/Dockerfile`, `run.sh` and `extract_results.py` share the same commit timestamp `2026-09-06T18:11:10-04:00`; `env-resolved.txt` is older, `2026-09-06T17:25:25-04:00`. All four claims, their values and their tolerances are inside the commit that predates the run. No block finding under rule 7.

## Rule 8 — paper-level verdict

Accepted. All four entries of `report.json` `claims[]` have `verdict` = `"reproduced"`, so `verdict` = `"reproduced"` is the required value; `report.md` `## Summary verdict: **reproduced**` agrees.

## Rule 6 — deviations, including the `extract_results.py` question

Both manifest entries are present with a non-empty `approved_by`: `report.json` `deviations[0].approved_by` and `deviations[1].approved_by` = `"maintainer (recorded post-run; neither change touches the paper's code)"`, `date` = `"2026-09-06"`, and both are rendered in report.md's Deviations log. Searching `work/dominguezconde-2022-celltypist/logs/container_run.log` for steps not listed in the manifest turns up the following, addressed in the findings below.

---

## Findings

### Finding 1 — `extract_results.py` is not a deviation requiring a ledger entry
**Severity: note.**
**Field:** the post-annotate step visible in `work/dominguezconde-2022-celltypist/logs/container_run.log` as `== extract_results.py (repro-lab's own script; public API and this run's own log)`.
**Expected:** either a `deviations[]` entry in `targets/dominguezconde-2022-celltypist/repro-target.yaml`, or documentation showing the step does not alter the paper's method.
**Found:** documentation, and the step does not alter the method. `repro-target.yaml` `results:` comment states "run.sh's last step is extract_results.py (repro-lab's own script, not the paper's code): it reads the model through celltypist's public API for T1 and T2 and parses annotate.log for the two numbers the stage itself printed (T3, T4), and writes them to results.csv. No value is retyped." `targets/dominguezconde-2022-celltypist/run.sh` matches: the final `python /work/extract_results.py --model … --annotate-log /work/out/annotate.log --out /work/out/results.csv`. Reading `targets/dominguezconde-2022-celltypist/extract_results.py`, T3 and T4 are regex captures out of the annotate stage's own stdout (`re.search(r"(\d+) features used for prediction", log)` and `re.search(r"Input data has \d+ cells and (\d+) genes", log)`), and T1 and T2 are `len(m.cell_types)` and `len(m.features)` on `celltypist.models.Model.load(a.model)` — the library's public API against the hash-verified model file in `provenance.json` `id: model_immune_all_low_v2`. It runs after the annotate stage and writes only `out/…/results.csv`; the clone is unmodified, evidenced by the log's closing `== git status --porcelain inside the clone after the run (empty means untouched):` followed by no output. My finding: this is a read-out of the run, not a change to the paper's procedure under `docs/CONVENTIONS.md` line "Every departure from the paper's own stated procedure", and it does not need a `deviations[]` entry. It is disclosed in the manifest and in `run.sh`. No action.

### Finding 2 — one step in the container log is not described anywhere in the manifest
**Severity: note.**
**Field:** the log line `model cell_types 98 | model features 6639` in `work/dominguezconde-2022-celltypist/logs/container_run.log`.
**Expected:** for every step in the log, a description in `repro-target.yaml` (`stages[]`, `harness.stages[]`, or the `results:` comment).
**Found:** `repro-target.yaml` `stages[]` lists only the `annotate` stage `cmd`, and the `results:` comment describes only `extract_results.py`. The line comes from a separate in-container probe in `run.sh` — `python -c "import celltypist; m=celltypist.models.Model.load('/work/data/celltypist/Immune_All_Low.pkl'); print('model cell_types', len(m.cell_types), '| model features', len(m.features))"` — documented only by `run.sh`'s own inline comment ("repro-lab's own read-only probe of the model file, so that T1 (cell types) and T2 (features) are derivable from this run's stdout rather than a post-run check"). It is read-only and its numbers agree with `results.json` `metrics.T1_n_cell_types` = 98 and `metrics.T2_n_features` = 6639, so no number is affected. Suggest the manifest's `results:` comment name this probe alongside `extract_results.py` so that every line of the log maps to the manifest without opening `run.sh`.

### Finding 3 — the deviations' `approved_by` names no person and contradicts the manifest's own commit time
**Severity: fix.**
**Field:** report.md Deviations log, "approved by maintainer (recorded post-run; neither change touches the paper's code), 2026-09-06", both bullets.
**Expected:** `repro-target.yaml` `deviations[].approved_by` identifying who approved, consistent with `docs/CONVENTIONS.md`, which requires the deviation to be "logged in `deviations[]` with `approved_by` before the run proceeds".
**Found:** `deviations[0].approved_by` and `deviations[1].approved_by` are both the string `"maintainer (recorded post-run; neither change touches the paper's code)"`. Two problems for a public reader. First, "maintainer" is unqualified, and both deviations concern the celltypist repository, so it can be read as the upstream celltypist maintainer having approved; nothing in the repository records contact with them — `repro-target.yaml` `selection.C6.justification` records only that `ChuanXu1 (COLLABORATOR)` replies to GitHub issues. Second, "recorded post-run" sits against rule 7's evidence that the entries were committed at `2026-09-06T22:11:10Z`, before the run at `22:18:25Z`, and against the `docs/CONVENTIONS.md` requirement that approval precede the run. Fix by naming the approving role unambiguously (this repository's maintainer) and by stating the timing in terms that match the commit record.

### Finding 4 — "every pinned component matched" overstates what is pinned
**Severity: note.**
**Field:** report.md `## Environment delta` → "None: every pinned component matched."
**Expected:** wording consistent with `repro-target.yaml` `deviations[1].why`, which states "Dependency versions remain unpinned, as the project leaves them", and `environment.notes`, which records "requirements.txt (126 bytes) is eight open lower bounds".
**Found:** the sentence is generated verbatim by `harness/render_report.py` whenever `report.json` `environment_delta` is `[]`, and the underlying fact is correct — `work/dominguezconde-2022-celltypist/env_actual.json` key `delta` = `[]`. But what the empty delta means here is that this run's `pip freeze` matched `targets/dominguezconde-2022-celltypist/env-resolved.txt`, a file this repository generated from its own earlier build of the same Dockerfile (`git log -1` on it returns `2026-09-06T17:25:25-04:00`, 53 minutes before the run), not that the project pins those versions. The base image and the code SHA are genuinely pinned (`env_actual.json` `base_image` = `python@sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b`, matching the `FROM` line in `targets/dominguezconde-2022-celltypist/Dockerfile`; `run_log.json` `code_sha` matching manifest `code[0].commit`); the 51 dependency versions in `env-resolved.txt`, among them `scikit-learn==1.6.1`, are a captured resolution, not a pin. Since this is harness-wide phrasing in `render_report.py`, it is a note rather than a fix on this report, but a reader of the published report.md alone will draw a stronger conclusion than the evidence supports.

### Finding 5 — the report's wall time is the harness-level interval, not the stage duration
**Severity: note.**
**Field:** report.md "- Wall time: 0.133 min".
**Expected:** a wall-time figure traceable to `work/dominguezconde-2022-celltypist/run_log.json`.
**Found:** traceable, and accepted. `report.json` `cost.wall_minutes` = 0.133 is `harness/diff_claims.py`'s `round((t1 - t0).total_seconds() / 60, 3)` over `run_log.json` `started_at` = `"2026-09-06T22:18:17+00:00"` and `finished_at` = `"2026-09-06T22:18:25+00:00"`, both second-truncated. The stage's own measured duration is `run_log.json` `stages[0].seconds` = 8.16, which is 0.136 min. The two differ only by the truncation of the ISO timestamps and no rule is broken; recorded so a reader comparing 0.133 against the `exit 0 in 8.16 s` line in `reports/dominguezconde-2022-celltypist/run_transcript.txt` is not left guessing.

### Finding 6 — the zero token and dollar figures are unexplained in the published report
**Severity: note.**
**Field:** report.md "- Agent tokens: 0" and "- Estimated cost: USD 0.0".
**Expected:** the reading given in `harness/README.md` under "Cost": "Token and dollar counts are zero: these runs were driven from a terminal, and no wrapper was in place to count them. A zero here means 'not measured by an agent wrapper', not 'free'."
**Found:** both values trace to `report.json` `cost.agent_tokens` = 0 and `cost.usd_estimate` = 0.0, set as literals by `harness/diff_claims.py` with the inline comment "filled in by the agent wrapper when one is used". The clarification exists only in `harness/README.md`; report.md carries the bare zeros. A reader of the report alone can take them as measurements.

### Finding 7 — report.md omits the manifest's `status: candidate` and its scope caveat
**Severity: note.**
**Field:** report.md header block (DOI, Code, Generated).
**Expected:** some signal of `repro-target.yaml` key `status: candidate` and of the manifest's `notes`, which state plainly that "The C1=2 above is earned by the PAPER's deposited data — ArrayExpress E-MTAB-11536 and Zenodo 10.5281/zenodo.6334988. This reproduction does not use either", and "Why this is a candidate and not selected: C4 is 1. The claims above are real and checkable, but they are model and data shapes, not the paper's scientific results".
**Found:** neither appears in report.md, which `harness/render_report.py` builds from `report.json` alone; `report.json` has no field for either. The verdict "reproduced" is correct under rule 8 and is properly scoped to the four claims in `claims[]`, but the published report does not tell a reader that those four claims are artefact shapes rather than the paper's scientific findings. Relatedly, the report.md per-claim table's `metric` column shows the `harness.claim_keys` values (`T1_n_cell_types`, `T2_n_features`, `T3_n_features_used`, `T4_n_genes_input`) rather than the manifest's prose `metric` strings such as `n_cell_types in model Immune_All_Low.pkl v2` — the documented mapping, but it removes the last in-report hint of what is being counted. Also worth recording for the reader: T1 and T2 are read from the model file by the probe of finding 2 and by `extract_results.py`, not produced by the annotate stage, so "reproduced" for those two means the pinned model artefact has the shape the notebook printed; only T3 and T4 come from the annotate run's own output.

### Finding 8 — `checkpoints.md` is missing from this report directory
**Severity: fix.**
**Field:** `reports/dominguezconde-2022-celltypist/`.
**Expected:** per `reports/README.md` ("`checkpoints.md` (transcripts of the harness checkpoints firing, on a scratch copy)") and `docs/CONVENTIONS.md` ("`reports/<slug>/` holds `report.json`, `report.md`, `checkpoints.md` and `review.md`"), a `checkpoints.md` in each report directory.
**Found:** `reports/dominguezconde-2022-celltypist/` contains `report.json`, `report.md`, `container_run.log`, `fresh_clone.md` and `run_transcript.txt` — no `checkpoints.md`. `reports/muzellec-2023-pydeseq2/` does contain one. The four checkpoints named in `docs/CONVENTIONS.md` are all no-ops on this target (`checkpoints.max_download_gb: 5` against a 38,555,938-byte total fetch, `max_stage_minutes: 60` against `harness.stages[0].expected_minutes: 2`, both `deviations[].approved_by` non-empty, and all four claims in tolerance), so nothing fired and nothing is being concealed; the file is still required by two documents in the repository. Add it, or state in it that no checkpoint fired on this target and why.

### Tone check
The report.md text passes. It contains no statement that the paper or the authors' results are wrong, no speculation about the authors' intent, and no adjective about the paper's quality. `harness/render_report.py`'s "Human review required" section, which carries the mandated "we could not obtain X … the closest we reached was Z" phrasing, is absent from this report because no claim is flagged, which is correct. The deviations text describes changes to this repository's own fetch and install steps and says so ("No file under the clone is touched; only our fetch step changes").

### Supporting checks
`reports/dominguezconde-2022-celltypist/container_run.log` is byte-identical to `work/dominguezconde-2022-celltypist/logs/container_run.log`. `reports/dominguezconde-2022-celltypist/run_transcript.txt` matches the evidence files on every value it prints: image id `sha256:866b1ca53427a3f2eeb969372dc15235fb055755fea053e0553a872b4ecebb5d` and base `python@sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b` against `env_actual.json` keys `image_id` and `base_image`; container python `3.9.25` against `env_actual.json` key `python` and the log's `== python: Python 3.9.25`; `35730948` and `2824990` bytes against `provenance.json`; `8.16 s` against `run_log.json` `stages[0].seconds`; `fe357564a6625d3b1732a022fd39f18e55696e80` against `run_log.json` `code_sha`; `4/4 claims within tolerance -> verdict: reproduced` against `report.json` `verdict`. `reports/dominguezconde-2022-celltypist/fresh_clone.md` records a fresh-clone regeneration at HEAD `ee4c0b2` whose masked `report.md` and normalised `report.json` diffs are empty.

Zero "block" findings: two "fix" (findings 3 and 8) and six "note".

APPROVED

---

Executor's disposition of the two "fix" findings, recorded here rather than argued away: finding 8 is closed by `checkpoints.md` in this directory, which states that no checkpoint fired on this target and why. Finding 3 concerns the manifest's `approved_by` string, which is a pre-run manifest value; changing it after the run would itself be a post-run manifest edit, so it is left as committed and the finding stands as recorded.
