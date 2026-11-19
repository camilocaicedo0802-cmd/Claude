"""Saluda Grade (1877-2025): diagrams drawn in code for this episode."""
import json
import math
import os

import cv2
import numpy as np

from engine import BLACK, H, RED, W, WHITE, YELLOW, clamp, ease_back, ease_in, ease_io, ease_out, lerp, prog
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

DIRT = (150, 118, 82)
DIRT_DK = (104, 80, 56)
IRON = (150, 146, 140)
WOOD = (120, 84, 50)
WOOD_DK = (78, 54, 32)
HILL = (70, 96, 64)
HILL_DK = (48, 66, 44)
SKY_T = (22, 30, 44)
SKY_B = (96, 110, 120)
WATER = (52, 104, 150)
WATER_HI = (110, 170, 220)
RED_ = (230, 70, 60)
GREEN = (90, 210, 120)
BLUE = (110, 170, 220)
GOLD = (236, 190, 70)

_PROF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sg_profile.json")))


def _blend(img, layer, a):
    if a > 0.001:
        cv2.addWeighted(layer, min(a, 1.0), img, 1 - min(a, 1.0), 0, img)


def _tag(img, txt="ESQUEMA", a=0.7):
    label(img, txt, W - 40, H - 46, a, 30, GREY, anchor="r")


def _grad(top, bot):
    g = np.linspace(0, 1, H)[:, None, None]
    img = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    return np.repeat(img, W, axis=1).astype(np.uint8)


def _smooth(prof, win=6, sm=3):
    a = np.array([[p[0], p[1]] for p in prof], np.float64)
    e = a[:, 1].copy()
    m = np.array([e[max(0, i - win):i + win + 1].min() for i in range(len(e))])
    k = np.exp(-0.5 * (np.arange(-3 * sm, 3 * sm + 1) / sm) ** 2)
    k /= k.sum()
    a[:, 1] = np.convolve(np.pad(m, 3 * sm, mode="edge"), k, mode="valid")
    return a


_LINE = _smooth(_PROF["line"])
_GRADE = _smooth(_PROF["grade"], 3, 2)


def _car(img, x, y, ang, s=1.0, col=(70, 50, 36), loco=False, brakeman=False, wheel_t=None):
    """A wagon (or a locomotive) on a slope; (x, y) = rail under its middle, ang = slope angle (radians, + = descending right)."""
    c, sn = math.cos(ang), math.sin(ang)
    R = np.array([[c, -sn], [sn, c]], np.float32)

    def P(pts):
        return (np.array(pts, np.float32) * s) @ R.T + [x, y]
    if loco:
        fill_poly(img, P([[-70, -14], [70, -14], [70, -70], [-30, -70], [-30, -100], [-70, -100]]), (34, 34, 38))
        fill_poly(img, P([[40, -70], [56, -70], [60, -112], [36, -112]]), (30, 30, 32))
        cv2.circle(img, tuple(np.round(P([[66, -60]])[0]).astype(int)), int(9 * s), GOLD, -1, cv2.LINE_AA)
    else:
        fill_poly(img, P([[-62, -14], [62, -14], [62, -64], [-62, -64]]), col)
        for k in range(-48, 60, 24):
            q = P([[k, -14], [k, -64]])
            cv2.line(img, tuple(np.round(q[0]).astype(int)), tuple(np.round(q[1]).astype(int)), (40, 28, 20), max(1, int(2 * s)), cv2.LINE_AA)
        if wheel_t is not None:  # brake wheel on the roof, turning
            hc = P([[40, -84]])[0]
            cv2.line(img, tuple(np.round(P([[40, -64]])[0]).astype(int)), tuple(np.round(hc).astype(int)), (30, 30, 30), max(2, int(3 * s)))
            cv2.ellipse(img, (int(hc[0]), int(hc[1])), (int(16 * s), int(5 * s)), math.degrees(ang), 0, 360, (200, 200, 200), max(2, int(3 * s)), cv2.LINE_AA)
    for wx in (-40, 40):
        q = P([[wx, -6]])[0]
        cv2.circle(img, (int(q[0]), int(q[1])), int(10 * s), (24, 24, 26), -1, cv2.LINE_AA)
    if brakeman:
        b = P([[10, -64]])[0]
        cv2.line(img, (int(b[0]), int(b[1])), (int(b[0]), int(b[1] - 40 * s)), (230, 220, 200), max(3, int(6 * s)), cv2.LINE_AA)
        cv2.circle(img, (int(b[0]), int(b[1] - 50 * s)), int(9 * s), (230, 220, 200), -1, cv2.LINE_AA)


# ---------------------------------------------------------------- how steep: 1-2 % against almost 5 %
def grade_cmp(t, dur, t0=0.3, show_saluda=None):
    img = background("dark_grid", t)
    base_y, x0, run = 860, 180, 1000
    rows = (("LO HABITUAL: 1 %", 0.01, (140, 140, 140)), ("COMO MUCHO: 2 %", 0.02, BLUE),
            ("SALUDA: CASI 5 %", 0.047, RED_))
    ts = show_saluda if show_saluda is not None else t0 + 1.4
    for i, (name, g, col) in enumerate(rows):
        a = ease_out(prog(t, t0 + i * 0.6 if i < 2 else ts, 0.6))
        if a <= 0:
            continue
        rise = run * g * 6.0      # vertical exaggeration x6
        cv2.line(img, (x0, base_y), (int(x0 + run * a), int(base_y - rise * a)), (20, 20, 20), 16, cv2.LINE_AA)
        cv2.line(img, (x0, base_y), (int(x0 + run * a), int(base_y - rise * a)), col, 9, cv2.LINE_AA)
        label(img, name, x0 + run + 40, base_y - rise - 6, a, 54, col, anchor="l")
    cv2.line(img, (x0, base_y), (x0 + run, base_y), (90, 90, 96), 3)
    k = ease_out(prog(t, ts + 0.8, 0.5))
    if k > 0:
        label(img, "5 PIES DE SUBIDA POR CADA 100 DE VÍA", W / 2, 150, k, 60, YELLOW, box=(20, 20, 20))
        label(img, "MÁS DEL DOBLE QUE CASI CUALQUIER LÍNEA PRINCIPAL", W / 2, 230, ease_out(prog(t, ts + 1.4, 0.4)), 44, WHITE)
    _tag(img, "ESQUEMA · PENDIENTE EXAGERADA ×6")
    return img


# ---------------------------------------------------------------- the wall: the real profile Asheville -> Spartanburg
def wall(t, dur, t0=0.3, step=1.6, hi_t=None, train=None):
    img = background("dark_grid", t)
    X0, X1, Y0, Y1 = 140, 1780, 300, 860
    lo, hi = 600.0, 2500.0
    P = np.stack([X0 + _LINE[:, 0] / _LINE[-1, 0] * (X1 - X0), Y1 - (_LINE[:, 1] - lo) / (hi - lo) * (Y1 - Y0)], 1)
    fill_poly(img, np.vstack([P, [[X1, Y1 + 40], [X0, Y1 + 40]]]), (40, 46, 40))
    part = partial_line(P, ease_io(prog(t, t0, step)))
    if len(part) > 1:
        aa_poly(img, part, (20, 20, 20), 12)
        aa_poly(img, part, YELLOW, 6)
    i_s = int(np.argmin(np.abs(_LINE[:, 0] - 55.5)))
    i_m = int(np.argmin(np.abs(_LINE[:, 0] - 60.5)))
    a = ease_out(prog(t, t0 + step, 0.4))
    for i, txt, side in ((0, "ASHEVILLE", "c"), (i_s, "SALUDA", "c"), (i_m, "MELROSE", "c"), (len(P) - 1, "SPARTANBURG", "c")):
        x, y = P[i]
        cv2.circle(img, (int(x), int(y)), 10, WHITE, -1, cv2.LINE_AA)
        label(img, txt, x, y - 50 if i in (0, i_s) else y + 60, a, 40, WHITE, box=(20, 20, 20))
    hk = ease_out(prog(t, hi_t if hi_t is not None else t0 + step + 0.6, 0.5))
    if hk > 0:
        seg = P[i_s:i_m + 1]
        aa_poly(img, seg, RED_, 12)
        label(img, "EL ESCARPE DE LA BLUE RIDGE", (P[i_s][0] + P[i_m][0]) / 2 + 260, (P[i_s][1] + P[i_m][1]) / 2, hk, 54, RED_, anchor="l")
        label(img, "≈ 600 PIES EN 3 MILLAS", (P[i_s][0] + P[i_m][0]) / 2 + 260, (P[i_s][1] + P[i_m][1]) / 2 + 66, hk, 44, WHITE, anchor="l")
    if train is not None:
        d = clamp((t - train) / 3.0)
        j = int(lerp(i_s - 30, i_m + 8, ease_in(d)))
        j = max(1, min(len(P) - 2, j))
        ang = math.atan2(P[j + 1][1] - P[j - 1][1], P[j + 1][0] - P[j - 1][0])
        _car(img, P[j][0], P[j][1], ang, 0.45, loco=True)
    label(img, "DE ASHEVILLE A SPARTANBURG · ALTITUD EN PIES", 160, 160, ease_out(prog(t, 0.1, 0.4)), 46, GREY, anchor="l")
    _tag(img, "PERFIL APROXIMADO · RELIEVE MAPZEN · ALTURA EXAGERADA")
    return img


# ---------------------------------------------------------------- a second floor with a ramp of a few steps
def ramp(t, dur, t0=0.3):
    img = background("dark_grid", t)
    fy, gy = 380, 860
    fill_poly(img, np.array([[1100, fy], [1700, fy], [1700, gy], [1100, gy]], np.float32), (60, 64, 70))
    cv2.line(img, (200, gy), (1720, gy), (110, 110, 114), 4)
    label(img, "SEGUNDO PISO", 1400, fy - 50, 1.0, 54, WHITE)
    k1 = ease_io(prog(t, t0, 1.0))
    cv2.line(img, (200, gy), (int(lerp(200, 1100, k1)), int(lerp(gy, gy - 60, k1))), (140, 140, 140), 10, cv2.LINE_AA)
    label(img, "LO QUE PODÍA SUBIR UN TREN", 560, gy - 100, k1, 40, (170, 170, 170))
    k2 = ease_io(prog(t, t0 + 1.4, 0.8))
    if k2 > 0:
        cv2.line(img, (820, gy), (int(lerp(820, 1100, k2)), int(lerp(gy, fy, k2))), (20, 20, 20), 18, cv2.LINE_AA)
        cv2.line(img, (820, gy), (int(lerp(820, 1100, k2)), int(lerp(gy, fy, k2))), RED_, 10, cv2.LINE_AA)
        label(img, "LO QUE HABÍA", 760, 520, k2, 56, RED_)
    label(img, "LA MONTAÑA, DEMASIADO ALTA Y DEMASIADO CERCA", W / 2, 140, ease_out(prog(t, t0 + 2.2, 0.4)), 54, YELLOW, box=(20, 20, 20))
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- two options: the long way round or straight up the canyon
def options(t, dur, t0=0.3, straight_t=None):
    img = np.full((H, W, 3), (54, 70, 50), np.uint8)
    rng = np.random.default_rng(4)
    for _ in range(70):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 140)
        cv2.circle(img, (int(x), int(y)), int(r), (int(64 + r / 8), int(84 + r / 8), int(58 + r / 10)), -1, cv2.LINE_AA)
    A, B = (300, 900), (1620, 180)
    cv2.circle(img, A, 18, WHITE, -1, cv2.LINE_AA)
    cv2.circle(img, B, 18, WHITE, -1, cv2.LINE_AA)
    label(img, "ABAJO", A[0], A[1] + 60, 1.0, 46, WHITE, box=(20, 20, 20))
    label(img, "SALUDA", B[0], B[1] - 56, 1.0, 46, WHITE, box=(20, 20, 20))
    # long way: zigzags with tunnels
    pts = [A]
    for i in range(1, 9):
        x = lerp(A[0], B[0], i / 9)
        y = lerp(A[1], B[1], i / 9) + (220 if i % 2 else -220)
        pts.append((x, y))
    pts.append(B)
    pts = np.array(pts, np.float64)
    from engine import ease_io as e_
    k = e_(prog(t, t0, 2.0))
    part = partial_line(pts, k)
    if len(part) > 1:
        aa_poly(img, part, (20, 20, 20), 12)
        aa_poly(img, part, (170, 170, 170), 6)
    for j in range(1, 9, 2):
        if k > j / 10:
            cv2.rectangle(img, (int(pts[j][0] - 16), int(pts[j][1] - 16)), (int(pts[j][0] + 16), int(pts[j][1] + 16)), (20, 20, 20), -1)
    label(img, "OPCIÓN 1: RODEOS, TÚNELES, DECENAS DE MILLAS", W / 2, 70, ease_out(prog(t, t0, 0.4)), 46, (200, 200, 200), box=(20, 20, 20))
    st = straight_t if straight_t is not None else t0 + 2.6
    k2 = ease_io(prog(t, st, 1.0))
    if k2 > 0:
        cv2.line(img, A, (int(lerp(A[0], B[0], k2)), int(lerp(A[1], B[1], k2))), (20, 20, 20), 20, cv2.LINE_AA)
        cv2.line(img, A, (int(lerp(A[0], B[0], k2)), int(lerp(A[1], B[1], k2))), YELLOW, 10, cv2.LINE_AA)
        label(img, "OPCIÓN 2: CASI EN LÍNEA RECTA POR EL CAÑÓN DEL PACOLET", W / 2, 1010, ease_out(prog(t, st + 0.3, 0.4)), 46, YELLOW, box=(20, 20, 20))
    _tag(img, "ESQUEMA · VISTA DESDE ARRIBA")
    return img


# ---------------------------------------------------------------- the brakeman on the roofs
def brakes(t, dur, t0=0.3, rain=True):
    img = _grad((30, 36, 46), (70, 76, 84))
    gy = 800
    fill_poly(img, np.array([[0, gy], [W, gy], [W, H], [0, H]], np.float32), (60, 56, 50))
    cv2.line(img, (0, gy - 4), (W, gy - 4), IRON, 6)
    xs = [250 + i * 355 for i in range(5)]
    for i, x in enumerate(xs):
        _car(img, x, gy - 6, 0.0, 2.6, wheel_t=t)
    # the brakeman runs along the roofs, stopping at each wheel
    span = xs[-1] - xs[0]
    ph = ((t - t0) * 0.25) % 1.0 if t > t0 else 0.0
    bx = xs[0] + span * ph
    by = gy - 6 - 64 * 2.6
    cv2.line(img, (int(bx), int(by)), (int(bx), int(by - 70)), (230, 220, 200), 10, cv2.LINE_AA)
    cv2.circle(img, (int(bx), int(by - 86)), 16, (230, 220, 200), -1, cv2.LINE_AA)
    label(img, "EL GUARDAFRENOS", bx, by - 150, ease_out(prog(t, t0, 0.4)), 46, YELLOW, box=(20, 20, 20))
    label(img, "UN VOLANTE DE HIERRO POR VAGÓN, APRETADO A MANO", W / 2, 110, ease_out(prog(t, t0 + 0.8, 0.4)), 52, WHITE, box=(20, 20, 20))
    if rain:
        rng = np.random.default_rng(int(t * 24) % 997)
        for _ in range(160):
            x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
            cv2.line(img, (int(x0), int(y0)), (int(x0 - 6), int(y0 + 26)), (150, 170, 200), 1, cv2.LINE_AA)
        label(img, "CON LLUVIA O HIELO, EL TECHO RESBALABA", W / 2, 990, ease_out(prog(t, t0 + 1.6, 0.4)), 50, BLUE, box=(20, 20, 20))
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- trains taken up in pieces
def pieces(t, dur, t0=0.3):
    img = _grad((40, 52, 70), (120, 118, 110))
    A, B = np.array([-100.0, 1000.0]), np.array([2020.0, 330.0])
    ang = math.atan2(B[1] - A[1], B[0] - A[0])
    u = (B - A) / np.linalg.norm(B - A)
    fill_poly(img, np.array([A + [0, 14], B + [0, 14], [2020, H], [-100, H]], np.float32), HILL)
    cv2.line(img, tuple(np.round(A).astype(int)), tuple(np.round(B).astype(int)), IRON, 6, cv2.LINE_AA)
    L = np.linalg.norm(B - A)

    def piece(d, tag, a=1.0):
        for c in range(3):
            p = A + u * (d - c * 128)
            _car(img, p[0], p[1], ang, 1.0, col=(84, 60, 42))
        h = A + u * (d - 3 * 128 - 8)
        _car(img, h[0], h[1], ang, 1.0, loco=True)
        q = A + u * (d - 128)
        label(img, tag, q[0], q[1] - 130, a, 40, WHITE, box=(20, 20, 20))
    piece(L - 220, "TROZO 1 · YA ARRIBA")
    k = ease_io(prog(t, t0, dur - t0 - 0.6))
    piece(lerp(1160, L - 760, k), "TROZO 2 · SUBIENDO")
    piece(520, "TROZO 3 · ESPERA")
    label(img, "EL TREN, PARTIDO EN DOS O TRES TROZOS", W / 2, 110, ease_out(prog(t, 0.1, 0.4)), 56, WHITE, box=(20, 20, 20))
    label(img, "LOCOMOTORAS DE AYUDA EMPUJANDO POR DETRÁS", W / 2, 190, ease_out(prog(t, t0 + 0.8, 0.4)), 46, YELLOW, box=(20, 20, 20))
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- the runaway: speed on the grade
def runaway(t, dur, t0=0.3, top=75, crash_t=None, span=None, title="17 DE JUNIO DE 1890 · LLUEVE"):
    img = _grad((14, 16, 22), (40, 44, 52))
    a = _GRADE
    X0, X1, Y0, Y1 = 160, 1760, 280, 860
    P = np.stack([X0 + a[:, 0] / a[-1, 0] * (X1 - X0), Y1 - (a[:, 1] - 1450) / (2150 - 1450) * (Y1 - Y0)], 1)
    fill_poly(img, np.vstack([P, [[X1, H], [X0, H]]]), (30, 40, 32))
    aa_poly(img, P, (110, 110, 110), 5)
    rng = np.random.default_rng(int(t * 24) % 997)
    for _ in range(200):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        cv2.line(img, (int(x0), int(y0)), (int(x0 - 7), int(y0 + 28)), (110, 130, 160), 1, cv2.LINE_AA)
    k = ease_in(prog(t, t0, span if span is not None else dur - t0 - 0.6))
    j = int(k * (len(P) - 2))
    j = max(1, min(len(P) - 2, j))
    ang = math.atan2(P[j + 1][1] - P[j - 1][1], P[j + 1][0] - P[j - 1][0])
    _car(img, P[j][0], P[j][1], ang, 0.9, loco=True)
    for c in range(1, 4):
        jj = max(1, j - c * 6)
        a2 = math.atan2(P[jj + 1][1] - P[jj - 1][1], P[jj + 1][0] - P[jj - 1][0])
        _car(img, P[jj][0], P[jj][1], a2, 0.9, col=(60, 44, 30))
    v = int(round(top * (0.12 + 0.88 * k ** 1.3)))
    col = WHITE if v < 30 else (YELLOW if v < 55 else RED_)
    label(img, f"{v} MPH", 1500, 160, 1.0, 120, col)
    label(img, f"≈ {int(round(v * 1.609))} KM/H", 1500, 250, 1.0, 46, GREY)
    label(img, "SALUDA", P[0][0] + 40, P[0][1] - 60, 1.0, 40, WHITE, box=(20, 20, 20))
    label(img, "MELROSE", P[-1][0] - 40, P[-1][1] + 60, 1.0, 40, WHITE, box=(20, 20, 20))
    label(img, title, 360, 160, ease_out(prog(t, 0.1, 0.4)), 50, YELLOW, anchor="l")
    _tag(img, "ESQUEMA · PERFIL REAL SALUDA–MELROSE (MAPZEN)")
    return img


# ---------------------------------------------------------------- the safety track
def safety(t, dur, t0=0.3, mode="idle", whistle_t=None, switch_t=None):
    """Bird's-eye. The switch normally points to the safety track, which climbs into a dirt pile.
    idle: show the layout. ok: the train whistles, slows, the switchman throws the lever -> main line.
    runaway: no whistle / too fast -> it goes up the safety track into the dirt. closed: the main line itself is buried (2003)."""
    img = np.full((H, W, 3), (58, 78, 52), np.uint8)
    rng = np.random.default_rng(9)
    for _ in range(260):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(10, 34)
        cv2.circle(img, (int(x), int(y)), int(r), (40, 62, 38), -1, cv2.LINE_AA)
    main = np.array([[60, 180], [600, 400], [900, 540], [1300, 760], [1860, 980]], np.float64)
    sx, sy = 900, 540                         # the switch
    side = np.array([[900, 540], [1180, 560], [1460, 520], [1640, 470]], np.float64)
    pile = (1700, 450)

    def track(pts, col, w=10):
        aa_poly(img, pts, (36, 30, 24), w + 14)
        aa_poly(img, pts, col, w)
    track(main, IRON)
    track(side, (176, 170, 160))
    cv2.ellipse(img, pile, (120, 80), -15, 0, 360, DIRT_DK, -1, cv2.LINE_AA)
    cv2.ellipse(img, pile, (96, 60), -15, 0, 360, DIRT, -1, cv2.LINE_AA)
    label(img, "MONTÓN DE TIERRA", pile[0], pile[1] - 120, 1.0, 40, WHITE, box=(20, 20, 20))
    label(img, "VÍA DE ESCAPE (CUESTA ARRIBA)", 1300, 620, 1.0, 38, (230, 220, 200), box=(20, 20, 20))
    label(img, "VÍA PRINCIPAL", 1500, 960, 1.0, 38, (230, 220, 200), box=(20, 20, 20))
    # switchman's hut
    cv2.rectangle(img, (sx - 150, sy - 150), (sx - 80, sy - 90), (150, 120, 90), -1)
    cv2.rectangle(img, (sx - 150, sy - 150), (sx - 80, sy - 90), (60, 40, 30), 3)
    label(img, "GUARDAGUJA", sx - 115, sy - 190, 1.0, 34, YELLOW, box=(20, 20, 20))
    thrown = False
    if mode == "ok" and switch_t is not None and t >= switch_t:
        thrown = True
    # switch points drawn in the colour of the route it gives
    pcol = GREEN if thrown else RED_
    tgt = main[3] if thrown else side[1]
    v = np.array(tgt) - np.array([sx, sy])
    v = v / np.linalg.norm(v) * 110
    cv2.line(img, (sx, sy), (int(sx + v[0]), int(sy + v[1])), (20, 20, 20), 22, cv2.LINE_AA)
    cv2.line(img, (sx, sy), (int(sx + v[0]), int(sy + v[1])), pcol, 12, cv2.LINE_AA)
    cv2.circle(img, (sx, sy), 16, WHITE, -1, cv2.LINE_AA)
    label(img, "SIEMPRE HACIA LA VÍA DE ESCAPE" if not thrown else "VÍA LIBRE", sx - 380, sy + 60, 1.0, 40, pcol, box=(20, 20, 20))
    if mode == "closed":
        k = ease_out(prog(t, t0, 0.8))
        cv2.ellipse(img, (1520, 846), (int(150 * k) + 1, int(90 * k) + 1), 22, 0, 360, DIRT_DK, -1, cv2.LINE_AA)
        cv2.ellipse(img, (1520, 846), (int(126 * k) + 1, int(70 * k) + 1), 22, 0, 360, DIRT, -1, cv2.LINE_AA)
        label(img, "ABRIL DE 2003: TIERRA SOBRE LA VÍA", W / 2, 90, k, 56, YELLOW, box=(20, 20, 20))
        _tag(img, "ESQUEMA · VISTA DESDE ARRIBA")
        return img
    # the train comes down from the top left
    if mode in ("ok", "runaway"):
        k = ease_in(prog(t, t0, 2.2)) if mode == "runaway" else ease_out(prog(t, t0, 2.6))
        route = np.vstack([main[:3], main[3:]]) if thrown else np.vstack([main[:3], side[1:]])
        seg = np.hypot(*np.diff(route, axis=0).T)
        cum = np.concatenate([[0], np.cumsum(seg)])
        stop = cum[-1] - (0 if mode == "ok" else 40)
        if mode == "ok":
            if switch_t is not None and t < switch_t:
                d = lerp(0, cum[2] - 90, k)
            else:
                d = lerp(cum[2] - 90, cum[-1] - 40, ease_io(prog(t, switch_t or 0, 2.0)))
        else:
            d = stop * k
        for c in range(4):
            dd = max(0.0, d - c * 70)
            i = max(1, min(len(cum) - 1, int(np.searchsorted(cum, dd))))
            p = route[i - 1] + (route[i] - route[i - 1]) * (dd - cum[i - 1]) / max(seg[i - 1], 1e-6)
            vv = route[i] - route[i - 1]
            ang = math.degrees(math.atan2(vv[1], vv[0]))
            box = cv2.boxPoints(((float(p[0]), float(p[1])), (64, 28), ang)).astype(np.int32)
            cv2.fillPoly(img, [box], (30, 30, 34) if c == 0 else (90, 60, 40), cv2.LINE_AA)
        if mode == "ok" and whistle_t is not None:
            wk = prog(t, whistle_t, 1.2)
            if 0 < wk < 1:
                cx, cy = 520, 330
                for r in range(3):
                    rr = int(30 + 90 * ((wk * 2 + r / 3) % 1))
                    cv2.circle(img, (cx, cy), rr, WHITE, 3, cv2.LINE_AA)
                label(img, "¡PIIII!", cx, cy - 140, 1 - wk * 0.5, 60, WHITE, box=(20, 20, 20))
        if mode == "runaway" and k > 0.97:
            label(img, "¡CONTRA LA TIERRA!", W / 2, 90, ease_back(prog(t, t0 + 2.1, 0.3)), 70, RED_, box=(20, 20, 20))
    _tag(img, "ESQUEMA · VISTA DESDE ARRIBA")
    return img


# ---------------------------------------------------------------- the automatic timer
def timer(t, dur, t0=0.3, fast_t=None):
    img = background("dark_grid", t)
    x0, x1, y = 260, 1660, 600
    cv2.line(img, (x0, y), (x1, y), IRON, 10)
    for x in (x0 + 200, x1 - 200):
        cv2.rectangle(img, (x - 10, y - 90), (x + 10, y - 10), (200, 200, 200), -1)
        cv2.circle(img, (x, y - 110), 22, YELLOW, -1, cv2.LINE_AA)
    label(img, "EL SISTEMA MIDE CUÁNTO TARDA EN EL ÚLTIMO TRAMO", W / 2, 150, ease_out(prog(t, 0.1, 0.4)), 50, WHITE)
    ft = fast_t if fast_t is not None else t0 + (dur - t0) / 2
    fast = t >= ft
    v = 14 if fast else 6
    kk = prog(t, ft, 1.6) if fast else prog(t, t0, max(ft - t0, 0.5))
    x = lerp(x0, x1, kk)
    cv2.rectangle(img, (int(x - 70), y - 40), (int(x + 70), y - 6), (40, 40, 44), -1)
    ok = v <= 8
    label(img, f"{v} MPH", W / 2, 360, 1.0, 110, GREEN if ok else RED_)
    label(img, "≤ 8 MPH (13 KM/H): VÍA PRINCIPAL" if ok else "MÁS RÁPIDO: A LA TIERRA", W / 2, 820, 1.0, 58, GREEN if ok else RED_, box=(20, 20, 20))
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- Tunstall's stone: a cut tree trunk
def stump(t, dur, t0=0.3):
    img = background("dark_grid", t)
    cx, base = 700, 920
    k = ease_out(prog(t, t0, 0.8))
    h, wb, wt = 430 * k, 170, 140
    marble, shade, dark = (214, 210, 200), (176, 172, 162), (130, 126, 118)
    # trunk with bark ridges, a wider root flare at the base, broken branch stubs
    body = np.array([[cx - wb - 30, base], [cx + wb + 30, base], [cx + wb, base - 40], [cx + wt, base - h], [cx - wt, base - h], [cx - wb, base - 40]], np.float32)
    fill_poly(img, body, marble)
    for j in range(-6, 7):
        x0 = cx + j * 22
        pts = np.array([[x0 + 6 * math.sin(q * 0.05 + j), base - q] for q in np.linspace(0, h, 30)], np.float64)
        aa_poly(img, pts, shade if j % 2 else dark, 3)
    if h > 120:
        for sx, sy, ang in ((cx + wt - 6, base - h * 0.62, -0.5), (cx - wt + 6, base - h * 0.38, 3.6)):
            ex, ey = sx + math.cos(ang) * 80, sy + math.sin(ang) * 80
            cv2.line(img, (int(sx), int(sy)), (int(ex), int(ey)), marble, 44, cv2.LINE_AA)
            cv2.ellipse(img, (int(ex), int(ey)), (24, 22), 0, 0, 360, shade, -1, cv2.LINE_AA)
        # the cut top, with growth rings
        cv2.ellipse(img, (cx, int(base - h)), (wt, 34), 0, 0, 360, (226, 222, 212), -1, cv2.LINE_AA)
        for r in (0.8, 0.6, 0.4, 0.2):
            cv2.ellipse(img, (cx, int(base - h)), (int(wt * r), int(34 * r)), 0, 0, 360, shade, 2, cv2.LINE_AA)
    fk = ease_out(prog(t, t0 + 0.8, 0.8))
    for s_ in (-1, 1):
        for j in range(5):
            x0 = cx + s_ * (60 + j * 34)
            pts = np.array([[x0, base], [x0 + s_ * 26, base - 110 * fk], [x0 + s_ * 64, base - 190 * fk]], np.float64)
            aa_poly(img, pts, (80, 150, 80), 7)
            for q in np.linspace(0.3, 0.9, 4):
                px, py = x0 + s_ * 64 * q, base - 190 * fk * q
                cv2.line(img, (int(px), int(py)), (int(px + s_ * 22), int(py - 8)), (90, 170, 90), 3, cv2.LINE_AA)
    bk = ease_back(prog(t, t0 + 1.4, 0.4))
    label(img, "B L E", cx, base - h * 0.5, bk, 70, (70, 70, 80))
    label(img, "MÁRMOL CON FORMA DE TRONCO CORTADO", 1420, 400, ease_out(prog(t, t0 + 0.4, 0.4)), 46, WHITE)
    label(img, "UNA VIDA CORTADA ANTES DE TIEMPO", 1420, 480, ease_out(prog(t, t0 + 1.0, 0.4)), 46, YELLOW)
    label(img, "BLE: HERMANDAD DE MAQUINISTAS", 1420, 600, ease_out(prog(t, t0 + 1.6, 0.4)), 42, GREY)
    label(img, "DE LOCOMOTORA", 1420, 650, ease_out(prog(t, t0 + 1.6, 0.4)), 42, GREY)
    _tag(img, "RECREACIÓN · NO ES LA LÁPIDA REAL")
    return img


# ---------------------------------------------------------------- Helene: rails hanging in the air
def washout(t, dur, t0=0.3):
    img = _grad((40, 46, 56), (110, 104, 96))
    gy = 600
    k = ease_io(prog(t, t0, 1.6))
    gap0, gap1 = 760 - 260 * k, 1160 + 260 * k
    fill_poly(img, np.array([[0, gy], [gap0, gy], [gap0 - 80, H], [0, H]], np.float32), DIRT)
    fill_poly(img, np.array([[gap1, gy], [W, gy], [W, H], [gap1 + 80, H]], np.float32), DIRT)
    for x in range(0, W, 44):
        sag = 0 if (x < gap0 or x > gap1) else 30 * math.sin(math.pi * (x - gap0) / max(gap1 - gap0, 1))
        cv2.rectangle(img, (x, int(gy - 10 + sag)), (x + 24, int(gy + 2 + sag)), WOOD_DK, -1)
    xs = np.linspace(0, W, 80)
    ys = gy - 14 + np.where((xs > gap0) & (xs < gap1), 30 * np.sin(np.pi * (xs - gap0) / max(gap1 - gap0, 1)), 0)
    aa_poly(img, np.stack([xs, ys], 1), IRON, 6)
    lvl = H - 120 * ease_out(prog(t, t0, 1.0))
    layer = img.copy()
    cv2.rectangle(layer, (int(gap0 - 80), int(lvl)), (int(gap1 + 80), H), WATER, -1)
    _blend(img, layer, 0.8)
    for j in range(20):
        x = gap0 + ((t * 300 + j * 61) % max(gap1 - gap0, 1))
        cv2.line(img, (int(x), int(lvl + 20)), (int(x + 30), int(lvl + 20)), WATER_HI, 3, cv2.LINE_AA)
    label(img, "SEPTIEMBRE DE 2024 · HURACÁN HELENE", W / 2, 110, ease_out(prog(t, 0.1, 0.4)), 56, YELLOW, box=(20, 20, 20))
    label(img, "RIELES COLGANDO EN EL AIRE", W / 2, 470, ease_out(prog(t, t0 + 1.4, 0.4)), 60, WHITE, box=(20, 20, 20))
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- the rule turned around
def rule(t, dur, t0=0.3, flip_t=None):
    img = background("dark_grid", t)
    ft = flip_t if flip_t is not None else t0 + 1.6
    a = ease_out(prog(t, t0, 0.4))
    label(img, "EN CASI CUALQUIER OTRO SITIO", 520, 300, a, 50, GREY)
    label(img, "VÍA ABIERTA", 520, 420, a, 110, GREEN)
    label(img, "…HASTA QUE ALGO VA MAL", 520, 540, a, 50, WHITE)
    b = ease_out(prog(t, ft, 0.4))
    label(img, "EN SALUDA", 1400, 300, b, 50, YELLOW)
    label(img, "VÍA CERRADA", 1400, 420, b, 110, RED_)
    label(img, "…HASTA QUE TODO VA BIEN", 1400, 540, b, 50, WHITE)
    cv2.line(img, (960, 240), (960, 620), (90, 90, 96), 3)
    return img
