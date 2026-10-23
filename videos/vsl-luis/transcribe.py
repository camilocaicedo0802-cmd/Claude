#!/usr/bin/env python3
"""Word-level Spanish transcription of the raw take (timestamps on the raw timeline).

Usage:
    python3 transcribe.py <audio16k.wav> <model: medium|large-v3> <words.json>

Needs `pip install faster-whisper`. The audio must be 16 kHz mono 16-bit WAV.
"""
import json
import sys
import wave

import numpy as np
from faster_whisper import WhisperModel

src, model_name, out = sys.argv[1:4]
with wave.open(src) as wf:
    audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768

model = WhisperModel(model_name, device="cpu", compute_type="int8")
segments, _ = model.transcribe(audio, language="es", word_timestamps=True, vad_filter=False, beam_size=5)
words = []
for seg in segments:
    print(f"[{seg.start:6.2f}-{seg.end:6.2f}] {seg.text}")
    for w in seg.words:
        words.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 2)})
json.dump(words, open(out, "w"), ensure_ascii=False, indent=0)
