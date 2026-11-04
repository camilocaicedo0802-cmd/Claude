import json, subprocess, sys, time
import numpy as np
from faster_whisper import WhisperModel
audio, out, model_name = sys.argv[1], sys.argv[2], sys.argv[3]
t0 = time.time()
m = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
segs, info = m.transcribe(np.frombuffer(pcm, dtype=np.float32), language="es", word_timestamps=True, vad_filter=False, beam_size=5,
                          initial_prompt="Atlantic Avenue, Brooklyn, Nueva York, Long Island Rail Road, South Ferry, East River, Manhattan, Atlantic Street, Greenport, Stonington, Connecticut, Boston, Albany, Hunters Point, Queens, Walt Whitman, Brooklyn Standard, Bureau of Investigation, FBI, Ley Seca, Bob Diamond, Pratt Institute, John Wilkes Booth, Abraham Lincoln, Brooklyn Eagle, Howard Golden, Court Street, Borough Hall, Brooklyn Historic Railway Association, Red Hook, Hicks Street, National Geographic, Flatbush, Trader Joe's, Flatbush Avenue.")
res = []
for s in segs:
    res.append({"start": s.start, "end": s.end, "text": s.text, "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]})
    print(f"{s.start:7.2f} {s.text}", flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=0)
print("done", time.time() - t0)
