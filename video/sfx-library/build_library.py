"""Dedupe the client's SFX packs (by decoded-audio hash), convert to 48 kHz WAV, measure, categorise."""
import os, sys, glob, hashlib, subprocess, json, re, unicodedata
import numpy as np
SRC = sys.argv[1]; OUT = sys.argv[2]
os.makedirs(OUT + '/audio', exist_ok=True)
AUD = ('.wav', '.mp3', '.m4a', '.mpeg', '.aif', '.aiff', '.ogg', '.flac')

def decode(p):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-vn', '-ac', '2', '-ar', '48000', '-f', 'f32le', '-'],
                       capture_output=True)
    if r.returncode or not r.stdout:
        return None
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2)

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'^copia de ', '', s, flags=re.I)
    s = re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_').lower()
    return s

CATS = [
    ('typing', r'type|typing|teclado|tecla|keyboard|8-bit game'),
    ('click', r'mouse click|lighter|camera roll click|click(?!.*shutter)'),
    ('camera', r'shutter|camera|camara|cam_|flash|focusing'),
    ('whoosh', r'whoosh|woosh|swoosh|swhoosh|whip|transicion'),
    ('riser', r'riser|riseer|rise'),
    ('impact', r'boom|impact|hit|bass drop|sub bass|bass|grand hit|downer'),
    ('drone', r'drone|pulse|wind|thunder|ambient|warhorn'),
    ('pop', r'pop|snapchat|notification|disappear|among us|windows|acierto|censored|chasquido|cash'),
    ('marker', r'marker|rotulador|subrayado|resaltador|highlighter|bol.grafo|pen'),
    ('glass', r'glass|vidrio|foco|crash'),
    ('misc', r'.'),
]

def cat(name):
    n = name.lower()
    for c, rx in CATS:
        if re.search(rx, n):
            return c
    return 'misc'

seen = {}; lib = []
files = sorted(p for p in glob.glob(SRC + '/**/*', recursive=True) if p.lower().endswith(AUD))
for p in files:
    x = decode(p)
    if x is None or len(x) < 100:
        print('skip', p); continue
    h = hashlib.md5(np.round(x[:48000 * 3:7], 3).tobytes()).hexdigest()
    base = os.path.splitext(os.path.basename(p))[0]
    if h in seen:
        seen[h]['dupes'].append(os.path.relpath(p, SRC)); continue
    c = cat(base)
    name = slug(base)
    out = f'{OUT}/audio/{c}/{name}.wav'
    k = 2
    while os.path.exists(out):
        out = f'{OUT}/audio/{c}/{name}_{k}.wav'; k += 1
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-vn', '-ar', '48000', '-c:a', 'pcm_s16le', out], check=True)
    mono = x.mean(1)
    peak = float(np.abs(x).max())
    env = np.sqrt(np.convolve(mono ** 2, np.ones(480) / 480, 'same'))
    onset = float(np.argmax(env > env.max() * 0.3) / 48000)
    pk_t = float(np.argmax(env) / 48000)
    e = {'file': os.path.relpath(out, OUT), 'name': base, 'cat': c, 'dur': round(len(x) / 48000, 3),
         'peak_db': round(20 * np.log10(peak + 1e-9), 1), 'onset': round(onset, 3), 'peak_t': round(pk_t, 3),
         'source': os.path.relpath(p, SRC), 'dupes': []}
    seen[h] = e; lib.append(e)
json.dump(lib, open(OUT + '/library.json', 'w'), indent=1, ensure_ascii=False)
from collections import Counter
print(len(files), 'files ->', len(lib), 'unique'); print(Counter(e['cat'] for e in lib))

# ---- split the "25 sonidos de transiciones" compilation into single sounds
import scipy.io.wavfile as wf
comp = [e for e in lib if e['name'].startswith('25 sonidos')]
if comp:
    comp = comp[0]
    sr, x = wf.read(OUT + '/' + comp['file']); x = x.astype(np.float32) / 32768
    env = np.convolve(np.abs(x).max(1), np.ones(2400) / 2400, 'same'); act = env > 10 ** (-45 / 20)
    segs, i, n, gap = [], 0, len(act), int(0.35 * sr)
    while i < n:
        if act[i]:
            j = last = i
            while j < n and (j - last) < gap:
                if act[j]: last = j
                j += 1
            segs.append((i, last)); i = j
        else:
            i += 1
    segs = [(a, b) for a, b in segs if (b - a) / sr > 0.12]
    for k, (a, b) in enumerate(segs, 1):
        a = max(0, a - 480); b = min(n, b + 2400)
        y = x[a:b].copy(); f = 192; y[:f] *= np.linspace(0, 1, f)[:, None]; y[-f:] *= np.linspace(1, 0, f)[:, None]
        fn = f'audio/whoosh/transicion_{k:02d}.wav'
        wf.write(OUT + '/' + fn, sr, (y * 32767).astype(np.int16))
        e = np.abs(y).max(1); pk = float(np.argmax(np.convolve(e, np.ones(480) / 480, 'same')) / sr)
        lib.append({'file': fn, 'name': f'Transicion {k:02d}', 'cat': 'whoosh', 'dur': round(len(y) / sr, 3),
                    'peak_db': round(float(20 * np.log10(e.max() + 1e-9)), 1), 'onset': 0.01, 'peak_t': round(pk, 3),
                    'source': comp['source'] + f' (segmento {k}, {a / sr:.2f}-{b / sr:.2f}s)', 'dupes': []})
    os.remove(OUT + '/' + comp['file']); lib.remove(comp)

# ---- manual category fixes
FIX = {'Resaltador highlighter Sound Effect': 'marker', 'Windows_error': 'pop', '-camera-shutter-hard-click-1430': 'camera',
       'Film Burns SFX': 'retro', 'RELOJ': 'misc'}
for e in lib:
    if e['name'] in FIX and e['cat'] != FIX[e['name']]:
        c = FIX[e['name']]; nf = e['file'].replace('/' + e['cat'] + '/', '/' + c + '/')
        os.makedirs(os.path.dirname(OUT + '/' + nf), exist_ok=True); os.replace(OUT + '/' + e['file'], OUT + '/' + nf)
        e['file'] = nf; e['cat'] = c
for e in lib:
    for k in ('dur', 'peak_db', 'onset', 'peak_t'):
        e[k] = float(e[k])
json.dump(lib, open(OUT + '/library.json', 'w'), indent=1, ensure_ascii=False)
print('final', len(lib), Counter(e['cat'] for e in lib))
