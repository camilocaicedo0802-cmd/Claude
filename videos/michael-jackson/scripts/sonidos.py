"""Sintetiza efectos de sonido y una música de suspenso (todo por código, sin derechos).

Salidas en public/sfx/*.wav y public/musica.wav
Uso: python3 scripts/sonidos.py [--duracion-musica 64]
"""

import argparse
import os
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def guardar(nombre, x, gan=0.9):
    x = np.asarray(x, dtype=np.float64)
    pico = np.max(np.abs(x)) or 1.0
    x = x / pico * gan
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    datos = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(nombre, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(datos.tobytes())


def t(seg):
    return np.arange(int(SR * seg)) / SR


def env(n, ataque, caida):
    a = int(SR * ataque)
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a)
    e[a:] = np.exp(-np.arange(n - a) / (SR * caida))
    return e


def pasabajos(x, corte):
    """Filtro de un polo con corte variable (array o escalar)."""
    corte = np.broadcast_to(corte, x.shape)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        a = 1 - np.exp(-2 * np.pi * corte[i] / SR)
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def pasaaltos(x, corte):
    return x - pasabajos(x, corte)


def whoosh(dur=0.42):
    n = int(SR * dur)
    ruido = rng.standard_normal(n)
    tt = np.linspace(0, 1, n)
    corte = 300 + 5200 * np.sin(np.pi * tt) ** 2
    x = pasabajos(ruido, corte) - pasabajos(ruido, corte * 0.25)
    x *= np.sin(np.pi * tt) ** 1.6
    pan = np.stack([x * (1 - 0.6 * tt), x * (0.4 + 0.6 * tt)], axis=1)
    return pan


def boom(dur=1.6):
    tt = t(dur)
    frec = 70 * np.exp(-tt * 2.2) + 32
    fase = 2 * np.pi * np.cumsum(frec) / SR
    grave = np.sin(fase) * env(len(tt), 0.004, 0.45)
    ruido = pasabajos(rng.standard_normal(len(tt)), 900) * env(len(tt), 0.002, 0.25) * 1.4
    crujido = pasabajos(rng.standard_normal(len(tt)), 3500) * env(len(tt), 0.001, 0.05) * 0.5
    return np.tanh((grave * 1.3 + ruido + crujido) * 1.6)


def pop(dur=0.14):
    tt = t(dur)
    frec = 500 + 900 * tt / dur
    return np.sin(2 * np.pi * np.cumsum(frec) / SR) * env(len(tt), 0.002, 0.035)


def ding(dur=1.2):
    tt = t(dur)
    x = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * d)
            for f, a, d in [(1318.5, 1, 3.2), (2637, 0.45, 5), (3955, 0.2, 7), (1975.5, 0.3, 4)])
    return x * env(len(tt), 0.003, 10)


def golpe_dramatico(dur=1.4):
    """'Dun-dun' grave para la revelación."""
    tt = t(dur)
    salida = np.zeros(len(tt))
    for inicio, f0 in [(0.0, 73.4), (0.32, 69.3)]:
        i = int(SR * inicio)
        tl = tt[: len(tt) - i]
        voces = sum(np.sign(np.sin(2 * np.pi * f * m * tl)) / m
                    for f in (f0, f0 * 1.005, f0 * 2) for m in (1, 2, 3))
        nota = pasabajos(voces, 600 + 900 * np.exp(-tl * 6)) * np.exp(-tl * 2.6)
        timbal = np.sin(2 * np.pi * (f0 / 2) * tl) * np.exp(-tl * 5) * 2
        salida[i:] += nota + timbal
    return np.tanh(salida * 0.9)


def hoja(dur=0.16):
    n = int(SR * dur)
    x = pasaaltos(rng.standard_normal(n), 1200)
    tt = np.linspace(0, 1, n)
    return x * np.sin(np.pi * tt) ** 0.8 * (1 + 0.6 * np.sin(2 * np.pi * 38 * tt * dur))


def sello(dur=0.5):
    tt = t(dur)
    golpe = np.sin(2 * np.pi * (110 * np.exp(-tt * 9) + 55) * tt) * env(len(tt), 0.001, 0.09)
    click = pasabajos(rng.standard_normal(len(tt)), 2500) * env(len(tt), 0.0005, 0.02)
    return golpe * 1.4 + click


def moscas(dur=3.0):
    tt = t(dur)
    salida = np.zeros(len(tt))
    for base, fase in [(205, 0), (232, 1.7)]:
        frec = base + 18 * np.sin(2 * np.pi * 0.9 * tt + fase) + 6 * np.sin(2 * np.pi * 7 * tt)
        diente = 2 * ((np.cumsum(frec) / SR) % 1) - 1
        am = 0.55 + 0.45 * np.sin(2 * np.pi * 0.6 * tt + fase)
        salida += pasabajos(diente, 1800) * am
    return salida * env(len(tt), 0.2, 99)


def pluck(f, dur, brillo=0.5):
    """Cuerda pulsada Karplus-Strong (pizzicato)."""
    n = int(SR * dur)
    periodo = int(SR / f)
    buf = rng.uniform(-1, 1, periodo)
    salida = np.zeros(n)
    for i in range(n):
        salida[i] = buf[i % periodo]
        buf[i % periodo] = brillo * buf[i % periodo] + (1 - brillo) * buf[(i + 1) % periodo]
        buf[i % periodo] *= 0.996
    return salida


def viento(dur=3.0):
    n = int(SR * dur)
    tt = np.linspace(0, 1, n)
    ruido = rng.standard_normal(n)
    corte = 500 + 900 * (0.5 + 0.5 * np.sin(2 * np.pi * tt * 3.3)) + 600 * np.sin(2 * np.pi * tt * 0.7) ** 2
    x = pasabajos(ruido, corte) - pasabajos(ruido, corte * 0.2)
    return x * np.minimum(1, np.minimum(tt / 0.15, (1 - tt) / 0.25))


def beep(dur=0.16):
    tt = t(dur)
    return np.sin(2 * np.pi * 1046 * tt) * env(len(tt), 0.003, 0.08)


def aplausos(dur=2.2):
    n = int(SR * dur)
    salida = np.zeros(n)
    for _ in range(140):
        i = int(rng.uniform(0, n - SR * 0.05))
        m = int(SR * 0.03)
        salida[i:i + m] += pasaaltos(rng.standard_normal(m), 900) * np.exp(-np.arange(m) / (SR * 0.006)) * rng.uniform(0.4, 1)
    tt = np.linspace(0, 1, n)
    return salida * np.minimum(1, np.minimum(tt / 0.1, (1 - tt) / 0.4))


def objeto(dur=0.9):
    """Jingle de "objeto obtenido" (arpegio mayor ascendente)."""
    salida = np.zeros(int(SR * dur))
    for k, m in enumerate([72, 76, 79, 84]):
        f0 = 440 * 2 ** ((m - 69) / 12)
        tt = t(0.4)
        nota = (np.sign(np.sin(2 * np.pi * f0 * tt)) * 0.3 + np.sin(2 * np.pi * f0 * tt)) * np.exp(-tt * 7)
        i = int(SR * 0.09 * k)
        salida[i:i + len(nota)] += nota[: len(salida) - i]
    return salida


def tic(dur=0.05):
    tt = t(dur)
    return np.sin(2 * np.pi * 2600 * tt) * np.exp(-tt * 220)


def trueno(dur=2.4):
    tt = t(dur)
    crack = pasaaltos(rng.standard_normal(len(tt)), 1500) * env(len(tt), 0.001, 0.06) * 1.2
    retumbo = pasabajos(rng.standard_normal(len(tt)), 180) * env(len(tt), 0.05, 0.9) * 6
    return np.tanh(crack + retumbo)


def temblor(dur=1.6):
    tt = t(dur)
    base = pasabajos(rng.standard_normal(len(tt)), 90) * 8
    golpes = np.sin(2 * np.pi * 38 * tt) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 7 * tt)))
    return np.tanh((base + golpes * 0.6) * np.minimum(1, np.minimum(tt / 0.1, (dur - tt) / 0.4)))


def ola(dur=2.6):
    n = int(SR * dur)
    tt = np.linspace(0, 1, n)
    corte = 300 + 4000 * np.sin(np.pi * np.clip(tt * 1.2, 0, 1)) ** 2
    x = pasabajos(rng.standard_normal(n), corte)
    return x * np.sin(np.pi * tt) ** 0.7


def burbujas(dur=1.2):
    salida = np.zeros(int(SR * dur))
    for _ in range(14):
        i = int(rng.uniform(0, len(salida) - SR * 0.08))
        tl = np.arange(int(SR * 0.07)) / SR
        f0 = rng.uniform(500, 1200)
        b = np.sin(2 * np.pi * (f0 + 3000 * tl) * tl) * np.exp(-tl * 50)
        salida[i:i + len(b)] += b * rng.uniform(0.3, 1)
    return salida


def arpa(dur=1.8):
    """Glissando de arpa ascendente (pentatónica)."""
    salida = np.zeros(int(SR * dur))
    notas = [62, 64, 67, 69, 71, 74, 76, 79, 81, 83, 86]
    for k, m in enumerate(notas):
        f0 = 440 * 2 ** ((m - 69) / 12)
        p = pluck(f0, 1.0, brillo=0.6)
        i = int(SR * 0.055 * k)
        j = min(len(salida), i + len(p))
        salida[i:j] += p[: j - i] * 0.7
    return salida


def boing(dur=0.7):
    tt = t(dur)
    frec = 180 + 260 * np.exp(-tt * 5) * (1 + 0.5 * np.sin(2 * np.pi * 14 * tt))
    return np.sin(2 * np.pi * np.cumsum(frec) / SR) * env(len(tt), 0.004, 0.25)


def garabato(dur=0.9):
    n = int(SR * dur)
    tt = np.arange(n) / SR
    rasgos = (np.sin(2 * np.pi * 9 * tt) > 0.2).astype(float)
    x = pasaaltos(rng.standard_normal(n), 2500) * rasgos
    return x * np.minimum(1, np.minimum(tt / 0.03, (dur - tt) / 0.1))


def musica(dur, bpm=112, transporte=0):
    """Pizzicato de intriga en La menor + bajo + tic-tac + colchón grave."""
    corchea = 60 / bpm / 2
    n = int(SR * dur)
    mezcla = np.zeros((n, 2))
    nota = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    patron = [57, 60, 64, 60, 57, 60, 65, 64,   # Am
              55, 59, 62, 59, 56, 59, 64, 62,   # G / E
              53, 57, 60, 57, 53, 57, 62, 60,   # F
              52, 56, 59, 56, 52, 56, 59, 62]   # E
    cache = {}
    paso = 0
    tpos = 0.0
    while tpos < dur:
        m = patron[paso % len(patron)] + 12 + transporte
        if m not in cache:
            cache[m] = pluck(nota(m), 0.5)
        s = cache[m] * (0.9 if paso % 2 == 0 else 0.6)
        i = int(tpos * SR)
        j = min(n, i + len(s))
        pan = 0.35 + 0.3 * ((paso * 3) % 5) / 4
        mezcla[i:j, 0] += s[: j - i] * (1 - pan)
        mezcla[i:j, 1] += s[: j - i] * pan
        # bajo en cada negra
        if paso % 4 == 0:
            raiz = patron[(paso // 8) * 8 % len(patron)] - 12 + transporte
            tb = np.arange(int(SR * corchea * 3.6)) / SR
            b = (np.sin(2 * np.pi * nota(raiz) * tb) + 0.3 * np.sin(4 * np.pi * nota(raiz) * tb))
            b *= np.exp(-tb * 2.2)
            j = min(n, i + len(b))
            mezcla[i:j] += (b[: j - i] * 0.55)[:, None]
        # tic-tac
        if paso % 2 == 1:
            tc = np.arange(int(SR * 0.03)) / SR
            c = np.sin(2 * np.pi * (2400 if paso % 4 == 1 else 1800) * tc) * np.exp(-tc * 260)
            j = min(n, i + len(c))
            mezcla[i:j] += (c[: j - i] * 0.18)[:, None]
        paso += 1
        tpos += corchea
    # colchón grave que respira
    tt = np.arange(n) / SR
    raiz_hz = 55 * 2 ** (transporte / 12)
    colchon = (np.sin(2 * np.pi * raiz_hz * tt) + 0.5 * np.sin(2 * np.pi * raiz_hz * 1.4983 * tt)) * (0.5 + 0.5 * np.sin(2 * np.pi * tt / 8))
    mezcla += (colchon * 0.12)[:, None]
    fade = np.minimum(1, np.minimum(tt / 0.6, (dur - tt) / 1.5)).clip(0, 1)
    return mezcla * fade[:, None]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--duracion-musica", type=float, default=64)
    args = ap.parse_args()
    os.makedirs("public/sfx", exist_ok=True)
    guardar("public/sfx/whoosh.wav", whoosh(), 0.7)
    guardar("public/sfx/boom.wav", boom(), 0.95)
    guardar("public/sfx/pop.wav", pop(), 0.6)
    guardar("public/sfx/ding.wav", ding(), 0.6)
    guardar("public/sfx/dundun.wav", golpe_dramatico(), 0.95)
    guardar("public/sfx/hoja.wav", hoja(), 0.5)
    guardar("public/sfx/sello.wav", sello(), 0.9)
    guardar("public/sfx/moscas.wav", moscas(), 0.35)
    guardar("public/sfx/trueno.wav", trueno(), 0.9)
    guardar("public/sfx/temblor.wav", temblor(), 0.9)
    guardar("public/sfx/ola.wav", ola(), 0.8)
    guardar("public/sfx/burbujas.wav", burbujas(), 0.5)
    guardar("public/sfx/arpa.wav", arpa(), 0.6)
    guardar("public/sfx/viento.wav", viento(), 0.6)
    guardar("public/sfx/beep.wav", beep(), 0.5)
    guardar("public/sfx/aplausos.wav", aplausos(), 0.7)
    guardar("public/sfx/objeto.wav", objeto(), 0.6)
    guardar("public/sfx/tic.wav", tic(), 0.5)
    # mismo estilo que el short anterior pero en Re menor y un poco más rápido
    guardar("public/sfx/boing.wav", boing(), 0.7)
    guardar("public/sfx/garabato.wav", garabato(), 0.5)
    # chisme histórico: pizzicato más rápido y juguetón
    guardar("public/musica.wav", musica(args.duracion_musica, bpm=132, transporte=3), 0.8)
    print("listo")
