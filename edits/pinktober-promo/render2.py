"""Pinktober 15s promo: beat-synced cuts (190 BPM), neon kinetic type, pink grade, Tranqui end card."""
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

S = sys.argv[1]; OUT = sys.argv[2]
PREVIEW = 'preview' in sys.argv[3:]
R = f'{S}/raw/Pinktober'
FD = f'{S}/../fonts'
W, H, FPS = 1080, 1920, 30
TOTAL = 15.0
NF = int(TOTAL * FPS)
BEAT = 60 / 190

PINK = (255, 84, 176)
PINK_GLOW = (255, 20, 140)
NEON_CORE = (255, 214, 236)
WHITE = (255, 255, 255)

def font(name, size):
    return ImageFont.truetype(f'{FD}/{name}-latin-{"400" if name in ("allura", "archivo-black") else name.split(":")[1] if ":" in name else "400"}-normal.woff', size)

def F(kind, size):
    path = {'thin': 'josefin-sans-latin-300', 'reg': 'josefin-sans-latin-400', 'semi': 'josefin-sans-latin-600',
            'bold': 'josefin-sans-latin-700', 'heavy': 'archivo-black-latin-400', 'script': 'allura-latin-400'}[kind]
    return ImageFont.truetype(f'{FD}/{path}-normal.woff', size)

# ---------------- shots: (clip, src_in, beat_start, beat_end, transition_in, focus_y) ----------------
C = {1: '1eadec44-afd0-4d1e-bf9e-2019d2ed1c07.mp4', 2: '334d12d1-429c-441a-b563-08d24307aa87.mp4',
     3: '3aa3bebc-bb92-48f2-b963-a8091720cbfa.mp4', 4: '6e8f11c7-7848-4c23-adb9-fe8d6d40b9eb.mp4',
     5: '8fa9b502-0a99-463f-ab64-52ace2b73e4f.mp4', 6: '915b9ae4-e0db-4c3e-8fc5-4ce3187e299d.mp4',
     7: 'IMG_2091.MOV', 8: 'IMG_2157.MOV', 9: 'IMG_2161.MOV'}
SHOTS = [
    (4, 7.0, 0, 4, 'flash'),      # DANCE for a cause
    (8, 10.0, 4, 6, 'punch'),     # salsa
    (5, 5.2, 6, 8, 'whip'),       # bachata
    (6, 12.0, 8, 11, 'glitch'),   # latin dance
    (7, 4.0, 11, 14, 'punch'),    # social party
    (1, 12.5, 14, 17, 'whip'),    # join us for the
    (2, 52.3, 17, 22, 'punch'),   # 8th annual Pinktober
    (4, 12.0, 22, 24, 'flash'),   # Saturday
    (3, 20.0, 24, 27, 'glitch'),  # October 24th
    (2, 26.0, 27, 30, 'whip'),    # raising funds for the
    (4, 27.0, 30, 32, 'punch'),   # Pink Program
    (1, 28.5, 32, 35, 'whip'),    # bringing dance
    (9, 20.0, 35, 37, 'punch'),   # wellness
    (3, 93.0, 37, 40, 'glitch'),  # to breast cancer survivors
    (6, 15.0, 40, 43, 'whip'),    # and thrivers
]
END_T = 43 * BEAT

# ---------------- kinetic text ----------------
# VO sits at t = src - 0.48; word starts come from the transcription
def v(src): return src - 0.48
VIOLET = (140, 90, 255)

# Each element: dict(kind, size, text, color, y, t, end, anim, tracking=0, words=[(word, t)], lines=...)
def E(t, end, kind, size, text, color, y, anim, tracking=0, words=None):
    return dict(t=t, end=end, kind=kind, size=size, text=text, color=color, y=y, anim=anim, tracking=tracking, words=words)

TEXT = [
    E(v(0.84), v(2.02), 'thin', 160, 'DANCE', WHITE, 0.43, 'track', 24),
    E(v(1.18), v(2.02), 'script', 210, 'for a cause', PINK, 0.52, 'write'),
    E(v(2.36), v(3.26), 'heavy', 150, 'SALSA &', WHITE, 0.44, 'slam'),
    E(v(2.90), v(3.26), 'heavy', 165, 'BACHATA', PINK, 0.525, 'slam'),
    E(v(3.26), v(4.82), 'thin', 96, '', WHITE, 0.40, 'words', 18, [('LATIN', v(3.26)), ('DANCE', v(3.60))]),
    E(v(3.94), v(4.82), 'heavy', 175, 'SOCIAL', WHITE, 0.48, 'slam'),
    E(v(4.40), v(4.82), 'heavy', 175, 'PARTY', PINK, 0.565, 'slam'),
    E(v(5.24), v(6.06), 'bold', 150, '', WHITE, 0.45, 'words', 0, [('join', v(5.24)), ('us', v(5.46))]),
    E(v(5.74), v(6.06), 'semi', 110, '', WHITE, 0.525, 'words', 0, [('for', v(5.74)), ('the', v(5.96))]),
    E(v(6.10), v(7.50), 'bold', 100, '', WHITE, 0.385, 'words', 16, [('8TH', v(6.10)), ('ANNUAL', v(6.54))]),
    E(v(6.86), v(7.50), 'script', 300, 'Pinktober', PINK, 0.49, 'write'),
    E(v(7.62), v(8.94), 'badge', 0, 'SATURDAY|OCTOBER|24|TH', WHITE, 0.47, 'badge'),
    E(v(8.94), v(10.66), 'bold', 112, '', WHITE, 0.395, 'words', 0, [('raising', v(8.94)), ('funds', v(9.38))]),
    E(v(9.74), v(10.66), 'semi', 96, '', WHITE, 0.455, 'words', 0, [('for', v(9.74)), ('the', v(9.98))]),
    E(v(10.10), v(10.66), 'heavy', 175, 'PINK', PINK, 0.535, 'slam'),
    E(v(10.26), v(10.66), 'heavy', 140, 'PROGRAM', PINK, 0.61, 'slam'),
    E(v(10.66), v(12.02), 'bold', 112, '', WHITE, 0.41, 'words', 0, [('bringing', v(10.66))]),
    E(v(11.26), v(12.02), 'heavy', 165, 'DANCE', WHITE, 0.49, 'slam'),
    E(v(11.72), v(12.02), 'script', 230, 'wellness', PINK, 0.575, 'write'),
    E(v(12.02), END_T, 'bold', 100, '', WHITE, 0.385, 'words', 0, [('to', v(12.02)), ('breast', v(12.24)), ('cancer', v(12.48))]),
    E(v(12.74), END_T, 'heavy', 140, 'SURVIVORS', WHITE, 0.46, 'slam'),
    E(v(13.20), END_T, 'heavy', 140, '& THRIVERS', PINK, 0.535, 'slam'),
]
END_TEXT = [
    E(END_T + 0.05, TOTAL, 'script', 230, 'Pinktober', PINK, 0.235, 'write'),
    E(END_T + 0.30, TOTAL, 'bold', 54, 'SATURDAY · OCTOBER 24TH', WHITE, 0.315, 'ghost', 10),
    E(END_T + 0.45, TOTAL, 'semi', 76, 'Harnessing Wellness', WHITE, 0.665, 'ghost'),
    E(END_T + 0.55, TOTAL, 'semi', 76, 'Through Dance', WHITE, 0.715, 'ghost'),
]

# ---------------- text rendering ----------------
GPAD = 60
def text_img(kind, size, text, color, tracking):
    """RGBA element with neon glow (glow strength by style)."""
    f = F(kind, size)
    if tracking:
        widths = [f.getlength(ch) for ch in text]
        tw = int(sum(widths) + tracking * (len(text) - 1)) + 8
    else:
        tw = int(f.getlength(text)) + 8
    asc, desc = f.getmetrics()
    th = asc + desc + (int(size * 0.35) if kind == 'script' else 6)
    pad_x = int(size * 0.25) if kind == 'script' else 0
    core = Image.new('RGBA', (tw + 2 * pad_x, th), (0, 0, 0, 0)); d = ImageDraw.Draw(core)
    if tracking:
        x = pad_x
        for ch, wch in zip(text, widths):
            d.text((x, 0), ch, font=f, fill=color + (255,)); x += wch + tracking
    else:
        d.text((pad_x, int(size * 0.12) if kind == 'script' else 0), text, font=f, fill=color + (255,))
    if kind == 'script':  # neon tube: thicker stroke, near-white core, pink halo
        a = core.getchannel('A').filter(ImageFilter.MaxFilter(5))
        core = Image.new('RGBA', core.size, (NEON_CORE if color == PINK else WHITE) + (0,)); core.putalpha(a)
        return glowify(core, PINK_GLOW, 1.5)
    strength = 1.2 if color == PINK else 0.55
    return glowify(core, PINK_GLOW if color == PINK else (255, 200, 235), strength)

def glowify(core, gcol, strength):
    pad = GPAD
    W2, H2 = core.width + 2 * pad, core.height + 2 * pad
    out = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    a = Image.new('L', (W2, H2), 0); a.paste(core.getchannel('A'), (pad, pad))
    for r, k in [(28, 0.55), (12, 0.75), (4, 0.6)]:
        g = a.filter(ImageFilter.GaussianBlur(r)).point(lambda p, k=k: min(255, int(p * k * strength * 1.6)))
        lay = Image.new('RGBA', (W2, H2), gcol + (0,)); lay.putalpha(g)
        out.alpha_composite(lay)
    # dark halo so the type separates from bright shirts and pink outfits
    light = gcol != PINK_GLOW
    sh = a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(16 if light else 12)).point(
        lambda p: min(255, int(p * (1.25 if light else 0.75))))
    shadow = Image.new('RGBA', (W2, H2), (18, 0, 14, 0)); shadow.putalpha(sh)
    base = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); base.alpha_composite(shadow)
    if not light: base.alpha_composite(out)
    base.alpha_composite(core, (pad, pad))
    return base

_cache = {}
def cached(key, fn):
    if key not in _cache: _cache[key] = fn()
    return _cache[key]

def element(e, text=None, tracking=None):
    text = e['text'] if text is None else text
    tracking = e['tracking'] if tracking is None else tracking
    return cached(('el', e['kind'], e['size'], text, e['color'], tracking),
                  lambda: text_img(e['kind'], e['size'], text, e['color'], tracking))

def tinted(img, col, key):
    def mk():
        t = Image.new('RGBA', img.size, col + (0,)); t.putalpha(img.getchannel('A')); return t
    return cached(('tint', key, col), mk)

def with_alpha(img, alpha):
    if alpha >= 0.999: return img
    img = img.copy(); img.putalpha(img.getchannel('A').point(lambda p: int(p * max(0, alpha)))); return img

def scaled(img, sc):
    if abs(sc - 1) < 1e-3: return img
    return img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BILINEAR)

def ease_out(x): return 1 - (1 - x) ** 3
def ease_back(x, s=1.9): return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def clamp01(x): return max(0.0, min(1.0, x))

def beat_pulse(T):
    """Tiny scale kick on every beat for type that has already landed."""
    return 1 + 0.022 * max(0, 1 - ((T % BEAT) / BEAT) * 4)

def place(frame, img, cx, cy):
    frame.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))

# --- slam: huge, translucent and colour-split, settles to size (reference: TROPICAL NIGHTS)
def fx_slam(frame, e, T, cx, cy):
    base = element(e); u = T - e['t']; D = 0.28
    x = clamp01(u / D); k = ease_out(x)
    sc = 1.0 + 0.9 * (1 - k)
    if u > D: sc = 1 - 0.045 * math.sin(math.pi * clamp01((u - D) / 0.14))   # little settle bounce
    if x >= 1: sc *= beat_pulse(T)
    if x < 1:
        key = (e['text'], e['size'])
        ghost_a = 0.55 * (1 - k); off = 46 * (1 - k)
        for col, dx in [((255, 40, 160), -off), (VIOLET, off)]:
            g = with_alpha(scaled(tinted(base, col, key), sc * (1 + 0.06 * (1 - k))), ghost_a)
            place(frame, g, cx + dx, cy)
        main = with_alpha(scaled(base, sc), 0.35 + 0.65 * k)
        tint_col = PINK if e['color'] == WHITE else VIOLET
        if k < 0.85:  # starts colour-washed, clears to its own colour
            mix = Image.blend(tinted(base, tint_col, key), base, k / 0.85)
            main = with_alpha(scaled(mix, sc), 0.35 + 0.65 * k)
        place(frame, main, cx, cy)
    else:
        place(frame, scaled(base, sc), cx, cy)

# --- write-on: neon script drawn left to right (reference: "lovers")
def fx_write(frame, e, T, cx, cy, tip=False):
    base = element(e); u = T - e['t']; D = 0.42 if e['size'] >= 280 else 0.34
    x = clamp01(u / D); k = ease_out(x) if x < 1 else 1
    img = base
    if k < 1:
        a = np.asarray(base.getchannel('A'), np.float32)
        wpx = base.width; feather = 90
        front = -feather + k * (wpx + feather)
        ramp = np.clip((front - np.arange(wpx)) / feather, 0, 1)[None, :]
        img = base.copy(); img.putalpha(Image.fromarray((a * ramp).astype(np.uint8)))
    else:
        img = scaled(base, beat_pulse(T))
    # brief neon flicker right after it lands
    if 0.0 < u - D < 0.12 and int((u - D) * 30) % 2 == 1: img = with_alpha(img, 0.55)
    place(frame, img, cx, cy)
    if tip and 0 < k < 1:  # glint riding the writing front
        fx = cx - base.width / 2 + GPAD + k * (base.width - 2 * GPAD)
        st = scaled(star(), 0.75 + 0.35 * math.sin(u * 40) ** 2)
        place(frame, st, fx, cy - e['size'] * 0.08)

def star():
    def mk():
        n = 160; c = n / 2
        core = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(core)
        for ang, L, w in [(0, 70, 7), (90, 70, 7), (45, 30, 4), (135, 30, 4)]:
            dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            px, py = -dy * w / 2, dx * w / 2
            d.polygon([(c - dx * L, c - dy * L), (c + px, c + py), (c + dx * L, c + dy * L), (c - px, c - py)], fill=(255, 255, 255, 255))
        glow = Image.new('RGBA', (n, n), PINK_GLOW + (0,)); glow.putalpha(core.getchannel('A').filter(ImageFilter.GaussianBlur(9)).point(lambda p: min(255, p * 2)))
        out = Image.new('RGBA', (n, n), (0, 0, 0, 0)); out.alpha_composite(glow); out.alpha_composite(core)
        return out
    return cached(('star',), mk)

# --- tracking: letters gather from wide spacing with a soft blur
def fx_track(frame, e, T, cx, cy):
    u = T - e['t']; D = 0.4; x = clamp01(u / D); k = ease_out(x)
    tr = int(round(e['tracking'] + 70 * (1 - k)))
    img = element(e, tracking=tr)
    if x < 1:
        img = with_alpha(img, k)
        if k < 0.8: img = img.filter(ImageFilter.GaussianBlur(int(10 * (1 - k))))
    else:
        img = scaled(img, beat_pulse(T))
    place(frame, img, cx, cy)

# --- words: each word drops in on its own syllable (reference: "presale tickets are live now!")
def fx_words(frame, e, T, cx, cy):
    f = F(e['kind'], e['size']); space = f.getlength(' ') + e['tracking'] * 2
    imgs = [element(e, text=w) for w, _ in e['words']]
    core_w = [im.width - 2 * GPAD for im in imgs]
    total = sum(core_w) + space * (len(imgs) - 1)
    x0 = cx - total / 2
    for (w, tw), im, cw in zip(e['words'], imgs, core_w):
        u = T - tw
        if u >= 0:
            x = clamp01(u / 0.2)
            dy = -70 * (1 - ease_back(x, 2.2)); sc = 1.35 - 0.35 * ease_out(x)
            img = with_alpha(scaled(im, sc if x < 1 else beat_pulse(T)), min(1, x * 3))
            place(frame, img, x0 + cw / 2, cy + dy)
        x0 += cw + space

# --- date badge: glitchy calendar sticker that pops and tilts (reference: SEPTEMBER 26TH)
def badge_parts():
    def mk():
        CW, CH = 620, 460
        card = Image.new('RGBA', (CW + 120, CH + 200), (0, 0, 0, 0))
        ox, oy = 60, 110
        # shadow
        sh = Image.new('L', card.size, 0); ImageDraw.Draw(sh).rounded_rectangle((ox + 6, oy + 26, ox + CW + 6, oy + CH + 26), 52, fill=170)
        sh = sh.filter(ImageFilter.GaussianBlur(18)); shl = Image.new('RGBA', card.size, (40, 0, 25, 0)); shl.putalpha(sh)
        card.alpha_composite(shl)
        # gradient body
        grad = np.zeros((CH, CW, 4), np.uint8)
        top, bot = np.array([255, 110, 195]), np.array([200, 22, 128])
        for yy in range(CH):
            grad[yy, :, :3] = top + (bot - top) * (yy / CH); grad[yy, :, 3] = 255
        body = Image.fromarray(grad, 'RGBA')
        m = Image.new('L', (CW, CH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, CW - 1, CH - 1), 52, fill=255)
        body.putalpha(m); card.alpha_composite(body, (ox, oy))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((ox, oy, ox + CW, oy + CH), 52, outline=(255, 255, 255, 255), width=9)
        # glossy highlight
        gl = Image.new('L', card.size, 0); ImageDraw.Draw(gl).rounded_rectangle((ox + 24, oy + 18, ox + CW - 24, oy + CH * 0.42), 40, fill=55)
        gll = Image.new('RGBA', card.size, (255, 255, 255, 0)); gll.putalpha(gl.filter(ImageFilter.GaussianBlur(6)))
        card.alpha_composite(gll)
        # OCTOBER with extrude
        fo = F('heavy', 104); txt = 'OCTOBER'; tw = fo.getlength(txt); tx = ox + CW / 2 - tw / 2; ty = oy + 50
        for s in range(8, 0, -1): d.text((tx + s * 0.6, ty + s), txt, font=fo, fill=(120, 0, 70, 255))
        d.text((tx, ty), txt, font=fo, fill=(255, 255, 255, 255))
        # SATURDAY pill (rotated), sits across the card's top edge
        fp = F('heavy', 62); pt = 'SATURDAY'; pw = int(fp.getlength(pt)) + 70; ph = 104
        pill = Image.new('RGBA', (pw + 40, ph + 40), (0, 0, 0, 0)); dp = ImageDraw.Draw(pill)
        dp.rounded_rectangle((20, 20, 20 + pw, 20 + ph), ph // 2, fill=(255, 255, 255, 255))
        dp.text((20 + 35, 20 + 14), pt, font=fp, fill=(214, 18, 128, 255))
        pill = pill.rotate(6, resample=Image.BICUBIC, expand=True)
        card.alpha_composite(pill, (int(ox + CW / 2 - pill.width / 2 + 40), oy - pill.height // 2 - 8))
        # big number layer (separate so it can land on "24th")
        fn = F('heavy', 250); ft = F('heavy', 92)
        num = Image.new('RGBA', (CW, 300), (0, 0, 0, 0)); dn = ImageDraw.Draw(num)
        nw = fn.getlength('24'); tw2 = ft.getlength('TH'); nx = CW / 2 - (nw + tw2 + 8) / 2
        for s in range(14, 0, -1):
            dn.text((nx + s * 0.6, 0 + s), '24', font=fn, fill=(110, 0, 64, 255))
            dn.text((nx + nw + 8 + s * 0.4, 34 + s * 0.7), 'TH', font=ft, fill=(110, 0, 64, 255))
        dn.text((nx, 0), '24', font=fn, fill=(255, 255, 255, 255))
        dn.text((nx + nw + 8, 34), 'TH', font=ft, fill=(255, 255, 255, 255))
        return card, num, (ox, oy + 170)
    return cached(('badge',), mk)

def fx_badge(frame, e, T, cx, cy):
    card, num, (nx, ny) = badge_parts(); u = T - e['t']
    t_num = v(8.18) - e['t']
    comp = card.copy()
    if u >= t_num:
        un = u - t_num; x = clamp01(un / 0.22)
        sc = 1.7 - 0.7 * ease_back(x, 1.6) if x < 1 else 1
        n = with_alpha(scaled(num, sc), min(1, x * 3))
        comp.alpha_composite(n, (int(nx + num.width / 2 - n.width / 2), int(ny + num.height / 2 - n.height / 2)))
    if u < 0.12:   # glitch shards before the pop
        k = u / 0.12; img = Image.new('RGBA', comp.size, (0, 0, 0, 0)); rs = np.random.default_rng(int(T * 1000))
        hh = comp.height // 7
        for i in range(7):
            sl = comp.crop((0, i * hh, comp.width, (i + 1) * hh))
            dx = int(rs.uniform(-120, 120) * (1 - k))
            col = [(255, 40, 160), VIOLET, (255, 255, 255)][i % 3]
            img.alpha_composite(with_alpha(tinted(sl, col, ('shard', i)) if i % 2 else sl, 0.5 + 0.5 * k), (dx, i * hh))
        comp = scaled(img, 0.7 + 0.2 * k); ang = -18
    else:
        x = clamp01((u - 0.12) / 0.28)
        sc = 0.9 + 0.1 * ease_back(x, 2.2) if x < 1 else beat_pulse(T)
        ang = (-18 + 14 * ease_back(x, 1.6)) if x < 1 else (-4 + 1.4 * math.sin(2 * math.pi * 0.9 * (u - 0.4)))
        comp = scaled(comp, sc * 0.92)
    comp = comp.rotate(ang, resample=Image.BICUBIC, expand=True)
    bob = 6 * math.sin(2 * math.pi * 1.1 * u)
    place(frame, comp, cx, cy + bob)

# --- ghost: soft blur-in (end card lines)
def fx_ghost(frame, e, T, cx, cy):
    img = element(e); u = T - e['t']; x = clamp01(u / 0.2)
    sc = 1.2 - 0.2 * ease_out(x)
    img = with_alpha(scaled(img, sc), ease_out(x))
    if x < 0.8: img = img.filter(ImageFilter.GaussianBlur(int(12 * (1 - x))))
    place(frame, img, cx, cy)

def draw_element(frame, e, T):
    if not (e['t'] <= T < e['end']): return
    cx, cy = W / 2, H * e['y']
    a = e['anim']
    if a == 'slam': fx_slam(frame, e, T, cx, cy)
    elif a == 'write': fx_write(frame, e, T, cx, cy, tip=e['text'] == 'Pinktober')
    elif a == 'track': fx_track(frame, e, T, cx, cy)
    elif a == 'words': fx_words(frame, e, T, cx, cy)
    elif a == 'badge': fx_badge(frame, e, T, cx, cy)
    else: fx_ghost(frame, e, T, cx, cy)

# ---------------- footage ----------------
VIGNETTE = None
def vignette():
    """Edge vignette plus a soft dark band where the type sits, so pink words read over pink outfits."""
    global VIGNETTE
    if VIGNETTE is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        vg = np.clip(1.05 - 0.42 * r ** 2.2, 0.45, 1.0)
        band = 1 - 0.38 * np.exp(-((yy / H - 0.49) / 0.13) ** 2)
        VIGNETTE = (vg * band * 0.92)[..., None].astype(np.float32)
    return VIGNETTE

GRADE = ('eq=contrast=1.10:saturation=1.38:gamma=0.96,'
         'colorbalance=rs=0.05:gs=-0.04:bs=0.04:rm=0.06:gm=-0.05:bm=0.03:rh=0.03:gh=-0.02:bh=0.02')

def shot_frames(clip, src_in, n):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{src_in:.3f}', '-i', f'{R}/{C[clip]}', '-t', f'{n / FPS + 0.3:.3f}',
           '-vf', f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},{GRADE}',
           '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE); last = None
    for _ in range(n):
        buf = p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3: last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        yield last
    p.stdout.close(); p.wait()

def zoom(img, z, cx=0.5, cy=0.5):
    if abs(z - 1) < 1e-3: return img
    cw, ch = W / z, H / z
    x0 = min(max(cx * W - cw / 2, 0), W - cw); y0 = min(max(cy * H - ch / 2, 0), H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))

def footage_frame(arr, lt, sdur, tr, T):
    img = Image.fromarray(arr)
    z = 1.03 + 0.07 * (lt / sdur)            # steady push-in
    # on-beat pulse: tiny zoom kick on every beat
    bp = (T % BEAT) / BEAT; z += 0.018 * max(0, 1 - bp * 4)
    if tr in ('punch', 'flash', 'glitch') and lt < 0.16:
        z += 0.16 * (1 - ease_out(lt / 0.16))
    if tr == 'whip' and lt < 0.14:
        z += 0.25 * (1 - ease_out(lt / 0.14))
    img = zoom(img, z)
    if tr == 'whip' and lt < 0.12:
        k = int(28 * (1 - lt / 0.12)); a = np.asarray(img).astype(np.float32)
        acc = sum(np.roll(a, s, axis=0) for s in range(-k, k + 1, max(1, k // 6))) / len(range(-k, k + 1, max(1, k // 6)))
        img = Image.fromarray(acc.astype(np.uint8))
    a = np.asarray(img).astype(np.float32) * vignette()
    if tr == 'glitch' and lt < 0.12:          # RGB split
        s = int(26 * (1 - lt / 0.12)); a[..., 0] = np.roll(a[..., 0], s, axis=1); a[..., 2] = np.roll(a[..., 2], -s, axis=1)
    if tr == 'flash' and lt < 0.1:
        a = a + (255 - a) * (0.85 * (1 - lt / 0.1))
    # bar downbeat light pump
    bar = (T % (4 * BEAT)) / (4 * BEAT); a *= 1 + 0.07 * max(0, 1 - bar * 8)
    return np.clip(a, 0, 255).astype(np.uint8)

# ---------------- end card ----------------
LOGO = Image.open(f'{S}/work/tranqui_logo.png').convert('RGBA')
def end_card(T, bgsrc):
    u = T - END_T
    yy, xx = np.mgrid[0:H:4, 0:W:4].astype(np.float32)
    bg = np.zeros((H // 4, W // 4, 3), np.float32)
    for (cx, cy, r, col, sp) in [(0.25, 0.25, 0.55, (255, 40, 150), 0.6), (0.8, 0.75, 0.6, (170, 20, 120), -0.5), (0.6, 0.45, 0.35, (255, 120, 200), 0.9)]:
        cx2 = cx + 0.08 * math.sin(u * sp * 2); cy2 = cy + 0.06 * math.cos(u * sp * 2)
        d = np.sqrt(((xx / W - cx2) / r) ** 2 + ((yy / H - cy2) / r) ** 2)
        bg += np.array(col, np.float32) * np.clip(1 - d, 0, 1)[..., None] ** 2 * 0.75
    bg = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    foot = Image.fromarray(bgsrc).filter(ImageFilter.GaussianBlur(18))
    img = Image.blend(Image.fromarray((np.asarray(foot) * 0.32).astype(np.uint8)), bg, 0.6).convert('RGBA')
    if u < 0.1:
        a = np.asarray(img.convert('RGB')).astype(np.float32); a += (255 - a) * 0.9 * (1 - u / 0.1)
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
    # logo pop + glow ring
    x = min(1, u / 0.22); sc = 0.4 + 0.6 * ease_back(x, 1.6); size = int(400 * sc)
    lg = LOGO.resize((size, size), Image.LANCZOS)
    glow = Image.new('RGBA', (size + 160, size + 160), (0, 0, 0, 0))
    m = Image.new('L', glow.size, 0); ImageDraw.Draw(m).ellipse((80, 80, 80 + size, 80 + size), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(30)).point(lambda p: int(p * 0.8 * min(1, x * 2)))
    gl = Image.new('RGBA', glow.size, (255, 60, 170, 0)); gl.putalpha(m)
    cy = int(H * 0.49)
    img.alpha_composite(gl, (W // 2 - glow.width // 2, cy - glow.height // 2))
    lg.putalpha(lg.getchannel('A').point(lambda p: int(p * min(1, x * 3))))
    img.alpha_composite(lg, (W // 2 - size // 2, cy - size // 2))
    # sparkle glint on the ring (like the reference)
    st = u - 0.75
    if 0 <= st < 0.45:
        k = math.sin(math.pi * st / 0.45); d = ImageDraw.Draw(img)
        gx, gy = W // 2 + int(0.33 * 400), cy - int(0.36 * 400); r = int(70 * k)
        for ang, rr in [(0, r), (90, r), (45, r * 0.4), (135, r * 0.4)]:
            dx, dy = rr * math.cos(math.radians(ang)), rr * math.sin(math.radians(ang))
            d.line((gx - dx, gy - dy, gx + dx, gy + dy), fill=(255, 255, 255, int(255 * k)), width=4)
        d.ellipse((gx - 9, gy - 9, gx + 9, gy + 9), fill=(255, 255, 255, int(255 * k)))
    for e in END_TEXT: draw_element(img, e, T)
    return img

def main():
    enc = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', OUT]
    pe = subprocess.Popen(enc, stdin=subprocess.PIPE)
    fidx = 0; last_arr = None
    for si, (clip, src_in, b0, b1, tr) in enumerate(SHOTS):
        f0, f1 = int(round(b0 * BEAT * FPS)), int(round(b1 * BEAT * FPS))
        sdur = (f1 - f0) / FPS
        for k, arr in enumerate(shot_frames(clip, src_in, f1 - f0)):
            T = fidx / FPS
            frame = Image.fromarray(footage_frame(arr, k / FPS, sdur, tr, T)).convert('RGBA')
            for e in TEXT: draw_element(frame, e, T)
            pe.stdin.write(frame.convert('RGB').tobytes()); fidx += 1; last_arr = arr
            if PREVIEW and k == (f1 - f0) // 2: frame.convert('RGB').save(f'{S}/work/p_{si:02d}.jpg', quality=85)
    # end card over blurred pink-dress footage
    n_end = NF - fidx
    for k, arr in enumerate(shot_frames(4, 22.0, n_end)):
        T = fidx / FPS
        frame = end_card(T, arr)
        pe.stdin.write(frame.convert('RGB').tobytes()); fidx += 1
        if PREVIEW and k in (12, n_end - 2): frame.convert('RGB').save(f'{S}/work/p_end{k}.jpg', quality=85)
    pe.stdin.close(); pe.wait()
    json.dump({'end_t': END_T, 'beat': BEAT, 'cuts': [s[2] * BEAT for s in SHOTS], 'trans': [s[4] for s in SHOTS],
               'pinktober': v(6.86), 'frames': fidx}, open(f'{S}/work/timeline.json', 'w'))
    print('frames', fidx)

main()
