"""Emparejamiento espectral de SFX contra la parte hablada de la referencia.
Compara espectrogramas mel en dB solo en las celdas donde el SFX tiene energía.
Uso: python3 -I match_sfx_spec.py <ref.wav> <carpeta> <t_max_s> <salida.json>
"""
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import stft

SR = 22050
HOP = 220  # 10 ms
NFFT = 1024
NMEL = 64


def load(path, max_s=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR)]
    if max_s:
        cmd += ["-t", str(max_s)]
    cmd += ["-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, dtype=np.float32).copy()


def mel_fb():
    def hz2mel(h):
        return 2595 * np.log10(1 + h / 700)

    def mel2hz(m):
        return 700 * (10 ** (m / 2595) - 1)

    mels = np.linspace(hz2mel(30), hz2mel(SR / 2), NMEL + 2)
    hz = mel2hz(mels)
    bins = np.floor((NFFT + 1) * hz / SR).astype(int)
    fb = np.zeros((NMEL, NFFT // 2 + 1))
    for i in range(1, NMEL + 1):
        l, c, r = bins[i - 1], bins[i], bins[i + 1]
        for k in range(l, c):
            fb[i - 1, k] = (k - l) / max(c - l, 1)
        for k in range(c, r):
            fb[i - 1, k] = (r - k) / max(r - c, 1)
    return fb


FB = mel_fb()


def melspec_db(x):
    _, _, Z = stft(x, fs=SR, nperseg=NFFT, noverlap=NFFT - HOP, boundary=None, padded=False)
    P = np.abs(Z) ** 2
    M = FB @ P
    return 10 * np.log10(M + 1e-10)


ref_path, folder, tmax, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
R = melspec_db(load(ref_path, tmax))
nT = R.shape[1]

seen = {}
for root, _, names in os.walk(folder):
    for n in sorted(names):
        if not n.lower().endswith((".wav", ".mp3", ".m4a", ".mpeg", ".aac", ".ogg", ".flac")):
            continue
        p = os.path.join(root, n)
        h = hashlib.md5(open(p, "rb").read()).hexdigest()
        seen.setdefault(h, p)

rows = []
for p in sorted(seen.values()):
    x = load(p, 1.5)
    if len(x) < NFFT * 2:
        continue
    nz = np.where(np.abs(x) > 0.02 * (np.abs(x).max() + 1e-9))[0]
    if len(nz) == 0 or np.abs(x).max() < 1e-4:
        continue
    x = x[nz[0]:]
    S = melspec_db(x)
    L = S.shape[1]
    if L < 8 or L >= nT:
        continue
    mask = S > (S.max() - 35)
    if mask.sum() < 20:
        continue
    s_vals = S[mask]
    s_c = s_vals - s_vals.mean()
    s_n = np.sqrt((s_c ** 2).sum()) + 1e-9
    scores = np.empty(nT - L + 1)
    for t in range(nT - L + 1):
        r_vals = R[:, t : t + L][mask]
        r_c = r_vals - r_vals.mean()
        scores[t] = (r_c * s_c).sum() / (np.sqrt((r_c ** 2).sum()) * s_n + 1e-9)
    z = (scores - scores.mean()) / (scores.std() + 1e-9)
    order = np.argsort(-scores)
    picks = []
    for i in order:
        if len(picks) >= 3:
            break
        if all(abs(i - j) > 40 for j in picks):
            picks.append(int(i))
    for i in picks:
        rows.append({"file": os.path.relpath(p, folder), "time_s": round(i * HOP / SR, 2),
                     "score": round(float(scores[i]), 3), "z": round(float(z[i]), 2), "len_s": round(L * HOP / SR, 2)})

rows.sort(key=lambda r: -r["score"])
json.dump(rows, open(out, "w"), ensure_ascii=False, indent=1)
for r in rows[:45]:
    print(f'{r["score"]:.3f} z={r["z"]:5.2f} t={r["time_s"]:6.2f}s len={r["len_s"]:.2f}  {r["file"]}')
