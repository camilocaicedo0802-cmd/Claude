"""All on-screen graphics, timed to the voice (whisper word times mapped onto the timeline)."""
import json, math
import numpy as np, cv2
from PIL import Image
import gfx as G
from gfx import El, Caption, title, ORANGE, ORANGE_L, NAVY
from core import ROOT, ease_out_cubic, ease_in_cubic, ease_out_back, ease_out_expo, clamp
import timeline as T

WORDS = json.load(open(ROOT + 'felix/words.json'))
EARLY = 0.06   # captions lead the voice slightly


def wt(clip, idx, t_place, src_in, floor=None):
    """timeline time of word idx of clip"""
    w = WORDS[clip]['words'][idx]
    t = t_place + (w['s'] - src_in) - EARLY
    if floor is not None:
        t = max(t, floor)
    return round(t, 3)


def build():
    els = []
    # ================================================================ 1 HOOK
    # TULSA (behind the two of them) + HOMEOWNERS 🚿
    tulsa = title('TULSA', 'black', 175, tracking=-45, shadow=dict(radius=18, offset=(0, 10), opacity=0.5))
    els.append(El(tulsa, 540, 300, 0.03, 2.25, 'blurup', 'blurout', d_in=0.3, dy=60))
    home = title('HOMEOWNERS', 'black', 134, tracking=-45, grad=(ORANGE_L, ORANGE),
                 shadow=dict(radius=18, offset=(0, 10), opacity=0.45))
    els.append(El(home, 540, 455, wt('IMG_9096.wav', 1, 0.0, 0.38, floor=0.3), 2.25, 'blurup', 'blurout', d_in=0.3,
                  dy=60, behind=True))
    c = 'IMG_9096.wav'; tp, si = 0.0, 0.38
    els.append(Caption([('Thinking', 'l', wt(c, 2, tp, si)), ('about', 'l', wt(c, 3, tp, si))], wt(c, 4, tp, si)))
    els.append(Caption([('remodeling', 'l', wt(c, 4, tp, si)), ('your', 'l', wt(c, 5, tp, si)),
                        ('shower?', 'o', wt(c, 6, tp, si))], 3.05))
    els.append(Caption([('Let us', 'l', 3.18), ('help', 'b', wt(c, 9, tp, si)), ('you.', 'b', wt(c, 10, tp, si))], 3.70))
    # ================================================================ 2 West Home Improvement pill
    c = 'IMG_9103.wav'; tp, si = 4.02, 0.08
    els.append(Pill(wt(c, 1, tp, si), 6.25))
    els.append(Caption([('we', 'l', wt(c, 4, tp, si)), ('guide', 'b', wt(c, 5, tp, si)), ('you', 'l', wt(c, 6, tp, si))],
                       wt(c, 7, tp, si)))
    els.append(Caption([('through the', 'l', wt(c, 7, tp, si)), ('entire', 'l', wt(c, 9, tp, si)),
                        ('process.', 'o', wt(c, 10, tp, si))], 7.235))
    # ================================================================ 3 tile / fixtures / finishes
    c = 'IMG_9106.wav'; tp, si = 7.23, 0.0
    els.append(Caption([("We'll", 'l', 7.24), ('help', 'b', wt(c, 1, tp, si)), ('you', 'l', wt(c, 2, tp, si))],
                       wt(c, 3, tp, si)))
    els.append(Caption([('choose', 'l', wt(c, 3, tp, si)), ('the', 'l', wt(c, 4, tp, si)), ('right', 'b', wt(c, 5, tp, si))],
                       T.beat(14)))
    els.append(Scrim(T.beat(14) - 0.02, T.beat(18) + 0.05, y0=480, y1=1250, strength=0.42))
    items = [('TILE', T.beat(14)), ('FIXTURES', T.beat(15.5)), ('FINISHES', T.beat(17))]
    ys = [700, 865, 1030]
    t_out = T.beat(18) - 0.17
    for k, ((txt, ton), y) in enumerate(zip(items, ys)):
        w = title(txt, 'xbold', 132, tracking=-50)
        o = title(txt, 'xbold', 132, tracking=-50, grad=(ORANGE_L, ORANGE))
        nxt = items[k + 1][1] if k + 1 < len(items) else t_out
        els.append(El(o, 540, y, ton, nxt, 'blurup', 'cut', d_in=0.26, dy=55))
        if k + 1 < len(items):
            els.append(El(w, 540, y, nxt, t_out, 'cut', 'blurout', d_in=0.0))
        else:
            pass
    # last item stays orange until the exit
    els.append(El(title('FINISHES', 'xbold', 132, tracking=-50, grad=(ORANGE_L, ORANGE)), 540, ys[2], t_out - 0.0001,
                  t_out, 'cut', 'blurout', d_in=0.0))
    # ================================================================ 4 YOUR HOME. YOUR STYLE.
    els.append(Scrim(T.beat(18), T.beat(22), y0=520, y1=1150, strength=0.4))
    els.append(El(title('your', 'light', 92), 540, 690, T.beat(18) + 0.04, T.beat(20) - 0.12, 'blurup', 'blurout', dy=40))
    els.append(El(title('HOME.', 'black', 230, tracking=-45), 540, 860, T.beat(18) + 0.12, T.beat(20) - 0.12, 'blurup',
                  'blurout', dy=60))
    els.append(El(title('your', 'light', 92), 540, 690, T.beat(20) + 0.04, T.beat(22) - 0.15, 'blurup', 'blurout', dy=40))
    els.append(El(title('STYLE.', 'black', 230, tracking=-45, grad=(ORANGE_L, ORANGE)), 540, 860, T.beat(20) + 0.12,
                  T.beat(22) - 0.15, 'blurup', 'blurout', dy=60))
    # ================================================================ 5 And you know what? ... WE HANDLE EVERYTHING
    c = 'IMG_9111.wav'; tp, si = 13.20, 1.42
    els.append(Caption([('And', 'l', 13.27), ('you', 'l', wt(c, 1, tp, si)), ('know', 'l', wt(c, 2, tp, si)),
                        ('what?', 'b', wt(c, 3, tp, si))], wt(c, 4, tp, si)))
    els.append(Caption([('The', 'l', wt(c, 4, tp, si)), ('best', 'b', wt(c, 5, tp, si)), ('part?', 'o', wt(c, 6, tp, si))],
                       wt(c, 7, tp, si)))
    els.append(El(title('we handle', 'light', 96), 540, 445, wt(c, 7, tp, si), T.beat(26) - 0.1, 'blurup', 'blurout', dy=40))
    els.append(El(title('EVERYTHING.', 'black', 136, tracking=-45), 540, 590, wt(c, 9, tp, si), T.beat(26) - 0.1,
                  'blurup', 'blurout', dy=60, behind=True))
    els.append(Caption([('from', 'l', wt(c, 10, tp, si)), ('demolition', 'b', wt(c, 11, tp, si))], wt(c, 12, tp, si)))
    els.append(Caption([('to the', 'l', wt(c, 12, tp, si)), ('final', 'l', wt(c, 14, tp, si)),
                        ('installation.', 'o', wt(c, 15, tp, si))], T.beat(30) - 0.12))
    # ================================================================ 6 With shower remodels / STARTING AT $9,800
    c = 'IMG_9112.wav'; tp, si = 18.32, 0.40
    els.append(Caption([('With', 'l', 18.37), ('shower', 'b', wt(c, 1, tp, si)), ('remodels', 'l', wt(c, 2, tp, si))],
                       T.beat(32)))
    els.append(Price(t_label=wt(c, 3, tp, si), t_count=wt(c, 5, tp, si), t_land=20.95, t_out=T.beat(36) - 0.12))
    # ================================================================ 7 your dream shower is closer than you might think
    c = 'IMG_9112.wav'; tp, si = 21.72, 4.42
    els.append(Caption([('your', 'l', wt(c, 7, tp, si)), ('dream', 'o', wt(c, 8, tp, si)), ('shower', 'o', wt(c, 9, tp, si))],
                       wt(c, 10, tp, si)))
    els.append(Caption([('is', 'l', wt(c, 10, tp, si)), ('closer', 'b', wt(c, 11, tp, si)), ('than', 'l', wt(c, 12, tp, si))],
                       wt(c, 13, tp, si)))
    els.append(Caption([('you', 'l', wt(c, 13, tp, si)), ('might', 'l', wt(c, 14, tp, si)), ('think.', 'b', wt(c, 15, tp, si))],
                       T.beat(40) - 0.12))
    # ================================================================ 8 Reach out to get started
    els.append(Caption([('Reach', 'b', 24.30), ('out', 'b', 24.62), ('to get', 'l', 24.88), ('started.', 'o', 25.16)],
                       T.beat(43), size=70))
    # ================================================================ 9 END
    tE = T.beat(43)
    els.append(El(title('ready to upgrade', 'light', 82), 540, 640, tE + 0.15, 28.55, 'blurup', 'blurout', dy=40))
    els.append(El(title('YOUR', 'black', 190, tracking=-45), 540, 800, tE + 0.3, 28.55, 'blurup', 'blurout', dy=60))
    els.append(El(title('SHOWER?', 'black', 190, tracking=-45, grad=(ORANGE_L, ORANGE)), 540, 985, tE + 0.48, 28.55,
                  'blurup', 'blurout', dy=60))
    tL = T.beat(64 - 16)   # outro downbeat after the music splice (28.835)
    logo = G.load_logo(ROOT + 'raw/brand/WEST HOME/PNG/Recurso 7@4x.png', 720)
    els.append(El(G.pil_to_spr(logo, radius=20, offset=(0, 10), opacity=0.5), 540, 760, tL, 32.15, 'pop', 'blurout',
                  d_in=0.42, d_out=0.4))
    els.append(Label('DM US TO GET STARTED', tL + 0.6, 32.15, cy=1170))
    els.append(El(title('@felixwesthome', 'light', 50), 540, 1290, tL + 1.2, 32.15, 'rise', 'blurout', dy=40, d_in=0.25,
                  d_out=0.4))
    els.append(Fade(32.12, T.DUR))
    # ================================================================ hook preview card + flashes
    els.append(Card())
    return els


def dot():
    im = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
    from PIL import ImageDraw
    ImageDraw.Draw(im).ellipse((4, 4, 36, 36), fill=ORANGE + (255,))
    return G.pil_to_spr(im, radius=6, offset=(0, 2), opacity=0.4)


# ------------------------------------------------------------------ special elements
class Scrim:
    """soft darkening band behind titles on bright B-roll."""

    def __init__(self, t0, t1, y0, y1, strength=0.4, fade=0.15):
        self.t0, self.t1, self.y0, self.y1, self.s, self.f = t0, t1, y0, y1, strength, fade
        yy = np.arange(T.H, dtype=np.float32)
        c = (y0 + y1) / 2; hw = (y1 - y0) / 2
        prof = np.clip(1 - np.abs(yy - c) / (hw * 1.6), 0, 1) ** 1.4
        self.prof = prof[:, None, None]

    def active(self, t):
        return self.t0 <= t < self.t1

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        k = min(clamp((t - self.t0) / self.f), clamp((self.t1 - t) / self.f))
        canvas *= 1 - self.prof * self.s * k


class Fade:
    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1

    def active(self, t):
        return t >= self.t0

    def draw(self, canvas, t, base=None, mask=None):
        if t >= self.t0:
            canvas *= 1 - clamp((t - self.t0) / (self.t1 - self.t0 - 0.04))


class Pill:
    """smoked-glass dynamic-island pill: circle -> expands -> logo + name."""

    def __init__(self, t_in, t_out, cy=1120):
        self.t_in, self.t_out, self.cy = t_in, t_out, cy
        self.h, self.w = 150, 820
        icon = G.load_logo(ROOT + 'raw/brand/WEST HOME/PNG/Recurso 3@4x.png', 74)
        circ = Image.new('RGBA', (118, 118), (0, 0, 0, 0))
        from PIL import ImageDraw
        ImageDraw.Draw(circ).ellipse((0, 0, 117, 117), fill=ORANGE + (255,))
        circ.alpha_composite(icon, ((118 - icon.width) // 2, (118 - icon.height) // 2))
        self.circ = G.pil_to_spr(circ, shadow=False)
        t1, _ = G.text_rgba('West Home Improvement', 'semi', 46, tracking=-30)
        t2, _ = G.text_rgba('Shower remodeling  ·  Tulsa, OK', 'light', 31, tracking=-15)
        self.t1 = G.pil_to_spr(t1, shadow=False); self.t2 = G.pil_to_spr(t2, shadow=False)

    def active(self, t):
        return self.t_in <= t < self.t_out + 0.35

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        a = t - self.t_in
        h = self.h
        if t < self.t_out:
            s_c = ease_out_back(a / 0.22, 2.0)            # circle pop
            wexp = ease_out_cubic((a - 0.16) / 0.32)       # expand
            txt = ease_out_cubic((a - 0.36) / 0.3)        # text wipe
        else:
            b = t - self.t_out
            txt = 1 - ease_out_cubic(b / 0.14)
            wexp = 1 - ease_out_cubic((b - 0.08) / 0.18)
            s_c = 1 - ease_in_cubic((b - 0.22) / 0.13)
        if s_c <= 0.01:
            return
        w = h + (self.w - h) * clamp(wexp)
        hh = h * clamp(s_c, 0, 1.2)
        x0 = 540 - w / 2; y0 = self.cy - hh / 2
        G.glass(canvas, x0, y0, w, hh, int(hh / 2), tint=0.04, blur=26, border=0.35, dark=0.5)
        ccx = x0 + h / 2
        G.blit(canvas, self.circ, ccx, self.cy, scale=clamp(s_c, 0, 1.2) * 1.0)
        if txt > 0.01:
            tx0 = x0 + h + 8
            right = tx0 + (w - h - 30) * txt

            def mfn(X0, Y0, X1, Y1, right=right):
                xs = np.arange(X0, X1, dtype=np.float32)
                return np.repeat(np.clip((right - xs) / 30, 0, 1)[None, :], Y1 - Y0, 0)

            G.blit(canvas, self.t1, tx0 + self.t1.shape[1] / 2, self.cy - 22, mask_fn=mfn)
            G.blit(canvas, self.t2, tx0 + self.t2.shape[1] / 2, self.cy + 30, opacity=0.85, mask_fn=mfn)


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


def sparkle(canvas, x, y, r):
    if r < 2:
        return
    s = int(r * 2 + 8)
    im = np.zeros((s, s), np.float32)
    c = s // 2
    cv2.line(im, (c, 4), (c, s - 4), 1.0, 2, cv2.LINE_AA)
    cv2.line(im, (4, c), (s - 4, c), 1.0, 2, cv2.LINE_AA)
    im = cv2.GaussianBlur(im, (0, 0), 1.2) + cv2.GaussianBlur(im, (0, 0), 4) * 0.8
    im = np.clip(im, 0, 1)
    x0, y0 = int(x - c), int(y - c)
    reg = canvas[y0:y0 + s, x0:x0 + s]
    col = np.array([150, 210, 255], np.float32)
    canvas[y0:y0 + s, x0:x0 + s] = reg * (1 - im[..., None]) + col * im[..., None]


class Card:
    """floating preview card (reference: video card on her palm, white flash on entry)."""

    def __init__(self):
        import core as C
        s = T.CARD
        self.t0, self.t1 = s['t0'], s['t1']
        self.f, _ = C.srcmap(dict(t0=s['t0'], t1=s['t1'], src_in=s['src_in'], speed=s['speed']))
        plan = json.load(open(ROOT + 'edit/int_plan.json'))
        src, a, b = plan[str(len(T.SHOTS))]
        self.reader = C.Reader(C.int_name(src, a, b), a, C.probe_fps(src))
        self.w, self.h = 270, 480
        self.cx, self.cy = 880, 990
        self.mask = G.rounded_mask(self.w, self.h, 30)
        self.rot = -5.0

    def active(self, t):
        return self.t0 <= t < self.t1 + 0.2

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        a = t - self.t0
        if t < self.t1:
            sc = 0.55 + 0.45 * ease_out_back(a / 0.3, 1.8)
            op = clamp(a / 0.08)
            flash = clamp(1 - a / 0.16)
        else:
            b = (t - self.t1) / 0.2
            sc = 1 - 0.45 * ease_in_cubic(b); op = 1 - b; flash = 0
        fr = self.reader.at(min(self.f(t), self.f(self.t1)))
        k = max(self.w / fr.shape[1], self.h / fr.shape[0]) * 1.08
        fr = cv2.resize(fr, (int(math.ceil(fr.shape[1] * k)), int(math.ceil(fr.shape[0] * k))), interpolation=cv2.INTER_AREA)
        y = (fr.shape[0] - self.h) // 2; x = (fr.shape[1] - self.w) // 2
        fr = fr[y:y + self.h, x:x + self.w].astype(np.float32)
        import core as C
        fr = C.grade(np.clip(fr, 0, 255).astype(np.uint8), 'beige').astype(np.float32)
        fr = fr * (1 - flash) + 255 * flash
        bw = 7
        W2, H2 = self.w + 2 * bw, self.h + 2 * bw
        spr = np.zeros((H2, W2, 4), np.float32)
        outer = G.rounded_mask(W2, H2, 30 + bw)
        spr[..., :3] = 255 * outer[..., None]
        spr[..., 3] = outer
        inner = self.mask
        reg = spr[bw:bw + self.h, bw:bw + self.w]
        reg[..., :3] = reg[..., :3] * (1 - inner[..., None]) + fr * inner[..., None]
        # little label like the reference "600K 👀"
        sprs = G.with_shadow(Image.fromarray((np.dstack([np.clip(spr[..., [2, 1, 0]] / np.maximum(spr[..., 3:4], 1e-3), 0, 255),
                                                         spr[..., 3] * 255])).astype(np.uint8), 'RGBA'),
                             radius=22, offset=(0, 16), opacity=0.5)
        bob = 8 * math.sin(2 * math.pi * a / 1.8)
        G.blit(canvas, sprs, self.cx, self.cy + bob, scale=sc, rot=self.rot, opacity=op)
