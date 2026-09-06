#!/bin/bash
# targets/muzellec-2023-pydeseq2/run.sh - the whole untouched test, no manual steps.
set -euo pipefail
mkdir -p /work/out
cd /work/PyDESeq2
echo "== git HEAD: $(git rev-parse HEAD)"
echo "== python: $(python --version)"
echo "== pytest tests/ (the authors' own suite against the committed R DESeq2 v1.34.0 reference CSVs)"
pytest tests/ -q --junitxml=/work/out/pytest.xml
echo "== extract_results.py (repro-lab's own script; public API only)"
python /work/extract_results.py --out /work/out/results.csv
cat /work/out/results.csv
echo "== git status --porcelain inside the clone after the run (empty means untouched):"
git status --porcelain
