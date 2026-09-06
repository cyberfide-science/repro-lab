untouched: yes
date: 2026-09-06
host: Windows 11 Pro 10.0.26200, Docker Desktop 4.89.0 (Engine 29.7.2, linux/amd64), x86_64, 32 CPUs, 31 GB RAM, no GPU
image_id: sha256:e544f6ff44378f8334530aac3bb511ffdbb38d920146ecb75ad20773d68c41ff
manifest_commit: 93e65f4c18513ef7e42d5ac107ffe1566544f86b
command: docker run --rm -v "$(pwd -W)/data:/work/data:ro" -v "$(pwd -W)/out/muzellec-2023-pydeseq2:/work/out" repro-lab/muzellec-2023-pydeseq2
exit_code: 0
wall_time: 1m00s
first_error: |
  none
data_hashes_verified: yes
notes: |
  Build: docker build -t repro-lab/muzellec-2023-pydeseq2 targets/muzellec-2023-pydeseq2
  exited 0 in 72s (log: build.log). Clone HEAD inside the image is
  4426e4db990db1c511de3b1b9b7a514989663dad; git status --porcelain inside the
  clone printed nothing both in the built image and at the end of the run.

  Run: the authors' own suite, pytest tests/ -q, reported "65 passed in
  55.14s" (out/pytest.xml: tests=65 errors=0 failures=0 skipped=0). No
  DeprecationWarning was promoted to an error by filterwarnings = ["error"];
  the hazard predicted in the manifest did not fire on this resolution.
  Then extract_results.py (repro-lab's script, public API only) wrote
  out/results.csv:
    P1_log2FoldChange_gene1    0.632812476644658   claim 0.632812315254828, rel diff 2.6e-7, tol 0.02  -> inside
    P2_log10_padj_gene2       -2.783684562340294   claim -2.783680, abs diff 4.6e-6, tol 0.3         -> inside
    P3_size_factor_sample1     1.228980937268269   claim 1.22898093726827, rel diff 9e-16, tol 0.02  -> inside
    P4_top3_genes_by_abs_stat  gene5;gene2;gene4   claim [gene5, gene2, gene4], tau distance 0, tol 0 -> inside
  All four observed values are inside their pre-registered tolerances, so
  checkpoint 3 (out-of-tolerance claim) did not fire.

  Data: both files fetched by the manifest URIs, hashed with hash_data.py
  (09d632cc...137c3 3919 B; d96a5bbf...f0b6 1915 B). sha256sum of the clone's
  own datasets/synthetic/ copies inside the image gives the identical digests,
  so the fetched bytes and the bytes at the pinned SHA are the same file.
  The run reads the clone's copy (pydeseq2.utils.load_example_data), so the
  data mount is provenance, not an input.

  Environment: Python 3.12.14 in python:3.12-slim pinned by digest; resolved
  set in targets/muzellec-2023-pydeseq2/env-resolved.txt (numpy 2.5.3,
  pandas 3.0.5, scipy 1.18.1, scikit-learn 1.9.0, anndata 0.13.3.post0,
  formulaic 1.2.2, formulaic-contrasts 1.0.0, matplotlib 3.11.1, pytest 9.1.1).
  BLAS: scipy-openblas 0.3.34 (numpy.show_config in host.txt). Threads:
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONHASHSEED=0.
  Seeds: the pydeseq2/ package has no RNG calls (grep for np.random,
  random.seed, default_rng, RandomState, manual_seed finds none); the tests
  seed themselves (np.random.seed(42), default_rng(42)) for synthetic edge
  cases only. The reference pipeline is deterministic.

  Commit ordering: tolerances were pre-registered in c7d4385 (16:12:50-04:00);
  Dockerfile in 21b36ef; hashes in 93e65f4 (16:19:22-04:00); the run wrote
  out/ at 16:20 local. The command above is the Git Bash on Windows form
  ($(pwd -W) yields C:/... for Docker Desktop); on Linux/macOS use $PWD.
  Shell env: MSYS_NO_PATHCONV=1 was set in the host shell purely to stop Git
  Bash rewriting /work/... container paths in docker CLI arguments; it is not
  visible inside the container and changes nothing the pipeline does.

  Fresh-clone test (docs/CONVENTIONS.md, untouched test), 2026-09-06, following
  only README.md: git clone of this repo at 1634a16 into a scratch directory
  outside the tree; run.sh checked out as LF; docker build --no-cache exited
  0 in 56s and produced a new image id sha256:c669b0e4f23ee75c4c45d5eca16abf
  b11431a0b13bef8f17c17749e837084912 (a rebuild, so a new id; the one above
  is the recorded run's); the two data files re-fetched by URI and re-hashed
  by hash_data.py to the same digests (git diff on the manifest empty);
  docker run exited 0 in 58s with "65 passed in 51.96s", wrote pytest.xml and
  results.csv with byte-identical claim values, and the clone's git status
  was empty. pip freeze inside the fresh image is identical to the committed
  env-resolved.txt (same resolution one hour later). PASS.
