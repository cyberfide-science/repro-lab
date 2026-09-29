# repro-lab

Can a published computational pipeline run untouched, from a pinned manifest,
in a fresh container, with its claims and tolerances written down before the
first run? This is a repository of scripts and records that tests exactly that,
one paper at a time. It is not a package.

Each `targets/<slug>/` holds a `repro-target.yaml` manifest (pinned commit, data
URIs + sha256, pre-registered claims and tolerances, selection score), a
`Dockerfile` and a `run.sh`. Each `runs/<slug>/` holds the `untouched.md` record
and the captured log. Paper code is cloned inside the image at build time and is
never edited; data is mounted read-only at run time. A failure is recorded with
its first error, not fixed. The rules are in `docs/CONVENTIONS.md`.

## Layout

```
targets/<slug>/   repro-target.yaml, Dockerfile, run.sh, env-resolved.txt, host.txt
runs/<slug>/      untouched.md, stdout.txt, build.log
out/<slug>/       outputs written by the container
docs/             CONVENTIONS.md (criteria, schema, tolerances, untouched test)
hash_data.py      fills data[].sha256 in a manifest from the fetched files
harness/          the report harness: five stage scripts, the report schema, the role briefs
work/<slug>/      evidence files written by a harness run (gitignored, regenerated every run)
reports/<slug>/   report.json, report.md, run_transcript.txt, container_run.log, checkpoints.md, fresh_clone.md, review.md
```

## Run the PyDESeq2 target (Muzellec et al. 2023)

Data fetch and hash, done once before the run (`data/` is gitignored). The URIs
and paths are the manifest's `data[].uri` and `data[].path`:

```
git clone https://github.com/cyberfide-science/repro-lab.git repro-lab && cd repro-lab
mkdir -p data/pydeseq2
curl -fL -o data/pydeseq2/test_counts.csv   https://raw.githubusercontent.com/owkin/PyDESeq2/4426e4db990db1c511de3b1b9b7a514989663dad/datasets/synthetic/test_counts.csv
curl -fL -o data/pydeseq2/test_metadata.csv https://raw.githubusercontent.com/owkin/PyDESeq2/4426e4db990db1c511de3b1b9b7a514989663dad/datasets/synthetic/test_metadata.csv
python hash_data.py targets/muzellec-2023-pydeseq2/repro-target.yaml
```

Git Bash on Windows: prefix the `docker run` below with `MSYS_NO_PATHCONV=1` and
write `$(pwd -W)` instead of `$PWD`, otherwise the `-v` arguments are mangled.

```
docker build -t repro-lab/muzellec-2023-pydeseq2 targets/muzellec-2023-pydeseq2
docker run --rm -v "$PWD/data:/work/data:ro" -v "$PWD/out/muzellec-2023-pydeseq2:/work/out" repro-lab/muzellec-2023-pydeseq2
```

Expect `65 passed`, then `out/muzellec-2023-pydeseq2/{pytest.xml,results.csv}`
and an empty `git status` line for the clone.

## Results

| slug | paper | score | untouched |
|---|---|---|---|
| muzellec-2023-pydeseq2 | Muzellec et al. 2023, Bioinformatics (PyDESeq2) | 15 | yes |
| dominguezconde-2022-celltypist | Dominguez Conde et al. 2022, Science (CellTypist) | 14 | yes |
| luecken-2022-scib | Luecken et al. 2022, Nature Methods (scib-pipeline) | 12 | no: the paper's environment file could not be built as shipped; its pip block pins scib via a `git+git://` URL, a protocol GitHub no longer serves |
| luecken-2022-scib-metrics | Luecken et al. 2022, Nature Methods (scib package) | 14 | not attempted (fallback, not needed) |
| squair-2021-de | Squair et al. 2021, Nature Communications | 8 | not attempted (fails the selection gate) |

Full records: `runs/<slug>/untouched.md`. Resolved environments:
`targets/<slug>/env-resolved.txt`; host details in `host.txt`.

## Reports

A report is the manifest's claims checked against one harness run: every
claim with its pre-registered tolerance, the environment that actually ran,
the data hashes, the deviations ledger and the cost, as `report.json`
(validated against `harness/schema/report.schema.json`) and `report.md`
rendered from it. How the harness works: `harness/README.md`.

| slug | verdict | report |
|---|---|---|
| muzellec-2023-pydeseq2 | reproduced (4 of 4 claims) | [reports/muzellec-2023-pydeseq2/report.md](reports/muzellec-2023-pydeseq2/report.md) |
| dominguezconde-2022-celltypist | reproduced (4 of 4 claims) | [reports/dominguezconde-2022-celltypist/report.md](reports/dominguezconde-2022-celltypist/report.md) |
| reese-2026-rescore | not_reproduced (0 of 3 claims) | [reports/reese-2026-rescore/report.md](reports/reese-2026-rescore/report.md) |
| reese-2026-exomiser | not_reproduced (0 of 3 claims) | [reports/reese-2026-exomiser/report.md](reports/reese-2026-exomiser/report.md) |

reese-2026-rescore scores the deposited o1-preview answers under offline-only grounding (substituted
grounding was dropped after both Claude Opus 5.5 mapping-table attempts failed their pre-registered
agreement gate); reese-2026-exomiser's report gives a pessimistic-to-optimistic range alongside its point
values, because the reruns's tied Exomiser scores are ordered non-deterministically and the paper does not
state a tie rule. The one-time grounding step's provenance (which model, gate result, token counts) is in
`targets/reese-2026-rescore/grounding/opus-mondo-map.meta.json` and
`targets/reese-2026-rescore/grounding/attempt-2/opus-mondo-map.meta.json`. `fetch_verify` hashes its inputs
in 1 MiB chunks, so the multi-gigabyte Exomiser data files are never read into memory whole.

To regenerate, from the repository root with Docker running:

```
py -3 run_all.py muzellec-2023-pydeseq2
py -3 run_all.py dominguezconde-2022-celltypist
```

GNU make was not present on the machine that produced these reports, so
`run_all.py` is the documented substitute for `make report TARGET=<slug>`: it
runs the Makefile's five recipes in the Makefile's order and stops at the
first non-zero exit. The Makefile's path was verified by running its five
recipe commands by hand, in order, in a fresh copy; the transcript is in
`harness/README.md`. `HARNESS_APPROVE=1` pre-answers the two interactive
checkpoints and is for unattended runs only.

Fresh-clone check: clone this repository into an empty directory (no `data/`,
no `work/`), run the two commands above, then compare with the committed
reports with the timestamps and wall time masked:

```
mask() { sed -E -e 's/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:+.Z-]{5,}/TIMESTAMP/g' \
                -e 's/^- Wall time: .*/- Wall time: WALL/' "$1"; }
for s in muzellec-2023-pydeseq2 dominguezconde-2022-celltypist; do
  diff <(mask "reports/$s/report.md") <(mask "<orig>/reports/$s/report.md") && echo "$s: identical"
done
```

and for the JSON, with `generated_at`, `fetched_at` and `wall_minutes` removed:

```
norm() { py -3 -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); \
d['generated_at']='X'; d['cost']['wall_minutes']=0; \
[p.update(fetched_at='X') for p in d['data_provenance']]; \
print(json.dumps(d,indent=2,sort_keys=True))" "$1"; }
diff <(norm "reports/$s/report.json") <(norm "<orig>/reports/$s/report.json")
```

Both diffs were empty for both targets when the committed reports were made;
the commands and their output are in `reports/<slug>/fresh_clone.md`.

Where the evidence lives: `reports/<slug>/run_transcript.txt` is the terminal
output of the run, `container_run.log` is the container's stdout and stderr
(the code SHA line, the test-suite result, the clean `git status` inside the
clone), `checkpoints.md` shows every checkpoint firing on a scratch copy, and
`review.md` is the adversarial reviewer's verdict. The regenerated files under
`work/<slug>/` are gitignored.

The cost block records wall time from the run log. Token and dollar counts are
zero: these runs were driven from a terminal, and no wrapper was in place to
count them. A zero here means "not measured by an agent wrapper", not "free".

MIT licence for this repo; the paper repos keep their own.
