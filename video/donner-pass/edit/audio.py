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
TOTAL = 1130.06
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
MUSIC = [  # (start, end, file, offset_in_track, gain_db) -- gains bring every track to about -27.5 LUFS
    (0.0, 68.5, "Long Note Three", 0.0, -3.1),
    (66.8, 185.5, "Immersed", 0.0, -5.4),
    (183.8, 303.5, "Stay the Course", 0.0, -6.2),
    (302.3, 462.5, "Controlled Chaos", 0.0, -15.4),
    (461.2, 664.0, "Ice Demon", 0.0, -11.3),
    (662.6, 785.0, "Rising Tide", 0.0, -8.0),
    (783.7, 956.0, "Unanswered Questions", 0.0, -12.0),
    (954.4, 1059.0, "Simplex", 0.0, -13.6),
    (1057.8, TOTAL, "Night Vigil", 0.0, -11.0),
]


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
        path = os.path.join(ROOT, "assets", "music", name + ".mp3")
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
    for t0, d, g in ((0.0, 12.0, -14), (12.4, 4.0, -15), (824.0, 8.0, -14), (838.5, 17.0, -13), (944.7, 5.0, -15), (1039.3, 8.0, -15), (1099.5, 6.0, -15)):
        place(buf, drip_sfx(d, int(d * 2.5), int(t0)), t0, db(g))
    for t0, d, g in ((72.1, 12.0, -12), (95.0, 9.0, -11), (253.5, 4.0, -14), (264.7, 4.6, -14), (457.5, 7.0, -12), (464.4, 11.0, -12),
                     (475.4, 14.0, -14), (496.8, 8.0, -15), (509.7, 5.3, -14), (517.9, 15.0, -11), (529.4, 11.0, -15), (657.6, 5.0, -12),
                     (742.1, 4.7, -10), (765.1, 8.0, -15), (1079.0, 2.4, -11)):
        place(buf, wind(d), t0, db(g))
    for t in (37.3, 38.1, 38.9, 255.6, 256.4, 515.1, 515.9, 1035.9, 1036.7):
        place(buf, clank(), t, db(-15))
    for k in range(17):  # golpe, giro, golpe
        place(buf, clank(0.4, 760 + 40 * (k % 3)), 305.82 + 1.0 + k * 0.625 / 0.35 * 0.35 * 1.0 + 0.0, db(-16))
    for t, g in ((w("explosion", 323.3) - 0.2, -8), (w("claro", 410.4) + 0.3, -9), (w("explosion", 419.4) - 0.1, -10)):
        place(buf, boom(1.8, 90, 36), t, db(g))
        place(buf, rumble(2.4), t + 0.1, db(-10))
    place(buf, rumble(4.0), 518.0, db(-9))
    place(buf, boom(2.0, 70, 30), 523.4, db(-9))
    place(buf, rumble(5.0), 523.4, db(-8))
    for t0, d, g in ((16.7, 7.5, -17), (660.4, 2.7, -16), (712.4, 6.6, -17), (1019.9, 5.3, -17), (1062.7, 4.3, -18)):
        place(buf, engine(d), t0, db(g))
    for t0, d, g in ((1025.2, 6.3, -13), (1031.6, 4.1, -14)):
        place(buf, traffic_bed(d), t0, db(g))
    place(buf, heartbeat(2.0), 883.74, db(-12))
    return buf


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
