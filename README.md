# repro-lab

Can a published computational pipeline run untouched, from a pinned manifest,
in a fresh container, with its claims and tolerances written down before the
first run? This is a repository of scripts and records that tests exactly that,
one paper at a time. It is not a package.

Each `targets/<slug>/` holds a `repro-target.yaml` manifest (pinned commit, data
URIs + sha256, pre-registered claims and tolerances, selection score), a
`Dockerfile` and a `run.sh`. Each `runs/<slug>/` holds the `untouched.md` record
and the captured log. Paper code is cloned inside the image at build time and is
never edited; data is mounted read-only at run time. A failure is recorded with
its first error, not fixed. The rules are in `docs/CONVENTIONS.md`.

## Layout

```
targets/<slug>/   repro-target.yaml, Dockerfile, run.sh, env-resolved.txt, host.txt
runs/<slug>/      untouched.md, stdout.txt, build.log
out/<slug>/       outputs written by the container
docs/             CONVENTIONS.md (criteria, schema, tolerances, untouched test)
hash_data.py      fills data[].sha256 in a manifest from the fetched files
harness/ reports/ reserved, empty for now
```

## Run the PyDESeq2 target (Muzellec et al. 2023)

Data fetch and hash, done once before the run (`data/` is gitignored). The URIs
and paths are the manifest's `data[].uri` and `data[].path`:

```
git clone https://github.com/cyberfide-science/repro-lab.git repro-lab && cd repro-lab
mkdir -p data/pydeseq2
curl -fL -o data/pydeseq2/test_counts.csv   https://raw.githubusercontent.com/owkin/PyDESeq2/4426e4db990db1c511de3b1b9b7a514989663dad/datasets/synthetic/test_counts.csv
curl -fL -o data/pydeseq2/test_metadata.csv https://raw.githubusercontent.com/owkin/PyDESeq2/4426e4db990db1c511de3b1b9b7a514989663dad/datasets/synthetic/test_metadata.csv
python hash_data.py targets/muzellec-2023-pydeseq2/repro-target.yaml
```

Git Bash on Windows: prefix the `docker run` below with `MSYS_NO_PATHCONV=1` and
write `$(pwd -W)` instead of `$PWD`, otherwise the `-v` arguments are mangled.

```
docker build -t repro-lab/muzellec-2023-pydeseq2 targets/muzellec-2023-pydeseq2
docker run --rm -v "$PWD/data:/work/data:ro" -v "$PWD/out/muzellec-2023-pydeseq2:/work/out" repro-lab/muzellec-2023-pydeseq2
```

Expect `65 passed`, then `out/muzellec-2023-pydeseq2/{pytest.xml,results.csv}`
and an empty `git status` line for the clone.

## Results

| slug | paper | score | untouched |
|---|---|---|---|
| muzellec-2023-pydeseq2 | Muzellec et al. 2023, Bioinformatics (PyDESeq2) | 15 | yes |
| dominguezconde-2022-celltypist | Dominguez Conde et al. 2022, Science (CellTypist) | 14 | yes |
| luecken-2022-scib | Luecken et al. 2022, Nature Methods (scib-pipeline) | 12 | no: the paper's environment file could not be built as shipped; its pip block pins scib via a `git+git://` URL, a protocol GitHub no longer serves |
| luecken-2022-scib-metrics | Luecken et al. 2022, Nature Methods (scib package) | 14 | not attempted (fallback, not needed) |
| squair-2021-de | Squair et al. 2021, Nature Communications | 8 | not attempted (fails the selection gate) |

Full records: `runs/<slug>/untouched.md`. Resolved environments:
`targets/<slug>/env-resolved.txt`; host details in `host.txt`.

MIT licence for this repo; the paper repos keep their own.
