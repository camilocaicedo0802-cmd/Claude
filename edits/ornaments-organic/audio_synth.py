import numpy as np, wave, sys
SR = 44100
rng = np.random.default_rng(7)

def write(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

def adsr(n, a, d, s, r):
    e = np.ones(n) * s
    A, D, R = int(a*SR), int(d*SR), int(r*SR)
    e[:A] = np.linspace(0, 1, A)
    e[A:A+D] = np.linspace(1, s, D)
    e[-R:] *= np.linspace(1, 0, R)
    return e

def midi(m): return 440 * 2 ** ((m - 69) / 12)

def pluck(f, dur, bright=0.5):
    # Karplus-Strong, soft nylon-like
    n = int(dur * SR); N = int(SR / f)
    buf = rng.uniform(-1, 1, N) * 0.5
    buf = np.convolve(buf, np.ones(3) / 3, 'same')
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % N]
        buf[i % N] = 0.996 * (bright * buf[i % N] + (1 - bright) * buf[(i + 1) % N]) if True else 0
    return out * np.exp(-np.arange(n) / (SR * 1.2))

def bell(f, dur, amp=1.0):
    t = np.arange(int(dur * SR)) / SR
    x = (np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*6) + 0.2*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*10))
    return amp * x * np.exp(-t * 3.0) * np.minimum(1, t / 0.003)

def pad(freqs, dur):
    t = np.arange(int(dur * SR)) / SR
    x = sum(np.sin(2*np.pi*f*t + np.sin(2*np.pi*0.3*t)*0.4) + 0.3*np.sin(2*np.pi*2*f*t) for f in freqs) / len(freqs)
    return x * adsr(len(t), 0.6, 0.3, 0.8, 0.8)

def add(out, s, i):
    if i >= len(out): return
    m = min(len(s), len(out) - i); out[i:i+m] += s[:m]

# ---------- music: warm, soft, 92 bpm, I-vi-IV-V in F (holiday-ish music box + nylon pluck) ----------
def music(total=16.5, bpm=92):
    beat = 60 / bpm; bar = 4 * beat
    out = np.zeros(int((total + 3) * SR))
    prog = [[53, 57, 60, 65], [50, 57, 62, 65], [46, 53, 58, 62], [48, 55, 60, 64]]  # F, Dm, Bb, C
    melody = [[77, 76, 72, 74], [77, 74, 72, 69], [70, 74, 77, 74], [72, 76, 79, 76]]
    nbars = int(total / bar) + 2
    for b in range(nbars):
        ch = prog[b % 4]; t0 = b * bar
        p = pad([midi(m) for m in ch[1:]], bar + 0.8) * 0.10
        add(out, p, int(t0 * SR))
        # arpeggiated nylon plucks on eighths
        arp = [ch[0], ch[2], ch[3], ch[2] + 12, ch[3], ch[2], ch[1] + 12, ch[2]]
        for k, m in enumerate(arp):
            s = pluck(midi(m), 1.4, 0.5) * (0.20 if k % 2 == 0 else 0.13)
            add(out, s, int((t0 + k * beat / 2) * SR))
        # music-box melody on quarter notes (sparse)
        for k, m in enumerate(melody[b % 4]):
            if (b + k) % 3 == 2: continue
            s = bell(midi(m), 1.6, 0.09)
            add(out, s, int((t0 + k * beat) * SR))
        # very soft brushed hat + gentle kick
        for k in range(8):
            n = int(0.05 * SR); h = rng.normal(0, 1, n) * np.exp(-np.arange(n) / (SR * 0.012))
            h = np.diff(h, prepend=0) * (0.035 if k % 2 else 0.02)
            add(out, h, int((t0 + k * beat / 2) * SR))
        for k in (0, 2):
            t = np.arange(int(0.3 * SR)) / SR
            kk = np.sin(2*np.pi*(50 + 60*np.exp(-t*30))*t) * np.exp(-t*12) * 0.18
            add(out, kk, int((t0 + k * beat) * SR))
    out = out[:int(total * SR)]
    # simple reverb-ish (multi-tap), stereo widen
    L = out.copy(); R = out.copy()
    for d, g in [(0.031, .25), (0.047, .2), (0.089, .15), (0.137, .1)]:
        n = int(d * SR); L[n:] += out[:-n] * g; R[int(n*1.13):] += out[:-int(n*1.13)] * g
    st = np.stack([L, R], 1)
    st /= np.max(np.abs(st)) + 1e-9
    fade = np.ones(len(st)); fi = int(0.4*SR); fo = int(1.2*SR)
    fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
    return st * fade[:, None] * 0.9

# ---------- SFX ----------
def whoosh(dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    # sweeping bandpass via one-pole filters with moving cutoff
    fc = 400 + 5000 * np.sin(np.pi * t / dur) ** 2
    y = np.zeros(n); lp = 0; hp = 0; prev = 0
    for i in range(n):
        a = 1 - np.exp(-2*np.pi*fc[i]/SR); lp += a * (x[i] - lp)
        hp = 0.97 * (hp + lp - prev); prev = lp; y[i] = hp
    env = np.sin(np.pi * t / dur) ** 2
    y = y * env; return y / np.max(np.abs(y)) * 0.5

def pop():
    t = np.arange(int(0.09 * SR)) / SR
    x = np.sin(2*np.pi*(900 - 500*t/0.09)*t) * np.exp(-t*55)
    return x * 0.45

def ding():
    return (bell(midi(88), 1.2, 0.35) + bell(midi(95), 1.2, 0.18))

def sparkle():
    out = np.zeros(int(1.0 * SR))
    for k, m in enumerate([96, 100, 103, 108]):
        s = bell(midi(m), 0.6, 0.12); add(out, s, int(k * 0.06 * SR))
    return out

if __name__ == '__main__':
    d = sys.argv[1]
    write(f'{d}/music.wav', music())
    write(f'{d}/whoosh.wav', whoosh())
    write(f'{d}/pop.wav', pop())
    write(f'{d}/ding.wav', ding())
    write(f'{d}/sparkle.wav', sparkle())
