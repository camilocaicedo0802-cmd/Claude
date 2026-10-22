"""Music + synthesized SFX (whooshes, drop impact, typewriter ticks) mixed to match the edit."""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl import MUSIC_START, MUSIC_FILE

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.environ.get("JET_WORKDIR", os.path.join(HERE, "work"))  # raw/, newclips/, music2/, fonts2/
SR = 48000
DUR = float(sys.argv[1])
rng = np.random.default_rng(3)

raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{MUSIC_START:.4f}', '-t', f'{DUR:.4f}',
                      '-i', f'{S}/{MUSIC_FILE}', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                     capture_output=True).stdout
music = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
n = int(DUR * SR)
music = np.pad(music, ((0, max(0, n - len(music))), (0, 0)))[:n]
music /= np.abs(music).max() + 1e-9
music *= 0.89
fade = int(1.3 * SR)
music[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
music[:int(0.12 * SR)] *= np.linspace(0, 1, int(0.12 * SR))[:, None]


def bandsweep(noise, f_lo, f_hi):
    # time-varying one-pole lowpass minus a slower one -> moving band
    out = np.zeros_like(noise)
    a1 = a2 = 0.0
    cut = np.geomspace(f_lo, f_hi, len(noise) // 2)
    cut = np.concatenate([cut, cut[::-1]])
    cut = np.pad(cut, (0, len(noise) - len(cut)), mode='edge')
    k = 1 - np.exp(-2 * np.pi * cut / SR)
    k2 = 1 - np.exp(-2 * np.pi * cut * 0.25 / SR)
    for i in range(len(noise)):
        a1 += k[i] * (noise[i] - a1)
        a2 += k2[i] * (noise[i] - a2)
        out[i] = a1 - a2
    return out


def whoosh(length=0.42):
    m = int(length * SR)
    s = bandsweep(rng.normal(0, 1, m), 250, 5000)
    env = np.sin(np.linspace(0, np.pi, m)) ** 2
    s = s * env
    s /= np.abs(s).max()
    pan = np.linspace(-0.6, 0.6, m)
    return np.stack([s * (1 - pan) / 1.6, s * (1 + pan) / 1.6], 1), int(m * 0.55)  # peak index


def impact():
    m = int(1.6 * SR)
    t = np.arange(m) / SR
    f = 38 + 70 * np.exp(-t / 0.08)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45)
    click = rng.normal(0, 1, m) * np.exp(-t / 0.012) * 0.5
    s = np.tanh((sub + click) * 1.6)
    s /= np.abs(s).max()
    return np.stack([s, s], 1), 0


def tick():
    m = int(0.03 * SR)
    t = np.arange(m) / SR
    s = rng.normal(0, 1, m)
    s = s - np.convolve(s, np.ones(6) / 6, 'same')
    s *= np.exp(-t / 0.004)
    s /= np.abs(s).max()
    return np.stack([s, s], 1), 0


sfx = np.zeros_like(music)
ev = np.load(f'{S}/events.npy')
W_SAMPLE, I_SAMPLE, T_SAMPLE = whoosh(), impact(), tick()
for t, kind in ev:
    kind = int(kind)
    snd, peak, gain = {0: (*W_SAMPLE, 0.12), 1: (*T_SAMPLE, 0.08), 2: (*I_SAMPLE, 0.35), 3: (*T_SAMPLE, 0.06)}[kind]
    st = int(t * SR) - peak
    a, b = max(0, st), min(n, st + len(snd))
    if b > a:
        sfx[a:b] += snd[a - st:b - st] * gain

mix = music + sfx
mix = np.tanh(mix * 1.05) / np.tanh(1.05)  # soft limiter
mix = np.clip(mix, -1, 1)
with wave.open(f'{S}/mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32000).astype(np.int16).tobytes())
print('events', len(ev), 'dur', DUR)
