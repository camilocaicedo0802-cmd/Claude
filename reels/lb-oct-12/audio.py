#!/usr/bin/env python3
"""ASMR sound design for reel LB-OCT-12.

Soft, close and low: every effect is high-passed, low-passed (no harsh highs), placed only where
there is a clear physical action, over an almost inaudible pink-noise bed and a very quiet pad.

Usage:
    python audio.py --raw <dir with clips> --sfx <dir with Mixkit previews <id>.mp3> --out mix.wav
"""
import argparse
import json
import os
import subprocess

import numpy as np
from scipy import signal

import edl

SR = 48000
FPS = edl.FPS


# ---------------------------------------------------------------- helpers

def db(x):
    return 10 ** (x / 20)


def load(path, start=0.0, dur=None, hp=90, lp=6500, extra=""):
    """Decode a sound to float stereo, trimmed and gently filtered (no harsh lows or highs)."""
    af = [f"highpass=f={hp}", f"lowpass=f={lp}", f"lowpass=f={lp}"]  # 24 dB/oct: no harsh highs
    if extra:
        af.append(extra)
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start}", "-i", path]
    if dur:
        cmd += ["-t", f"{dur}"]
    cmd += ["-af", ",".join(af), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    x = x.reshape(-1, 2).astype(np.float64)
    peak = np.abs(x).max()
    return x / peak if peak > 0 else x


def fade(x, fin=0.01, fout=0.05):
    n = len(x)
    a, b = min(int(fin * SR), n // 2), min(int(fout * SR), n // 2)
    env = np.ones(n)
    if a:
        env[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    if b:
        env[n - b:] = np.cos(np.linspace(0, np.pi / 2, b)) ** 2
    return x * env[:, None]


def pan_gains(p):
    th = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return np.cos(th), np.sin(th)


def bandpass(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def lowpass(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, fs=SR, output="sos"), x, axis=0)


class Bus:
    def __init__(self, seconds):
        self.x = np.zeros((int(seconds * SR) + SR, 2))

    def add(self, sig, t, gain_db=0.0, pan=0.0, fin=0.01, fout=0.06):
        """Place a sound at time t (s). pan may be a (from, to) sweep."""
        sig = fade(sig, fin, fout) * db(gain_db)
        mono = sig.mean(axis=1) if sig.ndim == 2 else sig
        if isinstance(pan, tuple):
            p = np.linspace(pan[0], pan[1], len(mono))
        else:
            p = np.full(len(mono), float(pan))
        gl, gr = pan_gains(p)
        width = 0.35  # keep a little of the original stereo image
        if sig.ndim == 2:
            left = (1 - width) * mono * gl * np.sqrt(2) + width * sig[:, 0]
            right = (1 - width) * mono * gr * np.sqrt(2) + width * sig[:, 1]
        else:
            left, right = mono * gl * np.sqrt(2), mono * gr * np.sqrt(2)
        i = int(round(t * SR))
        if i < 0:
            left, right, i = left[-i:], right[-i:], 0
        n = min(len(left), len(self.x) - i)
        self.x[i:i + n, 0] += left[:n]
        self.x[i:i + n, 1] += right[:n]


def ff(x, af):
    """Run a stereo float buffer through an ffmpeg audio filter."""
    out = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", af,
                          "-f", "f32le", "-"], input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    y = np.frombuffer(out.stdout, np.float32).reshape(-1, 2).astype(np.float64)
    return np.pad(y, ((0, max(0, len(x) - len(y))), (0, 0)))[: len(x)]


def reverb_ir(seconds, damp_hz, seed):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-6.9 * t / seconds)[:, None]
    ir = lowpass(ir, damp_hz)
    ir[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(axis=0))


def convolve(x, ir):
    return np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)


# ---------------------------------------------------------------- timeline mapping

SHOTS, TOTAL = edl.build_timeline()
BY_ID = {s["id"]: s for s in SHOTS}
DURATION = TOTAL / FPS


def at(shot_id, src_t):
    """Output time (s) of a source time inside a shot."""
    s = BY_ID[shot_id]
    times = np.array(s["times"])
    if src_t <= times[0]:
        return s["start"] / FPS + (src_t - times[0])
    i = np.searchsorted(times, src_t) - 1
    i = min(i, len(times) - 2)
    frac = (src_t - times[i]) / (times[i + 1] - times[i])
    return (s["start"] + i + frac) / FPS


def motion(raw, shot_id):
    """Per-output-frame motion energy of a shot (0..1), used to drive fabric and skin textures."""
    s = BY_ID[shot_id]
    fps = 60 if s.get("ramp") else FPS
    cmd = ["ffmpeg", "-v", "error", "-ss", f'{s["times"][0]:.4f}', "-t", f'{s["tout"] - s["tin"] + 0.5:.3f}',
           "-i", os.path.join(raw, s["src"]),
           "-map", "0:v:0", "-vf", f"fps={fps},scale=72:128,format=gray", "-f", "rawvideo", "-"]
    fr = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.uint8)
    fr = fr.reshape(-1, 128, 72).astype(np.float32)
    idx = [min(int(round((t - s["times"][0]) * fps)), len(fr) - 1) for t in s["times"]]
    seq = fr[idx]
    m = np.r_[0, np.abs(np.diff(seq, axis=0)).mean(axis=(1, 2))]
    m = np.convolve(m, np.hanning(7) / np.hanning(7).sum(), mode="same")
    return np.clip(m / 18.0, 0, 1)


def env_to_audio(env_frames, length):
    t_f = np.arange(len(env_frames)) / FPS
    return np.interp(np.arange(length) / SR, t_f, env_frames)


# ---------------------------------------------------------------- synthesized textures

def pink(seconds, seed):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    spec = np.fft.rfft(rng.standard_normal((n, 2)), axis=0)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1]
    spec /= np.sqrt(f)[:, None]
    x = np.fft.irfft(spec, n, axis=0)
    x = lowpass(signal.sosfilt(signal.butter(2, 60, "high", fs=SR, output="sos"), x, axis=0), 2600)
    return x / np.sqrt((x ** 2).mean())


def fabric(env_frames, seed, lo=700, hi=5200, crackle=0.45):
    """Cloth rustle: dense tiny crackles plus a soft swish, shaped by on-screen motion."""
    rng = np.random.default_rng(seed)
    n = int(len(env_frames) / FPS * SR)
    env = env_to_audio(env_frames, n)
    rate = 30 + 420 * env  # crackle grains per second
    imp = (rng.random(n) < rate / SR) * rng.exponential(1.0, n)
    grain = np.hanning(int(0.006 * SR))
    crack = np.convolve(imp, grain, mode="same")
    noise = rng.standard_normal((n, 2))
    body = bandpass(noise, lo, hi)
    swish = bandpass(rng.standard_normal((n, 2)), lo * 0.6, hi * 0.5)
    x = body * (crackle * crack / (crack.std() + 1e-9))[:, None] * env[:, None] + swish * (1 - crackle) * env[:, None]
    x = lowpass(x, 5000, order=4)
    return x / (np.abs(x).max() + 1e-9)


def skin(env_frames, seed):
    """Hands gliding on oiled skin: very soft, low band noise."""
    rng = np.random.default_rng(seed)
    n = int(len(env_frames) / FPS * SR)
    env = env_to_audio(env_frames, n) ** 0.7
    x = bandpass(rng.standard_normal((n, 2)), 250, 2200) * env[:, None]
    return x / (np.abs(x).max() + 1e-9)


def hum(seconds, f0=118.0):
    """Gentle massage-device hum (low partials only)."""
    t = np.arange(int(seconds * SR)) / SR
    x = sum(a * np.sin(2 * np.pi * f0 * k * t + k) for k, a in [(1, 1.0), (2, 0.45), (3, 0.2), (4, 0.08)])
    x *= 1 + 0.12 * np.sin(2 * np.pi * 6.5 * t)
    x = lowpass(np.stack([x, x * 0.96], axis=1), 900)
    return x / np.abs(x).max()


def pad(seconds):
    """Minimal ambient pad: slow, warm chords (Dmaj9 - Bm9 - Gmaj9 - A6/9), long attack, lots of air."""
    chords = [[50, 57, 61, 64, 66], [47, 54, 57, 61, 62], [43, 50, 54, 57, 59], [45, 52, 57, 59, 61]]
    hold, xf = 7.0, 3.0
    n = int(seconds * SR)
    out = np.zeros((n, 2))
    t_all = np.arange(n) / SR
    k = 0
    start = 0.0
    while start < seconds:
        notes = chords[k % len(chords)]
        a, b = int(start * SR), min(n, int((start + hold + xf) * SR))
        t = t_all[a:b] - start
        env = np.minimum(1, t / xf) * np.minimum(1, np.maximum(0, (hold + xf - t) / xf))
        env = np.sin(env * np.pi / 2) ** 2
        for j, m in enumerate(notes):
            f = 440 * 2 ** ((m - 69) / 12)
            w = 0.9 if j == 0 else 0.55
            for det, ch in [(-0.0015, 0), (0.0015, 1)]:
                ph = 2 * np.pi * f * (1 + det) * t + j
                tone = np.sin(ph) + 0.12 * np.sin(2 * ph)
                out[a:b, ch] += w * tone * env * (1 + 0.15 * np.sin(2 * np.pi * 0.07 * t + j))
        start += hold
        k += 1
    out = lowpass(out, 850, order=4)
    out = 0.55 * out + 0.45 * convolve(out, reverb_ir(4.0, 2500, 7))
    return out / np.abs(out).max()


# ---------------------------------------------------------------- the mix

def build(raw, sfx_dir):
    S = lambda i: os.path.join(sfx_dir, f"{i}.mp3")
    fx, amb, mus = Bus(DURATION), Bus(DURATION), Bus(DURATION)

    step_hits = [0.90, 2.10, 2.70, 3.83, 4.61, 5.08, 5.67]
    steps = [load(S(534), t - 0.03, 0.34, hp=70, lp=3800) for t in step_hits]

    def step(t, g, pan=0.0, k=[0]):
        k[0] += 1
        fx.add(steps[k[0] % len(steps)], t, g, pan, 0.005, 0.12)

    whoosh = load(S(1461), 0.0, 1.2, hp=80, lp=3000)
    air = load(S(1489), 0.15, 1.6, hp=60, lp=2500)
    cloth = load(S(1898), 0.40, 1.40, hp=150, lp=6000)

    # Cuerpo 1: llega a casa
    fx.add(load(S(2856), 0.0, 0.6, hp=150, lp=4200), at("1a", 2.20), -27, 0.3)              # picaporte
    fx.add(air, at("1a", 2.30), -31, 0.25, 0.08, 0.4)                                        # aire de la puerta
    for t, g in [(2.95, -27), (3.40, -26), (3.85, -25), (4.30, -25)]:
        step(at("1a", t), g, 0.1)
    fx.add(load(S(182), 1.45, 1.0, hp=90, lp=3200), at("1b", 7.40) - 0.45, -28, 0.2, 0.15)  # cierra la puerta
    fx.add(cloth, at("1b", 9.45), -30, 0.0)                                                  # mochila
    for t in (10.10, 10.42):
        step(at("1b", t), -27, -0.1)
    fx.add(whoosh, at("1b", 10.62), -28, (0.5, -0.7), 0.06, 0.5)                             # efecto máscara
    fx.add(fabric(np.r_[np.linspace(0, 1, 12), np.linspace(1, 0, 18)], 11), at("1b", 10.62), -33, (0.4, -0.6))

    # Cuerpo 2: se sirve la bebida
    fx.add(load(S(1310), 0.10, 4.0, hp=140, lp=5000), at("2a", 1.95), -27, 0.15, 0.25, 0.6)  # líquido en la taza
    fx.add(load(S(2835), 1.30, 0.55, hp=300, lp=5000), at("2a", 4.95), -33, 0.2, 0.005, 0.3)  # tintineo suave
    fx.add(load(S(1307), 0.15, 0.80, hp=150, lp=5000), at("2b", 8.32), -30, -0.1, 0.02, 0.2)  # sorbo
    for t in (8.95, 9.25):
        step(at("2b", t), -24, -0.2)
    fx.add(whoosh, at("2b", 9.36), -29, (0.4, -0.8), 0.04, 0.45)                              # pasa frente a la cámara

    # Cuerpos 3 y 4: pasillo y habitación, ambiente casi en silencio + roce de la ropa
    amb.add(load(S(1173), 4.0, 11.0, hp=60, lp=1800), at("3", 2.55) - 0.3, -53, 0.0, 1.8, 2.5)
    for i, t in enumerate([2.75, 3.30, 3.85, 4.40, 4.95, 5.50, 6.02, 6.50]):
        step(at("3", t), -33 + i * 1.6, 0.0 + i * 0.04)
    fx.add(fabric(motion(raw, "3")[-30:], 12, crackle=0.35), at("3", 6.95) - 1.0, -34, (0.0, 0.7))
    for t in (14.35, 14.95, 15.55, 16.15, 16.75, 17.35):
        step(at("4b", t), -28, -0.1)
    fx.add(fabric(motion(raw, "4b") * 0.6, 13, crackle=0.3), at("4b", 13.95), -35, 0.0, 0.4, 0.6)

    # Cuerpo 5: habitación -> baño; interruptor antiguo y agua corriendo muy suave
    for t, g in [(119.05, -28), (119.55, -27), (120.05, -27)]:
        step(at("5a", t), g, -0.3)
    for t, g in [(123.95, -26), (124.45, -25), (124.95, -24)]:
        step(at("5b", t), g, 0.0)
    fx.add(load(S(2585), 0.0, 0.40, hp=200, lp=4800), at("5b", 125.15), -26, 0.45, 0.002, 0.15)  # clic
    amb.add(load(S(1323), 0.6, 7.0, hp=120, lp=2800), at("5b", 125.30), -42, 0.35, 1.4, 2.6)    # agua
    fx.add(air, at("5b", 125.80), -28, (0.3, -0.3), 0.05, 0.5)                                    # cabello cubre
    fx.add(fabric(np.r_[np.linspace(0, 1, 8), np.linspace(1, 0, 14)], 14, lo=1200, hi=6000, crackle=0.6),
           at("5b", 125.80), -32, 0.0)

    # Cuerpo 6: bata del perchero (sonido clave: la tela) y camisa que cubre la cámara
    fx.add(cloth, at("6a", 1.85) - 0.85, -29, 0.1)
    fx.add(fabric(motion(raw, "6a"), 21, lo=900, hi=6000, crackle=0.3), at("6a", 1.45), -30, 0.1, 0.3, 0.5)
    m6 = motion(raw, "6b")
    fx.add(fabric(m6, 22, lo=450, hi=3600, crackle=0.45), at("6b", 7.0), -30, 0.0, 0.3, 0.3)
    fx.add(whoosh, at("6b", 10.05), -31, (-0.2, 0.2), 0.05, 0.4)

    # Cuerpo 7: ponerse la bata (seda / algodón), cabello cubre la cámara
    fx.add(cloth, at("7a", 1.30) - 0.85, -27, -0.1)
    fx.add(fabric(motion(raw, "7a"), 31, lo=900, hi=6000, crackle=0.28), at("7a", 0.55), -29, -0.1, 0.4, 0.5)
    fx.add(fabric(motion(raw, "7b") * 0.7, 32, lo=900, hi=5500, crackle=0.25), at("7b", 8.40), -33, -0.1, 0.4, 0.5)
    fx.add(fabric(motion(raw, "7c"), 33, lo=1400, hi=6000, crackle=0.55), at("7c", 12.40), -33, 0.0, 0.4, 0.3)
    fx.add(air, at("7c", 15.55), -28, (-0.3, 0.3), 0.05, 0.6)

    # Cuerpo 8: masaje, yemas sobre el teléfono, hoja del calendario
    fx.add(skin(motion(raw, "8a"), 41), at("8a", 72.45), -35, 0.0, 0.3, 0.4)
    fx.add(load(S(1883), 0.10, 0.70, hp=200, lp=3800), at("8b", 24.05), -33, 0.1, 0.01, 0.2)   # aceite
    fx.add(skin(motion(raw, "8b") * 0.8, 42), at("8b", 24.0), -35, 0.0, 0.3, 0.4)
    taps = [load(S(1393), t - 0.01, 0.10, hp=300, lp=4200) for t in (0.12, 0.62, 1.38)]
    for i, t in enumerate((62.05, 62.55, 63.10)):
        fx.add(taps[i], at("8c", t), -34, 0.25, 0.002, 0.04)                                   # yemas en la pantalla
    fx.add(load(S(1101), 1.75, 0.85, hp=200, lp=5500), at("8d", 75.55), -27, 0.3, 0.02, 0.25)  # hoja del calendario
    t8 = at("8e", 89.25)
    amb.add(hum(DURATION - t8), t8, -61, 0.15, 0.8, 2.5)                                        # aparato de masaje
    fx.add(skin(motion(raw, "8e"), 43), t8, -38, 0.1, 0.4, 2.0)

    # Bed: almost inaudible pink noise, plus a minimal pad far below everything (<= -30 dB)
    amb.add(pink(DURATION, 5), 0.0, -71, 0.0, 1.5, 3.0)
    mus.add(pad(DURATION + 1), 0.0, 0.0, 0.0, 2.5, 3.5)

    room = reverb_ir(0.45, 3500, 3)
    fx.x = fx.x + 0.12 * convolve(fx.x, room)
    # gentle glue: rounds off transients so nothing sounds hard
    fx.x = ff(fx.x * db(12), "acompressor=threshold=0.05:ratio=2.5:attack=6:release=220:knee=8:makeup=1") * db(-12)
    return fx.x, amb.x, mus.x


def loudness(x):
    """Integrated loudness (LUFS) via ffmpeg's EBU R128 meter."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       input=x.astype(np.float32).tobytes(), capture_output=True)
    txt = p.stderr.decode()
    return float(json.loads(txt[txt.rindex("{"):])["input_i"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--sfx", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--target", type=float, default=-18.0, help="integrated loudness, LUFS (intimate, not loud)")
    ap.add_argument("--pad", type=float, default=-32.0, help="pad loudness in the final mix, LUFS")
    args = ap.parse_args()

    fx, amb, mus = build(args.raw, args.sfx)
    n = int(DURATION * SR)
    fx, amb, mus = fx[:n], amb[:n], mus[:n]
    dry = fx + amb
    gain = args.target - loudness(dry)
    mus_gain = args.pad - (loudness(mus) + gain)
    mix = (dry + mus * db(mus_gain)) * db(gain)
    gain2 = args.target - loudness(mix)
    mix *= db(gain2)
    peak = np.abs(mix).max()
    ceiling = db(-2.0)
    if peak > ceiling:  # soft clip only the rare peaks above -2 dBFS
        over = np.abs(mix) > ceiling * 0.8
        knee = ceiling * 0.8
        mix[over] = np.sign(mix[over]) * (knee + (ceiling - knee) * np.tanh((np.abs(mix[over]) - knee) / (ceiling - knee)))
    tail = int(2.0 * SR)
    mix[-tail:] *= np.cos(np.linspace(0, np.pi / 2, tail))[:, None] ** 2
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", args.out], input=mix.astype(np.float32).tobytes(), check=True)
    print(json.dumps({"mix_lufs": round(loudness(mix), 1),
                      "pad_lufs_in_mix": round(loudness(mus * db(mus_gain + gain + gain2)), 1),
                      "fx_lufs_in_mix": round(loudness(fx * db(gain + gain2)), 1),
                      "peak_dbfs": round(20 * np.log10(np.abs(mix).max()), 1)}))


if __name__ == "__main__":
    main()
