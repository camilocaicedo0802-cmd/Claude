"""Día 8 · apoyos: fotografías (polaroids), fragmentos cortos de B-roll y cara del vídeo editado.

Uso: python -I scripts/dia8/apoyos.py <carpeta crudo/> <modelo_yunet.onnx>
     (<carpeta crudo/> contiene dia7/crudo1_30.mp4 y dia7/crudo2_30.mp4)

- "vas a tomarte las mismas fotografías… de frente, de costado, de espalda y luego del otro costado": fotogramas del
  principio del crudo 2 del día 7 (camina por el cuarto antes de empezar: piel sin enrojecer, mismo fondo); "el otro
  costado" es el costado reflejado (ilustrativo). Las tomas del día 6 se descartaron: eran después de la sesión.
- "revisa si aparecieron moretones, irritación": dos fragmentos de ≈1 s de las piernas (crudo del día 7, recortados
  a la pierna, sin cara).
- "puedes seguir con la rutina": un fragmento del equipo sobre la pantorrilla (día 7).
Salidas: public/dia8/foto_*.jpg, public/dia8/apoyo_*.mp4 y src/dia8/data/caras.json.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
PUB = RAIZ / "public/dia8"

FOTOS = {  # nombre: (segundo del crudo 2 del día 7, recorte 2:3 "w:h:x:y", reflejar)
    "frente": (7.8, "1080:1620:0:0", False),
    "costado": (2.3, "1080:1620:0:0", False),
    "espalda": (3.2, "800:1200:275:300", False),
    "otro": (2.3, "1080:1620:0:0", True),
}
# nombre: (crudo, segundo, duración, recorte x, y) — recorte 780×1387 (9:16) escalado a 1080×1920
FRAGMENTOS = {
    "piel1": ("dia7/crudo2_30.mp4", 14.6, 1.0, 150, 533),
    "piel2": ("dia7/crudo1_30.mp4", 186.0, 1.0, 150, 450),
    "rutina": ("dia7/crudo2_30.mp4", 57.0, 1.6, 150, 533),
}


def main() -> None:
    crudo = Path(sys.argv[1])
    PUB.mkdir(parents=True, exist_ok=True)
    for nombre, (t, recorte, reflejar) in FOTOS.items():
        vf = f"crop={recorte},scale=600:900:flags=lanczos" + (",hflip" if reflejar else "")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", str(crudo / "dia7/crudo2_30.mp4"), "-frames:v", "1",
                        "-vf", vf, "-q:v", "2", str(PUB / f"foto_{nombre}.jpg")], check=True)
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
