# The report harness

Five scripts and three prompt files that turn a `targets/<slug>/repro-target.yaml`
manifest into `reports/<slug>/report.json` and `report.md`. The scripts share
nothing but the manifest and the files under `work/<slug>/`; each one reads
the manifest itself and writes one evidence file. There is no package, no
shared module and no framework: every script is short enough to read in full.

## How to run it

From the repository root, with Docker running:

```
py -3 run_all.py <slug>
```

or, where GNU make exists, `make report TARGET=<slug> PY="py -3"` (`PY`
defaults to `python3`). The two run the same five scripts in the same order
and stop at the first non-zero exit. Each script also runs on its own:
`py -3 harness/<stage>.py <slug>`. The slug is the directory name under
`targets/`.

`work/<slug>/` is regenerated on every run and is gitignored, as is `data/`.
`reports/<slug>/` is committed.

GNU make was not available on the machine that produced the committed
reports, so `run_all.py` produced them. The Makefile's path was verified by
running its recipe commands by hand, in the Makefile's order, on a fresh copy
of the repository; the result was the same report. The transcript, with the
host paths replaced by placeholders:

```
$ # the Makefile recipes, run by hand in the Makefile order, on the scratch copy with its manifest restored
$ rm -rf work/muzellec-2023-pydeseq2          # clean
$ py -3 harness/build_env.py muzellec-2023-pydeseq2
[build_env] docker build -t repro-lab/muzellec-2023-pydeseq2 targets/muzellec-2023-pydeseq2
[build_env] image repro-lab/muzellec-2023-pydeseq2 id sha256:f2226316d67088b598abb0a28a48410d4015c9edb983497424b48decd4a26402
[build_env] base python@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea; container python 3.12.14
[build_env] 0 difference(s) vs targets/muzellec-2023-pydeseq2/env-resolved.txt
$ echo $?  ->  0
$ py -3 harness/fetch_verify.py muzellec-2023-pydeseq2
[fetch_verify] synthetic_counts: 3919 bytes, sha256 OK
[fetch_verify] synthetic_metadata: 1915 bytes, sha256 OK
$ echo $?  ->  0
$ py -3 harness/run_pipeline.py muzellec-2023-pydeseq2
[run_pipeline] stage container_run: docker run --rm -v <scratch_copy>/data:/work/data:ro -v <scratch_copy>/out/muzellec-2023-pydeseq2:/work/out repro-lab/muzellec-2023-pydeseq2
[run_pipeline]   exit 0 in 55.18 s; log at work/muzellec-2023-pydeseq2/logs/container_run.log
[run_pipeline] code_sha from the run's own output: 4426e4db990db1c511de3b1b9b7a514989663dad
[run_pipeline] extracted 4 metrics -> work/muzellec-2023-pydeseq2/results.json
$ echo $?  ->  0
$ py -3 harness/diff_claims.py muzellec-2023-pydeseq2
[diff_claims] 4/4 claims within tolerance -> verdict: reproduced
[diff_claims] report.json validated against harness/schema/report.schema.json
[diff_claims] wrote reports/muzellec-2023-pydeseq2/report.json
$ echo $?  ->  0
$ py -3 harness/render_report.py muzellec-2023-pydeseq2
[render_report] wrote reports/muzellec-2023-pydeseq2/report.md
$ echo $?  ->  0
```

## The six stages

| Stage | Script | Evidence file |
|---|---|---|
| 1 build the environment | `harness/build_env.py` | `work/<slug>/env_actual.json` (image id, base image, container Python, and every difference between `pip freeze` inside the image and `targets/<slug>/env-resolved.txt`) |
| 2 fetch and verify data | `harness/fetch_verify.py` | `work/<slug>/provenance.json` (uri, expected and actual sha256, bytes, fetched_at, per `data[]` entry; every file is fetched every run) |
| 3 run the pipeline | `harness/run_pipeline.py` | `work/<slug>/logs/<stage id>.log` and `work/<slug>/run_log.json` (argv as written in the manifest, `{repo_root}` unsubstituted; exit code; seconds; and the code SHA read from the container's own `== git HEAD:` line) |
| 4 extract results | `harness/run_pipeline.py` (same script) | `work/<slug>/results.json`, parsed from the `key,value` CSV the container wrote at `harness.results_file`; nothing is retyped |
| 5 diff claims | `harness/diff_claims.py` | `reports/<slug>/report.json`, validated against `harness/schema/report.schema.json` before it is written |
| 6 render | `harness/render_report.py` | `reports/<slug>/report.md`, derived from `report.json`. The renderer computes exactly two integers, the summary line's "n of m claims within tolerance" (claims with verdict `reproduced`, claims total), because the report template requires that line; every other value is copied from `report.json` |

The environment is the image, so stage 1 builds `targets/<slug>/Dockerfile`
(a cached rebuild is correct; a fresh clone builds for real). A package present
in `env-resolved.txt` and missing from the image is a hard stop; a version
difference is recorded as an `environment_delta` entry and the run continues.
The manifest's `environment.python` is a floor, so a delta for `python` is
emitted only if the container's version is below it. For a Docker target an
empty delta means the image built for this run resolved to the same package
versions as `env-resolved.txt`, the freeze recorded when the image was first
built; it does not mean the upstream project pins those versions itself.

Stage 3 runs the manifest's `harness.stages[]` (one `docker run` per target
here) as an argv list with no shell; `{repo_root}` in the argv is replaced by
the absolute, forward-slashed repository root for the subprocess only, and
`run_log.json` records the argv as the manifest writes it, so no evidence
file holds a host path. The container's first stdout line,
`== git HEAD: <sha>`, is the code SHA the report carries. The script removes
any earlier `work/<slug>/results.json` before it starts and writes
`work/<slug>/run_log.json` exactly once, in a `finally`, after everything
else: on every stop (a deviation without `approved_by`, a declined checkpoint,
a non-zero stage exit, a missing `== git HEAD:` line, a stale results file)
`run_log.json` carries the stop message in `aborted`, `code_sha` null where
it was never read, and only the stages that ran, and `results.json` is
absent. So after any run, complete or stopped, `work/<slug>/run_log.json`
and `results.json` describe that run alone, together with the logs of the
stages that `run_log.json` lists; a stage log left from an earlier run may
remain in `work/<slug>/logs/` after a stop that happened before any stage
ran. `reports/<slug>/` is written only after a complete run, so after a
stopped run the committed report can be older than the `work/` beside it;
compare `generated_at` with `run_log.json`. If the SHA differs from the manifest's
`code[].commit`, the difference is an `environment_delta` entry whose
component starts with `code:`.

Stage 4 refuses to read a results file whose modification time is not later
than the moment stage 3 started: `out/<slug>/` is committed, so a fresh clone
starts with an earlier run's copy, and that copy is never scored.

Stage 5 maps the schema-version-1 manifest onto the report: `claims[].value`
is `claimed`, `harness.claim_keys[id]` is the `metric` key looked up in
`results.json`, and `rank-order` becomes `rank_order`. Tolerances and
tolerance types are copied unchanged. A `rank-order` claim with a non-zero
tolerance is refused (this harness only implements exact ordering). No
arithmetic is done on any value: the container's results file already holds
every number in the form the claim states it.

## The four checkpoints

| Checkpoint | Manifest key | Stage | What happens |
|---|---|---|---|
| Download size | `checkpoints.max_download_gb` against `data[].size_bytes` | 2 | prompt `Proceed? [y/N]`; anything but `y` exits 1 |
| Stage duration | `checkpoints.max_stage_minutes` against `harness.stages[].expected_minutes` | 3 | prompt `Proceed? [y/N]`; anything but `y` exits 1 |
| Unapproved deviation | `deviations[].approved_by` empty | 3 | refuses before any subprocess starts, exit 1 |
| Out of tolerance | a claim outside its `tolerance` | 5 | prints a `[checkpoint]` line naming the claim; the report is still written and the stage exits 0. It gates outreach, not the run |

The size and duration checkpoints test the manifest's declared values
(`data[].size_bytes`, `harness.stages[].expected_minutes`) against the limits
before the fetch or the stage starts; neither compares a measured size or a
measured duration.

A sha256 mismatch in stage 2 is not a checkpoint but a stop: `MISMATCH` is
printed, `provenance.json` records both hashes, and the stage exits 1.

`HARNESS_APPROVE=1` answers the two prompts with yes, non-interactively. It is
for unattended runs only; a person or agent driving the harness from a terminal
does not set it (see `harness/prompts/executor.md`).

## The prompts

`harness/prompts/planner.md`, `executor.md` and `reviewer.md` are the three
role briefs. The reviewer brief is the published text unchanged, and the
paths it names are resolved by this table:

| The reviewer brief names | In this repository |
|---|---|
| `repro-target.yaml` | `targets/<slug>/repro-target.yaml` |
| `report.json`, `report.md` | `reports/<slug>/report.json`, `reports/<slug>/report.md` |
| `work/results.json`, `work/env_actual.json`, `work/provenance.json`, `work/run_log.json`, `work/logs/*.log` | the same names under `work/<slug>/` |
| `upstream/` | the clone inside the image, built by `targets/<slug>/Dockerfile`; it is never in the working tree, so "never edit files under `upstream/`" holds structurally |
| rule 7's `git log -1 --format=%cI -- repro-target.yaml` | `git log -1 --format=%cI -- targets/<slug>/repro-target.yaml` |

The reviewer's verdict for each target is saved as `reports/<slug>/review.md`.

`harness/schema/test_negative.py` differs from the published version in three
ways: it mutates `claims[0]` (a reproduced claim with a numeric tolerance)
because neither report holds a `not_reproduced` claim to mutate, it takes the
report path as its argument instead of assuming one, and it opens files as
UTF-8.

## Cost

The cost block records wall time from the run log. Token and dollar counts are
zero: these runs were driven from a terminal, and no wrapper was in place to
count them. A zero here means "not measured by an agent wrapper", not "free".

## What would move a number next

Every claim in both reports reproduced, so no report carries an `undiagnosed`
claim; the cheapest honest way to see one is to rebuild an image with
`--no-cache` on a later date and let `environment_delta` fill up on its own,
or a second manifest variant (float32, a different BLAS, a newer resolution of
the same unpinned dependency set) with its own pre-registered tolerances.
