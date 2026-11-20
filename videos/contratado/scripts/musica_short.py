"""Música del short: el piano de cabaret del video largo y, en la escalada, el tic-tac del cronómetro (cada vez más rápido).
Se corta en seco en el giro (fin de «¿Y los hombres de Pápen...?») y ya no vuelve.
Uso: python3 scripts/musica_short.py  → public/musica.wav"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import cabaret as cb  # noqa: E402


def main():
    d = json.load(open("public/voz-palabras.json", encoding="utf-8"))
    fr = d["frases"]
    total = d["duracion"] + 2.0
    corte = fr[12]["fin"] + 0.05
    salida = np.zeros(int(cb.SR * total), np.float32)
    piano = cb.cabaret(corte + 0.5, bpm=124, swing=True)
    piano = piano[: int(cb.SR * corte)]
    f = int(0.04 * cb.SR)
    piano[-f:] *= np.linspace(1, 0, f)
    piano /= np.sqrt(np.mean(piano ** 2)) + 1e-9
    piano *= 10 ** (-18 / 20)
    salida[: len(piano)] += piano
    # tic-tac: del arranque del cronómetro («ganar») al corte, con el intervalo bajando de 0,5 a 0,22 s
    gan = [p for p in d["palabras"] if p["frase"] == 8][-1]["inicio"]
    t, k = gan, 0
    while t < corte - 0.05:
        tt = cb.t(0.05)
        clic = cb.banda(cb.ruido(0.05), 2500 if k % 2 == 0 else 1800, 8000) * np.exp(-tt * 140) * 0.35
        cb.poner(salida, clic, t)
        avance = (t - gan) / max(0.1, corte - gan)
        t += 0.5 - 0.28 * avance
        k += 1
    pico = float(np.max(np.abs(salida))) or 1.0
    cb.guardar("public/musica.wav", salida * min(1.0, 0.89 / pico), normalizar=False)
    print(f"música del short: {total:.1f} s (corte en {corte:.2f} s)")


if __name__ == "__main__":
    main()
