# targets/muzellec-2023-pydeseq2/Dockerfile
# Base image pinned by digest (python:3.12-slim as pulled on 2026-09-06).
# Python 3.12 is inside the project's declared range (requires-python >=3.11,
# classifiers 3.11/3.12/3.13 in pyproject.toml at 4426e4db).
FROM python@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea

ENV OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    PYTHONHASHSEED=0 PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work
RUN git clone https://github.com/owkin/PyDESeq2.git \
 && cd PyDESeq2 && git checkout 4426e4db990db1c511de3b1b9b7a514989663dad

# Editable install so pydeseq2.utils.load_example_data resolves the clone's own
# datasets/synthetic/ directory (it looks one level above the package). The
# [dev] extra is the project's own test group (pytest etc.).
RUN pip install -e "/work/PyDESeq2[dev]" \
 && pip freeze > /work/env-resolved.txt \
 && python -c "import numpy; numpy.show_config()" > /work/numpy-show-config.txt 2>&1

COPY run.sh /work/run.sh
COPY extract_results.py /work/extract_results.py
ENTRYPOINT ["bash", "/work/run.sh"]
