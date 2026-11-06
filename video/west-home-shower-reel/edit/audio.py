"""Voice + music + synthesized SFX mix -> out/mix.wav (48 kHz stereo)."""
import sys, os, subprocess, json, math
import numpy as np
import scipy.signal as sg
import scipy.io.wavfile as wf
import pyloudnorm as pyln
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T
from core import ROOT

SR = 48000
N = int(T.DUR * SR) + 1
OUT = ROOT + 'out/'
STEM = ROOT + 'out/stems/'
os.makedirs(STEM, exist_ok=True)
rng = np.random.default_rng(7)
meter = pyln.Meter(SR)


def load(path, a=None, b=None, ch=1, filt=None):
    cmd = ['ffmpeg', '-v', 'error']
    if a is not None:
        cmd += ['-ss', f'{a:.3f}']
    cmd += ['-i', path]
    if b is not None:
        cmd += ['-t', f'{b - a:.3f}']
    if filt:
        cmd += ['-af', filt]
    cmd += ['-vn', '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    return x.reshape(-1, ch) if ch > 1 else x


def fade(x, fi=0.012, fo=0.02):
    n1, n2 = int(fi * SR), int(fo * SR)
    x = x.copy()
    x[:n1] *= np.linspace(0, 1, n1) ** 2
    x[-n2:] *= np.linspace(1, 0, n2) ** 2
    return x


def db(x):
    return 10 ** (x / 20)


# ---------------------------------------------------------------- voice
VFILT = ('highpass=f=85,lowpass=f=15000,afftdn=nr=10:nf=-42,'
         'equalizer=f=200:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=9000:t=q:w=1.0:g=1.5,'
         'acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=3,deesser=i=0.35')
voice = np.zeros(N, np.float32)
vact = np.zeros(N, np.float32)
for path, a, b, tp in T.VOICE:
    pre = 0.35
    x = load(path, max(0, a - pre), b, 1, VFILT)
    x = x[int((a - max(0, a - pre)) * SR):]
    x = x.astype(np.float64)
    L = meter.integrated_loudness(x) if len(x) > SR * 0.5 else -20
    x *= db(-17.0 - L)
    x = fade(x)
    i = int(tp * SR)
    n = min(len(x), N - i)
    voice[i:i + n] += x[:n]
    vact[i:i + n] = 1
wf.write(STEM + 'voice.wav', SR, voice)

# ---------------------------------------------------------------- music (bar-aligned splice)
mus = load(ROOT + 'music/track_a.mp3', ch=2)
SPLICE_V, SPLICE_M = T.beat(40), 0.0348587766 + 0.6000508825 * 56   # video beat 40 <- track beat 56
a_end = int(SPLICE_V * SR)
xf = int(0.015 * SR)
music = np.zeros((N, 2), np.float32)
p1 = mus[:a_end + xf].copy()
p1[-2 * xf:] *= np.linspace(1, 0, 2 * xf)[:, None]
music[:len(p1)] += p1
s0 = int(SPLICE_M * SR) - xf
p2 = mus[s0:s0 + (N - (a_end - xf))].copy()
p2[:2 * xf] *= np.linspace(0, 1, 2 * xf)[:, None]
music[a_end - xf:a_end - xf + len(p2)] += p2
music[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
# fade out over the last 0.6 s
fo = int(0.6 * SR)
music[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5

# ducking envelope: voice activity smoothed (attack 60 ms, release 280 ms)
env = np.zeros(N, np.float32)
att, rel = math.exp(-1 / (0.06 * SR)), math.exp(-1 / (0.28 * SR))
v_rms = np.sqrt(sg.lfilter([1], [1, -0.999], voice.astype(np.float64) ** 2) * 0.001)
gate = (v_rms > db(-45)).astype(np.float32) * vact
# look-ahead 40 ms so the duck starts just before speech
la = int(0.04 * SR)
gate = np.concatenate([gate[la:], np.zeros(la, np.float32)])
e = 1.0
for i in range(0, N, 48):   # 1 ms control rate
    g = gate[i:i + 48].max()
    e = g + (e - g) * (att ** 48 if g > e else rel ** 48)
    env[i:i + 48] = e
ml = meter.integrated_loudness(music.astype(np.float64))
music *= db(-23.5 - ml)                       # bed level with no voice
duck_db = -8.0
music *= db(duck_db * env)[:, None]
wf.write(STEM + 'music.wav', SR, music)

# ---------------------------------------------------------------- SFX synthesis
def stft_shape(noise, centers, widths, fs=SR):
    f, t, Z = sg.stft(noise, fs, nperseg=1024, noverlap=768)
    tt = np.linspace(0, 1, Z.shape[1])
    c = np.interp(tt, np.linspace(0, 1, len(centers)), centers)
    wdt = np.interp(tt, np.linspace(0, 1, len(widths)), widths)
    lf = np.log(np.maximum(f, 20))[:, None]
    mask = np.exp(-((lf - np.log(c)[None, :]) ** 2) / (2 * wdt[None, :] ** 2))
    _, y = sg.istft(Z * mask, fs, nperseg=1024, noverlap=768)
    return y[:len(noise)]


def whoosh(dur=0.42, peak=0.55, lo=400, hi=3500, pan=0.0, pan_sweep=0.0, gain=-18, airy=True):
    n = int(dur * SR)
    tt = np.linspace(0, 1, n)
    x = rng.standard_normal(n)
    pk = peak
    cen = [lo, lo * 1.5, hi, hi * 0.9, lo * 1.2]
    y = stft_shape(x, cen, [0.9, 0.8, 0.6, 0.7, 0.9])
    envl = np.where(tt < pk, (tt / pk) ** 2.2, np.exp(-(tt - pk) / (1 - pk) * 4.5))
    y = y * envl
    if airy:
        y += 0.25 * stft_shape(rng.standard_normal(n), [6000, 9000, 7000], [0.4, 0.4, 0.4]) * envl
    y /= np.abs(y).max() + 1e-9
    p = np.clip(pan + pan_sweep * (tt - pk), -1, 1)
    L = y * np.cos((p + 1) * math.pi / 4); R = y * np.sin((p + 1) * math.pi / 4)
    return np.stack([L, R], 1) * db(gain), int(pk * n)


def pop(f0=780, f1=230, dur=0.11, gain=-17):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.018)
    ph = 2 * math.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / 0.035)
    cl = rng.standard_normal(n) * np.exp(-t / 0.002) * 0.3
    cl = sg.sosfilt(sg.butter(2, 2500, 'hp', fs=SR, output='sos'), cl)
    y = y + cl
    y /= np.abs(y).max()
    return np.stack([y, y], 1) * db(gain), 0


def click(gain=-22, f=2600, dur=0.03):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2 * math.pi * f * t) * np.exp(-t / 0.004) + rng.standard_normal(n) * np.exp(-t / 0.0015) * 0.6
    y = sg.sosfilt(sg.butter(2, 1200, 'hp', fs=SR, output='sos'), y)
    y /= np.abs(y).max()
    return np.stack([y, y], 1) * db(gain), 0


def tick(gain=-26):
    return click(gain, f=4200, dur=0.02)


def impact(gain=-14, dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 38 + 70 * np.exp(-t / 0.05)
    sub = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t / 0.32)
    nz = sg.sosfilt(sg.butter(2, 900, 'lp', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t / 0.06) * 1.5
    tail = stft_shape(rng.standard_normal(n), [2500, 1200, 500], [0.8, 0.8, 0.8]) * np.exp(-t / 0.35) * 0.35
    y = sub + nz + tail
    y /= np.abs(y).max()
    st = np.stack([y, sg.lfilter([1], [1], y)], 1)
    return st * db(gain), 0


def shimmer(gain=-22, dur=1.4):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for k, (fq, d) in enumerate([(2093, 0.0), (2637, 0.03), (3136, 0.06), (4186, 0.09), (5274, 0.12)]):
        m = t >= d
        tt = t[m] - d
        y[m] += np.sin(2 * math.pi * fq * tt * (1 + 0.002 * np.sin(2 * math.pi * 6 * tt))) * np.exp(-tt / 0.45) * (0.9 ** k)
    y += stft_shape(rng.standard_normal(n), [9000, 8000], [0.3, 0.3]) * np.exp(-t / 0.3) * 0.15
    y /= np.abs(y).max()
    L = y; R = np.concatenate([np.zeros(int(0.008 * SR)), y])[:n]
    return np.stack([L, R], 1) * db(gain), 0


def riser(dur=1.0, gain=-21):
    n = int(dur * SR); tt = np.linspace(0, 1, n)
    y = stft_shape(rng.standard_normal(n), [300, 1200, 5000], [0.5, 0.5, 0.45])
    tone = np.sin(2 * math.pi * np.cumsum(220 + 660 * tt ** 2) / SR) * 0.25
    y = (y / (np.abs(y).max() + 1e-9) + tone) * tt ** 2.2
    y[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    y /= np.abs(y).max()
    return np.stack([y, y], 1) * db(gain), n


def shutter(gain=-21):
    a, _ = click(gain, 1800, 0.03); b, _ = click(gain - 3, 1400, 0.04)
    out = np.zeros((int(0.09 * SR), 2)); out[:len(a)] += a; out[int(0.045 * SR):int(0.045 * SR) + len(b)] += b
    return out, 0


sfx = np.zeros((N, 2), np.float64)


def put(t, gen):
    y, anchor = gen
    i = int(t * SR) - anchor
    j0 = max(0, i); k0 = j0 - i
    n = min(len(y) - k0, N - j0)
    if n > 0:
        sfx[j0:j0 + n] += y[k0:k0 + n]


B = T.beat
# hook
put(0.0, impact(-19, 1.0)); put(0.03, whoosh(0.35, 0.5, 600, 4500, gain=-24))
put(0.05, pop(700, 200, gain=-19)); put(0.32, pop(820, 240, gain=-19)); put(0.55, pop(1100, 400, 0.09, gain=-21))
put(1.15, shutter(-20)); put(1.17, whoosh(0.3, 0.3, 900, 5000, pan=0.5, gain=-25))
# transitions
for tc, kind in [(B(6.5), 'left'), (B(18), 'up'), (B(30), 'right'), (B(36), 'left'), (B(40), 'up')]:
    ps = {'left': (0.6, -2.0), 'right': (-0.6, 2.0), 'up': (0.0, 0.0)}[kind]
    put(tc, whoosh(0.42, 0.62, 350, 3200, pan=ps[0], pan_sweep=ps[1], gain=-17))
put(B(9), whoosh(0.5, 0.55, 250, 2600, gain=-18))           # zoom in
put(B(22), whoosh(0.55, 0.55, 300, 2800, gain=-17))         # spin
put(B(22), impact(-24, 0.7))
put(B(32), whoosh(0.5, 0.6, 250, 3000, gain=-18))           # zoom into price shot
put(B(43), whoosh(0.7, 0.55, 300, 3600, gain=-17)); put(B(43), shimmer(-25, 1.6))
# pill / labels
put(4.28, click(-21)); put(4.40, whoosh(0.3, 0.4, 800, 5000, gain=-27))
# tile / fixtures / finishes, home / style
for tt in [B(14), B(15.5), B(17)]:
    put(tt, pop(600, 180, 0.13, gain=-17)); put(tt, tick(-27))
put(B(18) + 0.12, pop(560, 170, 0.13, gain=-18)); put(B(20) + 0.12, pop(620, 190, 0.13, gain=-18))
put(B(19), tick(-28)); put(B(21), tick(-28)); put(B(12), tick(-30)); put(B(38), tick(-29))
# everything
put(14.98, pop(560, 160, 0.14, gain=-17)); put(14.98, whoosh(0.3, 0.4, 500, 4000, gain=-26))
# montage ticks (from demolition to final installation)
for k in range(1, 8):
    put(B(26 + 0.5 * k), tick(-27 if k % 2 else -25))
# price build-up
put(B(32), riser(1.0, -22))
put(19.46, click(-20)); put(19.50, whoosh(0.3, 0.35, 900, 5000, gain=-26))
tc0, tl = 20.08, 20.95
k = 0
while True:
    p = k / 14
    t = tc0 + (tl - tc0) * (1 - (1 - p) ** 2.2) if p <= 1 else None
    if t is None or t >= tl - 0.03:
        break
    put(t, click(-27, 3400 + 60 * k, 0.015)); k += 1
put(tl, impact(-15, 1.3)); put(tl, shimmer(-20, 1.6)); put(tl, pop(900, 300, 0.1, gain=-20))
# end CTA
put(B(43) + 0.3, pop(560, 170, 0.13, gain=-19)); put(B(43) + 0.48, pop(640, 190, 0.13, gain=-18))
put(B(48), impact(-14, 1.6)); put(B(48), pop(700, 210, 0.12, gain=-18)); put(B(48), shimmer(-25, 1.2))
put(B(48) + 0.6, whoosh(0.35, 0.4, 700, 4500, pan=-0.3, pan_sweep=1.2, gain=-24)); put(B(48) + 0.6, click(-23))
put(B(48) + 1.2, pop(900, 320, 0.08, gain=-23))

wf.write(STEM + 'sfx.wav', SR, sfx.astype(np.float32))

# ---------------------------------------------------------------- mix + master
mix = np.stack([voice, voice], 1).astype(np.float64) + music.astype(np.float64) + sfx
L = meter.integrated_loudness(mix)
mix *= db(-14.3 - L)
wf.write(OUT + 'mix_pre.wav', SR, mix.astype(np.float32))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT + 'mix_pre.wav', '-af',
                'alimiter=limit=0.84:attack=3:release=60:level=disabled', '-c:a', 'pcm_s24le', OUT + 'mix.wav'], check=True)
sr_, fin = wf.read(OUT + 'mix.wav')
fin = fin.astype(np.float64) / 2 ** 31
print('final LUFS', round(meter.integrated_loudness(fin), 2), 'peak dBFS', round(20 * np.log10(np.abs(fin).max()), 2))
for name, x in [('voice', np.stack([voice, voice], 1)), ('music', music), ('sfx', sfx)]:
    print(name, 'LUFS (pre-master)', round(meter.integrated_loudness(x.astype(np.float64)), 1))
