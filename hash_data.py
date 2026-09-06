#!/usr/bin/env python3
"""Fill sha256 for every entry in the data: block of a repro-target.yaml.

Usage: python hash_data.py targets/<slug>/repro-target.yaml [--data-root .]
Standard library only. Text-scans the data: block (from "data:" to the next
top-level key) and rewrites each entry's sha256: line in place, so comments
and ordering survive. size_bytes is printed, not written.
"""
import argparse, hashlib, os, re, sys

def sha256_of(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--data-root", default=".")
    a = ap.parse_args()
    text = open(a.manifest, encoding="utf-8").read()
    blk = re.search(r"^data:\n(.*?)(?=^\S|\Z)", text, re.S | re.M)   # data: block only
    if not blk:
        sys.exit("no data: block found")
    entries = re.split(r"(?=^  - )", blk.group(1), flags=re.M)         # one list item each
    def fill(e):
        p = re.search(r"^\s+path:\s*(.+?)\s*$", e, re.M)
        s = re.search(r"^(\s+sha256:\s*)(.*)$", e, re.M)
        if not p:
            return e
        if not s:
            print(f"NO sha256 LINE  {p.group(1)}", file=sys.stderr); return e
        full = os.path.join(a.data_root, p.group(1))
        if not os.path.isfile(full):
            print(f"MISSING  {p.group(1)}", file=sys.stderr); return e
        d = sha256_of(full)
        print(f"{d}  {os.path.getsize(full):>10}  {p.group(1)}")
        return e[:s.start(2)] + d + e[s.end(2):]
    new = "".join(fill(e) for e in entries)
    out = text[:blk.start(1)] + new + text[blk.end(1):]
    open(a.manifest, "w", encoding="utf-8", newline="\n").write(out)

if __name__ == "__main__":
    main()
