"""Static/semi-static assets: phone mockup, chips, cards, chat UI, captions, tiles, logos."""
import json, math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from lib import *
from typo import tfont
from typo3 import ufont

SITE = f'{ROOT}/site'
STATUS_H = 0

# ---------- raw frames ----------
NFR = 933
@functools.lru_cache(maxsize=20)
def raw(i):
    i = int(min(max(i, 0), NFR - 1))
    from clean import clean_talking
    return clean_talking(i, cv2.cvtColor(cv2.imread(f'{ROOT}/frames/{i:04d}.jpg'), cv2.COLOR_BGR2RGB))
def raw_t(t): return raw(int(round(t * FPS)))

@functools.lru_cache(maxsize=8)
def mask(i):
    m = cv2.imread(f'{ROOT}/masks/{int(i):04d}.png', cv2.IMREAD_GRAYSCALE)
    return cv2.GaussianBlur(m, (0, 0), 1.2).astype(np.float32) / 255.0

SW_ = 1080
BAR = 110                   # synthetic status bar above the recorded page
SH_ = 1920 + BAR
def screen_t(t, clean=True):
    """Screen recording frame (full width) with a synthetic status bar on top."""
    from clean import clean_screen
    f = raw_t(t)
    if clean: f = clean_screen(int(round(t * FPS)), f)
    bar = np.empty((BAR, 1080, 3), np.uint8); bar[:] = f[2:6].reshape(-1, 3).mean(0).astype(np.uint8)
    return np.vstack([bar, f])

# ---------- phone ----------
PB = 30
PW, PH = SW_ + 2 * PB, SH_ + 2 * PB

@functools.lru_cache(maxsize=24)
def phone_tpl(rs):
    Wp, Hp = int(round(PW * rs)), int(round(PH * rs))
    ss = 2
    im = Image.new('RGBA', (Wp * ss, Hp * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, Wp * ss - 1, Hp * ss - 1], int(140 * rs * ss), fill=(74, 78, 84, 255))
    e = int(5 * rs * ss)
    d.rounded_rectangle([e, e, Wp * ss - 1 - e, Hp * ss - 1 - e], int(136 * rs * ss), fill=(10, 10, 12, 255))
    im = im.resize((Wp, Hp), Image.LANCZOS)
    bez = pil_premul(im)
    sx, sy = int(round(PB * rs)), int(round(PB * rs))
    sw, sh = int(round(SW_ * rs)), int(round(SH_ * rs))
    m = np.asarray(rounded_mask(sw, sh, max(2, int(108 * rs)))).astype(np.float32)[..., None] / 255
    isl = Image.new('RGBA', (Wp * ss, Hp * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(isl)
    iw, ih = 270 * rs * ss, 80 * rs * ss; cx = Wp * ss / 2; y0 = (PB + 26) * rs * ss
    d.rounded_rectangle([cx - iw / 2, y0, cx + iw / 2, y0 + ih], int(ih / 2), fill=(0, 0, 0, 255))
    # glass glare
    isl = isl.resize((Wp, Hp), Image.LANCZOS)
    glare = np.zeros((Hp, Wp), np.float32)
    yy, xx = np.mgrid[0:Hp, 0:Wp].astype(np.float32)
    g = (xx / Wp * 0.8 + yy / Hp * 0.35)
    glare = np.clip(1 - np.abs(g - 0.42) / 0.10, 0, 1) * 0.07
    return dict(bez=bez, m=m, sx=sx, sy=sy, sw=sw, sh=sh, isl=pil_premul(isl), glare=glare[..., None])

def build_phone(screen_u8, rs):
    rs = max(0.1, min(1.0, round(rs * 20) / 20))
    T = phone_tpl(rs)
    out = T['bez'].copy()
    scr = cv2.resize(screen_u8, (T['sw'], T['sh']), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    reg = out[T['sy']:T['sy'] + T['sh'], T['sx']:T['sx'] + T['sw']]
    m = T['m']
    reg[..., :3] = reg[..., :3] * (1 - m) + scr * m
    reg[..., 3:] = reg[..., 3:] * (1 - m) + m
    a = T['isl'][..., 3:]
    out = out * (1 - a) + T['isl']
    out[..., :3] += T['glare'] * out[..., 3:]
    return out

def draw_phone(canvas, screen_u8, cx, cy, s, rx=0, ry=0, rz=0, ax=0.5, ay=0.5, shadow=0.38, opacity=1.0):
    q = quad3d(PW, PH, cx, cy, s, rx, ry, rz, ax, ay)
    sc = quad_scale(q, PW, PH)
    if shadow > 0:
        shadow_quad(canvas, q, blur=70 * min(sc, 1.2) + 10, alpha=shadow * opacity, off=(18 * sc, 46 * sc))
    ph = build_phone(screen_u8, min(1.0, sc * 1.15))
    warp(canvas, ph, q, opacity)
    return q

def screen_pt(q, sx, sy):
    """Map a screen pixel (in 1080x1920 screen coords) to canvas coords via phone quad q."""
    src = np.array([[0, 0], [PW, 0], [PW, PH], [0, PH]], np.float32)
    M = cv2.getPerspectiveTransform(src, q.astype(np.float32))
    p = M @ np.array([sx + PB, sy + PB, 1.0])
    return p[0] / p[2], p[1] / p[2]

# ---------- screen overlays ----------
def overlay_box(scr, box, p, color=LIME_B, width=10, radius=34, fill_alpha=0.10):
    if p <= 0: return scr
    x0, y0, x1, y1 = box
    pad = 40
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(scr.shape[1], x1 + pad), min(scr.shape[0], y1 + pad)
    crop = Image.fromarray(scr[Y0:Y1, X0:X1]).convert('RGBA')
    ov = Image.new('RGBA', crop.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    s = 1.08 - 0.08 * e_out(p)
    cx, cy = (x0 + x1) / 2 - X0, (y0 + y1) / 2 - Y0
    hw, hh = (x1 - x0) / 2 * s, (y1 - y0) / 2 * s
    a = int(255 * clamp(p * 2.5))
    d.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], radius, fill=color + (int(255 * fill_alpha * clamp(p * 2.5)),),
                        outline=color + (a,), width=width)
    crop = Image.alpha_composite(crop, ov).convert('RGB')
    scr = scr.copy(); scr[Y0:Y1, X0:X1] = np.asarray(crop)
    return scr

def overlay_tap(scr, x, y, p):
    if p <= 0 or p >= 1: return scr
    scr = scr.copy()
    r = int(30 + 90 * e_out(p)); a = (1 - p)
    ov = scr.copy()
    cv2.circle(ov, (int(x), int(y)), int(44 * (1 - 0.3 * p)), (2, 59, 40), -1, cv2.LINE_AA)
    scr = cv2.addWeighted(ov, 0.35 * a, scr, 1 - 0.35 * a, 0)
    ov = scr.copy()
    cv2.circle(ov, (int(x), int(y)), r, (169, 233, 58), 10, cv2.LINE_AA)
    return cv2.addWeighted(ov, a, scr, 1 - a, 0)

# ---------- chips ----------
@functools.lru_cache(maxsize=64)
def chip(emo, text, style='white', size=44):
    fnt = ufont(700, False, size * 1.08)
    tw, bb = text_size(text, fnt)
    h = int(size * 2.15); ic = int(h * 0.72) if emo else 0
    padl = int(h * 0.16) if emo else int(h * 0.42); padr = int(h * 0.42)
    w = padl + ic + (int(h * 0.2) if emo else 0) + tw + padr
    bg, fg, icbg = {
        'white': (WHITE, GREEN, rgb('E8F6D3')),
        'lime': (LIME_B, GREEN_D, (255, 255, 255)),
        'dark': (GREEN, WHITE, rgb('1F6B4D')),
    }[style]
    ss = 3
    im = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], h * ss // 2, fill=bg + (255,))
    if emo:
        cy = h * ss // 2; cx = (padl + ic // 2) * ss
        d.ellipse([cx - ic * ss // 2, cy - ic * ss // 2, cx + ic * ss // 2, cy + ic * ss // 2], fill=icbg + (255,))
    im = im.resize((w, h), Image.LANCZOS)
    if emo:
        e = emoji_img(emo, int(ic * 0.62))
        im.alpha_composite(e, (padl + ic // 2 - e.width // 2, h // 2 - e.height // 2))
    x = padl + ic + (int(h * 0.2) if emo else 0)
    ImageDraw.Draw(im).text((x, h // 2), text, font=fnt, fill=fg, anchor='lm')
    im, _ = add_shadow(im, blur=16, off=(0, 10), alpha=0.30, pad=36)
    return pil_premul(im)

def chip_anim(canvas, t, t0, c, x, y, t1=None, s=1.0, float_amp=7, rot=0.0):
    if t < t0: return
    p = prog(t, t0, t0 + 0.32)
    sc = s * (0.2 + 0.8 * e_back(p, 2.6)) if p < 1 else s
    op = clamp((t - t0) / 0.08)
    if t1 is not None and t > t1:
        q = prog(t, t1, t1 + 0.2)
        sc *= 1 - e_in(q); op *= 1 - q
        if q >= 1: return
    yy = y + float_amp * math.sin((t - t0) * 2.6)
    paste(canvas, c, x, yy, sc, rot, op)

# ---------- listing cards ----------
@functools.lru_cache(maxsize=24)
def listing_card(img, name, loc, price, unit, kind=None, w=600, ih=440, heart_fill=0.0, badge=None):
    ss = 2
    pad_info = 190 if not badge else 250
    h = ih + pad_info
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    base = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    ImageDraw.Draw(base).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], 40 * ss, fill=(255, 255, 255, 255))
    im = base.resize((w, h), Image.LANCZOS)
    ph = cover(Image.open(f'{SITE}/img/{img}').convert('RGB'), w - 24, ih - 12)
    m = rounded_mask(w - 24, ih - 12, 30)
    im.paste(ph, (12, 12), m)
    d = ImageDraw.Draw(im)
    if kind:
        f = font(600, 26); tw, _ = text_size(kind, f)
        d.rounded_rectangle([30, 30, 30 + tw + 40, 30 + 52], 26, fill=(255, 255, 255, 235))
        d.text((50, 56), kind, font=f, fill=INK + (255,), anchor='lm')
    # heart
    hx, hy, hr = w - 70, 70, 36
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255, 120) if heart_fill < 0.5 else (255, 255, 255, 235))
    heart(d, hx, hy + 2, 30, heart_fill)
    y = ih + 22
    d.text((30, y), name, font=font(700, 40), fill=INK + (255,))
    y += 56
    pin = emoji_img('📍', 28); im.alpha_composite(pin, (30, y + 6))
    d.text((66, y), loc, font=font(500, 30), fill=(71, 86, 107, 255))
    y += 50
    fb = font(800, 40); tw, _ = text_size(price, fb)
    d.text((30, y), price, font=fb, fill=INK + (255,))
    d.text((30 + tw + 12, y + 8), unit, font=font(500, 30), fill=(71, 86, 107, 255))
    if badge:
        y += 66; f = font(600, 26); tw, _ = text_size(badge, f)
        d.rounded_rectangle([30, y, 30 + tw + 40, y + 48], 24, outline=(154, 175, 203, 255), width=2)
        d.text((50, y + 24), badge, font=f, fill=(71, 86, 107, 255), anchor='lm')
    im, _ = add_shadow(im, blur=26, off=(0, 22), alpha=0.33, pad=60)
    return pil_premul(im)

def heart(d, cx, cy, size, fill):
    pts = []
    for k in range(60):
        a = 2 * math.pi * k / 60
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * size / 34, cy + y * size / 34))
    if fill > 0.5:
        d.polygon(pts, fill=(239, 68, 68, 255))
    else:
        d.line(pts + [pts[0]], fill=(255, 255, 255, 255) if fill < 0 else (2, 8, 23, 255), width=4)

# ---------- photo card ----------
@functools.lru_cache(maxsize=12)
def photo_card(img, w=430, h=540, border=14, fx=0.5, fy=0.5):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    base = rounded_mask(w, h, 36)
    white = Image.new('RGBA', (w, h), (255, 255, 255, 255)); im.paste(white, (0, 0), base)
    ph = cover(Image.open(f'{SITE}/img/{img}').convert('RGB'), w - 2 * border, h - 2 * border, fx, fy)
    im.paste(ph, (border, border), rounded_mask(w - 2 * border, h - 2 * border, 26))
    im, _ = add_shadow(im, blur=24, off=(0, 20), alpha=0.35, pad=56)
    return pil_premul(im)

# ---------- grid tiles ----------
@functools.lru_cache(maxsize=40)
def tile(img, name, price, w=420, h=747):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ph = cover(Image.open(f'{SITE}/img/{img}').convert('RGB'), w, h).convert('RGBA')
    # bottom gradient + label
    g = Image.new('L', (1, h)); g.putdata([int(max(0, (y / h - 0.6) / 0.4) ** 1.4 * 210) for y in range(h)])
    shade = Image.new('RGBA', (w, h), (1, 30, 20, 255)); shade.putalpha(g.resize((w, h)))
    ph = Image.alpha_composite(ph, shade)
    d = ImageDraw.Draw(ph)
    d.text((26, h - 104), name, font=font(700, 30), fill=(255, 255, 255, 255))
    d.text((26, h - 62), price, font=font(800, 30), fill=LIME_B + (255,))
    im.paste(ph, (0, 0), rounded_mask(w, h, 36))
    return pil_premul(im)

# ---------- logos ----------
@functools.lru_cache(maxsize=8)
def logo(kind='white', width=300):
    im = Image.open(f'{ROOT}/brand/logo-{kind}.png').convert('RGBA')
    im = im.crop(im.getbbox())
    s = width / im.width
    return pil_premul(im.resize((width, int(im.height * s)), Image.LANCZOS))

# ---------- caption words ----------
@functools.lru_cache(maxsize=512)
def word_img(word, style, size):
    if style == 'big':
        fnt = font(900, size); col = LIME_B
    elif style == 'bigw':
        fnt = font(900, size); col = WHITE
    else:
        fnt = font(700, size); col = WHITE
    bb = fnt.getbbox(word, anchor='ls')
    pad = int(size * 0.5)
    w = bb[2] - bb[0] + 2 * pad; h = int(size * 1.5) + 2 * pad
    base_y = pad + int(size * 1.05)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh = Image.new('L', (w, h), 0)
    ImageDraw.Draw(sh).text((pad - bb[0], base_y), word, font=fnt, fill=255, anchor='ls',
                            stroke_width=max(2, size // 14), stroke_fill=255)
    sh = sh.filter(ImageFilter.GaussianBlur(size * 0.16))
    shadow = Image.new('RGBA', (w, h), (0, 18, 10, 0)); shadow.putalpha(sh.point(lambda v: int(min(255, v * 0.95))))
    im = Image.alpha_composite(im, shadow)
    d = ImageDraw.Draw(im)
    d.text((pad - bb[0], base_y), word, font=fnt, fill=col + (255,), anchor='ls',
           stroke_width=max(1, size // 30), stroke_fill=(1, 42, 28, 200))
    return pil_premul(im), pad, base_y, bb[2] - bb[0]

# ---------- chat screen ----------
CHAT_MSGS = [
    # (time, who, text, emoji, outgoing)
    (2.62, 'Ana', '¿Y quién reserva la cabaña?', '🏡', False),
    (3.20, 'Luis', 'Yo no', '😅', False),
    (3.66, 'Sofi', 'Yo tampoco', '🙈', False),
    (4.20, 'Ana', '@Tú te toca otra vez', '👀', False),
    (4.86, None, 'Siempre yo...', '😩', True),
]
NAME_COL = {'Ana': rgb('0B7A4B'), 'Luis': rgb('B45309'), 'Sofi': rgb('7C3AED')}

@functools.lru_cache(maxsize=2)
def chat_base():
    im = Image.new('RGB', (SW_, 1920), rgb('EFEAE0'))
    d = ImageDraw.Draw(im)
    # subtle dotted pattern
    for y in range(320, 1780, 60):
        for x in range((y // 60) % 2 * 30, SW_, 60):
            d.ellipse([x, y, x + 5, y + 5], fill=rgb('E4DED2'))
    d.rectangle([0, 0, SW_, 310], fill=GREEN)
    d.text((34, 228), '‹', font=font(600, 90), fill=WHITE, anchor='lm')
    d.ellipse([92, 166, 214, 288], fill=LIME_B)
    e = emoji_img('🏔', 72); im.paste(e, (153 - e.width // 2, 227 - e.height // 2), e)
    d.text((236, 200), 'Viaje a Tierras Altas', font=font(700, 46), fill=WHITE, anchor='lm')
    d.text((236, 258), 'Ana, Luis, Sofi, Tú', font=font(500, 33), fill=rgb('BFE3CF'), anchor='lm')
    d.rectangle([0, 1772, SW_, 1920], fill=rgb('F6F3EE'))
    d.rounded_rectangle([26, 1790, 730, 1890], 50, fill=WHITE)
    d.text((76, 1840), 'Mensaje', font=font(500, 36), fill=rgb('9AA3AE'), anchor='lm')
    d.ellipse([752, 1790, 852, 1890], fill=GREEN)
    d.ellipse([789, 1815, 815, 1855], fill=LIME_B)
    return np.asarray(im)

@functools.lru_cache(maxsize=8)
def chat_bubble(who, text, emo, out):
    fnt = font(600, 50); tw, _ = text_size(text, fnt)
    ew = 56
    w = 56 + tw + 14 + ew; h = 148 if who else 116
    w = max(w, 260)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 34, fill=(rgb('DCF5B8') if out else WHITE) + (255,))
    y = 22
    if who:
        d.text((28, y - 6), who, font=font(700, 34), fill=NAME_COL[who] + (255,)); y += 36
    d.text((28, y + 4), text, font=fnt, fill=INK + (255,))
    e = emoji_img(emo, 50); im.alpha_composite(e, (28 + tw + 14, y + 6))
    d.text((w - 22, h - 14), '4:02', font=font(500, 22), fill=(120, 130, 140, 255), anchor='rs')
    im, pad = add_shadow(im, blur=8, off=(0, 4), alpha=0.12, pad=20)
    return np.asarray(im), pad

def chat_screen(t):
    scr = chat_base().copy().astype(np.float32)
    y = 370
    for (t0, who, text, emo, out) in CHAT_MSGS:
        b, pad = chat_bubble(who, text, emo, out)
        bh, bw = b.shape[0] - 2 * pad, b.shape[1] - 2 * pad
        if t >= t0:
            p = prog(t, t0, t0 + 0.28)
            s = 0.3 + 0.7 * e_back(p, 2.2)
            x = (SW_ - 34 - bw) if out else 34
            ax = x + (bw if out else 0); ay = y + bh
            bi = cv2.resize(b, None, fx=s, fy=s, interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
            ox = int(ax - (bw if out else 0) * s - pad * s); oy = int(ay - bh * s - pad * s)
            hh, ww = bi.shape[:2]
            x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(SW_, ox + ww), min(1920, oy + hh)
            if x1 > x0 and y1 > y0:
                src = bi[y0 - oy:y1 - oy, x0 - ox:x1 - ox].astype(np.float32)
                a = src[..., 3:] / 255 * clamp((t - t0) / 0.08)
                scr[y0:y1, x0:x1] = scr[y0:y1, x0:x1] * (1 - a) + src[..., :3] * a
        y += bh + 30
    return scr.astype(np.uint8)
