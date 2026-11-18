"""Two thumbnails for Natchez Trace (1280x720): python thumbs_kc.py OUT_DIR"""
import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from PIL import Image
from timeline import res
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


# 1: the sunken trace + the claim
img = kb_frame(load_image(res("f_44238521561.jpg"), "doc"), 0.5, 0.5, 1.05)
img = (img.astype(np.float32) * 0.8).astype(np.uint8)
img = vignette(img, 0.6)
sp = text_sprite("67 AÑOS", "bebas", 230, YELLOW, True, stroke=6, tracking=4)
over(img, sp, 50, 10)
sp2 = text_sprite("PARA 2 CARRILES", "bebas", 160, WHITE, True, stroke=6, tracking=4)
over(img, sp2, 50, 240)
boxed(img, "Y NI UNA GASOLINERA", 60, 450, 100, (15, 15, 15), YELLOW)
s2 = text_sprite("NATCHEZ TRACE", "bebas", 70, WHITE, True, stroke=3, tracking=4)
over(img, s2, W - s2.w - 50, H - s2.h - 20)
save(img, "miniatura_1.jpg")

# 2: the empty parkway / the trail dug by feet
top = kb_frame(load_image(res("l_42697.jpg"), "doc"), 0.5, 0.55, 1.0, ow=W, oh=H // 2)
bot = kb_frame(load_image(res("w_grindstone.jpg"), "doc"), 0.5, 0.5, 1.0, ow=W, oh=H // 2)
img = np.concatenate([top, bot], axis=0)
cv2.rectangle(img, (0, H // 2 - 10), (W, H // 2 + 10), (20, 20, 20), -1)
cv2.line(img, (0, H // 2), (W, H // 2), YELLOW, 6)
img = vignette(img, 0.45)
for txt, y, col in (("SIN CAMIONES…", 40, WHITE), ("…Y DEBAJO, ESTO", H // 2 + 40, YELLOW)):
    s = text_sprite(txt, "bebas", 150, col, True, stroke=6, tracking=4)
    over(img, s, 50, y)
boxed(img, "HECHO A PIE", 1330, H // 2 + 300, 100, (15, 15, 15), YELLOW)
save(img, "miniatura_2.jpg")
print("ok")
