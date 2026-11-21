"""Genera la voz del video largo con Gemini TTS: el narrador por capítulos (Charon), las citas (voces secundarias)
y la muletilla «Ese ya no llega a nada» (un solo audio que se reutiliza).

Uso: python3 scripts/voz_capitulos.py --carpeta DIR [--tomas 2] [--solo narrador|citas|muletilla] [--capitulos 0,1]
Las llamadas van espaciadas para no pasar el límite por minuto.
"""

import argparse
import base64
import os
import subprocess
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(__file__))
import guion as _g  # noqa: E402
from guion import CAPITULOS, ESTILO_MULETILLA, GUION, INDICACIONES, PRONUNCIACION, SERIAS, VOCES_EXTRA  # noqa: E402

MODELO = os.environ.get("MODELO_TTS", "gemini-2.5-flash-preview-tts")
NARRADOR = (
    "Eres un narrador masculino latinoamericano (español neutro, con seseo) que cuenta historia en YouTube como un amigo: "
    "ritmo ágil, unas 175 palabras por minuto, frases encadenadas sin pausas largas, y una pequeña pausa antes de cada remate."
)
NARRADOR = getattr(_g, "NARRADOR", NARRADOR)


def generar(prompt, voz, salida, intentos=4):
    cuerpo = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voz}}}},
    }
    for k in range(intentos):
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent",
                          headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, json=cuerpo, timeout=900)
        if r.status_code == 200 and "content" not in r.json().get("candidates", [{}])[0]:
            print("sin audio:", str(r.json())[:300], flush=True)
            time.sleep(5)
            continue
        if r.status_code == 200:
            datos = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "-", salida],
                           input=base64.b64decode(datos), check=True)
            print("listo:", salida, flush=True)
            return True
        print(f"Gemini {r.status_code} (intento {k + 1}): {r.text[:160]}", flush=True)
        time.sleep(60 * (k + 1))
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", required=True)
    ap.add_argument("--tomas", type=int, default=2)
    ap.add_argument("--solo", default="")
    ap.add_argument("--capitulos", default="")
    ap.add_argument("--espera", type=float, default=25)
    ap.add_argument("--voces", default="", help="solo estas voces de citas (separadas por coma)")
    args = ap.parse_args()
    os.makedirs(args.carpeta, exist_ok=True)
    trabajos = []
    caps = [int(c) for c in args.capitulos.split(",") if c.strip()] or list(range(len(CAPITULOS)))
    if args.solo in ("", "narrador"):
        for c in caps:
            lineas = [t for t, cap, _e, voz in GUION if cap == c and not voz]
            serias = [GUION[i][0] for i in sorted(SERIAS) if GUION[i][1] == c and not GUION[i][3]]
            nota = ""
            if serias:
                nota = ("\nEstas frases son SERIAS: dilas más lento (unas 150 palabras por minuto), sin sonrisa ni ironía, con respeto:\n- "
                        + "\n- ".join(serias))
            prompt = (f"{INDICACIONES} {NARRADOR} {PRONUNCIACION}{nota}\n"
                      "Cuando una línea termina en dos puntos, viene una cita que dice otra persona: no la leas, sigue con la línea siguiente.\n\n"
                      f"Texto a narrar (capítulo «{CAPITULOS[c]}»; lee solo esto):\n" + "\n".join(lineas))
            for k in range(1, args.tomas + 1):
                trabajos.append((prompt, "Charon", os.path.join(args.carpeta, f"cap{c}_{k}.wav")))
    if args.solo in ("", "citas"):
        hechas = set()
        for t, _cap, _e, voz in GUION:
            if voz in VOCES_EXTRA and voz not in hechas and (not args.voces or voz in args.voces.split(",")):
                hechas.add(voz)
                nombre, estilo = VOCES_EXTRA[voz]
                prompt = f"{estilo} Dilo así, en español latinoamericano: {t}"
                for k in range(1, args.tomas + 1):
                    trabajos.append((prompt, nombre, os.path.join(args.carpeta, f"{voz}_{k}.wav")))
    if args.solo in ("", "muletilla"):
        prompt = f"{ESTILO_MULETILLA}\n\nTexto a decir (lee solo esto):\nEse ya no llega a nada."
        for k in range(1, 4):
            trabajos.append((prompt, "Charon", os.path.join(args.carpeta, f"muletilla_{k}.wav")))
    for i, (prompt, voz, salida) in enumerate(trabajos):
        if os.path.exists(salida):
            continue
        generar(prompt, voz, salida)
        if i < len(trabajos) - 1:
            time.sleep(args.espera)
    print("terminado", flush=True)


if __name__ == "__main__":
    main()
