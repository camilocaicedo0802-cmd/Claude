"""I-80 Wyoming diagrams: blowing snow, snow fences, wind past Elk Mountain, countdown, truck queue, survey..."""
import functools
import math

import cv2
import numpy as np

from engine import (BLACK, H, RED, W, WHITE, YELLOW, clamp, ease_back, ease_in, ease_io, ease_out, lerp, over,
                    over_center, prog, rounded_rect_sprite, text_sprite)
from gfx import background
from gfx2 import GREY, aa_poly, fill_poly, label, partial_line

SNOW = (236, 240, 246)
SKY0, SKY1 = (22, 28, 38), (58, 70, 86)
GROUND = (48, 50, 52)
ICE = (150, 190, 225)


# ------------------------------------------------------------------ helpers
@functools.lru_cache(maxsize=4)
def _sky():
    g = np.linspace(0, 1, H)[:, None, None]
    img = (np.array(SKY0) * (1 - g) + np.array(SKY1) * g).astype(np.uint8)
    return np.repeat(img, W, axis=1)


def arrow(img, x0, y0, x1, y1, col, th=5, head=22):
    cv2.line(img, (int(x0), int(y0)), (int(x1), int(y1)), col, th, cv2.LINE_AA)
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (-1, 1):
        a = ang + math.pi + s * 0.45
        cv2.line(img, (int(x1), int(y1)), (int(x1 + head * math.cos(a)), int(y1 + head * math.sin(a))), col, th,
                 cv2.LINE_AA)


def wind_lines(img, t, y0, y1, speed=1.0, n=14, alpha=0.5, seed=5):
    rng = np.random.default_rng(seed)
    layer = img.copy()
    for i in range(n):
        y = rng.uniform(y0, y1)
        ph = rng.uniform(0, 1)
        ln = rng.uniform(160, 340)
        x = ((t * 520 * speed * rng.uniform(0.8, 1.2) / W + ph) % 1.25) * (W + 400) - 300
        cv2.line(layer, (int(x), int(y)), (int(x + ln), int(y)), (200, 214, 230), 2, cv2.LINE_AA)
    img[:] = cv2.addWeighted(layer, alpha, img, 1 - alpha, 0)


# ------------------------------------------------------------------ blowing snow cross-section
GY = 760  # ground line


def _ground_profile(mode):
    xs = np.linspace(0, W, 400)
    ys = np.full_like(xs, GY, dtype=np.float64)
    if mode in ("trap", "fence", "road"):
        # road embankment centred at x=1300: 2 lanes on a raised fill
        x0, x1 = 1060, 1560
        ramp = 110
        for i, x in enumerate(xs):
            if x0 - ramp <= x < x0:
                ys[i] = GY - 70 * (x - (x0 - ramp)) / ramp
            elif x0 <= x <= x1:
                ys[i] = GY - 70
            elif x1 < x <= x1 + ramp:
                ys[i] = GY - 70 * (1 - (x - x1) / ramp)
    return np.stack([xs, ys], 1)


def _drift(x0, length, height, k):
    """Lee-side drift shape behind an obstacle at x0, grown to fraction k (smooth rise, long tail)."""
    L = length * (0.25 + 0.75 * k)
    h = height * k
    xs = np.linspace(x0, x0 + L, 90)
    u = (xs - x0) / max(L, 1)
    prof = np.where(u < 0.22, np.sin(np.clip(u / 0.22, 0, 1) * np.pi / 2) ** 0.8, (np.clip(1 - u, 0, 1) / 0.78) ** 1.5)
    ys = GY - h * prof
    return np.vstack([[x0, GY], np.stack([xs, ys], 1), [x0 + L, GY]])


FOCUS = {"travel": (W / 2, GY - 170, 1.12), "road": (1310, GY - 150, 1.6), "trap": (1300, GY - 150, 1.55),
         "fence": (1080, GY - 150, 1.4), "fence_h2": (1080, GY - 190, 1.25)}


def snow_section(t, dur, mode="travel", tag_t0=0.8):
    """mode: travel | road | trap | fence | fence_h2 . Cross-section of the plateau with wind-blown snow."""
    img = _sky().copy()
    prof = _ground_profile("road" if mode != "travel" else "travel")
    fill_poly(img, np.vstack([prof, [[W, H], [0, H]]]), GROUND)
    g = np.linspace(1.0, 0.45, H - GY)[:, None, None]
    img[GY:] = (img[GY:] * g).astype(np.uint8)
    aa_poly(img, prof, (110, 112, 114), 3)
    cv2.line(img, (0, GY + 2), (W, GY + 2), (160, 164, 170), 3, cv2.LINE_AA)
    wind_lines(img, t, 380, GY - 40, 1.0, 16, 0.35)
    if mode != "travel":
        cv2.rectangle(img, (1060, GY - 78), (1560, GY - 68), (30, 30, 32), -1)
        cv2.line(img, (1300, GY - 74), (1320, GY - 74), (230, 200, 60), 3)
        for x in (1080, 1540):
            cv2.line(img, (x, GY - 78), (x, GY - 128), (170, 172, 176), 7, cv2.LINE_AA)
            cv2.line(img, (x - 30, GY - 120), (x + 30, GY - 120), (170, 172, 176), 7, cv2.LINE_AA)
    fence_x = 760
    hf = 110 if mode == "fence" else 220
    if mode == "trap":
        k = ease_io(prog(t, 0.8, max(dur - 1.6, 1.0)))
        drift = _drift(1110, 520, 190, k)
        fill_poly(img, drift, SNOW)
        aa_poly(img, drift[1:-1], (190, 200, 214), 2)
    if mode in ("fence", "fence_h2"):
        k = ease_io(prog(t, 1.0, max(dur - 1.8, 1.0)))
        drift = _drift(fence_x + 6, (5.2 if mode == "fence" else 4.6) * hf, 1.15 * hf, k)
        fill_poly(img, drift, SNOW)
        cv2.line(img, (fence_x, GY), (fence_x, GY - hf), (120, 84, 50), 8, cv2.LINE_AA)
        cv2.line(img, (fence_x, GY - hf), (fence_x - int(hf * 0.7), GY), (120, 84, 50), 6, cv2.LINE_AA)
        for yy in range(GY - hf + 10, GY - 10, 22):
            cv2.line(img, (fence_x - 4, yy), (fence_x + 4, yy), (150, 110, 70), 10)
    # particles
    rng = np.random.default_rng(11)
    n = 300
    px = rng.uniform(0, 1, n)
    py = rng.uniform(0, 1, n) ** 2.2
    sp = rng.uniform(0.7, 1.3, n)
    layer = img.copy()
    for i in range(n):
        x = ((px[i] + t * 0.35 * sp[i]) % 1.0) * (W + 200) - 100
        hop = abs(math.sin((x / 160.0) + py[i] * 9.1)) * (25 + 380 * py[i])
        y = GY - 8 - hop
        if mode in ("fence", "fence_h2") and fence_x - 20 < x < fence_x + 520 and t > 1.0:
            y = GY - 8 - hop * clamp((x - fence_x - 300) / 220)
            if x > fence_x + 400:
                continue
        if mode == "trap" and 1000 < x < 1600 and t > 0.8:
            y = max(y, GY - 80 - hop * 0.3)
        cv2.circle(layer, (int(x), int(y)), 2 + int(sp[i] * 1.6), SNOW, -1, cv2.LINE_AA)
    img = cv2.addWeighted(layer, 0.85, img, 0.15, 0)
    fx, fy, sc = FOCUS[mode]
    M = np.array([[sc, 0, W / 2 - sc * fx], [0, sc, H / 2 - sc * fy]], np.float32)
    img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    def P(x, y):
        return (x - fx) * sc + W / 2, (y - fy) * sc + H / 2

    if mode == "travel":
        label(img, "NIEVE SECA, COMO POLVO", W / 2, 200, prog(t, 0.4, 0.4), 70, WHITE)
        label(img, "VIAJA CON EL VIENTO", W / 2, 280, prog(t, 1.0, 0.4), 56, YELLOW)
        arrow(img, 160, 470, 560, 470, YELLOW, 7, 30)
        label(img, "VIENTO", 360, 415, prog(t, 0.2, 0.4), 46, YELLOW)
    if mode == "road":
        label(img, "UNA CARRETERA = OBSTÁCULOS", W / 2, 150, prog(t, 0.3, 0.4), 64, WHITE)
        tags = [("DESNIVEL", 1630, GY - 30, tag_t0), ("TERRAPLÉN", 1000, GY - 30, tag_t0 + 0.7), ("BARANDAL", 1080, GY - 150, tag_t0 + 1.4)]
        for txt, x, y, t0 in tags:
            a = ease_out(prog(t, t0, 0.3))
            if a > 0:
                X, Y = P(x, y)
                cv2.circle(img, (int(X), int(Y)), int(14 * a), RED, -1, cv2.LINE_AA)
                label(img, txt, X, Y - 60, a, 50, RED)
    if mode == "trap":
        label(img, "LA NIEVE CAE DONDE EL VIENTO TROPIEZA", W / 2, 150, prog(t, 0.3, 0.4), 60, WHITE)
        X, Y = P(1330, GY - 260)
        label(img, "4 PIES  ·  +1 M", X, Y, prog(t, 1.6, 0.4), 60, YELLOW)
    if mode == "fence":
        label(img, "LA VALLA NO DETIENE LA NIEVE", W / 2, 150, prog(t, 0.3, 0.4), 62, WHITE)
        label(img, "LA HACE CAER ANTES", W / 2, 225, prog(t, 1.4, 0.4), 56, YELLOW)
        X, Y = P(1310, GY - 175)
        label(img, "CARRETERA LIMPIA", X, Y, prog(t, 2.2, 0.4), 50, YELLOW)
    if mode == "fence_h2":
        X, Y = P(fence_x, GY - hf - 60)
        label(img, "VALLA DE 12 PIES  ·  ≈ 4 M", X, Y, prog(t, 0.3, 0.4), 52, YELLOW)
    return img


def fence_math(t, dur, t2=1.9, final_t=3.6):
    """Doubling the fence height stores about four times the snow."""
    img = background("dark_grid", t)
    base = 820
    cols = [(560, 1.0, "VALLA BAJITA", "x1"), (1300, 2.0, "EL DOBLE DE ALTA", "x4")]
    for i, (cx, h, name, mult) in enumerate(cols):
        t0 = 0.3 if i == 0 else t2
        a = ease_out(prog(t, t0, 0.4))
        if a <= 0:
            continue
        hf = 110 * h
        x0 = cx - 330
        cv2.line(img, (x0 - 80, base), (x0 + 700, base), (90, 92, 94), 3, cv2.LINE_AA)
        cv2.line(img, (x0, base), (x0, int(base - hf * a)), (150, 110, 70), 10, cv2.LINE_AA)
        k = ease_io(prog(t, t0 + 0.4, 1.2))
        area = h * h  # ~ quadratic storage
        L = 240 * h * k
        xs = np.linspace(x0, x0 + max(L, 2), 60)
        u = (xs - x0) / max(L, 1)
        ys = base - hf * 1.1 * k * np.where(u < 0.2, 0.7 + 1.5 * u, (1 - u) ** 1.4 * 1.0)
        if L > 4:
            fill_poly(img, np.vstack([[x0, base], np.stack([xs, ys], 1), [x0 + L, base]]), SNOW)
        label(img, name, cx, base + 70, a, 46, WHITE)
        label(img, mult + " NIEVE", cx + 60, base - hf * 1.1 - 90, prog(t, t0 + 1.2, 0.3), 70 if i else 52,
              YELLOW if i else GREY)
    label(img, "DOBLE ALTURA  =  ~4 VECES MÁS NIEVE", W / 2, 170, prog(t, final_t, 0.4), 60, YELLOW)
    return img


# ------------------------------------------------------------------ wind accelerating around Elk Mountain
class FlowOverlay:
    """Wind past an isolated mountain (potential flow around a cylinder): streamlines with dashes that speed up
    where the flow squeezes past the obstacle. centre/radius in screen px; flow goes west->east."""

    def __init__(self, cx, cy, r, n=17, t0=0.0, label_text="EFECTO MANGUERA", span=None):
        self.cx, self.cy, self.r, self.t0, self.txt = cx, cy, r, t0, label_text
        span = span or (r * 3.4)
        self.lines = []
        for k, off in enumerate(np.linspace(-span, span, n)):
            if abs(off) < r * 0.12:
                off = math.copysign(r * 0.12, off if off else 1)
            p = np.array([-260.0, cy + off])
            pts = [p.copy()]
            for _ in range(2400):
                p = p + self._vel(p) * 4.0
                pts.append(p.copy())
                if p[0] > W + 260:
                    break
            self.lines.append(np.array(pts))

    def _vel(self, p):
        x, y = (p[0] - self.cx) / self.r, (p[1] - self.cy) / self.r
        r2 = max(x * x + y * y, 1.0)
        return np.array([1 - (x * x - y * y) / (r2 * r2), -2 * x * y / (r2 * r2)])

    def draw(self, img, t, dur):
        a = ease_out(prog(t, self.t0, 0.6)) * (1 - prog(t, dur - 0.4, 0.4))
        if a <= 0:
            return
        layer = img.copy()
        for i, pts in enumerate(self.lines):
            aa_poly(layer, pts[::6], (150, 165, 185), 1)
            n = len(pts)
            for j in range(6):
                head = int((t * 90 * 2.2 + j * n / 6 + i * 37) % n)
                tail = max(0, head - 22)
                seg = pts[tail:head + 1]
                if len(seg) < 2:
                    continue
                step = np.hypot(*(seg[-1] - seg[0])) / max(len(seg) - 1, 1) / 4.0
                k = clamp((step - 1.0) / 0.8)
                col = (int(lerp(205, 244, k)), int(lerp(220, 120, k)), int(lerp(235, 40, k)))
                aa_poly(layer, seg, col, 3 + int(3 * k))
        img[:] = cv2.addWeighted(layer, 0.85 * a, img, 1 - 0.85 * a, 0)
        if self.txt:
            label(img, self.txt, self.cx, self.cy - self.r * 1.9, a * prog(t, self.t0 + 1.0, 0.4), 50, YELLOW)


# ------------------------------------------------------------------ gust gauge
def gauge(img, t, dur, value=60, unit="MPH", sub="≈ 100 KM/H", cx=W * 0.5, cy=H * 0.58, r=300, t0=0.3):
    a = ease_out(prog(t, t0, 0.4))
    if a <= 0:
        return
    layer = img.copy()
    cv2.ellipse(layer, (int(cx), int(cy)), (r, r), 0, 180, 360, (40, 42, 46), 34, cv2.LINE_AA)
    k = ease_out(prog(t, t0 + 0.3, 1.4))
    jitter = math.sin(t * 23) * 2.0 * prog(t, t0 + 1.5, 0.2)
    ang = 180 + (value / 80.0) * 180 * k + jitter
    cv2.ellipse(layer, (int(cx), int(cy)), (r, r), 0, 180, ang, YELLOW if value < 55 else RED, 34, cv2.LINE_AA)
    for v in range(0, 81, 10):
        q = math.radians(180 + v / 80 * 180)
        cv2.line(layer, (int(cx + (r - 40) * math.cos(q)), int(cy + (r - 40) * math.sin(q))),
                 (int(cx + (r - 70) * math.cos(q)), int(cy + (r - 70) * math.sin(q))), WHITE, 3, cv2.LINE_AA)
    q = math.radians(ang)
    cv2.line(layer, (int(cx), int(cy)), (int(cx + (r - 60) * math.cos(q)), int(cy + (r - 60) * math.sin(q))), WHITE, 8,
             cv2.LINE_AA)
    cv2.circle(layer, (int(cx), int(cy)), 18, WHITE, -1, cv2.LINE_AA)
    img[:] = cv2.addWeighted(layer, a, img, 1 - a, 0)
    shown = int(round(value * k))
    label(img, f"{'+' if k > 0.98 else ''}{shown} {unit}", cx, cy + 90, a, 110, WHITE)
    label(img, sub, cx, cy + 180, a * prog(t, t0 + 1.4, 0.4), 50, YELLOW)


# ------------------------------------------------------------------ 4-day countdown (Oct 1970)
def countdown(t, dur, days=None, times=None, final_t=None, hi=None):
    days = days or [("SÁB", "3", "LA CINTA"), ("DOM", "4", "FAMILIAS"), ("LUN", "5", "TRÁILERES"),
                    ("MAR", "6", "TRÁILERES"), ("MIÉ", "7", "TORMENTA")]
    img = background("dark_grid", t)
    label(img, "OCTUBRE 1970", W / 2, 170, prog(t, 0.1, 0.4), 64, WHITE)
    n = len(days)
    cw, gap = 290, 34
    x0 = W / 2 - (n * cw + (n - 1) * gap) / 2
    step = max((dur - 1.6) / n, 0.5)
    for i, (dname, num, note) in enumerate(days):
        t0 = times[i] if times else 0.4 + i * step
        a = ease_out(prog(t, t0, 0.3))
        if a <= 0:
            continue
        last = i == n - 1
        x = x0 + i * (cw + gap)
        y = 330
        col = (34, 36, 40)
        card = rounded_rect_sprite(cw, 380, col, 12, 255, 3, RED if last and t > t0 + 0.4 else (80, 82, 86))
        over(img, card, x, y + 30 * (1 - a), a)
        label(img, dname, x + cw / 2, y + 60, a, 54, YELLOW if not last else RED)
        label(img, num, x + cw / 2, y + 185, a, 170, WHITE)
        label(img, note, x + cw / 2, y + 320, a * prog(t, t0 + 0.2, 0.3), 40, GREY if not last else RED)
    k = prog(t, final_t if final_t is not None else 0.4 + (n - 1) * step + 0.5, 0.3)
    if hi is not None and hi < n:
        x = x0 + hi * (cw + gap)
        pulse = 0.5 + 0.5 * math.sin(t * 5)
        cv2.rectangle(img, (int(x - 8), 322), (int(x + cw + 8), 718), YELLOW, 3 + int(3 * pulse))
    if k > 0:
        label(img, "CERRADA", W / 2, 860, ease_out(k), 120, RED)
    return img


# ------------------------------------------------------------------ 9 of 10 drivers survey
def survey(t, dur, big_t=3.2, sub_t=4.0):
    img = background("dark_grid", t)
    label(img, "¿TOMARÍA UN CAMINO MÁS CORTO?", W / 2, 200, prog(t, 0.2, 0.4), 60, WHITE)
    cw = 140
    x0 = W / 2 - (10 * cw + 9 * 26) / 2
    for i in range(10):
        a = ease_back(prog(t, 0.6 + i * 0.12, 0.3))
        if a <= 0:
            continue
        yes = i < 9
        on = t > big_t - 0.9 + i * 0.08
        col = YELLOW if (yes and on) else (110, 112, 116)
        x = x0 + i * (cw + 26) + cw / 2
        y = 520
        s = a
        body = np.array([[-60, 20], [-60, -10], [-38, -16], [-22, -46], [26, -46], [42, -16], [60, -10], [60, 20]],
                        np.float64) * s + [x, y]
        fill_poly(img, body, col)
        for wx in (-34, 34):
            cv2.circle(img, (int(x + wx * s), int(y + 22 * s)), int(15 * s), BLACK, -1, cv2.LINE_AA)
    k = prog(t, big_t, 0.4)
    label(img, "9 DE CADA 10: SÍ", W / 2, 720, ease_out(k), 96, YELLOW)
    label(img, "Y NO PENSABAN PARAR EN ROCK RIVER, MEDICINE BOW NI HANNA", W / 2, 830, prog(t, sub_t, 0.4), 40, WHITE)
    return img


# ------------------------------------------------------------------ truck queue: 8,000 trucks/day ≈ 100+ miles
def truck_queue(t, dur):
    img = background("dark_grid", t)
    y = 560
    cv2.rectangle(img, (80, y - 40), (W - 80, y + 40), (36, 37, 40), -1)
    for x in range(80, W - 80, 60):
        cv2.line(img, (x, y), (x + 30, y), (90, 90, 80), 3)
    k = ease_io(prog(t, 0.6, max(dur - 2.2, 1.5)))
    n = int(150 * k)
    for i in range(n):
        x = 100 + i * 11.3
        if x > W - 100:
            break
        cv2.rectangle(img, (int(x), y - 14), (int(x + 8), y + 14), YELLOW if i % 12 else WHITE, -1)
    # ruler
    cv2.line(img, (100, y + 110), (int(100 + (W - 200) * k), y + 110), WHITE, 3, cv2.LINE_AA)
    miles = 100 * k / 0.95
    label(img, f"{min(miles, 100):.0f} MILLAS" if k < 0.95 else "+100 MILLAS", 100 + (W - 200) * k, y + 170,
          prog(t, 0.6, 0.3), 54, WHITE)
    label(img, "8.000 CAMIONES AL DÍA", W / 2, 230, prog(t, 0.2, 0.4), 72, WHITE)
    label(img, "EN FILA: MÁS QUE TODO EL TRAMO CERRADO", W / 2, 310, prog(t, dur - 1.8, 0.4), 46, YELLOW)
    return img


# ------------------------------------------------------------------ closure gate arm over any frame
def gate_overlay(img, t, dur, t0=0.4, x=0.18, y=0.66, length=0.62):
    k = ease_io(prog(t, t0, 1.2))
    ang = lerp(-80, 0, k)
    px, py = W * x, H * y
    L = W * length
    q = math.radians(ang)
    ex, ey = px + L * math.cos(q), py + L * math.sin(q)
    nseg = 10
    for i in range(nseg):
        a0, a1 = i / nseg, (i + 1) / nseg
        p0 = (int(px + (ex - px) * a0), int(py + (ey - py) * a0))
        p1 = (int(px + (ex - px) * a1), int(py + (ey - py) * a1))
        cv2.line(img, p0, p1, RED if i % 2 == 0 else WHITE, 26, cv2.LINE_AA)
    cv2.rectangle(img, (int(px - 40), int(py - 40)), (int(px + 40), int(H)), (60, 60, 62), -1)
    on = (int(t * 2.5) % 2 == 0) and k > 0.5
    for dx in (-18, 18):
        cv2.circle(img, (int(px + dx), int(py - 70)), 16, RED if on else (80, 20, 24), -1, cv2.LINE_AA)
    if on:
        layer = img.copy()
        cv2.circle(layer, (int(px), int(py - 70)), 90, RED, -1, cv2.LINE_AA)
        img[:] = cv2.addWeighted(layer, 0.25, img, 0.75, 0)


# ------------------------------------------------------------------ phone group chat (truckers' radio advice)
def chat_overlay(img, t, dur, msgs, title="CAMIONEROS · I-80", x=0.62, t0=0.3, every=1.1):
    pw, ph = 600, 820
    px, py = W * x, (H - ph) / 2
    a = ease_out(prog(t, t0 - 0.2, 0.4))
    if a <= 0:
        return
    panel = rounded_rect_sprite(pw, ph, (24, 26, 30), 30, 235, 3, (70, 72, 76))
    over(img, panel, px, py, a)
    head = text_sprite(title, "sans_bold", 32, WHITE, False)
    over(img, head, px + 40, py + 20, a)
    cv2.line(img, (int(px + 30), int(py + 96)), (int(px + pw - 30), int(py + 96)), (70, 72, 76), 2)
    yy = py + 130
    for i, (who, txt) in enumerate(msgs):
        k = ease_out(prog(t, t0 + 0.3 + i * every, 0.3))
        if k <= 0:
            break
        body = text_sprite(txt, "sans_med", 30, WHITE, False)
        name = text_sprite(who, "sans_bold", 24, YELLOW, False)
        inner = max(body.w, name.w) - 48
        bw = min(pw - 60, inner + 44)
        bh = body.h + name.h - 64
        bub = rounded_rect_sprite(int(bw), int(bh), (44, 72, 60) if i % 2 else (52, 56, 64), 16, 255)
        dy = 20 * (1 - k)
        over(img, bub, px + 30, yy + dy, k)
        over(img, name, px + 30 + 22 - 24, yy - 14 + dy, k)
        over(img, body, px + 30 + 22 - 24, yy + name.h - 52 + dy, k)
        yy += bh + 22


# ------------------------------------------------------------------ typed document + signature (reconstruction)
def document(t, dur, lines, sign_t=2.0, footer="RECREACIÓN"):
    img = background("dark_grid", t)
    pw, ph = 1080, 960
    px, py = W / 2 - pw / 2, 60
    paper = rounded_rect_sprite(pw, ph, (232, 226, 210), 4, 255)
    sc = lerp(1.04, 1.0, ease_out(prog(t, 0, 1.0)))
    over_center(img, paper, W / 2, py + ph / 2, 1.0, sc)
    y = py + 80
    for i, (txt, size) in enumerate(lines):
        k = prog(t, 0.2 + i * 0.25, 0.35)
        n = int(len(txt) * k)
        if n <= 0:
            continue
        sp = text_sprite(txt[:n], "type", size, (30, 28, 26), False)
        over(img, sp, px + 80, y, 1.0)
        y += size + 30
    # signature as a scribble drawn over time
    k = ease_io(prog(t, sign_t, 1.2))
    if k > 0:
        xs = np.linspace(0, 1, 160)
        sig = np.stack([px + 560 + 360 * xs, py + ph - 210 - 34 * np.sin(xs * 23) * np.exp(-xs * 1.5) - 30 * xs], 1)
        aa_poly(img, partial_line(sig, k), (20, 30, 90), 4)
        cv2.line(img, (int(px + 540), int(py + ph - 160)), (int(px + 960), int(py + ph - 160)), (60, 58, 54), 2)
    if footer:
        label(img, footer, W - 150, H - 50, 0.8, 30, GREY)
    return img


# ------------------------------------------------------------------ stats panel
def stats_panel(t, dur, items, title=None):
    """items: list of (big_text, label, t0)."""
    img = background("dark_grid", t)
    if title:
        label(img, title, W / 2, 190, prog(t, 0.1, 0.4), 56, WHITE)
    n = len(items)
    cw = 520
    x0 = W / 2 - (n * cw) / 2
    for i, (big, lab, t0) in enumerate(items):
        a = ease_out(prog(t, t0, 0.35))
        if a <= 0:
            continue
        cx = x0 + i * cw + cw / 2
        sc = ease_back(prog(t, t0, 0.4))
        sp = text_sprite(big, "bebas", 210, YELLOW, True)
        over_center(img, sp, cx, 520, a, max(sc, 0.05))
        label(img, lab, cx, 690, a, 44, WHITE)
        if i:
            cv2.line(img, (int(x0 + i * cw), 400), (int(x0 + i * cw), 760), (70, 72, 76), 2)
    return img


# ------------------------------------------------------------------ straight line vs detour
def straight_vs_detour(t, dur):
    img = background("paper_grid", t)
    A, B = (300, 560), (1620, 560)
    k1 = ease_io(prog(t, 0.3, 0.9))
    xs = np.linspace(0, 1, 120)
    det = np.stack([A[0] + (B[0] - A[0]) * xs, 560 - 300 * np.sin(np.pi * xs) - 40 * np.sin(5 * np.pi * xs)], 1)
    k2 = ease_io(prog(t, 1.2, 1.2))
    aa_poly(img, partial_line(det, k2), (130, 128, 122), 6)
    aa_poly(img, partial_line(np.array([A, B], np.float64), k1), RED, 9)
    for p in (A, B):
        cv2.circle(img, p, 16, (30, 30, 30), -1, cv2.LINE_AA)
    label(img, "LÍNEA RECTA", W / 2, 625, prog(t, 0.8, 0.3), 60, RED, box=None)
    label(img, "RODEO", W / 2, 215, prog(t, 2.0, 0.3), 54, (110, 108, 104))
    label(img, "MÁS FÁCIL DE DEFENDER", W / 2, 760, prog(t, 2.6, 0.4), 52, (30, 30, 30))
    return img


# ------------------------------------------------------------------ cost comparison
def cost_compare(t, dur):
    img = background("dark_grid", t)
    for i, (yr, big, sub, col, t0) in enumerate([("1956", "YA ESTABA HECHA", "NO COSTABA NADA", WHITE, 0.2),
                                                   ("HOY", "≈ 6.000 MILLONES", "DE DÓLARES", YELLOW, 1.2)]):
        cx = W * (0.28 + 0.44 * i)
        a = ease_out(prog(t, t0, 0.4))
        label(img, yr, cx, 330, a, 90, GREY)
        label(img, big, cx, 520, a, 100 if i else 84, col)
        label(img, sub, cx, 640, a, 46, WHITE)
    cv2.line(img, (W // 2, 300), (W // 2, 700), (70, 72, 76), 2)
    return img


# ------------------------------------------------------------------ 1959 vs 1961 vs 1963 mini timeline
def lady_bird_timeline(t, dur):
    img = background("dark_grid", t)
    y = 560
    x0, x1 = 260, 1660
    k = ease_io(prog(t, 0.2, 1.0))
    cv2.line(img, (x0, y), (int(lerp(x0, x1, k)), y), (150, 152, 156), 4, cv2.LINE_AA)
    marks = [(1959, "TRAZADO APROBADO", YELLOW, 0.4), (1961, "LBJ, VICEPRESIDENTE", WHITE, 1.4), (1963, "LBJ, PRESIDENTE", WHITE, 2.2)]
    for yr, txt, col, t0 in marks:
        x = lerp(x0, x1, (yr - 1958) / 6.0)
        a = ease_out(prog(t, t0, 0.3))
        if a <= 0:
            continue
        cv2.circle(img, (int(x), y), int(18 * a), col, -1, cv2.LINE_AA)
        label(img, str(yr), x, y - 80, a, 80, col)
        label(img, txt, x, y + 80, a, 40, col)
    return img


# ------------------------------------------------------------------ phone frame (map seen on a phone)
def phone_overlay(img, t, dur, w=560, h=1000):
    a = ease_out(prog(t, 0.0, 0.5))
    cx, cy = W / 2, H / 2 + 20
    x0, y0, x1, y1 = int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2)
    mask = np.zeros((H, W), np.uint8)
    cv2.rectangle(mask, (x0, y0), (x1, y1), 255, -1)
    dark = (img * 0.25).astype(np.uint8)
    out = np.where(mask[..., None] > 0, img, dark)
    img[:] = (img * (1 - a) + out * a).astype(np.uint8)
    cv2.rectangle(img, (x0 - 14, y0 - 14), (x1 + 14, y1 + 14), (20, 20, 22), 22, cv2.LINE_AA)
    cv2.rectangle(img, (int(cx - 70), y0 - 6), (int(cx + 70), y0 + 14), (20, 20, 22), -1)
