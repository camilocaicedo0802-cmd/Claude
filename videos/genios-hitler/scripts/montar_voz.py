"""Monta la voz cruda: narrador + voces extra insertadas en su sitio, y la última frase más lenta.

Uso: python3 scripts/montar_voz.py --narrador N.wav --extra c1=A.wav --extra c2=B.wav --extra hacker=C.wav
     [--lenta 0.88] [--tempo-extra hacker=1.1]
Escribe public/voz-cruda.wav (24 kHz); después: python3 scripts/alinear.py --tempo T y scripts/efectos_voz.py
"""

import argparse
import re
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from alinear import SR, alinear, leer, transcribir  # noqa: E402
import guion as _g  # noqa: E402
from guion import GUION  # noqa: E402


def a_wav(x, ruta):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", ruta],
                   input=(np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes(), check=True)


def atempo(x, factor):
    datos = subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"atempo={factor}",
                            "-f", "s16le", "-"], input=(np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(datos, np.int16).astype(np.float32) / 32768


def rubber(x, tempo=1.0, semitonos=0.0):
    """cambia velocidad y tono conservando el timbre (formantes)"""
    if abs(tempo - 1) < 1e-3 and abs(semitonos) < 1e-3:
        return x
    filtro = f"rubberband=tempo={tempo:.4f}:pitch={2 ** (semitonos / 12):.5f}:formant=preserved"
    datos = subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", filtro, "-f", "s16le", "-"],
                           input=(np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(datos, np.int16).astype(np.float32) / 32768


def envolvente(x):
    win = int(SR * 0.005)
    n = len(x) // win
    return 20 * np.log10(np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1)) + 1e-9), win


def recortar(x, margen=0.02):
    db, win = envolvente(x)
    voz = np.where(db > np.percentile(db, 95) - 32)[0]
    a = max(0, voz[0] * win - int(margen * SR))
    b = min(len(x), (voz[-1] + 1) * win + int(margen * SR))
    return x[a:b]


def rms_voz(x):
    db, win = envolvente(x)
    e = 10 ** (db / 20)
    return float(np.sqrt(np.mean(e[db > np.percentile(db, 60)] ** 2)))


def silabas(texto):
    return len(re.findall(r"[aeiouáéíóúü]+", texto.lower()))


def f0_mediana(x):
    sr = SR
    win, hop = int(0.04 * sr), int(0.01 * sr)
    out = []
    for k in range(0, len(x) - win, hop):
        fr = x[k:k + win] * np.hanning(win)
        if np.sqrt(np.mean(fr ** 2)) < 0.02:
            continue
        ac = np.correlate(fr, fr, "full")[win - 1:]
        lo, hi = int(sr / 400), int(sr / 65)
        j = lo + int(np.argmax(ac[lo:hi]))
        if ac[j] / ac[0] > 0.45:
            out.append(sr / j)
    return float(np.median(out)) if out else 0.0


def trocear(x, indices):
    """parte un audio en frases (por los puntos más silenciosos) y mide la duración hablada de cada una"""
    fichas = [{"texto": tok, "frase": i} for i in indices for tok in GUION[i][0].split()]
    alinear(fichas, transcribir(x))
    fin = {i: max(f["fin"] for f in fichas if f["frase"] == i) for i in indices}
    ini = {i: min(f["ini"] for f in fichas if f["frase"] == i) for i in indices}
    bordes = [0] + [punto_quieto(x, fin[i] + 0.01) for i in indices[:-1]] + [len(x)]
    return {i: x[bordes[k]:bordes[k + 1]] for k, i in enumerate(indices)}, {i: fin[i] - ini[i] for i in indices}


def sin_silencio_inicial(x):
    db, win = envolvente(x)
    voz = np.where(db > np.percentile(db, 95) - 30)[0]
    return x[max(0, voz[0] * win - int(0.02 * SR)):] if len(voz) else x


def punto_quieto(x, t, ventana=0.25):
    """el instante más silencioso justo después de t"""
    i0 = int(t * SR)
    tramo = np.abs(x[i0:i0 + int(ventana * SR)])
    suave = np.convolve(tramo, np.ones(240) / 240, "same")
    return i0 + int(np.argmin(suave))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--narrador", required=True)
    ap.add_argument("--extra", action="append", default=[], help="voz=archivo")
    ap.add_argument("--lenta", type=float, default=0.0, help="atempo de la última frase (0 = decidir midiendo)")
    ap.add_argument("--tempo-extra", action="append", default=[], help="voz=factor")
    ap.add_argument("--salida", default="public/voz-cruda.wav")
    ap.add_argument("--remate", default="", help="audio aparte con las frases finales (desde --desde-remate)")
    ap.add_argument("--desde-remate", type=int, default=19)
    args = ap.parse_args()

    extras = dict(e.split("=", 1) for e in args.extra)
    tempos = {k: float(v) for k, v in (e.split("=", 1) for e in args.tempo_extra)}
    x = leer(args.narrador)
    narr = [i for i, fr in enumerate(GUION) if not fr[3]]
    trozos, dur = trocear(x, narr)
    if args.remate:
        y = leer(args.remate)
        finales = [i for i in narr if i >= args.desde_remate]
        t2, d2 = trocear(y, finales)
        g = rms_voz(x) / rms_voz(y)
        trozos.update({i: t * g for i, t in t2.items()})
        dur.update(d2)
        print(f"remate desde la frase {args.desde_remate} (ganancia {g:.2f})")

    ajustes = dict(getattr(_g, "AJUSTE_FRASES", {}))
    vel = {i: silabas(GUION[i][0]) / max(0.3, dur[i]) * ajustes.get(i, (1.0, 0))[0] for i in narr}
    ult = narr[-1]
    resto = float(np.median([v for i, v in vel.items() if i != ult]))
    print("sílabas/s por frase (con ajustes):", {i: round(v, 2) for i, v in vel.items()})
    print(f"última frase {vel[ult]:.2f} vs mediana {resto:.2f} ({vel[ult] / resto * 100 - 100:+.0f} %)")
    lenta = args.lenta or min(1.0, (resto * 0.89) / vel[ult])
    print(f"velocidad extra de la última frase: x{lenta:.3f}")
    t0, s0 = ajustes.get(ult, (1.0, 0.0))
    ajustes[ult] = (t0 * lenta, s0)
    nivel = rms_voz(x)
    piezas = []
    for i, (texto, _s, _e, voz) in enumerate(GUION):
        if not voz:
            tempo, semis = ajustes.get(i, (1.0, 0.0))
            trozo = trozos[i]
            if i > 0 and GUION[i - 1][3]:
                trozo = sin_silencio_inicial(trozo)
            pausa = getattr(_g, "PAUSAS_INSERTAR", {}).get(i, 0)
            if pausa:
                trozo = np.concatenate([np.zeros(int(pausa * SR), np.float32), sin_silencio_inicial(trozo)])
            hecho = rubber(trozo, tempo, semis)
            if semis:
                print(f"  frase {i}: tono {f0_mediana(trozo):.0f} → {f0_mediana(hecho):.0f} Hz")
            piezas.append(hecho)
            if (tempo, semis) != (1.0, 0.0):
                print(f"frase {i}: velocidad x{tempo:.3f}, {semis:+.1f} st")
            continue
        clip = recortar(leer(extras[voz]))
        if voz in tempos:
            clip = rubber(clip, tempos[voz])
        clip = clip * (nivel / rms_voz(clip)) * (0.9 if voz == "hacker" else 0.95)
        f = int(0.008 * SR)
        clip[:f] *= np.linspace(0, 1, f)
        clip[-f:] *= np.linspace(1, 0, f)
        piezas += [np.zeros(int(0.05 * SR), np.float32), clip, np.zeros(int(0.05 * SR), np.float32)]
        print(f"voz {voz} (frase {i}): {len(clip) / SR:.2f} s")
    salida = np.concatenate(piezas)
    a_wav(salida, args.salida)
    print(f"{args.salida}: {len(salida) / SR:.2f} s (narrador {len(x) / SR:.2f} s)")


if __name__ == "__main__":
    main()
