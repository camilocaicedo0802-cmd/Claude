"""Ridge Route (1915-2025): diagrams drawn in code for this episode."""
import json
import math
import os

import cv2
import numpy as np

from engine import BLACK, H, RED, W, WHITE, YELLOW, clamp, ease_back, ease_in, ease_io, ease_out, lerp, prog
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

ROCK = (96, 86, 72)
ROCK_DK = (66, 58, 48)
HILL = (120, 106, 74)
HILL_DK = (88, 78, 56)
CONCRETE = (196, 192, 182)
ASPHALT = (60, 62, 66)
WATER = (52, 104, 150)
WATER_HI = (110, 170, 220)
SKY_T = (22, 30, 44)
SKY_B = (120, 104, 90)
BLUE = (110, 170, 220)
GREEN = (80, 190, 110)
FIRE = (255, 140, 40)

_PROF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rr_profile.json")))


def _blend(img, layer, a):
    if a > 0.001:
        cv2.addWeighted(layer, min(a, 1.0), img, 1 - min(a, 1.0), 0, img)


def _tag(img, txt="ESQUEMA", a=0.7):
    label(img, txt, W - 160, H - 46, a, 30, GREY)


def _grad(top, bot):
    g = np.linspace(0, 1, H)[:, None, None]
    img = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    return np.repeat(img, W, axis=1).astype(np.uint8)


def _car(img, x, y, s=1.0, col=(40, 40, 44), a=1.0, smoke=0.0, t=0.0, facing=1):
    """1920s touring car in side view; (x, y) = ground under the middle."""
    tgt = img.copy() if a < 0.999 else img
    f = facing
    body = np.array([[-70, -18], [70, -18], [70, -38], [40, -40], [30, -62], [-40, -62], [-48, -40], [-70, -40]], np.float32)
    body[:, 0] *= f
    fill_poly(tgt, body * s + [x, y], col)
    cv2.rectangle(tgt, (int(x + f * 48 * s) if f > 0 else int(x - 66 * s), int(y - 58 * s)),
                  (int(x + 66 * s) if f > 0 else int(x - 48 * s), int(y - 40 * s)), (70, 70, 74), -1)
    for wx in (-45, 45):
        cv2.circle(tgt, (int(x + f * wx * s), int(y - 12 * s)), int(15 * s), (20, 20, 22), -1, cv2.LINE_AA)
        cv2.circle(tgt, (int(x + f * wx * s), int(y - 12 * s)), int(7 * s), (150, 140, 120), -1, cv2.LINE_AA)
    if smoke > 0:
        rng = np.random.default_rng(int(t * 10))
        for k in range(14):
            ph = ((t * 0.6 + k / 14) % 1.0)
            cx = x + f * 66 * s + rng.uniform(-8, 8) + ph * 30
            cy = y - 50 * s - ph * 160
            cv2.circle(tgt, (int(cx), int(cy)), int((8 + ph * 26) * s), (230, 230, 230), -1, cv2.LINE_AA)
    if tgt is not img:
        _blend(img, tgt, a)


# ---------------------------------------------------------------- 697 curves: the steering wheel
def curves(t, dur, t0=0.3, n=697, miles=44):
    img = background("dark_grid", t)
    k = ease_io(prog(t, t0, dur - t0 - 0.5))
    cx, cy, r = 560, 560, 300
    ang = k * 100 * 2 * math.pi
    cv2.circle(img, (cx, cy), r, (36, 36, 40), 34, cv2.LINE_AA)
    cv2.circle(img, (cx, cy), r, (90, 90, 96), 4, cv2.LINE_AA)
    for j in range(3):
        a = ang + j * 2 * math.pi / 3 + math.pi / 2
        cv2.line(img, (cx, cy), (int(cx + math.cos(a) * r), int(cy + math.sin(a) * r)), (60, 60, 66), 26, cv2.LINE_AA)
    cv2.circle(img, (cx, cy), 60, (60, 60, 66), -1, cv2.LINE_AA)
    a = ang - math.pi / 2
    cv2.circle(img, (int(cx + math.cos(a) * r), int(cy + math.sin(a) * r)), 20, YELLOW, -1, cv2.LINE_AA)
    label(img, f"{int(round(n * k))}", 1340, 380, 1.0, 230, YELLOW)
    label(img, "CURVAS", 1340, 520, 1.0, 70, WHITE)
    label(img, f"EN {miles} MILLAS · ≈ 70 KM", 1340, 600, ease_out(prog(t, t0 + 0.6, 0.4)), 46, GREY)
    label(img, f"≈ {int(round(100 * k))} VUELTAS AL VOLANTE", 1340, 720, ease_out(prog(t, t0 + 1.2, 0.4)), 56, WHITE)
    return img


# ---------------------------------------------------------------- canyon or ridge
def section(t, dur, mode="flood", t0=0.3):
    """Cross-section of the mountains. flood: the grade in the canyon bottom is swept away (1914). ridge: the road on the
    crest, rain runs off both sides. cut: modern machines cut straight through and fill the gully."""
    img = _grad(SKY_T, SKY_B)
    xs = np.linspace(0, W, 200)
    prof = 520 + 210 * np.sin(xs / 300 + 0.4) * np.cos(xs / 900) + 60 * np.sin(xs / 110)
    prof = np.clip(prof, 300, 900)
    i_crest = int(np.argmin(prof[40:160]) + 40)
    i_valley = int(np.argmax(prof[20:180]) + 20)
    ground = np.stack([xs, prof], 1)
    fill_poly(img, np.vstack([ground, [[W, H], [0, H]]]), HILL)
    aa_poly(img, ground, HILL_DK, 4)
    if mode == "flood":
        vx, vy = xs[i_valley], prof[i_valley]
        k = ease_in(prog(t, t0 + 1.0, 1.4))
        rd = 1.0 - k
        if rd > 0:
            cv2.rectangle(img, (int(vx - 70), int(vy - 10)), (int(vx + 70), int(vy)), CONCRETE, -1)
        lvl = vy - 140 * ease_out(prog(t, t0 + 0.3, 1.2))
        mask = (prof > lvl)
        layer = img.copy()
        for i in range(len(xs) - 1):
            if mask[i] and abs(i - i_valley) < 40:
                cv2.rectangle(layer, (int(xs[i]), int(lvl)), (int(xs[i + 1]) + 1, int(prof[i])), WATER, -1)
        _blend(img, layer, 0.85)
        for j in range(30):
            x = vx - 200 + ((t * 220 + j * 37) % 400)
            cv2.line(img, (int(x), int(lvl + 8)), (int(x + 26), int(lvl + 8)), WATER_HI, 3, cv2.LINE_AA)
        label(img, "MARZO DE 1914", W / 2, 120, ease_out(prog(t, 0.1, 0.4)), 64, YELLOW)
        label(img, "LA CRECIDA SE LLEVA LA EXPLANACIÓN DEL FONDO DEL CAÑÓN", W / 2, 190, ease_out(prog(t, t0 + 1.2, 0.4)), 44, WHITE)
    elif mode == "ridge":
        cx, cy = xs[i_crest], prof[i_crest]
        cv2.rectangle(img, (int(cx - 60), int(cy - 12)), (int(cx + 60), int(cy)), CONCRETE, -1)
        label(img, "LA CARRETERA, EN LA CRESTA", cx, cy - 90, ease_out(prog(t, t0, 0.4)), 50, YELLOW)
        rng = np.random.default_rng(3)
        for j in range(140):
            x0 = rng.uniform(0, W)
            y = (rng.uniform(0, 1) + t * 0.9) % 1.0 * 600 + 40
            cv2.line(img, (int(x0), int(y)), (int(x0 - 6), int(y + 22)), (170, 190, 220), 2, cv2.LINE_AA)
        k = ease_out(prog(t, t0 + 0.8, 0.6))
        for sgn in (-1, 1):
            pts = [(cx + sgn * (70 + 30 * q), cy + 14 + 26 * q * q * 1.0 + q * 40) for q in np.linspace(0, 6, 30)]
            pts = np.array([[x, prof[min(int(x / W * 199), 199)] + 6] for x, _ in pts if 0 < x < W])
            if len(pts) > 2:
                aa_poly(img, partial_line(pts, k), WATER_HI, 6)
        label(img, "EL AGUA ESCURRE HACIA LOS DOS LADOS", W / 2, 1000, ease_out(prog(t, t0 + 1.0, 0.4)), 50, WHITE)
    elif mode == "cut":
        k = ease_io(prog(t, t0, 2.0))
        y0 = prof[i_crest] + 160
        newp = np.where(xs < W, lerp(prof, np.full_like(prof, y0), k * (np.abs(prof - y0) < 400)), prof)
        g2 = np.stack([xs, newp], 1)
        layer = img.copy()
        fill_poly(layer, np.vstack([ground, [[W, H], [0, H]]]), (64, 70, 80))
        fill_poly(layer, np.vstack([g2, [[W, H], [0, H]]]), HILL)
        _blend(img, layer, 1.0)
        cv2.line(img, (0, int(y0)), (W, int(y0)), (90, 92, 96), 14)
        label(img, "CORTES GIGANTES Y RELLENOS", W / 2, 140, ease_out(prog(t, t0, 0.4)), 60, YELLOW)
        label(img, "LA AUTOPISTA ATRAVIESA LAS MONTAÑAS", W / 2, 210, ease_out(prog(t, t0 + 0.6, 0.4)), 44, WHITE)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- around every hill
def wrap(t, dur, t0=0.3, cut_t=None):
    """Bird's-eye: a road that wraps round each hill (1915) and a straight cut through them (later)."""
    img = np.full((H, W, 3), (88, 78, 56), np.uint8)
    hills = [(300 + i * 330, 560, 120 + 25 * (i % 2)) for i in range(5)]
    for x, y, r in hills:
        for k in range(7, 0, -1):
            c = 7 - k
            cv2.circle(img, (int(x), int(y)), int(r * k / 7 + 8), (int(92 + 12 * c), int(82 + 11 * c), int(58 + 7 * c)), -1, cv2.LINE_AA)
    pts = [[40, 560]]
    for i, (x, y, r) in enumerate(hills):
        sgn = -1 if i % 2 == 0 else 1
        for ang in np.linspace(math.pi, 0, 30):
            pts.append([x + math.cos(ang) * (r + 45), y + sgn * math.sin(ang) * (r + 45)])
    pts.append([W - 40, 560])
    part = partial_line(np.array(pts, np.float64), ease_io(prog(t, t0, 3.0)))
    if len(part) > 1:
        aa_poly(img, part, (20, 20, 20), 16)
        aa_poly(img, part, CONCRETE, 10)
    label(img, "SI HABÍA UN CERRO, LO RODEABA", W / 2, 100, ease_out(prog(t, t0, 0.4)), 60, WHITE)
    if cut_t is not None:
        a = ease_io(prog(t, cut_t, 1.0))
        if a > 0:
            cv2.line(img, (40, 560), (int(40 + (W - 80) * a), 560), (20, 20, 20), 26, cv2.LINE_AA)
            cv2.line(img, (40, 560), (int(40 + (W - 80) * a), 560), YELLOW, 14, cv2.LINE_AA)
            label(img, "CON MÁQUINAS: EN LÍNEA RECTA", W / 2, 1000, ease_out(prog(t, cut_t + 0.6, 0.4)), 56, YELLOW)
    _tag(img, "ESQUEMA · VISTA DESDE ARRIBA")
    return img


# ---------------------------------------------------------------- the time card
def timecard(t, dur, t0=0.3, out_t=None, early=True):
    img = background("dark_grid", t)
    pw, ph = 860, 560
    x0, y0 = W / 2 - pw / 2 - 260, 230
    a = ease_out(prog(t, t0, 0.5))
    if a > 0:
        layer = img.copy()
        cv2.rectangle(layer, (int(x0), int(y0)), (int(x0 + pw), int(y0 + ph)), (226, 220, 200), -1)
        cv2.rectangle(layer, (int(x0 + 14), int(y0 + 14)), (int(x0 + pw - 14), int(y0 + ph - 14)), (150, 140, 120), 2)
        _blend(img, layer, a)
        ink = (40, 36, 30)
        label(img, "RIDGE ROUTE · CONTROL DE VELOCIDAD", x0 + pw / 2, y0 + 70, a, 44, ink, box=None)
        label(img, "ENTRADA: CASTAIC", x0 + 60, y0 + 190, a, 50, ink, anchor="l")
        label(img, "SALIDA: GORMAN", x0 + 60, y0 + 330, a, 50, ink, anchor="l")
        label(img, "RECREACIÓN", x0 + pw - 140, y0 + ph - 40, a * 0.8, 28, (120, 110, 90))
    ka = ease_back(prog(t, t0 + 0.8, 0.4))
    if ka > 0:
        label(img, "8:05", x0 + 620, y0 + 190, ka, 90, (40, 60, 160))
    if out_t is not None:
        kb = ease_back(prog(t, out_t, 0.4))
        if kb > 0:
            label(img, "10:20" if early else "11:05", x0 + 620, y0 + 330, kb, 90, (40, 60, 160))
        kc = ease_out(prog(t, out_t + 0.8, 0.4))
        if kc > 0 and early:
            cx, cy = x0 + pw + 330, y0 + 280
            label(img, "DEMASIADO PRONTO", cx, cy - 60, kc, 60, RED)
            label(img, "= DEMASIADO RÁPIDO", cx, cy + 10, kc, 52, WHITE)
            label(img, "MULTA", cx, cy + 110, ease_back(prog(t, out_t + 1.4, 0.4)), 110, RED)
    return img


# ---------------------------------------------------------------- overheating, and brakes that fade
def climb(t, dur, mode="up", t0=0.3):
    """mode up: a 1920s car on a long grade, the radiator boils, a stone behind the wheel.
    mode down: rear-wheel brakes glowing, smoke, the drop beside the road."""
    img = _grad((30, 40, 56), (150, 120, 90))
    if mode == "up":
        ang = math.radians(-9)
        x0, y0 = 0, 900
        fill_poly(img, [[0, 900], [W, 900 - W * math.tan(-ang)], [W, H], [0, H]], HILL)
        k = clamp((t - t0) / 3.0)
        cx = lerp(300, 900, ease_out(k))
        cy = 900 - cx * math.tan(-ang)
        boil = prog(t, t0 + 2.2, 0.8)
        _car(img, cx, cy, 2.4, smoke=boil, t=t)
        if boil > 0.5:
            fill_poly(img, [[cx - 170, cy + 4], [cx - 135, cy - 30], [cx - 105, cy + 10]], (140, 136, 130))
            label(img, "UNA PIEDRA PARA CALZAR LA RUEDA", cx - 100, cy + 80, ease_out(prog(t, t0 + 3.2, 0.4)), 40, WHITE)
        label(img, "EL AGUA DEL RADIADOR HIERVE", W / 2, 130, ease_out(prog(t, t0 + 2.4, 0.4)), 64, YELLOW)
    else:
        fill_poly(img, [[0, 520], [W, 900], [W, H], [0, H]], HILL)
        fill_poly(img, [[0, 520], [W, 900], [W, 940], [0, 560]], ASPHALT)
        cv2.line(img, (0, 560), (W, 940), (40, 40, 40), 4)
        k = clamp((t - t0) / (dur - t0))
        cx = lerp(300, 1300, ease_in(k) * 0.9)
        cy = 520 + cx * (380 / W)
        heat = prog(t, t0 + 0.8, 1.6)
        _car(img, cx, cy + 20, 1.6, facing=1)
        rx, ry = cx - 45 * 1.6, cy + 20 - 12 * 1.6
        col = (int(lerp(150, 255, heat)), int(lerp(140, 80, heat)), int(lerp(120, 30, heat)))
        cv2.circle(img, (int(rx), int(ry)), int(9 * 1.6), col, -1, cv2.LINE_AA)
        rng = np.random.default_rng(int(t * 12))
        for j in range(int(30 * heat)):
            ph = rng.uniform(0, 1)
            cv2.circle(img, (int(rx - ph * 140 + rng.uniform(-10, 10)), int(ry - ph * 90)), int(8 + ph * 24), (200, 200, 200), -1, cv2.LINE_AA)
        label(img, "SOLO FRENABAN LAS RUEDAS DE ATRÁS", W / 2, 120, ease_out(prog(t, t0, 0.4)), 60, YELLOW)
        label(img, "SE RECALIENTAN Y DEJAN DE AGARRAR", W / 2, 190, ease_out(prog(t, t0 + 1.4, 0.4)), 46, WHITE)
        label(img, "SIN BARANDAS", W - 300, 1010, ease_out(prog(t, t0 + 2.0, 0.4)), 50, RED)
    _tag(img, "ILUSTRACIÓN")
    return img


# ---------------------------------------------------------------- the inns along the profile
def _near(lon, lat):
    return min(range(len(_PROF)), key=lambda k: (_PROF[k][2] - lon) ** 2 + (_PROF[k][3] - lat) ** 2)


_RS, _SB = _near(-118.7292, 34.6622), _near(-118.7095, 34.7411)
INNS = [(_RS, "RESERVOIR SUMMIT"), (int(_RS + (_SB - _RS) * 0.25), "NATIONAL FOREST INN"), (int(_RS + (_SB - _RS) * 0.5), "KELLY'S HALF WAY INN"),
        (int(_RS + (_SB - _RS) * 0.75), "TUMBLE INN"), (_SB, "SANDBERG'S")]


def inns(t, dur, t0=0.3, step=0.7, hi=None):
    img = _grad((18, 22, 32), (60, 56, 52))
    pr = [(d, e) for d, e, _, _ in _PROF]
    d0, d1 = pr[0][0], pr[-1][0]
    X0, X1, Y0, Y1 = 120, W - 120, 940, 260
    e0, e1 = 800.0, 4800.0
    sx = lambda d: X0 + (d - d0) / (d1 - d0) * (X1 - X0)
    sy = lambda e: Y0 + (e - e0) / (e1 - e0) * (Y1 - Y0)
    ground = np.array([[sx(d), sy(e)] for d, e in pr])
    fill_poly(img, np.vstack([ground, [[X1, H], [X0, H]]]), HILL_DK)
    fill_poly(img, np.vstack([[[0, ground[0][1]]], ground, [[W, ground[-1][1]], [W, H], [0, H]]]), HILL_DK)
    aa_poly(img, ground, CONCRETE, 5)
    for ft in (1000, 2000, 3000, 4000):
        y = sy(ft)
        cv2.line(img, (60, int(y)), (84, int(y)), (130, 130, 130), 2)
        label(img, f"{ft:,} PIES".replace(",", "."), 96, y, 0.8, 26, (160, 160, 160), anchor="l")
    label(img, "CASTAIC", X0 + 40, Y0 + 60, 0.9, 36, WHITE)
    label(img, "GRAPEVINE", X1 - 60, Y0 + 60, 0.9, 36, WHITE)
    for i, (j, name) in enumerate(INNS):
        a = ease_out(prog(t, t0 + i * step, 0.4))
        if a <= 0:
            continue
        x, y = ground[j]
        col = YELLOW if hi is None or hi == i else (200, 200, 200)
        lx, ly = 260 + i * 290, 250 + 55 * (i % 2)
        cv2.line(img, (int(x), int(y)), (int(lx), int(ly + 24)), col, 2, cv2.LINE_AA)
        cv2.circle(img, (int(x), int(y)), 11, col, -1, cv2.LINE_AA)
        label(img, name, lx, ly, a, 36, col)
    jmax = int(np.argmin(ground[:, 1]))
    label(img, "MÁS DE 4.200 PIES", ground[jmax][0] + 30, ground[jmax][1] + 60, ease_out(prog(t, t0 + 4 * step, 0.4)), 38, WHITE, anchor="l")
    label(img, "UNA POSADA EN LO ALTO DE CADA SUBIDA", W / 2, 110, ease_out(prog(t, 0.1, 0.4)), 56, WHITE)
    _tag(img, "PERFIL REAL · UBICACIONES APROXIMADAS")
    return img


# ---------------------------------------------------------------- Swede's Cut
def swedes(t, dur, t0=0.3):
    img = _grad((40, 60, 90), (170, 150, 120))
    cx, top, bot = W / 2, 260, 900
    k = ease_io(prog(t, t0, 1.6))
    d = (bot - top) * k
    fill_poly(img, [[0, top], [cx - 260, top], [cx - 90, top + d], [cx + 90, top + d], [cx + 260, top], [W, top], [W, H], [0, H]], ROCK)
    aa_poly(img, [[cx - 260, top], [cx - 90, top + d], [cx + 90, top + d], [cx + 260, top]], ROCK_DK, 4)
    if k > 0.95:
        cv2.rectangle(img, (int(cx - 90), int(top + d - 12)), (int(cx + 90), int(top + d)), CONCRETE, -1)
        xa = cx + 330
        cv2.arrowedLine(img, (int(xa), int(top + 6)), (int(xa), int(top + d - 6)), YELLOW, 5, cv2.LINE_AA, tipLength=0.04)
        cv2.arrowedLine(img, (int(xa), int(top + d - 6)), (int(xa), int(top + 6)), YELLOW, 5, cv2.LINE_AA, tipLength=0.04)
        label(img, "110 PIES", xa + 40, (top + bot) / 2 - 30, ease_out(prog(t, t0 + 1.6, 0.4)), 90, YELLOW, anchor="l")
        label(img, "MÁS DE 30 METROS", xa + 40, (top + bot) / 2 + 50, ease_out(prog(t, t0 + 1.9, 0.4)), 44, WHITE, anchor="l")
        hx, hy = cx - 20, top + d - 12
        cv2.circle(img, (int(hx), int(hy - 52)), 7, WHITE, -1, cv2.LINE_AA)
        cv2.line(img, (int(hx), int(hy - 45)), (int(hx), int(hy - 18)), WHITE, 4)
        cv2.line(img, (int(hx), int(hy - 18)), (int(hx - 7), int(hy)), WHITE, 3)
        cv2.line(img, (int(hx), int(hy - 18)), (int(hx + 7), int(hy)), WHITE, 3)
    label(img, "SWEDE'S CUT", W / 2, 120, ease_out(prog(t, 0.1, 0.4)), 72, YELLOW)
    _tag(img, "CORTE · ESQUEMA")
    return img


# ---------------------------------------------------------------- the bonds: 18 years of use, 50 of payments
def bonds(t, dur, t0=0.3, use_t=None, end_t=None):
    img = background("dark_grid", t)
    y0, y1 = 1910, 1970
    xa, xb, yy = 160, W - 160, 620
    sx = lambda y: xa + (y - y0) / (y1 - y0) * (xb - xa)
    cv2.line(img, (xa, yy), (xb, yy), (120, 124, 130), 3)
    for y in range(1910, 1971, 10):
        cv2.line(img, (int(sx(y)), yy - 10), (int(sx(y)), yy + 10), (140, 140, 140), 2)
        label(img, str(y), sx(y), yy + 46, 0.8, 32, GREY)
    k = ease_io(prog(t, t0, 2.5))
    yr = lerp(1915, 1965, k)
    for y in range(1916, int(yr) + 1):
        h = 60 + (1965 - y) * 1.2
        cv2.rectangle(img, (int(sx(y) - 6), int(yy - 20 - h)), (int(sx(y) + 6), int(yy - 20)), (90, 200, 120) if y <= 1933 else (230, 90, 70), -1)
    label(img, "PAGOS DE LA DEUDA", sx(1915) + 10, 240, ease_out(prog(t, t0, 0.4)), 40, WHITE, anchor="l")
    if use_t is not None:
        a = ease_out(prog(t, use_t, 0.4))
        cv2.rectangle(img, (int(sx(1915)), yy + 90), (int(sx(1915) + (sx(1933) - sx(1915)) * a), yy + 120), YELLOW, -1)
        label(img, "18 AÑOS DE USO (1915–1933)", sx(1915), yy + 170, a, 40, YELLOW, anchor="l")
    if end_t is not None:
        a = ease_out(prog(t, end_t, 0.4))
        cv2.rectangle(img, (int(sx(1915)), yy + 220), (int(sx(1915) + (sx(1965) - sx(1915)) * a), yy + 250), RED, -1)
        label(img, "50 AÑOS PAGÁNDOLA (HASTA 1965)", sx(1915), yy + 300, a, 40, RED, anchor="l")
    _tag(img, "ILUSTRACIÓN · VALORES NO A ESCALA")
    return img


# ---------------------------------------------------------------- three roads in layers
def layers(t, dur, t0=0.3, step=1.0):
    img = _grad((22, 30, 44), (70, 80, 92))
    xs = np.linspace(0, W, 120)
    top = 360 + 120 * np.cos((xs - W / 2) / 420) * -1 + 30 * np.sin(xs / 90)
    fill_poly(img, np.vstack([np.stack([xs, top], 1), [[W, H], [0, H]]]), HILL)
    i_c = int(np.argmin(top))
    a1 = ease_out(prog(t, t0, 0.5))
    if a1 > 0:
        cx, cy = xs[i_c], top[i_c]
        cv2.rectangle(img, (int(cx - 80), int(cy - 10)), (int(cx + 80), int(cy)), CONCRETE, -1)
        label(img, "1915 · LA CRESTA: CERRADA Y ROTA", cx, cy - 70, a1, 44, YELLOW)
    a2 = ease_out(prog(t, t0 + step, 0.5))
    lake_y = 820
    if a2 > 0:
        layer = img.copy()
        fill_poly(layer, [[220, lake_y], [W - 220, lake_y], [W - 420, 1000], [420, 1000]], WATER)
        _blend(img, layer, a2)
        cv2.rectangle(img, (760, 975), (1160, 985), (60, 70, 80), -1)
        label(img, "1933 · BAJO EL LAGO: HUNDIDA", W / 2, 1040, a2, 44, BLUE)
    a3 = ease_out(prog(t, t0 + 2 * step, 0.5))
    if a3 > 0:
        y = 640
        fill_poly(img, [[0, y - 30], [W, y - 30], [W, y + 30], [0, y + 30]], (50, 52, 56))
        for xx in range(0, W, 120):
            cv2.line(img, (int(xx + (t * 300) % 120), y), (int(xx + 60 + (t * 300) % 120), y), (230, 210, 120), 4)
        label(img, "1970 · ENTRE AMBAS: LA AUTOPISTA DE HOY", W / 2, y - 80, a3, 44, WHITE)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- the dam: the canyon road drowned
def drown(t, dur, t0=0.3):
    img = _grad((30, 44, 64), (150, 140, 120))
    xs = np.linspace(0, W, 160)
    prof = 900 - 520 * np.exp(-((xs - W / 2) / 520) ** 2) * 0 + 0
    prof = 330 + 600 * (1 - np.exp(-((xs - W / 2) / 360) ** 2))
    prof = 930 - 600 * (1 - np.exp(-((xs - W / 2) / 380) ** 2)) * 0
    canyon = 300 + 620 * np.exp(-((xs - W / 2) / 300) ** 2)
    fill_poly(img, np.vstack([np.stack([xs, canyon], 1), [[W, H], [0, H]]]), HILL)
    bottom = canyon.max()
    cv2.rectangle(img, (int(W / 2 - 60), int(bottom - 12)), (int(W / 2 + 60), int(bottom)), (70, 72, 76), -1)
    label(img, "US 99 (1933)", W / 2, bottom + 50, 1.0, 40, WHITE)
    k = ease_io(prog(t, t0 + 0.8, 2.6))
    lvl = lerp(bottom, bottom - 520, k)
    if k > 0:
        layer = img.copy()
        for i in range(len(xs) - 1):
            if canyon[i] > lvl:
                cv2.rectangle(layer, (int(xs[i]), int(lvl)), (int(xs[i + 1]) + 1, int(canyon[i])), WATER, -1)
        _blend(img, layer, 0.85)
    label(img, "UNA PRESA DE 387 PIES EN EL RÍO PIRU", W / 2, 120, ease_out(prog(t, t0, 0.4)), 56, YELLOW)
    label(img, "EL AGUA SE TRAGA LA CARRETERA", W / 2, 190, ease_out(prog(t, t0 + 2.0, 0.4)), 46, WHITE)
    _tag(img, "ESQUEMA")
    return img
