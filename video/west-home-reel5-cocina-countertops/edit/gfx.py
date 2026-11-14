"""Text, cards and motion graphics. All sprites are premultiplied RGBA float32 (0..1 alpha, 0..255 colour)."""
import math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from core import ease_out_cubic, ease_in_cubic, ease_out_back, ease_out_expo, clamp, ROOT

FONTS = ROOT + 'fonts/brand/'
F = dict(
    thin='Poppins-Thin.ttf', xlight='Poppins-ExtraLight.ttf', light='Poppins-Light.ttf', reg='Poppins-Regular.ttf',
    med='Poppins-Medium.ttf', semi='Poppins-SemiBold.ttf', bold='Poppins-Bold.ttf', xbold='Poppins-ExtraBold.ttf',
    black='Poppins-Black.ttf', cab_black='CabinetGrotesk-Black.otf', cab_xbold='CabinetGrotesk-Extrabold.otf', cab_bold='CabinetGrotesk-Bold.otf', cab_med='CabinetGrotesk-Medium.otf',
)
ORANGE = (255, 77, 0)          # brand orange (RGB)
ORANGE_L = (255, 122, 61)
NAVY = (19, 41, 58)
_font_cache = {}


def font(name, size):
    k = (name, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(FONTS + F[name], size)
    return _font_cache[k]


def _to_premult(rgba):
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    rgb = rgba[..., :3].astype(np.float32) * a
    return np.concatenate([rgb, a], 2)


def emoji_img(ch, height):
    f = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
    im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    s = height / im.height
    return im.resize((max(1, int(im.width * s)), int(height)), Image.LANCZOS)


def text_rgba(text, fname, size, fill=(255, 255, 255), tracking=0.0, grad=None, texture=None, emoji=None,
              emoji_scale=0.95):
    """render one line to a tight RGBA PIL image. tracking in em/1000 units. grad=(top_rgb, bottom_rgb) or
    ('h', left, right). texture: PIL RGB image used as fill."""
    f = font(fname, size)
    asc, desc = f.getmetrics()
    track = size * tracking / 1000.0
    # measure
    total = f.getlength(text) + track * max(0, len(text) - 1)
    pad = int(size * 0.15)
    Wd = int(total + 2 * pad + (size * 1.2 if emoji else 0)); Hd = asc + desc + 2 * pad
    mask = Image.new('L', (Wd, Hd), 0)
    d = ImageDraw.Draw(mask)
    if tracking == 0:
        d.text((pad, pad), text, font=f, fill=255)
    else:
        # keep the font's kerning: each glyph sits at the kerned prefix width plus the extra tracking
        for i, c in enumerate(text):
            d.text((pad + f.getlength(text[:i]) + track * i, pad), c, font=f, fill=255)
    m = np.asarray(mask).astype(np.float32) / 255.0
    ys, xs = np.nonzero(m > 0.01)
    if texture is not None:
        tex = texture.resize((Wd, Hd), Image.LANCZOS) if texture.size != (Wd, Hd) else texture
        rgb = np.asarray(tex.convert('RGB')).astype(np.float32)
    elif grad is not None:
        rgb = np.zeros((Hd, Wd, 3), np.float32)
        if grad[0] == 'h':
            x0, x1 = xs.min(), xs.max()
            u = np.clip((np.arange(Wd) - x0) / max(1, x1 - x0), 0, 1)[None, :, None]
            c0, c1 = np.array(grad[1], np.float32), np.array(grad[2], np.float32)
        else:
            y0, y1 = ys.min(), ys.max()
            u = np.clip((np.arange(Hd) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
            c0, c1 = np.array(grad[0], np.float32), np.array(grad[1], np.float32)
        rgb = rgb + c0 + (c1 - c0) * u
    else:
        rgb = np.zeros((Hd, Wd, 3), np.float32) + np.array(fill, np.float32)
    rgba = np.dstack([np.clip(rgb, 0, 255), m * 255]).astype(np.uint8)
    img = Image.fromarray(rgba, 'RGBA')
    if emoji:
        e = emoji_img(emoji, asc * emoji_scale)
        ex = int(pad + total + size * 0.18)
        img.alpha_composite(e, (ex, int(pad + asc * 0.08)))
    bb = img.getbbox()
    return img.crop((max(0, bb[0] - 2), max(0, bb[1] - 2), min(img.width, bb[2] + 2), min(img.height, bb[3] + 2))), \
        (pad + asc) - max(0, bb[1] - 2)   # baseline offset inside crop


def with_shadow(img, radius=14, offset=(0, 7), opacity=0.55, glow=None):
    """PIL RGBA -> premultiplied float sprite with soft drop shadow (and optional coloured glow)."""
    pad = radius * 3
    W_, H_ = img.width + 2 * pad, img.height + 2 * pad
    a = np.zeros((H_, W_), np.float32)
    a[pad:pad + img.height, pad:pad + img.width] = np.asarray(img)[..., 3] / 255.0
    out = np.zeros((H_, W_, 4), np.float32)
    if opacity > 0:
        sh = cv2.GaussianBlur(a, (0, 0), radius)
        M = np.float32([[1, 0, offset[0]], [0, 1, offset[1]]])
        sh = cv2.warpAffine(sh, M, (W_, H_)) * opacity
        out[..., 3] = sh
    if glow is not None:
        col, gr, gop = glow
        g = cv2.GaussianBlur(a, (0, 0), gr) * gop
        g = np.clip(g, 0, 1)
        out[..., :3] = out[..., :3] * (1 - g[..., None]) + np.array(col, np.float32)[None, None] * g[..., None]
        out[..., 3] = out[..., 3] * (1 - g) + g
    fg = np.zeros((H_, W_, 4), np.uint8)
    fg[pad:pad + img.height, pad:pad + img.width] = np.asarray(img)
    fgp = _to_premult(fg)
    fa = fgp[..., 3:4]
    out = fgp + out * (1 - fa)
    # store RGB as BGR for cv2 frames
    out = out[..., [2, 1, 0, 3]].copy()
    return out


def blit(canvas, spr, cx, cy, scale=1.0, rot=0.0, opacity=1.0, blur=0.0, mask_fn=None):
    """composite premultiplied BGRA float sprite centred at (cx,cy) onto float32 BGR canvas.
    mask_fn(xs, ys) -> optional extra alpha (h,w) in canvas coords for wipes."""
    if opacity <= 0.003 or scale <= 0.01:
        return None
    h, w = spr.shape[:2]
    if blur > 0.6:
        spr = cv2.GaussianBlur(spr, (0, 0), blur)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
    # bounding box in canvas
    corners = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]], np.float32) @ M.T
    bw = corners[:, 0].max() - corners[:, 0].min(); bh = corners[:, 1].max() - corners[:, 1].min()
    x0 = int(math.floor(cx - bw / 2)) - 2; y0 = int(math.floor(cy - bh / 2)) - 2
    x1 = int(math.ceil(cx + bw / 2)) + 2; y1 = int(math.ceil(cy + bh / 2)) + 2
    CH, CW = canvas.shape[:2]
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(CW, x1), min(CH, y1)
    if X1 <= X0 or Y1 <= Y0:
        return None
    M2 = M.copy()
    M2[0, 2] += cx - (M[0] @ np.array([w / 2, h / 2, 1])) - X0
    M2[1, 2] += cy - (M[1] @ np.array([w / 2, h / 2, 1])) - Y0
    roi = cv2.warpAffine(spr, M2, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    a = roi[..., 3:4] * opacity
    if mask_fn is not None:
        a = a * mask_fn(X0, Y0, X1, Y1)[..., None]
        rgb = roi[..., :3] * opacity * mask_fn(X0, Y0, X1, Y1)[..., None]
    else:
        rgb = roi[..., :3] * opacity
    region = canvas[Y0:Y1, X0:X1]
    canvas[Y0:Y1, X0:X1] = region * (1 - a) + rgb
    return (X0, Y0, X1, Y1)


# ------------------------------------------------------------------ animated element
class El:
    """a sprite with entrance/exit animation.
    anim_in: 'blurup' (reference: blur + rise + fade), 'pop', 'cut', 'rise'; anim_out: 'blurout', 'cut', 'drop'."""

    def __init__(self, spr, cx, cy, t_in, t_out, anim_in='blurup', anim_out='blurout', d_in=0.3, d_out=0.2,
                 dy=60, behind=False, rot=0.0, float_amp=0.0, scale=1.0, layer=0):
        self.spr, self.cx, self.cy, self.t_in, self.t_out = spr, cx, cy, t_in, t_out
        self.ai, self.ao, self.di, self.do, self.dy = anim_in, anim_out, d_in, d_out, dy
        self.behind, self.rot, self.float_amp, self.scale, self.layer = behind, rot, float_amp, scale, layer

    def active(self, t):
        return self.t_in - 0.001 <= t < self.t_out + self.do

    def state(self, t):
        op, y, s, b = 1.0, 0.0, 1.0, 0.0
        if t < self.t_in:
            return None
        p = (t - self.t_in) / self.di if self.di > 0 else 1
        if p < 1:
            if self.ai == 'blurup':
                e = ease_out_cubic(p); op = clamp(p * 1.6); y = self.dy * (1 - e); b = 18 * (1 - e); s = 1.05 - 0.05 * e
            elif self.ai == 'pop':
                op = clamp(p * 2.5); s = 0.35 + 0.65 * ease_out_back(p, 2.2); b = 6 * (1 - ease_out_cubic(p))
            elif self.ai == 'rise':
                e = ease_out_cubic(p); op = clamp(p * 2); y = self.dy * 0.4 * (1 - e); b = 5 * (1 - e)
            elif self.ai == 'zoomin':
                e = ease_out_cubic(p); op = clamp(p * 2); s = 1.6 - 0.6 * e; b = 14 * (1 - e)
        if t >= self.t_out:
            q = (t - self.t_out) / self.do if self.do > 0 else 1
            if q >= 1 or self.ao == 'cut':
                return None
            if self.ao == 'blurout':
                e = ease_in_cubic(q); op *= 1 - q; b += 16 * q; y -= 30 * e; s *= 1 + 0.04 * q
            elif self.ao == 'drop':
                e = ease_in_cubic(q); op *= 1 - q; s *= 1 - 0.5 * e
        if self.float_amp:
            y += self.float_amp * math.sin(2 * math.pi * (t - self.t_in) / 2.2)
        return op, y, s * self.scale, b

    def draw(self, canvas, t, base=None, mask=None):
        st = self.state(t)
        if st is None:
            return
        op, y, s, b = st
        box = blit(canvas, self.spr, self.cx, self.cy + y, s, self.rot, op, b)
        if self.behind and box is not None and mask is not None and base is not None:
            X0, Y0, X1, Y1 = box
            m = mask[Y0:Y1, X0:X1, None]
            canvas[Y0:Y1, X0:X1] = canvas[Y0:Y1, X0:X1] * (1 - m) + base[Y0:Y1, X0:X1] * m


def title(text, fname, size, **kw):
    sh = kw.pop('shadow', dict(radius=16, offset=(0, 8), opacity=0.5))
    kw.setdefault('tracking', -40)
    img, _ = text_rgba(text, fname, size, **kw)
    return with_shadow(img, **sh)


# ------------------------------------------------------------------ word-by-word captions
class Caption:
    """one line of words appearing one by one (reference: small light words + bold keywords)."""

    def __init__(self, words, t_end, cy=1330, size=62, gap=0.28, max_w=930):
        # words: list of (text, style, t_on); style in {'l','b','o'} light / bold white / bold orange
        self.t_end, self.cy = t_end, cy
        sprs = []
        for txt, st, ton in words:
            if st == 'l':
                img, base = text_rgba(txt, 'reg', size, tracking=-30)
            elif st == 'm':
                img, base = text_rgba(txt, 'med', size, tracking=-35)
            elif st == 'b':
                img, base = text_rgba(txt, 'bold', int(size * 1.08), tracking=-45)
            else:
                img, base = text_rgba(txt, 'xbold', int(size * 1.08), tracking=-45, grad=(ORANGE_L, ORANGE))
            sprs.append((img, base, ton, st))
        space = size * gap
        tot = sum(i.width for i, _, _, _ in sprs) + space * (len(sprs) - 1)
        sc = min(1.0, max_w / tot)
        self.items = []
        x = 540 - tot * sc / 2
        maxb = max(b for _, b, _, _ in sprs)
        for img, base, ton, st in sprs:
            spr = with_shadow(img, radius=9, offset=(0, 4), opacity=0.85, glow=((0, 0, 0), 16, 0.35))
            w = img.width * sc
            cx = x + w / 2
            # align baselines: sprite centre offset
            cy = cy_line = self.cy + (img.height / 2 - base) * sc
            self.items.append(El(spr, cx, cy, ton, t_end, anim_in='rise', anim_out='cut', d_in=0.12, d_out=0.0,
                                 dy=30, scale=sc))
            x += w + space * sc
        self.t0 = min(i.t_in for i in self.items)

    def active(self, t):
        return self.t0 <= t < self.t_end

    def draw(self, canvas, t, base=None, mask=None):
        if not self.active(t):
            return
        for it in self.items:
            it.draw(canvas, t)


# ------------------------------------------------------------------ glass pill (dynamic-island style)
def rounded_mask(w, h, r):
    m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (r, 0), (w - r, h), 255, -1)
    cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
    for cx, cy in [(r, r), (w - r - 1, r), (r, h - r - 1), (w - r - 1, h - r - 1)]:
        cv2.circle(m, (cx, cy), r, 255, -1, lineType=cv2.LINE_AA)
    return cv2.GaussianBlur(m, (3, 3), 0).astype(np.float32) / 255.0


def glass(canvas, x0, y0, w, h, r, tint=0.16, blur=24, border=0.45, shadow=True, dark=0.0):
    CH, CW = canvas.shape[:2]
    w, h = int(w), int(h); x0, y0 = int(x0), int(y0)
    if w < 4 or h < 4:
        return
    r = min(r, h // 2, w // 2)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(CW, x0 + w), min(CH, y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    m = rounded_mask(w, h, r)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    if shadow:
        pad = 40
        sx0, sy0, sx1, sy1 = max(0, X0 - pad), max(0, Y0 - pad + 14), min(CW, X1 + pad), min(CH, Y1 + pad + 14)
        sm = np.zeros((sy1 - sy0, sx1 - sx0), np.float32)
        yy0, xx0 = Y0 + 14 - sy0, X0 - sx0
        hh, ww = min(m.shape[0], sm.shape[0] - yy0), min(m.shape[1], sm.shape[1] - xx0)
        sm[yy0:yy0 + hh, xx0:xx0 + ww] = m[:hh, :ww]
        sm = cv2.GaussianBlur(sm, (0, 0), 18) * 0.35
        canvas[sy0:sy1, sx0:sx1] *= (1 - sm[..., None])
    region = canvas[Y0:Y1, X0:X1]
    bl = cv2.GaussianBlur(region, (0, 0), blur)
    g = bl * (1 - tint - dark) + 255 * tint
    # top highlight gradient
    hh = Y1 - Y0
    hl = np.linspace(0.10, 0.0, hh, dtype=np.float32)[:, None, None]
    g = g + 255 * hl
    canvas[Y0:Y1, X0:X1] = region * (1 - m[..., None]) + g * m[..., None]
    # border
    if border > 0:
        bm = np.zeros((h, w), np.uint8)
        cv2.rectangle(bm, (0, 0), (w - 1, h - 1), 0, -1)
        full = (rounded_mask(w, h, r) * 255).astype(np.uint8)
        er = cv2.erode(full, np.ones((5, 5), np.uint8))
        ring = (full.astype(np.float32) - er.astype(np.float32)) / 255.0
        ring = ring[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * border
        canvas[Y0:Y1, X0:X1] = canvas[Y0:Y1, X0:X1] * (1 - ring[..., None]) + 255 * ring[..., None]


def load_logo(path, width):
    im = Image.open(path).convert('RGBA')
    im = im.crop(im.getbbox())
    s = width / im.width
    im = im.resize((int(width), int(im.height * s)), Image.LANCZOS)
    return im


def pil_to_spr(im, shadow=True, **kw):
    if shadow:
        return with_shadow(im, **kw)
    a = np.asarray(im).astype(np.uint8)
    p = _to_premult(a)
    return p[..., [2, 1, 0, 3]].copy()
