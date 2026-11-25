"""Detecta caras en el A-roll editado (YuNet) para que nada las pise.

Uso: python3 scripts/caras.py v1 [v2 ...]
Salida: src/lote2/datos/<vid>_caras.json  → {"fps": 5, "caras": [[t, [[x, y, w, h], ...]], ...]} en px de 1080x1920
y un resumen por toma (caja que cubre todas las caras de la toma) para colocar textos y gráficos.
"""
import json, subprocess, sys
import cv2, numpy as np

MODELO = "modelos/yunet.onnx"
PASO = 0.2  # s

def frames(path, w=540, h=960):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={1 / PASO},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)

for vid in sys.argv[1:]:
    det = cv2.FaceDetectorYN.create(MODELO, "", (540, 960), score_threshold=0.55, nms_threshold=0.3, top_k=10)
    salida = []
    for i, im in enumerate(frames(f"public/lote2/edit/{vid}_aroll.mp4")):
        _, caras = det.detect(im)
        # solo caras reales: confianza alta y tamaño razonable (los carteles del fondo dan falsos positivos pequeños)
        cajas = [] if caras is None else [[round(float(c[0]) * 2), round(float(c[1]) * 2), round(float(c[2]) * 2), round(float(c[3]) * 2)]
                                          for c in caras if float(c[14]) >= 0.8 and float(c[2]) * 2 >= 110]
        salida.append([round(i * PASO, 2), cajas])
    json.dump({"paso": PASO, "caras": salida}, open(f"src/lote2/datos/{vid}_caras.json", "w"))
    d = json.load(open(f"src/lote2/datos/{vid}.json"))
    print(f"== {vid}: {len(salida)} muestras")
    for s in d["segmentos"]:
        cs = [c for t, cc in salida if s["editStart"] <= t < s["editStart"] + s["dur"] for c in cc]
        if not cs:
            print(f"  toma {s['i']:2d} {s['enc']:3s} {s['editStart']:6.2f}s  sin caras"); continue
        # agrupar por posición horizontal (una o dos personas)
        grupos = []
        for c in sorted(cs, key=lambda c: c[0] + c[2] / 2):
            cx = c[0] + c[2] / 2
            if grupos and abs(cx - grupos[-1][-1][0] - grupos[-1][-1][2] / 2) < 160: grupos[-1].append(c)
            else: grupos.append([c])
        txt = []
        for g in grupos:
            if len(g) < 2: continue
            a = np.array(g)
            x0, y0 = np.percentile(a[:, 0], 10), np.percentile(a[:, 1], 10)
            x1, y1 = np.percentile(a[:, 0] + a[:, 2], 90), np.percentile(a[:, 1] + a[:, 3], 90)
            txt.append(f"[x {x0:4.0f}-{x1:4.0f} y {y0:4.0f}-{y1:4.0f} n{len(g)}]")
        print(f"  toma {s['i']:2d} {s['enc']:3s} {s['editStart']:6.2f}-{s['editStart'] + s['dur']:6.2f}s  " + " ".join(txt))
