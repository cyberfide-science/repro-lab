# Reproducibility report: Systematic benchmarking demonstrates large language models have not reached the diagnostic accuracy of traditional rare-disease decision support tools

- DOI: 10.1038/s41431-026-02054-5
- Code: `bd7146d15798b4dd968fd64bc9a42e6971aa8fae`
- Generated: 2026-09-28T08:18:57.404+00:00

## Summary verdict: **not_reproduced**

0 of 3 claims within tolerance.

## Per-claim table

| id | figure | metric | claimed | obtained | tolerance | verdict | cause | extraction | evidence |
|---|---|---|---|---|---|---|---|---|---|
| RS1 | Figure 3 (medRxiv v3, PMC11302616) (Top-1, o1 preview — offline floor (OAK exact match only; CurateGPT step not run)) | RS1_o1_top1_frac_floor | 0.236 | 0.20161135622482257 | absolute 0.0005 | not_reproduced | undiagnosed | manual | `work/reese-2026-rescore/results.json` |
| RS2 | Figure 3 (medRxiv v3, PMC11302616) (Top-3, o1 preview — offline floor (OAK exact match only; CurateGPT step not run)) | RS2_o1_top3_frac_floor | 0.312 | 0.2649146364857088 | absolute 0.0005 | not_reproduced | undiagnosed | manual | `work/reese-2026-rescore/results.json` |
| RS3 | Figure 3 (medRxiv v3, PMC11302616) (Top-10, o1 preview — offline floor (OAK exact match only; CurateGPT step not run)) | RS3_o1_top10_frac_floor | 0.368 | 0.2973335891041627 | absolute 0.0005 | not_reproduced | undiagnosed | manual | `work/reese-2026-rescore/results.json` |

## Environment delta

None: every pinned component matched.

## Data provenance

| id | uri | bytes | sha256 verified | fetched |
|---|---|---|---|---|
| responses_zip | https://zenodo.org/records/15324355/files/all_models_responses.zip?download=1 | 9406802 | True | 2026-09-28T07:00:24.409+00:00 |
| gold_tsv | https://zenodo.org/records/15324355/files/correct_results.tsv?download=1 | 474639 | True | 2026-09-28T07:00:25.552+00:00 |
| mondo_semsql | file://data/manual/mondo-semsql-2026-09-27/mondo.db.gz | 242815274 | True | 2026-09-28T07:00:25.837+00:00 |
| opus_mondo_map | file://targets/reese-2026-rescore/grounding/opus-mondo-map.tsv | 406599 | True | 2026-09-28T07:00:25.839+00:00 |

## Deviations log

- RS1-RS3: answer lines are grounded to Mondo by OAK exact matching only; malco's CurateGPT fallback is not run (use_ontogpt_grounding=False) (why: The fallback queries an OpenAI embedding index at run time; the scored run makes no API call (--network none). Derived from the code: this can only lower the counts.; approved by Michael Wolfe, repro-lab maintainer, 2026-09-27)
- RS4-RS6: lines OAK cannot ground are mapped with a one-time Claude Opus 5.5 table (grounding/opus-mondo-map.tsv, built with Claude Code headless under OAuth) instead of CurateGPT/OpenAI embeddings (why: Reproduces the role of the paper's fallback step without a run-time API call; the table was built, validated (agreement with OAK on OAK-resolved names >= 0.90, fixed before the call) and committed before this run. It can move the counts in either direction.; approved by Michael Wolfe, repro-lab maintainer, 2026-09-27)
- Opus mapping table (RS4-RS6, EX4): the echo check in grounding/build_opus_map.py compares echoed and input names after Unicode NFC normalisation, instead of byte-exact, from chunk 80 attempt 4 on (why: Chunk 80 failed 3/3 only because the input Kohlschuetter-Toenz entry used decomposed diacritics (u/o + U+0308) that Opus echoed precomposed. Exact match implies NFC match, so the 94 accepted chunks are unaffected; only chunk 80 reruns; table names and lookups keep the input string byte-for-byte. Committed before chunk 80 reruns.; approved by Michael Wolfe, repro-lab maintainer, 2026-09-27)
- Opus mapping table, attempt 1 (committed at 851a94d): failed the pre-registered gate, agreement with OAK 0.2628 against 0.90; the prompt told the model to abstain when unsure, and it returned no match for 1,323 of 1,876 OAK-resolvable names. RS4-RS6 and EX4 were removed. (why: Recorded so the substituted-grounding claims show their full history.; approved by Michael Wolfe, repro-lab maintainer, 2026-09-27)
- Opus mapping table, attempt 2 (the last): revised prompt, committed before any call, asks for the single best Mondo term plus a confidence (high/medium/low), and no match only when nothing plausible exists. The gate and its definition are unchanged; confidence is recorded but used neither by the gate nor by the lookup. RS4-RS6 and EX4 are restored only if this attempt passes. Result (grounding/attempt-2/opus-mondo-map.meta.json): agreement 0.3545 against 0.90, gate failed, so RS4-RS6 and EX4 stay removed; Opus now named a term for all but 7 of the 1,876 OAK-resolvable names, but 1,154 of them paired a correct label with a wrong or obsolete Mondo number and fail the validity rule. (why: Attempt 1 failed because of the abstention instruction, not the mapping procedure; one further attempt was authorised by the maintainer, with no third.; approved by Michael Wolfe, repro-lab maintainer, 2026-09-27)

## Time and cost

- Wall time: 78.517 min
- Agent tokens: 0
- Estimated cost: USD 0.0

## Human review required

- RS1: we could not obtain 0.236 for RS1_o1_top1_frac_floor under the manifest's conditions; the closest we reached was 0.20161135622482257. Cause: undiagnosed.
- RS2: we could not obtain 0.312 for RS2_o1_top3_frac_floor under the manifest's conditions; the closest we reached was 0.2649146364857088. Cause: undiagnosed.
- RS3: we could not obtain 0.368 for RS3_o1_top10_frac_floor under the manifest's conditions; the closest we reached was 0.2973335891041627. Cause: undiagnosed.
