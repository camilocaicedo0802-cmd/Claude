"""Two thumbnails for Columbia River Highway (1280x720): python thumbs_cr.py OUT_DIR"""
import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from PIL import Image
from timeline import res
from engine import H, RED, W, WHITE, YELLOW, kb_frame, load_image, over, rounded_rect_sprite, text_sprite
OUT = sys.argv[1]
GOLD = (236, 190, 70)


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


# 1: inside the twin tunnels, light at the end + the claim
img = kb_frame(load_image(res("f_10488711553.jpg"), "doc"), 0.5, 0.55, 1.15)
img = (img.astype(np.float32) * 0.62).astype(np.uint8)
img = vignette(img, 0.7)
sp = text_sprite("9 DÍAS", "bebas", 260, YELLOW, True, stroke=7, tracking=6)
over(img, sp, 60, 10)
sp2 = text_sprite("DENTRO DE UN TÚNEL", "bebas", 150, WHITE, True, stroke=6, tracking=4)
over(img, sp2, 60, 290)
boxed(img, "¿POR QUÉ NO SE FUERON?", 70, 500, 96, (15, 15, 15), YELLOW)
s2 = text_sprite("OREGÓN · 1921", "bebas", 70, WHITE, True, stroke=3, tracking=4)
over(img, s2, W - s2.w - 50, H - s2.h - 20)
save(img, "miniatura_1.jpg")

# 2: Mitchell Point 1915 (blown up in 1966) over the new tunnel (2025)
top = kb_frame(load_image(res("f_31741900193.jpg"), "archival"), 0.5, 0.5, 1.1, ow=W, oh=H // 2)
bot = kb_frame(load_image(res("f_52411893685.jpg"), "doc"), 0.5, 0.5, 1.1, ow=W, oh=H // 2)
img = np.concatenate([top, bot], axis=0)
cv2.rectangle(img, (0, H // 2 - 10), (W, H // 2 + 10), (20, 20, 20), -1)
cv2.line(img, (0, H // 2), (W, H // 2), YELLOW, 6)
img = vignette(img, 0.45)
for txt, y, col in (("LO VOLARON EN PEDAZOS…", 40, WHITE), ("…Y LO HICIERON OTRA VEZ", H // 2 + 40, YELLOW)):
    s_ = text_sprite(txt, "bebas", 130, col, True, stroke=6, tracking=4)
    over(img, s_, 50, y)
boxed(img, "1966", W - 330, H // 2 - 170, 100, (15, 15, 15), (230, 70, 60))
boxed(img, "2025", W - 330, H - 190, 100, (15, 15, 15), YELLOW)
save(img, "miniatura_2.jpg")
print("ok")
