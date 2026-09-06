untouched: n/a
date: 2026-09-06
host: Windows 11 Pro 10.0.26200, Docker Desktop 4.89.0 (Engine 29.7.2, linux/amd64), x86_64, 32 CPUs, 31 GB RAM, no GPU
image_id: n/a (not built; no Dockerfile exists for this target)
manifest_commit: 93e65f4c18513ef7e42d5ac107ffe1566544f86b
command: n/a
exit_code: n/a
wall_time: n/a
first_error: |
  n/a
data_hashes_verified: n/a (not attempted; nothing was fetched)
notes: |
  Not attempted. The target fails the selection gate in docs/CONVENTIONS.md:
  total 8, below
  the threshold of 11, with zeros on C2 (no licence: gh api
  repos/neurorestore/DE-analysis returns license null and the tree at 167f55a
  has no LICENSE blob) and C3 (no environment file of any kind: the tree is
  .gitignore, R/ and README.md only), both inside the first four criteria.
  Status in the manifest is deferred.

  Cost declined by not attempting it: building an unpinned GPL-3.0 Seurat
  fork (github.com/jordansquair/Seurat, named in R/functions/run_DE.R) from
  source, reconstructing an R 4.x environment from nothing, and doing so for
  an analysis repo that carries no licence at all, which leaves the
  redistribution position of any fixed fork unclear. Nothing was cloned,
  downloaded or built; the manifest's <fill> placeholders are intentional.
