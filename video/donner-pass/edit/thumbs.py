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


# 1: the empty tunnel lit by a torch + NADIE LO FIRMÓ
src = load_image("f_6823968520.jpg", "cold")
img = kb_frame(src, 0.42, 0.5, 1.12)
gfx5.flashlight(img, 5.0, 1.0, path=((0.43, 0.45), (0.43, 0.45)), r=520, amb=0.22, wobble=0.0)
img = vignette(img, 0.7)
sp = text_sprite("NADIE LO FIRMÓ", "bebas", 210, WHITE, True, stroke=6, tracking=4)
over(img, sp, W - sp.w - 40, 30)
b = text_sprite("ABIERTO A MANO", "bebas", 140, (15, 15, 15), False, tracking=2)
boxed(img, "ABIERTO A MANO", W - b.w - 60, 250, 140, (15, 15, 15), YELLOW)
s2 = text_sprite("DONNER PASS · TÚNEL 6", "bebas", 78, WHITE, True, stroke=3, tracking=4)
over(img, s2, W - s2.w - 50, H - s2.h - 20)
save(img, "miniatura_1.jpg")

# 2: 1865 laborers (left) vs today's graffiti (right): MILES DE NOMBRES / NINGUNO DE ELLOS
left = kb_frame(load_image("l_1s00510_L.jpg", "archival"), 0.5, 0.5, 1.0, ow=W // 2, oh=H)
right = kb_frame(load_image("f_8306423263.jpg", "none"), 0.78, 0.5, 1.0, ow=W // 2, oh=H)
img = np.concatenate([left, right], axis=1)
img = vignette(img, 0.55)
cv2.line(img, (W // 2, 0), (W // 2, H), (0, 0, 0), 16)
cv2.line(img, (W // 2, 0), (W // 2, H), YELLOW, 6)
sp = text_sprite("MILES DE NOMBRES", "bebas", 150, WHITE, True, stroke=6, tracking=4)
over(img, sp, (W - sp.w) // 2, 20)
b = text_sprite("NI UNO DE ELLOS", "bebas", 150, (15, 15, 15), False, tracking=2)
boxed(img, "NI UNO DE ELLOS", (W - b.w) // 2, 200, 150, (15, 15, 15), YELLOW)
for txt, x in (("ENTONCES", 60), ("HOY", W - 60)):
    s = text_sprite(txt, "bebas", 120, WHITE, True, stroke=5, tracking=6)
    over(img, s, x if x < W // 2 else x - s.w, H - s.h - 20)
cv2.circle(img, (W // 4 + 40, H // 2 + 120), 150, RED, 12, cv2.LINE_AA)
save(img, "miniatura_2.jpg")
print("ok")
