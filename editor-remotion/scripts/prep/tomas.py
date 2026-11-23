"""Parte cada transcripción en «tomas» (una frase por toma) con ritmo y nivel, para elegir la mejor: material/tomas.json"""
import json, re, glob, os, numpy as np, librosa

tomas = []
for f in sorted(glob.glob("material/transcripciones/*.json")):
    n = os.path.basename(f)[:-5]
    r = json.load(open(f))
    words = [dict(w=w["word"].strip(), s=float(w["start"]), e=float(w["end"])) for s in r["segments"] for w in s.get("words", []) if w["word"].strip()]
    y, _ = librosa.load(f"material/audio16k/{n}.wav", sr=16000)
    cur = []

    def flush():
        global cur
        if not cur:
            return
        a, b = cur[0]["s"], cur[-1]["e"]
        seg = y[int(a * 16000):int(b * 16000)]
        db = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)
        gaps = [cur[i + 1]["s"] - cur[i]["e"] for i in range(len(cur) - 1)]
        k = len([t for t in tomas if t["clip"] == n]) + 1
        tomas.append(dict(clip=n, id=f"{n}_{k}", start=round(a, 2), end=round(b, 2), dur=round(b - a, 2), wps=round(len(cur) / (b - a), 2),
                          db=round(float(db), 1), maxgap=round(max(gaps), 2) if gaps else 0, text=" ".join(w["w"] for w in cur), words=cur))
        cur = []

    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if nxt is None or re.search(r"[.?!]$", w["w"]) or (nxt["s"] - w["e"] > 0.9):
            flush()

json.dump(tomas, open("material/tomas.json", "w"), ensure_ascii=False, indent=1)
for t in tomas:
    print(f"{t['id']:15s} {t['start']:6.2f}-{t['end']:6.2f} {t['dur']:5.2f}s {t['wps']:.1f} pal/s {t['db']:6.1f} dB | {t['text'][:110]}")
