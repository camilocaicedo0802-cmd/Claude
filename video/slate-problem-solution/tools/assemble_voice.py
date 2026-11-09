import os
import sys, json, numpy as np, soundfile as sf
sys.path.insert(0, sys.argv[1]); from voice_edl import EDL, CLIPS
talk = sys.argv[2]; out = sys.argv[3]
SR = 48000; HOP = 480  # 10 ms
GAP = float(sys.argv[4]) if len(sys.argv) > 4 else 0.14     # pause between segments
MAXSIL = 0.22; KEEPSIL = 0.12                                   # compress internal silences
src = {k: sf.read(f"{talk}/{v}.wav", dtype="float32")[0] for k, v in CLIPS.items()}
def env_db(x):
    e = np.sqrt(np.convolve(x**2, np.ones(HOP*2)/(HOP*2), "same"))[::HOP]
    return 20*np.log10(e + 1e-9)
_tone = {}
def room_tone(c, n):
    """Quietest 0.6 s of the clip (real room tone, not digital silence), faded at both ends."""
    if c not in _tone:
        x = src[c]; win = int(0.6*SR); hop = int(0.05*SR)
        e = np.array([np.sqrt((x[k:k+win]**2).mean()) for k in range(0, len(x)-win, hop)])
        ok = np.where(e > 1e-5)[0]; k = ok[np.argmin(e[ok])] * hop
        _tone[c] = x[k:k+win].copy()
    y = np.resize(_tone[c], n).astype(np.float32); f = int(0.01*SR)
    y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    return y
pieces = []; tl = 0.0; voice = []
for i, (c, a, b, txt) in enumerate(EDL):
    x = src[c]; db = env_db(x); floor = np.percentile(db, 8); thr = floor + 10
    ia, ib = int(a*100), int(b*100)
    # refine start: move to first frame above thr, minus 40 ms
    seg = db[ia:ib]; act = np.where(seg > thr)[0]
    s = ia + max(0, act[0] - 4); e = ia + min(len(seg) + (30 if i == len(EDL)-1 else 0), act[-1] + (28 if i == len(EDL)-1 else 10))
    if os.environ.get('NOREFINE'): s, e = ia, ib
    # find internal silences
    on = db[s:e] > thr; runs = []; j = 0
    while j < len(on):
        if not on[j]:
            k = j
            while k < len(on) and not on[k]: k += 1
            if (k - j)/100 > MAXSIL and (len(on) - k) >= 15 and (e - s) > 250: runs.append((j, k))   # only compress long phrases
            j = k
        else: j += 1
    keep = []; cur = s
    for (j, k) in runs:
        cut0 = s + j + int(KEEPSIL*50); cut1 = s + k - int(KEEPSIL*50)
        keep.append((cur, cut0)); cur = cut1
    keep.append((cur, e))
    for (p0, p1) in keep:
        y = x[p0*HOP:p1*HOP].copy(); f = int(0.008*SR)
        y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
        voice.append(y)
        pieces.append({"seg": i, "clip": CLIPS[c], "src0": p0/100, "src1": p1/100, "t0": round(tl, 3), "t1": round(tl + len(y)/SR, 3)})
        tl += len(y)/SR
    if i < len(EDL) - 1:
        voice.append(room_tone(c, int(GAP*SR))); tl += GAP
v = np.concatenate(voice)
sf.write(out, v, SR, subtype="PCM_24")
json.dump(pieces, open(out.replace(".wav", "_map.json"), "w"), indent=1)
print("total", round(len(v)/SR, 2), "s;", len(pieces), "pieces")
for p in pieces: print(p)
