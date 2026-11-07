import sys, json
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[3], device="cpu", compute_type="int8")
import scipy.io.wavfile as wf, numpy as np
sr,a=wf.read(sys.argv[1]); a=a.astype(np.float32)/32768.0
segs, info = m.transcribe(a, language=sys.argv[4] if len(sys.argv)>4 else None, word_timestamps=True, vad_filter=False, beam_size=5)
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end,"p":w.probability} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
json.dump(out, open(sys.argv[2],"w"), ensure_ascii=False, indent=1)
