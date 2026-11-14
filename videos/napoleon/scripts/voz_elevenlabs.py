"""Narración con ElevenLabs v3 (voces prediseñadas: el plan gratis no permite voces de biblioteca por API).

Uso:  python3 scripts/voz_elevenlabs.py [--voz FGY2WhTYpPnrIDTdsKH5] [--estabilidad 0.5]
Escribe public/voz-cruda.wav; después correr scripts/alinear.py.
En la nube de Claude Code: SSL_CERT_FILE=/root/.ccr/ca-bundle.crt REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt
"""

import argparse
import base64
import os
import subprocess
import sys

import requests

sys.path.insert(0, os.path.dirname(__file__))
from guion import GUION  # noqa: E402


def texto_con_etiquetas():
    return " ".join(f"[{etiqueta}] {texto}" for texto, _, _, etiqueta in GUION)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voz", default="FGY2WhTYpPnrIDTdsKH5")  # Laura (ElevenLabs, prediseñada)
    ap.add_argument("--estabilidad", type=float, default=0.5)
    ap.add_argument("--salida", default="public/voz-cruda.wav")
    args = ap.parse_args()
    texto = texto_con_etiquetas()
    print(f"{len(texto)} caracteres")
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{args.voz}?output_format=pcm_24000",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
        json={"text": texto, "model_id": "eleven_v3", "language_code": "es", "voice_settings": {"stability": args.estabilidad}},
        timeout=600,
    )
    if r.status_code != 200:
        sys.exit(f"ElevenLabs {r.status_code}: {r.text[:400]}")
    pcm = r.content if r.headers.get("content-type", "").startswith("audio") else base64.b64decode(r.json()["audio_base64"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "-", args.salida], input=pcm, check=True)
    print("listo:", args.salida)


if __name__ == "__main__":
    main()
