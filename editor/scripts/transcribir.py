"""Transcribe un vídeo o audio con Whisper (faster-whisper) con tiempos por palabra.

Uso: python -I scripts/transcribir.py <video_o_audio> <salida.json> [modelo=large-v3-turbo]
Requiere: pip install faster-whisper numpy (y acceso a huggingface.co la primera vez, para bajar el modelo).
"""
import json
import subprocess
import sys
import time

import numpy as np
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
modelo = sys.argv[3] if len(sys.argv) > 3 else "large-v3-turbo"
t = time.time()
# Decodifica con ffmpeg (evita incompatibilidades de PyAV) a 16 kHz mono
pcm = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
    capture_output=True, check=True,
).stdout
audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
m = WhisperModel(modelo, device="cpu", compute_type="int8")
segs, info = m.transcribe(audio, language="es", word_timestamps=True, vad_filter=False, beam_size=5,
                          condition_on_previous_text=False)
words, segments = [], []
for s in segs:
    segments.append({"start": s.start, "end": s.end, "text": s.text.strip()})
    for w in s.words:
        words.append({"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3), "prob": round(w.probability, 3)})
json.dump({"model": modelo, "duration": info.duration, "segments": segments, "words": words},
          open(out, "w"), ensure_ascii=False, indent=1)
print(f"ok {len(words)} palabras en {time.time() - t:.0f}s")
for s in segments:
    print(f"[{s['start']:6.2f}-{s['end']:6.2f}] {s['text']}")
print("baja confianza:", [(w["text"], w["start"]) for w in words if w["prob"] < 0.7])
