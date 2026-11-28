"""Música y efectos del short del Titanic (todo sintetizado, de composición propia y libre de derechos).

Música: pieza de misterio marino en re menor, compás de 6/8 que mece como el mar: bordón grave de cuerdas, arpa en
arpegios y, desde el iceberg, un pulso que sube la tensión. Se corta después de «¿Y frenaron?» (silencio para el «No.»),
vuelve con un piano melancólico y respetuoso para la carta, se detiene en la pausa de «el único que tenía la llave…»
y cierra suave con un acorde final para el veredicto.
Efectos: campana de la cofa (tres toques), telégrafo Morse y bocina de barco.
Uso: python3 scripts/oceano.py [--solo efectos|musica]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import cabaret as cb  # noqa: E402
from cabaret import SR, banda, guardar, hz, poner, ruido, t  # noqa: E402

rng = np.random.default_rng(1912)


def bordon(m, dur, vel=0.5):
    """cuerdas graves sostenidas: sierra filtrada con vibrato lento y crescendo suave"""
    tt = t(dur)
    f = hz(m) * (1 + 0.003 * np.sin(2 * np.pi * 4.8 * tt))
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * fase) / k for k in range(1, 9))
    env = np.minimum(1, tt / 0.8) * np.minimum(1, np.maximum(0, dur - tt) / 0.6)
    return banda(x * env, 50, 900) * vel * 0.3


def arpa(m, vel=0.5):
    return cb.pizz(m, 1.6, vel)


def celesta(m, dur=1.2, vel=0.4):
    tt = t(dur)
    x = sum(np.sin(2 * np.pi * hz(m) * r * tt) * np.exp(-tt * d) * a for r, d, a in ((1, 3.0, 1.0), (2, 5.0, 0.4), (3.01, 8.0, 0.2), (4.2, 12.0, 0.1)))
    return x * np.minimum(1, tt / 0.003) * vel * 0.35


def pulso(vel=0.6):
    """latido grave (bombo apagado)"""
    tt = t(0.35)
    f = 70 * np.exp(-tt * 9) + 38
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 11) * vel


# armonía en re menor (un acorde por compás de 6/8): Dm, Bb, Gm, A
ACORDES = [(38, (50, 53, 57)), (34, (50, 53, 58)), (31, (50, 55, 58)), (33, (49, 52, 57))]
MELODIA_PIANO = [(0, 69, 1.5), (1.5, 70, 0.5), (2, 69, 1), (3, 65, 3), (6, 67, 1.5), (7.5, 69, 0.5), (8, 70, 1), (9, 69, 3),
                 (12, 62, 1.5), (13.5, 65, 0.5), (14, 67, 1), (15, 69, 3), (18, 64, 1.5), (19.5, 65, 0.5), (20, 64, 1), (21, 61, 3)]


def misterio(dur, tension=0.0, vel=1.0):
    """6/8 a 92 negras con punto por minuto; `tension` 0..1 suma el pulso y el arpa más densa"""
    out = np.zeros(int(SR * dur) + SR * 4, np.float32)
    corchea = 60 / 92 / 3
    compas = corchea * 6
    k = 0
    while k * compas < dur:
        b, ac = ACORDES[k % 4]
        t0 = k * compas
        poner(out, bordon(b, compas + 0.4, 0.55 * vel), t0)
        poner(out, bordon(b + 7, compas + 0.4, 0.25 * vel), t0)
        notas = [ac[0], ac[1], ac[2], ac[1] + 12, ac[2], ac[1]]
        for i, m in enumerate(notas):
            poner(out, arpa(m, (0.42 if i == 0 else 0.3) * vel), t0 + i * corchea)
        if tension > 0:
            for p in (0, 3):
                poner(out, pulso(0.9 * tension * vel), t0 + p * corchea)
            poner(out, celesta(ac[2] + 24, 0.8, 0.5 * tension * vel), t0 + 5 * corchea)
        k += 1
    return out[: int(SR * dur)]


def carta(dur, vel=1.0):
    """piano melancólico sobre el bordón (respeto: es una tragedia real)"""
    out = np.zeros(int(SR * dur) + SR * 4, np.float32)
    negra = 60 / 72
    for p, m, d in MELODIA_PIANO:
        if p * negra < dur:
            poner(out, cb.piano(m, d * negra, 0.55 * vel), p * negra)
    for i in range(int(dur / (3 * negra)) + 1):
        b, ac = ACORDES[i % 4]
        poner(out, bordon(b, 3 * negra + 0.4, 0.4 * vel), i * 3 * negra)
        for j, m in enumerate(ac):
            poner(out, cb.piano(m, 3 * negra, 0.18 * vel), i * 3 * negra + j * 0.05)
    return out[: int(SR * dur)]


def acorde_final(vel=1.0):
    dur = 3.2
    out = np.zeros(int(SR * dur), np.float32)
    for j, m in enumerate((38, 50, 57, 62, 65, 69)):
        poner(out, cb.piano(m, 2.6, 0.35 * vel), j * 0.035)
    poner(out, bordon(38, dur, 0.5 * vel), 0)
    poner(out, celesta(74, 2.0, 0.5 * vel), 0.1)
    return out


def generar_musica():
    d = json.load(open("public/voz-palabras.json", encoding="utf-8"))
    fr = d["frases"]
    total = d["duracion"] + 2.0
    out = np.zeros(int(SR * total), np.float32)
    nivel = 10 ** (-18 / 20)

    def pegar(x, a, b, g=1.0, fade=0.05):
        x = x[: int((b - a) * SR)].copy()
        rms = np.sqrt(np.mean(x ** 2)) + 1e-9
        x = x / rms * nivel * g
        f = int(fade * SR)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        poner(out, x, a)

    a1, b1 = 0.0, fr[6]["inicio"]
    a2, b2 = fr[6]["inicio"], fr[19]["fin"] + 0.03            # desde el iceberg, con pulso; corta tras «¿Y frenaron?»
    a3, b3 = fr[21]["inicio"] - 0.1, fr[24]["fin"] + 0.03     # la carta (después del «No.»)
    a4, b4 = fr[25]["inicio"] - 0.05, total
    pegar(misterio(b1 - a1 + 0.5), a1, b1 + 0.3, 1.0)
    pegar(misterio(b2 - a2, tension=1.0), a2, b2, 1.05, fade=0.03)
    pegar(carta(b3 - a3), a3, b3, 0.9, fade=0.04)
    fin = acorde_final()
    pegar(np.concatenate([misterio(fr[26]["inicio"] - a4, vel=0.8), fin]), a4, b4, 0.85)
    pico = float(np.max(np.abs(out))) or 1.0
    guardar("public/musica.wav", out * min(1.0, 0.89 / pico), normalizar=False)
    print("música: " + ", ".join(f"{a:.2f}–{b:.2f}" for a, b in ((a1, b1), (a2, b2), (a3, b3), (a4, b4))))


# ---------------- efectos ----------------

def campana():
    """la campana de la cofa: tres toques"""
    out = np.zeros(int(SR * 2.6), np.float32)
    for k in range(3):
        tt = t(1.6)
        x = sum(np.sin(2 * np.pi * 1180 * r * tt) * np.exp(-tt * dcy) * a for r, dcy, a in ((1, 2.2, 1.0), (2.0, 3.5, 0.5), (2.76, 5.0, 0.35), (5.4, 9.0, 0.2)))
        poner(out, x * np.minimum(1, tt / 0.002) * 0.5, k * 0.38)
    return out


def morse():
    """telégrafo: · · · — — — · · · (pitidos de 700 Hz)"""
    out = np.zeros(int(SR * 2.2), np.float32)
    punto = 0.07
    tiempo = 0.0
    for c in "...---...":
        d = punto if c == "." else punto * 3
        tt = t(d)
        poner(out, np.sin(2 * np.pi * 700 * tt) * np.minimum(1, np.minimum(tt, d - tt) / 0.006) * 0.5, tiempo)
        tiempo += d + punto
    return out


def bocina():
    """bocina grave de barco de vapor (dos tonos)"""
    dur = 2.0
    tt = t(dur)
    x = np.zeros_like(tt)
    for f0 in (110, 138):
        f = f0 * (1 + 0.004 * np.sin(2 * np.pi * 5 * tt))
        fase = 2 * np.pi * np.cumsum(f) / SR
        x += sum(np.sin(k * fase) / k ** 0.8 for k in range(1, 12))
    env = np.minimum(1, tt / 0.15) * np.minimum(1, np.maximum(0, dur - tt) / 0.4)
    return banda(x * env, 70, 2200) * 0.3 + banda(ruido(dur), 200, 1200) * env * 0.04


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", default="")
    args = ap.parse_args()
    os.makedirs("public/sfx", exist_ok=True)
    if args.solo in ("", "efectos"):
        for nombre, x, gan in [("campana", campana(), 0.7), ("morse", morse(), 0.6), ("bocina", bocina(), 0.7)]:
            guardar(f"public/sfx/{nombre}.wav", x, gan)
        print("efectos listos")
    if args.solo in ("", "musica"):
        generar_musica()


if __name__ == "__main__":
    main()
