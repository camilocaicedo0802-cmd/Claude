"""Efectos de las voces extra sobre public/voz.wav (después de alinear.py):
- comentarios de internet (c1, c2): filtro de celular
- mensaje del hacker: voz fría con eco (la cola del eco se suma a lo que sigue)

Uso: python3 scripts/efectos_voz.py
"""

import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from guion import GUION  # noqa: E402

SR = 48000
FILTROS = {
    "c1": "highpass=f=480,lowpass=f=3300,acompressor=threshold=-20dB:ratio=4:attack=4:release=60,acrusher=bits=11:mode=log:aa=1:mix=0.25,volume=2.7",
    "c2": "highpass=f=520,lowpass=f=3100,acompressor=threshold=-20dB:ratio=4:attack=4:release=60,acrusher=bits=11:mode=log:aa=1:mix=0.25,volume=2.7",
    "hacker": "highpass=f=140,lowpass=f=6500,aecho=0.85:0.7:110|240:0.32|0.2,volume=2.3",
}
COLA = {"hacker": 0.45}


def leer(ruta):
    datos = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(datos, np.int16).astype(np.float32) / 32768


def procesar(x, filtro, cola):
    f = filtro + (f",apad=pad_dur={cola}" if cola else "")
    datos = subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f, "-f", "s16le", "-"],
                           input=(np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(datos, np.int16).astype(np.float32) / 32768


def main():
    voz = leer("public/voz.wav")
    datos = json.load(open("public/voz-palabras.json", encoding="utf-8"))
    for fr in datos["frases"]:
        etiqueta = GUION[fr["i"]][3]
        if etiqueta not in FILTROS:
            continue
        a, b = int(max(0, fr["inicio"] - 0.04) * SR), int(min(len(voz) / SR, fr["fin"] + 0.08) * SR)
        cola = COLA.get(etiqueta, 0)
        hecho = procesar(voz[a:b], FILTROS[etiqueta], cola)
        n = b - a
        k = int(0.01 * SR)
        mezcla = hecho[:n].copy()
        mezcla[:k] = voz[a:a + k] * np.linspace(1, 0, k) + mezcla[:k] * np.linspace(0, 1, k)
        voz[a:b] = mezcla
        resto = hecho[n:]
        if len(resto):
            resto = resto * np.linspace(1, 0, len(resto)) ** 2
            fin = min(len(voz), b + len(resto))
            voz[b:fin] += resto[: fin - b]
        print(f"[{fr['i']:02d}] {etiqueta}: {fr['inicio']:.2f}–{fr['fin']:.2f} s")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "alimiter=limit=0.95:level=false", "public/voz.wav"],
                   input=(np.clip(voz, -1, 1) * 32767).astype(np.int16).tobytes(), check=True)
    print("listo: public/voz.wav")


if __name__ == "__main__":
    main()
