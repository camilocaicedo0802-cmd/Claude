import json, sys, glob, os
import numpy as np, scipy.io.wavfile as wf
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
prompt = sys.argv[3] if len(sys.argv) > 3 else None
out = {}
for f in sorted(glob.glob(sys.argv[1] + '/*.wav')):
    sr, a = wf.read(f); a = a.astype(np.float32) / 32768
    segs, info = m.transcribe(a, word_timestamps=True, initial_prompt=prompt, vad_filter=False)
    ws = []; seg_out = []
    for s in segs:
        seg_out.append({"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text.strip()})
        ws += [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)} for w in s.words]
    out[os.path.basename(f)] = {"lang": info.language, "segs": seg_out, "words": ws, "dur": len(a) / sr}
    print('==', os.path.basename(f), f"{len(a)/sr:.1f}s", info.language, flush=True)
    for s in seg_out: print(f"  [{s['s']:6.2f}-{s['e']:6.2f}] {s['t']}", flush=True)
json.dump(out, open(sys.argv[2], 'w'), indent=1)
