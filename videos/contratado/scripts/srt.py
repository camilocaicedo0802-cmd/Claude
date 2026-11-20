"""Subtítulos para YouTube (no van quemados en el video): out/genios-hitler.srt

Usa los tiempos por palabra de public/voz-palabras.json. Cada subtítulo: máximo 2 líneas de 42 caracteres,
cortando en pausas naturales (puntuación). Los nombres van bien escritos (el guion los trae con la grafía
que ayuda a la pronunciación: Pápen, Híndenburg, Dájau).
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import guion as g  # noqa: E402

GRAFIA = {"Pápen": "Papen", "Híndenburg": "Hindenburg", "Dájau": "Dachau"}
MAX_LINEA = 42
MAX_CUE = 2 * MAX_LINEA


def bien_escrito(t):
    for a, b in GRAFIA.items():
        t = t.replace(a, b)
    return t


def lineas(texto):
    if len(texto) <= MAX_LINEA:
        return texto
    palabras = texto.split()
    opciones = []
    for k in range(1, len(palabras)):
        a, b = " ".join(palabras[:k]), " ".join(palabras[k:])
        opciones.append((max(len(a), len(b)), abs(len(a) - len(b)), f"{a}\n{b}"))
    return min(opciones)[2]


def hms(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    datos = json.load(open("public/voz-palabras.json", encoding="utf-8"))
    cues = []
    for i, (texto, *_r) in enumerate(g.GUION):
        toks = texto.split()
        ps = [p for p in datos["palabras"] if p["frase"] == i]
        # tiempos por token del guion (los "visibles" pueden juntar varias palabras: se reparten)
        tiempos = []
        for p in ps:
            tiempos.append((p["inicio"], p["inicio"] + p["duracion"]))
        if len(tiempos) != len(toks):
            ini, fin = datos["frases"][i]["inicio"], datos["frases"][i]["fin"]
            paso = (fin - ini) / len(toks)
            tiempos = [(ini + k * paso, ini + (k + 1) * paso) for k in range(len(toks))]
        # trozos parejos de hasta MAX_CUE caracteres, cortando de preferencia tras puntuación
        total = len(texto)
        n = max(1, -(-total // MAX_CUE))
        cortes, acum = [], 0
        for k, w in enumerate(toks[:-1]):
            acum += len(w) + 1
            cortes.append((k, acum, bool(re.search(r"[,.:;?!…»]$", w))))
        fin_trozo, a = [], 0
        for j in range(1, n):
            meta = total * j / n
            cands = [c for c in cortes if c[0] >= a and abs(c[1] - meta) < 16]
            if not cands:
                cands = [min((c for c in cortes if c[0] >= a), key=lambda c: abs(c[1] - meta))]
            k = min(cands, key=lambda c: abs(c[1] - meta) - (12 if c[2] else 0))[0]
            fin_trozo.append(k)
            a = k + 1
        a = 0
        for k in fin_trozo + [len(toks) - 1]:
            cues.append([tiempos[a][0], tiempos[k][1], bien_escrito(" ".join(toks[a:k + 1]))])
            a = k + 1
    # que ninguno se encime con el siguiente y que duren al menos 1 s si hay espacio
    for j, c in enumerate(cues):
        sig = cues[j + 1][0] if j + 1 < len(cues) else c[1] + 2
        c[1] = min(max(c[1] + 0.25, c[0] + 1.0), sig - 0.04)
    os.makedirs("out", exist_ok=True)
    with open("out/genios-hitler.srt", "w", encoding="utf-8") as f:
        for j, (a, b, t) in enumerate(cues, 1):
            f.write(f"{j}\n{hms(a)} --> {hms(b)}\n{lineas(t)}\n\n")
    print(f"out/genios-hitler.srt: {len(cues)} subtítulos")


if __name__ == "__main__":
    main()
