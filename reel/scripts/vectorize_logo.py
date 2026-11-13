"""Vectoriza el logotipo de Macizo a partir del camión de la foto 5 (FOTO MACIZO 5).

Recorta el rótulo, lo amplía 8x, separa las letras negras y la "i" dorada (dos rectángulos) y traza
las letras con potrace. Genera dos SVG: negro y blanco. El lema "Madera en el Diseño" se compone aparte.
Uso: python3 -I vectorize_logo.py <foto_macizo_5.jpg> <carpeta_salida>
"""
import subprocess
import sys

import numpy as np
import potrace  # paquete "potracer"
from scipy import ndimage as ndi

src, out = sys.argv[1], sys.argv[2]
W = 2280
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"crop=285:185:288:893,scale={W}:-1:flags=lanczos",
                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.uint8).reshape(-1, W, 3).astype(float)
H = a.shape[0]
r, g, b = a[..., 0], a[..., 1], a[..., 2]
lum = ndi.gaussian_filter(a @ [0.3, 0.59, 0.11], 2.0)
yy, xx = np.mgrid[0:H, 0:W]
big_zone = (yy > 80) & (yy < 1080) & (xx > 40) & (xx < 2190)


def clean(m, minsz):
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    return np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > minsz])


lum_soft = ndi.gaussian_filter(a @ [0.3, 0.59, 0.11], 2.5)
big = clean((lum_soft < 100) & big_zone, 3000)
# Mediana sobre la máscara: alisa el ruido JPEG ampliado sin redondear las esquinas rectas de las letras.
big = ndi.median_filter(big.astype(np.uint8), size=25).astype(bool)

gold = (r - b > 55) & (r > 110) & (g > 60) & (b < 120) & big_zone
gold = ndi.binary_closing(ndi.binary_opening(gold, iterations=2), structure=np.ones((5, 25)), iterations=2)
big &= ~ndi.binary_dilation(gold, iterations=14)  # sin restos oscuros pegados a la "i" dorada
lab2, n2 = ndi.label(gold)
rects = []
for i in range(1, n2 + 1):
    m = lab2 == i
    if m.sum() < 3000:
        continue
    y_, x_ = np.nonzero(m)
    rects.append(tuple(int(v) for v in (np.percentile(x_, 0.5), np.percentile(y_, 0.5),
                                         np.percentile(x_, 99.5), np.percentile(y_, 99.5))))


def trace(mask):
    # potracer considera "tinta" los píxeles False: se invierte la máscara.
    pl = potrace.Bitmap(~mask).trace(turdsize=300, alphamax=0.9, opticurve=True, opttolerance=0.6)
    d = []
    for c in pl:
        sp = c.start_point
        d.append(f"M{sp.x:.0f},{sp.y:.0f}")
        for s in c.segments:
            if s.is_corner:
                d.append(f"L{s.c.x:.0f},{s.c.y:.0f}L{s.end_point.x:.0f},{s.end_point.y:.0f}")
            else:
                d.append(f"C{s.c1.x:.0f},{s.c1.y:.0f} {s.c2.x:.0f},{s.c2.y:.0f} {s.end_point.x:.0f},{s.end_point.y:.0f}")
        d.append("Z")
    return "".join(d)


# El lema "Madera en el Diseño" se compone como texto en el vídeo (sus trazos finos no se vectorizan bien).
pb = trace(big)
yb, xb = np.nonzero(big)
x0 = min(xb.min(), *[q[0] for q in rects])
y0 = min(yb.min(), *[q[1] for q in rects])
x1 = max(xb.max(), *[q[2] for q in rects])
y1 = yb.max()
pad = 24
vb = f"{x0 - pad} {y0 - pad} {x1 - x0 + 2 * pad} {y1 - y0 + 2 * pad}"
gold_svg = "".join(f'<rect x="{q[0]}" y="{q[1]}" width="{q[2] - q[0] + 1}" height="{q[3] - q[1] + 1}" fill="#E3A51E"/>'
                   for q in rects)
for name, fill in [("macizo_logotipo_negro.svg", "#141414"), ("macizo_logotipo_blanco.svg", "#F5F5F5")]:
    with open(f"{out}/{name}", "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">\n'
                f'<!-- Logotipo de Macizo vectorizado a partir del camión de la foto 5 (potrace) -->\n'
                f'<path d="{pb}" fill="{fill}" fill-rule="evenodd"/>{gold_svg}\n</svg>\n')
print("viewBox", vb, "| barras doradas:", rects)
