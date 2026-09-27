#!/usr/bin/env python3
"""Resolve every prompt id in exomiser-gold.jsonl to one phenopacket and write cases.tsv.

Run once, before the manifest commit, from the repository root:
    py -3 targets/reese-2026-exomiser/resolve_cases.py \
        data/reese-2026/all_models_responses.zip data/reese-2026/phenopackets.tar.gz \
        targets/reese-2026-exomiser/cases.tsv

Standard library only. Reads both archives directly (no extraction). A prompt id
resolves to a phenopacket when the phenopacket's `id` field, named the way
phenopacket2prompt names its prompt files, equals the prompt id:
    Utility.getFileName: phenopacketID.replaceAll("[^\\w]","_") + "_" + languageCode + "-prompt.txt"
(monarch-initiative/phenopacket2prompt, src/main/java/org/monarchinitiative/
phenopacket2prompt/cmd/Utility.java, lines 81-82 at 4e3dcd0bfeeb7651455b788633572acffff811c9).
Java's \\w without UNICODE_CHARACTER_CLASS is ASCII [a-zA-Z_0-9], hence re.ASCII.
The gold for each case is that line's `gold.disease_id`, as malco uses it.
Every prompt id resolving to zero or to more than one phenopacket is printed,
and the script exits 1 without writing cases.tsv if there is any. Output columns:
row (1-based, 4 digits), prompt_id, phenopacket_id, gold_id.
"""
import json, os, re, sys, tarfile, zipfile

GOLD_MEMBER = "all_models_responses/exomiser-gold.jsonl"


def prompt_name(ppkt_id):
    return re.sub(r"[^\w]", "_", ppkt_id, flags=re.ASCII) + "_en-prompt.txt"


def main():
    if len(sys.argv) != 4:
        sys.exit("usage: resolve_cases.py <all_models_responses.zip> <phenopackets.tar.gz> <cases.tsv>")
    zip_path, tgz_path, out_path = sys.argv[1:]

    with zipfile.ZipFile(zip_path) as z:
        gold = [json.loads(l) for l in z.read(GOLD_MEMBER).decode("utf-8").splitlines() if l.strip()]

    by_name = {}
    with tarfile.open(tgz_path, "r:gz") as t:
        for m in t:
            base = os.path.basename(m.name)
            if not m.isfile() or not base.endswith(".json") or base.startswith("._"):
                continue  # skip macOS AppleDouble "._" entries
            ppkt_id = json.load(t.extractfile(m))["id"]
            by_name.setdefault(prompt_name(ppkt_id), []).append(ppkt_id)

    rows, bad = [], []
    for g in gold:
        hits = by_name.get(g["id"], [])
        if len(hits) != 1:
            bad.append((g["id"], hits))
        else:
            rows.append((g["id"], hits[0], g["gold"]["disease_id"]))

    ppkts = sum(len(v) for v in by_name.values())
    print(f"prompt ids: {len(gold)} ({len({g['id'] for g in gold})} distinct); phenopackets: {ppkts}")
    print(f"unresolved or ambiguous: {len(bad)}")
    for pid, hits in bad:
        print(f"  {pid}\t{len(hits)} phenopacket(s)\t{';'.join(hits)}")
    unused = sorted(v for k, vs in by_name.items() if k not in {g['id'] for g in gold} for v in vs)
    print(f"phenopackets with no prompt id in the gold file: {len(unused)}")
    for u in unused:
        print(f"  {u}")
    if bad:
        sys.exit(1)
    # row: 1-based, zero-padded to 4 digits, in exomiser-gold.jsonl line order. Exomiser input and output
    # file names use it (case-<row>.json), never the phenopacket id, which can contain "/" or U+00A0.
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("row\tprompt_id\tphenopacket_id\tgold_id\n")
        for i, r in enumerate(rows, start=1):
            f.write(f"{i:04d}\t" + "\t".join(r) + "\n")
    print(f"wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
