"""Descarga en paralelo archivos de Drive listados en un JSON del manifiesto.
Uso: python3 scripts/descargar_drive.py <lista.json> <carpeta_destino> [hilos]
Conserva la subcarpeta ('path') y omite los ya descargados con el tamaño correcto.
"""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

lista, dest = sys.argv[1], sys.argv[2]
hilos = int(sys.argv[3]) if len(sys.argv) > 3 else 4
items = json.load(open(lista))

def safe(s):
    return "".join(c if c not in '\\:*?"<>|' else "_" for c in s)

def bajar(x):
    d = os.path.join(dest, safe(x.get("path", "")))
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, safe(x["name"]))
    if os.path.exists(out) and x.get("size") and os.path.getsize(out) == int(x["size"]):
        return "ya", out
    url = f"https://drive.usercontent.google.com/download?id={x['id']}&export=download&confirm=t"
    for i in range(4):
        r = subprocess.run(["curl", "-sL", "--fail", "-o", out, url])
        if r.returncode == 0 and os.path.getsize(out) > 0:
            return "ok", out
        time.sleep(2 * (i + 1))
    return "ERROR", out

with ThreadPoolExecutor(hilos) as ex:
    res = list(ex.map(bajar, items))
errs = [o for s, o in res if s == "ERROR"]
print(f"total {len(res)} · nuevos {sum(s=='ok' for s,_ in res)} · ya estaban {sum(s=='ya' for s,_ in res)} · errores {len(errs)}")
for e in errs: print("  ERROR", e)
