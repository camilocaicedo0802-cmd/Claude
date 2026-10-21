import sys, json
from faster_whisper import WhisperModel
m = WhisperModel("small.en", device="cpu", compute_type="int8")
import numpy as np, subprocess
aud = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
segs, _ = m.transcribe(aud, word_timestamps=True, vad_filter=False)
out=[]
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
    for w in s.words: out.append([round(w.start,2), round(w.end,2), w.word])
json.dump(out, open(sys.argv[2],"w"))
