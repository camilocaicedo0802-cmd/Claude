"""Miniaturas 1280x720 al estilo de los ejemplos: fondo oscuro, figura central con brillo rojo, 2-3 palabras enormes."""
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import grade, kb_frame, load_image  # noqa: E402
from mist import LightTunnel, Rings  # noqa: E402
from timeline import S  # noqa: E402

W, H = 1920, 1080
FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
RED = (235, 22, 34)
WHT = (255, 255, 255)
YEL = (255, 214, 10)


def vframe(key, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", S(key), "-frames:v", "1", "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    return np.asarray(Image.open(__import__("io").BytesIO(raw)).convert("RGB"))


def cover(img, cx=0.5, cy=0.5, z=1.0):
    return kb_frame(img, cx, cy, z, ow=W, oh=H)


def red_grade(img, k=0.6):
    f = img.astype(np.float32) / 255
    g = f.mean(-1, keepdims=True)
    f = g + (f - g) * 0.5
    f = f * np.array([1 + 0.5 * k, 1 - 0.35 * k, 1 - 0.4 * k])
    f = 0.5 + (f - 0.5) * 1.25
    return np.clip(f * 255, 0, 255).astype(np.uint8)


def vignette(img, s=0.75):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = np.clip(1 - s * np.clip(r - 0.35, 0, None) ** 1.3, 0.12, 1)[..., None]
    return (img * v).astype(np.uint8)


def glow_behind(img, cx, cy, r, color=RED, a=0.9):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r ** 2)))[..., None] * a
    return np.clip(img + g * np.array(color), 0, 255).astype(np.uint8)


def big_text(im, lines, x, y, size, align="left", stroke=10, glow=RED):
    """lines: [(texto, color)], apiladas. Texto con contorno negro grueso y halo de color."""
    f = ImageFont.truetype(os.path.join(FONTS, "BebasNeue.ttf"), size)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    gl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d, dg = ImageDraw.Draw(lay), ImageDraw.Draw(gl)
    yy = y
    for txt, col in lines:
        w = f.getlength(txt)
        xx = x if align == "left" else x - w / 2 if align == "center" else x - w
        dg.text((xx, yy), txt, font=f, fill=glow + (255,), stroke_width=stroke + 14, stroke_fill=glow + (255,))
        d.text((xx, yy), txt, font=f, fill=col + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
        yy += size * 0.86
    gl = gl.filter(ImageFilter.GaussianBlur(28))
    out = Image.alpha_composite(im.convert("RGBA"), Image.blend(Image.new("RGBA", im.size, (0, 0, 0, 0)), gl, 0.75))
    return Image.alpha_composite(out, lay)


def red_circle(im, cx, cy, r, w=12):
    d = ImageDraw.Draw(im)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED + (255,), width=w)
    return im


def arrow(im, x0, y0, x1, y1, w=16):
    d = ImageDraw.Draw(im)
    d.line([x0, y0, x1, y1], fill=RED + (255,), width=w)
    v = np.array([x1 - x0, y1 - y0], float)
    v /= np.linalg.norm(v)
    n = np.array([-v[1], v[0]])
    p = np.array([x1, y1])
    d.polygon([tuple(p + v * 30), tuple(p - v * 20 + n * 34), tuple(p - v * 20 - n * 34)], fill=RED + (255,))
    return im


def save(im, path):
    im.convert("RGB").resize((1280, 720), Image.LANCZOS).save(path, quality=93)
    print(path)


def thumb1(out):  # bebé + túnel de luz: "¿YA MORISTE ANTES?"
    lt = LightTunnel((1.0, 1.0))
    lt.setup(1)
    bg = lt.frame(0.5).astype(np.float32)
    bg = np.roll(bg, int(W * 0.22), 1)
    baby = cover(load_image(S("us_JoeYzwliXto"), "none"), 0.5, 0.45, 1.05)
    baby = (red_grade(baby, 0.85).astype(np.float32) * 0.78)
    mask = np.zeros((H, W), np.float32)
    mask[:, : int(W * 0.62)] = 1
    mask = cv2.GaussianBlur(mask, (0, 0), 120)[..., None]
    img = baby * mask + bg * (1 - mask) * np.array([1.0, 0.85, 0.75])
    img = glow_behind(np.clip(img, 0, 255).astype(np.uint8), W * 0.9, H * 0.55, 220, (255, 245, 230), 0.8).astype(np.float32)
    img = vignette(np.clip(img, 0, 255).astype(np.uint8), 0.6)
    im = Image.fromarray(img)
    im = big_text(im, [("¿YA MORISTE", WHT), ("ANTES?", RED)], W * 0.97, H * 0.08, 240, "right")
    return save(im, out)


def thumb2(out):  # silueta caminando hacia la luz: "NO ES EL CIELO"
    fr = vframe("mk_4747", 4.0)
    img = cover(fr, 0.5, 0.5, 1.15)
    img = red_grade(img, 0.35)
    img = glow_behind(img, W * 0.5, H * 0.45, 260, (255, 240, 220), 0.9)
    img = vignette(img, 0.8)
    im = Image.fromarray(img)
    im = big_text(im, [("NO ES", WHT), ("EL CIELO", RED)], W * 0.04, H * 0.3, 270, "left")
    im = arrow(im, W * 0.86, H * 0.16, W * 0.6, H * 0.38)
    return save(im, out)


def thumb3(out):  # foto antigua de bebé enmarcada con círculo rojo: "VIDA Nº 1000"
    bg = cover(load_image(S("wm_pieter-bruegel-the-elder-the-tower"), "none"), 0.5, 0.5, 1.1)
    bg = (red_grade(bg, 0.8) * 0.35).astype(np.uint8)
    bg = cv2.GaussianBlur(bg, (0, 0), 6)
    im = Image.fromarray(vignette(bg, 0.6)).convert("RGBA")
    ph = Image.fromarray(grade(load_image(S("wm_vera-andersen"), "none"), "sepia"))
    ph.thumbnail((620, 760))
    card = Image.new("RGBA", (ph.width + 36, ph.height + 36), (245, 240, 230, 255))
    card.paste(ph, (18, 18))
    card = card.rotate(-5, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    px, py = int(W * 0.06), int(H * 0.1)
    sh.paste((0, 0, 0, 200), (px + 20, py + 26, px + 20 + card.width, py + 26 + card.height))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(20)))
    im.paste(card, (px, py), card)
    im = red_circle(im, px + card.width * 0.5, py + card.height * 0.33, 150)
    im = big_text(im, [("VIDA", WHT), ("Nº 1000", RED)], W * 0.96, H * 0.14, 300, "right")
    return save(im, out)


if __name__ == "__main__":
    d = sys.argv[1]
    os.makedirs(d, exist_ok=True)
    thumb1(os.path.join(d, "miniatura_1.jpg"))
    thumb2(os.path.join(d, "miniatura_2.jpg"))
    thumb3(os.path.join(d, "miniatura_3.jpg"))
