"""On-screen graphics for reel 5 (kitchen countertops) + the SFX events they trigger. Style from estilo.md:
word-by-word subtitles (Cabinet Grotesk, white, keyword in brand orange, stacked lines, fade+blur in),
concept icon badges with a pop and a ring flash, split screens, red edge glow, warm light leak, CTA at the top."""
import json, math, re, unicodedata
import numpy as np, cv2
from PIL import Image
import gfx as G
from gfx import ORANGE, ORANGE_L
from core import ROOT, ease_out_cubic, ease_in_cubic, ease_out_back, clamp
import timeline as T
import icons

SFX = []          # (time, kind, gain_db)
OR = (ORANGE_L, ORANGE)
BGR = lambda c: np.array([c[2], c[1], c[0]], np.float32)


def sfx(t, kind, gain=0.0):
    SFX.append((round(t, 3), kind, gain))


# ------------------------------------------------------------------ words (Whisper on the assembled voice)
WORDS = json.load(open(ROOT + 'edit/words_out.json'))
_norm = lambda x: ''.join(c for c in unicodedata.normalize('NFD', x.lower()) if c.isalnum() and not unicodedata.combining(c))
_wi = 0


def take(token):
    """next occurrence of token in the word stream (keeps the caption script in sync with the audio)."""
    global _wi
    for j in range(_wi, min(_wi + 6, len(WORDS))):
        if _norm(WORDS[j]['w']) == _norm(token):
            _wi = j + 1
            return max(0.0, WORDS[j]['s'] - 0.03)
    raise AssertionError((token, [w['w'] for w in WORDS[_wi:_wi + 6]]))


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
    fr = _person_frames(t0, t1)
    if not fr:
        return 0.0
    a, b, c, d = int(max(0, y0) / 4), int(min(1920, y1) / 4), int(max(0, x0) / 4), int(min(1080, x1) / 4)
    return max(float(m[a:b, c:d].mean()) for m in fr)


def head_top(t0, t1):
    fr = _person_frames(t0, t1)
    tops = [int(np.where(m[:300, 70:200].any(1))[0].min()) * 4 for m in fr if m[:300, 70:200].any()]
    return min(tops) if tops else None


# ------------------------------------------------------------------ subtitles
STY = {'b': ('cab_bold', 76), 'e': ('cab_xbold', 116), 'h': ('cab_black', 168)}
_spr_cache = {}


def word_sprite(text, sk, orange):
    k = (text, sk, orange)
    if k not in _spr_cache:
        fname, size = STY[sk]
        img, base = G.text_rgba(text, fname, size, tracking=-18, grad=OR if orange else None)
        spr = G.with_shadow(img, radius=10, offset=(0, 4), opacity=0.66, glow=((0, 0, 0), 26, 0.42))
        _spr_cache[k] = (spr, img.width, img.height, base)
    return _spr_cache[k]


def parse(script):
    """'line|line' ; '!' prefix = emphasis size, '!!' = hero size ; *word* = orange ; tok=Display shows Display."""
    rows = []
    for line in script.split('|'):
        line = line.strip(); sk = 'b'
        if line.startswith('!!'):
            sk, line = 'h', line[2:]
        elif line.startswith('!'):
            sk, line = 'e', line[1:]
        words = []
        for tokd in line.split():
            orange = tokd.startswith('*') and tokd.endswith('*')
            tokd = tokd.strip('*')
            tok, _, disp = tokd.partition('=')
            disp = disp or tok
            words.append((disp, orange, take(re.sub(r'[¿?¡!,.]', '', tok))))
        rows.append((sk, words))
    return rows


class Sub:
    """one caption block: stacked lines, every word fades in (with blur) on its own time; hard cut at t_end."""

    def __init__(self, script, t_end, zone='a', cy=None):
        self.rows = parse(script)
        cuts = [s['t0'] for s in T.SHOTS[1:]]
        snap = lambda tw: next((c for c in cuts if tw < c <= tw + 0.12), tw)   # never start a word 1-3 frames before a cut
        self.rows = [(sk, [(d, o, snap(tw)) for d, o, tw in ws]) for sk, ws in self.rows]
        self.t_end = t_end
        self.t0 = min(w[2] for _, ws in self.rows for w in ws)
        self.items = []
        lines = []
        for sk, ws in self.rows:
            size = STY[sk][1]
            sp = size * 0.24
            sprs = [word_sprite(d, sk, o) + (t,) for d, o, t in ws]
            wtot = sum(s[1] for s in sprs) + sp * (len(sprs) - 1)
            lines.append((sk, size, sp, sprs, wtot))
        self.w = max(l[4] for l in lines)
        sc = min(1.0, 980 / self.w)
        self.sc = sc
        self.h = sum(l[1] * 0.98 for l in lines) * sc
        self.lines = lines
        self.zone = zone
        self.above = False
        self.cy = cy if cy is not None else self.place()
        y = self.cy - self.h / 2
        for sk, size, sp, sprs, wtot in lines:
            x = 540 - wtot * sc / 2
            base_y = y + size * 0.80 * sc
            for spr, w, h, base, t in sprs:
                cx = x + w * sc / 2
                cyw = base_y - base * sc + h * sc / 2
                self.items.append((spr, cx, cyw, t, sk))
                x += (w + sp) * sc
            y += size * 0.98 * sc

    def place(self):
        hw = self.w * self.sc / 2 + 20
        if self.zone == 'b':
            return 1095
        if self.zone == 'seam':
            return 960
        # A-roll: Samantha's hand covers the island in most shots, so subtitles live in the band above Félix's head
        # bottom edge anchored to the highest head position over the whole shot -> a steady baseline per shot
        ov = [s_ for s_ in T.SHOTS if s_['t0'] < self.t_end and self.t0 < s_['t1'] and s_.get('person')]
        ht = head_top(min(s_['t0'] for s_ in ov), max(s_['t1'] for s_ in ov)) if ov else None
        self.above = True
        return max(70 + self.h / 2, (ht if ht is not None else 420) - 26 - self.h / 2)

    def active(self, t):
        return self.t0 <= t < self.t_end

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        for spr, cx, cy, tw, sk in self.items:
            a = t - tw
            if a < 0:
                continue
            p = clamp(a / 0.15)
            e = ease_out_cubic(p)
            sc = self.sc * (0.94 + 0.06 * e)
            if sk != 'b':
                sc = self.sc * (0.82 + 0.18 * min(1.08, ease_out_back(clamp(a / 0.22), 2.0)))
            G.blit(canvas, spr, cx, cy, scale=sc, opacity=e, blur=5 * (1 - e))

    def below(self, gap=95):
        return 540, self.cy + self.h / 2 + gap


# ------------------------------------------------------------------ icon badge
class Badge:
    def __init__(self, name, t_in, t_out, cx, cy, size=138, gain=-7):
        self.spr = G.pil_to_spr(icons.badge(name, size), radius=12, offset=(0, 6), opacity=0.45)
        self.t_in, self.t_out, self.cx, self.cy, self.size = t_in, t_out, cx, cy, size
        sfx(t_in, 'pop', gain)

    def active(self, t):
        return self.t_in <= t < self.t_out + 0.12

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        a = t - self.t_in
        sc = 0.55 + 0.45 * min(1.12, ease_out_back(clamp(a / 0.24), 2.4))
        op = clamp(a / 0.08)
        if t >= self.t_out:
            q = (t - self.t_out) / 0.12; sc *= 1 - 0.4 * q; op *= 1 - q
        G.blit(canvas, self.spr, self.cx, self.cy, scale=sc, opacity=op)
        if a < 0.34:                                   # white ring flash
            q = a / 0.34
            r = int(self.size * (0.5 + 0.45 * ease_out_cubic(q)))
            ring = np.zeros((T.H, T.W), np.float32)
            cv2.circle(ring, (int(self.cx), int(self.cy)), r, 1.0, max(2, int(7 * (1 - q))), cv2.LINE_AA)
            k = ring[..., None] * 0.85 * (1 - q)
            canvas[:] = canvas * (1 - k) + 255 * k


# ------------------------------------------------------------------ helpers for photo panels
_ph = {}


def photo(name):
    if name not in _ph:
        _ph[name] = cv2.imread(T.PH + name + '.png')
    return _ph[name]


def cover(img, w, h, fy=0.5, zoom=1.0):
    """crop img to the w:h aspect around vertical focus fy, scaled by zoom, resized to (w,h)."""
    H_, W_ = img.shape[:2]
    if W_ / H_ > w / h:
        ch = H_ / zoom; cw = ch * w / h
    else:
        cw = W_ / zoom; ch = cw * h / w
    cx = W_ / 2; cy = min(max(fy * H_, ch / 2), H_ - ch / 2)
    M = np.float32([[w / cw, 0, -(cx - cw / 2) * w / cw], [0, h / ch, -(cy - ch / 2) * h / ch]])
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_AREA if cw > w else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def grade(img):
    import core
    return core.grade(img, 'stock')


def pill(text, size=58, pad=(34, 18)):
    img, _ = G.text_rgba(text, 'cab_xbold', size, tracking=-10)
    w, h = img.width + 2 * pad[0], img.height + 2 * pad[1]
    box = np.zeros((h, w, 4), np.float32)
    m = G.rounded_mask(w, h, 16)
    box[..., :3] = BGR(ORANGE) * m[..., None]; box[..., 3] = m
    t = G.pil_to_spr(img, shadow=False)
    th, tw = t.shape[:2]
    y0, x0 = (h - th) // 2, (w - tw) // 2
    a = t[..., 3:4]
    box[y0:y0 + th, x0:x0 + tw] = t + box[y0:y0 + th, x0:x0 + tw] * (1 - a)
    return box


class Split:
    """full-frame comparison: top panel slides in from the left, bottom from the right, labels + optional heat bars."""

    def __init__(self, t0, t1, a, b, ta, tb, la, lb, fa=0.5, fb=0.5, bars=None):
        self.t0, self.t1, self.ta, self.tb = t0, t1, ta, tb
        self.imgs = [grade(cover(photo(a), 1080, 952, fa, 1.0)), grade(cover(photo(b), 1080, 952, fb, 1.0))]
        self.labels = [pill(la), pill(lb)]
        self.bars = bars
        if bars:
            self.btitle = G.pil_to_spr(G.text_rgba('RESISTENCIA AL CALOR', 'cab_bold', 34, tracking=10)[0], radius=8, opacity=0.6)
            self.flame = G.pil_to_spr(icons.badge('flame', 84), radius=8, opacity=0.4)
        sfx(ta, 'swoosh', -9); sfx(tb, 'swoosh', -9)

    def active(self, t):
        return self.t0 <= t < self.t1

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        canvas[:] = np.array([30, 24, 20], np.float32)
        for i, (img, tt, y0, sgn) in enumerate(((self.imgs[0], self.ta, 0, -1), (self.imgs[1], self.tb, 968, 1))):
            if t < tt:
                continue
            p = ease_out_cubic(clamp((t - tt) / 0.32))
            dx = int(sgn * 1080 * (1 - p))
            z = 1.0 + 0.05 * clamp((t - tt) / max(0.5, self.t1 - tt))
            if z > 1.001:
                big = cv2.resize(img, None, fx=z, fy=z); oy, ox = (big.shape[0] - 952) // 2, (big.shape[1] - 1080) // 2
                pan = big[oy:oy + 952, ox:ox + 1080]
            else:
                pan = img
            xa, xb = max(0, dx), min(1080, 1080 + dx)
            canvas[y0:y0 + 952, xa:xb] = pan[:, xa - dx:xb - dx]
            # label
            q = clamp((t - tt - 0.18) / 0.22)
            if q > 0:
                lab = self.labels[i]
                ly = y0 + (80 if i == 0 else 150)          # bottom label sits lower so the seam subtitle stays clear
                G.blit(canvas, lab, 70 + lab.shape[1] / 2 + dx, ly, scale=0.85 + 0.15 * ease_out_back(q, 2.0), opacity=q)
            if self.bars and q > 0:
                v = self.bars[i] * ease_out_cubic(clamp((t - tt - 0.25) / 0.6))
                by = ly + 125
                bg = canvas[by - 70:by + 60, 40:1040]
                canvas[by - 70:by + 60, 40:1040] = bg * (1 - 0.45 * q)
                G.blit(canvas, self.btitle, 160 + self.btitle.shape[1] / 2, by - 30, opacity=q)
                G.blit(canvas, self.flame, 90, by, opacity=q)
                cv2.rectangle(canvas, (150, by + 8), (1000, by + 30), (255, 255, 255), -1, cv2.LINE_AA)
                canvas[by + 8:by + 31, 150:1001] = canvas[by + 8:by + 31, 150:1001] * 0.35 + 0.65 * 70
                x1 = int(150 + 850 * v)
                if x1 > 152:
                    g = np.linspace(0, 1, x1 - 150)[None, :, None]
                    canvas[by + 8:by + 31, 150:x1] = BGR(ORANGE_L) * (1 - g) + BGR(ORANGE) * g
        # divider
        if t >= self.tb:
            canvas[952:968] = canvas[952:968] * 0.2 + 255 * 0.8


class Patterns:
    """'hay más variación en los patrones': three stone strips slide up one after another."""

    def __init__(self, t0, t1, names, times):
        self.t0, self.t1, self.times = t0, t1, times
        self.strips = [grade(cover(photo(n), 352, 1920, 0.5, 1.15)) for n in names]
        for tt in times:
            sfx(tt, 'swoosh', -12)

    def active(self, t):
        return self.t0 <= t < self.t1

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        canvas[:] = np.array([30, 24, 20], np.float32)
        for i, (s, tt) in enumerate(zip(self.strips, self.times)):
            if t < tt:
                continue
            p = ease_out_cubic(clamp((t - tt) / 0.36))
            dy = int(1920 * (1 - p)) * (1 if i % 2 == 0 else -1)
            x0 = i * 364
            ya, yb = max(0, dy), min(1920, 1920 + dy)
            canvas[ya:yb, x0:x0 + 352] = s[ya - dy:yb - dy]


class Grid:
    """'un distribuidor de materiales': a showroom wall of four slabs popping in."""

    def __init__(self, t0, t1, names, times):
        self.t0, self.t1, self.times = t0, t1, times
        self.tiles = [grade(cover(photo(n), 528, 948, 0.5, 1.1)) for n in names]
        for tt in times:
            sfx(tt, 'click', -9)

    def active(self, t):
        return self.t0 <= t < self.t1

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        canvas[:] = np.array([30, 24, 20], np.float32)
        for i, (tile, tt) in enumerate(zip(self.tiles, self.times)):
            if t < tt:
                continue
            p = clamp((t - tt) / 0.26)
            sc = 0.86 + 0.14 * min(1.04, ease_out_back(p, 1.6))
            z = 1.0 + 0.04 * clamp((t - tt) / 2.0)
            tl = cv2.resize(tile, None, fx=sc * z, fy=sc * z)
            th, tw = tl.shape[:2]
            cx, cy = 8 + 264 + (i % 2) * 540, 8 + 474 + (i // 2) * 964
            x0, y0 = int(cx - tw / 2), int(cy - th / 2)
            cw, ch = min(tw, 528), min(th, 948)
            ox, oy = (tw - cw) // 2, (th - ch) // 2
            X0, Y0 = int(cx - cw / 2), int(cy - ch / 2)
            op = ease_out_cubic(p)
            canvas[Y0:Y0 + ch, X0:X0 + cw] = canvas[Y0:Y0 + ch, X0:X0 + cw] * (1 - op) + tl[oy:oy + ch, ox:ox + cw] * op


class Shrink:
    """'no es lo mismo mirarla completa a mirar un sample pequeño': the full slab shrinks into a small sample card."""

    def __init__(self, t_s, t1, d=0.5):
        self.ts, self.t1, self.d = t_s, t1, d
        sfx(t_s, 'swoosh', -8)

    def active(self, t):
        return self.ts <= t < self.t1

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        e = ease_out_cubic(clamp((t - self.ts) / self.d))
        src = canvas.copy()
        bg = cv2.GaussianBlur(cv2.resize(src, (270, 480)), (0, 0), 6)
        bg = cv2.resize(bg, (1080, 1920)) * (1 - 0.55 * e)
        w = int(1080 + (380 - 1080) * e); h = int(1920 + (380 - 1920) * e)
        cy = int(960 + (820 - 960) * e)
        # centre crop of the slab with the card's aspect
        if w / h > 1080 / 1920:
            cw, ch = 1080, int(1080 * h / w)
        else:
            ch, cw = 1920, int(1920 * w / h)
        crop = src[960 - ch // 2:960 - ch // 2 + ch, 540 - cw // 2:540 - cw // 2 + cw]
        card = cv2.resize(crop, (w, h), interpolation=cv2.INTER_AREA)
        canvas[:] = bg
        x0, y0 = 540 - w // 2, cy - h // 2
        r = int(32 * e)
        m = G.rounded_mask(w, h, max(1, r)) if r > 1 else np.ones((h, w), np.float32)
        bw = int(10 * e)
        if bw > 0:
            mo = G.rounded_mask(w + 2 * bw, h + 2 * bw, r + bw)
            sh = cv2.GaussianBlur(mo, (0, 0), 18) * 0.5 * e
            ys, xs = y0 - bw + 14, x0 - bw
            reg = canvas[ys:ys + h + 2 * bw, xs:xs + w + 2 * bw]
            reg[:] = reg * (1 - sh[:reg.shape[0], :reg.shape[1], None])
            reg = canvas[y0 - bw:y0 + h + bw, x0 - bw:x0 + w + bw]
            reg[:] = reg * (1 - mo[..., None]) + 255 * mo[..., None]
        reg = canvas[y0:y0 + h, x0:x0 + w]
        reg[:] = reg * (1 - m[..., None]) + card * m[..., None]


class PriceBars:
    """cost card over the cabinets: GRANITO $ (short bar) vs CUARZO $$ (taller)."""

    def __init__(self, t_in, t_bars, t_out, x0=30, y0=600, w=250, h=300):
        self.t_in, self.tb, self.t_out = t_in, t_bars, t_out
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        tx = lambda s, f, z, **k: G.pil_to_spr(G.text_rgba(s, f, z, **k)[0], radius=6, opacity=0.5)
        self.title = tx('COSTO', 'cab_xbold', 40, tracking=40)
        self.lbl = [tx('GRANITO', 'cab_bold', 26), tx('CUARZO', 'cab_bold', 26)]
        self.cur = [tx('$', 'cab_black', 52, grad=OR), tx('$$', 'cab_black', 52)]
        sfx(t_in, 'pop', -9); sfx(t_bars, 'click', -8); sfx(t_bars + 0.12, 'click', -10)

    def active(self, t):
        return self.t_in <= t < self.t_out

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        a = clamp((t - self.t_in) / 0.22)
        x0, y0, w, h = self.x0, self.y0, self.w, self.h
        G.glass(canvas, x0, y0, w, h, 30, tint=0.0, blur=22, border=0.35 * a, shadow=True, dark=0.42 * a)
        G.blit(canvas, self.title, x0 + w / 2, y0 + 42, opacity=a)
        base_y = y0 + h - 62
        for i, (hh, cx) in enumerate(((80, x0 + 68), (150, x0 + w - 68))):
            p = ease_out_cubic(clamp((t - self.tb - i * 0.12) / 0.35))
            top = int(base_y - hh * p)
            col = BGR(ORANGE) if i == 0 else np.array([235, 235, 235], np.float32)
            if p > 0:
                canvas[top:base_y, int(cx - 30):int(cx + 30)] = col
                G.blit(canvas, self.cur[i], cx, top - 32, opacity=p)
            G.blit(canvas, self.lbl[i], cx, base_y + 28, opacity=a)


class RedGlow:
    def __init__(self, t_in, t_out):
        self.t_in, self.t_out = t_in, t_out
        yy, xx = np.mgrid[0:T.H, 0:T.W].astype(np.float32)
        d = np.minimum(np.minimum(xx, T.W - 1 - xx), np.minimum(yy, T.H - 1 - yy))
        self.m = (np.clip(1 - d / 150.0, 0, 1) ** 1.6)[..., None]
        sfx(t_in, 'bass', -5)

    def active(self, t):
        return self.t_in <= t < self.t_out

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        a = 0.62 * ease_out_cubic(clamp((t - self.t_in) / 0.25)) * (0.9 + 0.1 * math.sin((t - self.t_in) * 9))
        k = self.m * a
        canvas[:] = canvas * (1 - k) + np.array([52, 52, 226], np.float32) * k


class Leak:
    """warm light-leak flash (B-roll -> A-roll), drawn after the person matte."""
    post = True

    def __init__(self, tc):
        self.tc = tc
        yy, xx = np.mgrid[0:T.H:4, 0:T.W:4].astype(np.float32)
        r = np.sqrt(((xx - T.W * 0.85) / T.W) ** 2 + ((yy - T.H * 0.15) / T.H) ** 2)
        self.rad = cv2.resize(np.clip(1 - r / 1.0, 0, 1), (T.W, T.H))[..., None]
        sfx(tc - 0.12, 'swoosh', -8); sfx(tc, 'shine', -10)

    def active(self, t):
        return self.tc - 0.2 <= t < self.tc + 0.38

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        a = t - self.tc
        white = math.exp(-(a / 0.075) ** 2) * 0.92
        warm = (clamp((a + 0.2) / 0.2) if a < 0 else math.exp(-a / 0.16)) * 0.75
        k = np.clip(self.rad * warm, 0, 1)
        canvas[:] = canvas * (1 - k) + np.array([60, 150, 255], np.float32) * k
        canvas[:] = canvas * (1 - white) + np.array([225, 240, 255], np.float32) * white


class CTA:
    """'comenta la palabra' + "COCINA" (orange, revealed left -> right) above Félix's head, like the reference's CTA;
    then COCINA moves up and 'y nos pondremos en contacto contigo' types in under it."""

    def __init__(self, t_end, y1=160, y2=318, y3=330):
        self.t_end = t_end
        self.lines = []

        def line(words, y, size_sc):
            ws = [(w, take(w)) for w in words]
            sprs = [word_sprite(w if w != 'podremos' else 'pondremos', 'b', False) for w, _ in ws]
            sp = 76 * 0.24 * size_sc
            tot = sum(s_[1] * size_sc for s_ in sprs) + sp * (len(sprs) - 1)
            x = 540 - tot / 2; out = []
            for (w, tt), s_ in zip(ws, sprs):
                out.append((s_[0], x + s_[1] * size_sc / 2, y, tt, size_sc)); x += s_[1] * size_sc + sp
            return out
        self.l1 = line(['comenta', 'la', 'palabra'], y1, 0.9)
        self.tk = take('cocina')
        self.l2 = line(['y', 'nos', 'podremos', 'en', 'contacto', 'contigo'], y3, 0.70)
        self.tmove = self.l2[0][3] - 0.12
        img, _ = G.text_rgba('"COCINA"', 'cab_black', 186, tracking=-10, grad=OR)
        self.kw = G.with_shadow(img, radius=12, offset=(0, 6), opacity=0.55, glow=((0, 0, 0), 24, 0.3))
        self.y1, self.y2 = y1, y2
        sfx(self.tk, 'pop', -4)
        for i in range(6):
            sfx(self.tk + 0.03 * i, 'key', -8)
        for _, _, _, tt, _ in self.l1 + self.l2:
            sfx(tt, 'key', -15)

    def active(self, t):
        return self.l1[0][3] <= t < self.t_end

    def _words(self, canvas, t, ws, fade_out=None):
        for spr, cx, cy, tt, sc in ws:
            a = t - tt
            if a < 0:
                continue
            e = ease_out_cubic(clamp(a / 0.15))
            op = e
            if fade_out is not None and t >= fade_out:
                op *= 1 - clamp((t - fade_out) / 0.12)
            G.blit(canvas, spr, cx, cy, scale=sc * (0.94 + 0.06 * e), opacity=op, blur=5 * (1 - e))

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        self._words(canvas, t, self.l1, fade_out=self.tmove)
        a = t - self.tk
        if a >= 0:
            m = ease_out_cubic(clamp((t - self.tmove) / 0.25))
            y = self.y2 + (self.y1 + 10 - self.y2) * m
            s = 1.0 - 0.2 * m
            w = self.kw.shape[1]
            right = (540 - w / 2) + w * ease_out_cubic(clamp(a / 0.2))

            def mfn(X0, Y0, X1, Y1):
                xs = np.arange(X0, X1, dtype=np.float32)
                return np.repeat(np.clip((right - xs) / 30, 0, 1)[None, :], Y1 - Y0, 0)
            G.blit(canvas, self.kw, 540, y, scale=s, mask_fn=mfn if a < 0.2 else None)
        self._words(canvas, t, self.l2)


# ------------------------------------------------------------------ the edit
def build():
    global _wi
    SFX.clear(); _wi = 0
    E = []
    U = []   # full-frame panels go first (under the subtitles)
    sh = {i: s for i, s in enumerate(T.SHOTS)}

    def S(script, t_end, zone='a', **kw):
        s = Sub(script, t_end, zone, **kw); E.append(s)
        for _, _, _, tt, sk in s.items:
            sfx(tt, 'key', -15 if sk == 'b' else -11)
        return s

    def badge(sub, name, t_in, side=False):
        if sub.above or side:
            x = min(985, 540 + sub.w * sub.sc / 2 + 95); y = sub.cy
        else:
            x, y = sub.below()
        E.append(Badge(name, t_in, sub.t_end, x, y))

    # HOOK — Samantha (off camera) asks Félix
    S('Félix,', 0.45)
    S('¿Qué pasa', 0.84)
    S('si quiero | !remodelar', 1.90)
    s = S('mi *cocina*', 2.72)
    badge(s, 'kitchen', s.items[-1][3], side=True)
    S('y no sé qué', 3.52)
    S('!!*countertop*', 3.98)
    S('elegir?', T.vs(1))
    # "Tenemos dos opciones, el granito o el cuarzo."
    S('Tenemos | !!dos=2 *opciones*', T.SPLIT1)
    U.append(Split(T.SPLIT1, T.vs(3), 'granite_kitchen', 'quartz_kitchen', T.SPLIT1 + 0.01, 6.70, 'GRANITO', 'CUARZO',
                   fa=0.62, fb=0.62))
    S('el *granito* o el *cuarzo*', T.vs(3), 'seam')
    # "¿Cuál es la diferencia entre los dos materiales?"
    S('¿Cuál es | la diferencia', 8.40)
    S('entre los dos | !*materiales?*', T.vs(4))
    # "El granito puede ser un poco más económico, pero requiere mayor mantenimiento."
    S('El granito | puede ser', 10.82)
    s = S('un poco más | !*económico,*', T.CLEAN)
    E.append(PriceBars(T.vs(4) + 0.3, s.items[-1][3] - 0.2, T.CLEAN))
    s = S('pero requiere | mayor | !*mantenimiento.*', T.vs(5), 'b')
    badge(s, 'spray', s.items[-1][3])
    # "El cuarzo es un material fabricado, hay más variación en los patrones."
    s = S('El cuarzo es | un material | !*fabricado,*', T.vs(6), 'b')
    badge(s, 'factory', s.items[-1][3])
    t_hay = WORDS[_wi]['s']
    U.append(Patterns(T.vs(6), T.vs(7), ['quartz_pattern', 'quartz_white_detail', 'slab_closeup'],
                      [T.vs(6) + 0.01, t_hay + 0.30, t_hay + 0.62]))
    s = S('hay más | variación | en los | !*patrones.*', T.vs(7), 'b')
    badge(s, 'swatches', s.items[-1][3])
    # "Lo mejor de todo es que ya viene completamente sellado."
    S('Lo mejor de todo', 18.96)
    S('es que ya viene', 19.52)
    s = S('completamente | !!*sellado.*', T.vs(8))
    badge(s, 'shield', s.items[-1][3], side=True)
    # "El cuarzo resiste calor, pero no tanto como el granito,"
    S('El cuarzo', 21.86)
    s = S('resiste | !*calor,*', T.HEAT_CMP)
    badge(s, 'flame', s.items[-1][3], side=True)
    U.append(Split(T.HEAT_CMP, T.STEAM, 'granite_texture', 'quartz_white_detail', T.HEAT_CMP + 0.01, 23.30,
                   'GRANITO', 'CUARZO', bars=(0.92, 0.58)))
    S('pero no tanto | como el *granito,*', T.STEAM, 'seam')
    # "entonces tienes que ser cuidadoso a la hora de usar tus ollas calientes,"
    S('entonces | tienes que ser | !cuidadoso', 25.66, 'b')
    s = S('a la hora de usar | tus | !*ollas* *calientes,*', T.POTS, 'b')
    badge(s, 'pot', s.items[-2][3])
    # "no dejarlas encima de tu countertop porque se puede dañar."
    S('no dejarlas | encima de | tu countertop', 29.33, 'b')
    s = S('porque | !!*se* *puede* | !!*dañar.*', T.vs(9), 'b')
    E.append(RedGlow(s.t0, T.vs(9)))
    badge(s, 'warning', s.items[-1][3])
    # "¿Qué opción me recomendarías tú?"
    E.append(Leak(T.vs(9)))
    S('¿Qué opción | me', 31.24)
    S('!*recomendarías* | tú?', T.vs(10))
    # "Hacemos un appointment y vamos a un distribuidor de materiales"
    s = S('Hacemos un | !*appointment*', 33.24)
    badge(s, 'calendar', s.items[-1][3], side=True)
    S('y vamos a', T.vs(11))
    U.append(Grid(T.vs(11), T.SLAB_FULL, ['granite_colorful', 'quartz_white_detail', 'granite_texture', 'slab_closeup'],
                  [T.vs(11) + 0.01 + 0.16 * i for i in range(4)]))
    s = S('un *distribuidor* | de materiales', T.SLAB_FULL, 'b')
    badge(s, 'warehouse', s.items[1][3])
    # "porque no es lo mismo mirarla completo a mirar un sample pequeño."
    S('porque no es | lo mismo | mirarla | !*completo*', 37.80, 'b')
    t_a = WORDS[_wi]['s']
    U.append(Shrink(t_a, T.vs(13)))
    S('a mirar | un *sample* | !!*pequeño.*', T.vs(13), 'b', cy=1480)
    # "Y si quieres que mi equipo y yo te ayudemos,"
    S('Y si quieres que', 40.04)
    s = S('mi equipo y yo', 40.70)
    tw = [it[3] for it in s.items]
    for x, tt in zip((400, 540, 680), (tw[0], tw[1], tw[3])):
        E.append(Badge('worker', tt, 40.70, x, s.cy - s.h / 2 - 78, size=112, gain=-9))
    S('te *ayudemos,*', T.vs(14))
    # CTA — "comenta la palabra cocina y nos pondremos en contacto contigo."
    E.append(CTA(T.DUR))
    return U + E

