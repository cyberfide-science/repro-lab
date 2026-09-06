#!/bin/bash
# targets/dominguezconde-2022-celltypist/run.sh - the manifest's annotate stage.
set -euo pipefail
mkdir -p /work/out
cd /work
echo "== clone HEAD: $(git -C /work/celltypist rev-parse HEAD)"
echo "== python: $(python --version)"
python -c "import sklearn, scanpy, numpy, pandas; print('scikit-learn', sklearn.__version__, '| scanpy', scanpy.__version__, '| numpy', numpy.__version__, '| pandas', pandas.__version__)"
celltypist --indata /work/data/celltypist/demo_2000_cells.h5ad \
           --model /work/data/celltypist/Immune_All_Low.pkl \
           --outdir /work/out/
echo "== files written to /work/out:"
ls -l /work/out
echo "== git status --porcelain inside the clone after the run (empty means untouched):"
git -C /work/celltypist status --porcelain
