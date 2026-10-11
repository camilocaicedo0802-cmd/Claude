"""Construye la música (bucle de la cama musical de la referencia) y los SFX.
- Música: pista 'other' de Demucs (htdemucs_ft) de la referencia -> componente armónico (HPSS) -> bucle con fundidos.
- SFX de la referencia: componente percusivo de 'no_vocals' en los instantes medidos en estilo.md.
- SFX sintetizados: tick, boom, blip, swipe, riser, scribble, sand."""
import numpy as np, librosa, soundfile as sf, os
REF = "/home/user/Claude/referencia"
OUT = "/home/user/Claude/video/public"
SR = 44100
os.makedirs(f"{OUT}/sfx", exist_ok=True); os.makedirs(f"{OUT}/audio", exist_ok=True)

def db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
def norm_peak(x, peak_db=-1.0):
    p = np.max(np.abs(x)) + 1e-12
    return x * (10 ** (peak_db / 20) / p)
def fade(x, fi=0.005, fo=0.02):
    n = len(x); a = np.ones(n)
    i = int(fi * SR); o = int(fo * SR)
    if i: a[:i] = np.linspace(0, 1, i)
    if o: a[-o:] = np.minimum(a[-o:], np.linspace(1, 0, o))
    return x * (a[:, None] if x.ndim == 2 else a)

# ---------- música ----------
other, _ = librosa.load(f"{REF}/separado4/htdemucs_ft/audio_ref/other.wav", sr=SR, mono=False)
bass, _ = librosa.load(f"{REF}/separado4/htdemucs_ft/audio_ref/bass.wav", sr=SR, mono=False)
mus = other + bass
harm = np.stack([librosa.effects.hpss(ch, margin=2.0)[0] for ch in mus])  # (2, n)
seg = harm[:, int(0.30 * SR): int(8.30 * SR)]          # 8 s útiles
xf = int(1.0 * SR)
target = int(43.5 * SR)
out = np.zeros((2, target + len(seg[0])))
pos = 0; first = True
t = np.linspace(0, np.pi / 2, xf)
fin, fout = np.sin(t), np.cos(t)
while pos < target:
    s = seg.copy()
    if not first: s[:, :xf] *= fin
    s[:, -xf:] *= fout
    out[:, pos:pos + s.shape[1]] += s
    pos += s.shape[1] - xf; first = False
out = out[:, :target]
out = norm_peak(out, -3.0)
print("música RMS", round(db(out), 1), "dB")
sf.write(f"{OUT}/audio/musica_ref_loop.wav", out.T, SR)

# ---------- SFX de la referencia ----------
nv, _ = librosa.load(f"{REF}/separado/htdemucs_ft/audio_ref/no_vocals.wav", sr=SR, mono=False)
perc = np.stack([librosa.effects.hpss(ch, margin=1.5)[1] for ch in nv])
for name, a, b in [("ref_whoosh_in", 0.00, 1.30), ("ref_pop", 3.30, 3.90), ("ref_whoosh_tr", 4.28, 4.95),
                   ("ref_whoosh_soft", 6.28, 6.95), ("ref_impact", 7.58, 8.30)]:
    x = nv[:, int(a * SR):int(b * SR)] * 0.6 + perc[:, int(a * SR):int(b * SR)] * 0.4
    x = fade(x.T, 0.003, 0.08)
    sf.write(f"{OUT}/sfx/{name}.wav", norm_peak(x, -1.0), SR)

# ---------- SFX sintetizados ----------
rng = np.random.default_rng(7)
def env(n, a, d):  # ataque/decay exponencial
    t = np.arange(n) / SR
    e = np.minimum(t / max(a, 1e-4), 1.0) * np.exp(-np.maximum(t - a, 0) / d)
    return e
def stereo(x, w=0.15):
    d = int(0.008 * SR)
    l = x; r = np.concatenate([np.zeros(d), x[:-d]])
    return np.stack([l * (1 - w) + r * w, r * (1 - w) + l * w], 1)
def bandnoise(n, lo, hi):
    X = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, n)
def sweep_noise(n, f0, f1, q=0.6):
    """ruido filtrado con banda móvil (whoosh)"""
    hop = 512; outp = np.zeros(n + hop * 2)
    win = np.hanning(hop * 2)
    for i in range(0, n, hop):
        p = i / n
        fc = f0 * (f1 / f0) ** p
        seg = bandnoise(hop * 2, fc * (1 - q), fc * (1 + q)) * win
        outp[i:i + hop * 2] += seg
    return outp[:n]

# tick de reloj
n = int(0.09 * SR); t = np.arange(n) / SR
tick = (np.sin(2 * np.pi * 3200 * t) * 0.6 + bandnoise(n, 2000, 9000) * 0.5) * env(n, 0.0005, 0.012)
sf.write(f"{OUT}/sfx/tick.wav", norm_peak(stereo(tick, 0.05), -6), SR)
# boom grave (impacto)
n = int(1.6 * SR); t = np.arange(n) / SR
fr = 55 * np.exp(-t * 1.2) + 32
boom = np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, 0.003, 0.45) + bandnoise(n, 30, 400) * env(n, 0.001, 0.05) * 0.6
sf.write(f"{OUT}/sfx/boom.wav", norm_peak(stereo(boom, 0.1), -1), SR)
# blip (notificación suave)
n = int(0.22 * SR); t = np.arange(n) / SR
blip = (np.sin(2 * np.pi * 1320 * t) + 0.4 * np.sin(2 * np.pi * 1980 * t)) * env(n, 0.002, 0.05)
blip += np.sin(2 * np.pi * 880 * t) * env(n, 0.002, 0.03) * 0.5
sf.write(f"{OUT}/sfx/blip.wav", norm_peak(stereo(blip, 0.2), -4), SR)
# pop (aparición de elemento)
n = int(0.18 * SR); t = np.arange(n) / SR
pf = 900 * np.exp(-t * 40) + 180
pop = np.sin(2 * np.pi * np.cumsum(pf) / SR) * env(n, 0.001, 0.03) + bandnoise(n, 1500, 7000) * env(n, 0.0005, 0.006) * 0.4
sf.write(f"{OUT}/sfx/pop.wav", norm_peak(stereo(pop, 0.2), -3), SR)
# swipe (deslizar pantalla)
n = int(0.35 * SR)
sw = sweep_noise(n, 600, 5000, 0.5) * np.sin(np.linspace(0, np.pi, n)) ** 1.5
sf.write(f"{OUT}/sfx/swipe.wav", norm_peak(stereo(sw, 0.35), -3), SR)
# whoosh largo (transición)
n = int(0.75 * SR)
wh = sweep_noise(n, 250, 2600, 0.7) * np.sin(np.linspace(0, np.pi, n)) ** 2
wh += sweep_noise(n, 80, 300, 0.6) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.6
sf.write(f"{OUT}/sfx/whoosh_long.wav", norm_peak(stereo(wh, 0.4), -2), SR)
# riser (subida de tensión)
n = int(1.8 * SR); t = np.arange(n) / SR
rs = sweep_noise(n, 300, 6000, 0.35) * (t / t[-1]) ** 2.2
rs += np.sin(2 * np.pi * np.cumsum(110 * 2 ** (t * 1.6)) / SR) * (t / t[-1]) ** 3 * 0.25
sf.write(f"{OUT}/sfx/riser.wav", norm_peak(fade(stereo(rs, 0.3), 0.01, 0.01), -3), SR)
# scribble (tachar con rotulador)
n = int(0.45 * SR); t = np.arange(n) / SR
am = 0.55 + 0.45 * np.sin(2 * np.pi * 14 * t)
sc = bandnoise(n, 1800, 7000) * am * env(n, 0.01, 0.25)
sf.write(f"{OUT}/sfx/scribble.wav", norm_peak(stereo(sc, 0.1), -6), SR)
# arena / disolución
n = int(1.4 * SR); t = np.arange(n) / SR
gr = np.zeros(n)
for _ in range(900):
    p = int(rng.uniform(0, n - 400)); L = int(rng.uniform(40, 300))
    gr[p:p + L] += rng.standard_normal(L) * np.hanning(L) * rng.uniform(0.2, 1)
gr = np.convolve(gr, np.ones(3) / 3, "same") * (np.sin(np.linspace(0, np.pi, n)) ** 0.7)
sf.write(f"{OUT}/sfx/sand.wav", norm_peak(stereo(gr, 0.5), -6), SR)
print("ok")
