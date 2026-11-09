"""Road to Nowhere (Swain County, NC): diagrams drawn in code for this episode."""
import functools
import math

import cv2
import numpy as np

from engine import (BLACK, H, RED, W, WHITE, YELLOW, clamp, ease_back, ease_in, ease_io, ease_out, lerp, over,
                    over_center, prog, rounded_rect_sprite, text_sprite)
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

WATER = (34, 78, 118)
WATER_HI = (70, 130, 175)
EARTH = (64, 56, 46)
EARTH_DK = (40, 36, 31)
GRASS = (54, 78, 52)
FOREST = (36, 58, 40)
ROAD = (128, 126, 120)
PAPER = (234, 228, 212)
INK = (34, 32, 30)
ORANGE = (214, 120, 40)
GREEN = (80, 170, 96)


def _sky(t, top=(16, 20, 28), bot=(44, 54, 66)):
    g = np.linspace(0, 1, H)[:, None, None]
    img = (np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g)
    img = np.repeat(img, W, axis=1).astype(np.uint8)
    return img


def _poly(img, pts, col, alpha=1.0):
    if alpha >= 0.999:
        fill_poly(img, pts, col)
        return
    layer = img.copy()
    fill_poly(layer, pts, col)
    cv2.addWeighted(layer, alpha, img, 1 - alpha, 0, img)


def _cross(img, x, y, s, col, a=1.0, th=4):
    if a <= 0:
        return
    layer = img.copy() if a < 1 else img
    cv2.line(layer, (int(x), int(y - s)), (int(x), int(y + s * 0.9)), col, th, cv2.LINE_AA)
    cv2.line(layer, (int(x - s * 0.55), int(y - s * 0.4)), (int(x + s * 0.55), int(y - s * 0.4)), col, th, cv2.LINE_AA)
    if a < 1:
        cv2.addWeighted(layer, a, img, 1 - a, 0, img)


def _stone(img, x, y, s, col=(170, 168, 160), a=1.0, tilt=0.0):
    """Rounded-top headstone, bottom centre at (x, y)."""
    if a <= 0:
        return
    ang = np.linspace(math.pi, 0, 12)
    top = np.stack([x + np.cos(ang) * s * 0.5, y - s * 1.1 + -np.sin(ang) * s * 0.5], 1)
    pts = np.vstack([[x - s * 0.5, y], top, [x + s * 0.5, y]])
    if tilt:
        c, sn = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        pts = (pts - [x, y]) @ np.array([[c, -sn], [sn, c]]).T + [x, y]
    _poly(img, pts, col, a)


def _house(img, x, y, s, col=(150, 120, 92), roof=(90, 60, 50), a=1.0):
    """Small farmhouse, bottom centre at (x, y)."""
    body = [[x - s, y], [x - s, y - s * 1.1], [x + s, y - s * 1.1], [x + s, y]]
    rf = [[x - s * 1.2, y - s * 1.05], [x, y - s * 1.9], [x + s * 1.2, y - s * 1.05]]
    _poly(img, body, col, a)
    _poly(img, rf, roof, a)
    _poly(img, [[x - s * 0.25, y], [x - s * 0.25, y - s * 0.6], [x + s * 0.2, y - s * 0.6], [x + s * 0.2, y]], (50, 40, 34), a)


def _church(img, x, y, s, a=1.0):
    col = (226, 222, 210)
    _poly(img, [[x - s, y], [x - s, y - s * 1.2], [x + s, y - s * 1.2], [x + s, y]], col, a)
    _poly(img, [[x - s * 1.15, y - s * 1.15], [x, y - s * 1.9], [x + s * 1.15, y - s * 1.15]], (120, 118, 112), a)
    _poly(img, [[x - s * 0.28, y - s * 1.6], [x - s * 0.28, y - s * 2.5], [x + s * 0.28, y - s * 2.5], [x + s * 0.28, y - s * 1.6]], col, a)
    _poly(img, [[x - s * 0.36, y - s * 2.45], [x, y - s * 3.2], [x + s * 0.36, y - s * 2.45]], (120, 118, 112), a)
    _cross(img, x, y - s * 3.45, s * 0.32, col, a, 3)


def _school(img, x, y, s, a=1.0):
    col = (176, 80, 64)
    _poly(img, [[x - s * 1.6, y], [x - s * 1.6, y - s * 1.2], [x + s * 1.6, y - s * 1.2], [x + s * 1.6, y]], col, a)
    _poly(img, [[x - s * 1.75, y - s * 1.15], [x, y - s * 1.8], [x + s * 1.75, y - s * 1.15]], (90, 60, 50), a)
    for k in (-1.0, -0.4, 0.4, 1.0):
        _poly(img, [[x + s * k - s * 0.18, y - s * 0.45], [x + s * k - s * 0.18, y - s * 0.9], [x + s * k + s * 0.18, y - s * 0.9],
                    [x + s * k + s * 0.18, y - s * 0.45]], (230, 210, 150), a)


def _tree(img, x, y, s, col=FOREST, a=1.0):
    _poly(img, [[x - s * 0.5, y], [x, y - s * 2.0], [x + s * 0.5, y]], col, a)


def _boat(img, x, y, s, a=1.0, flowers=True):
    hull = [[x - s * 1.4, y - s * 0.25], [x + s * 1.5, y - s * 0.25], [x + s * 1.1, y + s * 0.35], [x - s * 1.2, y + s * 0.35]]
    _poly(img, hull, (236, 234, 228), a)
    _poly(img, [[x - s * 0.4, y - s * 0.25], [x - s * 0.4, y - s * 0.75], [x + s * 0.5, y - s * 0.75], [x + s * 0.5, y - s * 0.25]], (60, 70, 86), a)
    if flowers:
        for i, c in enumerate(((230, 80, 120), (250, 200, 60), (120, 160, 240), (240, 120, 60))):
            cv2.circle(img, (int(x + s * (0.75 + 0.18 * i)), int(y - s * 0.38)), max(3, int(s * 0.12)), c, -1, cv2.LINE_AA)


# =================================================================== the valley, in cross-section
VX = np.linspace(0, W, 200)


def _valley_ground(x):
    """Ground height (screen y) across the valley: south slope (left), floor, north slope (right)."""
    x = np.asarray(x, np.float64)
    floor = 880.0
    lk = np.clip((640.0 - x) / 640.0, 0, 1)
    rk = np.clip((x - 1180.0) / 740.0, 0, 1)
    y = floor - 560.0 * lk ** 0.8 - 600.0 * rk ** 0.85
    y = y - 12 * np.sin(x / 70.0) * ((lk > 0.05) | (rk > 0.05))
    y = y + 34 * np.exp(-((x - 1600.0) / 70.0) ** 2)      # a small flat knoll on the north slope
    return y


LAKE_Y = 640.0           # lake surface (full pool)
CEM_X = 1600.0           # family cemetery on a knoll of the north slope


def _water_poly(level):
    xs = np.linspace(0, W, 240)
    g = _valley_ground(xs)
    ok = g > level
    if not ok.any():
        return None
    xa, xb = xs[ok][0], xs[ok][-1]
    top = [[xa, level], [xb, level]]
    bottom = [[x, gy] for x, gy in zip(xs[ok][::-1], g[ok][::-1])]
    return np.array(top + bottom, np.float64)


def valley(t, dur, mode="life", t_flood=0.6, flood_dur=4.0, show_labels=True, cem_t=2.3):
    """Cross-section of the Little Tennessee valley.
    modes: life (the valley before the water), flood (the lake rises), cut (no way to the graves by land),
           boat (families cross by boat and walk up to the knoll)."""
    img = _sky(t)
    # far ridges
    for k, (yy, col) in enumerate(((420, (38, 46, 54)), (500, (44, 52, 58)))):
        xs = np.linspace(0, W, 60)
        ys = yy + 40 * np.sin(xs / (170 + 60 * k) + k * 2) + 26 * np.sin(xs / 61.0 + k)
        fill_poly(img, np.vstack([np.stack([xs, ys], 1), [[W, H], [0, H]]]), col)
    g = _valley_ground(VX)
    ground = np.vstack([np.stack([VX, g], 1), [[W, H], [0, H]]])
    fill_poly(img, ground, EARTH)
    aa_poly(img, np.stack([VX, g], 1), GRASS, 10)
    # trees on the slopes
    rng = np.random.default_rng(7)
    for x in rng.uniform(20, W - 20, 70):
        gy = float(np.interp(x, VX, g))
        if 640 < x < 1130 or abs(x - CEM_X) < 90:
            continue
        _tree(img, x, gy + 4, rng.uniform(16, 26), FOREST if rng.random() > 0.3 else (44, 70, 46))

    life = mode == "life"
    # the town on the valley floor
    def appear(i):
        return ease_back(prog(t, 0.3 + 0.18 * i, 0.4)) if life else 1.0
    floor = 880
    items = [("house", 700, 28), ("house", 790, 24), ("church", 880, 28), ("school", 1000, 24), ("house", 1110, 26),
             ("house", 1160, 20)]
    for i, (kind, x, s) in enumerate(items):
        k = appear(i)
        if k <= 0:
            continue
        s2 = s * max(k, 0.01)
        if kind == "house":
            _house(img, x, floor, s2)
        elif kind == "church":
            _church(img, x, floor, s2)
        else:
            _school(img, x, floor, s2)
    # river (in the middle of the floor) and the old road on its north bank
    cv2.ellipse(img, (935, floor + 2), (30, 7), 0, 0, 360, WATER_HI, -1, cv2.LINE_AA)
    rk = ease_out(prog(t, 1.6, 0.6)) if life else 1.0
    if rk > 0:
        cv2.rectangle(img, (1040, floor - 3), (int(lerp(1040, 1080, rk)), floor + 6), ROAD, -1)
        cv2.rectangle(img, (1046, floor - 14), (1068, floor - 4), (200, 70, 60), -1)
    # family cemetery on the north knoll
    cy = float(np.interp(CEM_X, VX, g))
    ck = appear(len(items) + 1)
    for j, dx in enumerate((-46, -18, 10, 38)):
        _stone(img, CEM_X + dx, cy + 2 - 0.42 * dx * 0.3, 19, (182, 180, 172), min(1.0, ck * 1.0), tilt=(6 if j == 1 and mode == "boat" else 0))
    # water
    level = None
    if mode == "flood":
        k = ease_io(prog(t, t_flood, flood_dur))
        level = lerp(floor + 6, LAKE_Y, k)
    elif mode in ("cut", "boat", "under"):
        level = LAKE_Y
    if level is not None and level < floor + 4:
        wp = _water_poly(level)
        if wp is not None:
            _poly(img, wp, WATER, 0.94)
            xs = np.linspace(wp[0, 0], wp[1, 0], 120)
            ys = level + 3 * np.sin(xs / 22.0 + t * 3.0)
            aa_poly(img, np.stack([xs, ys], 1), WATER_HI, 3)
    if show_labels:
        if life:
            label(img, "GRANJAS", 745, 770, ease_out(prog(t, 0.6, 0.4)), 44, WHITE)
            label(img, "IGLESIAS Y ESCUELAS", 940, 690, ease_out(prog(t, 1.1, 0.4)), 44, WHITE)
            label(img, "RÍO", 935, 935, ease_out(prog(t, 1.4, 0.4)), 40, WATER_HI)
            label(img, "NC 288", 1060, 935, ease_out(prog(t, 1.9, 0.4)), 40, YELLOW)
            label(img, "CEMENTERIO FAMILIAR", CEM_X, cy - 110, ease_out(prog(t, cem_t, 0.4)), 42, WHITE)
        if mode == "flood":
            label(img, "NOVIEMBRE DE 1944", W / 2, 130, ease_out(prog(t, 0.2, 0.4)), 64, YELLOW)
            label(img, "SE CIERRAN LAS COMPUERTAS", W / 2, 200, ease_out(prog(t, 0.5, 0.4)), 46, WHITE)
            label(img, "PUEBLOS, GRANJAS Y LA NC 288, BAJO EL AGUA", W / 2, 960, ease_out(prog(t, t_flood + flood_dur * 0.7, 0.5)),
                  44, WHITE)
        if mode in ("cut", "boat"):
            label(img, "LAGO FONTANA", 920, LAKE_Y + 120, 1.0, 50, WATER_HI)
            label(img, "TUMBAS SOBRE EL AGUA", CEM_X, cy - 110, ease_out(prog(t, 0.3, 0.4)), 44, YELLOW)
            label(img, "LADERA NORTE", 1700, 200, 0.8, 38, GREY)
    if mode == "cut":
        # a road that cannot reach the knoll
        k = ease_io(prog(t, 0.8, 1.4))
        wp = _water_poly(LAKE_Y)
        xl = float(wp[0, 0])
        xs_ = np.linspace(60, xl, 30)
        path = np.stack([xs_, np.interp(xs_, VX, g) - 8], 1)
        aa_poly(img, partial_line(path, k), ROAD, 10)
        if k >= 1:
            xk = ease_back(prog(t, 2.3, 0.35))
            if xk > 0:
                s = 44 * xk
                cx_, cy_ = xl + 10, LAKE_Y - 60
                for sg in (1, -1):
                    cv2.line(img, (int(cx_ - s), int(cy_ - s * sg)), (int(cx_ + s), int(cy_ + s * sg)), BLACK, 16, cv2.LINE_AA)
                    cv2.line(img, (int(cx_ - s), int(cy_ - s * sg)), (int(cx_ + s), int(cy_ + s * sg)), RED, 10, cv2.LINE_AA)
            label(img, "POR TIERRA, NO HAY CAMINO", W / 2, 130, ease_out(prog(t, 2.5, 0.4)), 60, WHITE)
    if mode == "boat":
        k = ease_io(prog(t, 0.4, max(dur - 2.2, 1.0)))
        wp = _water_poly(LAKE_Y)
        xl, xr = float(wp[0, 0]), float(wp[1, 0])
        bx = lerp(xl + 60, xr - 50, min(k * 1.15, 1.0))
        _boat(img, bx, LAKE_Y - 4 + 2 * math.sin(t * 2.5), 30)
        if k > 0.86:
            kk = prog(k, 0.86, 0.14)
            for i in range(3):
                px = lerp(xr - 30, CEM_X - 70 + i * 22, kk)
                py = lerp(LAKE_Y - 10, cy - 8, kk) + i * 2
                cv2.circle(img, (int(px), int(py - 30)), 7, WHITE, -1, cv2.LINE_AA)
                cv2.line(img, (int(px), int(py - 22)), (int(px), int(py)), WHITE, 5, cv2.LINE_AA)
        label(img, "EN LANCHA", bx, LAKE_Y + 60, 1.0, 44, YELLOW)
    return _push(img, t, dur, 1.16, 1.24, 1010, 640)


def _push(img, t, dur, z0, z1, cx, cy):
    z = lerp(z0, z1, ease_io(t / max(dur, 1e-3)))
    M = np.array([[z, 0, W / 2 - z * cx], [0, z, H / 2 - z * cy]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


# =================================================================== Fontana Dam vs a skyscraper
def dam_height(t, dur):
    img = background("dark_grid", t)
    base = 930
    ppm = 4.4  # screen px per metre
    # the dam: a tall concrete wall in profile
    k = ease_io(prog(t, 0.3, 2.2))
    hd = 146 * ppm * k
    x0 = 520
    pts = [[x0 - 250, base], [x0 - 250 + 210, base - hd], [x0 + 40, base - hd], [x0 + 60, base]]
    fill_poly(img, pts, (176, 172, 164))
    for j in range(1, 12):
        yy = base - hd * j / 12
        cv2.line(img, (int(x0 - 250 + 210 * j / 12), int(yy)), (int(x0 + 40 + 20 * (1 - j / 12)), int(yy)), (150, 146, 140), 1)
    # water behind it
    if k > 0.2:
        fill_poly(img, [[x0 + 60, base], [x0 + 40, base - hd * 0.94], [W - 1080, base - hd * 0.94], [W - 1080, base]], WATER)
    # building of ~48 floors
    kb = ease_io(prog(t, 1.2, 2.0))
    hb = 146 * ppm * kb
    bx = 1330
    cv2.rectangle(img, (bx - 120, int(base - hb)), (bx + 120, base), (70, 76, 86), -1)
    for f in range(int(48 * kb)):
        yy = base - (f + 0.5) * 3.04 * ppm
        for c in range(6):
            cv2.rectangle(img, (bx - 104 + c * 36, int(yy - 4)), (bx - 84 + c * 36, int(yy + 4)), (210, 196, 120), -1)
    cv2.line(img, (120, base), (W - 120, base), (90, 92, 96), 3)
    # height marks
    a = ease_out(prog(t, 2.4, 0.5))
    if a > 0:
        yt = base - 146 * ppm
        cv2.line(img, (300, int(yt)), (1520, int(yt)), YELLOW, 2, cv2.LINE_AA)
        label(img, "480 PIES · 146 M", 300, yt - 46, a, 64, YELLOW, anchor="l")
    label(img, "PRESA FONTANA", x0 - 100, base + 50, ease_out(prog(t, 0.6, 0.4)), 46, WHITE)
    label(img, "UN EDIFICIO DE ≈ 48 PISOS", bx, base + 50, ease_out(prog(t, 1.6, 0.4)), 46, WHITE)
    label(img, "LA MÁS ALTA AL ESTE DE LAS MONTAÑAS ROCOSAS", W / 2, 110, ease_out(prog(t, 3.0, 0.5)), 52, WHITE)
    return img


# =================================================================== icon counters (families, graves, cemeteries)
def icon_grid(t, dur, kind="house", n=131, per=10, total=1311, title="FAMILIAS", sub="SALIERON DEL VALLE", t0=0.3, fill=2.2,
              cols=None, color=WHITE):
    img = background("dark_grid", t)
    cols = cols or (19 if n > 60 else 10 if n > 20 else 7)
    rows = (n + cols - 1) // cols
    cell = min(64, 760 / max(rows, 1), 1500 / cols)
    gx0 = W / 2 - cols * cell / 2 + cell / 2
    gy0 = 590 - rows * cell / 2 + cell / 2 + 40
    k = prog(t, t0, fill)
    shown = int(n * ease_out(k))
    for i in range(shown):
        x = gx0 + (i % cols) * cell
        y = gy0 + (i // cols) * cell
        s = cell * 0.30
        if kind == "house":
            _house(img, x, y + s, s, (196, 190, 176), (130, 120, 110))
        elif kind == "grave":
            _stone(img, x, y + s * 1.1, s * 1.15, (176, 174, 168))
        else:
            _cross(img, x, y, s * 1.3, color, 1.0, 5)
    v = int(round(total * ease_out(k)))
    label(img, f"{v:,}", W / 2, 120, ease_out(prog(t, 0.1, 0.3)), 130, YELLOW)
    label(img, title, W / 2, 230, ease_out(prog(t, 0.2, 0.3)), 56, WHITE)
    if sub:
        label(img, sub, W / 2, H - 70, ease_out(prog(t, t0 + fill * 0.6, 0.4)), 44, GREY)
    if per > 1:
        label(img, f"CADA ICONO = {per}", W - 230, H - 70, 0.7 * ease_out(prog(t, t0 + 0.4, 0.4)), 30, GREY)
    return img


# =================================================================== the 1943 agreement (recreation)
PARTIES = ["CONDADO DE SWAIN", "TVA", "DEPARTAMENTO DEL INTERIOR", "ESTADO DE CAROLINA DEL NORTE"]


def agreement(t, dur, mode="parties", times=None, hl_t=1.9, red_t=3.2, term_t=None):
    """mode: parties (four signatures), terms (what each side gets), clause (the fine print), void (cancelled in 2010)."""
    img = background("dark_grid", t)
    pw, ph = 1180, 1000
    cx, cy = W / 2, 560
    zoom = 1.0
    if mode == "clause":
        zoom = lerp(1.0, 1.55, ease_io(prog(t, 0.6, 1.4)))
    paper = np.full((ph, pw, 3), PAPER, np.uint8)
    rng = np.random.default_rng(3)
    noise = rng.normal(0, 4, (ph // 4, pw // 4)).astype(np.float32)
    paper = np.clip(paper.astype(np.float32) + cv2.resize(noise, (pw, ph))[..., None], 0, 255).astype(np.uint8)

    def txt(s, x, y, size, col=INK, f="type", a=1.0, anchor="l"):
        sp = text_sprite(s, f, size, col, False)
        xx = x if anchor == "l" else x - sp.w / 2
        over(paper, sp, xx - 24, y - sp.h / 2, a)
        return sp

    txt("ACUERDO", pw / 2, 90, 64, INK, "serif", anchor="c")
    txt("30 DE JULIO DE 1943", pw / 2, 160, 40, INK, "type", anchor="c")
    cv2.line(paper, (90, 205), (pw - 90, 205), (120, 112, 100), 2)
    if mode in ("parties", "void"):
        for i, p in enumerate(PARTIES):
            ti = times[i] if times else 0.4 + 0.45 * i
            a = ease_out(prog(t, ti, 0.4)) if mode == "parties" else 1.0
            y = 300 + i * 160
            txt(p, 110, y, 40, INK, "type", a)
            k = ease_io(prog(t, ti + 0.2, 0.7)) if mode == "parties" else 1.0
            if k > 0:
                xs = np.linspace(0, 1, 90)
                sig = np.stack([780 + 300 * xs, y + 30 - 26 * np.sin(xs * (17 + i * 3)) * np.exp(-xs * 1.4) - 20 * xs], 1)
                aa_poly(paper, partial_line(sig, k), (30, 40, 110), 3)
            cv2.line(paper, (760, int(y + 52)), (1100, int(y + 52)), (110, 104, 96), 1)
    else:
        lines = [("1. LA TVA PAGA AL CONDADO $400,000", "POR LA CARRETERA QUE SE HUNDE"),
                 ("2. LA TVA COMPRA LA ORILLA NORTE", "≈ 44,000 ACRES (18,000 HA), PARA EL PARQUE"),
                 ("3. INTERIOR CONSTRUYE UNA CARRETERA NUEVA", "≈ 30 MILLAS, DE BRYSON CITY A LA PRESA")]
        for i, (l1, l2) in enumerate(lines):
            a = ease_out(prog(t, (term_t[i] if term_t else 0.3 + 0.9 * i), 0.4)) if mode == "terms" else 1.0
            y = 290 + i * 150
            txt(l1, 100, y, 40, INK, "type", a)
            txt(l2, 140, y + 52, 32, (90, 84, 76), "type", a)
        # fine print
        fy = 800
        txt("… SIEMPRE QUE EL CONGRESO APRUEBE", 100, fy, 30, (70, 66, 60))
        txt("TODOS LOS FONDOS NECESARIOS.", 100, fy + 44, 30, (70, 66, 60))
        if mode == "clause":
            hk = ease_out(prog(t, hl_t, 0.6))
            if hk > 0:
                layer = paper.copy()
                cv2.rectangle(layer, (80, fy - 26), (int(80 + 700 * hk), fy + 70), (60, 200, 240), -1)
                cv2.addWeighted(layer, 0.45, paper, 0.55, 0, paper)
            rk = ease_out(prog(t, red_t, 0.5))
            if rk > 0:
                txt("SI NO LO HACE, NO ES INCUMPLIMIENTO.", 100, fy + 110, 32, (170, 30, 40), "type", rk)
    sp_paper = np.ascontiguousarray(paper)
    from engine import Sprite
    rgba = np.dstack([sp_paper, np.full(sp_paper.shape[:2], 255, np.uint8)])
    sprite = Sprite(rgba)
    oy = 0.0
    if mode == "clause":
        oy = -lerp(0, 330, ease_io(prog(t, 0.6, 1.4)))
    over_center(img, sprite, cx, cy + oy, 1.0, zoom * lerp(1.03, 1.0, ease_out(prog(t, 0, 0.8))) * 0.95)
    if mode == "void":
        k = ease_back(prog(t, 0.5, 0.4))
        if k > 0:
            st = text_sprite("ANULADO · 2010", "bebas", int(150 * k), RED, False, tracking=6)
            M = cv2.getRotationMatrix2D((W / 2, H / 2), 14, 1.0)
            layer = np.zeros_like(img)
            over_center(layer, st, W / 2, H / 2, 1.0)
            layer = cv2.warpAffine(layer, M, (W, H))
            m = (layer.sum(2) > 0)[..., None]
            img[:] = np.where(m, layer, img)
    label(img, "RECREACIÓN", W - 150, H - 46, 0.75, 30, GREY)
    return img


# =================================================================== the rock: pyrite, cut, acid water
def apple(t, dur):
    img = background("dark_grid", t)
    # whole apple
    for i, (x, cut) in enumerate(((620, False), (1300, True))):
        a = ease_out(prog(t, 0.2 + 0.6 * i, 0.4))
        if a <= 0:
            continue
        r = 190
        if not cut:
            cv2.circle(img, (x, 560), r, (176, 36, 44), -1, cv2.LINE_AA)
            cv2.ellipse(img, (x - 60, 490), (50, 80), 30, 0, 360, (210, 70, 70), -1, cv2.LINE_AA)
            cv2.line(img, (x, 380), (x + 10, 330), (90, 60, 40), 10, cv2.LINE_AA)
            cv2.ellipse(img, (x + 45, 345), (40, 18), -20, 0, 360, (70, 140, 60), -1, cv2.LINE_AA)
            label(img, "ENTERA: AGUANTA DÍAS", x, 820, a, 48, WHITE)
        else:
            k = ease_io(prog(t, 1.6, max(dur - 2.0, 1.0)))
            flesh = np.array([232, 222, 170], np.float32) * (1 - k) + np.array([150, 104, 52], np.float32) * k
            cv2.circle(img, (x, 560), r, (176, 36, 44), -1, cv2.LINE_AA)
            cv2.circle(img, (x, 560), r - 14, tuple(int(c) for c in flesh), -1, cv2.LINE_AA)
            for ang in range(0, 360, 72):
                px = x + 40 * math.cos(math.radians(ang))
                py = 560 + 40 * math.sin(math.radians(ang))
                cv2.ellipse(img, (int(px), int(py)), (14, 7), ang, 0, 360, (60, 40, 30), -1, cv2.LINE_AA)
            label(img, "CORTADA: SE OSCURECE", x, 820, a, 48, ORANGE if k > 0.5 else WHITE)
    label(img, "CON LA ROCA PASA ALGO PARECIDO", W / 2, 140, ease_out(prog(t, dur - 1.6, 0.4)), 56, YELLOW)
    return img


def _rock_section(img, t, cut_k):
    """Hillside section: soil, the dark Anakeesta layer with pyrite glints; cut_k opens a road cut."""
    xs = np.linspace(0, W, 120)
    surf = 300 + 0.42 * xs * 0 + 230 * (1 - xs / W) ** 1.2 + 30 * np.sin(xs / 140)
    surf = 260 + (xs / W) * 420 + 20 * np.sin(xs / 120)
    fill_poly(img, np.vstack([np.stack([xs, surf], 1), [[W, H], [0, H]]]), EARTH)
    # anakeesta layer band
    top = surf + 120
    band = np.vstack([np.stack([xs, top], 1), np.stack([xs[::-1], (top + 260)[::-1]], 1)])
    fill_poly(img, band, (44, 46, 52))
    rng = np.random.default_rng(11)
    for _ in range(140):
        x = rng.uniform(0, W)
        ty = float(np.interp(x, xs, top))
        y = rng.uniform(ty + 10, ty + 250)
        tw = 0.5 + 0.5 * math.sin(t * 3 + x)
        cv2.circle(img, (int(x), int(y)), int(rng.uniform(2, 5)), (int(160 + 60 * tw), int(140 + 50 * tw), 60), -1, cv2.LINE_AA)
    aa_poly(img, np.stack([xs, surf], 1), GRASS, 12)
    for x in np.arange(30, W, 70):
        _tree(img, x, float(np.interp(x, xs, surf)) + 4, 22)
    if cut_k > 0:
        # a notch cut into the slope for the road
        cx0, cx1 = 760, 1180
        y0 = float(np.interp(cx0, xs, surf))
        depth = 330 * cut_k
        notch = [[cx0 - 40, y0 - 10], [cx1, float(np.interp(cx1, xs, surf)) - 10], [cx1, y0 + depth], [cx0 + 80, y0 + depth]]
        fill_poly(img, notch, (30, 36, 44))
        face = [[cx0 - 40, y0 - 10], [cx0 + 80, y0 + depth], [cx0 + 30, y0 + depth], [cx0 - 70, y0 + 10]]
        fill_poly(img, face, (58, 60, 66))
        rng2 = np.random.default_rng(4)
        for _ in range(26):
            u, v = rng2.uniform(0, 1), rng2.uniform(0, 1)
            px = lerp(lerp(cx0 - 60, cx0 + 50, v), lerp(cx0 - 20, cx0 + 70, v), u)
            py = lerp(y0, y0 + depth - 6, v)
            cv2.circle(img, (int(px), int(py)), 3, (220, 190, 80), -1, cv2.LINE_AA)
        fill_poly(img, [[cx0 + 80, y0 + depth], [cx1, y0 + depth], [cx1, y0 + depth + 16], [cx0 + 80, y0 + depth + 16]], ROAD)
        return (cx0 + 80, y0 + depth, cx1)
    return None


def rock(t, dur, mode="buried"):
    """modes: buried (harmless underground), cut (road cut, rain, acid runoff killing a creek)."""
    img = _sky(t, (20, 24, 30), (40, 46, 52))
    cut_k = 0.0 if mode == "buried" else ease_io(prog(t, 0.3, 1.2))
    info = _rock_section(img, t, cut_k)
    label(img, "ANAKEESTA · PIZARRA CON PIRITA", 470, 540 if mode == "buried" else 420, ease_out(prog(t, 0.3, 0.4)), 46, YELLOW)
    if mode == "buried":
        label(img, "ENTERRADA, NO HACE DAÑO", W / 2, 120, ease_out(prog(t, 1.0, 0.4)), 64, WHITE)
        return img
    x0, yb, x1 = info
    # rain
    rk = prog(t, 1.6, 0.5)
    if rk > 0:
        rng = np.random.default_rng(5)
        for i in range(90):
            x = rng.uniform(0, W)
            sp = rng.uniform(700, 1000)
            ph = rng.uniform(0, 1)
            y = ((t * sp / H + ph) % 1.0) * H
            cv2.line(img, (int(x), int(y)), (int(x - 6), int(y + 22)), (150, 170, 196), 2, cv2.LINE_AA)
    # acid water running down the cut and towards the creek on the right
    ak = ease_io(prog(t, 2.4, 2.2))
    if ak > 0:
        path = np.array([[x0 + 20, yb - 180], [x0 + 60, yb - 40], [x0 + 200, yb + 6], [x1 + 40, yb + 40], [1460, 900], [1700, 990], [W, 1010]])
        part = partial_line(path, ak)
        aa_poly(img, part, ORANGE, 12)
        label(img, "AGUA ÁCIDA + METALES", 1240, 760, ease_out(prog(t, 3.0, 0.4)), 46, ORANGE)
    # creek with fish
    cv2.ellipse(img, (1700, 1010), (260, 40), 0, 0, 360, (46, 92, 120) if ak < 0.9 else (60, 90, 70), -1, cv2.LINE_AA)
    fk = prog(t, 4.2, 1.0)
    for i, fx in enumerate((1620, 1720, 1800)):
        ang = 180 * ease_io(fk)
        col = (200, 210, 220) if fk < 0.5 else (120, 120, 110)
        fy = 1010 - 8 * fk
        cv2.ellipse(img, (fx, int(fy)), (24, 10), ang, 0, 360, col, -1, cv2.LINE_AA)
        tail = [[fx + 22 * math.cos(math.radians(ang)), fy], [fx + 38 * math.cos(math.radians(ang)), fy - 10], [fx + 38 * math.cos(math.radians(ang)), fy + 10]]
        fill_poly(img, tail, col)
    if fk > 0.3:
        label(img, "LOS ARROYOS MUEREN", 1640, 880, ease_out(prog(t, 4.6, 0.4)), 44, RED)
    label(img, "AL ABRIRLA: AIRE + LLUVIA", W / 2, 110, ease_out(prog(t, 0.5, 0.4)), 60, WHITE)
    return img


# =================================================================== the promised road, mile by mile (schematic)
# 30 miles from the dam (left) to Bryson City (right); mile marks are illustrative of the story's figures
RX0, RX1, RY = 170, 1750, 560


def _mx(mile):  # miles measured from the dam
    return RX0 + (RX1 - RX0) * mile / 30.0


def road_progress(t, dur, stage=1948, t0=0.3, nothing_t=None):
    """Schematic of the 30-mile North Shore Road promise. stage: 1943, 1948, 1958, 1962, 1970, 1972."""
    img = background("dark_grid", t)
    # lake under the road
    fill_poly(img, [[RX0, RY + 70], [RX1 - 140, RY + 70], [RX1 - 140, RY + 150], [RX0, RY + 150]], (30, 56, 80))
    label(img, "LAGO FONTANA", (RX0 + RX1) / 2 - 70, RY + 112, 0.8, 40, WATER_HI)
    # promised route
    cv2.line(img, (RX0, RY), (RX1, RY), (70, 72, 78), 6, cv2.LINE_AA)
    for m in range(0, 31, 5):
        x = _mx(m)
        cv2.line(img, (int(x), RY - 14), (int(x), RY + 14), (90, 92, 96), 2)
    label(img, "PRESA FONTANA", RX0 + 40, RY - 70, 1.0, 40, WHITE)
    label(img, "BRYSON CITY", RX1 - 40, RY - 70, 1.0, 40, WHITE)
    label(img, "LA CARRETERA PROMETIDA · ≈ 30 MILLAS", W / 2, 150, ease_out(prog(t, 0.1, 0.4)), 56, WHITE)
    # cemeteries along the north shore, between the dam and the tunnel
    for i, m in enumerate(np.linspace(2.5, 22.5, 10)):
        _cross(img, _mx(m), RY - 120 - 18 * math.sin(i * 1.7), 16, (200, 198, 190), 0.85, 4)
    label(img, "CEMENTERIOS DE LA ORILLA NORTE", _mx(12.5), RY - 210, 0.9, 38, GREY)

    def seg(m0, m1, start, d=1.2, col=YELLOW, w=14):
        k = ease_io(prog(t, start, d))
        if k > 0:
            cv2.line(img, (int(_mx(m0)), RY), (int(lerp(_mx(m0), _mx(m1), k)), RY), BLACK, w + 6, cv2.LINE_AA)
            cv2.line(img, (int(_mx(m0)), RY), (int(lerp(_mx(m0), _mx(m1), k)), RY), col, w, cv2.LINE_AA)
        return k

    order = [1948, 1958, 1962, 1970, 1972]
    done = [y for y in order if y < stage]
    if stage >= 1948:
        k = seg(0, 0.9, t0 if stage == 1948 else -5)
        if stage == 1948:
            label(img, "1948 · MENOS DE UNA MILLA", _mx(0.6), RY + 210, ease_out(prog(t, t0 + 0.8, 0.4)), 46, YELLOW, anchor="l")
            label(img, "Y DESPUÉS, NADA", W / 2, 900, ease_out(prog(t, nothing_t if nothing_t is not None else t0 + 2.4, 0.4)), 58, WHITE)
    if stage >= 1958:
        seg(27.0, 30, t0 if stage == 1958 else -5, col=(210, 210, 200))
        if stage == 1958:
            label(img, "1958 · EL ESTADO, HASTA EL PARQUE", _mx(27.5), RY + 210, ease_out(prog(t, t0 + 0.8, 0.4)), 46, WHITE, anchor="r")
    if stage >= 1962:
        seg(24.0, 27.0, t0 if stage == 1962 else -5, d=2.0)
        if stage == 1962:
            label(img, "1960 · OBRAS DENTRO DEL PARQUE", _mx(25.5), RY + 210, ease_out(prog(t, t0 + 0.8, 0.4)), 46, YELLOW, anchor="r")
    if stage >= 1970:
        seg(21.0, 24.0, t0 if stage == 1970 else -5, d=1.6)
        tk = ease_back(prog(t, t0 + 1.4 if stage == 1970 else -5, 0.4))
        if tk > 0:
            x = _mx(21.0)
            cv2.rectangle(img, (int(x - 22 * tk), int(RY - 30 * tk)), (int(x + 22 * tk), int(RY + 30 * tk)), BLACK, -1)
            cv2.ellipse(img, (int(x), int(RY + 30 * tk)), (int(16 * tk), int(40 * tk)), 0, 180, 360, YELLOW, -1, cv2.LINE_AA)
            label(img, "TÚNEL · 1970", x, RY - 70, tk, 44, YELLOW)
        if stage == 1970:
            label(img, "PUENTE DE NOLAND CREEK", _mx(22.5), RY + 210, ease_out(prog(t, t0 + 0.6, 0.4)), 42, WHITE)
    if stage >= 1972:
        k = ease_io(prog(t, t0, 1.6))
        if k > 0:
            for m in np.arange(1.2, 20.8, 0.8):
                if m / 21.0 < k:
                    cv2.line(img, (int(_mx(m)), RY), (int(_mx(m + 0.4)), RY), RED, 8, cv2.LINE_AA)
        label(img, "1972 · LA OBRA SE PARA", W / 2, 820, ease_out(prog(t, t0 + 0.4, 0.4)), 60, RED)
        label(img, "≈ 6 MILLAS HECHAS · MÁS DE 20 POR HACER", W / 2, 900, ease_out(prog(t, t0 + 1.4, 0.4)), 48, WHITE)
    label(img, "ESQUEMA", W - 130, H - 46, 0.6, 30, GREY)
    return img


# =================================================================== money
def check(t, dur, mode="check"):
    """Recreated $52 million settlement and the trust fund that can only spend its interest."""
    img = background("dark_grid", t)
    if mode == "check":
        cw, ch = 1500, 640
        k = ease_out(prog(t, 0.0, 0.7))
        card = np.full((ch, cw, 3), (226, 236, 222), np.uint8)
        for y in range(0, ch, 6):
            cv2.line(card, (0, y), (cw, y), (214, 226, 210), 1)
        cv2.rectangle(card, (14, 14), (cw - 14, ch - 14), (120, 150, 120), 3)

        def tx(s, x, y, size, col=INK, f="type", anchor="l"):
            sp = text_sprite(s, f, size, col, False)
            over(card, sp, (x if anchor == "l" else x - sp.w) - 24, y - sp.h / 2)

        tx("6 DE FEBRERO DE 2010 · BRYSON CITY", cw - 60, 70, 34, INK, "type", "r")
        tx("PÁGUESE A:", 60, 180, 34, (90, 90, 90))
        tx("CONDADO DE SWAIN, CAROLINA DEL NORTE", 300, 180, 44, INK)
        cv2.line(card, (300, 210), (cw - 60, 210), (120, 120, 120), 1)
        nk = ease_out(prog(t, 0.6, 1.4))
        tx(f"$ {int(52_000_000 * nk):,}.00", cw - 60, 300, 70, INK, "mono", "r")
        tx("CINCUENTA Y DOS MILLONES DE DÓLARES", 60, 390, 40, INK)
        cv2.line(card, (60, 420), (cw - 60, 420), (120, 120, 120), 1)
        tx("CONCEPTO: EN LUGAR DE LA CARRETERA PROMETIDA EN 1943", 60, 520, 32, (90, 90, 90))
        sk = ease_io(prog(t, 2.0, 0.9))
        if sk > 0:
            xs = np.linspace(0, 1, 90)
            sig = np.stack([980 + 380 * xs, 560 - 28 * np.sin(xs * 21) * np.exp(-xs * 1.4) - 14 * xs], 1)
            aa_poly(card, partial_line(sig, sk), (30, 40, 110), 3)
        from engine import Sprite
        sp = Sprite(np.dstack([card, np.full(card.shape[:2], 255, np.uint8)]))
        over_center(img, sp, W / 2, H / 2 + 10, k, lerp(0.92, 1.0, k))
        label(img, "RECREACIÓN", W - 150, H - 46, 0.75, 30, GREY)
        return img
    # vault: the 52 million stays put; only the interest comes out
    vx, vy = 700, 560
    cv2.rectangle(img, (vx - 260, vy - 260), (vx + 260, vy + 260), (70, 74, 82), -1)
    cv2.rectangle(img, (vx - 260, vy - 260), (vx + 260, vy + 260), (120, 124, 132), 6)
    cv2.circle(img, (vx + 150, vy), 60, (120, 124, 132), 6, cv2.LINE_AA)
    ang = t * 40
    for a in range(0, 360, 60):
        cv2.line(img, (vx + 150, vy), (int(vx + 150 + 50 * math.cos(math.radians(a + ang))), int(vy + 50 * math.sin(math.radians(a + ang)))),
                 (150, 154, 160), 4, cv2.LINE_AA)
    label(img, "$52 MILLONES", vx - 40, vy - 40, 1.0, 78, YELLOW)
    label(img, "GUARDADOS", vx - 40, vy + 40, 1.0, 50, WHITE)
    # interest dripping out
    for i in range(6):
        ph = ((t * 0.5 + i / 6.0) % 1.0)
        x = lerp(vx + 280, 1500, ph)
        y = vy + 200 - 120 * math.sin(math.pi * ph)
        cv2.circle(img, (int(x), int(y)), 22, (230, 190, 60), -1, cv2.LINE_AA)
        cv2.circle(img, (int(x), int(y)), 22, (170, 130, 30), 3, cv2.LINE_AA)
    label(img, "SOLO LOS INTERESES", 1480, 380, ease_out(prog(t, 0.6, 0.4)), 56, WHITE)
    label(img, "≈ $1 MILLÓN AL AÑO", 1480, 460, ease_out(prog(t, 1.0, 0.4)), 64, YELLOW)
    label(img, "ESCUELAS · SEGURIDAD", 1480, 860, ease_out(prog(t, 1.6, 0.4)), 46, GREY)
    return img


def bars(t, dur, items, title=None, unit=None, log=False, t0=0.3, step=0.9):
    """Horizontal bars: items = [(label, value, value_text, color)]."""
    img = background("dark_grid", t)
    vmax = max(v for _, v, _, _ in items)
    n = len(items)
    y0 = 560 - (n - 1) * 120
    for i, (lab, v, vt, col) in enumerate(items):
        k = ease_out(prog(t, t0 + i * step, 1.0))
        if k <= 0:
            continue
        y = y0 + i * 240
        wbar = 1300 * (v / vmax) * k
        label(img, lab, 180, y - 64, 1.0, 46, WHITE, anchor="l")
        cv2.rectangle(img, (180, int(y - 30)), (int(180 + max(wbar, 6)), int(y + 30)), col, -1)
        label(img, vt, int(180 + max(wbar, 6)) + 40, y, k, 64, col, anchor="l")
    if title:
        label(img, title, W / 2, 120, ease_out(prog(t, 0.1, 0.4)), 60, WHITE)
    if unit:
        label(img, unit, W / 2, H - 70, 0.7, 34, GREY)
    return img


# =================================================================== headstone illustration
def headstone(t, dur):
    img = _sky(t, (14, 16, 20), (30, 34, 38))
    fill_poly(img, [[0, 860], [W, 820], [W, H], [0, H]], (34, 46, 34))
    k = ease_out(prog(t, 0.2, 0.8))
    x, y, s = W / 2, 880, 330
    ang = np.linspace(math.pi, 0, 24)
    top = np.stack([x + np.cos(ang) * s * 0.5, y - s * 1.1 - np.sin(ang) * s * 0.5], 1)
    pts = np.vstack([[x - s * 0.5, y], top, [x + s * 0.5, y]])
    c, sn = math.cos(math.radians(-7)), math.sin(math.radians(-7))
    pts = (pts - [x, y]) @ np.array([[c, -sn], [sn, c]]).T + [x, y]
    _poly(img, pts, (150, 148, 140), k)
    if k > 0.5:
        label(img, "1 · FEB · 1924", x - 10, y - 300, prog(t, 0.8, 0.5), 54, (60, 58, 54))
        label(img, "1 · FEB · 1924", x - 18, y - 220, prog(t, 1.1, 0.5), 54, (60, 58, 54))
    label(img, "NACIÓ Y MURIÓ EL MISMO DÍA", W / 2, 130, ease_out(prog(t, 1.4, 0.4)), 62, WHITE)
    label(img, "SU NOMBRE, MAL ESCRITO EN LA PIEDRA", W / 2, 210, ease_out(prog(t, 2.2, 0.4)), 46, YELLOW)
    label(img, "ILUSTRACIÓN", W - 150, H - 46, 0.7, 30, GREY)
    return img


# =================================================================== year card ("1943 – ?")
def year_q(t, dur, start="1943", q_t=1.0):
    img = background("black", t)
    a = ease_out(prog(t, 0.1, 0.5))
    label(img, start, W / 2 - 300, H / 2, a, 260, WHITE)
    label(img, "–", W / 2, H / 2, ease_out(prog(t, 0.5, 0.4)), 220, GREY)
    k = ease_back(prog(t, q_t, 0.5))
    if k > 0:
        pulse = 1.0 + 0.06 * math.sin(t * 5)
        sp = text_sprite("?", "bebas", int(300 * k * pulse), YELLOW, True)
        over_center(img, sp, W / 2 + 280, H / 2, 1.0)
    return img
