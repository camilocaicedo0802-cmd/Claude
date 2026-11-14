"""Recorta la mitad izquierda de las estereografías de la Library of Congress (l_1s*.jpg) quitando el cartón
del soporte (columnas/filas con saturación mediana >= 0.42) y guarda l_<id>_L.jpg.

usage: python stereo_crop.py CARPETA_IMG"""
import glob, os, sys
import numpy as np
from PIL import Image


def run(mask):
    best, s = (0, 0, 0), None
    for i, v in enumerate(list(mask) + [False]):
        if v and s is None:
            s = i
        if not v and s is not None:
            if i - s > best[0]:
                best = (i - s, s, i)
            s = None
    return best[1], best[2]


for p in sorted(glob.glob(os.path.join(sys.argv[1], "l_1s*.jpg"))):
    if p.endswith("_L.jpg"):
        continue
    im = Image.open(p).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    H, W, _ = a.shape
    half = a[:, :int(W * 0.5)]
    mx, mn = half.max(2), half.min(2)
    sat = (mx - mn) / (mx + 1)
    x0, x1 = run(np.median(sat, 0) < 0.42)
    y0, y1 = run(np.median(sat[:, x0:x1], 1) < 0.42)
    if x1 - x0 < W * 0.25 or y1 - y0 < H * 0.4:
        x0, x1, y0, y1 = int(W * 0.06), int(W * 0.47), int(H * 0.06), int(H * 0.86)
    px, py = int(0.025 * (x1 - x0)), int(0.025 * (y1 - y0))
    crop = im.crop((x0 + px, y0 + py, x1 - px, y1 - py))
    q = p[:-4] + "_L.jpg"
    crop.save(q, quality=93)
    print(os.path.basename(q), crop.size)
