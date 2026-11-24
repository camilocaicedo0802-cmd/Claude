"""Builds the voice track (cut + 1.1x + cleanup) and a synthesized SFX layer, then mixes them."""
import subprocess, sys, os
import numpy as np
from scipy.io import wavfile
from scipy import signal
sys.argv = [sys.argv[0], sys.argv[1]]
sys.path.insert(0, os.path.join(sys.argv[1], "scripts"))
import full as edl

SP = sys.argv[1]
os.chdir(SP)
SR = 48000

# ---------- voice ----------
parts, labels = [], []
for i, (name, a, b) in enumerate(edl.SEGS):
    if a is None:
        r0 = edl.ROOMTONE[name]
        a, b = r0, r0 + b
    d = b - a
    parts.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,aresample={SR},"
                 f"afade=t=in:st=0:d=0.012,afade=t=out:st={d-0.02:.3f}:d=0.02[s{i}]")
    labels.append(f"[s{i}]")
fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1[cat];" \
     "[cat]highpass=f=90,afftdn=nf=-28," \
     "equalizer=f=3500:t=q:w=1.2:g=2.5,equalizer=f=250:t=q:w=1.0:g=-2," \
     "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2," \
     f"loudnorm=I=-14:TP=-1.5:LRA=7,aresample={SR},atrim=0:{edl.TOTAL:.4f}[v]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "raw/toma_ugc.mov", "-filter_complex", fc,
                "-map", "[v]", "-ac", "1", "-c:a", "pcm_s16le", "work/voice_full.wav"], check=True)

# ---------- SFX ----------
rng = np.random.default_rng(7)
N = int(edl.NF / edl.FPS * SR) + SR
sfx = np.zeros(N)


def env(n, a, r):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / r)
    return e


def bp(x, lo, hi):
    sos = signal.butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def whoosh(dur=0.38, up=True, gain=0.35):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    bands = [(300, 900), (900, 2500), (2500, 7000)]
    layers = [bp(noise, lo, hi) for lo, hi in bands]
    t = np.linspace(0, 1, n)
    pos = t if up else 1 - t
    w = [np.clip(1 - abs(pos * 2 - k), 0, 1) for k in range(3)]
    y = sum(l * wk for l, wk in zip(layers, w))
    shape = np.sin(np.pi * np.clip(t * 1.15, 0, 1)) ** 1.6
    y = y * shape
    return gain * y / (np.abs(y).max() + 1e-9)


def pop(gain=0.3, f0=950, f1=320):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.018)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / 0.028)
    return gain * y


def riser(dur=0.55, gain=0.16):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 260 * (5 ** (t / dur))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sin(ph) + 0.35 * np.sin(2 * ph)) * (t / dur) ** 1.5 * (1 - np.exp(-(dur - t) / 0.02))
    y += 0.4 * bp(rng.standard_normal(n), 2000, 8000) * (t / dur) ** 2 * 0.3
    return gain * y / np.abs(y).max()


def ding(gain=0.22):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * 1318.5 * t) + 0.5 * np.sin(2 * np.pi * 1975.5 * t) * np.exp(-t / 0.15)
         + 0.25 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t / 0.32) * np.minimum(1, t / 0.003)
    return gain * y / np.abs(y).max()


def drop(gain=0.2):
    # descending "bloop" for "baje"
    n = int(0.32 * SR)
    t = np.arange(n) / SR
    f = 900 * (0.35 ** (t / 0.32))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / 0.12) * np.minimum(1, t / 0.004)
    return gain * y


def place(x, t):
    i = int(t * SR)
    j = min(N, i + len(x))
    sfx[i:j] += x[: j - i]


fps = edl.FPS
sys.path.insert(0, "scripts")


def impact(gain=0.32):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    f = 120 * np.exp(-t / 0.08) + 45
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / 0.22) * np.minimum(1, t / 0.002)
    y += 0.35 * bp(rng.standard_normal(n), 400, 5000) * np.exp(-t / 0.05)
    return gain * y / np.abs(y).max()


def shimmer(dur=0.6, gain=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = bp(rng.standard_normal(n), 3000, 11000) * np.sin(np.pi * t / dur) ** 2
    return gain * y / np.abs(y).max()


SH = edl.SH
T = edl.T
st = lambda k: SH[k]["t0"]
# cuts into b-roll / scenes
for k, up, g in (("V2", True, 0.22), ("V3", False, 0.18), ("V8", False, 0.22), ("S2", True, 0.22),
                 ("S4", False, 0.24), ("S6", True, 0.18), ("S7a", False, 0.2), ("V10", True, 0.22),
                 ("V11", False, 0.18)):
    place(whoosh(0.34, up, g), st(k) - 0.17)
for k in ("V7", "S3", "V13"):
    place(whoosh(0.42, True, 0.28), st(k) - 0.21)
    place(pop(0.15, 1400, 700), st(k) + 0.14)
for k in ("V7", "S5"):
    place(shimmer(0.55, 0.14), st(k) - 0.22)
place(whoosh(0.30, True, 0.18), st("S5") - 0.15)
# card pops
place(pop(0.17, 1100, 520), st("S4") + 0.05)
place(pop(0.17, 1100, 520), st("S7b") + 0.05)
# emphasis
place(impact(0.16), T(1.0) - 0.85)               # HOLIS
place(riser(0.5, 0.12), T(35.85) - 0.5)
place(impact(0.22), T(35.85))                    # SUBE
place(impact(0.18), T(43.92))                    # ARRIBA
place(drop(0.16), st("S7c") + 0.2)               # BAJE
place(whoosh(0.3, False, 0.18), T(46.15))
place(impact(0.28), T(46.15) + 0.16)             # MAS RAPIDO
place(impact(0.20), st("V13") + 0.15)            # NUTRIPLUS
place(shimmer(0.9, 0.12), st("V13") + 0.3)
sfx = sfx[: int(edl.TOTAL * SR)]
wavfile.write("work/sfx_full.wav", SR, (np.clip(sfx, -1, 1) * 32767).astype(np.int16))

# ---------- mix ----------
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/voice_full.wav", "-i", "work/sfx_full.wav",
                "-filter_complex", "[1:a]volume=0.8[f];[0:a][f]amix=inputs=2:normalize=0:duration=first,"
                "alimiter=limit=0.93[m]", "-map", "[m]", "-ar", str(SR), "-ac", "2", "work/mix_full.wav"],
               check=True)
print("audio ok", edl.TOTAL)
