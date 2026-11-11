"""Extra effects for the spray tan reel, on top of engine.py (SLATE graphic line):
frosted-glass cards (reference style), calendar animation, festive particles, zoom-blur transitions."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from engine import *

def rounded_mask(w, h, r):
    m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (r, 0), (w - r, h), 255, -1); cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
    for cx, cy in [(r, r), (w - r - 1, r), (r, h - r - 1), (w - r - 1, h - r - 1)]:
        cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    return m.astype(np.float32) / 255.0

def ring_mask(w, h, r, th=2):
    a = rounded_mask(w, h, r)
    b = np.zeros_like(a); inner = rounded_mask(w - 2 * th, h - 2 * th, max(1, r - th)); b[th:h - th, th:w - th] = inner
    return np.clip(a - b, 0, 1)

def glass(frame, x, y, w, h, r=36, a=1.0, tint=0.16, blur_r=22, border=0.55, shadow=0.25, warm=(1.0, 0.985, 0.96)):
    """Frosted glass panel drawn in place: blurred backdrop + white tint + thin bright border + soft shadow."""
    if a <= 0.01: return
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0: return
    m = rounded_mask(w, h, r)[y0 - y:y1 - y, x0 - x:x1 - x][..., None] * a
    # soft drop shadow under the card
    if shadow > 0:
        pad = 40; sm = np.zeros((h + 2 * pad, w + 2 * pad), np.float32)
        sm[pad:pad + h, pad:pad + w] = rounded_mask(w, h, r)
        sm = blur(sm, 18) * shadow * a
        composite(frame, solid_layer(sm, "#000000", x - pad, y - pad + 10))
    reg = frame[y0:y1, x0:x1]
    # blur a slightly larger area for natural edges
    gx0, gy0, gx1, gy1 = max(0, x0 - 40), max(0, y0 - 40), min(W, x1 + 40), min(H, y1 + 40)
    big = frame[gy0:gy1, gx0:gx1]
    small = cv2.resize(big, (max(1, big.shape[1] // 4), max(1, big.shape[0] // 4)), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), blur_r / 4)
    bl = cv2.resize(small, (big.shape[1], big.shape[0]), interpolation=cv2.INTER_LINEAR)[y0 - gy0:y1 - gy0, x0 - gx0:x1 - gx0]
    bl = bl * (1 - tint) + np.array(warm, np.float32) * tint
    reg[:] = reg * (1 - m) + bl * m
    bm = ring_mask(w, h, r, 2)[y0 - y:y1 - y, x0 - x:x1 - x] * border * a
    composite(frame, solid_layer(bm, "#FFFFFF", x0, y0))

def text_layers_at(text, fspec, size, cx, cy, color="#FFFFFF", tracking=0.0, alpha=1.0, glow=False, shadow=True):
    f = font(fspec[0], size, fspec[1])
    m, _, _ = text_mask(text, f, tracking_px=tracking * size, pad=24)
    x = cx - m.shape[1] / 2; y = cy - m.shape[0] / 2
    if glow:
        ls = glow_text(m, color, x, y, glow_sigma=30, glow_gain=1.6, glow_op=0.8)
    elif shadow:
        ls = with_shadow(m, color, x, y, sh_r=6, sh_op=0.45)
    else:
        ls = [solid_layer(m, color, x, y)]
    return [Layer(l.rgb, l.alpha * alpha, l.x, l.y) for l in ls]

class GlassPill:
    """Frosted glass pill with a caps label (like the reference's floating UI cards). Pops in with overshoot."""
    def __init__(self, text, t0, t1, cx, cy, size=40, fspec=COND, tracking=0.12, padx=46, h=None, color="#FFFFFF"):
        self.text, self.t0, self.t1, self.cx, self.cy = text, t0, t1, cx, cy
        self.size, self.fspec, self.tr, self.color = size, fspec, tracking, color
        f = font(fspec[0], size, fspec[1])
        self.tw = f.getlength(text) + tracking * size * (len(text) - 1)
        self.w = int(self.tw + 2 * padx); self.h = h or int(size * 1.9)

    def apply(self, frame, t):
        if t < self.t0 or t >= self.t1: return
        lt = t - self.t0
        u = clamp01(lt / 0.32); s = 1 + 0.10 * math.sin(math.pi * u) * (1 - u) if u < 1 else 1.0
        a = ease_out(lt / 0.18) * (1 - clamp01((t - (self.t1 - 0.15)) / 0.15))
        sc = 0.82 + 0.18 * ease_out(u) * s
        w, h = int(self.w * sc), int(self.h * sc)
        glass(frame, self.cx - w / 2, self.cy - h / 2, w, h, r=h // 2, a=a)
        for l in text_layers_at(self.text, self.fspec, self.size * sc, self.cx, self.cy + 1, self.color, self.tr, a, shadow=False):
            composite(frame, l)

class CalendarCard:
    """Glass calendar: a week row pops in, the event day gets a ring, then two days before it gets
    filled 'BOOK' and an arc arrow draws from BOOK to EVENT."""
    def __init__(self, t0, t1, cx, cy, w=820, h=470, month="DECEMBER", start_day=18, event_idx=5, book_idx=3,
                 ev_label="EVENT", bk_label="BOOK", arrow_label="2 DAYS"):
        self.labels = (ev_label, bk_label, arrow_label)
        self.t0, self.t1, self.cx, self.cy, self.w, self.h = t0, t1, cx, cy, w, h
        self.month, self.d0, self.ev, self.bk = month, start_day, event_idx, book_idx

    def apply(self, frame, t):
        if t < self.t0 or t >= self.t1: return
        lt = t - self.t0
        a = ease_out(lt / 0.25) * (1 - clamp01((t - (self.t1 - 0.18)) / 0.18))
        rise = (1 - ease_out(lt / 0.35)) * 60
        x, y = self.cx - self.w / 2, self.cy - self.h / 2 + rise
        glass(frame, x, y, self.w, self.h, r=44, a=a, tint=0.20)
        # header
        for l in text_layers_at(self.month, COND, 44, self.cx, y + 62, "#FFFFFF", 0.22, a, shadow=False):
            composite(frame, l)
        L = np.zeros((self.h, self.w), np.float32)
        cv2.line(L, (60, 108), (self.w - 60, 108), 0.5, 2, cv2.LINE_AA)
        composite(frame, solid_layer(L * a, "#FFFFFF", x, y))
        days = ["M", "T", "W", "T", "F", "S", "S"]
        colw = (self.w - 80) / 7
        for i in range(7):
            ci = clamp01((lt - 0.10 - i * 0.045) / 0.18)
            if ci <= 0: continue
            cxi = x + 40 + colw * (i + 0.5)
            for l in text_layers_at(days[i], CAPF, 26, cxi, y + 150, "#FFFFFF", 0, a * ci * 0.75, shadow=False):
                composite(frame, l)
            for l in text_layers_at(str(self.d0 + i), CAPF, 46 * (0.8 + 0.2 * ease_out(ci)), cxi, y + 232, "#FFFFFF", -0.02, a * ci, shadow=False):
                composite(frame, l)
        # event ring (draws on) + label
        ev_x = x + 40 + colw * (self.ev + 0.5); bk_x = x + 40 + colw * (self.bk + 0.5); cy = y + 232
        ue = clamp01((lt - 0.55) / 0.35)
        if ue > 0:
            R = np.zeros((self.h, self.w), np.float32)
            cv2.ellipse(R, (int(ev_x - x), int(cy - y)), (44, 44), -90, 0, 360 * ease_out(ue), 1.0, 3, cv2.LINE_AA)
            composite(frame, solid_layer(R * a, "#FFFFFF", x, y))
            for l in text_layers_at(self.labels[0], COND, 28, ev_x, y + 318, "#FFFFFF", 0.16, a * ease_out(ue), shadow=False):
                composite(frame, l)
        # book day: filled disc pops, label BOOK
        ub = clamp01((lt - 0.95) / 0.25)
        if ub > 0:
            s = ease_out(ub) * (1 + 0.15 * math.sin(math.pi * ub) * (1 - ub))
            D = np.zeros((self.h, self.w), np.float32)
            cv2.circle(D, (int(bk_x - x), int(cy - y)), max(1, int(44 * s)), 1.0, -1, cv2.LINE_AA)
            composite(frame, solid_layer(D * a * 0.95, "#FFF8EE", x, y))
            for l in text_layers_at(str(self.d0 + self.bk), CAPF, 46, bk_x, cy, "#2A2420", -0.02, a * ease_out(ub), shadow=False):
                composite(frame, l)
            for l in text_layers_at(self.labels[1], COND, 28, bk_x, y + 318, "#FFFFFF", 0.16, a * ease_out(ub), shadow=False):
                composite(frame, l)
        # arc arrow BOOK -> EVENT
        ua = clamp01((lt - 1.20) / 0.40)
        if ua > 0:
            A = np.zeros((self.h, self.w), np.float32)
            p0 = np.array([bk_x - x, cy - y + 62 + 40]); p2 = np.array([ev_x - x, cy - y + 62 + 40]); p1 = (p0 + p2) / 2 + np.array([0, 55])
            n = 40; k = max(2, int(n * ease_out(ua)))
            pts = [((1 - s) ** 2) * p0 + 2 * (1 - s) * s * p1 + (s ** 2) * p2 for s in np.linspace(0, ease_out(ua), k)]
            pts = np.array(pts, np.int32)
            cv2.polylines(A, [pts], False, 0.9, 3, cv2.LINE_AA)
            if ua > 0.9:
                tip = pts[-1]; d = pts[-1] - pts[-4]; d = d / (np.linalg.norm(d) + 1e-6)
                nrm = np.array([-d[1], d[0]])
                for sgn in (1, -1):
                    q = tip - d * 16 + nrm * 9 * sgn
                    cv2.line(A, tuple(int(v) for v in tip), tuple(int(v) for v in q), 0.9, 3, cv2.LINE_AA)
            composite(frame, solid_layer(A * a, "#FFFFFF", x, y))
            for l in text_layers_at(self.labels[2], COND, 30, (bk_x + ev_x) / 2, y + 415, "#FFFFFF", 0.18, a * ease_out(ua), shadow=False):
                composite(frame, l)

class Particles:
    """Subtle festive particles. kind: 'leaves' (autumn, drifting down), 'snow' (soft flakes + warm bokeh),
    'confetti' (gold flecks bursting then falling)."""
    def __init__(self, kind, t0, t1, n=26, seed=0, opacity=0.85):
        self.kind, self.t0, self.t1, self.op = kind, t0, t1, opacity
        rng = np.random.default_rng(seed)
        self.p = dict(x=rng.uniform(0, W, n), y=rng.uniform(-0.25 * H, 0.9 * H, n), s=rng.uniform(0.6, 1.4, n),
                      ph=rng.uniform(0, 6.28, n), sp=rng.uniform(0.6, 1.3, n), rot=rng.uniform(0, 6.28, n),
                      c=rng.integers(0, 3, n), vx=rng.normal(0, 1, n), vy=rng.uniform(0.3, 1.0, n), z=rng.uniform(0.5, 1.0, n))
        self.n = n

    def layers(self, t):
        if t < self.t0 or t >= self.t1: return []
        lt = t - self.t0; p = self.p
        fade = ease_out(lt / 0.35) * (1 - clamp01((t - (self.t1 - 0.25)) / 0.25)) * self.op
        if self.kind == "leaves":
            cols = ["#C8742C", "#B4532A", "#D9A441"]
            L = np.zeros((H, W, 3), np.float32); A = np.zeros((H, W), np.float32)
            for i in range(self.n):
                x = p["x"][i] + 60 * math.sin(p["ph"][i] + lt * 1.6 * p["sp"][i]) + 40 * p["vx"][i] * lt
                y = p["y"][i] + 260 * p["sp"][i] * lt
                if not (-60 < x < W + 60 and -60 < y < H + 60): continue
                s = 34 * p["s"][i]; ang = p["rot"][i] + lt * 2.2 * p["sp"][i]
                pts = []
                for k in range(16):  # leaf: pointed ellipse
                    th = 2 * math.pi * k / 16; rr = s * (0.55 + 0.45 * abs(math.cos(th)))
                    px, py = rr * math.cos(th), 0.45 * s * math.sin(th)
                    pts.append([x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)])
                m = np.zeros((H, W), np.uint8)
                cv2.fillPoly(m, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
                c = np.array(hex2rgb(cols[p["c"][i]]), np.float32) / 255
                mm = m.astype(np.float32) / 255 * (0.55 + 0.35 * p["z"][i])
                L += mm[..., None] * c; A = np.maximum(A, mm)
            A = blur(A, 0.8)
            rgb = np.where(A[..., None] > 0, L / np.maximum(A[..., None], 1e-3) * np.minimum(A[..., None], 1), 0)
            return [Layer(np.clip(rgb, 0, 1), A * fade, 0, 0)]
        if self.kind == "snow":
            S = np.zeros((H, W), np.float32); B = np.zeros((H, W), np.float32)
            for i in range(self.n):
                x = (p["x"][i] + 30 * math.sin(p["ph"][i] + lt * 1.2)) % W
                y = (p["y"][i] + 150 * p["vy"][i] * lt) % (H * 1.1)
                cv2.circle(S, (int(x), int(y)), max(2, int(6.5 * p["s"][i] * p["z"][i])), float(0.7 + 0.3 * p["z"][i]), -1, cv2.LINE_AA)
                if i % 3 == 0:  # warm bokeh lights near the top
                    bx = (p["x"][i] * 1.7) % W; by = (p["y"][i] * 0.35) % (0.35 * H)
                    tw = 0.5 + 0.5 * math.sin(p["ph"][i] + lt * 3)
                    cv2.circle(B, (int(bx), int(by)), int(22 * p["s"][i]), float(0.35 * tw), -1, cv2.LINE_AA)
            S = np.clip(blur(S, 1.8) * 1.3, 0, 1); G = blur(S, 7) * 0.6; B = blur(B, 10)
            return [solid_layer(B * fade, "#FFD9A0", 0, 0), solid_layer(np.clip(G, 0, 1) * fade * 0.8, "#000000", 0, 2), solid_layer(S * fade, "#FFFFFF", 0, 0)]
        if self.kind == "confetti":
            cols = ["#E8C77A", "#F5E6C4", "#D4A64A"]
            C = np.zeros((H, W, 3), np.float32); A = np.zeros((H, W), np.float32)
            for i in range(self.n):
                # burst from upper centre, then gravity
                ang = p["ph"][i]; v0 = 900 * p["sp"][i]
                x = W / 2 + math.cos(ang) * v0 * 1.6 * min(lt, 0.5) * (1 - min(lt, 0.5)) + 60 * p["vx"][i] * lt
                y = 0.13 * H + math.sin(ang) * v0 * 0.5 * min(lt, 0.5) * (1 - min(lt, 0.5)) + 260 * max(0, lt - 0.25) ** 1.4
                if not (0 < x < W and 0 < y < H): continue
                w2, h2 = 9 * p["s"][i], 4 * p["s"][i] * abs(math.sin(p["rot"][i] + lt * 8))+1
                ang2 = p["rot"][i] + lt * 5
                box = cv2.boxPoints(((x, y), (w2 * 2, h2 * 2), math.degrees(ang2))).astype(np.int32)
                m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [box], 255, cv2.LINE_AA)
                mm = m.astype(np.float32) / 255
                c = np.array(hex2rgb(cols[p["c"][i]]), np.float32) / 255
                C += mm[..., None] * c; A = np.maximum(A, mm)
            rgb = np.where(A[..., None] > 0, C / np.maximum(A[..., None], 1e-3) * np.minimum(A[..., None], 1), 0)
            glow = blur(A, 6) * 0.35
            return [solid_layer(glow * fade, "#FFE7B0", 0, 0), Layer(np.clip(rgb, 0, 1), A * fade, 0, 0)]
        return []

def zoom_blur(frame, amount, cx=0.5, cy=0.5, n=8):
    """Radial zoom blur (reference transition). amount ~0..0.25 = max extra scale."""
    if amount <= 0.002: return frame
    acc = np.zeros_like(frame)
    for k in range(n):
        s = 1 + amount * k / (n - 1)
        M = np.array([[s, 0, (1 - s) * cx * W], [0, s, (1 - s) * cy * H]], np.float32)
        acc += cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / n

class ZoomTransition:
    """Zoom-blur + slight push around a cut at time tc (half-duration d)."""
    def __init__(self, tc, d=0.16, amount=0.22):
        self.tc, self.d, self.amount = tc, d, amount

    def post(self, frame, t):
        u = 1 - abs(t - self.tc) / self.d
        if u <= 0: return frame
        a = self.amount * (u ** 1.5)
        s = 1 + 0.08 * (u ** 2)
        M = np.array([[s, 0, (1 - s) * W / 2], [0, s, (1 - s) * H / 2]], np.float32)
        f = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return zoom_blur(f, a)

class Flash:
    """Soft white flash peaking at tc (used under a few title hits)."""
    def __init__(self, tc, d=0.10, peak=0.35):
        self.tc, self.d, self.peak = tc, d, peak

    def post(self, frame, t):
        u = 1 - abs(t - self.tc) / self.d
        if u <= 0: return frame
        a = self.peak * u * u
        return frame * (1 - a) + a
