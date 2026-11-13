"""Church Hill Tunnel (Richmond, 1872-2025): diagrams drawn in code for this episode."""
import math

import cv2
import numpy as np

from engine import BLACK, H, RED, W, WHITE, YELLOW, Sprite, clamp, ease_back, ease_in, ease_io, ease_out, lerp, over, \
    over_center, prog, rounded_rect_sprite, text_sprite
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

CLAY = (78, 92, 108)
CLAY_DK = (58, 70, 84)
SOIL = (84, 66, 50)
GRASS = (60, 92, 56)
BRICK = (150, 72, 52)
TIMBER = (150, 112, 70)
CONCRETE = (170, 168, 160)
SAND = (196, 170, 120)
WATER = (40, 84, 120)
WATER_HI = (80, 140, 180)
INK = (34, 32, 30)
PAPER = (234, 228, 212)
STEAM = (235, 235, 235)

# tunnel geometry in screen space: west portal on the left, east portal on the right
X0, X1 = 150, 1770
TY, TH = 760, 74          # tunnel centre line (floor at TY + TH/2)
FT = (X1 - X0) / 4000.0   # screen px per foot along the tunnel


def _sky(top=(18, 22, 30), bot=(46, 54, 64)):
    g = np.linspace(0, 1, H)[:, None, None]
    img = (np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g)
    return np.repeat(img, W, axis=1).astype(np.uint8)


def surface(x):
    """Church Hill profile (screen y): rises from the west valley to the hilltop, falls to the east."""
    x = np.asarray(x, np.float64)
    k = np.clip((x - 40) / (W - 80), 0, 1)
    y = 560 - 300 * np.sin(np.pi * (0.12 + 0.82 * k)) ** 1.4 + 12 * np.sin(x / 70.0)
    return y


def _poly(img, pts, col, alpha=1.0):
    if alpha >= 0.999:
        fill_poly(img, pts, col)
        return
    layer = img.copy()
    fill_poly(layer, pts, col)
    cv2.addWeighted(layer, alpha, img, 1 - alpha, 0, img)


def _rowhouse(img, x, y, s, col, a=1.0, tilt=0.0, roof=(70, 62, 60)):
    body = np.array([[-s, 0], [-s, -1.5 * s], [s, -1.5 * s], [s, 0]], np.float64)
    rf = np.array([[-1.1 * s, -1.45 * s], [0, -2.05 * s], [1.1 * s, -1.45 * s]], np.float64)
    c, sn = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    R = np.array([[c, -sn], [sn, c]])
    _poly(img, body @ R.T + [x, y], col, a)
    _poly(img, rf @ R.T + [x, y], roof, a)
    for wx in (-0.5, 0.5):
        win = np.array([[wx * s - 0.18 * s, -0.55 * s], [wx * s - 0.18 * s, -1.0 * s], [wx * s + 0.18 * s, -1.0 * s],
                        [wx * s + 0.18 * s, -0.55 * s]])
        _poly(img, win @ R.T + [x, y], (230, 210, 140), a * 0.9)


def _church(img, x, y, s, a=1.0, col=(232, 228, 216)):
    _poly(img, [[x - 1.4 * s, y], [x - 1.4 * s, y - 1.3 * s], [x + 1.4 * s, y - 1.3 * s], [x + 1.4 * s, y]], col, a)
    _poly(img, [[x - 1.55 * s, y - 1.25 * s], [x, y - 1.95 * s], [x + 1.55 * s, y - 1.25 * s]], (110, 108, 104), a)
    _poly(img, [[x - 0.35 * s, y - 1.6 * s], [x - 0.35 * s, y - 2.9 * s], [x + 0.35 * s, y - 2.9 * s], [x + 0.35 * s, y - 1.6 * s]], col, a)
    _poly(img, [[x - 0.25 * s, y - 2.9 * s], [x - 0.25 * s, y - 3.4 * s], [x + 0.25 * s, y - 3.4 * s], [x + 0.25 * s, y - 2.9 * s]], col, a)
    _poly(img, [[x - 0.3 * s, y - 3.35 * s], [x, y - 3.95 * s], [x + 0.3 * s, y - 3.35 * s]], (110, 108, 104), a)


def _tree(img, x, y, s, a=1.0):
    cv2.line(img, (int(x), int(y)), (int(x), int(y - s)), (70, 56, 40), max(2, int(s / 6)), cv2.LINE_AA)
    cv2.circle(img, (int(x), int(y - 1.4 * s)), int(0.7 * s), (52, 86, 52), -1, cv2.LINE_AA)


def _person(img, x, y, s, col=WHITE, phase=0.0, run=False):
    cv2.circle(img, (int(x), int(y - 2.6 * s)), int(0.45 * s), col, -1, cv2.LINE_AA)
    cv2.line(img, (int(x), int(y - 2.1 * s)), (int(x), int(y - 1.0 * s)), col, max(2, int(s * 0.35)), cv2.LINE_AA)
    sw = math.sin(phase) * (0.7 if run else 0.25)
    for sg in (1, -1):
        cv2.line(img, (int(x), int(y - 1.0 * s)), (int(x + sg * sw * s), int(y)), col, max(2, int(s * 0.3)), cv2.LINE_AA)
        cv2.line(img, (int(x), int(y - 1.9 * s)), (int(x - sg * sw * s), int(y - 1.2 * s)), col, max(2, int(s * 0.25)), cv2.LINE_AA)


def _locomotive(img, x, y, s=1.0, col=(70, 72, 80), crushed=0.0, cars=10):
    """Side view, facing west (left). x = front of the engine, y = rail level."""
    def P(pts):
        return np.array(pts, np.float64) * s + [x, y]
    # boiler, cab, chimney, tender
    fill_poly(img, P([[0, -22], [0, -56], [96, -56], [96, -22]]), col)
    fill_poly(img, P([[8, -56], [8, -76], [22, -76], [22, -56]]), col)
    cab_top = -92 + 34 * crushed
    fill_poly(img, P([[96, -22], [96, cab_top], [140, cab_top], [140, -22]]), (84, 84, 92))
    fill_poly(img, P([[106, cab_top + 12], [106, cab_top + 30], [130, cab_top + 30], [130, cab_top + 12]]), (200, 170, 90))
    fill_poly(img, P([[144, -20], [144, -60], [214, -60], [214, -20]]), (66, 66, 74))
    for wx in (20, 52, 84, 118):
        cv2.circle(img, tuple(P([[wx, -14]])[0].astype(int)), int(13 * s), (90, 90, 96), -1, cv2.LINE_AA)
        cv2.circle(img, tuple(P([[wx, -14]])[0].astype(int)), int(13 * s), (20, 20, 20), 2, cv2.LINE_AA)
    num = text_sprite("231", "bebas", max(8, int(26 * s)), YELLOW, False)
    over(img, num, x + 104 * s, y + (cab_top + 34) * s, 1.0)
    for c in range(cars):
        cx = x + (222 + c * 66) * s
        fill_poly(img, np.array([[cx, y - 26 * s], [cx, y - 16 * s], [cx + 60 * s, y - 16 * s], [cx + 60 * s, y - 26 * s]]), (110, 90, 66))
        for wx in (10, 50):
            cv2.circle(img, (int(cx + wx * s), int(y - 9 * s)), int(8 * s), (80, 80, 84), -1, cv2.LINE_AA)


def _hill(img, t, clay=True, houses=True, church=True, park=False, cut=None):
    xs = np.linspace(0, W, 240)
    ys = surface(xs)
    fill_poly(img, np.vstack([np.stack([xs, ys], 1), [[W, H], [0, H]]]), SOIL)
    if clay:
        top = ys + 70
        fill_poly(img, np.vstack([np.stack([xs, top], 1), [[W, H], [0, H]]]), CLAY)
        rng = np.random.default_rng(3)
        for _ in range(60):
            x = rng.uniform(0, W)
            y = rng.uniform(float(np.interp(x, xs, top)) + 20, H - 10)
            cv2.ellipse(img, (int(x), int(y)), (int(rng.uniform(20, 60)), 3), 0, 0, 360, CLAY_DK, -1, cv2.LINE_AA)
    aa_poly(img, np.stack([xs, ys], 1), GRASS, 10)
    if houses:
        rng = np.random.default_rng(9)
        for x in np.arange(240, 1700, 92):
            if church and abs(x - 900) < 120:
                continue
            if park and 300 < x < 620:
                continue
            col = tuple(int(c) for c in rng.choice([BRICK, (170, 150, 120), (126, 64, 50), (180, 170, 150)]))
            _rowhouse(img, x, float(np.interp(x, xs, ys)) + 4, 20, col)
    if church:
        cx = 900
        _church(img, cx, float(np.interp(cx, xs, ys)) + 4, 30)
    if park:
        for x in (340, 410, 480, 560):
            _tree(img, x, float(np.interp(x, xs, ys)) + 2, 30)
    return xs, ys


def _tube(img, x0=X0, x1=X1, col=(16, 16, 18), arch=None, frac=1.0):
    xe = lerp(x0, x1, frac)
    fill_poly(img, [[x0, TY - TH / 2], [xe, TY - TH / 2], [xe, TY + TH / 2], [x0, TY + TH / 2]], col)
    if arch is not None:
        for x in np.arange(x0 + 6, xe - 6, 26):
            cv2.line(img, (int(x), int(TY - TH / 2)), (int(x), int(TY + TH / 2)), arch, 2, cv2.LINE_AA)
        cv2.line(img, (int(x0), int(TY - TH / 2)), (int(xe), int(TY - TH / 2)), arch, 4, cv2.LINE_AA)
    cv2.line(img, (int(x0), int(TY + TH / 2 - 4)), (int(xe), int(TY + TH / 2 - 4)), (80, 76, 70), 3, cv2.LINE_AA)


def _portal(img, x, col=(120, 116, 110), plug=False):
    fill_poly(img, [[x - 16, TY + TH / 2], [x - 16, TY - TH / 2 - 16], [x + 16, TY - TH / 2 - 16], [x + 16, TY + TH / 2]], col)
    if plug:
        fill_poly(img, [[x - 12, TY + TH / 2], [x - 12, TY - TH / 2 - 12], [x + 12, TY - TH / 2 - 12], [x + 12, TY + TH / 2]], CONCRETE)


def _cam(img, z, cx, cy):
    M = np.array([[z, 0, W / 2 - z * cx], [0, z, H / 2 - z * cy]], np.float32)
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return out, (lambda x, y: (z * x + M[0, 2], z * y + M[1, 2]))


def hill(t, dur, mode="intro", t0=0.3, props_t=None, tumble_t=None):
    """Church Hill in cross-section. modes: intro, dig (1872 timbering), sink (Jan 1873), done (1873, 4,000 ft, 19th to
    31st), leak (water and timber props), work (1925 crews), collapse (Oct 2 1925), rescue (shafts from the park),
    seal (1926 sand and plugs), today (park on top, plugged west, flooded east)."""
    img = _sky()
    park = mode in ("collapse", "seal", "today", "work", "rescue")
    xs, ys = _hill(img, t, park=park)
    L = []          # labels in scene coordinates: (text, x, y, alpha, size, color, anchor)
    S = []          # labels in screen coordinates
    cam = (1.0, W / 2, H / 2)
    loc_x = X0 + 100 * FT + 18
    if mode == "intro":
        k = ease_io(prog(t, t0 + 1.2, 1.6))
        if k > 0:
            _tube(img, frac=k, col=(16, 16, 18))
        L += [("SAINT JOHN · 1775", 900, float(np.interp(900, xs, ys)) - 150, ease_out(prog(t, t0, 0.4)), 46, YELLOW, "c"),
              ("CHURCH HILL", 1420, 230, ease_out(prog(t, t0 + 0.4, 0.4)), 60, WHITE, "c")]
        S += [("AQUÍ DEBAJO SE VA A CAVAR", W / 2, 960, ease_out(prog(t, t0 + 2.4, 0.4)), 54, YELLOW, "c")]
    elif mode == "dig":
        k = ease_io(prog(t, t0, max(dur - 1.0, 1.0)))
        face = lerp(X0 + 160, X0 + 700, k)
        _tube(img, X0, face, arch=BRICK)
        for x in np.arange(face - 130, face, 26):
            cv2.line(img, (int(x), int(TY - TH / 2)), (int(x), int(TY + TH / 2)), TIMBER, 4, cv2.LINE_AA)
            cv2.line(img, (int(x - 12), int(TY - TH / 2 + 4)), (int(x + 12), int(TY - TH / 2 + 4)), TIMBER, 4, cv2.LINE_AA)
        for i in range(3):
            _person(img, face - 30 - i * 40, TY + TH / 2 - 4, 9, (220, 214, 200), t * 6 + i, False)
        cam = (1.9, X0 + 380, TY - 60)
        S += [("ARCILLA AZULADA, BLANDA Y HÚMEDA", W / 2, 140, ease_out(prog(t, t0 + 0.2, 0.4)), 56, (170, 190, 215), "c"),
              ("PUNTALES DE MADERA", W * 0.66, 400, ease_out(prog(t, t0 + 1.2, 0.4)), 46, (220, 170, 110), "c"),
              ("ARCOS DE LADRILLO", W * 0.28, 820, ease_out(prog(t, t0 + 2.2, 0.4)), 46, (230, 140, 110), "c")]
    elif mode == "sink":
        _tube(img, X0, X0 + 980, arch=BRICK)
        cx = 760
        ck = prog(t, t0, 1.2)
        if ck > 0:
            for ox in (-110, -40, 50, 120):
                y0 = float(np.interp(cx + ox, xs, ys))
                pts = np.array([[cx + ox, y0], [cx + ox + 10, y0 + 50], [cx + ox - 6, y0 + 100]])
                aa_poly(img, partial_line(pts, ck), (16, 16, 16), 4)
        drop = 80 * ease_in(prog(t, t0 + 2.0, 0.7))
        if drop > 0:
            x0b, x1b = cx - 150, cx + 150
            seg = (xs > x0b) & (xs < x1b)
            top = np.stack([xs[seg], ys[seg]], 1)
            pit = np.vstack([top, (top + [0, drop])[::-1]])
            fill_poly(img, pit, (12, 12, 14))
            aa_poly(img, top + [0, drop], GRASS, 8)
            for i, hx in enumerate((cx - 92, cx, cx + 92)):
                hy = float(np.interp(hx, xs, ys)) + 4 + drop
                tilt = 0 if i != 1 else 170 * ease_in(prog(t, tumble_t if tumble_t is not None else t0 + 2.3, 1.0))
                _rowhouse(img, hx, hy - (0 if i != 1 else 14 * math.sin(math.radians(tilt))), 20, BRICK if i != 1 else (180, 170, 150), 1.0, tilt)
            L += [("≈ 20 PIES · MÁS DE 6 M", cx + 190, float(np.interp(cx, xs, ys)) + 50, ease_out(prog(t, t0 + 2.6, 0.4)), 46, YELLOW, "l")]
        cam = (1.5, cx, float(np.interp(cx, xs, ys)) + 120)
        S += [("ENERO DE 1873", W / 2, 110, ease_out(prog(t, 0.1, 0.4)), 64, YELLOW, "c"),
              ("GRIETAS EN LAS CALLES", W / 2, 180, ease_out(prog(t, t0 + 0.5, 0.4)), 44, WHITE, "c")]
    elif mode == "done":
        k = ease_io(prog(t, t0, 1.6))
        _tube(img, arch=BRICK)
        _portal(img, X0)
        _portal(img, X1)
        if k > 0:
            yb = TY + TH / 2 + 70
            cv2.line(img, (X0, int(yb)), (int(lerp(X0, X1, k)), int(yb)), YELLOW, 4, cv2.LINE_AA)
            for x in (X0, X1):
                cv2.line(img, (x, int(yb - 14)), (x, int(yb + 14)), YELLOW, 4, cv2.LINE_AA)
        L += [("≈ 4.000 PIES · ≈ 1.200 M", W / 2, TY + TH / 2 + 120, ease_out(prog(t, t0 + 1.4, 0.4)), 58, YELLOW, "c"),
              ("CALLE 19", X0 + 30, TY - 120, ease_out(prog(t, t0 + 0.4, 0.4)), 44, WHITE, "c"),
              ("CALLE 31", X1 - 30, TY - 120, ease_out(prog(t, t0 + 0.8, 0.4)), 44, WHITE, "c")]
    elif mode == "leak":
        _tube(img, arch=BRICK)
        _portal(img, X0)
        _portal(img, X1)
        rng = np.random.default_rng(2)
        for i in range(80):
            x = rng.uniform(X0 + 20, X1 - 20)
            ph = (t * rng.uniform(0.8, 1.6) + rng.uniform(0, 1)) % 1.0
            y = lerp(TY - TH / 2 - 120, TY + TH / 2 - 6, ph)
            cv2.line(img, (int(x), int(y)), (int(x), int(y + 10)), WATER_HI, 2, cv2.LINE_AA)
        pt = props_t if props_t is not None else t0 + 1.6
        pk = ease_io(prog(t, pt, 1.4))
        if pk > 0:
            for x in np.arange(X0 + 30, lerp(X0 + 30, X1 - 30, pk), 14):
                cv2.line(img, (int(x), int(TY - TH / 2)), (int(x + 8), int(TY + TH / 2)), TIMBER, 3, cv2.LINE_AA)
                cv2.line(img, (int(x + 8), int(TY - TH / 2)), (int(x), int(TY + TH / 2)), TIMBER, 3, cv2.LINE_AA)
            S += [("TANTOS PUNTALES QUE YA NO CABÍA UN TREN", W / 2, 960, ease_out(prog(t, pt + 0.8, 0.4)), 50, YELLOW, "c")]
        S += [("SOLO PASABA EL AGUA", W / 2, 110, ease_out(prog(t, t0, 0.4)), 60, (150, 190, 225), "c")]
    elif mode in ("work", "collapse"):
        _tube(img, arch=BRICK, col=(44, 40, 36))
        _portal(img, X0)
        for x in np.arange(X0 + 340, X0 + 1100, 120):
            fill_poly(img, [[x, TY - TH / 2], [x + 40, TY - TH / 2], [x + 40, TY + TH / 2], [x, TY + TH / 2]], (120, 118, 112))
        ct = t0 + 2.0 if mode == "collapse" else 99
        lights = True
        if mode == "collapse" and t0 + 0.6 < t < ct and int(t * 12) % 3 == 0:
            lights = False
        crushed = ease_in(prog(t, ct + 0.1, 0.5))
        _locomotive(img, loc_x, TY + TH / 2 - 6, 0.55, crushed=crushed)
        if lights and t < ct:
            for x in np.arange(X0 + 60, X1 - 40, 70):
                cv2.circle(img, (int(x), int(TY - TH / 2 + 8)), 4, (255, 236, 160), -1, cv2.LINE_AA)
        rng = np.random.default_rng(5)
        px0 = rng.uniform(X0 + 330, X0 + 900, 16)
        for i in range(16):
            x = px0[i]
            run = mode == "collapse" and t > ct
            if run:
                x = x + (t - ct) * rng.uniform(40, 80)
            _person(img, x, TY + TH / 2 - 4, 7, (220, 214, 200), t * (9 if run else 3) + i, run)
        if mode == "collapse" and t > ct - 0.6:
            rk = prog(t, ct - 0.6, 0.6)
            for j in range(10):
                bx = loc_x + rng.uniform(0, 250)
                by = lerp(TY - TH / 2, TY + TH / 2 - 6, (rk * rng.uniform(0.7, 1.3)) % 1.0)
                cv2.rectangle(img, (int(bx), int(by)), (int(bx + 8), int(by + 5)), BRICK, -1)
        if mode == "collapse":
            k = ease_in(prog(t, ct, 0.5))
            if k > 0:
                cx0, cx1 = X0 + 20, loc_x + 200 * FT
                top = np.array([[x, TY - TH / 2 - 40 + 30 * math.sin(x / 11.0)] for x in np.linspace(cx0, cx1, 40)])
                fill_poly(img, np.vstack([top + [0, k * 80], [[cx1, TY + TH / 2], [cx0, TY + TH / 2]]]), CLAY_DK)
        cam = (2.6, 380, TY - 10)
        S += [("LOCOMOTORA 231 · 10 VAGONES", W * 0.42, 330, ease_out(prog(t, t0 + 0.2, 0.4)) * (1 if t < ct else 0), 50, YELLOW, "c")]
        if mode == "work":
            S += [("≈ 200 HOMBRES DENTRO", W / 2, 960, ease_out(prog(t, t0 + 0.6, 0.4)), 56, WHITE, "c"),
                  ("BOCA OESTE", 362, 760, 0.9, 40, GREY, "c")]
        else:
            S += [("PARPADEAN LAS LUCES", W / 2, 960, ease_out(prog(t, t0 + 0.6, 0.3)) * (1 - prog(t, ct, 0.2)), 56, YELLOW, "c")]
    elif mode == "rescue":
        _tube(img, arch=BRICK)
        _locomotive(img, loc_x, TY + TH / 2 - 6, 0.55, crushed=1.0)
        fill_poly(img, [[X0 + 20, TY - TH / 2], [loc_x + 200 * FT, TY - TH / 2], [loc_x + 200 * FT, TY + TH / 2], [X0 + 20, TY + TH / 2]], CLAY_DK)
        sx = loc_x + 70
        sy = float(np.interp(sx, xs, ys))
        depth = lerp(0, TY - TH / 2 - sy, ease_io(prog(t, t0, max(dur - 1.5, 1.0))))
        wob = 5 * math.sin(t * 2.0)
        fill_poly(img, [[sx - 34 + wob, sy], [sx + 34 - wob, sy], [sx + 22, sy + depth], [sx - 22, sy + depth]], (20, 18, 16))
        fill_poly(img, [[sx + 60, sy - 4], [sx + 60, sy - 46], [sx + 130, sy - 46], [sx + 130, sy - 4]], (50, 50, 54))
        aa_poly(img, [[sx + 70, sy - 46], [sx + 18, sy - 110], [sx - 6, sy - 30]], (70, 70, 74), 7)
        for k in range(4):
            ph = (t * 0.6 + k * 0.25) % 1.0
            cv2.circle(img, (int(sx + 110 + 26 * ph), int(sy - 56 - 100 * ph)), int(8 + 16 * ph), (200, 200, 200), -1, cv2.LINE_AA)
        for i in range(8):
            _person(img, sx + 160 + i * 26, sy + 2, 7, (200, 196, 186), i, False)
        cam = (1.6, 610, (sy + TY) / 2 - 10)
        S += [("UNA PALA DE VAPOR, DESDE ARRIBA", W / 2, 70, ease_out(prog(t, 0.2, 0.4)), 58, YELLOW, "c"),
              ("CADA VEZ QUE AVANZABAN, LA ARCILLA SE DERRUMBABA", W / 2, 980, ease_out(prog(t, t0 + 2.0, 0.4)), 46, WHITE, "c")]
    elif mode == "teaser":
        _tube(img, arch=BRICK)
        _locomotive(img, loc_x, TY + TH / 2 - 6, 0.55, crushed=1.0)
        fill_poly(img, [[X0 + 20, TY - TH / 2], [loc_x + 200 * FT, TY - TH / 2], [loc_x + 200 * FT, TY + TH / 2], [X0 + 20, TY + TH / 2]], CLAY_DK)
        layer = img.copy()
        fill_poly(layer, [[loc_x + 200 * FT, TY - TH / 2], [X1, TY - TH / 2], [X1, TY + TH / 2], [loc_x + 200 * FT, TY + TH / 2]], SAND)
        cv2.addWeighted(layer, 0.85, img, 0.15, 0, img)
        _portal(img, X0, plug=True)
        _portal(img, X1, plug=True)
        L += [("JEFFERSON PARK", 450, 220, ease_out(prog(t, t0, 0.4)), 48, (150, 210, 150), "c")]
        S += [("DEBAJO NO SOLO HAY UN TREN", W / 2, 960, ease_out(prog(t, t0 + 0.8, 0.4)), 56, YELLOW, "c")]
    elif mode in ("seal", "today"):
        sk = 1.0 if mode == "today" else ease_io(prog(t, t0 + 0.4, 2.2))
        _tube(img, arch=BRICK)
        _locomotive(img, loc_x, TY + TH / 2 - 6, 0.55, crushed=1.0)
        fill_poly(img, [[X0 + 20, TY - TH / 2], [loc_x + 200 * FT, TY - TH / 2], [loc_x + 200 * FT, TY + TH / 2], [X0 + 20, TY + TH / 2]], CLAY_DK)
        if sk > 0:
            xe = lerp(X1, loc_x + 200 * FT, sk)
            layer = img.copy()
            fill_poly(layer, [[xe, TY - TH / 2], [X1, TY - TH / 2], [X1, TY + TH / 2], [xe, TY + TH / 2]], SAND)
            cv2.addWeighted(layer, 0.85, img, 0.15, 0, img)
        pk = 1.0 if mode == "today" else ease_back(prog(t, t0 + 2.8, 0.4))
        if pk > 0:
            _portal(img, X0, plug=True)
            _portal(img, X1, plug=True)
        if mode == "seal":
            S += [("ARENA · Y DOS TAPONES DE CONCRETO", W / 2, 960, ease_out(prog(t, t0 + 1.0, 0.4)), 54, YELLOW, "c"),
                  ("PRIMAVERA DE 1926", W / 2, 110, ease_out(prog(t, 0.1, 0.4)), 64, WHITE, "c")]
            L += [("LA 231, 10 VAGONES Y DOS JORNALEROS", loc_x + 60, TY - 150, ease_out(prog(t, t0 + 3.4, 0.4)), 44, WHITE, "l")]
        else:
            layer = img.copy()
            fill_poly(layer, [[X1 - 420, TY - 6], [X1, TY - 6], [X1, TY + TH / 2], [X1 - 420, TY + TH / 2]], WATER)
            cv2.addWeighted(layer, 0.85, img, 0.15, 0, img)
            L += [("BOCA OESTE: TAPÓN Y REJA", X0 + 30, TY - 150, ease_out(prog(t, t0, 0.4)), 44, WHITE, "l"),
                  ("BOCA ESTE: INUNDADA", X1 - 30, TY - 150, ease_out(prog(t, t0 + 0.8, 0.4)), 44, (150, 190, 225), "r"),
                  ("JEFFERSON PARK", 450, 220, ease_out(prog(t, t0 + 1.4, 0.4)), 48, (150, 210, 150), "c")]
    z, cx, cy = cam
    img, f = _cam(img, z, cx, cy)
    if mode == "collapse":
        ct = t0 + 2.0
        if t > ct:
            dk = ease_out(prog(t, ct, 0.35))
            img[:] = (img.astype(np.float32) * (1 - 0.86 * dk)).astype(np.uint8)
            S += [("SE VIENE ABAJO EL TECHO: ≈ 200 PIES · ≈ 60 M", W / 2, 140, ease_out(prog(t, ct + 0.3, 0.4)), 56, RED, "c"),
                  ("LAS LUCES SE APAGAN", W / 2, 960, ease_out(prog(t, ct + 1.0, 0.4)), 56, WHITE, "c")]
    for (txt, x, y, a, size, col, anc) in L:
        sx, sy = f(x, y)
        label(img, txt, sx, sy, a, size, col, anchor=anc)
    for (txt, x, y, a, size, col, anc) in S:
        label(img, txt, x, y, a, size, col, anchor=anc)
    return img


def plasticine(t, dur, close_t=None):
    """Digging in wet clay is like a hole in a block of wet plasticine: it holds a while, then wants to close."""
    img = background("dark_grid", t)
    bx0, bx1, by0, by1 = 560, 1360, 360, 820
    cv2.rectangle(img, (bx0, by0), (bx1, by1), CLAY, -1)
    for i in range(10):
        y = by0 + 20 + i * 44
        cv2.line(img, (bx0, y), (bx1, y + 6), CLAY_DK, 3, cv2.LINE_AA)
    k_open = ease_out(prog(t, 0.4, 0.8))
    ct = close_t if close_t is not None else dur * 0.55
    k_close = ease_in(prog(t, ct, dur - ct - 0.3))
    r = 120 * k_open * (1 - 0.85 * k_close)
    if r > 2:
        ang = np.linspace(0, math.pi, 30)
        arc = np.stack([W / 2 + np.cos(ang) * r * 1.2, by1 - np.sin(ang) * r * 1.6], 1)
        fill_poly(img, np.vstack([arc, [[W / 2 - r * 1.2, by1]]]), (14, 14, 16))
        # sagging roof arrows
        if k_close > 0.05:
            for dx in (-60, 0, 60):
                cv2.arrowedLine(img, (int(W / 2 + dx), int(by1 - r * 1.6 - 90)), (int(W / 2 + dx), int(by1 - r * 1.6 - 20)), YELLOW, 5,
                                cv2.LINE_AA, tipLength=0.35)
    label(img, "PLASTILINA MOJADA", W / 2, 260, ease_out(prog(t, 0.2, 0.4)), 64, (170, 190, 215))
    label(img, "EL HUECO AGUANTA UN RATO…", W / 2, 900, ease_out(prog(t, 0.8, 0.4)) * (1 - prog(t, ct - 0.3, 0.3)), 52, WHITE)
    label(img, "…PERO SIEMPRE QUIERE CERRARSE", W / 2, 900, ease_out(prog(t, ct, 0.4)), 52, YELLOW)
    return img


def tunnel_run(t, dur, t0=0.3):
    """Top-down strip of the tunnel: the west mouth blocked, men running ~3/4 mile east in the dark towards the light."""
    img = np.full((H, W, 3), 6, np.uint8)
    y0, y1 = 470, 610
    cv2.rectangle(img, (X0, y0), (X1, y1), (22, 22, 24), -1)
    glow = np.zeros_like(img)
    cv2.circle(glow, (X1, (y0 + y1) // 2), 90, (255, 240, 200), -1, cv2.LINE_AA)
    glow = cv2.GaussianBlur(glow, (0, 0), 40)
    img[:] = np.clip(img.astype(np.int32) + glow.astype(np.int32), 0, 255).astype(np.uint8)
    fill_poly(img, [[X0, y0], [X0 + 90, y0], [X0 + 70, y1], [X0, y1]], CLAY_DK)
    label(img, "DERRUMBE", X0 + 50, y0 - 46, ease_out(prog(t, t0, 0.4)), 40, RED)
    rng = np.random.default_rng(8)
    for i in range(40):
        sp = rng.uniform(70, 140)
        x = X0 + 200 + rng.uniform(0, 500) + max(0, t - t0) * sp
        if x > X1 - 10:
            continue
        y = rng.uniform(y0 + 14, y1 - 14) + 4 * math.sin(t * 9 + i)
        cv2.circle(img, (int(x), int(y)), 6, (210, 204, 190), -1, cv2.LINE_AA)
    label(img, "BOCA ESTE", X1 - 40, y1 + 60, 1.0, 44, YELLOW)
    label(img, "≈ ¾ DE MILLA A OSCURAS · MÁS DE 1 KM", W / 2, 820, ease_out(prog(t, t0 + 1.0, 0.4)), 54, WHITE)
    label(img, "VISTA DESDE ARRIBA · ESQUEMA", W - 220, H - 46, 0.6, 30, GREY)
    return img


def coffin(t, dur, n_t=1.0, a_t=1.8, b_t=2.8, bottom="ERA EL NÚMERO DE SU LOCOMOTORA"):
    img = background("black", t)
    k = ease_out(prog(t, 0.2, 1.0))
    pts = np.array([[-260, -60], [-140, -110], [300, -80], [330, 0], [300, 80], [-140, 110], [-260, 60]], np.float64)
    pts = pts * lerp(0.9, 1.0, k) + [W / 2, H / 2 + 40]
    _poly(img, pts, (92, 60, 40), k)
    aa_poly(img, np.vstack([pts, pts[:1]]), (130, 92, 62), 6)
    nk = ease_out(prog(t, n_t, 0.8))
    if nk > 0:
        sp = text_sprite("231", "bebas", 170, (236, 230, 214), False, tracking=8)
        over_center(img, sp, W / 2 + 30, H / 2 + 46, nk)
    if a_t is not None:
        label(img, "NO ERA SU EDAD NI SU FECHA", W / 2, 180, ease_out(prog(t, a_t, 0.4)), 56, WHITE)
    if b_t is not None:
        label(img, bottom, W / 2, 900, ease_out(prog(t, b_t, 0.4)), 56, YELLOW)
    label(img, "ILUSTRACIÓN", W - 150, H - 46, 0.7, 30, GREY)
    return img


def company_list(t, dur, mode="list", hl_t=2.6, row_t=0.4, c1=0.6, c2=2.0):
    """Recreated company list: three missing, then two; one with a single initial."""
    img = background("dark_grid", t)
    pw, ph = 1000, 900
    paper = np.full((ph, pw, 3), PAPER, np.uint8)

    def txt(s, x, y, size, col=INK, f="type", a=1.0):
        sp = text_sprite(s, f, size, col, False)
        over(paper, sp, x - 24, y - sp.h / 2, a)

    txt("C&O · OBRA DEL TÚNEL DE CHURCH HILL", 70, 80, 34)
    txt("2 DE OCTUBRE DE 1925 · DESAPARECIDOS", 70, 130, 34)
    cv2.line(paper, (60, 170), (pw - 60, 170), (120, 112, 100), 2)
    rows = [("THOMAS MASON", "MAQUINISTA"), ("RICHARD LEWIS", "JORNALERO"), ("H. SMITH", "JORNALERO")]
    for i, (n, r) in enumerate(rows):
        a = ease_out(prog(t, row_t + 0.5 * i, 0.4)) if mode == "list" else 1.0
        y = 260 + i * 120
        txt(n, 90, y, 52, INK, "type", a)
        txt(r, 640, y, 34, (90, 84, 76), "type", a)
    if mode in ("list",):
        hk = ease_out(prog(t, hl_t, 0.5))
        if hk > 0:
            cv2.ellipse(paper, (190, 500), (150, 52), -3, 0, 360, (180, 30, 40), 5, cv2.LINE_AA)
            txt("SOLO UNA INICIAL", 90, 590, 34, (180, 30, 40), "type", hk)
    if mode == "count":
        k = ease_out(prog(t, c1, 0.4))
        cv2.line(paper, (80, 640), (900, 640), (120, 112, 100), 2, cv2.LINE_AA)
        txt("LISTA OFICIAL: 3, LUEGO 2", 90, 720, 44, (180, 30, 40), "type", k)
        txt("OBREROS: «ENTRE 10 Y 15»", 90, 790, 40, INK, "type", ease_out(prog(t, c2, 0.4)))
    sprite = Sprite(np.dstack([paper, np.full(paper.shape[:2], 255, np.uint8)]))
    over_center(img, sprite, W / 2, H / 2 + 20, 1.0, 0.95)
    label(img, "RECREACIÓN", W - 150, H - 46, 0.75, 30, GREY)
    return img


def names_wall(t, dur, t0=0.2, step=0.75):
    img = background("black", t)
    names = [("MASON", WHITE), ("MOSBY", WHITE), ("LEWIS", WHITE), ("SMITH", (200, 196, 186))]
    for i, (n, c) in enumerate(names):
        a = ease_out(prog(t, t0 + i * step, 0.4))
        label(img, n, W / 2, 230 + i * 150, a, 120, c)
    k = ease_out(prog(t, t0 + 4 * step + 0.6, 0.6))
    if k > 0:
        for i in range(12):
            x = 260 + i * 125
            label(img, "?", x, 860, k * (0.3 + 0.7 * (i % 3 == 0)), 90, (120, 120, 124))
    return img


def history_line(t, dur, marks=None, title=None, t0=0.3, step=0.35):
    img = background("dark_grid", t)
    marks = marks or [("1775", "PATRICK HENRY"), ("1865", "RICHMOND ARDE"), ("1873", "EL TÚNEL"), ("1902", "SE ABANDONA"),
                      ("1925", "EL DERRUMBE"), ("1926", "SELLADO"), ("2025", "100 AÑOS")]
    y = 560
    x0, x1 = 180, 1740
    k = ease_io(prog(t, t0, 1.2))
    cv2.line(img, (x0, y), (int(lerp(x0, x1, k)), y), (120, 122, 126), 4, cv2.LINE_AA)
    n = len(marks)
    for i, (yr, txt) in enumerate(marks):
        x = x0 + (x1 - x0) * i / (n - 1)
        a = ease_out(prog(t, t0 + 0.4 + i * step, 0.35))
        if a <= 0:
            continue
        col = YELLOW if yr in ("1925", "1926") else WHITE
        cv2.circle(img, (int(x), y), 14, col, -1, cv2.LINE_AA)
        label(img, yr, x, y - 70 if i % 2 == 0 else y + 70, a, 60, col)
        label(img, txt, x, y - 130 if i % 2 == 0 else y + 130, a, 34, GREY)
    if title:
        label(img, title, W / 2, 140, ease_out(prog(t, 0.1, 0.4)), 60, WHITE)
    return img


def verdict(t, dur):
    img = background("dark_grid", t)
    pw, ph = 1080, 880
    paper = np.full((ph, pw, 3), PAPER, np.uint8)

    def txt(s, x, y, size, col=INK, f="type", a=1.0, anchor="l"):
        sp = text_sprite(s, f, size, col, False)
        xx = x if anchor == "l" else x - sp.w / 2
        over(paper, sp, xx - 24, y - sp.h / 2, a)

    txt("VEREDICTO DEL JURADO FORENSE", pw / 2, 90, 50, INK, "serif", anchor="c")
    txt("RICHMOND, OCTUBRE DE 1925", pw / 2, 160, 34, INK, "type", anchor="c")
    cv2.line(paper, (80, 200), (pw - 80, 200), (120, 112, 100), 2)
    lines = ["THOMAS MASON MURIÓ POR LA", "NEGLIGENCIA DE LOS RESPONSABLES", "DE LA C&O AL APUNTALAR EL TÚNEL."]
    for i, l in enumerate(lines):
        txt(l, 100, 300 + i * 80, 42, INK, "type", ease_out(prog(t, 0.4 + 0.5 * i, 0.4)))
    hk = ease_out(prog(t, 2.2, 0.6))
    if hk > 0:
        layer = paper.copy()
        cv2.rectangle(layer, (80, 352), (int(80 + 700 * hk), 412), (60, 200, 240), -1)
        cv2.addWeighted(layer, 0.45, paper, 0.55, 0, paper)
        txt("NEGLIGENCIA DE LOS RESPONSABLES", 100, 380, 42, INK)
    sk = ease_io(prog(t, 3.0, 1.0))
    if sk > 0:
        xs_ = np.linspace(0, 1, 90)
        sig = np.stack([560 + 360 * xs_, 700 - 30 * np.sin(xs_ * 19) * np.exp(-xs_ * 1.4) - 14 * xs_], 1)
        aa_poly(paper, partial_line(sig, sk), (30, 40, 110), 3)
    cv2.line(paper, (540, 740), (960, 740), (110, 104, 96), 1)
    sprite = Sprite(np.dstack([paper, np.full(paper.shape[:2], 255, np.uint8)]))
    over_center(img, sprite, W / 2, H / 2 + 20, 1.0, 0.95)
    label(img, "RECREACIÓN", W - 150, H - 46, 0.75, 30, GREY)
    return img


def warnings2(t, dur, t1=0.3, t2=1.4, t3=2.8):
    img = background("dark_grid", t)
    for i, (yr, a1, a2, tt) in enumerate((("1873", "SE TRAGA CASAS", "", t1), ("1925", "LADRILLOS AL AGUA", "LUCES QUE PARPADEAN", t2))):
        cx = W * (0.28 + 0.44 * i)
        a = ease_out(prog(t, tt, 0.4))
        label(img, "AVISO " + str(i + 1), cx, 300, a, 50, GREY)
        label(img, yr, cx, 420, a, 150, YELLOW)
        label(img, a1, cx, 560, a, 50, WHITE)
        if a2:
            label(img, a2, cx, 630, a, 50, WHITE)
    cv2.line(img, (W // 2, 260), (W // 2, 700), (70, 72, 76), 2)
    label(img, "Y LAS DOS VECES SE SIGUIÓ ADELANTE", W / 2, 860, ease_out(prog(t, t3, 0.4)), 58, RED)
    return img


def why_sealed(t, dur, items=None, t0=0.3, step=1.2, times=None):
    img = background("dark_grid", t)
    items = items or [("LA COLINA YA NO DEJABA ENTRAR", WHITE), ("ERA LO MÁS BARATO", YELLOW), ("UN JURADO HABLÓ DE NEGLIGENCIA", YELLOW),
                      ("FALTABAN JORNALEROS QUE CASI NADIE CONTÓ", RED)]
    for i, (s, c) in enumerate(items):
        a = ease_out(prog(t, times[i] if times else t0 + i * step, 0.4))
        y = 300 + i * 150
        if a > 0:
            cv2.rectangle(img, (240, int(y - 40)), (252, int(y + 40)), c, -1)
        label(img, s, 300, y, a, 64, c, anchor="l")
    label(img, "¿POR QUÉ SE SELLÓ?", W / 2, 140, ease_out(prog(t, 0.1, 0.4)), 60, GREY)
    return img
