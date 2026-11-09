"""Graphics for Cabany reel #3, modelled on 'Video de referencia Cabany 2':
Poppins captions (white SemiBold + green ExtraBold highlights), glowing top box, dashed-ring
number circles, dashed icon boxes, ghost icons, people counter, 3D pillars, comment bar."""
import math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from lib import *

G1 = rgb('C8F56A')   # light top of green text
G2 = rgb('8FD43A')   # main green
G3 = rgb('5CB82C')   # bottom
GLOW = rgb('7EE04A')

def pfont(w, italic, size):
    return _pf(int(w), bool(italic), int(round(size)))
@functools.lru_cache(maxsize=256)
def _pf(w, italic, size):
    return ImageFont.truetype(f'{FONT_DIR}/Poppins-{w}{"Italic" if italic else ""}.ttf', size)

def _mask(text, f, track, pad):
    tr = track * f.size
    xs = [f.getlength(text[:i]) + i * tr for i in range(len(text))]
    adv = (f.getlength(text) + (len(text) - 1) * tr) if text else 0
    asc, desc = f.getmetrics()
    W_ = int(adv + 2 * pad + f.size * 0.3); H_ = int(asc + desc + 2 * pad)
    base = pad + asc
    m = Image.new('L', (W_, H_), 0); d = ImageDraw.Draw(m)
    for ch, x in zip(text, xs):
        d.text((pad + x, base), ch, font=f, fill=255, anchor='ls')
    cap = -f.getbbox('H', anchor='ls')[1]
    return np.asarray(m).astype(np.float32) / 255, base, adv, cap

@functools.lru_cache(maxsize=512)
def text_img(text, weight=600, italic=False, size=64, fill='white', track=-0.01, glow=0.0, shadow=0.55):
    """premultiplied RGBA; returns (img, pad, baseline, advance, cap)"""
    f = pfont(weight, italic, size)
    pad = int(size * 0.55)
    m, base, adv, cap = _mask(text, f, track, pad)
    h, w = m.shape
    out = np.zeros((h, w, 4), np.float32)
    # soft drop shadow
    sh = np.roll(cv2.GaussianBlur(m, (0, 0), max(1.0, size * 0.07)), int(size * 0.05), axis=0) * shadow
    out[..., 3] = np.clip(sh, 0, 1)
    if fill == 'green':
        yy = np.arange(h, dtype=np.float32)[:, None]
        p = np.clip((yy - (base - cap)) / max(1, cap), 0, 1)
        a, b, c = [np.array(x, np.float32) / 255 for x in (G1, G2, G3)]
        col = np.where(p[..., None] < 0.5, a + (b - a) * (p[..., None] / 0.5), b + (c - b) * ((p[..., None] - 0.5) / 0.5))
        col = np.broadcast_to(col, (h, w, 3))
    else:
        col = np.ones((h, w, 3), np.float32)
    if glow > 0:
        g = np.clip(cv2.GaussianBlur(m, (0, 0), size * 0.18) * glow, 0, 1)
        gc = np.array(GLOW, np.float32) / 255 if fill == 'green' else np.ones(3, np.float32)
        out[..., :3] = out[..., :3] * (1 - g[..., None]) + gc * g[..., None]
        out[..., 3] = out[..., 3] * (1 - g) + g
    out[..., :3] = out[..., :3] * (1 - m[..., None]) + col * m[..., None]
    out[..., 3] = out[..., 3] * (1 - m) + m
    return out, pad, base, adv, cap

STY = {
    'w': dict(weight=600, size=64),                               # white SemiBold phrase
    'wb': dict(weight=700, size=70),                              # white Bold
    'g': dict(weight=800, size=100, fill='green', track=-0.02, glow=0.25),        # green ExtraBold
    'gi': dict(weight=800, italic=True, size=100, fill='green', track=-0.02, glow=0.25),
    'gc': dict(weight=800, size=92, fill='green', track=-0.01, glow=0.25),        # green caps
    'wc': dict(weight=800, italic=True, size=88, track=0.0),     # white ExtraBold Italic caps
    'num': dict(weight=800, italic=True, size=190, fill='green', glow=0.35),
    'big': dict(weight=800, size=150, fill='green', track=-0.02, glow=0.45),
}

def get(text, style, size=None):
    kw = dict(STY[style])
    if size: kw['size'] = size
    if style in ('gc', 'wc'): text = text.upper()
    return text_img(text, **kw)

def put(c, img, x_left, base_y, op=1.0, s=1.0, blur=0.0):
    im, pad, by, adv, cap = img
    if op <= 0.003: return
    if blur > 0.3: im = cv2.GaussianBlur(im, (0, 0), blur)
    ih, iw = im.shape[:2]
    cx = x_left - pad + iw / 2; cy = base_y - by + ih / 2
    gx = x_left + adv / 2; gy = base_y - cap / 2
    paste(c, im, gx + (cx - gx) * s, gy + (cy - gy) * s, s, 0, op)

def pop_state(t, t0, t1, pop=0.16, out=0.07):
    """reference word animation: quick scale-down pop + blur-in, quick fade-out."""
    if t < t0 or t >= t1 + out: return None
    p = prog(t, t0, t0 + pop)
    s = 1.22 - 0.22 * e_out(p)
    op = clamp((t - t0) / 0.05)
    bl = 6 * (1 - e_out(p))
    if t >= t1:
        q = prog(t, t1, t1 + out); op *= 1 - q; bl = max(bl, 8 * q)
    return op, s, bl

def caption(c, t, cap, y):
    """cap: dict(t0, t1, lines=[(style, text, t_line)], x=None)"""
    if not (cap['t0'] <= t < cap['t1'] + 0.08): return
    rows = []
    for st, txt, tl in cap['lines']:
        img = get(txt, st)
        while img[3] > 980: img = get(txt, st, int(STY[st]['size'] * 980 / img[3]))
        rows.append((img, tl, st))
    hts = [r[0][4] * (1.42 if r[2] in ('w', 'wb') else 1.18) for r in rows]
    yy = y - sum(hts) / 2
    for (img, tl, st), h in zip(rows, hts):
        base = yy + h * (0.86 if st in ('w', 'wb') else 0.92)
        ps = pop_state(t, tl, cap['t1'])
        if ps:
            put(c, img, cap.get('x', 540) - img[3] / 2, base, ps[0], ps[1], ps[2])
        yy += h

def number_word(c, t, n, word, t0, t_word, t1, y, x_center=540):
    """'1 SOLUTIONS' layout: big green italic number + white italic caps word."""
    num = get(str(n), 'num'); wd = get(word, 'wc')
    gap = 26
    total = num[3] + gap + wd[3]
    x0 = x_center - total / 2
    ps = pop_state(t, t0, t1, 0.2)
    if ps: put(c, num, x0, y + num[4] * 0.42, ps[0], ps[1], ps[2])
    ps = pop_state(t, t_word, t1)
    if ps: put(c, wd, x0 + num[3] + gap, y + wd[4] * 0.5, ps[0], ps[1], ps[2])

# ------------------------------------------------------------------ glowing top box
def glow_box(c, t, t0, t1, cx, cy, w, h, alpha=0.55):
    if t < t0 or t >= t1 + 0.15: return 0.0
    op = clamp((t - t0) / 0.12) * (1 - clamp((t - t1) / 0.15))
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    m = np.asarray(rounded_mask(int(w), int(h), 26)).astype(np.float32) / 255
    X0, Y0 = max(0, x0), max(0, y0); X1, Y1 = min(W, x0 + int(w)), min(H, y0 + int(h))
    mm = m[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, None] * op
    reg = c[Y0:Y1, X0:X1]
    bl = cv2.GaussianBlur(reg, (0, 0), 10)
    reg[:] = reg * (1 - mm) + (bl * 0.45 + np.array((0.02, 0.05, 0.03), np.float32)) * mm * (1 - alpha * 0.3) + reg * 0 * mm
    return op

@functools.lru_cache(maxsize=8)
def house_glyph(size):
    """bold glowing house symbol (like the reference's glowing $ glyphs)"""
    ss = 3; S_ = size * ss
    m = Image.new('L', (S_, S_), 0); d = ImageDraw.Draw(m)
    d.polygon([(.5 * S_, .06 * S_), (.96 * S_, .48 * S_), (.84 * S_, .48 * S_), (.84 * S_, .94 * S_), (.16 * S_, .94 * S_), (.16 * S_, .48 * S_), (.04 * S_, .48 * S_)], fill=255)
    d.rectangle([.42 * S_, .64 * S_, .58 * S_, .94 * S_], fill=0)
    d.rectangle([.62 * S_, .1 * S_, .74 * S_, .34 * S_], fill=255)
    m = np.asarray(m.resize((size, size), Image.LANCZOS)).astype(np.float32) / 255
    pad = size // 2
    m = np.pad(m, pad)
    h, w = m.shape
    yy = np.arange(h, dtype=np.float32)[:, None]
    p = np.clip((yy - pad) / size, 0, 1)
    a, b, c_ = [np.array(x, np.float32) / 255 for x in (G1, G2, G3)]
    col = np.where(p[..., None] < 0.5, a + (b - a) * (p[..., None] / 0.5), b + (c_ - b) * ((p[..., None] - 0.5) / 0.5))
    col = np.broadcast_to(col, (h, w, 3))
    g = np.clip(cv2.GaussianBlur(m, (0, 0), size * 0.14) * 0.7, 0, 1)
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = np.array(GLOW, np.float32) / 255 * g[..., None]; out[..., 3] = g
    out[..., :3] = out[..., :3] * (1 - m[..., None]) + col * m[..., None]
    out[..., 3] = out[..., 3] * (1 - m) + m
    return out

def drop_in(c, t, t0, img, x, y, t1=None, dy=-120, s0=1.0):
    if t < t0: return
    p = prog(t, t0, t0 + 0.22)
    yy = y + dy * (1 - e_back(p, 1.6))
    op = clamp((t - t0) / 0.06)
    s = s0
    if t1 is not None and t >= t1:
        q = prog(t, t1, t1 + 0.15); op *= 1 - q; s *= 1 + 0.1 * q
        if q >= 1: return
    bl = 0
    im = img if p > 0.6 else cv2.GaussianBlur(img, (0, 0), 1 + 5 * (1 - p))
    paste(c, im, x, yy, s, 0, op)

# ------------------------------------------------------------------ number circles
@functools.lru_cache(maxsize=4)
def num_circle(n, size=130):
    ss = 3; S_ = size * ss
    im = Image.new('RGBA', (S_, S_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([8 * ss, 8 * ss, S_ - 8 * ss, S_ - 8 * ss], fill=(12, 14, 12, 235))
    d.ellipse([12 * ss, 12 * ss, S_ - 12 * ss, S_ - 12 * ss], outline=(255, 255, 255, 230), width=5 * ss)
    # dashed outer ring
    r = S_ / 2 - 2 * ss
    for k in range(28):
        a0 = k / 28 * 360; a1 = a0 + 7
        d.arc([S_ / 2 - r, S_ / 2 - r, S_ / 2 + r, S_ / 2 + r], a0, a1, fill=G2 + (255,), width=3 * ss)
    f = pfont(800, True, int(size * 0.62) * ss)
    d.text((S_ / 2, S_ / 2 + 4 * ss), str(n), font=f, fill=(255, 255, 255, 255), anchor='mm')
    im = im.resize((size, size), Image.LANCZOS)
    im, _ = add_shadow(im, blur=12, off=(0, 8), alpha=0.4, pad=30)
    return pil_premul(im)

# ------------------------------------------------------------------ dashed icon boxes
def _dashed_rect(d, box, color, width, dash=14, gap=9, r=18):
    x0, y0, x1, y1 = box
    for (a, b) in [((x0 + r, y0), (x1 - r, y0)), ((x1, y0 + r), (x1, y1 - r)), ((x1 - r, y1), (x0 + r, y1)), ((x0, y1 - r), (x0, y0 + r))]:
        L = math.dist(a, b); n = int(L // (dash + gap)) + 1
        for k in range(n):
            s0 = k * (dash + gap) / L; s1 = min(1, (k * (dash + gap) + dash) / L)
            d.line([(a[0] + (b[0] - a[0]) * s0, a[1] + (b[1] - a[1]) * s0), (a[0] + (b[0] - a[0]) * s1, a[1] + (b[1] - a[1]) * s1)], fill=color, width=width)
    for cx, cy, a0 in [(x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], a0 + 20, a0 + 70, fill=color, width=width)

@functools.lru_cache(maxsize=16)
def icon_box(kind, label=None, size=210):
    ss = 2; S_ = size * ss
    im = Image.new('RGBA', (S_, S_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, S_ - 1, S_ - 1], 22 * ss, fill=(10, 14, 11, 215))
    inner = (int(S_ * 0.1), int(S_ * 0.1), int(S_ * 0.9), int(S_ * (0.74 if label else 0.9)))
    if kind.endswith('.webp'):
        ph = cover(Image.open(f'{ROOT}/site/img/{kind}').convert('RGB'), inner[2] - inner[0], inner[3] - inner[1])
        im.paste(ph, inner[:2], rounded_mask(inner[2] - inner[0], inner[3] - inner[1], 14 * ss))
    else:
        draw_icon(d, kind, inner, ss)
    if label:
        f = pfont(800, False, int(size * 0.17) * ss)
        d.text((S_ / 2, S_ * 0.86), label, font=f, fill=G2 + (255,), anchor='mm')
    _dashed_rect(d, (3 * ss, 3 * ss, S_ - 3 * ss, S_ - 3 * ss), G2 + (255,), 3 * ss, 12 * ss, 8 * ss, 22 * ss)
    im = im.resize((size, size), Image.LANCZOS)
    # outer glow
    a = np.asarray(im)[..., 3].astype(np.float32) / 255
    g = np.clip(cv2.GaussianBlur(a, (0, 0), 10) * 0.35, 0, 1)
    pad = 40
    out = np.zeros((size + 2 * pad, size + 2 * pad, 4), np.float32)
    gp = np.pad(g, pad); out[..., :3] = np.array(GLOW, np.float32) / 255 * gp[..., None] * 0.8; out[..., 3] = gp * 0.8
    src = pil_premul(im); sp = np.pad(src, ((pad, pad), (pad, pad), (0, 0)))
    out = out * (1 - sp[..., 3:]) + sp
    return out

def draw_icon(d, kind, box, ss):
    x0, y0, x1, y1 = box; w = x1 - x0; h = y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    lw = int(5 * ss)
    wh = (245, 245, 245, 255)
    if kind == 'card':
        d.rounded_rectangle([cx - w * .4, cy - h * .26, cx + w * .4, cy + h * .26], 10 * ss, fill=(235, 235, 235, 255))
        d.rectangle([cx - w * .4, cy - h * .14, cx + w * .4, cy - h * .04], fill=(40, 40, 40, 255))
        d.rounded_rectangle([cx - w * .3, cy + h * .06, cx - w * .1, cy + h * .16], 3 * ss, fill=G2 + (255,))
    elif kind == 'phonepay':
        d.rounded_rectangle([cx - w * .2, cy - h * .38, cx + w * .2, cy + h * .38], 12 * ss, fill=(235, 235, 235, 255))
        d.rounded_rectangle([cx - w * .16, cy - h * .3, cx + w * .16, cy + h * .26], 6 * ss, fill=(30, 34, 32, 255))
        d.line([(cx - w * .08, cy - h * .02), (cx - w * .01, cy + h * .07), (cx + w * .1, cy - h * .1)], fill=G2 + (255,), width=lw, joint='curve')
    elif kind == 'calendar':
        d.rounded_rectangle([cx - w * .36, cy - h * .3, cx + w * .36, cy + h * .36], 10 * ss, fill=(240, 240, 240, 255))
        d.rectangle([cx - w * .36, cy - h * .3, cx + w * .36, cy - h * .1], fill=G3 + (255,))
        f = pfont(800, False, int(h * .32))
        d.text((cx, cy + h * .14), 'NOV', font=f, fill=(20, 20, 20, 255), anchor='mm')
        for x in (-.18, .18): d.rounded_rectangle([cx + w * x - 4 * ss, cy - h * .4, cx + w * x + 4 * ss, cy - h * .22], 3 * ss, fill=(200, 200, 200, 255))

# ------------------------------------------------------------------ ghost icons (behind subject)
@functools.lru_cache(maxsize=4)
def ghost_check(size):
    ss = 2; S_ = size * ss
    m = Image.new('L', (S_, S_), 0); d = ImageDraw.Draw(m)
    d.line([(.14 * S_, .54 * S_), (.4 * S_, .8 * S_), (.88 * S_, .22 * S_)], fill=255, width=int(.16 * S_), joint='curve')
    for x, y in [(.14, .54), (.88, .22)]: d.ellipse([(x - .08) * S_, (y - .08) * S_, (x + .08) * S_, (y + .08) * S_], fill=255)
    m = np.asarray(m.resize((size, size), Image.LANCZOS)).astype(np.float32) / 255
    pad = size // 3; m = np.pad(m, pad)
    g = np.clip(cv2.GaussianBlur(m, (0, 0), size * 0.06) * 0.9, 0, 1)
    out = np.zeros(m.shape + (4,), np.float32)
    a = np.maximum(m * 0.55, g * 0.5)
    out[..., :3] = a[..., None]; out[..., 3] = a
    return out

# ------------------------------------------------------------------ people counter
@functools.lru_cache(maxsize=2)
def person_icon(size=96):
    ss = 3; S_ = size * ss
    m = Image.new('L', (S_, S_), 0); d = ImageDraw.Draw(m)
    d.ellipse([.32 * S_, .04 * S_, .68 * S_, .4 * S_], fill=255)
    d.rounded_rectangle([.14 * S_, .46 * S_, .86 * S_, 1.1 * S_], int(.3 * S_), fill=255)
    m = np.asarray(m.resize((size, size), Image.LANCZOS)).astype(np.float32) / 255
    pad = 16; m = np.pad(m, pad)
    h, w = m.shape
    yy = np.arange(h, dtype=np.float32)[:, None]; p = np.clip((yy - pad) / size, 0, 1)
    a, b = np.array(G1, np.float32) / 255, np.array(G3, np.float32) / 255
    col = np.broadcast_to(a + (b - a) * p[..., None], (h, w, 3))
    g = np.clip(cv2.GaussianBlur(m, (0, 0), 8) * 0.6, 0, 1)
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = np.array(GLOW, np.float32) / 255 * g[..., None]; out[..., 3] = g
    out[..., :3] = out[..., :3] * (1 - m[..., None]) + col * m[..., None]; out[..., 3] = out[..., 3] * (1 - m) + m
    return out

# ------------------------------------------------------------------ 3D pillars chart
def pillar(c, x, base_y, w, d, h, col_front, col_side, col_top, cam_dx=0.0):
    """isometric-ish extruded box; x = left of front face, base_y = bottom."""
    if h <= 1: return None
    dx, dy = d * (0.55 + cam_dx), -d * 0.42
    front = [(x, base_y - h), (x + w, base_y - h), (x + w, base_y), (x, base_y)]
    side = [(x + w, base_y - h), (x + w + dx, base_y - h + dy), (x + w + dx, base_y + dy), (x + w, base_y)]
    top = [(x, base_y - h), (x + dx, base_y - h + dy), (x + w + dx, base_y - h + dy), (x + w, base_y - h)]
    sc = 2
    for poly, col in [(side, col_side), (front, col_front), (top, col_top)]:
        mk = np.zeros((H // sc, W // sc), np.float32)
        cv2.fillConvexPoly(mk, (np.array(poly) / sc * 16).astype(np.int32), 1.0, cv2.LINE_AA, 4)
        mk = cv2.resize(mk, (W, H))[..., None]
        if callable(col): colimg = col(poly)
        else: colimg = np.array(col, np.float32)
        c[:] = c * (1 - mk) + colimg * mk
    return front

def vgrad(poly, top_col, bot_col):
    ys = [p[1] for p in poly]; y0, y1 = min(ys), max(ys)
    yy = np.linspace(0, 1, H, dtype=np.float32)
    p = np.clip((np.arange(H, dtype=np.float32) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
    a = np.array(top_col, np.float32); b = np.array(bot_col, np.float32)
    return np.broadcast_to(a + (b - a) * p, (H, W, 3))

# ------------------------------------------------------------------ comment bar
@functools.lru_cache(maxsize=32)
def comment_bar(typed, sent=False, btn_hover=False):
    w, h = 900, 150
    ss = 2
    im = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], 40 * ss, fill=(255, 255, 255, 250))
    im = im.resize((w, h), Image.LANCZOS); d = ImageDraw.Draw(im)
    # avatar
    av = Image.new('RGBA', (96, 96), (0, 0, 0, 0)); da = ImageDraw.Draw(av)
    da.ellipse([0, 0, 95, 95], fill=GREEN + (255,))
    lg = Image.open(f'{ROOT}/brand/logo-white.png').convert('RGBA'); lg = lg.crop(lg.getbbox())
    lw = 78; lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    av.alpha_composite(lg, (48 - lw // 2, 48 - lg.height // 2))
    im.alpha_composite(av, (26, 27))
    d.text((136, 56), 'cabanypanama', font=pfont(700, False, 25), fill=(20, 20, 20, 255), anchor='lm')
    d.text((136, 94), 'Comenta', font=pfont(500, False, 22), fill=(120, 125, 130, 255), anchor='lm')
    # input pill
    bx0, bx1 = 500, 760
    d.rounded_rectangle([bx0 - 150, 36, bx1, 114], 39, fill=(242, 244, 242, 255), outline=(220, 224, 220, 255), width=2)
    txt = typed if typed else 'Escribe aquí...'
    col = (20, 20, 20, 255) if typed else (150, 155, 160, 255)
    d.text((bx0 - 124, 75), txt, font=pfont(800 if typed else 500, False, 30 if typed else 24), fill=col, anchor='lm')
    # send button
    bc = G3 if btn_hover else G2
    d.rounded_rectangle([778, 36, 876, 114], 39, fill=(bc if not sent else GREEN) + (255,))
    if sent:
        d.line([(808, 76), (822, 90), (848, 60)], fill=(255, 255, 255, 255), width=7, joint='curve')
    else:
        d.text((827, 75), 'Enviar', font=pfont(700, False, 24), fill=(255, 255, 255, 255), anchor='mm')
    im, _ = add_shadow(im, blur=22, off=(0, 12), alpha=0.35, pad=40)
    return pil_premul(im)

@functools.lru_cache(maxsize=1)
def cursor_img():
    ss = 3; S_ = 64 * ss
    im = Image.new('RGBA', (S_, S_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(.1, .05), (.1, .78), (.3, .6), (.45, .92), (.58, .86), (.44, .55), (.7, .55)]
    d.polygon([(x * S_, y * S_) for x, y in pts], fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=3 * ss)
    im = im.resize((64, 64), Image.LANCZOS)
    im, _ = add_shadow(im, blur=4, off=(2, 3), alpha=0.4, pad=10)
    return pil_premul(im)
