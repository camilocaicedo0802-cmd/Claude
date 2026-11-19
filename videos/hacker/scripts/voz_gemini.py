"""Narración con Gemini TTS (Google AI Studio): narrador masculino, con entonación y momentos clave marcados.

Requiere que el proyecto de la clave de AI Studio tenga la facturación activada
(sin ella Google responde 403 "free tier is not available for this project").
Uso:  python3 scripts/voz_gemini.py [--modelo gemini-2.5-flash-preview-tts] [--voz Charon]
Escribe public/voz-cruda.wav; después:  python3 scripts/alinear.py --voz "Gemini · Charon"
"""

import argparse
import base64
import os
import subprocess
import sys

import requests

sys.path.insert(0, os.path.dirname(__file__))
import guion as _g  # noqa: E402
from guion import DIRECCION, GUION, INDICACIONES, PRONUNCIACION  # noqa: E402

def estilo(indices):
    return ESTILO_BASE + "\n".join(f"{n + 1}. {DIRECCION[i]}" for n, i in enumerate(indices))


ESTILO_BASE = (
    INDICACIONES
    + " Eres un narrador masculino latinoamericano (español neutro, con seseo) que cuenta historias en redes sociales: "
    "voz narrativa, cálida y envolvente, con muchas subidas y bajadas de entonación, pausas dramáticas antes de cada "
    "revelación y énfasis claro en los momentos clave. Ritmo ágil pero sin atropellarse. "
    + PRONUNCIACION
    + " " + getattr(_g, 'ESTILO_EXTRA', '')
    + "\n"
    "Dirección por frase (NO la leas en voz alta, solo úsala para interpretar):\n"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="gemini-2.5-flash-preview-tts")
    ap.add_argument("--voz", default="Charon")
    ap.add_argument("--salida", default="public/voz-cruda.wav")
    ap.add_argument("--frases", default="", help="índices separados por coma: narra solo esas frases (para rehacer una parte)")
    args = ap.parse_args()
    ap_narrador = [i for i, fr in enumerate(GUION) if len(fr) < 4 or not fr[3]]
    indices = [int(i) for i in args.frases.split(",") if i.strip()] or ap_narrador
    guion = "\n".join(GUION[i][0] for i in indices)
    cuerpo = {
        "contents": [{"parts": [{"text": f"{estilo(indices)}\n\nTexto a narrar (lee solo esto):\n{guion}"}]}],
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
