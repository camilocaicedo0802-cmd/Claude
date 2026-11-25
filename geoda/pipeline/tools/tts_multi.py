#!/usr/bin/env python3
"""Todas las frases de un personaje en UNA petición de voz (misma voz exacta, una sola cuota) con pausas entre frases.
uso: tts_multi.py salida.wav voz perfil.txt frases.txt   (frases.txt: una frase por línea)"""
import json, sys, base64, subprocess, time
out, voice, prof_f, lines_f = sys.argv[1:5]
profile = open(prof_f).read().strip()
lines = [l.strip() for l in open(lines_f) if l.strip()]
transcript = '\n\n[pausa larga]\n\n'.join(lines)
prompt = profile + "\nEntre cada frase hay una pausa larga de un segundo (no digas la palabra 'pausa').\n\n#### TRANSCRIPT\n" + transcript
body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["AUDIO"],
        "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
q = out + '.req.json'; json.dump(body, open(q, 'w'))
for M in ['gemini-3.8-flash-lite-tts', 'gemini-3.1-flash-tts-preview', 'gemini-3.8-flash-tts', 'gemini-2.5-flash-preview-tts']:
    r = subprocess.run(['curl', '-sS', '--max-time', '240', f'https://generativelanguage.googleapis.com/v1beta/models/{M}:generateContent',
                        '-H', 'Content-Type: application/json', '-d', f'@{q}'], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    try:
        d = json.loads(r.stdout); raw = base64.b64decode(d['candidates'][0]['content']['parts'][0]['inlineData']['data'])
        pcm = out + '.pcm'; open(pcm, 'wb').write(raw)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', '24000', '-ac', '1', '-i', pcm, out], check=True, stdin=subprocess.DEVNULL)
        print('OK', M, out); sys.exit(0)
    except Exception:
        print(M, 'fail', r.stdout[:120].replace('\n', ' '), file=sys.stderr)
sys.exit(1)
