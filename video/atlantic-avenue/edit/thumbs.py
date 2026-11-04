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


# 1: the brick tunnel with a lone explorer + NUEVA YORK LO PERDIÓ
img = kb_frame(load_image("f_4323697878.jpg", "doc"), 0.42, 0.55, 1.1)
gfx5.flashlight(img, 5.0, 1.0, path=((0.36, 0.62), (0.36, 0.62)), r=560, amb=0.35, wobble=0.0)
img = vignette(img, 0.7)
sp = text_sprite("NUEVA YORK", "bebas", 190, WHITE, True, stroke=6, tracking=4)
over(img, sp, W - sp.w - 40, 20)
sp2 = text_sprite("LO PERDIÓ", "bebas", 190, YELLOW, True, stroke=6, tracking=4)
over(img, sp2, W - sp2.w - 40, 200)
b = text_sprite("UN TÚNEL DE 1844", "bebas", 110, (15, 15, 15), False, tracking=2)
boxed(img, "UN TÚNEL DE 1844", W - b.w - 60, 420, 110, (15, 15, 15), YELLOW)
s2 = text_sprite("BAJO ATLANTIC AVENUE · BROOKLYN", "bebas", 64, WHITE, True, stroke=3, tracking=4)
over(img, s2, W - s2.w - 50, H - s2.h - 20)
save(img, "miniatura_1.jpg")

# 2: street above (the manhole) and the vault below, cut in two
top = kb_frame(load_image("f_4322956255.jpg", "doc"), 0.5, 0.62, 1.0, ow=W, oh=H // 2)
bot = kb_frame(load_image("f_4267479707.jpg", "none"), 0.5, 0.55, 1.0, ow=W, oh=H // 2)
bot = np.clip(bot.astype(np.float32) * 1.6 + 6, 0, 255).astype(np.uint8)
img = np.concatenate([top, bot], axis=0)
cv2.rectangle(img, (0, H // 2 - 10), (W, H // 2 + 10), (20, 20, 20), -1)
cv2.line(img, (0, H // 2), (W, H // 2), YELLOW, 6)
img = vignette(img, 0.5)
for txt, y, col in (("ARRIBA: LA CALLE", 30, WHITE), ("ABAJO: 1844", H // 2 + 30, YELLOW)):
    s = text_sprite(txt, "bebas", 150, col, True, stroke=6, tracking=4)
    over(img, s, 50, y)
b = text_sprite("LA ÚNICA PUERTA", "bebas", 96, (15, 15, 15), False, tracking=2)
boxed(img, "LA ÚNICA PUERTA", 1090, 300, 96, (15, 15, 15), YELLOW)
cv2.circle(img, (905, 272), 135, RED, 12, cv2.LINE_AA)
save(img, "miniatura_2.jpg")
print("ok")
