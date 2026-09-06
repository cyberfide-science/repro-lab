# repro-lab

Unit 1 of an AI-for-science reproducibility track: can a published pipeline run
untouched, from a manifest, in a fresh container? This is a repository of
scripts and records, not a package. Each `targets/<slug>/` holds a
`repro-target.yaml` manifest (pinned commit, data URIs + sha256, pre-registered
claims and tolerances), a `Dockerfile` and a `run.sh`; each `runs/<slug>/` holds
the `untouched.md` record and the captured log. Paper code is cloned inside the
image at build time and is never edited; data is mounted at run time.

## Run the target that carries the exit criterion (PyDESeq2, Muzellec et al. 2023)

```
git clone <path-or-url-of-this-repo> repro-lab && cd repro-lab
docker build -t repro-lab/muzellec-2023-pydeseq2 targets/muzellec-2023-pydeseq2
docker run --rm -v "$PWD/data:/work/data:ro" -v "$PWD/out/muzellec-2023-pydeseq2:/work/out" repro-lab/muzellec-2023-pydeseq2
```

Expect `65 passed`, then `out/muzellec-2023-pydeseq2/{pytest.xml,results.csv}`
and an empty `git status` line for the clone. Git Bash on Windows: prefix the
run with `MSYS_NO_PATHCONV=1` and write `$(pwd -W)` instead of `$PWD`.

Data fetch and hash (done once, before the run; `data/` is gitignored): fetch
each `data[].uri` in the manifest to its `data[].path` with `curl -fL -o`, then
`python hash_data.py targets/muzellec-2023-pydeseq2/repro-target.yaml` writes
the sha256 lines and prints the byte sizes.

Results and outcomes: `runs/<slug>/untouched.md` (one per target, five in all).
Resolved environment: `targets/<slug>/env-resolved.txt`, host in `host.txt`.

MIT licence for this repo; the paper repos keep their own.
