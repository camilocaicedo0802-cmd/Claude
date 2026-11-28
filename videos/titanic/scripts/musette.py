"""Música y efectos del short de la Torre Eiffel (todo sintetizado, libre de derechos).

Música: vals musette parisino de composición propia, con acordeón (dos lengüetas desafinadas que «baten»),
bajo y acordes de guitarra en tres por cuatro. Se corta en la pausa del giro («...le pide un soborno.»), vuelve en
«Y eso lo convence», se detiene un instante en «¿Y cómo terminó?» y regresa suave para el final.
Efectos: silbato de policía, tren con vapor, chatarra, «shh», suspiro de alivio.
Uso: python3 scripts/musette.py [--solo efectos|musica]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import cabaret as cb  # noqa: E402
from cabaret import SR, banda, guardar, hz, poner, ruido, t  # noqa: E402

rng = np.random.default_rng(1925)


def acordeon(m, dur, vel=0.4):
    """nota de acordeón musette: dos lengüetas, una +12 cents, timbre de lengüeta (armónicos impares y pares)"""
    tt = t(dur + 0.08)
    out = np.zeros_like(tt)
    for cents in (0.0, 12.0):
        f = hz(m) * 2 ** (cents / 1200)
        fase = 2 * np.pi * f * tt
        out += sum(np.sin(k * fase) * (0.9 / k ** 0.9) for k in range(1, 9))
    env = np.minimum(1, tt / 0.03) * np.minimum(1, np.maximum(0, (dur + 0.08 - tt)) / 0.07)
    return banda(out * env, 200, 5000) * vel * 0.25


def guitarra(midis, dur, vel=0.3):
    tt = t(dur)
    out = np.zeros_like(tt)
    for j, m in enumerate(midis):
        f = hz(m)
        d = int(j * 0.012 * SR)
        x = sum(np.sin(2 * np.pi * k * f * tt) / k for k in range(1, 6)) * np.exp(-tt * 7)
        out[d:] += x[: len(out) - d]
    return out * vel * 0.3


# vals en la menor: 16 compases (pulso, midi, duración en pulsos)
MELODIA = [
    (0, 76, 1), (1, 77, 0.5), (1.5, 76, 0.5), (2, 75, 1), (3, 76, 2), (5, 72, 1),
    (6, 74, 1), (7, 76, 0.5), (7.5, 74, 0.5), (8, 72, 1), (9, 71, 2), (11, 69, 1),
    (12, 72, 1), (13, 76, 1), (14, 81, 1), (15, 80, 2), (17, 76, 1),
    (18, 77, 1), (19, 76, 1), (20, 74, 1), (21, 76, 3),
    (24, 76, 1), (25, 77, 0.5), (25.5, 76, 0.5), (26, 75, 1), (27, 76, 2), (29, 79, 1),
    (30, 81, 1), (31, 79, 0.5), (31.5, 77, 0.5), (32, 76, 1), (33, 74, 2), (35, 77, 1),
    (36, 76, 1), (37, 74, 1), (38, 72, 1), (39, 71, 1), (40, 72, 1), (41, 74, 1), (42, 69, 3), (45, 69, 3),
]
ARMONIA = [(45, (69, 72, 76)), (45, (69, 72, 76)), (40, (68, 71, 74)), (40, (68, 71, 74)), (45, (69, 72, 76)), (45, (69, 72, 76)), (38, (69, 74, 77)), (40, (68, 71, 74)),
           (45, (69, 72, 76)), (45, (69, 72, 76)), (40, (68, 71, 74)), (40, (68, 71, 74)), (38, (69, 74, 77)), (40, (68, 71, 74)), (45, (69, 72, 76)), (45, (69, 72, 76))]


def vals(dur, bpm=168, vel=1.0):
    out = np.zeros(int(SR * dur), np.float32)
    beat = 60 / bpm
    ciclo = len(ARMONIA) * 3 * beat
    k = 0
    while k * ciclo < dur:
        base = k * ciclo
        for c, (b, ac) in enumerate(ARMONIA):
            t0 = base + c * 3 * beat
            poner(out, cb.pizz(b, 0.6, 0.7 * vel), t0)
            for p in (1, 2):
                poner(out, guitarra(ac, beat * 0.9, 0.9 * vel), t0 + p * beat)
        for p, m, d in MELODIA:
            poner(out, acordeon(m, d * beat * 0.96, 0.5 * vel), base + p * beat)
        k += 1
    return out


def generar_musica():
    d = json.load(open("public/voz-palabras.json", encoding="utf-8"))
    fr = d["frases"]
    total = d["duracion"] + 2.0
    out = np.zeros(int(SR * total), np.float32)
    tramos = [(0.0, fr[11]["fin"] + 0.02, 1.0), (fr[12]["inicio"] - 0.05, fr[18]["fin"] + 0.02, 1.0), (fr[20]["inicio"] - 0.05, total, 0.75)]
    pieza = vals(total + 1)
    rms = np.sqrt(np.mean(pieza ** 2)) + 1e-9
    f = int(0.04 * SR)
    for a, b, g in tramos:
        x = pieza[int(a * SR):int(b * SR)].copy() / rms * 10 ** (-18 / 20) * g
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        poner(out, x, a)
    pico = float(np.max(np.abs(out))) or 1.0
    guardar("public/musica.wav", out * min(1.0, 0.89 / pico), normalizar=False)
    print("música: " + ", ".join(f"{a:.2f}–{b:.2f}" for a, b, _ in tramos))


# ---------------- efectos ----------------

def silbato():
    out = np.zeros(int(SR * 1.4), np.float32)
    for k, (ini, dur) in enumerate(((0.0, 0.35), (0.45, 0.8))):
        tt = t(dur)
        trino = 1 + 0.03 * np.sign(np.sin(2 * np.pi * 28 * tt))
        x = np.sin(2 * np.pi * np.cumsum(2900 * trino) / SR) + 0.3 * banda(ruido(dur), 2000, 5000)
        poner(out, x * np.minimum(1, np.minimum(tt / 0.02, (dur - tt) / 0.05)) * 0.5, ini)
    return out


def tren():
    n = int(SR * 2.5)
    out = np.zeros(n, np.float32)
    for k in range(8):
        tt = t(0.25)
        poner(out, banda(ruido(0.25), 200, 3000) * np.exp(-tt * 12) * 0.7, k * 0.25)
    tt = t(1.0)
    pito = sum(np.sin(2 * np.pi * f * tt) for f in (523, 659, 784)) * np.minimum(1, np.minimum(tt / 0.05, (1.0 - tt) / 0.2)) * 0.18
    poner(out, pito, 1.3)
    return out


def chatarra():
    n = int(SR * 1.6)
    out = np.zeros(n, np.float32)
    for k in range(10):
        tt = t(0.6)
        golpe = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, d in ((rng.uniform(300, 900), 8), (rng.uniform(1200, 3000), 14), (rng.uniform(3000, 5000), 22)))
        poner(out, golpe * 0.25 + banda(ruido(0.6), 500, 6000) * np.exp(-tt * 30) * 0.3, k * 0.08 + rng.uniform(0, 0.04))
    return out


def shh():
    tt = t(0.9)
    return banda(ruido(0.9), 2500, 7000) * np.sin(np.pi * tt / 0.9) ** 0.8 * 0.6


def suspiro():
    tt = t(1.0)
    return banda(ruido(1.0), 300, 2500) * np.exp(-tt * 2.5) * np.minimum(1, tt / 0.06) * 0.6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", default="")
    args = ap.parse_args()
    os.makedirs("public/sfx", exist_ok=True)
    if args.solo in ("", "efectos"):
        for nombre, x, gan in [("silbato", silbato(), 0.6), ("tren", tren(), 0.7), ("chatarra", chatarra(), 0.7), ("shh", shh(), 0.6), ("suspiro", suspiro(), 0.6)]:
            guardar(f"public/sfx/{nombre}.wav", x, gan)
        print("efectos listos")
    if args.solo in ("", "musica"):
        generar_musica()


if __name__ == "__main__":
    main()
