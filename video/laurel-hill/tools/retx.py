import json, sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=4)
out = {}
for a, b in [(150, 175), (684, 712)]:
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", "voz.mp3", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    segs, _ = m.transcribe(np.frombuffer(pcm, dtype=np.float32), language="es", word_timestamps=True, beam_size=5,
                           initial_prompt="Chip Ganassi, Monessen, Pittsburgh, 500 Millas de Indianápolis, Pennsylvania Turnpike, Laurel Hill.")
    ws = []
    for s in segs:
        print(f"{a + s.start:7.2f} {s.text}", flush=True)
        ws += [{"w": w.word, "s": a + w.start, "e": a + w.end} for w in s.words]
    out[f"{a}-{b}"] = ws
json.dump(out, open("retx.json", "w"), ensure_ascii=False, indent=0)
