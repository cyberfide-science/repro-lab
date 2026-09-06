# Checkpoints on this target

No checkpoint fired during the recorded run (`run_transcript.txt` in this
directory), and none was expected to: `checkpoints.max_download_gb: 5`
against a total fetch of 38,555,938 bytes (`report.json` `data_provenance[].bytes`),
`checkpoints.max_stage_minutes: 60` against `harness.stages[0].expected_minutes: 2`,
both `deviations[]` entries carry a non-empty `approved_by`, and all four claims
are within tolerance (`report.json` `claims[].verdict`). A sha256 mismatch did
not occur: both `provenance.json` entries are `verified: true`.

The checkpoints are the harness's, not the target's, so they are demonstrated
once, on a scratch copy of the PyDESeq2 target with a deliberately altered
manifest: `reports/muzellec-2023-pydeseq2/checkpoints.md`. What this target
exercises for real is the deviations ledger: both of its deviations appear in
`report.md` rather than stopping the run.
