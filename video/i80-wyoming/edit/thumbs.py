import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from PIL import Image
import gfx3, maps
from engine import H, RED, W, WHITE, YELLOW, grade, kb_frame, load_image, over, over_center, rounded_rect_sprite, text_sprite
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


# 1: blowing snow + gate + CERRADA EN 4 DÍAS
src = load_image("f_55252804633.jpg", "cold")
img = kb_frame(src, 0.5, 0.55, 1.12)
img = vignette(img, 0.9)
gfx3.gate_overlay(img, 3.0, 4.0, t0=0.0, x=0.08, y=0.74, length=0.62)
sp = text_sprite("CERRADA", "bebas", 300, WHITE, True, stroke=6, tracking=6)
over(img, sp, 980, 90)
boxed(img, "EN 4 DÍAS", 1080, 380, 210, (15, 15, 15), YELLOW)
s2 = text_sprite("I-80 · WYOMING", "bebas", 84, WHITE, True, tracking=6)
over(img, s2, 1140, 640)
Image.fromarray(img).resize((1280, 720), Image.LANCZOS).save(f"{OUT}/miniatura_1.jpg", quality=92)

# 2: map with red I-80 + wind + "EL ATAJO QUE EL VIENTO CERRÓ"
ms = maps.MapScene("loc", [(0, -106.35, 41.62, 0.95)],
                   [dict(type="road", name="80", level="Interstate", bbox=(-107.7, 40.9, -105.0, 42.3), t0=-5, draw=0.01, color=RED, width=14),
                    dict(type="road", name="30", level="Federal", bbox=(-107.0, 41.2, -105.5, 42.1), t0=-5, draw=0.01, color=(200, 200, 200), width=6),
                    dict(type="pin", at="elk_mtn", t0=-5, color=WHITE, pulse=False)])
ms.setup(10)
img = ms.frame(3.0)
bm = maps.basemap("loc")
ex, ey = bm.px(*maps.COORDS["elk_mtn"])
cx, cy = bm.px(-106.35, 41.62)
fl = gfx3.FlowOverlay(960 + (ex - cx) * 0.95, 540 + (ey - cy) * 0.95, 95, t0=-5, label_text=None)
fl.draw(img, 3.0, 10)
img = vignette(img, 0.7)
sp = text_sprite("19 MILLAS", "bebas", 230, YELLOW, True, stroke=5, tracking=4)
over(img, sp, 60, 40)
sp = text_sprite("QUE EL VIENTO", "bebas", 150, WHITE, True, stroke=5, tracking=4)
over(img, sp, 60, 270)
sp = text_sprite("NO PERDONA", "bebas", 150, WHITE, True, stroke=5, tracking=4)
over(img, sp, 60, 420)
boxed(img, "I-80 · WYOMING", 70, 880, 80, (15, 15, 15), YELLOW)
Image.fromarray(img).resize((1280, 720), Image.LANCZOS).save(f"{OUT}/miniatura_2.jpg", quality=92)
print("ok")
