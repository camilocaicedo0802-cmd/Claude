"""Portadas verticales 1080x1920 para los 3 shorts (mismo estilo que las miniaturas)."""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thumbs_mist as T  # noqa: E402
from engine import load_image  # noqa: E402

T.W, T.H = 1080, 1920
W, H = T.W, T.H


def finish(im, path):
    im.convert("RGB").save(path, quality=93)
    print(path)


def c1(path):
    fr = T.vframe("mk_4747", 4.0)
    img = T.cover(fr, 0.5, 0.5, 1.0)
    img = T.red_grade(img, 0.35)
    img = T.glow_behind(img, W * 0.5, H * 0.45, 300, (255, 240, 220), 0.9)
    im = Image.fromarray(T.vignette(img, 0.7))
    im = T.big_text(im, [("¿Y SI ESA LUZ", T.WHT)], W / 2, H * 0.07, 170, "center")
    im = T.big_text(im, [("NO ES", T.WHT), ("EL CIELO?", T.RED)], W / 2, H * 0.66, 230, "center")
    finish(im, path)


def c2(path):
    img = T.cover(load_image(T.S("us_JoeYzwliXto"), "none"), 0.45, 0.5, 1.0)
    img = (T.red_grade(img, 0.85) * 0.8).astype(np.uint8)
    im = Image.fromarray(T.vignette(img, 0.7))
    im = T.big_text(im, [("¿POR QUÉ NO", T.WHT), ("RECUERDAS", T.WHT)], W / 2, H * 0.06, 190, "center")
    im = T.big_text(im, [("TUS OTRAS", T.RED), ("VIDAS?", T.RED)], W / 2, H * 0.66, 230, "center")
    finish(im, path)


def c3(path):
    fr = T.vframe("mk_4504", 4.0)
    img = T.cover(fr, 0.5, 0.45, 1.0)
    img = (T.red_grade(img, 0.7) * 0.85).astype(np.uint8)
    im = Image.fromarray(T.vignette(img, 0.7))
    im = T.big_text(im, [("¿LO ESTÁS", T.WHT), ("VIVIENDO", T.WHT)], W / 2, H * 0.06, 200, "center")
    im = T.big_text(im, [("OTRA VEZ?", T.RED)], W / 2, H * 0.74, 250, "center")
    finish(im, path)


if __name__ == "__main__":
    d = sys.argv[1]
    os.makedirs(d, exist_ok=True)
    c1(os.path.join(d, "portada_short_1.jpg"))
    c2(os.path.join(d, "portada_short_2.jpg"))
    c3(os.path.join(d, "portada_short_3.jpg"))
