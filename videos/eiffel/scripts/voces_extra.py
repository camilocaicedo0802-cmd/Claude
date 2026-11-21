"""Voces extra con Gemini TTS: los comentarios de internet y el mensaje del hacker (una voz distinta cada uno).

Uso: python3 scripts/voces_extra.py --carpeta <dir> [--tomas 2]
Escribe <dir>/<voz>_<toma>.wav (24 kHz) para cada frase cuya voz esté en VOCES_EXTRA.
"""

import argparse
import base64
import os
import subprocess
import sys

import requests

sys.path.insert(0, os.path.dirname(__file__))
from guion import GUION, PRONUNCIACION, VOCES_EXTRA  # noqa: E402


def generar(texto, voz, estilo, salida, modelo="gemini-2.5-flash-preview-tts"):
    prompt = f"{estilo} {PRONUNCIACION} Español latinoamericano neutro.\n\nTexto a decir (lee solo esto):\n{texto}"
    cuerpo = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voz}}}},
    }
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, json=cuerpo, timeout=300,
    )
    if r.status_code != 200:
        sys.exit(f"Gemini {r.status_code}: {r.text[:300]}")
    datos = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "-", salida], input=base64.b64decode(datos), check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", required=True)
    ap.add_argument("--tomas", type=int, default=2)
    args = ap.parse_args()
    os.makedirs(args.carpeta, exist_ok=True)
    for texto, _sec, _enf, etiqueta in GUION:
        if etiqueta not in VOCES_EXTRA:
            continue
        voz, estilo = VOCES_EXTRA[etiqueta]
        for k in range(1, args.tomas + 1):
            salida = os.path.join(args.carpeta, f"{etiqueta}_{k}.wav")
            generar(texto, voz, estilo, salida)
            print("listo:", salida)


if __name__ == "__main__":
    main()
