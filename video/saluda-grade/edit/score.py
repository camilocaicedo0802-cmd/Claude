"""Original score, synthesised from scratch (no samples, no third-party music): one cue per chapter.

usage: python score.py OUT_DIR    -> writes cue_1.wav .. cue_9.wav (48 kHz stereo)"""
import os
import sys

import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(int(os.environ.get("SCORE_SEED", "7")))


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, f, order=2):
    b, a = signal.butter(order, min(f, SR / 2 - 100) / (SR / 2), "low")
    return signal.lfilter(b, a, x, axis=0)


def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "high")
    return signal.lfilter(b, a, x, axis=0)


def env_adsr(n, a=0.01, d=0.2, s=0.7, r=0.3):
    t = np.arange(n) / SR
    L = n / SR
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    e *= np.clip((L - t) / max(r, 1e-4), 0, 1)
    return e


def place(buf, x, t):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i]


def st(m, pan=0.0):
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    return np.stack([m * l, m * r], 1) * 1.41


# ------------------------------------------------------------------ instruments
_TABLES = {}


def _saw_table(nh):
    """One band-limited saw cycle with nh harmonics (soft roll-off), cached."""
    if nh not in _TABLES:
        ph = np.arange(2048) / 2048
        _TABLES[nh] = sum(np.sin(2 * np.pi * h * ph) / h * (1 - 0.5 * h / (nh + 1)) for h in range(1, nh + 1))
        _TABLES[nh] /= np.abs(_TABLES[nh]).max()
    return _TABLES[nh]


def _osc(f, n, cutoff):
    nh = int(max(1, min(40, cutoff // f)))
    tab = _saw_table(nh)
    ph = (f * np.arange(n) / SR + rng.random()) % 1.0
    idx = ph * 2048
    i0 = idx.astype(np.int64) % 2048
    fr = idx - np.floor(idx)
    return tab[i0] * (1 - fr) + tab[(i0 + 1) % 2048] * fr


def pad(notes, dur, bright=1400, detune=7, lfo=0.07, amp=0.12):
    """Detuned band-limited saw ensemble with a gentle low-pass and slow swell."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for m in notes:
        for c, pan in ((-detune, -0.6), (0, 0.0), (detune, 0.6)):
            f = hz(m) * 2 ** (c / 1200)
            out += st(_osc(f, n, bright * 1.6), pan) / 3
    out = lp(out, bright, 2)
    out *= (0.85 + 0.15 * np.sin(2 * np.pi * lfo * t + rng.random() * 6))[:, None]
    e = env_adsr(n, min(2.5, dur * 0.3), 1.0, 1.0, min(2.5, dur * 0.3))[:, None]
    return out * e * amp / max(1, len(notes) ** 0.5)


def pluck(m, dur=1.6, amp=0.2, bright=1.0, pan=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    s = np.zeros(n)
    for h in range(1, 14):
        if f0 * h > 12000:
            break
        s += np.sin(2 * np.pi * f0 * h * t + rng.random() * 6) * np.exp(-t * (1.6 + 0.9 * h / bright)) / h ** 1.1
    s *= np.minimum(1, t / 0.003)
    return st(s * amp, pan)


def piano(m, dur=3.0, amp=0.22, pan=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    s = np.zeros(n)
    for h in range(1, 10):
        fh = f0 * h * np.sqrt(1 + 0.0004 * h * h)
        if fh > 14000:
            break
        s += np.sin(2 * np.pi * fh * t) * np.exp(-t * (0.9 + 0.6 * h)) * (0.9 ** h)
    s += hp(rng.normal(0, 1, n), 2000) * np.exp(-t * 120) * 0.05
    s *= np.minimum(1, t / 0.004) * np.clip((dur - t) / 0.4, 0, 1)
    return st(s * amp, pan)


def bell(m, dur=4.0, amp=0.1, pan=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    s = sum(np.sin(2 * np.pi * f0 * r * t) * np.exp(-t * d) * g for r, d, g in ((1, 0.8, 1), (2.76, 1.6, 0.4), (5.4, 3.0, 0.2), (8.93, 5, 0.1)))
    return st(s * np.minimum(1, t / 0.002) * amp, pan)


def bass(m, dur=0.6, amp=0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    s = np.sin(2 * np.pi * f0 * t) + 0.35 * np.sin(4 * np.pi * f0 * t) + 0.12 * np.sin(6 * np.pi * f0 * t)
    s *= np.exp(-t * 3.5) * np.minimum(1, t / 0.01)
    return st(s * amp)


def drone(m, dur, amp=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.003 * t) + 0.25 * np.sin(2 * np.pi * f * 3.01 * t)
    s *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.05 * t)
    e = env_adsr(n, 4.0, 1, 1, 4.0)
    return st(s * e * amp)


def kick(amp=0.5):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return st(s * amp)


def timp(m=38, amp=0.45):
    n = int(1.8 * SR)
    t = np.arange(n) / SR
    f = hz(m) * (1 + 0.15 * np.exp(-t * 12))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4) + lp(rng.normal(0, 1, n), 300) * np.exp(-t * 25) * 0.4
    return st(s * amp)


def hat(amp=0.05, d=0.06, pan=0.3):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = hp(rng.normal(0, 1, n), 6000) * np.exp(-t * 60)
    return st(s * amp, pan)


def brush(amp=0.04, d=0.25):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = signal.lfilter(*signal.butter(2, [2500 / (SR / 2), 9000 / (SR / 2)], "band"), rng.normal(0, 1, n)) * np.sin(np.pi * t / d)
    return st(s * amp, rng.uniform(-0.3, 0.3))


def tremolo(notes, dur, rate=7.0, amp=0.08):
    p = pad(notes, dur, bright=2200, amp=amp)
    t = np.arange(len(p)) / SR
    return p * (0.6 + 0.4 * np.sin(2 * np.pi * rate * t))[:, None]


def reverb(x, rt=2.4, mix=0.3):
    n = int(rt * SR)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-t * 6.9 / rt)[:, None]
    ir = lp(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum(0))
    wet = np.stack([signal.oaconvolve(x[:, c], ir[:, c])[: len(x)] for c in (0, 1)], 1)
    return x * (1 - mix) + wet * mix * 1.4


# ------------------------------------------------------------------ cues
def chords_over(dur, prog, bar):
    """Yield (t, chord) every bar, cycling through prog."""
    out, t, i = [], 0.0, 0
    while t < dur:
        out.append((t, prog[i % len(prog)]))
        t += bar
        i += 1
    return out


def lay_pad(buf, dur, prog, bar, **kw):
    for t, ch in chords_over(dur, prog, bar):
        place(buf, pad(ch, bar + 2.0, **kw), t)


def cue_dark(dur):  # intro: drone, low pulse, sparse metallic tones
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    place(buf, drone(33, dur + 3, 0.16), 0)
    lay_pad(buf, dur, [[45, 52, 55], [44, 51, 55], [41, 48, 52], [43, 50, 53]], 8.0, bright=700, amp=0.10)
    for t in np.arange(4, dur - 2, 4.0):
        place(buf, kick(0.35), t)
        place(buf, kick(0.2), t + 0.42)
    for t in np.arange(6, dur - 3, 7.0):
        place(buf, bell(rng.choice([69, 72, 76, 75]), 5, 0.05, rng.uniform(-0.7, 0.7)), t + rng.uniform(0, 1.5))
    return buf


def cue_street(dur):  # 1840s street: light plucked folk arpeggios, major key
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    prog = [[50, 57, 62, 66], [55, 62, 67, 71], [57, 64, 69, 73], [50, 57, 62, 66], [47, 54, 59, 62], [55, 62, 67, 71], [57, 64, 69, 73], [57, 61, 64, 69]]
    beat = 60 / 104
    bar = beat * 4
    lay_pad(buf, dur, [p[:3] for p in prog], bar * 2, bright=900, amp=0.05)
    for t, ch in chords_over(dur, prog, bar):
        place(buf, bass(ch[0] - 12, beat * 1.5, 0.22), t)
        place(buf, bass(ch[1] - 12, beat * 1.5, 0.16), t + beat * 2)
        patt = [ch[1], ch[2], ch[3], ch[2], ch[1] + 12, ch[3], ch[2], ch[3]]
        for k, m in enumerate(patt):
            place(buf, pluck(m, 1.2, 0.09, 1.3, 0.25 if k % 2 else -0.25), t + k * beat / 2)
    return buf


def cue_drama(dur):  # journey and the street war: minor ostinato, timpani
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    prog = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [40, 47, 52, 56]]
    beat = 60 / 92
    bar = beat * 4
    lay_pad(buf, dur, prog, bar, bright=1300, amp=0.09)
    for t, ch in chords_over(dur, prog, bar):
        place(buf, timp(ch[0] - 12, 0.32), t)
        for k in range(8):
            m = ch[(k % 3) + 1] + (12 if k == 6 else 0)
            place(buf, pluck(m, 0.5, 0.06, 0.8, -0.2 if k % 2 else 0.2), t + k * beat / 2)
    return buf


def cue_noir(dur):  # rumours: walking bass, brushes, minor 7th chords
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    prog = [[50, 53, 57, 60], [55, 58, 62, 65], [48, 51, 55, 58], [52, 55, 58, 62]]
    walk = [[38, 41, 43, 45], [43, 46, 48, 49], [36, 39, 41, 42], [40, 43, 45, 44]]
    beat = 60 / 84
    bar = beat * 4
    for i, (t, ch) in enumerate(chords_over(dur, prog, bar)):
        for k, m in enumerate(walk[i % 4]):
            place(buf, bass(m, beat * 1.1, 0.26), t + k * beat)
            place(buf, brush(0.035), t + k * beat)
            place(buf, hat(0.03, 0.05), t + k * beat + beat * 0.66)
        if i % 2 == 0:
            for j, m in enumerate(ch):
                place(buf, piano(m + 12, 2.6, 0.06, -0.3 + 0.2 * j), t + beat * 1.5 + j * 0.03)
    lay_pad(buf, dur, [c[:3] for c in prog], bar, bright=600, amp=0.04)
    return buf


def cue_quest(dur):  # the search: pulsing arpeggio, rising, Lydian colour
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    prog = [[48, 55, 62, 66], [50, 57, 62, 69], [45, 52, 59, 64], [53, 60, 64, 67]]
    beat = 60 / 112
    bar = beat * 4
    lay_pad(buf, dur, prog, bar * 2, bright=1600, amp=0.07)
    for i, (t, ch) in enumerate(chords_over(dur, prog, bar)):
        place(buf, kick(0.22), t)
        place(buf, kick(0.16), t + beat * 2)
        for k in range(16):
            m = ch[k % 4] + 12 * ((k // 4) % 2)
            place(buf, pluck(m, 0.35, 0.05, 1.6, 0.4 if k % 2 else -0.4), t + k * beat / 4)
    return buf


def cue_tension(dur):  # the descent: heartbeat pulse, tremolo strings, rising
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    place(buf, drone(31, dur + 3, 0.14), 0)
    prog = [[43, 50, 55], [44, 51, 56], [43, 50, 55], [42, 49, 54]]
    for t, ch in chords_over(dur, prog, 6.0):
        place(buf, tremolo([m + 12 for m in ch], 8.0, 6.5, 0.07), t)
    for t in np.arange(1.0, dur - 1, 60 / 66):
        place(buf, kick(0.3), t)
        place(buf, kick(0.18), t + 0.2)
    return buf


def cue_sad(dur):  # second closure: slow minor chords, piano melody
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    prog = [[45, 52, 57, 60], [41, 48, 53, 57], [48, 55, 60, 64], [43, 50, 55, 59]]
    mel = [76, 74, 72, 71, 72, 69, 67, 69]
    bar = 5.0
    lay_pad(buf, dur, prog, bar, bright=1000, amp=0.08)
    for i, (t, ch) in enumerate(chords_over(dur, prog, bar)):
        place(buf, bass(ch[0] - 12, 3.0, 0.2), t)
        for j, m in enumerate(ch[1:]):
            place(buf, piano(m + 12, 3.5, 0.05, -0.3 + 0.3 * j), t + 0.2 * j)
        place(buf, piano(mel[i % len(mel)], 4.0, 0.07, 0.1), t + 2.5)
    return buf


def cue_calm(dur):  # today: airy pad, sparse bells
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    prog = [[48, 55, 60, 64, 67], [53, 60, 65, 69], [45, 52, 57, 60, 64], [50, 57, 62, 65]]
    lay_pad(buf, dur, prog, 7.0, bright=1800, amp=0.08)
    for t in np.arange(2, dur - 3, 3.5):
        place(buf, bell(rng.choice([72, 76, 79, 84, 81]), 4.5, 0.045, rng.uniform(-0.6, 0.6)), t + rng.uniform(0, 1))
    return buf


def cue_end(dur):  # conclusion: piano arpeggios, minor turning to major, swell
    buf = np.zeros((int(dur * SR) + SR * 4, 2))
    prog = [[45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [48, 55, 60, 64, 67], [43, 50, 55, 59, 62],
            [41, 48, 53, 57, 60], [48, 55, 60, 64, 67], [43, 50, 55, 59, 62], [48, 55, 60, 64, 67]]
    beat = 60 / 76
    bar = beat * 4
    lay_pad(buf, dur, [p[:4] for p in prog], bar, bright=1300, amp=0.07)
    for t, ch in chords_over(dur, prog, bar):
        place(buf, bass(ch[0] - 12, bar, 0.2), t)
        for k in range(8):
            place(buf, piano(ch[1 + k % 4] + 12, 2.2, 0.05, -0.3 + 0.15 * (k % 4)), t + k * beat / 2)
    return buf


CUES = [cue_dark, cue_street, cue_drama, cue_noir, cue_quest, cue_tension, cue_sad, cue_calm, cue_end]


def main():
    out_dir = sys.argv[1]
    lens = [float(x) for x in sys.argv[2:]] or [70, 145, 200, 103, 141, 143, 207, 78, 92]
    os.makedirs(out_dir, exist_ok=True)
    import subprocess
    for i, (fn, L) in enumerate(zip(CUES, lens)):
        x = fn(L + 4.0)
        x = reverb(x, 2.6 if i not in (1, 4) else 1.6, 0.32)
        x = hp(x, 30)
        x = x[: int((L + 4.0) * SR)]
        x /= np.abs(x).max() + 1e-9
        x *= 0.7
        path = os.path.join(out_dir, f"cue_{i + 1}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", path],
                       input=x.astype("<f4").tobytes(), check=True)
        print(path, round(L + 4.0, 1))


if __name__ == "__main__":
    main()
