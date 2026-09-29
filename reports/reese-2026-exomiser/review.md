# Reviewer findings: `reese-2026-exomiser`

Provenance: independent adversarial review, round 1, by a reviewer agent that built nothing it reviews, run
on 2026-09-29 against base-repo commit `71ec8e5`. Brief applied: `harness/prompts/reviewer.md`, rule by
rule. The reviewer had no write access and edited nothing. The full round-1 text, covering both targets, is
`unitR1/docs/reviews/r1-review-1.md` in the base repository, filed there verbatim as the precedent
`unit2/docs/reviews/` does.

M = `targets/reese-2026-exomiser/repro-target.yaml`, W = `work/reese-2026-exomiser/`,
R = `reports/reese-2026-exomiser/report.json`, O = `out/reese-2026-exomiser/`.

## Per-rule table

| Rule | Result | Evidence |
|---|---|---|
| 1 | PASS (on local `work/` files at review time; the transcript and container log did not yet exist as committed evidence) | Code sha `7a4dc1e06bf489f7815a873ef6c34a83c3b2e99b` from W `run_log.json` = `container_run.log:1`; Java `17.0.20.1` at line 2; Mondo version `obo:mondo/releases/2026-09-01/mondo.owl` at line 10; network check "unreachable" at line 11. Obtained values: W `results.json` = O `results.csv` = `container_run.log:231-233`. Data provenance: eight rows in W `provenance.json`, sha256 and bytes equal to M `data[]`. Wall time 288.983 min = 17339.4 s. |
| 2 | PASS | 63 of 63 numeric tokens in `report.md` occur verbatim in `report.json`. |
| 3 | PASS | Every claim carries tolerance 0.0005, tolerance_type absolute; the values 0.355/0.463/0.585 never change. |
| 4 | PASS | EX1-EX3 are `not_reproduced` with cause `undiagnosed`, printed in the human-review section. |
| 5 | vacuous | Every extraction is `manual`. |
| 6 | PASS for method deviations | Four deviation entries, all approved and dated. The tie rule, the differential construction, the Orphanet-to-Mondo mapping, minimal scoring, batching and the genome-assembly startup requirement are documented in the manifest's `notes`/comments as an unpublished method or a startup requirement, not deviations. Two unlisted process steps were found on the host (the void run and a pre-harness full-cohort analysis run); both are now disclosed in `fresh_clone.md`. |
| 7 | PASS | The manifest's last commit precedes the run's `results.json` mtime and `generated_at`. |
| 8 | PASS | 0 of 3 claims within tolerance -> `not_reproduced`. |
| Tone | PASS | Only the renderer's permitted discrepancy form is used. |
| Regeneration | PASS for the schema and negative-test checks as written; the byte-identity check on `results.csv` fails on one scheduling-dependent work counter (see Findings and `fresh_clone.md`), which is a declared, exempted exception, not an unresolved defect. |

## Check: tie band

Neither `report.md` states an optimistic/pessimistic range; the band exists only as evidence keys in
`results.csv` and `per_case.tsv`. Verified: every band count and fraction matches a recount of
`per_case.tsv`; the optimistic rank is always <= the point rank <= the pessimistic rank, on all 5,212 rows;
the tie rule (score descending, then a hash of the disease id ascending) matches the pre-registered rule.
All three claimed values lie inside the band (pessimistic to optimistic): EX1 0.3533474007289469 to
0.3769422597352772; EX2 0.46019566468444273 to 0.4807212737387301 (the point equals the pessimistic end);
EX3 0.5691540379819682 to 0.5896796470362555. The full wording is in `fresh_clone.md`.

## Findings relevant to this report

- **`fresh_clone.md` was missing.** Resolved by this commit's predecessor, which added the clone
  transcript, the masked and normalised diffs, the `results.csv` work-counter difference and its
  explanation, the negative-schema-test explanation, the matching `o1_subst_n_top1`, and the tie-band
  sentences for EX1-EX3.
- **The byte-identity check on `results.csv` fails on `exomiser_n_scored_pairs`** (line 27 of the file).
  Ruled: this key counts each worker's own process-local scoring-cache misses, and cases reach the workers
  out of a fixed order, so the total varies by run (79,252 in the void run, 79,548 in the scored run,
  79,571 in the fresh clone). It carries no information about any claim or the tie band, both of which are
  computed from `per_case.tsv`, which is byte-identical across all three runs, as is every other line of
  `results.csv`. The key is excluded from the byte-identity comparison and used by no claim; no code change
  was made after the run, since that would require a new scored run for a field no claim reads. Both values
  are recorded explicitly in `fresh_clone.md`.
- **This directory had no `run_transcript.txt` or `container_run.log`.** Resolved by this commit's
  predecessor: both files are now present, the transcript with host paths replaced by a placeholder.
- **The void run was disclosed nowhere committed.** Resolved by this commit's predecessor: `fresh_clone.md`
  now records its window (about 09:41-14:16Z on 2026-09-28), its image id, that it produced no `run_log.json`
  and so no report, and that its `per_case.tsv` is identical to the committed one.
- **The `mondo_semsql` data entry pointed at a gitignored local file**, because the mirror release was still
  pending when the manifest was committed. **Resolved by this commit's successor**: the uri now points at
  the published mirror release asset; `sha256` and `size_bytes` are unchanged. See "Post-run address
  change" below once that commit exists.
- **This `review.md` file did not exist.** Resolved by this commit.
- **`README.md` carried no report row for this target.** Resolved in an earlier documentation commit, which
  added the Reports-table row and the tie-band sentence.

## Notes

- **N2.** Both manifests' notes still describe the Exomiser scorer as running "with a copy of the authors'
  score caches" and scoring "each item," which is stale: the scorer keeps its own in-process memo per
  worker and never opens the copied cache files, and only the minimal item set is scored. Results are
  unaffected, because the caches are unreadable on this platform regardless. The accurate description is in
  this review and in the current spec revision; the manifest text itself is not edited, since only the
  `mondo_semsql` uri may change after the run.
- **N6.** A hygiene grep pattern aimed at spec references also matched the word "batches" in this target's
  own batching text (host facts, manifest, scoring script), because the pattern predates the batching
  design. The spec's grep pattern is corrected in the current spec revision; no manifest or report change
  follows.
- **N8.** `minimal_scoring_check.md` does not say that the pre-harness analysis run behind its 40-row table
  failed while reducing batch 190 and was resumed for batches 190-208 with a raised memory limit. This is
  now recorded in `fresh_clone.md`'s void-run section; `minimal_scoring_check.md` itself is not edited,
  since its 40-row result is unaffected and unchanged.
- **N9.** No committed file records exactly when the score-cache conversion attempt ran relative to its
  pre-registration commit, so the ordering cannot be proven from timestamps alone (only from commit order).
  Recorded here as an evidentiary gap; no manifest or code change.
- **N10.** Evidence paths in the report point into the gitignored `work/` directory, and "None: every
  pinned component matched" is broader than what `env_actual.json` alone shows. Carried forward unchanged,
  as in unit 2's equivalent note; not a result-affecting finding.
- **N11.** This report's fresh clone was made from the local repository path, not the public mirror. The
  tree-identity check against the public mirror follows the subtree push, which is outside this pass; not
  yet performed.
- **N13.** Not independently verified in this round: that every batch-file path inside the container
  matches the ASCII naming pattern the scored run relies on, and one cross-target provenance equality
  check. Left as an open verification item for a future round; neither affects a claim in this report.

## Post-run address change

Commit `b92f1e3` changed the manifest's `mondo_semsql` uri from the local placeholder
`file://data/manual/mondo-semsql-2026-09-27/mondo.db.gz` to the published mirror release asset,
`https://github.com/cyberfide-science/repro-lab/releases/download/data-mondo-semsql-2026-09-27/mondo.db.gz`.
`sha256` (`499f7078e4b60434e812500db709c8f03d52722c0d5543397947101b04bbefb0`) and `size_bytes`
(`242815274`) are unchanged, so the data behind the committed run is identical; the committed `report.json`
keeps the `file://` uri, because that is where the bytes came from in the run it records. No report was
regenerated.

APPROVED
