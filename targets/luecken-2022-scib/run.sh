#!/bin/bash
# targets/luecken-2022-scib/run.sh - the paper's own entrypoint, unchanged.
# Data is expected under /work/data (mounted read-only). The paper config
# points at absolute Theis-lab HPC paths, which is one of the recorded blockers.
set -euo pipefail
mkdir -p /work/out
cd /work/scib-pipeline
echo "== git HEAD: $(git rev-parse HEAD)"
snakemake --configfile configs/reproduce_paper.yaml -j 1
echo "== git status --porcelain inside the clone after the run (empty means untouched):"
git status --porcelain
