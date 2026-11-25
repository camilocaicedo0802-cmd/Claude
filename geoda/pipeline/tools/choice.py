import json, base64, subprocess, tempfile, os, time, sys
def ask(clip, a, b, q):
    fn = tempfile.mktemp(suffix='.mp3')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(b - a), '-i', clip, '-vn', '-ac', '1', '-ar', '16000', '-b:a', '96k', fn], check=True)
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": "audio/mp3", "data": base64.b64encode(open(fn, 'rb').read()).decode()}}, {"text": q}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
    jf = tempfile.mktemp(suffix='.json'); json.dump(body, open(jf, 'w')); os.remove(fn)
    for M in ['gemini-3.1-flash-lite-preview', 'gemini-3.8-flash', 'gemini-3-flash-preview'] * 2:
        r = subprocess.run(['curl', '-sS', '--max-time', '90', f'https://generativelanguage.googleapis.com/v1beta/models/{M}:generateContent',
                            '-H', 'Content-Type: application/json', '-d', f'@{jf}'], capture_output=True, text=True)
        try:
            return M, json.loads(r.stdout)['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            print(M, r.stdout[:100].replace('\n', ' '), file=sys.stderr); time.sleep(12)
    return None
if __name__ == '__main__':
    q = ("Listen very carefully, syllable by syllable. Which of these is said? A) '¿Y uno deja de sudar?'  B) '¿Y no deja de sudar?'  "
         "C) '¿Y uno no deja de sudar?'. Answer as JSON {\"choice\":\"A|B|C\",\"syllables_before_deja\":n}")
    import os  # carpeta de trabajo: GEODA_WORK o ~/.geoda_work (la crea setup_work.sh)
    G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
    for clip, a, b in [(f'{G}/hf/w_host_0.mp4', 11.1, 12.45), (f'{G}/hf/w_h4_0.mp4', 0.0, 1.5)]:
        print(clip.split('/')[-1], ask(clip, a, b, q))
