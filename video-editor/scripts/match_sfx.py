"""Busca en qué instantes aparece cada SFX de una carpeta dentro de un audio
mezclado (la referencia). Correlación cruzada normalizada de la forma de onda
(16 kHz mono), con normalización por energía local.
Uso: python3 -I match_sfx.py <referencia.wav> <carpeta_sfx> <salida.json>
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import fftconvolve

SR = 16000


def load(path, max_s=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR)]
    if max_s:
        cmd += ["-t", str(max_s)]
    cmd += ["-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


ref_path, folder, out = sys.argv[1], sys.argv[2], sys.argv[3]
ref = load(ref_path)
ref_sq_cum = np.concatenate([[0.0], np.cumsum(ref.astype(np.float64) ** 2)])

results = []
files = []
for root, _, names in os.walk(folder):
    for n in names:
        if n.lower().endswith((".wav", ".mp3", ".m4a", ".mpeg", ".aac", ".ogg", ".flac")):
            files.append(os.path.join(root, n))
files.sort()

for f in files:
    tpl = load(f, max_s=1.2)
    # recorta silencio inicial del template
    nz = np.where(np.abs(tpl) > 0.01 * (np.abs(tpl).max() + 1e-9))[0]
    if len(nz) == 0 or len(tpl) < 400:
        continue
    lead = nz[0]
    tpl = tpl[lead:]
    if len(tpl) > len(ref):
        tpl = tpl[: len(ref) // 2]
    tpl = tpl - tpl.mean()
    tn = np.sqrt((tpl.astype(np.float64) ** 2).sum()) + 1e-9
    corr = fftconvolve(ref, tpl[::-1], mode="valid")
    L = len(tpl)
    win_energy = np.sqrt(ref_sq_cum[L:] - ref_sq_cum[:-L])[: len(corr)] + 1e-9
    ncc = corr / (win_energy * tn)
    # top picos separados >= 0.3 s
    order = np.argsort(-np.abs(ncc))
    picks = []
    for idx in order:
        if len(picks) >= 4:
            break
        if all(abs(idx - p) > 0.3 * SR for p, _ in picks):
            picks.append((int(idx), float(ncc[idx])))
    for idx, score in picks:
        results.append(
            {
                "file": os.path.relpath(f, folder),
                "time_s": round((idx - lead) / SR, 3),
                "score": round(score, 3),
            }
        )
    best = max(abs(s) for _, s in picks)
    print(f"{best:6.3f}  {os.path.relpath(f, folder)}  @ {[round((i - lead) / SR, 2) for i, _ in picks]}", flush=True)

results.sort(key=lambda r: -abs(r["score"]))
with open(out, "w", encoding="utf-8") as fh:
    json.dump(results, fh, ensure_ascii=False, indent=1)
