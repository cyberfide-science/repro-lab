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

## The six stages

| Stage | Script | Evidence file |
|---|---|---|
| 1 build the environment | `harness/build_env.py` | `work/<slug>/env_actual.json` (image id, base image, container Python, and every difference between `pip freeze` inside the image and `targets/<slug>/env-resolved.txt`) |
| 2 fetch and verify data | `harness/fetch_verify.py` | `work/<slug>/provenance.json` (uri, expected and actual sha256, bytes, fetched_at, per `data[]` entry; every file is fetched every run) |
| 3 run the pipeline | `harness/run_pipeline.py` | `work/<slug>/logs/<stage id>.log` and `work/<slug>/run_log.json` (argv, exit code, seconds, and the code SHA read from the container's own `== git HEAD:` line) |
| 4 extract results | `harness/run_pipeline.py` (same script) | `work/<slug>/results.json`, parsed from the `key,value` CSV the container wrote at `harness.results_file`; nothing is retyped |
| 5 diff claims | `harness/diff_claims.py` | `reports/<slug>/report.json`, validated against `harness/schema/report.schema.json` before it is written |
| 6 render | `harness/render_report.py` | `reports/<slug>/report.md`, derived from `report.json` and carrying no number the JSON does not |

The environment is the image, so stage 1 builds `targets/<slug>/Dockerfile`
(a cached rebuild is correct; a fresh clone builds for real). A package present
in `env-resolved.txt` and missing from the image is a hard stop; a version
difference is recorded as an `environment_delta` entry and the run continues.
The manifest's `environment.python` is a floor, so a delta for `python` is
emitted only if the container's version is below it.

Stage 3 runs the manifest's `harness.stages[]` (one `docker run` per target
here) as an argv list with no shell; `{repo_root}` in the argv is replaced by
the absolute, forward-slashed repository root. The container's first stdout
line, `== git HEAD: <sha>`, is the code SHA the report carries; if that line is
absent the stage stops and no report is written. If it differs from the
manifest's `code[].commit`, the difference is an `environment_delta` entry
whose component starts with `code:`.

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

A sha256 mismatch in stage 2 is not a checkpoint but a stop: `MISMATCH` is
printed, `provenance.json` records both hashes, and the stage exits 1.

`HARNESS_APPROVE=1` answers the two prompts with yes, non-interactively. It is
for unattended runs only; a person or agent driving the harness from a terminal
does not set it (see `harness/prompts/executor.md`).

## The prompts

`harness/prompts/planner.md`, `executor.md` and `reviewer.md` are the three
role briefs. The reviewer brief is the published text unchanged, and the
paths it names are resolved by this table:

| The brief says | In this repository |
|---|---|
| `repro-target.yaml` | `targets/<slug>/repro-target.yaml` |
| `report.json`, `report.md` | `reports/<slug>/report.json`, `reports/<slug>/report.md` |
| `work/results.json`, `work/env_actual.json`, `work/provenance.json`, `work/run_log.json`, `work/logs/*.log` | the same names under `work/<slug>/` |
| `upstream/` | the clone inside the image, built by `targets/<slug>/Dockerfile`; it is never in the working tree, so "never edit files under `upstream/`" holds structurally |
| rule 7's `git log -1 --format=%cI -- repro-target.yaml` | `git log -1 --format=%cI -- targets/<slug>/repro-target.yaml` |

The reviewer's verdict for each target is saved as `reports/<slug>/review.md`.

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
