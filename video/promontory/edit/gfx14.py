"""Promontory Summit (1862-1942): diagrams drawn in code for this episode."""
import json
import math
import os

import cv2
import numpy as np

from engine import BLACK, H, RED, W, WHITE, YELLOW, clamp, ease_back, ease_in, ease_io, ease_out, lerp, prog
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

GOLD = (236, 190, 70)
GOLD_DK = (150, 110, 30)
GOLD_HI = (255, 236, 160)
IRON = (96, 92, 88)
IRON_HI = (150, 146, 140)
WOOD = (120, 84, 50)
WOOD_DK = (78, 54, 32)
LAUREL = (150, 96, 56)
DIRT = (150, 124, 88)
DIRT_DK = (110, 90, 64)
WATER = (52, 104, 150)
WATER_HI = (110, 170, 220)
PINK = (196, 96, 110)
TEAL = (70, 150, 140)
SKY_T = (22, 30, 44)
SKY_B = (120, 104, 90)
BLUE = (110, 170, 220)
RED_ = (230, 70, 60)
GREEN = (90, 200, 110)
CP_COL = (230, 110, 60)    # Central Pacific
UP_COL = (110, 170, 230)   # Union Pacific

_PROF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pm_profile.json")))


def _grade(prof, win=8, sm=4):
    """A railroad grade has no needle peaks: rolling minimum (~3 km) then smoothing (~1.5 km)."""
    a = np.array([[p[0], p[1]] for p in prof], np.float64)
    e = a[:, 1].copy()
    m = np.array([e[max(0, i - win):i + win + 1].min() for i in range(len(e))])
    k = np.exp(-0.5 * (np.arange(-3 * sm, 3 * sm + 1) / sm) ** 2)
    k /= k.sum()
    pad = np.pad(m, 3 * sm, mode="edge")
    a[:, 1] = np.convolve(pad, k, mode="valid")
    return a


_OLD = _grade(_PROF["old"])
_CUT = _grade(_PROF["cutoff"])
_CUT[:, 1] = np.maximum(_CUT[:, 1], 4212)


def _blend(img, layer, a):
    if a > 0.001:
        cv2.addWeighted(layer, min(a, 1.0), img, 1 - min(a, 1.0), 0, img)


def _tag(img, txt="ESQUEMA", a=0.7):
    label(img, txt, W - 40, H - 46, a, 30, GREY, anchor="r")


def _grad(top, bot):
    g = np.linspace(0, 1, H)[:, None, None]
    img = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    return np.repeat(img, W, axis=1).astype(np.uint8)


def _loco(img, x, y, s=1.0, col=(40, 40, 44), trim=(200, 60, 50), facing=1, smoke=0.0, t=0.0, a=1.0, stack="funnel"):
    """1860s 4-4-0 in side view; (x, y) = rail under the middle; facing=1 -> pointing right."""
    tgt = img.copy() if a < 0.999 else img
    f = facing

    def P(pts):
        p = np.array(pts, np.float32)
        p[:, 0] *= f
        return p * s + [x, y]
    fill_poly(tgt, P([[-150, -30], [110, -30], [110, -40], [-150, -40]]), (30, 30, 32))           # frame
    fill_poly(tgt, P([[-60, -40], [90, -40], [90, -96], [-60, -96]]), col)                          # boiler
    fill_poly(tgt, P([[-150, -40], [-62, -40], [-62, -150], [-150, -150]]), trim)                    # cab
    fill_poly(tgt, P([[-160, -150], [-52, -150], [-52, -162], [-160, -162]]), (30, 30, 32))           # cab roof
    fill_poly(tgt, P([[-138, -138], [-74, -138], [-74, -104], [-138, -104]]), (230, 210, 140))       # window
    if stack == "funnel":
        fill_poly(tgt, P([[54, -96], [78, -96], [100, -170], [32, -170]]), (30, 30, 32))
    else:
        fill_poly(tgt, P([[56, -96], [76, -96], [76, -160], [56, -160]]), (30, 30, 32))
    fill_poly(tgt, P([[0, -96], [24, -96], [24, -120], [0, -120]]), GOLD)                            # dome
    fill_poly(tgt, P([[90, -40], [140, -10], [90, -10]]), (30, 30, 32))                               # pilot
    cv2.circle(tgt, (int(x + f * 98 * s), int(y - 110 * s)), int(14 * s), GOLD, -1, cv2.LINE_AA)    # headlamp
    for wx, r in ((-110, 34), (-40, 34), (40, 20), (78, 20)):
        cx, cy = int(x + f * wx * s), int(y - r * s)
        cv2.circle(tgt, (cx, cy), int(r * s), trim if r > 30 else (40, 40, 44), -1, cv2.LINE_AA)
        cv2.circle(tgt, (cx, cy), int(r * s), (20, 20, 22), max(2, int(4 * s)), cv2.LINE_AA)
        cv2.circle(tgt, (cx, cy), int(5 * s), (20, 20, 22), -1, cv2.LINE_AA)
    if smoke > 0:
        rng = np.random.default_rng(7)
        for k in range(16):
            ph = (t * 0.5 + k / 16) % 1.0
            cx = x + f * (66 - ph * 120) * s + rng.uniform(-10, 10)
            cy = y - (175 + ph * 260) * s
            cv2.circle(tgt, (int(cx), int(cy)), int((10 + ph * 34) * s), (210, 210, 214), -1, cv2.LINE_AA)
    if tgt is not img:
        _blend(img, tgt, a)


def _rails(img, y, x0=0, x1=W, s=1.0, ties=True, col=(150, 146, 140), a=1.0):
    tgt = img.copy() if a < 0.999 else img
    if ties:
        for x in range(int(x0), int(x1), int(46 * s)):
            cv2.rectangle(tgt, (x, int(y)), (x + int(26 * s), int(y + 12 * s)), WOOD_DK, -1)
    cv2.rectangle(tgt, (int(x0), int(y - 6 * s)), (int(x1), int(y)), col, -1)
    if tgt is not img:
        _blend(img, tgt, a)


# ---------------------------------------------------------------- the spike(s)
def _spike(img, cx, cy, s=1.0, metal="gold", a=1.0, rot=0.0, text=True):
    """A railroad spike pointing down; (cx, cy) = centre of the head."""
    tgt = img.copy()
    body, hi, dk = (GOLD, GOLD_HI, GOLD_DK) if metal == "gold" else (IRON, IRON_HI, (60, 58, 56))
    pts = np.array([[-60, -26], [60, -26], [60, 0], [22, 0], [22, 440], [0, 500], [-22, 440], [-22, 0], [-60, 0]], np.float32)
    c, sn = math.cos(rot), math.sin(rot)
    R = np.array([[c, -sn], [sn, c]], np.float32)
    P = (pts * s) @ R.T + [cx, cy]
    fill_poly(tgt, P, body)
    hl = (np.array([[-16, 10], [-6, 10], [-6, 430], [-16, 420]], np.float32) * s) @ R.T + [cx, cy]
    fill_poly(tgt, hl, hi)
    aa_poly(tgt, P, dk, max(2, int(3 * s)), closed=True)
    if text and metal == "gold" and abs(rot) < 0.01:
        for k, yy in enumerate(range(60, 400, 52)):
            cv2.line(tgt, (int(cx + 4 * s), int(cy + yy * s)), (int(cx + 14 * s), int(cy + (yy + 30) * s)), dk, max(1, int(2 * s)), cv2.LINE_AA)
    _blend(img, tgt, a)


def spike(t, dur, t0=0.3, mode="gold", swap_t=None, t_names=None, t_phrase=None, t_tie=None, inch=True):
    """gold: the 1869 golden spike, engraved, on the polished laurel tie. swap: after swap_t the gold one is pulled and an
    ordinary iron spike goes in. pull: 1942, a bar lifts an iron spike one inch."""
    img = background("dark_grid", t)
    cx, top = 760, 250
    # polished laurel tie in section + rail
    fill_poly(img, np.array([[360, 700], [1160, 700], [1160, 860], [360, 860]], np.float32), LAUREL if mode != "pull" else WOOD)
    for k in range(6):
        cv2.line(img, (360, 712 + k * 24), (1160, 708 + k * 25), (170, 112, 66) if mode != "pull" else WOOD_DK, 2, cv2.LINE_AA)
    fill_poly(img, np.array([[860, 640], [1100, 640], [1100, 700], [860, 700]], np.float32), IRON_HI)
    if mode == "gold":
        k = ease_out(prog(t, t0, 0.8))
        _spike(img, cx, lerp(-300, top, k), 0.9, "gold", 1.0)
        a = ease_out(prog(t, t0 + 0.9, 0.4))
        label(img, "EL CLAVO DE ORO", 1460, 300, a, 86, GOLD)
        label(img, "17,6 QUILATES · ENCARGO DE DAVID HEWES", 1460, 390, ease_out(prog(t, t0 + 1.3, 0.4)), 38, WHITE)
        label(img, "NOMBRES DE LOS DIRECTIVOS GRABADOS", 1460, 450, ease_out(prog(t, t_names if t_names is not None else t0 + 1.7, 0.4)), 38, GREY)
        label(img, "«QUE DIOS MANTENGA UNIDO AL PAÍS»", 1460, 520, ease_out(prog(t, t_phrase if t_phrase is not None else t0 + 2.1, 0.4)), 44, YELLOW)
        label(img, "DURMIENTE DE MADERA PULIDA", 760, 920, ease_out(prog(t, t_tie if t_tie is not None else t0 + 2.5, 0.4)), 50, (230, 180, 120))
    elif mode == "swap":
        st = swap_t if swap_t is not None else t0 + 1.5
        k_out = ease_in(prog(t, st, 0.8))
        _spike(img, cx, top - 900 * k_out, 0.9, "gold", 1.0 - 0.3 * k_out)
        k_in = ease_out(prog(t, st + 1.0, 0.7))
        if k_in > 0:
            _spike(img, cx, lerp(-300, top, k_in), 0.9, "iron", 1.0)
        label(img, "UNOS MINUTOS EN LA VÍA", 1460, 330, ease_out(prog(t, t0, 0.4)), 70, GOLD)
        label(img, "LO SACARON…", 1460, 450, ease_out(prog(t, st, 0.4)), 60, WHITE)
        label(img, "…Y PUSIERON UNO DE HIERRO", 1460, 540, ease_out(prog(t, st + 1.2, 0.4)), 60, IRON_HI)
    elif mode == "pull":
        lift = ease_io(prog(t, t0 + 0.8, 1.2)) * 26
        _spike(img, cx, top - lift, 0.9, "iron", 1.0, text=False)
        # the bar
        bx = np.array([[cx - 30, top + 6 - lift], [cx + 520, top - 300 - lift * 3], [cx + 540, top - 280 - lift * 3], [cx - 10, top + 26 - lift]], np.float32)
        fill_poly(img, bx, (60, 60, 64))
        label(img, "8 DE SEPTIEMBRE DE 1942", 1460, 520, ease_out(prog(t, t0, 0.4)), 56, YELLOW)
        if inch:
            label(img, "UNA PULGADA", 1460, 610, ease_back(prog(t, t0 + 1.6, 0.4)), 90, WHITE)
            label(img, "≈ 2,5 CM", 1460, 700, ease_out(prog(t, t0 + 2.0, 0.4)), 46, GREY)
        else:
            label(img, "EL GOBERNADOR TIRA DEL CLAVO", 1460, 610, ease_out(prog(t, t0 + 0.6, 0.4)), 50, WHITE)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- paid by the mile
def paid(t, dur, t0=0.3):
    img = background("dark_grid", t)
    k = ease_io(prog(t, t0, dur - t0 - 0.6))
    label(img, "EL GOBIERNO PAGABA POR CADA MILLA", W / 2, 120, ease_out(prog(t, 0.1, 0.4)), 64, WHITE)
    for i, (name, col, miles) in enumerate((("CENTRAL PACIFIC", CP_COL, 690), ("UNION PACIFIC", UP_COL, 1086))):
        y = 360 + i * 300
        label(img, name, 120, y - 70, 1.0, 54, col, anchor="l")
        L = 1300 * k * miles / 1086
        cv2.rectangle(img, (120, y), (120 + int(L), y + 60), col, -1)
        for m in range(0, int(L), 52):
            cv2.line(img, (120 + m, y), (120 + m, y + 60), (20, 20, 20), 2)
        label(img, f"{int(miles * k)} MILLAS", 160 + L, y + 30, 1.0, 50, WHITE, anchor="l")
        n = int(k * 14 * miles / 1086)
        for j in range(n):
            cx, cy = 140 + j * 54, y + 120
            cv2.circle(img, (cx, cy), 20, GOLD, -1, cv2.LINE_AA)
            label(img, "$", cx, cy + 2, 1.0, 34, GOLD_DK)
    label(img, "DINERO + TIERRAS", W / 2, 930, ease_out(prog(t, t0 + 1.0, 0.4)), 58, GOLD)
    label(img, "CUANTAS MÁS MILLAS, MÁS COBRABAN", W / 2, 1010, ease_out(prog(t, t0 + 2.0, 0.4)), 50, YELLOW)
    _tag(img, "ESQUEMA · MILLAS HASTA PROMONTORY")
    return img


# ---------------------------------------------------------------- one foot a day through granite
def granite(t, dur, t0=0.3):
    img = background("dark_grid", t)
    x0, x1, y0, y1 = 200, 1720, 260, 860
    rng = np.random.default_rng(5)
    fill_poly(img, np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], np.float32), (112, 108, 104))
    for _ in range(900):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        c = int(rng.uniform(70, 170))
        cv2.circle(img, (int(x), int(y)), int(rng.uniform(1, 4)), (c, c, c - 6), -1)
    days = int(ease_io(prog(t, t0, dur - t0 - 0.8)) * 30)
    ft = 30 * 1.0  # px per foot below
    pxft = 30
    bore = days * pxft
    cv2.rectangle(img, (x0, 520), (x0 + bore, 760), (16, 16, 18), -1)
    cv2.ellipse(img, (x0 + bore, 640), (40, 120), 0, -90, 90, (16, 16, 18), -1, cv2.LINE_AA)
    # a man for scale (6 ft)
    mx = x0 + max(bore - 40, 40)
    cv2.circle(img, (mx, 760 - 6 * pxft + 14), 14, (210, 200, 180), -1, cv2.LINE_AA)
    cv2.line(img, (mx, 760 - 6 * pxft + 28), (mx, 760 - 70), (210, 200, 180), 10)
    cv2.line(img, (mx, 760 - 70), (mx - 16, 760), (210, 200, 180), 8)
    cv2.line(img, (mx, 760 - 70), (mx + 16, 760), (210, 200, 180), 8)
    label(img, "GRANITO", W / 2 + 300, 330, 1.0, 70, (220, 220, 220))
    label(img, f"DÍA {max(days, 1)}", 340, 160, ease_out(prog(t, t0, 0.3)), 90, YELLOW, anchor="l")
    label(img, f"{days} PIES" if days != 1 else "1 PIE", 1300, 160, ease_out(prog(t, t0, 0.3)), 90, WHITE)
    label(img, "EN ALGUNOS TÚNELES: UN PIE (30 CM) AL DÍA", W / 2, 960, ease_out(prog(t, t0 + 0.6, 0.4)), 54, YELLOW)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- two grades, one train
def parallel(t, dur, t0=0.3, blast_t=None):
    """Bird's-eye: two grades side by side across the desert; blasts from the rival crew."""
    img = np.full((H, W, 3), (150, 132, 100), np.uint8)
    rng = np.random.default_rng(11)
    for _ in range(500):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        cv2.circle(img, (int(x), int(y)), int(rng.uniform(3, 9)), (122, 120, 82), -1, cv2.LINE_AA)   # sagebrush
    k = ease_io(prog(t, t0, 2.4))
    for i, (y, col, name) in enumerate(((470, CP_COL, "CENTRAL PACIFIC"), (610, UP_COL, "UNION PACIFIC"))):
        x1 = 80 + (W - 160) * k
        cv2.rectangle(img, (80, y - 34), (int(x1), y + 34), DIRT_DK, -1)
        cv2.rectangle(img, (80, y - 22), (int(x1), y + 22), DIRT, -1)
        cv2.line(img, (80, y), (int(x1), y), col, 6, cv2.LINE_AA)
        label(img, name, 120, y - 80 if i == 0 else y + 80, ease_out(prog(t, t0 + 0.3, 0.4)), 46, col, anchor="l")
    bt = blast_t if blast_t is not None else t0 + 2.2
    for j in range(3):
        ph = prog(t, bt + j * 0.5, 0.9)
        if 0 < ph < 1:
            cx, cy = 600 + j * 380, 610 + rng.integers(-8, 8)
            r = int(30 + 140 * ease_out(ph))
            layer = img.copy()
            cv2.circle(layer, (cx, cy), r, (250, 220, 160), -1, cv2.LINE_AA)
            cv2.circle(layer, (cx, cy), int(r * 0.55), (255, 150, 60), -1, cv2.LINE_AA)
            _blend(img, layer, 0.8 * (1 - ph))
    label(img, "≈ 250 MILLAS DE TERRAPLENES PARALELOS", W / 2, 120, ease_out(prog(t, 0.1, 0.4)), 60, WHITE, box=(20, 20, 20))
    label(img, "DOS CAMINOS PARA UN SOLO TREN", W / 2, 960, ease_out(prog(t, bt + 1.0, 0.4)), 64, YELLOW, box=(20, 20, 20))
    _tag(img, "ESQUEMA · VISTA DESDE ARRIBA")
    return img


# ---------------------------------------------------------------- ten miles in one day
def tenmiles(t, dur, t0=0.3):
    img = _grad((40, 60, 96), (200, 170, 120))
    k = ease_io(prog(t, t0, dur - t0 - 0.8))
    # sun arc
    ang = math.pi * (1 - k)
    sx, sy = W / 2 + math.cos(ang) * 760, 640 - math.sin(ang) * 460
    cv2.circle(img, (int(sx), int(sy)), 46, (255, 220, 120), -1, cv2.LINE_AA)
    fill_poly(img, np.array([[0, 700], [W, 700], [W, H], [0, H]], np.float32), (140, 122, 92))
    _rails(img, 800, 0, int(80 + (W - 160) * k))
    label(img, "28 DE ABRIL DE 1869", W / 2, 110, 1.0, 60, WHITE, box=(20, 20, 20))
    label(img, f"{10 * k:.1f} MILLAS".replace(".", ","), W / 2, 230, 1.0, 120, YELLOW)
    label(img, "≈ 16 KM DE VÍA EN UN SOLO DÍA", W / 2, 960, ease_out(prog(t, t0 + 1.0, 0.4)), 56, WHITE, box=(20, 20, 20))
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- DONE, by telegraph
MORSE = {"D": "-..", "O": "---", "N": "-.", "E": "."}


def morse(t, dur, t0=0.3):
    img = background("dark_grid", t)
    x = 330
    tt = t0
    for ch in "DONE":
        a = ease_back(prog(t, tt, 0.3))
        label(img, ch, x + 150, 330, a, 170, WHITE)
        cx = x + 150 - (len(MORSE[ch]) - 1) * 42
        for j, sym in enumerate(MORSE[ch]):
            b = ease_out(prog(t, tt + 0.1 + j * 0.12, 0.15))
            if b <= 0:
                continue
            px = int(cx + j * 84)
            if sym == ".":
                cv2.circle(img, (px, 540), 18, YELLOW, -1, cv2.LINE_AA)
            else:
                cv2.rectangle(img, (px - 34, 528), (px + 34, 552), YELLOW, -1)
        x += 320
        tt += 0.55
    label(img, "«HECHO»", W / 2, 760, ease_back(prog(t, tt + 0.2, 0.4)), 130, YELLOW)
    label(img, "UNA SOLA PALABRA, A TODO EL PAÍS", W / 2, 900, ease_out(prog(t, tt + 0.7, 0.4)), 54, WHITE)
    _tag(img, "TELÉGRAFO · CÓDIGO MORSE")
    return img


# ---------------------------------------------------------------- the profile: over the hill or across the lake
def profile(t, dur, t0=0.3, mode="old", step=1.2):
    """Side view Lucin -> Ogden (both lines scaled to the same width). old: the line climbs Promontory (helper engines).
    both: + the cutoff, flat on the lake."""
    img = background("dark_grid", t)
    X0, X1, Y0, Y1 = 140, 1780, 300, 800
    lo, hi = 4000.0, 5100.0

    def P(arr):
        return np.stack([X0 + arr[:, 0] / arr[-1, 0] * (X1 - X0), Y1 - (arr[:, 1] - lo) / (hi - lo) * (Y1 - Y0)], 1)
    ly = Y1 - (4200 - lo) / (hi - lo) * (Y1 - Y0)
    layer = img.copy()
    cv2.rectangle(layer, (X0, int(ly)), (X1, Y1 + 40), WATER, -1)
    _blend(img, layer, 0.35)
    label(img, "NIVEL DEL LAGO", X1 - 10, ly + 30, 0.8, 34, WATER_HI, anchor="r")
    po = P(_OLD)
    k = ease_io(prog(t, t0, step))
    part = partial_line(po, k)
    if len(part) > 1:
        aa_poly(img, part, (20, 20, 20), 12)
        aa_poly(img, part, YELLOW, 6)
    i_sum = int(np.argmax(_OLD[:, 1]))
    sx, sy = po[i_sum]
    a = ease_out(prog(t, t0 + step * 0.7, 0.4))
    label(img, "PROMONTORY · ≈ 4.900 PIES", sx, sy - 70, a, 46, YELLOW)
    label(img, "LUCIN", X0, Y1 + 80, 1.0, 44, WHITE)
    label(img, "OGDEN", X1, Y1 + 80, 1.0, 44, WHITE)
    label(img, "LÍNEA VIEJA: POR LA LOMA DE PROMONTORY", 160, 130, ease_out(prog(t, t0, 0.4)), 50, YELLOW, anchor="l")
    if mode == "old":
        b = ease_out(prog(t, t0 + step, 0.5))
        if b > 0:
            j = int(np.searchsorted(_OLD[:, 0], _OLD[i_sum, 0] - 9.0))
            hx, hy = po[j]
            _loco(img, hx - 40, hy + 8, 0.32, facing=1, a=b, smoke=1.0, t=t)
            _loco(img, hx - 110, hy + 22, 0.32, facing=1, a=b, smoke=1.0, t=t + 0.3)
            label(img, "LOCOMOTORAS DE AYUDA", hx - 80, hy + 110, b, 40, WHITE, box=(20, 20, 20))
    else:
        kc = ease_io(prog(t, t0 + step + 0.4, step))
        part = partial_line(P(_CUT), kc)
        if len(part) > 1:
            aa_poly(img, part, (20, 20, 20), 12)
            aa_poly(img, part, (90, 220, 255), 6)
        label(img, "ATAJO DE LUCIN: POR EL LAGO", 160, 200, ease_out(prog(t, t0 + step + 0.4, 0.4)), 50, (90, 220, 255), anchor="l")
        label(img, "44 MILLAS MENOS · SIN SUBIDA", W / 2, 965, ease_back(prog(t, t0 + 2 * step + 0.6, 0.4)), 60, WHITE, box=(20, 20, 20))
    _tag(img, "PERFIL APROXIMADO · RELIEVE MAPZEN · ALTURA EXAGERADA")
    return img


# ---------------------------------------------------------------- the trestle and the fill that sank
def trestle(t, dur, t0=0.3, mode="build"):
    img = _grad((40, 52, 70), (150, 130, 110))
    wy = 600
    layer = img.copy()
    cv2.rectangle(layer, (0, wy), (W, H), WATER, -1)
    _blend(img, layer, 0.95)
    for j in range(40):
        x = (j * 97 + t * 40) % W
        cv2.line(img, (int(x), wy + 20 + (j % 5) * 60), (int(x + 40), wy + 20 + (j % 5) * 60), WATER_HI, 2, cv2.LINE_AA)
    bottom = 960
    fill_poly(img, np.array([[0, bottom], [W, bottom], [W, H], [0, H]], np.float32), (70, 60, 50))
    if mode == "build":
        k = ease_io(prog(t, t0, dur - t0 - 0.6))
        # fill on the left, trestle in the middle
        fill_poly(img, np.array([[0, wy - 30], [520, wy - 30], [700, bottom], [0, bottom]], np.float32), DIRT)
        xe = 520 + (W - 520) * k
        for x in range(560, int(xe), 70):
            cv2.line(img, (x, wy - 30), (x, bottom), WOOD, 12)
            cv2.line(img, (x - 30, bottom), (x, wy - 30), WOOD_DK, 4)
        cv2.rectangle(img, (0, wy - 46), (int(xe), wy - 30), WOOD, -1)
        _rails(img, wy - 46, 0, int(xe), 0.8)
        label(img, "RELLENO DE ROCA Y TIERRA", 260, wy - 120, ease_out(prog(t, t0, 0.4)), 44, WHITE)
        label(img, "PUENTE DE MADERA: CASI 12 MILLAS (≈ 19 KM)", 1200, wy - 120, ease_out(prog(t, t0 + 1.0, 0.4)), 46, YELLOW)
        label(img, "SOBRE EL AGUA SALADA", 1200, wy - 66, ease_out(prog(t, t0 + 1.4, 0.4)), 40, WHITE)
    else:  # sink: rock dumped from cars disappears into the soft bottom
        cyc = (t - t0) % 2.2 if t > t0 else 0
        n = int(max(0, t - t0) // 2.2)
        sink = min(1.0, n * 0.22 + ease_io(prog(cyc, 0.6, 1.4)) * 0.22)
        mound = wy - 30 + 200 * (1 - min(1.0, n * 0.25)) * 0
        top = bottom - (bottom - (wy - 30)) * (0.35 + 0.65 * ease_out(prog(t, t0, 0.1)))
        pile_h = (bottom - (wy - 20)) * (1 - 0.8 * ease_io(prog(cyc, 0.7, 1.3)))
        fill_poly(img, np.array([[700, bottom], [1220, bottom], [1060, bottom - pile_h], [860, bottom - pile_h]], np.float32), DIRT)
        sunk = (bottom + 30 + min(n, 5) * 24)
        fill_poly(img, np.array([[640, bottom], [1280, bottom], [1180, sunk + 60], [740, sunk + 60]], np.float32), DIRT_DK)
        # dump car
        cv2.rectangle(img, (820, wy - 150), (1100, wy - 70), (90, 70, 50), -1)
        _rails(img, wy - 60, 600, 1320, 0.8)
        ph = prog(cyc, 0.1, 0.6)
        if 0 < ph < 1:
            for j in range(18):
                rx = 860 + (j * 37) % 220
                ry = wy - 70 + ph * (bottom - wy + 40) + (j % 4) * 12
                cv2.circle(img, (int(rx), int(ry)), 9, DIRT, -1, cv2.LINE_AA)
        label(img, f"TONELADAS Y TONELADAS… (CARGA {n + 1})", W / 2, 110, 1.0, 54, WHITE, box=(20, 20, 20))
        label(img, "EL FONDO SE TRAGABA EL RELLENO", W / 2, 1020, ease_out(prog(t, t0 + 1.4, 0.4)), 58, YELLOW, box=(20, 20, 20))
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- 1908: a dozen trains a day vs one a week
def traffic(t, dur, t0=0.3, row2=None):
    img = background("dark_grid", t)
    label(img, "1908", W / 2, 90, 1.0, 70, YELLOW)
    rows = (("ATAJO DEL LAGO", (90, 220, 255), 24, "≈ 12 TRENES AL DÍA EN CADA SENTIDO"),
            ("PROMONTORY", YELLOW, 1, "1 TREN A LA SEMANA"))
    for i, (name, col, n, cap) in enumerate(rows):
        y = 360 + i * 380
        ti = t0 if i == 0 else (row2 if row2 is not None else t0 + 0.6)
        label(img, name, 120, y - 120, ease_out(prog(t, ti, 0.4)), 56, col, anchor="l")
        cv2.line(img, (120, y), (W - 120, y), (110, 110, 110), 4)
        for j in range(n):
            if n > 1:
                d = ((t - t0) * 260 * (1 if j % 2 == 0 else -1) + j * (W - 240) / n * 2) % (W - 240)
                x = 120 + d
                yy = y - 26 if j % 2 == 0 else y + 26
            else:
                x = 120 + (W - 240) * clamp((t - ti) / max(dur - ti, 1) * 0.3)
                yy = y - 26
            if t > ti:
                cv2.rectangle(img, (int(x - 60), int(yy - 14)), (int(x + 60), int(yy + 14)), col, -1)
        label(img, cap, W / 2, y + 110, ease_out(prog(t, ti + 0.3, 0.4)), 50, WHITE)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- scrap drive
def scrap(t, dur, t0=0.3):
    img = background("dark_grid", t)
    items = [("OLLAS", (140, 140, 140)), ("VERJAS", (90, 90, 96)), ("CARROS", (120, 70, 50)), ("REJAS", (70, 70, 74)),
             ("CAÑONES", (60, 80, 60)), ("RIELES", (150, 146, 140))]
    pile_k = ease_io(prog(t, t0 + 0.4 * len(items), 1.0))
    for i, (name, col) in enumerate(items):
        a = ease_out(prog(t, t0 + i * 0.4, 0.3))
        fall = ease_in(prog(t, t0 + i * 0.4 + 0.4, 0.5))
        x = 260 + i * 280
        y = lerp(360, 760, fall)
        if a > 0:
            cv2.rectangle(img, (int(x - 70), int(y - 40)), (int(x + 70), int(y + 40)), col, -1)
            label(img, name, x, y - 90 if fall < 0.5 else 300, a * (1 - 0.6 * fall), 44, WHITE)
    fill_poly(img, np.array([[400, 900], [1520, 900], [1260, 900 - 200 * pile_k], [660, 900 - 200 * pile_k]], np.float32), (110, 100, 90))
    label(img, "CHATARRA PARA LA GUERRA", W / 2, 110, ease_out(prog(t, 0.1, 0.4)), 70, YELLOW)
    label(img, "BARCOS · TANQUES · CAÑONES", W / 2, 990, ease_out(prog(t, t0 + 2.6, 0.4)), 56, WHITE)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- tearing up the line
def teardown(t, dur, t0=0.3, speed=1.0, title=True):
    """Side view: a work train backs up; behind it the rails are lifted and only the bare embankment remains."""
    img = _grad((70, 90, 120), (210, 180, 130))
    gy = 760
    fill_poly(img, np.array([[0, gy + 10], [W, gy + 10], [W, H], [0, H]], np.float32), (150, 130, 96))
    fill_poly(img, np.array([[0, gy - 30], [W, gy - 30], [W, gy + 30], [0, gy + 30]], np.float32), DIRT)
    k = ease_io(prog(t, t0, (dur - t0 - 0.4) / speed))
    edge = W - 200 - 1300 * k            # rails exist only left of the edge
    _rails(img, gy - 30, 0, int(edge))
    # work train (flat cars loaded with rails) right at the edge, pointing right
    for j in range(3):
        cx = edge - 160 - j * 300
        cv2.rectangle(img, (int(cx - 130), int(gy - 90)), (int(cx + 130), int(gy - 60)), (60, 50, 40), -1)
        for r in range(min(6, int(k * 18) - j * 6) if k * 18 > j * 6 else 0):
            cv2.rectangle(img, (int(cx - 120), int(gy - 100 - r * 8)), (int(cx + 120), int(gy - 94 - r * 8)), (150, 146, 140), -1)
        for wx in (-90, 90):
            cv2.circle(img, (int(cx + wx), int(gy - 50)), 16, (30, 30, 30), -1, cv2.LINE_AA)
    # crane at the edge
    cx = edge + 40
    cv2.line(img, (int(cx), int(gy - 60)), (int(cx + 160), int(gy - 300)), (200, 160, 40), 10, cv2.LINE_AA)
    lift = 0.5 + 0.5 * math.sin(t * 3)
    cv2.line(img, (int(cx + 160), int(gy - 300)), (int(cx + 160), int(gy - 60 - 120 * lift)), (40, 40, 40), 3)
    cv2.rectangle(img, (int(cx + 60), int(gy - 66 - 120 * lift)), (int(cx + 260), int(gy - 58 - 120 * lift)), (150, 146, 140), -1)
    label(img, "DETRÁS: SOLO EL TERRAPLÉN", (edge + W) / 2 + 100, gy - 140, ease_out(prog(t, t0 + 1.2, 0.4)), 46, WHITE, box=(20, 20, 20))
    if title:
        label(img, "HASTA 3 MILLAS AL DÍA", W / 2, 120, ease_out(prog(t, 0.1, 0.4)), 66, YELLOW, box=(20, 20, 20))
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- Mary Ipsen at both parties
def lifeline(t, dur, t0=0.3, end=True, t42=None, t73=None):
    img = background("dark_grid", t)
    x0, x1, y = 260, 1660, 560
    t42 = t42 if t42 is not None else t0 + 2.2
    t73 = t73 if t73 is not None else t0 + 1.6
    k = ease_io(prog(t, t0 + 0.4, max(t42 - t0 - 0.4, 0.6)))
    cv2.line(img, (x0, y), (x1, y), (80, 80, 84), 6, cv2.LINE_AA)
    cv2.line(img, (x0, y), (int(lerp(x0, x1, k)), y), YELLOW, 10, cv2.LINE_AA)
    for x, yr, age, txt, tt in ((x0, "1869", "12 AÑOS", "LA FIESTA QUE UNIÓ EL PAÍS", t0), (x1, "1942", "85 AÑOS", "LA FIESTA QUE LO DESARMÓ", t42)):
        a = ease_back(prog(t, tt, 0.4))
        if a > 0:
            cv2.circle(img, (x, y), 34, GOLD, -1, cv2.LINE_AA)
            label(img, yr, x, y - 120, a, 100, YELLOW)
            label(img, age, x, y + 90, a, 56, WHITE)
            label(img, txt, x, y + 160, a, 40, GREY)
    label(img, "MARY IPSEN", W / 2, 140, ease_out(prog(t, 0.1, 0.4)), 80, WHITE)
    label(img, "73 AÑOS", W / 2, y - 60, ease_out(prog(t, t73, 0.4)), 70, YELLOW)
    return img


# ---------------------------------------------------------------- the lake cut in two
def split_lake(t, dur, t0=0.3):
    img = background("dark_grid", t)
    cx, cy = 960, 560
    pts = np.array([[640, 180], [900, 140], [1140, 260], [1220, 480], [1320, 620], [1280, 860], [1080, 960], [900, 880], [760, 700],
                    [640, 520], [560, 340]], np.float32)
    k = ease_io(prog(t, t0 + 0.6, 1.4))
    north = tuple(int(lerp(a, b, k)) for a, b in zip((52, 104, 150), PINK))
    south = tuple(int(lerp(a, b, k)) for a, b in zip((52, 104, 150), TEAL))
    mask = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mask, [pts.astype(np.int32)], 1)
    yy = np.arange(H)[:, None]
    img[(mask > 0) & (yy < 560)] = north
    img[(mask > 0) & (yy >= 560)] = south
    aa_poly(img, pts, (180, 180, 180), 3, closed=True)
    d = ease_out(prog(t, t0, 0.6))
    cv2.line(img, (400, 560), (int(400 + (1520 - 400) * d), 560), (20, 20, 20), 20)
    cv2.line(img, (400, 560), (int(400 + (1520 - 400) * d), 560), DIRT, 12)
    label(img, "TERRAPLÉN · AÑOS 50", 260, 520, d, 40, WHITE, anchor="l")
    label(img, "NORTE:", 1590, 250, ease_out(prog(t, t0 + 1.4, 0.4)), 56, PINK)
    label(img, "MUCHO MÁS SALADO,", 1590, 320, ease_out(prog(t, t0 + 1.4, 0.4)), 44, WHITE)
    label(img, "ROJIZO, CASI ROSA", 1590, 375, ease_out(prog(t, t0 + 1.4, 0.4)), 44, WHITE)
    label(img, "SUR: VERDE", 1590, 860, ease_out(prog(t, t0 + 1.8, 0.4)), 56, TEAL)
    _tag(img, "ESQUEMA · GRAN LAGO SALADO")
    return img


# ---------------------------------------------------------------- overlay: the frame of the famous photo, the workers outside it
def outframe(img, t, dur, t0=0.3):
    """FnOverlay: darkens a margin round the picture and draws the edge of the frame: what the camera left out."""
    k = ease_out(prog(t, t0, 0.6))
    if k <= 0:
        return img
    m = int(150 * k)
    layer = img.copy()
    layer[:, :m] = (layer[:, :m] * 0.25).astype(np.uint8)
    layer[:, W - m:] = (layer[:, W - m:] * 0.25).astype(np.uint8)
    img[:] = layer
    for x in (m, W - m):
        for y in range(0, H, 40):
            cv2.line(img, (x, y), (x, y + 22), YELLOW, 4)
    return img
