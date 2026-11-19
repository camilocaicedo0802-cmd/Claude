"""Monta la voz del video largo frase por frase, con las pausas exactas del guion.

- Corta cada frase del narrador de su toma de capítulo (whisper + alineación difusa) y la recorta al habla.
- Dentro de cada frase, los silencios (y respiraciones) de más de 0,30 s se acortan a 0,22 s.
- Las citas y la muletilla van con su voz; la muletilla es UN audio que se repite igual las cuatro veces.
- Velocidad: la sátira a ~178 palabras/min y las frases serias a ~150 (medidas con sus pausas).
- Entre frases va silencio digital de la duración exacta de PAUSAS (sin respiraciones).

Uso: python3 scripts/montar_largo.py --carpeta DIR --tomas 0=1,1=2,... --citas papen=1,... --muletilla 2
Escribe public/voz-cruda.wav (24 kHz). Después: python3 scripts/alinear.py --sin-cortes
"""

import argparse
import json
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import guion as g  # noqa: E402
from alinear import SR, alinear, leer, transcribir  # noqa: E402

OBJ_SATIRA = 178.0
OBJ_SERIO = 150.0


def a_wav(x, ruta):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", ruta],
                   input=(np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes(), check=True)


def rubber(x, tempo=1.0):
    if abs(tempo - 1) < 1e-3:
        return x
    datos = subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af",
                            f"rubberband=tempo={tempo:.4f}:formant=preserved", "-f", "s16le", "-"],
                           input=(np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(datos, np.int16).astype(np.float32) / 32768


def env_db(x, win):
    n = len(x) // win
    if n == 0:
        return np.array([-120.0])
    return 20 * np.log10(np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1)) + 1e-9)


def recortar(x, ref_db, margen_ini=0.03, margen_fin=0.07):
    """recorta al habla: umbral relativo al nivel de referencia de la toma"""
    win = int(SR * 0.005)
    db = env_db(x, win)
    voz = np.where(db > ref_db - 34)[0]
    if not len(voz):
        return x
    a = max(0, voz[0] * win - int(margen_ini * SR))
    b = min(len(x), (voz[-1] + 1) * win + int(margen_fin * SR))
    return x[a:b]


def comprimir_silencios(x, ref_db, maximo=0.30, deja=0.22):
    """acorta los silencios internos (y respiraciones) largos"""
    win = int(SR * 0.005)
    db = env_db(x, win)
    quieto = db < ref_db - 27
    piezas, cursor, j = [], 0, 0
    n = len(quieto)
    while j < n:
        if quieto[j]:
            k = j
            while k < n and quieto[k]:
                k += 1
            largo = (k - j) * win / SR
            if largo > maximo and j > 0 and k < n:
                c0 = j * win + int((deja / 2) * SR)
                c1 = k * win - int((deja / 2) * SR)
                piezas.append(x[cursor:c0])
                cursor = c1
            j = k
        else:
            j += 1
    piezas.append(x[cursor:])
    f = int(0.006 * SR)
    for p in piezas[1:]:
        if len(p) > 2 * f:
            p[:f] *= np.linspace(0, 1, f)
    for p in piezas[:-1]:
        if len(p) > 2 * f:
            p[-f:] *= np.linspace(1, 0, f)
    return np.concatenate(piezas) if piezas else x


def punto_quieto(x, t, ventana=0.3):
    i0 = int(t * SR)
    tramo = np.abs(x[i0:i0 + int(ventana * SR)])
    if not len(tramo):
        return min(len(x), i0)
    suave = np.convolve(tramo, np.ones(240) / 240, "same")
    return i0 + int(np.argmin(suave))


def nivel_ref(x):
    db = env_db(x, int(SR * 0.005))
    return float(np.percentile(db, 95))


def rms_voz(x):
    db = env_db(x, int(SR * 0.005))
    e = 10 ** (db / 20)
    return float(np.sqrt(np.mean(e[db > np.percentile(db, 60)] ** 2)))


def palabras(t):
    return len(t.split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", required=True)
    ap.add_argument("--tomas", required=True, help="capítulo=toma, separados por coma")
    ap.add_argument("--citas", default="", help="voz=toma, separados por coma (por defecto 1)")
    ap.add_argument("--muletilla", default="1")
    ap.add_argument("--salida", default="public/voz-cruda.wav")
    args = ap.parse_args()
    tomas = {int(a): b for a, b in (p.split("=") for p in args.tomas.split(","))}
    citas = dict(p.split("=") for p in args.citas.split(",") if p) if args.citas else {}

    trozos = {}
    ref_global = []
    for c, k in sorted(tomas.items()):
        x = leer(os.path.join(args.carpeta, f"cap{c}_{k}.wav"))
        ref = nivel_ref(x)
        ref_global.append(rms_voz(x))
        idx = [i for i, fr in enumerate(g.GUION) if fr[1] == c and not fr[3]]
        fichas = [{"texto": tok, "frase": i} for i in idx for tok in g.GUION[i][0].split()]
        alinear(fichas, transcribir(x))
        fin = {i: max(f["fin"] for f in fichas if f["frase"] == i) for i in idx}
        bordes = [0] + [punto_quieto(x, fin[i] + 0.01) for i in idx[:-1]] + [len(x)]
        for n, i in enumerate(idx):
            trozo = x[bordes[n]:bordes[n + 1]].copy()
            trozo = recortar(trozo, ref)
            trozos[i] = comprimir_silencios(trozo, ref)
        print(f"capítulo {c}: {len(idx)} frases (toma {k})", flush=True)
    nivel = float(np.median(ref_global))

    def clip(nombre):
        y = leer(os.path.join(args.carpeta, nombre))
        y = comprimir_silencios(recortar(y, nivel_ref(y)), nivel_ref(y))
        return y * (nivel / rms_voz(y))

    muletilla = clip(f"muletilla_{args.muletilla}.wav") * 1.0
    for i, (t, _c, _e, voz) in enumerate(g.GUION):
        if voz == g.M:
            trozos[i] = muletilla
        elif voz:
            trozos[i] = clip(f"{voz}_{citas.get(voz, '1')}.wav") * 0.92

    # velocidades: la sátira y lo serio, cada grupo a su ritmo (contando sus pausas)
    narr = [i for i, fr in enumerate(g.GUION) if not fr[3]]
    def factor(grupo, objetivo):
        w = sum(palabras(g.GUION[i][0]) for i in grupo)
        d = sum(len(trozos[i]) / SR for i in grupo)
        p = sum(min(g.PAUSAS.get(i, g.PAUSA_NORMAL), 0.5) for i in grupo)
        necesario = w * 60 / objetivo - p
        return d / necesario
    serias = [i for i in narr if i in g.SERIAS]
    satira = [i for i in narr if i not in g.SERIAS]
    t_sat = float(np.clip(factor(satira, OBJ_SATIRA), 0.8, 1.35))
    t_ser = float(np.clip(factor(serias, OBJ_SERIO), 0.7, 1.3))
    print(f"velocidad: sátira x{t_sat:.3f}, serio x{t_ser:.3f}", flush=True)

    piezas, mapa, t = [], [], 0.0
    for i, (texto, cap, _e, voz) in enumerate(g.GUION):
        y = trozos[i]
        if not voz:
            y = rubber(y, t_ser if i in g.SERIAS else t_sat)
        piezas.append(y)
        mapa.append({"i": i, "inicio": round(t, 3), "fin": round(t + len(y) / SR, 3)})
        t += len(y) / SR
        pausa = g.PAUSAS.get(i, g.PAUSA_NORMAL) if i < len(g.GUION) - 1 else 0.5
        piezas.append(np.zeros(int(pausa * SR), np.float32))
        t += pausa
    salida = np.concatenate(piezas)
    a_wav(salida, args.salida)
    with open(os.path.join(os.path.dirname(args.salida), "voz-montaje.json"), "w", encoding="utf-8") as f:
        json.dump(mapa, f, ensure_ascii=False)
    w_sat = sum(palabras(g.GUION[i][0]) for i in satira)
    d_sat = sum(m["fin"] - m["inicio"] + g.PAUSAS.get(m["i"], g.PAUSA_NORMAL) for m in mapa if m["i"] in satira)
    w_ser = sum(palabras(g.GUION[i][0]) for i in serias)
    d_ser = sum(m["fin"] - m["inicio"] + min(g.PAUSAS.get(m["i"], g.PAUSA_NORMAL), 0.5) for m in mapa if m["i"] in serias)
    print(f"{args.salida}: {len(salida) / SR / 60:.2f} min · sátira {w_sat / d_sat * 60:.0f} ppm · serio {w_ser / d_ser * 60:.0f} ppm", flush=True)


if __name__ == "__main__":
    main()
