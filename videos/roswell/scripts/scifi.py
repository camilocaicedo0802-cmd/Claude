"""Música y efectos del short de Roswell (todo sintetizado, libre de derechos).

Música: ciencia ficción de los años 50 con theremín (seno con portamento y vibrato), bajo pellizcado y vibráfono
en re menor. Se corta en el giro («Y en 1994...») y vuelve más juguetona (rápida y en mayor) en el remate («¿Y los cuerpos?»).
Efectos: papel que se arruga, balido, imprenta, risas con eco, estática de tele, susurro y sonar.
Uso: python3 scripts/scifi.py [--solo efectos|musica]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import cabaret as cb  # noqa: E402
from cabaret import SR, banda, guardar, hz, poner, ruido, t  # noqa: E402

rng = np.random.default_rng(47)


def theremin(notas, bpm, vibrato=6.0, prof=0.012, porta=0.06, vel=0.35):
    """notas: lista de (pulso, midi, duración en pulsos). Glissando entre notas seguidas."""
    beat = 60 / bpm
    total = max(p + d for p, _m, d in notas) * beat + 0.6
    n = int(SR * total)
    frec = np.zeros(n, np.float32)
    env = np.zeros(n, np.float32)
    prev = None
    for p, m, d in notas:
        a, b = int(p * beat * SR), int((p + d) * beat * SR)
        f1 = hz(m)
        if prev is None:
            prev = f1
        k = np.arange(b - a) / SR
        glis = np.clip(k / porta, 0, 1)
        frec[a:b] = prev + (f1 - prev) * glis
        env[a:b] = np.minimum(1, np.minimum(k / 0.05, (b - a) / SR - k + 0.02) / 0.08)
        prev = f1
    tt = np.arange(n) / SR
    frec = frec * (1 + prof * np.sin(2 * np.pi * vibrato * tt))
    fase = 2 * np.pi * np.cumsum(frec) / SR
    sonido = (np.sin(fase) + 0.15 * np.sin(2 * fase) + 0.05 * np.sin(3 * fase)) * env * vel
    return sonido.astype(np.float32)


def vibrafono(m, dur, vel=0.3):
    tt = t(dur + 1.0)
    f = hz(m)
    trem = 1 + 0.25 * np.sin(2 * np.pi * 5.5 * tt)
    return (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 4 * f * tt) * np.exp(-tt * 6)) * np.exp(-tt * 1.6) * trem * vel


def pieza(dur, bpm=96, jugueton=False):
    out = np.zeros(int(SR * dur), np.float32)
    beat = 60 / bpm
    compas = 4 * beat
    if not jugueton:
        # re menor misterioso: bajo pellizcado y acordes de vibráfono; el theremín canta una frase que sube y baja
        bajos = [38, 38, 41, 36, 38, 38, 43, 45]
        acordes = [(62, 65, 69), (62, 65, 69), (65, 69, 72), (60, 64, 67), (62, 65, 69), (62, 65, 70), (67, 70, 74), (64, 69, 73)]
        melodia = [(0, 74, 1.5), (1.5, 77, 0.5), (2, 76, 1), (3, 73, 1), (4, 74, 3), (8, 77, 1.5), (9.5, 81, 0.5), (10, 79, 1), (11, 77, 1), (12, 76, 3),
                   (16, 74, 1.5), (17.5, 77, 0.5), (18, 81, 2), (20, 82, 1), (21, 81, 1), (22, 77, 2), (24, 76, 2), (26, 73, 2), (28, 74, 4)]
    else:
        # re mayor juguetón y más rápido
        bajos = [38, 45, 38, 45, 43, 45, 38, 45]
        acordes = [(62, 66, 69), (61, 64, 69), (62, 66, 69), (61, 64, 69), (67, 71, 74), (64, 69, 73), (62, 66, 69), (61, 64, 69)]
        melodia = [(0, 74, 0.5), (0.5, 78, 0.5), (1, 81, 1), (2, 78, 0.5), (2.5, 74, 0.5), (3, 76, 1), (4, 74, 0.5), (4.5, 78, 0.5), (5, 81, 1), (6, 86, 2),
                   (8, 83, 0.5), (8.5, 81, 0.5), (9, 79, 1), (10, 78, 0.5), (10.5, 76, 0.5), (11, 74, 1), (12, 81, 2), (14, 74, 2)]
    ciclo = len(bajos) * compas
    k = 0
    while k * ciclo < dur:
        base = k * ciclo
        for c, (b, ac) in enumerate(zip(bajos, acordes)):
            t0 = base + c * compas
            for pulso in range(4):
                if jugueton or pulso in (0, 2):
                    poner(out, cb.pizz(b if pulso % 2 == 0 else b + 7, 0.5, 0.6), t0 + pulso * beat)
            poner(out, sum(vibrafono(m, compas * 0.9, 0.12) for m in ac), t0)
        poner(out, theremin(melodia, bpm), base)
        k += 1
    return out


def generar_musica():
    d = json.load(open("public/voz-palabras.json", encoding="utf-8"))
    fr = d["frases"]
    total = d["duracion"] + 2.0
    out = np.zeros(int(SR * total), np.float32)
    corte = fr[11]["inicio"] - 0.05
    vuelve = fr[15]["inicio"] - 0.15
    a = pieza(corte + 0.3, bpm=92)[: int(SR * corte)]
    f = int(0.05 * SR)
    a[-f:] *= np.linspace(1, 0, f)
    b = pieza(total - vuelve + 0.5, bpm=132, jugueton=True)[: int(SR * (total - vuelve))]
    b[:f] *= np.linspace(0, 1, f)
    for x, ini in ((a, 0.0), (b, vuelve)):
        x = x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * 10 ** (-18 / 20)
        poner(out, x, ini)
    pico = float(np.max(np.abs(out))) or 1.0
    guardar("public/musica.wav", out * min(1.0, 0.89 / pico), normalizar=False)
    print(f"música: {total:.1f} s (corte en {corte:.2f} s, vuelve en {vuelve:.2f} s)")


# ---------------- efectos ----------------

def arruga():
    n = int(SR * 0.9)
    out = np.zeros(n, np.float32)
    for _ in range(90):
        i = int(rng.uniform(0, 0.8) * SR)
        m = int(rng.uniform(0.003, 0.012) * SR)
        out[i:i + m] += rng.standard_normal(m).astype(np.float32) * rng.uniform(0.1, 0.6)
    return banda(out, 1500, 9000)


def balido():
    tt = t(0.9)
    f = 420 + 40 * np.sin(2 * np.pi * 9 * tt) * (tt > 0.15)
    fase = 2 * np.pi * np.cumsum(f) / SR
    voz = sum(np.sin(k * fase) / k for k in range(1, 12))
    return banda(voz, 300, 3500) * np.sin(np.pi * tt / 0.9) ** 0.6 * 0.5


def imprenta():
    n = int(SR * 1.6)
    out = np.zeros(n, np.float32)
    for k in range(10):
        tt = t(0.12)
        golpe = banda(ruido(0.12), 200, 3000) * np.exp(-tt * 40) + np.sin(2 * np.pi * 140 * tt) * np.exp(-tt * 30) * 0.4
        poner(out, golpe, k * 0.15)
    return out + banda(ruido(1.6), 100, 600) * 0.06


def risas():
    """«¡ja, ja, ja!» con eco"""
    seco = np.zeros(int(SR * 1.4), np.float32)
    for k in range(6):
        tt = t(0.16)
        f = 230 - k * 8
        fase = 2 * np.pi * f * tt
        voz = sum(np.sin(j * fase) * (1 / j) for j in range(1, 14))
        a = banda(voz, 600, 1400) * 0.8 + banda(voz, 1000, 2600) * 0.5
        a += banda(ruido(0.16), 1200, 5000) * 0.25 * np.exp(-tt * 30)
        poner(seco, a * np.sin(np.pi * tt / 0.16), k * 0.2)
    out = np.zeros(int(SR * 3.0), np.float32)
    for e in range(4):
        poner(out, seco * (0.55 ** e), e * 0.35)
    return out


def estatica():
    tt = t(1.2)
    return banda(ruido(1.2), 800, 9000) * 0.5 * np.minimum(1, (1.2 - tt) / 0.2) + np.sin(2 * np.pi * 15734 / 4 * tt) * 0.03


def susurro():
    n = int(SR * 1.6)
    out = np.zeros(n, np.float32)
    for k in range(5):
        tt = t(0.22)
        s_ = banda(ruido(0.22), 3000, 8000) * np.sin(np.pi * tt / 0.22) * 0.5
        poner(out, s_, 0.1 + k * 0.28 + rng.uniform(0, 0.05))
    return out


def sonar():
    tt = t(1.6)
    return np.sin(2 * np.pi * 1150 * tt) * np.exp(-tt * 3) * 0.6 + np.sin(2 * np.pi * 1150 * tt) * np.exp(-np.maximum(0, tt - 0.5) * 3) * (tt > 0.5) * 0.25


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", default="")
    args = ap.parse_args()
    os.makedirs("public/sfx", exist_ok=True)
    if args.solo in ("", "efectos"):
        for nombre, x, gan in [("arruga", arruga(), 0.7), ("balido", balido(), 0.6), ("imprenta", imprenta(), 0.7), ("risas", risas(), 0.7),
                               ("estatica", estatica(), 0.5), ("susurro", susurro(), 0.6), ("sonar", sonar(), 0.6)]:
            guardar(f"public/sfx/{nombre}.wav", x, gan)
        print("efectos listos")
    if args.solo in ("", "musica"):
        generar_musica()


if __name__ == "__main__":
    main()
