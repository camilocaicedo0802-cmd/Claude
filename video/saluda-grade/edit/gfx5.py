"""Donner Pass diagrams: flashlight in the tunnel, snow depth, the Donner party, Summit Tunnel No. 6 in section
(four headings, the shaft, the meeting, the 1925 tunnel), hand drilling, daily progress, wages, snow corridors,
snowshed section, the payroll, the storm count."""
import functools
import math

import cv2
import numpy as np

from engine import (BLACK, H, RED, W, WHITE, YELLOW, clamp, ease_back, ease_in, ease_io, ease_out, lerp, over,
                    over_center, prog, rounded_rect_sprite, text_sprite)
from gfx import background
from gfx2 import GREY, ROCK, aa_poly, fill_poly, label, partial_line

SNOW = (232, 238, 246)
SKY0, SKY1 = (16, 22, 32), (40, 52, 68)
GRANITE = (78, 76, 72)
STEEL = (150, 160, 170)


@functools.lru_cache(maxsize=2)
def _sky():
    g = np.linspace(0, 1, H)[:, None, None]
    img = (np.array(SKY0) * (1 - g) + np.array(SKY1) * g).astype(np.uint8)
    return np.repeat(img, W, axis=1)


# ------------------------------------------------------------------ flashlight (overlay on a photo)
@functools.lru_cache(maxsize=1)
def _grid():
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    return xx * 4, yy * 4


def flashlight(img, t, dur, path=((0.3, 0.55), (0.7, 0.45)), r=420, amb=0.08, t0=0.0, wobble=1.0):
    """Darken the frame except a soft moving beam (a person exploring with a torch)."""
    k = ease_io(prog(t, t0, max(dur - t0, 0.1)))
    pts = np.array(path, np.float32)
    seg = k * (len(pts) - 1)
    i = min(int(seg), len(pts) - 2)
    f = seg - i
    x = (pts[i, 0] * (1 - f) + pts[i + 1, 0] * f) * W + math.sin(t * 2.3) * 18 * wobble
    y = (pts[i, 1] * (1 - f) + pts[i + 1, 1] * f) * H + math.sin(t * 1.7 + 1) * 12 * wobble
    xx, yy = _grid()
    d2 = ((xx - x) ** 2 + (yy - y) ** 2) / (r * r)
    m = np.exp(-d2 * 1.6) * 1.15 + np.exp(-d2 * 0.35) * 0.25
    m = cv2.resize(np.clip(m, 0, 1.25), (W, H), interpolation=cv2.INTER_LINEAR)
    fade_in = prog(t, 0, 0.35)
    m = amb + (1 - amb) * m
    m = 1 - fade_in + fade_in * m
    warm = np.array([1.04, 1.0, 0.9], np.float32)
    img[:] = np.clip(img.astype(np.float32) * m[..., None] * warm, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ snow depth vs a two-storey house
def snow_depth(t, dur, inches=411, peak=800, peak_t=None, title="NIEVE AL AÑO EN LA CUMBRE"):
    img = _sky().copy()
    base = 930
    px_per_m = 30.0
    cv2.rectangle(img, (0, base), (W, H), (40, 42, 44), -1)
    # house (≈ 7 m) and a person (1.75 m)
    hx = 520
    hh = int(7 * px_per_m)
    fill_poly(img, np.array([[hx - 120, base], [hx - 120, base - hh + 60], [hx, base - hh - 20], [hx + 120, base - hh + 60], [hx + 120, base]]), (70, 58, 50))
    cv2.rectangle(img, (hx - 30, base - 90), (hx + 30, base), (40, 32, 28), -1)
    ph = int(1.75 * px_per_m)
    cv2.circle(img, (700, base - ph + 6), 7, (220, 210, 200), -1, cv2.LINE_AA)
    cv2.line(img, (700, base - ph + 12), (700, base - 18), (220, 210, 200), 5, cv2.LINE_AA)
    cv2.line(img, (700, base - 18), (692, base), (220, 210, 200), 4, cv2.LINE_AA)
    cv2.line(img, (700, base - 18), (708, base), (220, 210, 200), 4, cv2.LINE_AA)
    m_avg = inches * 0.0254
    k = ease_out(prog(t, 0.3, 1.6))
    top = base - m_avg * px_per_m * k
    layer = img.copy()
    cv2.rectangle(layer, (900, int(top)), (1500, base), SNOW, -1)
    img = cv2.addWeighted(layer, 0.92, img, 0.08, 0)
    for m in range(0, 26, 2):
        y = base - m * px_per_m
        cv2.line(img, (1530, int(y)), (1560 if m % 4 == 0 else 1548, int(y)), (160, 160, 160), 2, cv2.LINE_AA)
        if m % 4 == 0:
            label(img, f"{m} M", 1600, y, 0.8, 30, GREY, "l")
    if k > 0.05:
        label(img, f"{int(inches * k)} PULGADAS", 1200, top - 60, 1.0, 70, WHITE)
        label(img, f"≈ {m_avg * k:.1f} M".replace(".", ","), 1200, top - 120, prog(t, 1.4, 0.4), 44, YELLOW)
    if peak and peak_t is not None:
        a = prog(t, peak_t, 0.4)
        if a > 0:
            yp = base - peak * 0.0254 * px_per_m
            for x in range(880, 1520, 30):
                cv2.line(img, (x, int(yp)), (x + 16, int(yp)), RED, 4, cv2.LINE_AA)
            label(img, f"RÉCORD: +{peak} PULGADAS · ≈ 20 M", 1200, yp - 40, a, 46, RED)
    label(img, title, W / 2, 80, prog(t, 0.1, 0.4), 54, WHITE)
    return img


# ------------------------------------------------------------------ 81 emigrants, 45 survivors
def party(t, dur, total=81, survive=45, t_die=1.8):
    img = background("dark_grid", t)
    cols = 27
    sx, sy = 52, 120
    x0 = W / 2 - (cols - 1) * sx / 2
    y0 = 380
    rng = np.random.default_rng(81)
    dead = set(rng.choice(total, total - survive, replace=False).tolist())
    for i in range(total):
        a = ease_out(prog(t, 0.2 + i * 0.012, 0.3))
        if a <= 0:
            continue
        x, y = x0 + (i % cols) * sx, y0 + (i // cols) * sy
        col = WHITE
        if i in dead:
            f = prog(t, t_die + (i % 7) * 0.05, 0.6)
            col = tuple(int(lerp(c0, c1, f)) for c0, c1 in zip(WHITE, (70, 60, 62)))
        cv2.circle(img, (int(x), int(y - 30)), 11, col, -1, cv2.LINE_AA)
        fill_poly(img, np.array([[x - 14, y + 18], [x - 10, y - 14], [x + 10, y - 14], [x + 14, y + 18]]), col)
    label(img, "81 COLONOS", W / 2, 190, prog(t, 0.2, 0.4), 80, WHITE)
    a = prog(t, t_die + 0.6, 0.4)
    if a > 0:
        label(img, "45 SOBREVIVIERON", W / 2, 860, a, 80, YELLOW)
    label(img, "INVIERNO DE 1846", W / 2, 950, prog(t, 0.4, 0.4), 40, GREY)
    return img


# ------------------------------------------------------------------ Summit Tunnel No. 6 in section
X0, X1 = 140, 1780
TY = 760
PX0, PX1 = 480, 1440        # portals (1,659 ft)


@functools.lru_cache(maxsize=2)
def _summit_profile():
    xs = np.linspace(0, W, 420)
    t = np.clip((xs - X0) / (X1 - X0), 0, 1)
    y = 900 - 360 * np.sin(np.pi * t) ** 1.3
    y = np.where((xs < X0) | (xs > X1), 900, y)
    rng = np.random.default_rng(6)
    y += np.convolve(rng.normal(0, 6, len(xs)), np.ones(9) / 9, mode="same") * (y < 899)
    return xs, y


@functools.lru_cache(maxsize=2)
def _summit_bg():
    img = background("dark_grid", 0.0).copy()
    xs, ys = _summit_profile()
    fill_poly(img, np.vstack([[0, H], np.stack([xs, ys], 1), [W, H]]), GRANITE)
    rng = np.random.default_rng(3)
    for _ in range(260):  # granite speckle
        x = rng.uniform(X0, X1)
        yt = np.interp(x, xs, ys)
        y = rng.uniform(yt + 6, H)
        cv2.circle(img, (int(x), int(y)), int(rng.integers(2, 5)), (98, 96, 92) if rng.random() < 0.5 else (60, 58, 56), -1, cv2.LINE_AA)
    aa_poly(img, np.stack([xs, ys], 1), (170, 168, 160), 4)
    return img


def _surf(x):
    xs, ys = _summit_profile()
    return float(np.interp(x, xs, ys))


def _bore(img, xa, xb, y=TY, h=16, col=YELLOW, fill=(12, 12, 14)):
    if abs(xb - xa) < 2:
        return
    a, b = sorted((xa, xb))
    cv2.rectangle(img, (int(a), int(y - h)), (int(b), int(y + h)), fill, -1)
    cv2.line(img, (int(a), int(y - h)), (int(b), int(y - h)), col, 3, cv2.LINE_AA)
    cv2.line(img, (int(a), int(y + h)), (int(b), int(y + h)), col, 3, cv2.LINE_AA)


def tunnel6(t, dur, mode="plan"):
    """modes: plan, fronts, shaft, meet, depth, two."""
    img = _summit_bg().copy()
    mid = (PX0 + PX1) / 2 + 40
    top = _surf(mid)
    if mode == "plan":
        k = ease_io(prog(t, 0.3, 1.6))
        _bore(img, PX0, lerp(PX0, PX1, k))
        a = prog(t, 1.8, 0.4)
        cv2.line(img, (PX0, TY + 70), (PX1, TY + 70), YELLOW, 2, cv2.LINE_AA)
        for x in (PX0, PX1):
            cv2.line(img, (x, TY + 58), (x, TY + 82), YELLOW, 2, cv2.LINE_AA)
        label(img, "+1.600 PIES DE GRANITO · ≈ 500 M", (PX0 + PX1) / 2, TY + 120, a, 48, YELLOW)
        label(img, "TÚNEL N.º 6", W / 2, 150, prog(t, 0.2, 0.4), 80, WHITE)
        label(img, "LA CUMBRE, POR DENTRO", W / 2, 230, prog(t, 0.6, 0.4), 44, GREY)
    elif mode in ("fronts", "shaft"):
        k = ease_io(prog(t, 0.6 if mode == "fronts" else 2.2, max(dur - 1.4, 1.0)))
        reach = (mid - PX0) * 0.42 * k
        _bore(img, PX0, PX0 + reach)
        _bore(img, PX1, PX1 - reach)
        ks = ease_io(prog(t, 0.4, 1.4)) if mode == "shaft" else ease_io(prog(t, 1.2, 1.2))
        sy = lerp(top, TY, ks)
        cv2.rectangle(img, (int(mid - 22), int(top)), (int(mid + 22), int(sy)), (12, 12, 14), -1)
        cv2.line(img, (int(mid - 22), int(top)), (int(mid - 22), int(sy)), YELLOW, 3, cv2.LINE_AA)
        cv2.line(img, (int(mid + 22), int(top)), (int(mid + 22), int(sy)), YELLOW, 3, cv2.LINE_AA)
        if ks >= 0.999:
            _bore(img, mid - reach * 0.5, mid + reach * 0.5)
        # headings arrows
        heads = [(PX0 + reach, 1), (PX1 - reach, -1)]
        if ks >= 0.999:
            heads += [(mid - reach * 0.5, -1), (mid + reach * 0.5, 1)]
        for i, (x, d) in enumerate(heads):
            cv2.arrowedLine(img, (int(x - d * 10), TY), (int(x + d * 50), TY), WHITE, 5, cv2.LINE_AA, tipLength=0.4)
            label(img, str(i + 1), x + d * 20, TY - 60, prog(t, 0.6 + i * 0.3, 0.3), 54, YELLOW)
        if mode == "fronts":
            label(img, "4 FRENTES A LA VEZ", W / 2, 150, prog(t, 0.2, 0.4), 74, WHITE)
        else:
            # shaft house + locomotive Sacramento
            hx, hy = mid, top - 6
            fill_poly(img, np.array([[hx - 90, hy], [hx - 90, hy - 70], [hx, hy - 120], [hx + 90, hy - 70], [hx + 90, hy]]), (110, 82, 56))
            cv2.rectangle(img, (int(hx + 100), int(hy - 40)), (int(hx + 190), int(hy)), (40, 40, 44), -1)
            cv2.rectangle(img, (int(hx + 160), int(hy - 70)), (int(hx + 178), int(hy - 40)), (40, 40, 44), -1)
            cv2.circle(img, (int(hx + 120), int(hy)), 10, (90, 90, 90), -1, cv2.LINE_AA)
            cv2.circle(img, (int(hx + 170), int(hy)), 10, (90, 90, 90), -1, cv2.LINE_AA)
            puff = (t * 0.8) % 1
            cv2.circle(img, (int(hx + 169), int(hy - 80 - 40 * puff)), int(8 + 18 * puff), (200, 200, 200), 2, cv2.LINE_AA)
            label(img, "POZO DE 8 × 12 PIES", mid - 40, top + 60, prog(t, 0.8, 0.4), 44, YELLOW, "r")
            label(img, "≈ 2,5 × 3,5 M", mid - 40, top + 110, prog(t, 1.0, 0.4), 34, GREY, "r")
            label(img, "LA «SACRAMENTO» · 12 TONELADAS", hx + 140, hy - 150, prog(t, 1.4, 0.4), 40, WHITE)
            label(img, "EL POZO DEL MEDIO", W / 2, 120, prog(t, 0.2, 0.4), 64, WHITE)
    elif mode == "meet":
        k = ease_in(prog(t, 0.3, max(dur - 1.6, 1.0)))
        q1, q3 = (PX0 + mid) / 2, (mid + PX1) / 2
        _bore(img, PX0, lerp(PX0, q1, k))
        _bore(img, lerp(mid, q1, k), mid)
        _bore(img, mid, lerp(mid, q3, k))
        _bore(img, lerp(PX1, q3, k), PX1)
        cv2.rectangle(img, (int(mid - 22), int(top)), (int(mid + 22), int(TY)), (12, 12, 14), -1)
        if k >= 0.999:
            f = prog(t, 0.3 + max(dur - 1.6, 1.0), 0.6)
            for qx in (q1, q3):
                layer = img.copy()
                cv2.circle(layer, (int(qx), TY), int(20 + 160 * f), YELLOW, 5, cv2.LINE_AA)
                img = cv2.addWeighted(layer, 1 - f, img, f, 0)
            a = prog(t, 0.6 + max(dur - 1.6, 1.0), 0.4)
            label(img, "ERROR: 2 PULGADAS · ≈ 5 CM", W / 2, TY + 130, a, 60, YELLOW)
        label(img, "AGOSTO DE 1867", W / 2, 150, prog(t, 0.2, 0.4), 74, WHITE)
    elif mode == "depth":
        _bore(img, PX0, PX1)
        a = prog(t, 0.4, 0.5)
        x = mid
        cv2.line(img, (int(x), int(top + 6)), (int(x), TY - 18), YELLOW, 3, cv2.LINE_AA)
        for yy in (top + 6, TY - 18):
            cv2.line(img, (int(x - 14), int(yy)), (int(x + 14), int(yy)), YELLOW, 3, cv2.LINE_AA)
        label(img, "124 PIES DE ROCA · ≈ 38 M", x + 30, (top + TY) / 2, a, 48, YELLOW, "l")
        cv2.line(img, (PX0, TY + 70), (PX1, TY + 70), WHITE, 2, cv2.LINE_AA)
        label(img, "1.659 PIES · ≈ 506 M", (PX0 + PX1) / 2, TY + 115, prog(t, 0.9, 0.4), 52, WHITE)
        label(img, "TÚNEL N.º 6", W / 2, 150, prog(t, 0.2, 0.4), 74, WHITE)
    elif mode == "two":
        _bore(img, PX0, PX1, col=(150, 150, 150))
        label(img, "1868 · VÍA VIEJA", (PX0 + PX1) / 2, TY - 60, prog(t, 0.2, 0.4), 40, GREY)
        k = ease_io(prog(t, 0.8, 1.6))
        y2 = 870
        _bore(img, 0, lerp(0, W, k), y=y2, h=18, col=YELLOW)
        if k > 0.3:
            ph = (t * 0.25) % 1
            cv2.circle(img, (int(lerp(-40, W + 40, ph)), y2), 12, WHITE, -1, cv2.LINE_AA)
        label(img, "1925 · TÚNEL NUEVO: 10.322 PIES · CASI 2 MILLAS", W / 2, y2 + 80, prog(t, 1.6, 0.4), 46, YELLOW)
        label(img, "DOS VÍAS: UNA POR ARRIBA, OTRA POR ABAJO", W / 2, 150, prog(t, 2.4, 0.4), 58, WHITE)
    return img


# ------------------------------------------------------------------ hand drilling + blast
def hand_drill(t, dur):
    img = background("dark_grid", t)
    fill_poly(img, np.array([[0, 560], [W, 560], [W, H], [0, H]]), GRANITE)
    rng = np.random.default_rng(9)
    for _ in range(140):
        cv2.circle(img, (int(rng.uniform(0, W)), int(rng.uniform(570, H))), int(rng.integers(2, 5)), (100, 98, 94), -1, cv2.LINE_AA)
    cx = 960
    phase = min(t, 4.2)
    depth = 20 + 160 * prog(t, 0.2, 3.8)
    blast = prog(t, 5.6, 0.1)
    if t < 4.2:
        # steel
        rot = (t * 3.0) % 1
        cv2.rectangle(img, (cx - 16, int(560 - 300 + depth)), (cx + 16, int(560 + depth)), STEEL, -1)
        for k in range(4):
            yy = 560 - 280 + depth + ((k / 4 + rot) % 1) * 280
            cv2.line(img, (cx - 16, int(yy)), (cx + 16, int(yy - 14)), (110, 118, 126), 3, cv2.LINE_AA)
        # hammer swing
        sw = (t * 1.6) % 1
        ang = math.radians(-80 + 75 * ease_in(min(sw / 0.6, 1)) if sw < 0.6 else -5 - 75 * ease_out((sw - 0.6) / 0.4))
        pivot = (cx + 380, 200)
        L = 420
        hx, hy = pivot[0] + L * math.cos(math.pi + ang), pivot[1] + L * math.sin(math.pi + ang)
        cv2.line(img, pivot, (int(hx), int(hy)), (150, 110, 70), 16, cv2.LINE_AA)
        cv2.rectangle(img, (int(hx - 55), int(hy - 32)), (int(hx + 55), int(hy + 32)), (60, 62, 66), -1)
        if sw > 0.58 and sw < 0.68:
            for k in range(8):
                a = rng.uniform(-math.pi, 0)
                cv2.line(img, (cx, int(560 - 300 + depth)), (int(cx + 80 * math.cos(a)), int(560 - 300 + depth + 80 * math.sin(a))), YELLOW, 3, cv2.LINE_AA)
        label(img, "GOLPE · GIRO · GOLPE", W / 2, 160, prog(t, 0.3, 0.4), 64, WHITE)
        label(img, "UN AGUJERO DE UN PAR DE PULGADAS", W / 2, 230, prog(t, 1.2, 0.4), 40, GREY)
    else:
        cv2.rectangle(img, (cx - 20, 560), (cx + 20, int(560 + depth)), (20, 20, 22), -1)
        kp = prog(t, 4.3, 0.6)
        cv2.rectangle(img, (cx - 20, int(560 + depth - (depth - 10) * kp)), (cx + 20, int(560 + depth)), (60, 56, 50), -1)
        if t > 4.9:
            fuse = np.array([[cx, 560], [cx + 60, 500], [cx + 180, 530], [cx + 320, 460]], float)
            burn = prog(t, 4.9, 0.8)
            aa_poly(img, partial_line(fuse, 1 - burn), (200, 180, 140), 5)
            p = partial_line(fuse, 1 - burn)[-1]
            cv2.circle(img, (int(p[0]), int(p[1])), int(12 + 6 * math.sin(t * 40)), (255, 200, 80), -1, cv2.LINE_AA)
        label(img, "PÓLVORA NEGRA · MECHA · ¡TODOS CORREN!", W / 2, 160, prog(t, 4.3, 0.4), 58, WHITE)
        if blast > 0:
            f = prog(t, 5.6, 1.0)
            r = 80 + 900 * ease_out(f)
            xx, yy = np.meshgrid(np.arange(0, W, 4), np.arange(0, H, 4))
            d = np.sqrt((xx - cx) ** 2 + (yy - 560) ** 2) / r
            m = np.clip(1 - d, 0, 1) ** 1.5 * (1 - f) * 1.2
            m = cv2.resize(m.astype(np.float32), (W, H))
            glow = np.array([255, 214, 150], np.float32)
            img = np.clip(img * (1 - m[..., None]) + glow * m[..., None], 0, 255).astype(np.uint8)
            rng2 = np.random.default_rng(12)
            for _ in range(60):
                a = rng2.uniform(-math.pi, 0); v = rng2.uniform(300, 1100)
                x = cx + math.cos(a) * v * f; y = 560 + math.sin(a) * v * f + 600 * f * f
                cv2.circle(img, (int(x), int(y)), int(rng2.integers(3, 9)), (90, 86, 80), -1, cv2.LINE_AA)
    return img


# ------------------------------------------------------------------ progress per day vs a ruler
def progress_bars(t, dur, items=(("PÓLVORA NEGRA", 14, 0.4), ("NITROGLICERINA", 22, None)), title="AVANCE POR FRENTE Y POR DÍA"):
    img = background("dark_grid", t)
    px_in = 26
    x0 = 420
    for i, (name, inches, at) in enumerate(items):
        if at is None:
            continue
        y = 440 + i * 230
        k = ease_out(prog(t, at, 1.2))
        cv2.rectangle(img, (x0, y), (int(x0 + inches * px_in * k), y + 80), YELLOW if i else (200, 200, 200), -1)
        for j in range(0, inches + 1):
            xx = x0 + j * px_in
            if xx <= x0 + inches * px_in * k:
                cv2.line(img, (xx, y + 80), (xx, y + (60 if j % 6 else 48)), (30, 30, 30), 2)
        label(img, name, x0 - 30, y + 40, prog(t, at, 0.3), 46, WHITE, "r")
        cm = round(inches * 2.54)
        label(img, f"{int(inches * k)} PULGADAS · ≈ {int(cm * k)} CM", x0 + inches * px_in * k + 30, y + 40, prog(t, at + 0.6, 0.3), 46,
              YELLOW if i else WHITE, "l")
    label(img, title, W / 2, 200, prog(t, 0.1, 0.4), 60, WHITE)
    return img


def set_progress_items(*items):
    def fn(t, dur):
        return progress_bars(t, dur, items)
    return fn


# ------------------------------------------------------------------ wages card
def wages(t, dur, t2=2.4):
    img = background("dark_grid", t)
    cards = [("TRABAJADOR CHINO", ["$26 AL MES", "6 DÍAS A LA SEMANA", "LA COMIDA, DE SU BOLSILLO"], 0.3, YELLOW),
             ("TRABAJADOR BLANCO", ["LA COMPAÑÍA", "LE DABA DE COMER"], t2, (200, 200, 200))]
    for i, (head, lines, at, col) in enumerate(cards):
        a = ease_out(prog(t, at, 0.4))
        if a <= 0:
            continue
        cx = W / 2 + (i - 0.5) * 760
        card = rounded_rect_sprite(640, 560, (30, 32, 36), 18, 255, 3, col)
        over_center(img, card, cx, 560, a, lerp(0.9, 1.0, ease_back(prog(t, at, 0.4))))
        label(img, head, cx, 340, a, 54, col)
        for j, ln in enumerate(lines):
            label(img, ln, cx, 480 + j * 90, prog(t, at + 0.3 + j * 0.3, 0.3), 56 if j == 0 else 42, WHITE)
    return img


# ------------------------------------------------------------------ snow corridors between barracks and tunnel
def snow_corridor(t, dur, depth_ft=18):
    img = _sky().copy()
    ground = 900
    snow_top = ground - depth_ft * 0.3048 * 55
    cv2.rectangle(img, (0, ground), (W, H), (44, 44, 46), -1)
    fill_poly(img, np.array([[1350, ground], [1350, 380], [1650, 300], [W, 330], [W, ground]]), GRANITE)
    cv2.rectangle(img, (1350, ground - 140), (1430, ground), (12, 12, 14), -1)
    label(img, "TÚNEL", 1395, ground - 170, 0.9, 36, GREY)
    for bx in (220, 520):
        cv2.rectangle(img, (bx, ground - 120), (bx + 200, ground), (110, 82, 56), -1)
        fill_poly(img, np.array([[bx - 10, ground - 120], [bx + 100, ground - 180], [bx + 210, ground - 120]]), (90, 66, 46))
    k = ease_out(prog(t, 0.2, 1.4))
    st = lerp(ground, snow_top, k)
    layer = img.copy()
    cv2.rectangle(layer, (0, int(st)), (1350, ground), SNOW, -1)
    img = cv2.addWeighted(layer, 0.82, img, 0.18, 0)
    # corridor
    kc = ease_io(prog(t, 1.4, 1.4))
    x_end = lerp(420, 1350, kc)
    cv2.rectangle(img, (420, ground - 110), (int(x_end), ground), (60, 70, 84), -1)
    if kc >= 1:
        f = ((t - 2.8) * 0.18) % 1
        x = lerp(430, 1340, f)
        cv2.circle(img, (int(x), ground - 70), 9, YELLOW, -1, cv2.LINE_AA)
        cv2.line(img, (int(x), ground - 60), (int(x), ground - 25), YELLOW, 5, cv2.LINE_AA)
    a = prog(t, 1.2, 0.4)
    cv2.line(img, (60, int(snow_top)), (60, ground), YELLOW, 3, cv2.LINE_AA)
    label(img, f"≈ {depth_ft} PIES · +5 M", 90, snow_top + 40, a, 46, YELLOW, "l")
    label(img, "PASILLOS POR DEBAJO DE LA NIEVE", W / 2, 120, prog(t, 1.6, 0.4), 60, WHITE)
    return img


# ------------------------------------------------------------------ storms counter
def storms(t, dur, n=44, every=0.06, title="INVIERNO DE 1866–1867"):
    img = background("dark_grid", t)
    cols = 11
    for i in range(n):
        a = ease_out(prog(t, 0.4 + i * every, 0.25))
        if a <= 0:
            continue
        x = W / 2 + (i % cols - (cols - 1) / 2) * 120
        y = 360 + (i // cols) * 120
        s = 34 * a
        for k in range(3):
            ang = math.radians(k * 60)
            cv2.line(img, (int(x - s * math.cos(ang)), int(y - s * math.sin(ang))), (int(x + s * math.cos(ang)), int(y + s * math.sin(ang))),
                     SNOW, 4, cv2.LINE_AA)
    shown = int(clamp((t - 0.4) / every + 1, 0, n))
    label(img, f"{shown} TORMENTAS", W / 2, 880, prog(t, 0.4, 0.3), 96, YELLOW)
    label(img, title, W / 2, 180, prog(t, 0.1, 0.4), 56, WHITE)
    return img


# ------------------------------------------------------------------ snowshed section
def snowshed(t, dur):
    img = _sky().copy()
    # slope
    fill_poly(img, np.array([[0, 360], [W, 820], [W, H], [0, H]]), GRANITE)
    ys = lambda x: 360 + (820 - 360) * x / W
    # shed on a bench cut into the slope
    sx0, sx1, sb = 760, 1240, 800
    fill_poly(img, np.array([[sx0 - 40, sb], [sx1 + 200, sb], [sx1 + 200, H], [sx0 - 40, H]]), GRANITE)
    k = ease_out(prog(t, 0.2, 1.0))
    if k > 0:
        roof = np.array([[sx0, sb], [sx0, ys(sx0)], [sx1, ys(sx1)], [sx1, sb]])
        fill_poly(img, roof, (120, 88, 58))
        for x in range(sx0 + 20, sx1, 60):
            cv2.line(img, (x, sb), (x, int(ys(x))), (80, 58, 38), 6, cv2.LINE_AA)
        aa_poly(img, np.array([[sx0 - 20, ys(sx0 - 20)], [sx1 + 20, ys(sx1 + 20)]]), (70, 50, 34), 10)
        cv2.rectangle(img, (sx0 + 20, sb - 110), (sx1 - 20, sb - 4), (24, 22, 20), -1)
    # train inside
    if t > 1.0:
        f = ((t - 1.0) * 0.35) % 1
        tx = lerp(sx0 - 400, sx1 + 400, f)
        x_a, x_b = max(sx0 + 22, tx - 160), min(sx1 - 22, tx + 160)
        if x_b > x_a:
            cv2.rectangle(img, (int(x_a), sb - 80), (int(x_b), sb - 14), (200, 120, 50), -1)
    # snow sliding over
    rng = np.random.default_rng(5)
    for i in range(70):
        ph = ((t * 0.5 + rng.uniform(0, 1)) % 1)
        x = lerp(80, 1700, ph)
        y = ys(x) - 12 - rng.uniform(0, 30)
        cv2.circle(img, (int(x), int(y)), int(rng.integers(5, 11)), SNOW, -1, cv2.LINE_AA)
    label(img, "LA NIEVE RESBALA POR ENCIMA", 600, 240, prog(t, 0.8, 0.4), 52, WHITE)
    label(img, "EL TREN PASA POR DEBAJO", (sx0 + sx1) / 2, sb + 70, prog(t, 1.4, 0.4), 46, YELLOW)
    label(img, "SNOWSHEDS · COBERTIZOS DE MADERA", W / 2, 90, prog(t, 0.1, 0.4), 56, WHITE)
    return img


# ------------------------------------------------------------------ the payroll (recreation)
def payroll(t, dur, hl_t=3.0):
    img = background("dark_grid", t)
    pw, ph = 1320, 900
    px, py = W / 2 - pw / 2, 90
    paper = rounded_rect_sprite(pw, ph, (232, 224, 204), 4, 255)
    over_center(img, paper, W / 2, py + ph / 2, 1.0, lerp(1.04, 1.0, ease_out(prog(t, 0, 1.0))))
    ink = (40, 34, 30)
    heads = [("CUADRILLA", 90), ("A NOMBRE DE", 330), ("HOMBRES", 820), ("PAGO", 1060)]
    for txt, x in heads:
        sp = text_sprite(txt, "type", 34, ink, False)
        over(img, sp, px + x, py + 70, prog(t, 0.2, 0.3))
    cv2.line(img, (int(px + 70), int(py + 140)), (int(px + pw - 70), int(py + 140)), ink, 2)
    rows = [("N.º 1", "CAPATAZ", "30", "$780"), ("N.º 2", "CONTRATISTA", "35", "$910"), ("N.º 3", "JOHN CHINAMAN", "40", "$1.040"),
            ("N.º 4", "JOHN CHINAMAN", "32", "$832"), ("N.º 5", "CAPATAZ", "38", "$988"), ("N.º 6", "JOHN CHINAMAN", "30", "$780")]
    for i, row in enumerate(rows):
        a = prog(t, 0.6 + i * 0.3, 0.3)
        if a <= 0:
            continue
        y = py + 180 + i * 100
        for (txt, x), (_, hx) in zip(zip(row, [90, 330, 840, 1060]), heads):
            sp = text_sprite(txt, "type", 40, ink, False)
            over(img, sp, px + x, y, a)
        if row[1] == "JOHN CHINAMAN":
            k = prog(t, hl_t, 0.4)
            if k > 0:
                layer = img.copy()
                cv2.rectangle(layer, (int(px + 320), int(y + 6)), (int(px + 320 + 420 * k), int(y + 70)), (255, 214, 60), -1)
                img = cv2.addWeighted(layer, 0.45, img, 0.55, 0)
    label(img, "RECREACIÓN", W - 150, H - 50, 0.8, 30, GREY)
    return img


# ------------------------------------------------------------------ "the photo" highlight: no Chinese worker in it
def missing(img, t, dur, t0=0.6, text="NI UN SOLO TRABAJADOR CHINO"):
    a = ease_out(prog(t, t0, 0.4))
    if a <= 0:
        return
    layer = img.copy()
    cv2.rectangle(layer, (0, int(H * 0.78)), (W, int(H * 0.92)), (12, 12, 14), -1)
    img[:] = cv2.addWeighted(layer, 0.75 * a, img, 1 - 0.75 * a, 0)
    label(img, text, W / 2, H * 0.85, a, 64, YELLOW)
