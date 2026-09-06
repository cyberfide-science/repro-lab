# Fresh-clone regeneration: `muzellec-2023-pydeseq2`

The repository was cloned into a scratch directory with no `data/` and no
`work/` (both are gitignored), `py -3 run_all.py muzellec-2023-pydeseq2` was run there,
and the regenerated `report.md` and `report.json` were compared with the
ones in this directory with `generated_at`, every `fetched_at` and the
wall time masked. The clone's HEAD was `bd3aeb6`, the commit that carries
the round-1 harness fixes and the corrected manifests; the reports from this
run were not yet committed, so the comparison is against the working tree's
copies, which are the files committed here unchanged. The clone started with
the previously committed `out/muzellec-2023-pydeseq2/results.csv`; stage 4's
modification-time check accepted the file only because the container
rewrote it during this run. Absolute host paths in the transcript are
replaced by `<fresh_clone>` and `<orig>`.

```
$ git clone <base repo> repro-fresh && cd repro-fresh/unit1/repro-lab
$ git rev-parse --short HEAD  ->  bd3aeb6
$ ls data work 2>&1
ls: cannot access 'data': No such file or directory
ls: cannot access 'work': No such file or directory
$ py -3 run_all.py muzellec-2023-pydeseq2
[build_env] docker build -t repro-lab/muzellec-2023-pydeseq2 targets/muzellec-2023-pydeseq2
[build_env] image repro-lab/muzellec-2023-pydeseq2 id sha256:f2226316d67088b598abb0a28a48410d4015c9edb983497424b48decd4a26402
[build_env] base python@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea; container python 3.12.14
[build_env] 0 difference(s) vs targets/muzellec-2023-pydeseq2/env-resolved.txt
[fetch_verify] synthetic_counts: 3919 bytes, sha256 OK
[fetch_verify] synthetic_metadata: 1915 bytes, sha256 OK
[run_pipeline] stage container_run: docker run --rm -v <fresh_clone>/data:/work/data:ro -v <fresh_clone>/out/muzellec-2023-pydeseq2:/work/out repro-lab/muzellec-2023-pydeseq2
[run_pipeline]   exit 0 in 57.34 s; log at work/muzellec-2023-pydeseq2/logs/container_run.log
[run_pipeline] code_sha from the run's own output: 4426e4db990db1c511de3b1b9b7a514989663dad
[run_pipeline] extracted 4 metrics -> work/muzellec-2023-pydeseq2/results.json
[diff_claims] 4/4 claims within tolerance -> verdict: reproduced
[diff_claims] report.json validated against harness/schema/report.schema.json
[diff_claims] wrote reports/muzellec-2023-pydeseq2/report.json
[render_report] wrote reports/muzellec-2023-pydeseq2/report.md
[run_all] done: reports/muzellec-2023-pydeseq2/report.json, reports/muzellec-2023-pydeseq2/report.md
$ echo $?  ->  0
```

The masking functions and the diffs, run from the fresh clone with `<orig>`
the path of this repository:

```
mask() { sed -E -e 's/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:+.Z-]{5,}/TIMESTAMP/g'                 -e 's/^- Wall time: .*/- Wall time: WALL/' "$1"; }
norm() { py -3 -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); d['generated_at']='X'; d['cost']['wall_minutes']=0; [p.update(fetched_at='X') for p in d['data_provenance']]; print(json.dumps(d,indent=2,sort_keys=True))" "$1"; }
$ diff <(mask reports/muzellec-2023-pydeseq2/report.md) <(mask <orig>/reports/muzellec-2023-pydeseq2/report.md) && echo "muzellec-2023-pydeseq2: identical"
muzellec-2023-pydeseq2: identical
$ diff <(norm reports/muzellec-2023-pydeseq2/report.json) <(norm <orig>/reports/muzellec-2023-pydeseq2/report.json) && echo "muzellec-2023-pydeseq2: report.json identical"
muzellec-2023-pydeseq2: report.json identical
```

Both diffs are empty.
