#!/usr/bin/env python3
"""Verifica cada frase cortada: transcribe el tramo solo y lo compara con el texto del guion.
uso: verify_lines.py spec.json  (lista de {"id","clip","a","b","texto"})"""
import sys, json, base64, subprocess, tempfile, os, time, re, unicodedata
def norm(s):
    s = unicodedata.normalize('NFD', s.lower()); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.replace('14', 'catorce')
    return re.sub(r'[^a-zñ ]', ' ', s).split()
def stt(clip, a, b):
    fn = tempfile.mktemp(suffix='.mp3')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', clip, '-vn', '-ac', '1', '-ar', '16000',
                    '-b:a', '64k', fn], check=True)
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": "audio/mp3", "data": base64.b64encode(open(fn, 'rb').read()).decode()}},
             {"text": "Transcribe exactly what is said (Spanish). Include cut-off words at the start or end as heard (e.g. 'pie-'). "
                      "Return only the transcript text."}]}], "generationConfig": {"temperature": 0}}
    os.remove(fn); jf = tempfile.mktemp(suffix='.json'); json.dump(body, open(jf, 'w'))
    for M in ['gemini-3.8-flash', 'gemini-3-flash-preview'] * 4:
        r = subprocess.run(['curl', '-sS', '--max-time', '120', f'https://generativelanguage.googleapis.com/v1beta/models/{M}:generateContent',
                            '-H', 'Content-Type: application/json', '-d', f'@{jf}'], capture_output=True, text=True)
        try:
            t = json.loads(r.stdout)['candidates'][0]['content']['parts'][0]['text'].strip(); os.remove(jf); return t
        except Exception:
            time.sleep(10)
    return '??'
spec = json.load(open(sys.argv[1])); ok = True
for s in spec:
    t = stt(s['clip'], s['a'], s['b'])
    good = norm(t) == norm(s['texto'])
    ok &= good
    print(f"{'OK ' if good else 'MAL'} {s['id']:4s} {s['a']:6.2f}-{s['b']:6.2f}  oído: {t}")
sys.exit(0 if ok else 2)
