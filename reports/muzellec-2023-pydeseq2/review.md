# Reviewer findings: `muzellec-2023-pydeseq2`

Provenance: independent adversarial review, round 3, run by a reviewer agent
that did not build the harness and did not write the round-1 or round-2
reviews, on 2026-09-06 against base-repo commit `100d605` (this report was
generated at 053b797 and is unchanged at HEAD). Brief applied:
`harness/prompts/reviewer.md`, rule by rule. `HARNESS_APPROVE` unset; no
checkpoint fired. The reviewer has no write access and edited nothing. The
full round-3 text, including the harness findings and the REQ table, is
`unit2/docs/reviews/unit2-review-3.md` in the base repository.

M = `targets/muzellec-2023-pydeseq2/repro-target.yaml`,
W = `work/muzellec-2023-pydeseq2/`, R = `reports/muzellec-2023-pydeseq2/report.json`.

## Rule 1 / rule 2 — every number, verdict, version, hash and date

| md line | Statement | Traces to (file → key) | |
|---|---|---|---|
| 1 | title "PyDESeq2: a python package for bulk RNA-seq differential expression analysis" | R `paper.title` ← M `paper.title` | accept |
| 3 | DOI 10.1093/bioinformatics/btad547 | R `paper.doi` ← M `paper.doi` | accept |
| 4 | Code `4426e4db990db1c511de3b1b9b7a514989663dad` | R `paper.code_sha` ← W `run_log.json` `code_sha` ← W `logs/container_run.log:1` `== git HEAD: 4426e4db…`; equals M `code[0].commit` | accept |
| 5 | Generated 2026-09-06T23:12:11.642+00:00 | R `generated_at` | accept |
| 7 | Summary verdict **reproduced** | R `verdict` (rule 8) | accept |
| 9 | "4 of 4 claims within tolerance." | R `claims[]` length 4, all `reproduced`; the two integers counted at `render_report.py:20-21` | accept, note N-1 (declared exemption in REQ-U2-04) |
| 15 | P1 claimed 0.632812315254828 | R `claims[0].claimed` ← M `claims[P1].value` | accept |
| 15 | P1 obtained 0.632812476644658 | W `results.json` `metrics.P1_log2FoldChange_gene1` ← `out/muzellec-2023-pydeseq2/results.csv` row 2 ← W `logs/container_run.log:21` | accept |
| 15 | P1 metric `P1_log2FoldChange_gene1` | M `harness.claim_keys.P1` (mapping documented `harness/README.md` stage 5) | accept |
| 15 | P1 relative 0.02 | R `claims[0].tolerance` / `tolerance_type` ← M `claims[P1]`, unchanged | accept |
| 15 | P1 reproduced / n/a / manual | R `claims[0].verdict` / `cause_category` / `extraction` ← M `claims[P1].extraction` | accept |
| 16 | P2 claimed -2.78368 | R `claims[1].claimed` ← M `claims[P2].value` -2.783680 (numerically equal; JSON float serialisation) | accept, note N-2 |
| 16 | P2 obtained -2.783684562340294 | W `results.json` `metrics.P2_log10_padj_gene2` ← `results.csv` row 3 ← `container_run.log:22`; the log10 is taken inside the container by `targets/muzellec-2023-pydeseq2/extract_results.py`, committed before the run | accept |
| 16 | P2 absolute 0.3 | R `claims[1]` ← M `claims[P2]` | accept |
| 17 | P3 claimed 1.22898093726827 / obtained 1.228980937268269 | R `claims[2].claimed` ← M `claims[P3].value`; obtained ← W `results.json` `metrics.P3_size_factor_sample1` ← `results.csv` row 4 ← `container_run.log:23` | accept |
| 17 | P3 relative 0.02 | R `claims[2]` ← M `claims[P3]` | accept |
| 18 | P4 claimed ['gene5', 'gene2', 'gene4'] | R `claims[3].claimed` ← M `claims[P4].value`, rendered as a Python list repr | accept, note N-3 |
| 18 | P4 obtained gene5;gene2;gene4 | W `results.json` `metrics.P4_top3_genes_by_abs_stat` ← `results.csv` row 5 ← `container_run.log:24` | accept |
| 18 | P4 rank_order 0 | R `claims[3].tolerance` 0 ← M `claims[P4].tolerance` 0; `rank-order` → `rank_order`, the one documented mapping | accept |
| 22 | "None: every pinned component matched." | R `environment_delta` [] ← W `env_actual.json` `delta` [] (image id `sha256:f2226316…`, base `python@sha256:78387bc3…`, container python 3.12.14) | accept, note N-4 |
| 28 | synthetic_counts, 3919 bytes, True, 2026-09-06T23:11:15.809+00:00 | R `data_provenance[0]` ← W `provenance.json[0]`; `sha256_actual` = `sha256_expected` = M `data[0].sha256` 09d632cc…37c3; bytes = M `data[0].size_bytes` | accept |
| 29 | synthetic_metadata, 1915 bytes, True, 2026-09-06T23:11:15.938+00:00 | R `data_provenance[1]` ← W `provenance.json[1]`; d96a5bbf…f0b6 = M `data[1].sha256`; 1915 = M `data[1].size_bytes` | accept |
| 33 | Deviations log: None. | R `deviations` [] ← M `deviations` [] | accept |
| 37 | Wall time 0.917 min | R `cost.wall_minutes` from W `run_log.json` `started_at` 23:11:16Z / `finished_at` 23:12:11Z (`stages[0].seconds` 55.4) | accept, note N3-7 |
| 38-39 | Agent tokens 0, Estimated cost USD 0.0 | R `cost.agent_tokens`, `cost.usd_estimate`; the reading "not measured by an agent wrapper" is in `harness/README.md` "Cost" | accept, note N-5 |

Rejected sentences: **none**. Numeric-token check: all 39 distinct numeric
tokens in `report.md` occur verbatim in `report.json`; zero misses. Nothing in
`report.md` was recomputed, re-rounded or corrected in prose.

## Rules 3-8

- **Rule 3 — PASS.** All four claims carry the manifest's `tolerance`
  (0.02 / 0.3 / 0.02 / 0) and `tolerance_type` unchanged, the sole substitution
  being the documented `rank-order` → `rank_order` implemented at
  `diff_claims.py:35`, which rejects any other value. `claimed` equals M
  `value` in all four. `git diff c53d9ca 100d605 -- targets/muzellec-2023-pydeseq2/`
  is empty: no tolerance moved after the manifest was committed.
- **Rule 4 — vacuous and correct.** No claim is `not_reproduced`; all
  `cause_category` are `n/a`, which the schema conditional enforces.
- **Rule 5 — vacuous.** All four claims are `extraction: manual`, rendered in
  the extraction column. No claim is `digitized`.
- **Rule 6 — PASS.** `work/muzellec-2023-pydeseq2/logs/container_run.log`
  contains, in order: `git rev-parse HEAD` (1), `python --version` (2),
  `pytest tests/ -q --junitxml=/work/out/pytest.xml` (3-5, "65 passed in
  51.29s") = M `stages[reference_suite]`, `extract_results.py` (6-24) =
  M `stages[extract]` and M `results:`, `cat results.csv` (20-24), and
  `git status --porcelain` inside the clone (25) which emits nothing, so the
  clone was untouched. The only two steps that are the paper's method are both
  in the manifest. `deviations: []` is therefore correct, and no step in the
  log lacks a manifest entry.
- **Rule 7 — PASS, strictly, with no precision caveat.** Manifest last commit
  `c53d9ca` **2026-09-06T18:11:10-04:00 = 22:11:10Z** <
  `work/muzellec-2023-pydeseq2/results.json` mtime **2026-09-06T23:12:11.419Z**
  < `generated_at` **2026-09-06T23:12:11.642Z** (and `report.json` mtime
  23:12:11.644Z). The manifest predates the run by 1 h 01 m, and the
  results → report ordering is now provable from the report alone at
  millisecond precision.
- **Rule 8 — PASS.** 4 of 4 claims `reproduced` → paper-level verdict
  `reproduced`, as `diff_claims.py:71` computes it.
- **Tone — PASS.** No prohibited phrasing anywhere in `report.md`. The
  renderer can only emit the permitted discrepancy form
  ("we could not obtain X … the closest we reached was Z"), re-verified live by
  reproducing the out-of-tolerance demonstration in a scratch copy.

## Regeneration

From a fresh clone of `100d605` with no `data/` and no `work/`,
`py -3 run_all.py muzellec-2023-pydeseq2 < /dev/null` exits 0 and the masked
diffs of `report.json` and `report.md` against the committed files
(`generated_at`, `fetched_at`, wall time masked) are **empty**.
`out/muzellec-2023-pydeseq2/results.csv` regenerates byte-identically.

## Findings

Zero **block**. Zero **fix** on this report. Notes carried forward unchanged
and accepted as dispositioned: N-1 (the two counted integers, a bounded
exemption declared in REQ-U2-04), N-2 (-2.78368 vs -2.783680), N-3 (P4 claimed
renders as a Python list literal while obtained uses the `;` results-file
form), N-4 ("every pinned component matched" is broader than the evidence:
`environment.python` 3.11 is a floor and the 3.12.14 actually run appears only
in `env_actual.json`), N-5 (Agent tokens 0 / USD 0.0 unqualified in
`report.md`). One new note, N3-7: `run_log.json` timestamps remain
second-precision, so `wall_minutes` is quantised to whole seconds. None of
these touches a published value.

APPROVED
