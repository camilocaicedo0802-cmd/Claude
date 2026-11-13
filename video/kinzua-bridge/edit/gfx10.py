"""Kinzua Bridge (1882-2026): diagrams drawn in code for this episode."""
import json
import math
import os

import cv2
import numpy as np

from engine import BLACK, H, RED, W, WHITE, YELLOW, Sprite, clamp, ease_back, ease_in, ease_io, ease_out, lerp, over, \
    over_center, prog, rounded_rect_sprite, text_sprite
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

IRON = (128, 72, 54)        # 1882 wrought iron (rust red)
IRON_DK = (92, 52, 40)
STEEL = (96, 104, 116)      # 1900 steel
STEEL_DK = (66, 72, 82)
STONE = (186, 164, 126)     # sandstone pedestals
STONE_DK = (140, 122, 92)
FOREST = (44, 64, 44)
FOREST_HI = (60, 84, 56)
CREEK = (70, 120, 160)
GREEN = (80, 190, 110)
GLASS = (150, 210, 230)
PAPER = (234, 228, 212)
INK = (34, 32, 30)
SKY_TOP, SKY_BOT = (40, 52, 70), (120, 136, 150)

# ---------------------------------------------------------------- bridge geometry (side elevation, south on the left)
_PROF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "kz_profile.json")))
FT_LEN = 2053.0
X0, X1 = 110.0, 1810.0
HS = (X1 - X0) / FT_LEN            # px per foot along the bridge
VS = 1.38                          # px per foot vertically (slight exaggeration)
DECK_Y = 300.0
DECK_ELEV = min(_PROF["ft"]) + 301.0
N_T = 20
TW, TSP, END = 38.5, 61.5, 57.0
FALLEN = list(range(6, 17))        # 11 towers (schematic)
CENTER = list(range(9, 14))        # gave way first
LIFTED = (10, 11, 12)              # torn off their bases, hanging from the rails for an instant


def ground_elev(s):
    """Ground elevation (ft) at s feet from the south abutment, from the real terrain profile."""
    k0, k1, ft = _PROF["k0"], _PROF["k1"], _PROF["ft"]
    k = s / FT_LEN
    u = (k - k0) / (k1 - k0) * (len(ft) - 1)
    return float(np.interp(u, np.arange(len(ft)), ft))


def sx(s):
    return X0 + s * HS


def gy(s):
    return DECK_Y + (DECK_ELEV - ground_elev(s)) * VS


def tower_s(i):
    return END + i * (TW + TSP)


def _grad(top, bot):
    g = np.linspace(0, 1, H)[:, None, None]
    img = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    return np.repeat(img, W, axis=1).astype(np.uint8)


def _blend(img, layer, a):
    if a > 0.001:
        cv2.addWeighted(layer, min(a, 1.0), img, 1 - min(a, 1.0), 0, img)


def _tag(img, txt="ESQUEMA", a=0.7):
    label(img, txt, W - 160, H - 46, a, 30, GREY)


def _valley(img, night=False, seed=3):
    """Far ridge, valley profile filled with forest, creek at the bottom."""
    xs = np.linspace(0, W, 220)
    rng = np.random.default_rng(seed)
    far = 360 + 40 * np.sin(xs / 260.0) + 18 * np.sin(xs / 70.0 + 1.3)
    fill_poly(img, np.vstack([np.stack([xs, far], 1), [[W, H], [0, H]]]), (58, 72, 70) if not night else (24, 30, 32))
    ss = (xs - X0) / HS
    ys = np.array([gy(s) for s in ss])
    col = FOREST if not night else (22, 32, 24)
    fill_poly(img, np.vstack([np.stack([xs, ys], 1), [[W, H], [0, H]]]), col)
    # tree texture
    for _ in range(420):
        x = rng.uniform(0, W)
        yb = float(np.interp(x, xs, ys))
        y = rng.uniform(yb + 4, min(H, yb + 160))
        r = int(rng.uniform(5, 11))
        c = FOREST_HI if not night else (30, 42, 32)
        cv2.circle(img, (int(x), int(y)), r, tuple(int(v * rng.uniform(0.85, 1.1)) for v in c), -1, cv2.LINE_AA)
    aa_poly(img, np.stack([xs, ys], 1), (74, 100, 68) if not night else (34, 46, 36), 4)
    i = int(np.argmax(ys))
    cx, cy = xs[i], ys[i]
    cv2.ellipse(img, (int(cx), int(cy + 6)), (26, 5), 0, 0, 360, CREEK, -1, cv2.LINE_AA)
    return xs, ys


def _pedestal(img, x, y, w=14, a=1.0, col=STONE):
    p = np.array([[x - w, y + 4], [x + w, y + 4], [x + w * 0.8, y - 10], [x - w * 0.8, y - 10]], np.float64)
    if a >= 0.999:
        fill_poly(img, p, col)
    else:
        layer = img.copy()
        fill_poly(layer, p, col)
        _blend(img, layer, a)


def _tower(img, i, col, a=1.0, top=None, lift=0.0, squash=1.0, dx=0.0, rot=0.0, width=3):
    """One tower in elevation: two legs + X bracing. squash<1 = falling out of the picture plane."""
    s0, s1 = tower_s(i), tower_s(i) + TW
    xa, xb = sx(s0) + dx, sx(s1) + dx
    ya, yb = gy(s0), gy(s1)
    yt = DECK_Y if top is None else top
    ya2, yb2 = ya - lift, yb - lift
    # squash toward the ground
    yt_a = ya2 - (ya2 - yt) * squash
    yt_b = yb2 - (yb2 - yt) * squash
    tgt = img if a >= 0.999 else img.copy()
    pts_a = np.array([[xa, yt_a], [xa, ya2]])
    pts_b = np.array([[xb, yt_b], [xb, yb2]])
    if rot:
        c = np.array([(xa + xb) / 2, (ya2 + yb2) / 2])
        R = np.array([[math.cos(rot), -math.sin(rot)], [math.sin(rot), math.cos(rot)]])
        pts_a = (pts_a - c) @ R.T + c
        pts_b = (pts_b - c) @ R.T + c
    for p in (pts_a, pts_b):
        cv2.line(tgt, tuple(p[0].astype(int)), tuple(p[1].astype(int)), col, width + 1, cv2.LINE_AA)
    n = max(1, int(abs(ya2 - yt_a) / 34))
    for k in range(n):
        f0, f1 = k / n, (k + 1) / n
        a0 = pts_a[0] + (pts_a[1] - pts_a[0]) * f0
        a1 = pts_a[0] + (pts_a[1] - pts_a[0]) * f1
        b0 = pts_b[0] + (pts_b[1] - pts_b[0]) * f0
        b1 = pts_b[0] + (pts_b[1] - pts_b[0]) * f1
        cv2.line(tgt, tuple(a0.astype(int)), tuple(b1.astype(int)), col, max(1, width - 1), cv2.LINE_AA)
        cv2.line(tgt, tuple(b0.astype(int)), tuple(a1.astype(int)), col, max(1, width - 1), cv2.LINE_AA)
        cv2.line(tgt, tuple(a1.astype(int)), tuple(b1.astype(int)), col, max(1, width - 2), cv2.LINE_AA)
    if tgt is not img:
        _blend(img, tgt, a)


def _deck(img, s0, s1, col, a=1.0, y=DECK_Y, rails=True, sag=0.0):
    x0, x1 = sx(s0), sx(s1)
    tgt = img if a >= 0.999 else img.copy()
    p = np.array([[x0, y], [x1, y + sag], [x1, y + sag + 12], [x0, y + 12]], np.float64)
    fill_poly(tgt, p, col)
    n = max(1, int((x1 - x0) / 10))
    for k in range(n):
        xa = x0 + (x1 - x0) * k / n
        xb = x0 + (x1 - x0) * (k + 1) / n
        ya = y + sag * k / n
        yb = y + sag * (k + 1) / n
        cv2.line(tgt, (int(xa), int(ya + 12)), (int(xb), int(yb)), tuple(int(c * 0.7) for c in col), 1, cv2.LINE_AA)
    if rails:
        cv2.line(tgt, (int(x0), int(y - 3)), (int(x1), int(y + sag - 3)), (160, 160, 166), 2, cv2.LINE_AA)
    if tgt is not img:
        _blend(img, tgt, a)


def _debris(img, i, k=1.0, seed=0):
    """A fallen tower lying twisted on the valley floor."""
    rng = np.random.default_rng(seed + i)
    s = tower_s(i) + TW / 2
    x, y = sx(s), gy(s)
    layer = img.copy()
    for _ in range(14):
        a = rng.uniform(-0.5, 0.5)
        L = rng.uniform(20, 70)
        x0 = x + rng.uniform(-40, 40)
        y0 = y + rng.uniform(-14, 6)
        cv2.line(layer, (int(x0), int(y0)), (int(x0 + L * math.cos(a)), int(y0 + L * math.sin(a) * 0.4)), IRON, 3, cv2.LINE_AA)
    _blend(img, layer, k)


def viaduct(t, dur, mode="full", t0=0.3, steel=None, dims=False, build_d=6.0, checks=None, check_t=None, fall_t=None,
            labels=True, night=False, hl_base=False, title=None, zoom=None):
    """Side elevation of the Kinzua Viaduct over the real valley profile.
    modes: full | build | steel | repair | collapse | after | skywalk"""
    img = _grad(SKY_TOP, SKY_BOT) if not night else _grad((8, 10, 16), (30, 34, 44))
    _valley(img, night)
    st = 1.0 if steel is None else steel   # 0 = iron 1882, 1 = steel 1900 (sweeps left to right)
    if mode == "build":
        k = ease_io(prog(t, t0, build_d))
        n_up = k * N_T
        for i in range(N_T):
            g = clamp(n_up - i, 0, 1)
            if g <= 0:
                continue
            _pedestal(img, sx(tower_s(i)), gy(tower_s(i)))
            _pedestal(img, sx(tower_s(i) + TW), gy(tower_s(i) + TW))
            yb = min(gy(tower_s(i)), gy(tower_s(i) + TW))
            top = yb - (yb - DECK_Y) * ease_out(g)
            _tower(img, i, IRON, top=top)
        se = END + n_up * (TW + TSP)
        if se > 0:
            _deck(img, 0, min(FT_LEN, se + (TW if n_up >= N_T else 0) + (END if n_up >= N_T else 0)), IRON_DK)
        if k < 1:
            # the traveller crane at the head of the deck
            cx = sx(min(se, FT_LEN))
            cv2.line(img, (int(cx - 30), int(DECK_Y - 2)), (int(cx - 30), int(DECK_Y - 70)), (210, 200, 160), 4, cv2.LINE_AA)
            cv2.line(img, (int(cx - 30), int(DECK_Y - 70)), (int(cx + 60), int(DECK_Y - 40)), (210, 200, 160), 4, cv2.LINE_AA)
            cv2.line(img, (int(cx + 60), int(DECK_Y - 40)), (int(cx + 60), int(DECK_Y + 60)), (210, 200, 160), 1, cv2.LINE_AA)
            label(img, "GRÚA SOBRE EL PROPIO PUENTE", cx, DECK_Y - 120, ease_out(prog(t, t0 + 0.8, 0.4)), 40, YELLOW) if labels else None
        _tag(img)
        return img
    fall = mode in ("collapse",)
    gone = set(FALLEN) if mode in ("after", "skywalk") else set()
    ft = fall_t if fall_t is not None else t0
    for i in range(N_T):
        s0 = tower_s(i)
        frac_x = (sx(s0) - X0) / (X1 - X0)
        c = IRON if frac_x > st else STEEL
        if mode in ("after", "skywalk", "repair", "collapse"):
            c = STEEL
        _pedestal(img, sx(s0), gy(s0))
        _pedestal(img, sx(s0 + TW), gy(s0 + TW))
        if i in gone:
            _debris(img, i)
            continue
        if fall and i in FALLEN:
            order = 0.0 if i in CENTER else (0.9 + 0.22 * abs(i - 11.5))
            lt = ft + order
            lift = 0.0
            if i in LIFTED:
                lift = 14 * ease_out(prog(t, ft - 0.9, 0.5))
            kf = ease_in(prog(t, lt, 1.1))
            if kf >= 1:
                _debris(img, i, 1.0)
                continue
            _tower(img, i, c, lift=lift, squash=max(0.02, math.cos(kf * math.pi / 2)), rot=0.04 * math.sin((t - ft) * 9) * (1 - kf))
            if kf > 0.6:
                _debris(img, i, (kf - 0.6) / 0.4)
            continue
        _tower(img, i, c)
    # deck spans
    for i in range(-1, N_T):
        s0 = 0 if i < 0 else tower_s(i)
        s1 = FT_LEN if i == N_T - 1 else tower_s(i + 1) + TW
        if i >= 0:
            s1 = tower_s(i) + TW + TSP + TW if i < N_T - 1 else FT_LEN
        frac_x = (sx(s0) - X0) / (X1 - X0)
        c = IRON_DK if frac_x > st else STEEL_DK
        if mode in ("after", "skywalk", "repair", "collapse"):
            c = STEEL_DK
        over_gone = (i in gone) or (i + 1 in gone)
        if over_gone:
            continue
        if fall and (i in FALLEN or i + 1 in FALLEN):
            ii = i if i in FALLEN else i + 1
            order = 0.0 if ii in CENTER else (0.9 + 0.22 * abs(ii - 11.5))
            kf = ease_in(prog(t, ft + order, 1.1))
            if kf >= 1:
                continue
            _deck(img, s0, s1, c, a=1 - kf, sag=60 * kf)
            continue
        _deck(img, s0, s1, c)
    if hl_base:
        hk = ease_out(prog(t, hl_base if isinstance(hl_base, (int, float)) and hl_base is not True else t0, 0.5))
        for i in range(N_T):
            for s in (tower_s(i), tower_s(i) + TW):
                cv2.circle(img, (int(sx(s)), int(gy(s) - 2)), int(11 * hk) + 1, YELLOW, 2, cv2.LINE_AA)
        if labels:
            label(img, "LA BASE SIGUE SIENDO DE 1882", W / 2, H - 120, hk, 52, YELLOW)
    if mode == "repair" or checks is not None:
        order = checks or [0, 1, 2, 3, 4, 5, 19, 18, 17]
        ct = check_t if check_t is not None else t0
        for j, i in enumerate(order):
            a = ease_out(prog(t, ct + 0.45 * j, 0.3))
            if a <= 0:
                continue
            x = sx(tower_s(i) + TW / 2)
            y = gy(tower_s(i)) + 22
            pts = np.array([[x - 12, y], [x - 3, y + 10], [x + 14, y - 12]], np.float64)
            layer = img.copy()
            cv2.circle(layer, (int(x), int(y)), 20, (30, 60, 40), -1, cv2.LINE_AA)
            aa_poly(layer, pts, GREEN, 5)
            _blend(img, layer, a)
    if mode == "skywalk":
        k = ease_out(prog(t, t0, 0.8))
        s_end = tower_s(5) + TW + 10
        x0, x1 = sx(0), sx(s_end)
        layer = img.copy()
        cv2.line(layer, (int(x0), int(DECK_Y - 18)), (int(x1), int(DECK_Y - 18)), (200, 200, 206), 3, cv2.LINE_AA)
        for x in np.arange(x0, x1, 14):
            cv2.line(layer, (int(x), int(DECK_Y - 18)), (int(x), int(DECK_Y)), (200, 200, 206), 1, cv2.LINE_AA)
        cv2.rectangle(layer, (int(x1 - 46), int(DECK_Y - 4)), (int(x1), int(DECK_Y + 6)), GLASS, -1)
        _blend(img, layer, k)
        if labels:
            label(img, "KINZUA SKY WALK · 2011", sx(s_end / 2), DECK_Y - 70, k, 44, YELLOW)
            label(img, "PISO DE VIDRIO", x1 + 30, DECK_Y + 60, ease_out(prog(t, t0 + 0.8, 0.4)), 36, GLASS, anchor="l")
    if dims:
        dk = ease_out(prog(t, dims if not isinstance(dims, bool) else t0, 0.6))
        if dk > 0:
            xm = sx(tower_s(11) + TW + TSP / 2)
            ym = max(gy(s) for s in np.linspace(0, FT_LEN, 200))
            cv2.arrowedLine(img, (int(xm), int(DECK_Y + 16)), (int(xm), int(ym - 6)), YELLOW, 3, cv2.LINE_AA, tipLength=0.04)
            cv2.arrowedLine(img, (int(xm), int(ym - 6)), (int(xm), int(DECK_Y + 16)), YELLOW, 3, cv2.LINE_AA, tipLength=0.04)
            label(img, "301 PIES · 92 M", xm + 24, (DECK_Y + ym) / 2, dk, 50, YELLOW, anchor="l")
            y = int(DECK_Y - 60)
            cv2.arrowedLine(img, (int(X0), y), (int(X1), y), WHITE, 2, cv2.LINE_AA, tipLength=0.01)
            cv2.arrowedLine(img, (int(X1), y), (int(X0), y), WHITE, 2, cv2.LINE_AA, tipLength=0.01)
            label(img, "2.053 PIES · 625 M", W / 2, y - 40, ease_out(prog(t, (dims if not isinstance(dims, bool) else t0) + 0.6, 0.5)), 48, WHITE)
    if title:
        label(img, title, W / 2, 130, ease_out(prog(t, 0.1, 0.4)), 58, WHITE)
    if mode in ("full", "steel") and steel is not None and labels and 0 < st < 1:
        xx = X0 + (X1 - X0) * st
        cv2.line(img, (int(xx), 200), (int(xx), int(DECK_Y + 20)), YELLOW, 2, cv2.LINE_AA)
    _tag(img)
    if zoom:
        z, cx, cy = zoom
        M = np.array([[z, 0, W / 2 - z * cx], [0, z, H / 2 - z * cy]], np.float32)
        img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return img


def viaduct_zoom(t, dur, mode="full", z0=1.0, z1=1.0, c0=(W / 2, H / 2), c1=(W / 2, H / 2), **kw):
    k = ease_io(prog(t, 0.0, dur))
    z = math.exp(lerp(math.log(z0), math.log(z1), k))
    return viaduct(t, dur, mode, zoom=(z, lerp(c0[0], c1[0], k), lerp(c0[1], c1[1], k)), **kw)


# ---------------------------------------------------------------- the garden chair in the wind
def chair(t, dur, gust_t=1.0, bolt_t=None, rot_t=None):
    img = _grad((150, 176, 196), (210, 214, 206))
    gy_ = 820
    fill_poly(img, [[0, gy_], [W, gy_], [W, H], [0, H]], (150, 150, 140))
    for x in range(0, W, 90):
        cv2.line(img, (x, gy_), (x - 60, H), (130, 130, 122), 2, cv2.LINE_AA)
    cx = W / 2
    tilt = 0.0
    fly = 0.0
    gk = ease_in_out_gust(t, gust_t)
    bolt = bolt_t is not None and t >= bolt_t and (rot_t is None or t < rot_t)
    rotten = rot_t is not None and t >= rot_t
    if rotten:
        fk = ease_in(prog(t, rot_t + 0.4, 1.4))
        tilt = 0.18 + 0.9 * fk
        fly = fk
    elif bolt:
        tilt = 0.02 * gk
    else:
        tilt = 0.18 * gk
    # chair geometry (side view), pivot at the leeward foot (right)
    piv = np.array([cx + 120, gy_])
    pts = {
        "seat": np.array([[-120, -200], [120, -200]]),
        "back": np.array([[-120, -200], [-140, -440]]),
        "l1": np.array([[-120, -200], [-120, 0]]),
        "l2": np.array([[120, -200], [120, 0]]),
    }
    R = np.array([[math.cos(tilt), -math.sin(tilt)], [math.sin(tilt), math.cos(tilt)]])
    off = np.array([cx, gy_]) + np.array([fly * 900, -fly * 380])
    for k, p in pts.items():
        q = (p + [0, 0]) - [120, 0]
        q = q @ R.T + [120, 0] + off
        cv2.line(img, tuple(q[0].astype(int)), tuple(q[1].astype(int)), (70, 60, 50), 18, cv2.LINE_AA)
    # bolts at the feet
    for fx in (-120, 120):
        foot = (np.array([fx, 0]) - [120, 0]) @ R.T + [120, 0] + off
        col = (90, 90, 96) if not rotten else (90, 60, 40)
        if bolt or rotten or bolt_t is not None:
            cv2.rectangle(img, (int(cx + fx - 14), gy_ - 4), (int(cx + fx + 14), gy_ + 10), col, -1)
            cv2.line(img, (int(cx + fx), gy_), (int(cx + fx), gy_ + 46), col, 6)
            if rotten:
                for k in range(5):
                    cv2.circle(img, (int(cx + fx + np.sin(k * 3) * 10), gy_ + 10 + k * 8), 4, (140, 90, 50), -1, cv2.LINE_AA)
    # wind arrows
    if gk > 0.05:
        for j in range(5):
            y = 330 + j * 90
            x0 = 60 + ((t * 600 + j * 170) % 500)
            cv2.arrowedLine(img, (int(x0), y), (int(x0 + 220), y), (250, 250, 250), 6, cv2.LINE_AA, tipLength=0.25)
    # weight arrow
    cv2.arrowedLine(img, (int(cx + 10), 470), (int(cx + 10), 600), (40, 40, 160), 7, cv2.LINE_AA, tipLength=0.3)
    label(img, "PESO", cx + 40, 520, 0.9, 44, (40, 40, 160), anchor="l")
    if gk > 0.3 and not bolt and not rotten:
        label(img, "SE LEVANTA", cx - 120, gy_ - 40, gk, 44, RED)
        label(img, "SE CLAVA", cx + 140, gy_ + 50, gk, 44, WHITE, anchor="l")
    if bolt:
        label(img, "ATORNILLADA: NO SE MUEVE", W / 2, 160, ease_out(prog(t, bolt_t, 0.4)), 62, (40, 120, 60))
    if rotten:
        label(img, "TORNILLOS PODRIDOS: SE VA", W / 2, 160, ease_out(prog(t, rot_t, 0.4)), 62, RED)
    if not bolt and not rotten:
        label(img, "UNA RÁFAGA DE COSTADO", W / 2, 160, ease_out(prog(t, gust_t, 0.4)), 62, INK)
    _tag(img, "ESQUEMA")
    return img


def ease_in_out_gust(t, t0):
    k = prog(t, t0, 1.0)
    return ease_out(k) * (0.85 + 0.15 * math.sin(t * 7))


# ---------------------------------------------------------------- one tower seen end-on, with its anchors
def tower_end(t, dur, mode="weight", t0=0.3, wind_t=None, lift_t=None, sway_t=None, labels=True):
    img = background("dark_grid", t)
    base_y = 880
    top_y = 160
    half_top, half_bot = 90, 300
    cx = W / 2
    wk = ease_out(prog(t, wind_t if wind_t is not None else t0 + 0.8, 0.6)) if mode in ("wind", "lift", "sway") else 0.0
    rock = 0.0
    lift = 0.0
    if mode == "lift":
        lift = 22 * ease_out(prog(t, lift_t if lift_t is not None else t0 + 1.5, 0.8))
    if mode == "sway":
        st = sway_t if sway_t is not None else t0 + 0.5
        k = prog(t, st, dur - st)
        rock = 0.05 * math.sin((t - st) * 5.0) * (0.4 + k)
        lift = max(0.0, 26 * math.sin((t - st) * 5.0) * (0.4 + k))
    piv = np.array([cx + half_bot, base_y])
    R = np.array([[math.cos(rock), -math.sin(rock)], [math.sin(rock), math.cos(rock)]])

    def P(x, y):
        q = np.array([x, y]) - piv
        return q @ R.T + piv

    # pedestals
    for sgn in (-1, 1):
        x = cx + sgn * half_bot
        fill_poly(img, [[x - 60, base_y], [x + 60, base_y], [x + 70, base_y + 120], [x - 70, base_y + 120]], STONE)
    # legs + bracing
    lA0, lA1 = P(cx - half_top, top_y), P(cx - half_bot, base_y - lift)
    lB0, lB1 = P(cx + half_top, top_y), P(cx + half_bot, base_y)
    for a, b in ((lA0, lA1), (lB0, lB1)):
        cv2.line(img, tuple(a.astype(int)), tuple(b.astype(int)), STEEL, 14, cv2.LINE_AA)
    for k in range(5):
        f0, f1 = k / 5, (k + 1) / 5
        a0, a1 = lA0 + (lA1 - lA0) * f0, lA0 + (lA1 - lA0) * f1
        b0, b1 = lB0 + (lB1 - lB0) * f0, lB0 + (lB1 - lB0) * f1
        cv2.line(img, tuple(a0.astype(int)), tuple(b1.astype(int)), STEEL_DK, 5, cv2.LINE_AA)
        cv2.line(img, tuple(b0.astype(int)), tuple(a1.astype(int)), STEEL_DK, 5, cv2.LINE_AA)
        cv2.line(img, tuple(a1.astype(int)), tuple(b1.astype(int)), STEEL_DK, 4, cv2.LINE_AA)
    deck = [P(cx - 160, top_y - 10), P(cx + 160, top_y - 10), P(cx + 160, top_y + 6), P(cx - 160, top_y + 6)]
    fill_poly(img, np.array(deck), STEEL_DK)
    # anchor bolts
    for sgn in (-1, 1):
        x = cx + sgn * half_bot
        ly = lift if sgn < 0 else 0
        col = (120, 80, 50)
        cv2.line(img, (int(x), int(base_y - ly)), (int(x), int(base_y + 90)), col, 8)
        if sgn < 0 and lift > 4:
            cv2.line(img, (int(x), int(base_y - ly)), (int(x), int(base_y - ly + 8)), RED, 10)
    if labels:
        label(img, "UNA TORRE VISTA DE FRENTE", W / 2, 80, ease_out(prog(t, 0.1, 0.4)), 50, GREY)
        if mode == "weight":
            for x in (cx - 180, cx + 180):
                cv2.arrowedLine(img, (int(x), 330), (int(x), 470), (90, 150, 230), 8, cv2.LINE_AA, tipLength=0.3)
            label(img, "CONTRA EL PESO: SOBRADO", W / 2, 1035, ease_out(prog(t, t0, 0.4)), 54, (90, 200, 120))
        if wk > 0:
            for j in range(3):
                y = 260 + j * 130
                x0 = 120 + ((t * 500 + j * 120) % 260)
                cv2.arrowedLine(img, (int(x0), y), (int(x0 + 240), y), (230, 230, 230), 8, cv2.LINE_AA, tipLength=0.25)
            label(img, "VIENTO DE COSTADO", 300, 180, wk, 50, WHITE)
        if mode == "wind":
            label(img, "TODO DEPENDE DE LOS PERNOS DE LA BASE", W / 2, 1035, ease_out(prog(t, (wind_t or t0) + 1.0, 0.4)), 50, YELLOW)
            ka = ease_out(prog(t, (wind_t or t0) + 1.0, 0.4))
            for sgn in (-1, 1):
                cv2.circle(img, (int(cx + sgn * half_bot), int(base_y + 40)), int(60 * ka) + 1, YELLOW, 4, cv2.LINE_AA)
        if mode == "lift":
            la = ease_out(prog(t, (lift_t or t0 + 1.5), 0.4))
            cv2.arrowedLine(img, (int(cx - half_bot - 120), base_y + 40), (int(cx - half_bot - 120), base_y - 140), RED, 9, cv2.LINE_AA,
                            tipLength=0.3)
            label(img, "TIRÓN HACIA ARRIBA", cx - half_bot - 120, base_y - 200, la, 46, RED)
            cv2.arrowedLine(img, (int(cx + half_bot + 120), base_y - 140), (int(cx + half_bot + 120), base_y + 40), (90, 150, 230), 9,
                            cv2.LINE_AA, tipLength=0.3)
            label(img, "SE CLAVA", cx + half_bot + 120, base_y - 200, la, 46, (90, 150, 230))
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- the anchor bolt, close up
def bolt(t, dur, mode="1882", t0=0.3, k_t=None, labels=True):
    """Cross-section of a tower foot on its sandstone pedestal.
    modes: 1882 | short | sleeve | snap | sleevefail | washer | new2011"""
    img = background("dark_grid", t)
    cx = W / 2
    top = 520
    # pedestal
    fill_poly(img, [[cx - 420, top], [cx + 420, top], [cx + 470, H], [cx - 470, H]], STONE)
    for y in range(top + 70, H, 80):
        cv2.line(img, (int(cx - 440), y), (int(cx + 440), y), STONE_DK, 2, cv2.LINE_AA)
    rng = np.random.default_rng(2)
    for _ in range(80):
        x, y = rng.uniform(cx - 420, cx + 420), rng.uniform(top + 10, H)
        cv2.circle(img, (int(x), int(y)), int(rng.uniform(1, 3)), STONE_DK, -1)
    raise_ = 0.0
    if mode in ("short", "sleeve", "snap", "sleevefail", "washer"):
        raise_ = 80.0 * (ease_out(prog(t, t0, 0.8)) if mode == "short" else 1.0)
    plate_y = top - 30 - raise_
    leg_col = IRON if mode == "1882" else STEEL
    # tower leg + base plate
    fill_poly(img, [[cx - 60, 60], [cx + 60, 60], [cx + 60, plate_y], [cx - 60, plate_y]], leg_col)
    fill_poly(img, [[cx - 200, plate_y], [cx + 200, plate_y], [cx + 200, plate_y + 30], [cx - 200, plate_y + 30]], leg_col)
    if raise_ > 0:  # shim / grout under the new plate
        fill_poly(img, [[cx - 200, plate_y + 30], [cx + 200, plate_y + 30], [cx + 200, top], [cx - 200, top]], (150, 146, 136))
    # bolts (two, left and right)
    kk = ease_out(prog(t, k_t if k_t is not None else t0 + 0.6, 0.8))
    snap_k = ease_in(prog(t, k_t if k_t is not None else t0 + 0.8, 0.6)) if mode == "snap" else 0.0
    for sgn in (-1, 1):
        bx = cx + sgn * 140
        old_top = top - 50          # the 1882 bolt reached just above the old plate
        bot = top + 360
        iron = (120, 82, 54)
        # old bolt
        cv2.line(img, (int(bx), int(old_top)), (int(bx), int(bot)), iron, 16)
        if mode == "new2011":
            continue
        if mode in ("sleeve", "snap", "sleevefail", "washer") or (mode == "short" and kk > 0):
            a = 1.0 if mode != "short" else kk
            # sleeve coupler + new extension
            layer = img.copy()
            cv2.rectangle(layer, (int(bx - 18), int(old_top - 50)), (int(bx + 18), int(old_top + 10)), (150, 156, 166), -1)
            cv2.line(layer, (int(bx), int(old_top - 50)), (int(bx), int(plate_y - 40)), (150, 156, 166), 12)
            _blend(img, layer, a)
        top_of_bolt = plate_y - 40 if mode != "1882" else plate_y - 40
        # washer + nut
        wy = plate_y - 10
        wash_lift = 0.0
        if mode == "washer":
            wash_lift = 120 * ease_io(prog(t, k_t if k_t is not None else t0 + 0.8, 1.0))
        cv2.rectangle(img, (int(bx - 40), int(wy - 8 - wash_lift)), (int(bx + 40), int(wy + 2 - wash_lift)), (176, 176, 182), -1)
        cv2.rectangle(img, (int(bx - 26), int(wy - 40 - wash_lift)), (int(bx + 26), int(wy - 8 - wash_lift)), (110, 110, 118), -1)
        if mode == "1882":
            cv2.line(img, (int(bx), int(plate_y - 40)), (int(bx), int(plate_y + 30)), iron, 16)
        if mode in ("sleevefail", "washer") and (sgn < 0 or mode == "washer"):
            ck = ease_out(prog(t, k_t if k_t is not None else t0 + 0.8, 0.8)) if mode == "sleevefail" else (1.0 if wash_lift > 60 else 0.0)
            for j in range(4):
                y = old_top - 44 + j * 14
                cv2.line(img, (int(bx - 18), int(y)), (int(bx - 18 + 30 * ck), int(y + 6)), (20, 20, 20), 2, cv2.LINE_AA)
        if mode == "snap" and sgn < 0 and snap_k > 0:
            gap = 30 * snap_k
            y = top + 120
            cv2.rectangle(img, (int(bx - 12), int(y - gap / 2)), (int(bx + 12), int(y + gap / 2)), STONE, -1)
    if mode == "new2011":
        k2 = ease_out(prog(t, t0, 1.2))
        for j, (dx, deep) in enumerate(((-180, False), (-100, True), (100, True), (180, False))):
            bx = cx + dx
            depth = (H - top) * (1.0 if deep else 0.55) * k2
            cv2.line(img, (int(bx), int(plate_y - 30)), (int(bx), int(top + depth)), (176, 182, 196), 12)
        if labels:
            label(img, "2011: CUATRO ANCLAJES POR PATA", W / 2, 120, ease_out(prog(t, t0, 0.4)), 60, YELLOW)
            label(img, "DOS SE CLAVAN 70 PIES EN LA ROCA", W / 2, 200, ease_out(prog(t, t0 + 1.0, 0.4)), 50, WHITE)
        _tag(img, "ESQUEMA")
        return img
    if labels:
        if mode == "1882":
            label(img, "PEDESTAL DE ARENISCA · 1882", cx, H - 70, ease_out(prog(t, t0, 0.4)), 50, INK)
            label(img, "PERNO DE HIERRO · ~1 PULGADA", cx + 360, top - 150, ease_out(prog(t, t0 + 0.6, 0.4)), 44, YELLOW, anchor="l")
            cv2.line(img, (int(cx + 160), int(top - 60)), (int(cx + 340), int(top - 140)), YELLOW, 2, cv2.LINE_AA)
        if mode == "short":
            label(img, "EL PUENTE NUEVO QUEDA MÁS ALTO…", W / 2, 120, ease_out(prog(t, t0, 0.4)), 56, WHITE)
            label(img, "…Y EL PERNO VIEJO, CORTO", W / 2, 200, ease_out(prog(t, t0 + 0.9, 0.4)), 56, YELLOW)
            label(img, "EMPALME: UN MANGUITO DE ACERO", cx + 360, top - 170, kk, 44, (180, 190, 210), anchor="l")
        if mode == "sleeve":
            label(img, "MANGUITO DE 1900", cx + 360, top - 170, ease_out(prog(t, t0, 0.4)), 46, (180, 190, 210), anchor="l")
            label(img, "PERNO DE 1882", cx + 360, top + 120, ease_out(prog(t, t0 + 0.4, 0.4)), 46, (200, 140, 90), anchor="l")
        if mode == "snap":
            label(img, "1 DE CADA 4: EL PERNO DE 1882 SE PARTIÓ", W / 2, 140, ease_out(prog(t, t0, 0.4)), 54, RED)
        if mode == "sleevefail":
            label(img, "3 DE CADA 4: FALLÓ EL MANGUITO", W / 2, 140, ease_out(prog(t, t0, 0.4)), 54, YELLOW)
        if mode == "washer":
            label(img, "LAS GRIETAS, TAPADAS POR LA ARANDELA", W / 2, 140, ease_out(prog(t, t0, 0.4)), 54, YELLOW)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- metal fatigue: a paper clip bent again and again
def clip(t, dur, t0=0.3, snap_t=None):
    img = background("dark_grid", t)
    st = snap_t if snap_t is not None else dur - 1.0
    ang = 0.9 * math.sin((t - t0) * 6.0) if t < st else 0.9
    cx, cy = W / 2, H / 2 + 40
    # fixed half (left)
    def clip_pts(scale=1.0):
        u = np.linspace(0, 1, 120)
        pts = []
        for k in u:
            a = k * 2 * math.pi * 1.5
            r = 60 + 30 * (k > 0.5)
            pts.append([math.cos(a) * r * 2.2 * scale, math.sin(a) * r * scale])
        return np.array(pts)
    left = np.array([[-360, -50], [0, -50], [0, 50], [-360, 50], [-360, -20], [-60, -20]], np.float64) + [cx, cy]
    aa_poly(img, left, (200, 200, 210), 12)
    c, s = math.cos(ang), math.sin(ang)
    right = np.array([[0, -50], [360, -50], [360, 50], [40, 50], [40, -20], [300, -20]], np.float64)
    if t >= st:
        right = right + [60 * ease_out(prog(t, st, 0.4)), 120 * ease_in(prog(t, st, 0.8))]
    right = right @ np.array([[c, s], [-s, c]]) + [cx, cy]
    aa_poly(img, right, (200, 200, 210), 12)
    n = int(max(0, t - t0) / 0.5)
    hk = min(1.0, n / max(1, int((st - t0) / 0.5)))
    cv2.circle(img, (int(cx), int(cy - 50)), int(10 + 20 * hk), (int(80 + 170 * hk), 120, 255 - int(150 * hk)), -1, cv2.LINE_AA)
    label(img, f"DOBLECES: {n}", W / 2, 200, 0.9, 60, WHITE)
    if t >= st:
        label(img, "SE PARTE", W / 2, 880, ease_out(prog(t, st, 0.3)), 90, RED)
    else:
        label(img, "FATIGA: VIBRACIÓN TRAS VIBRACIÓN", W / 2, 880, ease_out(prog(t, t0, 0.4)), 54, YELLOW)
    return img


# ---------------------------------------------------------------- numbers and comparisons
def gauge(t, dur, t0=0.3, crit_t=None, torn_t=None):
    img = background("dark_grid", t)
    cx, cy, R = W / 2, 700, 380
    cv2.ellipse(img, (int(cx), int(cy)), (R, R), 0, 180, 360, (70, 72, 78), 30, cv2.LINE_AA)
    vmax = 140.0

    def ang(v):
        return math.pi + math.pi * v / vmax

    for v in range(0, 141, 20):
        a = ang(v)
        p0 = (int(cx + math.cos(a) * (R - 30)), int(cy + math.sin(a) * (R - 30)))
        p1 = (int(cx + math.cos(a) * (R + 16)), int(cy + math.sin(a) * (R + 16)))
        cv2.line(img, p0, p1, (180, 180, 186), 3, cv2.LINE_AA)
        label(img, str(v), cx + math.cos(a) * (R + 70), cy + math.sin(a) * (R + 70), 0.8, 40, GREY)
    ck = ease_out(prog(t, crit_t if crit_t is not None else t0, 0.5))
    if ck > 0:
        a = ang(94)
        cv2.ellipse(img, (int(cx), int(cy)), (R, R), 0, math.degrees(a), 360, RED, 30, cv2.LINE_AA)
        label(img, "VIENTO CRÍTICO: 94 MPH", W / 2, 180, ck, 60, RED)
    tk = ease_io(prog(t, torn_t if torn_t is not None else t0 + 1.4, 1.4))
    v = 94 * tk + (1.5 * math.sin(t * 13) * tk if tk < 1 else 0.0)
    a = ang(v)
    cv2.line(img, (int(cx), int(cy)), (int(cx + math.cos(a) * (R - 50)), int(cy + math.sin(a) * (R - 50))), YELLOW, 10, cv2.LINE_AA)
    cv2.circle(img, (int(cx), int(cy)), 24, YELLOW, -1, cv2.LINE_AA)
    label(img, f"TORNADO: {int(round(v))} MPH", W / 2, 860, ease_out(prog(t, torn_t if torn_t is not None else t0 + 1.4, 0.3)), 66, YELLOW)
    label(img, "≈ 150 KM/H", W / 2, 940, ease_out(prog(t, (torn_t if torn_t is not None else t0 + 1.4) + 1.0, 0.3)), 44, WHITE)
    return img


def weights(t, dur, t0=0.3):
    img = background("dark_grid", t)
    base = 820
    for i, (yr, v, col) in enumerate((("1882", 1.0, IRON), ("1900", 1.85, STEEL))):
        k = ease_out(prog(t, t0 + 0.6 * i, 0.8))
        x = W * (0.33 + 0.34 * i)
        h = 260 * v * k
        cv2.rectangle(img, (int(x - 110), int(base - h)), (int(x + 110), base), col, -1)
        label(img, yr, x, base + 60, 0.9, 64, WHITE)
        label(img, "LOCOMOTORAS", x, base + 120, 0.7, 36, GREY)
    label(img, "+85 %", W * 0.67, base - 260 * 1.85 - 70, ease_out(prog(t, t0 + 1.4, 0.4)), 110, YELLOW)
    label(img, "EL PUENTE DE HIERRO SE QUEDÓ CHICO", W / 2, 140, ease_out(prog(t, t0 + 2.0, 0.4)), 58, WHITE)
    return img


def heights(t, dur, t0=0.3, step=0.7, times=None):
    img = background("dark_grid", t)
    base = 920
    sc = 1.7
    items = [("KINZUA 1882", 301, YELLOW), ("TORRES DEL PUENTE DE BROOKLYN", 276, WHITE), ("EDIFICIO DE 30 PISOS", 300, GREY)]
    for i, (name, ft, col) in enumerate(items):
        k = ease_out(prog(t, times[i] if times else t0 + i * step, 0.6))
        if k <= 0:
            continue
        x = W * (0.2 + 0.3 * i)
        h = ft * sc * k
        if i == 0:
            for j in range(3):
                xx = x - 60 + j * 60
                cv2.line(img, (int(xx), base), (int(xx), int(base - h)), col, 6, cv2.LINE_AA)
            for y in np.arange(base, base - h, -40):
                cv2.line(img, (int(x - 60), int(y)), (int(x + 60), int(y - 40)), col, 3, cv2.LINE_AA)
                cv2.line(img, (int(x + 60), int(y)), (int(x - 60), int(y - 40)), col, 3, cv2.LINE_AA)
        elif i == 1:
            fill_poly(img, [[x - 60, base], [x + 60, base], [x + 50, base - h], [x - 50, base - h]], (150, 140, 120))
            for yy in (0.55, 0.8):
                cv2.ellipse(img, (int(x - 22), int(base - h * yy)), (14, 40), 0, 180, 360, (40, 40, 44), -1)
                cv2.ellipse(img, (int(x + 22), int(base - h * yy)), (14, 40), 0, 180, 360, (40, 40, 44), -1)
        else:
            fill_poly(img, [[x - 70, base], [x + 70, base], [x + 70, base - h], [x - 70, base - h]], (70, 74, 82))
            for y in np.arange(base - 12, base - h, -18):
                cv2.line(img, (int(x - 60), int(y)), (int(x + 60), int(y)), (110, 114, 122), 2)
        label(img, f"{ft} PIES", x, base - h - 50, k, 54, col)
        label(img, name, x, base + 50, k, 34, col)
    cv2.line(img, (60, base), (W - 60, base), (120, 122, 126), 3)
    return img


def phoenix(t, dur, t0=0.3, stave_t=None):
    img = background("dark_grid", t)
    cx, cy, R = W / 2 - 260, H / 2 + 40, 230
    n = 8
    k = ease_out(prog(t, t0, 0.8))
    for j in range(n):
        a0 = 2 * math.pi * j / n
        a1 = 2 * math.pi * (j + 1) / n
        sep = (1 - k) * 120
        mid = (a0 + a1) / 2
        ox, oy = math.cos(mid) * sep, math.sin(mid) * sep
        arc = [(cx + ox + math.cos(a) * r, cy + oy + math.sin(a) * r) for r in (R,) for a in np.linspace(a0 + 0.02, a1 - 0.02, 20)]
        inner = [(cx + ox + math.cos(a) * (R - 34), cy + oy + math.sin(a) * (R - 34)) for a in np.linspace(a1 - 0.02, a0 + 0.02, 20)]
        fill_poly(img, np.array(arc + inner), IRON)
        for a in (a0 + 0.02, a1 - 0.02):
            p0 = (cx + ox + math.cos(a) * (R - 34), cy + oy + math.sin(a) * (R - 34))
            p1 = (cx + ox + math.cos(a) * (R + 46), cy + oy + math.sin(a) * (R + 46))
            cv2.line(img, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), IRON_DK, 12, cv2.LINE_AA)
        if k > 0.95:
            for rr in (R + 10, R + 30):
                a = a0
                cv2.circle(img, (int(cx + math.cos(a) * rr), int(cy + math.sin(a) * rr)), 7, (200, 190, 170), -1, cv2.LINE_AA)
    label(img, "COLUMNA HUECA DE HIERRO FORJADO", cx, 140, ease_out(prog(t, 0.1, 0.4)), 50, WHITE)
    label(img, "SEGMENTOS CURVOS REMACHADOS", cx, 930, ease_out(prog(t, t0 + 0.9, 0.4)), 46, YELLOW)
    sk = ease_out(prog(t, stave_t if stave_t is not None else t0 + 1.6, 0.5))
    if sk > 0:
        bx, by = W * 0.78, H / 2 + 40
        layer = img.copy()
        for j in range(7):
            x = bx - 150 + j * 44
            bulge = 26 * math.sin(math.pi * (j + 0.5) / 7)
            pts = np.array([[x, by - 240], [x + 40, by - 240], [x + 40 + bulge * 0.3, by], [x + 40, by + 240], [x, by + 240],
                            [x - bulge * 0.3, by]], np.float64)
            fill_poly(layer, pts, (140, 100, 60))
            aa_poly(layer, np.vstack([pts, pts[:1]]), (90, 62, 36), 3)
        for y in (by - 160, by + 160):
            cv2.ellipse(layer, (int(bx), int(y)), (172, 16), 0, 0, 360, (70, 70, 76), 10, cv2.LINE_AA)
        _blend(img, layer, sk)
        label(img, "COMO LAS TABLAS DE UN BARRIL", bx, 930, sk, 46, YELLOW)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- recreated reports
def _paper(pw, ph, col=PAPER, seed=0):
    rng = np.random.default_rng(seed)
    paper = np.full((ph, pw, 3), col, np.float32) + rng.normal(0, 4, (ph, pw, 1))
    return np.clip(paper, 0, 255).astype(np.uint8)


def _ptxt(paper, s, x, y, size, col=INK, f="type", a=1.0, anchor="l"):
    sp = text_sprite(s, f, size, col, False)
    xx = x if anchor == "l" else x - sp.w / 2
    over(paper, sp, xx - 24, y - sp.h / 2, a)


def report(t, dur, kind="2002", t0=0.3, step=0.7, times=None, hl_t=None):
    img = background("dark_grid", t)
    pw, ph = 1200, 920
    paper = _paper(pw, ph, PAPER, 4)
    if kind == "2002":
        head = ("INSPECCIÓN DEL VIADUCTO KINZUA", "PENNSYLVANIA · 2002")
        rows = ["ACERO OXIDADO", "CIMIENTOS DE CONCRETO AGRIETADOS", "PERNOS DE ANCLAJE MUY CORROÍDOS"]
        hl = 2
        foot = "RIESGO: UN VIENTO FUERTE DE COSTADO PODRÍA ARRANCAR LAS TORRES DE SUS PEDESTALES"
    else:
        head = ("INFORME TÉCNICO DEL DERRUMBE", "PENNSYLVANIA · DICIEMBRE DE 2003")
        rows = ["FALLOS EN LOS ANCLAJES DEL LADO DEL VIENTO", "1 DE CADA 4: PERNO DE 1882 PARTIDO",
                "3 DE CADA 4: MANGUITOS DE 1900 ROTOS", "GRIETAS DE FATIGA PREVIAS, BAJO LAS ARANDELAS"]
        hl = 0
        foot = "RESISTENCIA POR TORRE: ~30 T DE TIRÓN · VIENTO CRÍTICO: 94 MPH"
    _ptxt(paper, head[0], pw / 2, 80, 44, INK, "serif", anchor="c")
    _ptxt(paper, head[1], pw / 2, 140, 30, INK, "type", anchor="c")
    cv2.line(paper, (60, 180), (pw - 60, 180), (120, 112, 100), 2)
    for i, r in enumerate(rows):
        a = ease_out(prog(t, times[i] if times else t0 + i * step, 0.4))
        y = 260 + i * 100
        _ptxt(paper, "· " + r, 80, y, 40, INK, "type", a)
    ht = hl_t if hl_t is not None else (times[hl] if times else t0 + hl * step) + 0.4
    hk = ease_out(prog(t, ht, 0.5))
    if hk > 0:
        layer = paper.copy()
        y = 260 + hl * 100
        cv2.rectangle(layer, (64, y - 34), (int(64 + (pw - 130) * hk), y + 34), (60, 200, 240), -1)
        cv2.addWeighted(layer, 0.45, paper, 0.55, 0, paper)
        _ptxt(paper, "· " + rows[hl], 80, y, 40, INK, "type")
    fk = ease_out(prog(t, (times[-1] if times else t0 + len(rows) * step) + 0.6, 0.5))
    words = foot.split()
    line1 = " ".join(words[: len(words) // 2])
    line2 = " ".join(words[len(words) // 2:])
    _ptxt(paper, line1, 80, ph - 170, 34, (150, 30, 40), "type", fk)
    _ptxt(paper, line2, 80, ph - 120, 34, (150, 30, 40), "type", fk)
    sprite = Sprite(np.dstack([paper, np.full(paper.shape[:2], 255, np.uint8)]))
    over_center(img, sprite, W / 2, H / 2 + 10, 1.0, 0.95)
    label(img, "RECREACIÓN", W - 150, H - 46, 0.75, 30, GREY)
    return img


def four_bases(t, dur, t0=0.3, t1=None):
    img = background("dark_grid", t)
    t1 = t1 if t1 is not None else t0 + 1.2
    for j in range(4):
        x = W * (0.2 + 0.2 * j)
        y = 560
        a = ease_out(prog(t, t0 + 0.15 * j, 0.4))
        fill_poly(img, [[x - 90, y + 60], [x + 90, y + 60], [x + 100, y + 200], [x - 100, y + 200]], STONE)
        cv2.line(img, (int(x), int(y - 140)), (int(x), int(y + 180)), (130, 88, 58), 14)
        if j == 0:
            k = ease_out(prog(t, t1, 0.5))
            cv2.rectangle(img, (int(x - 14), int(y + 10 - 16 * k)), (int(x + 14), int(y + 10 + 16 * k)), (16, 17, 19), -1)
            label(img, "PERNO 1882 PARTIDO", x, y + 280, k, 34, RED)
        else:
            k = ease_out(prog(t, t1 + 0.6, 0.5))
            cv2.rectangle(img, (int(x - 20), int(y - 80)), (int(x + 20), int(y - 20)), (150, 156, 166), -1)
            for q in range(3):
                cv2.line(img, (int(x - 20), int(y - 74 + q * 18)), (int(x - 20 + 34 * k), int(y - 68 + q * 18)), (20, 20, 20), 3)
            label(img, "MANGUITO ROTO", x, y + 280, k, 34, YELLOW)
        if a < 1:
            layer = background("dark_grid", t)
            _blend(img, layer, 1 - a)
    label(img, "LO QUE FALLÓ, DE CADA 4 BASES", W / 2, 140, ease_out(prog(t, 0.1, 0.4)), 58, WHITE)
    _tag(img, "ESQUEMA")
    return img


def visible_vs_hidden(t, dur, t0=0.3, t1=None):
    img = background("dark_grid", t)
    t1 = t1 if t1 is not None else t0 + 1.5
    a = ease_out(prog(t, t0, 0.4))
    b = ease_out(prog(t, t1, 0.4))
    label(img, "LO QUE SE VEÍA", W * 0.3, 260, a, 64, WHITE)
    label(img, "1900 · ACERO NUEVO", W * 0.3, 380, a, 80, (150, 170, 200))
    label(img, "LO QUE LO SUJETABA", W * 0.7, 260, b, 64, WHITE)
    label(img, "1882 · PERNOS DE HIERRO", W * 0.7, 380, b, 80, (210, 140, 90))
    label(img, "+ EMPALMES DE 1900", W * 0.7, 470, b, 54, YELLOW)
    cv2.line(img, (W // 2, 200), (W // 2, 560), (70, 72, 76), 2)
    return img


def detour(t, dur, t0=0.3, t1=None):
    """Going round the valley (down to the floor and up again) versus straight across the top."""
    img = _grad(SKY_TOP, SKY_BOT)
    xs, ys = _valley(img)
    t1 = t1 if t1 is not None else t0 + 2.2
    # winding route: switchbacks down one side and up the other
    pts = []
    for k in np.linspace(0, 1, 400):
        x = lerp(X0, X1, k)
        yb = float(np.interp(x, xs, ys))
        pts.append([x + 60 * math.sin(k * 26), yb - 6])
    pts = np.array(pts)
    k = ease_io(prog(t, t0, 1.8))
    layer = img.copy()
    part = partial_line(pts, k)
    if len(part) > 1:
        for i in range(0, len(part) - 1, 2):
            cv2.line(layer, tuple(part[i].astype(int)), tuple(part[i + 1].astype(int)), (230, 120, 90), 5, cv2.LINE_AA)
    _blend(img, layer, 1.0)
    label(img, "RODEAR: BAJAR Y VOLVER A SUBIR", W / 2, 140, ease_out(prog(t, t0, 0.4)) * (1 - 0.6 * prog(t, t1, 0.3)), 56, (240, 150, 120))
    k2 = ease_io(prog(t, t1, 1.0))
    if k2 > 0:
        cv2.line(img, (int(X0), int(DECK_Y)), (int(lerp(X0, X1, k2)), int(DECK_Y)), YELLOW, 8, cv2.LINE_AA)
        label(img, "CRUZAR POR ARRIBA, EN LÍNEA RECTA", W / 2, 210, ease_out(prog(t, t1, 0.4)), 60, YELLOW)
    _tag(img)
    return img


def fscale(t, dur, t0=0.2):
    img = background("dark_grid", t)
    names = ["F0", "F1", "F2", "F3", "F4", "F5"]
    for i, n in enumerate(names):
        a = ease_out(prog(t, t0 + 0.12 * i, 0.3))
        x = W * (0.17 + 0.132 * i)
        h = 80 + 60 * i
        col = YELLOW if n == "F1" else (90, 92, 98)
        cv2.rectangle(img, (int(x - 60), int(760 - h * a)), (int(x + 60), 760), col, -1)
        label(img, n, x, 820, a, 64, YELLOW if n == "F1" else WHITE)
    label(img, "ESCALA DE TORNADOS", W / 2, 160, ease_out(prog(t, 0.1, 0.4)), 60, GREY)
    label(img, "F1: UNO DE LOS NIVELES MÁS BAJOS", W / 2, 960, ease_out(prog(t, t0 + 0.9, 0.4)), 58, YELLOW)
    return img
