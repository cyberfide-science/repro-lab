# Reproducibility report: Systematic benchmarking demonstrates large language models have not reached the diagnostic accuracy of traditional rare-disease decision support tools

- DOI: 10.1038/s41431-026-02054-5
- Code: `7a4dc1e06bf489f7815a873ef6c34a83c3b2e99b`
- Generated: 2026-09-29T02:25:50.239+00:00

## Summary verdict: **not_reproduced**

0 of 3 claims within tolerance.

## Per-claim table

| id | figure | metric | claimed | obtained | tolerance | verdict | cause | extraction | evidence |
|---|---|---|---|---|---|---|---|---|---|
| EX1 | Figure 3 (medRxiv v3, PMC11302616) (Top-1, Exomiser) | EX1_exomiser_top1_frac | 0.355 | 0.35449836946096297 | absolute 0.0005 | not_reproduced | undiagnosed | manual | `work/reese-2026-exomiser/results.json` |
| EX2 | Figure 3 (medRxiv v3, PMC11302616) (Top-3, Exomiser) | EX2_exomiser_top3_frac | 0.463 | 0.46019566468444273 | absolute 0.0005 | not_reproduced | undiagnosed | manual | `work/reese-2026-exomiser/results.json` |
| EX3 | Figure 3 (medRxiv v3, PMC11302616) (Top-10, Exomiser) | EX3_exomiser_top10_frac | 0.585 | 0.5697295223479762 | absolute 0.0005 | not_reproduced | undiagnosed | manual | `work/reese-2026-exomiser/results.json` |

## Environment delta

None: every pinned component matched.

## Data provenance

| id | uri | bytes | sha256 verified | fetched |
|---|---|---|---|---|
| exomiser_cli_14_0_1 | https://github.com/exomiser/Exomiser/releases/download/14.0.1/exomiser-cli-14.0.1-distribution.zip | 75878122 | True | 2026-09-28T21:20:59.957+00:00 |
| exomiser_2406_phenotype | https://data.monarchinitiative.org/exomiser/data/2406_phenotype.zip | 6236618638 | True | 2026-09-28T21:24:50.317+00:00 |
| exomiser_2406_hg19 | https://data.monarchinitiative.org/exomiser/data/2406_hg19.zip | 19329398823 | True | 2026-09-28T21:36:40.460+00:00 |
| phenopackets_tgz | https://zenodo.org/records/15324355/files/phenopackets.tar.gz?download=1 | 3412803 | True | 2026-09-28T21:36:43.780+00:00 |
| gold_tsv | https://zenodo.org/records/15324355/files/correct_results.tsv?download=1 | 474639 | True | 2026-09-28T21:36:44.961+00:00 |
| responses_zip | https://zenodo.org/records/15324355/files/all_models_responses.zip?download=1 | 9406802 | True | 2026-09-28T21:36:49.279+00:00 |
| mondo_semsql | file://data/manual/mondo-semsql-2026-09-27/mondo.db.gz | 242815274 | True | 2026-09-28T21:36:49.581+00:00 |
| opus_mondo_map | file://targets/reese-2026-rescore/grounding/opus-mondo-map.tsv | 406599 | True | 2026-09-28T21:36:49.585+00:00 |

## Deviations log

- EX4: o1-preview answers are grounded by OAK exact matching, then the one-time Claude Opus 5.5 table, instead of CurateGPT/OpenAI embeddings (why: Same as reese-2026-rescore RS4-RS6: no run-time API call; the table is committed and hash-verified.; approved by Michael Wolfe, repro-lab maintainer, 2026-09-27)
- Opus mapping table (RS4-RS6, EX4): the echo check in grounding/build_opus_map.py compares echoed and input names after Unicode NFC normalisation, instead of byte-exact, from chunk 80 attempt 4 on (why: Chunk 80 failed 3/3 only because the input Kohlschuetter-Toenz entry used decomposed diacritics (u/o + U+0308) that Opus echoed precomposed. Exact match implies NFC match, so the 94 accepted chunks are unaffected; only chunk 80 reruns; table names and lookups keep the input string byte-for-byte. Committed before chunk 80 reruns.; approved by Michael Wolfe, repro-lab maintainer, 2026-09-27)
- Opus mapping table, attempt 1 (committed at 851a94d): failed the pre-registered gate, agreement with OAK 0.2628 against 0.90; the prompt told the model to abstain when unsure, and it returned no match for 1,323 of 1,876 OAK-resolvable names. RS4-RS6 and EX4 were removed. (why: Recorded so the substituted-grounding claims show their full history.; approved by Michael Wolfe, repro-lab maintainer, 2026-09-27)
- Opus mapping table, attempt 2 (the last): revised prompt, committed before any call, asks for the single best Mondo term plus a confidence (high/medium/low), and no match only when nothing plausible exists. The gate and its definition are unchanged; confidence is recorded but used neither by the gate nor by the lookup. RS4-RS6 and EX4 are restored only if this attempt passes. Result (grounding/attempt-2/opus-mondo-map.meta.json): agreement 0.3545 against 0.90, gate failed, so RS4-RS6 and EX4 stay removed; Opus now named a term for all but 7 of the 1,876 OAK-resolvable names, but 1,154 of them paired a correct label with a wrong or obsolete Mondo number and fail the validity rule. (why: Attempt 1 failed because of the abstention instruction, not the mapping procedure; one further attempt was authorised by the maintainer, with no third.; approved by Michael Wolfe, repro-lab maintainer, 2026-09-27)

## Time and cost

- Wall time: 288.983 min
- Agent tokens: 0
- Estimated cost: USD 0.0

## Human review required

- EX1: we could not obtain 0.355 for EX1_exomiser_top1_frac under the manifest's conditions; the closest we reached was 0.35449836946096297. Cause: undiagnosed.
- EX2: we could not obtain 0.463 for EX2_exomiser_top3_frac under the manifest's conditions; the closest we reached was 0.46019566468444273. Cause: undiagnosed.
- EX3: we could not obtain 0.585 for EX3_exomiser_top10_frac under the manifest's conditions; the closest we reached was 0.5697295223479762. Cause: undiagnosed.
