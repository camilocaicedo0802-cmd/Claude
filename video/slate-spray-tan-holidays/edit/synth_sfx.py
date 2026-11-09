"""Subtle synthesized SFX (no samples): soft whoosh, short riser, glass pop."""
import sys, numpy as np, soundfile as sf, scipy.signal as ss
SR = 48000; out = sys.argv[1]; rng = np.random.default_rng(7)
def norm(x, pk=0.89): return x / (np.abs(x).max() + 1e-9) * pk
def stereo(x, w=0.15):
    d = int(0.004 * SR); r = np.concatenate([np.zeros(d), x[:-d]])
    return np.stack([x * (1 + w) / 2 + r * (1 - w) / 2, r * (1 + w) / 2 + x * (1 - w) / 2], 1)
def sweep_noise(dur, f0, f1, env):
    n = int(dur * SR); x = rng.normal(0, 1, n); y = np.zeros(n); blk = 512
    fc = np.geomspace(f0, f1, n // blk + 1)
    zi = None
    for k in range(0, n, blk):
        f = fc[k // blk]; b, a = ss.butter(2, [max(40, f * 0.6) / (SR / 2), min(0.99, f * 1.6 / (SR / 2))], "band")
        seg = x[k:k + blk]
        y[k:k + blk] = ss.lfilter(b, a, seg)
    return y * env(np.linspace(0, 1, n))
# whoosh: band-passed noise sweeping down then up, bell envelope (0.45 s)
w = sweep_noise(0.45, 4500, 900, lambda u: np.sin(np.pi * u) ** 2 * (1 - 0.3 * u))
sf.write(f"{out}/whoosh.wav", norm(stereo(w)), SR, subtype="PCM_24")
# riser: rising noise + faint rising sine, ends abruptly into the cut (0.7 s)
n = int(0.7 * SR); u = np.linspace(0, 1, n)
r = sweep_noise(0.7, 600, 9000, lambda u: u ** 2.2)
ph = 2 * np.pi * np.cumsum(np.geomspace(300, 2400, n)) / SR
r = r / (np.abs(r).max() + 1e-9) + 0.25 * np.sin(ph) * u ** 3
r[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
sf.write(f"{out}/riser.wav", norm(stereo(r)), SR, subtype="PCM_24")
# glass pop: short pitched blip with fast decay + tiny click (0.12 s)
n = int(0.14 * SR); t = np.arange(n) / SR
p = np.sin(2 * np.pi * (1400 - 600 * t / t[-1]) * t) * np.exp(-t * 38) + 0.4 * np.sin(2 * np.pi * 2900 * t) * np.exp(-t * 70)
p[: int(0.001 * SR)] *= np.linspace(0, 1, int(0.001 * SR))
sf.write(f"{out}/pop.wav", norm(stereo(p, 0.05)), SR, subtype="PCM_24")
print("ok")
