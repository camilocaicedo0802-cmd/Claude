"""Genera src/timeline.ts (60 fps) a partir de las transcripciones alineadas.

- Corta pausas > MAX_GAP (estilo.md §1: pausas internas ≤ 0,3 s): deja PAD_OUT tras la última
  palabra y PAD_IN antes de la siguiente. Cada tramo continuo es un segmento (jump cut).
- Los cortes se cuadran a fotogramas de la toma (30 fps); la línea de tiempo va a 60 fps.
- CUT="toma:desde-hasta,..." quita tramos enteros (en segundos de la toma).
"""
import json, os
FPS_SRC = 30
FPS = 60
TAKES = ["4846", "4863", "4843", "4868"]
MAX_GAP = 0.22
MIN_REMOVED = 0.15
PAD_OUT = 0.07
PAD_IN = 0.05
# Tramos fuera (decisión editorial; ver estilo.md §10 / mensaje al cliente):
#  4863 17.70–20.40 «porque eso es lo que está realizando» (frase confusa) · 4863 21.5– «Déjalo ahí» (fuera de guion)
CUT = {"4863": [(17.70, 20.40), (21.40, 99)], "4843": [(9.80, 10.60)]}
# 4843: fuera «Número uno,» (nunca dice «dos» ni «tres»: la enumeración la hace el gráfico 01·02·03).
# Pausas que se conservan entre las tres preguntas para que cada número tenga su golpe:
KEEP = {("4843", "comprarte,"): 0.6, ("4843", "ti"): 0.6}
FIX = {("4863", "ordenado,"): "desordenado,", ("4863", "eso"): None}  # «como ve todo desordenado» (la alineación lo confirma)

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
segments, words = [], []
t = 0.0
for take in TAKES:
    ws = json.load(open(os.path.join(root, "transcripciones", f"g4_{take}_alineado.json")))
    ws = [w for w in ws if not any(a <= w["s"] < b for a, b in CUT.get(take, []))]
    out_ws = []
    for w in ws:
        k = (take, w["text"])
        if k in FIX and FIX[k] is None and take == "4863" and 10.0 < w["s"] < 10.2:
            # «eso» unido a «desordenado»: se funde con la palabra siguiente
            continue
        if k in FIX and FIX[k]:
            w = dict(w, text=FIX[k])
        out_ws.append(w)
    ws = out_ws
    groups, cur = [], [ws[0]]
    for a, b in zip(ws, ws[1:]):
        gap = b["s"] - a["e"]
        keep = KEEP.get((take, a["text"]))
        if keep and gap <= keep:
            cur.append(b)
        elif gap > MAX_GAP and gap - (PAD_OUT + PAD_IN) >= MIN_REMOVED:
            groups.append(cur); cur = [b]
        else:
            cur.append(b)
    groups.append(cur)
    for g in groups:
        fin = round(max(0.0, g[0]["s"] - PAD_IN) * FPS_SRC)
        fout = round((g[-1]["e"] + PAD_OUT) * FPS_SRC)
        seg = dict(take=take, idx=len(segments), srcIn=fin / FPS_SRC, srcOut=fout / FPS_SRC, start=round(t, 4))
        segments.append(seg)
        for w in g:
            words.append(dict(text=w["text"], s=round(t + w["s"] - fin / FPS_SRC, 3), e=round(t + w["e"] - fin / FPS_SRC, 3), seg=seg["idx"], take=take))
        t += (fout - fin) / FPS_SRC
out = os.path.join(root, "src", "timeline.ts")
with open(out, "w") as f:
    f.write("// Generado por scripts/build_timeline.py. No editar a mano.\n")
    f.write("export type Segment = {take: string; idx: number; srcIn: number; srcOut: number; start: number};\n")
    f.write("export type Word = {text: string; s: number; e: number; seg: number; take: string};\n")
    f.write(f"export const SPEECH = {round(t, 4)}; // segundos de voz\n")
    f.write("export const SEGMENTS: Segment[] = " + json.dumps(segments, ensure_ascii=False) + ";\n")
    f.write("export const WORDS: Word[] = " + json.dumps(words, ensure_ascii=False, indent=0) + ";\n")
print(f"{len(segments)} segmentos, {len(words)} palabras, voz {t:.2f}s")
for s in segments:
    w_ = [w["text"] for w in words if w["seg"] == s["idx"]]
    print(f"{s['idx']:2d} {s['take']} src {s['srcIn']:6.2f}-{s['srcOut']:6.2f} -> tl {s['start']:6.2f}  {' '.join(w_)}")
