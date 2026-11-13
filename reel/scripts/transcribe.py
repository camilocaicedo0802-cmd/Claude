"""Transcribe un audio con faster-whisper (modelo Whisper large-v3) con tiempos por palabra.
Uso: python3 transcribe.py <audio> <salida.json> [idioma]
"""
import json, sys
import subprocess
import numpy as np
from faster_whisper import WhisperModel


def load_audio(path, sr=16000):
    """Decodifica con ffmpeg a PCM mono 16 kHz (evita la incompatibilidad de PyAV)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0

audio, out = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else None
model = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
segments, info = model.transcribe(
    load_audio(audio), language=lang, word_timestamps=True, vad_filter=True,
    beam_size=5, condition_on_previous_text=False,
)
res = {"language": info.language, "duration": info.duration, "segments": []}
for s in segments:
    res["segments"].append({
        "start": s.start, "end": s.end, "text": s.text.strip(),
        "words": [{"word": w.word, "start": w.start, "end": w.end, "prob": w.probability} for w in (s.words or [])],
    })
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}", flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
