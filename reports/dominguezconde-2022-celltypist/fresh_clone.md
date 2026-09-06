# Fresh-clone regeneration: `dominguezconde-2022-celltypist`

The repository was cloned into a scratch directory with no `data/` and no
`work/` (both are gitignored), `py -3 run_all.py dominguezconde-2022-celltypist` was run there,
and the regenerated `report.md` and `report.json` were compared with the
ones in this directory with `generated_at`, every `fetched_at` and the
wall time masked. The clone's HEAD was `bd3aeb6`, the commit that carries
the round-1 harness fixes and the corrected manifests; the reports from this
run were not yet committed, so the comparison is against the working tree's
copies, which are the files committed here unchanged. The clone started with
the previously committed `out/dominguezconde-2022-celltypist/results.csv`; stage 4's
modification-time check accepted the file only because the container
rewrote it during this run. Absolute host paths in the transcript are
replaced by `<fresh_clone>` and `<orig>`.

```
$ git clone <base repo> repro-fresh && cd repro-fresh/unit1/repro-lab
$ git rev-parse --short HEAD  ->  bd3aeb6
$ ls data work 2>&1
ls: cannot access 'data': No such file or directory
ls: cannot access 'work': No such file or directory
$ py -3 run_all.py dominguezconde-2022-celltypist
[build_env] docker build -t repro-lab/dominguezconde-2022-celltypist targets/dominguezconde-2022-celltypist
[build_env] image repro-lab/dominguezconde-2022-celltypist id sha256:866b1ca53427a3f2eeb969372dc15235fb055755fea053e0553a872b4ecebb5d
[build_env] base python@sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b; container python 3.9.25
[build_env] 0 difference(s) vs targets/dominguezconde-2022-celltypist/env-resolved.txt
[fetch_verify] demo_cells: 35730948 bytes, sha256 OK
[fetch_verify] model_immune_all_low_v2: 2824990 bytes, sha256 OK
[run_pipeline] stage container_run: docker run --rm -v <fresh_clone>/data:/work/data:ro -v <fresh_clone>/out/dominguezconde-2022-celltypist:/work/out repro-lab/dominguezconde-2022-celltypist
[run_pipeline]   exit 0 in 7.61 s; log at work/dominguezconde-2022-celltypist/logs/container_run.log
[run_pipeline] code_sha from the run's own output: fe357564a6625d3b1732a022fd39f18e55696e80
[run_pipeline] extracted 4 metrics -> work/dominguezconde-2022-celltypist/results.json
[diff_claims] 4/4 claims within tolerance -> verdict: reproduced
[diff_claims] report.json validated against harness/schema/report.schema.json
[diff_claims] wrote reports/dominguezconde-2022-celltypist/report.json
[render_report] wrote reports/dominguezconde-2022-celltypist/report.md
[run_all] done: reports/dominguezconde-2022-celltypist/report.json, reports/dominguezconde-2022-celltypist/report.md
$ echo $?  ->  0
```

The masking functions and the diffs, run from the fresh clone with `<orig>`
the path of this repository:

```
mask() { sed -E -e 's/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:+.Z-]{5,}/TIMESTAMP/g'                 -e 's/^- Wall time: .*/- Wall time: WALL/' "$1"; }
norm() { py -3 -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); d['generated_at']='X'; d['cost']['wall_minutes']=0; [p.update(fetched_at='X') for p in d['data_provenance']]; print(json.dumps(d,indent=2,sort_keys=True))" "$1"; }
$ diff <(mask reports/dominguezconde-2022-celltypist/report.md) <(mask <orig>/reports/dominguezconde-2022-celltypist/report.md) && echo "dominguezconde-2022-celltypist: identical"
dominguezconde-2022-celltypist: identical
$ diff <(norm reports/dominguezconde-2022-celltypist/report.json) <(norm <orig>/reports/dominguezconde-2022-celltypist/report.json) && echo "dominguezconde-2022-celltypist: report.json identical"
dominguezconde-2022-celltypist: report.json identical
```

Both diffs are empty.
