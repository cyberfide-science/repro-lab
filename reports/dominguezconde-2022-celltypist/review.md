# Reviewer findings: `dominguezconde-2022-celltypist`

Provenance: independent adversarial review, round 3, run by a reviewer agent
that did not build the harness and did not write the round-1 or round-2
reviews, on 2026-09-06 against base-repo commit `100d605` (this report was
generated at 053b797 and is unchanged at HEAD). Brief applied:
`harness/prompts/reviewer.md`, rule by rule. `HARNESS_APPROVE` unset; no
checkpoint fired. The reviewer has no write access and edited nothing. The
full round-3 text, including the harness findings and the REQ table, is
`unit2/docs/reviews/unit2-review-3.md` in the base repository.

M = `targets/dominguezconde-2022-celltypist/repro-target.yaml`,
W = `work/dominguezconde-2022-celltypist/`,
R = `reports/dominguezconde-2022-celltypist/report.json`.

## Rule 1 / rule 2 — every number, verdict, version, hash and date

| md line | Statement | Traces to (file → key) | |
|---|---|---|---|
| 1 | title "Cross-tissue immune cell analysis reveals tissue-specific features in humans" | R `paper.title` ← M `paper.title` | accept |
| 3 | DOI 10.1126/science.abl5197 | R `paper.doi` ← M `paper.doi` | accept |
| 4 | Code `fe357564a6625d3b1732a022fd39f18e55696e80` | R `paper.code_sha` ← W `run_log.json` `code_sha` ← W `logs/container_run.log:1`; equals M `code[0].commit` | accept |
| 5 | Generated 2026-09-06T23:12:28.284+00:00 | R `generated_at` | accept |
| 7 | Summary verdict **reproduced** | R `verdict` (rule 8) | accept |
| 9 | "4 of 4 claims within tolerance." | R `claims[]` length 4, all `reproduced`; counted at `render_report.py:20-21` | accept, note N-1 (declared exemption) |
| 15 | T1 98 / 98, absolute 0, manual | claimed ← M `claims[T1].value`; obtained ← W `results.json` `metrics.T1_n_cell_types` ← `out/dominguezconde-2022-celltypist/results.csv` row 2 ← `container_run.log:46`; independently printed at `container_run.log:4` by the declared model probe | accept |
| 16 | T2 6639 / 6639 | claimed ← M `claims[T2].value`; obtained ← `metrics.T2_n_features` ← `results.csv` row 3 ← `container_run.log:4,47` | accept |
| 17 | T3 5645 / 5645 | claimed ← M `claims[T3].value`; obtained ← `metrics.T3_n_features_used` ← `results.csv` row 4 ← `container_run.log:33` "5645 features used for prediction" | accept |
| 18 | T4 18950 / 18950 | claimed ← M `claims[T4].value`; obtained ← `metrics.T4_n_genes_input` ← `results.csv` row 5 ← `container_run.log:31` "Input data has 2000 cells and 18950 genes" | accept |
| 15-18 | absolute 0 ×4 | R `claims[0..3].tolerance` / `tolerance_type` ← M `claims[T1..T4]`, identical | accept |
| 15-18 | reproduced / n/a / manual ×4 | R `claims[].verdict` / `cause_category` / `extraction` ← M `claims[].extraction` | accept |
| 22 | "None: every pinned component matched." | R `environment_delta` [] ← W `env_actual.json` `delta` [] (image id `sha256:866b1ca5…`, base `python@sha256:2d97f691…`, container python 3.9.25) | accept, note N-4 |
| 28 | demo_cells, 35730948 bytes, True, 2026-09-06T23:12:19.653+00:00 | R `data_provenance[0]` ← W `provenance.json[0]`; `sha256_actual` = `sha256_expected` = M `data[0].sha256` 167d038d…ae9b; bytes = M `data[0].size_bytes` | accept |
| 29 | model_immune_all_low_v2, 2824990 bytes, True, 2026-09-06T23:12:20.780+00:00 | R `data_provenance[1]` ← W `provenance.json[1]`; 290874d3…6502 = M `data[1].sha256` | accept |
| 33-35 | deviation 1: the versioned model URL, `models.json` last-modified 2026-03-16, code frozen 2025-06-25, approver "Michael Wolfe, repro-lab maintainer (not the celltypist authors; approved 2026-09-06 before the harness run; neither change touches the paper's code)", date 2026-09-06 | R `deviations[0]` copied verbatim from M `deviations[0]`; the two dates originate in M `environment.notes` and the M `code[0]` comment | accept; F-1 **closed** |
| 36-38 | deviation 2: install from the pinned clone rather than `pip install celltypist`, Dockerfile 579 bytes at fe357564, same approver, date 2026-09-06 | R `deviations[1]` ← M `deviations[1]`; 579 bytes originates in M `environment.notes` / M `selection.C3.justification` | accept; F-1 **closed** |
| 42 | Wall time 0.133 min | R `cost.wall_minutes` from W `run_log.json` `started_at` 23:12:20Z / `finished_at` 23:12:28Z (`stages[0].seconds` 7.19) | accept, note N3-7 |
| 43-44 | Agent tokens 0, Estimated cost USD 0.0 | R `cost.agent_tokens`, `cost.usd_estimate` | accept, note N-5 |

Rejected sentences: **none**. Numeric-token check: all 40 distinct numeric
tokens in `report.md` occur verbatim in `report.json`; zero misses.

## Rules 3-8

- **Rule 3 — PASS.** All four claims are `tolerance: 0`, `tolerance_type:
  absolute` in both M and R, and `claimed` equals M `value` in all four. The
  only change to this manifest since it was first committed is `781720a`
  (the `approved_by` strings and the `results:` comment); `git diff 781720a
  100d605 -- targets/` is empty. No tolerance moved.
- **Rule 4 — vacuous and correct.** No `not_reproduced` claim; all
  `cause_category` are `n/a`.
- **Rule 5 — vacuous.** All four claims are `extraction: manual`, shown in the
  extraction column. No claim is `digitized`.
- **Rule 6 — PASS, with every non-manifest step accounted for.**
  `logs/container_run.log` contains: line 1 `git rev-parse HEAD`; line 2
  `python --version`; line 3 a dependency-version echo; line 4 the model-shape
  probe `model cell_types 98 | model features 6639` — read-only, repro-lab
  owned, and **now declared in M `results:`** (the round-1 note N-6 is closed);
  lines 29-36 the `celltypist` annotate stage = M `stages[annotate]`; lines
  37-43 `ls -l /work/out`; lines 44-49 `extract_results.py`, described in M
  `results:`; line 50 `git status --porcelain` inside the clone, which emits
  nothing, so no file under the clone was edited. No step alters the paper's
  method, and every step that is not the paper's method is either a manifest
  `deviations[]` entry or a declared repro-lab observation. Both manifest
  deviations carry a non-empty `approved_by`; `run_pipeline.py:46-48` refuses
  to start without one, re-verified live.
- **Rule 7 — PASS, strictly, with no precision caveat.** Manifest last commit
  `781720a` **2026-09-06T18:48:40-04:00 = 22:48:40Z** <
  `work/dominguezconde-2022-celltypist/results.json` mtime
  **2026-09-06T23:12:28.058Z** < `generated_at`
  **2026-09-06T23:12:28.284Z** (and `report.json` mtime 23:12:28.285Z). The
  manifest, including the corrected `approved_by` strings, predates the run by
  23 m 48 s. The approval is therefore pre-run in the repository's own record,
  which is what round-1 finding F-1 asked for.
- **Rule 8 — PASS.** 4 of 4 claims `reproduced` → paper-level verdict
  `reproduced`.
- **Tone — PASS.** No "the paper is wrong", no speculation about the authors'
  intent, no adjectives about the paper's quality. The deviation entries
  describe our run's conditions and name our own approver explicitly as not
  being the celltypist authors.

## Regeneration

From a fresh clone of `100d605` with no `data/` and no `work/`,
`py -3 run_all.py dominguezconde-2022-celltypist < /dev/null` exits 0 and the
masked diffs of `report.json` and `report.md` against the committed files
(`generated_at`, `fetched_at`, wall time masked) are **empty**.
`out/dominguezconde-2022-celltypist/results.csv` regenerates byte-identically.

## Findings

Zero **block**. Zero **fix** on this report. F-1 (round 1) is closed: the
manifest was corrected under a fresh pre-run commit, not by rewording the
report. N-6 is closed: the model-shape probe is declared in M `results:`.
Notes carried forward: N-4 (an empty delta means this run matched
`env-resolved.txt`, not that the project pins anything), N-5 (cost zeros
unqualified in `report.md`), N-7 (`report.md` carries no signal of M
`status: candidate` nor of the manifest's note that T1-T4 are model and data
shapes rather than the paper's scientific results — the schema has no scope
field, so this remains a note). New notes: N3-6, the two deviation bullets
render broken across lines because the folded YAML values keep their trailing
newline (`render_report.py:36`) — text is correct, layout only; and N3-5,
`checkpoints.md` in this directory still says `review.md` records F-1, which
this replacement does not — point that sentence at
`unit2/docs/reviews/unit2-review-1.md`. None touches a published value.

APPROVED
