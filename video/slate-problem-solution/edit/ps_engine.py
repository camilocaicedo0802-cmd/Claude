"""Problem vs Solution effects on top of st_engine/engine (SLATE graphic line). No emojis: icons are drawn."""
import math, numpy as np, cv2
from st_engine import *

WARM = "#F6D9B0"          # solution accent (light caramel / tan)

def star_mask(size, points=4, inner=0.38, rot=0.0):
    """Filled n-point star (4 = sparkle), antialiased, in a size x size float mask."""
    s = int(size * 4); m = np.zeros((s, s), np.uint8); c = s / 2; R = s * 0.48
    pts = []
    for k in range(points * 2):
        r = R if k % 2 == 0 else R * inner
        a = rot + math.pi * k / points - math.pi / 2
        pts.append([c + r * math.cos(a), c + r * math.sin(a)])
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (size, size), interpolation=cv2.INTER_AREA)

class LabelPill:
    """Small glass pill label (PROBLEM / SOLUTION) with an optional drawn icon; pops in with overshoot."""
    def __init__(self, text, t0, t1, cx, cy, icon=None, warm=False, size=34):
        self.text, self.t0, self.t1, self.cx, self.cy, self.icon, self.warm, self.size = text, t0, t1, cx, cy, icon, warm, size
        f = font(COND[0], size, COND[1]); self.tw = f.getlength(text) + 0.24 * size * (len(text) - 1)
        self.iw = int(size * 0.95) if icon else 0
        self.w = int(self.tw + self.iw + (14 if icon else 0) + 64); self.h = int(size * 1.9)

    def apply(self, frame, t):
        if t < self.t0 or t >= self.t1: return
        lt = t - self.t0; u = clamp01(lt / 0.30)
        sc = 0.75 + 0.25 * ease_out(u) + 0.08 * math.sin(math.pi * u) * (1 - u)
        a = ease_out(lt / 0.15) * (1 - clamp01((t - (self.t1 - 0.12)) / 0.12))
        w, h = int(self.w * sc), int(self.h * sc)
        tint = 0.30 if self.warm else 0.18
        warmc = (1.0, 0.90, 0.78) if self.warm else (1.0, 0.985, 0.96)
        glass(frame, self.cx - w / 2, self.cy - h / 2, w, h, r=h // 2, a=a, tint=tint, warm=warmc, border=0.6)
        x0 = self.cx - (self.tw + self.iw + (14 if self.icon else 0)) * sc / 2
        if self.icon == "star":
            spin = (1 - ease_out(clamp01(lt / 0.5))) * 1.2
            m = star_mask(max(4, int(self.iw * sc)), 4, 0.36, spin)
            composite(frame, solid_layer(m * a, "#FFFFFF", x0, self.cy - m.shape[0] / 2))
        elif self.icon == "q":
            m = np.zeros((int(self.iw * sc), int(self.iw * sc)), np.float32); r = m.shape[0] // 2
            cv2.circle(m, (r, r), r - 2, 1.0, 2, cv2.LINE_AA)
            composite(frame, solid_layer(m * a, "#FFFFFF", x0, self.cy - r))
            for l in text_layers_at("?", COND, self.size * 0.8 * sc, x0 + r, self.cy + 1, "#FFFFFF", 0, a, shadow=False):
                composite(frame, l)
        tx = x0 + ((self.iw + 14) * sc if self.icon else 0) + self.tw * sc / 2
        for l in text_layers_at(self.text, COND, self.size * sc, tx, self.cy + 1, "#FFFFFF", 0.24, a, shadow=False):
            composite(frame, l)

class ProblemCard:
    """Frosted glass card with the problem typed in serif italic (one or two lines). Slides down + pops in."""
    def __init__(self, lines, t0, t1, cy, size=74, cps=30.0):
        self.lines, self.t0, self.t1, self.cy, self.size = lines, t0, t1, cy, size
        f = font(SERIF[0], size, SERIF[1])
        self.lw = [f.getlength(s) for s in lines]
        self.w = int(min(W - 90, max(self.lw) + 110)); self.lh = int(size * 1.12)
        self.h = int(self.lh * len(lines) + 70)
        self.label = LabelPill("PROBLEM", t0, t1, W / 2, cy - self.h / 2, icon="q", warm=False, size=30)
        n0 = 0; self.typers = []
        for i, s in enumerate(lines):
            ts = t0 + 0.12 + n0 / cps
            y = cy - (len(lines) - 1) * self.lh / 2 + i * self.lh + 8
            self.typers.append(TypeLine(s, ts, t1, cx=W / 2, cy=y, size=size, cps=cps))
            n0 += len(s)

    def apply(self, frame, t):
        if t < self.t0 or t >= self.t1: return
        lt = t - self.t0; u = ease_out(lt / 0.28)
        a = ease_out(lt / 0.16) * (1 - clamp01((t - (self.t1 - 0.12)) / 0.12))
        dy = (1 - u) * -40; sc = 0.92 + 0.08 * u
        w, h = int(self.w * sc), int(self.h * sc)
        glass(frame, W / 2 - w / 2, self.cy - h / 2 + dy, w, h, r=40, a=a, tint=0.14, blur_r=26, border=0.5)
        for tl in self.typers:
            for l in tl.layers(t):
                composite(frame, Layer(l.rgb, l.alpha * a, l.x, int(l.y + dy)))
        self.label.apply(frame, t)

class Twinkles:
    """A few cute 4-point stars popping and twinkling around a rectangle (cx, cy, w, h)."""
    def __init__(self, t0, t1, cx, cy, w, h, n=6, seed=0, color="#FFFFFF", maxsize=34):
        self.t0, self.t1 = t0, t1; rng = np.random.default_rng(seed)
        side = rng.integers(0, 4, n); u = rng.uniform(0, 1, n)
        xs = np.where(side == 0, cx - w / 2 - rng.uniform(10, 40, n), np.where(side == 1, cx + w / 2 + rng.uniform(10, 40, n), cx - w / 2 + u * w))
        ys = np.where(side == 2, cy - h / 2 - rng.uniform(5, 30, n), np.where(side == 3, cy + h / 2 + rng.uniform(5, 30, n), cy - h / 2 + u * h))
        self.p = dict(x=xs, y=ys, s=rng.uniform(0.45, 1.0, n) * maxsize, d=rng.uniform(0.05, 0.45, n), ph=rng.uniform(0, 6.28, n), rot=rng.uniform(-0.3, 0.3, n))
        self.n, self.color = n, color

    def layers(self, t):
        if t < self.t0 or t >= self.t1: return []
        lt = t - self.t0; out = []
        fade = 1 - clamp01((t - (self.t1 - 0.15)) / 0.15)
        for i in range(self.n):
            u = clamp01((lt - self.p["d"][i]) / 0.25)
            if u <= 0: continue
            pop = ease_out(u) * (1 + 0.35 * math.sin(math.pi * u) * (1 - u))
            tw = 0.65 + 0.35 * math.sin(self.p["ph"][i] + lt * 7)
            sz = max(4, int(self.p["s"][i] * pop * (0.85 + 0.15 * tw)))
            m = star_mask(sz, 4, 0.30, self.p["rot"][i] + lt * 0.6)
            g = blur(np.pad(m, 8), 3) * 0.6
            x, y = self.p["x"][i] - sz / 2, self.p["y"][i] - sz / 2
            out.append(solid_layer(g * fade * tw, "#FFF2D8", x - 8, y - 8))
            out.append(solid_layer(m * fade * min(1, tw + 0.2), self.color, x, y))
        return out

class SolutionTitle:
    """SOLUTION pill + warm sparkle title (+ optional serif sub-line) + twinkle stars."""
    def __init__(self, lines, t0, t1, cy=0.150 * H, size=118, sub=None, sub_size=86, sub_t=None, seed=0, pill_cy=0.072 * H):
        self.pill = LabelPill("SOLUTION", t0, t1, W / 2, pill_cy, icon="star", warm=True, size=30)
        self.title = SparkleTitle(lines, t0 + 0.10, t1, cy=cy, size=size, color=WARM, dur=0.36, seed=seed + 3)
        nl = len(lines); th = size * (0.92 * 1.25 * (nl - 1) + 0.9)
        self.sub = None
        if sub:
            fs = font(SERIF[0], 100, SERIF[1]); sub_size = min(sub_size, 100 * (W - 150) / fs.getlength(sub))
            self.sub = TypeLine(sub, sub_t or (t0 + 0.45), t1, cx=W / 2, cy=cy + size * 1.25 + (nl - 1) * size * 0.575, size=sub_size)
        f = font(COND[0], size, COND[1]); tw = max(f.getlength(s) for s in lines) * 0.94
        self.stars = Twinkles(t0 + 0.30, t1, W / 2, cy, tw + 30, th + 10, n=5, seed=seed)

    def apply(self, frame, t):
        self.pill.apply(frame, t)
        for o in (self.title, self.sub, self.stars):
            if o is None: continue
            for l in o.layers(t): composite(frame, l)

class WhipTransition:
    """Fast horizontal whip-pan around a cut: outgoing frame slides left with motion blur, incoming arrives from the right."""
    def __init__(self, tc, d=0.12, dist=0.45):
        self.tc, self.d, self.dist = tc, d, dist

    def post(self, frame, t):
        u = (t - self.tc) / self.d
        if abs(u) >= 1: return frame
        k = (1 - abs(u)) ** 1.6
        shift = -self.dist * W * (1 - abs(u)) ** 2.2 if u < 0 else self.dist * W * (1 - abs(u)) ** 2.2
        M = np.array([[1, 0, shift], [0, 1, 0]], np.float32)
        f = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        L = max(3, int(80 * k)) | 1                       # motion-blur length at half resolution
        small = cv2.resize(f, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
        small = cv2.blur(small, (L, 1))
        return cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)

class LabeledCalendar(CalendarCard):
    """CalendarCard with custom labels (event / book / arrow)."""
    def __init__(self, *a, ev_label="EVENT", bk_label="BOOK", arrow_label="2 DAYS", **k):
        super().__init__(*a, **k); self.labels = (ev_label, bk_label, arrow_label)

    def apply(self, frame, t):
        import st_engine as SE
        orig = SE.text_layers_at
        ev, bk, ar = self.labels
        def patched(text, *aa, **kk):
            text = {"EVENT": ev, "BOOK": bk, "2 DAYS": ar}.get(text, text)
            return orig(text, *aa, **kk)
        SE.text_layers_at = patched
        try:
            super().apply(frame, t)
        finally:
            SE.text_layers_at = orig
