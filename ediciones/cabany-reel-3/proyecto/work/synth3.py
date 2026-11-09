"""Original music bed + synthesized SFX + voice mix for the Cabany reel."""
import os, sys, math
import numpy as np
import scipy.io.wavfile as wf
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
import edl
DUR = round(edl.DUR_EDIT + 0.9, 2)
N = int(SR * DUR)
rng = np.random.default_rng(11)
BEAT = 60 / 92          # 92 BPM
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

