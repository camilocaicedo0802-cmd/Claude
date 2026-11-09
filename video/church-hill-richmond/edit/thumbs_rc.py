"""Two thumbnails for Church Hill (1280x720): python thumbs_rc.py OUT_DIR"""
import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from PIL import Image
import gfx5
from engine import H, RED, W, WHITE, YELLOW, kb_frame, load_image, over, rounded_rect_sprite, text_sprite
OUT = sys.argv[1]


def vignette(img, k=0.75):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    m = np.clip(1 - k * (r - 0.4).clip(0) ** 1.5, 0.15, 1)
    return (img * m[..., None]).astype(np.uint8)


def boxed(img, txt, x, y, size, fg, bg, fname="bebas"):
    sp = text_sprite(txt, fname, size, fg, False, tracking=2)
    bx = rounded_rect_sprite(sp.w - 20, sp.h - 30, bg, 8, 255)
    over(img, bx, x + 10, y + 15)
    over(img, sp, x, y)
    return sp


def save(img, name):
    Image.fromarray(img).resize((1280, 720), Image.LANCZOS).save(f"{OUT}/{name}", quality=92)


# 1: the plugged portal + the claim
img = kb_frame(load_image("f_6991547591.jpg", "doc"), 0.62, 0.5, 1.05)
img = (img.astype(np.float32) * 0.8).astype(np.uint8)
img = vignette(img, 0.6)
sp = text_sprite("UN TREN", "bebas", 200, WHITE, True, stroke=6, tracking=4)
over(img, sp, 50, 20)
sp2 = text_sprite("ENTERRADO", "bebas", 200, YELLOW, True, stroke=6, tracking=4)
over(img, sp2, 50, 200)
boxed(img, "CON SUS HOMBRES DENTRO", 60, 430, 96, (15, 15, 15), YELLOW)
s2 = text_sprite("RICHMOND · 1925", "bebas", 70, WHITE, True, stroke=3, tracking=4)
over(img, s2, W - s2.w - 50, H - s2.h - 20)
save(img, "miniatura_1.jpg")

# 2: the park above, the dark tunnel below
top = kb_frame(load_image("u_GvL__XG0to4.jpg", "doc"), 0.5, 0.6, 1.0, ow=W, oh=H // 2)
bot = kb_frame(load_image("u_9O770ZdQQjs.jpg", "none"), 0.5, 0.5, 1.0, ow=W, oh=H // 2)
img = np.concatenate([top, bot], axis=0)
cv2.rectangle(img, (0, H // 2 - 10), (W, H // 2 + 10), (20, 20, 20), -1)
cv2.line(img, (0, H // 2), (W, H // 2), YELLOW, 6)
img = vignette(img, 0.45)
for txt, y, col in (("ARRIBA: UN PARQUE", 40, WHITE), ("ABAJO: LA 231", H // 2 + 40, YELLOW)):
    s = text_sprite(txt, "bebas", 150, col, True, stroke=6, tracking=4)
    over(img, s, 50, y)
boxed(img, "DESDE 1925", 1260, H // 2 + 300, 104, (15, 15, 15), YELLOW)
save(img, "miniatura_2.jpg")
print("ok")
