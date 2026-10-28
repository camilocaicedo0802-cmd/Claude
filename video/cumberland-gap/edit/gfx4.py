"""Cumberland Gap diagrams: the notch in the wall, the two roads stacked in the pass, the tunnel (pilot bore,
meeting crews, twin tubes), erasing the old road, brake heat, the 40-year timeline, calendar, cost bars."""
import functools
import math

import cv2
import numpy as np

from engine import (BLACK, H, RED, W, WHITE, YELLOW, clamp, ease_back, ease_in, ease_io, ease_out, lerp, over,
                    over_center, prog, rounded_rect_sprite, text_sprite)
from gfx import background
from gfx2 import GREY, ROCK, aa_poly, fill_poly, label, partial_line

DIRT = (150, 112, 70)
GREEN = (70, 120, 64)
WATER = (90, 160, 220)
SKY0, SKY1 = (18, 24, 32), (44, 56, 70)


@functools.lru_cache(maxsize=2)
def _sky():
    g = np.linspace(0, 1, H)[:, None, None]
    img = (np.array(SKY0) * (1 - g) + np.array(SKY1) * g).astype(np.uint8)
    return np.repeat(img, W, axis=1)


def _tree(img, x, y, s, col=GREEN, a=1.0):
    if a <= 0.02:
        return
    s = s * a
    pts = np.array([[x, y - 2.4 * s], [x - s, y], [x + s, y]])
    fill_poly(img, pts, col)
    pts = np.array([[x, y - 3.3 * s], [x - 0.75 * s, y - 1.4 * s], [x + 0.75 * s, y - 1.4 * s]])
    fill_poly(img, pts, tuple(min(255, c + 18) for c in col))


# ------------------------------------------------------------------ front view: the wall and its notch
@functools.lru_cache(maxsize=2)
def _ridge(seed=3):
    xs = np.linspace(-40, W + 40, 260)
    rng = np.random.default_rng(seed)
    base = 430 + 26 * np.sin(xs / 210.0) + 14 * np.sin(xs / 77.0 + 1.3)
    base += np.convolve(rng.normal(0, 6, len(xs)), np.ones(5) / 5, mode="same")
    return xs, base


def ridge_front(t, dur, mode="notch", title="CUMBERLAND GAP", sub="1.631 PIES  ·  ≈ 500 M"):
    """modes: notch (the wall has a gap), cut (pioneers' notch vs. 20 ft cut), warpath (traffic of people/animals)."""
    img = _sky().copy()
    xs, base = _ridge()
    cx, depth, half = W / 2, 170, 150
    k = ease_io(prog(t, 0.3, 1.0)) if mode == "notch" else 1.0
    notch = depth * k * np.exp(-((xs - cx) / half) ** 2 * 1.6)
    ys = base + notch
    if mode == "cut":
        kc = ease_io(prog(t, 1.0, 1.2))
        ys = ys + 34 * kc * np.exp(-((xs - cx) / (half * 0.55)) ** 4)
    poly = np.vstack([[-40, H + 10], np.stack([xs, ys], 1), [W + 40, H + 10]])
    fill_poly(img, poly, (40, 46, 44))
    # forest texture: rows of small trees following the slope
    rng = np.random.default_rng(7)
    for i in range(420):
        x = rng.uniform(0, W)
        yb = np.interp(x, xs, ys)
        y = yb + rng.uniform(10, 300)
        s = rng.uniform(6, 11)
        _tree(img, x, y, s, (36 + int(rng.uniform(0, 14)), 66 + int(rng.uniform(0, 20)), 46))
    aa_poly(img, np.stack([xs, ys], 1), (120, 128, 118), 3)
    if mode == "notch":
        a = prog(t, 1.2, 0.4)
        yb = np.interp(cx, xs, ys)
        cv2.line(img, (int(cx), int(yb) - 210), (int(cx), int(yb) - 30), YELLOW, 4, cv2.LINE_AA)
        cv2.circle(img, (int(cx), int(yb)), 12, YELLOW, -1, cv2.LINE_AA)
        if a > 0:
            label(img, title, cx, yb - 270, a, 80, WHITE)
            if sub:
                label(img, sub, cx, yb - 200, prog(t, 1.6, 0.4), 52, YELLOW)
        label(img, "LOS APALACHES", 260, 250, prog(t, 0.1, 0.4), 56, GREY)
    elif mode == "cut":
        old = base + notch
        aa_poly(img, np.stack([xs, old], 1)[np.abs(xs - cx) < 260], WHITE, 3)
        yb0, yb1 = np.interp(cx, xs, old), np.interp(cx, xs, ys)
        a = prog(t, 1.6, 0.4)
        if a > 0:
            cv2.line(img, (int(cx + 200), int(yb0)), (int(cx + 200), int(yb1)), YELLOW, 4, cv2.LINE_AA)
            for yy in (yb0, yb1):
                cv2.line(img, (int(cx + 185), int(yy)), (int(cx + 215), int(yy)), YELLOW, 4, cv2.LINE_AA)
            label(img, "−20 PIES  ·  ≈ 6 M", cx + 250, (yb0 + yb1) / 2, a, 56, YELLOW, "l")
        label(img, "EL PASO DE LOS PIONEROS", cx, yb0 - 120, prog(t, 0.3, 0.4), 46, WHITE)
    elif mode == "warpath":
        yb = np.interp(cx, xs, ys)
        for i in range(9):
            f = ((t * 0.16 + i / 9) % 1.0)
            x = lerp(cx - 420, cx + 420, f)
            y = np.interp(x, xs, ys) - 8
            cv2.circle(img, (int(x), int(y)), 8, YELLOW if i % 3 else WHITE, -1, cv2.LINE_AA)
        label(img, "EL CAMINO DE LOS GUERREROS", cx, yb - 200, prog(t, 0.3, 0.5), 66, WHITE)
    return img


# ------------------------------------------------------------------ side cross-section of the pass
X0, X1 = 120, 1800          # extent of the mountain
PX0, PX1 = 520, 1400        # tunnel portals
TY = 800                    # tunnel level


@functools.lru_cache(maxsize=2)
def _pass_profile():
    xs = np.linspace(0, W, 400)
    t = np.clip((xs - X0) / (X1 - X0), 0, 1)
    y = 900 - 520 * np.sin(np.pi * t) ** 1.6
    y = np.where((xs < X0) | (xs > X1), 900, y)
    rng = np.random.default_rng(5)
    y += np.convolve(rng.normal(0, 4, len(xs)), np.ones(9) / 9, mode="same") * (y < 899)
    return xs, y


@functools.lru_cache(maxsize=2)
def _pass_bg():
    img = background("dark_grid", 0.0).copy()
    xs, ys = _pass_profile()
    poly = np.vstack([[0, H], np.stack([xs, ys], 1), [W, H]])
    fill_poly(img, poly, ROCK)
    for k in range(1, 8):
        aa_poly(img, np.stack([xs, np.minimum(ys + k * 52, 1060)], 1), (60, 58, 55), 2)
    aa_poly(img, np.stack([xs, ys], 1), (150, 146, 138), 4)
    cv2.line(img, (0, 900), (W, 900), (90, 90, 90), 2, cv2.LINE_AA)
    return img


def _surface(x0, x1, lift=0.0, n=160):
    xs, ys = _pass_profile()
    sx = np.linspace(x0, x1, n)
    return np.stack([sx, np.interp(sx, xs, ys) - lift], 1)


def _trees_on(img, a, seed=2, x0=X0 + 60, x1=X1 - 60, n=34):
    xs, ys = _pass_profile()
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(x0, x1)
        d = rng.uniform(0, 1)
        _tree(img, x, np.interp(x, xs, ys) - 6, 13 + 5 * d, GREEN, clamp(a * 1.4 - i / n * 0.4))


def _traffic(img, path, t, n=6, speed=0.12, col=WHITE, r=9):
    seg = np.hypot(*np.diff(path, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    for i in range(n):
        d = ((t * speed + i / n) % 1.0) * cum[-1]
        k = min(max(int(np.searchsorted(cum, d)), 1), len(path) - 1)
        p = path[k - 1] + (path[k] - path[k - 1]) * (d - cum[k - 1]) / max(seg[k - 1], 1e-6)
        cv2.circle(img, (int(p[0]), int(p[1])), r, col if i % 4 else RED, -1, cv2.LINE_AA)


def _dashed(img, path, col, th, dash=18, gap=12):
    seg = np.hypot(*np.diff(path, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    on = (cum % (dash + gap)) < dash
    for k in range(len(path) - 1):
        if on[k]:
            cv2.line(img, (int(path[k][0]), int(path[k][1])), (int(path[k + 1][0]), int(path[k + 1][1])), col, th, cv2.LINE_AA)


def _tube(img, x0, x1, y, col_edge=YELLOW, h=22, fill=(14, 14, 16)):
    if x1 - x0 < 2:
        return
    cv2.rectangle(img, (int(x0), int(y - h)), (int(x1), int(y + h)), fill, -1)
    cv2.line(img, (int(x0), int(y - h)), (int(x1), int(y - h)), col_edge, 3, cv2.LINE_AA)
    cv2.line(img, (int(x0), int(y + h)), (int(x1), int(y + h)), col_edge, 3, cv2.LINE_AA)


def pass_section(t, dur, mode="layers"):
    """modes: layers, idea, pilot, meet, open, erase, today."""
    img = _pass_bg().copy()
    road = _surface(X0 + 40, X1 - 40, 10)
    trail = _surface(X0 + 40, X1 - 40, 4)
    top = road[np.argmin(road[:, 1])]
    if mode == "layers":
        k1 = ease_io(prog(t, 0.2, 1.2))
        _dashed(img, partial_line(trail, k1), DIRT, 6)
        k2 = ease_io(prog(t, 1.6, 1.2))
        lifted = road.copy()
        lifted[:, 1] -= 18
        part = partial_line(lifted, k2)
        aa_poly(img, part, (0, 0, 0), 16)
        aa_poly(img, part, YELLOW, 9)
        label(img, "1775 · WILDERNESS ROAD", top[0] - 380, top[1] + 120, prog(t, 0.6, 0.4), 44, DIRT)
        label(img, "1926 · US-25E", top[0] + 360, top[1] - 90, prog(t, 2.2, 0.4), 50, YELLOW)
        label(img, "UNO ENCIMA DEL OTRO", W / 2, 170, prog(t, 2.8, 0.4), 70, WHITE)
        if t > 2.6:
            _traffic(img, lifted, t, 7, 0.08)
    elif mode == "idea":
        lifted = road.copy()
        lifted[:, 1] -= 14
        aa_poly(img, lifted, (0, 0, 0), 14)
        aa_poly(img, lifted, YELLOW, 8)
        _traffic(img, lifted, t, 8, 0.07)
        k = ease_io(prog(t, 0.9, 1.4))
        x = lerp(PX0, PX1, k)
        if k > 0:
            for xx in np.arange(PX0, x, 30):
                cv2.line(img, (int(xx), TY), (int(min(xx + 16, x)), TY), WHITE, 5, cv2.LINE_AA)
        label(img, "¿Y SI PASA POR DEBAJO?", W / 2, TY + 110, prog(t, 1.8, 0.4), 64, WHITE)
        label(img, "1956 · SERVICIO DE PARQUES NACIONALES", W / 2, 160, prog(t, 0.2, 0.4), 50, YELLOW)
    elif mode == "pilot":
        aa_poly(img, road, (110, 106, 98), 6)
        k = ease_io(prog(t, 0.3, max(dur - 1.0, 1.0)))
        x = lerp(PX0, lerp(PX0, PX1, 4100 / 4600), k)
        _tube(img, PX0, x, TY, WHITE, 12)
        cv2.circle(img, (int(x), TY), 16, YELLOW, -1, cv2.LINE_AA)
        feats = [(0.18, "ARCILLA", (150, 120, 80)), (0.36, "CUEVAS", (24, 24, 26)), (0.52, "ARROYOS", WATER),
                 (0.7, "CAVERNA · 85 PIES", (24, 24, 26)), (0.86, "LAGO · 30 PIES", WATER)]
        for f, name, col in feats:
            fx = lerp(PX0, PX1, f)
            if x >= fx - 4:
                a = prog(t, 0.3 + (dur - 1.0) * f * 0.95, 0.35)
                if "CAVERNA" in name:
                    cv2.ellipse(img, (int(fx), TY - 110), (60, 95), 0, 0, 360, col, -1, cv2.LINE_AA)
                elif "LAGO" in name:
                    cv2.ellipse(img, (int(fx), TY + 70), (90, 34), 0, 0, 360, col, -1, cv2.LINE_AA)
                elif name == "ARROYOS":
                    aa_poly(img, np.array([[fx - 120, TY - 60], [fx - 40, TY - 40], [fx + 30, TY - 70], [fx + 110, TY - 50]]), col, 6)
                elif name == "CUEVAS":
                    cv2.circle(img, (int(fx - 30), TY - 60), 26, col, -1, cv2.LINE_AA)
                    cv2.circle(img, (int(fx + 40), TY + 50), 20, col, -1, cv2.LINE_AA)
                else:
                    cv2.ellipse(img, (int(fx), TY + 54), (70, 26), 0, 0, 360, col, -1, cv2.LINE_AA)
                label(img, name, fx, TY + (150 if "CAVERNA" not in name else -240), a, 40, WHITE)
        label(img, "TÚNEL PILOTO · 1985–1986", W / 2, 160, prog(t, 0.1, 0.4), 60, YELLOW)
        feet = int(4100 * k)
        label(img, f"{feet:,} PIES".replace(",", "."), W / 2, 240, prog(t, 0.3, 0.3), 52, WHITE)
    elif mode == "meet":
        aa_poly(img, road, (110, 106, 98), 6)
        k = ease_in(prog(t, 0.3, max(dur - 1.4, 1.0)))
        mid = (PX0 + PX1) / 2
        xl, xr = lerp(PX0, mid, k), lerp(PX1, mid, k)
        _tube(img, PX0, xl, TY)
        _tube(img, xr, PX1, TY)
        for x in (xl, xr):
            cv2.circle(img, (int(x), TY), 14, WHITE, -1, cv2.LINE_AA)
        if k >= 0.999:
            f = prog(t, 0.3 + max(dur - 1.4, 1.0), 0.6)
            layer = img.copy()
            cv2.circle(layer, (int(mid), TY), int(30 + 260 * f), YELLOW, 6, cv2.LINE_AA)
            img = cv2.addWeighted(layer, 1 - f, img, f, 0)
            label(img, "9 JULIO 1992", mid, TY - 140, prog(t, 0.4 + max(dur - 1.4, 1.0), 0.3), 72, YELLOW)
        label(img, "DOS CUADRILLAS · UNA HACIA LA OTRA", W / 2, 160, prog(t, 0.1, 0.4), 56, WHITE)
    elif mode == "open":
        lifted = road.copy()
        lifted[:, 1] -= 14
        aa_poly(img, lifted, (90, 86, 80), 6)
        k = ease_io(prog(t, 0.2, 1.0))
        _tube(img, PX0, lerp(PX0, PX1, k), TY - 34, YELLOW, 18)
        _tube(img, PX0, lerp(PX0, PX1, k), TY + 34, YELLOW, 18)
        if k >= 1:
            _traffic(img, np.array([[0, TY - 34], [W, TY - 34]], float), t, 7, 0.16)
            _traffic(img, np.array([[W, TY + 34], [0, TY + 34]], float), t + 0.3, 7, 0.16)
        cv2.line(img, (PX0, TY + 110), (PX1, TY + 110), YELLOW, 2, cv2.LINE_AA)
        for xx in (PX0, PX1):
            cv2.line(img, (xx, TY + 96), (xx, TY + 124), YELLOW, 2, cv2.LINE_AA)
        label(img, "4.600 PIES · ≈ 1,4 KM", W / 2, TY + 160, prog(t, 1.0, 0.4), 50, YELLOW)
        label(img, "18 OCTUBRE 1996", W / 2, 160, prog(t, 0.2, 0.4), 72, WHITE)
        label(img, "2 TUBOS · 2 CARRILES POR SENTIDO", W / 2, 240, prog(t, 0.8, 0.4), 46, GREY)
    elif mode in ("erase", "today"):
        lifted = road.copy()
        lifted[:, 1] -= 14
        k = ease_io(prog(t, 0.6, max(dur - 1.6, 1.2))) if mode == "erase" else 1.0
        n = len(lifted)
        cut = int(n * k)
        if cut < n:
            aa_poly(img, lifted[cut:], (0, 0, 0), 14)
            aa_poly(img, lifted[cut:], YELLOW, 8)
        if cut > 1:
            _dashed(img, trail[:cut], DIRT, 5, 12, 10)
            xs_done = lifted[cut - 1, 0]
            _trees_on(img, 1.0, x1=xs_done, n=int(34 * k))
        _tube(img, PX0, PX1, TY - 34, (120, 120, 120), 18)
        _tube(img, PX0, PX1, TY + 34, (120, 120, 120), 18)
        _traffic(img, np.array([[0, TY - 34], [W, TY - 34]], float), t, 8, 0.18)
        _traffic(img, np.array([[W, TY + 34], [0, TY + 34]], float), t + 0.3, 8, 0.18)
        if mode == "erase":
            label(img, "BORRAR LA CARRETERA", W / 2, 160, prog(t, 0.2, 0.4), 72, WHITE)
        else:
            f = (t * 0.035) % 1.0
            p = partial_line(trail, f)[-1]
            cv2.circle(img, (int(p[0]), int(p[1]) - 10), 10, WHITE, -1, cv2.LINE_AA)
            label(img, "ARRIBA: SILENCIO", top[0], top[1] - 150, prog(t, 0.3, 0.4), 60, WHITE)
            label(img, "ABAJO: +30.000 VEHÍCULOS AL DÍA", W / 2, TY + 150, prog(t, 1.0, 0.4), 54, YELLOW)
    return img


# ------------------------------------------------------------------ brake temperature overlay
def brake_heat(img, t, dur, t0=0.3, steps=6, every=0.55, x=0.86, y=0.2):
    a = ease_out(prog(t, t0, 0.3)) * (1 - prog(t, dur - 0.3, 0.3))
    if a <= 0:
        return
    bx, by, bw, bh = int(W * x), int(H * y), 70, 560
    layer = img.copy()
    cv2.rectangle(layer, (bx - 20, by - 70), (bx + bw + 20, by + bh + 120), (14, 14, 16), -1)
    n = int(clamp((t - t0) / every, 0, steps))
    frac = clamp((n + clamp(((t - t0) % every) / every) * (n < steps)) / steps)
    fh = int(bh * frac)
    col = tuple(int(lerp(c0, c1, frac)) for c0, c1 in zip(YELLOW, RED))
    cv2.rectangle(layer, (bx, by), (bx + bw, by + bh), (60, 60, 64), 3)
    cv2.rectangle(layer, (bx + 6, by + bh - fh), (bx + bw - 6, by + bh - 6), col, -1)
    cv2.circle(layer, (bx + bw // 2, by + bh + 50), 50, col, -1, cv2.LINE_AA)
    img[:] = cv2.addWeighted(layer, a, img, 1 - a, 0)
    label(img, "FRENOS", bx + bw / 2, by - 40, a, 40, WHITE)
    label(img, f"CURVA {max(n, 1)}", bx + bw / 2 - 260, by + bh - fh, a, 46, col, "l")


# ------------------------------------------------------------------ the 40-year timeline
def timeline(t, dur, events, hi=None, title=None, y0=1940, y1=2000, red=()):
    """events: list of (year, label, appear_t). hi: year to pulse."""
    img = background("dark_grid", t)
    xa, xb, yy = 160, W - 160, 600
    k = ease_io(prog(t, 0.1, 0.8))
    cv2.line(img, (xa, yy), (int(lerp(xa, xb, k)), yy), (110, 112, 116), 4, cv2.LINE_AA)
    for yr in range(y0, y1 + 1, 10):
        x = lerp(xa, xb, (yr - y0) / (y1 - y0))
        if x <= lerp(xa, xb, k):
            cv2.line(img, (int(x), yy - 12), (int(x), yy + 12), (110, 112, 116), 3, cv2.LINE_AA)
            label(img, str(yr), x, yy + 50, 0.7, 34, GREY)
    for i, (yr, lab, at) in enumerate(events):
        a = ease_out(prog(t, at, 0.35))
        if a <= 0:
            continue
        x = lerp(xa, xb, (yr - y0) / (y1 - y0))
        up = i % 2 == 0
        col = RED if yr in red else YELLOW
        r = 13 + (6 * abs(math.sin(t * 4)) if yr == hi else 0)
        cv2.circle(img, (int(x), yy), int(r), col, -1, cv2.LINE_AA)
        ly = yy - 150 if up else yy + 150
        cv2.line(img, (int(x), yy + (-16 if up else 16)), (int(x), int(ly + (40 if up else -40))), col, 2, cv2.LINE_AA)
        label(img, str(int(yr)), x, ly - 26 if up else ly + 6, a, 54, col)
        label(img, lab, x, ly + 26 if up else ly + 58, a, 32, WHITE)
    if title:
        label(img, title, W / 2, 170, prog(t, 0.2, 0.4), 66, WHITE)
    return img


def span_bar(img, t, dur, ya, yb, text, t0=0.3, y1940=1940, y2000=2000, yy=600, col=YELLOW):
    xa, xb = 160, W - 160
    k = ease_io(prog(t, t0, 1.0))
    if k <= 0:
        return
    x0 = lerp(xa, xb, (ya - y1940) / (y2000 - y1940))
    x1 = lerp(xa, xb, (yb - y1940) / (y2000 - y1940))
    xe = lerp(x0, x1, k)
    cv2.rectangle(img, (int(x0), yy - 300), (int(xe), yy - 284), col, -1)
    label(img, text, (x0 + x1) / 2, yy - 340, prog(t, t0 + 0.8, 0.4), 60, col)


# ------------------------------------------------------------------ calendar cards
def calendar(t, dur, cards, title=None):
    """cards: list of (day, month_year, caption, appear_t, color)."""
    img = background("dark_grid", t)
    n = len(cards)
    cw, ch, gap = 420, 470, 70
    x0 = W / 2 - (n * cw + (n - 1) * gap) / 2
    for i, (day, my, cap, at, col) in enumerate(cards):
        a = ease_out(prog(t, at, 0.35))
        if a <= 0:
            continue
        cx = x0 + i * (cw + gap) + cw / 2
        sc = lerp(0.85, 1.0, ease_back(prog(t, at, 0.4)))
        card = rounded_rect_sprite(cw, ch, (238, 234, 226), 18, 255)
        over_center(img, card, cx, 560, a, sc)
        head = rounded_rect_sprite(cw, 110, col, 18, 255)
        over_center(img, head, cx, 560 - ch / 2 * sc + 55 * sc, a, sc)
        label(img, my, cx, 560 - ch / 2 * sc + 52 * sc, a, int(46 * sc), WHITE)
        label(img, day, cx, 590, a, int(210 * sc), (24, 24, 26))
        label(img, cap, cx, 560 + ch / 2 + 50, a, 44, col if col != (60, 62, 66) else WHITE)
    if title:
        label(img, title, W / 2, 140, prog(t, 0.1, 0.4), 60, WHITE)
    return img


# ------------------------------------------------------------------ cost bars
def cost_bars(t, dur, items, title=None, unit="MILLONES DE DÓLARES"):
    """items: list of (label, value, appear_t, color)."""
    img = background("dark_grid", t)
    vmax = max(v for _, v, _, _ in items)
    n = len(items)
    bw, gap, base = 260, 160, 900
    x0 = W / 2 - (n * bw + (n - 1) * gap) / 2
    for i, (lab, v, at, col) in enumerate(items):
        k = ease_out(prog(t, at, 0.9))
        if k <= 0:
            continue
        h = 560 * v / vmax * k
        x = x0 + i * (bw + gap)
        cv2.rectangle(img, (int(x), int(base - h)), (int(x + bw), base), col, -1)
        label(img, f"{int(round(v * k))}", x + bw / 2, base - h - 60, 1.0, 96, col)
        label(img, lab, x + bw / 2, base + 50, 1.0, 40, WHITE)
    if title:
        label(img, title, W / 2, 150, prog(t, 0.1, 0.4), 62, WHITE)
    label(img, unit, W / 2, 220, prog(t, 0.3, 0.4), 38, GREY)
    return img


# ------------------------------------------------------------------ hazmat escort at the portal
def hazmat(t, dur):
    img = background("dark_grid", t)
    y = 600
    cv2.rectangle(img, (0, y - 70), (W, y + 70), (36, 37, 40), -1)
    for x in range(0, W, 70):
        cv2.line(img, (x, y), (x + 36, y), (200, 200, 200), 3, cv2.LINE_AA)
    px = 1450
    fill_poly(img, np.array([[px - 30, 200], [W, 200], [W, H], [px - 30, H], [px - 30, y + 90], [px, y + 90], [px, y - 90],
                             [px - 30, y - 90]]), ROCK)
    cv2.rectangle(img, (px, y - 90), (W, y + 90), (12, 12, 14), -1)
    label(img, "BOCA DEL TÚNEL", px + 230, 260, prog(t, 0.2, 0.4), 44, GREY)
    # queue of trucks waiting
    for i in range(4):
        x = 980 - i * 250
        cv2.rectangle(img, (int(x - 100), y - 34), (int(x + 100), y + 34), (190, 190, 186), -1)
        cv2.rectangle(img, (int(x + 100), y - 30), (int(x + 140), y + 30), (150, 150, 146), -1)
    # escorted truck going in
    k = ease_io(prog(t, 0.8, max(dur - 1.2, 1.0)))
    x = lerp(1180, 1900, k)
    cv2.rectangle(img, (int(x - 100), y - 34), (int(x + 100), y + 34), (230, 120, 40), -1)
    d = np.array([[x, y - 22], [x + 22, y], [x, y + 22], [x - 22, y]])
    fill_poly(img, d, (250, 200, 40))
    ex = x + 230
    cv2.rectangle(img, (int(ex - 50), y - 26), (int(ex + 50), y + 26), (230, 230, 226), -1)
    if int(t * 6) % 2:
        cv2.circle(img, (int(ex), y - 32), 12, (60, 120, 255), -1, cv2.LINE_AA)
    else:
        cv2.circle(img, (int(ex), y - 32), 12, RED, -1, cv2.LINE_AA)
    label(img, "CARGA PELIGROSA: DE UNO EN UNO, CON ESCOLTA", W / 2 - 120, 160, prog(t, 0.2, 0.4), 56, WHITE)
    return img


# ------------------------------------------------------------------ comments call to action
def comments(img, t, dur, line1, line2, cta="CUÉNTANOS EN LOS COMENTARIOS"):
    a = ease_out(prog(t, 0.2, 0.4))
    if a <= 0:
        return
    bx, by = W / 2, H * 0.56
    bub = rounded_rect_sprite(1180, 230, (245, 242, 235), 28, 255)
    over_center(img, bub, bx, by, a)
    tail = np.array([[bx - 360, by + 105], [bx - 430, by + 175], [bx - 290, by + 110]])
    if a > 0.9:
        fill_poly(img, tail, (245, 242, 235))
    label(img, line1, bx, by - 40, a, 60, (20, 20, 20))
    label(img, line2, bx, by + 32, a, 46, (20, 20, 20))
    label(img, cta, W / 2, H * 0.82, prog(t, 0.9, 0.4), 50, YELLOW)


# ------------------------------------------------------------------ dripping water overlay
def drips(img, t, dur, n=40, seed=3, col=(170, 200, 230)):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(0, W)
        sp = rng.uniform(500, 900)
        ph = rng.uniform(0, 1)
        y = ((t * sp / H + ph) % 1.0) * (H + 80) - 40
        cv2.line(img, (int(x), int(y)), (int(x), int(y + 18)), col, 2, cv2.LINE_AA)
