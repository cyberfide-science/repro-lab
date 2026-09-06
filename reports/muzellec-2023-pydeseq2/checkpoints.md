# Checkpoint demonstrations

Every transcript below comes from a scratch copy of this repository with a
deliberately altered `targets/muzellec-2023-pydeseq2/repro-target.yaml`; the
manifest in this repository is unchanged (`git diff -- targets/` is empty), and
the scratch copy was discarded afterwards. Each block shows the edit, the
command and the exit code exactly as run (Git Bash on Windows). The scratch
copy started with a copy of the real `work/muzellec-2023-pydeseq2/` from the
recorded run, so demonstration 6 needed no second container run.

Demonstration 3 changes the manifest's expectation rather than the file: both
data sources are `https://` URIs that are re-fetched every run, so the
equivalent of appending a byte to a local file is to change one hex character
of `data[0].sha256`. Demonstration 6's `0.70` is a fabricated value for the
demonstration only; the repository's P1 remains `0.632812315254828`.

```
### 1. Download-size checkpoint, answered n
$ sed -i "s/^  max_download_gb: 5$/  max_download_gb: 0.0/" targets/muzellec-2023-pydeseq2/repro-target.yaml
$ echo n | py -3 harness/fetch_verify.py muzellec-2023-pydeseq2
[checkpoint] data 'synthetic_counts' is 3.919e-06 GB (> 0.0 GB limit). Proceed? [y/N] [fetch_verify] stopped at human checkpoint
$ echo $?  ->  1

### 2. Same manifest, pre-approved with HARNESS_APPROVE=1
$ HARNESS_APPROVE=1 py -3 harness/fetch_verify.py muzellec-2023-pydeseq2
[checkpoint] data 'synthetic_counts' is 3.919e-06 GB (> 0.0 GB limit). -- approved via HARNESS_APPROVE=1
[fetch_verify] synthetic_counts: 3919 bytes, sha256 OK
[checkpoint] data 'synthetic_metadata' is 1.915e-06 GB (> 0.0 GB limit). -- approved via HARNESS_APPROVE=1
[fetch_verify] synthetic_metadata: 1915 bytes, sha256 OK
$ echo $?  ->  0

### 3. sha256 mismatch
$ # limit restored; one hex character of data[0].sha256 changed (09d632cc... -> 09d632cd...)
$ sed -i "s/09d632cc7b2792602599793062f980bd5a767afa9757943738263976f0e137c3/09d632cd7b2792602599793062f980bd5a767afa9757943738263976f0e137c3/" targets/muzellec-2023-pydeseq2/repro-target.yaml
$ py -3 harness/fetch_verify.py muzellec-2023-pydeseq2
[fetch_verify] synthetic_counts: 3919 bytes, sha256 MISMATCH
[fetch_verify] hash mismatch for synthetic_counts; not proceeding
$ echo $?  ->  1
$ cat work/muzellec-2023-pydeseq2/provenance.json
[
  {
    "id": "synthetic_counts",
    "uri": "https://raw.githubusercontent.com/owkin/PyDESeq2/4426e4db990db1c511de3b1b9b7a514989663dad/datasets/synthetic/test_counts.csv",
    "dest": "data/pydeseq2/test_counts.csv",
    "sha256_expected": "09d632cd7b2792602599793062f980bd5a767afa9757943738263976f0e137c3",
    "sha256_actual": "09d632cc7b2792602599793062f980bd5a767afa9757943738263976f0e137c3",
    "bytes": 3919,
    "fetched_at": "2026-09-06T22:20:07+00:00",
    "verified": false
  }
]

### 4. Stage-duration checkpoint, answered n
$ # sha256 restored
$ sed -i "s/^  max_stage_minutes: 30$/  max_stage_minutes: 0.01/" targets/muzellec-2023-pydeseq2/repro-target.yaml
$ echo n | py -3 harness/run_pipeline.py muzellec-2023-pydeseq2
[checkpoint] stage 'container_run' expected 5 min (> 0.01 min limit). Proceed? [y/N] [run_pipeline] stopped at human checkpoint
$ echo $?  ->  1

### 5. Deviation without approved_by
$ # limit restored
$ sed -i "s/^deviations: \[\]$/deviations:\n  - what: demonstration entry with no approver\n    why: to show the refusal\n    approved_by:\n    date: 2026-09-06/" targets/muzellec-2023-pydeseq2/repro-target.yaml
$ py -3 harness/run_pipeline.py muzellec-2023-pydeseq2
[run_pipeline] deviation 'demonstration entry with no approver' has no approved_by; stopping
$ echo $?  ->  1

### 6. Out-of-tolerance claim (P1 value changed 0.632812315254828 -> 0.70 in the scratch manifest only)
$ # deviations restored; work/muzellec-2023-pydeseq2/ is a copy of the real run, so no container run is needed
$ sed -i "s/^    value: 0.632812315254828$/    value: 0.70/" targets/muzellec-2023-pydeseq2/repro-target.yaml
$ py -3 harness/diff_claims.py muzellec-2023-pydeseq2
[diff_claims] 3/4 claims within tolerance -> verdict: partially
[checkpoint] P1 (P1_log2FoldChange_gene1): claimed 0.7, obtained 0.632812476644658 [relative 0.02] -- needs human review before any outreach
[diff_claims] report.json validated against harness/schema/report.schema.json
[diff_claims] wrote reports/muzellec-2023-pydeseq2/report.json
$ echo $?  ->  0
$ py -3 harness/render_report.py muzellec-2023-pydeseq2
[render_report] wrote reports/muzellec-2023-pydeseq2/report.md
$ echo $?  ->  0
$ grep -A2 "^## Human review required" reports/muzellec-2023-pydeseq2/report.md
## Human review required

- P1: we could not obtain 0.7 for P1_log2FoldChange_gene1 under the manifest's conditions; the closest we reached was 0.632812476644658. Cause: undiagnosed.
$ grep "^| P1 " reports/muzellec-2023-pydeseq2/report.md
| P1 | n/a - reference output committed in the repo, not a paper figure | P1_log2FoldChange_gene1 | 0.7 | 0.632812476644658 | relative 0.02 | not_reproduced | undiagnosed | manual | `work/muzellec-2023-pydeseq2/results.json` |
```

## Schema negative test

Run in this repository, against the real reports, after the recorded runs:

```
$ py -3 harness/schema/test_negative.py reports/muzellec-2023-pydeseq2/report.json
cause_category='undiagnosed': 1 error(s): 'n/a' was expected
tolerance=None: 1 error(s): None is not of type 'number'
$ py -3 harness/schema/test_negative.py reports/dominguezconde-2022-celltypist/report.json
cause_category='undiagnosed': 1 error(s): 'n/a' was expected
tolerance=None: 1 error(s): None is not of type 'number'
```

Both mutations are rejected for both reports: a reproduced claim may not carry
a cause other than `n/a`, and a claim with a numeric tolerance type may not
have a null tolerance.
