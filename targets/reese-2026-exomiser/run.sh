#!/bin/bash
# targets/reese-2026-exomiser/run.sh - the whole scored run, no manual steps, no network.
set -euo pipefail
mkdir -p /work/out /work/run /work/exomiser-data
echo "== git HEAD: $(git -C /work/Exomiser rev-parse HEAD)"
echo "== java: $(java -version 2>&1 | head -1)"
echo "== python: $(python --version)"
echo "== pheval.llm HEAD: $(git -C /work/pheval.llm rev-parse HEAD)"

# The program and its data, extracted in this run from the hash-verified zips under /work/data.
unzip -q /work/data/exomiser-cli-14.0.1-distribution.zip -d /work
cp /work/application.properties /work/exomiser-cli-14.0.1/application.properties
for z in 2406_phenotype.zip 2406_hg19.zip; do
  t0=$(date +%s)
  unzip -q "/work/data/$z" -d /work/exomiser-data
  echo "== extracted $z from /work/data in $(( $(date +%s) - t0 )) s"
done
du -sb /work/exomiser-data/* | sed 's/^/== data: /'

# The pinned Mondo SemSQL file, gunzipped to where oaklib's sqlite:obo:mondo looks (fresh mtime).
mkdir -p /root/.data/oaklib
gunzip -c /work/data/mondo.db.gz > /root/.data/oaklib/mondo.db
echo "== mondo version: $(python -c "import sqlite3; print(';'.join(r[0] for r in sqlite3.connect('/root/.data/oaklib/mondo.db').execute(\"SELECT object FROM statements WHERE predicate='owl:versionIRI'\")))")"

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

# Outputs of an earlier run never survive into this one.
rm -rf /work/wk/raw /work/wk/items /work/wk/raw_json.sha256
mkdir -p /work/wk/raw /work/wk/items

echo "== cases"
python /work/score_exomiser.py cases
echo "== analyse (Exomiser 14.0.1, --preset phenotype-only, no VCF)"
python /work/score_exomiser.py analyse

python -c "import zipfile,sys; sys.stdout.buffer.write(zipfile.ZipFile('/work/data/all_models_responses.zip').read('all_models_responses/gpt-01-preview.jsonl'))" > /work/run/gpt-01-preview.jsonl
cp -r /work/pheval.llm/caches /work/run/caches
cd /work/run
echo "== score_exomiser.py score (repro-lab's own script; malco's functions)"
python /work/score_exomiser.py score 2>&1 | tee /work/out/scorer.log
cat /work/out/results.csv
echo "== git status --porcelain inside the clones after the run (empty means untouched):"
git -C /work/pheval.llm status --porcelain
git -C /work/Exomiser status --porcelain
