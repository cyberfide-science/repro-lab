untouched: n/a
date: 2026-09-06
host: Windows 11 Pro 10.0.26200, Docker Desktop 4.89.0 (Engine 29.7.2, linux/amd64), x86_64, 32 CPUs, 31 GB RAM, no GPU
image_id: n/a (not built)
manifest_commit: 93e65f4c18513ef7e42d5ac107ffe1566544f86b
command: n/a
exit_code: n/a
wall_time: n/a
first_error: |
  n/a
data_hashes_verified: n/a (not attempted; nothing was fetched)
notes: |
  Not attempted; the exit criterion was met by muzellec-2023-pydeseq2
  (runs/muzellec-2023-pydeseq2/untouched.md: untouched yes, exit 0). Per plan
  step 9 this fallback is built only if PyDESeq2 fails to run untouched, so
  it stays status: candidate. No Dockerfile or run.sh was written for it and
  none of its three fixture files was downloaded; the manifest's sha256
  placeholders are intentionally unfilled.
