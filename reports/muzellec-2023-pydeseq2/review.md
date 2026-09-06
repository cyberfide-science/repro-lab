# Reviewer findings: `muzellec-2023-pydeseq2` (round 1)

Provenance: run by an independent reviewer agent, not the author of the
harness, on 2026-09-06 against base-repo commit `d0860b1` (repro-lab reports
at `f854529`). The reviewer prompt applied is `harness/prompts/reviewer.md`,
rule by rule, with the path mapping in `harness/README.md` ("The prompts").
The report was regenerated in a fresh clone (`py -3 run_all.py
muzellec-2023-pydeseq2`, exit 0, `HARNESS_APPROVE` unset, no checkpoint
fired) and the masked `report.md` / normalised `report.json` diffs against
the committed files were empty. Checkpoint demonstrations 5 and 6 were re-run
on a scratch manifest with byte-identical output; the extra negative path
(stage command replaced so no `== git HEAD:` line is emitted) exited 1 with
"cannot record code_sha, stopping" and left `report.json` unchanged;
`harness/schema/test_negative.py reports/muzellec-2023-pydeseq2/report.json`
exited 0 with the output recorded in `checkpoints.md`.

## Rule 1 / rule 2 trace

M = `targets/muzellec-2023-pydeseq2/repro-target.yaml`, W = `work/muzellec-2023-pydeseq2/`.

| md line | Statement | Traces to (file -> key) | |
|---|---|---|---|
| 1 | title "PyDESeq2: a python package ..." | report.json paper.title <- M paper.title | accept |
| 3 | DOI 10.1093/bioinformatics/btad547 | report.json paper.doi <- M paper.doi | accept |
| 4 | Code 4426e4db990db1c511de3b1b9b7a514989663dad | report.json paper.code_sha <- W run_log.json code_sha <- W logs/container_run.log:1 `== git HEAD: 4426e4db...`; equals M code[0].commit | accept |
| 5 | Generated 2026-09-06T22:18:04+00:00 | report.json generated_at | accept |
| 7 | Summary verdict reproduced | report.json verdict | accept (rule 8) |
| 9 | "4 of 4 claims within tolerance." | report.json claims[] length 4, all reproduced; both numerals computed at harness/render_report.py:22-23 | accept, note N-1 |
| 15 | P1 claimed 0.632812315254828 | claims[0].claimed <- M claims[P1].value | accept |
| 15 | P1 obtained 0.632812476644658 | claims[0].obtained <- W results.json metrics.P1_log2FoldChange_gene1 <- out/muzellec-2023-pydeseq2/results.csv row 2 <- W logs/container_run.log:21 | accept |
| 15 | P1 metric P1_log2FoldChange_gene1 | M harness.claim_keys.P1 (mapping documented harness/README.md stage 5) | accept |
| 15 | P1 relative 0.02 | claims[0].tolerance/tolerance_type <- M claims[P1] | accept |
| 15 | P1 reproduced / n/a / manual | claims[0].verdict/cause_category/extraction <- M claims[P1].extraction | accept |
| 16 | P2 claimed -2.78368 | claims[1].claimed <- M claims[P2].value -2.783680 (numerically equal; JSON float serialisation) | accept, note N-2 |
| 16 | P2 obtained -2.783684562340294 | W results.json metrics.P2_log10_padj_gene2 <- results.csv row 3 <- container_run.log:22; log10 taken inside the container by targets/muzellec-2023-pydeseq2/extract_results.py:39, committed 3ada983 (2026-09-06T17:25:25-04:00), before the 22:17:06Z run | accept |
| 16 | P2 absolute 0.3 | claims[1] <- M claims[P2] | accept |
| 17 | P3 claimed 1.22898093726827 / obtained 1.228980937268269 | claims[2].claimed <- M claims[P3].value; obtained <- W results.json metrics.P3_size_factor_sample1 <- results.csv row 4 <- container_run.log:23 | accept |
| 17 | P3 relative 0.02 | claims[2] <- M claims[P3] | accept |
| 18 | P4 claimed ['gene5', 'gene2', 'gene4'] | claims[3].claimed <- M claims[P4].value; rendered as a Python list repr | accept, note N-3 |
| 18 | P4 obtained gene5;gene2;gene4 | W results.json metrics.P4_top3_genes_by_abs_stat <- results.csv row 5 <- container_run.log:24 | accept |
| 18 | P4 rank_order 0 | claims[3].tolerance 0 <- M claims[P4].tolerance 0; tolerance_type rank-order -> rank_order, the one documented mapping | accept |
| 22 | "None: every pinned component matched." | report.json environment_delta [] <- W env_actual.json delta [] | accept, note N-4 |
| 28 | synthetic_counts 3919 True 2026-09-06T22:17:05+00:00 | report.json data_provenance[0] <- W provenance.json[0]; sha256 09d632cc...37c3 = M data[0].sha256; bytes = M data[0].size_bytes | accept |
| 29 | synthetic_metadata 1915 True | data_provenance[1] <- W provenance.json[1]; d96a5bbf...f0b6 = M data[1].sha256; 1915 = M data[1].size_bytes | accept |
| 33 | Deviations log None. | report.json deviations [] <- M deviations [] | accept |
| 37 | Wall time 0.95 min | report.json cost.wall_minutes from W run_log.json started_at 22:17:06 / finished_at 22:18:03 (stages[0].seconds 56.99) | accept |
| 38-39 | Agent tokens 0, Estimated cost USD 0.0 | cost.agent_tokens, cost.usd_estimate; meaning only in harness/README.md "Cost" | accept, note N-5 |

Rejected sentences: none. Every numeric token in report.md occurs in
report.json (zero misses), with the caveat that "4 of 4" occurs only as a
substring (N-1).

## Rules 3-8

- Rule 3 pass. All four claims: tolerance identical (0.02 / 0.3 / 0.02 / 0), tolerance_type identical except rank-order -> rank_order for P4, claimed == M value. harness/diff_claims.py:35 implements exactly that substitution and rejects any other value.
- Rule 4 vacuous, correctly (no not_reproduced claim; all cause_category n/a, enforced by the schema conditional).
- Rule 5 vacuous (all extraction manual, rendered in the extraction column).
- Rule 6 pass. container_run.log: git rev-parse HEAD (1), python --version (2), pytest tests/ (3-5, = M stages[reference_suite]), extract_results.py (6-24, = M stages[extract]), cat results.csv (20-24), git status --porcelain (25). Only two are method steps and both are in the manifest. deviations [] is correct.
- Rule 7 pass. Manifest last commit 2026-09-06T18:11:10-04:00 = 22:11:10Z; results.json mtime 22:18:03.801Z; generated_at 22:18:04Z. git diff c53d9ca HEAD -- targets/ is empty.
- Rule 8 pass. 4/4 -> reproduced.
- Tone pass. No prohibited phrasing; the renderer can only emit the permitted discrepancy form (render_report.py:44-46), verified in demo 6.

## Findings that concern this report

F-2 — fix. work/<slug>/run_log.json records an absolute host path. harness/run_pipeline.py:45 substitutes {repo_root} with the absolute root and :49 stores the substituted argv, while every path recorded in an evidence file should be repository-relative. Mitigation: work/ is gitignored; committed transcripts redact it. Fix: store the argv with {repo_root} unsubstituted.

F-3 — fix. On the "no == git HEAD:" abort, run_pipeline.py:59-63 exits before writing run_log.json but :51 has already overwritten logs/<stage>.log, leaving work/ holding two different runs (reproduced live). Fix: write run_log.json (code_sha null) before the SHA check, as the non-zero-return branch at :55 does.

N-1 — note. "4 of 4 claims within tolerance." is computed by the renderer (render_report.py:22-23); harness/README.md:70 and render_report.py:3-4 claim nothing is computed. The report template itself mandates the count, so the renderer is right; the documentation is wrong.

N-2 — note. P2 claimed -2.78368 vs manifest -2.783680; numerically identical.

N-3 — note. P4 claimed renders as a Python list literal while obtained uses the results-file form gene5;gene2;gene4.

N-4 — note. "None: every pinned component matched." is broader than the evidence: environment.python 3.11 is a floor, and the version run (3.12.14) appears nowhere in report.md.

N-5 — note. Agent tokens 0 / USD 0.0 unqualified in report.md; the reading "not measured" exists only in harness/README.md.

N-8 — note, correcting the earlier review.md in this directory: run_pipeline.py:51 writes stdout then stderr, concatenated; the git status line is the last stdout line and produced no output, so the clone was untouched and the log proves it.

Zero "block" findings.

APPROVED (reports/muzellec-2023-pydeseq2)
