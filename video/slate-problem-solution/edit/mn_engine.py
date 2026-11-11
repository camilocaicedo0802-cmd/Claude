"""Minimal SLATE line (reel 3 v4). Same fonts (Poppins + Playfair Display Italic), flat colour, no glow;
only a faint shadow for legibility. Text moves in with short slides (CapCut 'minimal' vocabulary: slide/wipe),
sizes play against each other (R2), single-word captions (R1/R3), numbered items with a progress row (R1),
one person cut-out 'sticker' moment (R3). Safe zone (client's 'Margen seguro.png'): x 50-1027, y 212-1547,
and x <= 920 below y 1117."""
import math, numpy as np, cv2
from engine import *

SAFE = dict(x0=50, x1=1027, y0=212, y1=1547, xr_low=920, y_low=1117)
WHITE, CREAM = "#FFFFFF", "#F7EEE3"
STY = {   # style -> (font file, weight, size, sx, colour, tracking)
    "s": ("Poppins-SemiBold.ttf", None, 50, 1.0, WHITE, 0.0),
    "m": ("Poppins-Medium.ttf", None, 52, 1.0, WHITE, 0.0),
    "b": ("Poppins-Bold.ttf", None, 104, 1.0, WHITE, -0.02),
    "B": ("Poppins-Bold.ttf", None, 230, 1.0, WHITE, -0.04),
    "n": ("Poppins-Bold.ttf", None, 128, 1.0, WHITE, -0.02),
    "p": ("PlayfairDisplay-Italic[wght].ttf", 500, 124, 0.92, CREAM, 0.0),
    "P": ("PlayfairDisplay-Italic[wght].ttf", 500, 150, 0.92, CREAM, 0.0),
    "c": ("Poppins-SemiBold.ttf", None, 58, 1.0, WHITE, -0.01),           # caption
    "ce": ("PlayfairDisplay-Italic[wght].ttf", 500, 96, 0.92, CREAM, 0.0),  # caption emphasis
}

def tmask(text, st, scale=1.0):
    f, w, size, sx, col, tr = STY[st]
    size = size * scale
    ft = font(f, size, w)
    m, base, _ = text_mask(text, ft, tracking_px=tr * size, pad=24, sx=sx)
    asc, desc = ft.getmetrics()
    bb = ft.getbbox("H")
    return m, base, col, (bb[3] - bb[1])          # mask, baseline (in mask px), colour, cap height

def flat(m, col, x, y, a=1.0, shadow=0.18):
    """Flat text: a barely-there soft shadow for legibility, nothing else."""
    out = []
    if shadow > 0:
        pad = 18; s = blur(np.pad(m, pad), 6) * shadow * a
        out.append(solid_layer(s, "#000000", x - pad, y - pad + 2))
    out.append(solid_layer(m * a, col, x, y))
    return out

def slide_in(m, u, dist=34):
    """Slide-up entrance with a touch of vertical motion blur while moving. Returns (mask, dy, alpha)."""
    e = ease_out(u); dy = dist * (1 - e); a = clamp01(u / 0.55)
    if u < 0.9:
        k = int(10 * (1 - u)) * 2 + 1
        if k > 2: m = cv2.blur(m, (1, k))
    return m, dy, a

class Block:
    """R2-style kinetic block: rows of (text, style) tokens, left-aligned, anchored at its bottom-left (x, y_bottom).
    Each token slides up at its own time. Optional underline under one row, drawn left->right (wipe)."""
    def __init__(self, rows, times, t_out, x=90, y_bottom=1500, underline=None, d_out=0.16, align="left", max_w=830):
        self.t_out, self.d_out = t_out, d_out
        self.items = []
        scale = 1.0
        for _ in range(6):                          # auto-fit: shrink the whole block until it fits max_w
            info = []; k = 0
            for row in rows:
                toks = []
                for (text, st) in row:
                    m, base, col, cap = tmask(text, st, scale); toks.append((m, base, col, cap, st, times[k])); k += 1
                gap = 22 * scale
                w = sum(t[0].shape[1] - 48 for t in toks) + gap * (len(toks) - 1)
                cap = max(t[3] for t in toks)
                info.append((toks, w, cap, gap))
            mw = max(r[1] for r in info)
            if mw <= max_w: break
            scale *= max(0.75, max_w / mw * 0.99)
        self.scale = scale
        # stack rows bottom-up with leading proportional to the larger cap height of adjacent rows
        ul_row = underline[0] if underline is not None else -1
        ys = []; yb = y_bottom
        for i in range(len(info) - 1, -1, -1):
            ys.insert(0, yb)
            if i > 0:
                yb -= info[i][2] + 0.32 * info[i - 1][2] + 16          # tight baseline-to-baseline leading
                if i - 1 == ul_row: yb -= 30                          # room for the underline below row i-1
        maxw = max(r[1] for r in info)
        self.bounds = (x, ys[0] - info[0][2], x + maxw, y_bottom)
        for ri, ((toks, w, cap, gap), yb) in enumerate(zip(info, ys)):
            xx = x if align == "left" else (x + (maxw - w) / 2 if align == "center" else x + maxw - w)
            for (m, base, col, c, st, ton) in toks:
                self.items.append(dict(m=m, x=xx - 24, y=yb - base, col=col, t=ton))
                xx += m.shape[1] - 48 + gap
        self.ul = None
        if underline is not None:
            ri, t_draw = underline
            toks, w, cap, gap = info[ri]
            xx = x if align == "left" else (x + (maxw - w) / 2 if align == "center" else x + maxw - w)
            self.ul = (xx, ys[ri] + 18, w, t_draw)

    def layers(self, t):
        if t >= self.t_out + self.d_out: return []
        u_out = clamp01((t - self.t_out) / self.d_out); ao = 1 - u_out; dyo = -22 * ease_inout(u_out)
        out = []
        for it in self.items:
            if t < it["t"]: continue
            m, dy, a = slide_in(it["m"], clamp01((t - it["t"]) / 0.24))
            out += flat(m, it["col"], it["x"], it["y"] + dy + dyo, a * ao)
        if self.ul and t >= self.ul[3]:
            x, y, w, td = self.ul; u = ease_out(clamp01((t - td) / 0.30))
            L = np.zeros((10, int(w) + 4), np.float32)
            cv2.line(L, (2, 5), (2 + int(w * u), 5), 1.0, 4, cv2.LINE_AA)
            out += flat(L, CREAM, x - 2, y + dyo, ao, shadow=0.12)
        return out

class NumberTitle:
    """R1-style numbered item: big number, label rows beside it (word by word with the voice), progress row of dots."""
    def __init__(self, n, total, rows, times, t_on, t_out, x=90, y_bottom=1455, d_out=0.16):
        self.n, self.total, self.t_on, self.t_out, self.d_out = n, total, t_on, t_out, d_out
        self.num, nb, ncol, ncap = tmask(f"{n}.", "n")
        self.nx = x - 24; self.ny = y_bottom - nb
        lx = x + self.num.shape[1] - 48 + 34
        self.label = Block(rows, times, t_out, x=lx, y_bottom=y_bottom, d_out=d_out, max_w=SAFE["xr_low"] - 10 - lx)
        self.dots_y = y_bottom + 46; self.dots_x = x + 8

    def layers(self, t):
        if t < self.t_on or t >= self.t_out + self.d_out: return []
        u_out = clamp01((t - self.t_out) / self.d_out); ao = 1 - u_out; dyo = -22 * ease_inout(u_out)
        u = clamp01((t - self.t_on) / 0.22)
        s = 0.82 + 0.18 * ease_out(u) + 0.06 * math.sin(math.pi * u) * (1 - u)    # small bounce
        m = self.num
        if s != 1.0:
            h, w = m.shape; m2 = cv2.resize(m, (max(1, int(w * s)), max(1, int(h * s))), interpolation=cv2.INTER_LINEAR)
            ox = self.nx; oy = self.ny + (h - m2.shape[0]) * 0.7
        else:
            m2, ox, oy = m, self.nx, self.ny
        out = flat(m2, WHITE, ox, oy + dyo, clamp01(u / 0.5) * ao)
        out += self.label.layers(t)
        # progress dots
        ud = clamp01((t - self.t_on - 0.10) / 0.25)
        if ud > 0:
            D = np.zeros((24, 26 * self.total + 4), np.float32); F = np.zeros_like(D)
            for i in range(self.total):
                cx = 12 + 26 * i
                if i < self.n - 1: cv2.circle(F, (cx, 12), 6, 0.55, -1, cv2.LINE_AA)
                elif i == self.n - 1: cv2.circle(F, (cx, 12), 7, 1.0, -1, cv2.LINE_AA)
                else: cv2.circle(D, (cx, 12), 6, 0.55, 2, cv2.LINE_AA)
            a = ease_out(ud) * ao
            out.append(solid_layer(D * a, WHITE, self.dots_x, self.dots_y + dyo))
            out.append(solid_layer(F * a, CREAM, self.dots_x, self.dots_y + dyo))
        return out

class WordCaptions:
    """One word at a time (R1/R3). Words of <=2 letters join the next word. Emphasised words switch to
    Playfair Italic, larger and cream. Slide-up 12 px + fade, no glow."""
    def __init__(self, words, ypos_fn, hide_fn, emph=(), maxdur=0.95):
        self.ypos, self.hide = ypos_fn, hide_fn
        em = {e.lower().strip(".,?!") for e in emph}
        isem = lambda w: w["w"].lower().strip(".,?!") in em
        chunks = []; i = 0
        while i < len(words):
            grp = [words[i]]
            while (len(grp[-1]["w"].strip(".,?!")) <= 2 and not isem(grp[-1]) and i + 1 < len(words)
                   and not isem(words[i + 1]) and words[i + 1]["s"] - grp[-1]["e"] < 0.25):
                i += 1; grp.append(words[i])
            i += 1
            chunks.append(grp)
        self.chunks = []
        for k, g in enumerate(chunks):
            s = g[0]["s"] - 0.03
            nxt = chunks[k + 1][0]["s"] - 0.03 if k + 1 < len(chunks) else g[-1]["e"] + 0.4
            e = min(nxt, g[-1]["e"] + maxdur * 0.6, s + maxdur) if nxt - s > maxdur else nxt
            txt = " ".join(w["w"] for w in g)
            st = "ce" if (len(g) == 1 and isem(g[0])) else "c"
            m, base, col, cap = tmask(txt, st)
            self.chunks.append(dict(s=s, e=e, m=m, col=col, base=base, st=st))
        self.cur = None

    def layers(self, t):
        if self.hide(t): return []
        for c in self.chunks:
            if c["s"] <= t < c["e"]:
                m, dy, a = slide_in(c["m"], clamp01((t - c["s"]) / 0.12), dist=12)
                y = self.ypos(t)
                yy = y - c["base"] + (14 if c["st"] == "ce" else 0)
                return flat(m, c["col"], W / 2 - m.shape[1] / 2, yy + dy, a, shadow=0.22)
        return []

class Cutout:
    """R3 'sticker' moment: the person is cut out (rembg u2net_human_seg) with a white outline and a soft offset
    shadow over a blurred, desaturated warm-grey version of the frame. Applied to the base frame (PRE)."""
    def __init__(self, t0, t1, model_home):
        import os
        self.t0, self.t1 = t0, t1; os.environ.setdefault("U2NET_HOME", model_home); self.sess = None

    def pre(self, f, t):
        if not (self.t0 <= t < self.t1): return f
        from rembg import new_session, remove
        from PIL import Image
        if self.sess is None: self.sess = new_session("u2net_human_seg")
        small = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).resize((540, 960))
        m = np.asarray(remove(small, session=self.sess, only_mask=True).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
        bg = cv2.GaussianBlur(f, (0, 0), 30); g = bg.mean(2, keepdims=True)
        bg = (bg * 0.30 + g * 0.70) * 0.60 + np.array([0.055, 0.048, 0.040], np.float32)
        mb = (m > 0.5).astype(np.uint8)
        ring = cv2.dilate(mb, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))).astype(np.float32)
        ring = cv2.GaussianBlur(ring, (0, 0), 1.2)
        sh = cv2.GaussianBlur(np.roll(np.roll(ring, 16, 0), 10, 1), (0, 0), 12) * 0.45
        out = bg * (1 - sh[..., None]); out = out * (1 - ring[..., None]) + ring[..., None] * 0.985
        mm = cv2.GaussianBlur(m, (0, 0), 0.8)[..., None]
        return out * (1 - mm) + f * mm

class BottomShade:
    """Soft black gradient on the lower part of the frame (client's 'degradados negros') so flat white text
    stays readable over bright b-roll without adding shadows to the text itself."""
    def __init__(self, when, top=0.55, strength=0.42):
        self.when = when
        y = np.linspace(0, 1, H, dtype=np.float32)
        g = np.clip((y - top) / (1 - top), 0, 1) ** 1.6 * strength
        self.g = g[:, None, None]
    def pre(self, f, t):
        return f * (1 - self.g) if self.when(t) else f

class FadeOut:
    def __init__(self, t0, t1): self.t0, self.t1 = t0, t1
    def post(self, f, t):
        if t < self.t0: return f
        return f * (1 - ease_inout(clamp01((t - self.t0) / (self.t1 - self.t0))))

class SoftZoom:
    """Very light zoom-blur on a cut (only a couple of times in the video)."""
    def __init__(self, tc, d=0.10, amount=0.08): self.tc, self.d, self.amount = tc, d, amount
    def post(self, f, t):
        u = 1 - abs(t - self.tc) / self.d
        if u <= 0: return f
        a = self.amount * u ** 1.5; acc = np.zeros_like(f)
        for k in range(6):
            s = 1 + a * k / 5
            M = np.array([[s, 0, (1 - s) * W / 2], [0, s, (1 - s) * H / 2]], np.float32)
            acc += cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return acc / 6
