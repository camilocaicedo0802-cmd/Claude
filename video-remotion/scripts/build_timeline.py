"""Genera src/v1/timeline.ts a partir de las transcripciones alineadas.

- Corta pausas: cuando el hueco entre palabras supera MAX_GAP, se deja PAD_OUT
  tras la última palabra y PAD_IN antes de la siguiente (estilo.md: sin pausas > 0,25 s).
- Cada tramo continuo es un "segmento" (jump cut). Las palabras se reubican en
  tiempo de la línea de tiempo.
"""
import json, os, sys
FPS = 30
# uso: build_timeline.py [id] [tomas...]   (por defecto, el video 1)
VID = sys.argv[1] if len(sys.argv) > 1 else "v1"
TAKES = sys.argv[2:] if len(sys.argv) > 2 else ["4871", "4857", "4858", "4865", "4864"]
MAX_GAP = 0.22
MIN_REMOVED = 0.15  # no cortar si se quitaría menos de esto (evita saltos inútiles)
PAD_OUT = 0.07
PAD_IN = 0.05
# Pausas que se conservan un poco más por intención dramática (texto de la palabra anterior)
KEEP_BREATH = {"Nadie,": 0.16, "negocio": 0.10} if VID == "v1" else {}

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
segments, words = [], []
t = 0.0
for take in TAKES:
    ws = json.load(open(os.path.join(root, "transcripciones", f"{VID}_{take}_alineado.json")))
    groups, cur = [], [ws[0]]
    for a, b in zip(ws, ws[1:]):
        gap = b["s"] - a["e"]
        keep = KEEP_BREATH.get(a["text"])
        if gap > MAX_GAP and gap - (PAD_OUT + PAD_IN) >= MIN_REMOVED and not (keep and gap <= keep + PAD_OUT + PAD_IN + 0.3):
            groups.append(cur); cur = [b]
        else:
            cur.append(b)
    groups.append(cur)
    # fuera tramos sueltos de muletillas (< 0,3 s solo con "y", "o", "pues", "eh"): solo meterían un salto
    FILLER = {"y", "o", "pues", "eh", "este"}
    groups = [g for g in groups if not (g[-1]["e"] - g[0]["s"] < 0.3 and all(w["text"].lower().strip(",.") in FILLER for w in g))]
    for gi, g in enumerate(groups):
        src_in = max(0.0, g[0]["s"] - PAD_IN)
        src_out = g[-1]["e"] + PAD_OUT
        if VID == "v1" and g[0]["text"] in ("Nadie,",):
            src_in = g[0]["s"] - 0.03
        # cuadrar a fotogramas
        fin = round(src_in * FPS); fout = round(src_out * FPS)
        seg = dict(take=take, idx=len(segments), srcIn=fin, srcOut=fout, start=round(t * FPS))
        segments.append(seg)
        for w in g:
            ws_ = (seg["start"] + (w["s"] * FPS - fin)) / FPS
            we_ = (seg["start"] + (w["e"] * FPS - fin)) / FPS
            words.append(dict(text=w["text"], s=round(ws_, 3), e=round(we_, 3), seg=seg["idx"], take=take))
        t += (fout - fin) / FPS
total = round(t * FPS)
out = os.path.join(root, "src", VID, "timeline.ts")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    f.write("// Generado por scripts/build_timeline.py. No editar a mano.\n")
    f.write("import type {Segment, Word} from '../engine/types';\n") if VID != "v1" else (f.write("export type Segment = {take: string; idx: number; srcIn: number; srcOut: number; start: number};\n"), f.write("export type Word = {text: string; s: number; e: number; seg: number; take: string};\n"))
    f.write(f"export const SPEECH_FRAMES = {total};\n")
    f.write("export const SEGMENTS: Segment[] = " + json.dumps(segments, ensure_ascii=False) + ";\n")
    f.write("export const WORDS: Word[] = " + json.dumps(words, ensure_ascii=False, indent=0) + ";\n")
print(f"{len(segments)} segmentos, {len(words)} palabras, voz {t:.2f}s ({total} f)")
for s in segments:
    ws = [w["text"] for w in words if w["seg"] == s["idx"]]
    print(f"{s['idx']:2d} {s['take']} src {s['srcIn']/FPS:6.2f}-{s['srcOut']/FPS:6.2f} -> tl {s['start']/FPS:6.2f}  {' '.join(ws)}")
