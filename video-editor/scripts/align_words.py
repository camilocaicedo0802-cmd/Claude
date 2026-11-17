"""Alineación forzada palabra a palabra (torchaudio MMS_FA, CTC multilingüe).
Entrada: JSON [{"id":..., "start":s, "end":s, "text":"texto exacto"}] con tiempos del
archivo original. Salida: mismas entradas + "words":[{text,start,end,score}] en
segundos absolutos. Uso: python3 -I align_words.py <audio> <entrada.json> <salida.json>"""
import json, re, subprocess, sys, unicodedata
import numpy as np
import torch, torchaudio

audio, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
bundle = torchaudio.pipelines.MMS_FA
model = bundle.get_model(with_star=False).eval()
DICT = bundle.get_dict(star=None)
SR = bundle.sample_rate
NUM = {"305": "three o five", "4": "cuatro", "1": "uno"}

def norm(word):
    w = NUM.get(word.strip("¿?¡!.,"), word)
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z' ]", "", w).strip()

def load(a, b):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", audio, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return torch.from_numpy(np.frombuffer(pcm, np.float32).copy()).unsqueeze(0)

items = json.load(open(src))
for it in items:
    wav = load(it["start"], it["end"])
    display = it["text"].split()
    tokens_per_word = []
    for w in display:
        n = norm(w)
        tokens_per_word.append([DICT[c] for c in n.replace(" ", "") if c in DICT])
    flat = [t for tw in tokens_per_word for t in tw]
    with torch.inference_mode():
        emission, _ = model(wav)
        aligned, scores = torchaudio.functional.forced_align(emission, torch.tensor([flat], dtype=torch.int32), blank=0)
    aligned, scores = aligned[0], scores[0].exp()
    spans = torchaudio.functional.merge_tokens(aligned, scores)
    ratio = wav.shape[1] / emission.shape[1] / SR
    words, k = [], 0
    for w, tw in zip(display, tokens_per_word):
        seg = spans[k:k + len(tw)]
        k += len(tw)
        words.append({"text": w, "start": round(it["start"] + seg[0].start * ratio, 3),
                      "end": round(it["start"] + seg[-1].end * ratio, 3),
                      "score": round(float(np.mean([s.score for s in seg])), 2)})
    it["words"] = words
    print(f'[{it["id"]}] ' + " ".join(f'{w["text"]}({w["start"]:.2f}-{w["end"]:.2f}|{w["score"]})' for w in words), flush=True)
json.dump(items, open(dst, "w"), ensure_ascii=False, indent=1)
