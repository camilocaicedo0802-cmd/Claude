"""Builds the voice track (cut + 1.1x + cleanup) and a synthesized SFX layer, then mixes them."""
import subprocess, sys, os
import numpy as np
from scipy.io import wavfile
from scipy import signal
import edl

SP = sys.argv[1]
os.chdir(SP)
SR = 48000

# ---------- voice ----------
parts, labels = [], []
for i, (name, a, b) in enumerate(edl.AUDIO_SEGS):
    d = b - a
    parts.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,aresample={SR},"
                 f"afade=t=in:st=0:d=0.012,afade=t=out:st={d-0.02:.3f}:d=0.02[s{i}]")
    labels.append(f"[s{i}]")
fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1[cat];" \
     f"[cat]atempo={edl.SPEED},highpass=f=90,afftdn=nf=-28," \
     "equalizer=f=3500:t=q:w=1.2:g=2.5,equalizer=f=250:t=q:w=1.0:g=-2," \
     "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2," \
     f"loudnorm=I=-14:TP=-1.5:LRA=7,aresample={SR},atrim=0:{edl.TOTAL:.4f}[v]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "raw/toma_ugc.mov", "-filter_complex", fc,
                "-map", "[v]", "-ac", "1", "-c:a", "pcm_s16le", "work/voice.wav"], check=True)

# ---------- SFX ----------
rng = np.random.default_rng(7)
N = int(edl.NFRAMES / edl.FPS * SR) + SR
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
shot = {s["id"]: s for s in edl.SHOTS}
place(whoosh(0.34, True, 0.30), shot["S2"]["f0"] / fps - 0.17)
place(whoosh(0.40, True, 0.34), shot["S3"]["f0"] / fps - 0.2)
place(riser(0.5), edl.src_to_out(35.45))
place(pop(0.30), shot["S4"]["f0"] / fps + 0.02)
place(pop(0.22, 1200, 500), edl.src_to_out(38.98))
place(whoosh(0.34, False, 0.30), shot["S5"]["f0"] / fps - 0.17)
place(pop(0.20, 1100, 420), shot["S5"]["f0"] / fps + 0.05)
place(whoosh(0.26, True, 0.22), shot["S6"]["f0"] / fps - 0.13)
place(whoosh(0.26, False, 0.20), shot["S7a"]["f0"] / fps - 0.13)
place(pop(0.24), shot["S7a"]["f0"] / fps + 0.02)
place(drop(0.22), edl.src_to_out(45.62))
place(ding(0.20), edl.src_to_out(47.16))

sfx = sfx[: int(edl.TOTAL * SR)]
wavfile.write("work/sfx.wav", SR, (np.clip(sfx, -1, 1) * 32767).astype(np.int16))

# ---------- mix ----------
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/voice.wav", "-i", "work/sfx.wav",
                "-filter_complex", "[1:a]volume=0.8[f];[0:a][f]amix=inputs=2:normalize=0:duration=first,"
                "alimiter=limit=0.93[m]", "-map", "[m]", "-ar", str(SR), "-ac", "2", "work/mix.wav"],
               check=True)
print("audio ok", edl.TOTAL)
