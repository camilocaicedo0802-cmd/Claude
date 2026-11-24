#!/usr/bin/env python3
"""Límites precisos de cada frase en un clip con voz: tiempos de Gemini ajustados con la energía del audio."""
import json, subprocess, numpy as np, re

def envelope(src, sr=16000, hop=0.01):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    h = int(sr * hop); n = len(x) // h
    rms = np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    return db, hop

def norm(w):
    return re.sub(r'[^\wáéíóúñü0-9]', '', w.lower())

def line_spans(src, words_json, starts, pad0=0.06, pad1=0.10):
    """starts: lista con las primeras palabras (2) de cada frase, en orden. Devuelve [(t0, t1)]."""
    W = json.load(open(words_json))
    db, hop = envelope(src)
    floor = np.percentile(db, 20); thr = floor + 0.35 * (np.percentile(db, 95) - floor)
    idx, i = [], 0
    for st in starts:
        toks = [norm(t) for t in st.split()]
        while i < len(W) and not all(norm(W[i + k]['w']) == toks[k] for k in range(len(toks)) if i + k < len(W)):
            i += 1
        idx.append(i); i += 1
    out = []
    for j, a in enumerate(idx):
        b = (idx[j + 1] - 1) if j + 1 < len(idx) else len(W) - 1
        s, e = float(W[a]['s']), float(W[b].get('e', W[b]['s'] + 0.4))
        nxt = float(W[idx[j + 1]]['s']) if j + 1 < len(idx) else len(db) * hop
        prv = out[-1][1] if out else 0.0
        # inicio: retroceder hasta el silencio (máx. 0,25 s)
        k = int(s / hop)
        while k > 0 and k > int((s - 0.25) / hop) and db[k - 1] > thr and (k - 1) * hop > prv:
            k -= 1
        t0 = max(prv, k * hop - pad0)
        # fin: avanzar hasta el silencio, sin pasar el inicio de la frase siguiente
        k = int(max(e, s + 0.3) / hop)
        lim = int(min(nxt - 0.05, e + 0.6) / hop)
        while k < min(len(db) - 1, lim) and db[k] > thr:
            k += 1
        t1 = min(k * hop + pad1, nxt - 0.02)
        out.append((round(t0, 3), round(t1, 3)))
    return out

if __name__ == '__main__':
    import sys
    print(line_spans(sys.argv[1], sys.argv[2], sys.argv[3].split('|')))
