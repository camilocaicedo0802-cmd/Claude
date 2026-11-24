"""Transcribe un archivo con Whisper (faster-whisper) y guarda tiempos por palabra.
Uso: python3 scripts/transcribir.py <entrada> <salida.json> [idioma] [modelo]
Salida: lista de Caption de Remotion {text,startMs,endMs,timestampMs,confidence}
"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

src, dst = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else "es"
model_name = sys.argv[4] if len(sys.argv) > 4 else "large-v3"

pcm = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
    capture_output=True, check=True,
).stdout
audio = np.frombuffer(pcm, dtype=np.float32)

model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
segments, info = model.transcribe(
    audio, language=lang, word_timestamps=True, beam_size=5,
    vad_filter=False, condition_on_previous_text=False,
)
captions = []
for seg in segments:
    for w in seg.words:
        captions.append({
            "text": w.word if w.word.startswith(" ") else " " + w.word,
            "startMs": round(w.start * 1000),
            "endMs": round(w.end * 1000),
            "timestampMs": round((w.start + w.end) / 2 * 1000),
            "confidence": round(float(w.probability), 3),
        })
        print(f"{w.start:7.2f} {w.end:7.2f} {w.probability:.2f} {w.word}", flush=True)
json.dump(captions, open(dst, "w"), ensure_ascii=False, indent=1)
print(f"OK {len(captions)} palabras -> {dst}")
