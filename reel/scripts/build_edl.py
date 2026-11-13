"""Construye la lista de cortes (EDL) del VIDEO BASE y remapea las palabras de Whisper al timeline final.

Entrada:  base16k.wav (audio del vídeo base) y base_words.json (Whisper large-v3, tiempos por palabra).
Salida:   src/data/edl.json  -> segmentos [{srcIn, srcOut, outIn}] en segundos (alineados a fotogramas de 30 fps)
          src/data/words.json -> palabras [{i, text, start, end}] en tiempo de salida

Reglas (estilo.md §1): silencios comprimidos a <=0,12 s, sin respiraciones, repeticiones fuera.
Uso: python3 build_edl.py <base16k.wav> <base_words.json> <carpeta src/data>
"""
import json
import subprocess
import sys

import numpy as np

FPS = 30
SR = 16000
wav, words_path, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-af", "highpass=f=80", "-ac", "1", "-ar", str(SR),
                      "-f", "s16le", "-"], check=True, capture_output=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
DUR = len(x) / SR
HOP = 160  # 10 ms
n = len(x) // HOP
env = 20 * np.log10(np.sqrt((x[: n * HOP].reshape(n, HOP) ** 2).mean(1)) + 1e-9)

# --- 1. Regiones de voz: energía > umbral, rellenando huecos < 180 ms -----------------
THR = -43.0
voiced = env > THR
regions, i = [], 0
while i < n:
    if voiced[i]:
        j = i
        while j < n and voiced[j]:
            j += 1
        regions.append([i * 0.01, j * 0.01])
        i = j
    else:
        i += 1
merged = []
for a, b in regions:
    if merged and a - merged[-1][1] < 0.18:
        merged[-1][1] = b
    else:
        merged.append([a, b])
speech = [r for r in merged if r[1] - r[0] > 0.08]

# --- 2. Cortes de contenido (tiempos de origen) -----------------------------------------
CONTENT_CUTS = [
    (0.0, 9.70),  # todo lo anterior a "silla en la que me estoy sentando" (correcciones del usuario, rondas 2 y 3)
    (21.63, 22.05),  # muletilla "eh" entre "realmente una" y "de estas piezas" (corrección del usuario)
    (33.29, 38.45),  # "Es más, algo que tal vez tú no sabes, tenemos metalmecánica" (repetido)
    (48.40, 49.75),  # "te quiero decir,"
    (59.33, 61.27),  # "es decir, de nuestra experiencia es"
]


def subtract(intervals, cuts):
    out = []
    for a, b in intervals:
        pieces = [(a, b)]
        for c0, c1 in cuts:
            nxt = []
            for p0, p1 in pieces:
                if c1 <= p0 or c0 >= p1:
                    nxt.append((p0, p1))
                    continue
                if p0 < c0:
                    nxt.append((p0, c0))
                if c1 < p1:
                    nxt.append((c1, p1))
            pieces = nxt
        out += [p for p in pieces if p[1] - p[0] > 0.06]
    return out


speech = subtract(speech, CONTENT_CUTS)


def snap_min(t, lo, hi):
    """Mueve un punto de corte al mínimo de energía dentro de [lo, hi]."""
    a, b = max(0, int(lo * 100)), min(n - 1, int(hi * 100))
    if b <= a:
        return t
    k = a + int(np.argmin(env[a:b]))
    return k * 0.01


# --- 3. Padding (máx. 60 ms por lado => hueco final <= 120 ms) y fusión ----------------
PAD = 0.06
segs = []
for k, (a, b) in enumerate(speech):
    prev_end = speech[k - 1][1] if k else 0.0
    next_start = speech[k + 1][0] if k + 1 < len(speech) else DUR
    a2 = max(a - PAD, (prev_end + a) / 2)
    b2 = min(b + PAD, (b + next_start) / 2)
    segs.append([a2, b2])

segs = [list(p) for p in subtract(segs, [(c0 - 0.005, c1) for c0, c1 in CONTENT_CUTS])]  # el padding nunca entra en un corte

# Fusiona segmentos casi contiguos (el hueco original ya era corto: no hay nada que quitar)
fused = []
for a, b in segs:
    if fused and a - fused[-1][1] < 0.02:
        fused[-1][1] = b
    else:
        fused.append([a, b])

# --- 4. Alinear a fotogramas -------------------------------------------------------------
edl, out_t = [], 0.0
for a, b in fused:
    fa = round(a * FPS)
    fb = int(b * FPS + 1e-6) if any(abs(b - c0) < 0.02 for c0, _ in CONTENT_CUTS) else round(b * FPS)
    if fb - fa < 3:
        continue
    edl.append({"srcIn": fa / FPS, "srcOut": fb / FPS, "outIn": round(out_t * FPS) / FPS})
    out_t += (fb - fa) / FPS

total = out_t


def src_to_out(t):
    for s in edl:
        if s["srcIn"] - 1e-6 <= t <= s["srcOut"] + 1e-6:
            return s["outIn"] + (t - s["srcIn"])
    return None


# --- 5. Palabras remapeadas + correcciones ortográficas ---------------------------------
FIX = {"evanistería": "ebanistería", "Ames": "Eames", "Creps": "Crepes", "and": "&", "macizo": "Macizo"}
d = json.load(open(words_path))
W = [w for s in d["segments"] for w in s["words"]]
words = []
# Correcciones manuales de tiempos de Whisper verificadas con la energía del audio
TIME_OVERRIDE = {93: (38.50, 38.70)}  # "La" (empresa): Whisper la sitúa dentro del silencio previo
for i, w in enumerate(W):
    s, e = TIME_OVERRIDE.get(i, (w["start"], w["end"]))
    # la palabra se conserva si solapa >= 40 ms con un segmento conservado (Whisper desplaza bordes)
    ov = [(min(e, g["srcOut"]) - max(s, g["srcIn"]), g) for g in edl]
    best = max(ov, key=lambda o: o[0])
    if e - s < 0.04:  # palabra de duración ~0 (p. ej. "la que"): basta con que caiga dentro
        best = next(((0.04, g) for g in edl if g["srcIn"] <= s <= g["srcOut"]), (0, None))
    if best[0] < 0.04:
        continue
    seg = best[1]
    s = max(s, seg["srcIn"])
    e = min(e, seg["srcOut"])
    raw_text = w["word"].strip()
    core = raw_text.strip(",.;:¿?¡!")
    text = raw_text.replace(core, FIX.get(core, core)) if core else raw_text
    words.append({"i": i, "text": text, "start": round(src_to_out(s), 3), "end": round(src_to_out(e), 3),
                  "src": round(w["start"], 2)})

json.dump({"fps": FPS, "duration": round(total, 3), "segments": edl}, open(f"{out_dir}/edl.json", "w"), indent=1)
json.dump(words, open(f"{out_dir}/words.json", "w"), ensure_ascii=False, indent=0)
print(f"segmentos: {len(edl)}  duración final: {total:.2f}s (origen {DUR:.2f}s)  palabras: {len(words)}/{len(W)}")
print(" ".join(f"{w['i']}:{w['text']}@{w['start']:.2f}" for w in words))
kept_idx = {w["i"] for w in words}
print("DESCARTADAS:", " ".join(f"{i}:{W[i]['word'].strip()}@{W[i]['start']:.2f}" for i in range(len(W)) if i not in kept_idx))
# tramos eliminados con su energía máxima (para detectar voz perdida)
prev = 0.0
for g in edl + [{"srcIn": DUR, "srcOut": DUR}]:
    a, b = prev, g["srcIn"]
    if b - a > 0.05:
        seg_env = env[int(a * 100):int(b * 100)]
        loud = (seg_env > -42).sum() * 0.01
        print(f"  quitado {a:6.2f}-{b:6.2f} ({b-a:4.2f}s) max {seg_env.max():5.1f}dB  >-42dB: {loud:.2f}s")
    prev = g["srcOut"]
