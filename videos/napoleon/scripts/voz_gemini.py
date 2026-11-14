"""Narración con Gemini TTS (Google AI Studio).

Requiere un proyecto de AI Studio con facturación activa (el nivel gratis devuelve 403 en este proyecto).
Uso:  python3 scripts/voz_gemini.py [--modelo gemini-2.5-pro-preview-tts] [--voz Laomedeia]
Escribe public/voz-cruda.wav; después correr scripts/alinear.py.
"""

import argparse
import base64
import os
import subprocess
import sys

import requests

sys.path.insert(0, os.path.dirname(__file__))
from guion import GUION, INDICACIONES  # noqa: E402

ESTILO = (
    INDICACIONES
    + " Habla en español latinoamericano neutro (seseo, acento colombiano suave), como una creadora de contenido que "
    "cuenta un chisme histórico con complicidad e ironía, a un ritmo ágil de unas tres palabras por segundo. "
    "Pronuncia 'Little Boney' en inglés. La pregunta final es la frase con más energía y volumen de todo el audio."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="gemini-2.5-pro-preview-tts")
    ap.add_argument("--voz", default="Laomedeia")
    ap.add_argument("--salida", default="public/voz-cruda.wav")
    args = ap.parse_args()
    guion = "\n".join(t for t, *_ in GUION)
    cuerpo = {
        "contents": [{"parts": [{"text": f"{ESTILO}\n\nTexto a narrar:\n{guion}"}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": args.voz}}},
        },
    }
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{args.modelo}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, json=cuerpo, timeout=600,
    )
    if r.status_code != 200:
        sys.exit(f"Gemini {r.status_code}: {r.text[:400]}")
    datos = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "-", args.salida],
                   input=base64.b64decode(datos), check=True)
    print("listo:", args.salida)


if __name__ == "__main__":
    main()
