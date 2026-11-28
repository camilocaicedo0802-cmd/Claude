"""Narración en UNA sola toma con Gemini TTS (como el short de Napoleón): el narrador cuenta todo seguido y actúa él
mismo las citas, sin montaje por frases. Después solo se recortan las pausas
largas y se acelera un poco (máximo 10–12 %), así la voz conserva su fluidez natural.

Uso: SSL_CERT_FILE=/root/.ccr/ca-bundle.crt REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt \
     python3 scripts/voz_una_toma.py --salida DIR/toma.wav [--modelo gemini-2.5-pro-preview-tts] [--voz Charon]
Luego: python3 scripts/montar_natural.py --narrador DIR/toma.wav --tempo 1.10 && python3 scripts/alinear.py --sin-cortes --tempo 1.10
"""

import argparse
import base64
import os
import subprocess
import sys

import requests

sys.path.insert(0, os.path.dirname(__file__))
from guion import DIRECCION, ESTILO_TOMA, GUION  # noqa: E402

ESTILO = (
    ESTILO_TOMA + "\n"
    "Dirección por frase (NO la leas en voz alta, solo úsala para interpretar):\n"
    + "\n".join(f"{i + 1}. {d}" for i, d in enumerate(DIRECCION))
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="gemini-2.5-flash-preview-tts")
    ap.add_argument("--voz", default="Charon")
    ap.add_argument("--salida", required=True)
    args = ap.parse_args()
    guion = "\n".join(t for t, *_ in GUION)
    cuerpo = {
        "contents": [{"parts": [{"text": f"{ESTILO}\n\nTexto a narrar (lee solo esto):\n{guion}"}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": args.voz}}},
        },
    }
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{args.modelo}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, json=cuerpo, timeout=900,
    )
    if r.status_code != 200:
        sys.exit(f"Gemini {r.status_code}: {r.text[:300]}")
    cand = r.json()["candidates"][0]
    if "content" not in cand:
        sys.exit(f"sin audio: {str(cand)[:300]}")
    datos = cand["content"]["parts"][0]["inlineData"]["data"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "-", args.salida],
                   input=base64.b64decode(datos), check=True)
    print("listo:", args.salida)


if __name__ == "__main__":
    main()
