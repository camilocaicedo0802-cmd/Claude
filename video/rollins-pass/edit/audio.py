"""Build the soundtrack: voice + music beds (ducked) + synthesized SFX synced to the edit.

usage: python audio.py OUT.wav"""
import os
import subprocess
import sys

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOTAL = 1171.49
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(1)


def load(path, start=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", path]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def db(x):
    return 10 ** (x / 20)


def place(buf, clip, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[: j - i] * gain


def fade(x, fin=0.0, fout=0.0):
    n = len(x)
    if fin > 0:
        k = min(n, int(fin * SR))
        x[:k] *= np.linspace(0, 1, k)[:, None]
    if fout > 0:
        k = min(n, int(fout * SR))
        x[n - k:] *= np.linspace(1, 0, k)[:, None]
    return x


def stereo(m, pan=0.0):
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    return np.stack([m * l * 1.41, m * r * 1.41], 1).astype(np.float32)


# ------------------------------------------------------------------ SFX synthesis
def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def lp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def whoosh(d=0.55, lo=300, hi=5000):
    n = int(d * SR)
    t = np.linspace(0, 1, n)
    noise = rng.normal(0, 1, n)
    # sweep: blend of low and high bands
    low = bp(noise, lo, lo * 4)
    high = bp(noise, hi / 3, hi)
    env = np.sin(np.pi * t) ** 2
    mix = low * (1 - t) + high * t
    m = mix * env
    m /= np.abs(m).max() + 1e-9
    l = m * np.clip(1.4 - t * 1.2, 0, 1)
    r = m * np.clip(0.2 + t * 1.2, 0, 1)
    return np.stack([l, r], 1).astype(np.float32) * 0.6


def boom(d=1.8, f0=110, f1=38):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 2.6)
    s += lp(rng.normal(0, 1, n), 400) * np.exp(-t * 18) * 0.6
    s = np.tanh(s * 1.6)
    return stereo(s / np.abs(s).max() * 0.9)


def hit(d=0.35):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 180 * t * np.exp(-t * 3)) * np.exp(-t * 16)
    s += hp(rng.normal(0, 1, n), 2000) * np.exp(-t * 60) * 0.5
    return stereo(s / np.abs(s).max() * 0.7)


def riser(d=1.6):
    n = int(d * SR)
    t = np.linspace(0, 1, n)
    f = 180 + 1100 * t ** 2
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * 0.4 + bp(rng.normal(0, 1, n), 800, 6000) * 0.6 * t
    s *= t ** 2
    return stereo(s / np.abs(s).max() * 0.5)


def rumble(d=6.0, swell=True):
    n = int(d * SR)
    t = np.linspace(0, 1, n)
    brown = np.cumsum(rng.normal(0, 1, n))
    brown = hp(brown, 18)
    s = lp(brown, 70, 4)
    env = (np.sin(np.pi * t) ** 1.5) if swell else np.ones(n)
    env *= 0.75 + 0.25 * np.sin(2 * np.pi * t * 3.1)
    s = s / (np.abs(s).max() + 1e-9) * env
    return stereo(s * 0.95)


def shutter():
    out = np.zeros((int(0.25 * SR), 2), np.float32)
    for k, g in ((0, 1.0), (0.07, 0.7)):
        n = int(0.012 * SR)
        c = hp(rng.normal(0, 1, n), 1500) * np.exp(-np.arange(n) / SR * 400)
        place(out, stereo(c / np.abs(c).max() * 0.6), k, g)
    return out


def ticks(d=1.0, rate=14):
    out = np.zeros((int(d * SR), 2), np.float32)
    for k in np.arange(0, d - 0.03, 1 / rate):
        n = int(0.008 * SR)
        c = hp(rng.normal(0, 1, n), 2500) * np.exp(-np.arange(n) / SR * 600)
        place(out, stereo(c / np.abs(c).max() * 0.25, rng.uniform(-0.3, 0.3)), k)
    return out


def static(d=1.0):
    n = int(d * SR)
    s = bp(rng.normal(0, 1, n), 1000, 8000) * (0.6 + 0.4 * (rng.random(n) > 0.97))
    return fade(stereo(s / np.abs(s).max() * 0.12), 0.05, 0.2)


def engine(d=4.0):
    """Distant race engine reverberating in a tunnel (low-passed, growing)."""
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 70 + 160 * (t / d) ** 1.3
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sign(np.sin(ph * k)) / k for k in (1, 2, 3, 4))
    s = lp(s, 900, 4) + lp(rng.normal(0, 1, n), 300) * 0.3
    s = np.tanh(s * 1.5)
    # simple reverb: sum of delays
    out = s.copy()
    for dl, g in ((0.031, 0.5), (0.057, 0.4), (0.089, 0.33), (0.131, 0.25), (0.177, 0.2)):
        k = int(dl * SR)
        out[k:] += s[:-k] * g
    env = np.minimum(1, t / 0.8) * np.minimum(1, (d - t) / 0.6)
    out = out * env
    return stereo(out / np.abs(out).max() * 0.6)


def gunshot():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    s = rng.normal(0, 1, n) * np.exp(-t * 30) + np.sin(2 * np.pi * 90 * t) * np.exp(-t * 12)
    out = s.copy()
    for dl, g in ((0.05, 0.5), (0.11, 0.35), (0.19, 0.25), (0.3, 0.15)):
        k = int(dl * SR)
        out[k:] += s[:-k] * g
    return stereo(lp(out, 3000) / np.abs(out).max() * 0.6)


def birds(d=4.0, n=7, seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros((int(d * SR), 2), np.float32)
    for _ in range(n):
        t0 = r.uniform(0, d - 0.6)
        m = int(r.integers(2, 5))
        f0 = r.uniform(2600, 4200)
        for k in range(m):
            L = r.uniform(0.05, 0.12)
            tt = np.arange(int(L * SR)) / SR
            f = f0 * (1 + 0.35 * np.sin(np.pi * tt / L)) * r.uniform(0.9, 1.1)
            c = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / L) ** 2
            place(out, stereo(c * 0.25, r.uniform(-0.7, 0.7)), t0 + k * (L + 0.03))
    return out


def squeal(d=1.2):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 2300 + 250 * np.sin(2 * np.pi * 6 * t)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + bp(rng.normal(0, 1, n), 1800, 3600) * 0.6
    env = np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.3)
    return stereo(s / np.abs(s).max() * env * 0.35)


def horn(d=1.4):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = sum(np.sign(np.sin(2 * np.pi * f * t)) / (i + 1) for i, f in enumerate((233, 294, 349)))
    s = lp(s, 1600, 2)
    env = np.minimum(1, t / 0.04) * np.minimum(1, (d - t) / 0.1)
    # doppler-ish pass: pan left to right
    m = s / np.abs(s).max() * env * 0.5
    pan = np.linspace(-0.9, 0.9, n)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    return np.stack([m * l * 1.41, m * r * 1.41], 1).astype(np.float32)


def heartbeat(d=2.0, bpm=62):
    out = np.zeros((int(d * SR), 2), np.float32)
    for k in np.arange(0, d - 0.3, 60 / bpm):
        for dt, g in ((0, 1.0), (0.18, 0.7)):
            n = int(0.16 * SR)
            tt = np.arange(n) / SR
            c = np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 26)
            place(out, stereo(c * 0.9 * g), k + dt)
    return out


def jackhammer(d=3.0, rate=13):
    out = np.zeros((int(d * SR), 2), np.float32)
    for k in np.arange(0, d - 0.05, 1 / rate):
        n = int(0.05 * SR)
        tt = np.arange(n) / SR
        c = (bp(rng.normal(0, 1, n), 400, 3500) + np.sin(2 * np.pi * 120 * tt)) * np.exp(-tt * 70)
        place(out, stereo(c / (np.abs(c).max() + 1e-9) * 0.45, 0.1), k)
    return fade(out, 0.1, 0.3)


def drip_sfx(d=4.0, n=10, seed=3):
    r = np.random.default_rng(seed)
    out = np.zeros((int(d * SR), 2), np.float32)
    for _ in range(n):
        L = 0.09
        tt = np.arange(int(L * SR)) / SR
        f = r.uniform(900, 1700) * (1 + 1.5 * tt / L)
        c = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 45)
        out_c = np.zeros(len(c) + int(0.25 * SR))
        out_c[:len(c)] += c
        for dl, g in ((0.05, 0.45), (0.11, 0.3), (0.2, 0.18)):
            k = int(dl * SR)
            out_c[k:k + len(c)] += c * g
        place(out, stereo(out_c * 0.3, r.uniform(-0.6, 0.6)), r.uniform(0, d - 0.4))
    return out


def traffic_bed(d=4.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    brown = lp(np.cumsum(rng.normal(0, 1, n)), 200, 2)
    brown = hp(brown, 25)
    hiss = bp(rng.normal(0, 1, n), 500, 2500) * 0.25
    pass_env = 0.6 + 0.4 * np.sin(2 * np.pi * t / 1.7) ** 2
    m = (brown / (np.abs(brown).max() + 1e-9) + hiss) * pass_env
    return fade(stereo(m / np.abs(m).max() * 0.6), 0.5, 0.8)


def clank(d=0.5, f0=820.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f0 * r * t) * np.exp(-t * (14 + 6 * i)) / (i + 1) for i, r in enumerate((1.0, 2.76, 5.4, 8.9)))
    s += hp(rng.normal(0, 1, n), 3000) * np.exp(-t * 90) * 0.4
    return stereo(s / np.abs(s).max() * 0.6, rng.uniform(-0.3, 0.3))


# ------------------------------------------------------------------ music
# (start, end, file in assets/yt, offset_in_track, gain_db): YouTube Audio Library tracks chosen per chapter,
# gains bring every track to about -27.5 LUFS. Written by the music step into work/music.json.
SLOTS = [(0.0, 67.6), (66.4, 208.4), (207.0, 404.9), (403.5, 504.0), (502.6, 641.2), (639.8, 779.9), (778.5, 983.2), (981.8, 1056.9),
         (1055.5, TOTAL)]
_MJ = os.path.join(ROOT, "work", "music.json")
MUSIC = [tuple(m) for m in __import__("json").load(open(_MJ))] if os.path.exists(_MJ) else []


def wind(d=6.0, gust=0.6):
    """Howling wind: band-passed noise with slow random gusts."""
    n = int(d * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    g = np.interp(t, np.linspace(0, d, max(4, int(d * 1.5))), rng.uniform(1 - gust, 1.0, max(4, int(d * 1.5))))
    lo = bp(noise, 180, 900, 2) * 0.8
    hi = bp(noise, 900, 3200, 2) * 0.35 * g
    whistle = np.sin(2 * np.pi * np.cumsum(420 + 160 * g) / SR) * 0.06 * g
    m = (lo + hi) * g + whistle
    m = m / (np.abs(m).max() + 1e-9)
    env = np.minimum(1, np.minimum(t / 0.8, (d - t) / 1.2))
    l = m * env
    r = np.roll(m, int(0.013 * SR)) * env
    return np.stack([l, r], 1).astype(np.float32) * 0.8


def build_music():
    buf = np.zeros((N, 2), np.float32)
    for s, e, name, off, g in MUSIC:
        path = os.path.join(ROOT, "assets", name)
        clip = load(path, off, e - s + 0.5)
        # loop if the track is shorter than the slot
        need = int((e - s) * SR)
        while len(clip) < need:
            clip = np.concatenate([clip, load(path, 8.0, e - s)])
        clip = clip[:need]
        fade(clip, 2.0 if s > 0 else 0.5, 3.0)
        place(buf, clip, s, db(g))
    return buf


def duck(music, voice, depth_db=-9.0, attack=0.08, release=0.6):
    """Lower the music while the voice is active."""
    v = np.abs(voice).mean(1)
    win = int(0.05 * SR)
    env = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, mode="same"))
    thr = np.percentile(env[env > 1e-4], 35) if np.any(env > 1e-4) else 0.01
    active = (env > thr).astype(np.float32)
    # smooth with asymmetric attack/release
    a_up, a_dn = 1 - np.exp(-1 / (attack * SR)), 1 - np.exp(-1 / (release * SR))
    g = np.empty_like(active)
    x = 0.0
    step = 64
    for i in range(0, len(active), step):
        tgt = active[i:i + step].max()
        coef = a_up if tgt > x else a_dn
        x += (tgt - x) * (1 - (1 - coef) ** step)
        g[i:i + step] = x
    gain = db(depth_db * g)
    return music * gain[:, None]


def build_sfx():
    import timeline
    from gfx import BigText, CCTV, Counter, Stamp
    import gfx
    import gfx2
    import gfx3
    buf = np.zeros((N, 2), np.float32)
    shots = timeline.build()
    shots.sort(key=lambda s: s.start)
    for i, s in enumerate(shots):
        s.end = shots[i + 1].start if i + 1 < len(shots) else TOTAL
    WH = whoosh()
    WH2 = whoosh(0.4, 500, 7000)
    BOOM = boom()
    HIT = hit()
    RIS = riser()
    SH = shutter()
    for i, s in enumerate(shots):
        if s.tr in ("whip_l", "whip_r"):
            place(buf, WH, s.start - 0.3, db(-8))
        elif s.tr == "glitch":
            place(buf, static(0.35), s.start - 0.15, db(-2))
            place(buf, WH2, s.start - 0.2, db(-10))
        elif s.tr == "zoom":
            place(buf, WH, s.start - 0.35, db(-9))
        elif s.tr == "flash":
            place(buf, HIT, s.start - 0.02, db(-8))
        elif s.tr == "black":
            pass
        # chapter cards: riser before + boom on title
        ovs = s.ov
        names = [type(o).__name__ for o in ovs]
        if any(isinstance(o, BigText) and o.text.startswith("CAPÍTULO") for o in ovs):
            place(buf, RIS, s.start - 1.4, db(-14))
            place(buf, BOOM, s.start + 0.2, db(-7))
        for o in ovs:
            if isinstance(o, Stamp):
                place(buf, BOOM, s.start + o.t0, db(-9))
                place(buf, HIT, s.start + o.t0, db(-6))
            elif isinstance(o, BigText) and o.anim == "pop" and not o.text.startswith("CAPÍTULO"):
                place(buf, HIT, s.start + o.t0, db(-9))
            elif isinstance(o, Counter):
                place(buf, ticks(min(o.cd, 1.4), 18), s.start + o.t0, db(-14))
            elif isinstance(o, CCTV):
                place(buf, static(min(1.2, s.end - s.start)), s.start, db(-12))
            elif isinstance(o, gfx.FnOverlay) and o.fn is gfx3.gate_overlay:
                g0 = s.start + o.kw.get("t0", 0.4)
                place(buf, whoosh(0.9, 200, 2500), g0, db(-14))
                place(buf, HIT, g0 + 1.15, db(-6))
                place(buf, boom(0.8, 90, 50), g0 + 1.15, db(-12))
            elif isinstance(o, gfx.FnOverlay) and o.fn is gfx2.shutter_flash:
                for tt in o.kw.get("times", ()):
                    place(buf, SH, s.start + tt, db(-6))
            elif isinstance(o, gfx.Flash) and o.color[0] == 255 and o.color[1] in (230, 240):
                place(buf, gunshot(), s.start + o.t0, db(-10))
        if names and "Rich" in names and s.base.__class__.__name__ == "Solid":
            place(buf, ticks(1.0, 16), s.start + 0.1, db(-20))
    # handcrafted beds for this episode (kept subtle under the voice)
    from words import at as w
    # --- intro: the dirt road above the trees, the barrier, the trains in the snow
    for t0, d in ((0.0, 6.6), (13.5, 4.2), (26.3, 1.6), (43.7, 2.0), (50.9, 5.2)):
        place(buf, wind(d, 0.5), t0, db(-21))
    place(buf, car_pass(4.0) * 0.5, 0.2, db(-22))
    place(buf, scrape(0.5) * 0.5, 6.8, db(-22))
    place(buf, clank(0.3, 1900), 9.6, db(-24))
    place(buf, clank(0.4, 520), 16.0, db(-19))
    place(buf, chuff(5.0, 2.4), 21.9, db(-21))
    place(buf, steam_whistle(1.6), 24.0, db(-22))
    place(buf, wind(4.4, 0.9), 27.8, db(-18))
    place(buf, heartbeat(2.4, 58), 31.2, db(-18))
    place(buf, coins(), 38.3, db(-20))
    place(buf, ticks(2.4, 2.0), 41.3, db(-24))
    place(buf, drip_sfx(2.6, 5, 4), 48.5, db(-20))
    place(buf, riser(1.6), 54.4, db(-20))
    # --- Denver, Moffat and the toll road
    place(buf, crowd(3.6) * 0.5, 68.8, db(-25))
    place(buf, hooves(3.0, 2.2) * 0.5, 68.8, db(-24))
    place(buf, wind(4.0, 0.4), 72.5, db(-23))
    place(buf, chuff(6.0, 2.0) * 0.6, 86.6, db(-23))
    place(buf, paper(0.6), 92.9, db(-20))
    place(buf, coins(), 98.3, db(-19))
    place(buf, crowd(4.0) * 0.4, 104.2, db(-25))
    place(buf, paper(0.6), 108.4, db(-21))
    place(buf, clank(0.5, 300), w("banca", 117.6), db(-17))
    place(buf, coins(), 119.0, db(-20))
    place(buf, jackhammer(2.0, 9) * 0.4, 122.9, db(-25))
    place(buf, chuff(4.0, 2.6), 125.7, db(-21))
    place(buf, steam_whistle(1.4), 131.0, db(-23))
    place(buf, typewriter(2.4), 144.3, db(-22))
    place(buf, hit(0.35), w("dejaron", 149.6), db(-18))
    place(buf, hooves(4.0, 1.8) * 0.6, 163.7, db(-20))
    place(buf, cart(4.0), 163.9, db(-21))
    place(buf, coins(), 174.6, db(-17))
    place(buf, wind(4.0, 1.0), 182.3, db(-17))
    place(buf, wind(4.6, 0.6), 192.8, db(-21))
    place(buf, chuff(3.0, 2.4), 205.7, db(-19))
    place(buf, steam_whistle(1.6), 206.2, db(-20))
    # --- the shortcut over the top
    place(buf, chuff(5.0, 2.0) * 0.7, 217.4, db(-22))
    for k in range(5):
        place(buf, rivet(1500 + 60 * k), 272.9 + 0.7 * k, db(-24))
    place(buf, shovel(), 273.6, db(-21))
    place(buf, shovel(), 274.5, db(-22))
    place(buf, creak(1.0), 284.0, db(-20))
    place(buf, chuff(7.0, 1.2), 303.3, db(-19))
    place(buf, chuff(6.0, 1.0), 309.8, db(-21))
    place(buf, steam_whistle(1.8), 318.6, db(-20))
    place(buf, wind(8.0, 0.5), 318.5, db(-22))
    place(buf, birds(3.0, 4, 2), 337.1, db(-24))
    place(buf, wind(3.4, 0.8), 340.3, db(-20))
    # --- the Hill in winter
    place(buf, wind(14.0, 1.0), 343.8, db(-18))
    place(buf, wind(5.0, 1.0), 354.2, db(-19))
    for k in range(6):
        place(buf, axe(), 359.8 + 0.75 * k, db(-22))
    place(buf, wind(4.0, 0.8), 365.1, db(-21))
    place(buf, creak(1.2), 373.6, db(-16))
    place(buf, snap(), 375.0, db(-15))
    place(buf, fire(6.8), 376.6, db(-17))
    place(buf, chuff(4.0, 1.4), 383.6, db(-20))
    place(buf, tornado_bed(5.0) * 0.5, 387.1, db(-21))
    place(buf, chuff(3.0, 2.2) * 0.6, 395.7, db(-23))
    place(buf, wind(6.0, 1.0), 399.0, db(-17))
    place(buf, wind(10.0, 0.7), 403.2, db(-20))
    place(buf, heartbeat(4.0, 56), 413.6, db(-16))
    place(buf, wind(12.0, 0.6), 415.7, db(-21))
    place(buf, fire(3.0) * 0.6, 426.8, db(-19))
    place(buf, shovel(), 431.6, db(-21))
    place(buf, typewriter(2.0), 435.4, db(-23))
    place(buf, squeal(1.2), 444.0, db(-19))
    place(buf, steel_crash(), 445.6, db(-20))
    place(buf, rumble(4.0, True), 451.2, db(-15))
    place(buf, boom(1.4, 70, 30), w("lúd", 452.6), db(-17))
    place(buf, rumble(3.6, True), 460.4, db(-16))
    place(buf, wind(3.0, 0.8), 470.5, db(-21))
    # --- the trap
    place(buf, fire(4.6), 475.2, db(-19))
    place(buf, shovel(), 480.0, db(-20))
    place(buf, shovel(), 481.0, db(-21))
    place(buf, creak(1.0), 483.3, db(-21))
    place(buf, drip_sfx(3.0, 6, 9), 485.7, db(-20))
    place(buf, snap(), w("vigas", 490.6), db(-17))
    place(buf, clank(0.5, 600), w("rieles", 491.9), db(-18))
    place(buf, creak(1.0), w("tramos", 493.4), db(-18))
    place(buf, coins(), 495.4, db(-18))
    place(buf, paper(0.6), 501.9, db(-20))
    place(buf, ticks(2.4, 2.0), 505.2, db(-26))
    place(buf, typewriter(2.0), 518.5, db(-22))
    place(buf, ticks(4.0, 1.0), 524.8, db(-24))
    place(buf, heartbeat(3.2, 52), 531.8, db(-17))
    place(buf, hit(0.4), w("quebró", 541.2), db(-14))
    place(buf, chuff(5.0, 2.0) * 0.6, 549.9, db(-23))
    place(buf, wind(5.0, 0.6), 555.6, db(-22))
    # --- the state pays for the tunnel
    place(buf, crowd(5.0) * 0.6, 594.8, db(-22))
    place(buf, typewriter(3.0), 594.9, db(-22))
    place(buf, crowd(3.0) * 0.7, 603.0, db(-21))
    place(buf, jackhammer(4.4, 12), 613.1, db(-20))
    place(buf, jackhammer(4.0, 10) * 0.7, 623.3, db(-22))
    place(buf, rumble(3.0, False), 629.2, db(-20))
    place(buf, ticks(3.0, 2.0), 633.0, db(-24))
    place(buf, jackhammer(6.0, 13) * 0.6, 636.5, db(-24))
    place(buf, boom(1.6, 90, 34), 643.5, db(-14))
    place(buf, boom(1.8, 80, 30), 646.0, db(-15))
    place(buf, beep(0.2, 900), 659.0, db(-22))
    place(buf, boom(1.4, 70, 28), 660.6, db(-18))
    place(buf, chuff(5.0, 1.8), 668.4, db(-20))
    place(buf, steam_whistle(1.8), 669.0, db(-20))
    place(buf, typewriter(2.0), 694.6, db(-23))
    place(buf, heartbeat(4.0, 54), 705.0, db(-18))
    place(buf, wind(5.0, 0.4), 717.8, db(-23))
    # --- the end of the Hill; the Zephyr, the ski train
    place(buf, chuff(4.0, 2.2) * 0.6, 739.8, db(-22))
    place(buf, wind(4.0, 0.6), 748.5, db(-22))
    place(buf, clank(0.5, 450), 753.6, db(-19))
    place(buf, clank(0.5, 380), 754.9, db(-20))
    place(buf, diesel(5.0), 763.9, db(-21))
    place(buf, diesel(4.0), 789.1, db(-19))
    place(buf, horn(1.4), 790.0, db(-22))
    place(buf, diesel(4.0), 793.3, db(-21))
    place(buf, rumble(6.0, False), 810.3, db(-21))
    place(buf, rumble(4.0, False) * 0.7, 817.2, db(-23))
    place(buf, diesel(4.0) * 0.7, 823.9, db(-22))
    place(buf, rumble(3.0, False), w("negro", 837.3), db(-18))
    place(buf, wind(4.0, 0.9), 842.4, db(-19))
    # --- water across the Divide
    for t0, d in ((859.4, 4.6), (864.0, 5.0)):
        place(buf, river(d), t0, db(-19))
    place(buf, river(10.5), 876.1, db(-21))
    place(buf, drip_sfx(4.0, 8, 5), 895.7, db(-18))
    place(buf, splash(1.0), 900.4, db(-21))
    place(buf, drip_sfx(2.0, 4, 6), 917.2, db(-17))
    place(buf, river(4.0), 933.9, db(-20))
    place(buf, coins(), 940.6, db(-19))
    place(buf, paper(0.6), 950.1, db(-19))
    place(buf, diesel(4.0) * 0.6, 957.6, db(-23))
    place(buf, cart(3.0) * 0.6, 966.0, db(-23))
    # --- the Hill today
    place(buf, wind(5.0, 0.5), 975.1, db(-22))
    place(buf, car_pass(4.0), 982.2, db(-19))
    place(buf, wind(6.0, 0.6), 986.7, db(-22))
    place(buf, car_pass(4.0) * 0.7, 989.6, db(-21))
    place(buf, clank(0.4, 520), 1003.2, db(-20))
    place(buf, rumble(3.0, True), 1006.3, db(-15))
    place(buf, boom(1.2, 80, 30), 1007.6, db(-17))
    place(buf, rumble(2.4, True), 1022.3, db(-17))
    place(buf, car_pass(4.0) * 0.6, 1027.4, db(-21))
    place(buf, wind(6.0, 0.9), 1034.5, db(-20))
    for k in range(8):
        place(buf, footstep(), 1043.9 + 0.55 * k, db(-20))
    place(buf, wind(8.0, 0.8), 1047.7, db(-20))
    place(buf, wind(15.0, 0.6), 1056.8, db(-22))
    place(buf, clank(0.5, 520), 1106.7, db(-20))
    place(buf, coins(), 1117.5, db(-21))
    place(buf, coins(), 1139.4, db(-19))
    place(buf, wind(4.0, 0.8), 1141.3, db(-20))
    place(buf, wind(6.0, 0.5), 1151.7, db(-22))
    place(buf, wind(9.0, 0.9), 1156.1, db(-21))
    return buf


def diesel(d=4.0, f0=34.0):
    """Idling diesel / outboard motor: low pulsing harmonics plus rough noise, low-passed."""
    n = int(d * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.03 * np.sin(2 * np.pi * 0.4 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    m = sum(np.sin(h * ph) / h for h in range(1, 9))
    m *= 0.7 + 0.3 * np.sign(np.sin(ph / 2))
    m += bp(rng.normal(0, 1, n), 80, 700) * 0.5
    m = lp(m, 650, 2)
    m = m / (np.abs(m).max() + 1e-9)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.9)
    return stereo(m * env * 0.55, rng.uniform(-0.2, 0.2))


def rain(d=6.0, density=220):
    """Rain: soft high hiss plus many tiny random drop clicks."""
    n = int(d * SR)
    t = np.arange(n) / SR
    hiss = bp(rng.normal(0, 1, n), 1500, 7000) * 0.35
    drops = np.zeros(n)
    for k in rng.integers(0, n - 400, int(d * density)):
        m = 300
        tt = np.arange(m) / SR
        drops[k:k + m] += np.sin(2 * np.pi * rng.uniform(2000, 5000) * tt) * np.exp(-tt * 900) * rng.uniform(0.2, 1.0)
    x = hiss + bp(drops, 1500, 8000)
    x = x / (np.abs(x).max() + 1e-9)
    env = np.minimum(1, t / 0.8) * np.minimum(1, (d - t) / 1.0)
    l = x * env
    r = np.roll(x, int(0.011 * SR)) * env
    return np.stack([l, r], 1).astype(np.float32) * 0.5


def hooves(d=3.0, rate=3.6):
    out = np.zeros((int(d * SR), 2), np.float32)
    for k in np.arange(0, d - 0.1, 1 / rate):
        for dt in (0.0, 0.11):
            n = int(0.05 * SR)
            tt = np.arange(n) / SR
            c = (bp(rng.normal(0, 1, n), 600, 2600) * 0.8 + np.sin(2 * np.pi * 320 * tt)) * np.exp(-tt * 80)
            place(out, stereo(c / (np.abs(c).max() + 1e-9) * 0.4, rng.uniform(-0.3, 0.3)), k + dt + rng.uniform(0, 0.02))
    return fade(out, 0.3, 0.5)


def chuff(d=4.0, rate=2.0):
    """Steam locomotive exhaust beats plus a low rumble."""
    out = np.zeros((int(d * SR), 2), np.float32)
    for k in np.arange(0, d - 0.2, 1 / rate):
        n = int(0.32 * SR)
        tt = np.arange(n) / SR
        c = bp(rng.normal(0, 1, n), 250, 2200) * np.exp(-tt * 11)
        place(out, stereo(c / (np.abs(c).max() + 1e-9) * 0.5), k)
    out += rumble(d, False) * 0.35
    return fade(out, 0.5, 0.8)


def whistle(d=1.8):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) for f in (466, 554, 698)) + bp(rng.normal(0, 1, n), 400, 1600) * 0.5
    env = np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.6)
    out = s * env
    for dl, g in ((0.09, 0.4), (0.21, 0.25)):
        k = int(dl * SR)
        out[k:] += (s * env)[:-k] * g
    return stereo(lp(out, 2500) / np.abs(out).max() * 0.35)


def siren(d=4.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 700 + 400 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.6 * t))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 1.0)
    return stereo(lp(s, 3000) * env * 0.3, -0.3)


def scrape(d=1.4):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = bp(rng.normal(0, 1, n), 300, 4000) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))
    s += np.sin(2 * np.pi * (180 + 60 * t) * t) * 0.3
    env = np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.3)
    return stereo(s / np.abs(s).max() * env * 0.5)


def scrape_soft(d=5.0):
    out = np.zeros((int(d * SR), 2), np.float32)
    for k in np.arange(0, d - 0.6, 0.9):
        place(out, scrape(0.5) * 0.6, k + rng.uniform(0, 0.15))
    return out


def flood_bed(d=4.0):
    """Rushing muddy water: low-passed noise with a slow surge."""
    n = int(d * SR)
    x = lp(rng.normal(0, 1, n), 900, 2) + 0.4 * bp(rng.normal(0, 1, n), 200, 2200)
    t = np.arange(n) / SR
    env = 0.7 + 0.3 * np.sin(2 * np.pi * 0.35 * t + rng.uniform(0, 6))
    y = x * env
    fade(y.reshape(-1, 1), 0.4, 0.6)
    y = y / (np.abs(y).max() + 1e-6) * 0.5
    return stereo(y.astype(np.float32), 0.0)


def surf(d=4.0, seed=0):
    """A wave arriving and pulling back over sand."""
    r = np.random.default_rng(seed)
    n = int(d * SR)
    x = bp(r.normal(0, 1, n), 300, 7000)
    t = np.arange(n) / SR
    env = np.clip(np.sin(np.pi * t / d), 0, 1) ** 1.5 * (0.6 + 0.4 * np.sin(2 * np.pi * t / max(d, 1.0)))
    y = (x * env).astype(np.float32)
    y = y / (np.abs(y).max() + 1e-6) * 0.5
    return stereo(y, 0.0)


def shovel():
    """A spade biting into wet sand."""
    n = int(0.35 * SR)
    x = bp(rng.normal(0, 1, n), 500, 4000)
    env = np.exp(-np.arange(n) / (0.07 * SR))
    y = (x * env).astype(np.float32)
    y = y / (np.abs(y).max() + 1e-6) * 0.6
    return stereo(y, rng.uniform(-0.3, 0.3))


def probe():
    """An iron rod pushed into the bed: a short scrape and a dull tick."""
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    x = bp(rng.normal(0, 1, n), 1200, 6000) * np.exp(-t / 0.05) * 0.5 + np.sin(2 * np.pi * 1250 * t) * np.exp(-t / 0.03) * 0.4
    return stereo(x.astype(np.float32), rng.uniform(-0.4, 0.4))


def paper(d=0.6):
    n = int(d * SR)
    x = hp(rng.normal(0, 1, n), 2500) * (rng.uniform(0, 1, n) > 0.7)
    env = np.sin(np.pi * np.arange(n) / n)
    y = (x * env * 0.35).astype(np.float32)
    return stereo(y, 0.1)


def typewriter(d=2.0, rate=9.0):
    out = np.zeros((int(d * SR), 2), np.float32)
    t = 0.0
    while t < d - 0.1:
        c = clank(0.06, rng.uniform(2400, 3200))
        place(out, c, t, 0.7)
        t += rng.uniform(0.6, 1.4) / rate
    return out


def fire(d=3.0):
    n = int(d * SR)
    x = lp(rng.normal(0, 1, n), 600) * 0.4
    cr = (rng.uniform(0, 1, n) > 0.9993) * rng.normal(0, 1, n) * 3
    y = (x + hp(cr, 1500)).astype(np.float32)
    y = y / (np.abs(y).max() + 1e-6) * 0.4
    return stereo(y, 0.0)


def splash(d=1.5):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = bp(rng.normal(0, 1, n), 200, 5000) * np.exp(-t / 0.35)
    y = (x / (np.abs(x).max() + 1e-6) * 0.7).astype(np.float32)
    return stereo(y, 0.0)


def tornado_bed(d=6.0):
    """Roaring wind: band-limited noise with a slow swirl and gusts."""
    n = int(d * SR)
    t = np.arange(n) / SR
    x = lp(rng.normal(0, 1, n), 700, 2) * 0.8 + bp(rng.normal(0, 1, n), 300, 3000) * 0.35
    env = 0.6 + 0.25 * np.sin(2 * np.pi * 0.7 * t) + 0.15 * np.sin(2 * np.pi * 2.3 * t + 1.0)
    y = x * env
    k = min(n // 3, int(0.8 * SR))
    y[:k] *= np.linspace(0, 1, k)
    y[n - k:] *= np.linspace(1, 0, k)
    y = (y / (np.abs(y).max() + 1e-6) * 0.6).astype(np.float32)
    l = y
    r = np.roll(y, int(0.011 * SR))
    return np.stack([l, r], 1)


def steel_crash():
    """Heavy steel hitting the ground: low thump + metallic ring + debris noise."""
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (60 - 25 * t) * t) * np.exp(-t / 0.25)
    ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.4) * a for f, a in ((310, 0.3), (517, 0.2), (733, 0.15), (1190, 0.1)))
    noise = bp(rng.normal(0, 1, n), 400, 5000) * np.exp(-t / 0.18) * 0.5
    y = (thump + ring + noise).astype(np.float32)
    y = y / (np.abs(y).max() + 1e-6) * 0.8
    return stereo(y, rng.uniform(-0.4, 0.4))


def rivet(f0=1700.0):
    """A rivet hammer blow: short bright metallic tick."""
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * f0 * t) * 0.6 + bp(rng.normal(0, 1, n), 2000, 9000) * 0.4) * np.exp(-t / 0.018)
    return stereo(y.astype(np.float32) * 0.7, rng.uniform(-0.5, 0.5))


def musket():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    y = bp(rng.normal(0, 1, n), 200, 6000) * np.exp(-t / 0.08) + lp(rng.normal(0, 1, n), 300) * np.exp(-t / 0.5) * 0.6
    y = (y / (np.abs(y).max() + 1e-6) * 0.7).astype(np.float32)
    return stereo(y, rng.uniform(-0.6, 0.6))


def crowd(d=4.0):
    n = int(d * SR)
    x = bp(rng.normal(0, 1, n), 250, 2500)
    t = np.arange(n) / SR
    env = 0.7 + 0.3 * np.sin(2 * np.pi * 0.4 * t) * np.sin(2 * np.pi * 1.7 * t)
    y = x * env
    k = min(n // 3, int(0.6 * SR))
    y[:k] *= np.linspace(0, 1, k)
    y[n - k:] *= np.linspace(1, 0, k)
    return stereo((y / (np.abs(y).max() + 1e-6) * 0.4).astype(np.float32), 0.0)


def torch_cut(d=3.0):
    n = int(d * SR)
    x = hp(rng.normal(0, 1, n), 1500) * 0.3 + (rng.uniform(0, 1, n) > 0.9985) * rng.normal(0, 1, n) * 2
    k = min(n // 4, int(0.3 * SR))
    x[:k] *= np.linspace(0, 1, k)
    x[n - k:] *= np.linspace(1, 0, k)
    return stereo((x / (np.abs(x).max() + 1e-6) * 0.4).astype(np.float32), 0.2)


def snap():
    """A bolt snapping: sharp crack + short ring."""
    n = int(0.8 * SR)
    t = np.arange(n) / SR
    y = hp(rng.normal(0, 1, n), 1200) * np.exp(-t / 0.01) * 1.2 + np.sin(2 * np.pi * 2300 * t) * np.exp(-t / 0.15) * 0.4 + \
        np.sin(2 * np.pi * 120 * t) * np.exp(-t / 0.08) * 0.5
    return stereo((y / (np.abs(y).max() + 1e-6) * 0.8).astype(np.float32), 0.0)


def creak(d=1.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 90 + 40 * np.sin(2 * np.pi * 0.8 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sign(np.sin(ph)) * 0.3 * np.sin(np.pi * t / d) + bp(rng.normal(0, 1, n), 200, 1200) * 0.1
    return stereo(lp(y, 1500).astype(np.float32), rng.uniform(-0.3, 0.3))


def door_slam():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 90 * t) * np.exp(-t / 0.06) + bp(rng.normal(0, 1, n), 300, 3000) * np.exp(-t / 0.03) * 0.5
    return stereo((y / (np.abs(y).max() + 1e-6) * 0.7).astype(np.float32), 0.3)


def car_pass(d=4.0):
    """A car passing by on a quiet road: filtered noise with a Doppler-ish swell."""
    n = int(d * SR)
    t = np.arange(n) / SR
    x = lp(rng.normal(0, 1, n), 1200) * 0.7 + bp(rng.normal(0, 1, n), 150, 600) * 0.4
    env = np.exp(-((t - d / 2) / (d / 4.5)) ** 2)
    y = (x * env).astype(np.float32)
    y = y / (np.abs(y).max() + 1e-6) * 0.6
    pan = np.clip((t - d / 2) / (d / 2), -1, 1)
    l = y * np.cos((pan + 1) * np.pi / 4) * 1.41
    r = y * np.sin((pan + 1) * np.pi / 4) * 1.41
    return np.stack([l, r], 1).astype(np.float32)


def truck_pass(d=4.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = lp(rng.normal(0, 1, n), 500) * 0.8 + np.sin(2 * np.pi * 48 * t) * 0.3
    env = np.exp(-((t - d / 2) / (d / 4.0)) ** 2)
    y = (x * env).astype(np.float32)
    return stereo(y / (np.abs(y).max() + 1e-6) * 0.7, 0.0)


def motorbike(d=3.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 70 + 20 * np.sin(2 * np.pi * 0.3 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.3 + lp(rng.normal(0, 1, n), 900) * 0.3
    env = np.exp(-((t - d / 2) / (d / 3.5)) ** 2)
    return stereo(lp(x * env, 2500).astype(np.float32), 0.0)


def footstep():
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    x = lp(rng.normal(0, 1, n), 700) * np.exp(-t / 0.04) + bp(rng.normal(0, 1, n), 800, 3000) * np.exp(-t / 0.02) * 0.4
    return stereo((x / (np.abs(x).max() + 1e-6) * 0.5).astype(np.float32), rng.uniform(-0.3, 0.3))


def axe():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.06) + bp(rng.normal(0, 1, n), 600, 4000) * np.exp(-t / 0.03) * 0.6
    return stereo((x / (np.abs(x).max() + 1e-6) * 0.7).astype(np.float32), rng.uniform(-0.4, 0.4))


def river(d=5.0):
    n = int(d * SR)
    x = bp(rng.normal(0, 1, n), 200, 3000) * 0.5 + lp(rng.normal(0, 1, n), 300) * 0.4
    t = np.arange(n) / SR
    env = 0.8 + 0.2 * np.sin(2 * np.pi * 0.25 * t)
    y = x * env
    k = min(n // 3, int(0.7 * SR))
    y[:k] *= np.linspace(0, 1, k)
    y[n - k:] *= np.linspace(1, 0, k)
    return stereo((y / (np.abs(y).max() + 1e-6) * 0.45).astype(np.float32), 0.0)


def paddle(d=6.0, rate=1.6):
    out = np.zeros((int(d * SR), 2), np.float32)
    t = 0.0
    while t < d - 0.5:
        n = int(0.4 * SR)
        tt = np.arange(n) / SR
        x = bp(rng.normal(0, 1, n), 200, 2500) * np.exp(-tt / 0.12)
        place(out, stereo((x * 0.5).astype(np.float32), 0.0), t, 1.0)
        t += 1.0 / rate
    out += river(d) * 0.6
    return out


def steam_whistle(d=1.8):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((392, 0.5), (494, 0.35), (587, 0.25)))
    x += bp(rng.normal(0, 1, n), 1500, 6000) * 0.15
    env = np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.4)
    return stereo((x * env * 0.5).astype(np.float32), 0.2)


def drum_march(d=5.0, bpm=104):
    out = np.zeros((int(d * SR), 2), np.float32)
    beat = 60.0 / bpm
    t = 0.0
    k = 0
    while t < d - 0.3:
        n = int(0.15 * SR)
        tt = np.arange(n) / SR
        x = bp(rng.normal(0, 1, n), 150, 5000) * np.exp(-tt / 0.03) * (1.0 if k % 2 == 0 else 0.6)
        place(out, stereo(x.astype(np.float32) * 0.6, 0.0), t, 1.0)
        t += beat / (2 if k % 4 == 3 else 1)
        k += 1
    return out


def chains(d=4.0):
    out = np.zeros((int(d * SR), 2), np.float32)
    t = 0.0
    while t < d - 0.3:
        for j in range(3):
            place(out, clank(0.12, rng.uniform(2200, 3400)), t + j * 0.05, 0.4)
        t += rng.uniform(0.5, 0.9)
    return out


def coins():
    out = np.zeros((int(1.5 * SR), 2), np.float32)
    for j in range(9):
        place(out, clank(0.15, rng.uniform(3000, 4800)), j * 0.09 + rng.uniform(0, 0.04), 0.5)
    return out


def cart(d=4.0):
    out = np.zeros((int(d * SR), 2), np.float32)
    out += creak(d) * 0.6
    out += hooves(d, 2.0) * 0.4
    return out


def crane(d=4.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * (120 + 15 * np.sin(2 * np.pi * 0.5 * t)) * t) * 0.2 + lp(rng.normal(0, 1, n), 400) * 0.3
    return stereo(x.astype(np.float32), 0.0)


def beep(d=0.12, f=1800):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 18)
    return stereo(s * 0.3)


def main():
    out = sys.argv[1]
    voice = load(os.path.join(ROOT, "work", "voz.mp3"))
    v = np.zeros((N, 2), np.float32)
    v[: len(voice)] = voice[:N]
    music = build_music()
    music = duck(music, v)
    sfx = build_sfx()
    mix = v * db(0) + music * db(0.5) + sfx * db(-11)
    mix = mix[: int(TOTAL * SR)]
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    raw = (mix.astype("<f4")).tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s16le", out], input=raw, check=True)
    # stems for later adjustment
    for name, x in (("music", music), ("sfx", sfx)):
        x = x[: int(TOTAL * SR)] * (db(0.5) if name == "music" else db(-11))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        "-c:a", "pcm_s16le", out.replace(".wav", f"_{name}.wav")], input=x.astype("<f4").tobytes(), check=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
