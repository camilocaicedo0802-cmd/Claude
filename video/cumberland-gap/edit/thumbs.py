import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from PIL import Image
import gfx4
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


def red_x(img, cx, cy, s, th=26):
    for sg in (1, -1):
        cv2.line(img, (int(cx - s), int(cy - s * sg)), (int(cx + s), int(cy + s * sg)), (0, 0, 0), th + 14, cv2.LINE_AA)
        cv2.line(img, (int(cx - s), int(cy - s * sg)), (int(cx + s), int(cy + s * sg)), RED, th, cv2.LINE_AA)


# 1: the hairpin road with a red X + LA BORRARON
src = load_image("u_F3edSiwSJkw.jpg", "doc")
img = kb_frame(src, 0.5, 0.5, 1.05)
img = vignette(img, 0.9)
img = (img * 0.82).astype(np.uint8)
red_x(img, 1320, 860, 150, 24)
sp = text_sprite("LA BORRARON", "bebas", 230, WHITE, True, stroke=6, tracking=4)
over(img, sp, 50, 40)
boxed(img, "A PROPÓSITO", 70, 300, 150, (15, 15, 15), YELLOW)
s2 = text_sprite("MASSACRE MOUNTAIN · US-25E", "bebas", 74, WHITE, True, stroke=3, tracking=4)
over(img, s2, 70, 900)
Image.fromarray(img).resize((1280, 720), Image.LANCZOS).save(f"{OUT}/miniatura_1.jpg", quality=92)

# 2: the mountain diagram: road over the top crossed out, tunnel below, 40 AÑOS
img = gfx4._pass_bg().copy()
road = gfx4._surface(gfx4.X0 + 40, gfx4.X1 - 40, 24)
from gfx2 import aa_poly
aa_poly(img, road, (0, 0, 0), 22)
aa_poly(img, road, YELLOW, 12)
xs, ys = gfx4._pass_profile()
top = int(xs[np.argmin(ys)])
red_x(img, top, int(ys.min()) + 10, 110, 22)
gfx4._tube(img, gfx4.PX0, gfx4.PX1, gfx4.TY + 40, YELLOW, 34)
gfx4._traffic(img, np.array([[0, gfx4.TY + 40], [W, gfx4.TY + 40]], float), 1.0, 7, 0.16, r=12)
sp = text_sprite("40 AÑOS", "bebas", 250, YELLOW, True, stroke=6, tracking=6)
over(img, sp, 60, 10)
sp = text_sprite("PARA BORRAR", "bebas", 100, WHITE, True, stroke=4, tracking=3)
over(img, sp, 70, 250)
sp = text_sprite("UNA CARRETERA", "bebas", 100, WHITE, True, stroke=4, tracking=3)
over(img, sp, 70, 350)
boxed(img, "CUMBERLAND GAP", 1290, 960, 80, (15, 15, 15), YELLOW)
img = vignette(img, 0.6)
Image.fromarray(img).resize((1280, 720), Image.LANCZOS).save(f"{OUT}/miniatura_2.jpg", quality=92)
print("ok")
