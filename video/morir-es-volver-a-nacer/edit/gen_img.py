"""Genera imágenes con Gemini (nativo). uso: gen_img.py prompts.json out_dir [modelo] [solo_clave]
prompts.json: {"clave": "prompt", ...}. Guarda out_dir/clave.png; salta las existentes."""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

STYLE = (" Cinematic film still, 16:9 widescreen, dark moody documentary look, low-key lighting, warm amber and "
         "deep red tones, volumetric light, subtle film grain, shallow depth of field, photorealistic, highly detailed. "
         "No text, no letters, no watermark, no logos.")


def gen(model, prompt, aspect="16:9"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE", "TEXT"], "imageConfig": {"aspectRatio": aspect}}}
    for k in range(6):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=600))
            for p in r["candidates"][0]["content"]["parts"]:
                d = p.get("inlineData") or p.get("inline_data")
                if d:
                    return base64.b64decode(d["data"])
            print("sin imagen:", json.dumps(r)[:300], flush=True)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300].replace("\n", " ")
            print("HTTP", e.code, msg, flush=True)
            if e.code == 400:
                return None
        except Exception as e:  # noqa
            print("error", e, flush=True)
        time.sleep(15 * (k + 1))
    return None


def main():
    prompts = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "gemini-3.1-flash-image"
    only = sys.argv[4] if len(sys.argv) > 4 else None
    os.makedirs(out, exist_ok=True)
    for k, p in prompts.items():
        if only and k != only:
            continue
        fn = os.path.join(out, k + ".png")
        if os.path.exists(fn):
            continue
        aspect = "9:16" if k.startswith("v_") else "16:9"
        full = p if k.startswith("raw_") else p + STYLE
        img = gen(model, full, aspect)
        if img:
            open(fn, "wb").write(img)
            print("ok", k, len(img) // 1024, "KB", flush=True)
        else:
            print("FALLO", k, flush=True)


if __name__ == "__main__":
    main()
