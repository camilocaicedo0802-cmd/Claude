"""Time-based overlays drawn on top of shots (kinetic text, captions, logos, stamps...)."""
import math, hashlib
import numpy as np, cv2
from PIL import Image, ImageDraw
from core import (W, H, render_word, blit, ease_out, ease_in, ease_io, clamp01, word_times, font,
                  load_image, rgba_from_bgra_u8, add_glow, STYLES)

MARK = {"*": "r", "~": "script", "^": "lcd", "+": "wb", "!": "rb"}


def _h(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


class Overlay:
    z = 0

    def active(self, t):
        return self.t0 - 0.01 <= t <= self.t1 + 0.01


class Text(Overlay):
    """Kinetic text block. markup: words split by spaces, '/' newline, prefixes * red, ~ script, + white black-italic, ! red black-italic.
    timed=True aligns each word to the narration; otherwise words stagger from t0."""

    def __init__(self, t0, t1, markup, x=W / 2, y=H / 2, size=54, base="w", timed=True, stagger=0.07,
                 align="center", anim="pop", box=False, maxw=1500, jitter=0.07, z=5, exit="fade", tlist=None,
                 script_scale=1.7, upper=True, drift=0.035):
        self.t0, self.t1, self.z = t0, t1, z
        size = size * 1.1
        self.anim, self.box, self.exit, self.drift = anim, box, exit, drift
        lines = [l.split() for l in markup.split("/")]
        flat = [w for l in lines for w in l]
        plain = [w.lstrip("*~^+!") for w in flat]
        if tlist is not None:
            times = tlist
        elif timed:
            times = word_times(plain, t0)
            times = [max(t0, tt - 0.04) for tt in times]
        else:
            times = [t0 + i * stagger for i in range(len(flat))]
        self.items = []
        k = 0
        y_cursor = 0
        line_boxes = []
        for li, line in enumerate(lines):
            row = []
            x_cursor = 0
            lh = 0
            for w in line:
                st = base
                ch = w[0]
                if ch in MARK:
                    st = MARK[ch]
                    w = w[1:]
                sz = size * (script_scale if st == "script" else 1.0)
                txt = w if (st == "script" or not upper) else w.upper()
                img, adv, pad = render_word(txt, st, sz)
                rnd = (_h(w + str(k)) % 1000) / 1000 - 0.5
                row.append(dict(img=img, adv=adv, pad=pad, x=x_cursor, t=times[k], jit=rnd * jitter * size, st=st, sz=sz))
                x_cursor += adv + size * 0.28
                lh = max(lh, sz)
                k += 1
            width = x_cursor - size * 0.28
            line_boxes.append((row, width, y_cursor, lh))
            y_cursor += lh * 1.12
        total_h = y_cursor
        for row, width, ly, lh in line_boxes:
            if align == "center":
                ox = x - width / 2
            elif align == "left":
                ox = x
            else:
                ox = x - width
            for it in row:
                it["X"] = ox + it["x"] - it["pad"]
                # baseline align: scripts sit a bit lower
                it["Y"] = y - total_h / 2 + ly + (lh - it["sz"]) * 0.8 - it["pad"] + it["jit"] + (
                    -it["sz"] * 0.18 if it["st"] == "script" else 0)
                self.items.append(it)
        xs = [it["X"] + it["pad"] for it in self.items]
        xe = [it["X"] + it["pad"] + it["adv"] for it in self.items]
        self.bbox = (min(xs) - size * 0.5, y - total_h / 2 - size * 0.25, max(xe) + size * 0.5, y + total_h / 2 + size * 0.35)

    def draw(self, f, t):
        vis_all = 1.0
        if self.exit == "fade" and t > self.t1 - 0.22:
            vis_all = clamp01((self.t1 - t) / 0.22)
        if vis_all <= 0:
            return
        grow = 1 + self.drift * clamp01((t - self.t0) / max(0.1, self.t1 - self.t0))
        cxb = (self.bbox[0] + self.bbox[2]) / 2
        cyb = (self.bbox[1] + self.bbox[3]) / 2
        if self.box:
            first = min(it["t"] for it in self.items)
            a = 0.6 * vis_all * ease_out((t - first) / 0.25)
            if a > 0:
                x0, y0, x1, y1 = [int(v) for v in self.bbox]
                x0, y0 = max(0, x0 - 20), max(0, y0 - 10)
                x1, y1 = min(W, x1 + 20), min(H, y1 + 10)
                f[y0:y1, x0:x1] *= (1 - a)
        for it in self.items:
            p = (t - it["t"]) / 0.22
            if p < 0:
                continue
            a = ease_out(p) * vis_all
            if self.anim == "slam":
                sc = 1 + 1.3 * (1 - ease_out(p * 1.4))
            elif self.anim == "rise":
                sc = 1.0
            else:
                sc = 1 + 0.32 * (1 - ease_out(p))
            if self.exit == "fade" and t > self.t1 - 0.22:
                sc *= 1 + 0.12 * (1 - vis_all)
            img = it["img"]
            cx = it["X"] + img.shape[1] / 2
            cy = it["Y"] + img.shape[0] / 2 + (18 * (1 - ease_out(p)) if self.anim == "rise" else 0)
            cx = cxb + (cx - cxb) * grow
            cy = cyb + (cy - cyb) * grow
            blit(f, img, 0, 0, opacity=a, scale=sc * grow, cx=cx, cy=cy)


class DateCap(Overlay):
    """Red translucent box with two lines (reference: '2:40 P.M. / 6 MAYO 2010')."""

    def __init__(self, t0, t1, l1, l2, x=95, y=700, z=6):
        self.t0, self.t1, self.z = t0, t1, z
        self.x, self.y = x, y
        self.i1 = render_word(l1, "lcdw", 112)
        self.i2 = render_word(l2.upper(), "w", 72) if l2 else None
        w1 = self.i1[1]
        w2 = self.i2[1] if self.i2 else 0
        self.bw = int(max(w1, w2) + 90)
        self.bh = 240 if l2 else 140
        rng = np.random.default_rng(_h(l1 + l2))
        box = np.zeros((self.bh + 40, self.bw + 40), np.float32)
        cv2.rectangle(box, (20, 20), (20 + self.bw, 20 + self.bh), 1.0, -1)
        noise = rng.random(box.shape).astype(np.float32)
        box = cv2.GaussianBlur(box, (0, 0), 3) * (0.85 + 0.15 * noise)
        self.mask = np.clip(box, 0, 1)

    def draw(self, f, t):
        p = ease_out((t - self.t0) / 0.35)
        vis = clamp01((self.t1 - t) / 0.25)
        a = 0.78 * vis
        if p <= 0 or a <= 0:
            return
        mh, mw = self.mask.shape
        ww = max(1, int(mw * p))
        x0, y0 = self.x - 20, self.y - 20
        sub = self.mask[:, :ww] * a
        ys, xs = slice(max(0, y0), min(H, y0 + mh)), slice(max(0, x0), min(W, x0 + ww))
        m = sub[: ys.stop - ys.start, : xs.stop - xs.start, None]
        red = np.array([0.09, 0.09, 0.78], np.float32)
        f[ys, xs] = f[ys, xs] * (1 - m) + red * m
        ta = clamp01((t - self.t0 - 0.15) / 0.25) * vis
        img, adv, pad = self.i1
        blit(f, img, self.x + 32 - pad, self.y + 6 - pad, opacity=ta)
        if self.i2:
            img, adv, pad = self.i2
            blit(f, img, self.x + 34 - pad, self.y + 128 - pad, opacity=clamp01((t - self.t0 - 0.3) / 0.25) * vis)


class Label(Overlay):
    """Small tracked uppercase label (reference: '1970S PUNJAB, INDIA')."""

    def __init__(self, t0, t1, text, x=W / 2, y=870, size=34, style="label", z=6):
        self.t0, self.t1, self.z = t0, t1, z
        self.img, self.adv, self.pad = render_word(text.upper(), style, size, tracking=0.12)
        self.x, self.y = x, y

    def draw(self, f, t):
        a = ease_out((t - self.t0) / 0.4) * clamp01((self.t1 - t) / 0.3)
        sc = 1 + 0.05 * clamp01((t - self.t0) / (self.t1 - self.t0))
        blit(f, self.img, 0, 0, opacity=a, scale=sc, cx=self.x, cy=self.y)


class Logo(Overlay):
    def __init__(self, t0, t1, path, x=W / 2, y=H / 2, h=420, anim="reveal", glow=None, z=4, white=False, sweep=True):
        self.t0, self.t1, self.z = t0, t1, z
        im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 3:
            im = cv2.cvtColor(im, cv2.COLOR_BGR2BGRA)
        ys, xs = np.where(im[:, :, 3] > 8)
        im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        s = h / im.shape[0]
        im = cv2.resize(im, (int(im.shape[1] * s), int(h)), interpolation=cv2.INTER_AREA)
        img = rgba_from_bgra_u8(im)
        if white:
            a = img[:, :, 3:4]
            lum = img[:, :, :3].mean(-1, keepdims=True) / np.maximum(a, 1e-4)
            # dark parts -> white, colored parts keep
            sat = img[:, :, :3].max(-1, keepdims=True) - img[:, :, :3].min(-1, keepdims=True)
            col = np.where(sat / np.maximum(a, 1e-4) > 0.25, img[:, :, :3], a * 1.0)
            img = np.concatenate([col, a], -1)
        if glow:
            img = add_glow(img, glow[0], glow[1], glow[2] if len(glow) > 2 else None)
        self.img = img
        self.x, self.y, self.anim, self.sweep = x, y, anim, sweep

    def draw(self, f, t):
        d = t - self.t0
        vis = clamp01((self.t1 - t) / 0.3)
        if self.anim == "reveal":
            a = ease_out(d / 0.6) * vis
            sc = 1.18 - 0.18 * ease_out(d / 1.6)
        else:  # pop
            p = clamp01(d / 0.35)
            a = ease_out(p * 1.5) * vis
            sc = 0.55 + 0.45 * ease_out(p) + 0.08 * math.sin(p * math.pi) * (1 - p)
        img = self.img
        if self.sweep and 0.25 < d < 1.5:
            h, w = img.shape[:2]
            u = (d - 0.25) / 1.0
            pos = -0.3 + 1.6 * u
            xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
            yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
            band = np.exp(-(((xx * 0.8 + yy * 0.4) - pos) / 0.08) ** 2) * 0.85
            img = img.copy()
            img[:, :, :3] = img[:, :, :3] + (img[:, :, 3:4] - img[:, :, :3]) * band[:, :, None] * (img[:, :, 3:4] > 0.5)
        blit(f, img, 0, 0, opacity=a, scale=sc, cx=self.x, cy=self.y)


class Stamp(Overlay):
    def __init__(self, t0, t1, text, x=W / 2, y=H / 2, size=120, color=(220, 25, 25), angle=-12, z=7, font_name="anton"):
        self.t0, self.t1, self.z = t0, t1, z
        f = font(font_name, size)
        tw = int(f.getlength(text))
        asc, desc = f.getmetrics()
        bw, bh = tw + int(size * 0.8), asc + desc + int(size * 0.35)
        im = Image.new("L", (bw + 40, bh + 40), 0)
        d = ImageDraw.Draw(im)
        lw = max(6, size // 12)
        d.rectangle([20, 20, 20 + bw, 20 + bh], outline=255, width=lw)
        d.rectangle([20 + lw * 2, 20 + lw * 2, 20 + bw - lw * 2, 20 + bh - lw * 2], outline=255, width=max(2, lw // 3))
        d.text((20 + bw / 2, 20 + bh / 2 + size * 0.04), text, font=f, fill=255, anchor="mm")
        m = np.asarray(im, np.float32) / 255
        rng = np.random.default_rng(_h(text))
        grit = cv2.GaussianBlur(rng.random(m.shape).astype(np.float32), (0, 0), 1.2)
        m = m * np.clip((grit - 0.25) * 2.2, 0.15, 1)
        pad = 60
        m = cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
        R = cv2.getRotationMatrix2D((m.shape[1] / 2, m.shape[0] / 2), angle, 1.0)
        m = cv2.warpAffine(m, R, (m.shape[1], m.shape[0]))
        col = np.array(color[::-1], np.float32) / 255
        self.img = np.concatenate([col * m[:, :, None] * 0.95, m[:, :, None] * 0.95], -1)
        self.x, self.y = x, y

    def draw(self, f, t):
        p = clamp01((t - self.t0) / 0.16)
        vis = clamp01((self.t1 - t) / 0.25)
        sc = 2.4 - 1.4 * ease_in(p)
        a = clamp01(p * 2) * vis
        blit(f, self.img, 0, 0, opacity=a, scale=sc, cx=self.x, cy=self.y)


class Counter(Overlay):
    def __init__(self, t0, t1, v0, v1, ta, tb, fmt, x=W / 2, y=H / 2, size=150, style="lcd", z=6):
        self.t0, self.t1, self.z = t0, t1, z
        self.v0, self.v1, self.ta, self.tb, self.fmt = v0, v1, ta, tb, fmt
        self.x, self.y, self.size, self.style = x, y, size, style

    def draw(self, f, t):
        u = ease_out((t - self.ta) / max(0.01, self.tb - self.ta))
        v = self.v0 + (self.v1 - self.v0) * u
        s = self.fmt(v)
        img, adv, pad = render_word(s, self.style, self.size)
        a = ease_out((t - self.t0) / 0.2) * clamp01((self.t1 - t) / 0.25)
        pulse = 1 + (0.06 * (1 - ease_out((t - self.tb) / 0.3)) if t > self.tb else 0)
        blit(f, img, 0, 0, opacity=a, scale=pulse, cx=self.x, cy=self.y)


class Flash(Overlay):
    def __init__(self, t0, dur=0.25, strength=0.9, color=(1, 1, 1), z=9):
        self.t0, self.t1, self.z = t0, t0 + dur, z
        self.dur, self.s, self.c = dur, strength, np.array(color[::-1], np.float32)

    def draw(self, f, t):
        k = (1 - clamp01((t - self.t0) / self.dur)) ** 2 * self.s
        f[:] = f * (1 - k) + self.c * k


class Darken(Overlay):
    """Darken the frame (for text legibility) with optional blur-free vignette band."""

    def __init__(self, t0, t1, amount=0.45, z=1):
        self.t0, self.t1, self.z, self.a = t0, t1, z, amount

    def draw(self, f, t):
        a = self.a * clamp01((t - self.t0) / 0.3) * clamp01((self.t1 - t) / 0.3)
        f *= (1 - a)
