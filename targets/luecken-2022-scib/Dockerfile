# targets/luecken-2022-scib/Dockerfile
# The Unit 1 brief section 5.1 skeleton, unchanged except for the digest pin
# (condaforge/miniforge3:24.3.0-0 as pulled on 2026-09-06; git 2.25.1 and
# mamba 1.5.8 are already in the image). The env file is the paper's own
# envs/scIB-python-paper.yml at e97631a, used as-is. It is NOT edited here.
FROM condaforge/miniforge3@sha256:f412616c712b00c09b4fdfd3001941d1876dfed5ab821bcf1e48ada60b70b7cb

ENV OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    PYTHONHASHSEED=0

WORKDIR /work
RUN git clone https://github.com/theislab/scib-pipeline.git \
 && cd scib-pipeline && git checkout e97631a478e063883cee5db0dcebbf42d8268ab0

RUN mamba env create -f scib-pipeline/envs/scIB-python-paper.yml \
 && mamba clean -afy
SHELL ["conda", "run", "-n", "scIB-python-paper", "/bin/bash", "-c"]

RUN pip freeze > /work/env-resolved.txt
COPY run.sh /work/run.sh
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "scIB-python-paper", "bash", "/work/run.sh"]
