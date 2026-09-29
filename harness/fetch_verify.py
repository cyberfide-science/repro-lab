#!/usr/bin/env python3
"""Stage 2: fetch every data file in the manifest and verify its SHA256.
Writes work/<slug>/provenance.json. Every file is fetched every run; the hash
is the only proof of which bytes ran. Human checkpoint: any single download
above checkpoints.max_download_gb stops and asks (HARNESS_APPROVE=1 answers
yes non-interactively, for CI)."""
import hashlib, json, os, shutil, sys, urllib.request
from datetime import datetime, timezone
import yaml

if len(sys.argv) != 2:
    print("usage: py -3 harness/fetch_verify.py <slug>", file=sys.stderr)
    sys.exit(2)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = sys.argv[1]
M = yaml.safe_load(open(os.path.join(ROOT, "targets", SLUG, "repro-target.yaml"), encoding="utf-8"))
WORK = os.path.join(ROOT, "work", SLUG)
os.makedirs(WORK, exist_ok=True)
os.chdir(ROOT)

limit = M["checkpoints"]["max_download_gb"]
prov_path = os.path.join(WORK, "provenance.json")


def approve(msg):
    if os.environ.get("HARNESS_APPROVE") == "1":
        print(f"[checkpoint] {msg} -- approved via HARNESS_APPROVE=1")
        return
    if input(f"[checkpoint] {msg} Proceed? [y/N] ").strip().lower() != "y":
        sys.exit("[fetch_verify] stopped at human checkpoint")


prov = []
for d in M["data"]:
    dest = d["path"]
    size_gb = d["size_bytes"] / 1e9
    if size_gb > limit:
        approve(f"data '{d['id']}' is {size_gb} GB (> {limit} GB limit).")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if d["uri"].startswith("file://"):
        shutil.copyfile(d["uri"][len("file://"):], dest)
    else:
        urllib.request.urlretrieve(d["uri"], dest)
    hs = hashlib.sha256()
    with open(dest, "rb") as f:  # 1 MiB chunks, as in hash_data.py: multi-GB files never read whole
        for block in iter(lambda: f.read(1 << 20), b""): hs.update(block)
    h = hs.hexdigest()
    ok = h == d["sha256"]
    prov.append({"id": d["id"], "uri": d["uri"], "dest": dest,
                 "sha256_expected": d["sha256"], "sha256_actual": h,
                 "bytes": os.path.getsize(dest),
                 "fetched_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                 "verified": ok})
    print(f"[fetch_verify] {d['id']}: {os.path.getsize(dest)} bytes, sha256 {'OK' if ok else 'MISMATCH'}")
    if not ok:
        json.dump(prov, open(prov_path, "w", encoding="utf-8", newline="\n"), indent=2)
        sys.exit(f"[fetch_verify] hash mismatch for {d['id']}; not proceeding")
json.dump(prov, open(prov_path, "w", encoding="utf-8", newline="\n"), indent=2)
