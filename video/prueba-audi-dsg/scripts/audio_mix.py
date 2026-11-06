"""Builds the soundtrack: voice (from the Lienzo, cut per the EDL), an original
synthesized phonk/trap beat (copyright-free by construction) and synthesized SFX
(whoosh, pop, tick, impact, boom, glitch, error, data, ding, riser, stamp, swish).
Writes stems + a premix; loudness is normalized afterwards with ffmpeg."""
import json, os, sys, wave
import numpy as np
from scipy import signal

S = os.path.dirname(os.path.abspath(__file__))
SR = 48000
rng = np.random.default_rng(11)
edl = json.load(open(os.path.join(S, "..", "remotion", "src", "edl.json")))
TOTAL = edl["total"]
N = int(TOTAL * SR) + SR


def read_wav(p):
    w = wave.open(p)
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x


def write_wav(p, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], "band")
    return signal.lfilter(b, a, x)


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), "low")
    return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


# ------------------------------------------------------------------ VOICE
src = read_wav(os.path.join(S, "..", "work", "lienzo48k.wav"))
voice = np.zeros(N, np.float32)
fade = int(0.008 * SR)
for seg in edl["voice"]:
    a, b = seg["src"]
    chunk = src[int(a * SR):int(b * SR)].copy()
    ramp = np.linspace(0, 1, fade)
    chunk[:fade] *= ramp
    chunk[-fade:] *= ramp[::-1]
    o = int(seg["out"] * SR)
    voice[o:o + len(chunk)] += chunk
# gentle presence lift
voice = voice + 0.25 * bp(voice, 2500, 6000)
VPK = np.max(np.abs(voice)) + 1e-9
_vn = voice / VPK * 0.95
_w = int(0.05 * SR)
_venv = np.sqrt(np.convolve(_vn ** 2, np.ones(_w) / _w, mode="same"))
V_REF_DB = 20 * np.log10(np.sqrt(np.mean(_vn[_venv > 0.02] ** 2)) + 1e-12)  # voice RMS while talking

# SFX sit UNDER the voice: each sound is levelled by its loudest 100 ms window.
SFX_BASE = -8.0  # dB relative to the voice RMS
SFX_OFF = {"whoosh": 0, "whoosh_short": -1, "swish": -3, "pop": -3, "tick": -8, "impact": -2, "boom": -2,
           "glitch": -7, "error": -6, "data": -9, "ding": -5, "riser": -4, "stamp": -3}


def level(x, kind):
    w = int(0.1 * SR)
    if len(x) <= w:
        loud = np.sqrt(np.mean(x ** 2))
    else:
        c = np.convolve(x ** 2, np.ones(w) / w, mode="valid")
        loud = np.sqrt(np.max(c))
    target = V_REF_DB + SFX_BASE + SFX_OFF.get(kind, -4)
    return x * 10 ** ((target - 20 * np.log10(loud + 1e-12)) / 20)

# ------------------------------------------------------------------ SFX
def s_whoosh(dur=0.42, up=True):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    t = np.linspace(0, 1, n)
    # sweep a band through the noise in blocks
    out = np.zeros(n)
    blocks = 24
    for i in range(blocks):
        s0, s1 = i * n // blocks, (i + 1) * n // blocks
        fc = 300 + (5200 if up else 2600) * (np.sin(np.pi * (i + 0.5) / blocks) ** 1.5)
        seg = bp(noise[max(0, s0 - 400):s1], fc * 0.6, fc * 1.6)[-(s1 - s0):]
        out[s0:s1] = seg
    envl = np.sin(np.pi * t) ** 2 * (0.4 + 0.6 * t)
    return norm(out * envl, 0.8)


def s_swish():
    return s_whoosh(0.22) * 0.8


def s_pop():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 28) + 380
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * env_exp(n, 0.025)
    x[:int(0.003 * SR)] += rng.standard_normal(int(0.003 * SR)) * 0.6
    return norm(x, 0.85)


def s_tick():
    n = int(0.018 * SR)
    x = hp(rng.standard_normal(n), 3000) * env_exp(n, 0.004)
    return norm(x, 0.7)


def s_impact():
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 120 * np.exp(-t * 9) + 42
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.28)
    crack = bp(rng.standard_normal(n), 800, 7000) * env_exp(n, 0.05)
    x = np.tanh(2.2 * body) + 0.55 * crack
    return norm(x, 0.95)


def s_boom():
    n = int(1.8 * SR)
    t = np.arange(n) / SR
    f = 70 * np.exp(-t * 3) + 30
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.65)
    air = lp(rng.standard_normal(n), 1800) * env_exp(n, 0.35) * 0.5
    x = np.tanh(2.6 * body) + air
    return norm(x, 0.98)


def s_glitch():
    n = int(0.22 * SR)
    x = np.zeros(n)
    pos = 0
    while pos < n:
        L = int(rng.uniform(0.008, 0.03) * SR)
        f = rng.choice([180, 260, 420, 900, 1500, 2400])
        t = np.arange(L) / SR
        seg = np.sign(np.sin(2 * np.pi * f * t)) * rng.uniform(0.3, 1)
        if rng.random() < 0.3:
            seg = rng.standard_normal(L) * 0.8
        x[pos:pos + L] = seg[:max(0, min(L, n - pos))]
        pos += L
    x = np.round(x * 6) / 6
    return norm(x * np.linspace(1, 0.3, n), 0.6)


def s_error():
    out = []
    for f in (330, 247):
        n = int(0.11 * SR)
        t = np.arange(n) / SR
        out.append(signal.square(2 * np.pi * f * t) * 0.6 * np.minimum(1, env_exp(n, 0.08) * 1.2))
        out.append(np.zeros(int(0.02 * SR)))
    x = lp(np.concatenate(out), 3500)
    return norm(x, 0.6)


def s_data():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    f = rng.choice([1800, 2200, 2600, 3100])
    return norm(np.sin(2 * np.pi * f * t) * env_exp(n, 0.012), 0.4)


def s_ding():
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 1318.5 * t) + 0.5 * np.sin(2 * np.pi * 1975.5 * t) + 0.25 * np.sin(2 * np.pi * 2637 * t)) * env_exp(n, 0.25)
    return norm(x, 0.6)


def s_riser(dur=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    blocks = 30
    for i in range(blocks):
        s0, s1 = i * n // blocks, (i + 1) * n // blocks
        fc = 400 + 7000 * (i / blocks) ** 2
        out[s0:s1] = bp(noise[max(0, s0 - 400):s1], fc * 0.7, fc * 1.5)[-(s1 - s0):]
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / dur) ** 2) / SR) * 0.3
    envl = (t / dur) ** 2
    return norm((out + tone) * envl, 0.7)


def s_stamp():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t * 12) + 50) / SR) * env_exp(n, 0.09)
    slap = bp(rng.standard_normal(n), 400, 4000) * env_exp(n, 0.03)
    return norm(np.tanh(2 * thud) + 0.7 * slap, 0.9)


BANK = {"whoosh": s_whoosh(), "whoosh_short": s_whoosh(0.3), "swish": s_swish(), "pop": s_pop(), "tick": s_tick(),
        "impact": s_impact(), "boom": s_boom(), "glitch": s_glitch(), "error": s_error(), "ding": s_ding(),
        "riser": s_riser(1.0), "stamp": s_stamp()}
# whoosh peak should land on the cut: shift so the envelope peak hits t
OFFSET = {"whoosh": -0.24, "whoosh_short": -0.17, "swish": -0.12, "riser": -1.0}

sfx = np.zeros(N, np.float32)
for e in edl["sfx"]:
    k = e["kind"]
    x = s_data() if k == "data" else BANK[k]
    x = level(x, k)
    a3 = int(0.004 * SR)
    x = x.copy(); x[:a3] *= np.linspace(0, 1, a3)
    if k == "riser" and e["t"] > edl["music"]["end"] - 2:
        x = level(s_riser(1.2), k)
        off = -1.2
    else:
        off = OFFSET.get(k, 0.0)
    i = int((e["t"] + off) * SR)
    if i < 0:
        x = x[-i:]; i = 0
    j = min(N, i + len(x))
    sfx[i:j] += x[:j - i] * e["gain"]

# ------------------------------------------------------------------ MUSIC (original, synthesized)
M = edl["music"]
bpm = M["bpm"]
beat = 60 / bpm
s16 = beat / 4
t0 = M["drop"]
music = np.zeros(N, np.float32)
drums = np.zeros(N, np.float32)


def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= N or i + len(x) <= 0:
        return
    if i < 0:
        x = x[-i:]; i = 0
    j = min(N, i + len(x))
    buf[i:j] += x[:j - i] * g


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 160 * np.exp(-t * 35) + 48
    return np.tanh(2.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.12))


def snare():
    n = int(0.28 * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 190 * t) * env_exp(n, 0.05)
    nz = bp(rng.standard_normal(n), 1200, 9000) * env_exp(n, 0.09)
    clap = np.zeros(n)
    for d in (0, 0.011, 0.022):
        k = int(d * SR)
        clap[k:] += bp(rng.standard_normal(n - k), 900, 5000) * env_exp(n - k, 0.03)
    return norm(0.5 * tone + nz + 0.6 * clap, 0.8)


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    x = hp(rng.standard_normal(n), 7000) * env_exp(n, 0.07 if open_ else 0.012)
    return norm(x, 0.35 if open_ else 0.28)


def cowbell(freq, dur=0.22):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = signal.square(2 * np.pi * freq * t) + signal.square(2 * np.pi * freq * 1.48 * t)
    x = bp(x, freq * 0.8, freq * 3.2) * env_exp(n, 0.09)
    return norm(x, 0.5)


def bass808(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.5 * np.exp(-t * 40))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    envl = np.minimum(1, t / 0.004) * np.exp(-t / max(0.25, dur * 0.8))
    rel = int(0.03 * SR)
    envl[-rel:] *= np.linspace(1, 0, rel)
    return np.tanh(2.4 * x * envl) * 0.9


def pad_chord(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for fr in freqs:
        for det in (-0.004, 0.004):
            ff = fr * (1 + det)
            for h in range(1, 9):
                x += np.sin(2 * np.pi * ff * h * t + rng.uniform(0, 6.28)) / (h ** 1.6)
    envl = np.minimum(1, t / 0.35) * np.minimum(1, (dur - t) / 0.3)
    return norm(lp(x, 1600) * envl, 0.25)


# A minor: Am | F | G | E
CH = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66], [164.81, 207.65, 246.94]]
BASS = [55.0, 43.65, 49.0, 41.2]
MEL = [  # cowbell riff, 8ths per bar (None = rest)
    [880, None, 880, 1046.5, None, 880, 1318.5, 1174.7],
    [880, None, 880, 1046.5, None, 1174.7, 1046.5, 880],
    [784, None, 784, 987.8, None, 784, 1174.7, 987.8],
    [830.6, None, 830.6, 987.8, None, 1318.5, 1174.7, 987.8],
]
bar = beat * 4
# intro pad (before the drop) – dark, filtered
tt = 0.0
while tt < t0:
    add(music, pad_chord([x / 2 for x in CH[0]], min(bar, t0 - tt) + 0.3), tt, 0.7)
    tt += bar
add(music, bass808(55.0, t0) * 0.35, 0.0)

end_t = M["end"]
dropout = M["dropout"]
cta = M["cta"]
K, SN, HC, HO = kick(), snare(), hat(), hat(True)
nbars = int((end_t - t0) / bar) + 1
for b in range(nbars):
    tb = t0 + b * bar
    ci = b % 4
    add(music, pad_chord(CH[ci], bar + 0.25), tb, 0.55)
    # 808 bass on 16th steps 0 and 10 (and 7 pickup on bar 4)
    for step, L in ((0, 7), (10, 6)):
        add(music, bass808(BASS[ci], s16 * L), tb + step * s16, 0.9)
    for step in (0, 7, 10):
        add(drums, K, tb + step * s16, 0.9)
    for step in (4, 12):
        add(drums, SN, tb + step * s16, 0.75)
    for step in range(0, 16, 2):
        add(drums, HC, tb + step * s16, 0.8)
    if b % 2 == 1:  # hat roll
        for k in range(6):
            add(drums, HC, tb + 13 * s16 + k * s16 / 2, 0.55)
    add(drums, HO, tb + 14 * s16, 0.6)
    for k, fr in enumerate(MEL[ci]):
        if fr:
            add(music, cowbell(fr), tb + k * 2 * s16, 0.55)

mus = music + drums
tt = np.arange(N) / SR
# dropout before "BAJA PRESIÓN"
g = np.ones(N, np.float32)
a, b = dropout
g[(tt >= a) & (tt < b)] = 0.0
# CTA: thin the beat (keep pad+808 lowpassed)
cta_mask = (tt >= cta) & (tt < end_t)
mus_lp = lp(mus, 900)
mus = np.where(cta_mask, mus_lp * 0.9, mus)
# stop at end card, then ring out a final chord
g[tt >= end_t] = 0.0
mus = mus * g
add(mus, pad_chord(CH[0], TOTAL - end_t + 0.2) * 1.6, end_t)
add(mus, bass808(55.0, 1.6), end_t, 0.9)
fo = int(0.9 * SR)
endN = int(TOTAL * SR)
mus[endN - fo:endN] *= np.linspace(1, 0, fo)
mus[endN:] = 0

# ------------------------------------------------------------------ DUCKING under the voice
win = int(0.02 * SR)
v_env = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode="same"))
active = (v_env > 0.012).astype(np.float32)
# smooth: fast attack, slow release
duck = np.zeros(N, np.float32)
att, rel = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.35 * SR))
# vectorised-ish one-pole via scipy for release (approx: max filter then lowpass)
hold = signal.convolve(active, np.ones(int(0.15 * SR)), mode="same") > 0
duck = lp(hold.astype(np.float32), 4.0, order=1)
duck = np.clip(duck, 0, 1)
music_gain = 1.0 - 0.72 * duck  # about -11 dB under voice

def db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


voice_n = voice / (np.max(np.abs(voice)) + 1e-9) * 0.95
speech = hold & (np.abs(voice_n) > -1)
v_db = db(voice_n[hold])
mus_d = mus * music_gain
m_db = db(mus_d[hold])
mus_d = mus_d * 10 ** ((v_db - 12 - m_db) / 20)  # music 12 dB under the voice while talking
sfx_n = lp(sfx, 9000)
print("voice ref dB", round(V_REF_DB, 1), "sfx peak", round(float(np.max(np.abs(sfx_n))), 3))
print("voice dB", round(v_db, 1), "music under voice dB", round(db(mus_d[hold]), 1), "music in gaps dB", round(db(mus_d[~hold & (tt < edl['music']['end'])]), 1))
mix = voice_n + mus_d + sfx_n
pk = np.max(np.abs(mix)) + 1e-9
endN = int(TOTAL * SR)
for name, x in (("stem_voice", voice_n), ("stem_music", mus_d), ("stem_sfx", sfx_n), ("premix", mix)):
    write_wav(os.path.join(S, "..", "work", f"{name}.wav"), x[:endN] / pk * 0.98)
print("ok", TOTAL, "mix peak before norm", float(pk))
