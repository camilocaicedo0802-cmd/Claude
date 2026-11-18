"""Rollins Pass (1873-2025): diagrams drawn in code for this episode."""
import json
import math
import os

import cv2
import numpy as np

from engine import BLACK, H, RED, W, WHITE, YELLOW, clamp, ease_back, ease_in, ease_io, ease_out, lerp, prog
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line
from gfx9 import car, loco

SNOW = (232, 236, 242)
SNOW_SH = (176, 186, 200)
ROCK = (78, 74, 70)
ROCK_DK = (52, 50, 48)
WOOD = (150, 112, 70)
WOOD_DK = (100, 72, 44)
WATER = (60, 120, 180)
WATER_HI = (120, 180, 230)
SKY_T = (16, 20, 30)
SKY_B = (44, 56, 76)
BLUE = (110, 170, 220)
GREEN = (80, 190, 110)
COAL = (34, 34, 36)

_PROF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rp_profile.json")))


def _blend(img, layer, a):
    if a > 0.001:
        cv2.addWeighted(layer, min(a, 1.0), img, 1 - min(a, 1.0), 0, img)


def _tag(img, txt="ESQUEMA", a=0.7):
    label(img, txt, W - 160, H - 46, a, 30, GREY)


def _grad(top, bot):
    g = np.linspace(0, 1, H)[:, None, None]
    img = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    return np.repeat(img, W, axis=1).astype(np.uint8)


def _snowfall(img, t, n=160, seed=3, speed=120, wind=60, size=2, a=1.0, y1=H):
    if a <= 0:
        return
    rng = np.random.default_rng(seed)
    xs, ys, ph = rng.uniform(0, W, n), rng.uniform(0, H, n), rng.uniform(0, 6.28, n)
    layer = img.copy()
    for x, y, p in zip(xs, ys, ph):
        yy = (y + t * speed * (0.7 + 0.3 * math.sin(p))) % H
        xx = (x + t * wind + 14 * math.sin(t * 1.3 + p)) % W
        if yy < y1:
            cv2.circle(layer, (int(xx), int(yy)), size, SNOW, -1, cv2.LINE_AA)
    _blend(img, layer, a)


# ---------------------------------------------------------------- the mountain in section: over the top or through it
def profile(t, dur, mode="over", t0=0.3, tunnel_t=None, diff_t=None):
    """Cross-section along the Moffat Tunnel line (real ground, Mapzen terrain). mode 'over': the line climbs over the
    top; 'tunnel': the tunnel is bored at ~9,200 ft and the train goes straight through; 'both': both at once."""
    img = _grad(SKY_T, SKY_B)
    pr = [(d, e) for d, e in _PROF["prof"] if e]
    d0, d1 = pr[0][0], pr[-1][0]
    e0, e1 = 8000.0, 12800.0
    X0, X1, Y0, Y1 = 120, W - 120, 1000, 190
    sx = lambda d: X0 + (d - d0) / (d1 - d0) * (X1 - X0)
    sy = lambda e: Y0 + (e - e0) / (e1 - e0) * (Y1 - Y0)
    ground = np.array([[sx(d), sy(e)] for d, e in pr])
    fill_poly(img, np.vstack([ground, [[X1, H], [X0, H]], ]), ROCK)
    fill_poly(img, np.vstack([[[0, ground[0][1]]], ground, [[W, ground[-1][1]], [W, H], [0, H]]]), ROCK)
    # snow cap above ~11,000 ft
    cap = ground[ground[:, 1] < sy(11000)]
    if len(cap) > 2:
        fill_poly(img, np.vstack([cap, [[cap[-1][0], sy(11000)], [cap[0][0], sy(11000)]]]), (200, 206, 214))
    aa_poly(img, ground, (120, 116, 110), 3)
    # elevation ticks
    for ft in range(8000, 12800, 1000):
        y = sy(ft)
        cv2.line(img, (60, int(y)), (84, int(y)), (120, 124, 130), 2)
        label(img, f"{ft:,} PIES".replace(",", "."), 96, y, 0.8, 26, (150, 154, 160), anchor="l")
    ep, wp = _PROF["ep_km"], _PROF["wp_km"]
    # the line over the top: up to Corona, 11,660 ft (the real summit is north of this section: drawn above the crest)
    if mode in ("over", "both"):
        k = ease_io(prog(t, t0, 2.6))
        top = sy(11660)
        path = np.array([[sx(d0), sy(9000)], [sx(ep - 1.2), sy(9800)], [sx(ep + 1.0), sy(10900)], [sx(8.0), top - 40],
                         [sx(9.0), top - 70], [sx(10.0), top - 40], [sx(wp - 2.0), sy(10600)], [sx(wp), sy(9300)], [sx(d1), sy(8900)]])
        pts = np.array(path)
        from maps import catmull
        sm = catmull(pts, 18)
        part = partial_line(sm, k)
        if len(part) > 1:
            aa_poly(img, part, (0, 0, 0), 12)
            aa_poly(img, part, YELLOW, 6)
            hx, hy = part[-1]
            cv2.circle(img, (int(hx), int(hy)), 13, WHITE, -1, cv2.LINE_AA)
        a = ease_out(prog(t, t0 + 1.2, 0.4))
        label(img, "CORONA · 11.660 PIES", sx(9.0), top - 130, a, 52, YELLOW)
        label(img, "≈ 3.560 M", sx(9.0), top - 88, a, 34, WHITE)
    if mode in ("tunnel", "both"):
        tt = tunnel_t if tunnel_t is not None else t0
        k = ease_io(prog(t, tt, 1.8))
        ye, ya, yw = sy(9197), sy(9239), sy(9058)
        xe, xw = sx(ep), sx(wp)
        xm = (xe + xw) / 2
        bore = np.array([[xe, ye], [xm, ya], [xw, yw]])
        part = partial_line(bore[::-1] if False else bore, k)
        if len(part) > 1:
            aa_poly(img, part, (0, 0, 0), 22)
            aa_poly(img, part, (30, 30, 32), 16)
            aa_poly(img, part, WHITE, 3)
        a = ease_out(prog(t, tt + 0.3, 0.4))
        label(img, "TÚNEL MOFFAT · 6,2 MILLAS", xm, ya + 70, a, 46, WHITE)
        label(img, "9.239 PIES · CASI EN PLANO (< 1 %)", xm, ya + 118, a, 34, (200, 204, 210))
        for x, y, tx in ((xe, ye, "BOCA ESTE"), (xw, yw, "BOCA OESTE")):
            cv2.circle(img, (int(x), int(y)), 12, YELLOW, -1, cv2.LINE_AA)
            label(img, tx, x, y - 44, a, 30, YELLOW)
        if diff_t is not None:
            a2 = ease_out(prog(t, diff_t, 0.5))
            if a2 > 0:
                xa = sx(12.3)
                y_top, y_bot = sy(11660), ya
                cv2.arrowedLine(img, (int(xa), int(y_bot - 6)), (int(xa), int(y_top + 6)), YELLOW, 5, cv2.LINE_AA, tipLength=0.06)
                cv2.arrowedLine(img, (int(xa), int(y_top + 6)), (int(xa), int(y_bot - 6)), YELLOW, 5, cv2.LINE_AA, tipLength=0.06)
                cv2.line(img, (int(xa - 60), int(y_top)), (int(xa + 60), int(y_top)), YELLOW, 2, cv2.LINE_AA)
                label(img, "≈ 2.400 PIES", xa + 40, (y_top + y_bot) / 2 - 20, a2, 50, YELLOW, anchor="l")
                label(img, "MÁS ABAJO", xa + 40, (y_top + y_bot) / 2 + 26, a2, 36, WHITE, anchor="l")
        # a train running through
        if prog(t, tt + 1.8, 0.1) > 0:
            kk = ((t - tt - 1.8) / 3.0) % 1.0
            p = partial_line(bore, kk)[-1]
            cv2.circle(img, (int(p[0]), int(p[1])), 9, YELLOW, -1, cv2.LINE_AA)
    label(img, "ESTE · DENVER", 220, 120, 0.7, 30, GREY)
    label(img, "OESTE · WINTER PARK", W - 260, 120, 0.7, 30, GREY)
    _tag(img, "CORTE · RELIEVE REAL, ALTURAS EXAGERADAS")
    return img


# ---------------------------------------------------------------- 2 % vs 4 %
def grade(t, dur, t0=0.3, t2=1.6, helpers_t=3.0, cart_t=None):
    """A normal main line keeps under 2 %; the Hill climbed at 4 %: a few cars and two or three engines per train."""
    img = background("dark_grid", t)
    for i, (pct, lab, col, tt) in enumerate(((2, "FERROCARRIL NORMAL", (170, 176, 184), t0), (4, "LA COLINA", YELLOW, t2))):
        a = ease_out(prog(t, tt, 0.5))
        if a <= 0:
            continue
        cy = 520 if i == 0 else 950
        x0, x1 = 160, W - 160
        rise = (x1 - x0) * pct / 100 * 6.0   # slope drawn x6
        k = ease_io(prog(t, tt, 0.8))
        y1 = cy - rise * k
        layer = img.copy()
        fill_poly(layer, [[x0, cy], [x1, y1], [x1, cy + 30], [x0, cy + 30]], (60, 58, 56))
        aa_poly(layer, [[x0, cy], [x1, y1]], col, 6)
        _blend(img, layer, a)
        label(img, f"{pct} %", x1 - 60, y1 - 60, a, 96, col, anchor="r")
        label(img, lab, x0 + 10, cy + 70, a, 46, col, anchor="l")
        if i == 1 and k >= 1:
            ang = math.atan2(-(y1 - cy), x1 - x0)
            n_help = 1 + int(prog(t, helpers_t, 0.01)) * 2
            run = ((t - tt) * 0.035) % 0.3 + 0.18
            # helper engines + 3 cars, climbing slowly
            xs = x0 + (x1 - x0) * run
            for j in range(3):
                xc = xs - j * 210
                car(img, xc, cy - (xc - x0) * math.tan(ang), 0.8, 1, ang, a=a)
            xl = xs + 270
            loco(img, xl, cy - (xl - x0) * math.tan(ang), 0.8, 1, ang, num="", a=a, tender=True)
            if n_help > 1:
                for j in range(2):
                    xh = xs - 3 * 210 - 30 - j * 300
                    loco(img, xh + 240, cy - (xh + 240 - x0) * math.tan(ang), 0.8, 1, ang, num="", a=ease_out(prog(t, helpers_t + j * 0.4, 0.4)),
                         tender=True)
                label(img, "2 O 3 LOCOMOTORAS POR TREN", W * 0.6, 1020, ease_out(prog(t, helpers_t + 0.6, 0.4)), 50, YELLOW)
    if cart_t is not None:
        label(img, "COMO EMPUJAR UN CARRITO LLENO CUESTA ARRIBA", W / 2, 100, ease_out(prog(t, cart_t, 0.4)), 50, WHITE)
    _tag(img, "PENDIENTE EXAGERADA")
    return img


# ---------------------------------------------------------------- Riflesight Notch: the line crosses over itself
def loop(t, dur, t0=0.3, cross_t=None):
    """Isometric sketch of the loop at Riflesight Notch: the track climbs around and passes over itself on a trestle."""
    img = _grad((20, 26, 34), (52, 62, 72))
    fill_poly(img, [[0, 760], [W, 640], [W, H], [0, H]], (64, 70, 60))
    fill_poly(img, [[0, 600], [700, 380], [1300, 470], [W, 300], [W, 640], [0, 760]], (78, 82, 74))
    # helix: parameter s in [0,1]: approach from the left, loop around, then cross over the approach and climb right
    def P(s):
        if s < 0.35:
            u = s / 0.35
            x, y, z = lerp(-700, 0, u), lerp(260, 120, u), lerp(0, 40, u)
        elif s < 0.8:
            u = (s - 0.35) / 0.45
            x = 300 * math.sin(u * 2 * math.pi)
            y = 120 - 260 * (1 - math.cos(u * 2 * math.pi)) / 2
            z = 40 + u * 90
        else:
            u = (s - 0.8) / 0.2
            x, y, z = lerp(0, 760, u), lerp(120, -40, u), lerp(130, 190, u)
        return x, y, z
    def scr(x, y, z):
        return W / 2 + x * 0.95 + y * 0.55, 700 + y * 0.45 - z * 1.6 - x * 0.12
    ss = np.linspace(0, 1, 500)
    pts = np.array([scr(*P(s)) for s in ss])
    k = ease_io(prog(t, t0, 3.0))
    n = max(2, int(len(pts) * k))
    # trestle bents under the upper crossing
    xa = scr(*P(0.8 + 0.2 * 0.0))
    for s in np.linspace(0.8, 0.86, 7):
        if s > ss[n - 1]:
            break
        x, y = scr(*P(s))
        yb = scr(P(s)[0], P(s)[1], 0)[1]
        cv2.line(img, (int(x - 14), int(y)), (int(x - 22), int(yb + 4)), WOOD, 5, cv2.LINE_AA)
        cv2.line(img, (int(x + 14), int(y)), (int(x + 22), int(yb + 4)), WOOD, 5, cv2.LINE_AA)
        cv2.line(img, (int(x - 18), int((y + yb) / 2)), (int(x + 18), int((y + yb) / 2)), WOOD_DK, 3, cv2.LINE_AA)
    # draw lower part first then upper part so the crossing reads
    low, high = pts[:min(n, int(0.8 * len(pts)))], pts[int(0.8 * len(pts)):n] if n > int(0.8 * len(pts)) else []
    aa_poly(img, low, (0, 0, 0), 14)
    aa_poly(img, low, (210, 210, 214), 6)
    if len(high) > 1:
        aa_poly(img, high, (0, 0, 0), 16)
        aa_poly(img, high, YELLOW, 7)
    hx, hy = pts[n - 1]
    cv2.circle(img, (int(hx), int(hy)), 14, WHITE, -1, cv2.LINE_AA)
    if cross_t is not None:
        a = ease_out(prog(t, cross_t, 0.4))
        cx, cy = scr(*P(0.815))
        cv2.circle(img, (int(cx), int(cy + 30)), int(70 + 10 * math.sin(t * 4)), YELLOW, 3, cv2.LINE_AA) if a > 0 else None
        label(img, "LA VÍA PASA POR ENCIMA DE SÍ MISMA", W / 2, 120, a, 60, YELLOW)
    label(img, "RIFLESIGHT NOTCH", W / 2, 200, ease_out(prog(t, 0.1, 0.4)), 46, WHITE)
    label(img, "SUBE", 200, 860, ease_out(prog(t, t0, 0.4)), 40, GREY)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- the snowsheds: a roof over the line
def shed(t, dur, mode="cover", t0=0.3, x_t=None):
    """Cross-section of a timber snowshed on a ledge. modes: cover (the roof goes up), leak (snow through the cracks),
    crush (the weight breaks the beams), fire (1918)."""
    img = _grad((14, 18, 26), (40, 48, 62))
    # mountainside
    fill_poly(img, [[0, 300], [700, 560], [700, 820], [W, 900], [W, H], [0, H]], ROCK)
    fill_poly(img, [[700, 820], [W, 900], [W, 920], [700, 840]], ROCK_DK)
    x0, x1, yb, yt = 760, 1500, 820, 560
    # track
    cv2.rectangle(img, (x0 - 60, yb), (x1 + 120, yb + 14), (90, 90, 96), -1)
    k = ease_out(prog(t, t0, 1.2)) if mode == "cover" else 1.0
    crush = ease_in(prog(t, t0 + 1.4, 1.0)) if mode == "crush" else 0.0
    fire = prog(t, t0 + 0.4, 2.0) if mode == "fire" else 0.0
    # posts
    for i, x in enumerate(np.linspace(x0, x1, 6)):
        if k * 6 < i:
            break
        sag = crush * (60 if 1 <= i <= 4 else 10)
        cv2.rectangle(img, (int(x - 12), int(yt + sag)), (int(x + 12), yb), WOOD if fire < 0.5 else (60, 40, 30), -1)
    # roof (sloped down-hill so snow slides off), sags when crushed
    if k > 0.3:
        mid = (x0 + x1) / 2
        roof = np.array([[x0 - 40, yt - 70], [mid, yt - 30 + crush * 120], [x1 + 60, yt + 10]])
        rp = partial_line(roof, clamp((k - 0.3) / 0.7))
        if len(rp) > 1:
            aa_poly(img, rp, WOOD_DK if fire < 0.5 else (50, 34, 26), 26)
            aa_poly(img, rp, WOOD if fire < 0.5 else (70, 50, 36), 18)
        if crush > 0.5:
            cv2.line(img, (int(mid - 30), int(yt - 20 + crush * 110)), (int(mid + 25), int(yt - 50 + crush * 120)), (30, 22, 16), 6, cv2.LINE_AA)
    # snow load on the roof and against the uphill wall
    sn = ease_out(prog(t, t0 + 0.6, 1.4)) if mode != "fire" else 0.6
    if sn > 0 and mode != "fire":
        fill_poly(img, [[0, 300 - 120 * sn], [x0 - 40, yt - 70 - 160 * sn], [(x0 + x1) / 2, yt - 30 - 140 * sn + crush * 120],
                        [x1 + 60, yt + 10 - 60 * sn], [x1 + 60, yt + 10], [(x0 + x1) / 2, yt - 30 + crush * 120], [x0 - 40, yt - 70], [0, 300]], SNOW)
    if mode == "leak":
        rng = np.random.default_rng(5)
        for j in range(60):
            x = rng.uniform(x0 + 40, x1 - 40)
            yy = yt + ((t * 160 + rng.uniform(0, 400)) % 260)
            cv2.circle(img, (int(x), int(yy)), 3, SNOW, -1, cv2.LINE_AA)
        drift = ease_out(prog(t, t0 + 0.5, 3.0))
        fill_poly(img, [[x0, yb], [x0 + 200, yb - 60 * drift], [x0 + 520, yb - 90 * drift], [x1, yb - 30 * drift], [x1, yb]], SNOW)
        label(img, "LA NIEVE SE COLABA POR LAS RENDIJAS", W / 2, 120, ease_out(prog(t, t0 + 0.3, 0.4)), 56, YELLOW)
    if mode == "crush":
        label(img, "EL PESO APLASTABA LAS VIGAS", W / 2, 120, ease_out(prog(t, t0 + 1.4, 0.4)), 60, RED)
    if mode == "cover":
        label(img, "KILÓMETROS DE TECHO DE MADERA", W / 2, 120, ease_out(prog(t, t0 + 0.4, 0.4)), 60, YELLOW)
        label(img, "EL TREN PASA POR DEBAJO", (x0 + x1) / 2, yb + 70, ease_out(prog(t, t0 + 1.2, 0.4)), 40, WHITE)
    if mode == "fire":
        rng = np.random.default_rng(int(t * 12))
        layer = img.copy()
        for j in range(90):
            x = rng.uniform(x0 - 40, x1 + 60)
            h = rng.uniform(40, 220) * (0.4 + fire)
            yb2 = yt + rng.uniform(-40, 200)
            col = (255, int(rng.uniform(90, 200)), 30)
            cv2.ellipse(layer, (int(x), int(yb2 - h / 2)), (int(rng.uniform(10, 26)), int(h / 2)), 0, 0, 360, col, -1, cv2.LINE_AA)
        _blend(img, layer, 0.55 + 0.25 * math.sin(t * 9))
        label(img, "1918 · EL INCENDIO DE CORONA", W / 2, 120, ease_out(prog(t, 0.1, 0.4)), 64, (255, 160, 60))
    if mode != "fire":
        _snowfall(img, t, 140, 4, 110, 80, 2, 0.9)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- the rotary snowplow
def rotary(t, dur, t0=0.3, spin=1.0):
    """Side view: a rotary plow pushed by a locomotive into a drift; the bladed wheel throws the snow aside."""
    img = _grad((18, 22, 30), (60, 70, 86))
    fill_poly(img, [[0, 820], [W, 820], [W, H], [0, H]], (90, 94, 100))
    cv2.rectangle(img, (0, 820), (W, 834), (70, 70, 76), -1)
    # the drift ahead
    k = ease_io(prog(t, t0, dur - t0))
    xp = lerp(520, 980, k)
    fill_poly(img, [[xp + 150, 820], [xp + 160, 430], [xp + 400, 380], [W, 360], [W, 820]], SNOW)
    fill_poly(img, [[xp + 150, 820], [xp + 160, 430], [xp + 200, 420], [xp + 190, 820]], SNOW_SH)
    # the plow car
    body = np.array([[xp - 380, 800], [xp - 380, 520], [xp - 40, 520], [xp + 40, 470], [xp + 150, 470], [xp + 150, 800]])
    fill_poly(img, body, (40, 42, 48))
    cv2.rectangle(img, (int(xp - 340), 560), (int(xp - 260), 620), (200, 190, 120), -1)
    # wheel with blades (seen edge-on as a disk)
    cx, cy, r = xp + 120, 650, 150
    cv2.ellipse(img, (int(cx), int(cy)), (40, r), 0, 0, 360, (150, 30, 30), -1, cv2.LINE_AA)
    for j in range(8):
        a = j * math.pi / 4 + t * 9 * spin
        cv2.line(img, (int(cx), int(cy)), (int(cx + 36 * math.cos(a)), int(cy + r * math.sin(a))), (220, 220, 220), 5, cv2.LINE_AA)
    for wx in (xp - 320, xp - 180, xp + 20):
        cv2.circle(img, (int(wx), 800), 26, (30, 30, 30), -1, cv2.LINE_AA)
    # the pushing engine
    loco(img, xp - 384, 820, 1.0, 1, 0.0, num="", light=0.0)
    # snow thrown sideways (arc up and over)
    rng = np.random.default_rng(7)
    layer = img.copy()
    for j in range(260):
        ph = (t * 1.6 + rng.uniform(0, 1)) % 1.0
        sx0, sy0 = cx + 30, cy - r * 0.6
        vx, vy = rng.uniform(-260, 60), rng.uniform(-900, -600)
        x = sx0 + vx * ph
        y = sy0 + vy * ph + 1100 * ph * ph
        cv2.circle(layer, (int(x), int(y)), int(rng.uniform(2, 6)), SNOW, -1, cv2.LINE_AA)
    _blend(img, layer, ease_out(prog(t, t0 + 0.2, 0.5)))
    label(img, "QUITANIEVES ROTATIVA", W / 2, 110, ease_out(prog(t, 0.1, 0.4)), 64, YELLOW)
    label(img, "UNA RUEDA DE CUCHILLAS QUE ESCUPE LA NIEVE A LOS LADOS", W / 2, 180, ease_out(prog(t, 0.6, 0.4)), 40, WHITE)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- a train trapped in the snow
def trapped(t, dur, t0=0.2, days=(1, 30), temp_t=None, coal_t=None):
    """A train buried in a snow cut: the snow climbs over the windows, the day count goes up, -20 °C, the coal runs out."""
    img = _grad((10, 12, 18), (36, 42, 54))
    fill_poly(img, [[0, 860], [W, 860], [W, H], [0, H]], (70, 74, 82))
    # train
    loco(img, 1380, 860, 1.25, 1, 0.0, num="", light=0.2)
    for j in range(3):
        x = 1380 - 330 - j * 270
        cv2.rectangle(img, (int(x - 250), 640), (int(x), 840), (64, 46, 34), -1)
        for wv in range(4):
            wx = x - 230 + wv * 58
            cv2.rectangle(img, (int(wx), 680), (int(wx + 38), 730), (230, 190, 110), -1)
        cv2.rectangle(img, (int(x - 254), 626), (int(x + 4), 644), (40, 30, 24), -1)
    k = ease_io(prog(t, t0, dur - t0 - 0.2))
    snow_y = lerp(850, 655, k)
    xs = np.linspace(0, W, 40)
    top = snow_y + 22 * np.sin(xs / 140 + 1.3) + 10 * np.sin(xs / 47)
    fill_poly(img, np.vstack([np.stack([xs, top], 1), [[W, H], [0, H]]]), SNOW)
    _snowfall(img, t, 220, 9, 150, 140, 2, 1.0)
    # day counter
    d = int(lerp(days[0], days[1], k))
    label(img, f"DÍA {d}", 260, 150, ease_out(prog(t, t0, 0.3)), 96, YELLOW)
    if temp_t is not None:
        a = ease_out(prog(t, temp_t, 0.4))
        cx, cy = W - 230, 300
        cv2.rectangle(img, (cx - 18, cy - 150), (cx + 18, cy + 110), (200, 200, 210), 3)
        lv = lerp(cy + 100, cy + 40, ease_out(prog(t, temp_t, 1.0)))
        cv2.rectangle(img, (cx - 10, int(lv)), (cx + 10, cy + 100), (90, 160, 255), -1)
        cv2.circle(img, (cx, cy + 130), 34, (90, 160, 255), -1, cv2.LINE_AA)
        label(img, "-20 °C", cx - 60, cy - 40, a, 72, (150, 200, 255), anchor="r")
    if coal_t is not None:
        a = ease_out(prog(t, coal_t, 0.4))
        c = 1 - ease_io(prog(t, coal_t, 2.5))
        x0, y0 = 760, 150
        label(img, "CARBÓN", x0 - 40, y0, a, 50, WHITE, anchor="r")
        cv2.rectangle(img, (x0, y0 - 24), (x0 + 400, y0 + 24), (90, 90, 96), 2)
        cv2.rectangle(img, (x0 + 4, y0 - 20), (int(x0 + 4 + 392 * c), y0 + 20), RED if c < 0.3 else (200, 200, 200), -1)
    _tag(img, "ILUSTRACIÓN")
    return img


# ---------------------------------------------------------------- the money: summers in, winters out
def seasons(t, dur, t0=0.3, step=0.45, tunnel_t=None):
    """Each summer some money came in; each winter the Hill took that and a bit more. The tunnel fund never grew."""
    img = background("dark_grid", t)
    yrs = list(range(1905, 1912))
    x0, x1, ymid = 220, W - 220, 600
    cv2.line(img, (x0 - 40, ymid), (x1 + 40, ymid), (120, 124, 130), 2)
    bw = (x1 - x0) / len(yrs)
    bal = 0.0
    pts = [(x0, ymid)]
    for i, y in enumerate(yrs):
        a = ease_out(prog(t, t0 + i * step, 0.3))
        if a <= 0:
            break
        up, down = 150, 190 + i * 6
        xs = x0 + i * bw
        ka = ease_out(prog(t, t0 + i * step, 0.25))
        kb = ease_out(prog(t, t0 + i * step + step * 0.5, 0.25))
        cv2.rectangle(img, (int(xs + 14), int(ymid - up * ka)), (int(xs + bw / 2 - 4), ymid), GREEN, -1)
        cv2.rectangle(img, (int(xs + bw / 2 + 4), ymid), (int(xs + bw - 14), int(ymid + down * kb)), RED, -1)
        label(img, str(y), xs + bw / 2, ymid + 260, a, 34, GREY)
        if i == 0:
            label(img, "VERANO", xs + bw * 0.27, ymid - up - 34, a, 30, GREEN)
            label(img, "INVIERNO", xs + bw * 0.75, ymid + down + 34, kb, 30, RED)
        bal += (up - down) * kb
        pts.append((xs + bw, ymid - bal * 0.0 + (i + 1) * 30 * kb))
    label(img, "CADA VERANO ENTRABA ALGO · CADA INVIERNO SE IBA ESO Y UN POCO MÁS", W / 2, 140, ease_out(prog(t, 0.1, 0.4)), 46, WHITE)
    if tunnel_t is not None:
        a = ease_out(prog(t, tunnel_t, 0.4))
        x = lerp(x1 - 80, x1 + 260, ease_io(prog(t, tunnel_t, dur - tunnel_t)))
        cv2.ellipse(img, (int(x), 300), (60, 70), 0, 180, 360, (230, 230, 230), 6, cv2.LINE_AA)
        cv2.line(img, (int(x - 60), 300), (int(x + 60), 300), (230, 230, 230), 6)
        label(img, "EL TÚNEL", x, 220, a, 40, YELLOW)
        label(img, "SE ALEJABA", x, 380, a, 34, WHITE)
    _tag(img, "ILUSTRACIÓN · VALORES NO A ESCALA")
    return img


# ---------------------------------------------------------------- the pioneer bore beside the main tunnel
def pioneer(t, dur, mode="probe", t0=0.3):
    """Cross-section of the two bores. probe: a small 8-ft bore to read the rock first; water: enlarged to ~10.5 ft and
    carrying west-slope water to Denver; rate: 21 ft a day for 48 months."""
    img = background("dark_grid", t)
    fill_poly(img, [[0, 260], [W, 260], [W, H], [0, H]], ROCK)
    rng = np.random.default_rng(3)
    for _ in range(140):
        x, y = rng.uniform(0, W), rng.uniform(280, H)
        cv2.circle(img, (int(x), int(y)), int(rng.uniform(3, 10)), ROCK_DK, -1, cv2.LINE_AA)
    px_ft = 22.0
    # main railway tunnel: 16 ft wide x 24 ft high
    mx, my = 1180, 900
    a1 = ease_out(prog(t, t0 + (1.2 if mode == "probe" else 0.0), 0.5))
    if a1 > 0:
        layer = img.copy()
        w2, h = 8 * px_ft, 24 * px_ft
        cv2.rectangle(layer, (int(mx - w2), int(my - h + w2)), (int(mx + w2), int(my)), (14, 14, 16), -1)
        cv2.ellipse(layer, (int(mx), int(my - h + w2)), (int(w2), int(w2)), 0, 180, 360, (14, 14, 16), -1, cv2.LINE_AA)
        _blend(img, layer, a1)
        label(img, "TÚNEL DEL TREN", mx, my + 60, a1, 44, WHITE)
        cv2.rectangle(img, (int(mx - 120), int(my - 10)), (int(mx + 120), int(my)), (90, 90, 96), -1)
    # pioneer bore: 8 ft (probe) -> 10.5 ft (water)
    sx, sy = 640, 900
    k = ease_out(prog(t, t0, 0.6))
    d_ft = 8.0 if mode in ("probe", "rate") else lerp(8.0, 10.5, ease_io(prog(t, t0 + 0.6, 1.0)))
    r = d_ft / 2 * px_ft * k
    if r > 1:
        cv2.circle(img, (int(sx), int(sy - r)), int(r), (14, 14, 16), -1, cv2.LINE_AA)
        if mode == "water":
            wl = sy - r * 0.8
            fill_poly(img, [[sx - r * 0.95, wl], [sx + r * 0.95, wl], [sx + r * 0.6, sy - r * 0.2], [sx - r * 0.6, sy - r * 0.2]], WATER)
            for j in range(6):
                xx = sx - r * 0.7 + ((t * 80 + j * 40) % (r * 1.4))
                cv2.line(img, (int(xx), int(wl + 6)), (int(xx + 16), int(wl + 6)), WATER_HI, 3, cv2.LINE_AA)
        txt = f"{d_ft:.1f} PIES".replace(".0 ", " ").replace(".", ",") if mode == "water" else "8 PIES"
        label(img, "TÚNEL PEQUEÑO", sx, sy + 60, k, 44, YELLOW)
        label(img, txt, sx, sy - 2 * r - 40, k, 40, YELLOW)
    # person for scale
    hx = sx + 330
    cv2.circle(img, (hx, int(sy - 5.6 * px_ft)), 12, (220, 220, 220), -1, cv2.LINE_AA)
    cv2.line(img, (hx, int(sy - 5.1 * px_ft)), (hx, int(sy - 2.6 * px_ft)), (220, 220, 220), 6)
    cv2.line(img, (hx, int(sy - 2.6 * px_ft)), (hx - 14, sy), (220, 220, 220), 5)
    cv2.line(img, (hx, int(sy - 2.6 * px_ft)), (hx + 14, sy), (220, 220, 220), 5)
    if mode == "probe":
        label(img, "PRIMERO, UN TÚNEL DE PRUEBA PARA CONOCER LA ROCA", W / 2, 150, ease_out(prog(t, 0.1, 0.4)), 50, WHITE)
    elif mode == "water":
        label(img, "1936 · EL TÚNEL DE PRUEBA LLEVA AGUA", W / 2, 150, ease_out(prog(t, 0.1, 0.4)), 56, BLUE)
    elif mode == "rate":
        v = 21 * ease_out(prog(t, t0, 1.0))
        label(img, f"{v:.0f} PIES AL DÍA", W / 2, 140, ease_out(prog(t, t0, 0.3)), 80, YELLOW)
        label(img, "≈ 6,5 METROS · DURANTE 48 MESES", W / 2, 210, ease_out(prog(t, t0 + 0.6, 0.4)), 44, WHITE)
    _tag(img, "CORTE · ESQUEMA")
    return img


# ---------------------------------------------------------------- water across the Divide
def water(t, dur, t0=0.3, glass_t=None):
    """West-slope snowmelt (Fraser River) -> under the Continental Divide (Moffat water tunnel) -> South Boulder Creek ->
    Gross Reservoir -> Denver -> a kitchen tap."""
    img = _grad((22, 30, 44), (60, 78, 100))
    # the Divide (west on the left, east on the right)
    ridge = np.array([[0, 700], [300, 620], [620, 360], [760, 300], [880, 360], [1200, 640], [1500, 760], [W, 800]])
    fill_poly(img, np.vstack([ridge, [[W, H], [0, H]]]), ROCK)
    fill_poly(img, [[560, 410], [620, 360], [760, 300], [880, 360], [950, 420], [760, 380]], SNOW)
    label(img, "DIVISORIA CONTINENTAL", 760, 250, ease_out(prog(t, 0.1, 0.4)), 40, WHITE)
    label(img, "VERTIENTE OESTE", 260, 520, ease_out(prog(t, 0.2, 0.4)), 40, BLUE)
    label(img, "RÍO FRASER", 260, 570, ease_out(prog(t, 0.3, 0.4)), 34, WHITE)
    label(img, "VERTIENTE ESTE · LADO SECO", 1560, 640, ease_out(prog(t, 0.3, 0.4)), 40, (220, 190, 120))
    # flow path
    path = np.array([[150, 690], [420, 640], [560, 660], [960, 640], [1250, 700], [1480, 770], [1700, 800], [1800, 790]])
    k = ease_io(prog(t, t0, 2.5))
    part = partial_line(path, k)
    if len(part) > 1:
        aa_poly(img, part, (20, 40, 60), 20)
        aa_poly(img, part, WATER, 12)
        seg = np.hypot(*np.diff(part, axis=0).T)
        cum = np.concatenate([[0], np.cumsum(seg)])
        for j in range(24):
            d = (t * 160 + j * cum[-1] / 24) % max(cum[-1], 1)
            i = min(max(int(np.searchsorted(cum, d)), 1), len(part) - 1)
            p = part[i - 1] + (part[i] - part[i - 1]) * (d - cum[i - 1]) / max(seg[i - 1], 1e-6)
            cv2.circle(img, (int(p[0]), int(p[1])), 5, WATER_HI, -1, cv2.LINE_AA)
    a = ease_out(prog(t, t0 + 0.9, 0.4))
    label(img, "TÚNEL DE AGUA MOFFAT", 760, 700, a, 40, YELLOW)
    a = ease_out(prog(t, t0 + 1.7, 0.4))
    label(img, "SOUTH BOULDER CREEK · GROSS RESERVOIR", 1300, 860, a, 32, WHITE)
    a = ease_out(prog(t, t0 + 2.4, 0.4))
    label(img, "DENVER", 1780, 860, a, 46, YELLOW)
    if glass_t is not None:
        a = ease_out(prog(t, glass_t, 0.4))
        if a > 0:
            gx, gy = 1700, 300
            fill_poly(img, [[gx - 70, gy - 120], [gx + 70, gy - 120], [gx + 55, gy + 110], [gx - 55, gy + 110]], (200, 210, 220))
            lv = lerp(gy + 100, gy - 70, ease_out(prog(t, glass_t + 0.2, 1.2)))
            fill_poly(img, [[gx - 70 + (gy - 120 - lv) * -0.065 * -1, lv], [gx + 70 - (lv - gy + 120) * 0.065, lv], [gx + 52, gy + 104], [gx - 52, gy + 104]], WATER)
            label(img, "UN VASO EN UNA COCINA DE DENVER", gx, gy + 170, a, 34, WHITE)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- the road today
def speed_sign(t, dur, t0=0.2):
    img = _grad((30, 40, 52), (90, 104, 116))
    fill_poly(img, [[0, 820], [W, 780], [W, H], [0, H]], (110, 96, 78))
    a = ease_back(prog(t, t0, 0.5))
    cx, cy = W / 2, 470
    s = 1.0 * a
    if s > 0:
        cv2.rectangle(img, (int(cx - 10), int(cy + 200 * s)), (int(cx + 10), 900), (150, 150, 156), -1)
        cv2.rectangle(img, (int(cx - 190 * s), int(cy - 250 * s)), (int(cx + 190 * s), int(cy + 220 * s)), (30, 30, 30), -1)
        cv2.rectangle(img, (int(cx - 180 * s), int(cy - 240 * s)), (int(cx + 180 * s), int(cy + 210 * s)), (244, 244, 244), -1)
        label(img, "SPEED", cx, cy - 170 * s, a, int(70 * s) + 1, BLACK)
        label(img, "LIMIT", cx, cy - 100 * s, a, int(70 * s) + 1, BLACK)
        label(img, "20", cx, cy + 70 * s, a, int(230 * s) + 1, BLACK)
    label(img, "SIN BARANDAS · CAMINO DE TIERRA", W / 2, 960, ease_out(prog(t, t0 + 0.6, 0.4)), 50, WHITE)
    return img
