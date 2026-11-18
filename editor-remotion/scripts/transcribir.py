#!/usr/bin/env python3
"""Transcribe un audio/vídeo con Whisper (faster-whisper large-v3) con tiempos por palabra.
Uso: transcribir.py <entrada> <salida.json> [idioma] [prompt]
Salida: JSON con lista de palabras {text,startMs,endMs,confidence} (tiempos relativos al archivo de origen)."""
import sys, json, subprocess
import numpy as np
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else None
prompt = sys.argv[4] if len(sys.argv) > 4 else None
model = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
# Decodifica con ffmpeg a PCM 16 kHz mono (evita depender de PyAV).
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     check=True, capture_output=True).stdout
audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
segments, info = model.transcribe(audio, language=lang, word_timestamps=True, vad_filter=False,
                                  beam_size=5, initial_prompt=prompt, condition_on_previous_text=False)
words, segs = [], []
for s in segments:
    segs.append({"start": s.start, "end": s.end, "text": s.text.strip()})
    for w in s.words or []:
        words.append({"text": w.word, "startMs": round(w.start * 1000), "endMs": round(w.end * 1000),
                      "confidence": round(w.probability, 3)})
json.dump({"language": info.language, "duration": info.duration, "segments": segs, "words": words},
          open(out, "w"), ensure_ascii=False, indent=1)
print(f"{src}: idioma={info.language} dur={info.duration:.2f}s palabras={len(words)}")
for s in segs: print(f"  [{s['start']:6.2f}-{s['end']:6.2f}] {s['text']}")
