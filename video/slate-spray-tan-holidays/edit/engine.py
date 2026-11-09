"""Vertical reel compositor: shots (ffmpeg decode) + animated text overlays (PIL/numpy) -> ffmpeg encode.
Effects modelled on the reference reel: sparkle reveal titles, serif typewriter, serif tracking-in words,
fade-up lines, word-by-word captions and a white end card with the SLATE logo."""
import os, json, math, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
SRC_W, SRC_H = 1512, 2688          # decode size (1.4x headroom for zooms)
FONT_DIR = os.environ.get("FONT_DIR", "")

# ---------------------------------------------------------------- fonts
@functools.lru_cache(None)
def font(name, size, wght=None):
    f = ImageFont.truetype(os.path.join(FONT_DIR, name), int(round(size)))
    if wght is not None:
        try:
            axes = f.get_variation_axes()
            f.set_variation_by_axes([wght if (a["name"] in (b"Weight", "Weight")) else a["default"] for a in axes])
        except Exception:
            pass
    return f

COND = ("Oswald[wght].ttf", 500)                 # condensed bold uppercase titles
SERIF = ("EBGaramond-Italic[wght].ttf", 600)     # serif italic accents
CAPF = ("Poppins-Bold.ttf", None)                # captions: Poppins Bold, tight tracking + glow
SANSB = ("Inter[opsz,wght].ttf", 700)            # bold sans (fade-up line)
MONT = ("Montserrat[wght].ttf", 400)             # end card text
MONT_L = ("Montserrat[wght].ttf", 300)

def fit_size(fspec, text, width, tracking=0.0):
    name, w = fspec
    f = font(name, 100, w)
    l = f.getlength(text) + tracking * 100 * max(0, len(text) - 1)
    return 100 * width / l

# ---------------------------------------------------------------- helpers
def ease_out(u): u = min(max(u, 0.0), 1.0); return 1 - (1 - u) ** 3
def ease_inout(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
def clamp01(u): return min(max(u, 0.0), 1.0)

def hex2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def tracked_x(text, f, tracking_px, track_spaces=True):
    """x position of each char; with track_spaces=False the tracking only tightens letters inside words."""
    xs = []; k = 0
    for i, ch in enumerate(text):
        if i > 0 and (track_spaces or (text[i - 1] != " " and ch != " ")): k += 1
        xs.append(f.getlength(text[:i]) + tracking_px * k)
    return xs, k

def text_mask(text, f, tracking_px=0.0, pad=20, sx=1.0, track_spaces=True):
    """Render text alpha mask (float32 0..1) with per-char tracking. Returns (mask, baseline_y, char_xs)."""
    asc, desc = f.getmetrics()
    xs, k = tracked_x(text, f, tracking_px, track_spaces)
    total = (f.getlength(text) + tracking_px * k)
    w = int(math.ceil(total)) + 2 * pad; h = asc + desc + 2 * pad
    im = Image.new("L", (w, h), 0); d = ImageDraw.Draw(im)
    if tracking_px == 0:
        d.text((pad, pad), text, font=f, fill=255)
    else:
        for ch, cx in zip(text, xs):
            d.text((pad + cx, pad), ch, font=f, fill=255)
    m = np.asarray(im, np.float32) / 255.0
    if sx != 1.0:
        m = cv2.resize(m, (max(1, int(w * sx)), h), interpolation=cv2.INTER_AREA)
    return m, pad + asc, xs

def blur(a, r):
    if r <= 0.05: return a
    k = int(r * 3) * 2 + 1
    return cv2.GaussianBlur(a, (k, k), r)

class Layer:
    """RGBA float layer positioned at (x, y) (top-left) in frame coordinates."""
    def __init__(self, rgb, alpha, x, y):
        self.rgb, self.alpha, self.x, self.y = rgb, alpha, int(round(x)), int(round(y))

def solid_layer(mask, color, x, y):
    c = np.array(hex2rgb(color), np.float32) / 255.0
    rgb = np.empty(mask.shape + (3,), np.float32); rgb[:] = c
    return Layer(rgb, mask, x, y)

def glow_text(mask, color, x, y, glow_sigma=48, glow_gain=2.3, glow_op=1.0, sh_sigma=4, sh_dy=3, sh_op=0.95):
    """Reference caption look: wide white halo (bloom) behind, fine dark shadow just under the letters, white text.
    Parameters fitted to the luminance profile measured around the reference captions."""
    pad = int(glow_sigma * 2.6)
    m = np.pad(mask, pad)
    small = cv2.resize(m, (m.shape[1] // 4, m.shape[0] // 4), interpolation=cv2.INTER_AREA)
    g = cv2.resize(blur(small, glow_sigma / 4), (m.shape[1], m.shape[0]), interpolation=cv2.INTER_LINEAR)
    g = np.clip(g * glow_gain, 0, 1) * glow_op
    sh = np.roll(blur(m, sh_sigma), sh_dy, 0) * sh_op
    return [solid_layer(g, "#FFFFFF", x - pad, y - pad),
            solid_layer(sh, "#000000", x - pad, y - pad),
            solid_layer(mask, color, x, y)]

def with_shadow(mask, color, x, y, sh_r=7, sh_dy=3, sh_op=0.5, glow=None):
    """Text layer + soft drop shadow (+ optional white glow). Returns list of layers (back to front)."""
    out = []
    pad = int(sh_r * 3)
    m = np.pad(mask, pad)
    s = blur(m, sh_r) * sh_op
    out.append(solid_layer(s, "#000000", x - pad, y - pad + sh_dy))
    if glow:
        g = blur(m, glow[0]) * glow[1]
        out.append(solid_layer(np.clip(g, 0, 1), "#FFFFFF", x - pad, y - pad))
    out.append(solid_layer(mask, color, x, y))
    return out

def composite(frame, layer):
    """frame: float32 HxWx3 (0..1). Alpha 'over'."""
    a = layer.alpha; h, w = a.shape
    x0, y0 = layer.x, layer.y
    fx0, fy0 = max(0, x0), max(0, y0); fx1, fy1 = min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0: return
    lx0, ly0 = fx0 - x0, fy0 - y0; lx1, ly1 = lx0 + (fx1 - fx0), ly0 + (fy1 - fy0)
    al = a[ly0:ly1, lx0:lx1, None]
    if al.max() <= 0.001: return
    reg = frame[fy0:fy1, fx0:fx1]
    reg *= (1 - al); reg += layer.rgb[ly0:ly1, lx0:lx1] * al

# ---------------------------------------------------------------- text effects
class SparkleTitle:
    """Left-to-right reveal with a glowing, blurred front and glitter particles (condensed caps)."""
    def __init__(self, lines, t0, t1, cy, size, color="#FFF8EE", dur=0.47, line_gap=0.92, seed=1, sx=0.94):
        self.t0, self.t1, self.dur = t0, t1, dur
        f = font(COND[0], size, COND[1])
        masks = [text_mask(s, f, pad=0, sx=sx)[0] for s in lines]
        lh = int(size * line_gap * 1.25)
        w = max(m.shape[1] for m in masks); asc, desc = f.getmetrics()
        hh = lh * (len(lines) - 1) + masks[-1].shape[0]
        P = 70
        M = np.zeros((hh + 2 * P, w + 2 * P), np.float32)
        for i, m in enumerate(masks):
            ox = P + (w - m.shape[1]) // 2; oy = P + i * lh
            M[oy:oy + m.shape[0], ox:ox + m.shape[1]] = np.maximum(M[oy:oy + m.shape[0], ox:ox + m.shape[1]], m)
        self.M = M; self.P = P; self.tw = w
        self.A1 = blur(M, 4); self.A2 = blur(M, 16)
        self.x = W / 2 - M.shape[1] / 2; self.y = cy - M.shape[0] / 2
        self.color = color
        rng = np.random.default_rng(seed)
        n = 90
        self.parts = dict(
            u=rng.random(n) ** 0.9, dx=rng.normal(0, 18, n), y=rng.uniform(P - 0.35 * hh, P + 1.35 * hh, n),
            vx=rng.normal(35, 45, n), vy=rng.normal(-15, 35, n), life=rng.uniform(0.18, 0.55, n),
            r=rng.uniform(1.2, 3.6, n) ** 1.1, tw=rng.uniform(0, 6.28, n), star=rng.random(n) < 0.25)
        self.static = None

    def front(self, u):
        return self.P - 30 + (self.tw + 60) * ease_inout(u)

    def layers(self, t):
        if t < self.t0 or t >= self.t1: return []
        lt = t - self.t0
        fade_out = 1.0 - clamp01((t - (self.t1 - 0.12)) / 0.12)
        u = clamp01(lt / self.dur)
        xs = np.arange(self.M.shape[1], dtype=np.float32)
        xf = self.front(u)
        done = clamp01((lt - self.dur) / 0.18)          # glow fades after reveal
        if lt > self.dur + 0.75:
            if self.static is None:
                self.static = with_shadow(self.M, self.color, self.x, self.y, sh_r=8, sh_op=0.45, glow=(10, 0.12))
            return [Layer(l.rgb, l.alpha * fade_out, l.x, l.y) for l in self.static]
        soft = 26.0
        m = np.clip((xf - xs) / soft + 0.5, 0, 1)                      # revealed region
        g = np.exp(-(((xf - xs) / (0.30 * self.tw)) ** 2)) * (xs < xf + 40)   # glow near the front
        g = g * (1 - done)
        crisp = self.M * (m * (1 - 0.85 * g))[None, :]
        glow = np.clip(self.A1 * 1.5 + self.A2 * 1.1, 0, 1) * (np.clip((xf + 40 - xs) / 40, 0, 1) * g)[None, :]
        out = with_shadow(crisp, self.color, self.x, self.y, sh_r=8, sh_op=0.45 * (1 - 0.6 * g.mean()), glow=(10, 0.12))
        out.append(solid_layer(np.clip(glow, 0, 1), "#FFFFFF", self.x, self.y))
        # glitter
        p = self.parts; spawn = self.t0 + p["u"] * self.dur * 1.05
        age = t - spawn; alive = (age >= 0) & (age < p["life"])
        if alive.any():
            G = np.zeros_like(self.M)
            for i in np.where(alive)[0]:
                a = age[i]; k = (1 - a / p["life"][i]) ** 1.4 * (0.6 + 0.4 * math.sin(p["tw"][i] + a * 40))
                px = self.front(p["u"][i]) + p["dx"][i] + p["vx"][i] * a
                py = p["y"][i] + p["vy"][i] * a
                r = p["r"][i]
                ix, iy = int(px), int(py)
                if 3 < ix < G.shape[1] - 4 and 3 < iy < G.shape[0] - 4:
                    cv2.circle(G, (ix, iy), max(1, int(round(r))), float(k), -1, lineType=cv2.LINE_AA)
                    if p["star"][i]:
                        L = int(r * 4)
                        cv2.line(G, (ix - L, iy), (ix + L, iy), float(k * 0.7), 1, cv2.LINE_AA)
                        cv2.line(G, (ix, iy - L), (ix, iy + L), float(k * 0.7), 1, cv2.LINE_AA)
            G = np.clip(G + blur(G, 3) * 1.5, 0, 1)
            out.append(solid_layer(G * fade_out, "#FFFFFF", self.x, self.y))
        return [Layer(l.rgb, l.alpha * fade_out, l.x, l.y) for l in out]

class TypeLine:
    """Serif italic line, typed letter by letter; each letter fades and settles from a larger scale."""
    def __init__(self, text, t0, t1, cx, cy, size, color="#FFFFFF", cps=34.0, fspec=SERIF, letter_dur=0.09, instant=False):
        self.t0, self.t1, self.text, self.cps, self.ld = t0, t1, text, cps, letter_dur
        self.f = font(fspec[0], size, fspec[1]); self.color = color; self.instant = instant
        full, base, xs = text_mask(text, self.f, pad=30)
        self.full = full; self.xs = xs; self.pad = 30
        self.x = cx - full.shape[1] / 2; self.y = cy - full.shape[0] / 2
        # per-char glyph masks
        self.glyphs = []
        for i, ch in enumerate(text):
            m, _, _ = text_mask(ch, self.f, pad=30)
            self.glyphs.append(m)
        self.static = None

    def layers(self, t):
        if t < self.t0 or t >= self.t1: return []
        lt = t - self.t0; n = len(self.text)
        fade_out = 1.0 - clamp01((t - (self.t1 - 0.12)) / 0.12)
        if self.instant or lt > n / self.cps + self.ld + 0.02:
            if self.static is None:
                self.static = with_shadow(self.full, self.color, self.x, self.y, sh_r=7, sh_op=0.5)
            if self.instant:
                a = ease_out(lt / 0.12)
                return [Layer(l.rgb, l.alpha * fade_out * a, l.x, l.y) for l in self.static]
            return [Layer(l.rgb, l.alpha * fade_out, l.x, l.y) for l in self.static]
        M = np.zeros_like(self.full)
        for i, ch in enumerate(self.text):
            if ch == " ": continue
            ts = i / self.cps
            if lt < ts: break
            u = clamp01((lt - ts) / self.ld)
            g = self.glyphs[i]; s = 1.35 - 0.35 * ease_out(u)
            if s != 1.0:
                gh, gw = g.shape; g2 = cv2.resize(g, (max(1, int(gw * s)), max(1, int(gh * s))), interpolation=cv2.INTER_LINEAR)
                ox = int(self.xs[i] - (g2.shape[1] - gw) / 2); oy = int(-(g2.shape[0] - gh) * 0.6)
            else:
                g2 = g; ox = int(self.xs[i]); oy = 0
            a = ease_out(u)
            y0, x0 = max(0, oy), max(0, ox)
            y1 = min(M.shape[0], oy + g2.shape[0]); x1 = min(M.shape[1], ox + g2.shape[1])
            M[y0:y1, x0:x1] = np.maximum(M[y0:y1, x0:x1], g2[y0 - oy:y1 - oy, x0 - ox:x1 - ox] * a)
        return [Layer(l.rgb, l.alpha * fade_out, l.x, l.y) for l in with_shadow(M, self.color, self.x, self.y, sh_r=7, sh_op=0.5)]

class TrackIn:
    """Serif word that zooms in while its wide letter-spacing collapses (the 'Steam,' effect)."""
    def __init__(self, text, t0, t1, cx, cy, size, color="#FFFFFF", dur=0.30):
        self.text, self.t0, self.t1, self.dur = text, t0, t1, dur
        self.cx, self.cy, self.size, self.color = cx, cy, size, color
        self.static = None

    def layers(self, t):
        if t < self.t0 or t >= self.t1: return []
        lt = t - self.t0
        fade_out = 1.0 - clamp01((t - (self.t1 - 0.08)) / 0.08)
        u = ease_out(lt / self.dur)
        if u >= 0.999:
            if self.static is None:
                f = font(SERIF[0], self.size, SERIF[1]); m, _, _ = text_mask(self.text, f, pad=30)
                self.static = with_shadow(m, self.color, self.cx - m.shape[1] / 2, self.cy - m.shape[0] / 2, sh_r=8, sh_op=0.5)
            return [Layer(l.rgb, l.alpha * fade_out, l.x, l.y) for l in self.static]
        s = 0.42 + 0.58 * u
        f = font(SERIF[0], max(8, self.size * s), SERIF[1])
        track = (1 - u) * 0.55 * self.size * s
        m, _, _ = text_mask(self.text, f, tracking_px=track, pad=30)
        sy = min(1.0, 0.15 + lt / 0.08)
        if sy < 1.0:
            m = cv2.resize(m, (m.shape[1], max(1, int(m.shape[0] * sy))), interpolation=cv2.INTER_AREA)
        a = min(1.0, 0.35 + 0.65 * u)
        return [Layer(l.rgb, l.alpha * a * fade_out, l.x, l.y) for l in
                with_shadow(m, self.color, self.cx - m.shape[1] / 2, self.cy - m.shape[0] / 2, sh_r=8, sh_op=0.5)]

class FadeUp:
    """A line that rises a few px while fading in from blur (the 'refreshed / and glowing.' effect)."""
    def __init__(self, text, t0, t1, cx, cy, size, fspec, color="#FFFFFF", dur=0.38, dy=22):
        self.t0, self.t1, self.dur, self.dy = t0, t1, dur, dy
        f = font(fspec[0], size, fspec[1]); self.m, _, _ = text_mask(text, f, pad=34)
        self.x = cx - self.m.shape[1] / 2; self.y = cy - self.m.shape[0] / 2; self.color = color
        self.static = None

    def layers(self, t):
        if t < self.t0 or t >= self.t1: return []
        lt = t - self.t0; u = ease_out(lt / self.dur)
        fade_out = 1.0 - clamp01((t - (self.t1 - 0.12)) / 0.12)
        if u >= 0.999:
            if self.static is None:
                self.static = with_shadow(self.m, self.color, self.x, self.y, sh_r=7, sh_op=0.5)
            return [Layer(l.rgb, l.alpha * fade_out, l.x, l.y) for l in self.static]
        m = blur(self.m, 6 * (1 - u))
        col = self.color if u > 0.6 else "#D8D8D8"
        return [Layer(l.rgb, l.alpha * u * fade_out, l.x, l.y) for l in
                with_shadow(m, col, self.x, self.y + self.dy * (1 - u), sh_r=7, sh_op=0.5)]

class Captions:
    """Word-by-word captions: each word fades in (slight blur) at its spoken time, in short chunks."""
    def __init__(self, words, size, ypos_fn, hide_fn, color="#FFFFFF", max_words=3, max_chars=17, lead=0.04, tracking=-0.04):
        self.f = font(CAPF[0], size, CAPF[1]); self.size = size; self.tr = tracking * size
        self.ypos_fn, self.hide_fn, self.color, self.lead = ypos_fn, hide_fn, color, lead
        # chunking
        chunks = []; cur = []
        for i, w in enumerate(words):
            cur.append(w)
            txt = " ".join(x["w"] for x in cur)
            nxt = words[i + 1] if i + 1 < len(words) else None
            brk = (w["w"][-1] in ",.?!" or len(cur) >= max_words or
                   (nxt is not None and len(txt) + 1 + len(nxt["w"]) > max_chars) or
                   (nxt is not None and nxt["s"] - w["e"] > 0.35))
            if brk or nxt is None:
                chunks.append(cur); cur = []
        self.chunks = []
        for k, c in enumerate(chunks):
            start = c[0]["s"] - self.lead
            end = chunks[k + 1][0]["s"] - self.lead if k + 1 < len(chunks) else c[-1]["e"] + 0.5
            end = min(end, c[-1]["e"] + 0.6)
            self.chunks.append(dict(words=c, s=start, e=end))
        self.cache = {}

    def chunk_masks(self, k):
        if k in self.cache: return self.cache[k]
        c = self.chunks[k]; txt = " ".join(w["w"] for w in c["words"])
        full, base, xs = text_mask(txt, self.f, tracking_px=self.tr, pad=24, track_spaces=False)
        # word spans (x ranges) within the full mask
        spans = []; pos = 0
        for w in c["words"]:
            i0 = txt.index(w["w"], pos); i1 = i0 + len(w["w"]); pos = i1
            x0 = 24 + xs[i0] - 3
            x1 = 24 + xs[i1 - 1] + self.f.getlength(txt[i1 - 1]) + 5
            spans.append((int(x0), int(math.ceil(x1))))
        self.cache[k] = (full, spans); return self.cache[k]

    def layers(self, t):
        if self.hide_fn(t): return []
        for k, c in enumerate(self.chunks):
            if c["s"] <= t < c["e"]:
                full, spans = self.chunk_masks(k)
                M = np.zeros_like(full)
                for w, (x0, x1) in zip(c["words"], spans):
                    u = (t - (w["s"] - self.lead)) / 0.13
                    if u <= 0: continue
                    a = ease_out(u)
                    seg = full[:, x0:x1]
                    if a < 1: seg = blur(seg, 2.5 * (1 - a)) * a
                    M[:, x0:x1] = np.maximum(M[:, x0:x1], seg)
                cy = self.ypos_fn(t)
                return glow_text(M, self.color, W / 2 - full.shape[1] / 2, cy - full.shape[0] / 2)
        return []

class EndCard:
    """White card, SLATE logo darkening in, typewriter line, then the location fading in."""
    def __init__(self, t0, t1, line1, line2):
        self.t0, self.t1, self.line1, self.line2 = t0, t1, line1, line2
        # logo: box + letters S L (lambda) T E
        bw, bh = 430, 158; stroke = 5
        L = np.zeros((bh + 20, bw + 20), np.float32)
        cv2.rectangle(L, (10, 10), (10 + bw, 10 + bh), 1.0, stroke, lineType=cv2.LINE_AA)
        f = font(MONT_L[0], 84, 300)
        letters = ["S", "L", "A", "T", "E"]; adv = []
        im = Image.new("L", L.shape[::-1], 0); d = ImageDraw.Draw(im)
        gap = 30; widths = [f.getlength(ch) for ch in letters]; widths[2] = 62
        total = sum(widths) + gap * 4; x = 10 + (bw - total) / 2
        asc, desc = f.getmetrics(); bbox = f.getbbox("S"); cap = bbox[3] - bbox[1]
        ytop = 10 + (bh - cap) / 2 - bbox[1]
        for ch, wd in zip(letters, widths):
            if ch == "A":
                x0, x1 = x, x + wd; yb = 10 + (bh + cap) / 2; yt = yb - cap
                lw = 5
                cv2.line(L, (int(x0), int(yb)), (int((x0 + x1) / 2), int(yt)), 1.0, lw, cv2.LINE_AA)
                cv2.line(L, (int((x0 + x1) / 2), int(yt)), (int(x1), int(yb)), 1.0, lw, cv2.LINE_AA)
            else:
                d.text((x, ytop), ch, font=f, fill=255)
            x += wd + gap
        L = np.maximum(L, np.asarray(im, np.float32) / 255.0)
        self.logo = L; self.lx = W / 2 - L.shape[1] / 2; self.ly = 0.455 * H - L.shape[0] / 2
        self.f1 = font(MONT[0], 34, 400)
        self.m1, _, self.xs1 = text_mask(line1, self.f1, pad=10)
        self.m2, _, _ = text_mask(line2, self.f1, pad=10)

    def background(self, t):
        return t0_le(self.t0, t) and t < self.t1

    def layers(self, t):
        if t < self.t0 or t >= self.t1: return []
        lt = t - self.t0; out = []
        # logo: light grey -> near black
        u = ease_inout(lt / 1.7)
        g = 0.82 - 0.70 * u
        lay = solid_layer(self.logo, "#000000", self.lx, self.ly); lay.rgb[:] = g
        out.append(lay)
        # typewriter line 1 (~20 chars/s)
        n = len(self.line1); k = int(clamp01((lt - 0.05) / (n / 22.0)) * n)
        if k > 0:
            x_cut = int(10 + self.f1.getlength(self.line1[:k]) + 1)
            m = self.m1.copy(); m[:, x_cut:] = 0
            lay = solid_layer(m, "#222222", W / 2 - self.m1.shape[1] / 2, 0.5185 * H); out.append(lay)
        t2 = 0.05 + n / 22.0 + 0.05
        if lt > t2:
            a = ease_out((lt - t2) / 0.35)
            lay = solid_layer(self.m2 * a, "#222222", W / 2 - self.m2.shape[1] / 2, 0.5185 * H + 44); out.append(lay)
        return out

def t0_le(a, b): return a <= b

# ---------------------------------------------------------------- shots
class ShotReader:
    def __init__(self, path, src, nframes, vf_extra=""):
        vf = f"fps={FPS},scale={SRC_W}:{SRC_H}:flags=lanczos" + (("," + vf_extra) if vf_extra else "") + ",format=rgb24"
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{src:.3f}", "-i", path, "-frames:v", str(nframes + 2),
               "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=SRC_W * SRC_H * 3 * 2)
        self.last = None

    def read(self):
        b = self.p.stdout.read(SRC_W * SRC_H * 3)
        if len(b) == SRC_W * SRC_H * 3:
            self.last = np.frombuffer(b, np.uint8).reshape(SRC_H, SRC_W, 3)
        return self.last

    def close(self):
        try:
            self.p.stdout.close(); self.p.kill(); self.p.wait()
        except Exception:
            pass

def view(frame, z, cx, cy):
    cw, ch = SRC_W / z, SRC_H / z
    x0 = min(max(cx * SRC_W - cw / 2, 0), SRC_W - cw); y0 = min(max(cy * SRC_H - ch / 2, 0), SRC_H - ch)
    M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
    return cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_AREA if z < 1.3 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
