#!/usr/bin/env python3
"""Descarga en paralelo los archivos de un manifiesto TSV (id, tipo, ruta) a una carpeta.
Uso: descargar_tsv.py <manifiesto.tsv> <destino> [regex_incluir] [regex_excluir]"""
import sys, re, os, subprocess, unicodedata
from concurrent.futures import ThreadPoolExecutor
tsv, dest = sys.argv[1], sys.argv[2]
inc = re.compile(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else None
exc = re.compile(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] else None
def limpio(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")
jobs, seen = [], set()
for line in open(tsv):
    fid, tipo, ruta = line.rstrip("\n").split("\t")
    if tipo != "archivo" or (inc and not inc.search(ruta)) or (exc and exc.search(ruta)): continue
    partes = ruta.split("/")[1:]
    out = os.path.join(dest, *[limpio(p) for p in partes])
    if out in seen: continue
    seen.add(out); jobs.append((fid, out, ruta))
def run(j):
    fid, out, ruta = j
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r = subprocess.run(["scripts/drive_dl.sh", fid, out], capture_output=True, text=True)
    return (r.returncode, out, ruta, r.stderr.strip()[-200:])
with ThreadPoolExecutor(6) as ex: res = list(ex.map(run, jobs))
with open(os.path.join(dest, "_mapa.tsv"), "a") as f:
    for rc, out, ruta, err in res: f.write(f"{'ok' if rc == 0 else 'FALLO'}\t{out}\t{ruta}\n")
fallos = [r for r in res if r[0] != 0]
print(f"{dest}: {len(res) - len(fallos)} ok, {len(fallos)} fallos")
for r in fallos[:10]: print("  FALLO", r[2], r[3])
