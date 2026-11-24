#!/usr/bin/env python3
"""Transcripción con tiempos por palabra (Gemini). uso: stt.py clip.mp4 > clip.words.json"""
import json, sys, base64, subprocess, tempfile, os
src = sys.argv[1]
wav = tempfile.mktemp(suffix='.mp3')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '1', '-ar', '16000', '-b:a', '48k', wav], check=True)
b64 = base64.b64encode(open(wav, 'rb').read()).decode(); os.remove(wav)
prompt = ("Transcribe this Spanish (Colombia) audio exactly, word by word. Return ONLY JSON: "
          '{"words":[{"w":"palabra","s":start_seconds,"e":end_seconds}, ...]} with precise timestamps in seconds (3 decimals). '
          "Keep punctuation attached to words. Do not translate.")
body = {"contents": [{"parts": [{"inline_data": {"mime_type": "audio/mp3", "data": b64}}, {"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
fn = tempfile.mktemp(suffix='.json'); json.dump(body, open(fn, 'w'))
import time
for M in ['gemini-3.8-flash', 'gemini-3-flash-preview', 'gemini-3.8-flash', 'gemini-3-flash-preview', 'gemini-3.8-flash']:
    r = subprocess.run(['curl', '-sS', '--max-time', '180', f'https://generativelanguage.googleapis.com/v1beta/models/{M}:generateContent',
                        '-H', 'Content-Type: application/json', '-d', f'@{fn}'], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout); t = d['candidates'][0]['content']['parts'][0]['text']
        words = json.loads(t)['words']; print(json.dumps(words, ensure_ascii=False)); os.remove(fn); sys.exit(0)
    except Exception as e:
        print(M, 'fail', r.stdout[:120], file=sys.stderr); time.sleep(20)
sys.exit(1)
