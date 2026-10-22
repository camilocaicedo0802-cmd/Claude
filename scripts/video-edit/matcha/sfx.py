"""Synthesize the sound effects used by the edit (all generated, no external samples)."""
import numpy as np, scipy.signal as sg, scipy.io.wavfile as wf, sys, os
SR = 48000
out = sys.argv[1]
rng = np.random.default_rng(7)

def save(name, x, peak=0.89):
    x = np.asarray(x, np.float64)
    if x.ndim == 1: x = np.stack([x, x], 1)
    x = x / (np.abs(x).max() + 1e-9) * peak
    wf.write(os.path.join(out, name + ".wav"), SR, (x * 32767).astype(np.int16))

def env_ad(n, a, d, curve=3.0):
    t = np.arange(n) / SR
    e = np.where(t < a, (t / a) ** 2, np.exp(-(t - a) / d * curve / 3))
    return e

def bandsweep(noise, f0, f1, q=2.0, steps=64):
    # time-varying bandpass by block processing
    n = len(noise); y = np.zeros(n); blk = n // steps + 1
    zi = None
    for k in range(steps):
        s, e = k * blk, min(n, (k + 1) * blk)
        if s >= n: break
        f = f0 * (f1 / f0) ** (k / (steps - 1))
        b, a = sg.butter(2, [max(30, f / q), min(SR / 2 - 100, f * q)], btype="band", fs=SR)
        if zi is None: zi = sg.lfilter_zi(b, a) * 0
        y[s:e], zi = sg.lfilter(b, a, noise[s:e], zi=zi)
    return y

# whoosh: noise swept up then down, swelling then cutting
def whoosh(dur=0.45, f0=300, f1=4000, pan=True):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    sweep = bandsweep(noise, f0, f1, q=1.8)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2.2
    e *= np.clip((dur - t) / 0.05, 0, 1)
    x = sweep * e
    if pan:
        p = np.linspace(-0.8, 0.8, n)
        return np.stack([x * np.sqrt((1 - p) / 2), x * np.sqrt((1 + p) / 2)], 1)
    return x

save("whoosh1", whoosh(0.40, 250, 5000))
save("whoosh2", whoosh(0.55, 150, 3000))
save("whoosh3", whoosh(0.30, 600, 8000))

# pop: short sine with fast downward pitch + click
def pop(f0=900, f1=300, dur=0.12):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 40)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 35)
    x[:200] += rng.standard_normal(200) * np.linspace(0.6, 0, 200)
    return x
save("pop1", pop())
save("pop2", pop(1400, 500, 0.10))
save("pop3", pop(700, 200, 0.14))

# impact / boom: sub drop + noise burst
def impact(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t * 18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    nb = sg.lfilter(*sg.butter(2, 2500, fs=SR), rng.standard_normal(n)) * np.exp(-t * 22)
    x = np.tanh(1.6 * (sub + 0.6 * nb))
    return x
save("impact", impact())

# riser: noise + rising tone, 1.2 s
def riser(dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = bandsweep(rng.standard_normal(n), 200, 7000, q=1.5)
    f = 200 * (8 ** (t / dur))
    tone = sg.sawtooth(2 * np.pi * np.cumsum(f) / SR) * 0.15
    tone = sg.lfilter(*sg.butter(2, 3000, fs=SR), tone)
    e = (t / dur) ** 2.5
    return (noise + tone) * e
save("riser", riser())

# ding: bell partials
def ding(f=1318.5, dur=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    parts = [(1, 1, 3), (2.0, 0.5, 4.5), (2.76, 0.35, 6), (5.4, 0.2, 9), (8.9, 0.1, 12)]
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in parts)
    x[:100] *= np.linspace(0, 1, 100)
    return x
save("ding", ding())
save("ding_low", ding(987.8))

# shimmer / sparkle: random high bell grains
def shimmer(dur=0.8):
    n = int(dur * SR); x = np.zeros(n)
    for k in range(14):
        s = int(rng.uniform(0, dur * 0.6) * SR); f = rng.uniform(2500, 6000)
        m = min(n - s, int(0.25 * SR)); t = np.arange(m) / SR
        x[s:s + m] += np.sin(2 * np.pi * f * t) * np.exp(-t * 18) * rng.uniform(0.3, 1)
    return x
save("shimmer", shimmer())

# glitch: bit-crushed square bursts
def glitch(dur=0.25):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(6):
        s = int(k * n / 6); e = int((k + 1) * n / 6)
        f = rng.uniform(150, 1800)
        x[s:e] = sg.square(2 * np.pi * f * t[s:e]) * rng.uniform(0.3, 1)
    x = np.round(x * 4) / 4
    return x * np.exp(-t * 6)
save("glitch", glitch())

# camera shutter / tick
def click():
    n = int(0.06 * SR); t = np.arange(n) / SR
    x = sg.lfilter(*sg.butter(2, [1500, 9000], btype="band", fs=SR), rng.standard_normal(n)) * np.exp(-t * 90)
    return x
save("click", click())

# cartoon wobble for the dizzy moment
def wobble(dur=0.7):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 500 + 180 * np.sin(2 * np.pi * 9 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * np.clip(t / 0.02, 0, 1)
save("wobble", wobble())
print(sorted(os.listdir(out)))
