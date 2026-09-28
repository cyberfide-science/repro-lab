# targets/reese-2026-exomiser/Dockerfile
# Java: Eclipse Temurin 17 JRE (eclipse-temurin:17-jre as pulled on 2026-09-27; 17.0.20.1+1), by digest,
# copied into the Python image. Exomiser 14.0.1 requires Java 17 or later.
FROM eclipse-temurin@sha256:34d6aaf0fa4ef553c470234ec23c32c7d5c0f370c2bd4b0bf8a16838052d85f0 AS jre

# Base image pinned by digest (python:3.12-slim as pulled on 2026-09-27; Python 3.12.14), the same as
# reese-2026-rescore. pheval.llm's pyproject.toml at bd7146d declares python = "^3.12".
FROM python@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f

ENV OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    PYTHONHASHSEED=0 PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1

COPY --from=jre /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk

# build-essential: chroma-hnswlib 0.7.3 (pinned in malco's lock) is compiled from its sdist.
# unzip: the Exomiser distribution and the 2406 data zips are extracted in the run.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git build-essential unzip \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work
# The tag clone exists only so that run.sh's first line reports the commit of the released code; the
# program that runs is the release's distribution zip (a hash-verified data[] entry).
RUN git clone --depth 1 --branch 14.0.1 https://github.com/exomiser/Exomiser.git
RUN git clone https://github.com/monarch-initiative/pheval.llm.git \
 && cd pheval.llm && git checkout bd7146d15798b4dd968fd64bc9a42e6971aa8fae

# malco's poetry.lock installed unchanged, exactly as in reese-2026-rescore.
RUN python -m venv /opt/poetry && /opt/poetry/bin/pip install poetry==1.8.4 \
 && python -m venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv PATH=/opt/venv/bin:/opt/java/openjdk/bin:$PATH
RUN cd /work/pheval.llm \
 && /opt/poetry/bin/poetry config virtualenvs.create false \
 && POETRY_REQUESTS_TIMEOUT=300 /opt/poetry/bin/poetry install --only main --no-interaction \
 && test -z "$(git status --porcelain)" \
 && pip freeze > /work/env-resolved.txt

# Output only: keeps malco's tqdm progress bars out of the committed scorer.log.
ENV TQDM_DISABLE=1
COPY cases.tsv output-options.yml application.properties /work/
COPY run.sh score_exomiser.py /work/
ENTRYPOINT ["bash", "/work/run.sh"]
