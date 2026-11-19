"""Kiowa Creek (Bennett, Colorado, 1878-1997): diagrams drawn in code for this episode."""
import math

import cv2
import numpy as np

from engine import BLACK, H, RED, W, WHITE, YELLOW, Sprite, clamp, ease_back, ease_in, ease_io, ease_out, lerp, over, \
    over_center, prog, rounded_rect_sprite, text_sprite
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

SAND = (200, 178, 132)
SAND_DK = (162, 140, 100)
SAND_WET = (126, 108, 80)
SOIL = (92, 76, 58)
SOIL_DK = (70, 58, 46)
FILL = (146, 124, 92)
FILL_DK = (100, 84, 64)
GRASS = (92, 110, 64)
TIMBER = (150, 112, 70)
TIMBER_DK = (104, 76, 46)
MUD = (92, 70, 48)
MUD_HI = (150, 126, 96)
WATER = (40, 84, 120)
WATER_HI = (90, 150, 190)
IRON = (54, 56, 62)
IRON_HI = (96, 98, 106)
INK = (34, 32, 30)
PAPER = (234, 228, 212)
NIGHT_TOP, NIGHT_BOT = (6, 8, 14), (18, 22, 32)
DAY_TOP, DAY_BOT = (96, 132, 170), (176, 192, 204)


def _grad(top, bot):
    g = np.linspace(0, 1, H)[:, None, None]
    img = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    return np.repeat(img, W, axis=1).astype(np.uint8)


def _poly(img, pts, col, alpha=1.0):
    if alpha <= 0.001:
        return
    if alpha >= 0.999:
        fill_poly(img, pts, col)
        return
    layer = img.copy()
    fill_poly(layer, pts, col)
    cv2.addWeighted(layer, alpha, img, 1 - alpha, 0, img)


def _blend(img, layer, a):
    if a > 0.001:
        cv2.addWeighted(layer, a, img, 1 - a, 0, img)


def _rain(img, t, n=260, col=(170, 180, 200), a=0.5, seed=0, slant=0.25, length=38):
    rng = np.random.default_rng(seed + int(t * 30) % 6)
    layer = img.copy()
    xs = rng.uniform(-100, W + 100, n)
    ys = rng.uniform(-50, H, n)
    for x, y in zip(xs, ys):
        cv2.line(layer, (int(x), int(y)), (int(x - slant * length), int(y + length)), col, 1, cv2.LINE_AA)
    _blend(img, layer, a)


def _tag(img, txt, a=0.7):
    label(img, txt, W - 160, H - 46, a, 30, GREY)


# ---------------------------------------------------------------- rolling stock (side view)
def _xf(pts, x, y, s, facing, ang):
    p = np.array(pts, np.float64) * s
    p[:, 0] *= facing
    c, sn = math.cos(ang), math.sin(ang)
    return p @ np.array([[c, sn], [-sn, c]]) + [x, y]


def _wheel(img, cx, cy, r, col=(70, 70, 76), spokes=True, rot=0.0):
    cv2.circle(img, (int(cx), int(cy)), int(r), col, -1, cv2.LINE_AA)
    cv2.circle(img, (int(cx), int(cy)), int(r), (24, 24, 26), max(1, int(r / 7)), cv2.LINE_AA)
    if spokes and r > 8:
        for k in range(6):
            a = rot + k * math.pi / 3
            cv2.line(img, (int(cx), int(cy)), (int(cx + math.cos(a) * r * 0.8), int(cy + math.sin(a) * r * 0.8)),
                     (36, 36, 40), max(1, int(r / 10)), cv2.LINE_AA)
    cv2.circle(img, (int(cx), int(cy)), max(2, int(r * 0.18)), (30, 30, 32), -1, cv2.LINE_AA)


def loco(img, x, y, s=1.0, facing=1, ang=0.0, drivers=2, num="51", light=0.0, roll=0.0, col=IRON, a=1.0,
         tender=True):
    """1870s 4-4-0 'American' type. (x, y) = front of the pilot at rail level; facing=1 points right.
    Local frame: forward = +x, up = -y; units ~ px at s=1 (engine ~300 px long)."""
    tgt = img if a >= 0.999 else img.copy()

    def P(pts):
        return _xf(pts, x, y, s, facing, ang)

    body = col
    hi = IRON_HI
    # pilot (cow catcher)
    fill_poly(tgt, P([[0, 0], [-34, 0], [-12, -30], [0, -30]]), (120, 70, 50))
    # frame
    fill_poly(tgt, P([[-14, -24], [-250, -24], [-250, -36], [-14, -36]]), (40, 40, 44))
    # boiler
    fill_poly(tgt, P([[-30, -40], [-30, -88], [-196, -88], [-196, -40]]), body)
    fill_poly(tgt, P([[-30, -46], [-30, -82], [-24, -82], [-24, -46]]), hi)
    # smoke box front + headlight
    fill_poly(tgt, P([[-26, -88], [-26, -116], [-58, -116], [-58, -88]]), (130, 110, 60))
    fill_poly(tgt, P([[-22, -94], [-22, -110], [-30, -110], [-30, -94]]), (250, 230, 160) if light > 0 else (160, 150, 120))
    # balloon stack
    fill_poly(tgt, P([[-58, -88], [-62, -126], [-46, -150], [-94, -150], [-80, -126], [-84, -88]]), (60, 60, 66))
    fill_poly(tgt, P([[-42, -150], [-42, -160], [-98, -160], [-98, -150]]), (44, 44, 48))
    # domes
    for dx in (-118, -160):
        fill_poly(tgt, P([[dx + 10, -88], [dx + 8, -104], [dx, -110], [dx - 8, -104], [dx - 10, -88]]), (150, 124, 70))
    # cab
    fill_poly(tgt, P([[-196, -36], [-196, -132], [-252, -132], [-252, -36]]), (110, 70, 48))
    fill_poly(tgt, P([[-190, -138], [-258, -138], [-252, -130], [-196, -130]]), (70, 46, 34))
    fill_poly(tgt, P([[-204, -96], [-204, -120], [-226, -120], [-226, -96]]), (40, 34, 30))
    # number plate on the cab side
    if num:
        sp = text_sprite(num, "bebas", max(8, int(30 * s)), YELLOW, False)
        c = P([[-226, -70]])[0]
        over_center(tgt, sp, c[0], c[1], 1.0)
    # wheels: 2 small leading + drivers
    for wx in (-48, -84):
        c = P([[wx, -12]])[0]
        _wheel(tgt, c[0], c[1], 12 * s, rot=roll * 1.6)
    if drivers == 2:
        dxs = (-136, -184)
    else:
        dxs = (-118, -158, -198)
    for wx in dxs:
        c = P([[wx, -21]])[0]
        _wheel(tgt, c[0], c[1], 21 * s, rot=roll)
    rod = P([[dxs[0], -21 + 8 * math.sin(roll)], [dxs[-1], -21 + 8 * math.sin(roll)]])
    cv2.line(tgt, tuple(rod[0].astype(int)), tuple(rod[1].astype(int)), (170, 170, 176), max(2, int(4 * s)), cv2.LINE_AA)
    if tender:
        fill_poly(tgt, P([[-262, -28], [-262, -100], [-372, -100], [-372, -28]]), (66, 66, 72))
        fill_poly(tgt, P([[-262, -100], [-262, -108], [-372, -108], [-372, -100]]), (30, 30, 30))
        for wx in (-280, -310, -330, -360):
            c = P([[wx, -12]])[0]
            _wheel(tgt, c[0], c[1], 12 * s, rot=roll * 1.6)
    if light > 0:
        glow = np.zeros_like(img)
        c = P([[-22, -102]])[0]
        d = P([[400, -86]])[0] - c
        nd = d / max(np.hypot(*d), 1e-6)
        perp = np.array([-nd[1], nd[0]])
        L = 700 * s
        cone = np.array([c, c + nd * L + perp * 70 * s, c + nd * L - perp * 70 * s])
        fill_poly(glow, cone, (255, 236, 180))
        cv2.circle(glow, (int(c[0]), int(c[1])), int(20 * s), (255, 255, 230), -1, cv2.LINE_AA)
        glow = cv2.GaussianBlur(glow, (0, 0), 18 * s)
        if tgt is img:
            img[:] = np.clip(img.astype(np.int32) + (glow.astype(np.float32) * 0.55 * light).astype(np.int32), 0, 255)
        else:
            tgt[:] = np.clip(tgt.astype(np.int32) + (glow.astype(np.float32) * 0.55 * light).astype(np.int32), 0, 255)
    if tgt is not img:
        _blend(img, tgt, a)


def car(img, x, y, s=1.0, facing=1, ang=0.0, col=(118, 84, 60), a=1.0, kind="box"):
    """Freight car, (x, y) = front coupler at rail level. Length ~ 200 px at s=1."""
    tgt = img if a >= 0.999 else img.copy()

    def P(pts):
        return _xf(pts, x, y, s, facing, ang)

    if kind == "box":
        fill_poly(tgt, P([[-6, -26], [-6, -112], [-196, -112], [-196, -26]]), col)
        fill_poly(tgt, P([[-2, -112], [-200, -112], [-196, -120], [-6, -120]]), tuple(int(c * 0.7) for c in col))
        for k in range(1, 6):
            p = P([[-6 - 32 * k, -30], [-6 - 32 * k, -108]])
            cv2.line(tgt, tuple(p[0].astype(int)), tuple(p[1].astype(int)), tuple(int(c * 0.8) for c in col), max(1, int(2 * s)),
                     cv2.LINE_AA)
    else:  # flat car with scrap
        fill_poly(tgt, P([[-6, -26], [-6, -40], [-196, -40], [-196, -26]]), col)
        fill_poly(tgt, P([[-20, -40], [-40, -66], [-80, -58], [-120, -74], [-170, -60], [-186, -40]]), (88, 82, 78))
    for wx in (-30, -56, -146, -172):
        c = P([[wx, -12]])[0]
        _wheel(tgt, c[0], c[1], 12 * s, spokes=False)
    if tgt is not img:
        _blend(img, tgt, a)


# ---------------------------------------------------------------- the crossing, side view (west on the left)
GY = 640                 # plain level
RY = 500                 # rail level on the embankment
EX0, EX1 = 150, 1770     # embankment toes on the plain
CX0, CX1 = 560, 1360     # creek banks
BX0, BX1 = 870, 1050     # wooden bridge over the deepest part
BED = 735                # creek bed bottom


def ground_y(x):
    x = np.asarray(x, np.float64)
    k = np.clip((x - CX0) / (CX1 - CX0), 0, 1)
    dip = (BED - GY) * np.sin(np.pi * k) ** 0.6
    dip = np.where((x > CX0) & (x < CX1), dip, 0)
    return GY + dip + 4 * np.sin(x / 45.0)


def emb_top(x, k=1.0):
    """Embankment crest: rail level between the ramps, sloping down to the plain at the toes."""
    x = np.asarray(x, np.float64)
    up = np.clip((x - EX0) / 260.0, 0, 1)
    dn = np.clip((EX1 - x) / 260.0, 0, 1)
    ramp = np.minimum(up, dn)
    y = GY - (GY - RY) * ramp * k
    return y


def _section_bg(night=False, flood=0.0):
    img = _grad(NIGHT_TOP, NIGHT_BOT) if night else _grad(DAY_TOP, DAY_BOT)
    xs = np.linspace(0, W, 320)
    gy = ground_y(xs)
    # deep soil
    fill_poly(img, np.vstack([np.stack([xs, gy], 1), [[W, H], [0, H]]]), SOIL_DK if night else SOIL)
    # sand body under the creek
    sx = np.linspace(CX0 - 60, CX1 + 60, 120)
    sand_top = ground_y(sx)
    sand_bot = sand_top + 70 + 120 * np.sin(np.pi * np.clip((sx - CX0 + 60) / (CX1 - CX0 + 120), 0, 1)) ** 0.8
    pts = np.vstack([np.stack([sx, sand_top], 1), np.stack([sx[::-1], sand_bot[::-1]], 1)])
    fill_poly(img, pts, tuple(int(c * (0.45 if night else 1.0)) for c in (SAND_WET if flood > 0.5 else SAND_DK)))
    bed = np.stack([sx, sand_top], 1)
    aa_poly(img, bed, tuple(int(c * (0.5 if night else 1.0)) for c in SAND), 8)
    # grass on the plain
    for x0, x1 in ((0, CX0 + 10), (CX1 - 10, W)):
        gx = np.linspace(x0, x1, 60)
        aa_poly(img, np.stack([gx, ground_y(gx) - 2], 1), tuple(int(c * (0.4 if night else 1.0)) for c in GRASS), 7)
    return img, xs, gy


def _embankment(img, night=False, k=1.0, gap=None, bite=0.0):
    """Earth fill between the crest and the ground. gap=(x0, x1) leaves an opening (bridge or washout)."""
    xs = np.linspace(EX0, EX1, 400)
    top = emb_top(xs, k)
    gy = ground_y(xs)
    col = tuple(int(c * (0.45 if night else 1.0)) for c in FILL)
    dk = tuple(int(c * (0.45 if night else 1.0)) for c in FILL_DK)
    segs = [(EX0, EX1)] if gap is None else [(EX0, gap[0]), (gap[1], EX1)]
    for a, b in segs:
        m = (xs >= a) & (xs <= b)
        if m.sum() < 2:
            continue
        sx, st, sg = xs[m], top[m], gy[m]
        if gap is not None and bite > 0:
            # ragged eroded faces next to the gap
            d = np.minimum(np.abs(sx - gap[0]), np.abs(sx - gap[1]))
            st = st + bite * 60 * np.exp(-d / 70.0)
        pts = np.vstack([np.stack([sx, st], 1), np.stack([sx[::-1], sg[::-1]], 1)])
        fill_poly(img, pts, col)
        aa_poly(img, np.stack([sx, st], 1), dk, 5)
    return xs, top


def _rails(img, x0, x1, night=False, a=1.0, y=RY):
    tgt = img if a >= 0.999 else img.copy()
    for x in np.arange(x0 + 8, x1 - 4, 22):
        cv2.line(tgt, (int(x), int(y + 2)), (int(x + 12), int(y + 2)), (70, 56, 40) if not night else (40, 34, 28), 6)
    cv2.line(tgt, (int(x0), int(y - 4)), (int(x1), int(y - 4)), (150, 150, 156) if not night else (90, 90, 96), 4, cv2.LINE_AA)
    if tgt is not img:
        _blend(img, tgt, a)


def _trestle(img, x0=BX0, x1=BX1, night=False, a=1.0, temp=False, drop=0.0, tilt=0.0):
    tgt = img if a >= 0.999 else img.copy()
    col = TIMBER if not night else TIMBER_DK
    if temp:
        col = (176, 150, 104)
    cx = (x0 + x1) / 2
    xs = np.linspace(x0, x1, 4)
    for bx in xs:
        gb = float(ground_y(bx))
        p = np.array([[bx - 6, RY + 8], [bx + 6, RY + 8], [bx + 6, gb], [bx - 6, gb]], np.float64)
        p = _rot_about(p, cx, RY, tilt) + [0, drop]
        fill_poly(tgt, p, col)
    for i in range(3):
        a0, a1 = xs[i], xs[i + 1]
        g = float(ground_y((a0 + a1) / 2))
        for q in ([[a0, RY + 12], [a1, g - 10]], [[a1, RY + 12], [a0, g - 10]]):
            p = _rot_about(np.array(q, np.float64), cx, RY, tilt) + [0, drop]
            cv2.line(tgt, tuple(p[0].astype(int)), tuple(p[1].astype(int)), col, 4, cv2.LINE_AA)
    deck = _rot_about(np.array([[x0 - 10, RY - 2], [x1 + 10, RY - 2], [x1 + 10, RY + 12], [x0 - 10, RY + 12]], np.float64),
                      cx, RY, tilt) + [0, drop]
    fill_poly(tgt, deck, tuple(int(c * 0.8) for c in col))
    if tgt is not img:
        _blend(img, tgt, a)


def _rot_about(p, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    q = p - [cx, cy]
    return q @ np.array([[c, s], [-s, c]]) + [cx, cy]


def _water(img, level, col=MUD, a=0.92, t=0.0, x0=CX0 - 120, x1=CX1 + 120, hi=MUD_HI, seed=0, against=False):
    """Fill the creek channel up to screen y = level (only where the ground is lower).
    against=True: water piled against the embankment face, limited to where the fill is higher than the water."""
    xs = np.linspace(x0, x1, 300)
    gy = ground_y(xs)
    m = gy > level
    if against:
        m &= emb_top(xs) < level - 6
    if m.sum() < 2:
        return
    sx = xs[m]
    sg = gy[m]
    surf = level + 4 * np.sin(sx / 33.0 + t * 5) + 2 * np.sin(sx / 11.0 - t * 7)
    pts = np.vstack([np.stack([sx, surf], 1), np.stack([sx[::-1], sg[::-1]], 1)])
    layer = img.copy()
    fill_poly(layer, pts, col)
    _blend(img, layer, a)
    layer = img.copy()
    rng = np.random.default_rng(seed)
    n = int(len(sx) * 0.12)
    bx = rng.uniform(0, 1, n)
    by = rng.uniform(0, 1, n)
    ln = rng.uniform(40, 130, n)
    sp = rng.uniform(80, 220, n)
    span = max(sx[-1] - sx[0], 1)
    for f0, f, L, v in zip(bx, by, ln, sp):
        x = sx[0] + (f0 * span + t * v) % span
        gyx = float(ground_y(x))
        y = level + 12 + f * (gyx - level - 18)
        if y > gyx - 6:
            continue
        cv2.line(layer, (int(x), int(y)), (int(min(x + L, sx[-1])), int(y)), hi, 2, cv2.LINE_AA)
    aa_poly(layer, np.stack([sx, surf], 1), hi, 3)
    _blend(img, layer, 0.55 * a)


def crossing(t, dur, mode="dry", t0=0.3, fall_t=None, labels=True, bt=None, tender_t=None, temp_t=None, no_t=None,
             pit_t=None, dig_d=None, cars=True):
    """Side view of the Kansas Pacific crossing of Kiowa Creek. Modes:
    dry | build | flood | gap | fall | recover | search | shuffle | magnet."""
    night = mode in ("gap", "fall")
    img, xs, gy = _section_bg(night, flood=1.0 if mode in ("gap", "fall") else 0.0)
    if mode == "build":
        k = ease_io(prog(t, t0, 1.6))
        bt_ = bt if bt is not None else t0 + 1.4
        _embankment(img, False, k, gap=(BX0, BX1) if prog(t, bt_ - 0.2, 0.1) > 0 else None)
        bk = ease_out(prog(t, bt_, 0.8))
        if bk > 0:
            _trestle(img, a=bk)
            _rails(img, EX0 + 200, EX1 - 200, a=bk)
        if labels:
            label(img, "TERRAPLÉN", 380, 380, ease_out(prog(t, t0 + 0.8, 0.4)), 54, WHITE)
            label(img, "PUENTE DE MADERA", (BX0 + BX1) / 2, 360, ease_out(prog(t, bt_ + 0.5, 0.4)), 54, YELLOW)
        _tag(img, "ESQUEMA")
        return img
    if mode == "dry":
        _embankment(img, False, 1.0, gap=(BX0, BX1))
        _trestle(img)
        _rails(img, EX0 + 200, EX1 - 200)
        if labels:
            label(img, "KIOWA CREEK · ARENA Y CASI NUNCA AGUA", W / 2, 140, ease_out(prog(t, t0, 0.4)), 58, WHITE)
            label(img, "TERRAPLÉN", 330, 420, ease_out(prog(t, t0 + 0.5, 0.4)), 46, (220, 214, 200))
            label(img, "PUENTE DE MADERA", (BX0 + BX1) / 2, 410, ease_out(prog(t, t0 + 0.9, 0.4)), 46, YELLOW)
            label(img, "ARENA", 1240, 800, ease_out(prog(t, t0 + 1.3, 0.4)), 46, (240, 226, 190))
        _tag(img, "ESQUEMA")
        return img
    if mode == "flood":
        lvl = lerp(BED + 10, RY + 40, ease_io(prog(t, t0, dur * 0.45)))
        bite = ease_in(prog(t, t0 + dur * 0.45, dur * 0.35))
        gap0 = (lerp(BX0, BX0 - 160, bite), lerp(BX1, BX1 + 140, bite))
        _embankment(img, False, 1.0, gap=gap0, bite=bite)
        if bite < 0.7:
            _trestle(img, drop=bite * 260, tilt=bite * 0.6, a=1 - ease_in(prog(bite, 0.3, 0.4)))
        _rails(img, EX0 + 200, gap0[0] - 10)
        _rails(img, gap0[1] + 10, EX1 - 200)
        _water(img, lvl, (58, 96, 128), 0.85, t, EX0, EX1, hi=(130, 176, 210), against=True)
        if labels:
            label(img, "NO CABE BAJO EL PUENTE", W / 2, 140, ease_out(prog(t, t0 + 0.6, 0.4)) * (1 - prog(t, t0 + dur * 0.45, 0.3)), 58, WHITE)
            label(img, "SE COME LA TIERRA DE LOS LADOS", W / 2, 140, ease_out(prog(t, t0 + dur * 0.45 + 0.2, 0.4)), 58, YELLOW)
        _tag(img, "ESQUEMA")
        return img
    gap = (BX0 - 160, BX1 + 140)
    if mode in ("gap", "fall"):
        lvl = RY + 70
        _embankment(img, True, 1.0, gap=gap, bite=1.0)
        _water(img, lvl, (30, 28, 24), 0.95, t, gap[0], gap[1], hi=(70, 66, 60))
        _rails(img, EX0 + 200, gap[0] - 10, night=True)
        _rails(img, gap[1] + 10, EX1 - 200, night=True)
        if mode == "fall":
            ft = fall_t if fall_t is not None else dur * 0.55
            v = 330.0
            front = gap[0] - 10 + v * (t - ft)
            n_cars = 6
            if t < ft:
                loco(img, front, RY - 4, 0.62, 1, 0.0, light=1.0, roll=t * 7)
                for i in range(n_cars):
                    car(img, front - 0.62 * 380 - i * 0.62 * 204, RY - 4, 0.62, kind="box" if i % 2 else "flat")
            else:
                k = ease_in(prog(t, ft, 0.9))
                lx = gap[0] + 60 + 110 * ease_out(prog(t, ft, 1.0))
                ly = lerp(RY - 4, RY + 150, k)
                loco(img, lx, ly, 0.62, 1, -0.75 * k, light=1.0 - 0.8 * k)
                for i in range(n_cars):
                    ti = ft + 0.25 + 0.22 * i
                    kk = ease_in(prog(t, ti, 0.7))
                    base = gap[0] - 10 - 0.62 * 380 - i * 0.62 * 204 + v * min(t - ft, 0.3 + 0.22 * i)
                    cx = base + 80 * kk
                    cy = lerp(RY - 4, RY + 110 - 30 * i, kk) if i < 3 else RY - 4
                    car(img, cx, cy, 0.62, 1, (-0.5 + 0.25 * i) * kk if i < 3 else 0.0, kind="box" if i % 2 else "flat")
            _water(img, lvl, (30, 28, 24), 0.45, t, gap[0], gap[1], hi=(70, 66, 60))
            _rain(img, t, 220, (120, 130, 150), 0.5, seed=3)
        else:
            _rain(img, t, 200, (110, 120, 140), 0.45, seed=5)
            if labels:
                label(img, "DONDE HABÍA VÍA, UN HUECO LLENO DE AGUA", W / 2, 150, ease_out(prog(t, t0, 0.4)), 56, WHITE)
        _tag(img, "ESQUEMA")
        return img
    # after the flood: daylight, low water
    if mode == "recover":
        _embankment(img, False, 1.0, gap=gap, bite=1.0)
        _water(img, BED - 20, MUD, 0.85, t, gap[0], gap[1])
        tk = ease_out(prog(t, temp_t if temp_t is not None else t0 + 2.6, 0.8))
        if tk > 0:
            _trestle(img, gap[0], gap[1], temp=True, a=tk)
            _rails(img, gap[0] - 10, gap[1] + 10, a=tk)
        _rails(img, EX0 + 200, gap[0] - 10)
        _rails(img, gap[1] + 10, EX1 - 200)
        # cars come out one by one
        for i in range(4 if cars else 0):
            ti = t0 + 0.3 + 0.45 * i
            k = ease_in(prog(t, ti, 0.6))
            if k >= 1:
                continue
            cx = gap[0] + 120 + 150 * i
            car(img, cx + 160, BED - 10 - 360 * k, 0.55, 1, 0.3 - 0.2 * i, a=1 - k, kind="box" if i % 2 else "flat")
        # the tender
        k = ease_in(prog(t, tender_t if tender_t is not None else t0 + 2.1, 0.6))
        if k < 1 and cars:
            p = np.array([[0, 0], [110, 0], [110, -70], [0, -70]], np.float64) * 0.62 + [gap[1] - 170, BED - 6 - 300 * k]
            _poly(img, p, (66, 66, 72), 1 - k)
        if labels:
            label(img, "VAGONES: SÍ", W * 0.36, 140, ease_out(prog(t, t0 + 0.4, 0.4)), 58, WHITE)
            label(img, "TÉNDER: SÍ", W * 0.64, 140, ease_out(prog(t, tender_t if tender_t is not None else t0 + 2.1, 0.4)), 58, WHITE)
            lk = ease_out(prog(t, no_t if no_t is not None else t0 + 3.4, 0.5))
            label(img, "LA LOCOMOTORA: NO", W / 2, 230, lk, 64, RED)
        _tag(img, "ESQUEMA")
        return img
    if mode in ("search", "shuffle", "magnet"):
        _embankment(img, False, 1.0, gap=gap, bite=1.0)
        _trestle(img, gap[0], gap[1], temp=True)
        _rails(img, EX0 + 200, EX1 - 200)
    if mode == "search":
        # 40 ft pit dug into the creek bed, rods probing, sand sliding back
        px = 950
        depth_px = 300
        k = ease_io(prog(t, pit_t if pit_t is not None else t0 + 0.4, dig_d if dig_d is not None else dur * 0.45))
        d = depth_px * k
        top = float(ground_y(px))
        pit = np.array([[px - 120, top], [px + 120, top], [px + 60, top + d], [px - 60, top + d]], np.float64)
        pit_ext = np.array([[px - 120, top], [px + 120, top], [px + 60, top + d], [px - 60, top + d]], np.float64)
        img_wet = img.copy()
        fill_poly(img_wet, pit_ext, (36, 30, 24))
        _blend(img, img_wet, 1.0)
        # sliding sand on the walls
        rng = np.random.default_rng(int(t * 10))
        for _ in range(int(18 * k)):
            yy = rng.uniform(top, top + d)
            side = rng.choice([-1, 1])
            xx = px + side * lerp(120, 60, (yy - top) / max(d, 1)) - side * rng.uniform(0, 12)
            cv2.line(img, (int(xx), int(yy)), (int(xx - side * 8), int(yy + 16)), SAND_DK, 2, cv2.LINE_AA)
        # rods
        for i, rx in enumerate((760, 820, 1090, 1150)):
            rk = ease_out(prog((t * 0.9 + i * 0.37) % 1.6, 0.0, 0.7))
            ry0 = float(ground_y(rx))
            cv2.line(img, (rx, int(ry0 - 60 + 120 * rk)), (rx, int(ry0 + 120 * rk + 20)), (150, 150, 156), 4, cv2.LINE_AA)
        # tiny diggers at the bottom
        if d > 60:
            for j in (-1, 1):
                fx, fy = px + j * 24, top + d
                cv2.circle(img, (int(fx), int(fy - 26)), 6, (220, 214, 200), -1, cv2.LINE_AA)
                cv2.line(img, (int(fx), int(fy - 20)), (int(fx), int(fy - 6)), (220, 214, 200), 3, cv2.LINE_AA)
        # ruler
        rx = px + 170
        cv2.line(img, (rx, int(top)), (rx, int(top + d)), WHITE, 3, cv2.LINE_AA)
        for f in range(0, 41, 10):
            yy = top + depth_px * f / 40.0
            if yy <= top + d + 1:
                cv2.line(img, (rx - 10, int(yy)), (rx + 10, int(yy)), WHITE, 3, cv2.LINE_AA)
        ft_now = int(round(40 * k))
        if k > 0:
            label(img, f"{ft_now} PIES", rx + 30, top + d, min(1.0, k * 4), 50, YELLOW, anchor="l")
        if labels:
            label(img, "VARILLAS DE HIERRO Y PALAS", W / 2, 140, ease_out(prog(t, t0, 0.4)), 58, WHITE)
            if k > 0.9:
                label(img, "40 PIES · MÁS DE 12 METROS", W / 2, 230, ease_out(prog(k, 0.9, 0.1)), 50, YELLOW)
        _tag(img, "ESQUEMA")
        return img
    if mode == "shuffle":
        # each flood reshuffles the sand layers; the '?' keeps moving
        sx = np.linspace(CX0 - 40, CX1 + 40, 120)
        st = ground_y(sx)
        n = 6
        for i in range(n):
            ph = t * 0.9 + i * 1.3
            y = st + 20 + i * 24 + 10 * np.sin(sx / (60 + 9 * i) + ph)
            aa_poly(img, np.stack([sx, y], 1), SAND if i % 2 else SAND_WET, 3)
        cyc = int(max(0, t - t0) / 1.1)
        rng = np.random.default_rng(cyc + 4)
        qx = rng.uniform(CX0 + 120, CX1 - 120)
        qy = float(ground_y(qx)) + rng.uniform(40, 150)
        a = 1 - prog((t - t0) % 1.1, 0.8, 0.3)
        label(img, "?", qx, qy, a * ease_out(prog((t - t0) % 1.1, 0.0, 0.25)), 110, YELLOW)
        if labels:
            label(img, "CADA CRECIDA BARAJA LA ARENA", W / 2, 140, ease_out(prog(t, t0, 0.4)), 58, WHITE)
        _tag(img, "ESQUEMA")
        return img
    if mode == "magnet":
        # a magnetometer sweeping the bed; a buried engine would bend the field lines (dashed ghost)
        mx = lerp(CX0 + 40, CX1 - 40, (math.sin(t * 0.7 - 1.2) + 1) / 2)
        my = float(ground_y(mx)) - 40
        cv2.circle(img, (int(mx), int(my)), 18, YELLOW, -1, cv2.LINE_AA)
        cv2.line(img, (int(mx), int(my + 18)), (int(mx), int(my + 40)), YELLOW, 3, cv2.LINE_AA)
        gk = ease_out(prog(t, t0 + 1.0, 0.6))
        if gk > 0:
            gx, gyy = 980, 860
            layer = img.copy()
            p = np.array([[0, 0], [-300, 0], [-300, -80], [0, -80]], np.float64) + [gx + 150, gyy]
            for k in range(len(p)):
                a0, a1 = p[k], p[(k + 1) % len(p)]
                n = int(np.hypot(*(a1 - a0)) / 18)
                for j in range(0, n, 2):
                    q0 = a0 + (a1 - a0) * j / n
                    q1 = a0 + (a1 - a0) * (j + 1) / n
                    cv2.line(layer, tuple(q0.astype(int)), tuple(q1.astype(int)), WHITE, 3, cv2.LINE_AA)
            for r in (120, 170, 220):
                cv2.ellipse(layer, (gx, gyy - 40), (r + 60, r // 2), 0, 180, 360, (120, 170, 220), 2, cv2.LINE_AA)
            _blend(img, layer, gk * 0.8)
            label(img, "UNA MOLE DE HIERRO DEFORMARÍA EL CAMPO", W / 2, 140, gk, 54, WHITE)
        _tag(img, "ESQUEMA")
        return img
    raise KeyError(mode)


# ---------------------------------------------------------------- plan view of the washout
def washout_plan(t, dur, t0=0.2, front_d=None, solo_t=None, erode_t=None, erode_d=None, cede_t=None):
    """Seen from above: the flood comes from the south, piles against the embankment, squeezes under the bridge,
    eats the fill on both sides and takes the bridge."""
    img = np.full((H, W, 3), (70, 74, 56), np.uint8)
    rng = np.random.default_rng(2)
    for _ in range(500):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        cv2.circle(img, (int(x), int(y)), int(rng.uniform(2, 5)), (78, 84, 60), -1)
    ys = np.arange(0, H + 1, 8)
    cxs = 960 + 70 * np.sin(ys / 190.0)
    hw = 230
    left = np.stack([cxs - hw, ys], 1)
    right = np.stack([cxs + hw, ys], 1)
    fill_poly(img, np.vstack([left, right[::-1]]), SAND)
    # flood front coming from the bottom (south)
    k_front = ease_io(prog(t, t0, front_d if front_d is not None else dur * 0.35))
    yf = lerp(H + 40, 0, k_front)
    k_wide = ease_out(prog(t, t0 + dur * 0.25, dur * 0.3))
    ew = hw + 140 * k_wide
    ey0, ey1 = 470, 560
    erode = ease_in(prog(t, erode_t if erode_t is not None else t0 + dur * 0.5, erode_d if erode_d is not None else dur * 0.35))
    gap_hw = lerp(70, 300, erode)
    gcx = float(np.interp((ey0 + ey1) / 2, ys, cxs))
    if k_front > 0:
        layer = img.copy()
        south = ys >= max(yf, ey1)
        if south.sum() > 1:
            ly, lx = ys[south], cxs[south]
            fill_poly(layer, np.vstack([np.stack([lx - ew, ly], 1), np.stack([lx[::-1] + ew, ly[::-1]], 1)]), MUD)
        if yf < ey1:
            fill_poly(layer, np.array([[gcx - gap_hw, ey0 - 2], [gcx + gap_hw, ey0 - 2], [gcx + gap_hw, ey1 + 2],
                                       [gcx - gap_hw, ey1 + 2]], np.float64), MUD)
        if yf < ey0:
            north = ys <= ey0
            ly, lx = ys[north], cxs[north]
            jet = gap_hw * (0.8 + 0.6 * np.clip((ey0 - ly) / 400.0, 0, 1))
            m = ly >= yf
            if m.sum() > 1:
                fill_poly(layer, np.vstack([np.stack([lx[m] - jet[m], ly[m]], 1), np.stack([lx[m][::-1] + jet[m][::-1], ly[m][::-1]], 1)]),
                          MUD)
        # flow streaks
        for i in range(60):
            sx = gcx + rng.uniform(-ew, ew)
            sy = (H - ((t * 260 + i * 53) % (H + 200))) + 100
            if sy < yf or (ey0 - 10 < sy < ey1 + 10 and abs(sx - gcx) > gap_hw):
                continue
            if sy < ey0 and abs(sx - gcx) > gap_hw * 1.3:
                continue
            cv2.line(layer, (int(sx), int(sy)), (int(sx), int(sy - 40)), MUD_HI, 3, cv2.LINE_AA)
        _blend(img, layer, 0.95)
    # embankment with the opening
    for xa, xb in ((0, gcx - gap_hw), (gcx + gap_hw, W)):
        if xb - xa < 4:
            continue
        pts = np.array([[xa, ey0], [xb, ey0], [xb, ey1], [xa, ey1]], np.float64)
        if erode > 0:
            # ragged edge at the opening
            edge = xb if xa == 0 else xa
            jag = [[edge, ey0]]
            for j in range(1, 8):
                yy = ey0 + (ey1 - ey0) * j / 8
                jag.append([edge + (-1 if xa == 0 else 1) * rng.uniform(0, 30) * erode, yy])
            jag.append([edge, ey1])
            if xa == 0:
                pts = np.array([[0, ey0]] + jag + [[0, ey1]], np.float64)
            else:
                pts = np.array([[W, ey0]] + jag + [[W, ey1]], np.float64)
        fill_poly(img, pts, FILL)
        cv2.line(img, (int(xa), int(ey0 + 30)), (int(xb), int(ey0 + 30)), (150, 150, 156), 3, cv2.LINE_AA)
        cv2.line(img, (int(xa), int(ey1 - 30)), (int(xb), int(ey1 - 30)), (150, 150, 156), 3, cv2.LINE_AA)
    # bridge planks over the opening, washed away (north = up) as the fill goes
    for j in range(9):
        x = gcx - 70 + j * 17
        dk = ease_in(prog(erode, 0.15 + 0.05 * j, 0.5))
        y = (ey0 + ey1) / 2 - 900 * dk
        ang = dk * (j - 4) * 0.4
        p = np.array([[-6, -50], [6, -50], [6, 50], [-6, 50]], np.float64)
        p = _rot_about(p, 0, 0, ang) + [x + dk * (j - 4) * 30, y]
        _poly(img, p, TIMBER, 1 - dk)
    cv2.arrowedLine(img, (80, 150), (80, 60), WHITE, 5, cv2.LINE_AA, tipLength=0.3)
    label(img, "N", 120, 104, 0.9, 44, WHITE, anchor="l")
    label(img, "VISTA DESDE ARRIBA · ESQUEMA", W - 260, H - 46, 0.7, 30, (220, 220, 220))
    st = solo_t if solo_t is not None else t0 + dur * 0.32
    ct = cede_t if cede_t is not None else t0 + dur * 0.6
    label(img, "LA CRECIDA", gcx + 330, H - 180, ease_out(prog(t, t0 + 0.4, 0.4)) * (1 - prog(t, st, 0.3)), 56, WHITE)
    label(img, "SOLO CABE BAJO EL PUENTE", W / 2, 110, ease_out(prog(t, st, 0.4)) * (1 - prog(t, ct - 0.5, 0.3)), 58, WHITE)
    label(img, "EL TERRAPLÉN CEDE", W / 2, 110, ease_out(prog(t, ct, 0.4)), 64, YELLOW)
    return img


# ---------------------------------------------------------------- analogies
def hose(t, dur, open_t=1.4, travel=1.3):
    img = background("dark_grid", t)
    u = np.linspace(0, 1, 260)
    xs = 260 + 1360 * u
    ys = 600 + 120 * np.sin(u * 2.4 * math.pi) * (1 - 0.4 * u)
    path = np.stack([xs, ys], 1)
    # tap
    fill_poly(img, [[150, 520], [262, 520], [262, 640], [150, 640]], (120, 122, 128))
    ang = -ease_out(prog(t, open_t - 0.3, 0.3)) * math.pi / 2
    c = np.array([205, 500])
    hd = np.array([[-50, -8], [50, -8], [50, 8], [-50, 8]], np.float64)
    hd = _rot_about(hd, 0, 0, ang) + c
    fill_poly(img, hd, RED)
    aa_poly(img, path, (60, 92, 64), 34)
    aa_poly(img, path, (40, 62, 44), 22)
    k = ease_in(prog(t, open_t, travel))
    if k > 0:
        aa_poly(img, partial_line(path, k), WATER_HI, 20)
    if k >= 1:
        rng = np.random.default_rng(int(t * 30))
        end = path[-1]
        for _ in range(70):
            r = rng.uniform(10, 380)
            a = rng.uniform(-0.18, 0.18)
            p = end + [r * math.cos(a), r * math.sin(a) + r * r / 2400]
            cv2.circle(img, (int(p[0]), int(p[1])), int(rng.uniform(3, 7)), WATER_HI, -1, cv2.LINE_AA)
    label(img, "MANGUERA VACÍA: SECA, NO PESA NADA", W / 2, 230, ease_out(prog(t, 0.2, 0.4)) * (1 - prog(t, open_t, 0.3)), 58, WHITE)
    label(img, "ABRES LA LLAVE…", W / 2, 230, ease_out(prog(t, open_t, 0.3)) * (1 - prog(t, open_t + travel + 0.2, 0.3)), 64, YELLOW)
    label(img, "…EN SEGUNDOS LLEGA A LA PUNTA, CON FUERZA", W / 2, 230, ease_out(prog(t, open_t + travel + 0.2, 0.4)), 58, YELLOW)
    return img


def grains(t, dur, t_water=1.2, t_sink=2.6, t_dry=None, labels=True):
    """Sand grains: packed (holds weight) -> water forces through, grains part, the weight sinks -> water goes, grains close."""
    img = background("dark_grid", t)
    t_dry = t_dry if t_dry is not None else dur - 2.2
    bx0, bx1, by0, by1 = 420, 1500, 420, 960
    cv2.rectangle(img, (bx0 - 8, by0 - 200), (bx1 + 8, by1 + 8), (60, 62, 66), 3)
    wk = ease_io(prog(t, t_water, 0.8)) * (1 - ease_io(prog(t, t_dry, 0.9)))
    sep = 1.0 + 0.32 * wk
    r = 17
    cols = int((bx1 - bx0) / (2 * r)) + 1
    rows = int((by1 - by0) / (2 * r * 0.88))
    rng = np.random.default_rng(1)
    jit = rng.uniform(-1, 1, (rows, cols, 2))
    sinkk = ease_io(prog(t, t_sink, max(0.5, t_dry - t_sink - 0.2)))
    # the weight (an engine silhouette) starts on the surface and sinks while the sand is "liquid"
    surf = by0 + 4
    ly = surf + sinkk * 300
    if wk > 0:
        layer = img.copy()
        cv2.rectangle(layer, (bx0, by0 - 10), (bx1, by1), WATER, -1)
        _blend(img, layer, 0.45 * wk)
    loco(img, 1260, ly, 1.25, 1, 0.0, num="", tender=False)
    base = img.copy()
    for i in range(rows):
        for j in range(cols):
            cx = bx0 + r + j * 2 * r + (r if i % 2 else 0)
            cy = by1 - r - i * 2 * r * 0.88
            cx = W / 2 + (cx - W / 2) * 1.0
            cy = by1 - (by1 - cy) * sep
            if cy < by0 - 160:
                continue
            jx, jy = jit[i, j] * (2 + 7 * wk) * np.array([math.sin(t * 5 + i), math.cos(t * 4 + j)])
            if cx > bx1 - r + 2:
                continue
            col = (int(lerp(SAND[0], SAND_WET[0], wk)), int(lerp(SAND[1], SAND_WET[1], wk)), int(lerp(SAND[2], SAND_WET[2], wk)))
            cv2.circle(img, (int(cx + jx), int(cy + jy)), r - 2, col, -1, cv2.LINE_AA)
    ga = 1.0 - 0.35 * wk
    if ga < 0.999:
        cv2.addWeighted(img, ga, base, 1 - ga, 0, img)
    if wk > 0.05:
        for i in range(14):
            x = bx0 + 60 + i * 76
            y = by1 - ((t * 220 + i * 61) % (by1 - by0 + 120))
            cv2.arrowedLine(img, (int(x), int(y + 40)), (int(x), int(y)), WATER_HI, 4, cv2.LINE_AA, tipLength=0.4)
    if labels:
        label(img, "SECA: AGUANTA EL PESO", W / 2, 150, ease_out(prog(t, 0.2, 0.4)) * (1 - prog(t, t_water, 0.3)), 60, WHITE)
        label(img, "CON AGUA: LOS GRANOS SE SEPARAN", W / 2, 150,
              ease_out(prog(t, t_water + 0.2, 0.4)) * (1 - prog(t, t_sink + 0.8, 0.3)), 60, (150, 200, 240))
        label(img, "LO QUE PESA SE HUNDE", W / 2, 150, ease_out(prog(t, t_sink + 0.9, 0.4)) * (1 - prog(t, t_dry, 0.3)), 60, YELLOW)
        label(img, "SE VA EL AGUA Y LA ARENA SE CIERRA", W / 2, 150, ease_out(prog(t, t_dry + 0.3, 0.4)), 60, YELLOW)
    _tag(img, "ESQUEMA")
    return img


# ---------------------------------------------------------------- night cab, point of view
def cab(t, dur, end_t=None, rain=True):
    """Looking ahead from the cab at night: the headlight shows a few metres of wet track, nothing else."""
    img = np.full((H, W, 3), (4, 5, 8), np.uint8)
    vx, vy = W / 2, 520
    f = 900.0
    gauge = 1.6
    end_t = end_t if end_t is not None else dur + 10
    speed = 9.0
    zend = max(1.2, 60 - (58.6 / 5.5) * max(0.0, t - (end_t - 5.5)))
    layer = np.zeros_like(img)
    # ground plane faintly lit by the headlight
    pts = []
    for z in np.linspace(1.2, 40, 60):
        pts.append((z, vy + f * 1.2 / z))
    glow = np.zeros((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((xx - vx) / 520.0) ** 2) - (((yy - (H + 60)) / 380.0) ** 2)) * 1.0
    glow = glow * (yy > vy + 10)
    for c, v in zip(range(3), (150, 130, 100)):
        layer[..., c] = np.clip(glow * v, 0, 255).astype(np.uint8)
    img = np.clip(img.astype(np.int32) + layer.astype(np.int32), 0, 255).astype(np.uint8)
    # sleepers moving towards the camera
    off = (t * speed) % 1.0
    for i in range(80):
        z = 1.2 + i * 0.5 - off * 0.5
        if z < 1.0 or z > zend:
            continue
        y = vy + f * 1.2 / z
        hw = f * (gauge * 0.75) / z
        b = clamp(1.6 / z, 0, 1)
        col = tuple(int(c * b) for c in (120, 96, 70))
        cv2.line(img, (int(vx - hw), int(y)), (int(vx + hw), int(y)), col, max(1, int(30 / z)), cv2.LINE_AA)
    # rails up to the edge of the washout
    for sgn in (-1, 1):
        zs = np.linspace(1.05, zend, 120)
        x = vx + sgn * f * (gauge / 2) / zs
        y = vy + f * 1.2 / zs
        for k in range(len(zs) - 1):
            b = clamp(2.4 / zs[k], 0, 1)
            cv2.line(img, (int(x[k]), int(y[k])), (int(x[k + 1]), int(y[k + 1])), tuple(int(c * b) for c in (210, 210, 220)), 3,
                     cv2.LINE_AA)
    if zend < 59:
        y = vy + f * 1.2 / zend
        cv2.rectangle(img, (0, int(vy)), (W, int(y)), (2, 2, 4), -1)
    if rain:
        _rain(img, t, 360, (190, 190, 170), 0.35, seed=9, slant=-0.1, length=46)
    # cab window frame
    cv2.rectangle(img, (0, 0), (W, 70), (14, 12, 10), -1)
    cv2.rectangle(img, (0, 0), (110, H), (14, 12, 10), -1)
    cv2.rectangle(img, (W - 110, 0), (W, H), (14, 12, 10), -1)
    _tag(img, "RECREACIÓN", 0.6)
    return img


# ---------------------------------------------------------------- documents (recreations)
def _paper(pw, ph, col=PAPER, seed=0):
    paper = np.full((ph, pw, 3), col, np.uint8)
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 5, (ph, pw, 1))
    paper = np.clip(paper.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return paper


def _ptxt(paper, s, x, y, size, col=INK, f="type", a=1.0, anchor="l"):
    sp = text_sprite(s, f, size, col, False)
    xx = x if anchor == "l" else x - sp.w / 2
    over(paper, sp, xx - 24, y - sp.h / 2, a)
    return sp.w - 48


def newspaper(t, dur, hl1=1.6, hl2=2.6):
    img = background("dark_grid", t)
    pw, ph = 1100, 900
    paper = _paper(pw, ph, (226, 218, 196), 3)
    _ptxt(paper, "DIARIO DE DENVER", pw / 2, 70, 64, INK, "serif_black", anchor="c")
    _ptxt(paper, "JULIO DE 1914", pw / 2, 132, 30, INK, "type", anchor="c")
    cv2.line(paper, (50, 160), (pw - 50, 160), INK, 3)
    cv2.line(paper, (50, 168), (pw - 50, 168), INK, 1)
    _ptxt(paper, "EL TREN QUE SE TRAGÓ", pw / 2, 230, 58, INK, "serif", anchor="c")
    _ptxt(paper, "EL KIOWA", pw / 2, 300, 58, INK, "serif", anchor="c")
    rng = np.random.default_rng(5)
    for col_i in range(2):
        x0 = 70 + col_i * 500
        for r in range(12):
            y = 380 + r * 36
            w = rng.uniform(330, 440) if r % 5 != 4 else rng.uniform(120, 240)
            cv2.line(paper, (x0, y), (int(x0 + w), y), (150, 144, 130), 8)
    h1 = ease_out(prog(t, hl1, 0.5))
    h2 = ease_out(prog(t, hl2, 0.5))
    for k, (s, y) in ((h1, ("25 VAGONES DE CHATARRA", 560)), (h2, ("LOCOMOTORA BALDWIN Nº 73", 720))):
        if k <= 0:
            continue
        layer = paper.copy()
        cv2.rectangle(layer, (60, y - 34), (int(60 + 900 * k), y + 34), (60, 200, 240), -1)
        cv2.addWeighted(layer, 0.5, paper, 0.5, 0, paper)
        _ptxt(paper, s, 80, y, 50, INK, "type", k)
    sprite = Sprite(np.dstack([paper, np.full(paper.shape[:2], 255, np.uint8)]))
    over_center(img, sprite, W / 2, H / 2 + 20, 1.0, 0.95)
    label(img, "RECREACIÓN", W - 150, H - 46, 0.75, 30, GREY)
    return img


def legend(t, dur, t0=0.3, step=0.9, last_t=None):
    img = background("dark_grid", t)
    label(img, "1878 · REGISTROS", W * 0.3, 190, ease_out(prog(t, t0, 0.4)), 60, WHITE)
    label(img, "1914 · PERIÓDICO", W * 0.7, 190, ease_out(prog(t, t0, 0.4)), 60, YELLOW)
    cv2.line(img, (W // 2, 160), (W // 2, 700), (70, 72, 76), 2)
    rows = [("LOCOMOTORA Nº 51", "BALDWIN Nº 73"), ("UN TREN DE CARGA", "25 VAGONES DE CHATARRA")]
    for i, (a, b) in enumerate(rows):
        k = ease_out(prog(t, t0 + 0.6 + step * i, 0.4))
        y = 360 + i * 170
        label(img, a, W * 0.3, y, k, 62, WHITE)
        label(img, b, W * 0.7, y, ease_out(prog(t, t0 + 1.0 + step * i, 0.4)), 62, YELLOW)
    lt = last_t if last_t is not None else t0 + 1.2 + step * 2
    label(img, "LO QUE NUNCA CAMBIÓ: SEGUÍA PERDIDA", W / 2, 860, ease_out(prog(t, lt, 0.4)), 62, RED)
    return img


def ledger(t, dur, mode="find", t0=0.3, notes_t=None):
    img = background("dark_grid", t)
    pw, ph = 1360, 900
    paper = _paper(pw, ph, (222, 210, 176), 7)
    cv2.line(paper, (pw // 2, 30), (pw // 2, ph - 30), (170, 156, 126), 4)
    _ptxt(paper, "REGISTRO DE LOCOMOTORAS", 340, 70, 40, INK, "serif", anchor="c")
    _ptxt(paper, "KANSAS PACIFIC RY.", 1020, 70, 40, INK, "serif", anchor="c")
    heads = [("Nº", 70), ("FABRICANTE", 160), ("AÑO", 470), ("NOTAS", 720)]
    for s, x in heads:
        _ptxt(paper, s, x, 140, 28, (90, 80, 64), "type")
    cv2.line(paper, (50, 166), (pw - 50, 166), (120, 108, 90), 2)
    rows = [("49", "BALDWIN", "1870"), ("50", "BALDWIN", "1870"), ("51", "BALDWIN", "1870"), ("52", "BALDWIN", "1870"),
            ("53", "BALDWIN", "1870")]
    for i, (n, mk, yr) in enumerate(rows):
        y = 230 + i * 70
        for s, x in ((n, 70), (mk, 160), (yr, 470)):
            _ptxt(paper, s, x, y, 34, INK, "type")
        cv2.line(paper, (50, y + 32), (pw - 50, y + 32), (196, 184, 156), 1)
    hk = ease_out(prog(t, t0 + 0.4, 0.5))
    if hk > 0:
        layer = paper.copy()
        cv2.rectangle(layer, (50, 230 + 2 * 70 - 30), (int(50 + (pw - 100) * hk), 230 + 2 * 70 + 30), (60, 200, 240), -1)
        cv2.addWeighted(layer, 0.4, paper, 0.6, 0, paper)
    notes = ["Desenterrada de noche.", "Remolcada a Kansas City.", "Reconstruida, 1880.", "Renumerada: 1026."]
    nt = notes_t or [t0 + 1.0, t0 + 2.0, t0 + 3.0, t0 + 4.0]
    show = {"find": 2, "full": 4, "rebuilt": 3}[mode]
    for i, s in enumerate(notes[:show]):
        k = ease_out(prog(t, nt[i], 0.5)) if mode != "full" or i >= 2 else 1.0
        if mode == "full" and i >= 2:
            k = ease_out(prog(t, nt[i - 2], 0.5))
        _ptxt(paper, s, 720, 560 + i * 72, 44, (40, 52, 110), "serif_it", k)
    cv2.arrowedLine(paper, (700, 370), (700, 520), (40, 52, 110), 3, cv2.LINE_AA, tipLength=0.08)
    sprite = Sprite(np.dstack([paper, np.full(paper.shape[:2], 255, np.uint8)]))
    over_center(img, sprite, W / 2, H / 2 + 10, 1.0, 0.95)
    label(img, "RECREACIÓN", W - 150, H - 46, 0.75, 30, GREY)
    return img


# ---------------------------------------------------------------- searches
def reading(t, dur, t0=0.3, ghost_t=None, years_t=None):
    img = background("dark_grid", t)
    x0, x1, yb = 200, 1720, 640
    cv2.line(img, (x0, yb), (x1, yb), (90, 92, 96), 2)
    cv2.line(img, (x0, 300), (x0, 820), (90, 92, 96), 2)
    label(img, "LECTURA DEL MAGNETÓMETRO", W / 2, 150, ease_out(prog(t, 0.1, 0.4)), 58, WHITE)
    xs = np.linspace(x0, x1, 400)
    rng = np.random.default_rng(2)
    noise = np.convolve(rng.normal(0, 1, 400), np.ones(9) / 9, "same") * 18
    ys = yb + noise
    k = ease_io(prog(t, t0, 2.0))
    aa_poly(img, partial_line(np.stack([xs, ys], 1), k), (120, 220, 140), 4)
    gt = ghost_t if ghost_t is not None else t0 + 2.4
    gk = ease_out(prog(t, gt, 0.6))
    if gk > 0:
        spike = yb - 300 * np.exp(-((xs - 1000) / 70.0) ** 2) * gk
        layer = img.copy()
        pts = np.stack([xs, spike], 1)
        for i in range(0, len(pts) - 1, 4):
            cv2.line(layer, tuple(pts[i].astype(int)), tuple(pts[i + 2].astype(int)), YELLOW, 4, cv2.LINE_AA)
        _blend(img, layer, 0.9)
        label(img, "ASÍ MARCARÍA UNA LOCOMOTORA", 1000, 260, gk, 46, YELLOW)
    yt = years_t or [gt + 1.0, gt + 1.5, gt + 2.0]
    for i, yr in enumerate(("1981", "1982", "1989")):
        a = ease_out(prog(t, yt[i], 0.3))
        label(img, yr + ": NADA", 420 + i * 540, 880, a, 54, WHITE)
    return img


def satellite(t, dur, t0=0.2):
    img = np.full((H, W, 3), (4, 6, 12), np.uint8)
    rng = np.random.default_rng(4)
    for _ in range(260):
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.6)
        b = int(rng.uniform(60, 200))
        cv2.circle(img, (int(x), int(y)), 1, (b, b, b), -1)
    R = 2600
    cx, cy = W / 2, H + R - 330
    cv2.circle(img, (int(cx), int(cy)), R, (34, 56, 70), -1, cv2.LINE_AA)
    cv2.circle(img, (int(cx), int(cy)), R, (90, 150, 200), 6, cv2.LINE_AA)
    tx, ty = W / 2 + 80, H - 200
    sx = lerp(200, 1720, ease_io(prog(t, t0, dur - 0.4)))
    sy = 210
    # satellite icon
    fill_poly(img, [[sx - 22, sy - 16], [sx + 22, sy - 16], [sx + 22, sy + 16], [sx - 22, sy + 16]], (200, 200, 206))
    for d in (-1, 1):
        fill_poly(img, [[sx + d * 30, sy - 12], [sx + d * 110, sy - 12], [sx + d * 110, sy + 12], [sx + d * 30, sy + 12]], (60, 90, 160))
    # beam
    layer = img.copy()
    fill_poly(layer, [[sx, sy + 18], [sx - 180, ty + 40], [sx + 180, ty + 40]], (120, 200, 255))
    _blend(img, layer, 0.18)
    cv2.rectangle(img, (int(tx - 70), int(ty - 30)), (int(tx + 70), int(ty + 30)), YELLOW, 3)
    label(img, "KIOWA CREEK", tx, ty + 80, 1.0, 40, YELLOW)
    label(img, "BUSCANDO UNA GRAN MASA DE HIERRO", W / 2, 90, ease_out(prog(t, t0 + 0.3, 0.4)), 52, WHITE)
    _tag(img, "ESQUEMA")
    return img


def numbers1989(t, dur, t0=0.2, step=0.6, times=None):
    img = background("dark_grid", t)
    items = [("+300", "PERSONAS"), ("≈30", "DETECTORES Y RADARES"), ("1", "RETROEXCAVADORA"), ("1", "SATÉLITE")]
    for i, (n, s) in enumerate(items):
        a = ease_out(prog(t, times[i] if times else t0 + i * step, 0.4))
        cx = W * (0.14 + 0.24 * i)
        label(img, n, cx, 470, a, 170, YELLOW)
        label(img, s, cx, 620, a, 42, WHITE)
    label(img, "ENERO DE 1989", W / 2, 200, ease_out(prog(t, 0.05, 0.4)), 60, GREY)
    return img


# ---------------------------------------------------------------- the answer
def rebuild(t, dur, t0=0.3, t1=None, num_t=None):
    img = background("dark_grid", t)
    t1 = t1 if t1 is not None else t0 + 1.6
    k = ease_io(prog(t, t1, 0.8))
    drivers = 2 if k < 0.5 else 3
    nk = ease_io(prog(t, num_t, 0.6)) if num_t is not None else 0.0
    num = "51" if nk < 0.5 else "1026"
    a = 1 - abs(k - 0.5) * 2 if 0 < k < 1 else 0
    loco(img, 1400, 700, 1.9, 1, 0.0, drivers=drivers, num=num)
    if 0 < k < 1:
        layer = img.copy()
        cv2.rectangle(layer, (0, 0), (W, H), (240, 230, 200), -1)
        _blend(img, layer, 0.5 * (1 - abs(k - 0.5) * 2))
    label(img, "ANTES: 2 RUEDAS MOTRICES POR LADO", W / 2, 180, ease_out(prog(t, t0, 0.4)) * (1 - prog(t, t1, 0.3)), 56, WHITE)
    label(img, "1880: SALE CON MÁS RUEDAS MOTRICES", W / 2, 180, ease_out(prog(t, t1 + 0.4, 0.4)), 56, YELLOW)
    if num_t is not None:
        label(img, "NUEVO NÚMERO: 1026", W / 2, 900, ease_out(prog(t, num_t + 0.3, 0.4)), 60, YELLOW)
    _tag(img, "ILUSTRACIÓN")
    return img


def two_lanes(t, dur, t0=0.3, step=0.45, hl_t=None):
    img = background("dark_grid", t)
    x0, x1 = 200, 1760

    def X(yr):
        return x0 + (x1 - x0) * (yr - 1875) / (1995 - 1875)

    ya, yb = 360, 700
    for y, txt, c in ((ya, "LO QUE SE CONTABA", WHITE), (yb, "LO QUE PASÓ", YELLOW)):
        k = ease_io(prog(t, t0, 1.0))
        cv2.line(img, (x0, y), (int(lerp(x0, x1, k)), y), c, 3, cv2.LINE_AA)
        label(img, txt, x0 - 10, y - 110, ease_out(prog(t, t0, 0.4)), 46, c, anchor="l")
    top = [(1878, "1878 · PERDIDA", 300), (1914, "1914 · «SIGUE PERDIDA»", 930), (1981, "1981 · CUSSLER", 1300),
           (1989, "1989 · 300 PERSONAS", 1640)]
    bot = [(1878, "1878 · A KANSAS CITY", 330), (1880, "1880 · RECONSTRUIDA", 1010), (1886, "AÑOS 1880 · Nº 1026", 1340),
           (1900, "HASTA FIN DE SIGLO", 1660)]
    for lane, (items, y, c, dy) in enumerate(((top, ya, WHITE, -50), (bot, yb, YELLOW, 70))):
        for i, (yr, s_, lx) in enumerate(items):
            a = ease_out(prog(t, t0 + 0.6 + (i + 4 * lane) * step, 0.35))
            if a <= 0:
                continue
            x = X(yr)
            cv2.circle(img, (int(x), y), 12, c, -1, cv2.LINE_AA)
            ly = y + dy
            layer = img.copy()
            cv2.line(layer, (int(x), y), (int(lx), int(ly - 18 * np.sign(dy))), (110, 110, 116), 2, cv2.LINE_AA)
            _blend(img, layer, a)
            label(img, s_, lx, ly, a, 38, c if lane else (220, 220, 224))
    hk = ease_out(prog(t, hl_t if hl_t is not None else t0 + 0.6 + 8 * step, 0.4))
    if hk > 0:
        x = int(X(1914))
        cv2.line(img, (x, 330), (x, 760), RED, 3, cv2.LINE_AA)
        label(img, "EN 1914 LLEVABA MÁS DE 30 AÑOS DE VUELTA EN LAS VÍAS", W / 2, 920, hk, 50, RED)
    return img


def merger(t, dur, t0=0.3, join_t=None, note_t=None):
    img = background("dark_grid", t)
    jt = join_t if join_t is not None else t0 + 1.2
    k = ease_io(prog(t, jt, 0.9))
    for i, (s, sub) in enumerate((("KANSAS PACIFIC", "EN QUIEBRA"), ("UNION PACIFIC", ""))):
        cx = lerp(W * (0.27 + 0.46 * i), W / 2, k)
        a = 1 - ease_in(prog(t, jt + 0.6, 0.3)) if i == 0 else 1.0
        bw, bh = 560, 190
        sp = rounded_rect_sprite(bw, bh, (40, 44, 52) if i == 0 else (52, 46, 30), 12, 255)
        over_center(img, sp, cx, 420, a * ease_out(prog(t, t0 + 0.2 * i, 0.4)))
        label(img, s, cx, 400 if sub else 420, a * ease_out(prog(t, t0 + 0.2 * i, 0.4)), 60, WHITE if i == 0 else YELLOW)
        if sub:
            label(img, sub, cx, 460, a * ease_out(prog(t, t0, 0.4)), 34, RED)
    label(img, "1880", W / 2, 230, ease_out(prog(t, jt + 0.5, 0.4)), 90, YELLOW)
    # list of engine numbers scrolling under the merger; one of them slips through
    lk = ease_out(prog(t, jt + 1.0, 0.4))
    if lk > 0:
        for i in range(-2, 12):
            n = 40 + i
            y = 660 + ((i * 60 - (t - jt) * 50) % 720) - 60
            if y < 620 or y > 1040:
                continue
            c = YELLOW if n == 51 else (150, 150, 156)
            label(img, f"Nº {n}", W / 2, y, lk * (1 - abs(y - 830) / 260), 44, c)
    nt = note_t if note_t is not None else jt + 2.6
    label(img, "NO ES UNA PRUEBA · SOLO UNA COINCIDENCIA DE FECHAS", W / 2, 1010, ease_out(prog(t, nt, 0.4)), 46, WHITE)
    return img


def theory(t, dur, t0=0.3, step=0.9, deny_t=None):
    img = background("dark_grid", t)
    label(img, "LA TEORÍA DE CUSSLER", W / 2, 170, ease_out(prog(t, 0.1, 0.4)), 64, WHITE)
    steps = ["DARLA POR PERDIDA", "COBRAR EL SEGURO", "RECUPERARLA A ESCONDIDAS"]
    for i, s in enumerate(steps):
        a = ease_out(prog(t, t0 + i * step, 0.4))
        cx = W * (0.2 + 0.3 * i)
        sp = rounded_rect_sprite(480, 200, (40, 44, 52), 14, 255)
        over_center(img, sp, cx, 500, a)
        label(img, str(i + 1), cx, 450, a, 60, YELLOW)
        label(img, s, cx, 530, a, 40, WHITE)
        if i < 2:
            ak = ease_out(prog(t, t0 + i * step + 0.5, 0.3))
            if ak > 0:
                cv2.arrowedLine(img, (int(cx + 250), 500), (int(cx + 250 + 70 * ak), 500), YELLOW, 6, cv2.LINE_AA, tipLength=0.4)
    dt = deny_t if deny_t is not None else t0 + 3 * step + 0.4
    label(img, "LA COMPAÑÍA SIEMPRE LO NEGÓ", W / 2, 820, ease_out(prog(t, dt, 0.4)), 60, RED)
    return img


def names3(t, dur, t0=0.3, step=0.8, end_t=None, bottom="NADIE SABE DÓNDE FUERON ENTERRADOS"):
    img = background("black", t)
    names = [("JOHN BACON", WHITE), ("GEORGE PIATT", WHITE), ("FRANK SELDON… ¿O BELDEN?", (210, 206, 196))]
    for i, (n, c) in enumerate(names):
        a = ease_out(prog(t, t0 + i * step, 0.4))
        label(img, n, W / 2, 300 + i * 160, a, 104, c)
    if bottom:
        et = end_t if end_t is not None else t0 + 3 * step + 0.5
        label(img, bottom, W / 2, 870, ease_out(prog(t, et, 0.5)), 54, YELLOW)
    return img


def two_places(t, dur, t0=0.3, t1=None):
    img = background("dark_grid", t)
    t1 = t1 if t1 is not None else t0 + 1.4
    a = ease_out(prog(t, t0, 0.4))
    # left: shovel in sand
    lx = W * 0.28
    fill_poly(img, [[lx - 260, 760], [lx + 260, 760], [lx + 300, 860], [lx - 300, 860]], tuple(int(c * a) for c in SAND))
    sh = np.array([[-8, -300], [8, -300], [8, -40], [-8, -40]], np.float64) + [lx, 760]
    _poly(img, sh, TIMBER, a)
    _poly(img, np.array([[-40, -50], [40, -50], [30, 40], [0, 70], [-30, 40]], np.float64) + [lx, 760], (150, 150, 156), a)
    label(img, "DONDE BUSCABAN", lx, 260, a, 60, WHITE)
    # right: an open ledger
    b = ease_out(prog(t, t1, 0.4))
    rx = W * 0.72
    _poly(img, np.array([[-300, -150], [0, -120], [300, -150], [300, 150], [0, 180], [-300, 150]], np.float64) + [rx, 560],
          (222, 210, 176), b)
    if b > 0:
        cv2.line(img, (int(rx), 440), (int(rx), 740), (150, 136, 110), 3, cv2.LINE_AA)
        for i in range(6):
            for d in (-1, 1):
                y = 470 + i * 42
                cv2.line(img, (int(rx + d * 40), y), (int(rx + d * 250), y), (150, 140, 120), 4)
        cv2.line(img, (int(rx + 40), 470 + 2 * 42), (int(rx + 250), 470 + 2 * 42), (40, 52, 110), 6)
    label(img, "DONDE ESTABA LA RESPUESTA", rx, 260, b, 60, YELLOW)
    return img


def count_up(t, dur, value=2900, t0=0.3, title="BENNETT · CENSO DE 2020", unit="HABITANTES", prefix="CASI "):
    img = background("dark_grid", t)
    k = ease_out(prog(t, t0, 1.4))
    v = int(round(value * k / 100.0) * 100) if k < 1 else value
    label(img, title, W / 2, 300, ease_out(prog(t, 0.1, 0.4)), 60, GREY)
    label(img, f"{prefix}{v:,}".replace(",", ","), W / 2, 540, ease_out(prog(t, t0, 0.3)), 200, YELLOW)
    label(img, unit, W / 2, 720, ease_out(prog(t, t0 + 0.4, 0.4)), 60, WHITE)
    return img


def anatomy(t, dur, t_chim=0.6, t_boil=1.6, t_tend=2.8):
    """The engine in profile with its parts named: tall stack, iron boiler, tender for coal and water."""
    img = background("dark_grid", t)
    s = 2.6
    x, y = 1500, 760
    loco(img, x, y, s, 1, 0.0, num="51", roll=t * 0.0)
    cv2.line(img, (60, int(y + 4)), (1860, int(y + 4)), (150, 150, 156), 5, cv2.LINE_AA)
    items = [(t_chim, (x - 70 * s, y - 158 * s), (1600, 220), "CHIMENEA ALTA", WHITE),
             (t_boil, (x - 140 * s, y - 64 * s), (1060, 300), "CALDERA DE HIERRO", WHITE),
             (t_tend, (x - 318 * s, y - 70 * s), (520, 300), "TÉNDER: CARBÓN Y AGUA", YELLOW)]
    for tt, (px_, py_), (lx, ly), txt, col in items:
        a = ease_out(prog(t, tt, 0.4))
        if a <= 0:
            continue
        layer = img.copy()
        cv2.line(layer, (int(px_), int(py_)), (int(lx), int(ly + 34)), col, 3, cv2.LINE_AA)
        cv2.circle(layer, (int(px_), int(py_)), 9, col, -1, cv2.LINE_AA)
        _blend(img, layer, a)
        label(img, txt, lx, ly, a, 54, col)
    _tag(img, "ILUSTRACIÓN")
    return img
