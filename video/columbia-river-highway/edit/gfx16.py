"""Columbia River Highway (1913-2025): diagrams drawn in code for this episode."""
import math

import cv2
import numpy as np

from engine import H, W, WHITE, YELLOW, clamp, ease_back, ease_in, ease_io, ease_out, lerp, prog
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

ROCK = (64, 60, 58)
ROCK_HI = (92, 86, 80)
ROCK_DK = (40, 38, 38)
WATER = (40, 82, 120)
WATER_HI = (90, 140, 190)
CONC = (170, 168, 160)
CEDAR = (170, 112, 64)
CEDAR_DK = (120, 76, 42)
RED_ = (230, 70, 60)
GREEN = (90, 210, 120)
BLUE = (110, 170, 220)
GOLD = (236, 190, 70)
SNOW = (236, 238, 244)


def _tag(img, txt="ESQUEMA", a=0.7):
    label(img, txt, W - 40, H - 46, a, 30, GREY, anchor="r")


def _rng_rocks(n, seed, x0, x1, y0, y1, r0=10, r1=26):
    rng = np.random.default_rng(seed)
    return [(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(r0, r1), rng.uniform(0, 6.28), int(rng.integers(5, 8))) for _ in range(n)]


def _rock(img, x, y, r, a0, k, col=ROCK_HI):
    pts = np.array([[x + r * (0.75 + 0.25 * math.sin(i * 2.3 + a0)) * math.cos(a0 + i * 6.283 / k),
                     y + r * (0.75 + 0.25 * math.cos(i * 1.7 + a0)) * math.sin(a0 + i * 6.283 / k)] for i in range(k)], np.float64)
    fill_poly(img, pts, col)
    aa_poly(img, pts, ROCK_DK, 2, closed=True)


def _car(img, x, y, s=1.0, col=(46, 46, 52), truck=False, mirror=False):
    """1915-style car (or a 1930 truck) seen from the side, wheels on y."""
    if truck:
        cv2.rectangle(img, (int(x - 120 * s), int(y - 120 * s)), (int(x + 50 * s), int(y - 22 * s)), (120, 96, 70), -1)
        cv2.rectangle(img, (int(x + 50 * s), int(y - 90 * s)), (int(x + 110 * s), int(y - 22 * s)), col, -1)
        cv2.rectangle(img, (int(x + 62 * s), int(y - 80 * s)), (int(x + 96 * s), int(y - 56 * s)), (150, 170, 190), -1)
        for wx in (-90, -40, 80):
            cv2.circle(img, (int(x + wx * s), int(y - 12 * s)), int(16 * s), (24, 24, 24), -1, cv2.LINE_AA)
            cv2.circle(img, (int(x + wx * s), int(y - 12 * s)), int(6 * s), (150, 150, 150), -1, cv2.LINE_AA)
        if mirror:
            cv2.line(img, (int(x + 104 * s), int(y - 84 * s)), (int(x + 124 * s), int(y - 100 * s)), (200, 200, 200), max(2, int(3 * s)), cv2.LINE_AA)
        return
    body = np.array([[-70, -18], [70, -18], [70, -40], [36, -44], [20, -70], [-34, -70], [-44, -44], [-70, -40]], np.float64) * s + [x, y]
    fill_poly(img, body, col)
    cv2.rectangle(img, (int(x - 26 * s), int(y - 64 * s)), (int(x + 14 * s), int(y - 46 * s)), (150, 170, 190), -1)
    for wx in (-44, 44):
        cv2.circle(img, (int(x + wx * s), int(y - 14 * s)), int(15 * s), (20, 20, 20), -1, cv2.LINE_AA)
        cv2.circle(img, (int(x + wx * s), int(y - 14 * s)), int(6 * s), (160, 160, 160), -1, cv2.LINE_AA)


# ---------------------------------------------------------------- the gorge in cross-section: rail at the water, cliffs above
def hang(t, dur, t0=0.3, road_t=None, i84_t=None, cut_t=None, title="LA GARGANTA DEL COLUMBIA, EN CORTE"):
    img = background("dark_grid", t)
    yw = 860
    # cliff profile (river on the left, plateau on the right)
    prof = np.array([[520, yw], [560, 820], [640, 790], [700, 640], [760, 560], [800, 420], [880, 330], [1040, 300], [1240, 250],
                     [1500, 220], [1920, 200], [1920, 1080], [520, 1080]], np.float64)
    fill_poly(img, prof, ROCK)
    for k in range(6):  # basalt flows (horizontal banding)
        y = 330 + k * 90
        aa_poly(img, np.array([[700 + k * 10, y], [1920, y - 20]], np.float64), ROCK_DK, 3)
    fill_poly(img, np.array([[0, yw], [560, yw], [520, 1080], [0, 1080]], np.float64), WATER)
    aa_poly(img, np.array([[0, yw], [556, yw]], np.float64), WATER_HI, 3)
    label(img, "RÍO COLUMBIA", 260, 960, ease_out(prog(t, t0, 0.4)), 50, BLUE)
    # railroad on the shore bench
    ka = ease_out(prog(t, t0 + 0.5, 0.5))
    if ka > 0:
        cv2.line(img, (560, 820), (640, 790), (30, 30, 30), 10)
        cv2.rectangle(img, (575, 770), (635, 806), (46, 46, 56), -1)
        label(img, "FERROCARRIL", 600, 740, ka, 40, WHITE, box=(20, 20, 20))
    label(img, title, W / 2, 110, ease_out(prog(t, 0.05, 0.4)), 58, WHITE)
    if road_t is None:
        kq = ease_back(prog(t, t0 + 1.4, 0.4))
        label(img, "¿Y LA CARRETERA?", 1000, 520, kq, 72, YELLOW, box=(20, 20, 20))
    else:
        kr = ease_out(prog(t, road_t, 0.7))
        if kr > 0:  # shelf blasted into the cliff, with a stone wall on the void side
            y = 560
            fill_poly(img, np.array([[760, y], [760 + 90 * kr, y], [760 + 90 * kr, y - 70], [770, y - 70]], np.float64), (24, 24, 26))
            cv2.rectangle(img, (742, y - 18), (762, y + 40), (150, 140, 120), -1)
            cv2.line(img, (760, y), (int(760 + 90 * kr), y), GOLD, 8)
            if kr > 0.6:
                _car(img, 805, y, 0.42, (40, 40, 44))
            label(img, "LA CARRETERA, COLGADA DE LA ROCA", 1280, 470, kr, 54, GOLD, box=(20, 20, 20))
            label(img, "CIENTOS DE PIES SOBRE EL AGUA", 1280, 540, ease_out(prog(t, road_t + 0.6, 0.4)), 42, WHITE)
    if i84_t is not None:
        ki = ease_out(prog(t, i84_t, 0.7))
        if ki > 0:  # low road on fill at the water's edge
            fill_poly(img, np.array([[430, yw], [560, yw], [560, 820], [470, 820]], np.float64), (110, 104, 92))
            cv2.line(img, (470, 820), (int(470 + 90 * ki), 820), (200, 200, 200), 8)
            label(img, "LA NUEVA: A RAS DEL AGUA", 330, 700, ki, 46, WHITE, box=(20, 20, 20))
    if cut_t is not None:
        kc = ease_out(prog(t, cut_t, 0.6))
        if kc > 0:
            fill_poly(img, np.array([[560, 820], [560 + 130 * kc, 820], [700 + 40 * kc, 640], [700, 640], [640, 790]], np.float64), (110, 104, 92))
            aa_poly(img, np.array([[560 + 130 * kc, 820], [700 + 40 * kc, 640]], np.float64), RED_, 6)
            label(img, "1966: RECORTAN EL PIE DEL ACANTILADO", 1180, 760, kc, 50, RED_, box=(20, 20, 20))
            label(img, "PARA 4 CARRILES", 1180, 830, ease_out(prog(t, cut_t + 0.5, 0.4)), 44, WHITE)
    _tag(img, "ESQUEMA · SIN ESCALA")
    return img


# ---------------------------------------------------------------- a tunnel with windows, seen from the river
def windows(t, dur, t0=0.3, n=5, length="≈ 390 PIES · 120 M", sub="5 VENTANAS · ~20 PIES DE ALTO", title="MITCHELL POINT · 1915",
            car_t=None, new=False, flash=True):
    img = background("dark_grid", t)
    fill_poly(img, np.array([[0, 260], [300, 200], [700, 150], [1200, 170], [1600, 140], [1920, 200], [1920, 900], [0, 900]], np.float64), ROCK)
    for k in range(5):
        aa_poly(img, np.array([[0, 330 + k * 120], [1920, 300 + k * 125]], np.float64), ROCK_DK, 3)
    fill_poly(img, np.array([[0, 900], [1920, 900], [1920, 1080], [0, 1080]], np.float64), WATER)
    aa_poly(img, np.array([[0, 900], [1920, 900]], np.float64), WATER_HI, 3)
    x0, x1, yb, hgt = 260, 1660, 640, 140
    k = ease_io(prog(t, t0, 0.9))
    xe = lerp(x0, x1, k)
    # tunnel bore (dashed, inside the rock)
    for xx in range(x0, int(xe), 40):
        cv2.line(img, (xx, yb), (min(xx + 22, int(xe)), yb), (20, 20, 20), 4)
        cv2.line(img, (xx, yb - hgt), (min(xx + 22, int(xe)), yb - hgt), (20, 20, 20), 4)
    # portals
    for px in (x0, x1):
        if px <= xe + 1:
            cv2.ellipse(img, (px, yb), (54, hgt), 0, 180, 360, (14, 14, 16), -1, cv2.LINE_AA)
            cv2.rectangle(img, (px - 54, yb - 2), (px + 54, yb + 8), (14, 14, 16), -1)
    ccar = None
    if car_t is not None:
        ccar = lerp(x0 - 120, x1 + 120, clamp((t - car_t) / 4.5))
    ws = [lerp(x0 + 180, x1 - 180, (i + 0.5) / n) if n > 1 else (x0 + x1) / 2 for i in range(n)]
    ww = (x1 - x0 - 360) / n * 0.62
    for i, wx in enumerate(ws):
        a = ease_back(prog(t, t0 + 0.9 + i * 0.18, 0.35))
        if a <= 0:
            continue
        top, bot = yb - hgt * 0.95, yb - 18
        pts = np.array([[wx - ww / 2 * a, bot], [wx - ww / 2 * a, top + 30], [wx, top], [wx + ww / 2 * a, top + 30], [wx + ww / 2 * a, bot]], np.float64)
        lit = 0.0
        if flash and ccar is not None:
            lit = clamp(1 - abs(ccar - wx) / 160)
        col = tuple(int(lerp(c0, c1, lit)) for c0, c1 in zip((20, 26, 34), (150, 200, 235)))
        fill_poly(img, pts, col)
        aa_poly(img, pts, (210, 200, 180) if new else (190, 176, 150), 3, closed=True)
    if ccar is not None and x0 - 120 < ccar < x1 + 120:
        _car(img, ccar, yb, 0.75, (30, 30, 34) if not new else (180, 40, 40))
    # ledge outside, along the windows
    kl = ease_out(prog(t, t0 + 1.8, 0.5))
    if kl > 0:
        aa_poly(img, np.array([[x0, yb + 14], [x0 + (x1 - x0) * kl, yb + 14]], np.float64), (150, 140, 120), 6)
        label(img, length, (x0 + x1) / 2, yb + 80, kl, 54, YELLOW, box=(20, 20, 20))
        label(img, sub, (x0 + x1) / 2, yb + 150, ease_out(prog(t, t0 + 2.2, 0.4)), 44, WHITE)
    label(img, title, W / 2, 90, ease_out(prog(t, 0.05, 0.4)), 60, WHITE)
    _tag(img, "ESQUEMA · VISTO DESDE EL RÍO · SIN ESCALA")
    return img


# ---------------------------------------------------------------- Lancaster's rule: 5 feet per 100, no tight curves
def rule5(t, dur, t0=0.3, curve_t=None):
    img = background("dark_grid", t)
    x0, y0, run = 260, 820, 900
    rise = run * 0.05 * 4.0
    k = ease_out(prog(t, t0, 0.8))
    tri = np.array([[x0, y0], [x0 + run * k, y0], [x0 + run * k, y0 - rise * k]], np.float64)
    fill_poly(img, tri, (52, 58, 62))
    aa_poly(img, np.array([[x0, y0], [x0 + run * k, y0 - rise * k]], np.float64), GOLD, 8)
    a = ease_out(prog(t, t0 + 0.8, 0.4))
    label(img, "100 PIES", x0 + run / 2, y0 + 50, a, 50, WHITE)
    label(img, "5", x0 + run + 50, y0 - rise / 2, a, 70, YELLOW)
    c = clamp((t - t0 - 1.0) / 3.0)
    if c > 0:
        cx = x0 + run * ease_io(c)
        _car(img, cx, y0 - rise * ease_io(c) - 4, 0.6)
    label(img, "NINGUNA CUESTA DE MÁS DE 5 PIES POR CADA 100", W / 2, 140, ease_out(prog(t, 0.1, 0.4)), 58, YELLOW, box=(20, 20, 20))
    ct = curve_t if curve_t is not None else t0 + 2.2
    kc = ease_out(prog(t, ct, 0.7))
    if kc > 0:  # a wide curve vs. a tight one
        cxy = (1500, 560)
        cv2.ellipse(img, cxy, (230, 230), 0, 180, 180 + 180 * kc, GOLD, 10, cv2.LINE_AA)
        cv2.ellipse(img, (1500, 560), (60, 60), 0, 180, 180 + 180 * kc, (110, 110, 110), 8, cv2.LINE_AA)
        if kc > 0.9:
            cv2.line(img, (1440, 520), (1560, 600), RED_, 10, cv2.LINE_AA)
            cv2.line(img, (1560, 520), (1440, 600), RED_, 10, cv2.LINE_AA)
        label(img, "CURVAS AMPLIAS", 1500, 860, kc, 54, GOLD)
    _tag(img, "ESQUEMA · PENDIENTE EXAGERADA ×4")
    return img


# ---------------------------------------------------------------- the old road over Mitchell Point: one car at a time
def flagmen(t, dur, t0=0.3, horses_t=None):
    img = background("dark_grid", t)
    pts = np.array([[100, 860], [500, 840], [760, 520], [960, 430], [1160, 520], [1420, 840], [1820, 860], [1820, 1080], [100, 1080]], np.float64)
    fill_poly(img, pts, ROCK)
    road = pts[:7]
    k = ease_io(prog(t, t0, 0.8))
    part = partial_line(road, k)
    if len(part) > 1:
        aa_poly(img, part, (150, 120, 80), 12)
    for i, (x, y) in enumerate(((560, 820), (960, 410), (1360, 820))):
        a = ease_back(prog(t, t0 + 0.9 + i * 0.3, 0.4))
        if a <= 0:
            continue
        cv2.line(img, (x, y), (x, int(y - 110 * a)), (220, 220, 220), 5)
        fill_poly(img, np.array([[x, y - 110 * a], [x + 56 * a, y - 92 * a], [x, y - 74 * a]], np.float64), RED_ if i != 1 else YELLOW)
        cv2.circle(img, (x - 18, int(y - 40)), 14, (200, 170, 140), -1, cv2.LINE_AA)
    label(img, "3 HOMBRES CON BANDERAS", W / 2, 150, ease_out(prog(t, t0 + 1.0, 0.4)), 60, YELLOW, box=(20, 20, 20))
    label(img, "SOLO CABÍA UN AUTO: PASABAN POR TURNOS", W / 2, 230, ease_out(prog(t, t0 + 1.6, 0.4)), 46, WHITE)
    c = clamp((t - t0 - 1.6) / 3.5)
    if c > 0 and horses_t is None:
        x = lerp(500, 880, ease_io(c))
        y = float(np.interp(x, road[:, 0], road[:, 1]))
        _car(img, x, y, 0.55)
    if horses_t is not None:
        kh = ease_out(prog(t, horses_t, 0.5))
        x = lerp(820, 640, ease_io(clamp((t - horses_t) / 3.0)))
        y = float(np.interp(x, road[:, 0], road[:, 1]))
        _car(img, x, y, 0.55)
        if kh > 0:
            label(img, "LO BAJARON CON UN TIRO DE CABALLOS", W / 2, 960, kh, 54, GOLD, box=(20, 20, 20))
    _tag(img, "ESQUEMA · SIN ESCALA")
    return img


# ---------------------------------------------------------------- 1915 car vs 1930 truck in the same portal
def squeeze(t, dur, t0=0.3, truck_t=None):
    img = background("dark_grid", t)
    cx, yb, rw, rh = 960, 860, 300, 420
    fill_poly(img, np.array([[200, 200], [1720, 200], [1720, 1000], [200, 1000]], np.float64), ROCK)
    cv2.ellipse(img, (cx, yb - rh + rw), (rw, rw), 0, 180, 360, (16, 16, 18), -1, cv2.LINE_AA)
    cv2.rectangle(img, (cx - rw, yb - rh + rw), (cx + rw, yb), (16, 16, 18), -1)
    cv2.line(img, (200, yb), (1720, yb), (120, 110, 96), 6)
    tt = truck_t if truck_t is not None else t0 + 2.0
    if t < tt:
        a = ease_out(prog(t, t0, 0.5))
        # front view of a small car: box + wheels
        cv2.rectangle(img, (cx - 110, yb - 190), (cx + 110, yb - 40), (60, 60, 66), -1)
        cv2.rectangle(img, (cx - 80, yb - 180), (cx + 80, yb - 120), (150, 170, 190), -1)
        for wx in (-90, 90):
            cv2.rectangle(img, (cx + wx - 18, yb - 50), (cx + wx + 18, yb), (20, 20, 20), -1)
        label(img, "1915: SOBRA SITIO", W / 2, 130, a, 64, GREEN, box=(20, 20, 20))
    else:
        a = ease_out(prog(t, tt, 0.4))
        w2, h2 = 300, 360
        cv2.rectangle(img, (cx - w2, yb - h2), (cx + w2, yb - 40), (120, 96, 70), -1)
        cv2.rectangle(img, (cx - 160, yb - h2 + 50), (cx + 160, yb - h2 + 150), (150, 170, 190), -1)
        for s_ in (-1, 1):
            mx = cx + s_ * (w2 + 26)
            cv2.line(img, (cx + s_ * w2, yb - 260), (mx, yb - 290), (210, 210, 210), 6)
            if int(t * 12) % 2:
                for j in range(5):
                    ang = j * 0.6 + t * 9
                    cv2.line(img, (mx, yb - 290), (int(mx + s_ * 30 * math.cos(ang)), int(yb - 290 + 30 * math.sin(ang))), GOLD, 3, cv2.LINE_AA)
        for wx in (-240, 240):
            cv2.rectangle(img, (cx + wx - 24, yb - 50), (cx + wx + 24, yb), (20, 20, 20), -1)
        label(img, "1930: LOS ESPEJOS ROZAN LA ROCA", W / 2, 130, a, 64, RED_, box=(20, 20, 20))
    _tag(img, "ESQUEMA · SIN ESCALA")
    return img


# ---------------------------------------------------------------- the twin tunnels in section: filled, dug out, rebuilt
_FILL = _rng_rocks(260, 7, 330, 1590, 470, 690, 12, 30)


def fill(t, dur, t0=0.3, mode="fill", reveal_t=None, title=None):
    img = background("dark_grid", t)
    fill_poly(img, np.array([[0, 160], [1920, 130], [1920, 1080], [0, 1080]], np.float64), ROCK)
    for k in range(6):
        aa_poly(img, np.array([[0, 230 + k * 140], [1920, 210 + k * 140]], np.float64), ROCK_DK, 3)
    x0, x1, yt, yb = 300, 1620, 460, 700
    fill_poly(img, np.array([[x0, yb], [x0, yt + 40], [x0 + 40, yt], [x1 - 40, yt], [x1, yt + 40], [x1, yb]], np.float64), (18, 18, 20))
    cv2.rectangle(img, (930, yt - 10), (990, yb + 10), ROCK, -1)          # rock between the two tunnels
    for wx in (620, 1300):  # windows to the river (seen as notches in the section)
        cv2.rectangle(img, (wx - 40, yt + 30), (wx + 40, yt + 120), (60, 80, 100), -1)
    insc = (1150, 600)

    def inscription(a, glow=0.0):
        if a <= 0:
            return
        if glow > 0:
            ov = img.copy()
            cv2.circle(ov, insc, 120, (255, 220, 120), -1, cv2.LINE_AA)
            cv2.addWeighted(ov, 0.25 * glow, img, 1 - 0.25 * glow, 0, img)
        for j, w_ in enumerate((120, 90, 70)):
            cv2.line(img, (insc[0] - w_ // 2, insc[1] - 30 + j * 26), (insc[0] + w_ // 2, insc[1] - 30 + j * 26), (210, 200, 180), 4, cv2.LINE_AA)
        label(img, "LAS FIRMAS", insc[0], insc[1] + 70, a, 38, YELLOW, box=(20, 20, 20))
    if mode == "fill":
        kf = clamp((t - t0) / max(dur - t0 - 1.2, 1.0))
        inscription(1.0 if kf < 0.6 else 1 - prog(kf, 0.6, 0.3))
        nshow = int(len(_FILL) * ease_in(kf))
        for (x, y, r, a0, kk) in _FILL[:nshow]:
            _rock(img, x, y, r, a0, kk)
        label(img, title or "1954-55: RELLENOS DE ROCA, DE PUNTA A PUNTA", W / 2, 100, ease_out(prog(t, 0.1, 0.4)), 56, WHITE, box=(20, 20, 20))
    elif mode == "dig":
        kd = clamp((t - t0) / max((reveal_t or dur - 1.0) - t0, 1.0))
        xcut = lerp(x0, insc[0] + 40, ease_io(kd))
        for (x, y, r, a0, kk) in _FILL:
            if x > xcut:
                _rock(img, x, y, r, a0, kk)
        for px in range(x0 + 80, int(xcut), 120):  # props holding the roof
            cv2.line(img, (px, yt + 4), (px, yb - 4), CEDAR, 10)
            cv2.line(img, (px - 30, yt + 6), (px + 30, yt + 6), CEDAR_DK, 8)
        if xcut > x0 + 20:
            cv2.circle(img, (int(xcut - 50), yb - 70), 16, (240, 200, 60), -1, cv2.LINE_AA)  # a helmet lamp
            cv2.circle(img, (int(xcut - 50), yb - 70), 40, (240, 200, 60), 2, cv2.LINE_AA)
        if reveal_t is not None and t >= reveal_t:
            inscription(ease_out(prog(t, reveal_t, 0.4)), glow=0.5 + 0.5 * math.sin((t - reveal_t) * 5))
        label(img, title or "1994: SACANDO LA ROCA, POCO A POCO", W / 2, 100, ease_out(prog(t, 0.1, 0.4)), 56, WHITE, box=(20, 20, 20))
        label(img, "PUNTALES A CADA PASO", 600, 820, ease_out(prog(t, t0 + 1.0, 0.4)), 46, CEDAR)
    else:  # rebuilt
        inscription(1.0)
        kb = ease_out(prog(t, t0, 0.6))
        for bx in range(x0 + 40, x1, 70):
            if bx < x0 + (x1 - x0) * kb and not 920 < bx < 1000:
                cv2.line(img, (bx, yt), (bx, yt - 70), (200, 200, 200), 3)
        if kb > 0:
            label(img, "PERNOS Y CONCRETO", 640, 380, kb, 46, WHITE, box=(20, 20, 20))
        kc = ease_out(prog(t, t0 + 1.0, 0.6))
        if kc > 0:
            for x in range(x0 + 10, int(x0 + (x1 - x0) * kc), 36):
                if not 920 < x < 1000:
                    cv2.line(img, (x, yt + 12), (x, yb - 4), CEDAR if (x // 36) % 2 else CEDAR_DK, 14)
            label(img, "CEDRO DE OTRO TÚNEL VIEJO", 640, 800, kc, 46, CEDAR, box=(20, 20, 20))
        label(img, title or "2000: REABIERTOS A PIE Y EN BICI", W / 2, 100, ease_out(prog(t, 0.1, 0.4)), 56, WHITE, box=(20, 20, 20))
    _tag(img, "ESQUEMA · CORTE SIN ESCALA")
    return img


# ---------------------------------------------------------------- the inscription (recreation, translated)
def carving(t, dur, t0=0.3, names_t=None):
    img = background("dark_grid", t)
    rng = np.random.default_rng(3)
    stone = np.full((H, W, 3), 0, np.uint8)
    base = np.array([96, 90, 84], np.float32)
    noise = rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32)
    noise = cv2.resize(cv2.GaussianBlur(noise, (0, 0), 1.2), (W, H))
    stone[:] = np.clip(base + noise[..., None] * 14, 0, 255).astype(np.uint8)
    k = ease_out(prog(t, 0.0, 0.6))
    cv2.addWeighted(stone, k, img, 1 - k, 0, img)
    lines = [("ATRAPADOS POR LA NIEVE", 0.0), ("DEL 19 AL 27 DE NOVIEMBRE DE 1921", 0.9)]
    nt = names_t if names_t is not None else t0 + 2.2
    for i, (tx, dt) in enumerate(lines):
        a = ease_out(prog(t, t0 + dt, 0.7))
        label(img, tx, W / 2 + 3, 330 + i * 130 + 3, a, 84, (40, 38, 36), fname="type")
        label(img, tx, W / 2, 330 + i * 130, a, 84, (200, 192, 176), fname="type")
    a = ease_out(prog(t, nt, 0.7))
    for j, tx in enumerate(("C. SADILEK", "E. B. MARVIN")):
        label(img, tx, W / 2 + 3, 650 + j * 110 + 3, a, 90, (40, 38, 36), fname="type")
        label(img, tx, W / 2, 650 + j * 110, a, 90, (226, 210, 170), fname="type")
    _tag(img, "RECREACIÓN · TEXTO TRADUCIDO, NO ES LA INSCRIPCIÓN REAL")
    return img


# ---------------------------------------------------------------- nine days, 19 to 27 November 1921
def days(t, dur, t0=0.3, step=0.42):
    img = background("dark_grid", t)
    label(img, "NOVIEMBRE DE 1921", W / 2, 170, ease_out(prog(t, 0.05, 0.4)), 64, WHITE)
    for i in range(9):
        d = 19 + i
        a = ease_back(prog(t, t0 + i * step, 0.3))
        if a <= 0:
            continue
        x = 250 + i * 178
        y = 520
        cv2.rectangle(img, (x - 74, y - 110), (x + 74, y + 110), (230, 230, 232), -1)
        cv2.rectangle(img, (x - 74, y - 110), (x + 74, y - 60), (190, 50, 44), -1)
        label(img, str(d), x, y + 20, a, 110, (30, 30, 34))
        cv2.line(img, (x - 56, y - 34), (x + 56, y + 90), (190, 50, 44), 8, cv2.LINE_AA)
    kk = ease_out(prog(t, t0 + 9 * step + 0.2, 0.5))
    label(img, "NUEVE DÍAS DENTRO DEL TÚNEL", W / 2, 820, kk, 72, YELLOW, box=(20, 20, 20))
    return img


# ---------------------------------------------------------------- the east wind funnelling through the gorge
def funnel(t, dur, t0=0.3):
    img = background("dark_grid", t)
    top = np.array([[0, 340], [500, 360], [800, 470], [1120, 470], [1420, 360], [1920, 300]], np.float64)
    bot = np.array([[0, 760], [500, 740], [800, 610], [1120, 610], [1420, 740], [1920, 800]], np.float64)
    fill_poly(img, np.vstack([[[0, 0], [1920, 0]], top[::-1]]), ROCK)
    fill_poly(img, np.vstack([bot, [[1920, 1080], [0, 1080]]]), ROCK)
    label(img, "OESTE · COSTA", 240, 250, ease_out(prog(t, t0, 0.4)), 46, GREY)
    label(img, "ESTE · INTERIOR HELADO", 1640, 210, ease_out(prog(t, t0, 0.4)), 46, BLUE)
    for j in range(7):
        yy = 420 + j * 40
        for s in range(6):
            ph = ((t - t0) * 0.35 + s / 6 + j * 0.07) % 1.0
            x = 1880 - ph * 1840
            sp = 1.0 + 1.8 * math.exp(-((x - 960) / 260) ** 2)
            ln = 50 * sp
            y = yy + (bot[2, 1] + top[2, 1]) / 2 - 540 if 700 < x < 1220 else yy
            y = lerp(yy, 540 + (yy - 540) * 0.35, math.exp(-((x - 960) / 300) ** 2))
            a = clamp((t - t0) / 0.6)
            if a > 0:
                cv2.arrowedLine(img, (int(x + ln), int(y)), (int(x), int(y)), (int(lerp(150, 220, sp / 2.8)), int(lerp(190, 235, sp / 2.8)), 255),
                                3, cv2.LINE_AA, tipLength=0.35)
    label(img, "EL VIENTO DEL ESTE ENTRA COMO POR UN EMBUDO", W / 2, 960, ease_out(prog(t, t0 + 1.2, 0.4)), 54, YELLOW, box=(20, 20, 20))
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- the rockfall shelter: 5,000 lb from 200 ft
def shelter(t, dur, t0=0.3, drop_t=None):
    img = background("dark_grid", t)
    fill_poly(img, np.array([[1180, 80], [1920, 80], [1920, 1080], [1260, 1080], [1260, 640], [1200, 600]], np.float64), ROCK)
    fill_poly(img, np.array([[0, 900], [1920, 900], [1920, 1080], [0, 1080]], np.float64), (60, 58, 54))
    k = ease_out(prog(t, t0, 0.6))
    if k > 0:  # concrete canopy on columns
        x0, x1 = 500, 1260
        cv2.rectangle(img, (int(x0 + (x1 - x0) * (1 - k)), 600), (x1, 650), CONC, -1)
        for cx in range(540, 1260, 120):
            if cx > x0 + (x1 - x0) * (1 - k):
                cv2.rectangle(img, (cx - 12, 650), (cx + 12, 900), (150, 148, 140), -1)
        label(img, "TEJADO DE CONCRETO", 860, 560, k, 46, WHITE, box=(20, 20, 20))
    dt = drop_t if drop_t is not None else t0 + 1.2
    d = clamp((t - dt) / 1.0)
    if t >= dt:
        y = lerp(120, 560, d * d) if d < 1 else 560 - 160 * math.sin(min((t - dt - 1.0) * 3, math.pi))
        x = 1120 if d < 1 else 1120 - (t - dt - 1.0) * 260
        _rock(img, x, y, 46, 1.2, 7, (120, 110, 100))
        cv2.line(img, (1340, 120), (1340, 560), (200, 200, 200), 2)
        label(img, "200 PIES · 61 M", 1480, 340, 1.0, 44, WHITE, anchor="l")
        label(img, "5.000 LIBRAS", 1080, 60 + 0 * d, 1.0, 60, YELLOW)
        label(img, "MÁS DE 2 TONELADAS", 1080, 120, ease_out(prog(t, dt + 0.3, 0.4)), 40, WHITE)
    _car(img, 860, 900, 0.0001)
    for i, x in enumerate((700, 820)):  # walkers under the canopy
        cv2.circle(img, (x, 800), 16, (200, 200, 200), -1, cv2.LINE_AA)
        cv2.line(img, (x, 816), (x, 870), (200, 200, 200), 8)
        cv2.line(img, (x, 870), (x - 14, 900), (200, 200, 200), 6)
        cv2.line(img, (x, 870), (x + 14, 900), (200, 200, 200), 6)
    _tag(img, "ESQUEMA · SIN ESCALA")
    return img


# ---------------------------------------------------------------- thirty years burying, forty digging up
def era(t, dur, t0=0.3, mark=None):
    img = background("dark_grid", t)
    y0, x0, x1 = 600, 160, 1760
    yr = lambda y: x0 + (y - 1913) / (2025 - 1913) * (x1 - x0)
    k = ease_io(prog(t, t0, 0.8))
    cv2.line(img, (x0, y0), (int(lerp(x0, x1, k)), y0), (120, 120, 126), 6)
    ev = [(1915, "ABRE", GOLD), (1921, "LA NIEVE", BLUE), (1948, "ONEONTA", RED_), (1954, "GEMELOS", RED_), (1966, "MITCHELL POINT", RED_),
          (1987, "EL PLAN", GREEN), (2000, "GEMELOS", GREEN), (2009, "ONEONTA", GREEN), (2025, "MITCHELL POINT", GREEN)]
    for i, (y, txt, col) in enumerate(ev):
        a = ease_back(prog(t, t0 + 0.5 + i * 0.22, 0.3))
        if a <= 0:
            continue
        x = yr(y)
        up = i % 2 == 0
        cv2.circle(img, (int(x), y0), int(12 * a), col, -1, cv2.LINE_AA)
        cv2.line(img, (int(x), y0), (int(x), y0 - 90 if up else y0 + 90), col, 3)
        label(img, str(y), x, y0 - 120 if up else y0 + 120, a, 44, WHITE)
        label(img, txt, x, y0 - 170 if up else y0 + 170, a, 34, col)
    kb = ease_out(prog(t, t0 + 2.8, 0.6))
    if kb > 0:
        cv2.rectangle(img, (int(yr(1936)), 240), (int(yr(1966)), 280), RED_, -1)
        label(img, "30 AÑOS ENTERRÁNDOLA", (yr(1936) + yr(1966)) / 2, 200, kb, 50, RED_)
        cv2.rectangle(img, (int(yr(1985)), 240), (int(yr(2025)), 280), GREEN, -1)
        label(img, "40 DESENTERRÁNDOLA", (yr(1985) + yr(2025)) / 2, 200, ease_out(prog(t, t0 + 3.3, 0.6)), 50, GREEN)
    _tag(img, "FECHAS DEL GUION")
    return img


# ---------------------------------------------------------------- price tags going up in Mosier
def prices(t, dur, t0=0.3):
    img = background("dark_grid", t)
    for i, (txt, x) in enumerate((("HOTEL", 640), ("RESTAURANTE", 1280))):
        a = ease_back(prog(t, t0 + i * 0.4, 0.4))
        if a <= 0:
            continue
        cv2.rectangle(img, (x - 230, 330), (x + 230, 620), (232, 226, 210), -1)
        label(img, txt, x, 400, a, 60, (40, 40, 40))
        up = clamp((t - t0 - 0.8 - i * 0.3) / 1.6)
        label(img, "$" * (1 + int(up * 3)), x, 520, a, 110, (180, 40, 36))
        cv2.arrowedLine(img, (x + 270, 600), (x + 270, int(600 - 220 * ease_out(up))), RED_, 12, cv2.LINE_AA, tipLength=0.3)
    label(img, "MOSIER, NOVIEMBRE DE 1921", W / 2, 170, ease_out(prog(t, 0.05, 0.4)), 56, WHITE)
    label(img, "SUBIERON LOS PRECIOS", W / 2, 800, ease_out(prog(t, t0 + 1.4, 0.4)), 76, YELLOW, box=(20, 20, 20))
    _tag(img, "ESQUEMA")
    return img
