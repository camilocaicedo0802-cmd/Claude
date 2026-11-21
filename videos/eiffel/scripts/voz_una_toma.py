"""Narración en UNA sola toma con Gemini TTS (como el short de Napoleón): el narrador cuenta todo seguido y actúa él
mismo las citas (Lustig en susurro, la esposa seca), sin montaje por frases. Después solo se recortan las pausas
largas y se acelera un poco (máximo 10 %) con alinear.py, así la voz conserva su fluidez natural.

Uso: SSL_CERT_FILE=/root/.ccr/ca-bundle.crt REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt \
     python3 scripts/voz_una_toma.py --salida DIR/toma.wav [--modelo gemini-2.5-pro-preview-tts] [--voz Charon]
Luego: python3 scripts/alinear.py --entrada DIR/toma.wav --tempo 1.08
"""

import argparse
import base64
import os
import subprocess
import sys

import requests

sys.path.insert(0, os.path.dirname(__file__))
from guion import GUION, PRONUNCIACION  # noqa: E402

DIRECCION = [
    "arranca arriba, con energía y picardía; acentúa 'vendió' y haz una micro pausa corta después de 'Torre Éifel'",
    "con una sonrisa cómplice, casi riéndote",
    "'Mira' relajado y conversacional; 'oxidada' y 'cuesta una fortuna' rápido, de pasada; en 'había nacido para ser desmontada' sube con sorpresa",
    "ágil, preparando la idea",
    "ACTÚA a Lustig: susurro suave, elegante y seguro, saboreando la idea, sin acento extranjero",
    "'Primero' claro y marcado",
    "'Después' más rápido, la historia se acelera",
    "rápido, con picardía",
    "ACTÚA a Lustig: voz baja y persuasiva de negocio secreto; 'Pero ni una palabra' casi en susurro",
    "'Uno quiere comprarla' con ilusión; 'pero su esposa sospecha' baja el tono",
    "ACTÚA a la esposa: seca y escéptica; la pregunta sube al final",
    "baja la voz, como quien cuenta la mejor parte; 'funcionario corrupto' saboreándolo y acentúa 'soborno'; después, medio segundo de silencio",
    "corto, seguro y con un punto de admiración",
    "'Mira' explicativo y rápido; acentúa 'nunca'; 'pero un funcionario de verdad, sí' con tono de '¿lo ves?'",
    "rápido, con una micro pausa al final",
    "incredulidad divertida",
    "pregunta rápida",
    "'Nunca llegó' seco; 'vergüenza' con gracia, compadeciendo al comprador",
    "'volvió a intentarlo' pícaro; 'y esta vez tuvo que huir' rápido, como una huida",
    "frena, más misterioso; un breve silencio después",
    "'Murió preso' neutral, sin burla; micro pausa después de 'pusieron:'",
    "más lento, seco e irónico, con media sonrisa; ahí termina, sin respiración ni ningún sonido después",
]
assert len(DIRECCION) == len(GUION)

ESTILO = (
    "Cuenta esto como un amigo que cuenta un chisme buenísimo y admira un poco la jugada del estafador: cómplice, pícaro, "
    "muy expresivo, nunca de documental. Eres un narrador masculino latinoamericano (español neutro, con seseo) que cuenta "
    "historias en redes sociales: voz narrativa, cálida y envolvente, con muchas subidas y bajadas de entonación y énfasis "
    "claro en los momentos clave. Ritmo rápido de video corto, unas 190 palabras por minuto, frases encadenadas y sin "
    "respiraciones audibles, pero natural, sin atropellarte. Cuando hablan Lustig o la esposa, tú mismo cambias la voz "
    f"para actuarlos. {PRONUNCIACION}\n"
    "Dirección por frase (NO la leas en voz alta, solo úsala para interpretar):\n"
    + "\n".join(f"{i + 1}. {d}" for i, d in enumerate(DIRECCION))
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="gemini-2.5-pro-preview-tts")
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
