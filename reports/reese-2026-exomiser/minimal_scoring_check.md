# Minimal against full Exomiser scoring: pre-registered check

Run before the scored run, on the full-cohort item lists of an analysis run made outside the harness
(the same image, `--network none`, `--memory 20g`, the same `score_exomiser.py` as committed at c7b83aa),
with `SCORERS=12 python score_exomiser.py verify`. The sample: rows 0001-0020 (the audit rows) plus the 20
other rows whose tie group at the deciding score g is largest, ties broken by row number. Every item of
those 40 rows was scored with malco's `score_grounded_result` ("full"), and compared with the minimal
item set the scored run uses ("minimal": Step A up to the first correct item or rank 10, then the rest of
the tie group at g). Ranks are shown capped at 10 (">10" means not in the top 10); R is the point rank
under the tie rule, O and P the optimistic and pessimistic ends of the tie band. The pass condition, fixed
before the check, is agreement on all 40 rows.

The check's own output, unedited:

```
minimal scoring of all 5212 cases: 80721 (item, gold) pairs in 63.5 min on 12 processes; full scoring of the 40 sample rows: 129009 distinct pairs; agreement 40 of 40
```

| row | set | tie group at g | minimal R / O / P | full R / O / P | agree |
|---|---|---|---|---|---|
| 0001 | audit | 1057 | >10 / 1 / >10 | >10 / 1 / >10 | yes |
| 0002 | audit | 1 | 1 / 1 / 1 | 1 / 1 / 1 | yes |
| 0003 | audit | 1 | 1 / 1 / 1 | 1 / 1 / 1 | yes |
| 0004 | audit | 1 | 2 / 2 / 2 | 2 / 2 / 2 | yes |
| 0005 | audit | 1 | 3 / 3 / 3 | 3 / 3 / 3 | yes |
| 0006 | audit | 1 | 1 / 1 / 1 | 1 / 1 / 1 | yes |
| 0007 | audit | 1 | 1 / 1 / 1 | 1 / 1 / 1 | yes |
| 0008 | audit | 1 | 1 / 1 / 1 | 1 / 1 / 1 | yes |
| 0009 | audit | 1 | 2 / 2 / 2 | 2 / 2 / 2 | yes |
| 0010 | audit | 1057 | >10 / 1 / >10 | >10 / 1 / >10 | yes |
| 0011 | audit | 1 | 9 / 9 / 9 | 9 / 9 / 9 | yes |
| 0012 | audit | 1 | 7 / 7 / 7 | 7 / 7 / 7 | yes |
| 0013 | audit | 1 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0014 | audit | 1 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0015 | audit | 1 | 2 / 2 / 2 | 2 / 2 / 2 | yes |
| 0016 | audit | 1 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0017 | audit | 44 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0018 | audit | 1 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0019 | audit | 1 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0020 | audit | 1 | 7 / 7 / 7 | 7 / 7 / 7 | yes |
| 2096 | largest tie | 2290 | >10 / 1 / >10 | >10 / 1 / >10 | yes |
| 4938 | largest tie | 2290 | >10 / 1 / >10 | >10 / 1 / >10 | yes |
| 1482 | largest tie | 1706 | >10 / 1 / >10 | >10 / 1 / >10 | yes |
| 5180 | largest tie | 1706 | >10 / 1 / >10 | >10 / 1 / >10 | yes |
| 0181 | largest tie | 1485 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0289 | largest tie | 1485 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0873 | largest tie | 1485 | >10 / 1 / >10 | >10 / 1 / >10 | yes |
| 1275 | largest tie | 1485 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 2965 | largest tie | 1485 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0256 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0326 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0480 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 0540 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 1119 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 1234 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 1434 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 1537 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 1648 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 1798 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
| 2118 | largest tie | 1451 | >10 / >10 / >10 | >10 / >10 / >10 | yes |
