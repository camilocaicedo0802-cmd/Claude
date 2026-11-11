import sys, json, wave, numpy as np
def load(f):
    w=wave.open(f); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768; return a
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[1], device="cpu", compute_type="int8")
out = {}
for f in sys.argv[3:]:
    segs, info = m.transcribe(load(f), language="en", word_timestamps=True, vad_filter=False, beam_size=5)
    res = []
    for s in segs:
        res.append({"start": s.start, "end": s.end, "text": s.text, "words": [(w.start, w.end, w.word) for w in s.words]})
        print(f"{f.split('/')[-1]} [{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
    out[f.split('/')[-1]] = res
json.dump(out, open(sys.argv[2], "w"), indent=1)
