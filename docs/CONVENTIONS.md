# Conventions

The rules every manifest, Dockerfile, run.sh and run record in this repo follows.
Manifests cite this file by section name in their comments.

## Selection criteria and gate

Each candidate paper is scored 0, 1 or 2 on eight criteria. Scores and a one-line
justification (naming the source consulted) live in the manifest's `selection:`
block.

| | Criterion | 2 | 1 | 0 |
|---|---|---|---|---|
| C1 | Data availability | Deposited public record with DOI or accession, no login or data-use agreement | Public and stable (e.g. files in the repo at a pinned SHA, or a fixed URL) but no DOI or accession | Not available |
| C2 | Code licence | OSI licence declared and a LICENSE file in the tree | Licence declared but ambiguous or partial | No licence |
| C3 | Environment specification | Lock file or fully pinned Dockerfile/env file | A declared, resolvable dependency set (lower bounds, unpinned Dockerfile, or a partly pinned env file) | No environment file of any kind |
| C4 | Ground truth to compare against | Machine-readable reference numbers committed in the repo or supplementary data (metrics table, reference CSVs, test expectations) | Checkable numbers exist but are not a metrics table (e.g. stored notebook output) | Nothing to compare against |
| C5 | Publication status | Peer-reviewed journal article | Preprint | Neither |
| C6 | Maintainer engagement | A maintainer or collaborator replied to an issue within the last year | Replies exist but are older than a year, or releases without replies | None |
| C7 | Language and dependencies | Pure Python | Mixed, or R reached through rpy2 with a Python-only slice available | R only, or depends on an unpinned fork |
| C8 | Compute and data size | CPU minutes, no GPU, data well under 20 GB | A tractable slice exists; whole record near the 20 GB ceiling or many datasets | Above the ceiling, GPU or cluster required |

**Gate:** total >= 11 and no zero on C1-C4. A target that fails the gate is
recorded with status `deferred` and is not attempted.

**Status enum:** `selected` (attempted), `candidate` (attempted only if a
selected target does not run untouched), `deferred` (fails the gate).

## repro-target.yaml schema

| Key | Meaning |
|---|---|
| `schema_version` | Currently 1. |
| `slug` | `<firstauthor>-<year>-<short>`; also the directory name under `targets/` and `runs/`. |
| `status` | One of the status enum above. |
| `paper` | `title`, `doi`, `journal`, `year`, `first_author`, `last_author`, `url`. |
| `code[]` | One entry per repo: `role` (`package`, `pipeline` or `figures`), `repo`, `commit` (full SHA, verified via the GitHub API on the date recorded), `licence`, `entrypoint`. |
| `environment` | `kind` (`docker`), `spec` (the Dockerfile in the target directory), `python` (version as pinned or floored by the paper), `notes` (what the repo ships, known breaks recorded before the run). |
| `data[]` | One entry per input: `id`, `uri` (fetchable, stable), `path` (under the gitignored `data/`), `sha256` (filled by `hash_data.py`, never by hand), `size_bytes`. |
| `claims[]` | `id`, `figure`, `panel`, `metric`, `value`, `tolerance`, `tolerance_type`, `extraction` (`manual` for now), `source` (where the value was read and how the tolerance was chosen). |
| `checkpoints` | `max_download_gb`, `max_stage_minutes`. See human checkpoints below. |
| `deviations[]` | Every departure from the paper's own stated procedure, each with `what`, `why`, `approved_by`, `date`. Empty means the paper's procedure was followed as-is. |
| `stages[]` | `id`, `cmd` (argv list), `expected_minutes`. The run.sh executes these in order. |
| `results.file` | The output file, relative to the container's `/work`, that the claims are checked against. |
| `harness` | `image`, `results_file` (host path of `results.file`), `claim_keys` (claim id -> key in the results file), `stages[]` (`id`, `cmd` as an argv list with `{repo_root}` substituted at run time, `expected_minutes`). The host-level commands the report harness runs; `stages[]` above stays the in-container list. |
| `selection` | `C1`..`C8` each `{score, justification}`, and `total`. |
| `notes` | Gate verdict, expected untouched outcome with its reasoning, known weaknesses. |

Placeholders are written as `<fill: ...>` and say why the value is missing.
A placeholder is never replaced by a guess.

## Claims and tolerances

- `absolute`: |observed - value| <= tolerance.
- `relative`: |observed - value| / |value| <= tolerance.
- `rank-order`: `value` is an ordered list; `tolerance` is the largest allowed
  Kendall tau distance (0 means the ordering must be exactly preserved). Do not
  rank on a column that contains ties.
- p-values: compare log10(p) with an absolute tolerance of 0.3 (about a factor
  of two). A relative tolerance on a p-value is meaningless.
- The report schema spells the rank type `rank_order` and the harness maps
  `rank-order` onto it. `tolerance: 0` is the only rank tolerance the harness
  implements (exact ordering); a non-zero rank tolerance is refused rather than
  approximated.

Tolerance sources, in order of preference: (1) the precision the authors
themselves assert at (a test suite's tolerance, a stated rounding); (2) a
sensible value for the metric's range (0.02 absolute for a metric bounded in
[0,1]); (3) an observed spread from a seed sweep. Claims and tolerances are
committed before any run, and the run record cites the commit that fixed them.
Changing a tolerance after a run means recording old value, new value and
reason in git.

## The untouched test

A target runs untouched when all of the following hold:

1. Fresh clone of this repo into a scratch directory.
2. `docker build` from the committed Dockerfile, with no cache.
3. Every `data[]` entry fetched by its `uri` and hash-verified with `hash_data.py`
   against the committed `sha256`.
4. `docker run` with the committed `run.sh` as entrypoint exits 0.
5. The expected outputs (`results.file` and any other named artefact) are present.
6. No file under the paper's clone was edited: `git status --porcelain` inside
   the clone is empty in the built image and at the end of the run.
7. No manual step outside the Dockerfile and run.sh.

The answer is recorded in `runs/<slug>/untouched.md` with these fields:
`untouched` (yes / no / n/a), `date`, `host`, `image_id`, `manifest_commit`,
`command`, `exit_code`, `wall_time`, `first_error` (verbatim, the first error
the run printed), `data_hashes_verified`, `notes` (build, run, per-claim
observed value against tolerance, environment, seeds, anything a reader needs
to rerun it). A "no" with the first error recorded exactly is a valid result.

## Human checkpoints

The run stops and asks before continuing when:

1. any single download exceeds `checkpoints.max_download_gb` (5 GB in every
   manifest here);
2. any step deviates from the paper's stated method, including skipping a step
   the paper's own procedure performs - the deviation is logged in
   `deviations[]` with `approved_by` before the run proceeds;
3. any observed claim value falls outside its tolerance.

A failure is recorded, not fixed. The obvious fix (an edited URL, a pinned
dependency the project does not pin, a patched config) turns "untouched" into
"no" by definition; whether to apply it is a decision for the harness, not for
the run record.

## The report

The report harness (`harness/`, described in `harness/README.md`) runs six
stages, each writing one evidence file under the gitignored `work/<slug>/`:

1. build the environment -> `env_actual.json` (image id, base image, container
   Python, every difference from `targets/<slug>/env-resolved.txt`);
2. fetch and verify data -> `provenance.json` (expected and actual sha256 per
   `data[]` entry; a mismatch stops the run);
3. run the pipeline -> `logs/<stage id>.log` and `run_log.json` (argv, exit
   code, seconds, the code SHA read from the container's `== git HEAD:` line);
4. extract results -> `results.json`, parsed from the manifest's `results.file`
   without retyping;
5. diff claims -> `reports/<slug>/report.json`, validated against
   `harness/schema/report.schema.json` (JSON Schema draft 2020-12) before it
   is written;
6. render -> `reports/<slug>/report.md`, carrying no number the JSON does not.

The four checkpoints and the manifest keys they read: download size
(`checkpoints.max_download_gb` against `data[].size_bytes`), stage duration
(`checkpoints.max_stage_minutes` against `harness.stages[].expected_minutes`),
an unapproved deviation (`deviations[].approved_by` empty; the run refuses to
start), and an out-of-tolerance claim (the report is still written, flagged
for human review before any outreach).

`reports/<slug>/` holds `report.json`, `report.md`, `checkpoints.md` and
`review.md`. The adversarial reviewer brief is `harness/prompts/reviewer.md`;
the mapping from the paths it names onto this repository's layout is in
`harness/README.md`.

## Environment capture

- Everything runs in a container. The base image is pinned by digest
  (`FROM image@sha256:...`), with the tag and pull date in a comment.
- `OMP_NUM_THREADS`, `MKL_NUM_THREADS` and `OPENBLAS_NUM_THREADS` are set to 1
  and `PYTHONHASHSEED=0` in the image.
- The paper's repo is cloned inside the image and checked out at `code[].commit`.
  The environment is built from the paper's own env file or install path where
  one exists; otherwise from its declared dependencies, resolved once at build
  time.
- `pip freeze` (inside the environment) is written to `env-resolved.txt` and
  committed under `targets/<slug>/`; it is the record of what actually ran.
- `host.txt` records the host OS, Docker version, CPU count, RAM, GPU and BLAS
  (`numpy.show_config`).
- `hash_data.py` fills `sha256` for every `data[]` entry from the fetched file
  and prints `size_bytes`; a missing file is reported, not skipped.

Dockerfile skeleton:

```
FROM <base>@sha256:<digest>          # tag and pull date in a comment
ENV OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONHASHSEED=0
WORKDIR /work
RUN git clone <code[].repo> && cd <dir> && git checkout <code[].commit>
RUN <build the environment from the paper's own files>
RUN pip freeze > /work/env-resolved.txt
COPY run.sh /work/run.sh
ENTRYPOINT ["bash", "/work/run.sh"]
```

run.sh prints `== git HEAD: <sha>` as its first line, runs the manifest's
stages, writes the manifest's `results.file` as a two-column `key,value` CSV,
and finishes with `git status --porcelain` inside the clone.
