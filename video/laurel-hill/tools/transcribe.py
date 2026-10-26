import json, sys, time
from faster_whisper import WhisperModel
audio, out, model_name = sys.argv[1], sys.argv[2], sys.argv[3]
t0 = time.time()
m = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
import subprocess, numpy as np
pcm = subprocess.run(["ffmpeg","-v","error","-i",audio,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True,check=True).stdout
samples = np.frombuffer(pcm, dtype=np.float32)
segs, info = m.transcribe(samples, language="es", word_timestamps=True, vad_filter=False, beam_size=5,
                          initial_prompt="Laurel Hill, Pensilvania, Pennsylvania Turnpike, Vanderbilt, Carnegie, Frick, J. P. Morgan, Corsair, Ganassi, IndyCar, Alex Palou, Dario Franchitti, Jamie McMurray, Ben Bowlby.")
res = []
for s in segs:
    res.append({"start": s.start, "end": s.end, "text": s.text,
                "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]})
    print(f"{s.start:7.2f} {s.text}", flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=0)
print("done", time.time() - t0)
