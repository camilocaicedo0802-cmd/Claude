import json, sys, subprocess, numpy as np
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
raw = subprocess.run(["ffmpeg","-v","error","-i",src,"-ar","16000","-ac","1","-f","s16le","-"],capture_output=True,check=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32)/32768
m = WhisperModel(sys.argv[3] if len(sys.argv)>3 else "small", device="cpu", compute_type="int8")
segs,_ = m.transcribe(a, language="es", word_timestamps=True, condition_on_previous_text=False)
res=[{"s":s.start,"e":s.end,"t":s.text,"words":[{"s":w.start,"e":w.end,"w":w.word.strip()} for w in s.words]} for s in segs]
json.dump(res, open(out,"w"), ensure_ascii=False)
print(len(res), "segmentos", sum(len(s["words"]) for s in res), "palabras")
