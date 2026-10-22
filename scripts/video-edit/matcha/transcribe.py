"""Spanish transcription with word timestamps (faster-whisper large-v3, CPU).

Usage: python3 transcribe.py <voice_16k_mono.wav> <words_raw.json>
The raw output is then corrected by hand into words.json (e.g. "helado" -> "la hoja").
"""
import json, sys
import numpy as np
import scipy.io.wavfile as wf
from faster_whisper import WhisperModel

m = WhisperModel("large-v3", device="cpu", compute_type="int8")
sr, a = wf.read(sys.argv[1])
segs, info = m.transcribe(a.astype(np.float32) / 32768.0, language="es", word_timestamps=True, beam_size=5)
out = []
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
    for w in s.words:
        out.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=0)
