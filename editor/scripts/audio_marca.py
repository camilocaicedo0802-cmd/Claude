"""Sintetiza desde cero la música de fondo y los efectos de sonido (100 % propios, sin derechos de terceros).

Uso: python -I scripts/audio_marca.py [duracion_musica_s]
     (sin argumento lee src/data/edit.json y suma HOLD = 0,7 s)
Requiere: numpy, scipy.
Salida: public/audio/*.wav (48 kHz, estéreo, 16 bits)
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
RAIZ = Path(__file__).resolve().parent.parent
OUT = RAIZ / "public/audio"
rng = np.random.default_rng(21)


# ---------- utilidades ----------
def t_(dur):
    return np.arange(int(dur * SR)) / SR


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def filtro(x, tipo, f, orden=2):
    sos = butter(orden, f, btype=tipo, fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


def estereo(m, pan=0.0):
    """pan -1 (izq) … 1 (dcha), ley de potencia constante"""
    a = (pan + 1) * np.pi / 4
    return np.stack([m * np.cos(a), m * np.sin(a)], axis=1)


def reverb(x, dur=2.2, decay=0.55, wet=0.3):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    ir = np.stack([rng.standard_normal(n), rng.standard_normal(n)], 1) * np.exp(-tt / decay)[:, None]
    ir = filtro(ir, "lowpass", 5000)
    ir /= np.sqrt((ir ** 2).sum(0, keepdims=True))
    mojado = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + mojado * wet


def guardar(nombre, x, pico_db=-3.0):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = estereo(x)
    x = x / (np.abs(x).max() + 1e-9) * 10 ** (pico_db / 20)
    OUT.mkdir(parents=True, exist_ok=True)
    wavfile.write(OUT / f"{nombre}.wav", SR, (x * 32767).astype(np.int16))
    print(f"  {nombre}.wav  {len(x) / SR:.2f}s")


def ruido(dur):
    return rng.standard_normal(int(dur * SR))


# ---------- música: pad + piano eléctrico + bajo + percusión ligera (84 BPM, Fa mayor) ----------
def musica(duracion):
    bpm = 84
    beat = 60 / bpm
    compas = 4 * beat
    n = int((duracion + 2.5) * SR)
    mix = np.zeros((n, 2))
    acordes = [[53, 57, 60, 64], [57, 60, 64, 67], [50, 53, 57, 60], [46, 50, 53, 57]]  # Fmaj7 Am7 Dm7 Bbmaj7
    bajos = [41, 45, 38, 34]
    total_compases = int(np.ceil(duracion / compas)) + 1
    fin_ritmo = duracion - 1.5  # la percusión se calla antes del final

    def poner(señal, inicio):
        i = int(inicio * SR)
        if i >= n:
            return
        j = min(n, i + len(señal))
        mix[i:j] += señal[: j - i]

    for b in range(total_compases):
        t0 = b * compas
        ac = acordes[b % 4]
        # PAD: armónicos suaves, dos voces desafinadas, ataque lento
        dur = compas + 1.0
        tt = t_(dur)
        env = np.minimum(1, tt / 0.7) * np.clip((dur - tt) / 1.0, 0, 1)
        for k, nota in enumerate(ac):
            for det, pan in ((-6, -0.6), (6, 0.6)):
                f = hz(nota) * 2 ** (det / 1200)
                s = sum(np.sin(2 * np.pi * f * h * tt + rng.uniform(0, 6.28)) / h ** 1.6 for h in range(1, 7))
                poner(estereo(s * env * 0.05, pan), t0)
        # PIANO ELÉCTRICO: arpegio en corcheas, una octava arriba
        if b >= 0:
            patron = [0, 1, 2, 3, 2, 1, 2, 3]
            for k, idx in enumerate(patron):
                f = hz(ac[idx] + 12)
                tt = t_(1.2)
                vel = rng.uniform(0.55, 0.9)
                env = np.minimum(1, tt / 0.004) * np.exp(-tt / 0.45)
                s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / 0.15)) * env * vel
                poner(estereo(s * 0.11, 0.35 if k % 2 else -0.35), t0 + k * beat / 2)
        # BAJO: tiempos 1 y 3 a partir del compás 2
        if b >= 1:
            for tb in (0, 2):
                tt = t_(beat * 1.6)
                env = np.minimum(1, tt / 0.01) * np.exp(-tt / 0.8) * np.clip((beat * 1.6 - tt) / 0.1, 0, 1)
                f = hz(bajos[b % 4])
                s = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * env
                poner(estereo(s * 0.10), t0 + tb * beat)
        # PERCUSIÓN: a partir del compás 3 (bombo suave 1 y 3, chasquido 2 y 4, shaker en semicorcheas)
        if b >= 2 and t0 < fin_ritmo:
            for tb in range(4):
                tg = t0 + tb * beat
                if tg > fin_ritmo:
                    break
                if tb in (0, 2):
                    tt = t_(0.35)
                    fase = 2 * np.pi * np.cumsum(45 + 75 * np.exp(-tt / 0.04)) / SR
                    poner(estereo(np.sin(fase) * np.exp(-tt / 0.12) * 0.12), tg)
                else:
                    c = filtro(ruido(0.18), "bandpass", [1200, 3500]) * np.exp(-t_(0.18) / 0.04)
                    poner(estereo(c * 0.09, 0.1), tg)
                for s16 in range(4):
                    sh = filtro(ruido(0.06), "highpass", 6500) * np.exp(-t_(0.06) / 0.015)
                    poner(estereo(sh * (0.05 if s16 % 2 else 0.028), 0.4), tg + s16 * beat / 4)

    mix = reverb(mix, dur=2.6, decay=0.7, wet=0.32)
    # Limpieza para que la voz mande: fuera graves < 70 Hz y hueco suave (−4 dB) en 1–3 kHz
    mix = filtro(mix, "highpass", 70)
    mix = mix - 0.37 * filtro(mix, "bandpass", [1000, 3000])
    mix = mix[: int(duracion * SR)]
    tt = t_(duracion)
    mix *= (np.minimum(1, tt / 0.4) * np.clip((duracion - tt) / 1.5, 0, 1))[:, None]
    mix = np.tanh(mix * 1.4)
    return mix


# ---------- efectos ----------
def whoosh(dur=0.75, pico=0.42, f0=250, f1=3000, suave=False):
    tt = t_(dur)
    x = ruido(dur)
    env = np.where(tt < pico, (tt / pico) ** 2, np.exp(-(tt - pico) / (0.12 if suave else 0.16)))
    out = np.zeros_like(x)
    hop = 512
    zi = None
    for i in range(0, len(x), hop):
        fc = f0 + (f1 - f0) * np.sin(np.pi * min(1, i / len(x)) * 0.5 + 0.0) ** 1.5
        sos = butter(2, [fc * 0.5, min(fc * 1.6, 20000)], btype="bandpass", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + hop], zi = sosfilt(sos, x[i:i + hop], zi=zi)
    out *= env
    pan = np.linspace(-0.7, 0.7, len(out))
    a = (pan + 1) * np.pi / 4
    return reverb(np.stack([out * np.cos(a), out * np.sin(a)], 1), dur=1.0, decay=0.3, wet=0.2)


def pop():
    tt = t_(0.18)
    f = 300 + 700 * np.exp(-tt / 0.018)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.05)
    s[: int(0.003 * SR)] += filtro(ruido(0.003), "highpass", 3000) * 0.3
    return reverb(estereo(s), dur=0.6, decay=0.15, wet=0.15)


def tecleo(dur=1.6):
    x = np.zeros(int(dur * SR))
    t = 0.02
    while t < dur - 0.05:
        i = int(t * SR)
        clic = filtro(ruido(0.006), "bandpass", [2000, 6000]) * np.exp(-t_(0.006) / 0.0015)
        golpe = np.sin(2 * np.pi * rng.uniform(160, 220) * t_(0.025)) * np.exp(-t_(0.025) / 0.006)
        v = rng.uniform(0.6, 1.0)
        x[i:i + len(clic)] += clic * v
        x[i:i + len(golpe)] += golpe * 0.5 * v
        t += rng.uniform(0.055, 0.1)
    return reverb(estereo(x, 0.1), dur=0.4, decay=0.08, wet=0.12)


def campanita(notas=(88, 93), retraso=0.09):
    dur = 2.2
    x = np.zeros(int(dur * SR))
    for k, nota in enumerate(notas):
        tt = t_(dur - k * retraso)
        f = hz(nota)
        s = sum(a * np.sin(2 * np.pi * f * p * tt) * np.exp(-tt / d)
                for p, a, d in ((1, 1, 1.1), (2.76, 0.45, 0.5), (5.4, 0.22, 0.25), (8.93, 0.1, 0.12)))
        s *= np.minimum(1, tt / 0.002)
        i = int(k * retraso * SR)
        x[i:i + len(s)] += s * (1 if k == 0 else 0.8)
    return reverb(estereo(x, 0.2), dur=2.0, decay=0.6, wet=0.35)


def tictac(dur=1.4, paso=0.14):
    x = np.zeros(int(dur * SR))
    t, k = 0.0, 0
    while t < dur - 0.03:
        f = 2600 if k % 2 == 0 else 1700
        tt = t_(0.03)
        s = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.004) + filtro(ruido(0.03), "highpass", 4000) * np.exp(-tt / 0.002) * 0.4
        i = int(t * SR)
        x[i:i + len(s)] += s
        t += paso
        k += 1
    return reverb(estereo(x, -0.2), dur=0.5, decay=0.1, wet=0.15)


def blips(dur=0.7, n=11):
    x = np.zeros(int((dur + 0.15) * SR))
    for k in range(n):
        p = k / (n - 1)
        t = dur * (1 - (1 - p) ** (1 / 3)) if k else 0.0  # sigue la curva de la cuenta (ease-out)
        f = 700 + 900 * p
        tt = t_(0.05)
        s = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.015) * np.minimum(1, tt / 0.002)
        i = int(t * SR)
        x[i:i + len(s)] += s * (0.6 + 0.4 * p)
    return reverb(estereo(x), dur=0.6, decay=0.15, wet=0.2)


def escalones():
    x = np.zeros(int(1.4 * SR))
    for k, nota in enumerate((72, 76, 79, 84)):  # Do Mi Sol Do
        tt = t_(0.8)
        f = hz(nota)
        s = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 4 * f * tt) * np.exp(-tt / 0.03)) * np.exp(-tt / 0.25)
        i = int(k * 0.15 * SR)
        x[i:i + len(s)] += s * np.minimum(1, tt / 0.002)
    return reverb(estereo(x, 0.15), dur=1.2, decay=0.35, wet=0.25)


def tarjeta():
    dur = 0.32
    tt = t_(dur)
    desliza = filtro(ruido(dur), "bandpass", [600, 2500]) * np.sin(np.pi * np.clip(tt / 0.22, 0, 1)) ** 2 * 0.5
    golpe = np.zeros_like(tt)
    i = int(0.2 * SR)
    g = np.sin(2 * np.pi * 95 * t_(0.12)) * np.exp(-t_(0.12) / 0.04)
    golpe[i:i + len(g)] = g[: len(golpe) - i]
    return reverb(estereo(desliza + golpe), dur=0.6, decay=0.12, wet=0.15)


def tachado():
    dur = 0.32
    tt = t_(dur)
    rugoso = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 38 * tt + 3 * np.sin(2 * np.pi * 7 * tt)))
    s = filtro(ruido(dur), "bandpass", [1500, 5000]) * rugoso * np.sin(np.pi * tt / dur) ** 0.7
    return estereo(filtro(s, "lowpass", 7000), 0.15)


def brillo(dur=1.2):
    x = np.zeros(int((dur + 0.5) * SR))
    for k in range(26):
        t = dur * (k / 26) ** 0.7
        f = rng.uniform(3000, 8000)
        tt = t_(0.25)
        s = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.06) * np.minimum(1, tt / 0.002)
        i = int(t * SR)
        x[i:i + len(s)] += s * rng.uniform(0.3, 1.0)
    return reverb(estereo(x), dur=1.5, decay=0.5, wet=0.45)


def impacto():
    dur = 1.0
    tt = t_(dur)
    sub = np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-tt / 0.08)) / SR) * np.exp(-tt / 0.35)
    trans = filtro(ruido(dur), "lowpass", 1500) * np.exp(-tt / 0.03) * 0.5
    return reverb(estereo(sub + trans), dur=1.5, decay=0.5, wet=0.25)


def subida(dur=0.85):
    tt = t_(dur)
    f = 200 * (6 ** (tt / dur))
    tono = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35
    s = (filtro(ruido(dur), "highpass", 1500) * 0.5 + tono) * (tt / dur) ** 2.2
    s[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    return reverb(estereo(s), dur=0.8, decay=0.2, wet=0.2)


def main():
    if len(sys.argv) > 1:
        duracion = float(sys.argv[1])
    else:
        duracion = json.load(open(RAIZ / "src/data/edit.json"))["duration"] + 0.7
    print(f"Música {duracion:.2f}s y efectos → {OUT}")
    guardar("musica", musica(duracion), pico_db=-1.0)
    guardar("whoosh", whoosh())
    guardar("swish", whoosh(dur=0.45, pico=0.22, f0=900, f1=6000, suave=True))
    guardar("pop", pop())
    guardar("tecleo", tecleo())
    guardar("campanita", campanita())
    guardar("tictac", tictac())
    guardar("blips", blips())
    guardar("escalones", escalones())
    guardar("tarjeta", tarjeta())
    guardar("tachado", tachado())
    guardar("brillo", brillo())
    guardar("impacto", impacto())
    guardar("subida", subida())


if __name__ == "__main__":
    main()
