untouched: no
date: 2026-09-06
host: Windows 11 Pro 10.0.26200, Docker Desktop 4.89.0 (Engine 29.7.2, linux/amd64), x86_64, 32 CPUs, 31 GB RAM, no GPU
image_id: n/a (docker build failed at Dockerfile:15, no image was produced)
manifest_commit: 93e65f4c18513ef7e42d5ac107ffe1566544f86b
command: docker build --progress=plain --no-cache -t repro-lab/luecken-2022-scib targets/luecken-2022-scib
exit_code: 1
wall_time: 5m06s
first_error: |
  fatal: unable to connect to github.com: github.com[0: 140.82.112.3]: errno=Connection refused
  during "git clone --filter=blob:none --quiet git://github.com/theislab/scib.git" run by pip for
  scib-pipeline/envs/scIB-python-paper.yml pip block line 1 (git+git://github.com/theislab/scib.git@0.2.0),
  inside `mamba env create -f scib-pipeline/envs/scIB-python-paper.yml` at targets/luecken-2022-scib/Dockerfile:15
data_hashes_verified: n/a (build failed before the run; the 5 GB checkpoint fired on the 20.1 GB figshare record and the user chose to skip the download)
notes: |
  Outcome matches the manifest's first predicted error: the pip stage of the
  paper's own environment file fails because GitHub no longer serves the
  unauthenticated git:// protocol. The exact pip line, the clone attempt and
  the refusal are in stdout.txt (the full docker build log, 5.6 KB).

  Finding against the manifest's second predicted error: the conda solver did NOT fail. mamba 1.5.8 on
  conda-forge + bioconda solved python=3.7 with numba<=0.46, scvi=0.6.7,
  r-seurat=3.1.1 etc. in about 33 s and downloaded/extracted the packages
  (including CUDA/cuDNN pulled in by the scvi/tensorflow pins) in about 3.5
  minutes. Only the pip block failed. No env-resolved.txt exists because the
  environment was never completed; a partial conda solve is not the paper's
  environment.

  Not fixed, on purpose: the obvious change (git+https://) is an edit to a
  file in the paper's repo and is a decision for the harness, not for this
  record. The Dockerfile is the skeleton in docs/CONVENTIONS.md with the base
  image pinned by
  digest; envs/scIB-python-paper.yml was used as-is. The second, independent
  blocker recorded in the manifest (configs/reproduce_paper.yaml points at
  absolute Theis-lab HPC paths) was not reached.

  Data checkpoint: the figshare record 10.6084/m9.figshare.12420968 is
  20,125,347,347 bytes (DataCite), above checkpoints.max_download_gb: 5, and
  the per-file breakdown could not be obtained (HTTP 403 on every figshare
  endpoint). The checkpoint fired and the user decided to skip the download.
  Nothing was fetched from figshare; the manifest's path and sha256 remain
  placeholders, and hash_data.py reports that path as MISSING by design.

  run.sh (snakemake --configfile configs/reproduce_paper.yaml -j 1) is
  committed but was never executed.
