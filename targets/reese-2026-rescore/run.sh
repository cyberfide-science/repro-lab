#!/bin/bash
# targets/reese-2026-rescore/run.sh - the whole scored run, no manual steps, no network.
set -euo pipefail
mkdir -p /work/out /work/run
cd /work/pheval.llm
echo "== git HEAD: $(git rev-parse HEAD)"
echo "== python: $(python --version)"

# The pinned Mondo SemSQL file, gunzipped to where oaklib's sqlite:obo:mondo looks
# (pystow module "oaklib"); a fresh mtime keeps oaklib's 1-week cache policy from refetching.
mkdir -p /root/.data/oaklib
gunzip -c /work/data/mondo.db.gz > /root/.data/oaklib/mondo.db
echo "== mondo version: $(python -c "import sqlite3; print(';'.join(r[0] for r in sqlite3.connect('/root/.data/oaklib/mondo.db').execute(\"SELECT object FROM statements WHERE predicate='owl:versionIRI'\")))")"

python -c "import zipfile,sys; sys.stdout.buffer.write(zipfile.ZipFile('/work/data/all_models_responses.zip').read('all_models_responses/gpt-01-preview.jsonl'))" > /work/run/gpt-01-preview.jsonl
echo "== gpt-01-preview.jsonl: $(wc -l < /work/run/gpt-01-preview.jsonl) lines"

# curategpt, openai and llm are installed from malco's lock and imported by malco; they must be unreachable.
python - <<'PY'
import socket, sys
seen = []
try:
    socket.setdefaulttimeout(5)
    socket.getaddrinfo("api.openai.com", 443)
    sys.exit("== network check: DNS lookup of api.openai.com succeeded; this run must be offline")
except OSError as e:
    seen.append(type(e).__name__)
try:
    socket.create_connection(("api.openai.com", 443), timeout=5).close()
    sys.exit("== network check: TCP connection to api.openai.com:443 succeeded; this run must be offline")
except OSError as e:
    seen.append(type(e).__name__)
print(f"== network check: unreachable ({', '.join(seen)})")
PY

cp -r /work/pheval.llm/caches /work/run/caches
cd /work/run
echo "== score_rescore.py (repro-lab's own script; malco's functions)"
python /work/score_rescore.py 2>&1 | tee /work/out/scorer.log
cat /work/out/results.csv
echo "== git status --porcelain inside the clone after the run (empty means untouched):"
git -C /work/pheval.llm status --porcelain
