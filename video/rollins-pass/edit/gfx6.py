"""Atlantic Avenue diagrams: the 1840s street with a locomotive, cut-and-cover in section, the tunnel along the avenue
(sealed ends, one door, the scan behind the Hicks Street wall, today), the descent through the manhole, the plans,
the rumour board, the permit, the London comparison and the radio story."""
import functools
import math

import cv2
import numpy as np

from engine import (BLACK, H, RED, W, WHITE, YELLOW, clamp, ease_back, ease_in, ease_io, ease_out, lerp, over,
                    over_center, prog, rounded_rect_sprite, text_sprite)
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

BRICK = (128, 66, 46)
BRICK2 = (104, 52, 38)
MORTAR = (70, 56, 50)
SOIL = (74, 58, 44)
SOIL2 = (60, 47, 36)
ASPHALT = (54, 54, 56)
HOUSE = (88, 64, 52)
HOUSE2 = (74, 54, 46)
WINDOW = (232, 196, 120)
PAPER = (232, 224, 204)
INK = (40, 36, 32)
BLUE = (28, 62, 118)


def _bricks(img, x0, y0, x1, y1, bw=46, bh=20, col=BRICK, col2=BRICK2):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    if x1 <= x0 or y1 <= y0:
        return
    cv2.rectangle(img, (x0, y0), (x1, y1), MORTAR, -1)
    r = 0
    for y in range(y1, y0, -bh):
        off = (bw // 2) if r % 2 else 0
        for x in range(x0 - off, x1, bw):
            a, b = max(x + 2, x0), min(x + bw - 2, x1)
            if b > a:
                c = col if (x // bw + r) % 3 else col2
                cv2.rectangle(img, (a, max(y - bh + 2, y0)), (b, y - 1), c, -1)
        r += 1


def _soil(img, pts, seed=4):
    fill_poly(img, pts, SOIL)
    rng = np.random.default_rng(seed)
    pts = np.asarray(pts, float)
    x0, y0 = pts.min(0)
    x1, y1 = pts.max(0)
    mask = np.zeros(img.shape[:2], np.uint8)
    fill_poly(mask, pts, 255)
    for _ in range(int((x1 - x0) * (y1 - y0) / 1800)):
        x, y = int(rng.uniform(x0, x1)), int(rng.uniform(y0, y1))
        if 0 <= y < H and 0 <= x < W and mask[y, x]:
            cv2.circle(img, (x, y), int(rng.integers(2, 5)), SOIL2 if rng.random() < 0.6 else (92, 74, 58), -1, cv2.LINE_AA)


def _house(img, x, base, w, h, seed=0, lit=0.5):
    rng = np.random.default_rng(seed)
    col = HOUSE if seed % 2 else HOUSE2
    cv2.rectangle(img, (int(x), int(base - h)), (int(x + w), int(base)), col, -1)
    cv2.rectangle(img, (int(x - 6), int(base - h - 14)), (int(x + w + 6), int(base - h)), (50, 40, 36), -1)
    for fy in range(int(base - h + 30), int(base - 60), 70):
        for fx in range(int(x + 22), int(x + w - 30), 56):
            on = rng.random() < lit
            cv2.rectangle(img, (fx, fy), (fx + 26, fy + 40), WINDOW if on else (36, 32, 30), -1)
    cv2.rectangle(img, (int(x + w / 2 - 18), int(base - 56)), (int(x + w / 2 + 18), int(base)), (40, 30, 26), -1)


def _person(img, x, y, s=1.0, col=(210, 210, 210), walk=0.0):
    hd = int(9 * s)
    cv2.circle(img, (int(x), int(y - 46 * s)), hd, col, -1, cv2.LINE_AA)
    cv2.line(img, (int(x), int(y - 38 * s)), (int(x), int(y - 16 * s)), col, max(2, int(5 * s)), cv2.LINE_AA)
    sw = math.sin(walk) * 8 * s
    cv2.line(img, (int(x), int(y - 16 * s)), (int(x - 6 * s + sw), int(y)), col, max(2, int(4 * s)), cv2.LINE_AA)
    cv2.line(img, (int(x), int(y - 16 * s)), (int(x + 6 * s - sw), int(y)), col, max(2, int(4 * s)), cv2.LINE_AA)


def _loco(img, x, y, s=1.0, boxed=0.0, smoke_t=0.0):
    """1840s locomotive facing right; x = front, y = rail level."""
    def r(a, b, c, d, col):
        cv2.rectangle(img, (int(x + a * s), int(y + b * s)), (int(x + c * s), int(y + d * s)), col, -1)
    r(-230, -40, -20, -20, (40, 40, 44))           # frame
    r(-200, -100, -40, -40, (70, 72, 78))          # boiler
    r(-230, -140, -170, -40, (60, 50, 44))          # cab
    r(-70, -160, -46, -100, (40, 40, 44))           # stack
    cv2.ellipse(img, (int(x - 58 * s), int(y - 166 * s)), (int(22 * s), int(10 * s)), 0, 0, 360, (40, 40, 44), -1)
    for wx in (-190, -120, -60):
        cv2.circle(img, (int(x + wx * s), int(y - 18 * s)), int(18 * s), (30, 30, 32), -1, cv2.LINE_AA)
        cv2.circle(img, (int(x + wx * s), int(y - 18 * s)), int(18 * s), (120, 120, 120), 2, cv2.LINE_AA)
    pts = np.array([[x - 20 * s, y - 40 * s], [x + 20 * s, y - 4 * s], [x - 20 * s, y - 4 * s]])
    fill_poly(img, pts, (90, 90, 96))               # cow-catcher
    if boxed > 0:
        layer = img.copy()
        cv2.rectangle(layer, (int(x - 236 * s), int(y - 190 * s)), (int(x + 12 * s), int(y - 30 * s)), (96, 72, 50), -1)
        fill_poly(layer, np.array([[x - 246 * s, y - 190 * s], [x - 112 * s, y - 250 * s], [x + 22 * s, y - 190 * s]]), (74, 54, 40))
        for wx in range(-210, 0, 60):
            cv2.rectangle(layer, (int(x + wx * s), int(y - 160 * s)), (int(x + (wx + 30) * s), int(y - 120 * s)), (40, 32, 26), -1)
        cv2.addWeighted(layer, boxed, img, 1 - boxed, 0, img)
    for k in range(4):
        ph = (smoke_t * 0.6 + k / 4) % 1
        cv2.circle(img, (int(x - 58 * s - 120 * ph * s), int(y - 180 * s - 90 * ph * s)), int((10 + 30 * ph) * s),
                   (150, 150, 150), 2, cv2.LINE_AA)


# ------------------------------------------------------------------ the 1840s street with trains in the middle
def street_train(t, dur, mode="street"):
    """modes: street (6 mph + rider with red flag), box (locomotive in a box), brake (several blocks to stop)."""
    img = background("dark_grid", t)
    base = 820
    for i, x in enumerate(range(-40, W + 40, 230)):
        _house(img, x, 600, 210, 330 + (i * 37) % 90, seed=i, lit=0.35)
    cv2.rectangle(img, (0, 600), (W, H), (58, 54, 50), -1)      # cobbles
    rng = np.random.default_rng(2)
    for _ in range(500):
        cv2.circle(img, (int(rng.uniform(0, W)), int(rng.uniform(612, H))), 3, (70, 66, 60), -1)
    for yy in (base, base + 26):
        cv2.line(img, (0, yy), (W, yy), (150, 140, 128), 4, cv2.LINE_AA)
    if mode == "brake":
        # blocks between cross streets
        bx = [200, 620, 1040, 1460, 1880]
        for x in bx:
            cv2.rectangle(img, (x - 18, 600), (x + 18, H), (44, 42, 40), -1)
        k = ease_out(prog(t, 0.3, max(dur - 1.0, 1.0)))
        fx = lerp(330, 1700, k)
        _loco(img, fx, base, 1.3, smoke_t=t * (1 - k))
        if k < 0.98:
            for j in range(3):
                cv2.line(img, (int(fx - 210 + j * 70), base + 6), (int(fx - 250 + j * 70), base + 30), YELLOW, 3, cv2.LINE_AA)
        cv2.arrowedLine(img, (330, 980), (int(fx), 980), YELLOW, 6, cv2.LINE_AA, tipLength=0.02)
        label(img, "UN TREN CARGADO: VARIAS CUADRAS PARA FRENAR", W / 2, 150, prog(t, 0.2, 0.4), 62, WHITE)
        return img
    fx = 520 + t * 55 if mode == "street" else 980 + t * 30
    rider_x = fx + 330
    _loco(img, fx, base, 1.5, boxed=ease_io(prog(t, 0.6, 0.8)) if mode == "box" else 0.0, smoke_t=t)
    # rider with red flag
    if mode == "street":
        hx = rider_x
        cv2.ellipse(img, (int(hx), int(base - 70)), (60, 26), 0, 0, 360, (90, 64, 44), -1, cv2.LINE_AA)
        for lx in (-40, -20, 24, 44):
            ph = math.sin(t * 6 + lx) * 10
            cv2.line(img, (int(hx + lx), int(base - 60)), (int(hx + lx + ph), int(base)), (90, 64, 44), 7, cv2.LINE_AA)
        cv2.line(img, (int(hx + 50), int(base - 80)), (int(hx + 82), int(base - 120)), (90, 64, 44), 14, cv2.LINE_AA)
        _person(img, hx, base - 90, 1.0, (200, 196, 190))
        pole = (int(hx + 18), int(base - 160))
        cv2.line(img, (int(hx + 8), int(base - 110)), pole, (200, 190, 170), 4, cv2.LINE_AA)
        wav = math.sin(t * 7) * 10
        fill_poly(img, np.array([pole, (pole[0] + 70, pole[1] + 8 + wav), (pole[0] + 66, pole[1] + 46 + wav), (pole[0], pole[1] + 40)]), RED)
        for i, px in enumerate((300, 980, 1500)):
            _person(img, px + 12 * math.sin(t * 0.7 + i), 700 + (i % 2) * 40, 1.1, (170, 170, 170), walk=t * 5 + i)
        # signs
        a = prog(t, 0.4, 0.4)
        sp = rounded_rect_sprite(300, 200, (236, 236, 228), 20, 255, 8, BLACK)
        over(img, sp, 80, 60, a)
        label(img, "6", 230, 150, a, 120, BLACK, fname="bebas")
        label(img, "MPH · ≈ 10 KM/H", 230, 230, a, 36, BLACK)
        b = prog(t, 1.6, 0.4)
        cx, cy = 1700, 170
        if b > 0:
            cv2.circle(img, (cx, cy), int(100 * ease_back(b)), (236, 236, 228), -1, cv2.LINE_AA)
            cv2.circle(img, (cx, cy), int(100 * ease_back(b)), RED, 14, cv2.LINE_AA)
            label(img, "SILBATO", cx, cy - 4, b, 34, BLACK)
            cv2.line(img, (cx - 66, cy + 66), (cx + 66, cy - 66), RED, 14, cv2.LINE_AA)
        label(img, "UN JINETE CON BANDERA ROJA DELANTE", W / 2, 1020, prog(t, 1.0, 0.4), 50, WHITE)
    else:
        label(img, "UNA CAJA PARA QUE LOS CABALLOS NO SE ESPANTARAN", W / 2, 150, prog(t, 0.6, 0.4), 56, WHITE)
    return img


# ------------------------------------------------------------------ cut and cover, in section across the street
GY = 440          # street surface
FLOOR = 960       # tunnel floor
SPRING = 660      # top of the side walls
CROWN = 518       # top of the vault (17 ft above the floor)
TX0, TX1 = 687, 1233   # 21 ft wide


def _section_bg():
    img = background("dark_grid", 0.0).copy()
    for i, x in enumerate((20, 250, 1450, 1680)):
        _house(img, x, GY, 220, 300 + (i * 41) % 80, seed=i + 3, lit=0.3)
    return img


def _vault_poly(inner=True):
    pad = 0 if inner else 34
    xs = np.linspace(TX0 - pad, TX1 + pad, 60)
    cx, rx = (TX0 + TX1) / 2, (TX1 - TX0) / 2 + pad
    ys = SPRING - (SPRING - CROWN + pad) * np.sqrt(np.clip(1 - ((xs - cx) / rx) ** 2, 0, 1))
    return np.stack([xs, ys], 1)


def cut_cover(t, dur, mode="dig"):
    """modes: dig (the trench), build (walls, vault, street back on top)."""
    img = _section_bg().copy()
    ground = np.array([[0, GY], [W, GY], [W, H], [0, H]])
    if mode == "dig":
        _soil(img, ground)
        k = ease_io(prog(t, 0.3, max(dur - 1.6, 1.0)))
        depth = lerp(GY, FLOOR + 20, k)
        cv2.rectangle(img, (TX0 - 34, GY), (TX1 + 34, int(depth)), (16, 18, 22), -1)
        for side in (-1, 1):  # spoil heaps
            x = TX0 - 120 if side < 0 else TX1 + 120
            hgt = 90 * k
            fill_poly(img, np.array([[x - 110, GY], [x, GY - hgt], [x + 110, GY]]), SOIL)
        for j, x in enumerate((TX0 + 90, (TX0 + TX1) / 2, TX1 - 90)):
            y = depth
            sw = math.sin(t * 5 + j * 2)
            _person(img, x, y, 1.6, (200, 190, 170), walk=0)
            ex, ey = x + 40 * sw, y - 110 + 30 * abs(sw)
            cv2.line(img, (int(x), int(y - 60)), (int(ex), int(ey)), (150, 110, 70), 6, cv2.LINE_AA)
            cv2.line(img, (int(ex - 26), int(ey + 10)), (int(ex + 26), int(ey - 10)), (130, 130, 136), 7, cv2.LINE_AA)
        a = prog(t, 0.6, 0.4)
        cv2.arrowedLine(img, (int((TX0 + TX1) / 2), GY - 30), (TX0 - 30, GY - 30), YELLOW, 4, cv2.LINE_AA, tipLength=0.08)
        cv2.arrowedLine(img, (int((TX0 + TX1) / 2), GY - 30), (TX1 + 30, GY - 30), YELLOW, 4, cv2.LINE_AA, tipLength=0.08)
        label(img, "21 PIES · ≈ 6,5 M", W / 2, GY - 80, a, 54, YELLOW)
        label(img, "MAYO DE 1844 · A PICO Y PALA", W / 2, 100, prog(t, 0.2, 0.4), 64, WHITE)
        return img
    # build: walls rise, vault closes, earth goes back and the street returns
    kw = ease_io(prog(t, 0.2, 1.4))
    kv = ease_io(prog(t, 1.5, 1.2))
    kf = ease_io(prog(t, 2.7, 1.0))
    _soil(img, ground)
    cv2.rectangle(img, (TX0 - 34, int(lerp(FLOOR + 20, GY, kf))), (TX1 + 34, FLOOR + 20), (16, 18, 22), -1) if kf < 1 else None
    if kf <= 0:
        cv2.rectangle(img, (TX0 - 34, GY), (TX1 + 34, FLOOR + 20), (16, 18, 22), -1)
    wall_top = lerp(FLOOR + 20, SPRING, kw)
    _bricks(img, TX0 - 34, wall_top, TX0, FLOOR + 20)
    _bricks(img, TX1, wall_top, TX1 + 34, FLOOR + 20)
    if kv > 0:
        outer, inner = _vault_poly(False), _vault_poly(True)
        n = max(2, int(len(outer) * kv / 2))
        for side in (0, 1):
            o = outer[:n] if side == 0 else outer[::-1][:n]
            i = inner[:n] if side == 0 else inner[::-1][:n]
            ring = np.vstack([o, i[::-1]])
            fill_poly(img, ring, BRICK)
            aa_poly(img, o, BRICK2, 3)
    if kf > 0:
        layer = img.copy()
        _soil(layer, np.array([[TX0 - 34, GY], [TX1 + 34, GY], [TX1 + 34, SPRING], [TX0 - 34, SPRING]]), seed=9)
        cv2.addWeighted(layer, kf, img, 1 - kf, 0, img)
        outer, inner = _vault_poly(False), _vault_poly(True)
        fill_poly(img, np.vstack([outer, inner[::-1]]), BRICK)
        aa_poly(img, outer, BRICK2, 3)
        cv2.rectangle(img, (int((TX0 + TX1) / 2 - 560 * kf), GY - 14), (int((TX0 + TX1) / 2 + 560 * kf), GY), ASPHALT, -1)
    inside = np.vstack([_vault_poly(True), [[TX1, FLOOR], [TX0, FLOOR]]])
    if kv >= 1:
        fill_poly(img, inside, (16, 18, 22))
    cv2.rectangle(img, (TX0, FLOOR), (TX1, FLOOR + 20), (60, 58, 56), -1)
    if kf >= 1:
        ph = prog(t, 3.8, max(dur - 4.2, 0.6))
        if 0 < ph < 1:  # a train passes, seen from the front
            s = math.sin(math.pi * ph)
            cv2.rectangle(img, (int(W / 2 - 150), int(FLOOR - 330)), (int(W / 2 + 150), FLOOR - 10), (70, 72, 78), -1)
            cv2.circle(img, (int(W / 2), int(FLOOR - 230)), 46, (255, 230, 160) if s > 0.2 else (90, 90, 90), -1, cv2.LINE_AA)
        a = prog(t, 3.0, 0.4)
        cv2.line(img, (TX1 + 70, FLOOR), (TX1 + 70, CROWN), YELLOW, 3, cv2.LINE_AA)
        for yy in (FLOOR, CROWN):
            cv2.line(img, (TX1 + 56, yy), (TX1 + 84, yy), YELLOW, 3, cv2.LINE_AA)
        label(img, "17 PIES DE ALTO", TX1 + 100, (FLOOR + CROWN) / 2 - 24, a, 48, YELLOW, "l")
        label(img, "≈ 5 M", TX1 + 100, (FLOOR + CROWN) / 2 + 26, a, 40, GREY, "l")
    title = "MUROS DE LADRILLO · BÓVEDA · LA CALLE OTRA VEZ ENCIMA"
    label(img, title, W / 2, 100, prog(t, 0.2, 0.4), 54, WHITE)
    return img


# ------------------------------------------------------------------ the tunnel along the avenue, side view
STREET_Y = 330
T_TOP, T_BOT = 520, 780
AX0, AX1 = 140, 1780          # Columbia St .. Boerum Pl (≈ 2,500 ft)
XS = {"COLUMBIA": 140, "HICKS": 465, "HENRY": 751, "CLINTON": 1100, "COURT": 1471, "BOERUM": 1780}


@functools.lru_cache(maxsize=2)
def _profile_bg():
    img = background("dark_grid", 0.0).copy()
    for i, x in enumerate(range(-60, W, 190)):
        _house(img, x, STREET_Y - 30, 170, 150 + (i * 53) % 110, seed=i + 11, lit=0.25)
    cv2.rectangle(img, (0, STREET_Y - 30), (W, STREET_Y), ASPHALT, -1)
    _soil(img, np.array([[0, STREET_Y], [W, STREET_Y], [W, H], [0, H]]), seed=21)
    for name, x in XS.items():
        cv2.line(img, (x, STREET_Y - 30), (x, STREET_Y - 4), (150, 150, 150), 2)
        label(img, name + (" PL" if name == "BOERUM" else " ST"), x, STREET_Y - 62, 1.0, 30, GREY)
    return img


def _tube(img, x0, x1, col=(16, 18, 22), edge=BRICK):
    cv2.rectangle(img, (int(x0), T_TOP), (int(x1), T_BOT), col, -1)
    cv2.rectangle(img, (int(x0), T_TOP - 14), (int(x1), T_TOP), edge, -1)
    cv2.rectangle(img, (int(x0), T_BOT), (int(x1), T_BOT + 14), edge, -1)


def _plug(img, x, w=36):
    _bricks(img, x - w / 2, T_TOP - 14, x + w / 2, T_BOT + 14, bw=18, bh=12)


def _bus(img, x, y, s=1.0):
    cv2.rectangle(img, (int(x - 150 * s), int(y - 90 * s)), (int(x + 150 * s), int(y - 14 * s)), (40, 110, 170), -1)
    for wx in range(-130, 130, 44):
        cv2.rectangle(img, (int(x + wx * s), int(y - 80 * s)), (int(x + (wx + 32) * s), int(y - 50 * s)), (200, 220, 230), -1)
    for wx in (-95, 95):
        cv2.circle(img, (int(x + wx * s), int(y - 12 * s)), int(14 * s), (20, 20, 20), -1, cv2.LINE_AA)


def avenue_profile(t, dur, mode="seal"):
    """modes: open (1844-61 trains), seal (ends walled, middle hollow), onedoor, scan, today."""
    img = _profile_bg().copy()
    if mode == "open":
        _tube(img, AX0, AX1)
        ph = ((t * 0.18) % 1)
        x = lerp(AX0 - 200, AX1 + 200, ph)
        cv2.rectangle(img, (int(x - 160), T_BOT - 120), (int(x), T_BOT - 4), (90, 92, 98), -1)
        cv2.circle(img, (int(x), T_BOT - 80), 14, (255, 230, 160), -1, cv2.LINE_AA)
        cv2.line(img, (AX0, T_BOT + 60), (AX1, T_BOT + 60), YELLOW, 3, cv2.LINE_AA)
        label(img, "≈ 2.500 PIES · MÁS DE 750 M", (AX0 + AX1) / 2, T_BOT + 110, prog(t, 0.5, 0.4), 54, YELLOW)
        label(img, "3 DE DICIEMBRE DE 1844", W / 2, 110, prog(t, 0.2, 0.4), 64, WHITE)
        return img
    if mode == "seal":
        _tube(img, AX0, AX1)
        k1 = ease_out(prog(t, 0.4, 0.8))
        k2 = ease_out(prog(t, 1.0, 0.8))
        if k1 > 0:
            _soil(img, np.array([[AX0 - 10, T_TOP - 14], [AX0 + 150 * k1, T_TOP - 14], [AX0 + 150 * k1, T_BOT + 14], [AX0 - 10, T_BOT + 14]]), seed=5)
            _plug(img, AX0 + 150 * k1)
        if k2 > 0:
            _soil(img, np.array([[AX1 - 120 * k2, T_TOP - 14], [AX1 + 10, T_TOP - 14], [AX1 + 10, T_BOT + 14], [AX1 - 120 * k2, T_BOT + 14]]), seed=6)
            _plug(img, AX1 - 120 * k2)
        a = prog(t, 1.8, 0.5)
        if a > 0:
            x0, x1 = AX0 + 170, AX1 - 140
            cv2.line(img, (int(x0), T_BOT + 60), (int(x1), T_BOT + 60), YELLOW, 3, cv2.LINE_AA)
            label(img, "MÁS DE 2.000 PIES: HUECO Y ENTERO", (x0 + x1) / 2, T_BOT + 110, a, 56, YELLOW)
        label(img, "1861 · TAPARON LAS DOS BOCAS", W / 2, 110, prog(t, 0.2, 0.4), 64, WHITE)
        b = prog(t, 2.8, 0.4)
        if b > 0:
            label(img, "¿RELLENARLO ENTERO?  NI HABLAR", W / 2, 960, b, 58, WHITE, box=(150, 30, 30))
        return img
    # modes on the surviving tunnel: Hicks St wall .. east end
    _tube(img, XS["HICKS"], AX1 - 120)
    _plug(img, XS["HICKS"])
    _plug(img, AX1 - 120)
    mx = XS["COURT"]
    cv2.rectangle(img, (mx - 18, STREET_Y - 30), (mx + 18, T_TOP - 14), (24, 22, 20), -1)   # manhole + crawl
    cv2.ellipse(img, (mx, STREET_Y - 30), (34, 8), 0, 0, 360, (150, 150, 150), -1, cv2.LINE_AA)
    if mode == "onedoor":
        a = prog(t, 0.3, 0.4)
        cv2.arrowedLine(img, (mx + 150, T_TOP - 40), (mx + 26, T_TOP - 110), YELLOW, 6, cv2.LINE_AA, tipLength=0.2)
        label(img, "LA ÚNICA ENTRADA", mx + 40, T_TOP - 4, a, 46, YELLOW, "l")
        k = prog(t, 1.4, 0.6)
        if k > 0:
            sx = mx - 290
            for yy in range(STREET_Y, T_TOP - 14, 24):
                cv2.line(img, (sx - 30, yy), (sx - 30, yy + 12), WHITE, 3)
                cv2.line(img, (sx + 30, yy), (sx + 30, yy + 12), WHITE, 3)
            label(img, "UNA SEGUNDA ENTRADA", sx, T_BOT + 70, k, 44, WHITE)
        kx = ease_back(prog(t, 2.6, 0.4))
        if kx > 0:
            sx, sy, s = mx - 290, (STREET_Y + T_TOP) / 2, 60 * kx
            for sg in (1, -1):
                cv2.line(img, (int(sx - s), int(sy - s * sg)), (int(sx + s), int(sy + s * sg)), RED, 14, cv2.LINE_AA)
            label(img, "NUNCA APROBADA", sx, T_BOT + 120, prog(t, 2.8, 0.4), 44, (90, 90, 255))
        label(img, "UNA SOLA PUERTA", W / 2, 110, prog(t, 0.2, 0.4), 70, WHITE)
        return img
    if mode == "scan":
        wall = XS["HICKS"]
        k = ease_io(prog(t, 0.4, max(dur - 2.0, 1.5)))
        vx = lerp(XS["HENRY"], XS["COLUMBIA"] - 40, k)
        cv2.rectangle(img, (int(vx - 70), STREET_Y - 90), (int(vx + 70), STREET_Y - 34), (210, 210, 210), -1)
        for wx in (-44, 44):
            cv2.circle(img, (int(vx + wx), STREET_Y - 30), 12, (20, 20, 20), -1, cv2.LINE_AA)
        layer = img.copy()
        fill_poly(layer, np.array([[vx - 10, STREET_Y], [vx + 10, STREET_Y], [vx + 60, H], [vx - 60, H]]), (120, 200, 255))
        cv2.addWeighted(layer, 0.25, img, 0.75, 0, img)
        ox0, ox1 = wall - 230, wall - 70
        if vx < ox1 + 40:
            f = prog(vx, ox1 + 40, -1) if False else clamp((ox1 + 40 - vx) / 120)
            cv2.rectangle(img, (int(ox0), T_TOP + 60), (int(ox1), T_BOT - 30), (110, 120, 130), -1)
            layer = img.copy()
            cv2.rectangle(layer, (int(ox0) - 8, T_TOP + 52), (int(ox1) + 8, T_BOT - 22), YELLOW, 4)
            cv2.addWeighted(layer, f, img, 1 - f, 0, img)
            label(img, "OBJETO METÁLICO · ≈ 20 PIES · ≈ 6 M", ox0, T_BOT + 70, f, 46, YELLOW, "l")
            label(img, "¿QUÉ ES?", (ox0 + ox1) / 2, T_TOP - 60 + 0 * f, prog(t, dur - 1.4, 0.4), 60, WHITE)
        label(img, "LA PARED DE HICKS ST", wall + 30, T_TOP - 50, prog(t, 0.3, 0.4), 38, GREY, "l")
        label(img, "ENERO DE 2011 · ESCÁNER ELECTROMAGNÉTICO", W / 2, 110, prog(t, 0.2, 0.4), 58, WHITE)
        return img
    if mode == "today":
        for j in range(3):
            bx = ((t * 160 + j * 700) % (W + 400)) - 200
            _bus(img, bx, STREET_Y - 30, 0.9)
        a = prog(t, 0.4, 0.4)
        label(img, "ARRIBA: 2026", 220, STREET_Y - 150, a, 50, WHITE)
        label(img, "ABAJO: 1844", (XS["HICKS"] + AX1) / 2, (T_TOP + T_BOT) / 2, prog(t, 1.0, 0.4), 64, YELLOW)
        label(img, "LA TAPA DE ATLANTIC CON COURT", mx, T_BOT + 90, prog(t, 1.6, 0.4), 44, WHITE)
        return img
    return img


# ------------------------------------------------------------------ the descent (not to scale)
def descent(t, dur):
    img = background("dark_grid", t)
    gy, cy0, cy1 = 250, 380, 450           # street, crawl gap top/bottom
    vx0, vx1, vtop, vfloor = 250, 1100, 470, 1000
    _soil(img, np.array([[0, gy], [W, gy], [W, H], [0, H]]), seed=31)
    cv2.rectangle(img, (0, gy - 22), (W, gy), ASPHALT, -1)
    mx = 1500
    # manhole + 3 ft hole
    cv2.rectangle(img, (mx - 60, gy), (mx + 60, cy1), (14, 16, 20), -1)
    # crawl gap toward the west
    k = ease_io(prog(t, 1.0, 1.4))
    gx = lerp(mx - 60, vx1 - 40, k)
    cv2.rectangle(img, (int(gx), cy0), (mx - 60, cy1), (14, 16, 20), -1)
    # vault top (brick arch) and inside
    arch = np.stack([np.linspace(vx0, vx1, 60), vtop + 0 * np.linspace(0, 1, 60)], 1)
    xs = np.linspace(vx0, vx1, 60)
    ys = vtop + 140 * (((xs - (vx0 + vx1) / 2) / ((vx1 - vx0) / 2)) ** 2)
    arch = np.stack([xs, ys], 1)
    fill_poly(img, np.vstack([arch, [[vx1, vfloor], [vx0, vfloor]]]), BRICK)
    inner = np.stack([xs, ys + 34], 1)
    fill_poly(img, np.vstack([inner[2:-2], [[vx1 - 34, vfloor - 20], [vx0 + 34, vfloor - 20]]]), (16, 18, 22))
    # breach and rope ladder
    kb = prog(t, 2.6, 0.4)
    if kb > 0:
        bx = vx1 - 230
        cv2.circle(img, (bx, int(np.interp(bx, xs, ys)) + 14), int(40 * kb), (16, 18, 22), -1, cv2.LINE_AA)
        kl = ease_out(prog(t, 3.0, 0.6))
        ly = lerp(np.interp(bx, xs, ys) + 20, vfloor - 20, kl)
        for dx in (-18, 18):
            cv2.line(img, (bx + dx, int(np.interp(bx, xs, ys) + 20)), (bx + dx, int(ly)), (190, 170, 120), 3, cv2.LINE_AA)
        for yy in range(int(np.interp(bx, xs, ys) + 40), int(ly), 34):
            cv2.line(img, (bx - 18, yy), (bx + 18, yy), (190, 170, 120), 3, cv2.LINE_AA)
    # the explorer: down the hole, crawl west on the elbows, then down the ladder
    if t < 1.0:
        px, py = mx, lerp(gy - 10, cy1 - 4, ease_io(prog(t, 0.2, 0.7)))
        _person(img, px, py, 0.8, YELLOW)
    elif t < 2.6:
        px = lerp(mx - 70, vx1 - 230, ease_io(prog(t, 1.0, 1.5)))
        body = np.array([[px, cy1 - 14], [px + 70, cy1 - 12]])
        aa_poly(img, body, YELLOW, 16)
        cv2.circle(img, (int(px - 6), int(cy1 - 22)), 10, YELLOW, -1, cv2.LINE_AA)
        r = int(60 + 10 * math.sin(t * 9))
        layer = img.copy()
        cv2.circle(layer, (int(px - 30), int(cy1 - 20)), r, (255, 240, 200), -1, cv2.LINE_AA)
        cv2.addWeighted(layer, 0.25, img, 0.75, 0, img)
    else:
        bx = vx1 - 230
        py = lerp(np.interp(bx, xs, ys) + 30, vfloor - 20, ease_io(prog(t, 3.2, 1.0)))
        _person(img, bx, py, 0.8, YELLOW)
        if t > 4.3:
            layer = img.copy()
            fill_poly(layer, np.array([[bx, py - 40], [vx0 + 40, vfloor - 260], [vx0 + 40, vfloor - 30]]), (255, 236, 190))
            cv2.addWeighted(layer, 0.18 * prog(t, 4.3, 0.4), img, 1 - 0.18 * prog(t, 4.3, 0.4), 0, img)
    # dimensions
    a = prog(t, 0.4, 0.4)
    cv2.line(img, (mx + 90, gy), (mx + 90, cy1), WHITE, 2, cv2.LINE_AA)
    label(img, "3 PIES · < 1 M", mx + 110, (gy + cy1) / 2, a, 36, WHITE, "l")
    if k > 0.3:
        b = prog(t, 1.6, 0.4)
        label(img, "< 2 PIES DE ALTO · ≈ 60 CM", (gx + mx) / 2, cy0 - 40, b, 40, YELLOW)
        label(img, "70 PIES · MÁS DE 20 M", (gx + mx) / 2, cy1 + 40, b, 40, YELLOW)
    if kb > 0:
        label(img, "≈ 15 PIES · CASI 5 M", vx1 - 200, (vtop + vfloor) / 2 + 80, prog(t, 3.2, 0.4), 40, WHITE, "l")
    label(img, "1981 · LA BAJADA", W / 2, 90, prog(t, 0.1, 0.4), 64, WHITE)
    return img


# ------------------------------------------------------------------ the plans: a blueprint with a small circle
def blueprint(t, dur, hi_t=2.4):
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = BLUE
    for x in range(0, W, 40):
        cv2.line(img, (x, 0), (x, H), (40, 78, 136), 1)
    for y in range(0, H, 40):
        cv2.line(img, (0, y), (W, y), (40, 78, 136), 1)
    k = ease_io(prog(t, 0.2, 1.2))
    y0, y1 = 470, 610
    xa, xb = 120, lerp(120, 1800, k)
    lc = (220, 232, 245)
    cv2.line(img, (xa, y0), (int(xb), y0), lc, 3, cv2.LINE_AA)
    cv2.line(img, (xa, y1), (int(xb), y1), lc, 3, cv2.LINE_AA)
    sx = {"COLUMBIA": 200, "HICKS": 470, "HENRY": 720, "CLINTON": 1020, "COURT": 1340, "BOERUM": 1610}
    for i, (name, x) in enumerate(sx.items()):
        a = prog(t, 0.5 + i * 0.12, 0.3)
        if a <= 0:
            continue
        for dx in (-30, 30):
            cv2.line(img, (x + dx, 160), (x + dx, y0), lc, 2, cv2.LINE_AA)
            cv2.line(img, (x + dx, y1), (x + dx, 960), lc, 2, cv2.LINE_AA)
        label(img, name + (" PL." if name == "BOERUM" else " ST."), x, 120, a, 34, lc, fname="type")
    kt = prog(t, 1.4, 0.8)
    if kt > 0:
        for x in range(sx["COLUMBIA"], int(lerp(sx["COLUMBIA"], sx["BOERUM"], kt)), 36):
            cv2.line(img, (x, y0 + 30), (x + 18, y0 + 30), (150, 190, 230), 2)
            cv2.line(img, (x, y1 - 30), (x + 18, y1 - 30), (150, 190, 230), 2)
    label(img, "ATLANTIC AVENUE", 900, (y0 + y1) / 2, prog(t, 0.9, 0.5), 48, lc, fname="type")
    kc = prog(t, hi_t, 0.6)
    cx, cy = sx["COURT"], y1 - 22
    if kc > 0:
        cv2.ellipse(img, (cx, cy), (16, 16), 0, 0, 360 * kc, WHITE, 3, cv2.LINE_AA)
        f = prog(t, hi_t + 0.7, 0.6)
        if f > 0:
            ph = (t * 1.1) % 1
            layer = img.copy()
            cv2.circle(layer, (cx, cy), int(20 + 90 * ph), YELLOW, 5, cv2.LINE_AA)
            cv2.addWeighted(layer, (1 - ph) * f, img, 1 - (1 - ph) * f, 0, img)
            cv2.circle(img, (cx, cy), 18, YELLOW, 4, cv2.LINE_AA)
            label(img, "UNA ALCANTARILLA", cx + 40, cy + 120, f, 56, YELLOW, "l")
    label(img, "PLANO DEL TÚNEL · RECREACIÓN", W - 330, H - 50, 1.0, 28, (150, 190, 230), fname="type")
    return img


# ------------------------------------------------------------------ rumour board
def rumor_board(t, dur, cards):
    """cards: list of (t_in, text, sub, x, y)."""
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (62, 44, 30)
    rng = np.random.default_rng(5)
    noise = rng.normal(0, 9, (H // 4, W // 4)).astype(np.float32)
    noise = cv2.resize(cv2.GaussianBlur(noise, (0, 0), 1.2), (W, H))
    img = np.clip(img.astype(np.float32) + noise[..., None], 0, 255).astype(np.uint8)
    pins = []
    for i, (t0, text, sub, x, y) in enumerate(cards):
        a = ease_back(prog(t, t0, 0.35))
        if a <= 0:
            continue
        ang = ((i * 37) % 9 - 4) * 0.8
        sp = rounded_rect_sprite(400, 210, PAPER, 6, 255)
        over_center(img, sp, x, y, min(1, a * 1.5), a)
        label(img, text, x, y - 30, min(1, a * 1.5), 58, INK)
        if sub:
            label(img, sub, x, y + 40, min(1, a * 1.5), 34, (110, 90, 70))
        pins.append((x, y - 100, t0))
        cv2.circle(img, (int(x), int(y - 100)), 12, RED, -1, cv2.LINE_AA)
    for (x0, y0, ta), (x1, y1, tb) in zip(pins, pins[1:]):
        f = ease_io(prog(t, tb, 0.5))
        aa_poly(img, partial_line(np.array([[x0, y0], [(x0 + x1) / 2, max(y0, y1) + 50], [x1, y1]]), f), (180, 30, 30), 4)
    return img


# ------------------------------------------------------------------ the permit and the line nobody read
def permit(t, dur, mode="line"):
    """modes: line (highlight the revocation clause), signed (three renewals), revoked."""
    img = background("dark_grid", t)
    px0, py0, px1, py1 = 460, 70, 1460, 1030
    sp = rounded_rect_sprite(px1 - px0, py1 - py0, PAPER, 6, 255)
    over(img, sp, px0, py0)
    label(img, "PERMISO DE USO DEL TÚNEL", W / 2, 150, 1.0, 50, INK, fname="type")
    label(img, "BROOKLYN · 1986", W / 2, 205, 1.0, 34, (110, 90, 70), fname="type")
    rng = np.random.default_rng(3)
    ys = list(range(280, 900, 46))
    hl = ys[8]
    for y in ys:
        w = int(rng.uniform(560, 860))
        if y == hl:
            continue
        cv2.rectangle(img, (px0 + 70, y), (px0 + 70 + w, y + 12), (170, 160, 146), -1)
    k = ease_io(prog(t, 0.6, 0.8)) if mode == "line" else 1.0
    if k > 0:
        cv2.rectangle(img, (px0 + 50, hl - 30), (int(px0 + 50 + (px1 - px0 - 100) * k), hl + 40), (110, 220, 250), -1)
    label(img, "LA CIUDAD PODRÁ REVOCARLO EN CUALQUIER MOMENTO", W / 2, hl - 4, 1.0, 34, INK, fname="type")
    label(img, "Y SIN COMPENSACIÓN", W / 2, hl + 30, 1.0, 30, INK, fname="type")
    if mode == "signed":
        for i, yr in enumerate(("1986", "1998", "2008")):
            a = ease_back(prog(t, 0.5 + i * 0.6, 0.35))
            if a > 0:
                x = px0 + 230 + i * 270
                cv2.circle(img, (x, 960), int(70 * a), (40, 60, 150), 6, cv2.LINE_AA)
                label(img, yr, x, 960, min(1, a), 44, (40, 60, 150))
        label(img, "FIRMADO TRES VECES", W / 2, 40, prog(t, 2.2, 0.4), 50, YELLOW)
    elif mode == "revoked":
        a = ease_back(prog(t, 0.6, 0.35))
        if a > 0:
            st = text_sprite("REVOCADO", "bebas", int(180 * a) + 1, RED, False, tracking=6)
            over_center(img, st, W / 2, 470, 0.9)
        label(img, "17 DE DICIEMBRE DE 2010 · 4:45 P. M.", W / 2, 1060, prog(t, 1.2, 0.4), 40, WHITE)
    label(img, "RECREACIÓN", px1 - 120, py1 - 30, 1.0, 26, (130, 110, 90), fname="type")
    return img


# ------------------------------------------------------------------ 1844 vs 1863
def london(t, dur):
    img = background("dark_grid", t)
    y = 600
    x0, x1 = 300, 1620
    k = ease_io(prog(t, 0.3, 1.2))
    cv2.line(img, (x0, y), (int(lerp(x0, x1, k)), y), (150, 150, 150), 4, cv2.LINE_AA)
    for yr, x, name, col, t0 in ((1844, x0, "BROOKLYN · ATLANTIC STREET", YELLOW, 0.4), (1863, x1, "LONDRES · PRIMER METRO", WHITE, 1.4)):
        a = ease_back(prog(t, t0, 0.35))
        if a > 0:
            cv2.circle(img, (x, y), int(22 * a), col, -1, cv2.LINE_AA)
            label(img, str(yr), x, y - 110, min(a, 1), 110, col)
            label(img, name, x, y + 90, min(a, 1), 40, col)
    b = prog(t, 2.2, 0.5)
    if b > 0:
        aa_poly(img, np.array([[x0, y + 170], [x0, y + 200], [x1, y + 200], [x1, y + 170]]), YELLOW, 3)
        label(img, "19 AÑOS ANTES", W / 2, y + 270, b, 80, YELLOW)
    return img


# ------------------------------------------------------------------ radio waves over a photo
def radio(img, t, dur, lines, x=0.30, y=0.45, t0=0.6, every=1.1):
    cx, cy = W * x, H * y
    layer = img.copy()
    for k in range(4):
        ph = (t * 0.6 + k / 4) % 1
        cv2.ellipse(layer, (int(cx), int(cy)), (int(60 + 420 * ph), int(60 + 420 * ph)), 0, -50, 50, YELLOW, 6, cv2.LINE_AA)
        cv2.ellipse(layer, (int(cx), int(cy)), (int(60 + 420 * ph), int(60 + 420 * ph)), 0, 130, 230, YELLOW, 6, cv2.LINE_AA)
    cv2.addWeighted(layer, 0.45, img, 0.55, 0, img)
    for i, (txt, size) in enumerate(lines):
        a = prog(t, t0 + i * every, 0.4)
        if a > 0:
            label(img, txt, W * 0.70, H * 0.30 + i * 120, a, size, WHITE if i else YELLOW, box=(0, 0, 0) if i else None)
    return img


def counter_people(img, t, dur, n=400, t0=0.4):
    k = ease_out(prog(t, t0, 1.4))
    v = int(round(n * k))
    a = prog(t, t0, 0.3)
    layer = img.copy()
    cv2.rectangle(layer, (0, int(H * 0.30)), (W, int(H * 0.72)), (0, 0, 0), -1)
    cv2.addWeighted(layer, 0.45 * a, img, 1 - 0.45 * a, 0, img)
    label(img, f"HASTA {v}", W / 2, H * 0.44, a, 190, YELLOW)
    label(img, "PERSONAS AL MES", W / 2, H * 0.60, a, 70, WHITE)
    return img
