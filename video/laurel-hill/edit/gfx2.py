"""Custom animated diagrams and effects (pure code, no third-party footage)."""
import functools
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw

from engine import (BLACK, FPS, H, RED, STEEL, W, WHITE, YELLOW, Sprite, clamp, darken, ease_back, ease_in, ease_io,
                    ease_out, font, kb_frame, lerp, load_image, over, over_center, prog, rounded_rect_sprite,
                    text_sprite)
from gfx import background

GREY = (120, 122, 126)
DARKGREY = (52, 54, 58)
ROCK = (46, 44, 42)


def aa_poly(img, pts, col, thick, closed=False):
    p = np.round(np.asarray(pts, np.float64) * 4).astype(np.int32)
    cv2.polylines(img, [p], closed, col, thick, cv2.LINE_AA, shift=2)


def fill_poly(img, pts, col):
    p = np.round(np.asarray(pts, np.float64) * 4).astype(np.int32)
    cv2.fillPoly(img, [p], col, cv2.LINE_AA, shift=2)


def label(img, text, x, y, a=1.0, size=44, color=WHITE, anchor="c", fname="bebas", box=None):
    sp = text_sprite(text, fname, size, color, box is None, tracking=1 if fname == "bebas" else 0)
    if anchor == "c":
        px, py = x - sp.w / 2, y - sp.h / 2
    elif anchor == "l":
        px, py = x - 24, y - sp.h / 2
    else:
        px, py = x - sp.w + 24, y - sp.h / 2
    if box is not None:
        bx = rounded_rect_sprite(sp.w - 26, sp.h - 34, box, 5, 255)
        over(img, bx, px + 13, py + 17, a)
    over(img, sp, px, py, a)


def partial_line(pts, frac):
    pts = np.asarray(pts, np.float64)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    L = cum[-1] * clamp(frac)
    k = int(np.searchsorted(cum, L))
    if k <= 0:
        return pts[:1]
    if k >= len(pts):
        return pts
    a = (L - cum[k - 1]) / max(seg[k - 1], 1e-6)
    return np.vstack([pts[:k], pts[k - 1] + (pts[k] - pts[k - 1]) * a])


# ------------------------------------------------------------------ mountain cross-section
def mountain_profile(n=200, x0=160, x1=1760, base=860, peak=330, seed=4):
    xs = np.linspace(x0, x1, n)
    t = np.linspace(0, 1, n)
    rng = np.random.default_rng(seed)
    y = base - (base - peak) * np.sin(np.pi * t) ** 1.4
    y += np.convolve(rng.normal(0, 7, n), np.ones(7) / 7, mode="same")
    return np.stack([xs, y], 1)


@functools.lru_cache(maxsize=4)
def _mountain_bg(seed=4):
    img = background("dark_grid", 0.0)
    prof = mountain_profile(seed=seed)
    poly = np.vstack([[160, 1000], prof, [1760, 1000]])
    fill_poly(img, poly, ROCK)
    # strata lines
    for k in range(1, 7):
        yy = prof[:, 1] + k * 60
        pts = np.stack([prof[:, 0], np.minimum(yy, 980)], 1)
        aa_poly(img, pts, (60, 58, 55), 2)
    aa_poly(img, prof, (150, 146, 138), 4)
    cv2.line(img, (100, 1000), (1820, 1000), (90, 90, 90), 2, cv2.LINE_AA)
    return img, prof


def mountain(t, dur, mode="tunnel", seed=4):
    """modes: tunnel (draw tunnel through + 1 mile), bypass (tunnel vs over-the-top), bore (partial 830 ft),
    hidden (cars on top, dark tunnel below), pulse (car pulsing inside), elev (bypass + 2603 ft)."""
    bg, prof = _mountain_bg(seed)
    img = bg.copy()
    ty = 790
    tx0, tx1 = 330, 1590
    k_draw = ease_io(prog(t, 0.2, 1.4))
    if mode in ("tunnel", "bypass", "hidden", "pulse", "elev"):
        x = lerp(tx0, tx1, k_draw)
        cv2.rectangle(img, (tx0, ty - 22), (int(x), ty + 22), (14, 14, 16), -1)
        cv2.line(img, (tx0, ty - 22), (int(x), ty - 22), YELLOW if mode in ("tunnel", "pulse") else GREY, 3, cv2.LINE_AA)
        cv2.line(img, (tx0, ty + 22), (int(x), ty + 22), YELLOW if mode in ("tunnel", "pulse") else GREY, 3, cv2.LINE_AA)
        cv2.line(img, (100, ty + 22), (tx0, ty + 22), (180, 180, 180), 3, cv2.LINE_AA)
        cv2.line(img, (tx1, ty + 22), (1820, ty + 22), (180, 180, 180), 3, cv2.LINE_AA)
    if mode == "tunnel":
        a = prog(t, 1.4, 0.4)
        cv2.line(img, (tx0, ty + 70), (tx1, ty + 70), YELLOW, 2, cv2.LINE_AA)
        for xx in (tx0, tx1):
            cv2.line(img, (xx, ty + 58), (xx, ty + 82), YELLOW, 2, cv2.LINE_AA)
        label(img, "CASI UNA MILLA  ·  ≈ 1,4 KM", (tx0 + tx1) / 2, ty + 120, a, 46, YELLOW)
        label(img, "LAUREL HILL", W / 2, 250, prog(t, 0.6, 0.4), 64, WHITE)
    if mode == "bore":
        frac = 830 / 4541
        x = lerp(tx0, tx0 + (tx1 - tx0) * frac, k_draw)
        cv2.rectangle(img, (tx0, ty - 22), (int(x), ty + 22), (14, 14, 16), -1)
        cv2.rectangle(img, (tx0, ty - 22), (tx1, ty + 22), (90, 90, 90), 2, cv2.LINE_AA)
        a = prog(t, 1.2, 0.4)
        label(img, "830 PIES  ·  ≈ 250 M", tx0 + 130, ty - 70, a, 50, YELLOW, "l")
        label(img, "4.541 PIES (TÚNEL COMPLETO)", (tx0 + tx1) / 2 + 200, ty + 75, prog(t, 1.8, 0.4), 36, GREY)
        label(img, "1885: LA OBRA SE DETIENE", W / 2, 250, prog(t, 0.5, 0.4), 60, WHITE)
    if mode in ("bypass", "hidden", "elev"):
        # bypass over the crest
        bp = prof.copy()
        bp[:, 1] -= 16
        sel = (bp[:, 0] > 250) & (bp[:, 0] < 1670)
        bp = bp[sel]
        kb = ease_io(prog(t, 0.9 if mode == "bypass" else 0.1, 1.6))
        part = partial_line(bp, kb)
        if len(part) > 1:
            aa_poly(img, part, (0, 0, 0), 14)
            aa_poly(img, part, YELLOW, 7)
        if mode == "bypass":
            a = prog(t, 0.3, 0.4)
            label(img, "POR DENTRO", (tx0 + tx1) / 2, ty - 70, a, 46, GREY)
            if t > 2.2:
                cv2.line(img, (int((tx0 + tx1) / 2 - 150), ty - 70), (int((tx0 + tx1) / 2 + 150), ty - 70), RED, 5, cv2.LINE_AA)
            label(img, "POR ENCIMA", W / 2, 240, prog(t, 2.0, 0.4), 64, YELLOW)
        if mode == "elev":
            top = prof[np.argmin(prof[:, 1])]
            a = prog(t, 1.5, 0.4)
            cv2.circle(img, (int(top[0]), int(top[1] - 16)), 12, WHITE, -1, cv2.LINE_AA)
            label(img, "2.603 PIES  ·  ≈ 790 M", top[0], top[1] - 90, a, 54, WHITE)
            label(img, "EL PUNTO MÁS ALTO DE LA TURNPIKE", top[0], top[1] - 150, prog(t, 2.0, 0.4), 36, YELLOW)
        if mode == "hidden":
            n = 5
            for i in range(n):
                f = ((t * 0.12 + i / n) % 1.0)
                idx = int(f * (len(bp) - 1))
                p = bp[idx]
                cv2.circle(img, (int(p[0]), int(p[1] - 14)), 9, WHITE, -1, cv2.LINE_AA)
            a = prog(t, 1.2, 0.5)
            label(img, "?", (tx0 + tx1) / 2, ty, a, 80, YELLOW)
            label(img, "1964 · LA TRINCHERA", 1500, 280, prog(t, 0.4, 0.4), 40, YELLOW)
            label(img, "EL TÚNEL, A OSCURAS", (tx0 + tx1) / 2, ty + 90, a, 40, GREY)
    if mode == "pulse":
        f = (t * 0.45) % 1.0
        x = lerp(tx0 + 20, tx1 - 20, ease_io(f))
        cv2.circle(img, (int(x), ty), 12, RED, -1, cv2.LINE_AA)
        r = int(30 + 200 * ((t * 1.3) % 1.0))
        layer = img.copy()
        cv2.circle(layer, (int(x), ty), r, YELLOW, 3, cv2.LINE_AA)
        img = cv2.addWeighted(layer, 1 - ((t * 1.3) % 1.0), img, ((t * 1.3) % 1.0), 0)
    return img


# ------------------------------------------------------------------ lanes 4 -> 2
def lanes(t, dur, jam=False, title=None):
    img = background("dark_grid", t)
    y_mid = 560
    x_merge, x_portal = 1050, 1350
    lane_h = 70
    # road shape
    top4, bot4 = y_mid - 2 * lane_h, y_mid + 2 * lane_h
    top2, bot2 = y_mid - lane_h, y_mid + lane_h
    road = np.array([[0, top4], [x_merge, top4], [x_portal, top2], [W, top2], [W, bot2], [x_portal, bot2], [x_merge, bot4], [0, bot4]])
    fill_poly(img, road, (38, 39, 42))
    for k in (-1, 0, 1):
        yy = y_mid + k * lane_h
        for x in range(0, x_merge, 60):
            cv2.line(img, (x, yy), (x + 30, yy), (200, 200, 200) if k else YELLOW, 3 if k else 4, cv2.LINE_AA)
    cv2.line(img, (x_portal, y_mid), (W, y_mid), YELLOW, 4, cv2.LINE_AA)
    # mountain + portal
    mt = np.array([[x_portal - 40, 0], [W, 0], [W, H], [x_portal - 40, H], [x_portal - 40, bot2 + 10], [x_portal, bot2 + 10],
                   [x_portal, top2 - 10], [x_portal - 40, top2 - 10]])
    fill_poly(img, mt, ROCK)
    cv2.rectangle(img, (x_portal, top2), (W, bot2), (12, 12, 14), -1)
    cv2.line(img, (x_portal, y_mid), (W, y_mid), (90, 80, 30), 3, cv2.LINE_AA)
    label(img, "4 CARRILES", 420, top4 - 70, prog(t, 0.2, 0.4), 60, WHITE)
    label(img, "2 CARRILES", 1620, top2 - 70, prog(t, 0.8, 0.4), 60, YELLOW)
    label(img, "TÚNEL", 1620, bot2 + 60, prog(t, 0.8, 0.4), 40, GREY)
    # cars
    rng = np.random.default_rng(11)
    n = 34 if jam else 18
    speed = 260.0
    for i in range(n):
        lane = i % 4
        phase = rng.uniform(0, 1)
        y_lane = y_mid + (lane - 1.5) * lane_h
        if jam:
            # cars pile up before merge; queue grows with time
            q = (i // 4)
            stop_x = x_merge - 40 - q * 70 - lane * 6
            x = min(stop_x, -200 + (t * speed + phase * 900))
            if x >= stop_x - 1 and q < 2:
                x = stop_x + (t * 25 + phase * 40) % 50
        else:
            x = (-200 + (t * speed + phase * 2600)) % 2400 - 200
        y = y_lane
        if x > x_merge:
            k = clamp((x - x_merge) / (x_portal - x_merge))
            target = y_mid + (-0.5 if lane < 2 else 0.5) * lane_h
            y = lerp(y_lane, target, ease_io(k))
            if x > W:
                continue
        col = (210, 210, 205) if i % 5 else RED
        cv2.rectangle(img, (int(x - 22), int(y - 13)), (int(x + 22), int(y + 13)), col, -1, cv2.LINE_AA)
        cv2.rectangle(img, (int(x - 22), int(y - 13)), (int(x + 22), int(y + 13)), (20, 20, 20), 2, cv2.LINE_AA)
        if jam and x < x_merge:
            cv2.circle(img, (int(x - 22), int(y - 8)), 4, (255, 50, 50), -1, cv2.LINE_AA)
            cv2.circle(img, (int(x - 22), int(y + 8)), 4, (255, 50, 50), -1, cv2.LINE_AA)
    if title:
        label(img, title, W / 2, 140, prog(t, 0.3, 0.4), 70, WHITE)
    return img


# ------------------------------------------------------------------ tunnel cross section (two-way)
def tunnel_section(t, dur):
    img = background("dark_grid", t)
    cx, cy, r = W // 2, 760, 420
    fill_poly(img, np.array([[0, 300], [W, 300], [W, H], [0, H]]), ROCK)
    cv2.ellipse(img, (cx, cy), (r, r), 0, 180, 360, (16, 16, 18), -1, cv2.LINE_AA)
    cv2.rectangle(img, (cx - r, cy), (cx + r, cy + 120), (30, 30, 32), -1)
    cv2.ellipse(img, (cx, cy), (r, r), 0, 180, 360, (200, 200, 190), 5, cv2.LINE_AA)
    # lamps
    for k in range(5):
        ang = math.radians(220 + k * 25)
        px, py = cx + (r - 30) * math.cos(ang), cy + (r - 30) * math.sin(ang)
        cv2.circle(img, (int(px), int(py)), 10, (255, 236, 170), -1, cv2.LINE_AA)
    cv2.line(img, (cx, cy + 10), (cx, cy + 110), YELLOW, 5, cv2.LINE_AA)
    a = ease_out(prog(t, 0.4, 0.5))
    # arrows
    for side, d in ((-1, 1), (1, -1)):
        x0 = cx + side * r * 0.5
        L = 140 * a
        p0 = (int(x0 - d * L), cy + 60)
        p1 = (int(x0 + d * L), cy + 60)
        if L > 5:
            cv2.arrowedLine(img, p0, p1, WHITE, 8, cv2.LINE_AA, tipLength=0.3)
    label(img, "IDA", cx - r * 0.5, cy + 150, a, 52, WHITE)
    label(img, "VUELTA", cx + r * 0.5, cy + 150, a, 52, WHITE)
    label(img, "SIN SEPARACIÓN", cx, 200, prog(t, 1.0, 0.4), 70, YELLOW)
    # passing trucks
    f = (t * 0.6) % 1.0
    return img


# ------------------------------------------------------------------ waveform (rumble) overlay
def waveform_overlay(img, t, dur, y=0.5, amp=1.0, color=YELLOW):
    xs = np.arange(0, W, 6)
    env = 0.5 + 0.5 * np.sin(t * 2.1)
    k = prog(t, 0.0, 0.6) * (1 - prog(t, dur - 0.4, 0.4))
    ys = []
    for x in xs:
        u = x / W
        e = math.exp(-((u - 0.5) ** 2) / 0.06)
        v = (math.sin(u * 60 + t * 18) * 0.6 + math.sin(u * 23 - t * 11) * 0.4) * e * env
        ys.append(H * y + v * 120 * amp * k)
    pts = np.stack([xs, ys], 1)
    layer = img.copy()
    aa_poly(layer, pts, color, 4)
    img[:] = cv2.addWeighted(layer, 0.85, img, 0.15, 0)


def shake_frame(img, t, amt=8.0):
    dx = math.sin(t * 37.0) * amt + math.sin(t * 91.0) * amt * 0.4
    dy = math.cos(t * 43.0) * amt * 0.7
    M = np.array([[1.02, 0, dx - W * 0.01], [0, 1.02, dy - H * 0.01]], np.float32)
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)


class SnowOverlay:
    def __init__(self, n=260, seed=2, speed=1.0):
        rng = np.random.default_rng(seed)
        self.p = rng.uniform(0, 1, (n, 2))
        self.s = rng.uniform(0.4, 1.0, n)
        self.speed = speed

    def draw(self, img, t, dur):
        layer = img.copy()
        for (x, y), s in zip(self.p, self.s):
            yy = ((y + t * 0.07 * s * self.speed) % 1.0) * H
            xx = (x * W + math.sin(t * 0.8 + x * 20) * 30) % W
            cv2.circle(layer, (int(xx), int(yy)), int(1 + s * 3), (240, 240, 245), -1, cv2.LINE_AA)
        img[:] = cv2.addWeighted(layer, 0.75, img, 0.25, 0)


# ------------------------------------------------------------------ subscribe CTA
def subscribe(img, t, dur):
    a = ease_out(prog(t, 0.2, 0.4))
    if a <= 0:
        return
    bw, bh = 520, 120
    x, y = W / 2 - bw / 2, H * 0.62
    pressed = t > 1.6
    col = (60, 60, 60) if pressed else (204, 0, 0)
    sc = 1.0 - 0.06 * math.sin(math.pi * prog(t, 1.45, 0.25))
    btn = rounded_rect_sprite(bw, bh, col, 14, 255)
    over_center(img, btn, W / 2, y + bh / 2, a, sc)
    txt = text_sprite("SUSCRITO" if pressed else "SUSCRÍBETE", "sans_xb", 54, WHITE, False)
    over_center(img, txt, W / 2, y + bh / 2 + 2, a, sc)
    # bell
    bx, by = W / 2 + bw / 2 + 90, y + bh / 2
    bell = text_sprite("🔔", "sans", 10, WHITE, False) if False else None
    k = prog(t, 2.0, 0.3)
    if k > 0:
        ang = math.sin(t * 25) * 18 * (1 - prog(t, 2.3, 0.6))
        pts = np.array([[-30, 30], [-24, -10], [-12, -30], [0, -36], [12, -30], [24, -10], [30, 30]], np.float64)
        rot = np.array([[math.cos(math.radians(ang)), -math.sin(math.radians(ang))], [math.sin(math.radians(ang)), math.cos(math.radians(ang))]])
        pts = pts @ rot.T + [bx, by]
        fill_poly(img, pts, WHITE)
        cv2.circle(img, (int(bx), int(by + 40)), 8, WHITE, -1, cv2.LINE_AA)
    # cursor
    cx = lerp(W / 2 + 500, W / 2 + 60, ease_io(prog(t, 0.6, 0.8)))
    cy = lerp(y + 380, y + bh / 2 + 10, ease_io(prog(t, 0.6, 0.8)))
    if t > 0.6 and t < dur - 0.2:
        cur = np.array([[0, 0], [0, 46], [12, 35], [22, 56], [30, 52], [20, 32], [36, 32]], np.float64) + [cx, cy]
        fill_poly(img, cur, WHITE)
        aa_poly(img, cur, BLACK, 2, True)


def garage_close(t, dur, bg_fn):
    """Shutter door slides down over bg_fn(t)."""
    img = bg_fn(t)
    k = ease_in(prog(t, 0.3, dur - 0.6))
    hh = int(H * k)
    if hh > 0:
        door = np.zeros((hh, W, 3), np.uint8)
        door[:] = (70, 72, 74)
        for y in range(hh - 1, -1, -26):
            cv2.line(door, (0, y), (W, y), (40, 41, 43), 4)
            cv2.line(door, (0, y - 3), (W, y - 3), (110, 112, 114), 1)
        img[:hh] = door
        cv2.rectangle(img, (0, max(0, hh - 30)), (W, hh), (30, 30, 30), -1)
    return img


def lights_off(img, t, dur, start=0.4, span=1.6):
    """Progressively darken the image from far (centre) to near (edges) like lights switching off."""
    yy, xx = np.mgrid[0:H:4, 0:W:4].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.45) / (H / 2)) ** 2)
    k = prog(t, start, span)
    thr = k * 1.6
    mask = np.clip((thr - r) * 3, 0, 1)
    mask = cv2.resize(mask, (W, H))
    flick = 1.0 if int(t * 20) % 7 else 0.85
    out = img.astype(np.float32) * (1 - 0.93 * mask[..., None]) * flick
    img[:] = np.clip(out, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ aerodynamics
def aero(t, dur, mode="downforce"):
    img = background("dark_grid", t)
    # car silhouette (side view open-wheel)
    body = np.array([[620, 640], [760, 600], [900, 585], [1000, 560], [1060, 540], [1120, 548], [1180, 585], [1330, 595],
                     [1380, 610], [1390, 640]], np.float64)
    base_y = 660
    moving = mode == "track"
    dx = 0
    fill_poly(img, np.vstack([body + [dx, 0], [[1390 + dx, base_y], [620 + dx, base_y]]]), (200, 200, 196))
    cv2.rectangle(img, (560 + dx, 575), (600 + dx, 650), (200, 200, 196), -1)
    cv2.rectangle(img, (1350 + dx, 560), (1420 + dx, 575), (200, 200, 196), -1)
    for wx in (720, 1250):
        cv2.circle(img, (wx + dx, base_y), 48, (25, 25, 25), -1, cv2.LINE_AA)
        cv2.circle(img, (wx + dx, base_y), 48, (160, 160, 160), 3, cv2.LINE_AA)
        if moving:
            a = t * 12
            cv2.line(img, (int(wx + dx + 40 * math.cos(a)), int(base_y + 40 * math.sin(a))),
                     (int(wx + dx - 40 * math.cos(a)), int(base_y - 40 * math.sin(a))), (160, 160, 160), 3, cv2.LINE_AA)
    cv2.line(img, (0, base_y + 50), (W, base_y + 50), (110, 110, 110), 3, cv2.LINE_AA)
    if moving:
        for x in range(int(-(t * 900) % 120), W, 120):
            cv2.line(img, (x, base_y + 70), (x + 50, base_y + 70), (90, 90, 90), 3, cv2.LINE_AA)
    # streamlines
    n = 9
    for i in range(n):
        y0 = 380 + i * 34
        xs = np.arange(0, W, 8, dtype=np.float64)
        bump = np.exp(-((xs - 1000) / 330) ** 2) * (150 - i * 9)
        ys = y0 - bump * (1 if y0 < 600 else -0.2)
        pts = np.stack([xs, ys], 1)
        if mode in ("downforce", "windtunnel"):
            ph = (t * 1.4 + i * 0.13) % 1.0
            seg_n = len(pts)
            a0 = int(ph * seg_n)
            for s in range(0, seg_n - 20, 40):
                j = (s + a0) % (seg_n - 20)
                aa_poly(img, pts[j:j + 18], (120, 190, 235), 3)
        else:
            aa_poly(img, pts[::3], (70, 90, 105), 1)
    if mode == "downforce":
        a = ease_out(prog(t, 0.8, 0.5))
        for x in (760, 1000, 1240):
            L = 120 * a
            cv2.arrowedLine(img, (x, int(470 - L)), (x, 470), YELLOW, 8, cv2.LINE_AA, tipLength=0.35)
        label(img, "CARGA AERODINÁMICA", W / 2, 220, prog(t, 0.9, 0.4), 70, YELLOW)
        label(img, "EL AIRE «PEGA» EL AUTO AL ASFALTO", W / 2, 300, prog(t, 1.2, 0.4), 40, WHITE)
    if mode == "windtunnel":
        label(img, "TÚNEL DE VIENTO", W / 2, 200, prog(t, 0.2, 0.4), 72, WHITE)
        label(img, "AUTO QUIETO  ·  AIRE EN MOVIMIENTO", W / 2, 280, prog(t, 0.5, 0.4), 42, (120, 190, 235))
        # fan on left
        cx, cy = 140, 520
        cv2.circle(img, (cx, cy), 120, (90, 90, 90), 6, cv2.LINE_AA)
        for k in range(6):
            ang = t * 9 + k * math.pi / 3
            cv2.line(img, (cx, cy), (int(cx + 110 * math.cos(ang)), int(cy + 110 * math.sin(ang))), (170, 170, 170), 12, cv2.LINE_AA)
    if mode == "track":
        label(img, "EN LA PISTA", W / 2, 200, prog(t, 0.2, 0.4), 72, YELLOW)
        label(img, "AUTO EN MOVIMIENTO  ·  AIRE QUIETO", W / 2, 280, prog(t, 0.5, 0.4), 42, WHITE)
        label(img, "LAUREL HILL", W / 2, 920, prog(t, 1.2, 0.4), 56, YELLOW, box=None)
    return img


# ------------------------------------------------------------------ tunnel top view (test run)
def tunnel_topview(t, dur, mode="facts"):
    img = background("dark_grid", t)
    y0, y1 = 470, 610
    x0, x1 = 180, 1740
    fill_poly(img, np.array([[0, 0], [W, 0], [W, H], [0, H]]), (24, 25, 27))
    img[:] = cv2.addWeighted(img, 1, background("dark_grid", t), 0.5, 0)
    k = ease_io(prog(t, 0.1, 1.0))
    cv2.rectangle(img, (x0, y0), (int(lerp(x0, x1, k)), y1), (36, 37, 40), -1)
    cv2.rectangle(img, (x0, y0), (int(lerp(x0, x1, k)), y1), (200, 200, 190), 3, cv2.LINE_AA)
    if k >= 1:
        for xx in (x0, x1):
            cv2.line(img, (xx, y0 - 30), (xx, y1 + 30), RED, 10, cv2.LINE_AA)
    if mode == "facts":
        label(img, "CASI UNA MILLA EN LÍNEA RECTA", W / 2, 360, prog(t, 0.8, 0.4), 60, WHITE)
        label(img, "CERRADO POR LOS DOS LADOS", W / 2, 700, prog(t, 1.6, 0.4), 44, RED)
        label(img, "AIRE QUIETO", W / 2 - 360, 800, prog(t, 2.4, 0.4), 44, (120, 190, 235))
        label(img, "TEMPERATURA ESTABLE", W / 2 + 300, 800, prog(t, 3.0, 0.4), 44, YELLOW)
    else:
        # car run: accelerate, measure, brake
        tt = prog(t, 0.6, dur - 1.0)
        if tt < 0.55:
            f = 0.62 * (tt / 0.55) ** 2
        elif tt < 0.8:
            f = 0.62 + (tt - 0.55) / 0.25 * 0.25
        else:
            u = (tt - 0.8) / 0.2
            f = 0.87 + 0.1 * (1 - (1 - u) ** 2)
        x = lerp(x0 + 40, x1 - 40, f)
        cv2.rectangle(img, (int(x - 36), 525), (int(x + 36), 555), YELLOW, -1, cv2.LINE_AA)
        for a_, txt, xx, col in ((0.0, "ACELERAR", x0 + 300, WHITE), (0.45, "MEDIR", W / 2 + 120, (120, 190, 235)),
                                 (0.78, "FRENAR", x1 - 200, RED)):
            label(img, txt, xx, 400, prog(tt, a_, 0.08), 56, col)
        label(img, "MENOS DE UNA MILLA", W / 2, 700, prog(t, 0.3, 0.4), 44, GREY)
    return img


def telemetry(img, t, dur):
    """Data lines over an image."""
    layer = img.copy()
    k = prog(t, 0.2, dur * 0.8)
    for j, col in enumerate(((244, 196, 48), (120, 190, 235), (230, 90, 90))):
        xs = np.linspace(120, W - 120, 200)
        n = int(len(xs) * k)
        if n < 2:
            continue
        ys = 760 - j * 120 + 40 * np.sin(xs / 90 + j) + 25 * np.sin(xs / 31 + j * 2)
        aa_poly(layer, np.stack([xs[:n], ys[:n]], 1), col, 4)
    img[:] = cv2.addWeighted(layer, 0.9, img, 0.1, 0)
    for j, (txt, val) in enumerate((("VELOCIDAD", "162 KM/H"), ("CARGA", "+38%"), ("ARRASTRE", "-4%"))):
        label(img, f"{txt}  {val}", 260 + j * 520, 200, prog(t, 0.3 + j * 0.3, 0.3), 40, WHITE, box=(16, 16, 18))


# ------------------------------------------------------------------ patents / championships / titles
def patents(t, dur):
    img = background("dark_grid", t)
    label(img, "2006", W / 2, 170, prog(t, 0.1, 0.4), 90, YELLOW)
    for i in range(4):
        a = ease_back(prog(t, 0.5 + i * 0.35, 0.35))
        if a <= 0:
            continue
        x = W / 2 - 540 + i * 360
        y = 560
        sp = rounded_rect_sprite(260, 340, (232, 228, 218), 6, 255)
        over_center(img, sp, x, y, min(1, a), max(0.05, a))
        if a > 0.6:
            for k in range(7):
                yy = int(y - 120 + k * 32)
                cv2.line(img, (int(x - 95), yy), (int(x + (70 if k % 3 else 20)), yy), (150, 146, 138), 6)
            label(img, f"PATENTE {i + 1}", x, y + 210, 1, 34, WHITE)
    label(img, "SISTEMA PARA PROBAR VEHÍCULOS EN MOVIMIENTO", W / 2, 900, prog(t, 2.0, 0.4), 46, WHITE)
    label(img, "GANASSI  ·  BOWLBY", W / 2, 960, prog(t, 2.3, 0.4), 34, GREY)
    return img


def trophy(img, x, y, s=1.0, col=YELLOW):
    cup = np.array([[-40, -60], [40, -60], [34, -10], [12, 14], [12, 40], [36, 52], [-36, 52], [-12, 40], [-12, 14], [-34, -10]], np.float64) * s + [x, y]
    fill_poly(img, cup, col)
    cv2.ellipse(img, (int(x - 44 * s), int(y - 40 * s)), (int(18 * s), int(22 * s)), 0, 90, 270, col, int(6 * s), cv2.LINE_AA)
    cv2.ellipse(img, (int(x + 44 * s), int(y - 40 * s)), (int(18 * s), int(22 * s)), 0, -90, 90, col, int(6 * s), cv2.LINE_AA)


def championships(t, dur):
    img = background("dark_grid", t)
    label(img, "CAMPEONES DE INDYCAR", W / 2, 190, prog(t, 0.1, 0.4), 76, WHITE)
    for i, yr in enumerate((2008, 2009, 2010, 2011)):
        a = ease_back(prog(t, 0.6 + i * 0.45, 0.35))
        if a <= 0:
            continue
        x = W / 2 - 600 + i * 400
        trophy(img, x, 520, 1.6 * max(0.05, a))
        label(img, str(yr), x, 720, min(1, a), 80, WHITE)
    label(img, "4 SEGUIDOS", W / 2, 880, prog(t, 2.6, 0.4), 70, YELLOW)
    return img


def palou_titles(t, dur):
    img = background("dark_grid", t)
    label(img, "ÁLEX PALOU · TÍTULOS DE INDYCAR", W / 2, 190, prog(t, 0.1, 0.4), 64, WHITE)
    yrs = (2021, 2023, 2024, 2025, 2026)
    for i, yr in enumerate(yrs):
        a = ease_back(prog(t, 0.5 + i * 0.4, 0.35))
        if a <= 0:
            continue
        x = W / 2 - 640 + i * 320
        trophy(img, x, 520, 1.3 * max(0.05, a), YELLOW if yr >= 2023 else (200, 200, 200))
        label(img, str(yr), x, 700, min(1, a), 64, WHITE)
    k = prog(t, 2.8, 0.4)
    if k > 0:
        cv2.line(img, (int(W / 2 - 340), 790), (int(W / 2 + 660), 790), YELLOW, 6, cv2.LINE_AA)
        label(img, "CUATRO SEGUIDOS", W / 2 + 160, 850, k, 50, YELLOW)
        label(img, "QUINTO TÍTULO · MILWAUKEE, 30 AGO 2026", W / 2, 950, prog(t, 3.3, 0.4), 40, WHITE)
    return img


def triple_2010(t, dur, imgs, times=(0.6, 2.2, 3.8)):
    img = background("dark_grid", t)
    label(img, "2010 · UNA SOLA TEMPORADA", W / 2, 150, prog(t, 0.1, 0.4), 66, YELLOW)
    cards = (("INDY 500", "DARIO FRANCHITTI"), ("DAYTONA 500", "JAMIE McMURRAY"), ("BRICKYARD 400", "JAMIE McMURRAY"))
    for i, ((title, who), p) in enumerate(zip(cards, imgs)):
        a = ease_out(prog(t, times[i], 0.45))
        if a <= 0:
            continue
        x = W / 2 - 600 + i * 600
        y = 560 + 60 * (1 - a)
        if p:
            src = load_image(p, "doc")
            ph = kb_frame(src, 0.5, 0.5, 1.0, ow=520, oh=340)
            canvas = np.zeros((360, 540, 4), np.uint8)
            canvas[..., :3] = (236, 232, 222)
            canvas[..., 3] = 255
            canvas[10:350, 10:530, :3] = ph
            over_center(img, Sprite(canvas), x, y - 40, a)
        else:
            over_center(img, rounded_rect_sprite(540, 360, (40, 40, 44), 6, 255), x, y - 40, a)
            trophy(img, x, y - 40, 1.6)
        label(img, title, x, y + 190, a, 60, WHITE)
        label(img, who, x, y + 250, a, 38, YELLOW)
    return img


def circle_story(t, dur):
    img = background("dark_grid", t)
    cx, cy, r = W / 2, 560, 300
    k = ease_io(prog(t, 0.2, 2.6))
    cv2.ellipse(img, (int(cx), int(cy)), (r, r), -90, 0, int(360 * k), YELLOW, 5, cv2.LINE_AA)
    items = (("1881", "UN TREN QUE NUNCA LLEGÓ", -90), ("1940", "AUTOS DURANTE 24 AÑOS", 30), ("2003", "UN SECRETO", 150))
    for i, (yr, txt, ang) in enumerate(items):
        a = prog(t, 0.4 + i * 0.9, 0.4)
        x = cx + r * math.cos(math.radians(ang))
        y = cy + r * math.sin(math.radians(ang))
        cv2.circle(img, (int(x), int(y)), int(26 * a), YELLOW, -1, cv2.LINE_AA)
        label(img, yr, x, y - 80 if ang < 0 else y + 80, a, 64, WHITE)
        label(img, txt, x, y - 30 if ang < 0 else y + 130, a, 34, (210, 206, 198))
    return img


def comments_cta(img, t, dur):
    a = ease_out(prog(t, 0.2, 0.4))
    if a <= 0:
        return
    bx, by = W / 2, H * 0.58
    bub = rounded_rect_sprite(980, 220, (245, 242, 235), 28, 255)
    over_center(img, bub, bx, by, a)
    tail = np.array([[bx - 300, by + 100], [bx - 360, by + 170], [bx - 230, by + 105]])
    if a > 0.9:
        fill_poly(img, tail, (245, 242, 235))
    label(img, "¿QUÉ RECUERDA TU FAMILIA", bx, by - 40, a, 62, (20, 20, 20), fname="bebas")
    label(img, "DE LOS DOS CARRILES BAJO LA MONTAÑA?", bx, by + 30, a, 46, (20, 20, 20), fname="bebas")
    label(img, "CUÉNTAMELO EN LOS COMENTARIOS", W / 2, H * 0.82, prog(t, 0.9, 0.4), 50, YELLOW)


def sound_rings(img, t, dur, cx=0.55, cy=0.62):
    layer = img.copy()
    x, y = int(W * cx), int(H * cy)
    for k in range(5):
        ph = ((t * 0.7) + k / 5) % 1.0
        r = int(40 + ph * 900)
        a = (1 - ph)
        cv2.ellipse(layer, (x, y), (r, int(r * 0.6)), 0, 200, 340, YELLOW, max(1, int(6 * a)), cv2.LINE_AA)
    img[:] = cv2.addWeighted(layer, 0.8, img, 0.2, 0)


def speed_tunnel(t, dur, path="c021.jpg", grade="warm"):
    """Endless forward rush through a lit tunnel photo: looping zoom with motion blur."""
    src = load_image(path, grade)
    accel = 0.35 + 1.2 * prog(t, 0, dur)
    ph = (t * accel) % 1.0
    a = kb_frame(src, 0.5, 0.48, 1.0 + ph * 0.9)
    b = kb_frame(src, 0.5, 0.48, 1.0 + ((ph + 0.5) % 1.0) * 0.9)
    w = abs(ph - 0.5) * 2
    fr = cv2.addWeighted(a, 1 - w * 0.5, b, w * 0.5, 0)
    # radial blur approximation
    acc = fr.astype(np.float32)
    for s in (1.02, 1.045, 1.07):
        acc += cv2.warpAffine(fr, np.array([[s, 0, W / 2 * (1 - s)], [0, s, H * 0.48 * (1 - s)]], np.float32), (W, H)).astype(np.float32)
    return (acc / 4).astype(np.uint8)


def flare(img, t, dur, t0=0.3, d=0.9):
    """Headlights passing: bright flare moving from centre to right edge."""
    k = prog(t, t0, d)
    if k <= 0 or k >= 1:
        return
    x = int(lerp(W * 0.52, W * 1.15, ease_in(k)))
    y = int(lerp(H * 0.52, H * 0.7, ease_in(k)))
    r = int(lerp(20, 380, ease_in(k)))
    layer = np.zeros_like(img)
    cv2.circle(layer, (x, y), r, (255, 245, 210), -1, cv2.LINE_AA)
    cv2.circle(layer, (x - r, y), int(r * 0.9), (255, 245, 210), -1, cv2.LINE_AA)
    layer = cv2.GaussianBlur(layer, (0, 0), max(3, r * 0.45))
    img[:] = cv2.add(img, (layer.astype(np.float32) * 0.9).astype(np.uint8))


def shutter_flash(img, t, dur, times=(0.5, 1.3)):
    for t0 in times:
        if t0 <= t <= t0 + 0.12:
            k = 1 - (t - t0) / 0.12
            img[:] = cv2.addWeighted(np.full_like(img, 255), k * 0.9, img, 1 - k * 0.9, 0)
