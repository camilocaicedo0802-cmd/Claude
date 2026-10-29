"""Imágenes del piloto E001 con Nano Banana (API de Gemini).

Lee video/E001/planos_piloto.json y guarda cada imagen en video/E001/img/<id>.png.
Genera primero REF (hoja de personaje) y la adjunta en los planos con usa_referencia.
Las imágenes que ya existen no se regeneran (usa --forzar para rehacerlas).

Uso:
    GEMINI_API_KEY=... python3 scripts/e001_imagenes.py            # todas las que falten
    GEMINI_API_KEY=... python3 scripts/e001_imagenes.py REF S06     # solo esos planos
    GEMINI_API_KEY=... python3 scripts/e001_imagenes.py --forzar S05

Modelo: gemini-3.1-flash-image (Nano Banana 2), 16:9 en 2K.
Tarifa consultada el 29-oct-2026: 0,101 USD por imagen 2K; sin nivel gratuito.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PLANOS = RAIZ / "video/E001/planos_piloto.json"
CARPETA = RAIZ / "video/E001/img"
MODELO = "gemini-3.1-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"
TARIFA_2K = 0.101


def generar(plano, referencia):
    partes = [{"text": plano["prompt"]}]
    if referencia is not None:
        partes.append({"inline_data": {"mime_type": "image/png", "data": referencia}})
    cuerpo = {
        "contents": [{"parts": partes}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"},
        },
    }
    peticion = urllib.request.Request(
        URL,
        data=json.dumps(cuerpo).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]},
    )
    for intento in range(4):
        try:
            with urllib.request.urlopen(peticion, timeout=300) as r:
                datos = json.load(r)
            break
        except urllib.error.HTTPError as e:
            detalle = e.read().decode()[:400]
            if "free_tier" in detalle:  # proyecto sin facturación: reintentar no sirve
                raise RuntimeError(f"{plano['id']}: la clave de Gemini no tiene facturación activa") from None
            if e.code in (429, 500, 503) and intento < 3:
                time.sleep(10 * (intento + 1))
                continue
            raise RuntimeError(f"{plano['id']}: HTTP {e.code} {detalle}") from None
    for parte in datos["candidates"][0]["content"]["parts"]:
        imagen = parte.get("inlineData") or parte.get("inline_data")
        if imagen:
            destino = CARPETA / f"{plano['id']}.png"
            destino.write_bytes(base64.b64decode(imagen["data"]))
            return destino
    raise RuntimeError(f"{plano['id']}: la respuesta no trae imagen: {json.dumps(datos)[:400]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", nargs="*", help="planos a generar (por defecto, todos los que falten)")
    parser.add_argument("--forzar", action="store_true", help="regenerar aunque ya exista")
    parser.add_argument("--hilos", type=int, default=4)
    args = parser.parse_args()

    CARPETA.mkdir(parents=True, exist_ok=True)
    planos = [p for p in json.loads(PLANOS.read_text()) if p["prompt"]]
    if args.ids:
        planos = [p for p in planos if p["id"] in args.ids]
    if not args.forzar:
        planos = [p for p in planos if not (CARPETA / f"{p['id']}.png").exists()]

    ref = [p for p in planos if p["id"] == "REF"]
    resto = [p for p in planos if p["id"] != "REF"]
    if ref:
        print("REF ->", generar(ref[0], None).name, flush=True)

    ruta_ref = CARPETA / "REF.png"
    if any(p["usa_referencia"] for p in resto) and not ruta_ref.exists():
        sys.exit("Falta video/E001/img/REF.png: genera REF primero.")
    referencia = base64.b64encode(ruta_ref.read_bytes()).decode() if ruta_ref.exists() else None

    def tarea(p):
        try:
            return f"{p['id']} -> {generar(p, referencia if p['usa_referencia'] else None).name}"
        except Exception as e:  # se informa y se sigue con los demás
            return f"ERROR {e}"

    with ThreadPoolExecutor(args.hilos) as pool:
        for linea in pool.map(tarea, resto):
            print(linea, flush=True)

    hechas = len(ref) + len(resto)
    print(f"{hechas} imágenes solicitadas · coste aproximado {hechas * TARIFA_2K:.2f} USD")


if __name__ == "__main__":
    main()
