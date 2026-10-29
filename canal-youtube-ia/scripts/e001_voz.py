"""Narración del piloto E001 con ElevenLabs y sus marcas de tiempo por carácter.

Dos caminos, con la misma salida (video/E001/audio/E001_01.mp3 y E001_01_tiempos.json):

    # 1) Por API (requiere plan de pago: el plan gratuito no permite voces de la biblioteca por API)
    ELEVENLABS_API_KEY=... python3 scripts/e001_voz.py generar --voz lujan

    # 2) MP3 hecho a mano en la web de ElevenLabs y subido a video/E001/audio/E001_01.mp3
    ELEVENLABS_API_KEY=... python3 scripts/e001_voz.py alinear

    # Ver cuántos caracteres quedan en la cuenta
    ELEVENLABS_API_KEY=... python3 scripts/e001_voz.py cuota

El texto es la parte 01 de guiones/E001-textos-elevenlabs.md (bloques 1 a 3).
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TEXTOS = RAIZ / "guiones/E001-textos-elevenlabs.md"
AUDIO = RAIZ / "video/E001/audio"
MP3 = AUDIO / "E001_01.mp3"
TIEMPOS = AUDIO / "E001_01_tiempos.json"
API = "https://api.elevenlabs.io/v1"

# Voces de la biblioteca ya añadidas a la cuenta (español latinoamericano, masculinas, narrativas)
VOCES = {
    "lujan": ("GcbypXUfJn5DbptRc2U7", "Luján - Warm, Natural, Neutral"),
    "rodrigo": ("1p905cdbJ1e1JQxhFTGJ", "Rodrigo Zabú - Latin Spanish"),
    "albert": ("QcV29BrudEqfYY6zyOU8", "Albert - Deep, Resonate and Compelling"),
    "cesar": ("QtuQlibCvdX2iBrV4laj", "Cesar - Slow, Meditative, Warm"),
}
# Configuración recomendada en guiones/E001-textos-elevenlabs.md
AJUSTES = {"stability": 0.45, "similarity_boost": 0.75, "style": 0.2, "use_speaker_boost": True, "speed": 1.0}
MODELO = "eleven_multilingual_v2"


def texto_parte(n=1):
    md = TEXTOS.read_text()
    bloque = re.search(rf"## Parte {n:02d} .*?```\n(.*?)```", md, re.S)
    if not bloque:
        sys.exit(f"No encuentro la parte {n:02d} en {TEXTOS}")
    return bloque.group(1).strip()


def llamar(ruta, cuerpo=None, tipo="application/json", metodo=None):
    peticion = urllib.request.Request(
        f"{API}{ruta}", data=cuerpo, method=metodo or ("POST" if cuerpo else "GET"),
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": tipo},
    )
    try:
        with urllib.request.urlopen(peticion, timeout=600) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detalle = e.read().decode()[:500]
        sys.exit(f"ElevenLabs respondió HTTP {e.code}: {detalle}")


def cuota():
    s = llamar("/user/subscription")
    return s["tier"], s["character_limit"] - s["character_count"]


def guardar(texto, caracteres, inicios, finales, fuente, extra=None):
    datos = {"texto": texto, "fuente": fuente, "caracteres": caracteres, "inicios": inicios, "finales": finales}
    datos.update(extra or {})
    TIEMPOS.write_text(json.dumps(datos, ensure_ascii=False, indent=1))
    print(f"{TIEMPOS.relative_to(RAIZ)}: {len(caracteres)} caracteres, {finales[-1]:.1f} s")


def generar(voz):
    voice_id, nombre = VOCES[voz]
    texto = texto_parte(1)
    plan, quedan = cuota()
    print(f"Plan {plan}: quedan {quedan} caracteres; la parte 01 usa {len(texto)}")
    if quedan < len(texto):
        sys.exit("No alcanzan los caracteres del mes.")
    cuerpo = json.dumps({"text": texto, "model_id": MODELO, "voice_settings": AJUSTES}).encode()
    r = llamar(f"/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128", cuerpo)
    AUDIO.mkdir(parents=True, exist_ok=True)
    MP3.write_bytes(base64.b64decode(r["audio_base64"]))
    a = r["alignment"]
    guardar(texto, a["characters"], a["character_start_times_seconds"], a["character_end_times_seconds"],
            "elevenlabs-tts", {"voz": nombre, "voice_id": voice_id, "modelo": MODELO, "ajustes": AJUSTES})


def alinear():
    if not MP3.exists():
        sys.exit(f"Falta {MP3.relative_to(RAIZ)}")
    texto = texto_parte(1)
    frontera = uuid.uuid4().hex
    cuerpo = b"".join([
        f"--{frontera}\r\nContent-Disposition: form-data; name=\"text\"\r\n\r\n".encode(), texto.encode(), b"\r\n",
        f"--{frontera}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"E001_01.mp3\"\r\n"
        "Content-Type: audio/mpeg\r\n\r\n".encode(), MP3.read_bytes(), b"\r\n",
        f"--{frontera}--\r\n".encode(),
    ])
    r = llamar("/forced-alignment", cuerpo, f"multipart/form-data; boundary={frontera}")
    c = r["characters"]
    guardar(texto, [x["text"] for x in c], [x["start"] for x in c], [x["end"] for x in c],
            "elevenlabs-forced-alignment", {"perdida": r.get("loss")})


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="orden", required=True)
    g = sub.add_parser("generar")
    g.add_argument("--voz", choices=VOCES, default="lujan")
    sub.add_parser("alinear")
    sub.add_parser("cuota")
    args = parser.parse_args()
    if args.orden == "generar":
        generar(args.voz)
    elif args.orden == "alinear":
        alinear()
    else:
        plan, quedan = cuota()
        print(f"Plan {plan}: quedan {quedan} caracteres")


if __name__ == "__main__":
    main()
