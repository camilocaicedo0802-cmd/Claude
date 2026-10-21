"""Synthesized high-energy salsa bed (190 BPM, 2-3 son clave) for the Pinktober promo.
Writes music.wav (stems mixed) plus whoosh/boom/riser/sparkle SFX."""
import numpy as np, wave, sys

SR = 44100
BPM = 190
BEAT = 60 / BPM
E8 = BEAT / 2
rng = np.random.default_rng(11)

def write(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

def add(out, s, t, pan=0.0):
    i = int(round(t * SR))
    if i >= len(out) or i < 0: return
    m = min(len(s), len(out) - i)
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    out[i:i+m, 0] += s[:m] * l; out[i:i+m, 1] += s[:m] * r

def midi(m): return 440 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR

def onepole_lp(x, fc):
    """Time-varying one-pole low-pass; fc may be scalar or array."""
    fc = np.broadcast_to(fc, x.shape)
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y

def hp(x, fc):
    return x - onepole_lp(x, fc)

# ---------------- instruments ----------------
def piano(m, dur=0.42, vel=1.0):
    f = midi(m); t = tt(dur + 0.25); x = np.zeros_like(t)
    B = 0.00035
    for n in range(1, 14):
        fn = n * f * np.sqrt(1 + B * n * n)
        if fn > SR / 2.2: break
        amp = (1 / n ** 1.1) * (1.0 if n < 4 else 0.8)
        x += amp * np.sin(2 * np.pi * fn * t + rng.uniform(0, 6.28)) * np.exp(-t * (2.2 + 0.9 * n))
    env = np.minimum(1, t / 0.002) * np.where(t < dur, 1.0, np.exp(-(t - dur) * 30))
    ham = rng.normal(0, 1, len(t)) * np.exp(-t * 400) * 0.15
    return (x * env + ham) * 0.22 * vel

def bass(m, dur=0.45, vel=1.0):
    f = midi(m); t = tt(dur + 0.08)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 6) + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 10)
    env = np.minimum(1, t / 0.004) * np.exp(-t * 3.5) * np.where(t < dur, 1, np.exp(-(t - dur) * 60))
    pluck = rng.normal(0, 1, len(t)) * np.exp(-t * 300) * 0.08
    return (x * env + pluck) * 0.5 * vel

def conga(kind, vel=1.0):
    t = tt(0.35)
    if kind == 'open':   f0, dec, nz = 330, 9, 0.05
    elif kind == 'low':  f0, dec, nz = 220, 7, 0.05
    elif kind == 'slap': f0, dec, nz = 420, 30, 0.6
    else:                f0, dec, nz = 300, 45, 0.15   # muted heel/toe
    f = f0 * (1 + 0.25 * np.exp(-t * 60))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * dec) + 0.3 * np.sin(1.59 * ph) * np.exp(-t * dec * 1.6)
    n = hp(rng.normal(0, 1, len(t)), 1500) * np.exp(-t * (120 if kind != 'slap' else 60)) * nz
    return (x + n) * 0.35 * vel

def clave():
    t = tt(0.12)
    return (np.sin(2 * np.pi * 2350 * t) + 0.4 * np.sin(2 * np.pi * 3720 * t)) * np.exp(-t * 55) * 0.16

def campana(accent=False):
    t = tt(0.3); x = np.zeros_like(t)
    for f, a in [(820, 1), (1190, .7), (1680, .5), (2470, .35), (3330, .2)]:
        x += a * np.sin(2 * np.pi * f * t)
    x = np.tanh(x * 1.5) * np.exp(-t * (9 if accent else 14))
    return x * (0.10 if accent else 0.06)

def guiro(long=True):
    d = 0.16 if long else 0.06; t = tt(d)
    n = hp(rng.normal(0, 1, len(t)), 3000)
    ridges = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * (70 if long else 90) * t))
    env = np.sin(np.pi * t / d) ** 0.6
    return n * ridges * env * 0.05

def timbal(f0=520, vel=1.0):
    t = tt(0.4)
    x = np.sin(2 * np.pi * f0 * t) * np.exp(-t * 7) + 0.5 * np.sin(2 * np.pi * f0 * 1.51 * t) * np.exp(-t * 11)
    n = hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 40) * 0.6
    return (x + n) * 0.22 * vel

def brass(notes, dur=0.18, vel=1.0, swell=False):
    """Section stab: detuned saws, filter opening for the brassy 'bwap'."""
    t = tt(dur + 0.25); x = np.zeros_like(t)
    for m in notes:
        for det in (-0.06, 0.0, 0.07):
            f = midi(m + det)
            ph = (f * t + rng.uniform()) % 1.0
            x += 2 * ph - 1
    x /= len(notes) * 3
    att = 0.03 if not swell else 0.25
    fc = 600 + 5200 * np.minimum(1, t / att) * np.exp(-np.maximum(0, t - att) * 3)
    y = onepole_lp(onepole_lp(x, fc), fc * 1.3)
    env = np.minimum(1, t / (0.008 if not swell else 0.2)) * np.where(t < dur, 1, np.exp(-(t - dur) * 18))
    return np.tanh(y * env * 2.2) * 0.32 * vel

def crash(d=2.2, vel=1.0):
    t = tt(d); n = hp(hp(rng.normal(0, 1, len(t)), 4000), 4000)
    return n * np.exp(-t * 2.2) * 0.12 * vel

def boom(d=1.4):
    t = tt(d); f = 45 + 70 * np.exp(-t * 18)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * 0.9

# ---------------- arrangement ----------------
# I - IV - V - IV in G, two chords per bar
PROG = [(55, [67, 71, 74]), (60, [67, 72, 76]), (62, [66, 69, 74]), (60, [67, 72, 76])]  # (bass root, montuno triad)

def build(total=15.0, end_hit_beat=43, button_beat=46):
    out = np.zeros((int((total + 1) * SR), 2))
    nbeats = int(total / BEAT) + 1
    groove_end = button_beat * BEAT
    # montuno rhythm over one bar of eighths (1 = octave melody note, 2 = chord)
    mont = [2, 1, 0, 2, 1, 2, 0, 1]
    for b8 in range(int(groove_end / E8) + 1):
        t = b8 * E8; bar = b8 // 8; pos = b8 % 8
        if t >= groove_end - 1e-6: break
        chord_i = (bar * 2 + (1 if pos >= 4 else 0)) % 4
        root, triad = PROG[chord_i]
        # piano montuno
        k = mont[pos]
        if k == 1:
            top = triad[(b8 // 2) % 3]
            add(out, piano(top, 0.12, 0.9) + piano(top - 12, 0.12, 0.6), t, 0.15)
        elif k == 2:
            add(out, sum(piano(m, 0.1, 0.55) for m in triad), t, 0.15)
        # bass tumbao: anticipations on 2& and 4
        if pos == 3:
            nxt = PROG[(bar * 2 + 1) % 4][0]
            add(out, bass(nxt - 12, 0.5), t, 0)
        if pos == 6:
            nxt = PROG[((bar + 1) * 2) % 4][0]
            add(out, bass(nxt - 12, 0.3), t, 0)
        # congas tumbao
        if pos == 2: add(out, conga('slap'), t, -0.3)
        elif pos in (6,): add(out, conga('open'), t, -0.3)
        elif pos == 7: add(out, conga('low', 1.1), t, -0.35)
        else: add(out, conga('mute', 0.5), t, -0.3)
        # 2-3 son clave over two bars
        c = b8 % 16
        if c in (2, 4, 8, 11, 14): add(out, clave(), t, 0.4)
        # campana on quarters, accents on 1 and 3
        if pos % 2 == 0: add(out, campana(pos in (0, 4)), t, 0.35)
        # guiro: long on beats, short on offbeats
        add(out, guiro(pos % 2 == 0), t, -0.45)
    # brass mambo figure every 2 bars (pickups into bar), energy lift
    for bar in range(0, int(groove_end / (8 * E8)) + 1, 2):
        t0 = bar * 8 * E8
        if t0 + 7 * E8 < end_hit_beat * BEAT - 0.01:
            add(out, brass([74, 79, 83], 0.12, 0.7), t0 + 5 * E8, 0.2)
            add(out, brass([74, 79, 83], 0.14, 0.8), t0 + 7 * E8, 0.2)
    # intro hit
    add(out, brass([67, 71, 74, 79], 0.45, 1.2), 0.0, 0.1); add(out, crash(), 0.0); add(out, timbal(560), 0.0, -0.2)
    # timbal fill into the end hit
    for k, f0 in enumerate([600, 600, 520, 520, 460, 460]):
        add(out, timbal(f0, 0.8), (end_hit_beat - 1.5) * BEAT + k * E8 / 2 - 0.0, -0.2)
    # end hit + button
    add(out, brass([67, 71, 74, 79, 83], 0.35, 1.3), end_hit_beat * BEAT, 0.1)
    add(out, crash(2.5, 1.2), end_hit_beat * BEAT)
    add(out, brass([67, 71, 74, 79, 83], 0.6, 1.4), button_beat * BEAT, 0.1)
    add(out, crash(2.0, 1.1), button_beat * BEAT)
    add(out, timbal(460, 1.0), button_beat * BEAT, -0.2)
    out = out[:int(total * SR)]
    # room: short multi-tap reverb, stereo
    rev = np.zeros_like(out)
    for d, g in [(0.023, .22), (0.041, .18), (0.067, .14), (0.097, .1), (0.131, .07)]:
        n = int(d * SR); rev[n:, 0] += out[:-n, 0] * g; n2 = int(d * 1.17 * SR); rev[n2:, 1] += out[:-n2, 1] * g
    out = out + rev
    out = np.tanh(out * 1.4) / np.tanh(1.4)
    out /= np.max(np.abs(out)) + 1e-9
    fo = int(0.35 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return out * 0.9

def whoosh(d=0.4):
    t = tt(d); x = rng.normal(0, 1, len(t))
    fc = 300 + 6000 * np.sin(np.pi * t / d) ** 2
    y = hp(onepole_lp(x, fc), 200) * np.sin(np.pi * t / d) ** 2
    return y / np.max(np.abs(y)) * 0.5

def riser(d=1.0):
    t = tt(d); x = rng.normal(0, 1, len(t))
    y = hp(onepole_lp(x, 300 + 9000 * (t / d) ** 2), 400) * (t / d) ** 1.5
    return y / np.max(np.abs(y)) * 0.4

def sparkle():
    out = np.zeros(int(1.0 * SR))
    for k, m in enumerate([96, 100, 103, 108]):
        t = tt(0.6); s = np.sin(2 * np.pi * midi(m) * t) * np.exp(-t * 6) * 0.12
        i = int(k * 0.05 * SR); out[i:i+len(s)] += s[:len(out)-i]
    return out

if __name__ == '__main__':
    d = sys.argv[1]
    write(f'{d}/music.wav', build())
    write(f'{d}/whoosh.wav', whoosh())
    write(f'{d}/boom.wav', boom())
    write(f'{d}/riser.wav', riser())
    write(f'{d}/sparkle.wav', sparkle())
    print('beat', BEAT)
