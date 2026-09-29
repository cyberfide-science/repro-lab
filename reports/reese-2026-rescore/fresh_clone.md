# Fresh-clone regeneration: `reese-2026-rescore`

The repository was cloned into a scratch directory with no `data/` and no `work/` (both are gitignored),
and `HARNESS_APPROVE=1 py -3 run_all.py reese-2026-rescore` was run there under the maintainer's written
pre-approval of the rescore run and its fresh-clone rerun (it answers the stage-duration checkpoint only;
no rescore input exceeds the download limit). The clone's HEAD was `b0dffa6`, the commit that carries the
report in this directory. One input was placed by hand before the run: the pinned Mondo SemSQL file, at
the manifest's `file://data/manual/mondo-semsql-2026-09-27/mondo.db.gz`, because its mirror release is not
yet published (the manifest records this as pending); `fetch_verify` then copied it and verified its
sha256 like every other input. The Zenodo files were downloaded from their URIs. The clone started with
the committed `out/reese-2026-rescore/results.csv`; stage 4's modification-time check accepted the file
only because the container rewrote it during this run. Absolute host paths in the transcript are replaced
by `<fresh_clone>` and `<orig>`.

```
$ git clone <base repo> fresh && cd <repro-lab in the clone>
$ git rev-parse --short HEAD  ->  b0dffa6
$ ls data work 2>&1
ls: cannot access 'data': No such file or directory
ls: cannot access 'work': No such file or directory
$ mkdir -p data/manual/mondo-semsql-2026-09-27 && cp <orig>/data/manual/mondo-semsql-2026-09-27/mondo.db.gz data/manual/mondo-semsql-2026-09-27/
$ sha256sum data/manual/mondo-semsql-2026-09-27/mondo.db.gz
499f7078e4b60434e812500db709c8f03d52722c0d5543397947101b04bbefb0 *data/manual/mondo-semsql-2026-09-27/mondo.db.gz
$ HARNESS_APPROVE=1 py -3 run_all.py reese-2026-rescore
[build_env] docker build -t repro-lab/reese-2026-rescore targets/reese-2026-rescore
[build_env] image repro-lab/reese-2026-rescore id sha256:2a0da7cdf477dbea37ddac47030051691e6aa23d9f0bb4c780ec94a3ebd1e7f2
[build_env] base python@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f; container python 3.12.14
[build_env] 0 difference(s) vs targets/reese-2026-rescore/env-resolved.txt
[fetch_verify] responses_zip: 9406802 bytes, sha256 OK
[fetch_verify] gold_tsv: 474639 bytes, sha256 OK
[fetch_verify] mondo_semsql: 242815274 bytes, sha256 OK
[fetch_verify] opus_mondo_map: 406599 bytes, sha256 OK
[checkpoint] stage 'container_run' expected 527 min (> 30 min limit). -- approved via HARNESS_APPROVE=1
[run_pipeline] stage container_run: docker run --rm --network none -v <fresh_clone>/data/reese-2026:/work/data:ro -v <fresh_clone>/out/reese-2026-rescore:/work/out repro-lab/reese-2026-rescore
[run_pipeline]   exit 0 in 5041.12 s; log at work/reese-2026-rescore/logs/container_run.log
[run_pipeline] code_sha from the run's own output: bd7146d15798b4dd968fd64bc9a42e6971aa8fae
[run_pipeline] extracted 22 metrics -> work/reese-2026-rescore/results.json
[diff_claims] 0/3 claims within tolerance -> verdict: not_reproduced
[checkpoint] RS1 (RS1_o1_top1_frac_floor): claimed 0.236, obtained 0.20161135622482257 [absolute 0.0005] -- needs human review before any outreach
[checkpoint] RS2 (RS2_o1_top3_frac_floor): claimed 0.312, obtained 0.2649146364857088 [absolute 0.0005] -- needs human review before any outreach
[checkpoint] RS3 (RS3_o1_top10_frac_floor): claimed 0.368, obtained 0.2973335891041627 [absolute 0.0005] -- needs human review before any outreach
[diff_claims] report.json validated against harness/schema/report.schema.json
[diff_claims] wrote reports/reese-2026-rescore/report.json
[render_report] wrote reports/reese-2026-rescore/report.md
[run_all] done: reports/reese-2026-rescore/report.json, reports/reese-2026-rescore/report.md
$ echo $?  ->  0
```

The masking functions and the diffs, run from the fresh clone with `<orig>` the path of this repository:

```
mask() { sed -E -e 's/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:+.Z-]{5,}/TIMESTAMP/g' -e 's/^- Wall time: .*/- Wall time: WALL/' "$1"; }
norm() { py -3 -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); d['generated_at']='X'; d['cost']['wall_minutes']=0; [p.update(fetched_at='X') for p in d['data_provenance']]; print(json.dumps(d,indent=2,sort_keys=True))" "$1"; }
$ diff <(mask reports/reese-2026-rescore/report.md) <(mask <orig>/reports/reese-2026-rescore/report.md) && echo "reese-2026-rescore: identical"
reese-2026-rescore: identical
$ diff <(norm reports/reese-2026-rescore/report.json) <(norm <orig>/reports/reese-2026-rescore/report.json) && echo "reese-2026-rescore: report.json identical"
reese-2026-rescore: report.json identical
$ cmp out/reese-2026-rescore/results.csv <orig>/out/reese-2026-rescore/results.csv && cmp out/reese-2026-rescore/per_case.tsv <orig>/out/reese-2026-rescore/per_case.tsv && echo "results.csv and per_case.tsv byte-identical"
results.csv and per_case.tsv byte-identical
```

Both diffs are empty; the container's `results.csv` and `per_case.tsv` are byte-identical as well.

Negative schema test on the regenerated report:

```
$ py -3 harness/schema/test_negative.py reports/reese-2026-rescore/report.json
cause_category='undiagnosed': 0 error(s): 
tolerance=None: 1 error(s): None is not of type 'number'
```

The first line reports zero errors, and that is expected here: the mutation sets claim 1's
`cause_category` to `undiagnosed`, which the schema rejects only for a `reproduced` claim, and claim 1 (RS1)
is already `not_reproduced` with cause `undiagnosed`, so the mutated report is still valid. The second
mutation is rejected as it should be.

What the regenerated numbers say, in the wording the manifest fixed before the run: under offline-only
grounding (OAK exact match; the paper's CurateGPT step not run) we obtained 0.20161135622482257 against
23.6% at top 1, 0.2649146364857088 against 31.2% at top 3 and 0.2973335891041627 against 36.8% at top 10.
This condition can only lower the count, so these are a lower bound for this pipeline, not a test of the
paper's numbers. The paper-level verdict counts these three claims, so it is `not_reproduced`, as the
manifest's notes said before the run. The substituted-grounding claims were removed before any run
because both Claude Opus 5.5 mapping tables failed their pre-registered gate.

## Post-run mirror URI check

Date: 2026-09-29 (UTC). A local clone of the commit that changed `mondo_semsql`'s uri to the published
mirror release, with no `data/` present:

```
$ git clone <orig> <fresh_clone> && cd <repro-lab in the clone>
$ ls data work 2>&1
ls: cannot access 'data': No such file or directory
ls: cannot access 'work': No such file or directory
$ py -3 harness/fetch_verify.py reese-2026-rescore
[fetch_verify] responses_zip: 9406802 bytes, sha256 OK
[fetch_verify] gold_tsv: 474639 bytes, sha256 OK
[fetch_verify] mondo_semsql: 242815274 bytes, sha256 OK
[fetch_verify] opus_mondo_map: 406599 bytes, sha256 OK
```

The `mondo_semsql` line of `work/reese-2026-rescore/provenance.json`:

```json
{
  "id": "mondo_semsql",
  "uri": "https://github.com/cyberfide-science/repro-lab/releases/download/data-mondo-semsql-2026-09-27/mondo.db.gz",
  "dest": "data/reese-2026/mondo.db.gz",
  "sha256_expected": "499f7078e4b60434e812500db709c8f03d52722c0d5543397947101b04bbefb0",
  "sha256_actual": "499f7078e4b60434e812500db709c8f03d52722c0d5543397947101b04bbefb0",
  "bytes": 242815274,
  "verified": true
}
```

The Exomiser manifest's `mondo_semsql` entry was checked textually rather than re-fetched (its 19.3 GB and
6.2 GB siblings make a second full download pointless): `diff` of the `uri`/`sha256`/`size_bytes` lines of
both manifests' `mondo_semsql` entries is empty, so one verified download stands for both.
