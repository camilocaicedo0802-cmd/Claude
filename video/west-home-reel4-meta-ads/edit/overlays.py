"""On-screen graphics for reel 4 (Meta Ads) + the SFX events they trigger (typing on every text, other hits on key words)."""
import json, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import gfx as G
from gfx import El, title, ORANGE, ORANGE_L
from core import ROOT, WEST, ease_out_cubic, ease_in_cubic, ease_out_back, ease_out_expo, clamp
import timeline as T

WORDS = json.load(open(ROOT + 'felix/words.json'))
EARLY = 0.05
SFX = []          # (time, kind, gain_db)


def sfx(t, kind, gain=0.0):
    SFX.append((round(t, 3), kind, gain))


def wk(k, word, nth=0):
    """timeline time of the nth occurrence of `word` inside voice piece k (word times from the take's transcript)."""
    clip, si, so, tp = T.VOICE[k]
    name = clip.split('/')[-1].replace('.MOV', '.wav')
    norm = lambda x: ''.join(c for c in x.lower() if c.isalnum())
    hits = [w for w in WORDS[name]['words'] if si - 0.15 <= w['s'] < so and norm(w['w']) == norm(word)]
    assert len(hits) > nth, (k, word, [w['w'] for w in WORDS[name]['words'] if si - 0.15 <= w['s'] < so])
    return round(min(max(tp, tp + hits[nth]['s'] - si - EARLY), tp + so - si - 0.1), 3)


def wt(k, i):
    """timeline time of word i of voice clip k."""
    clip, si, so, tp = T.VOICE[k]
    name = clip.split('/')[-1].replace('.MOV', '.wav')
    w = WORDS[name]['words'][i]
    return round(max(tp, tp + w['s'] - si - EARLY), 3)


# ------------------------------------------------------------------ where the people are (person mattes from render)
_mk = {}


def _mask(n):
    if n not in _mk:
        im = cv2.imread(ROOT + f'masks/{n:05d}.png', cv2.IMREAD_GRAYSCALE)
        _mk[n] = None if im is None else cv2.resize(im, (270, 480), interpolation=cv2.INTER_AREA) > 100
    return _mk[n]


def _person_frames(t0, t1):
    out = []
    for n in range(int(math.ceil(t0 * T.FPS - 1e-6)), int(math.ceil(t1 * T.FPS))):
        tt = n / T.FPS
        if any(s.get('person') and s['t0'] <= tt < s['t1'] for s in T.SHOTS):
            m = _mask(n)
            if m is not None:
                out.append(m)
    return out


def covered(t0, t1, y0, y1, x0, x1):
    """largest fraction of the box (canvas px) covered by a person during [t0, t1)."""
    fr = _person_frames(t0, t1)
    if not fr:
        return 0.0
    a, b, c, d = int(y0 / 4), int(y1 / 4), int(max(0, x0) / 4), int(min(1080, x1) / 4)
    return max(float(m[a:b, c:d].mean()) for m in fr)


def head_top(t0, t1):
    fr = _person_frames(t0, t1)
    tops = [int(np.where(m[:, 60:210].any(1))[0].min()) * 4 for m in fr if m[:, 60:210].any()]
    return min(tops) if tops else None


def free_y(t0, t1, half_w, h=110, prefer=(1430, 1600), above_pad=80, floor=170):
    """y for a text line: a preferred low position if no person is there, else the free sky above the head."""
    for y in prefer:
        if covered(t0, t1, y - h * 0.6, y + h * 0.4, 540 - half_w, 540 + half_w) < 0.015:
            return y
    ht = head_top(t0, t1)
    return max(floor, (ht if ht is not None else 1500) - above_pad)


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

    def __init__(self, words, t_end, cy=None, size=66, gap=0.27, max_w=960):
        self.t_end = t_end
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
        self.half_w = tot * sc / 2 + 30
        if cy is None:
            cy = free_y(min(i[3] for i in items), t_end, self.half_w)
        self.cy = cy
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

    def move(self, cy):
        d = cy - self.cy
        for e in self.els:
            e.cy += d
        self.cy = cy

    def active(self, t):
        return self.t0 <= t < self.t_end

    def draw(self, canvas, t, base=None, mask=None):
        if self.active(t):
            for e in self.els:
                e.draw(canvas, t)


class Pill:
    """orange label pill, wiped in left -> right."""

    def __init__(self, text, t_in, t_out, cy, cx=540, size=50, typing=True, d_out=0.25):
        self.t_in, self.t_out, self.cy, self.cx, self.d_out = t_in, t_out, cy, cx, d_out
        img, _ = G.text_rgba(text, 'bold', size, tracking=-10)
        self.txt = G.pil_to_spr(img, shadow=False)
        self.w = img.width + 64; self.h = img.height + 36
        self.mask = G.rounded_mask(int(self.w), int(self.h), 16)
        if typing:
            for k in range(min(6, len(text))):
                sfx(t_in + 0.03 + k * 0.045, 'key', -6)

    def active(self, t):
        return self.t_in <= t < self.t_out + self.d_out

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        p = ease_out_cubic((t - self.t_in) / 0.28)
        op = 1.0 if t < self.t_out else 1 - clamp((t - self.t_out) / self.d_out)
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
    post = True

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
    OR = (ORANGE_L, ORANGE)
    C = lambda words, t_end, **kw: E.append(Caption(words, t_end, **kw))
    # ================================================================ HOOK — Peter: "This customer came at us with a couple of problems."
    E.append(Scrim(0.0, T.vs(1), 90, 450, 0.32))
    E.append(Pill('SOUTH TULSA · SHOWER REMODEL', 0.0, T.vs(1) - 0.1, 150, size=34, typing=False))
    E.append(Typed('THEY HAD', 0.05, T.vs(1) - 0.08, 255, size=100, rate=0.03))
    E.append(Typed('2 PROBLEMS…', 0.35, T.vs(1) - 0.08, 380, size=132, grad=OR, rate=0.04))
    sfx(0.35 + 4 * 0.04, 'bass', -6)
    C([('This', 'b', T.vs(0)), ('customer', 'b', wk(0, 'customer')), ('came', 'b', wk(0, 'came')), ('at', 'b', wk(0, 'at')), ('us', 'b', wk(0, 'us'))], wk(0, 'with'))
    C([('with', 'b', wk(0, 'with')), ('a', 'b', wk(0, 'a')), ('couple', 'b', wk(0, 'couple')), ('of', 'b', wk(0, 'of')), ('problems.', 'o', wk(0, 'problems'))], T.vs(1))
    # ================================================================ problem 1: the old shower
    E.append(Pill('PROBLEM #1', T.vs(1) + 0.05, T.vs(2) - 0.1, 250, size=44))
    E.append(Typed('OLD SHOWER', wk(1, 'remodel'), T.vs(2) - 0.1, 380, size=140, rate=0.035))
    C([('One,', 'b', T.vs(1)), ('they', 'b', wk(1, 'they')), ('needed', 'b', wk(1, 'needed')), ('to', 'b', wk(1, 'to'))], wk(1, 'remodel'))
    C([('remodel', 'b', wk(1, 'remodel')), ('an', 'b', wk(1, 'an')), ('existing', 'b', wk(1, 'existing')), ('shower,', 'o', wk(1, 'shower'))], T.vs(2))
    # ================================================================ problem 2: the unused jacuzzi
    cut2 = T.SHOTS[5]['t0']                      # Peter -> the old bathroom
    E.append(Pill('PROBLEM #2', T.vs(2) + 0.05, T.vs(3) - 0.12, 250, size=44))
    E.append(Typed('UNUSED', cut2 + 0.04, T.vs(3) - 0.12, 370, size=120, rate=0.035))
    E.append(Typed('JACUZZI TUB', cut2 + 0.30, T.vs(3) - 0.12, 500, size=132, grad=OR, rate=0.035))
    C([('and', 'b', T.vs(2)), ('two,', 'b', wk(2, 'two')), ('they', 'b', wk(2, 'they')), ('had', 'b', wk(2, 'had')), ('a', 'b', wk(2, 'a'))], wk(2, 'jacuzzi'))
    C([('jacuzzi', 'o', wk(2, 'jacuzzi')), ('tub', 'o', wk(2, 'tub')), ('that', 'b', wk(2, 'that'))], cut2)
    C([('was', 'b', wk(2, 'was')), ('not', 'o', wk(2, 'not')), ('usable', 'o', wk(2, 'usable'))], wk(2, 'space'))
    C([('space', 'b', wk(2, 'space')), ('anymore.', 'b', wk(2, 'anymore'))], T.vs(3))
    # ================================================================ the plan: jacuzzi area -> new shower
    E.append(Strike('JACUZZI', wk(3, 'jacuzzi'), wk(3, 'new'), T.REVEAL - 0.1, cy=330, size=150))
    E.append(Typed('NEW SHOWER', wk(3, 'new'), T.REVEAL - 0.1, 490, size=140, grad=OR, rate=0.035))
    C([('We', 'b', T.vs(3)), ('suggested', 'b', wk(3, 'suggested')), ('to', 'b', wk(3, 'to')), ('turn', 'b', wk(3, 'turn'))], wk(3, 'the'))
    C([('the', 'b', wk(3, 'the')), ('jacuzzi', 'o', wk(3, 'jacuzzi')), ('tub', 'b', wk(3, 'tub')), ('area', 'b', wk(3, 'area'))], wk(3, 'into'))
    C([('into', 'b', wk(3, 'into')), ('the', 'b', wk(3, 'the', 1)), ('new', 'o', wk(3, 'new')), ('shower', 'o', wk(3, 'shower')), ('area,', 'b', wk(3, 'area', 1))], T.REVEAL)
    # ================================================================ REVEAL — "creating this massive, beautiful new shower"
    E.append(Scrim(T.REVEAL, T.vs(4) - 0.02, 160, 640, 0.30))
    E.append(Typed('MASSIVE', wk(3, 'massive'), T.vs(4) - 0.1, 330, size=200, grad=OR, pop=True, sound=False))
    sfx(wk(3, 'massive'), 'impact', -3); sfx(wk(3, 'massive'), 'key', 0)
    E.append(Typed('BEAUTIFUL NEW SHOWER', wk(3, 'beautiful'), T.vs(4) - 0.1, 470, size=84, rate=0.022))
    # (no subtitle on "creating this": Félix fills the frame while he opens the door)
    # ================================================================ old shower area -> storage closet
    C([('and', 'b', T.vs(4)), ('turn', 'b', wk(4, 'turn')), ('the', 'b', wk(4, 'the')), ('old', 'o', wk(4, 'old')), ('shower', 'b', wk(4, 'shower'))], wk(4, 'area'))
    C([('area', 'b', wk(4, 'area')), ('into', 'b', wk(4, 'into')), ('a', 'b', wk(4, 'a'))], wk(4, 'storage'))
    E.append(Scrim(wk(4, 'storage'), T.vs(5) - 0.02, 560, 980, 0.36))
    E.append(Typed('STORAGE', wk(4, 'storage'), T.vs(5) - 0.1, 690, size=170, rate=0.035))
    E.append(Typed('CLOSET', wk(4, 'closet'), T.vs(5) - 0.1, 850, size=170, grad=OR, rate=0.035))
    # ================================================================ transformation / functionality / features
    C([('completely', 'b', T.vs(5)), ('transforming', 'o', wk(5, 'transforming'))], wk(5, 'their'))
    C([('their', 'b', wk(5, 'their')), ('space,', 'b', wk(5, 'space')), ('giving', 'b', wk(5, 'giving')), ('them', 'b', wk(5, 'them'))], T.vs(6))
    C([('FUNCTIONALITY', 'o', T.vs(6))], T.vs(7))
    E.append(Pill('BUILT-IN BENCH', T.vs(6) + 0.04, T.vs(7) - 0.08, 300, size=44, typing=False, d_out=0.06))
    C([('and', 'b', T.vs(7)), ('features', 'o', wk(7, 'features'))], wk(7, 'that'))
    C([('that', 'b', wk(7, 'that')), ('they', 'b', wk(7, 'they')), ('really', 'b', wk(7, 'really')), ('wanted.', 'o', wk(7, 'wanted'))], T.vs(8))
    feats = [('CUSTOM NICHE', 16), ('RAIN SHOWER HEAD', 17), ('NEW FIXTURES', 18), ('HANDHELD SPRAY', 19)]
    for txt, k in feats:
        s0 = T.SHOTS[k]
        E.append(Pill(txt, s0['t0'] + 0.03, s0['t1'] - 0.08, 300, size=46, typing=False, d_out=0.06))
        sfx(s0['t0'] + 0.03, 'click', -4)
    # ================================================================ price
    C([('Remember,', 'b', T.vs(8)), ('our', 'b', wk(8, 'our')), ('shower', 'b', wk(8, 'shower')), ('remodels', 'b', wk(8, 'remodels'))], wk(8, 'start'))
    E.append(Price(wk(8, 'start'), wk(8, '9'), T.vt(8, 3.05), T.vs(9)))
    sfx(wk(8, 'start'), 'swoosh', -6); sfx(T.vt(8, 3.05), 'impact', -3); sfx(T.vt(8, 3.05), 'shine', -5)
    # ================================================================ CTA — Peter: "Reach out today."
    E.append(Typed('REACH OUT', T.vs(9), T.ve(9) + 0.02, 0, size=128, rate=0.03))
    E[-1].auto_y = (T.vs(9), T.ve(9), 0)
    E.append(Typed('TODAY', T.vs(9) + 0.3, T.ve(9) + 0.02, 0, size=150, grad=OR, pop=True, sound=False))
    E[-1].auto_y = (T.vs(9), T.ve(9), 1)
    sfx(T.vs(9) + 0.3, 'pop', -2)
    # ================================================================ END card
    te = T.ve(9) + 0.05
    E.append(Typed('READY FOR YOUR', te + 0.08, T.DUR - 0.4, 540, size=84, rate=0.025))
    E.append(Typed('DREAM SHOWER?', te + 0.38, T.DUR - 0.4, 652, size=108, grad=OR, rate=0.03))
    E.append(Label('SEND US A MESSAGE', te + 0.62, T.DUR - 0.4, cy=790, size=56))
    sfx(te + 0.62, 'swoosh', -6); sfx(te + 0.62, 'click', -4)
    logo = G.load_logo(WEST + 'raw/brand/WEST HOME/PNG/Recurso 7@4x.png', 520)
    tl = max(te + 0.9, T.beat(64))
    E.append(El(G.pil_to_spr(logo, radius=20, offset=(0, 10), opacity=0.5), 540, 1120, tl, T.DUR - 0.35, 'pop', 'blurout',
                d_in=0.42, d_out=0.3))
    sfx(tl, 'pop', -2)
    E.append(El(title('Shower remodels · Tulsa & surrounding areas', 'bold', 44, tracking=-20), 540, 1390, tl + 0.3,
                T.DUR - 0.35, 'rise', 'blurout', dy=30, d_in=0.25, d_out=0.3))
    E.append(Fade(T.DUR - 0.35, T.DUR))
    # REACH OUT / TODAY above Peter's head
    ys = [e for e in E if getattr(e, 'auto_y', None)]
    if ys:
        a, b, _ = ys[0].auto_y
        ht = head_top(a, b) or 700
        ys[1].cy = ht - 110; ys[0].cy = ys[1].cy - 140
    layout(E)
    return E


def layout(E):
    """keep subtitles clear of the big titles (and of people): move a colliding caption below or above the title."""
    for e in E:
        if isinstance(e, Strike):
            e.resolve()
    titles = [e for e in E if isinstance(e, Typed) and e.h >= 90] + [e.ty for e in E if isinstance(e, Strike)]
    for c in [e for e in E if isinstance(e, Caption)]:
        live = [ti for ti in titles if ti.t_in < c.t_end and c.t0 < ti.t_out + ti.d_out]
        if not live:
            continue
        bands = sorted((ti.cy - ti.h * 0.5 - 30, ti.cy + ti.h * 0.5 + 30) for ti in live)
        hit = lambda y: any(y + 40 > a and y - 40 < b for a, b in bands)
        if not hit(c.cy):
            continue
        lo, hi = min(a for a, b in bands), max(b for a, b in bands)
        cands = [hi + 50, lo - 50]
        free = [y for y in cands if 170 <= y <= 1650 and covered(c.t0, c.t_end, y - 55, y + 45, 540 - c.half_w, 540 + c.half_w) < 0.015]
        c.move((free or cands)[0])


class Strike:
    """a typed title that gets crossed out with an orange line (e.g. the wall that was removed)."""

    def __init__(self, text, t_in, t_strike, t_out, cy=None, size=170):
        self.ty = Typed(text, t_in, t_out, 0, size=size, rate=0.04)
        self.t_in, self.ts, self.t_out = t_in, t_strike, t_out
        self.cy_ = cy
        self.w = self.ty.cuts[-1] - 48
        sfx(t_strike, 'stamp', -2); sfx(t_strike, 'swoosh', -6)

    def resolve(self):
        if self.cy_ is None:
            self.cy_ = free_y(self.t_in, self.t_out, self.w / 2 + 40, h=200, prefer=(), above_pad=120)
        self.ty.cy = self.cy_

    def active(self, t):
        return self.ty.active(t)

    def draw(self, canvas, t, base=None, mask=None):
        self.ty.draw(canvas, t)
        if t >= self.ts and t < self.t_out + self.ty.d_out:
            p = ease_out_cubic((t - self.ts) / 0.22)
            op = 1.0 if t < self.t_out else 1 - clamp((t - self.t_out) / self.ty.d_out)
            x0 = 540 - self.w / 2 - 30; x1 = x0 + (self.w + 60) * p
            y = int(self.cy_ + 8)
            col = np.array([ORANGE[2], ORANGE[1], ORANGE[0]], np.float32)
            th = 22
            ln = np.zeros((T.H, T.W), np.float32)
            cv2.line(ln, (int(x0), y + 18), (int(x1), y - 18), 1.0, th, cv2.LINE_AA)
            ln = ln[..., None] * op
            canvas[:] = canvas * (1 - ln) + col * ln


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


class Label:
    """brand label: orange box with white text (as on the Facebook cover), wiped in from the left."""

    def __init__(self, text, t_in, t_out, cy=1170, size=58):
        self.t_in, self.t_out, self.cy = t_in, t_out, cy
        img, _ = G.text_rgba(text, 'bold', size, tracking=-10)
        self.txt = G.pil_to_spr(img, shadow=False)
        self.w = img.width + 80; self.h = img.height + 44

    def active(self, t):
        return self.t_in <= t < self.t_out + 0.4

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        p = ease_out_cubic((t - self.t_in) / 0.35)
        op = 1.0 if t < self.t_out else 1 - clamp((t - self.t_out) / 0.4)
        x0 = 540 - self.w / 2; y0 = self.cy - self.h / 2
        right = x0 + self.w * p
        X0, X1 = int(x0), int(min(right, x0 + self.w)); Y0, Y1 = int(y0), int(y0 + self.h)
        if X1 > X0:
            m = G.rounded_mask(int(self.w), int(self.h), 14)[:, :X1 - X0]
            col = np.array([ORANGE[2], ORANGE[1], ORANGE[0]], np.float32)
            reg = canvas[Y0:Y1, X0:X1]
            mm = m[:reg.shape[0], :reg.shape[1], None] * op
            canvas[Y0:Y1, X0:X1] = reg * (1 - mm) + col * mm

        def mfn(A, B, C, D):
            xs = np.arange(A, C, dtype=np.float32)
            return np.repeat(np.clip((right + 12 - xs) / 24, 0, 1)[None, :], D - B, 0)

        G.blit(canvas, self.txt, 540, self.cy, opacity=op, mask_fn=None if p >= 0.999 else mfn)


class Price:
    """STARTING AT label + $9,800 counter with landing pop, shine and glow."""

    def __init__(self, t_label, t_count, t_land, t_out):
        self.tl, self.tc, self.tland, self.to = t_label, t_count, t_land, t_out
        self.label = Label('STARTING AT', t_label, t_out - 0.05, cy=770, size=60)
        self.cache = {}
        f = G.font('black', 235)
        self.final_w = f.getlength('$9,800')
        img, _ = G.text_rgba('$9,800', 'black', 235, tracking=-35, grad=((255, 255, 255), (255, 228, 214)))
        self.final = G.with_shadow(img, radius=22, offset=(0, 12), opacity=0.55, glow=(ORANGE, 26, 0.55))
        self.final_plain = G.with_shadow(img, radius=22, offset=(0, 12), opacity=0.55)
        self.mask_a = self.final[..., 3]

    def active(self, t):
        return self.tl <= t < self.to

    def spr_for(self, v):
        s = f'${v:,}'
        if s not in self.cache:
            img, _ = G.text_rgba(s, 'black', 235, tracking=-35, grad=((255, 255, 255), (255, 228, 214)))
            self.cache[s] = G.with_shadow(img, radius=22, offset=(0, 12), opacity=0.55)
        return self.cache[s]

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        self.label.draw(canvas, t)
        if t < self.tc:
            return
        cy = 985
        if t < self.tland:
            p = (t - self.tc) / (self.tland - self.tc)
            v = int(round(9800 * ease_out_expo(p) / 50.0) * 50)
            spr = self.spr_for(v)
            G.blit(canvas, spr, 540, cy, scale=0.9 + 0.1 * p, opacity=clamp(p * 4), blur=4 * (1 - p))
        else:
            q = t - self.tland
            s = 1 + 0.14 * math.exp(-q * 9) * math.cos(q * 22)
            glow_k = clamp(1 - q / 0.9)
            spr = self.final if glow_k > 0 else self.final_plain
            G.blit(canvas, self.final_plain, 540, cy, scale=s)
            if glow_k > 0:
                G.blit(canvas, self.final, 540, cy, scale=s, opacity=glow_k)
            # shine sweep across the numbers
            sh = clamp((q - 0.05) / 0.55)
            if 0 < sh < 1:
                h, w = self.final_plain.shape[:2]
                band = np.zeros((h, w), np.float32)
                xs = np.arange(w, dtype=np.float32)[None, :] + np.arange(h, dtype=np.float32)[:, None] * 0.35
                c = -200 + (w + 400) * sh
                band = np.clip(1 - np.abs(xs - c) / 70, 0, 1) * 0.75
                a = self.final_plain[..., 3]
                core = (a > 0.6).astype(np.float32)
                shine = np.zeros((h, w, 4), np.float32)
                shine[..., :3] = 255 * band[..., None] * core[..., None]
                shine[..., 3] = band * core
                G.blit(canvas, shine, 540, cy, scale=s)

