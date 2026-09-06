#!/bin/bash
# targets/dominguezconde-2022-celltypist/run.sh - the manifest's annotate stage.
set -euo pipefail
mkdir -p /work/out
cd /work
echo "== git HEAD: $(git -C /work/celltypist rev-parse HEAD)"
echo "== python: $(python --version)"
python -c "import sklearn, scanpy, numpy, pandas; print('scikit-learn', sklearn.__version__, '| scanpy', scanpy.__version__, '| numpy', numpy.__version__, '| pandas', pandas.__version__)"
# repro-lab's own read-only probe of the model file, so that T1 (cell types) and
# T2 (features) are derivable from this run's stdout rather than a post-run check.
python -c "import celltypist; m=celltypist.models.Model.load('/work/data/celltypist/Immune_All_Low.pkl'); print('model cell_types', len(m.cell_types), '| model features', len(m.features))"
celltypist --indata /work/data/celltypist/demo_2000_cells.h5ad \
           --model /work/data/celltypist/Immune_All_Low.pkl \
           --outdir /work/out/ 2>&1 | tee /work/out/annotate.log
echo "== files written to /work/out:"
ls -l /work/out
echo "== extract_results.py (repro-lab's own script; public API and this run's own log)"
python /work/extract_results.py --model /work/data/celltypist/Immune_All_Low.pkl \
                                --annotate-log /work/out/annotate.log \
                                --out /work/out/results.csv
cat /work/out/results.csv
echo "== git status --porcelain inside the clone after the run (empty means untouched):"
git -C /work/celltypist status --porcelain
