"""Tiempos PROVISIONALES de la voz (estimados desde el guion) para armar las escenas antes de tener la voz real.
Sátira a 178 ppm, frases serias a 150, citas a 165, con las pausas exactas de PAUSAS.
Escribe public/voz-palabras.json con el mismo formato que alinear.py (que lo reemplaza después)."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import guion as g  # noqa: E402
from alinear import aplicar_visibles, norm  # noqa: E402


def silabas(p):
    v = "aeiouáéíóúü"
    n, prev = 0, False
    for c in p.lower():
        es = c in v
        if es and not prev:
            n += 1
        prev = es
    return max(1, n)


def main():
    palabras, frases, t = [], [], 0.0
    for i, (texto, cap, enf, voz) in enumerate(g.GUION):
        toks = texto.split()
        ppm = 150 if i in g.SERIAS else (165 if voz else 178)
        dur_total = len(toks) * 60 / ppm
        pesos = [silabas(w) + 0.6 for w in toks]
        k = dur_total / sum(pesos)
        ini0 = t
        for w, p in zip(toks, pesos):
            d = p * k
            visible = w.upper() if enf else w
            palabras.append({"texto": norm(w), "inicio": round(t, 3), "duracion": round(d * 0.92, 3), "visible": visible,
                             "enfasis": bool(enf), "frase": i, "seccion": cap})
            t += d
        frases.append({"i": i, "texto": texto, "seccion": cap, "inicio": round(ini0, 3), "fin": round(t, 3)})
        t += g.PAUSAS.get(i, g.PAUSA_NORMAL)
    palabras = aplicar_visibles(palabras)
    with open("public/voz-palabras.json", "w", encoding="utf-8") as f:
        json.dump({"voz": "provisional", "duracion": round(t, 3), "frases": frases, "palabras": palabras}, f, ensure_ascii=False, indent=1)
    print(f"provisional: {t / 60:.2f} min")


if __name__ == "__main__":
    main()
