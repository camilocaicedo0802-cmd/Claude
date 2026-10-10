"""Día 10: caja de la cara en el vídeo editado (YuNet cada 3 fotogramas) para que ningún gráfico la toque.

Uso: python -I scripts/dia10/caras.py <modelo_yunet.onnx>
Salida: src/dia10/data/caras.json (misma forma que en los días 4–9: [fotograma, x, y, ancho, alto] en 1080×1920).
A cámara y sentada (como el día 8): la cara se ve siempre; si en algún fotograma no se detecta, Caras.tsx hereda la
detección más cercana.
"""
import json
import sys
from pathlib import Path

import cv2

RAIZ = Path(__file__).resolve().parent.parent.parent

det = cv2.FaceDetectorYN.create(sys.argv[1], "", (540, 960), 0.6)
cap = cv2.VideoCapture(str(RAIZ / "public/dia10/editado.mp4"))
caras, n, vistas = [], 0, 0
while True:
    ok, fr = cap.read()
    if not ok:
        break
    if n % 3 == 0:
        _, res = det.detect(cv2.resize(fr, (540, 960)))
        if res is not None and len(res):
            x, y, w, h = (float(v) * 2 for v in max(res, key=lambda r: r[14])[:4])
            caras.append([n, round(x), round(y), round(w), round(h)])
            vistas += 1
        else:
            caras.append([n, None, None, None, None])
    n += 1
json.dump({"cada": 3, "caras": caras}, open(RAIZ / "src/dia10/data/caras.json", "w"))
print(f"cara en {vistas} de {len(caras)} muestras")
