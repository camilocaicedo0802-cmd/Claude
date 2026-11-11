# Efectos de sonido sintetizados (originales): pop, whoosh, click, sparkle, chime, swoosh-up
import numpy as np, wave, os, sys
SR = 48000
out = sys.argv[1]
rng = np.random.default_rng(7)
def env_ad(n, a, d, shape=3.0):
    t = np.arange(n) / SR
    e = np.minimum(t / max(a, 1e-4), 1.0) * np.exp(-np.maximum(t - a, 0) * shape / max(d, 1e-4))
    return e
def save(name, x, gain=0.9):
    x = x / (np.max(np.abs(x)) + 1e-9) * gain
    st = np.stack([x, x], 1)
    w = wave.open(os.path.join(out, name + ".wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
def lp(x, fc):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(4, fc, 'lp', fs=SR, output='sos'), x)
def bp(x, lo, hi):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(3, [lo, hi], 'bp', fs=SR, output='sos'), x)
# POP: burbuja suave (sine con caída de tono)
n = int(0.12 * SR); t = np.arange(n) / SR
f = 900 * np.exp(-t * 18) + 380
pop = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.002, 0.05, 4)
save("pop", pop)
# POP2: más agudo (para palabras)
f = 1400 * np.exp(-t * 25) + 600
save("pop_hi", np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.001, 0.035, 4), 0.8)
# CLICK: tic corto
n = int(0.04 * SR); t = np.arange(n) / SR
click = (bp(rng.standard_normal(n), 2500, 7000) * 0.6 + np.sin(2 * np.pi * 1800 * t)) * env_ad(n, 0.0005, 0.008, 5)
save("click", click, 0.7)
# WHOOSH: ruido filtrado con barrido y envolvente en campana
n = int(0.42 * SR); t = np.arange(n) / SR
noise = rng.standard_normal(n)
from scipy.signal import butter, sosfilt
seg = 64; y = np.zeros(n)
for i in range(0, n, n // seg):
    j = min(n, i + n // seg); c = 600 + 5000 * (i / n) ** 1.3
    y[i:j] = sosfilt(butter(2, [c * 0.6, min(c * 1.8, 20000)], 'bp', fs=SR, output='sos'), noise[i:j])
e = np.sin(np.pi * np.clip(t / t[-1], 0, 1)) ** 2.2
whoosh = lp(y * e, 9000)
save("whoosh", whoosh, 0.75)
# SWISH corto (transición rápida)
n = int(0.22 * SR); t = np.arange(n) / SR
y = bp(rng.standard_normal(n), 1500, 9000) * (np.sin(np.pi * t / t[-1]) ** 3)
save("swish", y, 0.7)
# SPARKLE: notas agudas tipo campanita con arpegio
def bell(fr, dur, decay=6):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * fr * m * t) for m, a in [(1, 1), (2.76, 0.35), (5.4, 0.15), (8.9, 0.06)])
    return s * env_ad(n, 0.002, dur, decay)
n = int(0.9 * SR); sp = np.zeros(n)
for k, (fr, at) in enumerate([(2093, 0.0), (2637, 0.06), (3136, 0.12), (4186, 0.18)]):
    b = bell(fr, 0.6, 7) * (0.8 - k * 0.1); i = int(at * SR); sp[i:i + len(b)] += b[:n - i]
save("sparkle", sp, 0.6)
# CHIME: ding suave (para soluciones)
c = bell(1568, 1.1, 4.5) + 0.6 * bell(2349, 1.1, 5)
save("chime", c, 0.6)
# DING final (CTA)
d = bell(1319, 1.4, 3.5) + 0.7 * bell(1976, 1.4, 4) + 0.4 * bell(2637, 1.4, 5)
save("ding", d, 0.65)
# RISER suave para el hook
n = int(0.7 * SR); t = np.arange(n) / SR
y = bp(rng.standard_normal(n), 2000, 12000) * (t / t[-1]) ** 2.5
sh = np.sin(2 * np.pi * np.cumsum(400 + 1600 * (t / t[-1]) ** 2) / SR) * 0.15 * (t / t[-1]) ** 2
save("riser", y + sh, 0.6)
print("ok")
