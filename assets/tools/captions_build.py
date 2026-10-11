"""Whisper (tiempos por palabra) -> Caption[] de Remotion, con inicios corregidos tras pausas
usando la envolvente de energía de la voz (Whisper tiende a llegar 0.1–0.3 s tarde tras un silencio)."""
import json, numpy as np, librosa
W = json.load(open("/home/user/Claude/transcripcion/voz.json"))
y, sr = librosa.load("/home/user/Claude/video/public/audio/voz.mp3", sr=16000)
hop = 160
rms = librosa.feature.rms(y=y, frame_length=480, hop_length=hop)[0]
dbs = 20 * np.log10(rms + 1e-9)
thr = np.percentile(dbs, 95) - 30
t = np.arange(len(dbs)) * hop / sr
sil = dbs < thr
regions = []; s = None
for i, v in enumerate(sil):
    if v and s is None: s = i
    if (not v) and s is not None:
        if (i - s) * hop / sr >= 0.15: regions.append((t[s], t[i]))
        s = None
words = [dict(text=w["word"].strip(), start=w["start"], end=w["end"], p=w.get("probability")) for seg in W["segments"] for w in seg["words"]]
for i, w in enumerate(words):
    for a, b in regions:
        if b - 0.45 <= w["start"] <= b + 0.45 and (i == 0 or (words[i - 1]["end"] <= a + 0.5 and words[i - 1]["start"] < a)):
            if i > 0: words[i - 1]["end"] = min(words[i - 1]["end"], a + 0.05)
            # inicio = primera trama con voz clara (thr + 12 dB) tras el silencio, menos 30 ms
            j0 = int(b * sr / hop); j = j0
            while j < min(len(dbs), j0 + 40) and dbs[j] < thr + 12: j += 1
            w["start"] = round(float(max(b, t[j] - 0.03)), 3)
            break
for i, w in enumerate(words):
    if i + 1 < len(words): w["end"] = min(w["end"], words[i + 1]["start"])
    if w["end"] <= w["start"]: w["end"] = w["start"] + 0.08
caps = [{"text": (" " if i else "") + w["text"], "startMs": round(w["start"] * 1000), "endMs": round(w["end"] * 1000),
         "timestampMs": round((w["start"] + w["end"]) * 500), "confidence": round(w["p"], 3) if w["p"] is not None else None}
        for i, w in enumerate(words)]
lines = ["// Generado por assets/tools/captions_build.py a partir de Whisper (medium, tiempos por palabra).",
         "// Índice de cada palabra = posición en este array. No editar a mano: regenerar.",
         'import type { Caption } from "@remotion/captions";', "", "export const captions: Caption[] = ["]
for i, c in enumerate(caps):
    lines.append(f"  /* {i:2d} */ {json.dumps(c, ensure_ascii=False)},")
lines.append("];")
open("/home/user/Claude/video/src/data/captions.ts", "w").write("\n".join(lines) + "\n")
for i, c in enumerate(caps): print(i, repr(c["text"]), c["startMs"], c["endMs"])
