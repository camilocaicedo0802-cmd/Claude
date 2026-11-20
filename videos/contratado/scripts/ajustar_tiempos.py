"""Ajusta los tiempos de voz-palabras.json a los límites EXACTOS de cada frase que dejó el montaje (voz-montaje.json).

Whisper acierta casi siempre dentro de la frase, pero en algunos bordes se corre hasta 1 s (sobre todo junto a
pausas largas). El montaje sabe dónde empieza y termina cada frase porque la pegó él: aquí se reescalan las
palabras de cada frase para que queden dentro de [inicio, fin] del montaje (con los márgenes del recorte).
Uso (después de alinear.py --sin-cortes): python3 scripts/ajustar_tiempos.py
"""

import json

MARGEN_INI = 0.03
MARGEN_FIN = 0.07


def main():
    mapa = {m["i"]: m for m in json.load(open("public/voz-montaje.json", encoding="utf-8"))}
    datos = json.load(open("public/voz-palabras.json", encoding="utf-8"))
    peor = 0.0
    for fr in datos["frases"]:
        m = mapa[fr["i"]]
        a, b = m["inicio"] + MARGEN_INI, m["fin"] - MARGEN_FIN
        ws = [p for p in datos["palabras"] if p["frase"] == fr["i"]]
        w0 = min(p["inicio"] for p in ws)
        w1 = max(p["inicio"] + p["duracion"] for p in ws)
        peor = max(peor, abs(w0 - a), abs(w1 - b))
        k = (b - a) / max(1e-3, w1 - w0)
        for p in ws:
            p["inicio"] = round(a + (p["inicio"] - w0) * k, 3)
            p["duracion"] = round(max(0.06, p["duracion"] * k), 3)
        fr["inicio"] = round(a, 3)
        fr["fin"] = round(b, 3)
    with open("public/voz-palabras.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    print(f"tiempos ajustados al montaje (el mayor desfase corregido: {peor:.2f} s)")


if __name__ == "__main__":
    main()
