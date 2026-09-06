# Reviewer findings: `dominguezconde-2022-celltypist` (round 1)

Provenance: run by an independent reviewer agent, not the author of the
harness, on 2026-09-06 against base-repo commit `d0860b1` (repro-lab reports
at `f854529`). The reviewer prompt applied is `harness/prompts/reviewer.md`,
rule by rule, with the path mapping in `harness/README.md` ("The prompts").
The report was regenerated in a fresh clone (`py -3 run_all.py
dominguezconde-2022-celltypist`, exit 0, `HARNESS_APPROVE` unset, no
checkpoint fired) and the masked `report.md` / normalised `report.json` diffs
against the committed files were empty. Removing
`out/dominguezconde-2022-celltypist/results.csv` and re-running
`harness/run_pipeline.py` regenerated the file from the container with
identical content. Both manifest deviations carry a non-empty `approved_by`;
`run_pipeline.py:36-38` refuses to start without one (re-verified live).
`harness/schema/test_negative.py reports/dominguezconde-2022-celltypist/report.json`
exited 0 with the output recorded in `checkpoints.md`.

## Rule 1 / rule 2 trace

M = `targets/dominguezconde-2022-celltypist/repro-target.yaml`, W = `work/dominguezconde-2022-celltypist/`.

| md line | Statement | Traces to | |
|---|---|---|---|
| 1 | title "Cross-tissue immune cell analysis ..." | report.json paper.title <- M paper.title | accept |
| 3 | DOI 10.1126/science.abl5197 | paper.doi <- M paper.doi | accept |
| 4 | Code fe357564a6625d3b1732a022fd39f18e55696e80 | paper.code_sha <- W run_log.json code_sha <- W logs/container_run.log:1; equals M code[0].commit | accept |
| 5 | Generated 2026-09-06T22:18:26+00:00 | generated_at | accept |
| 7 | Summary verdict reproduced | verdict | accept |
| 9 | "4 of 4 claims within tolerance." | claims[] length 4, all reproduced; computed at render_report.py:22 | accept, note N-1 |
| 15 | T1 98 / 98 / absolute 0 / manual | M claims[T1].value 98; W results.json metrics.T1_n_cell_types; out/.../results.csv row 2; container_run.log:45; also printed at container_run.log:4 by the in-container model probe | accept |
| 16 | T2 6639 / 6639 | M claims[T2].value; metrics.T2_n_features; results.csv row 3; container_run.log:4,46 | accept |
| 17 | T3 5645 / 5645 | M claims[T3].value; metrics.T3_n_features_used; results.csv row 4; container_run.log:33 "5645 features used for prediction" | accept |
| 18 | T4 18950 / 18950 | M claims[T4].value; metrics.T4_n_genes_input; results.csv row 5; container_run.log:31 "Input data has 2000 cells and 18950 genes" | accept |
| 15-18 | absolute 0 x4 | claims[0..3].tolerance/tolerance_type <- M claims[T1..T4] identical | accept |
| 22 | "None: every pinned component matched." | environment_delta [] <- W env_actual.json delta [] (base python@sha256:2d97f691..., container python 3.9.25) | accept, note N-4 |
| 28 | demo_cells 35730948 True 22:18:16Z | data_provenance[0] <- W provenance.json[0]; 167d038d...ae9b = M data[0].sha256; bytes = M data[0].size_bytes | accept |
| 29 | model_immune_all_low_v2 2824990 True 22:18:17Z | data_provenance[1] <- W provenance.json[1]; 290874d3...6502 = M data[1].sha256 | accept |
| 33-35 | deviation 1 incl. URL, 2026-03-16, 2025-06-25, approval date 2026-09-06 | report.json deviations[0] copied verbatim from M deviations[0]; dates originate in M environment.notes and the M code[0] comment | accept as traced text; fix F-1 |
| 36-38 | deviation 2 incl. pinned SHA and 579 bytes | deviations[1] <- M deviations[1]; 579 bytes originates in M environment.notes / M selection.C3.justification | accept as traced text; fix F-1 |
| 42 | Wall time 0.133 min | cost.wall_minutes from W run_log.json started_at 22:18:17 / finished_at 22:18:25 | accept |
| 43-44 | Agent tokens 0, USD 0.0 | cost.agent_tokens, cost.usd_estimate | accept, note N-5 |

Rejected sentences: none. Numeric-token check: zero misses.

## Rules 3-8

- Rule 3 pass. All four tolerance 0 / absolute in both files; claimed == M value.
- Rule 4 / 5 vacuous and correct.
- Rule 6 pass with two notes. container_run.log contains: (a) line 3 dependency-version echo; (b) line 4 `model cell_types 98 | model features 6639`, an in-container probe defined only in targets/.../run.sh:11, named in neither M stages[] nor M results: (note N-6); (c) lines 37-42 ls -l /work/out; (d) line 43 extract_results.py, described in M results:; (e) line 49 git status --porcelain, emits nothing -> clone untouched. None alters the paper's method. Both manifest deviations carry a non-empty approved_by; run_pipeline.py:36-38 refuses to start without one (re-verified live).
- Rule 7 pass. Manifest commit 22:11:10Z; results.json mtime 22:18:25.752Z; generated_at 22:18:26Z. Dockerfile, run.sh and extract_results.py are in the same c53d9ca commit; harness/ frozen at ee4c0b2 = 22:16:49Z.
- Rule 8 pass. 4/4 -> reproduced.
- Tone pass.

## Findings that concern this report

F-1 — fix. Deviations: approved_by names no person and self-describes as post-run. report.md lines 35 and 38; report.json deviations[0..1].approved_by = "maintainer (recorded post-run; ...)". "maintainer" is unqualified and both deviations concern the celltypist repository, so it reads as though upstream approved; "recorded post-run" contradicts the rule-7 evidence (committed 22:11:10Z, run 22:18:17Z). Fix: manifest correction under a fresh pre-run commit before the next run of this target, not a rewording of the report.

F-2 — fix. work/<slug>/run_log.json records an absolute host path. harness/run_pipeline.py:45 substitutes {repo_root} with the absolute root and :49 stores the substituted argv, while every path recorded in an evidence file should be repository-relative. Mitigation: work/ is gitignored; committed transcripts redact it. Fix: store the argv with {repo_root} unsubstituted.

F-3 — fix. On the "no == git HEAD:" abort, run_pipeline.py:59-63 exits before writing run_log.json but :51 has already overwritten logs/<stage>.log, leaving work/ holding two different runs (reproduced live). Fix: write run_log.json (code_sha null) before the SHA check, as the non-zero-return branch at :55 does.

N-1 — note. "4 of 4 claims within tolerance." is computed by the renderer (render_report.py:22-23); harness/README.md:70 and render_report.py:3-4 claim nothing is computed. The report template itself mandates the count, so the renderer is right; the documentation is wrong.

N-4 — note. "None: every pinned component matched." is broader than the evidence: the empty delta means this run matched env-resolved.txt generated 53 minutes earlier, not that the project pins anything.

N-5 — note. Agent tokens 0 / USD 0.0 unqualified in report.md; the reading "not measured" exists only in harness/README.md.

N-6 — note. The model-shape probe (run.sh:11) appears in the container log but in no manifest field. T1 and T2 are properties of the pinned model file, not outputs of the annotate stage.

N-7 — note. report.md carries no signal of M status: candidate nor of the manifest note that the claims are model and data shapes, not the paper's scientific results.

Zero "block" findings.

APPROVED (reports/dominguezconde-2022-celltypist)
