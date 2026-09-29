# Reviewer findings: `reese-2026-rescore`

Provenance: independent adversarial review, round 1, by a reviewer agent that built nothing it reviews, run
on 2026-09-29 against base-repo commit `71ec8e5`. Brief applied: `harness/prompts/reviewer.md`, rule by
rule. The reviewer had no write access and edited nothing. The full round-1 text, covering both targets, is
`unitR1/docs/reviews/r1-review-1.md` in the base repository, filed there verbatim as the precedent
`unit2/docs/reviews/` does.

M = `targets/reese-2026-rescore/repro-target.yaml`, W = `work/reese-2026-rescore/`,
R = `reports/reese-2026-rescore/report.json`, O = `out/reese-2026-rescore/`.

## Per-rule table

| Rule | Result | Evidence |
|---|---|---|
| 1 | PASS | Title and DOI from M `paper`; code sha `bd7146d15798b4dd968fd64bc9a42e6971aa8fae` from W `run_log.json` `code_sha` = `container_run.log:1`; `generated_at` from R. Claimed values from M; obtained values from W `results.json` metrics RS1/2/3 = O `results.csv` = `container_run.log:18-20`; counts 1051/1381/1550 over 5213 recomputed independently from `per_case.tsv`. Environment delta: W `env_actual.json` `delta` is empty. Data provenance: W `provenance.json`, sha256 and bytes equal to M `data[]`. Wall time 78.517 min = 4710.95 s from W `run_log.json`. |
| 2 | PASS | 52 of 52 numeric tokens in `report.md` occur verbatim in `report.json`; nothing recomputed in prose. |
| 3 | PASS | Every claim carries tolerance 0.0005, tolerance_type absolute, at every manifest commit; the values 0.236/0.312/0.368 never change. |
| 4 | PASS | RS1-RS3 are `not_reproduced` with cause `undiagnosed`, and the word is printed in the human-review section. |
| 5 | vacuous | Every extraction is `manual`. |
| 6 | PASS | `container_run.log` shows, in order: git HEAD, python version, Mondo version, jsonl line count, network check (unreachable), the scoring step with 32 workers, the results, and an empty `git status` inside the clone. Offline-only grounding is one deviation; the substituted-grounding keys back no claim; the cache-unreadability finding is in `environment.notes` and `notes`. Five deviation entries, each with `approved_by` "Michael Wolfe, repro-lab maintainer", dated 2026-09-27. |
| 7 | PASS | The Opus mapping table's prompt, schema and gate are committed before the first call of each attempt; the claims, tolerances, tie rule and case list are committed before the scored run; the manifest's last commit precedes the run's `results.json` and `generated_at`. |
| 8 | PASS | 0 of 3 claims within tolerance -> `not_reproduced`. |
| Tone | PASS | Only the renderer's permitted discrepancy form is used; no statement characterises the authors' work. |
| Regeneration | PASS | A fresh clone at the commit that carries this report exits 0; the masked `report.md` and normalised `report.json` diffs are empty, and `out/` is byte-identical. |

## Findings relevant to this report

- **The `mondo_semsql` data entry pointed at a gitignored local file** (`file://data/manual/...`) because
  the mirror release was still pending when the manifest was committed. **Resolved by this commit's
  successor**: the uri now points at the published mirror release asset; `sha256` and `size_bytes` are
  unchanged. See "Post-run address change" below once that commit exists.
- **This `review.md` file did not exist.** Resolved by this commit.
- **`README.md` carried no report row for this target.** Resolved in the preceding documentation commit,
  which added the Reports-table row and a pointer to the grounding step's provenance files.

## Notes

- **N1.** The RS4-RS6 deviation text says the Opus mapping table was "validated (agreement ... >= 0.90 ...)
  and committed before this run", which reads as a pass when both attempts in fact failed the gate. The
  deviation entries for attempts 1 and 2 correct this, each stating its own agreement figure (0.2628 and
  0.3545) and that RS4-RS6 stayed removed. No manifest edit follows beyond what is already committed.
- **N3.** The attempt-1 deviation cites the commit that added the table and meta file; one row's name bytes
  were fixed in a later, disclosed commit that did not change the gate result. Recorded here; no manifest
  change.
- **N4.** The attempt-2 meta file's `echo_compare` field describes the NFC rule as applying "from chunk 80
  attempt 4 on; byte-exact before," but attempt 2 in fact applied NFC comparison to every chunk. This is a
  meta-file wording imprecision, not a result; not corrected, since no manifest or meta edit is permitted
  after the run.
- **N5.** The gate threshold was pre-registered in code four seconds before the first chunk call; the
  manifest notes and spec text restating it were committed only after that first call, so the
  pre-registration requirement is met in substance (the code came first) but not in the manifest's own
  prose. The spec text describing this history was corrected in the current spec revision; no manifest
  change.
- **N6.** A hygiene grep pattern aimed at spec references also matched the word "batches" in this target's
  own batching text (host facts, manifest, scorer script), because the pattern predates the batching design.
  The spec's grep pattern is corrected in the current spec revision; no manifest or report change follows.
- **N10.** Evidence paths in the report point into the gitignored `work/` directory, as in unit 2's reports,
  and "None: every pinned component matched" is broader than what `env_actual.json` shows on its own.
  Carried forward unchanged, as in unit 2's equivalent note; not a result-affecting finding.
- **N11.** This report's fresh clone was made from the local repository path, not the public mirror. The
  tree-identity check against the public mirror follows the subtree push, which is outside this pass; not
  yet performed.
- **N12.** The rescore stage took 78.5 minutes against an `expected_minutes` of 527, because the estimate's
  basis (a timed slice) assumed empty caches while the full run used 32 parallel workers. Harmless; the
  committed value was not changed after the run.

Under offline-only grounding we obtained 0.20161135622482257 against 23.6% at top-1, 0.2649146364857088
against 31.2% at top-3, and 0.2973335891041627 against 36.8% at top-10; this condition can only lower the
count. The paper-level verdict counts these three claims, so it is `not_reproduced`, as the manifest's
`notes:` said before the run.

APPROVED
