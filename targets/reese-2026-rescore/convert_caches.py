#!/usr/bin/env python3
"""Read the authors' malco score caches (Berkeley DB 1.85 hash files written on macOS) and copy every
key/value pair, byte for byte, into Linux-native dbm.gnu files where malco's shelve looks for them.

Lives in repro-lab, not in the clone. Read-only: it parses a copy of each .db file, checks the originals'
sha256 before and after, and never writes to the clone. malco's code is not modified; it simply finds a
readable cache at caches/<name> (shelve on Linux opens <name>, without the .db suffix).

Berkeley DB 1.85 hash format (4.4BSD db/hash: hash.h, page.h, hash_page.c), as read here:
- page 0 holds the header, big-endian on disk: magic 0x061561, version 2, lorder, bsize, bshift, dsize,
  ssize, sshift, ovfl_point, last_freed, max_bucket, high_mask, low_mask, ffactor, nkeys, hdrpages,
  h_charkey, spares[32] (int32), bitmaps[32] (uint16);
- bucket b lives on page b + hdrpages + (spares[log2(b+1)-1] if b else 0);
- an overflow address a (uint16) is page BUCKET_TO_PAGE((1 << (a >> 11)) - 1) + (a & 0x7FF);
- a page is an array of uint16 in the file's byte order (lorder): n = entries, then n entries as
  (key offset, data offset) pairs; key i spans [keyoff_i, end_{i-1}), data i spans [datoff_i, keyoff_i),
  with end_{-1} = bsize and end_i = datoff_i. A pair whose second entry is below REAL_KEY (4) is a marker:
  (addr, 0) chains to the overflow page addr; 1-3 mark a "big" pair stored across overflow pages. Big
  pairs are not implemented: if one is found the conversion stops, and the caches are left alone.

Fidelity checks (all must pass, otherwise nothing is written and the caches stay as they are):
  (a) pairs read == nkeys in the file's header;
  (b) every value unpickles to (key, value), and every score_grounded_result value is 0.0, 0.5 or 1.0;
  (c) 500 keys per file, drawn with random.Random(20260927) from the sorted key list: malco's own
      get_ground_truth_from_cache_or_compute (omim cache) and scoring.score (score cache), on a scratch
      copy of the converted caches, return exactly the dumped value, and CacheInfo counts every lookup as
      a hit. Evidence only: the same 500 score keys recomputed live against the pinned Mondo, with no
      cache, and the agreement with the cached values.
Usage: convert_caches.py <clone caches dir> <output caches dir>
"""
import dbm.gnu, hashlib, os, pickle, random, shutil, struct, sys, tempfile

NAMES = ("omim_mappings_cache", "score_grounded_result_cache")
MAGIC, REAL_KEY, SEED, SAMPLE = 0x061561, 4, 20260927, 500


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def read_185(path):
    data = open(path, "rb").read()
    (magic, version, lorder, bsize, bshift, dsize, ssize, sshift, ovfl_point, last_freed, max_bucket,
     high_mask, low_mask, ffactor, nkeys, hdrpages, h_charkey) = struct.unpack(">17i", data[:68])
    spares = struct.unpack(">32i", data[68:68 + 128])
    if magic != MAGIC or version != 2:
        raise ValueError(f"not a Berkeley DB 1.85 hash file (magic {magic:#x}, version {version})")
    order = "<" if lorder == 1234 else ">"

    def log2(n):
        i, k = 0, 1
        while k < n:
            k, i = k << 1, i + 1
        return i

    def bucket_to_page(b):
        return b + hdrpages + (spares[log2(b + 1) - 1] if b else 0)

    def oaddr_to_page(a):
        return bucket_to_page((1 << (a >> 11)) - 1) + (a & 0x7FF)

    def page(p):
        chunk = data[p << bshift:(p + 1) << bshift]
        return chunk if len(chunk) == bsize else None

    pairs, seen_pages = [], set()
    for b in range(max_bucket + 1):
        p = bucket_to_page(b)
        while p is not None:
            if p in seen_pages:
                raise ValueError(f"page {p} reached twice")
            seen_pages.add(p)
            pg = page(p)
            if pg is None:
                break  # never written: an empty bucket
            n = struct.unpack_from(order + "H", pg, 0)[0]
            ent = struct.unpack_from(order + f"{n}H", pg, 2) if n else ()
            end, nxt, i = bsize, None, 0
            while i < n:
                k, d = ent[i], ent[i + 1]
                if d < REAL_KEY:
                    if d == 0:  # overflow chain
                        nxt = oaddr_to_page(k)
                        i += 2
                        continue
                    raise ValueError(f"big key/data pair on page {p}; not implemented")
                pairs.append((pg[k:end], pg[d:k]))
                end, i = d, i + 2
            p = nxt
    return nkeys, pairs


def main():
    src, dst = sys.argv[1], sys.argv[2]
    before = {n: sha256(f"{src}/{n}.db") for n in NAMES}
    dumped = {}
    for n in NAMES:
        with tempfile.TemporaryDirectory() as t:
            shutil.copyfile(f"{src}/{n}.db", f"{t}/{n}.db")
            nkeys, pairs = read_185(f"{t}/{n}.db")
        print(f"== cache conversion: {n}.db: {len(pairs)} pairs read, header nkeys {nkeys}")
        if len(pairs) != nkeys or len({k for k, _ in pairs}) != len(pairs):
            sys.exit(f"== cache conversion: check (a) FAILED for {n}; caches left as they are")
        for k, v in pairs:
            key, val = pickle.loads(v)
            if n == "score_grounded_result_cache" and val not in (0.0, 0.5, 1.0):
                sys.exit(f"== cache conversion: check (b) FAILED for {n}: value {val!r}; caches left as they are")
        dumped[n] = pairs
    print("== cache conversion: check (a) pairs == header nkeys: passed; check (b) every value unpickles, "
          "every score in {0.0, 0.5, 1.0}: passed")

    staged = tempfile.mkdtemp()
    for n in NAMES:
        with dbm.gnu.open(f"{staged}/{n}", "n") as db:
            for k, v in dumped[n]:
                db[k] = v

    check_c(staged, dumped)
    after = {n: sha256(f"{src}/{n}.db") for n in NAMES}
    if after != before:
        sys.exit("== cache conversion: an original changed during the conversion; caches left as they are")
    os.makedirs(dst, exist_ok=True)
    for n in NAMES:
        shutil.copyfile(f"{staged}/{n}", f"{dst}/{n}")
    print(f"== cache conversion: done; originals unmodified (sha256 {before[NAMES[0]][:12]}..., "
          f"{before[NAMES[1]][:12]}...); gdbm copies at {dst}/<name>")


def check_c(staged, dumped):
    import pandas as pd
    from cachetools import LRUCache
    from cachetools.keys import hashkey
    from shelved_cache import PersistentCache
    from oaklib import get_adapter
    from malco.process.mondo_score_utils import get_ground_truth_from_cache_or_compute, score_grounded_result
    from malco.process.scoring import score

    def sample(n):
        pairs = sorted(dumped[n])
        return [pickle.loads(v) for _, v in random.Random(SEED).sample(pairs, min(SAMPLE, len(pairs)))]

    mondo = get_adapter("sqlite:obo:mondo")
    scratch = tempfile.mkdtemp()
    shutil.copytree(staged, f"{scratch}/caches")
    cwd = os.getcwd()
    os.chdir(scratch)
    try:
        omim = sample("omim_mappings_cache")
        pc1 = PersistentCache(LRUCache, "caches/omim_mappings_cache", maxsize=524288)
        pc1.hits = pc1.misses = 0
        pc1.initialize_if_not_initialized()
        bad = [k for k, v in omim if get_ground_truth_from_cache_or_compute(k[0], mondo, pc1) != v]
        hits1, misses1 = pc1.hits, pc1.misses
        pc1.close()
        if bad or hits1 != len(omim) or misses1:
            sys.exit(f"== cache conversion: check (c) FAILED for omim_mappings_cache ({len(bad)} differ, "
                     f"hits {hits1}, misses {misses1}); caches left as they are")
        sc = sample("score_grounded_result_cache")
        df = pd.DataFrame({"id": [f"k{i}" for i in range(len(sc))],
                           "gold": [{"disease_id": k[1]} for k, _ in sc],
                           "grounding": [[("x", [(k[0], "")])] for k, _ in sc]})
        out = score(df)  # prints malco's two CacheInfo lines; the second is the score cache
        got = [s[0]["grounded_score"] for s in out["scored"]]
        bad = sum(1 for (k, v), g in zip(sc, got) if g != v)
        if bad:
            sys.exit(f"== cache conversion: check (c) FAILED for score_grounded_result_cache ({bad} differ); "
                     "caches left as they are")
    finally:
        os.chdir(cwd)
    pc2 = PersistentCache(LRUCache, f"{scratch}/caches/score_grounded_result_cache", maxsize=524288)
    pc2.hits = pc2.misses = 0
    pc2.initialize_if_not_initialized()
    for k, _ in sc:
        try:
            pc2[hashkey(*k)]
            pc2.hits += 1
        except KeyError:
            pc2.misses += 1
    if pc2.hits != len(sc) or pc2.misses:
        sys.exit(f"== cache conversion: check (c) FAILED: score cache hits {pc2.hits}, misses {pc2.misses}")
    pc2.close()
    print(f"== cache conversion: check (c) {len(omim)} omim keys and {len(sc)} score keys through malco's own "
          f"code on the converted caches: identical values, all hits: passed")
    live = sum(1 for k, v in sc if score_grounded_result(k[0], k[1], mondo) == v)
    print(f"== cache conversion: evidence, not a gate: live rescoring of the {len(sc)} score keys against the "
          f"pinned Mondo, no cache, agrees with the authors' cached value for {live} ({live / len(sc):.4f})")
    shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
