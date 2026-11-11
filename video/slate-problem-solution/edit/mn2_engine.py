"""Reel 3 v5 — the client's own text presets (Drive 'material de edición'), rebuilt numerically from the preset files:
  * Texto Elegancia Real (Premiere V4 .mogrt)     -> hook: spread sans kicker words + script line (flicker, blur, L->R reveal)
  * slide_up / bounce_up (CapCut Minimal V2)      -> numbered problems
  * Three Aesthetic Words (Premiere Subs V3)      -> light / bold contrast, closing stack (rise + blur-in)
  * Apple Texto Deslizante 2 (Premiere V4)        -> captions: words glide up one by one
  * Dúo Cinemático (Premiere V4)                  -> script word overlapping the sans line
  * Texto Elegante (Premiere V4)                  -> painted marker underline (recoloured blush)
  * SB - Fade blanco elegante (DaVinci Títulos 2) -> storefront end: wide-spaced sans + typewriter script
Fonts: Poppins (brand sans, standing in for the presets' Inter) + Ocean Delight (the presets' script)."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from engine import *

WHITE, BLUSH, MARKER = "#FFFFFF", "#F1CFC4", "#C98C7E"
FK = {"L": ("Poppins-Light.ttf", None), "R": ("Poppins-Regular.ttf", None), "M": ("Poppins-Medium.ttf", None),
      "S": ("Poppins-SemiBold.ttf", None), "B": ("Poppins-Bold.ttf", None), "O": ("OceanDelight.ttf", None)}

def bez(x1, y1, x2, y2):
    """CSS cubic-bezier easing as a function of u in [0, 1]."""
    def f(u):
        u = min(max(u, 0.0), 1.0)
        t = u
        for _ in range(8):
            x = 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t * t * x2 + t ** 3 - u
            dx = 3 * (1 - t) ** 2 * x1 + 6 * (1 - t) * t * (x2 - x1) + 3 * t * t * (1 - x2)
            if abs(dx) < 1e-6: break
            t = min(max(t - x / dx, 0.0), 1.0)
        return 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t * t * y2 + t ** 3
    return f

SLIDE = bez(0.32, 0.94, 0.60, 1.00)      # CapCut minimal slide [READ]
BOUNCE = bez(0.17, 0.89, 0.32, 1.27)     # CapCut minimal bounce (easeOutBack) [READ]
AEST = bez(0.10, 0.00, 0.00, 1.00)       # Three Aesthetic Words rise [DECODED]
AEST_BLUR = bez(0.33, 0.00, 0.67, 1.00)
REVEAL = bez(0.34, 0.03, 0.00, 1.00)     # Elegancia Real / Texto Elegante reveal & trim [DECODED]

def tm(text, fk, size, tracking=0.0, pad=30, word_space=None):
    """Text mask. tracking in em; word_space (em) widens spaces (DaVinci 'word spacing')."""
    fn, w = FK[fk]
    ft = font(fn, size, w)
    if word_space is None:
        m, base, _ = text_mask(text, ft, tracking_px=tracking * size, pad=pad)
        return m, base, ft
    words = text.split(" "); ms = [text_mask(x, ft, tracking_px=tracking * size, pad=pad) for x in words]
    gap = int(word_space * size); hgt = max(m.shape[0] for m, _, _ in ms)
    wtot = sum(m.shape[1] - 2 * pad for m, _, _ in ms) + gap * (len(ms) - 1) + 2 * pad
    M = np.zeros((hgt, wtot), np.float32); x = pad
    for m, b, _ in ms:
        M[:m.shape[0], x - pad:x - pad + m.shape[1]] = np.maximum(M[:m.shape[0], x - pad:x - pad + m.shape[1]], m)
        x += m.shape[1] - 2 * pad + gap
    return M, ms[0][1], ft

def put(m, col, x, y, a=1.0, shadow=0.16):
    out = []
    if shadow > 0 and a > 0.01:
        pad = 16; s = blur(np.pad(m, pad), 6) * shadow * a
        out.append(solid_layer(s, "#000000", x - pad, y - pad + 2))
    out.append(solid_layer(m * a, col, x, y))
    return out

def blurm(m, r):
    return blur(m, r) if r > 0.3 else m

# ---------------------------------------------------------------- Texto Elegancia Real (hook)
class EleganciaReal:
    def __init__(self, kicker_words, script_lines, t0, t_out, cx=W / 2, y_script=1330, k=0.80, ks=58, ss=190, max_w=900):
        self.t0, self.t_out, self.k = t0, t_out, k
        if isinstance(script_lines, str): script_lines = [script_lines]
        while True:
            ms = [tm(l, "O", ss, tracking=-0.0096) for l in script_lines]
            if max(m.shape[1] - 60 for m, _, _ in ms) <= max_w or ss < 60: break
            ss *= 0.95
        # stack script lines (baseline step 0.80 em: ascenders tuck into the line above)
        n = len(ms); yb0 = y_script - (n - 1) * 0.80 * ss
        Hh = int(yb0 + (n - 1) * 0.80 * ss + ss * 0.6) ; top = int(yb0 - ss * 1.15)
        Wd = max(m.shape[1] for m, _, _ in ms)
        S = np.zeros((Hh - top, Wd), np.float32)
        for i, (m, b, _) in enumerate(ms):
            yy = int(yb0 + i * 0.80 * ss - b - top); xx = (Wd - m.shape[1]) // 2
            y0, y1 = max(0, yy), min(S.shape[0], yy + m.shape[0])
            S[y0:y1, xx:xx + m.shape[1]] = np.maximum(S[y0:y1, xx:xx + m.shape[1]], m[y0 - yy:y1 - yy])
        sm = S
        self.s = (sm, cx - sm.shape[1] / 2, top)
        sw = max(m.shape[1] for m, _, _ in ms) - 60
        y_script = yb0
        km = [tm(w, "B", ks, tracking=-0.0135) for w in kicker_words]   # spread evenly across the script width
        widths = [m.shape[1] - 60 for m, _, _ in km]; n = len(km)
        gap = 0.42 * ks; tot = sum(widths) + gap * (n - 1)              # natural phrase, slightly open word spacing
        x = cx - tot / 2; self.kw = []
        for i, (m, b, _) in enumerate(km):
            self.kw.append((m, x - 30, y_script - ss * 1.22 - b, i * 0.085 * k)); x += widths[i] + gap
        self.ks = ks

    def layers(self, t):
        if t < self.t0 or t >= self.t_out + 0.2: return []
        lt = (t - self.t0) / self.k; fo = 1 - clamp01((t - self.t_out) / 0.2); out = []
        for m, x, y, st in self.kw:                                # rise +0.34 em, fade, 0.19 s each [DECODED]
            u = clamp01((lt - st / self.k) / 0.19)
            if u <= 0: continue
            e = SLIDE(u); out += put(m, WHITE, x, y + 0.34 * self.ks * (1 - e), clamp01(u * 1.6) * fo)
        sm, x, y = self.s
        if lt >= 0.25:
            keys = [(0.25, 0), (0.33, 1), (0.42, 0.12), (0.46, 1), (0.54, 0), (0.58, 1), (0.67, 0), (0.71, 1)]
            op = 1.0
            for (ta, va), (tb, vb) in zip(keys, keys[1:]):
                if ta <= lt < tb: op = va + (vb - va) * (lt - ta) / (tb - ta); break
            bl = 0.0                                               # text blur 35 -> 0 -> 16 -> 0 (4K comp) [DECODED]
            for (ta, va), (tb, vb) in zip([(0.25, 35), (0.33, 0), (0.42, 16)], [(0.33, 0), (0.42, 16), (0.46, 0)]):
                if ta <= lt < tb: bl = va + (vb - va) * (lt - ta) / (tb - ta)
            rv = REVEAL(clamp01((lt - 0.29) / (1.46 - 0.29)))      # left -> right reveal [DECODED]
            cut = int(sm.shape[1] * rv); M = sm.copy()
            edge = np.clip((cut - np.arange(sm.shape[1])) / 40.0 + 0.5, 0, 1)[None, :]
            M = M * edge
            out += put(blurm(M, bl * 0.28), WHITE, x, y, op * fo)
        return out

# ---------------------------------------------------------------- numbered problems (CapCut slide/bounce)
class NumberedProblem:
    def __init__(self, n, total, rows, times, t_on, t_out, x=90, y_bottom=1450, max_w=None):
        """rows: [(text, fontkey, size), ...] stacked; times: one per row (row words slide in together)."""
        self.n, self.total, self.t_on, self.t_out = n, total, t_on, t_out
        self.num = tm(f"{n}.", "B", 132, tracking=-0.02)
        nm, nb, _ = self.num
        lx = x + nm.shape[1] - 60 + 30
        max_w = max_w or (905 - lx)
        sc = 1.0
        for _ in range(6):
            ms = [tm(t, fk, s * sc, tracking=-0.01) for (t, fk, s) in rows]
            if max(m.shape[1] - 60 for m, _, _ in ms) <= max_w: break
            sc *= max_w / max(m.shape[1] - 60 for m, _, _ in ms) * 0.99
        self.rows = []
        yb = y_bottom
        for i in range(len(rows) - 1, -1, -1):
            m, b, ft = ms[i]; self.rows.insert(0, (m, lx - 30, yb - b, times[i]))
            if i > 0:
                cap = rows[i][2] * sc * 0.72; capu = rows[i - 1][2] * sc * 0.72
                yb -= cap + 0.30 * capu + 14
        self.nx, self.ny = x - 30, y_bottom - nb
        self.dots = (x + 6, y_bottom + 44)

    def layers(self, t):
        if t < self.t_on or t >= self.t_out + 0.18: return []
        fo = 1 - clamp01((t - self.t_out) / 0.18); dyo = -20 * clamp01((t - self.t_out) / 0.18); out = []
        nm, nb, _ = self.num
        u = clamp01((t - self.t_on) / 0.5)                         # bounce_up 0.5 s, 50 px, fade 0.3 s [READ]
        out += put(nm, WHITE, self.nx, self.ny + 50 * (1 - BOUNCE(u)) + dyo, clamp01((t - self.t_on) / 0.3) * fo)
        for m, x, y, ton in self.rows:                            # slide_up 0.5 s, 50 px, fade 0.3 s [READ]
            if t < ton: continue
            u = clamp01((t - ton) / 0.5)
            out += put(m, WHITE, x, y + 50 * (1 - SLIDE(u)) + dyo, clamp01((t - ton) / 0.3) * fo)
        ud = clamp01((t - self.t_on - 0.12) / 0.3)
        if ud > 0:
            D = np.zeros((24, 26 * self.total + 4), np.float32); F = np.zeros_like(D)
            for i in range(self.total):
                c = 12 + 26 * i
                if i < self.n - 1: cv2.circle(F, (c, 12), 6, 0.55, -1, cv2.LINE_AA)
                elif i == self.n - 1: cv2.circle(F, (c, 12), 7, 1.0, -1, cv2.LINE_AA)
                else: cv2.circle(D, (c, 12), 6, 0.55, 2, cv2.LINE_AA)
            out.append(solid_layer(D * ud * fo, WHITE, self.dots[0], self.dots[1] + dyo))
            out.append(solid_layer(F * ud * fo, BLUSH, self.dots[0], self.dots[1] + dyo))
        return out

# ---------------------------------------------------------------- captions (Apple Texto Deslizante 2 + Dúo script word)
class GlideCaptions:
    def __init__(self, words, ypos_fn, hide_fn, emph=(), size=64, max_words=3, max_chars=17):
        self.ypos, self.hide, self.size = ypos_fn, hide_fn, size
        em = {e.lower().strip(".,?!") for e in emph}
        isem = lambda w: w["w"].lower().strip(".,?!") in em
        chunks = []; cur = []
        for i, w in enumerate(words):
            nxt = words[i + 1] if i + 1 < len(words) else None
            cur.append(w)
            txt = " ".join(x["w"] for x in cur)
            brk = (w["w"][-1] in ",.?!" or len(cur) >= max_words or nxt is None or nxt["s"] - w["e"] > 0.35
                   or len(txt) + 1 + len(nxt["w"]) > max_chars or isem(w) or (nxt is not None and isem(nxt)))
            if brk: chunks.append(cur); cur = []
        self.chunks = []
        for k, c in enumerate(chunks):
            s = c[0]["s"] - 0.05
            e = (chunks[k + 1][0]["s"] - 0.05) if k + 1 < len(chunks) else c[-1]["e"] + 0.45
            e = min(e, c[-1]["e"] + 0.7)
            toks = []
            for w in c:
                if isem(w):
                    m, b, _ = tm(w["w"].strip(".,"), "O", size * 2.15, tracking=-0.003); toks.append((m, b, BLUSH, w["s"], True))
                else:
                    m, b, _ = tm(w["w"], "S", size, tracking=-0.011); toks.append((m, b, WHITE, w["s"], False))
            gap = size * 0.28
            wtot = sum(m.shape[1] - 60 for m, _, _, _, _ in toks) + gap * (len(toks) - 1)
            self.chunks.append(dict(s=s, e=e, toks=toks, w=wtot, gap=gap))

    def layers(self, t):
        if self.hide(t): return []
        for c in self.chunks:
            if c["s"] <= t < c["e"]:
                y = self.ypos(t); x = W / 2 - c["w"] / 2; out = []
                for m, b, col, ts, script in c["toks"]:
                    u = clamp01((t - (ts - 0.05)) / 0.42)          # glide up 0.62 em + fade [DECODED/EST]
                    if u > 0:
                        e = SLIDE(u); dy = 0.62 * self.size * (1 - e)
                        yy = y - b + (self.size * 0.30 if script else 0)
                        out += put(m, col, x - 30, yy + dy, clamp01(u * 2.2), shadow=0.22)
                    x += m.shape[1] - 60 + c["gap"]
                return out
        return []

# ---------------------------------------------------------------- solutions: Dúo Cinemático + Texto Elegante marker
def brush_mask(w, h, seed=0):
    """Painted marker stroke (Texto Elegante): soft, slightly irregular band, tapered ends."""
    rng = np.random.default_rng(seed)
    M = np.zeros((h * 3, w + 40), np.float32)
    xs = np.arange(w + 40)
    wob = np.cumsum(rng.normal(0, 0.35, w + 40)); wob = (wob - wob.mean()) * 0.6
    top = h + wob - 2 * np.sin(np.linspace(0, math.pi, w + 40)) * h * 0.08
    th = h * (0.75 + 0.25 * np.sin(np.linspace(0, math.pi, w + 40)) ** 0.5)
    for i in range(0, w + 40):
        a, b = int(top[i]), int(top[i] + th[i])
        M[max(0, a):min(M.shape[0], b), i] = 1.0
    M = cv2.GaussianBlur(M, (0, 0), 2.2)
    grain = cv2.GaussianBlur(rng.random(M.shape).astype(np.float32), (0, 0), 1.0)
    return np.clip(M * (0.82 + 0.18 * grain), 0, 1)

class SolutionDuo:
    """line1: sans (S/B), white, words rise +0.39 em with blur 28->0 and a small damped bounce (Texto Elegante);
    optional blush marker under line1 (trim 0->100 over 1.0 s, REVEAL ease); line2: script (Ocean Delight, blush)
    overlapping the bottom of line1 (Dúo Cinemático), sliding up."""
    def __init__(self, line1, fk1, size1, line2, size2, t1, t2, t_out, x=90, y_base=1400, marker=True, seed=0, max_w=830):
        self.t1, self.t2, self.t_out, self.marker = t1, t2, t_out, marker
        sc = 1.0
        for _ in range(6):
            m1, b1, _ = tm(line1, fk1, size1 * sc, tracking=-0.02)
            m2, b2, _ = tm(line2, "O", size2 * sc, tracking=-0.003) if line2 else (None, 0, None)
            wmax = max(m1.shape[1] - 60, (m2.shape[1] - 60 + size1 * sc * 0.25) if m2 is not None else 0)
            if wmax <= max_w: break
            sc *= max_w / wmax * 0.99
        self.size1 = size1 * sc
        self.m1 = (m1, x - 30, y_base - b1)
        self.size2 = size2 * sc
        self.m2 = None
        if m2 is not None:                                         # place by measured ink: script x-height body sits just
            prof = m2.astype(np.float32).sum(1)                    # under line 1, only the tall ascenders cross into it
            xtop = int(np.argmax(prof > 0.35 * prof.max()))
            self.m2 = (m2, x - 30 + self.size1 * 0.10, y_base + self.size1 * 0.10 - xtop)
        self.br = brush_mask(int(m1.shape[1] - 50), int(self.size1 * 0.30), seed) if marker else None
        self.br_xy = (x - 18, y_base - self.size1 * 0.30 - self.size1 * 0.36)     # behind the lower third of the text

    def layers(self, t):
        if t < self.t1 or t >= self.t_out + 0.18: return []
        fo = 1 - clamp01((t - self.t_out) / 0.18); dyo = -18 * clamp01((t - self.t_out) / 0.18); out = []
        lt = t - self.t1
        if self.br is not None and lt > 0.30:                      # marker trim 0 -> 100 over 1.0 s [DECODED, scaled]
            u = REVEAL(clamp01((lt - 0.30) / 1.0)); B = self.br.copy(); cut = int(B.shape[1] * u)
            B[:, cut:] = 0; B[:, max(0, cut - 20):cut] *= np.linspace(1, 0, min(20, cut))[None, :] if cut > 0 else 1
            out.append(solid_layer(B * 0.92 * fo, MARKER, self.br_xy[0], self.br_xy[1] + dyo))
        if self.m2 is not None and t >= self.t2:
            m2, x2, y2 = self.m2; u2 = clamp01((t - self.t2) / 0.5)
            out += put(m2, BLUSH, x2, y2 + 50 * (1 - SLIDE(u2)) + dyo, clamp01((t - self.t2) / 0.3) * fo)
        m, x, y = self.m1
        u = clamp01(lt / 0.667)
        bounce = math.exp(-7 * lt) * math.cos(2 * math.pi * 3 * lt) if lt < 1.2 else 0
        dy = 0.39 * self.size1 * (1 - SLIDE(u)) + 4 * bounce * (u >= 1)
        out += put(blurm(m, 7 * (1 - clamp01(lt / 0.35))), WHITE, x, y + dy + dyo, clamp01(lt / 0.2) * fo)
        return out

# ---------------------------------------------------------------- closing: Three Aesthetic Words stack
class AestheticStack:
    def __init__(self, rows, times, t_out, x=90, y_bottom=1450):
        """rows: (text, fontkey, size, colour)."""
        self.t_out = t_out; self.items = []
        yb = y_bottom; tmp = []
        for i in range(len(rows) - 1, -1, -1):
            text, fk, size, col = rows[i]
            m, b, _ = tm(text, fk, size, tracking=-0.025 if fk != "O" else 0)
            tmp.insert(0, (m, x - 30, yb - b, times[i], col, size))
            if i > 0:
                cap = (size * 0.62 if fk == "O" else size * 0.72); capu = rows[i - 1][2] * 0.72
                yb -= cap + 0.30 * capu + 16                        # tight leading (~0.85), no collisions
        self.items = tmp

    def layers(self, t):
        if t >= self.t_out + 0.2: return []
        fo = 1 - clamp01((t - self.t_out) / 0.2); out = []
        for m, x, y, ton, col, size in self.items:
            if t < ton: continue
            lt = t - ton
            dy = 0.10 * 1080 * 0.55 * (1 - AEST(clamp01(lt / 1.11)))   # offset ~0.1 comp height -> 0 in 1.11 s [DECODED]
            bl = 15 * 0.5 * (1 - AEST_BLUR(clamp01(lt / 0.54)))       # blur 15 -> 0 in 0.54 s
            out += put(blurm(m, bl), col, x, y + dy, clamp01(lt / 0.20) * fo)
        return out

# ---------------------------------------------------------------- storefront: SB - Fade blanco elegante
class FadeBlancoElegante:
    def __init__(self, line_a, script, line_c, t_a, t_b, t_c, t_out, cx=W / 2, y_script=1240):
        self.t_a, self.t_b, self.t_c, self.t_out = t_a, t_b, t_c, t_out
        ft = font(FK["B"][0], 50); self.la = []
        # line A: Poppins Bold, very wide word spacing, letters staggered 1.21 frames [READ]
        A, ab, _ = tm(line_a, "B", 50, tracking=0.08, word_space=0.65)
        self.A = (A, cx - A.shape[1] / 2, y_script - 365 - ab)
        S, sb, sft = tm(script, "O", 330)
        self.S = (S, cx - S.shape[1] / 2, y_script - sb); self.nchar = len(script)
        # per-letter x cut positions for the typewriter
        self.cuts = [30 + sft.getlength(script[:i + 1]) for i in range(len(script))]
        Cm, cb, _ = tm(line_c, "L", 50, tracking=0.0)
        self.Cm = (Cm, cx - Cm.shape[1] / 2, y_script + 175 - cb)

    def layers(self, t):
        if t < self.t_a: return []
        out = []
        A, x, y = self.A; n = A.shape[1]
        k = clamp01((t - self.t_a) / (1.21 / 30 * 16))           # letters revealed progressively
        edge = np.clip((n * k - np.arange(n)) / 30.0, 0, 1)[None, :]
        out += put(A * edge, WHITE, x, y + 14 * (1 - SLIDE(clamp01((t - self.t_a) / 0.5))), 1.0)
        if t >= self.t_b:                                          # typewriter 14 frames, blur-on [READ]
            S, x, y = self.S; lt = t - self.t_b; T = 14 / 30
            i = min(self.nchar, int(lt / T * self.nchar) + 1); cut = int(self.cuts[i - 1]) + 6
            M = S.copy(); M[:, cut:] = 0
            prog = clamp01(lt / T * self.nchar - (i - 1))
            out += put(blurm(M, 5 * (1 - prog) if lt < T else 0), WHITE, x, y, 1.0)
        if t >= self.t_c:
            Cm, x, y = self.Cm; u = clamp01((t - self.t_c) / 0.5)
            out += put(Cm, WHITE, x, y + 30 * (1 - SLIDE(u)), clamp01((t - self.t_c) / 0.3))
        return out

# ---------------------------------------------------------------- library visuals
class GradientPNG:
    """Client's 'Degradado a negro subtítulos.png' as a soft legibility shade on b-roll."""
    def __init__(self, path, when, opacity=0.6):
        a = np.asarray(Image.open(path).convert("RGBA").resize((W, H)))[:, :, 3].astype(np.float32) / 255
        self.g = (a * opacity)[..., None]; self.when = when
    def pre(self, f, t):
        return f * (1 - self.g) if self.when(t) else f

class FilmBurn:
    """Client's 'film burns(2).mp4', screen-blended, its brightest frame on the cut tc."""
    def __init__(self, path, tc, peak_at=0.5, opacity=0.45):
        import subprocess
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo",
                              "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        self.fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
        pk = int(np.argmax([fr[::8, ::8].mean() for fr in self.fr]))
        self.t0 = tc - pk / FPS; self.op = opacity
    def post(self, f, t):
        i = int(round((t - self.t0) * FPS))
        if i < 0 or i >= len(self.fr): return f
        o = self.fr[i].astype(np.float32) / 255 * self.op
        return 1 - (1 - f) * (1 - o)
