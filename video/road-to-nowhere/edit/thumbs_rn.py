"""Two thumbnails for Road to Nowhere (1280x720): python thumbs_rn.py OUT_DIR"""
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


# 1: the unlit tunnel with light at the end + the price
img = kb_frame(load_image("f_50894285987.jpg", "doc"), 0.5, 0.52, 1.08)
gfx5.flashlight(img, 5.0, 1.0, path=((0.5, 0.5), (0.5, 0.5)), r=620, amb=0.32, wobble=0.0)
img = vignette(img, 0.6)
sp = text_sprite("PAGARON", "bebas", 150, WHITE, True, stroke=6, tracking=4)
over(img, sp, 60, 30)
sp2 = text_sprite("$52 MILLONES", "bebas", 230, YELLOW, True, stroke=8, tracking=4)
over(img, sp2, 50, 160)
b = text_sprite("POR NO TERMINARLA", "bebas", 104, (15, 15, 15), False, tracking=2)
boxed(img, "POR NO TERMINARLA", 70, 430, 104, (15, 15, 15), YELLOW)
s2 = text_sprite("UN TÚNEL A NINGUNA PARTE", "bebas", 64, WHITE, True, stroke=3, tracking=4)
over(img, s2, W - s2.w - 50, H - s2.h - 24)
save(img, "miniatura_1.jpg")

# 2: the sign, with the question mark circled
src = load_image("f_36562380744.jpg", "doc")
img = np.full((H, W, 3), 18, np.uint8)
left = kb_frame(src, 0.40, 0.48, 1.0, ow=W // 2 + 180, oh=H)
img[:, :W // 2 + 180] = left
img = vignette(img, 0.45)
# circle around "1943 - ?" on the sign
cv2.ellipse(img, (620, 642), (318, 96), -3, 0, 360, RED, 14, cv2.LINE_AA)

cv2.rectangle(img, (W // 2 + 180, 0), (W, H), (18, 18, 20), -1)
cv2.line(img, (W // 2 + 180, 0), (W // 2 + 180, H), YELLOW, 8)
for txt, y, col, size in (("LA CARRETERA", 70, WHITE, 128), ("QUE NUNCA", 220, WHITE, 128), ("TERMINARON", 370, YELLOW, 140)):
    s = text_sprite(txt, "bebas", size, col, True, stroke=5, tracking=3)
    over(img, s, W // 2 + 215, y)
boxed(img, "LAS TUMBAS, EN LANCHA", W // 2 + 220, 600, 84, (15, 15, 15), YELLOW)
save(img, "miniatura_2.jpg")
print("ok")
