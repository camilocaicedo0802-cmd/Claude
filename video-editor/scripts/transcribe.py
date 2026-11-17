"""Transcribe un audio con Whisper (faster-whisper large-v3) y escribe
captions en el formato `Caption` de @remotion/captions (tiempos por palabra).
Uso: python3 -I transcribe.py <audio> <salida.json> [idioma]
"""
import json
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel

audio, out = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else "es"
model = WhisperModel(
    "large-v3",
    device="cpu",
    compute_type="int8",
    download_root="/home/user/Claude/video-editor/.models",
)
pcm = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
    check=True,
    capture_output=True,
).stdout
waveform = np.frombuffer(pcm, dtype=np.float32)
segments, info = model.transcribe(
    waveform,
    language=lang,
    word_timestamps=True,
    vad_filter=False,
    beam_size=5,
    condition_on_previous_text=False,
)
captions = []
for seg in segments:
    for w in seg.words or []:
        captions.append(
            {
                "text": w.word if w.word.startswith(" ") else " " + w.word,
                "startMs": round(w.start * 1000),
                "endMs": round(w.end * 1000),
                "timestampMs": round((w.start + w.end) / 2 * 1000),
                "confidence": round(w.probability, 3),
            }
        )
    print(f"[{seg.start:7.2f} -> {seg.end:7.2f}] {seg.text}", flush=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(captions, f, ensure_ascii=False, indent=1)
print("words:", len(captions))
