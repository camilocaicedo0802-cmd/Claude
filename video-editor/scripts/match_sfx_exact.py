"""Busca copias exactas (o casi) de cada SFX dentro de la referencia.
Correlación normalizada de forma de onda sobre los primeros 0,6 s de cada SFX,
deduplicando por contenido. Uso: match_sfx_exact.py <ref.wav> <carpeta> <t_max> <salida.json>"""
import hashlib, json, os, subprocess, sys
import numpy as np
from scipy.signal import fftconvolve
SR = 16000
def load(p, ss=0, t=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", p] + (["-t", str(t)] if t else []) + ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL).stdout, np.float32).copy()
ref_p, folder, tmax, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
ref = load(ref_p, 0, tmax)
cum = np.concatenate([[0], np.cumsum(ref.astype(np.float64) ** 2)])
uniq = {}
for root, _, names in os.walk(folder):
    for n in names:
        if n.lower().endswith((".wav", ".mp3", ".m4a", ".mpeg", ".aac", ".ogg", ".flac", ".aif", ".aiff")):
            p = os.path.join(root, n)
            uniq.setdefault(hashlib.md5(open(p, "rb").read()).hexdigest(), p)
rows = []
for p in sorted(uniq.values()):
    x = load(p, 0, 2.0)
    if len(x) < 1600 or np.abs(x).max() < 1e-3:
        continue
    nz = np.where(np.abs(x) > 0.05 * np.abs(x).max())[0]
    x = x[nz[0]: nz[0] + int(0.6 * SR)]
    x = x - x.mean()
    L = len(x)
    if L < 800:
        continue
    cor = fftconvolve(ref, x[::-1], mode="valid")
    en = np.sqrt(np.maximum(cum[L:] - cum[:-L], 0))[: len(cor)] + 1e-9
    ncc = cor / (en * np.sqrt((x ** 2).sum()) + 1e-9)
    i = int(np.argmax(np.abs(ncc)))
    rows.append({"file": os.path.relpath(p, folder), "t": round(i / SR, 3), "ncc": round(float(abs(ncc[i])), 3)})
rows.sort(key=lambda r: -r["ncc"])
json.dump(rows, open(out, "w"), ensure_ascii=False, indent=1)
print("SFX únicos analizados:", len(rows))
for r in rows[:15]:
    print(f'{r["ncc"]:.3f} @ {r["t"]:6.2f}s  {r["file"]}')
