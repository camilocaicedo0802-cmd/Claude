"""Natchez Trace (1742-2026): diagrams drawn in code for this episode."""
import math

import cv2
import numpy as np

from engine import BLACK, H, RED, W, WHITE, YELLOW, Sprite, clamp, ease_back, ease_in, ease_io, ease_out, lerp, over, \
    over_center, prog, rounded_rect_sprite, text_sprite
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

LOESS = (176, 150, 112)
LOESS_DK = (140, 116, 84)
SOIL = (92, 74, 56)
GRASS = (78, 110, 64)
TREE = (52, 82, 52)
WATER = (52, 92, 128)
WATER_HI = (100, 150, 190)
WOOD = (150, 112, 70)
WOOD_DK = (104, 76, 46)
ASPHALT = (58, 60, 64)
PAPER = (234, 228, 212)
INK = (34, 32, 30)
GREEN = (80, 190, 110)


def _blend(img, layer, a):
    if a > 0.001:
        cv2.addWeighted(layer, min(a, 1.0), img, 1 - min(a, 1.0), 0, img)


def _tag(img, txt="ESQUEMA", a=0.7):
    label(img, txt, W - 160, H - 46, a, 30, GREY)


def _grad(top, bot):
    g = np.linspace(0, 1, H)[:, None, None]
    img = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    return np.repeat(img, W, axis=1).astype(np.uint8)


def _walker(img, x, y, s, col=WHITE, phase=0.0, pack=False):
    cv2.circle(img, (int(x), int(y - 2.6 * s)), int(0.45 * s), col, -1, cv2.LINE_AA)
    cv2.line(img, (int(x), int(y - 2.1 * s)), (int(x), int(y - 1.0 * s)), col, max(2, int(s * 0.35)), cv2.LINE_AA)
    sw = math.sin(phase) * 0.45
    for sg in (1, -1):
        cv2.line(img, (int(x), int(y - 1.0 * s)), (int(x + sg * sw * s), int(y)), col, max(2, int(s * 0.3)), cv2.LINE_AA)
        cv2.line(img, (int(x), int(y - 1.9 * s)), (int(x - sg * sw * s * 0.8), int(y - 1.2 * s)), col, max(2, int(s * 0.25)), cv2.LINE_AA)
    if pack:
        cv2.rectangle(img, (int(x - 0.75 * s), int(y - 2.1 * s)), (int(x - 0.2 * s), int(y - 1.3 * s)), WOOD, -1)


def _tree(img, x, y, s, a=1.0, col=TREE):
    cv2.line(img, (int(x), int(y)), (int(x), int(y - s)), (70, 56, 40), max(2, int(s / 6)), cv2.LINE_AA)
    cv2.circle(img, (int(x), int(y - 1.35 * s)), int(0.6 * s), col, -1, cv2.LINE_AA)


# ---------------------------------------------------------------- the river trip down and the walk home
def flatboat(t, dur, mode="down", t0=0.3, back_t=None):
    """The rivers carry the flatboat south for free; the way home is on foot, against the current."""
    img = _grad((40, 52, 66), (86, 102, 112))
    ry = 600
    fill_poly(img, [[0, ry], [W, ry], [W, H], [0, H]], WATER)
    rng = np.random.default_rng(4)
    for i in range(70):
        x = (rng.uniform(0, W) + t * 140) % W
        y = rng.uniform(ry + 16, H - 20)
        cv2.line(img, (int(x), int(y)), (int(x + rng.uniform(30, 90)), int(y)), WATER_HI, 2, cv2.LINE_AA)
    fill_poly(img, [[0, ry - 6], [W, ry - 6], [W, ry + 4], [0, ry + 4]], (72, 92, 70))
    for x in range(30, W, 70):
        _tree(img, x + 10 * math.sin(x), ry - 4, 44 + 14 * math.sin(x * 0.7))
    # current arrows
    for j in range(4):
        x0 = ((t * 160 + j * 480) % (W + 300)) - 150
        cv2.arrowedLine(img, (int(x0), 900), (int(x0 + 200), 900), (200, 220, 240), 5, cv2.LINE_AA, tipLength=0.25)
    label(img, "CORRIENTE", 220, 980, 0.8, 40, (200, 220, 240))
    label(img, "NORTE", 90, 300, 0.9, 50, WHITE, anchor="l")
    label(img, "SUR", W - 90, 300, 0.9, 50, WHITE, anchor="r")
    if mode == "down":
        k = ease_io(prog(t, t0, dur - t0 - 0.3))
        bx = lerp(160, 1500, k)
        by = ry + 10 + 6 * math.sin(t * 2)
        fill_poly(img, [[bx - 170, by], [bx + 170, by], [bx + 150, by + 50], [bx - 150, by + 50]], WOOD_DK)
        fill_poly(img, [[bx - 140, by - 70], [bx + 120, by - 70], [bx + 120, by], [bx - 140, by]], WOOD)
        for k2 in range(3):
            cv2.circle(img, (int(bx - 100 + k2 * 70), int(by - 90)), 22, (120, 84, 50), -1, cv2.LINE_AA)
        label(img, "RÍO ABAJO: GRATIS", W / 2, 180, ease_out(prog(t, t0, 0.4)), 70, YELLOW)
    else:
        bt = back_t if back_t is not None else t0
        k = ease_io(prog(t, bt, dur - bt - 0.3))
        x = lerp(W - 200, 260, k)
        _walker(img, x, ry - 8, 36, WHITE, t * 8, pack=True)
        label(img, "LA VUELTA: A PIE, CONTRA EL RÍO", W / 2, 180, ease_out(prog(t, bt, 0.4)), 66, YELLOW)
        label(img, "+400 MILLAS · 650 KM", W / 2, 260, ease_out(prog(t, bt + 0.8, 0.4)), 50, WHITE)
    _tag(img)
    return img


def treadmill(t, dur, t0=0.3):
    """A treadmill running the wrong way: the belt carries you down; the way back costs your feet."""
    img = background("dark_grid", t)
    cx, cy = W / 2, 640
    x0, x1 = cx - 600, cx + 600
    cv2.rectangle(img, (int(x0), cy), (int(x1), cy + 40), (60, 62, 68), -1)
    for x in np.arange(x0, x1, 40):
        xx = x0 + ((x - x0 + t * 260) % (x1 - x0))
        cv2.line(img, (int(xx), cy + 4), (int(xx), cy + 36), (100, 102, 110), 3)
    for xr in (x0, x1):
        cv2.circle(img, (int(xr), cy + 20), 32, (90, 92, 98), -1, cv2.LINE_AA)
    _walker(img, cx - 80 + 30 * math.sin(t * 2), cy, 60, WHITE, t * 9, pack=True)
    cv2.arrowedLine(img, (int(x0 + 100), cy + 120), (int(x1 - 100), cy + 120), WATER_HI, 7, cv2.LINE_AA, tipLength=0.04)
    label(img, "EL RÍO TE BAJABA GRATIS", W / 2, cy + 190, ease_out(prog(t, t0, 0.4)), 54, WATER_HI)
    cv2.arrowedLine(img, (int(cx + 260), cy - 300), (int(cx - 260), cy - 300), YELLOW, 7, cv2.LINE_AA, tipLength=0.08)
    label(img, "LA VUELTA LA PAGABAS CON LOS PIES", W / 2, cy - 380, ease_out(prog(t, t0 + 1.2, 0.4)), 58, YELLOW)
    _tag(img, "ILUSTRACIÓN")
    return img


# ---------------------------------------------------------------- the sunken trace, cross-section through time
def sunken(t, dur, t0=0.3, yrs=(1800, 1840), deep_d=None, person=True, roots_t=None):
    img = _grad((60, 84, 70), (130, 150, 120))
    gy = 380
    d_k = ease_io(prog(t, t0, deep_d if deep_d is not None else dur - t0 - 0.5))
    depth = 40 + 330 * d_k
    cx = W / 2
    half_top = 200 + 160 * d_k
    half_bot = 120
    xs = np.array([0, cx - half_top - 30, cx - half_top, cx - half_bot, cx + half_bot, cx + half_top, cx + half_top + 30, W])
    ys = np.array([gy, gy, gy + 6, gy + depth, gy + depth, gy + 6, gy, gy])
    fill_poly(img, np.vstack([np.stack([xs, ys], 1), [[W, H], [0, H]]]), LOESS)
    rng = np.random.default_rng(3)
    for _ in range(140):
        x, y = rng.uniform(0, W), rng.uniform(gy + 10, H)
        if abs(x - cx) < half_bot and y < gy + depth:
            continue
        cv2.circle(img, (int(x), int(y)), 2, LOESS_DK, -1)
    # trees on top
    for x in list(range(40, int(cx - half_top - 40), 110)) + list(range(int(cx + half_top + 60), W, 110)):
        _tree(img, x, gy, 70 + 10 * math.sin(x))
    # hanging roots
    rk = ease_out(prog(t, roots_t if roots_t is not None else t0 + (deep_d or dur) * 0.5, 0.8)) if d_k > 0.4 else 0.0
    if rk > 0:
        for sgn in (-1, 1):
            for j in range(9):
                f = (j + 0.5) / 9
                x = cx + sgn * lerp(half_top, half_bot, f)
                y = gy + depth * f
                L = (30 + 50 * rng.uniform()) * rk
                pts = np.array([[x, y], [x - sgn * 8, y + L * 0.5], [x - sgn * 4, y + L]])
                aa_poly(img, pts, (96, 70, 46), 3)
    # dust plume of passing feet / hooves
    n = int(max(0, t - t0) * 2.5)
    for k in range(3):
        ph = (t * 0.6 + k / 3) % 1
        x = cx - half_bot + ph * 2 * half_bot
        _walker(img, x, gy + depth, 26, (40, 40, 44), t * 9 + k)
    if person and d_k > 0.85:
        a = ease_out(prog(d_k, 0.85, 0.15))
        # two people stacked for scale
        x = cx + half_bot + 60
        cv2.line(img, (int(x), int(gy)), (int(x), int(gy + depth)), YELLOW, 3, cv2.LINE_AA)
        label(img, "MÁS ALTO QUE DOS PERSONAS", x + 30, gy + depth / 2, a, 46, YELLOW, anchor="l")
    yr = int(lerp(yrs[0], yrs[1], d_k))
    label(img, str(yr), 160, 120, 0.9, 80, WHITE, anchor="l")
    label(img, "POLVO FINO (LOESS) · PISADAS, CASCOS Y LLUVIA", W / 2, H - 70, ease_out(prog(t, t0, 0.4)), 46, INK)
    _tag(img)
    return img


# ---------------------------------------------------------------- a stand (inn): what you got for the night
def stand_menu(t, dur, t0=0.3, step=0.6, times=None, sleep_t=None):
    img = background("dark_grid", t)
    pw, ph = 900, 820
    rng = np.random.default_rng(6)
    paper = np.clip(np.full((ph, pw, 3), PAPER, np.float32) + rng.normal(0, 4, (ph, pw, 1)), 0, 255).astype(np.uint8)

    def txt(s, x, y, size, col=INK, f="serif", a=1.0, anchor="c"):
        sp = text_sprite(s, f, size, col, False)
        xx = x - sp.w / 2 if anchor == "c" else x - 24
        over(paper, sp, xx, y - sp.h / 2, a)

    txt("POSADA · «STAND»", pw / 2, 80, 54)
    cv2.line(paper, (80, 130), (pw - 80, 130), (120, 112, 100), 2)
    items = ["SÉMOLA DE MAÍZ", "TOCINO", "GALLETAS", "CAFÉ", "UN TRAGO DE WHISKY"]
    for i, s in enumerate(items):
        a = ease_out(prog(t, times[i] if times else t0 + i * step, 0.35))
        txt("· " + s, 120, 210 + i * 80, 46, INK, "type", a, anchor="l")
    st = sleep_t if sleep_t is not None else t0 + len(items) * step + 0.4
    sk = ease_out(prog(t, st, 0.4))
    cv2.line(paper, (80, 620), (pw - 80, 620), (120, 112, 100), 1)
    txt("CAMA: EL SUELO, JUNTO A DESCONOCIDOS", pw / 2, 680, 34, (150, 30, 40), "type", sk)
    txt("(O EL PORCHE)", pw / 2, 740, 30, (150, 30, 40), "type", sk)
    sprite = Sprite(np.dstack([paper, np.full(paper.shape[:2], 255, np.uint8)]))
    over_center(img, sprite, W / 2, H / 2 + 10, 1.0, 0.95)
    label(img, "ILUSTRACIÓN", W - 150, H - 46, 0.75, 30, GREY)
    return img


# ---------------------------------------------------------------- comparisons
def bars(t, dur, rows, title=None, t0=0.3, step=0.7, unit_max=None, times=None):
    """rows: [(label, value, text, color)] horizontal bars, log-ish scale when values differ a lot."""
    img = background("dark_grid", t)
    vmax = unit_max or max(r[1] for r in rows)
    x0, x1 = 560, 1480
    for i, (lab, v, txt, col) in enumerate(rows):
        a = ease_out(prog(t, times[i] if times else t0 + i * step, 0.4))
        k = ease_out(prog(t, (times[i] if times else t0 + i * step) + 0.1, 1.0))
        y = 380 + i * 200
        label(img, lab, x0 - 40, y, a, 54, WHITE, anchor="r")
        wv = max(8, (x1 - x0) * v / vmax * k)
        cv2.rectangle(img, (x0, int(y - 34)), (int(x0 + wv), int(y + 34)), col, -1)
        label(img, txt, x0 + wv + 30, y, a * ease_out(prog(k, 0.8, 0.2)), 54, col, anchor="l")
    if title:
        label(img, title, W / 2, 170, ease_out(prog(t, 0.1, 0.4)), 60, GREY)
    return img


def fuel(t, dur, t0=0.2):
    img = np.full((H, W, 3), (10, 10, 12), np.uint8)
    cx, cy, R = W / 2, 700, 380
    cv2.ellipse(img, (int(cx), int(cy)), (R, R), 0, 200, 340, (90, 92, 98), 8, cv2.LINE_AA)
    for k in range(5):
        a = math.radians(200 + k * 35)
        p0 = (int(cx + math.cos(a) * (R - 30)), int(cy + math.sin(a) * (R - 30)))
        p1 = (int(cx + math.cos(a) * (R + 10)), int(cy + math.sin(a) * (R + 10)))
        cv2.line(img, p0, p1, (170, 170, 176), 6, cv2.LINE_AA)
    label(img, "E", cx + math.cos(math.radians(200)) * (R + 70), cy + math.sin(math.radians(200)) * (R + 70), 1, 70, RED)
    label(img, "F", cx + math.cos(math.radians(340)) * (R + 70), cy + math.sin(math.radians(340)) * (R + 70), 1, 70, WHITE)
    k = ease_io(prog(t, t0, dur - t0))
    a = math.radians(lerp(285, 222, k))
    cv2.line(img, (int(cx), int(cy)), (int(cx + math.cos(a) * (R - 50)), int(cy + math.sin(a) * (R - 50))), (60, 140, 255), 12, cv2.LINE_AA)
    cv2.circle(img, (int(cx), int(cy)), 26, (60, 140, 255), -1, cv2.LINE_AA)
    if k > 0.6 and int(t * 3) % 2 == 0:
        cv2.circle(img, (int(cx - 220), int(cy + 120)), 26, (255, 170, 40), -1, cv2.LINE_AA)
        label(img, "RESERVA", cx - 170, cy + 120, 1.0, 40, (255, 170, 40), anchor="l")
    _tag(img, "ILUSTRACIÓN")
    return img


# ---------------------------------------------------------------- the rules of a park shaped like a road
def _icon(img, kind, x, y, s, col):
    if kind == "truck":
        cv2.rectangle(img, (int(x - 1.2 * s), int(y - 0.6 * s)), (int(x + 0.4 * s), int(y + 0.4 * s)), col, -1)
        cv2.rectangle(img, (int(x + 0.45 * s), int(y - 0.3 * s)), (int(x + 1.1 * s), int(y + 0.4 * s)), col, -1)
        for wx in (-0.8, 0.0, 0.8):
            cv2.circle(img, (int(x + wx * s), int(y + 0.55 * s)), int(0.22 * s), col, -1, cv2.LINE_AA)
    elif kind == "billboard":
        cv2.rectangle(img, (int(x - 1.1 * s), int(y - 0.8 * s)), (int(x + 1.1 * s), int(y + 0.1 * s)), col, -1)
        cv2.line(img, (int(x - 0.5 * s), int(y + 0.1 * s)), (int(x - 0.5 * s), int(y + 0.9 * s)), col, max(3, int(s * 0.15)))
        cv2.line(img, (int(x + 0.5 * s), int(y + 0.1 * s)), (int(x + 0.5 * s), int(y + 0.9 * s)), col, max(3, int(s * 0.15)))
    elif kind == "fuel":
        cv2.rectangle(img, (int(x - 0.6 * s), int(y - 0.9 * s)), (int(x + 0.4 * s), int(y + 0.9 * s)), col, -1)
        cv2.rectangle(img, (int(x - 0.4 * s), int(y - 0.7 * s)), (int(x + 0.2 * s), int(y - 0.2 * s)), (16, 17, 19), -1)
        cv2.line(img, (int(x + 0.4 * s), int(y - 0.4 * s)), (int(x + 0.9 * s), int(y)), col, max(3, int(s * 0.12)), cv2.LINE_AA)
        cv2.line(img, (int(x + 0.9 * s), int(y)), (int(x + 0.9 * s), int(y + 0.6 * s)), col, max(3, int(s * 0.12)), cv2.LINE_AA)
    elif kind == "light":
        cv2.rectangle(img, (int(x - 0.4 * s), int(y - 1.0 * s)), (int(x + 0.4 * s), int(y + 1.0 * s)), col, -1)
        for k in range(3):
            cv2.circle(img, (int(x), int(y - 0.6 * s + k * 0.6 * s)), int(0.22 * s), (16, 17, 19), -1, cv2.LINE_AA)
    elif kind == "shop":
        fill_poly(img, [[x - 1.0 * s, y + 0.8 * s], [x - 1.0 * s, y - 0.3 * s], [x, y - 1.0 * s], [x + 1.0 * s, y - 0.3 * s],
                        [x + 1.0 * s, y + 0.8 * s]], col)


def rules(t, dur, t0=0.3, step=0.6, times=None, speed_t=None):
    img = background("dark_grid", t)
    items = [("truck", "CAMIONES"), ("billboard", "CARTELES"), ("fuel", "GASOLINERAS"), ("light", "SEMÁFOROS"), ("shop", "TIENDAS")]
    for i, (k, s) in enumerate(items):
        a = ease_out(prog(t, times[i] if times else t0 + i * step, 0.35))
        if a <= 0:
            continue
        x = W * (0.12 + 0.19 * i)
        y = 420
        layer = img.copy()
        _icon(layer, k, x, y, 70, (200, 200, 206))
        cv2.circle(layer, (int(x), int(y)), 120, RED, 10, cv2.LINE_AA)
        cv2.line(layer, (int(x - 85), int(y - 85)), (int(x + 85), int(y + 85)), RED, 10, cv2.LINE_AA)
        _blend(img, layer, a)
        label(img, s, x, y + 180, a, 44, WHITE)
    st = speed_t if speed_t is not None else t0 + len(items) * step + 0.3
    sk = ease_out(prog(t, st, 0.4))
    if sk > 0:
        sp = rounded_rect_sprite(220, 270, (240, 240, 240), 14, 255)
        over_center(img, sp, W / 2, 860, sk)
        label(img, "SPEED", W / 2, 775, sk, 40, INK)
        label(img, "LIMIT", W / 2, 815, sk, 40, INK)
        label(img, "50", W / 2, 905, sk, 110, INK)
        label(img, "≈ 80 KM/H", W / 2 + 280, 860, sk, 50, YELLOW, anchor="l")
    return img


def park_road(t, dur, t0=0.3, buy_t=None):
    """Top view: the parkway with a strip of protected forest on each side; outside, the normal world."""
    img = np.full((H, W, 3), (70, 84, 60), np.uint8)
    rng = np.random.default_rng(2)
    # outside world: fields, houses, a highway with trucks
    for _ in range(40):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        if abs(y - H / 2) < 260:
            continue
        cv2.rectangle(img, (int(x), int(y)), (int(x + rng.uniform(80, 220)), int(y + rng.uniform(40, 120))), (96, 110, 70), -1)
    for _ in range(18):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        if abs(y - H / 2) < 280:
            continue
        cv2.rectangle(img, (int(x), int(y)), (int(x + 26), int(y + 20)), (170, 160, 150), -1)
    hy = 120
    cv2.rectangle(img, (0, hy - 20), (W, hy + 20), ASPHALT, -1)
    for j in range(8):
        x = (j * 260 + t * 420) % (W + 200) - 100
        cv2.rectangle(img, (int(x), hy - 14), (int(x + 70), hy - 2), (210, 210, 214), -1)
    label(img, "AUTOPISTA: CAMIONES, TIENDAS, GASOLINERAS", W / 2, hy + 60, ease_out(prog(t, t0 + 1.6, 0.4)), 40, WHITE)
    bk = ease_out(prog(t, buy_t if buy_t is not None else t0 + 0.6, 0.8))
    band = 230 * bk
    cv2.rectangle(img, (0, int(H / 2 - band)), (W, int(H / 2 + band)), (44, 70, 44), -1)
    for _ in range(int(240 * bk)):
        x, y = rng.uniform(0, W), H / 2 + rng.uniform(-band, band)
        cv2.circle(img, (int(x), int(y)), int(rng.uniform(8, 16)), (52, 86, 52), -1, cv2.LINE_AA)
    cv2.rectangle(img, (0, int(H / 2 - 22)), (W, int(H / 2 + 22)), ASPHALT, -1)
    for x in range(0, W, 80):
        cv2.line(img, (x, int(H / 2)), (x + 40, int(H / 2)), (230, 210, 120), 3)
    x = (t * 180) % (W + 100) - 50
    cv2.rectangle(img, (int(x), int(H / 2 + 4)), (int(x + 40), int(H / 2 + 18)), (220, 220, 224), -1)
    if bk > 0:
        label(img, "FRANJA DE BOSQUE PROTEGIDA", W / 2, H / 2 - band + 40, bk, 44, YELLOW)
        label(img, "FRANJA DE BOSQUE PROTEGIDA", W / 2, H / 2 + band - 40, bk, 44, YELLOW)
    label(img, "VISTA DESDE ARRIBA · ESQUEMA", W - 260, H - 46, 0.7, 30, (220, 220, 220))
    return img


# ---------------------------------------------------------------- 67 years, built piece by piece
SEGMENTS = [(0.40, 0.46, 1939), (0.62, 0.70, 1940), (0.12, 0.20, 1950), (0.80, 0.88, 1955), (0.47, 0.55, 1960),
            (0.27, 0.34, 1965), (0.71, 0.79, 1970), (0.56, 0.61, 1975), (0.88, 0.95, 1980), (0.02, 0.11, 1985),
            (0.35, 0.39, 1990), (0.95, 1.00, 1994), (0.21, 0.26, 2005), (0.00, 0.02, 2005)]


def pieces(t, dur, t0=0.3, y0=1938, y1=2005, mode="build", hold_war=True):
    img = background("dark_grid", t)
    x0, x1, y = 160, 1760, 560
    cv2.rectangle(img, (x0, y - 18), (x1, y + 18), (44, 46, 52), -1)
    k = ease_io(prog(t, t0, dur - t0 - 0.6))
    yr = lerp(y0, y1, k)
    for a, b, built in SEGMENTS:
        if built <= yr:
            col = YELLOW if built == 2005 else (200, 200, 206)
            cv2.rectangle(img, (int(lerp(x0, x1, a)), y - 18), (int(lerp(x0, x1, b)), y + 18), col, -1)
    label(img, "NATCHEZ", x0, y + 70, 0.9, 44, WHITE)
    label(img, "NASHVILLE", x1, y + 70, 0.9, 44, WHITE)
    label(img, "444 MILLAS", W / 2, y - 90, 0.8, 50, GREY)
    label(img, str(int(yr)), W / 2, 300, 1.0, 140, YELLOW)
    if 1941.5 < yr < 1946:
        label(img, "LA GUERRA SE LLEVA EL DINERO Y LOS HOMBRES", W / 2, 820, 1.0, 50, RED)
    if yr >= 2004.9:
        label(img, "21 DE MAYO DE 2005: COMPLETA", W / 2, 820, ease_out(prog(t, dur - 1.6, 0.4)), 56, YELLOW)
    _tag(img)
    return img


# ---------------------------------------------------------------- the Double Arch Bridge
def arch_bridge(t, dur, t0=0.3, build_d=None, dims_t=None, labels=True):
    img = _grad((70, 100, 130), (170, 186, 196))
    gy = 900
    vx0, vx1 = 160, 1760
    xs = np.linspace(0, W, 200)
    val = gy - 360 * np.clip(1 - ((xs - W / 2) / 760) ** 2, 0, 1) ** 0.6
    ground = np.where((xs < vx0) | (xs > vx1), 380, 380 + (gy - 380) * np.clip(1 - np.abs(xs - W / 2) / ((vx1 - vx0) / 2), 0, 1) ** 0.5)
    fill_poly(img, np.vstack([np.stack([xs, ground], 1), [[W, H], [0, H]]]), (70, 96, 62))
    for x in range(20, W, 60):
        gyx = float(np.interp(x, xs, ground))
        cv2.circle(img, (x, int(gyx + 16)), 26, (56, 84, 52), -1, cv2.LINE_AA)
    deck_y = 330
    k = ease_io(prog(t, t0, build_d if build_d is not None else dur * 0.7))
    arch_col = (210, 206, 196)
    # two arches meeting at a crown pier... drawn as two spans springing from the slopes and a central pier
    spans = [(vx0 + 40, W / 2 - 40), (W / 2 + 40, vx1 - 40)]
    for i, (a, b) in enumerate(spans):
        cx = (a + b) / 2
        half = (b - a) / 2
        th = np.linspace(-1, 1, 80)
        ax = cx + th * half
        ay = deck_y + 40 + 330 * th ** 2
        # cantilevered from both ends toward the middle
        m = np.abs(th) >= (1 - k)
        if m.sum() > 1:
            left = np.stack([ax[th <= 0][np.abs(th[th <= 0]) >= 1 - k], ay[th <= 0][np.abs(th[th <= 0]) >= 1 - k]], 1)
            right = np.stack([ax[th >= 0][np.abs(th[th >= 0]) >= 1 - k], ay[th >= 0][np.abs(th[th >= 0]) >= 1 - k]], 1)
            for part in (left, right):
                if len(part) > 1:
                    aa_poly(img, part, arch_col, 26)
            # temporary stay cables from the top while open
            if k < 1:
                for part, tip in ((left, left[-1] if len(left) else None), (right, right[0] if len(right) else None)):
                    if tip is not None:
                        top = (a if part is left else b, deck_y - 140)
                        cv2.line(img, (int(top[0]), int(top[1])), (int(tip[0]), int(tip[1])), (240, 200, 90), 2, cv2.LINE_AA)
                        cv2.line(img, (int(top[0]), int(top[1])), (int(top[0]), int(deck_y)), (240, 200, 90), 3, cv2.LINE_AA)
        # spandrel columns
        if k >= 1:
            for x in np.linspace(a + 40, b - 40, 9):
                ty = deck_y + 40 + 330 * ((x - cx) / half) ** 2
                cv2.line(img, (int(x), int(deck_y + 10)), (int(x), int(ty)), arch_col, 6, cv2.LINE_AA)
    pier_h = float(np.interp(W / 2, xs, ground))
    cv2.rectangle(img, (int(W / 2 - 22), int(deck_y + 10)), (int(W / 2 + 22), int(pier_h)), arch_col, -1)
    dk = min(1.0, k * 1.1)
    cv2.rectangle(img, (int(vx0 - 60), deck_y - 10), (int(lerp(vx0 - 60, vx1 + 60, dk if k >= 1 else 0.0) if k >= 1 else vx0 - 60), deck_y + 12),
                  arch_col, -1)
    if labels:
        if k < 1:
            label(img, "PIEZAS COLGADAS DESDE ARRIBA, CON CABLES PROVISIONALES", W / 2, 150, ease_out(prog(t, t0, 0.4)), 46, WHITE)
            label(img, "SIN TORRES NI ANDAMIOS DESDE EL FONDO", W / 2, 210, ease_out(prog(t, t0 + 0.8, 0.4)), 46, YELLOW)
        dt = dims_t if dims_t is not None else t0 + (build_d or dur * 0.7) + 0.3
        da = ease_out(prog(t, dt, 0.5))
        if da > 0:
            x = W / 2 + 60
            cv2.arrowedLine(img, (int(x), deck_y + 14), (int(x), int(pier_h - 6)), YELLOW, 3, cv2.LINE_AA, tipLength=0.05)
            label(img, "145 PIES · 44 M", x + 20, (deck_y + pier_h) / 2, da, 48, YELLOW, anchor="l")
            a, b = spans[0]
            cv2.line(img, (int(a), int(deck_y + 400)), (int(b), int(deck_y + 400)), WHITE, 3, cv2.LINE_AA)
            label(img, "ARCO: 582 PIES · 177 M", (a + b) / 2, deck_y + 450, ease_out(prog(t, dt + 0.6, 0.4)), 46, WHITE)
    _tag(img)
    return img


# ---------------------------------------------------------------- clay soil: swells with rain, shrinks with heat
def clay(t, dur, t0=0.3, cycles=2.0):
    img = background("dark_grid", t)
    x0, x1 = 260, 1660
    ph = math.sin(max(0, t - t0) / max(dur - t0, 0.1) * cycles * 2 * math.pi)
    swell = 30 * ph
    top = 520
    xs = np.linspace(x0, x1, 120)
    surf = top - swell * np.sin(np.pi * (xs - x0) / (x1 - x0)) ** 0.8
    fill_poly(img, np.vstack([np.stack([xs, surf + 60], 1), [[x1, 900], [x0, 900]]]), (150, 104, 70))
    fill_poly(img, np.vstack([np.stack([xs, surf], 1), np.stack([xs[::-1], surf[::-1] + 60], 1)]), ASPHALT)
    n = int(max(0, t - t0) / max(dur - t0, 0.1) * 14)
    rng = np.random.default_rng(1)
    for i in range(n):
        x = rng.uniform(x0 + 60, x1 - 60)
        y = float(np.interp(x, xs, surf))
        pts = np.array([[x, y], [x + rng.uniform(-14, 14), y + 20], [x + rng.uniform(-14, 14), y + 40], [x + rng.uniform(-10, 10), y + 58]])
        aa_poly(img, pts, (20, 20, 22), 3)
    if ph > 0.2:
        for j in range(16):
            x = x0 + (j * 97 + t * 50) % (x1 - x0)
            y = 200 + (t * 400 + j * 53) % 260
            cv2.line(img, (int(x), int(y)), (int(x - 6), int(y + 26)), (150, 190, 230), 2, cv2.LINE_AA)
        label(img, "LLUVIA: LA ARCILLA SE HINCHA", W / 2, 160, 1.0, 60, (150, 190, 230))
    elif ph < -0.2:
        cv2.circle(img, (W - 260, 220), 70, (60, 200, 250), -1, cv2.LINE_AA)
        label(img, "CALOR: SE ENCOGE", W / 2, 160, 1.0, 60, (60, 200, 250))
    label(img, "ARCILLA", W / 2, 800, 0.9, 54, WHITE)
    label(img, "ASFALTO", x1 + 40, top + 30, 0.9, 40, GREY, anchor="l")
    _tag(img)
    return img


# ---------------------------------------------------------------- two timelines
def two_decades(t, dur, t0=0.3, t1=None, t2=None):
    img = background("dark_grid", t)
    x0, x1 = 160, 1760

    def X(yr):
        return x0 + (x1 - x0) * (yr - 1935) / (2030 - 1935)

    y = 520
    cv2.line(img, (x0, y), (x1, y), (90, 92, 96), 3)
    k = ease_io(prog(t, t0, 1.6))
    cv2.rectangle(img, (int(X(1938)), y - 30), (int(lerp(X(1938), X(2005), k)), y + 30), (150, 150, 156), -1)
    label(img, "67 AÑOS DE OBRA", (X(1938) + X(2005)) / 2, y - 80, ease_out(prog(t, t0 + 0.8, 0.4)), 56, WHITE)
    t1 = t1 if t1 is not None else t0 + 2.0
    k2 = ease_io(prog(t, t1, 0.8))
    if k2 > 0:
        cv2.rectangle(img, (int(X(2005)), y - 30), (int(lerp(X(2005), X(2026), k2)), y + 30), YELLOW, -1)
        label(img, "COMPLETA: 21 AÑOS", (X(2005) + X(2026)) / 2, y + 90, ease_out(prog(t, t1 + 0.4, 0.4)), 50, YELLOW)
    t2 = t2 if t2 is not None else t1 + 1.6
    k3 = ease_out(prog(t, t2, 0.4))
    if k3 > 0:
        cv2.line(img, (int(X(2026)), y - 80), (int(X(2026)), y + 80), RED, 6, cv2.LINE_AA)
        label(img, "2026: PARTIDA OTRA VEZ", X(2026) - 20, y - 150, k3, 50, RED, anchor="r")
    for yr in (1938, 2005, 2026):
        label(img, str(yr), X(yr), y + 160 if yr != 2026 else y + 160, 0.9, 44, GREY)
    return img


def nobody_fast(t, dur, times=None, t0=0.3, step=1.0):
    img = background("dark_grid", t)
    items = [("LOS KAINTUCKS", "2 A 3 SEMANAS A PIE"), ("EL CORREO", "10 DÍAS"), ("JACKSON", "A PIE, JUNTO A SUS ENFERMOS"),
             ("BUSBY", "MURIÓ ESPERANDO"), ("TÚ", "50 MILLAS POR HORA")]
    for i, (a_, b_) in enumerate(items):
        a = ease_out(prog(t, times[i] if times else t0 + i * step, 0.4))
        y = 230 + i * 150
        label(img, a_, 640, y, a, 70, YELLOW if i == 4 else WHITE, anchor="r")
        label(img, b_, 700, y, a, 50, GREY, anchor="l")
    label(img, "NADIE LLEGÓ NUNCA RÁPIDO", W / 2, 100, ease_out(prog(t, 0.1, 0.4)), 60, WHITE)
    return img
