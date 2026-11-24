#!/usr/bin/env python3
"""Transcribe cada tramo de voz por separado (contenido fiable aunque los tiempos del modelo no lo sean).
uso: seg_stt.py clip.mp4 "a-b,a-b,..."  -> JSON [{"a":..,"b":..,"t":"texto"}]"""
import sys, json, base64, subprocess, tempfile, os, time
src, spec = sys.argv[1], sys.argv[2]
segs = [tuple(map(float, x.split('-'))) for x in spec.split(',')]
parts = []
for k, (a, b) in enumerate(segs):
    fn = tempfile.mktemp(suffix='.mp3')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(0, a - 0.05):.2f}', '-t', f'{b - a + 0.1:.2f}', '-i', src, '-vn', '-ac', '1',
                    '-ar', '16000', '-b:a', '64k', fn], check=True)
    parts.append({"text": f"Segmento {k + 1}:"})
    parts.append({"inline_data": {"mime_type": "audio/mp3", "data": base64.b64encode(open(fn, 'rb').read()).decode()}}); os.remove(fn)
parts.append({"text": "Transcribe exactly what is said in each audio segment above (Spanish, Colombia), word by word, including partial "
              "words at the edges written as heard. If a segment has no speech (breath, noise, knock), return an empty string. "
              'Return ONLY JSON: {"segments": ["texto 1", "texto 2", ...]} with one entry per segment, in order.'})
body = {"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
fn = tempfile.mktemp(suffix='.json'); json.dump(body, open(fn, 'w'))
for M in ['gemini-3.8-flash', 'gemini-3-flash-preview'] * 3:
    r = subprocess.run(['curl', '-sS', '--max-time', '240', f'https://generativelanguage.googleapis.com/v1beta/models/{M}:generateContent',
                        '-H', 'Content-Type: application/json', '-d', f'@{fn}'], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout); t = json.loads(d['candidates'][0]['content']['parts'][0]['text'])['segments']
        print(json.dumps([dict(a=a, b=b, t=x) for (a, b), x in zip(segs, t)], ensure_ascii=False)); os.remove(fn); sys.exit(0)
    except Exception:
        print(M, 'fail', r.stdout[:150], file=sys.stderr); time.sleep(15)
sys.exit(1)
