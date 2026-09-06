# targets/dominguezconde-2022-celltypist/Dockerfile
# Base image pinned by digest (python:3.9-slim as pulled on 2026-09-06), the
# same base the repo's own Dockerfile at fe357564 uses. Differences from that
# Dockerfile, both deliberate and recorded in repro-target.yaml environment.notes:
#   1. celltypist is installed from the clone at the pinned SHA, not from an
#      unversioned `pip install celltypist` on PyPI. Its dependencies are still
#      resolved unpinned from requirements.txt, exactly as the project declares.
#   2. `celltypist --update-models` is NOT run: the model is fetched by its
#      versioned URL as a data file and hash-verified (see data[] in the manifest).
FROM python@sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b

ENV OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    PYTHONHASHSEED=0 PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends git build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work
RUN git clone https://github.com/Teichlab/celltypist.git \
 && cd celltypist && git checkout fe357564a6625d3b1732a022fd39f18e55696e80

RUN pip install "/work/celltypist" \
 && pip freeze > /work/env-resolved.txt \
 && python -c "import numpy; numpy.show_config()" > /work/numpy-show-config.txt 2>&1

COPY run.sh /work/run.sh
ENTRYPOINT ["bash", "/work/run.sh"]
