"""Consulta a Gemini con uno o varios archivos multimedia (audio/vídeo/imagen).
Uso: python3 scripts/gemini.py <modelo> <prompt.txt> <archivo1> [archivo2 ...]
Usa la Files API (subida resumable) para archivos > 15 MB; inline para el resto.
La clave la inyecta el proxy; se envía un valor de relleno.
"""
import base64, json, urllib.error, mimetypes, os, sys, time, urllib.request

BASE = "https://generativelanguage.googleapis.com"
HDR = {"x-goog-api-key": "dummy"}

def req(url, data=None, headers=None, method=None):
    h = dict(HDR); h.update(headers or {})
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=600) as resp:
            return resp.read(), resp.headers
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"HTTP {e.code}: {e.read()[:800]!r}\n"); raise

def upload(path, mime):
    size = os.path.getsize(path)
    _, hd = req(f"{BASE}/upload/v1beta/files", data=json.dumps({"file": {"display_name": os.path.basename(path)}}).encode(),
                headers={"X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
                         "X-Goog-Upload-Header-Content-Length": str(size), "X-Goog-Upload-Header-Content-Type": mime,
                         "Content-Type": "application/json"}, method="POST")
    up = hd["X-Goog-Upload-URL"]
    body, _ = req(up, data=open(path, "rb").read(), headers={"X-Goog-Upload-Offset": "0", "X-Goog-Upload-Command": "upload, finalize",
                                                              "Content-Length": str(size)}, method="POST")
    f = json.loads(body)["file"]
    while f.get("state") == "PROCESSING":
        time.sleep(3)
        body, _ = req(f"{BASE}/v1beta/{f['name']}")
        f = json.loads(body)
    return {"file_data": {"mime_type": mime, "file_uri": f["uri"]}}

def part_for(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    if path.lower().endswith(".mov"): mime = "video/quicktime"
    if os.path.getsize(path) > 15 * 1024 * 1024:
        return upload(path, mime)
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(open(path, "rb").read()).decode()}}

model, prompt_file, files = sys.argv[1], sys.argv[2], sys.argv[3:]
parts = []
for p in files:
    parts.append({"text": f"=== ARCHIVO: {os.path.basename(p)} ==="})
    parts.append(part_for(p))
parts.append({"text": open(prompt_file).read()})
payload = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.2}}
body, _ = req(f"{BASE}/v1beta/models/{model}:generateContent", data=json.dumps(payload).encode(),
              headers={"Content-Type": "application/json"}, method="POST")
d = json.loads(body)
try:
    print("".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"]))
except Exception:
    print(json.dumps(d, indent=1)[:3000])
