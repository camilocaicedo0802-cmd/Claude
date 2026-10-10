"""Día 8 · apoyos: fotografías (polaroids), fragmentos cortos de B-roll y cara del vídeo editado.

Uso: python -I scripts/dia8/apoyos.py <carpeta crudo/> <modelo_yunet.onnx>
     (<carpeta crudo/> contiene dia7/crudo2_30.mp4, dia8/apoyo2/apoyo.mp4 —toma de apoyo del día 2— y
      dia8/moretones/m1.png, m2.webp, m3.png, m4.webp)

- "vas a tomarte las mismas fotografías… de frente, de costado, de espalda y luego del otro costado": las MISMAS
  escenas de la toma de apoyo del día 2 (frente 3,30 s · perfil 16,45 s · espalda 13,40 s, como scripts/dia2/convertir.sh)
  y el otro costado (8,60 s, de perfil hacia el otro lado con los brazos al frente). Clips cortos que se ven dentro de
  las polaroids (corrección del usuario: las del día 7 se veían yendo a cerrar la puerta).
- "revisa si aparecieron moretones, irritación": cuatro fotos de moretones en piernas que pasó el usuario, recortadas
  en cuadrado centrado en el morado (galería de tarjetas en Dia8.tsx).
- "puedes seguir con la rutina": un fragmento del equipo sobre la pantorrilla (día 7).
Salidas: public/dia8/foto_*.mp4, public/dia8/moreton_*.jpg, public/dia8/apoyo_rutina.mp4 y src/dia8/data/caras.json.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
PUB = RAIZ / "public/dia8"

# nombre: segundo de la toma de apoyo del día 2 (1,6 s de clip, recorte 2:3 de cabeza a pies)
FOTOS = {
    "frente": 3.30,
    "costado": 16.45,
    "espalda": 13.40,
    "otro": 8.60,
}
# nombre: (archivo, recorte cuadrado "lado:lado:x:y" centrado en el morado)
MORETONES = {
    "1": ("m1.png", "400:400:0:0"),
    "2": ("m2.webp", "900:900:475:112"),
    "3": ("m3.png", "576:576:302:0"),
    "4": ("m4.webp", "667:667:136:0"),
}
# nombre: (crudo, segundo, duración, recorte x, y) — recorte 780×1387 (9:16) escalado a 1080×1920
FRAGMENTOS = {
    "rutina": ("dia7/crudo2_30.mp4", 57.0, 1.6, 150, 533),
}


def main() -> None:
    crudo = Path(sys.argv[1])
    PUB.mkdir(parents=True, exist_ok=True)
    for nombre, t in FOTOS.items():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", str(crudo / "dia8/apoyo2/apoyo.mp4"), "-t", "1.6",
                        "-map", "0:v:0", "-an", "-vf", "fps=30,crop=1080:1620:0:250,scale=608:912:flags=lanczos",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        str(PUB / f"foto_{nombre}.mp4")], check=True)
    for nombre, (f, recorte) in MORETONES.items():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(crudo / "dia8/moretones" / f), "-frames:v", "1",
                        "-vf", f"crop={recorte},scale=720:720:flags=lanczos", "-q:v", "2", str(PUB / f"moreton_{nombre}.jpg")],
                       check=True)
    for nombre, (f, t, dur, x, y) in FRAGMENTOS.items():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", str(crudo / f), "-t", f"{dur}", "-an",
                        "-vf", f"crop=780:1387:{x}:{y},scale=1080:1920:flags=lanczos", "-c:v", "libx264", "-preset", "slow",
                        "-crf", "16", "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", str(PUB / f"apoyo_{nombre}.mp4")],
                       check=True)

    # Cara del vídeo editado (YuNet cada 3 fotogramas; aquí siempre se ve de frente)
    import cv2
    det = cv2.FaceDetectorYN.create(sys.argv[2], "", (540, 960), 0.55)
    cap = cv2.VideoCapture(str(PUB / "editado.mp4"))
    caras, n = [], 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if n % 3 == 0:
            _, res = det.detect(cv2.resize(fr, (540, 960)))
            if res is not None and len(res):
                x, y, w, h = (float(v) * 2 for v in max(res, key=lambda r: r[14])[:4])
                caras.append([n, round(x), round(y), round(w), round(h)])
            else:
                caras.append([n, None, None, None, None])
        n += 1
    json.dump({"cada": 3, "caras": caras}, open(RAIZ / "src/dia8/data/caras.json", "w"))
    vistas = [c for c in caras if c[1] is not None]
    print(f"cara en {len(vistas)} de {len(caras)} muestras · x {min(c[1] for c in vistas)}–{max(c[1] + c[3] for c in vistas)}"
          f" · y {min(c[2] for c in vistas)}–{max(c[2] + c[4] for c in vistas)}")


if __name__ == "__main__":
    main()
