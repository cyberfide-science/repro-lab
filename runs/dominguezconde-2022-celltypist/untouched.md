untouched: yes
date: 2026-09-06 20:47 UTC (re-run after review round 1; first run 20:20 UTC on image sha256:97b24331...1038)
host: Windows 11 Pro 10.0.26200, Docker Desktop 4.89.0 (Engine 29.7.2, linux/amd64), x86_64, 32 CPUs, 31 GB RAM, no GPU
image_id: sha256:85318092ccee03d898a49529718679ea51c60e0f6385b9981fa7207cc0772526
manifest_commit: 93e65f4c18513ef7e42d5ac107ffe1566544f86b
command: MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd -W)/data:/work/data:ro" -v "$(pwd -W)/out/dominguezconde-2022-celltypist:/work/out" repro-lab/dominguezconde-2022-celltypist
exit_code: 0
wall_time: 0m07s
first_error: |
  none
data_hashes_verified: yes
notes: |
  Build: docker build -t repro-lab/dominguezconde-2022-celltypist
  targets/dominguezconde-2022-celltypist exited 0 (log: build.log). The
  first build, 20:18 UTC, took 110s; this rebuild at 20:46 UTC took 2s
  because every layer up to and including pip install was served from the
  first build's cache and only the COPY run.sh layer changed. Clone HEAD
  fe357564a6625d3b1732a022fd39f18e55696e80; git status --porcelain inside
  the clone printed nothing in the image and at the end of the run.

  Why the re-run: review round 1 (finding 3) noted that T1 and T2 were only
  confirmed by an ad-hoc probe outside run.sh. run.sh now carries repro-lab's
  own read-only line, before the celltypist call, that loads the model file
  and prints len(cell_types) and len(features); the probe reads the model
  only, edits nothing in the clone, and is now part of the recorded run.

  Run: celltypist --indata demo_2000_cells.h5ad --model Immune_All_Low.pkl
  --outdir out/ (the manifest's annotate stage) exited 0 and wrote
  predicted_labels.csv (47,433 B), probability_matrix.csv (4,369,666 B) and
  decision_matrix.csv (3,813,844 B) to out/dominguezconde-2022-celltypist/.
  Claims, all observed exactly, each cited from stdout.txt:
    T1 cell types in model:           stdout line 4 "model cell_types 98 | model features 6639"; claim 98,   tol 0 -> match
    T2 features in model:             stdout line 4 "model cell_types 98 | model features 6639"; claim 6639, tol 0 -> match
    T3 features used for prediction: stdout "5645 features used for prediction"; claim 5645, tol 0 -> match
    T4 genes in demo input:           stdout "2000 cells and 18950 genes";        claim 18950, tol 0 -> match
  T1 is also corroborated by the 98 label columns of probability_matrix.csv.
  The model prints date 2022-07-16 00:20:42.927778, version v2, matching the
  tutorial notebook's stored output.

  manifest_commit above is the SHA whose manifest this run used. The manifest
  text was later amended for review round 1 findings 4 (deviations list) and
  5 (results.file placeholder) without touching claims or tolerances; the
  claim values and tolerances checked here are those of 93e65f4c.

  The unpickling failure predicted as UNCERTAIN in the manifest (open issue 164,
  scikit-learn 1.8) did NOT fire here, and the reason is worth recording:
  the base image is python:3.9-slim (the repo's own choice), and pip's
  unpinned resolution on Python 3.9 tops out at scikit-learn 1.6.1, numpy
  2.0.2, scanpy 1.10.3, pandas 2.3.3 (env-resolved.txt). The same Dockerfile
  on a newer Python would resolve a newer scikit-learn and the outcome could
  differ. That is the pinning gap the manifest describes, observed from the
  side where it happens to work.

  Two choices in OUR Dockerfile, not in the paper's code, recorded in the
  Dockerfile header and the manifest's environment.notes: celltypist is
  installed from the clone at the pinned SHA instead of an unversioned PyPI
  `pip install celltypist`; and --update-models is not run, the model being
  fetched by its versioned URL and hash-verified as a data file instead.
  The model was passed by explicit path and celltypist accepted it without
  the registry, so the finding the manifest warned about did not occur.

  Data: both files fetched by the manifest URIs and hashed with hash_data.py
  (demo_2000_cells.h5ad 167d038d...ae9b 35,730,948 B; Immune_All_Low.pkl
  290874d3...6502 2,824,990 B); sizes equal the content-lengths measured on
  2026-09-06 with curl -sIL. BLAS: scipy-openblas 0.3.27 (numpy 2.0.2). Threads: OMP/MKL/
  OPENBLAS_NUM_THREADS=1, PYTHONHASHSEED=0. Seeds: the annotate path used
  here (celltypist/classifier.py, models.py Model.load/predict) has no RNG
  call; np.random.seed/choice appear only in samples.py, train.py and
  models.py::convert, none of which this run executes. The Leiden-based
  --majority-voting option, which is seed-dependent, was not used.

  This target is not the end-to-end untouched demonstration (that is
  muzellec-2023-pydeseq2). Same Windows command-form note as that record:
  $(pwd -W) is the Git Bash form; on Linux/macOS use $PWD.
