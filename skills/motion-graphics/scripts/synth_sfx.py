#!/usr/bin/env python3
"""
Genera una biblioteca de efectos de sonido sintéticos (sin derechos de terceros) en <outdir>.

  tick        tic de reloj            boom        impacto grave
  blip        notificación suave      pop         aparición de elemento
  click       clic de interfaz        swipe       deslizar pantalla
  whoosh      barrido corto           whoosh_long transición larga
  riser       subida de tensión       scribble    tachar con rotulador
  sand        arena / disolución      glitch      fallo digital
  type        tecla (tecleo)          shimmer     brillo / aparición mágica

Uso: python3 synth_sfx.py public/sfx
"""
import os
import sys

import numpy as np
import soundfile as sf

SR = 44100
rng = np.random.default_rng(7)


def norm(x, db):
    return x * (10 ** (db / 20) / (np.max(np.abs(x)) + 1e-12))


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1.0) * np.exp(-np.maximum(t - a, 0) / d)


def stereo(x, w=0.15):
    dl = int(0.008 * SR)
    r = np.concatenate([np.zeros(dl), x[:-dl]])
    return np.stack([x * (1 - w) + r * w, r * (1 - w) + x * w], 1)


def band(n, lo, hi):
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, n)


def sweep(n, f0, f1, q=0.6):
    hop = 512
    out = np.zeros(n + hop * 2)
    win = np.hanning(hop * 2)
    for i in range(0, n, hop):
        fc = f0 * (f1 / f0) ** (i / n)
        out[i: i + hop * 2] += band(hop * 2, fc * (1 - q), fc * (1 + q)) * win
    return out[:n]


def fadeio(x, fi=0.003, fo=0.02):
    n = len(x)
    a = np.ones(n)
    i, o = int(fi * SR), int(fo * SR)
    a[:i] = np.linspace(0, 1, i)
    a[-o:] = np.minimum(a[-o:], np.linspace(1, 0, o))
    return x * a


def build():
    S = {}
    n = int(0.09 * SR); t = np.arange(n) / SR
    S["tick"] = (stereo((np.sin(2 * np.pi * 3200 * t) * 0.6 + band(n, 2000, 9000) * 0.5) * env(n, 0.0005, 0.012), 0.05), -6)
    n = int(1.6 * SR); t = np.arange(n) / SR
    fr = 55 * np.exp(-t * 1.2) + 32
    S["boom"] = (stereo(np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, 0.003, 0.45) + band(n, 30, 400) * env(n, 0.001, 0.05) * 0.6, 0.1), -1)
    n = int(0.22 * SR); t = np.arange(n) / SR
    S["blip"] = (stereo((np.sin(2 * np.pi * 1320 * t) + 0.4 * np.sin(2 * np.pi * 1980 * t)) * env(n, 0.002, 0.05) + np.sin(2 * np.pi * 880 * t) * env(n, 0.002, 0.03) * 0.5, 0.2), -4)
    n = int(0.18 * SR); t = np.arange(n) / SR
    pf = 900 * np.exp(-t * 40) + 180
    S["pop"] = (stereo(np.sin(2 * np.pi * np.cumsum(pf) / SR) * env(n, 0.001, 0.03) + band(n, 1500, 7000) * env(n, 0.0005, 0.006) * 0.4, 0.2), -3)
    n = int(0.06 * SR)
    S["click"] = (stereo(band(n, 1500, 9000) * env(n, 0.0003, 0.004) + np.sin(2 * np.pi * 2400 * np.arange(n) / SR) * env(n, 0.0003, 0.006) * 0.4, 0.05), -6)
    n = int(0.35 * SR)
    S["swipe"] = (stereo(sweep(n, 600, 5000, 0.5) * np.sin(np.linspace(0, np.pi, n)) ** 1.5, 0.35), -3)
    n = int(0.3 * SR)
    S["whoosh"] = (stereo(fadeio(sweep(n, 400, 3000, 0.7) * np.sin(np.linspace(0, np.pi, n)) ** 2), 0.4), -3)
    n = int(0.75 * SR)
    wl = sweep(n, 250, 2600, 0.7) * np.sin(np.linspace(0, np.pi, n)) ** 2 + sweep(n, 80, 300, 0.6) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.6
    S["whoosh_long"] = (stereo(wl, 0.4), -2)
    n = int(1.8 * SR); t = np.arange(n) / SR
    rs = sweep(n, 300, 6000, 0.35) * (t / t[-1]) ** 2.2 + np.sin(2 * np.pi * np.cumsum(110 * 2 ** (t * 1.6)) / SR) * (t / t[-1]) ** 3 * 0.25
    S["riser"] = (stereo(fadeio(rs, 0.01, 0.01), 0.3), -3)
    n = int(0.45 * SR); t = np.arange(n) / SR
    S["scribble"] = (stereo(band(n, 1800, 7000) * (0.55 + 0.45 * np.sin(2 * np.pi * 14 * t)) * env(n, 0.01, 0.25), 0.1), -6)
    n = int(1.4 * SR)
    gr = np.zeros(n)
    for _ in range(900):
        p = int(rng.uniform(0, n - 400)); L = int(rng.uniform(40, 300))
        gr[p: p + L] += rng.standard_normal(L) * np.hanning(L) * rng.uniform(0.2, 1)
    S["sand"] = (stereo(np.convolve(gr, np.ones(3) / 3, "same") * np.sin(np.linspace(0, np.pi, n)) ** 0.7, 0.5), -6)
    n = int(0.35 * SR); t = np.arange(n) / SR
    sq = np.sign(np.sin(2 * np.pi * 220 * t * (1 + 3 * (rng.random(n) > 0.97)))) * 0.4
    gate = (np.floor(t * 40) % 2 == 0).astype(float)
    S["glitch"] = (stereo(fadeio((sq + band(n, 2000, 12000) * 0.5) * gate * env(n, 0.001, 0.2)), 0.3), -6)
    n = int(0.08 * SR)
    S["type"] = (stereo(band(n, 800, 6000) * env(n, 0.0005, 0.01) + band(n, 100, 400) * env(n, 0.001, 0.02) * 0.6, 0.1), -8)
    n = int(1.2 * SR); t = np.arange(n) / SR
    sh = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) for f in (2093, 2637, 3136, 3951)) * env(n, 0.02, 0.35)
    S["shimmer"] = (stereo(sh + band(n, 6000, 14000) * env(n, 0.01, 0.2) * 0.3, 0.5), -8)
    return S


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "sfx"
    os.makedirs(out, exist_ok=True)
    for name, (x, db) in build().items():
        sf.write(os.path.join(out, f"{name}.wav"), norm(x, db), SR)
        print(os.path.join(out, f"{name}.wav"))
