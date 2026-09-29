# Fresh-clone regeneration: `reese-2026-exomiser`

The repository was cloned into a scratch directory with no `data/` and no `work/` (both are gitignored),
and `HARNESS_APPROVE=1 py -3 run_all.py reese-2026-exomiser` was run there under the maintainer's written
pre-approval of the Exomiser run and its fresh-clone rerun (it answers the two download-size checkpoints,
`exomiser_2406_phenotype` and `exomiser_2406_hg19`, and the stage-duration checkpoint). The clone's HEAD
was `71ec8e5`, the commit that carries the report in this directory. One input was placed by hand before
the run: the pinned Mondo SemSQL file, at the manifest's
`file://data/manual/mondo-semsql-2026-09-27/mondo.db.gz`, because its mirror release was still pending at
clone time; `fetch_verify` then copied it and verified its sha256 like every other input. Below is the
logging script's own log, verbatim, with timestamps kept and line order unchanged; absolute host paths are
replaced by `<clone>/` (the fresh clone) or `<repo>/` (this repository).

```
start=2026-09-29T11:26:02Z
clone_dir=<clone>
cmd=HARNESS_APPROVE=1 py -3 -u run_all.py reese-2026-exomiser
2026-09-29T11:26:02Z [clone] git clone <repo> <clone>
2026-09-29T11:26:02Z Cloning into '<clone>'...
2026-09-29T11:26:03Z done.
2026-09-29T11:26:04Z [clone] HEAD=71ec8e5
2026-09-29T11:26:04Z [clone] ls data work: ls: cannot access 'data': No such file or directory ls: cannot access 'work': No such file or directory 
2026-09-29T11:26:04Z [clone] copied mondo.db.gz, sha256: 499f7078e4b60434e812500db709c8f03d52722c0d5543397947101b04bbefb0 *data/manual/mondo-semsql-2026-09-27/mondo.db.gz
2026-09-29T11:26:08Z [build_env] docker build -t repro-lab/reese-2026-exomiser targets/reese-2026-exomiser
2026-09-29T11:26:08Z [build_env] image repro-lab/reese-2026-exomiser id sha256:0950f1af3c499ad99a129bbc392f8e348045d75a8354e6e39bbbaf12d7d93bcf
2026-09-29T11:26:08Z [build_env] base eclipse-temurin@sha256:34d6aaf0fa4ef553c470234ec23c32c7d5c0f370c2bd4b0bf8a16838052d85f0; container python 3.12.14
2026-09-29T11:26:08Z [build_env] 0 difference(s) vs targets/reese-2026-exomiser/env-resolved.txt
2026-09-29T11:42:13Z [fetch_verify] exomiser_cli_14_0_1: 75878122 bytes, sha256 OK
2026-09-29T11:42:13Z [checkpoint] data 'exomiser_2406_phenotype' is 6.236618638 GB (> 5 GB limit). -- approved via HARNESS_APPROVE=1
2026-09-29T11:42:13Z [fetch_verify] exomiser_2406_phenotype: 6236618638 bytes, sha256 OK
2026-09-29T11:42:14Z [checkpoint] data 'exomiser_2406_hg19' is 19.329398823 GB (> 5 GB limit). -- approved via HARNESS_APPROVE=1
2026-09-29T11:42:14Z [fetch_verify] exomiser_2406_hg19: 19329398823 bytes, sha256 OK
2026-09-29T11:42:14Z [fetch_verify] phenopackets_tgz: 3412803 bytes, sha256 OK
2026-09-29T11:42:14Z [fetch_verify] gold_tsv: 474639 bytes, sha256 OK
2026-09-29T11:42:14Z [fetch_verify] responses_zip: 9406802 bytes, sha256 OK
2026-09-29T11:42:14Z [fetch_verify] mondo_semsql: 242815274 bytes, sha256 OK
2026-09-29T11:42:14Z [fetch_verify] opus_mondo_map: 406599 bytes, sha256 OK
2026-09-29T16:19:18Z [checkpoint] stage 'container_run' expected 615 min (> 30 min limit). -- approved via HARNESS_APPROVE=1
2026-09-29T16:19:18Z [run_pipeline] stage container_run: docker run --rm --network none --memory 16g -v <clone>/data/reese-2026:/work/data:ro -v <clone>/work/reese-2026-exomiser:/work/wk -v <clone>/out/reese-2026-exomiser:/work/out repro-lab/reese-2026-exomiser
2026-09-29T16:19:18Z [run_pipeline]   exit 0 in 16625.75 s; log at work/reese-2026-exomiser/logs/container_run.log
2026-09-29T16:19:18Z [run_pipeline] code_sha from the run's own output: 7a4dc1e06bf489f7815a873ef6c34a83c3b2e99b
2026-09-29T16:19:18Z [run_pipeline] extracted 29 metrics -> work/reese-2026-exomiser/results.json
2026-09-29T16:19:19Z [diff_claims] 0/3 claims within tolerance -> verdict: not_reproduced
2026-09-29T16:19:19Z [checkpoint] EX1 (EX1_exomiser_top1_frac): claimed 0.355, obtained 0.35449836946096297 [absolute 0.0005] -- needs human review before any outreach
2026-09-29T16:19:19Z [checkpoint] EX2 (EX2_exomiser_top3_frac): claimed 0.463, obtained 0.46019566468444273 [absolute 0.0005] -- needs human review before any outreach
2026-09-29T16:19:19Z [checkpoint] EX3 (EX3_exomiser_top10_frac): claimed 0.585, obtained 0.5697295223479762 [absolute 0.0005] -- needs human review before any outreach
2026-09-29T16:19:19Z [diff_claims] report.json validated against harness/schema/report.schema.json
2026-09-29T16:19:19Z [diff_claims] wrote reports/reese-2026-exomiser/report.json
2026-09-29T16:19:19Z [render_report] wrote reports/reese-2026-exomiser/report.md
2026-09-29T16:19:19Z [run_all] done: reports/reese-2026-exomiser/report.json, reports/reese-2026-exomiser/report.md
2026-09-29T16:19:19Z [compare] comparing clone reports against <repo>/reports/reese-2026-exomiser
2026-09-29T16:19:19Z [compare] report.md: identical
2026-09-29T16:19:19Z [compare] report.json: identical
2026-09-29T16:19:19Z [compare] results.csv and per_case.tsv: DIFFER
exit=0
comparison=report.md: identical | report.json: identical | results.csv and per_case.tsv: DIFFER
end=2026-09-29T16:19:19Z
```

The logged `[compare]` step only flags that `results.csv` and `per_case.tsv` differ; it does not show the
diff. The following masking functions and diffs were run separately, after the logged script completed,
from the fresh clone with `<repo>` the path of this repository, to show exactly what differs:

```
mask() { sed -E -e 's/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:+.Z-]{5,}/TIMESTAMP/g' -e 's/^- Wall time: .*/- Wall time: WALL/' "$1"; }
norm() { py -3 -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); d['generated_at']='X'; d['cost']['wall_minutes']=0; [p.update(fetched_at='X') for p in d['data_provenance']]; print(json.dumps(d,indent=2,sort_keys=True))" "$1"; }
$ diff <(mask reports/reese-2026-exomiser/report.md) <(mask <repo>/reports/reese-2026-exomiser/report.md) && echo "reese-2026-exomiser: identical"
reese-2026-exomiser: identical
$ diff <(norm reports/reese-2026-exomiser/report.json) <(norm <repo>/reports/reese-2026-exomiser/report.json) && echo "reese-2026-exomiser: report.json identical"
reese-2026-exomiser: report.json identical
$ cmp out/reese-2026-exomiser/per_case.tsv <repo>/out/reese-2026-exomiser/per_case.tsv && echo "per_case.tsv byte-identical"
per_case.tsv byte-identical
$ diff out/reese-2026-exomiser/results.csv <repo>/out/reese-2026-exomiser/results.csv
27c27
< exomiser_n_scored_pairs,79571
---
> exomiser_n_scored_pairs,79548
```

`report.md` and `report.json` regenerate identically (masked/normalised), and `per_case.tsv` is
byte-identical. `results.csv` differs on exactly one line: `exomiser_n_scored_pairs` is 79571 here against
79548 in the committed run. This is the sum of each worker's process-local (prediction, gold) memo misses
under `imap_unordered` case dispatch (score_exomiser.py), so it varies with scheduling between runs. It is
a declared non-deterministic work counter, excluded from the byte-identity check and used by no claim.
Every other line of `results.csv`, and every row of `per_case.tsv`, is byte-identical.

Negative schema test on the regenerated report:

```
$ py -3 harness/schema/test_negative.py reports/reese-2026-exomiser/report.json
cause_category='undiagnosed': 0 error(s):
tolerance=None: 1 error(s): None is not of type 'number'
```

The first line reports zero errors, and that is expected here: the `undiagnosed` mutation gives 0 errors
because claims[0] (EX1) is already `not_reproduced` with cause `undiagnosed`, so the mutation leaves a
valid report; the `tolerance=None` mutation is rejected.

`o1_subst_n_top1` is 1101 in this container's `out/reese-2026-exomiser/results.csv`, equal to
`o1_subst_n_top1` in `out/reese-2026-rescore/results.csv` (both containers ground the deposited o1-preview
answers under substituted grounding from the same committed Opus 5.5 table).

The tie-band range for each claim, read from `results.csv` at full precision:

- EX1: we could not obtain 35.5% at the pre-registered tie order (score, then a hash of the disease id);
  the closest we reached was 0.35449836946096297. The published value lies within the range our run gives
  when tied scores are ordered best-first and worst-first (0.3533474007289469 to 0.3769422597352772), so
  ordering inside ties is enough to account for the difference. (`EX1_exomiser_top1_frac`,
  `EX1_exomiser_top1_frac_pess`, `EX1_exomiser_top1_frac_opt`)
- EX2: we could not obtain 46.3% at the pre-registered tie order (score, then a hash of the disease id);
  the closest we reached was 0.46019566468444273. The published value lies within the range our run gives
  when tied scores are ordered best-first and worst-first (0.46019566468444273 to 0.4807212737387301), so
  ordering inside ties is enough to account for the difference. (`EX2_exomiser_top3_frac`,
  `EX2_exomiser_top3_frac_pess`, `EX2_exomiser_top3_frac_opt`)
- EX3: we could not obtain 58.5% at the pre-registered tie order (score, then a hash of the disease id);
  the closest we reached was 0.5697295223479762. The published value lies within the range our run gives
  when tied scores are ordered best-first and worst-first (0.5691540379819682 to 0.5896796470362555), so
  ordering inside ties is enough to account for the difference. (`EX3_exomiser_top10_frac`,
  `EX3_exomiser_top10_frac_pess`, `EX3_exomiser_top10_frac_opt`)

## Void run (not the reported run)

A harness run of `reese-2026-exomiser` started about 09:41Z and died about 14:16Z on 2026-09-28, with image
id `0950f1af3c499ad99a129bbc392f8e348045d75a8354e6e39bbbaf12d7d93bcf`. The harness process died with no
`run_log.json`, so it produced no report; its outputs were moved to `work/_void-run-2026-09-28/`. Its
`per_case.tsv` is `cmp`-identical to the committed `out/reese-2026-exomiser/per_case.tsv`, and its
`results.csv` carries `exomiser_n_scored_pairs` 79252 (a third, scheduling-dependent value; see above). The
committed report comes from the later logged run, `generated_at` 2026-09-29T02:25:50.239+00:00, which
equals the host log's end time. There was no choice between differing results: the void run's
`per_case.tsv` and the committed one agree exactly.

A separate, pre-harness analysis run in `work/reese-2026-smoke` (outside the harness, no report) failed
while reducing batch 190 and was resumed for batches 190-208 with `--memory 20g`. It produced the 40-row
verification sample behind `minimal_scoring_check.md` and no claim value.

## Post-run mirror URI check

Rerun 2026-09-29 (UTC), start 23:16:45, end 23:17:08. A local clone of the commit that changed
`mondo_semsql`'s uri to the published mirror release, HEAD `82d6fa3c6332b90e3cfba20a19bc2dc3decf68a1`
(`git rev-parse HEAD` in the clone), with no `data/` present:

```
$ git clone <repo> <clone> && cd <clone>
$ git rev-parse HEAD
82d6fa3c6332b90e3cfba20a19bc2dc3decf68a1
$ ls data work 2>&1
ls: cannot access 'data': No such file or directory
ls: cannot access 'work': No such file or directory
```

Re-running `fetch_verify` for `reese-2026-exomiser` would re-download its 19.3 GB and 6.2 GB Exomiser data
files for no reason: the `mondo_semsql` entry is checked textually instead, against the rescore target's
verified download in the same clone (`py -3 harness/fetch_verify.py reese-2026-rescore`, run and recorded
in `reports/reese-2026-rescore/fresh_clone.md`):

```
$ py -3 harness/fetch_verify.py reese-2026-rescore
[fetch_verify] responses_zip: 9406802 bytes, sha256 OK
[fetch_verify] gold_tsv: 474639 bytes, sha256 OK
[fetch_verify] mondo_semsql: 242815274 bytes, sha256 OK
[fetch_verify] opus_mondo_map: 406599 bytes, sha256 OK
```

The full `mondo_semsql` entry of `work/reese-2026-rescore/provenance.json`, including `fetched_at`:

```json
{
  "id": "mondo_semsql",
  "uri": "https://github.com/cyberfide-science/repro-lab/releases/download/data-mondo-semsql-2026-09-27/mondo.db.gz",
  "dest": "data/reese-2026/mondo.db.gz",
  "sha256_expected": "499f7078e4b60434e812500db709c8f03d52722c0d5543397947101b04bbefb0",
  "sha256_actual": "499f7078e4b60434e812500db709c8f03d52722c0d5543397947101b04bbefb0",
  "bytes": 242815274,
  "fetched_at": "2026-09-29T23:17:08.425+00:00",
  "verified": true
}
```

```
$ diff <(grep -A3 'id: mondo_semsql' targets/reese-2026-rescore/repro-target.yaml | grep -E 'uri:|sha256:|size_bytes:') \
       <(grep -A3 'id: mondo_semsql' targets/reese-2026-exomiser/repro-target.yaml | grep -E 'uri:|sha256:|size_bytes:')
$ echo $?  ->  0
```

The diff of the `uri`/`sha256`/`size_bytes` lines of this manifest's `mondo_semsql` entry against the
rescore manifest's is empty, so the one verified download stands for both. The scratch clone was deleted
after this check.
