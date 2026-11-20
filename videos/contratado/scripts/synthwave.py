"""Música synthwave original (sintetizada por código, sin derechos) y efectos del short del hacker.

Uso: python3 scripts/synthwave.py [--duracion 60]
Escribe public/musica.wav y public/sfx/*.wav nuevos (zumbido de tele, cierre de bolsa, puerta de auto, neón,
notificación, bóveda, murmullo de oficina, tictac, chispas, servidores, caja registradora, puerta, nota, clic, glitch).
"""

import argparse
import os
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(11)


def guardar(nombre, x, gan=0.9):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    pico = np.max(np.abs(x)) or 1.0
    x = x / pico * gan
    datos = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(nombre, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(datos.tobytes())


def t(seg):
    return np.arange(int(SR * seg)) / SR


def banda(x, lo=0.0, hi=None, suave=0.15):
    """filtro pasabanda por FFT con bordes suaves (rápido para señales largas)"""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo > 0:
        m *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** (2 / suave * 0.15))
    if hi:
        m *= 1 / (1 + (f / hi) ** (2 / suave * 0.15))
    return np.fft.irfft(X * m, n=len(x))


def decae(n, ataque, caida):
    a = max(1, int(SR * ataque))
    e = np.exp(-np.arange(n) / (SR * caida))
    e[:a] *= np.linspace(0, 1, a)
    return e


def ruido(seg):
    return rng.standard_normal(int(SR * seg))


def nota_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ música

def sierra(f, tt, armonicos=18, corte=2500.0, desafinado=0.0):
    """sierra limitada en banda; `corte` atenúa los armónicos altos (filtro "analógico" barato)"""
    x = np.zeros_like(tt)
    for k in range(1, armonicos + 1):
        fk = f * k * (1 + desafinado)
        if fk > SR / 2.2:
            break
        x += np.sin(2 * np.pi * fk * tt) / k / (1 + (fk / corte) ** 2)
    return x


def cuadrada(f, tt, armonicos=9, corte=3000.0):
    x = np.zeros_like(tt)
    for k in range(1, armonicos * 2, 2):
        fk = f * k
        if fk > SR / 2.2:
            break
        x += np.sin(2 * np.pi * fk * tt) / k / (1 + (fk / corte) ** 2)
    return x


def bombo(dur=0.4):
    tt = t(dur)
    f = 45 + 95 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * decae(len(tt), 0.001, 0.16) * 1.2


def caja_bateria(dur=0.45):
    tt = t(dur)
    golpe = np.sin(2 * np.pi * 190 * tt) * decae(len(tt), 0.001, 0.05)
    cola = banda(ruido(dur), 900, 8000) * decae(len(tt), 0.001, 0.16)
    cola[int(0.28 * SR):] *= np.linspace(1, 0, len(cola) - int(0.28 * SR)) ** 3  # reverb "cortada" de los 80
    return golpe * 0.6 + cola * 0.9


def platillo(dur=0.06, abierto=False):
    d = 0.22 if abierto else dur
    return banda(ruido(d), 6000, None) * decae(int(SR * d), 0.0005, 0.08 if abierto else 0.015)


def synthwave(dur, bpm=100):
    n = int(SR * dur)
    izq, der = np.zeros(n), np.zeros(n)
    beat = 60 / bpm
    compas = 4 * beat
    # La menor: Am – F – C – G (un compás cada acorde)
    acordes = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]
    pump = np.ones(n)
    def suma(x, ini, gan=1.0, pan=0.0):
        i = int(ini * SR)
        if i >= n:
            return
        x = x[: n - i]
        izq[i:i + len(x)] += x * gan * (1 - pan)
        der[i:i + len(x)] += x * gan * (1 + pan)
    compases = int(np.ceil(dur / compas))
    for c in range(compases):
        raiz, triada = acordes[c % 4]
        t0 = c * compas
        intro = c < 2  # los dos primeros compases sin batería completa
        # pad: sierras desafinadas, ataque lento
        tt = t(compas + 0.3)
        pad = sum(sierra(nota_hz(m + 12), tt, 10, 1400, d) for m in triada for d in (-0.004, 0.004))
        env = np.minimum(1, tt / 0.35) * np.minimum(1, (compas + 0.3 - tt) / 0.3)
        suma(pad * env, t0, 0.05, -0.2)
        suma(pad * env, t0, 0.05, 0.2)
        # bajo: corcheas en la raíz con salto de octava
        for k in range(8):
            m = raiz - 24 + (12 if k % 4 == 3 else 0)
            tb = t(beat / 2)
            b = sierra(nota_hz(m), tb, 16, 700) * decae(len(tb), 0.004, 0.16)
            suma(b, t0 + k * beat / 2, 0.32)
        # arpegio en semicorcheas con eco
        patron = [0, 1, 2, 1, 0, 2, 1, 2] * 2
        for k in range(16):
            m = triada[patron[k]] + 12 + (12 if k in (6, 14) else 0)
            ta = t(beat / 4 * 1.6)
            a = cuadrada(nota_hz(m), ta, 7, 3600) * decae(len(ta), 0.002, 0.09)
            ini = t0 + k * beat / 4
            suma(a, ini, 0.09, 0.35 if k % 2 else -0.35)
            suma(a, ini + beat * 0.75, 0.035, -0.35 if k % 2 else 0.35)
        if intro:
            continue
        # batería: bombo en 1 y 3 (y en el 4 "y" cada dos compases), caja en 2 y 4, platillos en corcheas
        for k in (0, 2):
            suma(bombo(), t0 + k * beat, 0.9)
            i = int((t0 + k * beat) * SR)
            j = min(n, i + int(0.28 * SR))
            if j > i:
                pump[i:j] = np.minimum(pump[i:j], 0.45 + 0.55 * np.linspace(0, 1, j - i) ** 0.6)
        if c % 2:
            suma(bombo(), t0 + 3.5 * beat, 0.7)
        for k in (1, 3):
            suma(caja_bateria(), t0 + k * beat, 0.55)
        for k in range(8):
            suma(platillo(abierto=(k % 4 == 2)), t0 + k * beat / 2, 0.18 if k % 2 else 0.1, 0.3)
    # bombeo (sidechain) en todo menos la batería: se aplica al conjunto de forma suave
    izq *= 0.75 + 0.25 * pump
    der *= 0.75 + 0.25 * pump
    fade = np.minimum(1, np.arange(n) / (SR * 1.5)) * np.minimum(1, (n - np.arange(n)) / (SR * 2.0))
    return np.stack([izq * fade, der * fade], axis=1)


# ------------------------------------------------------------------ efectos

def zumbido_tele(dur=3.0):
    tt = t(dur)
    hum = sum(np.sin(2 * np.pi * 60 * k * tt) / k ** 1.3 for k in range(1, 7))
    silbido = banda(ruido(dur), 2000, 9000) * 0.12
    return (hum * 0.5 + silbido) * np.minimum(1, np.minimum(tt / 0.3, (dur - tt) / 0.6))


def cierre_bolsa(dur=0.7):
    n = int(SR * dur)
    x = np.zeros(n)
    tiempo, paso = 0.0, 0.016
    while tiempo < dur - 0.02:
        i = int(tiempo * SR)
        m = int(0.004 * SR)
        x[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (SR * 0.0012))
        tiempo += paso
        paso = max(0.006, paso * 0.95)
    return banda(x, 1500, 7000)


def puerta_auto(dur=0.8):
    tt = t(dur)
    golpe = np.sin(2 * np.pi * (75 - 20 * tt) * tt) * decae(len(tt), 0.001, 0.09)
    cuerpo = banda(ruido(dur), 80, 900) * decae(len(tt), 0.001, 0.07)
    pestillo = np.zeros(len(tt))
    i = int(0.05 * SR)
    m = int(0.012 * SR)
    pestillo[i:i + m] = banda(rng.standard_normal(m), 2500, 6000) * np.exp(-np.arange(m) / (SR * 0.003))
    return golpe * 1.2 + cuerpo * 0.8 + pestillo * 0.6


def neon(dur=2.0):
    tt = t(dur)
    zumbido = sum(np.sign(np.sin(2 * np.pi * 120 * k * tt)) / k ** 1.6 for k in (1, 2, 3))
    zumbido = banda(zumbido, 80, 1800)
    parpadeo = (rng.random(int(dur * 30)) > 0.12).astype(float)
    parpadeo = np.repeat(parpadeo, int(SR / 30))[: len(tt)]
    parpadeo = np.pad(parpadeo, (0, len(tt) - len(parpadeo)), constant_values=1)
    return zumbido * parpadeo * np.minimum(1, np.minimum(tt / 0.05, (dur - tt) / 0.3))


def notificacion(dur=0.7):
    tt = t(dur)
    x = np.zeros(len(tt))
    for ini, f in ((0.0, 988), (0.11, 1480)):
        i = int(ini * SR)
        u = tt[: len(tt) - i]
        x[i:] += (np.sin(2 * np.pi * f * u) + 0.25 * np.sin(2 * np.pi * 2 * f * u)) * np.exp(-u * 9)
    return x


def boveda(dur=1.8):
    tt = t(dur)
    boom = np.sin(2 * np.pi * np.cumsum(38 + 50 * np.exp(-tt * 9)) / SR) * decae(len(tt), 0.002, 0.45)
    metal = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, d in ((410, 5), (697, 6), (1130, 8), (1720, 10)))
    rumor = banda(ruido(dur), 30, 300) * decae(len(tt), 0.01, 0.5)
    return np.tanh(boom * 1.4 + metal * 0.18 + rumor * 0.6)


def murmullo(dur=3.0):
    n = int(SR * dur)
    x = np.zeros(n)
    for _ in range(9):
        silabas = (rng.random(int(dur * 9)) > 0.35).astype(float) * rng.uniform(0.4, 1)
        env = np.repeat(silabas, int(SR / 9) + 1)[:n]
        env = np.convolve(env, np.ones(1200) / 1200, "same")
        x += rng.standard_normal(n) * env
    voz = banda(x, 250, 2600)
    return voz * np.minimum(1, np.minimum(np.arange(n) / (SR * 0.3), (n - np.arange(n)) / (SR * 0.2)))


def tictac(dur=4.0):
    n = int(SR * dur)
    x = np.zeros(n)
    for k in range(int(dur * 2)):
        i = int(k * 0.5 * SR)
        m = int(0.03 * SR)
        u = np.arange(m) / SR
        f = 2600 if k % 2 == 0 else 1900
        x[i:i + m] += np.sin(2 * np.pi * f * u) * np.exp(-u * 260)
    return x


def chispas(dur=1.2):
    n = int(SR * dur)
    x = np.zeros(n)
    for _ in range(26):
        i = int(rng.uniform(0, dur - 0.03) * SR)
        m = int(rng.uniform(0.003, 0.02) * SR)
        x[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (SR * 0.003)) * rng.uniform(0.3, 1)
    tt = t(0.09)
    for ini in (0.15, 0.7):
        i = int(ini * SR)
        z = np.sign(np.sin(2 * np.pi * 150 * tt)) * 0.25 * np.exp(-tt * 25)
        x[i:i + len(z)] += z
    return banda(x, 400, 12000)


def servidores(dur=3.0):
    n = int(SR * dur)
    marron = np.cumsum(rng.standard_normal(n))
    marron = banda(marron - np.mean(marron), 40, 900)
    marron /= np.max(np.abs(marron))
    tt = t(dur)
    zumbido = np.sin(2 * np.pi * 120 * tt) * 0.25 + np.sin(2 * np.pi * 3150 * tt) * 0.02
    return (marron * 0.8 + zumbido) * (1 + 0.1 * np.sin(2 * np.pi * 0.7 * tt)) * np.minimum(1, np.minimum(tt / 0.3, (dur - tt) / 0.5))


def caja_registradora(dur=1.3):
    tt = t(dur)
    cajon = banda(ruido(0.25), 300, 3000) * np.linspace(0.3, 1, int(0.25 * SR)) * 0.5
    x = np.zeros(len(tt))
    x[: len(cajon)] += cajon
    i = int(0.2 * SR)
    u = tt[: len(tt) - i]
    campana = sum(np.sin(2 * np.pi * f * u) * np.exp(-u * d) * g for f, d, g in ((2093, 3.5, 1), (2637, 4, 0.7), (3136, 5, 0.5), (4186, 6, 0.35)))
    x[i:] += campana * 0.6
    golpe = np.sin(2 * np.pi * 90 * tt) * decae(len(tt), 0.001, 0.05)
    x[i:] += golpe[: len(tt) - i] * 0.5
    return x


def puerta_pesada(dur=1.6):
    tt = t(dur)
    golpe = np.sin(2 * np.pi * np.cumsum(55 + 30 * np.exp(-tt * 20)) / SR) * decae(len(tt), 0.001, 0.14)
    madera = np.sin(2 * np.pi * 210 * tt) * decae(len(tt), 0.001, 0.05) * 0.4
    cola = banda(ruido(dur), 60, 1200) * decae(len(tt), 0.01, 0.35) * 0.35
    pestillo = np.zeros(len(tt))
    i = int(0.12 * SR)
    m = int(0.015 * SR)
    pestillo[i:i + m] = banda(rng.standard_normal(m), 2000, 7000) * np.exp(-np.arange(m) / (SR * 0.004))
    return golpe * 1.3 + madera + cola + pestillo * 0.5


def nota_sostenida(dur=4.5):
    tt = t(dur)
    x = sum(np.sin(2 * np.pi * f * tt) * g + np.sin(2 * np.pi * f * 1.003 * tt) * g * 0.6 for f, g in ((110, 0.5), (220, 1), (329.6, 0.5), (440, 0.35)))
    return x * np.minimum(1, tt / 0.6) * np.minimum(1, (dur - tt) / 1.4)


def clic_apagado(dur=0.7):
    tt = t(dur)
    x = np.zeros(len(tt))
    m = int(0.006 * SR)
    x[:m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (SR * 0.001)) * 1.2
    f = 2400 * np.exp(-tt * 9) + 120
    x += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7) * 0.35
    return x


def glitch(dur=0.35):
    n = int(SR * dur)
    x = np.zeros(n)
    pos = 0
    while pos < n:
        m = int(rng.uniform(0.012, 0.05) * SR)
        u = np.arange(min(m, n - pos)) / SR
        f = rng.choice([220, 440, 880, 1320, 1760, 2640])
        trozo = np.sign(np.sin(2 * np.pi * f * u)) * 0.5 if rng.random() > 0.4 else rng.standard_normal(len(u))
        x[pos:pos + len(u)] = np.round(trozo * 6) / 6 * rng.uniform(0.3, 1)
        pos += m
    return x * np.minimum(1, (n - np.arange(n)) / (SR * 0.05))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--duracion", type=float, default=60)
    args = ap.parse_args()
    os.makedirs("public/sfx", exist_ok=True)
    for nombre, x, g in [
        ("zumbido", zumbido_tele(), 0.5), ("cierre", cierre_bolsa(), 0.6), ("puertaauto", puerta_auto(), 0.8),
        ("neon", neon(), 0.5), ("notif", notificacion(), 0.6), ("boveda", boveda(), 0.95), ("murmullo", murmullo(), 0.55),
        ("tictac", tictac(), 0.6), ("chispas", chispas(), 0.7), ("servidores", servidores(), 0.55),
        ("caja", caja_registradora(), 0.8), ("puerta", puerta_pesada(), 0.9), ("nota", nota_sostenida(), 0.6),
        ("clic", clic_apagado(), 0.7), ("glitch", glitch(), 0.5),
    ]:
        guardar(f"public/sfx/{nombre}.wav", x, g)
    guardar("public/musica.wav", synthwave(args.duracion), 0.85)
    print("listo")
