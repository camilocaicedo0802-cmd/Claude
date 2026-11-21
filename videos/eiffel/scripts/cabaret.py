"""Música y efectos del video largo (todo sintetizado por código: sin derechos).

Música (sigue la línea de tiempo de la voz, public/voz-palabras.json):
- tema de piano de cabaret de los años 20 (Re menor, con swing) y sus variaciones por capítulo:
  circo (la fiera domada), marcha pomposa con tuba (Hindenburg), pizzicato (los genios), zumbido grave (los dos meses),
  silencio total (Dachau), violonchelo solo (momentos serios) y el tema lento a piano solo (final).
Efectos nuevos: jarras, disparo apagado + yeso, abucheos, grillos, disco rayado, fuego, mazo, sobres, cajón.

Uso: python3 scripts/cabaret.py [--solo efectos|musica]
"""

import argparse
import json
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import guion as g  # noqa: E402

SR = 44100
rng = np.random.default_rng(23)


def guardar(nombre, x, gan=0.9, normalizar=True):
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    if normalizar:
        pico = float(np.max(np.abs(x))) or 1.0
        x = x / pico * gan
    datos = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(nombre, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(datos.tobytes())


def t(seg):
    return np.arange(int(SR * seg), dtype=np.float32) / SR


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def banda(x, lo=0.0, hi=None, orden=2.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo > 0:
        m *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** orden)
    if hi:
        m *= 1 / (1 + (f / hi) ** orden)
    return np.fft.irfft(X * m, n=len(x)).astype(np.float32)


def ruido(seg):
    return rng.standard_normal(int(SR * seg)).astype(np.float32)


# ============================================================ instrumentos

def piano(m, dur, vel=0.8):
    """nota de piano (aditiva, con algo de inarmonía y caída por parcial)"""
    largo = dur + 1.2
    tt = t(largo)
    f0 = hz(m)
    x = np.zeros_like(tt)
    B = 0.0004
    for k in range(1, 10):
        fk = f0 * k * np.sqrt(1 + B * k * k)
        if fk > SR / 2.3:
            break
        caida = 1.2 + 0.9 * k + f0 / 300
        x += np.sin(2 * np.pi * fk * tt + k) * np.exp(-tt * caida) / k ** 1.4
    ataque = np.minimum(1, tt / 0.004)
    soltar = np.ones_like(tt)
    i = int(dur * SR)
    if i < len(tt):
        soltar[i:] = np.exp(-(tt[i:] - dur) * 9)
    golpe = banda(ruido(0.02), 1500, 6000) * np.exp(-t(0.02) * 300) * 0.15
    x[: len(golpe)] += golpe
    return x * ataque * soltar * vel


def sierra(f, tt, armonicos=14, corte=1600.0):
    x = np.zeros_like(tt)
    for k in range(1, armonicos + 1):
        if f * k > SR / 2.3:
            break
        x += np.sin(2 * np.pi * f * k * tt) / k / (1 + (f * k / corte) ** 2)
    return x


def tuba(m, dur, vel=0.8):
    tt = t(dur + 0.15)
    x = sierra(hz(m), tt, 10, 420)
    env = np.minimum(1, tt / 0.03) * np.minimum(1, np.maximum(0, (dur + 0.15 - tt) / 0.12))
    return np.tanh(x * 1.6) * env * vel


def metal(midis, dur, vel=0.5):
    """acorde de bronces"""
    tt = t(dur + 0.1)
    x = sum(sierra(hz(m), tt * (1 + 0.002 * j), 12, 1800) for j, m in enumerate(midis))
    env = np.minimum(1, tt / 0.04) * np.exp(-tt * 1.5) * np.minimum(1, np.maximum(0, (dur + 0.1 - tt) / 0.08))
    return x * env * vel / max(1, len(midis))


def organillo(m, dur, vel=0.4):
    tt = t(dur)
    f = hz(m)
    x = np.sign(np.sin(2 * np.pi * f * tt)) * 0.5 + np.sin(2 * np.pi * 2 * f * tt) * 0.3
    x = banda(x, 0, 3500)
    return x * np.minimum(1, tt / 0.01) * np.minimum(1, np.maximum(0, (dur - tt) / 0.03)) * vel


def pizz(m, dur=0.5, vel=0.7):
    """cuerda pellizcada (Karplus-Strong)"""
    n = int(SR * dur)
    p = int(SR / hz(m))
    buf = rng.uniform(-1, 1, p).astype(np.float32)
    out = np.zeros(n, np.float32)
    for i in range(n):
        v = buf[i % p]
        out[i] = v
        buf[i % p] = 0.5 * (v + buf[(i + 1) % p]) * 0.994
    return banda(out, 60, 4000) * vel


def chelo(m, dur, vel=0.55):
    tt = t(dur + 0.3)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * tt) * np.minimum(1, tt / 0.6)
    f = hz(m) * vib
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * fase) / k / (1 + (hz(m) * k / 900) ** 2) for k in range(1, 12))
    arco = banda(ruido(dur + 0.3), 500, 4000) * 0.02
    env = np.minimum(1, tt / 0.25) * np.minimum(1, np.maximum(0, (dur + 0.3 - tt) / 0.35))
    return (x + arco) * env * vel


def caja_redoble(dur=0.12, vel=0.3):
    return banda(ruido(dur), 1500, 7000) * np.exp(-t(dur) * 30) * vel


def bombo_marcha(vel=0.6):
    tt = t(0.35)
    return np.sin(2 * np.pi * np.cumsum(60 + 60 * np.exp(-tt * 25)) / SR) * np.exp(-tt * 9) * vel


def platillo(vel=0.2):
    return banda(ruido(0.5), 5000, None) * np.exp(-t(0.5) * 7) * vel


# ============================================================ piezas (cada una devuelve un arreglo de `dur` s)

def poner(salida, x, ini):
    i = int(ini * SR)
    if i >= len(salida) or i < 0:
        return
    x = x[: len(salida) - i]
    salida[i:i + len(x)] += x


# Tema de cabaret (Re menor): 8 compases. (pulso, midi, duración en pulsos)
MELODIA = [
    (0, 69, 1), (1, 65, 0.5), (1.5, 62, 0.5), (2, 64, 0.5), (2.5, 65, 0.5), (3, 67, 0.5), (3.5, 69, 0.5),
    (4, 70, 1), (5, 69, 0.5), (5.5, 67, 0.5), (6, 65, 1), (7, 64, 1),
    (8, 67, 1), (9, 70, 0.5), (9.5, 69, 0.5), (10, 67, 0.5), (10.5, 65, 0.5), (11, 64, 1),
    (12, 61, 1), (13, 64, 0.5), (13.5, 67, 0.5), (14, 69, 2),
    (16, 74, 1), (17, 72, 0.5), (17.5, 69, 0.5), (18, 65, 1), (19, 62, 1),
    (20, 70, 1), (21, 68, 0.5), (21.5, 65, 0.5), (22, 62, 1), (23, 65, 1),
    (24, 64, 0.5), (24.5, 65, 0.5), (25, 67, 0.5), (25.5, 69, 0.5), (26, 67, 1), (27, 61, 1),
    (28, 62, 3),
]
ACORDES = [(38, [62, 65, 69]), (38, [62, 65, 69]), (43, [62, 67, 70]), (45, [61, 64, 67]),
           (38, [62, 65, 69]), (46, [62, 65, 68]), (45, [61, 64, 67]), (38, [62, 65, 69])]


def cabaret(dur, bpm=112, swing=True, transp=0, vel=1.0, melodia=True, sobrio=False):
    out = np.zeros(int(SR * dur), np.float32)
    beat = 60 / bpm
    ciclo = 8 * 4 * beat
    def tiempo(p):
        entero = np.floor(p)
        frac = p - entero
        if swing and abs(frac - 0.5) < 1e-6:
            frac = 2 / 3
        return (entero + frac) * beat
    k = 0
    while k * ciclo < dur:
        base = k * ciclo
        for c, (raiz, acorde) in enumerate(ACORDES):
            t0 = base + c * 4 * beat
            if sobrio:
                poner(out, piano(raiz + transp, beat * 3.6, 0.45 * vel), t0)
                poner(out, sum(piano(m + transp, beat * 3.6, 0.22 * vel) for m in acorde), t0 + beat * 0.02)
                continue
            # stride: bajo en 1 y 3, acorde en 2 y 4
            poner(out, piano(raiz + transp, beat * 0.9, 0.55 * vel), t0)
            poner(out, piano(raiz + 7 + transp - 12, beat * 0.9, 0.45 * vel), t0 + 2 * beat)
            for b in (1, 3):
                poner(out, sum(piano(m + transp, beat * 0.5, 0.2 * vel) for m in acorde), t0 + b * beat)
        if melodia:
            for p, m, d in MELODIA:
                poner(out, piano(m + 12 + transp, d * beat * 0.95, 0.42 * vel), base + tiempo(p))
        k += 1
    return out


def circo(dur, bpm=150, vel=1.0):
    """parodia de circo (original): bajo de tuba en 1, acordes de organillo en 2, carrera cromática arriba"""
    out = np.zeros(int(SR * dur), np.float32)
    beat = 60 / bpm
    prog = [(36, [60, 64, 67]), (43, [59, 62, 67]), (36, [60, 64, 67]), (41, [60, 65, 69]),
            (36, [60, 64, 67]), (43, [59, 65, 67]), (43, [59, 62, 67]), (36, [60, 64, 67])]
    linea = [67, 66, 67, 68, 69, 70, 71, 72, 71, 70, 69, 68, 67, 64, 67, 72]
    n = 0
    while n * beat < dur:
        raiz, acorde = prog[(n // 4) % len(prog)]
        if n % 2 == 0:
            poner(out, tuba(raiz, beat * 0.8, 0.6 * vel), n * beat)
        else:
            poner(out, sum(organillo(m, beat * 0.45, 0.18 * vel) for m in acorde), n * beat)
        poner(out, organillo(linea[(n * 2) % len(linea)] + 12, beat * 0.45, 0.25 * vel), n * beat)
        poner(out, organillo(linea[(n * 2 + 1) % len(linea)] + 12, beat * 0.45, 0.25 * vel), n * beat + beat / 2)
        if n % 8 == 7:
            poner(out, platillo(0.25 * vel), n * beat)
        n += 1
    return out


def marcha(dur, bpm=96, vel=1.0):
    """marcha pomposa con tuba (Si bemol mayor)"""
    out = np.zeros(int(SR * dur), np.float32)
    beat = 60 / bpm
    prog = [(34, [58, 62, 65]), (41, [57, 60, 65]), (34, [58, 62, 65]), (39, [58, 63, 67]),
            (34, [58, 62, 65]), (41, [57, 60, 63]), (41, [57, 60, 65]), (34, [58, 62, 65])]
    melo = [70, 70, 72, 74, 75, 74, 72, 70, 69, 70, 72, 69, 70, 74, 72, 70]
    n = 0
    while n * beat < dur:
        raiz, acorde = prog[(n // 4) % len(prog)]
        if n % 2 == 0:
            poner(out, tuba(raiz if n % 4 == 0 else raiz + 7, beat * 0.85, 0.7 * vel), n * beat)
            poner(out, bombo_marcha(0.35 * vel), n * beat)
        else:
            poner(out, metal(acorde, beat * 0.5, 0.55 * vel), n * beat)
        poner(out, caja_redoble(0.1, 0.12 * vel), n * beat + beat / 2)
        if n % 2 == 0:
            poner(out, metal([melo[(n // 2) % len(melo)] + 12], beat * 1.8, 0.35 * vel), n * beat)
        n += 1
    return out


def pizzicato(dur, bpm=118, vel=1.0):
    """cuerdas pellizcadas, conspirativas y juguetonas (La menor)"""
    out = np.zeros(int(SR * dur), np.float32)
    beat = 60 / bpm
    linea = [69, 72, 76, 72, 74, 71, 68, 71, 69, 72, 76, 79, 77, 74, 71, 68]
    bajos = [45, 45, 40, 40, 45, 45, 44, 40]
    cache = {}
    def nota(m, d, v):
        clave = (m, round(d, 3))
        if clave not in cache:
            cache[clave] = pizz(m, d, 1.0)
        return cache[clave] * v
    n = 0
    while n * beat / 2 < dur:
        ini = n * beat / 2
        if n % 2 == 0 or (n % 8) in (3, 7):
            poner(out, nota(linea[n % len(linea)], 0.45, 0.32 * vel), ini)
        if n % 4 == 0:
            poner(out, nota(bajos[(n // 4) % len(bajos)], 0.8, 0.45 * vel), ini)
        n += 1
    return out


def zumbido(dur, vel=1.0):
    tt = t(dur)
    x = (np.sin(2 * np.pi * 55 * tt) * 0.6 + np.sin(2 * np.pi * 82.4 * tt) * 0.25 + np.sin(2 * np.pi * 110.6 * tt) * 0.15)
    textura = banda(ruido(dur), 40, 220) * 0.4
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * tt)
    return (x + textura) * lfo * np.minimum(1, np.minimum(tt / 2.0, (dur - tt) / 1.5)) * vel


def chelo_solo(dur, vel=1.0):
    """frase lenta de violonchelo (Re menor) que se repite si hace falta"""
    out = np.zeros(int(SR * dur), np.float32)
    frase = [(50, 2.0), (53, 1.5), (52, 1.5), (50, 2.5), (45, 2.0), (48, 1.5), (46, 1.5), (45, 3.0)]
    pos = 0.0
    while pos < dur:
        for m, d in frase:
            if pos >= dur:
                break
            poner(out, chelo(m, min(d, dur - pos) * 0.98, 0.5 * vel), pos)
            pos += d
    fin = int(min(len(out), SR * 1.2))
    out[-fin:] *= np.linspace(1, 0, fin)
    return out


def final_piano(dur, vel=1.0):
    """el tema de la apertura, lento y a piano solo, hasta el último acorde"""
    x = cabaret(dur, bpm=66, swing=False, vel=vel)
    acorde = sum(piano(m, 3.5, 0.35) for m in (38, 50, 62, 65, 69, 74))
    out = x
    poner(out, acorde, max(0, dur - 3.8))
    fade = np.ones_like(out)
    k = int(SR * 4.0)
    fade[-k - int(SR * 3.8):-k] = np.linspace(1, 0.0, int(SR * 3.8))
    fade[-k:] = 0
    out = out * fade
    poner(out, acorde, max(0, dur - 3.8))
    return out


# ============================================================ efectos

def jarras():
    tt = t(1.0)
    choque = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, d in ((1860, 18), (2710, 22), (3920, 30))) * 0.5
    espuma = banda(ruido(1.0), 2500, 9000) * np.exp(-tt * 3) * np.minimum(1, tt / 0.05) * 0.25
    return choque + espuma


def disparo_yeso():
    tt = t(2.0)
    golpe = banda(ruido(2.0), 60, 900) * np.exp(-tt * 18) * 1.4
    cuerpo = np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 12)
    yeso = np.zeros_like(tt)
    for _ in range(80):
        i = int(rng.uniform(0.25, 1.6) * SR)
        m = int(0.01 * SR)
        yeso[i:i + m] += rng.standard_normal(m).astype(np.float32) * np.exp(-np.arange(m) / (SR * 0.002)) * rng.uniform(0.05, 0.25)
    return np.tanh(golpe + cuerpo) + banda(yeso, 800, 7000)


def abucheos():
    n = int(SR * 2.2)
    out = np.zeros(n, np.float32)
    tt = t(2.2)
    for _ in range(14):
        f0 = rng.uniform(110, 220)
        f = f0 * (1 - 0.15 * tt / 2.2) * (1 + 0.01 * np.sin(2 * np.pi * rng.uniform(4, 7) * tt))
        fase = 2 * np.pi * np.cumsum(f) / SR
        voz = sum(np.sin(k * fase) / k for k in range(1, 8))
        out += voz * rng.uniform(0.4, 1)
    out = banda(out, 150, 1500)
    return out * np.minimum(1, np.minimum(tt / 0.2, (2.2 - tt) / 0.5))


def grillos():
    n = int(SR * 3.0)
    out = np.zeros(n, np.float32)
    tt = t(3.0)
    for j, f in enumerate((4300, 4700)):
        tren = (np.sin(2 * np.pi * 30 * tt) > 0) * ((tt * 2.2 + j * 0.3) % 1 < 0.35)
        out += np.sin(2 * np.pi * f * tt) * tren * 0.5
    return out * np.minimum(1, np.minimum(tt / 0.2, (3.0 - tt) / 0.4))


def disco_rayado():
    tt = t(0.6)
    f = 900 + 1800 * np.abs(np.sin(2 * np.pi * 3.2 * tt))
    fase = 2 * np.pi * np.cumsum(f) / SR
    return (banda(ruido(0.6), 400, 5000) * 0.6 + np.sin(fase) * 0.3) * np.exp(-tt * 2)


def fuego():
    n = int(SR * 3.0)
    tt = t(3.0)
    base = banda(ruido(3.0), 100, 900) * 0.4
    chasq = np.zeros(n, np.float32)
    for _ in range(120):
        i = int(rng.uniform(0, 2.95) * SR)
        m = int(0.004 * SR)
        chasq[i:i + m] += rng.standard_normal(m).astype(np.float32) * rng.uniform(0.1, 0.6)
    return (base + banda(chasq, 1500, 9000)) * np.minimum(1, np.minimum(tt / 0.3, (3.0 - tt) / 0.5))


def mazo():
    tt = t(0.9)
    madera = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, d in ((420, 14), (980, 20), (1650, 28)))
    golpe = banda(ruido(0.9), 200, 3000) * np.exp(-tt * 60)
    sala = banda(ruido(0.9), 150, 2000) * np.exp(-tt * 5) * 0.12
    return madera * 0.6 + golpe + sala


def sobres():
    n = int(SR * 1.6)
    out = np.zeros(n, np.float32)
    for _ in range(26):
        i = int(rng.uniform(0, 1.45) * SR)
        m = int(0.06 * SR)
        out[i:i + m] += banda(rng.standard_normal(m).astype(np.float32), 1200, 6000) * np.hanning(m) * rng.uniform(0.2, 0.7)
    return out


def corcho():
    tt = t(0.3)
    return np.sin(2 * np.pi * np.cumsum(900 - 500 * tt) / SR) * np.exp(-tt * 25)


def chillido():
    """tres chillidos agudos de ratón"""
    out = np.zeros(int(SR * 0.9), np.float32)
    for k, ini in enumerate((0.0, 0.26, 0.5)):
        tt = t(0.18)
        f = 3200 + 900 * np.sin(np.pi * tt / 0.18) + 120 * np.sin(2 * np.pi * 38 * tt) + k * 150
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.18) ** 0.6
        poner(out, x * 0.8, ini)
    return out


def acorde():
    """acorde de piano de cabaret (re menor con sexta), un golpe"""
    out = np.zeros(int(SR * 2.4), np.float32)
    for m in (38, 50, 57, 62, 65, 71):
        poner(out, piano(m, 1.0, 0.85), 0.0)
    return out


def brindis():
    """copas de champán que chocan"""
    tt = t(1.6)
    return sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) * a for f, d, a in ((3120, 3.5, 0.5), (4680, 5, 0.35), (6210, 7, 0.25), (3150, 3.6, 0.4))) * np.minimum(1, tt / 0.002)


def crack():
    """madera que se parte"""
    tt = t(0.7)
    golpe = banda(ruido(0.7), 300, 5000) * np.exp(-tt * 40)
    astillas = np.zeros_like(tt)
    for _ in range(30):
        i = int(rng.uniform(0.0, 0.25) * SR)
        m = int(0.003 * SR)
        astillas[i:i + m] += rng.standard_normal(m).astype(np.float32) * rng.uniform(0.2, 0.8)
    cuerpo = np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 25) * 0.6
    return golpe + banda(astillas, 1200, 9000) + cuerpo


def silbido():
    """silbido alegre y despreocupado (una frase corta)"""
    notas = [(79, 0.18), (83, 0.18), (86, 0.3), (84, 0.18), (83, 0.18), (79, 0.45)]
    out = np.zeros(int(SR * 1.8), np.float32)
    pos = 0.0
    for m, d in notas:
        tt = t(d)
        f = hz(m) * (1 + 0.012 * np.sin(2 * np.pi * 6 * tt))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, np.minimum(tt / 0.02, (d - tt) / 0.04))
        x += banda(ruido(d), 1500, 4000) * 0.04
        poner(out, x * 0.6, pos)
        pos += d
    return out


def palmada():
    """palmada seca en la frente"""
    tt = t(0.4)
    return banda(ruido(0.4), 250, 3500) * np.exp(-tt * 45) + np.sin(2 * np.pi * 160 * tt) * np.exp(-tt * 30) * 0.4


def vapor():
    """silbido de vapor (tetera) que sale de las orejas"""
    tt = t(1.4)
    silbo = np.sin(2 * np.pi * np.cumsum(2400 + 300 * tt) / SR) * 0.25
    soplo = banda(ruido(1.4), 2500, 9000) * 0.5
    return (silbo + soplo) * np.minimum(1, np.minimum(tt / 0.08, (1.4 - tt) / 0.3))


def desinfla():
    """globo que se desinfla chillando"""
    tt = t(1.2)
    f = 700 * np.exp(-tt * 1.3) + 180 + 60 * np.sin(2 * np.pi * 18 * tt)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 + banda(ruido(1.2), 400, 3000) * 0.2
    return banda(x, 150, 4000) * np.minimum(1, np.minimum(tt / 0.02, (1.2 - tt) / 0.2))


def ronquido():
    """ronquido suave (inspirar y soltar)"""
    tt = t(2.4)
    env = np.clip(np.sin(np.pi * tt / 1.2), 0, 1) ** 2
    f = 70 + 15 * np.sin(np.pi * tt / 1.2)
    vibra = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 + np.sin(2 * np.pi * 28 * tt)) * 0.5
    return banda(vibra + ruido(2.4) * 0.15, 60, 900) * env


def ticket():
    """rollo de papel que se desenrolla con trinquete"""
    n = int(SR * 1.6)
    out = np.zeros(n, np.float32)
    for k in range(40):
        i = int((0.02 + k * 0.035 * (1 + k / 80)) * SR)
        m = int(0.006 * SR)
        if i + m < n:
            out[i:i + m] += rng.standard_normal(m).astype(np.float32) * np.exp(-np.arange(m) / (SR * 0.0015))
    return banda(out, 1500, 8000) + banda(ruido(1.6), 3000, 8000) * 0.04


def pasos():
    """botas marchando sobre adoquines"""
    n = int(SR * 2.4)
    out = np.zeros(n, np.float32)
    for k in range(12):
        ini = k * 0.2 + rng.uniform(-0.01, 0.01)
        tt = t(0.12)
        golpe = banda(ruido(0.12), 80, 1600) * np.exp(-tt * 45) + np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 40) * 0.5
        poner(out, golpe * (0.8 if k % 2 else 1.0), ini)
    return out


def proyector():
    """traqueteo de proyector de cine mudo"""
    tt = t(2.5)
    clac = (np.sin(2 * np.pi * 18 * tt) > 0.85).astype(np.float32)
    x = banda(ruido(2.5) * clac, 800, 5000) * 0.6 + banda(ruido(2.5), 200, 1200) * 0.08
    return x * np.minimum(1, np.minimum(tt / 0.1, (2.5 - tt) / 0.3))


def flash():
    """estallido de flash de magnesio"""
    tt = t(0.8)
    return banda(ruido(0.8), 300, 7000) * np.exp(-tt * 12) + np.sin(2 * np.pi * 110 * tt) * np.exp(-tt * 20) * 0.4


def tintineo():
    """tintineo metálico (medallas, aureola)"""
    out = np.zeros(int(SR * 1.2), np.float32)
    for k in range(6):
        tt = t(0.6)
        f = rng.uniform(2600, 5200)
        poner(out, np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) * rng.uniform(0.3, 0.6), k * 0.07 + rng.uniform(0, 0.03))
    return out


def rasga():
    """papel que se rasga"""
    tt = t(0.7)
    grano = (rng.random(len(tt)) < 0.08).astype(np.float32) * rng.standard_normal(len(tt)).astype(np.float32)
    return banda(grano, 1200, 9000) * np.minimum(1, np.minimum(tt / 0.03, (0.7 - tt) / 0.15)) + banda(ruido(0.7), 2000, 7000) * 0.08


def latigo():
    """chasquido de látigo"""
    tt = t(0.5)
    silbo = banda(ruido(0.5), 1500, 6000) * np.exp(-((tt - 0.12) / 0.06) ** 2) * 0.3
    chasq = banda(ruido(0.5), 800, 9000) * np.exp(-np.maximum(0, tt - 0.18) * 80) * (tt > 0.18)
    return silbo + chasq


def ronroneo():
    """ronroneo de gato"""
    tt = t(2.0)
    pulso = (1 + np.sin(2 * np.pi * 26 * tt)) * 0.5
    return banda(ruido(2.0), 40, 400) * pulso * np.minimum(1, np.minimum(tt / 0.2, (2.0 - tt) / 0.3)) * np.where((tt % 1.0) < 0.55, 1.0, 0.6)


def cadena():
    """cadena que cae al suelo"""
    out = np.zeros(int(SR * 1.0), np.float32)
    for k in range(14):
        tt = t(0.25)
        golpe = sum(np.sin(2 * np.pi * f * tt) for f in (1800 + k * 37, 2900 + k * 51, 4300)) * np.exp(-tt * 30) * 0.2
        poner(out, golpe, 0.03 + k * 0.035 + rng.uniform(0, 0.02))
    return out


def rugido():
    """rugido corto (de gatito con ganas de león)"""
    tt = t(1.1)
    f = 110 + 60 * np.sin(np.pi * tt / 1.1)
    voz = sum(np.sin(k * 2 * np.pi * np.cumsum(f) / SR) / k for k in range(1, 10))
    aspereza = banda(ruido(1.1), 200, 2500) * 0.5
    return banda(np.tanh(2 * voz) + aspereza, 80, 3000) * np.sin(np.pi * tt / 1.1) ** 0.7


def cremallera():
    """cremallera que se cierra"""
    tt = t(0.6)
    dientes = (np.sin(2 * np.pi * np.cumsum(120 + 500 * tt) / SR) > 0.9).astype(np.float32)
    return banda(ruido(0.6) * dientes, 1500, 8000) * np.minimum(1, (0.6 - tt) / 0.05)


def estornudo():
    """¡achú! exagerado"""
    out = np.zeros(int(SR * 1.3), np.float32)
    tt = t(0.5)
    aaa = banda(ruido(0.5), 300, 2500) * np.sin(np.pi * tt / 0.5) * 0.3 + np.sin(2 * np.pi * np.cumsum(220 + 120 * tt) / SR) * np.sin(np.pi * tt / 0.5) * 0.25
    poner(out, aaa, 0.0)
    tt2 = t(0.5)
    chu = banda(ruido(0.5), 1500, 9000) * np.exp(-tt2 * 8) * 1.2
    poner(out, chu, 0.55)
    return out


def cohete():
    """despegue de cohete con silbido"""
    tt = t(1.8)
    rugir = banda(ruido(1.8), 60, 1200) * np.minimum(1, tt / 0.2)
    silbo = np.sin(2 * np.pi * np.cumsum(600 + 1400 * tt) / SR) * 0.25
    return (rugir + silbo) * np.minimum(1, (1.8 - tt) / 0.4)


def salpica():
    """sopa que se derrama"""
    tt = t(0.8)
    chap = banda(ruido(0.8), 300, 4000) * np.exp(-tt * 9)
    gotas = np.zeros_like(tt)
    for _ in range(10):
        i = int(rng.uniform(0.15, 0.7) * SR)
        m = int(0.03 * SR)
        g = np.sin(2 * np.pi * rng.uniform(900, 1800) * np.arange(m) / SR) * np.exp(-np.arange(m) / (SR * 0.006))
        gotas[i:i + m] += g * 0.3
    return chap + gotas


def aplasta():
    """golpe sordo de bota que aplasta"""
    tt = t(0.6)
    return np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 9) + banda(ruido(0.6), 60, 700) * np.exp(-tt * 20) * 0.8


def lamida():
    """lengüetazo húmedo"""
    tt = t(0.45)
    return banda(ruido(0.45), 500, 5000) * np.sin(np.pi * tt / 0.45) ** 2 * (1 + 0.5 * np.sin(2 * np.pi * 30 * tt))


# ============================================================ línea de tiempo de la música

def plan_musical(F, total):
    """[(ini, fin, pieza, nivel)] según los tiempos de las frases"""
    def ini(i):
        return F[i]["inicio"]
    def fin(i):
        return F[i]["fin"]
    def cap(c):
        return min(i for i, fr in enumerate(g.GUION) if fr[1] == c)
    b = g.buscar
    disparos = b("Disparos.")
    tramos = [
        (0.0, ini(disparos), "cabaret", 1.0),
        (fin(disparos) + 0.5, fin(b("Mueren dieciséis")) + 0.4, "chelo", 1.0),
        (fin(b("Mueren dieciséis")) + 0.4, ini(cap(3)) - 0.1, "cabaret_rapido", 1.0),
        (ini(cap(3)) - 0.1, ini(cap(4)) - 0.1, "circo", 0.9),
        (ini(cap(4)) - 0.1, ini(b("Ojo: casi catorce")) - 0.2, "cabaret_sobrio", 1.0),
        (ini(b("Ojo: casi catorce")) - 0.2, fin(b("Eso pesa.")) + 0.3, "chelo", 1.0),
        (fin(b("Eso pesa.")) + 0.3, ini(cap(5)) - 0.1, "cabaret_sobrio", 1.0),
        (ini(cap(5)) - 0.1, ini(cap(6)) - 0.1, "marcha", 0.9),
        (ini(cap(6)) - 0.1, ini(b("Según el diario")) - 0.2, "cabaret_sobrio", 0.8),
        (ini(b("Según el diario")) - 0.2, fin(b("Si el partido se rompe")) + 0.4, "chelo", 1.0),
        (fin(b("Si el partido se rompe")) + 0.4, ini(cap(7)) - 0.1, "cabaret_sobrio", 0.8),
        (ini(cap(7)) - 0.1, ini(cap(8)) - 0.1, "pizzicato", 1.0),
        (ini(cap(8)) - 0.1, fin(b("Ni con miedo")), "zumbido", 1.0),
        # Dachau: silencio total (un segundo antes, la frase y un segundo después)
        (ini(b("Al día siguiente, el Parlamento vota")) - 0.05, ini(b("Pueden quitarnos")) - 0.2, "zumbido", 0.8),
        (ini(b("Pueden quitarnos")) - 0.2, fin(b("Pueden quitarnos")) + 0.4, "chelo", 1.0),
        (fin(b("Pueden quitarnos")) + 0.4, ini(cap(9)) - 0.1, "zumbido", 0.9),
        (ini(cap(9)) - 0.1, fin(b("Al secretario y al escritor")) + 0.3, "chelo", 1.0),
        (fin(b("Al secretario y al escritor")) + 0.3, ini(b("El hombre que «no llegaba")) - 0.2, "cabaret_sobrio", 0.8),
        (ini(b("El hombre que «no llegaba")) - 0.2, fin(b("Decenas de millones")) + 0.5, "chelo", 1.0),
        (fin(b("Decenas de millones")) + 0.5, total, "final", 1.0),
    ]
    return tramos


def generar_musica(F, total):
    out = np.zeros(int(SR * total) + SR, np.float32)
    piezas = {
        "cabaret": lambda d: cabaret(d, 112),
        "cabaret_rapido": lambda d: cabaret(d, 124),
        "cabaret_sobrio": lambda d: cabaret(d, 84, swing=False, transp=-12, melodia=False, sobrio=True),
        "circo": lambda d: circo(d),
        "marcha": lambda d: marcha(d),
        "pizzicato": lambda d: pizzicato(d),
        "zumbido": lambda d: zumbido(d),
        "chelo": lambda d: chelo_solo(d),
        "final": lambda d: final_piano(d),
    }
    objetivo = {"cabaret": -18, "cabaret_rapido": -18, "cabaret_sobrio": -20, "circo": -18, "marcha": -18,
                "pizzicato": -18, "zumbido": -21, "chelo": -19, "final": -18}
    for a, b, nombre, nivel in plan_musical(F, total):
        d = max(0.2, b - a)
        x = piezas[nombre](d)[: int(SR * d)]
        rms = float(np.sqrt(np.mean(x ** 2))) or 1e-6
        x = x * (10 ** (objetivo[nombre] / 20) / rms) * nivel
        k = min(len(x) // 4, int(SR * (0.02 if nombre in ("cabaret",) and a > 0 else 0.4)))
        if k > 0:
            x[:k] *= np.linspace(0, 1, k)
            x[-k:] *= np.linspace(1, 0, k)
        poner(out, x, a)
    return out[: int(SR * total)]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", default="")
    args = ap.parse_args()
    os.makedirs("public/sfx", exist_ok=True)
    if args.solo in ("", "efectos"):
        for nombre, x, gan in [("jarras", jarras(), 0.7), ("disparo", disparo_yeso(), 0.9), ("abucheos", abucheos(), 0.6),
                               ("grillos", grillos(), 0.4), ("rayado", disco_rayado(), 0.7), ("fuego", fuego(), 0.6),
                               ("mazo", mazo(), 0.9), ("sobres", sobres(), 0.6), ("corcho", corcho(), 0.6),
                               ("chillido", chillido(), 0.5), ("acorde", acorde(), 0.8), ("brindis", brindis(), 0.6), ("crack", crack(), 0.8),
                               ("silbido", silbido(), 0.5), ("palmada", palmada(), 0.8),
                               ("vapor", vapor(), 0.5), ("desinfla", desinfla(), 0.5), ("ronquido", ronquido(), 0.5), ("ticket", ticket(), 0.6),
                               ("pasos", pasos(), 0.7), ("proyector", proyector(), 0.5), ("flash", flash(), 0.7),
                               ("tintineo", tintineo(), 0.5), ("rasga", rasga(), 0.6), ("latigo", latigo(), 0.7), ("ronroneo", ronroneo(), 0.5),
                               ("cadena", cadena(), 0.6), ("rugido", rugido(), 0.7), ("cremallera", cremallera(), 0.6), ("estornudo", estornudo(), 0.8),
                               ("cohete", cohete(), 0.7), ("salpica", salpica(), 0.6), ("aplasta", aplasta(), 0.9), ("lamida", lamida(), 0.5)]:
            guardar(f"public/sfx/{nombre}.wav", x, gan)
        print("efectos listos", flush=True)
    if args.solo in ("", "musica"):
        datos = json.load(open("public/voz-palabras.json", encoding="utf-8"))
        F = datos["frases"]
        total = datos["duracion"] + 1.5
        musica = generar_musica(F, total)
        pico = float(np.max(np.abs(musica))) or 1.0
        guardar("public/musica.wav", musica * min(1.0, 0.89 / pico), normalizar=False)
        print(f"música lista: {total / 60:.2f} min", flush=True)
