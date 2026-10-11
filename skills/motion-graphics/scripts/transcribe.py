#!/usr/bin/env python3
"""
Transcribe la locución con Whisper (tiempos por palabra) y genera subtítulos para Remotion.

Corrige el retraso típico de Whisper tras una pausa (llega 0.1–0.3 s tarde): la primera palabra
después de un silencio se ancla al inicio real de la voz según la envolvente de energía.

Salida en <outdir>:
  words.json     [{i, text, start, end, p}]
  captions.ts    export const captions: Caption[] (tipo de @remotion/captions), con el índice de cada palabra comentado
  transcript.txt texto plano
Uso:
  python3 transcribe.py voz.mp3 video/src/data --model medium --lang es
"""
import argparse
import json
import os

import numpy as np


def as_wav(path):
    """librosa/soundfile no leen mp4/mov: extrae el audio a un wav temporal con ffmpeg."""
    import os
    import subprocess
    import tempfile

    if path.lower().endswith((".wav", ".mp3", ".flac", ".ogg")):
        return path
    tmp = os.path.join(tempfile.gettempdir(), "mg_" + os.path.basename(path) + ".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "1", "-ar", "16000", tmp], check=True)
    return tmp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("outdir")
    ap.add_argument("--model", default="medium")
    ap.add_argument("--lang", default=None)
    ap.add_argument("--from-json", default=None, help="reutilizar una salida JSON de whisper ya existente")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    if a.from_json:
        W = json.load(open(a.from_json))
    else:
        import whisper

        W = whisper.load_model(a.model).transcribe(a.audio, language=a.lang, word_timestamps=True)
        json.dump(W, open(os.path.join(a.outdir, "whisper_raw.json"), "w"), ensure_ascii=False)

    import librosa

    y, sr = librosa.load(as_wav(a.audio), sr=16000)
    hop = 160
    dbs = 20 * np.log10(librosa.feature.rms(y=y, frame_length=480, hop_length=hop)[0] + 1e-9)
    thr = np.percentile(dbs, 95) - 30
    t = np.arange(len(dbs)) * hop / sr
    regions, s = [], None
    for i, v in enumerate(dbs < thr):
        if v and s is None:
            s = i
        if not v and s is not None:
            if (i - s) * hop / sr >= 0.15:
                regions.append((t[s], t[i]))
            s = None

    words = [dict(text=w["word"].strip(), start=float(w["start"]), end=float(w["end"]), p=w.get("probability")) for seg in W["segments"] for w in seg.get("words", [])]
    fixed = 0
    for i, w in enumerate(words):
        for ra, rb in regions:
            first_after = i == 0 or (words[i - 1]["end"] <= ra + 0.5 and words[i - 1]["start"] < ra)
            if rb - 0.45 <= w["start"] <= rb + 0.45 and first_after:
                if i > 0:
                    words[i - 1]["end"] = min(words[i - 1]["end"], ra + 0.05)
                j0 = int(rb * sr / hop)
                j = j0
                while j < min(len(dbs), j0 + 40) and dbs[j] < thr + 12:
                    j += 1
                new = round(float(max(rb, t[min(j, len(t) - 1)] - 0.03)), 3)
                if abs(new - w["start"]) > 0.02:
                    fixed += 1
                w["start"] = new
                break
    for i, w in enumerate(words):
        if i + 1 < len(words):
            w["end"] = min(w["end"], words[i + 1]["start"])
        if w["end"] <= w["start"]:
            w["end"] = w["start"] + 0.08

    json.dump([{"i": i, **w} for i, w in enumerate(words)], open(os.path.join(a.outdir, "words.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(a.outdir, "transcript.txt"), "w").write(W.get("text", "").strip() + "\n")
    lines = [
        "// Generado por transcribe.py (Whisper, tiempos por palabra; inicios corregidos tras pausas).",
        "// El número comentado es el índice de cada palabra: úsalo para referenciar rangos en las escenas.",
        'import type { Caption } from "@remotion/captions";',
        "",
        "export const captions: Caption[] = [",
    ]
    for i, w in enumerate(words):
        c = {
            "text": (" " if i else "") + w["text"],
            "startMs": round(w["start"] * 1000),
            "endMs": round(w["end"] * 1000),
            "timestampMs": round((w["start"] + w["end"]) * 500),
            "confidence": round(w["p"], 3) if w["p"] is not None else None,
        }
        lines.append(f"  /* {i:3d} */ {json.dumps(c, ensure_ascii=False)},")
    lines.append("];")
    open(os.path.join(a.outdir, "captions.ts"), "w").write("\n".join(lines) + "\n")
    for i, w in enumerate(words):
        print(f"{i:3d} {w['start']:7.2f} {w['end']:7.2f}  {w['text']}")
    print(f"\n{len(words)} palabras · {fixed} inicios corregidos tras pausas · silencios: {len(regions)}")


if __name__ == "__main__":
    main()
