"""Shot bases, overlays and transitions built on engine.py."""
import functools
import math
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from engine import (BLACK, FPS, H, IMG, RED, STEEL, W, WHITE, YELLOW, Sprite, VideoReader, blend, blurred_bg,
                    clamp, darken, ease_back, ease_in, ease_io, ease_out, fit_into, font, kb_frame, lerp,
                    load_image, over, over_center, prog, rounded_rect_sprite, text_sprite)


# =================================================================== bases
class Base:
    def setup(self, dur):
        self.dur = dur

    def frame(self, t):
        raise NotImplementedError

    def close(self):
        pass


class Still(Base):
    """Ken Burns still. cam = (cx, cy, zoom[, rot])."""

    def __init__(self, path, cam0=(0.5, 0.5, 1.0), cam1=(0.5, 0.5, 1.12), grade="doc", ease="io", shake=0.0):
        self.path, self.cam0, self.cam1, self.g, self.ease, self.shake = path, cam0, cam1, grade, ease, shake

    def frame(self, t):
        src = load_image(self.path, self.g)
        p = t / max(self.dur, 1e-3)
        e = {"io": ease_io, "out": ease_out, "lin": lambda x: clamp(x), "in": ease_in}[self.ease](p)
        c0, c1 = self.cam0, self.cam1
        cx, cy, z = lerp(c0[0], c1[0], e), lerp(c0[1], c1[1], e), lerp(c0[2], c1[2], e)
        rot = lerp(c0[3] if len(c0) > 3 else 0, c1[3] if len(c1) > 3 else 0, e)
        if self.shake:
            cx += math.sin(t * 13.1) * self.shake * 0.004 + math.sin(t * 29.3) * self.shake * 0.002
            cy += math.cos(t * 11.7) * self.shake * 0.004
        return kb_frame(src, cx, cy, z, rot)


class Video(Base):
    def __init__(self, path, start=0.0, speed=1.0, grade="doc", zoom0=1.0, zoom1=1.0, cx=0.5, cy=0.5, reverse=False):
        self.path, self.start, self.speed, self.g = path, start, speed, grade
        self.zoom0, self.zoom1, self.cx, self.cy, self.reverse = zoom0, zoom1, cx, cy, reverse
        self.reader, self.pos = None, -1

    def frame(self, t):
        fi = int(round(t * FPS))
        if self.reader is None or fi < self.pos:
            if self.reader:
                self.reader.close()
            self.reader = VideoReader(self.path, self.start + fi / FPS * self.speed, self.speed, self.g,
                                      reverse=self.reverse)
            self.pos = fi - 1
        fr = None
        while self.pos < fi:
            fr = self.reader.read()
            self.pos += 1
        if fr is None:
            fr = self.reader.last
        z = lerp(self.zoom0, self.zoom1, ease_io(t / max(self.dur, 1e-3)))
        if abs(z - 1) > 1e-3 or self.cx != 0.5 or self.cy != 0.5:
            fr = kb_frame(fr, self.cx, self.cy, z)
        return fr

    def close(self):
        if self.reader:
            self.reader.close()
            self.reader = None


class Framed(Base):
    """Photo inside a white/yellow frame over a blurred or textured background, with optional caption."""

    def __init__(self, path, caption=None, grade="archival", bg="blur", box=(0.78, 0.74), zoom=(1.0, 1.06),
                 tilt=(0.0, 0.0), border=14, border_color=(236, 232, 222), slide=None, sub=None, cy=0.47):
        self.path, self.caption, self.g, self.bgk, self.box = path, caption, grade, bg, box
        self.zoom, self.tilt, self.border, self.bc, self.slide, self.sub, self.cyf = zoom, tilt, border, border_color, slide, sub, cy
        self._sp = None

    def _photo(self):
        if self._sp is None:
            src = load_image(self.path, self.g)
            ph = fit_into(src, int(W * self.box[0]), int(H * self.box[1]))
            b = self.border
            h, w = ph.shape[:2]
            canvas = np.zeros((h + 2 * b + 40, w + 2 * b + 40, 4), np.uint8)
            # shadow
            sh = np.zeros(canvas.shape[:2], np.uint8)
            cv2.rectangle(sh, (20 + 6, 20 + 10), (20 + w + 2 * b + 6, 20 + h + 2 * b + 10), 170, -1)
            sh = cv2.GaussianBlur(sh, (0, 0), 10)
            canvas[..., 3] = sh
            canvas[20:20 + h + 2 * b, 20:20 + w + 2 * b, :3] = self.bc
            canvas[20:20 + h + 2 * b, 20:20 + w + 2 * b, 3] = 255
            canvas[20 + b:20 + b + h, 20 + b:20 + b + w, :3] = ph
            self._sp = Sprite(canvas)
        return self._sp

    def _bg(self, t):
        if self.bgk == "blur":
            bg = blurred_bg(self.path, self.g, 0.38)
            dx = int(30 + 30 * math.sin(t * 0.2))
            return bg[34:34 + H, dx:dx + W].copy()
        return background(self.bgk, t)

    def frame(self, t):
        out = self._bg(t)
        sp = self._photo()
        p = t / max(self.dur, 1e-3)
        z = lerp(self.zoom[0], self.zoom[1], ease_io(p))
        cx, cy = W / 2, H * self.cyf
        a = 1.0
        if self.slide:
            k = ease_out(prog(t, 0, 0.55))
            dx, dy = {"l": (-W, 0), "r": (W, 0), "u": (0, -H), "d": (0, H)}[self.slide]
            cx += dx * (1 - k)
            cy += dy * (1 - k)
        rot = lerp(self.tilt[0], self.tilt[1], ease_io(p))
        if abs(rot) > 0.01:
            sp = rotate_sprite(sp, rot)
        over_center(out, sp, cx, cy, a, z)
        if self.caption:
            k = ease_out(prog(t, 0.35, 0.5))
            cap = text_sprite(self.caption, "bebas", 46, WHITE, True, tracking=2)
            yy = cy + sp.h * z / 2 + 18 - 10 * (1 - k)
            over(out, cap, cx - cap.w / 2, yy - 24, k)
            if self.sub:
                s2 = text_sprite(self.sub, "sans_med", 24, (200, 196, 186), True)
                over(out, s2, cx - s2.w / 2, yy + 26, k)
        return out


def rotate_sprite(sp, deg):
    h, w = sp.h, sp.w
    M = cv2.getRotationMatrix2D((w / 2, h / 2), deg, 1.0)
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(h * sin + w * cos), int(h * cos + w * sin)
    M[0, 2] += nw / 2 - w / 2
    M[1, 2] += nh / 2 - h / 2
    s = Sprite.__new__(Sprite)
    s.rgb = cv2.warpAffine(sp.rgb, M, (nw, nh), flags=cv2.INTER_LINEAR)
    a = cv2.warpAffine(sp.a[..., 0], M, (nw, nh), flags=cv2.INTER_LINEAR)
    s.a = a[..., None]
    s.h, s.w = nh, nw
    return s


@functools.lru_cache(maxsize=8)
def _grid_bg(kind):
    if kind == "dark_grid":
        img = np.full((H + 80, W + 80, 3), (16, 17, 19), np.uint8)
        for x in range(0, W + 80, 60):
            cv2.line(img, (x, 0), (x, H + 80), (34, 36, 40), 1)
        for y in range(0, H + 80, 60):
            cv2.line(img, (0, y), (W + 80, y), (34, 36, 40), 1)
        return img
    if kind == "paper_grid":
        img = np.full((H + 80, W + 80, 3), (236, 232, 222), np.uint8)
        for x in range(0, W + 80, 48):
            cv2.line(img, (x, 0), (x, H + 80), (214, 210, 200), 1)
        for y in range(0, H + 80, 48):
            cv2.line(img, (0, y), (W + 80, y), (214, 210, 200), 1)
        return img
    if kind == "concrete":
        src = load_image("u_tex1.jpg", "dark")
        return cv2.resize(kb_frame(src, 0.5, 0.5, 1.0), (W + 80, H + 80))
    if kind == "black":
        return np.full((H + 80, W + 80, 3), BLACK, np.uint8)
    raise KeyError(kind)


def background(kind, t=0.0):
    bg = _grid_bg(kind)
    dx = int(40 + 30 * math.sin(t * 0.15))
    dy = int(40 + 20 * math.cos(t * 0.11))
    return bg[dy:dy + H, dx:dx + W].copy()


class Solid(Base):
    def __init__(self, kind="black"):
        self.kind = kind

    def frame(self, t):
        return background(self.kind, t)


class Custom(Base):
    """Wrap a function f(t, dur) -> frame."""

    def __init__(self, fn, **kw):
        self.fn, self.kw = fn, kw

    def frame(self, t):
        return self.fn(t, self.dur, **self.kw)


class Seq(Base):
    """Several bases back-to-back inside one shot (fast montage), hard cuts."""

    def __init__(self, parts):
        self.parts = parts  # list of (dur, base)

    def setup(self, dur):
        self.dur = dur
        tot = sum(d for d, _ in self.parts)
        k = dur / tot
        self.parts = [(d * k, b) for d, b in self.parts]
        for d, b in self.parts:
            b.setup(d)

    def frame(self, t):
        acc = 0
        for d, b in self.parts:
            if t < acc + d or b is self.parts[-1][1]:
                return b.frame(t - acc)
            acc += d

    def close(self):
        for _, b in self.parts:
            b.close()


class Split(Base):
    """Side by side panels sliding in."""

    def __init__(self, bases, gap=10, labels=None, vs=False):
        self.bases, self.gap, self.labels, self.vs = bases, gap, labels, vs

    def setup(self, dur):
        self.dur = dur
        for b in self.bases:
            b.setup(dur)

    def frame(self, t):
        out = np.full((H, W, 3), BLACK, np.uint8)
        n = len(self.bases)
        pw = (W - self.gap * (n - 1)) // n
        for i, b in enumerate(self.bases):
            fr = b.frame(t)
            x0 = int(W / 2 - pw / 2)
            panel = fr[:, x0:x0 + pw]
            k = ease_out(prog(t, 0.12 * i, 0.5))
            off = int((1 - k) * (H if i % 2 == 0 else -H))
            x = i * (pw + self.gap)
            y0, y1 = max(0, off), min(H, H + off)
            if y1 > y0:
                out[y0:y1, x:x + pw] = panel[y0 - off:y1 - off]
            if self.labels:
                k2 = ease_out(prog(t, 0.45 + 0.15 * i, 0.4))
                lab = text_sprite(self.labels[i], "bebas", 54, WHITE, True, tracking=2)
                bar = rounded_rect_sprite(lab.w - 28, 64, BLACK, 4, 200)
                cx = x + pw / 2
                over(out, bar, cx - bar.w / 2, H - 150, k2)
                over(out, lab, cx - lab.w / 2, H - 162, k2)
        if self.vs:
            k = ease_back(prog(t, 0.6, 0.35))
            vs = text_sprite("VS", "bebas", 150, YELLOW, True, stroke=4, stroke_color=BLACK)
            over_center(out, vs, W / 2, H / 2, min(1, k * 1.5), max(0.01, k))
        return out

    def close(self):
        for b in self.bases:
            b.close()


# =================================================================== overlays
class Overlay:
    def draw(self, img, t, dur):
        raise NotImplementedError


def fade_env(t, dur, t_in, t_out=None, fin=0.3, fout=0.3):
    if t_out is None:
        t_out = dur
    a = prog(t, t_in, fin)
    b = 1 - prog(t, t_out - fout, fout)
    return min(a, b)


class Badge(Overlay):
    """Top-left location/date pill, e.g. 'PENSILVANIA • 1940'."""

    def __init__(self, text, t0=0.15, t1=None, pos="tl", color=YELLOW):
        self.text, self.t0, self.t1, self.pos, self.color = text, t0, t1, pos, color

    def draw(self, img, t, dur):
        a = fade_env(t, dur, self.t0, self.t1, 0.35, 0.35)
        if a <= 0:
            return
        tx = text_sprite(self.text, "bebas", 40, WHITE, False, tracking=3)
        bw = tx.w - 48 + 70
        pill = rounded_rect_sprite(bw, 58, (12, 12, 14), 29, 205)
        x = 70 if self.pos == "tl" else W - 70 - bw
        y = 62
        k = ease_out(prog(t, self.t0, 0.45))
        x += -30 * (1 - k)
        over(img, pill, x, y, a)
        cv2.circle(img, (int(x + 30), int(y + 29)), 8, self.color, -1, lineType=cv2.LINE_AA)
        over(img, tx, x + 52 - 24, y + 6 - 24 + 2, a)


class Caption(Overlay):
    """Lower caption: Bebas caps with a yellow bar wiping in."""

    def __init__(self, text, sub=None, t0=0.3, t1=None, y=0.86):
        self.text, self.sub, self.t0, self.t1, self.y = text, sub, t0, t1, y

    def draw(self, img, t, dur):
        a = fade_env(t, dur, self.t0, self.t1, 0.3, 0.3)
        if a <= 0:
            return
        tx = text_sprite(self.text, "bebas", 58, WHITE, True, tracking=2)
        k = ease_out(prog(t, self.t0, 0.5))
        y = H * self.y
        x = 110
        bar_w = int((tx.w - 40) * k)
        if bar_w > 2:
            cv2.rectangle(img, (x, int(y + 46)), (x + bar_w, int(y + 52)), YELLOW, -1)
        over(img, tx, x - 24, y - 30, a)
        if self.sub:
            s = text_sprite(self.sub, "sans_med", 28, (215, 210, 200), True)
            over(img, s, x - 24, y + 36, a * ease_out(prog(t, self.t0 + 0.25, 0.4)))


class LowerThird(Overlay):
    def __init__(self, name, role, t0=0.4, t1=None):
        self.name, self.role, self.t0, self.t1 = name, role, t0, t1

    def draw(self, img, t, dur):
        a = fade_env(t, dur, self.t0, self.t1, 0.3, 0.35)
        if a <= 0:
            return
        k = ease_out(prog(t, self.t0, 0.55))
        nm = text_sprite(self.name, "bebas", 64, WHITE, True, tracking=2)
        rl = text_sprite(self.role, "sans_med", 28, (25, 25, 25), False)
        x, y = 100, H - 230
        w = max(nm.w, rl.w + 30) - 30
        cv2.rectangle(img, (x - 18, int(y + 8)), (x - 10, int(y + 120)), YELLOW, -1)
        clip_w = int(w * k)
        if clip_w > 0:
            box = rounded_rect_sprite(rl.w - 18, 46, YELLOW, 3, 255)
            over(img, box, x, y + 76, a)
            over(img, rl, x - 14, y + 68, a)
        over(img, nm, x - 24 - 40 * (1 - k), y - 18, a)


class BigText(Overlay):
    """Single line of large text with an animation."""

    def __init__(self, text, fname="serif", size=110, color=WHITE, pos=(0.5, 0.5), t0=0.0, t1=None,
                 anim="up", stroke=0, tracking=0, shadow=True):
        self.text, self.fname, self.size, self.color, self.pos = text, fname, size, color, pos
        self.t0, self.t1, self.anim, self.stroke, self.tracking, self.shadow = t0, t1, anim, stroke, tracking, shadow

    def draw(self, img, t, dur):
        a = fade_env(t, dur, self.t0, self.t1, 0.25, 0.3)
        if a <= 0:
            return
        sp = text_sprite(self.text, self.fname, self.size, self.color, self.shadow, self.stroke, BLACK, self.tracking)
        cx, cy = W * self.pos[0], H * self.pos[1]
        k = prog(t, self.t0, 0.5)
        sc = 1.0
        if self.anim == "up":
            cy += 40 * (1 - ease_out(k))
        elif self.anim == "pop":
            sc = max(0.05, ease_back(prog(t, self.t0, 0.4)))
        elif self.anim == "zoom":
            sc = lerp(1.0, 1.08, prog(t, self.t0, dur - self.t0))
        elif self.anim == "type":
            n = int(len(self.text) * prog(t, self.t0, max(0.4, len(self.text) * 0.045)))
            if n <= 0:
                return
            sp = text_sprite(self.text[:n], self.fname, self.size, self.color, self.shadow, self.stroke, BLACK, self.tracking)
            full = text_sprite(self.text, self.fname, self.size, self.color, self.shadow, self.stroke, BLACK, self.tracking)
            over(img, sp, cx - full.w / 2, cy - sp.h / 2, a)
            return
        over_center(img, sp, cx, cy, a, sc)


class Rich(Overlay):
    """Kinetic sentence: words appear one by one (optionally at given times); some words highlighted.

    words: list of (text, appear_time, style) style in {"n", "h", "r"} (normal, yellow highlight, red)."""

    def __init__(self, words, x=0.5, y=0.5, maxw=0.62, size=58, align="center", t1=None, panel=False):
        self.words, self.x, self.y, self.maxw, self.size, self.align, self.t1, self.panel = words, x, y, maxw, size, align, t1, panel
        self._layout = None

    def _sprite(self, txt, style):
        if style == "n":
            return text_sprite(txt, "sans", self.size, WHITE, True)
        if style == "r":
            return text_sprite(txt, "sans_bold", self.size, (255, 92, 92), True)
        return text_sprite(txt, "serif_it", int(self.size * 1.04), (16, 16, 16), False)

    def layout(self):
        if self._layout:
            return self._layout
        space = self.size * 0.30
        lines, cur, curw = [], [], 0
        maxw = W * self.maxw
        for i, (txt, tm, st) in enumerate(self.words):
            sp = self._sprite(txt, st)
            w = sp.w - 48 + (16 if st == "h" else 0)
            if cur and curw + space + w > maxw:
                lines.append((cur, curw))
                cur, curw = [], 0
            cur.append((i, sp, w, st, tm))
            curw += (space if curw else 0) + w
        if cur:
            lines.append((cur, curw))
        lh = self.size * 1.42
        tot_h = lh * len(lines)
        y0 = H * self.y - tot_h / 2
        items = []
        for li, (ws, lw) in enumerate(lines):
            if self.align == "center":
                x = W * self.x - lw / 2
            else:
                x = W * self.x
            for (i, sp, w, st, tm) in ws:
                items.append((x, y0 + li * lh, sp, w, st, tm))
                x += w + space
        self._layout = (items, tot_h, max(l for _, l in lines))
        return self._layout

    def draw(self, img, t, dur):
        items, tot_h, mw = self.layout()
        end = self.t1 if self.t1 is not None else dur
        out_a = 1 - prog(t, end - 0.3, 0.3)
        if out_a <= 0:
            return
        if self.panel:
            pa = min(prog(t, items[0][5] - 0.2, 0.3), out_a)
            if pa > 0:
                x0 = int(W * self.x - mw / 2 - 40) if self.align == "center" else int(W * self.x - 40)
                y0 = int(H * self.y - tot_h / 2 - 26)
                pnl = rounded_rect_sprite(mw + 80, tot_h + 52, (10, 10, 12), 8, 170)
                over(img, pnl, x0, y0, pa)
        for (x, y, sp, w, st, tm) in items:
            k = prog(t, tm, 0.28)
            if k <= 0:
                continue
            a = min(ease_out(k), out_a)
            dy = 16 * (1 - ease_out(k))
            if st == "h":
                bw = int((w + 18) * ease_out(prog(t, tm, 0.22)))
                if bw > 2:
                    box = rounded_rect_sprite(bw, int(self.size * 1.18), YELLOW, 4, 255)
                    over(img, box, x - 8, y + self.size * 0.06, out_a)
                over(img, sp, x + 4 - 24, y - 24 + dy * 0.3, a)
            else:
                over(img, sp, x - 24, y - 24 + dy, a)


class Counter(Overlay):
    """Big number counting up with unit label."""

    def __init__(self, v0, v1, fmt="{:,.0f}", label="", t0=0.0, dur=1.4, pos=(0.5, 0.48), size=200, t1=None,
                 color=WHITE, sub=None, prefix=""):
        self.v0, self.v1, self.fmt, self.label, self.t0, self.cd = v0, v1, fmt, label, t0, dur
        self.pos, self.size, self.t1, self.color, self.sub, self.prefix = pos, size, t1, color, sub, prefix

    def draw(self, img, t, dur):
        a = fade_env(t, dur, self.t0, self.t1, 0.2, 0.3)
        if a <= 0:
            return
        k = ease_out(prog(t, self.t0, self.cd))
        v = lerp(self.v0, self.v1, k)
        s = self.prefix + self.fmt.format(v).replace(",", ".")
        sp = text_sprite(s, "bebas", self.size, self.color, True)
        cx, cy = W * self.pos[0], H * self.pos[1]
        full = text_sprite(self.prefix + self.fmt.format(self.v1).replace(",", "."), "bebas", self.size, self.color, True)
        over(img, sp, cx - full.w / 2, cy - sp.h / 2, a)
        if self.label:
            lb = text_sprite(self.label, "bebas", int(self.size * 0.3), YELLOW, True, tracking=4)
            over(img, lb, cx - lb.w / 2, cy + self.size * 0.42, a * ease_out(prog(t, self.t0 + 0.3, 0.4)))
        if self.sub:
            sb = text_sprite(self.sub, "sans_med", 30, (210, 206, 198), True)
            over(img, sb, cx - sb.w / 2, cy + self.size * 0.42 + 64, a * ease_out(prog(t, self.t0 + 0.5, 0.4)))


class Stamp(Overlay):
    def __init__(self, text, t0=0.3, color=RED, pos=(0.5, 0.5), angle=-12, size=120, t1=None):
        self.text, self.t0, self.color, self.pos, self.angle, self.size, self.t1 = text, t0, color, pos, angle, size, t1
        self._sp = None

    def sprite(self):
        if self._sp is None:
            f = font("bebas", self.size)
            tw = int(f.getlength(self.text))
            pad = 40
            im = Image.new("RGBA", (tw + pad * 2 + 40, self.size + pad * 2), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([12, 12, im.width - 12, im.height - 12], radius=14, outline=self.color + (255,), width=9)
            d.text((pad + 20, pad - 4), self.text, font=f, fill=self.color + (255,))
            arr = np.asarray(im).copy()
            rng = np.random.default_rng(3)
            noise = rng.random(arr.shape[:2]) < 0.18
            arr[..., 3][noise] = (arr[..., 3][noise] * 0.25).astype(np.uint8)
            im = Image.fromarray(arr).rotate(self.angle, expand=True, resample=Image.BICUBIC)
            self._sp = Sprite.from_pil(im)
        return self._sp

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        a = fade_env(t, dur, self.t0, self.t1, 0.05, 0.3)
        k = prog(t, self.t0, 0.18)
        sc = lerp(1.9, 1.0, ease_out(k))
        over_center(img, self.sprite(), W * self.pos[0], H * self.pos[1], a * min(1, k * 2), sc)


class TimelineBar(Overlay):
    """Horizontal tick timeline across the screen with a moving year marker (reference style)."""

    def __init__(self, y0, y1, t0=0.2, move=(0.3, 1.6), start_year=None, y=0.82, label_fmt="{}", t1=None):
        self.y0, self.y1, self.t0, self.move, self.y, self.fmt, self.t1 = y0, y1, t0, move, y, label_fmt, t1
        self.start_year = start_year if start_year is not None else y0

    def draw(self, img, t, dur):
        a = fade_env(t, dur, self.t0, self.t1, 0.3, 0.3)
        if a <= 0:
            return
        yy = int(H * self.y)
        span = self.y1 - self.y0
        layer = img.copy()
        x0, x1 = 120, W - 120
        n = 60
        for i in range(n + 1):
            x = int(x0 + (x1 - x0) * i / n)
            hh = 26 if i % 10 == 0 else 12
            cv2.line(layer, (x, yy - hh), (x, yy + hh), (235, 235, 235), 3 if i % 10 == 0 else 2, lineType=cv2.LINE_AA)
        k = ease_io(prog(t, self.move[0], self.move[1]))
        year = lerp(self.start_year, self.y1, k)
        xm = int(x0 + (x1 - x0) * (year - self.y0) / span)
        cv2.line(layer, (xm, yy - 46), (xm, yy + 46), YELLOW, 6, lineType=cv2.LINE_AA)
        img[:] = cv2.addWeighted(layer, a, img, 1 - a, 0)
        lab = text_sprite(self.fmt.format(int(round(year))), "bebas", 54, BLACK, False)
        box = rounded_rect_sprite(lab.w - 20, 62, YELLOW, 6, 255)
        over(img, box, xm - box.w / 2, yy - 128, a)
        over(img, lab, xm - lab.w / 2, yy - 132, a)


class CCTV(Overlay):
    """Security-camera look: monochrome green-grey, REC dot, running timestamp, scanlines."""

    def __init__(self, cam="CAM 03", place="LAUREL HILL · PORTAL OESTE", start="2026-01-14 02:47:"):
        self.cam, self.place, self.start = cam, place, start

    def draw(self, img, t, dur):
        g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        g = cv2.equalizeHist(g)
        g = (g.astype(np.float32) * 0.85 + 18)
        lines = (np.arange(H) % 4 < 2).astype(np.float32)[:, None] * 0.12
        g = g * (1 - lines)
        rng = np.random.default_rng(int(t * 30))
        g += rng.normal(0, 9, (H // 4, W // 4)).repeat(4, 0).repeat(4, 1)
        g = np.clip(g, 0, 255).astype(np.uint8)
        img[:] = np.stack([g * 0.86, g * 1.0, g * 0.88], -1).clip(0, 255).astype(np.uint8)
        sec = int(t) % 60
        fr = int((t % 1) * 30)
        ts = f"{self.start}{sec:02d}:{fr:02d}"
        for sp, x, y in [(text_sprite(self.cam, "mono", 40, WHITE, False), 70, 50),
                         (text_sprite(ts, "mono", 34, WHITE, False), W - 640, 50),
                         (text_sprite(self.place, "mono", 30, WHITE, False), 70, H - 110)]:
            over(img, sp, x, y)
        if int(t * 2) % 2 == 0:
            cv2.circle(img, (W - 120, H - 80), 14, (230, 40, 40), -1, lineType=cv2.LINE_AA)
            over(img, text_sprite("REC", "mono", 34, WHITE, False), W - 250, H - 112)
        c = (220, 220, 220)
        for (x, y, dx, dy) in [(40, 40, 1, 1), (W - 40, 40, -1, 1), (40, H - 40, 1, -1), (W - 40, H - 40, -1, -1)]:
            cv2.line(img, (x, y), (x + 60 * dx, y), c, 3)
            cv2.line(img, (x, y), (x, y + 60 * dy), c, 3)


class Callout(Overlay):
    """Line from a point to a label (reference style)."""

    def __init__(self, px, py, lx, ly, text, t0=0.3, t1=None, color=YELLOW):
        self.p, self.l, self.text, self.t0, self.t1, self.color = (px, py), (lx, ly), text, t0, t1, color

    def draw(self, img, t, dur):
        a = fade_env(t, dur, self.t0, self.t1, 0.2, 0.3)
        if a <= 0:
            return
        k = ease_out(prog(t, self.t0, 0.45))
        p = (int(W * self.p[0]), int(H * self.p[1]))
        l = (int(W * self.l[0]), int(H * self.l[1]))
        e = (int(lerp(p[0], l[0], k)), int(lerp(p[1], l[1], k)))
        cv2.circle(img, p, 9, self.color, -1, lineType=cv2.LINE_AA)
        cv2.circle(img, p, int(16 + 8 * math.sin(t * 5)), self.color, 2, lineType=cv2.LINE_AA)
        cv2.line(img, p, e, self.color, 3, lineType=cv2.LINE_AA)
        if k > 0.95:
            lab = text_sprite(self.text, "sans_bold", 34, (15, 15, 15), False)
            box = rounded_rect_sprite(lab.w - 28, 54, self.color, 4, 255)
            bx = l[0] - (box.w if l[0] < p[0] else 0)
            over(img, box, bx, l[1] - 27, a)
            over(img, lab, bx - 10, l[1] - 27 - 22, a)


class Flash(Overlay):
    """Quick white/black flash inside a shot (e.g. impact)."""

    def __init__(self, t0, dur=0.18, color=(255, 255, 255), peak=0.85):
        self.t0, self.d, self.color, self.peak = t0, dur, color, peak

    def draw(self, img, t, dur):
        if self.t0 <= t <= self.t0 + self.d:
            k = 1 - (t - self.t0) / self.d
            col = np.full_like(img, self.color)
            img[:] = cv2.addWeighted(col, k * self.peak, img, 1 - k * self.peak, 0)


class Darken(Overlay):
    def __init__(self, k=0.55, t0=0.0, ramp=0.4, t1=None):
        self.k, self.t0, self.ramp, self.t1 = k, t0, ramp, t1

    def draw(self, img, t, dur):
        a = fade_env(t, dur, self.t0, self.t1, self.ramp, 0.3) if self.t1 else prog(t, self.t0, self.ramp)
        if a > 0:
            img[:] = darken(img, 1 - (1 - self.k) * a)


class FnOverlay(Overlay):
    def __init__(self, fn, **kw):
        self.fn, self.kw = fn, kw

    def draw(self, img, t, dur):
        self.fn(img, t, dur, **self.kw)


# =================================================================== transitions
def whip(a, b, k, direction=1):
    """Whip pan from frame a to b, k in 0..1."""
    e = ease_io(k)
    off = int(e * W) * direction
    out = np.empty_like(a)
    if direction > 0:
        out[:, :W - off] = a[:, off:]
        out[:, W - off:] = b[:, :off]
    else:
        off = -off
        out[:, off:] = a[:, :W - off]
        out[:, :off] = b[:, W - off:]
    blur = int(1 + 120 * math.sin(math.pi * k))
    if blur > 2:
        out = cv2.blur(out, (blur, 1))
    return out


def zoom_through(a, b, k):
    if k < 0.5:
        e = ease_in(k * 2)
        z = 1 + e * 0.6
        fr = kb_frame(a, 0.5, 0.5, z)
        r = int(1 + e * 18)
        fr = cv2.blur(fr, (r, r))
        return blend(fr, np.full_like(fr, 255), e * 0.25)
    e = ease_out((k - 0.5) * 2)
    z = 1.6 - e * 0.6
    fr = kb_frame(b, 0.5, 0.5, z)
    r = int(1 + (1 - e) * 18)
    fr = cv2.blur(fr, (r, r))
    return blend(fr, np.full_like(fr, 255), (1 - e) * 0.25)


def glitch(a, b, k):
    base = a if k < 0.5 else b
    out = base.copy()
    rng = np.random.default_rng(int(k * 1000))
    sh = int(30 * math.sin(math.pi * k))
    out[..., 0] = np.roll(base[..., 0], sh, 1)
    out[..., 2] = np.roll(base[..., 2], -sh, 1)
    for _ in range(6):
        y = int(rng.uniform(0, H - 40))
        h = int(rng.uniform(8, 60))
        out[y:y + h] = np.roll(out[y:y + h], int(rng.uniform(-120, 120)), 1)
    return out


def transition(kind, a, b, k):
    if kind == "fade":
        return blend(a, b, ease_io(k))
    if kind == "black":
        if k < 0.5:
            return darken(a, 1 - ease_io(k * 2))
        return darken(b, ease_io((k - 0.5) * 2))
    if kind == "flash":
        base = a if k < 0.5 else b
        w = 1 - abs(k - 0.5) * 2
        return blend(base, np.full_like(base, 255), w ** 1.5 * 0.9)
    if kind == "whip_l":
        return whip(a, b, k, 1)
    if kind == "whip_r":
        return whip(a, b, k, -1)
    if kind == "zoom":
        return zoom_through(a, b, k)
    if kind == "glitch":
        return glitch(a, b, k)
    return b if k >= 0.5 else a
