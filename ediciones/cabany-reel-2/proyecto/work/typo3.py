"""Typography & motion system modelled on 'Video de referencia Cabany':
Urbanist (geometric, single-storey a/g) — huge black-weight words with a luminous
gradient + holographic texture + glow (green instead of the reference's pink), thin white
lead-in words overlapping them, small white chest words, frosted-glass pills,
double-line white icons that draw themselves on, and an iOS-style banner."""
import math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from lib import *

def ufont(w, italic, size):
    return _ufont(int(w), bool(italic), int(round(size)))
@functools.lru_cache(maxsize=256)
def _ufont(w, italic, size):
    return ImageFont.truetype(f'{FONT_DIR}/Urbanist-{w}{"Italic" if italic else ""}.ttf', size)

# ------------------------------------------------------------------ glyph rendering
def _glyph_mask(text, f, track, pad):
    tr = track * f.size
    xs = [f.getlength(text[:i]) + i * tr for i in range(len(text))]
    adv = (f.getlength(text) + (len(text) - 1) * tr) if text else 0
    asc, desc = f.getmetrics()
    W_ = int(adv + 2 * pad + f.size * 0.25); H_ = int(asc + desc + 2 * pad)
    base = pad + asc
    m = Image.new('L', (W_, H_), 0); d = ImageDraw.Draw(m)
    for ch, x in zip(text, xs):
        d.text((pad + x, base), ch, font=f, fill=255, anchor='ls')
    cap = -f.getbbox('H', anchor='ls')[1]
    return np.asarray(m).astype(np.float32) / 255, base, adv, cap

GREEN_STOPS = (rgb('F1FFC4'), rgb('B5F05A'), rgb('5FC23C'))

@functools.lru_cache(maxsize=256)
def big_word(text, size=190, seed=0):
    """Huge highlight word: luminous green gradient + holographic marble texture + glow."""
    f = ufont(900, False, size)
    pad = int(size * 0.45)
    m, base, adv, cap = _glyph_mask(text, f, -0.035, pad)
    h, w = m.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    top = base - cap * 1.02; bot = base + size * 0.22
    p = np.clip((yy - top) / max(1, bot - top), 0, 1)
    a, b_, c_ = [np.array(s, np.float32) / 255 for s in GREEN_STOPS]
    col = np.where(p[..., None] < 0.5, a + (b_ - a) * (p[..., None] / 0.5), b_ + (c_ - b_) * ((p[..., None] - 0.5) / 0.5))
    # holographic marble: soft bands of light/mint/yellow drifting through the letters
    r = np.random.default_rng(seed + len(text))
    ph = r.uniform(0, 6.28, 3)
    k = (np.sin(xx * 0.018 + 2.4 * np.sin(yy * 0.021 + ph[0]) + ph[1]) * 0.5 + 0.5)
    k2 = (np.sin(xx * 0.043 - yy * 0.017 + ph[2]) * 0.5 + 0.5)
    tex = (k * 0.65 + k2 * 0.35)[..., None]
    mint = np.array(rgb('D8FFF0'), np.float32) / 255
    yel = np.array(rgb('F4FF9E'), np.float32) / 255
    col = col * (0.86 + 0.24 * tex) + (mint * (tex > 0.72) * (tex - 0.72) * 0.9) + yel * (1 - tex) * 0.05
    # glossy top band
    gl = np.clip(1 - np.abs(p - 0.18) / 0.16, 0, 1)[..., None] * 0.16
    col = np.clip(col + gl, 0, 1)
    out = np.zeros((h, w, 4), np.float32)
    glow = cv2.GaussianBlur(m, (0, 0), size * 0.11)
    sh = np.roll(cv2.GaussianBlur(m, (0, 0), size * 0.05), int(size * 0.035), axis=0)
    ga = np.clip(glow * 0.55, 0, 1); sa = np.clip(sh * 0.42, 0, 1)
    gcol = np.array(rgb('7DEB3C'), np.float32) / 255
    # layer: shadow (black) -> glow (green) -> glyph
    out[..., 3] = sa
    out[..., :3] = out[..., :3] * (1 - ga[..., None]) + gcol * ga[..., None]
    out[..., 3] = out[..., 3] * (1 - ga) + ga
    out[..., :3] = out[..., :3] * (1 - m[..., None]) + col * m[..., None]
    out[..., 3] = out[..., 3] * (1 - m) + m
    return out, pad, base, adv, cap

@functools.lru_cache(maxsize=512)
def white_word(text, weight=300, italic=False, size=72, track=-0.02, shadow=0.5, glow=0.0, color=(255, 255, 255)):
    f = ufont(weight, italic, size)
    pad = int(size * 0.45)
    m, base, adv, cap = _glyph_mask(text, f, track, pad)
    h, w = m.shape
    out = np.zeros((h, w, 4), np.float32)
    sh = np.roll(cv2.GaussianBlur(m, (0, 0), max(1, size * 0.06)), int(size * 0.03), axis=0) * shadow
    out[..., 3] = np.clip(sh, 0, 1)
    if glow > 0:
        g = np.clip(cv2.GaussianBlur(m, (0, 0), size * 0.12) * glow, 0, 1)
        out[..., :3] = out[..., :3] * (1 - g[..., None]) + g[..., None]
        out[..., 3] = out[..., 3] * (1 - g) + g
    col = np.array(color, np.float32) / 255
    out[..., :3] = out[..., :3] * (1 - m[..., None]) + col * m[..., None]
    out[..., 3] = out[..., 3] * (1 - m) + m
    return out, pad, base, adv, cap

STY = {
    'big': lambda t, s=None: big_word(t, s or 190),
    'thin': lambda t, s=None: white_word(t, 300, False, s or 74),
    'thini': lambda t, s=None: white_word(t, 300, True, s or 80),
    'heavy': lambda t, s=None: white_word(t, 800, False, s or 70, -0.02, 0.6),
    'chest': lambda t, s=None: white_word(t, 400, False, s or 60, -0.01, 0.65),
    'chesti': lambda t, s=None: white_word(t, 300, True, s or 82, -0.01, 0.6),
}

def motion(img, dx, dy):
    """directional blur on a small premultiplied word image"""
    k = int(max(abs(dx), abs(dy)))
    if k < 2: return img
    if abs(dx) >= abs(dy): return cv2.blur(img, (k, 1))
    return cv2.blur(img, (1, k))

def put(c, img, x_left, base_y, op=1.0, s=1.0, blur=(0, 0), extra_blur=0):
    im, pad, by, adv, cap = img
    if op <= 0.003: return
    if blur != (0, 0): im = motion(im, *blur)
    if extra_blur > 0.3: im = cv2.GaussianBlur(im, (0, 0), extra_blur)
    ih, iw = im.shape[:2]
    cx = x_left - pad + iw / 2; cy = base_y - by + ih / 2
    gx = x_left + adv / 2; gy = base_y - cap / 2
    paste(c, im, gx + (cx - gx) * s, gy + (cy - gy) * s, s, 0, op)

def enter(t, t0, t1, kind='rise', life_drift=0.06):
    """returns (opacity, scale, dx, dy, motion blur) for an element alive in [t0, t1)."""
    if t < t0 or t >= t1 + 0.12: return None
    p = prog(t, t0, t0 + 0.17); e = e_out(p)
    op = clamp((t - t0) / 0.06)
    s = 1 + life_drift * prog(t, t0, max(t1, t0 + 0.5))
    dx = dy = 0; bl = (0, 0)
    if kind == 'rise':
        dy = 90 * (1 - e); s *= 1.12 - 0.12 * e; bl = (0, 40 * (1 - e))
    elif kind == 'whip':
        dx = -260 * (1 - e); bl = (70 * (1 - e), 0)
    elif kind == 'pop':
        s *= 0.6 + 0.4 * e_back(p, 2.2)
    elif kind == 'fade':
        pass
    if t >= t1:  # exit
        q = prog(t, t1, t1 + 0.08); op *= 1 - q; s *= 1 + 0.06 * q; bl = (0, 30 * q)
    return op, s, dx, dy, bl

# ------------------------------------------------------------------ layouts
def headline(c, t, H_, layer='all'):
    """H_: dict(y=baseline of big word, t0, t1, big=[(word, t)], thin=(text, t), heavy=(text, t), kind, size, x)"""
    if not (H_['t0'] - 0.01 <= t < H_['t1'] + 0.12): return
    size = H_.get('size', 190)
    bigs = [(w, tw) for w, tw in H_['big'] if tw <= t]
    y = H_['y']; xc = H_.get('x', 540)
    if layer == 'front':
        bigs_front = bigs
    if bigs and layer != 'front':
        # only the latest big word is shown (reference swaps them in place)
        w, tw = bigs[-1]
        nxt = [tt for _, tt in H_['big'] if tt > tw]
        t_end = min(nxt[0] if nxt else H_['t1'], H_['t1'])
        img = big_word(w, size)
        while img[3] > 1000 and size > 90:
            size = int(size * 0.9); img = big_word(w, size)
        st = enter(t, tw, t_end, H_.get('kind', 'rise'))
        if st:
            op, s, dx, dy, bl = st
            x = xc - img[3] / 2
            put(c, img, x + dx, y + dy, op, s, bl)
            bx0, bx1 = x, x + img[3]
        else:
            bx0, bx1 = xc - 300, xc + 300
    else:
        img = None; bx0, bx1 = xc - 300, xc + 300
    if bigs and layer == 'front':
        w, tw = bigs[-1]
        im2 = big_word(w, size)
        while im2[3] > 1000 and size > 90:
            size = int(size * 0.9); im2 = big_word(w, size)
        bx0, bx1 = xc - im2[3] / 2, xc + im2[3] / 2
    if H_.get('thin') and layer != 'front':
        txt, tt = H_['thin']
        words = txt.split(' ')
        wt = tt if isinstance(tt, (list, tuple)) else [tt] * len(words)
        shown = ' '.join(wd for wd, ti in zip(words, wt) if ti <= t)
        if shown:
            im = white_word(shown, 300, False, int(size * 0.39))
            full = white_word(txt, 300, False, int(size * 0.39))
            st = enter(t, wt[0], H_['t1'], 'fade', 0.04)
            if st:
                x = bx0 - full[3] * 0.10
                put(c, im, x, y - size * 0.62, st[0], st[1])
    if H_.get('heavy') and layer != 'behind':
        txt, tt = H_['heavy']
        words = txt.split(' ')
        wt = tt if isinstance(tt, (list, tuple)) else [tt] * len(words)
        shown = ' '.join(wd for wd, ti in zip(words, wt) if ti <= t)
        if shown:
            im = white_word(shown, 800, False, int(size * 0.36), -0.02, 0.6)
            full = white_word(txt, 800, False, int(size * 0.36), -0.02, 0.6)
            st = enter(t, wt[0], H_['t1'], 'pop', 0.03)
            if st:
                x = min(bx1 + 30, 1040) - full[3]
                put(c, im, x, y + size * 0.20, st[0], st[1])

def chest(c, t, y, items):
    """items: [(text, style, t0, t1)] — one at a time, centred."""
    for text, style, t0, t1 in items:
        st = enter(t, t0, t1, 'fade', 0.05)
        if st and t < t1 + 0.12:
            img = STY[style](text)
            put(c, img, 540 - img[3] / 2, y, st[0], st[1])

# ------------------------------------------------------------------ frosted glass pill
@functools.lru_cache(maxsize=32)
def pill_parts(text, size=54, icon=None):
    f = ufont(600, False, size)
    tw = f.getlength(text)
    h = int(size * 2.0); ic = int(h * 0.62) if icon else 0
    w = int(tw + h * 0.9 + (ic + h * 0.18 if icon else 0))
    ss = 3
    m = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], h * ss // 2, fill=255)
    m = np.asarray(m.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    ring = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(ring).rounded_rectangle([2, 2, w * ss - 3, h * ss - 3], h * ss // 2, outline=255, width=int(2.2 * ss))
    ring = np.asarray(ring.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    fg = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(fg)
    x = h * 0.45
    if icon:
        cx, cy, r = x + ic / 2, h / 2, ic / 2
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=LIME_B + (255,))
        e = emoji_img(icon, int(ic * 0.56)); fg.alpha_composite(e, (int(cx - e.width / 2), int(cy - e.height / 2)))
        x += ic + h * 0.18
    d.text((x, h / 2 + size * 0.04), text, font=f, fill=(255, 255, 255, 255), anchor='lm')
    return m, ring, pil_premul(fg)

def glass_pill(c, t, t0, t1, text, x, y, size=54, icon=None):
    st = enter(t, t0, t1, 'pop', 0.04)
    if not st: return
    op, s, *_ = st
    m, ring, fg = pill_parts(text, size, icon)
    h, w = m.shape
    sw, sh_ = int(w * s), int(h * s)
    if sw < 4: return
    x0, y0 = int(x - sw / 2), int(y - sh_ / 2)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + sw), min(H, y0 + sh_)
    if X1 <= X0 or Y1 <= Y0: return
    mm = cv2.resize(m, (sw, sh_))[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, None] * op
    rr = cv2.resize(ring, (sw, sh_))[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, None] * op
    pad = 40
    bx0, by0, bx1, by1 = max(0, X0 - pad), max(0, Y0 - pad), min(W, X1 + pad), min(H, Y1 + pad)
    blur = cv2.GaussianBlur(c[by0:by1, bx0:bx1], (0, 0), 16)[Y0 - by0:Y1 - by0, X0 - bx0:X1 - bx0]
    tint = np.array(rgb('0E3A28'), np.float32) / 255
    glass = blur * 0.55 + tint * 0.38 + 0.07
    # soft shadow under the pill
    shadow_quad(c, np.array([[x0, y0], [x0 + sw, y0], [x0 + sw, y0 + sh_], [x0, y0 + sh_]], np.float64), blur=30, alpha=0.25 * op, off=(0, 14))
    reg = c[Y0:Y1, X0:X1]
    reg[:] = reg * (1 - mm) + glass * mm
    reg[:] = reg * (1 - rr * 0.55) + rr * 0.55
    paste(c, fg, x, y, s, 0, op)

# ------------------------------------------------------------------ draw-on line icons
ICONS = {
    'cabin': [[(.08, .52), (.5, .12), (.92, .52)], [(.2, .42), (.2, .9), (.8, .9), (.8, .42)], [(.42, .9), (.42, .66), (.58, .66), (.58, .9)],
              [(.64, .3), (.64, .16), (.74, .16), (.74, .38)], [(.27, .56), (.36, .56), (.36, .66), (.27, .66), (.27, .56)]],
    'pin': [[(.5, .92), (.24, .55), (.2, .4), (.24, .25), (.36, .13), (.5, .09), (.64, .13), (.76, .25), (.8, .4), (.76, .55), (.5, .92)],
            [(.5, .27), (.6, .31), (.64, .4), (.6, .49), (.5, .53), (.4, .49), (.36, .4), (.4, .31), (.5, .27)]],
    'calendar': [[(.12, .2), (.88, .2), (.88, .9), (.12, .9), (.12, .2)], [(.12, .38), (.88, .38)], [(.32, .1), (.32, .28)], [(.68, .1), (.68, .28)],
                 [(.3, .55), (.4, .55)], [(.55, .55), (.65, .55)], [(.3, .72), (.4, .72)], [(.55, .72), (.65, .72)]],
    'bookmark': [[(.25, .08), (.75, .08), (.75, .92), (.5, .7), (.25, .92), (.25, .08)]],
    'share': [[(.3, .42), (.15, .42), (.15, .92), (.85, .92), (.85, .42), (.7, .42)], [(.5, .66), (.5, .08)], [(.32, .25), (.5, .08), (.68, .25)]],
    'mountain': [[(.04, .86), (.36, .34), (.52, .58), (.66, .42), (.96, .86), (.04, .86)], [(.27, .48), (.36, .56), (.45, .48)],
                 [(.8, .14), (.86, .2), (.8, .26), (.74, .2), (.8, .14)]],
    'search': [[(.42, .1), (.6, .16), (.7, .34), (.66, .52), (.52, .64), (.32, .64), (.18, .52), (.14, .34), (.24, .16), (.42, .1)], [(.6, .6), (.88, .9)]],
    'suitcase': [[(.1, .3), (.9, .3), (.9, .88), (.1, .88), (.1, .3)], [(.36, .3), (.36, .14), (.64, .14), (.64, .3)], [(.1, .52), (.9, .52)]],
}

def icon_frame(name, size, p, tube=True):
    """premultiplied RGBA of icon `name` drawn on up to progress p (0..1), double-line 'tube' style."""
    ss = 2; S_ = size * ss
    lines = ICONS[name]
    segs = []
    for pl in lines:
        for a, b in zip(pl, pl[1:]):
            segs.append((a, b, math.dist(a, b)))
    L = sum(s[2] for s in segs) * p
    lw = max(3, int(S_ * 0.05))
    m = Image.new('L', (S_, S_), 0); d = ImageDraw.Draw(m)
    acc = 0
    drawn = []
    for a, b, l in segs:
        if acc >= L: break
        k = min(1, (L - acc) / l) if l > 0 else 1
        e = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        drawn.append(((a[0] * S_, a[1] * S_), (e[0] * S_, e[1] * S_)))
        acc += l
    for (x0, y0), (x1, y1) in drawn:
        d.line([(x0, y0), (x1, y1)], fill=255, width=lw)
        for (x, y) in ((x0, y0), (x1, y1)):
            d.ellipse([x - lw / 2, y - lw / 2, x + lw / 2, y + lw / 2], fill=255)
    if tube:
        for (x0, y0), (x1, y1) in drawn:
            d.line([(x0, y0), (x1, y1)], fill=0, width=max(1, int(lw * 0.36)))
    mk = np.asarray(m.resize((size, size), Image.LANCZOS)).astype(np.float32) / 255
    out = np.zeros((size, size, 4), np.float32)
    g = np.clip(cv2.GaussianBlur(mk, (0, 0), size * 0.04) * 0.9, 0, 1)
    out[..., :3] = g[..., None] * 0.95; out[..., 3] = g * 0.75
    out[..., :3] = out[..., :3] * (1 - mk[..., None]) + mk[..., None]
    out[..., 3] = out[..., 3] * (1 - mk) + mk
    return out

def line_icon_anim(c, t, t0, t1, name, x, y, size=260):
    if t < t0 or t > t1 + 0.25: return
    p = e_out(prog(t, t0, t0 + 0.55))
    img = icon_frame(name, size, max(0.02, p))
    op = 1.0
    if t > t1:  # glitchy exit: horizontal slices jitter + fade
        q = prog(t, t1, t1 + 0.25); op = 1 - q
        rng = np.random.default_rng(int(t * 30))
        img = img.copy()
        for k in range(0, size, 12):
            img[k:k + 12] = np.roll(img[k:k + 12], int(rng.uniform(-40, 40) * q), axis=1)
    paste(c, img, x, y, 1.0 + 0.04 * prog(t, t0, t1), 0, op)

# ------------------------------------------------------------------ iOS-style banner
@functools.lru_cache(maxsize=4)
def banner_img(title, sub):
    w, h = 900, 150
    ss = 3
    im = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], 75 * ss, fill=(18, 22, 20, 225))
    d.rounded_rectangle([3, 3, w * ss - 4, h * ss - 4], 75 * ss, outline=(255, 255, 255, 40), width=3 * ss)
    im = im.resize((w, h), Image.LANCZOS); d = ImageDraw.Draw(im)
    d.ellipse([22, 22, 128, 128], fill=LIME_B + (255,))
    ic = icon_frame('calendar', 64, 1.0, tube=False)
    ic8 = Image.fromarray(np.clip(ic * 255, 0, 255).astype(np.uint8), 'RGBA')
    # dark glyph on the lime circle
    g = Image.new('RGBA', ic8.size, GREEN + (0,)); g.putalpha(ic8.split()[3])
    im.alpha_composite(g, (75 - 32, 75 - 32))
    d.text((156, 54), title, font=ufont(700, False, 40), fill=(255, 255, 255, 255), anchor='lm')
    d.text((156, 100), sub, font=ufont(400, False, 32), fill=(190, 200, 195, 255), anchor='lm')
    d.text((w - 46, 54), 'ahora', font=ufont(500, False, 28), fill=(160, 170, 165, 255), anchor='rm')
    im, _ = add_shadow(im, blur=22, off=(0, 14), alpha=0.35, pad=40)
    return pil_premul(im)

def banner(c, t, t0, t1, title, sub, y=300):
    if t < t0 or t > t1 + 0.25: return
    p = e_back(prog(t, t0, t0 + 0.38), 1.7)
    yy = y - 260 * (1 - p)
    op = clamp((t - t0) / 0.08)
    if t > t1:
        q = e_in(prog(t, t1, t1 + 0.25)); yy -= 260 * q; op *= 1 - q
    paste(c, banner_img(title, sub), 540, yy, 1.0, 0, op)
