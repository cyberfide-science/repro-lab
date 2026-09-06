# Contributing

Contributions are welcome as issues or pull requests.

A new target is a `targets/<slug>/` directory containing `repro-target.yaml`,
`Dockerfile` and `run.sh`, following `docs/CONVENTIONS.md`. Claims and
tolerances are committed before any run, so the commit that fixed them predates
the run record in `runs/<slug>/untouched.md`.

Rules that apply to every change:

- Never edit the paper's code inside an image. If the paper's procedure does
  not run as shipped, record the first error; do not fix it.
- Fill `sha256` with `hash_data.py`, never by hand.
- Pull requests that change a claim value or tolerance after a run has been
  recorded against it will not be merged.
