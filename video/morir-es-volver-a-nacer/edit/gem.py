"""Pregunta a Gemini (nativo) sobre audios/imágenes. uso: gem.py MODELO 'prompt' archivo1 [archivo2 ...]"""
import base64, json, os, sys, time, urllib.request, urllib.error, mimetypes
model, prompt, files = sys.argv[1], sys.argv[2], sys.argv[3:]
parts = [{"text": prompt}]
for f in files:
    mt = mimetypes.guess_type(f)[0] or "audio/mpeg"
    parts.append({"inline_data": {"mime_type": mt, "data": base64.b64encode(open(f, "rb").read()).decode()}})
body = {"contents": [{"role": "user", "parts": parts}]}
for k in range(5):
    try:
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": os.environ.get("GEMINI_API_KEY", "proxy-injected")})
        r = json.load(urllib.request.urlopen(req, timeout=600))
        print("".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"]))
        break
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode()[:300].replace("\n", " "), file=sys.stderr); time.sleep(15 * (k + 1))
