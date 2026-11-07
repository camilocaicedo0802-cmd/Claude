"""Typography system modelled on the 'how's going editors' reference:
tight grotesk (Inter Tight), heavy italics with gradient fills, stacked headlines,
one-word captions, flicker/ghost reveals, glossy 3D icon tiles and a light ring."""
import math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from lib import *

def tfont(w, italic, size):
    return _tfont(int(w), bool(italic), int(round(size)))
@functools.lru_cache(maxsize=256)
def _tfont(w, italic, size):
    return ImageFont.truetype(f'{FONT_DIR}/InterTight-{w}{"Italic" if italic else ""}.ttf', size)

GRADS = {
    'lime': (rgb('F2FFB8'), rgb('9BDD3C'), rgb('6CB52A')),
    'green': (rgb('2C8C5E'), rgb('0B5A3D'), rgb('023B28')),
    'mint': (rgb('FFFFFF'), rgb('CFF5E2'), rgb('8EDFBF')),
    'white': ((255, 255, 255),) * 3,
}

def _grad_img(w, h, stops, y0, y1):
    """vertical 3-stop gradient over [y0, y1] (glyph box)."""
    ys = np.clip((np.arange(h) - y0) / max(1, (y1 - y0)), 0, 1)[:, None]
    a, b, c = [np.array(s, np.float32) for s in stops]
    col = np.where(ys < 0.5, a + (b - a) * (ys / 0.5), b + (c - b) * ((ys - 0.5) / 0.5))
    return np.broadcast_to(col[:, None, :], (h, w, 3)).reshape(h, w, 3)

@functools.lru_cache(maxsize=512)
def type_img(text, w=800, italic=False, size=80, fill='white', track=-0.035, shadow=0.45, upper=False):
    """Render text with tracking + gradient. Returns (premul RGBA, pad, baseline_y, advance_width, cap_h)."""
    if upper: text = text.upper()
    f = tfont(w, italic, size)
    tr = track * size
    # x positions with kerning preserved
    xs = [f.getlength(text[:i]) + i * tr for i in range(len(text))]
    adv = (f.getlength(text) + (len(text) - 1) * tr) if text else 0
    asc, desc = f.getmetrics()
    pad = int(size * 0.45)
    W_ = int(adv + 2 * pad + size * 0.3); H_ = int(asc + desc + 2 * pad)
    base = pad + asc
    m = Image.new('L', (W_, H_), 0); d = ImageDraw.Draw(m)
    for ch, x in zip(text, xs):
        d.text((pad + x, base), ch, font=f, fill=255, anchor='ls')
    ma = np.asarray(m).astype(np.float32) / 255
    stops = GRADS[fill] if isinstance(fill, str) else (fill,) * 3
    cap_top = base - f.getbbox('H', anchor='ls')[1] * -1 if False else base + f.getbbox('H', anchor='ls')[1]
    col = _grad_img(W_, H_, stops, cap_top, base) / 255
    out = np.zeros((H_, W_, 4), np.float32)
    if shadow > 0:
        sh = cv2.GaussianBlur(ma, (0, 0), max(1.0, size * 0.07))
        if shadow > 0.6:  # heavier shadow for text over bright UI
            sh = np.maximum(sh, cv2.GaussianBlur(cv2.dilate(ma, np.ones((3, 3), np.uint8)), (0, 0), max(1.0, size * 0.035)))
        sh = np.clip(np.roll(sh, int(size * 0.04), axis=0) * shadow * (1.4 if shadow > 0.6 else 1.0), 0, 1)
        out[..., 3] = sh  # black shadow (premul rgb = 0)
    out[..., :3] = out[..., :3] * (1 - ma[..., None]) + col * ma[..., None]
    out[..., 3] = out[..., 3] * (1 - ma) + ma
    cap_h = -f.getbbox('H', anchor='ls')[1]
    return out, pad, base, adv, cap_h

STY = {
    # stacked headline
    'reg': dict(w=800, italic=False, size=70, fill='white'),
    'ital': dict(w=800, italic=True, size=64, fill='white'),
    'big': dict(w=900, italic=True, size=158, fill='lime', track=-0.045),
    'bigdark': dict(w=900, italic=True, size=158, fill='green', track=-0.045),
    'bigw': dict(w=900, italic=True, size=150, fill='white', track=-0.045),
    # one-word captions
    'word': dict(w=800, italic=True, size=80, fill='white'),
    'caps': dict(w=900, italic=False, size=104, fill='white', upper=True, track=-0.02),
    'key': dict(w=900, italic=True, size=128, fill='lime', track=-0.045),
    # tour captions
    'tsmall': dict(w=700, italic=True, size=56, fill='white', track=-0.02, shadow=0.85),
    'tbig': dict(w=900, italic=True, size=108, fill='lime', track=-0.04, shadow=0.85),
}

def get(text, style, size=None):
    kw = dict(STY[style])
    if size: kw['size'] = size
    return type_img(text, **kw)

def flicker(dt, ghost=False):
    """Opacity / scale / blur for a word that appeared dt seconds ago (reference-style flicker)."""
    if dt < 0: return 0.0, 1.0, 0.0
    if ghost:  # emphasized words: ghost first, then flicker on
        if dt < 0.10: return 0.28, 1.0, 3.0
        dt -= 0.10
    f = int(dt * 30)
    op = [0.45, 1.0, 0.2, 1.0][f] if f < 4 else 1.0
    s = 1 + 0.06 * (1 - e_out(clamp(dt / 0.25)))
    return op, s, 0.0

def draw_word(c, img, x_left, base_y, op, s=1.0, blur=0.0):
    im, pad, by, adv, ch = img
    if op <= 0.003: return
    if blur > 0.3:
        im = cv2.GaussianBlur(im, (0, 0), blur)
    ih, iw = im.shape[:2]
    cx = x_left - pad + iw / 2; cy = base_y - by + ih / 2
    # scale about the glyph centre
    gx = x_left + adv / 2; gy = base_y - ch / 2
    paste(c, im, gx + (cx - gx) * s, gy + (cy - gy) * s, s, 0, op)

def draw_stack(c, t, st):
    """st: dict(y, start, end, lines=[(style, [(word, t)], x_off)], size=None)"""
    if not (st['start'] <= t < st['end'] + 0.22): return
    out = clamp((t - st['end']) / 0.22) if t >= st['end'] else 0.0
    rows = []
    for ln in st['lines']:
        style, words = ln[0], ln[1]
        xo = ln[2] if len(ln) > 2 else 0
        sz = ln[3] if len(ln) > 3 else None
        imgs = [get(w, style, sz) for w, _ in words]
        gap = (sz or STY[style]['size']) * 0.24
        tw = sum(i[3] for i in imgs) + gap * (len(imgs) - 1)
        rows.append((style, words, imgs, gap, tw, xo, sz or STY[style]['size']))
    # tight leading: each line advances by its cap height * 1.18
    hts = [r[6] * 0.86 for r in rows]
    total = sum(hts)
    y = st['y'] - total / 2
    for (style, words, imgs, gap, tw, xo, size), h in zip(rows, hts):
        base = y + h
        x = 540 - tw / 2 + xo
        ghost = style.startswith('big')
        for img, (w, t0) in zip(imgs, words):
            op, s, bl = flicker(t - t0, ghost)
            if out > 0:
                op *= 1 - out; s *= 1 + 0.08 * out; bl = max(bl, 10 * out)
            draw_word(c, img, x, base, op, s, bl)
            x += img[3] + gap
        y += h

def draw_chunks(c, t, y, chunks):
    """one-word captions: chunks [(text, style, t0, t1)]"""
    for text, style, t0, t1 in chunks:
        if t0 <= t < t1:
            img = get(text, style)
            op, s, bl = flicker(t - t0, style == 'key')
            x = 540 - img[3] / 2
            draw_word(c, img, x, y, op, s, bl)


def line_icon(name, size):
    """Simple white line icons (reference uses white outline glyphs)."""
    ss = 4; S_ = size * ss; lw = int(S_ * 0.085)
    im = Image.new('L', (S_, S_), 0); d = ImageDraw.Draw(im)
    W2 = S_
    def R(x0, y0, x1, y1, r=0.12, fill=None):
        d.rounded_rectangle([x0 * W2, y0 * W2, x1 * W2, y1 * W2], int(r * W2), outline=255, width=lw, fill=fill)
    if name == 'calendar':
        R(.12, .2, .88, .88, .12)
        d.line([.12 * W2, .38 * W2, .88 * W2, .38 * W2], fill=255, width=lw)
        for x in (.32, .68): d.line([x * W2, .1 * W2, x * W2, .28 * W2], fill=255, width=lw)
        for i in range(3):
            for j in range(2):
                cx, cy = (.32 + i * .18) * W2, (.54 + j * .17) * W2; r = lw * .7
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    elif name == 'search':
        d.ellipse([.14 * W2, .14 * W2, .66 * W2, .66 * W2], outline=255, width=lw)
        d.line([.6 * W2, .6 * W2, .86 * W2, .86 * W2], fill=255, width=int(lw * 1.4))
    elif name == 'home':
        d.line([(.1 * W2, .5 * W2), (.5 * W2, .14 * W2), (.9 * W2, .5 * W2)], fill=255, width=lw, joint='curve')
        d.line([(.22 * W2, .42 * W2), (.22 * W2, .86 * W2), (.78 * W2, .86 * W2), (.78 * W2, .42 * W2)], fill=255, width=lw, joint='curve')
        R(.41, .6, .59, .86, .04)
    elif name == 'bed':
        d.line([(.1 * W2, .25 * W2), (.1 * W2, .82 * W2)], fill=255, width=lw)
        d.line([(.1 * W2, .66 * W2), (.9 * W2, .66 * W2), (.9 * W2, .82 * W2)], fill=255, width=lw)
        R(.4, .42, .9, .66, .08)
        d.ellipse([.17 * W2, .42 * W2, .35 * W2, .6 * W2], outline=255, width=lw)
    elif name == 'hourglass':
        d.line([(.22 * W2, .12 * W2), (.78 * W2, .12 * W2)], fill=255, width=lw)
        d.line([(.22 * W2, .88 * W2), (.78 * W2, .88 * W2)], fill=255, width=lw)
        d.line([(.28 * W2, .12 * W2), (.28 * W2, .25 * W2), (.5 * W2, .5 * W2), (.28 * W2, .75 * W2), (.28 * W2, .88 * W2)], fill=255, width=lw, joint='curve')
        d.line([(.72 * W2, .12 * W2), (.72 * W2, .25 * W2), (.5 * W2, .5 * W2), (.72 * W2, .75 * W2), (.72 * W2, .88 * W2)], fill=255, width=lw, joint='curve')
        d.polygon([(.36 * W2, .8 * W2), (.64 * W2, .8 * W2), (.5 * W2, .66 * W2)], fill=255)
    elif name == 'check':
        d.line([(.16 * W2, .52 * W2), (.4 * W2, .76 * W2), (.86 * W2, .26 * W2)], fill=255, width=int(lw * 1.5), joint='curve')
    elif name == 'clock':
        d.ellipse([.12 * W2, .12 * W2, .88 * W2, .88 * W2], outline=255, width=lw)
        d.line([(.5 * W2, .26 * W2), (.5 * W2, .5 * W2), (.68 * W2, .62 * W2)], fill=255, width=lw, joint='curve')
    im = im.resize((size, size), Image.LANCZOS)
    out = Image.new('RGBA', (size, size), (255, 255, 255, 0)); out.putalpha(im)
    return out

# ------------------------------------------------------------- icon tiles
TILE_GRADS = {'lime': (rgb('D9F99D'), rgb('7CC52A')), 'green': (rgb('3AA676'), rgb('0B5A3D')),
              'mint': (rgb('A7F0D2'), rgb('2FA07E')), 'gold': (rgb('F1DFA8'), rgb('B8913E')),
              'dark': (rgb('2B6B50'), rgb('012A1C'))}

@functools.lru_cache(maxsize=32)
def icon_tile(emo, grad='lime', size=170, shape='diamond'):
    ss = 3; S_ = size * ss
    top, bot = TILE_GRADS[grad]
    tile = Image.new('RGBA', (S_, S_), (0, 0, 0, 0))
    g = np.zeros((S_, S_, 4), np.uint8)
    yy, xx = np.mgrid[0:S_, 0:S_].astype(np.float32) / S_
    k = np.clip((xx * 0.4 + yy * 0.9) / 1.3, 0, 1)[..., None]
    g[..., :3] = (np.array(top) * (1 - k) + np.array(bot) * k).astype(np.uint8); g[..., 3] = 255
    grad_im = Image.fromarray(g)
    m = Image.new('L', (S_, S_), 0); d = ImageDraw.Draw(m)
    r = int(S_ * 0.22)
    d.rounded_rectangle([0, 0, S_ - 1, S_ - 1], r, fill=255)
    tile.paste(grad_im, (0, 0), m)
    # glossy highlight + bevel
    hl = Image.new('L', (S_, S_), 0); dh = ImageDraw.Draw(hl)
    dh.rounded_rectangle([int(S_ * .06), int(S_ * .05), int(S_ * .94), int(S_ * .5)], int(r * .8), fill=70)
    hl = hl.filter(ImageFilter.GaussianBlur(S_ * 0.04))
    white = Image.new('RGBA', (S_, S_), (255, 255, 255, 0)); white.putalpha(Image.fromarray(np.minimum(np.asarray(hl), np.asarray(m))))
    tile = Image.alpha_composite(tile, white)
    ed = Image.new('RGBA', (S_, S_), (0, 0, 0, 0)); de = ImageDraw.Draw(ed)
    de.rounded_rectangle([2, 2, S_ - 3, S_ - 3], r, outline=(255, 255, 255, 110), width=int(S_ * 0.018))
    tile = Image.alpha_composite(tile, ed)
    tile = tile.resize((size, size), Image.LANCZOS)
    # white glyph from emoji silhouette
    e = line_icon(emo, int(size * 0.5)) if emo.isascii() else emoji_img(emo, int(size * 0.5)).convert('RGBA')
    a = e.split()[3]
    glyph = Image.new('RGBA', e.size, (255, 255, 255, 0)); glyph.putalpha(a)
    gs = Image.new('RGBA', e.size, (0, 40, 20, 0)); gs.putalpha(a.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.35)))
    tile.alpha_composite(gs, (size // 2 - e.width // 2 + 2, size // 2 - e.height // 2 + 4))
    tile.alpha_composite(glyph, (size // 2 - e.width // 2, size // 2 - e.height // 2))
    if shape == 'diamond':
        big = Image.new('RGBA', (int(size * 1.45), int(size * 1.45)), (0, 0, 0, 0))
        big.alpha_composite(tile, ((big.width - size) // 2, (big.height - size) // 2))
        # rotate the tile body but keep the glyph upright: rotate tile without glyph, then re-add glyph
        body = Image.new('RGBA', big.size, (0, 0, 0, 0))
        t2 = icon_tile_body(top, bot, size)
        body.alpha_composite(t2, ((big.width - size) // 2, (big.height - size) // 2))
        body = body.rotate(45, resample=Image.BICUBIC)
        body.alpha_composite(gs, (big.width // 2 - e.width // 2 + 2, big.height // 2 - e.height // 2 + 4))
        body.alpha_composite(glyph, (big.width // 2 - e.width // 2, big.height // 2 - e.height // 2))
        tile = body
    tile, _ = add_shadow(tile, blur=16, off=(0, 14), alpha=0.35, pad=40)
    return pil_premul(tile)

@functools.lru_cache(maxsize=16)
def icon_tile_body(top, bot, size):
    ss = 3; S_ = size * ss
    yy, xx = np.mgrid[0:S_, 0:S_].astype(np.float32) / S_
    k = np.clip((xx * 0.4 + yy * 0.9) / 1.3, 0, 1)[..., None]
    g = np.zeros((S_, S_, 4), np.uint8)
    g[..., :3] = (np.array(top) * (1 - k) + np.array(bot) * k).astype(np.uint8); g[..., 3] = 255
    m = Image.new('L', (S_, S_), 0); r = int(S_ * 0.22)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, S_ - 1, S_ - 1], r, fill=255)
    tile = Image.new('RGBA', (S_, S_), (0, 0, 0, 0)); tile.paste(Image.fromarray(g), (0, 0), m)
    hl = Image.new('L', (S_, S_), 0)
    ImageDraw.Draw(hl).rounded_rectangle([int(S_ * .06), int(S_ * .05), int(S_ * .94), int(S_ * .5)], int(r * .8), fill=80)
    hl = hl.filter(ImageFilter.GaussianBlur(S_ * 0.04))
    w = Image.new('RGBA', (S_, S_), (255, 255, 255, 0)); w.putalpha(Image.fromarray(np.minimum(np.asarray(hl), np.asarray(m))))
    tile = Image.alpha_composite(tile, w)
    ed = Image.new('RGBA', (S_, S_), (0, 0, 0, 0))
    ImageDraw.Draw(ed).rounded_rectangle([2, 2, S_ - 3, S_ - 3], r, outline=(255, 255, 255, 120), width=int(S_ * 0.02))
    tile = Image.alpha_composite(tile, ed)
    return tile.resize((size, size), Image.LANCZOS)

def tile_anim(c, t, t0, img, x, y, t1=None, s=1.0):
    if t < t0: return
    p = prog(t, t0, t0 + 0.38)
    sc = s * e_back(p, 2.4) if p < 1 else s
    rot = -25 * (1 - e_out(p))
    op = clamp((t - t0) / 0.06)
    if t1 is not None and t >= t1:
        q = prog(t, t1, t1 + 0.18); sc *= 1 - e_in(q); op *= 1 - q
        if q >= 1: return
    yy = y + 6 * math.sin((t - t0) * 2.3 + x * 0.01)
    h, w = img.shape[:2]
    warp(c, img, quad3d(w, h, x, yy, max(sc, 0.01), 18 * (1 - p), -14 * (1 - p), rot), op)

# ------------------------------------------------------------- light ring
def light_ring(c, t, t0, t1, cx, cy, r0, r1, person=None, color=(0.75, 0.95, 1.0)):
    """Glowing ring that expands behind the subject (person = premul RGBA of subject in canvas space)."""
    if not (t0 <= t <= t1): return
    p = prog(t, t0, t1)
    r = r0 + (r1 - r0) * e_out(p)
    op = clamp(p / 0.12) * (1 - clamp((p - 0.65) / 0.35))
    sc = 0.5
    h, w = int(H * sc), int(W * sc)
    core = np.zeros((h, w), np.float32)
    cv2.ellipse(core, (int(cx * sc), int(cy * sc)), (int(r * sc), int(r * 1.02 * sc)), -8 + 30 * p, 0, 360, 1.0, max(1, int(4 * sc)), cv2.LINE_AA)
    glow = cv2.GaussianBlur(core, (0, 0), 14) * 4.0 + cv2.GaussianBlur(core, (0, 0), 3) * 1.2
    glow = cv2.resize(glow, (W, H))[..., None] * op
    col = np.array(color, np.float32)
    c += glow * col * 0.9
    np.clip(c, 0, 1, out=c)
    if person is not None:
        a = person[..., 3:]
        c *= (1 - a); c += person[..., :3]

def flash_mix(img, k):
    """bright blurred flash (reference transition). k in [0,1]."""
    if k <= 0.003: return img
    b = gblur(img, 2 + 28 * k)
    b = b * (1 - 0.55 * k) + 0.55 * k
    return np.clip(b * (1 + 0.6 * k), 0, 1)
