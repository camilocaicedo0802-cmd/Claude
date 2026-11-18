#!/usr/bin/env python3
"""usage: python udl.py PROYECTO < lineas.tsv
Read TSV lines from stdin: id, url, query, author, username, alt.
Download each to assets/img/u_<id>.jpg (skip if exists), verify JPEG > 100KB,
append to work/unsplash.json registry (dedupe by id)."""
import sys, os, json, subprocess

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PROYECTO", ".")
IMG = os.path.join(BASE, "assets/img")
REG = os.path.join(BASE, "work/unsplash.json")
os.makedirs(IMG, exist_ok=True)

reg = []
if os.path.exists(REG):
    with open(REG) as f:
        reg = json.load(f)
by_id = {r["id"]: r for r in reg}

for line in sys.stdin:
    line = line.rstrip("\n")
    if not line.strip():
        continue
    parts = line.split("\t")
    parts += [""] * (6 - len(parts))
    pid, url, query, author, username, alt = parts[:6]
    fn = os.path.join(IMG, f"u_{pid}.jpg")
    if url:
        full = url + ("&" if "?" in url else "?") + "w=2400&fm=jpg&q=85"
    ok = False
    if not os.path.exists(fn) or os.path.getsize(fn) < 100_000:
        if not url:
            print(f"FAIL {pid}: no url"); continue
        r = subprocess.run(["curl", "-sS", "-L", "--fail", "--retry", "4", "--retry-delay", "3", "--retry-all-errors", "-o", fn, full], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAIL {pid}: curl {r.stderr.strip()}")
            if os.path.exists(fn): os.remove(fn)
            continue
    ftype = subprocess.run(["file", "-b", fn], capture_output=True, text=True).stdout
    size = os.path.getsize(fn)
    if "JPEG" not in ftype or size < 100_000:
        print(f"FAIL {pid}: bad file ({ftype.strip()[:40]}, {size} B)")
        os.remove(fn)
        continue
    entry = {"id": pid, "file": fn, "author": author,
             "username": username, "alt": alt, "query": query}
    if pid in by_id:
        old = by_id[pid]
        for k in ("author", "username", "alt"):
            if not old.get(k) and entry[k]:
                old[k] = entry[k]
    else:
        reg.append(entry); by_id[pid] = entry
    print(f"OK {pid} {size//1024}KB")

with open(REG, "w") as f:
    json.dump(reg, f, ensure_ascii=False, indent=1)
print("registry:", len(reg))
