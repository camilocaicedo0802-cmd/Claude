import json, subprocess, sys, time
import numpy as np
from faster_whisper import WhisperModel
audio, out, model_name = sys.argv[1], sys.argv[2], sys.argv[3]
t0 = time.time()
m = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
segs, info = m.transcribe(np.frombuffer(pcm, dtype=np.float32), language="es", word_timestamps=True, vad_filter=False, beam_size=5,
                          initial_prompt="Cumberland Gap, Kentucky, Virginia, Tennessee, US-25E, Massacre Mountain, Apalaches, Cumberland Mountains, shawnee, cherokee, Thomas Walker, Cave Gap, Athiamiowee, Daniel Boone, Wilderness Road, Powell Valley, delaware, Middlesboro, Dixie Highway, Cumberland Gap National Historical Park, Richard Nixon, Ronald Reagan, Hal Rogers, Donald Hodel, Thomas Clark, Knoxville, Lexington.")
res = []
for s in segs:
    res.append({"start": s.start, "end": s.end, "text": s.text, "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]})
    print(f"{s.start:7.2f} {s.text}", flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=0)
print("done", time.time() - t0)
