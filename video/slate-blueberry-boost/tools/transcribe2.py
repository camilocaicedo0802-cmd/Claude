import sys, json, subprocess, numpy as np
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
raw=subprocess.run(["ffmpeg","-v","error","-i",src,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
audio=np.frombuffer(raw,dtype=np.float32)
m = WhisperModel(sys.argv[3] if len(sys.argv)>3 else "medium", device="cpu", compute_type="int8")
segs, info = m.transcribe(audio, word_timestamps=True, language="en", vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=300), condition_on_previous_text=False,
    initial_prompt="Radiant Blueberry Boost facial at Slate in Tulsa. Gua sha, hyaluronic serum, chilled facial globes.")
words=[]
for s in segs:
    line=[]
    for w in s.words:
        words.append({"w": w.word.strip(), "s": round(w.start,2), "e": round(w.end,2), "p": round(w.probability,2)})
        line.append(f"{w.word.strip()}@{w.start:.2f}")
    print(f"[{s.start:6.2f}-{s.end:6.2f}] " + " ".join(line))
json.dump(words, open(out,"w"), ensure_ascii=False)
