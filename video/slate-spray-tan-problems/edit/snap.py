# Ajusta inicio/fin de cada toma al habla real sin invadir palabras vecinas; guarda work/edl.json
import json, wave, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from edl_src import SEGS
P = sys.argv[1]
words = json.load(open(f"{P}/work/words.json"))
cache = {}
def load(f):
    if f not in cache:
        w = wave.open(f"{P}/work/{f}.wav"); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        hop = int(w.getframerate() * 0.01); n = len(x) // hop
        e = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
        floor = np.percentile(e, 8)
        cache[f] = (e, floor)
    return cache[f]
def allw(f):
    return [w for s in words[f + ".wav"] for w in s["words"]]
out = []
for sid, f, s, e, role, txt in SEGS:
    env, floor = load(f); thr = floor + 14
    ws = allw(f)
    prev_end = max([w["e"] for w in ws if w["e"] <= s + 0.05] + [0.0])
    next_start = min([w["s"] for w in ws if w["s"] >= e - 0.05] + [len(env) / 100])
    lo = max(prev_end + 0.05, s - 0.4); hi = min(next_start - 0.05, e + 0.45)
    # inicio: primer frame > thr desde lo
    i0 = int(lo * 100); st = s
    for i in range(i0, int((s + 0.2) * 100)):
        if env[i] > thr and env[i + 1] > thr: st = i / 100; break
    # fin: último frame > thr antes de hi
    en = e
    for i in range(int(hi * 100), int((e - 0.3) * 100), -1):
        if env[i] > thr and env[i - 1] > thr: en = i / 100 + 0.01; break
    a, b = max(lo, st - 0.06), min(hi, en + 0.12)
    out.append({"id": sid, "src": f, "in": round(a, 3), "out": round(b, 3), "role": role, "text": txt})
    print(f"{sid} {f} floor={floor:5.1f} {s:6.2f}->{a:6.2f}  {e:6.2f}->{b:6.2f}  dur={b - a:5.2f}  win=[{lo:.2f},{hi:.2f}]")
json.dump(out, open(f"{P}/work/edl.json", "w"), indent=1)
print("total", round(sum(o["out"] - o["in"] for o in out), 2))
