"""On-screen graphics for reel 3 + the SFX events they trigger (typing on every text, other hits on key words)."""
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
    for n in range(int(t0 * T.FPS), int(math.ceil(t1 * T.FPS))):
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
    # ================================================================ HOOK
    E.append(Scrim(0.0, T.vs(3) + 0.3, 80, 440, 0.35))
    E.append(Typed('THEY ONLY WANTED', 0.0, T.ve(3), 222, size=88, rate=0.026))
    E.append(Typed('A NEW SHOWER…', 0.48, T.ve(3), 330, size=118, grad=OR, rate=0.032))
    sfx(0.48 + 6 * 0.032, 'bass', -6)
    # the hook title carries the first two lines (Félix walks toward the camera there: no room for subtitles)
    C([('only', 'o', wk(1, 'only')), ('remodel', 'b', wk(2, 'remodel'))], wk(2, 'the'))
    C([('the', 'b', wk(2, 'the')), ('shower', 'o', wk(2, 'shower')), ('area,', 'b', wk(2, 'area'))], T.vs(3))
    C([('but', 'b', T.vs(3)), ('I', 'b', T.vs(4)), ('mean', 'b', wk(4, 'mean'))], wk(4, 'this'))
    C([('this', 'b', wk(4, 'this')), ('space', 'b', wk(4, 'space')), ('needs', 'b', wk(4, 'needs'))], wk(4, 'a'))
    C([('a', 'b', wk(4, 'a')), ('lot', 'o', wk(4, 'lot')), ('of', 'o', wk(4, 'of')), ('work,', 'o', wk(4, 'work'))], wk(4, 'so'))
    C([('so', 'b', wk(4, 'so')), ('I', 'b', wk(4, 'i', 1)), ('gave', 'b', wk(4, 'gave')), ('them', 'b', wk(4, 'them'))], wk(4, 'some'))
    C([('some', 'b', wk(4, 'some')), ('suggestions', 'o', wk(4, 'suggestion'))], wk(4, 'and'))
    C([('and', 'b', wk(4, 'and')), ('we', 'b', wk(4, 'we')), ('ended', 'b', wk(4, 'ended')), ('up', 'b', wk(4, 'up'))], wk(4, 'doing'))
    C([('doing', 'b', wk(4, 'doing'))], T.REVEAL - 0.02)
    E.append(Scrim(T.REVEAL - 0.05, T.vs(5) - 0.02, 620, 1000, 0.40))
    E.append(Typed('THE WHOLE', T.REVEAL - 0.04, T.vs(5) - 0.12, 720, size=120, rate=0.026, cursor=False))
    E.append(Typed('THING', T.REVEAL + 0.22, T.vs(5) - 0.12, 870, size=190, grad=OR, pop=True, sound=False))
    sfx(T.REVEAL + 0.22, 'impact', -2); sfx(T.REVEAL + 0.22, 'key', 0)
    # ================================================================ Are you ready to see something nice?
    C([('Are', 'b', T.vs(5)), ('you', 'b', wk(5, 'you')), ('ready?', 'o', wk(5, 'ready'))], wk(5, 'to'))
    C([('to', 'b', wk(5, 'to')), ('see', 'b', wk(5, 'see')), ('something', 'b', wk(5, 'something')), ('nice?', 'o', wk(5, 'nice'))], T.ve(5) + 0.1)
    sfx(T.ve(5) + 0.15, 'swoosh', -4)
    # ================================================================ big wall / narrow / demoed → open space
    tw = wk(6, 'big')
    C([('There', 'b', T.vs(6)), ('was', 'b', wk(6, 'was')), ('a', 'b', wk(6, 'a'))], tw)
    E.append(Strike('BIG WALL', tw, wk(8, 'demoed'), T.vs(8) + 0.9, cy=330, size=170))
    C([('so', 'b', T.vs(7)), ('it', 'b', wk(7, 'it')), ('was', 'b', wk(7, 'was')), ('really', 'b', wk(7, 'really'))], wk(7, 'narrow'))
    C([('narrow', 'o', wk(7, 'narrow')), ('to', 'b', wk(7, 'to')), ('get', 'b', wk(7, 'get'))], wk(7, 'into'))
    C([('into', 'b', wk(7, 'into')), ('the', 'b', wk(7, 'the')), ('shower.', 'b', wk(7, 'shower'))], T.vs(8))
    C([('We', 'b', T.vs(8)), ('demoed', 'o', wk(8, 'demoed')), ('the', 'b', wk(8, 'the')), ('whole', 'b', wk(8, 'whole')), ('thing', 'b', wk(8, 'thing'))], wk(8, 'out'))
    C([('out', 'b', wk(8, 'out')), ('to', 'b', wk(8, 'to')), ('make', 'b', wk(8, 'make')), ('a', 'b', wk(8, 'a')), ('really', 'b', wk(8, 'really'))], wk(8, 'open'))
    E.append(Scrim(wk(8, 'open'), T.vs(9) - 0.02, 620, 1000, 0.38))
    E.append(Typed('OPEN', wk(8, 'open'), T.vs(9) - 0.1, 730, size=170, rate=0.04))
    E.append(Typed('SPACE', wk(8, 'space'), T.vs(9) - 0.1, 890, size=170, grad=OR, rate=0.04))
    sfx(wk(8, 'space') + 0.2, 'bass', -6)
    # ================================================================ vanity / countertop / fixtures
    C([('With', 'b', T.vs(9)), ('a', 'b', wk(9, 'a')), ('new', 'b', wk(9, 'new'))], wk(9, 'custom'))
    C([('custom', 'b', wk(9, 'custom')), ('vanity', 'o', wk(9, 'vanity'))], T.vs(10))
    C([('countertop', 'o', T.vs(10) + 0.1), ('to', 'b', wk(10, 'to')), ('match', 'b', wk(10, 'match'))], wk(10, 'the'))
    C([('the', 'b', wk(10, 'the')), ('tile', 'o', wk(10, 'tile'))], T.vs(11))
    C([('All', 'b', T.vs(11)), ('the', 'b', wk(11, 'the')), ('fixtures', 'o', wk(11, 'fixtures'))], wk(11, 'are'))
    C([('are', 'b', wk(11, 'are')), ('completely', 'b', wk(11, 'completely')), ('new.', 'o', wk(11, 'new'))], T.vs(12))
    # ================================================================ the shower is the masterpiece
    E.append(Scrim(T.vs(12), T.vs(13) - 0.02, 560, 1000, 0.40))
    E.append(Typed('THE SHOWER IS', T.vs(12), T.vs(13) - 0.1, 690, size=104, rate=0.026))
    E.append(Typed('THE MASTERPIECE', wk(12, 'masterpiece') - 0.1, T.vs(13) - 0.1, 825, size=112, grad=OR, pop=True, sound=False))
    sfx(wk(12, 'masterpiece') - 0.1, 'impact', -4); sfx(wk(12, 'masterpiece') - 0.1, 'shine', -4)
    C([('Classic', 'b', T.vs(13)), ('subway', 'o', T.vs(14)), ('tile,', 'o', wk(14, 'tile')), ('but', 'b', wk(14, 'but'))], T.vs(15))
    C([('make', 'b', T.vs(15)), ('it', 'b', wk(15, 'it')), ('look', 'b', wk(15, 'look')), ('great', 'b', wk(15, 'great'))], wk(15, 'like'))
    C([('like', 'b', wk(15, 'like')), ('a', 'b', wk(15, 'a')), ('LUXURY', 'o', wk(15, 'luxury')), ('bathroom', 'b', wk(15, 'bathroom'))], T.vs(16))
    C([('custom', 'b', T.vs(16)), ('niche,', 'o', wk(16, 'niche'))], T.vs(17))
    C([('a', 'b', T.vs(17)), ('nice', 'b', wk(17, 'nice')), ('glass', 'o', T.vs(18))], wk(18, 'custom'))
    C([('custom', 'b', wk(18, 'custom')), ('door.', 'o', wk(18, 'door'))], T.vs(19))
    sfx(T.vs(18), 'glass', -6)
    # ================================================================ we did it again / call West Home Improvement
    C([('Alright', 'b', T.vs(19)), ('Felix,', 'b', wk(19, 'felix'))], wk(19, 'we'))
    C([('we', 'b', wk(19, 'we')), ('did', 'b', wk(19, 'did')), ('it', 'b', wk(19, 'it')), ('again!', 'o', wk(19, 'again'))], wk(19, 'yes'))
    C([('Yes,', 'b', wk(19, 'yes')), ('sir.', 'b', wk(19, 'sir'))], T.vs(20))
    sfx(wk(19, 'yes') + 0.05, 'pop', -4)
    C([('You', 'b', T.vs(20)), ('already', 'b', wk(20, 'already')), ('know,', 'b', wk(20, 'know'))], wk(20, 'call'))
    C([('call', 'o', wk(20, 'call')), ('West', 'b', wk(20, 'west')), ('Home', 'b', wk(20, 'home')), ('Improvement', 'b', wk(20, 'improvement'))], T.ve(20) + 0.04)
    # ================================================================ END card (space for the written CTA)
    te = T.ve(20) + 0.04
    logo = G.load_logo(WEST + 'raw/brand/WEST HOME/PNG/Recurso 7@4x.png', 560)
    E.append(El(G.pil_to_spr(logo, radius=20, offset=(0, 10), opacity=0.5), 540, 900, te + 0.1, T.DUR - 0.3, 'pop', 'blurout',
                d_in=0.42, d_out=0.3))
    sfx(te + 0.1, 'pop', -2); sfx(te + 0.1, 'swoosh', -8)
    E.append(Fade(T.DUR - 0.35, T.DUR))
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
