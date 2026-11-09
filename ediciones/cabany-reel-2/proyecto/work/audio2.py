"""Original music bed + synthesized SFX + voice mix for the Cabany reel."""
import os, sys, math
import numpy as np
import scipy.io.wavfile as wf
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
DUR = 33.0
N = int(SR * DUR)
rng = np.random.default_rng(11)
BEAT = 0.46            # 130 BPM -> bar = 1.84 s ; drop at 7.36 s = bar 4
BUILD0, DROP, BRK, END = 5.52, 7.36, 25.6, 30.9
BAR = BEAT * 4

def T(t): return int(round(t * SR))
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def noise(n): return rng.standard_normal(n)
def sos(kind, f, order=2):
    if kind == 'bp': return signal.butter(order, [f[0] / (SR / 2), f[1] / (SR / 2)], 'bandpass', output='sos')
    return signal.butter(order, f / (SR / 2), kind, output='sos')
def filt(x, kind, f, order=2): return signal.sosfilt(sos(kind, f, order), x)
def add(buf, x, t, gain=1.0, pan=0.0):
    i = T(t)
    if i >= buf.shape[1] or i + len(x) <= 0: return
    j0 = max(0, -i); x = x[j0:]; i = max(i, 0)
    n = min(len(x), buf.shape[1] - i)
    l = math.cos((pan + 1) * math.pi / 4); r = math.sin((pan + 1) * math.pi / 4)
    buf[0, i:i + n] += x[:n] * gain * l * 1.414
    buf[1, i:i + n] += x[:n] * gain * r * 1.414
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------- instruments
def kick(dur=0.45):
    n = T(dur); tt = np.arange(n) / SR
    f = 48 + 110 * np.exp(-tt / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * env_exp(n, 0.16)
    x[:200] += noise(200) * 0.25 * env_exp(200, 0.0015)
    return np.tanh(x * 1.6)

def clap():
    n = T(0.3); x = np.zeros(n)
    for k, d in enumerate([0, 0.011, 0.022]):
        b = filt(noise(T(0.2)), 'bp', (900, 3200)) * env_exp(T(0.2), 0.012 if k < 2 else 0.06)
        x[T(d):T(d) + len(b)] += b[:n - T(d)]
    return x * 0.9

def hat(open_=False):
    n = T(0.25 if open_ else 0.06)
    return filt(noise(n), 'highpass', 7500) * env_exp(n, 0.06 if open_ else 0.012)

def shaker():
    n = T(0.08); e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return filt(noise(n), 'bp', (5000, 11000)) * e

def marimba(freq, dur=0.6, bright=1.0):
    n = T(dur); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * freq * tt) * env_exp(n, 0.32)
         + 0.35 * bright * np.sin(2 * np.pi * freq * 3.93 * tt) * env_exp(n, 0.05)
         + 0.12 * bright * np.sin(2 * np.pi * freq * 9.2 * tt) * env_exp(n, 0.015))
    a = min(n, 60); x[:a] *= np.linspace(0, 1, a)
    return x

def pluck(freq, dur=0.5):
    # Karplus-Strong
    n = T(dur); L = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, L); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % L]
        buf[i % L] = 0.5 * (buf[i % L] + buf[(i + 1) % L]) * 0.996
    return filt(out, 'lowpass', 5000)

def saw(freq, n, detune=(0.0,)):
    tt = np.arange(n) / SR; x = np.zeros(n)
    for d in detune:
        f = freq * (1 + d); x += 2 * ((tt * f + rng.uniform()) % 1) - 1
    return x / len(detune)

def bass_note(freq, dur):
    n = T(dur); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * tt) + 0.25 * np.sin(2 * np.pi * freq * 2 * tt) + 0.08 * saw(freq, n)
    e = np.minimum(1, np.arange(n) / 200) * np.minimum(1, (n - np.arange(n)) / 600)
    return np.tanh(x * e * 1.2)

# ------------------------------------------------------------- music
# G - D - Em - C  (I-V-vi-IV), one chord per bar
CHORDS = [(55, [55, 59, 62]), (50, [50, 54, 57]), (52, [52, 55, 59]), (48, [48, 52, 55])]
LEAD = [(0, 79, .5), (0.75, 78, .5), (1.5, 76, .5), (2.5, 74, .75), (4, 76, .5), (4.75, 78, .5), (5.5, 79, .5), (6.5, 83, 1.0)]

def music():
    drums = np.zeros((2, N)); bass = np.zeros((2, N)); keys = np.zeros((2, N)); pad = np.zeros((2, N)); lead = np.zeros((2, N))
    K = kick(); CL = clap()
    side = np.ones(N)
    for b in range(int(DUR / BAR) + 1):
        t0 = b * BAR
        root, ch = CHORDS[b % 4]
        drop = DROP - 1e-6 <= t0 < BRK
        intro = t0 < BUILD0
        build = BUILD0 - 1e-6 <= t0 < DROP
        brk = BRK - 1e-6 <= t0 < END
        for k in range(4):
            tb = t0 + k * BEAT
            if tb >= END: break
            if (drop or intro or brk or (build and tb < DROP - 0.92)):
                g = 0.95 if drop else (0.55 if brk else 0.7)
                add(drums, K, tb, g)
                i = T(tb); n = min(T(0.3), N - i)
                if n > 0: side[i:i + n] = np.minimum(side[i:i + n], 1 - 0.75 * np.exp(-np.arange(n) / (0.09 * SR)))
            if drop and k in (1, 3): add(drums, CL, tb, 0.5)
            if brk and k in (1, 3): add(drums, CL, tb, 0.25)
            if drop or intro or brk:
                add(drums, hat(open_=drop and k % 2 == 1), tb + BEAT / 2, 0.20 if drop else 0.12, 0.25)
            if drop:
                for q in range(4): add(drums, shaker(), tb + q * BEAT / 4, 0.06 + 0.04 * (q % 2), -0.3)
        if drop or build:
            for k in range(8):
                tb = t0 + k * BEAT / 2
                if k % 2 == 1 and tb < BRK: add(bass, bass_note(mtof(root - 12), BEAT / 2 * 0.9), tb, 0.55)
        elif intro or brk:
            add(bass, bass_note(mtof(root - 12), BAR * 0.95), t0, 0.30)
        pat = [0, 0.75, 1.5, 2.5, 3.25] if (drop or brk) else [0, 1.5, 2.5]
        for p in pat:
            tb = t0 + p * BEAT
            if tb >= END: continue
            for m in ch: add(keys, marimba(mtof(m + 12), 0.45, 0.8), tb, 0.10, rng.uniform(-0.4, 0.4))
        n = T(BAR + 0.15)
        pd = sum(saw(mtof(m), n, (-0.004, 0.0, 0.005)) for m in ch)
        pd = filt(pd, 'lowpass', 1400 if drop else 900) * np.minimum(1, np.arange(n) / (0.12 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.12 * SR))
        if t0 < END: add(pad, pd, t0, 0.05, 0)
        if drop and b % 2 == 0:
            for off, m, ln in LEAD: add(lead, marimba(mtof(m), ln * BEAT + 0.3, 1.0), t0 + off * BEAT, 0.14, 0.15)
    t = BUILD0 + 0.3; step = BEAT / 2
    while t < DROP - 0.05:
        g = 0.12 + 0.35 * (t - BUILD0) / (DROP - BUILD0)
        add(drums, filt(noise(T(0.12)), 'bp', (700, 4000)) * env_exp(T(0.12), 0.03), t, g)
        t += step
        if t > DROP - 0.92: step = BEAT / 4
        if t > DROP - 0.46: step = BEAT / 8
    for m in [43, 55, 59, 62, 67]:
        add(keys, marimba(mtof(m + 12), 1.8, 0.9), END, 0.13, rng.uniform(-0.5, 0.5))
        n = T(2.0); x = saw(mtof(m), n, (-0.004, 0.005)); x = filt(x, 'lowpass', 1200) * env_exp(n, 0.9)
        add(pad, x, END, 0.05)
    add(drums, K, END, 0.9)
    for tr in (bass, pad, keys): tr *= side
    lp_keys = np.stack([filt(keys[c], 'lowpass', 700) for c in range(2)])
    lp_pad = np.stack([filt(pad[c], 'lowpass', 500) for c in range(2)])
    tt = np.arange(N) / SR
    k = np.ones(N)
    k = np.where(tt < BUILD0, 0.6, k)
    k = np.where((tt >= BUILD0) & (tt < DROP), 0.6 + 0.4 * ((tt - BUILD0) / (DROP - BUILD0)) ** 2, k)
    k = np.where((tt >= BRK) & (tt < END), 0.45, k)
    keys = lp_keys * (1 - k) + keys * k
    pad = lp_pad * (1 - k) + pad * k
    mix = drums * 0.9 + bass * 0.9 + keys + pad + lead
    ir = noise(T(1.1)) * env_exp(T(1.1), 0.28); ir = filt(ir, 'lowpass', 6000); ir /= np.abs(ir).sum() ** 0.5 * 8
    wet = np.stack([signal.fftconvolve((keys + lead + pad)[c], ir)[:N] for c in range(2)])
    mix += wet * 0.6
    mix = filt_st(mix, 'highpass', 30)
    mix[:, T(32.2):] *= np.linspace(1, 0, N - T(32.2))
    return mix

def filt_st(x, kind, f): return np.stack([filt(x[c], kind, f) for c in range(2)])

# ------------------------------------------------------------- SFX
def whoosh(dur=0.45, f0=300, f1=3500, peak=0.55, bright=1.0):
    n = T(dur); tt = np.linspace(0, 1, n)
    x = noise(n); out = np.zeros(n); blk = 256
    for i in range(0, n, blk):
        p = tt[i]
        fc = f0 * (f1 / f0) ** (p / peak) if p < peak else f1 * (f0 / f1) ** ((p - peak) / (1 - peak))
        fc = min(fc, SR / 2 * 0.9)
        b = signal.butter(2, [fc * 0.6 / (SR / 2), min(0.99, fc * 1.6 / (SR / 2))], 'bandpass', output='sos')
        out[i:i + blk] = signal.sosfilt(b, x[i:i + blk])
    e = np.where(tt < peak, (tt / peak) ** 2, ((1 - tt) / (1 - peak)) ** 1.5)
    out = out * e * bright
    return out / (np.abs(out).max() + 1e-9)

def pop(f=900, dur=0.09):
    n = T(dur); tt = np.arange(n) / SR
    fr = f * (1 + 1.4 * np.exp(-tt / 0.012))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * env_exp(n, 0.025)
    x[:60] += noise(60) * 0.3
    return x

def bubble(f=700):
    n = T(0.12); tt = np.arange(n) / SR
    fr = f * (0.7 + 1.0 * (1 - np.exp(-tt / 0.02)))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env_exp(n, 0.035) * np.minimum(1, np.arange(n) / 40)

def click():
    n = T(0.03)
    x = filt(noise(n), 'bp', (1800, 6000)) * env_exp(n, 0.003)
    x += np.sin(2 * np.pi * 2400 * np.arange(n) / SR) * env_exp(n, 0.004) * 0.4
    return x

def ding(f=1568, dur=0.9):
    n = T(dur); tt = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * r * tt) * env_exp(n, d) for a, r, d in [(1, 1, .35), (.5, 2.0, .2), (.25, 2.76, .12), (.15, 5.4, .05)])
    x[:30] *= np.linspace(0, 1, 30)
    return x

def impact(dur=1.4):
    n = T(dur); tt = np.arange(n) / SR
    f = 42 + 60 * np.exp(-tt / 0.06)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.45)
    x += filt(noise(n), 'lowpass', 900) * env_exp(n, 0.12) * 0.5
    return np.tanh(x * 1.4)

def riser(dur=2.0):
    n = T(dur); tt = np.linspace(0, 1, n)
    x = noise(n); out = np.zeros(n); blk = 512
    for i in range(0, n, blk):
        fc = 400 * (9000 / 400) ** tt[i]
        b = signal.butter(2, [fc * 0.7 / (SR / 2), min(0.99, fc * 1.4 / (SR / 2))], 'bandpass', output='sos')
        out[i:i + blk] = signal.sosfilt(b, x[i:i + blk])
    ph = 2 * np.pi * np.cumsum(220 * (4 ** tt)) / SR
    out = out / (np.abs(out).max() + 1e-9) + 0.25 * np.sin(ph) + 0.12 * np.sin(ph * 1.5)
    return out * tt ** 2.2

def shutter():
    a = filt(noise(T(0.02)), 'bp', (1500, 7000)) * env_exp(T(0.02), 0.004)
    b = filt(noise(T(0.05)), 'bp', (800, 5000)) * env_exp(T(0.05), 0.01)
    x = np.zeros(T(0.12)); x[:len(a)] += a; x[T(0.06):T(0.06) + len(b)] += b * 0.8
    return x

def shimmer(dur=1.2):
    n = T(dur); x = np.zeros(n)
    for k in range(28):
        f = rng.uniform(2500, 7000); t0 = rng.uniform(0, dur * 0.6); m = T(0.25)
        g = np.sin(2 * np.pi * f * np.arange(m) / SR) * env_exp(m, 0.06)
        i = T(t0); x[i:i + m] += g[:max(0, min(m, n - i))] * rng.uniform(0.2, 0.6)
    return x * np.linspace(1, 0.3, n)

def tick(): return pop(2600, 0.025) * 0.6

def chime():
    out = np.zeros(T(1.3))
    for k, m in enumerate([72, 76, 79, 84]):
        d = ding(mtof(m), 1.0); i = T(k * 0.07); out[i:i + len(d)] += d[:len(out) - i] * 0.6
    return out

def blip(f0=2430):
    """bright UI pop-up 'ting' (reference: partials near 9.7 kHz / 14.6 kHz)"""
    n = T(0.22); tt = np.arange(n) / SR
    fr = f0 * (1 + 0.06 * (1 - np.exp(-tt / 0.02)))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = (0.6 * np.sin(ph) * env_exp(n, 0.05) + 0.5 * np.sin(2 * ph) * env_exp(n, 0.06)
         + 0.35 * np.sin(4 * ph) * env_exp(n, 0.07) + 0.25 * np.sin(6 * ph) * env_exp(n, 0.07))
    x[:40] *= np.linspace(0, 1, 40)
    return x

def twinkle(dur=0.4, lo=2600, hi=7600):
    n = T(dur); x = np.zeros(n)
    k = 9
    for i in range(k):
        f = lo * (hi / lo) ** (i / (k - 1)); t0 = dur * 0.75 * i / k; m = T(0.14)
        g = np.sin(2 * np.pi * f * np.arange(m) / SR) * env_exp(m, 0.035)
        j = T(t0); x[j:j + m] += g[:max(0, min(m, n - j))] * (0.5 + 0.5 * i / k)
    return x

def ring_swoosh():
    w = whoosh(0.7, 500, 6000, peak=0.35)
    s = shimmer(0.8)[:len(w)]
    return w * 0.7 + np.pad(s, (0, len(w) - len(s))) * 0.6

def notif():
    out = np.zeros(T(0.6))
    for k, m in enumerate([84, 91]):
        d = ding(mtof(m), 0.5); i = T(k * 0.11); out[i:i + len(d)] += d[:len(out) - i] * 0.7
    return out

def sfx():
    S = np.zeros((2, N))
    W = lambda t, d=0.45, g=0.35, pan=0.0, **kw: add(S, whoosh(d, **kw), t - d * 0.55, g, pan)
    # big-word entrances: short airy swoosh (rise = upward, whip = sideways)
    for t, kind in [(0.98, 'rise'), (2.06, 'whip'), (3.48, 'whip'), (4.46, 'rise'), (4.74, 'rise'), (5.96, 'rise'),
                    (26.26, 'rise'), (27.24, 'whip'), (28.22, 'rise'), (30.34, 'rise')]:
        if kind == 'rise': W(t + 0.06, 0.26, 0.30, 0, f0=700, f1=7000, peak=0.6)
        else: W(t + 0.06, 0.30, 0.34, -0.5, f0=500, f1=5000, peak=0.5)
    # draw-on icons: sparkle ding (reference: tonal 4-8 kHz shine)
    for t, p in [(2.08, 0.4), (4.04, -0.4), (7.40, 0.0), (26.28, 0.4), (27.26, -0.4)]:
        add(S, twinkle(0.42, 3500, 9000), t, 0.22, p); add(S, ding(2637, 0.6), t + 0.02, 0.06, p)
    # door -> balcony flash
    W(2.62, 0.5, 0.42, 0.3, f0=600, f1=8000, peak=0.55)
    # heavy words: soft pop
    for t in (3.86, 6.42, 26.54, 28.64): add(S, pop(760, 0.08), t, 0.22)
    # iOS-style banner
    add(S, notif(), 6.52, 0.30, 0.0)
    # build into the drop / "paso 1"
    add(S, riser(1.5), 5.86, 0.28)
    W(7.36, 0.45, 0.45, 0, f0=800, f1=9000, peak=0.5)
    add(S, impact(1.3), 7.36, 0.55)
    add(S, pop(240, 0.16), 7.70, 0.45); add(S, impact(0.6), 7.70, 0.25)
    # into the tour
    W(8.06, 0.5, 0.45, 0, f0=200, f1=3000, peak=0.7)
    add(S, pop(300, 0.14), 8.45, 0.30)
    add(S, bubble(820), 8.58, 0.30)
    for k in range(16): add(S, click(), 8.62 + k * (10.66 - 8.62) / 16, 0.30, rng.uniform(-0.2, 0.2))   # typing the URL
    add(S, ding(2093, 0.5), 9.78, 0.10, 0.3)
    W(10.95, 0.35, 0.32, 0.5, f0=400, f1=5000)
    for k, t in enumerate([11.10, 11.54, 11.80]):
        W(t + 0.12, 0.3, 0.24, -0.6 if k % 2 == 0 else 0.6, f0=600, f1=6000); add(S, pop(620 + 60 * k), t + 0.18, 0.26)
    add(S, pop(1000), 11.74, 0.30)
    W(12.33, 0.30, 0.42, 0.7, f0=600, f1=6000)
    add(S, bubble(700), 12.42, 0.32)
    for k in range(4): add(S, shutter(), 13.98 + 0.12 * k, 0.50, -0.5 + 0.33 * k)
    W(15.33, 0.45, 0.45, 0, f0=200, f1=3000, peak=0.7)
    for k, t in enumerate([15.40, 15.62, 15.96]): add(S, pop(860 + 90 * k), t, 0.32, -0.4 + 0.4 * k)
    W(17.73, 0.28, 0.30, 0.4, f0=500, f1=5000)
    add(S, pop(1100, 0.12), 18.28, 0.45); add(S, ding(1760, 0.8), 18.30, 0.14)
    for k, t in enumerate([19.32, 19.96, 21.04]): add(S, pop(900 + 80 * k), t, 0.32, 0.3 * (k - 1))
    add(S, ding(2093, 0.5), 19.66, 0.10)
    W(20.32, 0.30, 0.32, -0.4, f0=500, f1=5000)
    W(22.40, 0.30, 0.32, 0.4, f0=500, f1=5000)
    add(S, bubble(760), 22.30, 0.32); add(S, twinkle(), 22.36, 0.16)
    add(S, ding(2093, 0.5), 22.74, 0.10)
    add(S, click(), 23.32, 0.6)
    add(S, pop(940), 23.46, 0.30); add(S, pop(1040), 24.18, 0.30)
    W(24.20, 0.28, 0.28, -0.4, f0=500, f1=5000)
    add(S, pop(600, 0.14), 25.12, 0.40); add(S, chime(), 25.24, 0.32); add(S, shimmer(0.9), 25.22, 0.16)
    W(25.60, 0.45, 0.45, 0, f0=800, f1=9000, peak=0.5)
    add(S, bubble(840), 30.46, 0.30)
    # ending
    add(S, riser(1.0), 29.92, 0.24)
    W(30.92, 0.55, 0.45, 0, f0=250, f1=4000)
    add(S, impact(1.6), 30.95, 0.45); add(S, shimmer(1.4), 31.05, 0.20)
    add(S, pop(900), 31.10, 0.30); add(S, ding(1568, 0.9), 31.14, 0.10)
    return S

# ------------------------------------------------------------- voice + mix
def voice():
    sr, a = wf.read(f'{ROOT}/work/voice.wav')
    a = a.astype(np.float64) / 32768.0
    if a.ndim == 2: a = a.mean(1)
    v = np.zeros(N); n = min(len(a), N); v[:n] = a[:n]
    v = filt(v, 'highpass', 85)
    # tiny presence lift
    v = v + 0.25 * filt(v, 'bp', (2500, 6000))
    # leveling (AGC): bring every phrase to the same loudness
    k = T(0.40)
    env = np.sqrt(np.convolve(v ** 2, np.ones(k) / k, 'same'))
    ref = np.percentile(env[env > env.max() * 0.05], 70)
    g = np.clip(ref / np.maximum(env, ref * 0.15), 0.7, 2.6)
    g = np.convolve(g, np.ones(T(0.30)) / T(0.30), 'same')
    v = v * g
    v = np.tanh(v / (np.abs(v).max() * 0.8)) * 0.9
    v[T(30.95):] *= np.maximum(0, 1 - (np.arange(N - T(30.95)) / (0.25 * SR)))
    return v

def envelope(x, win=0.05):
    k = int(win * SR); e = np.sqrt(np.convolve(x ** 2, np.ones(k) / k, 'same'))
    return e

if __name__ == '__main__':
    if os.path.exists(f'{ROOT}/work/music.wav') and '--fresh' not in sys.argv:
        m = wf.read(f'{ROOT}/work/music.wav')[1].T.astype(np.float64)
    else:
        m = music()
    s = sfx()
    v = voice()
    ev = envelope(v); ev = ev / (ev.max() + 1e-9)
    act = np.clip((ev - 0.04) / 0.10, 0, 1)
    act = np.convolve(act, np.ones(T(0.25)) / T(0.25), 'same')
    duck = 1 - 0.45 * np.clip(act, 0, 1)
    m = m / (np.abs(m).max() + 1e-9)
    s = s / (np.abs(s).max() + 1e-9)
    v = v / (np.abs(v).max() + 1e-9)
    mix = np.stack([v, v]) * 0.80 + m * 0.24 * duck + s * 0.40
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.95
    wf.write(f'{ROOT}/work/mix.wav', SR, (mix.T * 32767).astype(np.int16))
    wf.write(f'{ROOT}/work/music.wav', SR, (m.T * 0.9 * 32767).astype(np.int16))
    wf.write(f'{ROOT}/work/sfx.wav', SR, (s.T * 0.9 * 32767).astype(np.int16))
    print('ok')
