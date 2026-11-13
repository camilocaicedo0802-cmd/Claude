"""On-screen graphics for reel 2 + the SFX events they trigger (typing on every text, other hits on key words)."""
import json, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import gfx as G
from gfx import El, title, ORANGE, ORANGE_L
from core import ROOT, WEST, ease_out_cubic, ease_in_cubic, ease_out_back, clamp
import timeline as T

WORDS = json.load(open(ROOT + 'felix/words.json'))
EARLY = 0.05
SFX = []          # (time, kind, gain_db)


def sfx(t, kind, gain=0.0):
    SFX.append((round(t, 3), kind, gain))


def wt(k, i):
    """timeline time of word i of voice clip k."""
    clip, si, so, tp = T.VOICE[k]
    name = clip.split('/')[-1].replace('.MOV', '.wav')
    w = WORDS[name]['words'][i]
    return round(max(tp, tp + w['s'] - si - EARLY), 3)


# ------------------------------------------------------------------ typed text
class Typed:
    """one line of text typed letter by letter (stepwise reveal + cursor), then optional exit."""

    def __init__(self, text, t_in, t_out, cy, size=120, fname='black', grad=None, cx=540, rate=0.034,
                 tracking=-45, cursor=True, sound=True, gain=0.0, d_out=0.18, pop=False, rot=0.0, fill=(255, 255, 255)):
        self.t_in, self.t_out, self.cy, self.cx, self.rate, self.d_out = t_in, t_out, cy, cx, rate, d_out
        self.cursor, self.pop, self.rot = cursor, pop, rot
        f = G.font(fname, size)
        img, base = G.text_rgba(text, fname, size, tracking=tracking, grad=grad, fill=fill)
        self.spr = G.with_shadow(img, radius=16, offset=(0, 8), opacity=0.55)
        pad = 48                                   # with_shadow padding (radius*3)
        # x cut-off (in sprite coords) after each letter, from kerned prefix widths
        track = size * tracking / 1000.0
        left0 = pad + 2
        ink0 = G.font(fname, size).getbbox(text)[0]
        cuts = []
        for k in range(1, len(text) + 1):
            cuts.append(left0 + f.getlength(text[:k]) + track * (k - 1) - ink0 + 2)
        self.cuts = cuts
        self.text = text
        self.n = len(text)
        self.h = size
        if sound:
            for k, ch in enumerate(text):
                if ch != ' ':
                    sfx(t_in + k * rate, 'key', gain - 2.0 * (k % 2))
        self.t_done = t_in + self.n * rate

    def active(self, t):
        return self.t_in <= t < self.t_out + self.d_out

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        k = int((t - self.t_in) / self.rate) + 1 if self.rate > 0 else self.n
        k = min(self.n, k)
        right = self.cuts[k - 1] if k < self.n else 1e9
        op, sc, bl, dy = 1.0, 1.0, 0.0, 0.0
        if self.pop:
            a = t - self.t_in
            sc = 0.5 + 0.5 * ease_out_back(a / 0.22, 2.2); op = clamp(a / 0.06); right = 1e9
        if t >= self.t_out:
            q = (t - self.t_out) / self.d_out
            op *= 1 - q; bl = 14 * q; dy = -25 * ease_in_cubic(q); sc *= 1 + 0.03 * q
        h, w = self.spr.shape[:2]
        x0 = self.cx - w * sc / 2

        def mfn(X0, Y0, X1, Y1):
            xs = (np.arange(X0, X1, dtype=np.float32) - x0) / sc
            return np.repeat(np.clip(right - xs + 0.5, 0, 1)[None, :], Y1 - Y0, 0)

        box = G.blit(canvas, self.spr, self.cx, self.cy + dy, sc, self.rot, op, bl, mask_fn=None if right > w else mfn)
        if self.cursor and t < self.t_done + 0.35 and not self.pop and t < self.t_out:
            on = t < self.t_done or int((t - self.t_done) / 0.17) % 2 == 0
            if on:
                cx = x0 + min(right, self.cuts[-1]) * sc + 10
                hh = self.h * 0.78
                y0 = int(self.cy - hh / 2); y1 = int(self.cy + hh / 2)
                X0, X1 = int(cx), int(cx + max(6, self.h * 0.07))
                canvas[y0:y1, X0:X1] = np.array([ORANGE[2], ORANGE[1], ORANGE[0]], np.float32)


class Caption:
    """dynamic subtitles: thick words typed in one by one; keywords bigger, orange, with a pop."""

    def __init__(self, words, t_end, cy=1430, size=66, gap=0.27, max_w=960):
        self.t_end, self.cy = t_end, cy
        items = []
        for txt, st, ton in words:
            key = st == 'o'
            sz = int(size * (1.18 if key else 1.0))
            img, base = G.text_rgba(txt, 'black' if key else 'bold', sz, tracking=-40,
                                    grad=(ORANGE_L, ORANGE) if key else None)
            items.append((txt, img, base, ton, key, sz))
            sfx(ton, 'key', -1.0)
            if key:
                sfx(ton, 'pop', -4.0)
        space = size * gap
        tot = sum(i[1].width for i in items) + space * (len(items) - 1)
        sc = min(1.0, max_w / tot)
        x = 540 - tot * sc / 2
        self.els = []
        for txt, img, base, ton, key, sz in items:
            spr = G.with_shadow(img, radius=10, offset=(0, 5), opacity=0.85, glow=((0, 0, 0), 18, 0.4))
            w = img.width * sc
            cy = self.cy + (img.height / 2 - base) * sc
            self.els.append(El(spr, x + w / 2, cy, ton, t_end, anim_in='pop' if key else 'rise', anim_out='cut',
                               d_in=0.16 if key else 0.1, d_out=0.0, dy=26, scale=sc))
            x += w + space * sc
        self.t0 = min(e.t_in for e in self.els)

    def active(self, t):
        return self.t0 <= t < self.t_end

    def draw(self, canvas, t, base=None, mask=None):
        if self.active(t):
            for e in self.els:
                e.draw(canvas, t)


class Pill:
    """orange label pill, wiped in left -> right."""

    def __init__(self, text, t_in, t_out, cy, cx=540, size=50, typing=True):
        self.t_in, self.t_out, self.cy, self.cx = t_in, t_out, cy, cx
        img, _ = G.text_rgba(text, 'bold', size, tracking=-10)
        self.txt = G.pil_to_spr(img, shadow=False)
        self.w = img.width + 64; self.h = img.height + 36
        self.mask = G.rounded_mask(int(self.w), int(self.h), 16)
        if typing:
            for k in range(min(6, len(text))):
                sfx(t_in + 0.03 + k * 0.045, 'key', -6)

    def active(self, t):
        return self.t_in <= t < self.t_out + 0.25

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        p = ease_out_cubic((t - self.t_in) / 0.28)
        op = 1.0 if t < self.t_out else 1 - clamp((t - self.t_out) / 0.25)
        x0 = int(self.cx - self.w / 2); y0 = int(self.cy - self.h / 2)
        right = x0 + self.w * p
        X1 = int(min(right, x0 + self.w))
        if X1 > x0:
            # soft shadow
            reg = canvas[y0 + 8:y0 + 8 + self.h, x0:X1]
            sh = cv2.GaussianBlur(self.mask, (0, 0), 10)[:reg.shape[0], :X1 - x0, None] * 0.35 * op
            canvas[y0 + 8:y0 + 8 + self.h, x0:X1] = reg * (1 - sh)
            reg = canvas[y0:y0 + self.h, x0:X1]
            m = self.mask[:reg.shape[0], :X1 - x0, None] * op
            canvas[y0:y0 + self.h, x0:X1] = reg * (1 - m) + np.array([ORANGE[2], ORANGE[1], ORANGE[0]], np.float32) * m

        def mfn(A, B, C, D):
            xs = np.arange(A, C, dtype=np.float32)
            return np.repeat(np.clip((right - 14 - xs) / 20, 0, 1)[None, :], D - B, 0)

        G.blit(canvas, self.txt, self.cx, self.cy, opacity=op, mask_fn=None if p >= 0.999 else mfn)


class Checklist:
    """MIRRORS / LIGHTING / VANITY rows with check boxes that tick on each word."""

    def __init__(self, rows, t_out, x0=250, y0=650, step=150):
        self.t_out, self.rows = t_out, []
        for k, (txt, ton) in enumerate(rows):
            ty = Typed(txt, ton, t_out, y0 + k * step, size=96, fname='black', cx=0, rate=0.028, cursor=False, gain=-3)
            ty.cx = x0 + 120 + ty.spr.shape[1] / 2 - 48
            self.rows.append((ty, ton, y0 + k * step))
            sfx(ton + 0.08, 'click', -3)
        self.x0 = x0

    def active(self, t):
        return any(r[0].active(t) for r in self.rows)

    def draw(self, canvas, t, base=None, mask=None):
        for ty, ton, y in self.rows:
            if not ty.active(t):
                continue
            op = 1.0 if t < self.t_out else 1 - clamp((t - self.t_out) / 0.18)
            # box
            s = 74; x = self.x0; yy = int(y - s / 2)
            a = clamp((t - ton) / 0.1) * op
            col = np.array([255, 255, 255], np.float32)
            reg = canvas[yy:yy + s, x:x + s]
            ring = np.zeros((s, s), np.float32); cv2.rectangle(ring, (3, 3), (s - 4, s - 4), 1.0, 6, cv2.LINE_AA)
            if t >= ton + 0.08:
                fill = np.zeros((s, s), np.float32); cv2.rectangle(fill, (0, 0), (s - 1, s - 1), 1.0, -1)
                reg[:] = reg * (1 - fill[..., None] * a) + np.array([ORANGE[2], ORANGE[1], ORANGE[0]], np.float32) * fill[..., None] * a
                p = clamp((t - ton - 0.08) / 0.12)
                ck = np.zeros((s, s), np.float32)
                pts = [(16, 38), (31, 53), (58, 22)]
                if p > 0:
                    m1 = min(1.0, p * 2)
                    cv2.line(ck, pts[0], (int(pts[0][0] + (pts[1][0] - pts[0][0]) * m1), int(pts[0][1] + (pts[1][1] - pts[0][1]) * m1)), 1.0, 8, cv2.LINE_AA)
                    if p > 0.5:
                        m2 = (p - 0.5) * 2
                        cv2.line(ck, pts[1], (int(pts[1][0] + (pts[2][0] - pts[1][0]) * m2), int(pts[1][1] + (pts[2][1] - pts[1][1]) * m2)), 1.0, 8, cv2.LINE_AA)
                reg[:] = reg * (1 - ck[..., None] * a) + col * ck[..., None] * a
            else:
                reg[:] = reg * (1 - ring[..., None] * a) + col * ring[..., None] * a
            ty.draw(canvas, t)


class Stamp:
    """OUTDATED: slams in rotated with an orange frame."""

    def __init__(self, text, t_in, t_out, cy=820, size=150):
        self.t_in, self.t_out, self.cy = t_in, t_out, cy
        img, _ = G.text_rgba(text, 'black', size, tracking=-40, grad=(ORANGE_L, ORANGE))
        pad = 34
        box = Image.new('RGBA', (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
        d = ImageDraw.Draw(box)
        d.rounded_rectangle((4, 4, box.width - 5, box.height - 5), 18, outline=ORANGE + (255,), width=12)
        box.alpha_composite(img, (pad, pad))
        self.spr = G.with_shadow(box, radius=18, offset=(0, 10), opacity=0.55)
        sfx(t_in, 'stamp', 0)

    def active(self, t):
        return self.t_in <= t < self.t_out + 0.2

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        a = t - self.t_in
        sc = 1.0 + 0.7 * (1 - ease_out_cubic(a / 0.14)) if a < 0.14 else 1.0 + 0.04 * math.exp(-(a - 0.14) * 10) * math.cos((a - 0.14) * 30)
        op = clamp(a / 0.05)
        if t >= self.t_out:
            op *= 1 - clamp((t - self.t_out) / 0.2)
        shake = 10 * math.exp(-a * 14) * math.sin(a * 90)
        G.blit(canvas, self.spr, 540 + shake, self.cy, sc, -8.0, op, 0.0)


class LogoPill:
    """dark glass pill: orange circle with the isotype -> expands -> West Home Improvement."""

    def __init__(self, t_in, t_out, cy=1180):
        self.t_in, self.t_out, self.cy = t_in, t_out, cy
        self.h, self.w = 150, 820
        icon = G.load_logo(WEST + 'raw/brand/WEST HOME/PNG/Recurso 3@4x.png', 74)
        circ = Image.new('RGBA', (118, 118), (0, 0, 0, 0))
        ImageDraw.Draw(circ).ellipse((0, 0, 117, 117), fill=ORANGE + (255,))
        circ.alpha_composite(icon, ((118 - icon.width) // 2, (118 - icon.height) // 2))
        self.circ = G.pil_to_spr(circ, shadow=False)
        t1, _ = G.text_rgba('West Home Improvement', 'semi', 46, tracking=-30)
        t2, _ = G.text_rgba('Shower transformations  ·  Tulsa, OK', 'light', 30, tracking=-15)
        self.t1 = G.pil_to_spr(t1, shadow=False); self.t2 = G.pil_to_spr(t2, shadow=False)
        sfx(t_in, 'pop', -3); sfx(t_in + 0.18, 'swoosh', -8)

    def active(self, t):
        return self.t_in <= t < self.t_out + 0.35

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        a = t - self.t_in; h = self.h
        if t < self.t_out:
            s_c = ease_out_back(a / 0.22, 2.0); wexp = ease_out_cubic((a - 0.16) / 0.32); txt = ease_out_cubic((a - 0.36) / 0.3)
        else:
            b = t - self.t_out
            txt = 1 - ease_out_cubic(b / 0.14); wexp = 1 - ease_out_cubic((b - 0.08) / 0.18); s_c = 1 - ease_in_cubic((b - 0.22) / 0.13)
        if s_c <= 0.01:
            return
        w = h + (self.w - h) * clamp(wexp); hh = h * clamp(s_c, 0, 1.2)
        x0 = 540 - w / 2; y0 = self.cy - hh / 2
        G.glass(canvas, x0, y0, w, hh, int(hh / 2), tint=0.04, blur=26, border=0.35, dark=0.5)
        G.blit(canvas, self.circ, x0 + h / 2, self.cy, scale=clamp(s_c, 0, 1.2))
        if txt > 0.01:
            tx0 = x0 + h + 8; right = tx0 + (w - h - 30) * txt

            def mfn(X0, Y0, X1, Y1, right=right):
                xs = np.arange(X0, X1, dtype=np.float32)
                return np.repeat(np.clip((right - xs) / 30, 0, 1)[None, :], Y1 - Y0, 0)

            G.blit(canvas, self.t1, tx0 + self.t1.shape[1] / 2, self.cy - 22, mask_fn=mfn)
            G.blit(canvas, self.t2, tx0 + self.t2.shape[1] / 2, self.cy + 30, opacity=0.85, mask_fn=mfn)


class Fade:
    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1

    def active(self, t):
        return t >= self.t0

    def draw(self, canvas, t, base=None, mask=None):
        canvas *= 1 - clamp((t - self.t0) / (self.t1 - self.t0 - 0.04))


class Scrim:
    def __init__(self, t0, t1, y0, y1, strength=0.4, fade=0.12):
        self.t0, self.t1, self.s, self.f = t0, t1, strength, fade
        yy = np.arange(T.H, dtype=np.float32); c = (y0 + y1) / 2; hw = (y1 - y0) / 2
        self.prof = (np.clip(1 - np.abs(yy - c) / (hw * 1.5), 0, 1) ** 1.3)[:, None, None]

    def active(self, t):
        return self.t0 <= t < self.t1

    def draw(self, canvas, t, base=None, mask=None):
        k = min(clamp((t - self.t0) / self.f), clamp((self.t1 - t) / self.f))
        canvas *= 1 - self.prof * self.s * k


def build():
    SFX.clear()
    E = []
    O = lambda s: (ORANGE_L, ORANGE)
    # ================================================================ HOOK
    E.append(Scrim(0.0, 2.82, 160, 760, 0.35))
    E.append(Pill('TULSA HOMEOWNERS', 0.05, 2.70, 205, size=46))
    E.append(Typed('YOUR BATHROOM', 0.22, 2.74, 360, size=104))
    E.append(Typed("ISN'T THE", 0.72, 2.74, 482, size=104))
    t3 = 1.06
    E.append(Typed('PROBLEM…', t3, 2.74, 615, size=124, grad=(ORANGE_L, ORANGE)))
    sfx(t3 + 8 * 0.034, 'bass', -6)
    # ================================================================ Your shower might be the problem
    E.append(Scrim(2.82, 4.90, 260, 700, 0.35))
    E.append(Typed('YOUR', 2.92, 4.86, 400, size=104, rate=0.04))
    E.append(Typed('SHOWER', wt(1, 1), 4.86, 540, size=168, grad=(ORANGE_L, ORANGE), pop=True, sound=False))
    sfx(wt(1, 1), 'key', 0); sfx(wt(1, 1), 'bass', -4); sfx(wt(1, 1), 'pop', -2)
    E.append(Caption([('might', 'b', wt(1, 2)), ('be', 'b', wt(1, 3)), ('the', 'b', wt(1, 4)), ('problem.', 'o', wt(1, 5))], 4.86))
    # ================================================================ Think about it. You can change...
    E.append(Caption([('Think', 'b', wt(2, 0)), ('about', 'b', wt(2, 1)), ('it.', 'b', wt(2, 2))], wt(2, 3)))
    E.append(Caption([('You', 'b', wt(2, 3)), ('can', 'b', wt(2, 4)), ('change', 'b', wt(2, 5))], T.ba(12)))
    E.append(Scrim(T.ba(12), T.ba(16), 520, 1040, 0.42))
    E.append(Checklist([('MIRRORS', wt(2, 6)), ('LIGHTING', wt(2, 7)), ('VANITY', 8.28)], T.ba(16) - 0.1, y0=640))
    # ================================================================ But your shower still might look like it's from the 1990s
    E.append(Caption([('But', 'b', wt(3, 0)), ('your', 'b', wt(3, 1)), ('shower', 'o', wt(3, 2))], wt(3, 3)))
    E.append(Caption([('still', 'b', wt(3, 3)), ('might', 'b', wt(3, 4)), ('look', 'b', wt(3, 5))], wt(3, 6)))
    E.append(Caption([('like', 'b', wt(3, 6)), ("it's", 'b', wt(3, 7)), ('from', 'b', wt(3, 8)), ('the', 'b', wt(3, 9))], 11.76))
    # retro freeze
    E.append(Typed('1990s', 11.80, 12.80, 250, size=200, grad=((255, 214, 120), ORANGE), rate=0.05, rot=-4))
    sfx(11.76, 'shutter', 0); sfx(11.76, 'film', -6); sfx(11.80, 'flash', -6)
    E.append(VHS(11.80, 12.85))
    # ================================================================ The whole bathroom might feel outdated
    E.append(Caption([('The', 'b', wt(4, 0) + 0.1), ('whole', 'b', wt(4, 1)), ('bathroom', 'b', wt(4, 2))], wt(4, 3)))
    E.append(Caption([('might', 'b', wt(4, 3)), ('feel', 'b', wt(4, 4))], wt(4, 5)))
    E.append(Stamp('OUTDATED', wt(4, 5), 15.34, cy=860))
    # ================================================================ That's why we're focusing on shower transformations
    E.append(Caption([("That's", 'b', wt(5, 0)), ('why', 'b', wt(5, 1)), ("we're", 'b', wt(5, 2))], wt(5, 4)))
    E.append(Caption([('focusing', 'b', wt(5, 4)), ('on', 'b', wt(5, 5)), ('shower', 'o', wt(5, 6))], T.REVEAL - 0.1))
    E.append(Pill('BEFORE', 16.70, T.REVEAL - 0.12, 230, size=44, typing=False))
    sfx(16.70, 'key', -4)
    E.append(Pill('AFTER', T.REVEAL + 0.12, T.bb(18) - 0.05, 230, size=44, typing=False))
    sfx(T.REVEAL + 0.12, 'key', -4)
    E.append(Scrim(T.REVEAL, T.bb(18), 640, 980, 0.38))
    E.append(Typed('SHOWER', T.REVEAL + 0.02, T.bb(18) - 0.1, 735, size=92, rate=0.025, cursor=False, gain=-3))
    E.append(Typed('TRANSFORMATION', T.REVEAL, T.bb(18) - 0.1, 860, size=104, grad=(ORANGE_L, ORANGE), pop=True, sound=False))
    sfx(T.REVEAL - 0.16, 'swoosh', -2); sfx(T.REVEAL, 'impact', 0)
    # ================================================================ That makes a real difference
    E.append(Caption([('That', 'b', wt(6, 0) + 0.15), ('makes', 'b', wt(6, 1)), ('a', 'b', wt(6, 2))], wt(6, 3)))
    E.append(Caption([('real', 'b', wt(6, 3)), ('difference.', 'o', wt(6, 4))], 20.07))
    # ================================================================ From modern glass doors
    E.append(Caption([('From', 'b', wt(7, 0) + 0.55), ('modern', 'b', wt(7, 1))], wt(7, 2)))
    E.append(Scrim(wt(7, 2), 21.70, 560, 960, 0.38))
    E.append(Typed('GLASS', wt(7, 2), 21.70, 700, size=150, rate=0.04))
    E.append(Typed('DOORS', wt(7, 3), 21.70, 850, size=150, grad=(ORANGE_L, ORANGE), rate=0.04))
    sfx(wt(7, 2), 'glass', -6)
    # ================================================================ To beautiful finishes
    E.append(Caption([('To', 'b', wt(8, 0)), ('beautiful', 'b', wt(8, 1))], wt(8, 2)))
    E.append(Scrim(wt(8, 2), T.bb(27) - 0.05, 640, 920, 0.38))
    E.append(Typed('FINISHES', wt(8, 2), T.bb(27) - 0.12, 780, size=150, grad=(ORANGE_L, ORANGE), rate=0.035))
    sfx(wt(8, 2) + 0.3, 'shine', -6)
    # ================================================================ new shower catalog (no voice)
    tc = T.bb(27)
    E.append(Scrim(tc, 26.0, 240, 760, 0.42))
    E.append(Pill('NEW', tc + 0.05, 25.72, 300, size=44))
    E.append(Typed('SHOWER', tc + 0.25, 25.78, 450, size=140, rate=0.035))
    E.append(Typed('CATALOG', tc + 0.55, 25.78, 600, size=140, grad=(ORANGE_L, ORANGE), rate=0.035))
    E.append(Caption([('find', 'b', T.bb(29)), ('your', 'b', T.bb(29) + 0.25), ('style', 'o', T.bb(29) + 0.5)], 25.45))
    E.append(Caption([('easier', 'b', 25.45), ('than', 'b', 25.62), ('ever', 'b', 25.78)], 26.0))
    # ================================================================ Before even think remodel the whole bathroom
    E.append(Caption([('Before', 'b', wt(9, 0)), ('you', 'b', wt(9, 1)), ('even', 'b', wt(9, 1) + 0.15)], wt(9, 2)))
    E.append(Caption([('think', 'b', wt(9, 2)), ('to', 'b', wt(9, 3)), ('remodel', 'b', wt(9, 4))], wt(9, 6)))
    E.append(Caption([('the', 'b', wt(9, 6)), ('whole', 'b', wt(9, 6) + 0.1), ('bathroom,', 'b', wt(9, 7))], 28.40))
    E.append(Scrim(28.40, 29.79, 520, 1000, 0.42))
    E.append(Typed('JUST THINK', wt(9, 8), 29.74, 640, size=110, rate=0.03))
    E.append(Typed('ABOUT', wt(9, 10), 29.74, 770, size=110, rate=0.03))
    E.append(Typed('THE SHOWER', wt(9, 12), 29.74, 910, size=140, grad=(ORANGE_L, ORANGE), pop=True, sound=False))
    sfx(wt(9, 12), 'key', 0); sfx(wt(9, 12), 'bass', -5); sfx(wt(9, 12), 'pop', -3)
    # ================================================================ We are West Home Improvement. Let's make it happen!
    E.append(Caption([('We', 'b', wt(10, 0)), ('are', 'b', wt(10, 1))], wt(10, 2)))
    E.append(LogoPill(wt(10, 2), 31.30, cy=1180))
    E.append(Caption([("Let's", 'b', wt(10, 5)), ('make', 'b', wt(10, 6)), ('it', 'b', wt(10, 7)), ('happen!', 'o', wt(10, 8))], 32.33))
    # ================================================================ END
    te = 32.40
    E.append(Scrim(te, T.DUR, 440, 1000, 0.3))
    E.append(Typed("LET'S", te, 35.9, 560, size=112, rate=0.03, gain=-1))
    E.append(Typed('TRANSFORM', te + 0.15, 35.9, 690, size=124, rate=0.03, gain=-1))
    E.append(Typed('YOUR SHOWER', 32.77, 35.9, 840, size=140, grad=(ORANGE_L, ORANGE), pop=True, sound=False))
    sfx(32.77, 'impact', -3); sfx(32.77, 'key', 0)
    logo = G.load_logo(WEST + 'raw/brand/WEST HOME/PNG/Recurso 7@4x.png', 560)
    E.append(El(G.pil_to_spr(logo, radius=20, offset=(0, 10), opacity=0.5), 540, 1220, 33.95, 35.9, 'pop', 'blurout',
                d_in=0.42, d_out=0.35))
    sfx(33.95, 'pop', -2); sfx(33.95, 'swoosh', -8)
    E.append(Fade(35.95, T.DUR))
    return E


class VHS:
    """retro HUD inside the Super 8 frame: PLAY ▶ + date stamp."""

    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 44)
        def mk(s):
            im = Image.new('RGBA', (int(f.getlength(s)) + 20, 70), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((10, 6), s, font=f, fill=(255, 255, 255, 255))
            return G.with_shadow(im, radius=6, offset=(0, 0), opacity=0.0, glow=((255, 255, 255), 6, 0.35))
        self.play = mk('PLAY ▶')
        self.date = mk('JUN 14 1995')

    def active(self, t):
        return self.t0 <= t < self.t1

    def draw(self, canvas, t, base=None, mask=None):
        a = t - self.t0
        if int(a / 0.25) % 2 == 0 or a > 0.5:
            G.blit(canvas, self.play, 170 + self.play.shape[1] / 2, 500)
        G.blit(canvas, self.date, 910 - self.date.shape[1] / 2, 1440)
