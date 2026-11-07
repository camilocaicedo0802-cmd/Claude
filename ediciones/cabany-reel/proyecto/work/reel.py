"""Cabany reel: timeline + per-frame renderer."""
import sys, os, json, math
import numpy as np, cv2
from PIL import Image
from lib import *
from assets import *

DUR = 44.0
LIMEf = tuple(v / 255 for v in LIME_B)
WHITEf = (1.0, 1.0, 1.0)

def axs(sx): return (sx + PB) / PW
def ays(sy): return (sy + PB) / PH

# ---------------------------------------------------------------- captions
WORDS = []
for seg in json.load(open(f'{ROOT}/work/raw_words.json')):
    for w in seg['words']:
        WORDS.append([w['w'].strip().strip(',.').strip(), w['s'], w['e']])
WORDS[29][0] = 'ahorrar'
# phrases: list of lines (style, n_words, override_text)
PHRASES = [
    [('s', 4), ('b', 3)], [('s', 2), ('b', 2)], [('s', 5), ('b', 2)], [('s', 1), ('b', 1)],
    [('s', 2), ('b', 2)], [('s', 5), ('b', 1)], [('b', 3), ('s', 2)], [('s', 5)],
    [('s', 1), ('b', 2)], [('s', 2), ('b', 2, ['cabanypanama.com'])], [('s', 5), ('b', 4)],
    [('s', 1), ('b', 1)], [('s', 6), ('b', 3)], [('s', 7)], [('b', 3)], [('s', 4), ('b', 2)],
    [('s', 5), ('b', 2)], [('s', 1), ('b', 1)], [('s', 4), ('b', 4)], [('s', 4), ('b', 4)],
    [('s', 3), ('b', 1)], [('s', 2), ('b', 2)], [('s', 3), ('b', 2)], [('s', 3), ('b', 1)],
    [('s', 2), ('b', 2)], [('s', 1), ('b', 1)],
]
CAPS = []
_i = 0
for ph in PHRASES:
    lines = []
    for ln in ph:
        st, n = ln[0], ln[1]
        ws = WORDS[_i:_i + n]
        if len(ln) > 2:
            items = [(txt, ws[0][1]) for txt in ln[2]]
        else:
            items = [(w[0], w[1]) for w in ws]
        lines.append((st, items))
        _i += n
    start = lines[0][1][0][1]
    last_end = WORDS[_i - 1][2]
    CAPS.append(dict(lines=lines, start=start - 0.04, last_end=last_end))
assert _i == len(WORDS), (_i, len(WORDS))
for k, c in enumerate(CAPS):
    nxt = CAPS[k + 1]['start'] if k + 1 < len(CAPS) else 42.15
    c['end'] = min(nxt, c['last_end'] + 0.45) if nxt - c['last_end'] > 0.6 else nxt
CAPS[-1]['end'] = 42.12

def cap_y(t):
    if t < 2.48: return 1190
    if t < 5.34: return 1450
    if t < 7.63: return 1190
    if t < 10.1: return 455
    if t < 12.6: return 1190
    if t < 38.57: return 1450
    return 1370

def draw_captions(c, t):
    cap = next((x for x in CAPS if x['start'] <= t < x['end']), None)
    if not cap: return
    y = cap_y(t)
    rows = []
    for st, items in cap['lines']:
        size = 104 if st == 'b' else 54
        style = 'big' if st == 'b' else 'small'
        while True:
            imgs = [word_img(w, style, size) for w, _ in items]
            gap = size * 0.27
            tw = sum(i[3] for i in imgs) + gap * (len(imgs) - 1)
            if tw <= 960 or size < 40: break
            size = int(size * 0.92)
        rows.append((size, imgs, items, tw, gap))
    th = sum(r[0] * 1.16 for r in rows)
    yy = y - th / 2
    for size, imgs, items, tw, gap in rows:
        base = yy + size * 0.95
        x = 540 - tw / 2
        for (im, pad, by, ww), (w, tw0) in zip(imgs, items):
            if t >= tw0 - 0.02:
                p = prog(t, tw0 - 0.02, tw0 + 0.14)
                s = 0.55 + 0.45 * e_back(p, 2.4)
                op = clamp(p * 2.2)
                ih, iw = im.shape[:2]
                cx = x - pad + iw / 2; cy = base - by + ih / 2
                # scale around word center
                paste(c, im, x + ww / 2 + (cx - (x + ww / 2)), cy + (1 - s) * size * 0.25, s, 0, op)
            x += ww + gap
        yy += size * 1.16

# ---------------------------------------------------------------- watermark
def watermark(c):
    reg = c[120:230, 800:1060]
    lum = float((reg * np.array([0.3, 0.59, 0.11], np.float32)).sum(-1).mean())
    k = clamp((lum - 0.45) / 0.25)
    lw, lg = logo('white', 170), logo('green', 170)
    if k < 1: paste(c, lw, 935, 160, 1.0, 0, 0.62 * (1 - k))
    if k > 0: paste(c, lg, 935, 160, 1.0, 0, 0.62 * k)
    tx = url_text('dark' if k > 0.5 else 'light')
    paste(c, tx, 935, 222, 1.0, 0, 0.55)

@functools.lru_cache(maxsize=2)
def url_text(mode):
    from PIL import ImageDraw
    f = font(600, 24)
    im = Image.new('RGBA', (300, 40), (0, 0, 0, 0))
    col = (255, 255, 255, 255) if mode == 'light' else GREEN + (255,)
    ImageDraw.Draw(im).text((150, 20), 'cabanypanama.com', font=f, fill=col, anchor='mm')
    return pil_premul(im)

# ---------------------------------------------------------------- common
def grade(img):
    img = (img - 0.5) * 1.06 + 0.5
    g = img.mean(-1, keepdims=True)
    img = g + (img - g) * 1.08
    return np.clip(img, 0, 1)

def aroll(t, src_t, zoom, anchor):
    f = raw_t(src_t).astype(np.float32) / 255
    f = shift_img(f, 0, 0, zoom, anchor[0], anchor[1])
    return grade(f)

BLOBS_TOUR = [(140, 520, 340, LIMEf, 0.34, 0.0), (960, 1080, 300, LIMEf, 0.26, 2.0),
              (860, 300, 240, WHITEf, 0.55, 4.0), (180, 1560, 300, LIMEf, 0.20, 1.0)]
BLOBS_DARK = [(170, 420, 330, LIMEf, 0.20, 0.5), (940, 1250, 330, LIMEf, 0.16, 2.5), (900, 380, 220, LIMEf, 0.10, 4.2)]

def bg_tour(t):
    c = grad_bg('tour').copy(); blobs(c, t, BLOBS_TOUR); return c
def bg_dark(t):
    c = grad_bg('dark').copy(); blobs(c, t, BLOBS_DARK); return c

def push_motion(img, t, windows):
    for a, b, dx, dy in windows:
        if a <= t <= b:
            k = math.sin(math.pi * prog(t, a, b))
            return motion_blur(img, dx * k, dy * k)
    return img

# ---------------------------------------------------------------- scenes
def brand_tag(c, t):
    if not (0.2 <= t <= 2.45): return
    tag = brand_tag_img()
    p = e_out5(prog(t, 0.2, 0.55)); q = prog(t, 2.25, 2.45)
    x = 540 - (1 - p) * 700 - e_in(q) * 900
    paste(c, tag, x, 1405, 1.0, 0, 1.0)

@functools.lru_cache(maxsize=1)
def brand_tag_img():
    from PIL import ImageDraw
    lg = Image.open(f'{ROOT}/brand/logo-white.png').convert('RGBA'); lg = lg.crop(lg.getbbox())
    lw = 210; lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    f = font(600, 32); txt = 'Tierras Altas · Panamá'
    tw, _ = text_size(txt, f)
    w = 36 + lw + 30 + 2 + 30 + tw + 40; h = 104
    im = Image.new('RGBA', (w * 3, h * 3), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * 3 - 1, h * 3 - 1], 52 * 3, fill=GREEN + (240,))
    im = im.resize((w, h), Image.LANCZOS); d = ImageDraw.Draw(im)
    im.alpha_composite(lg, (36, h // 2 - lg.height // 2))
    x = 36 + lw + 30
    d.rectangle([x, 28, x + 2, h - 28], fill=LIME_B + (255,))
    d.text((x + 32, h // 2), txt, font=f, fill=(255, 255, 255, 255), anchor='lm')
    im, _ = add_shadow(im, blur=18, off=(0, 10), alpha=0.35, pad=40)
    return pil_premul(im)

def sc1(t):
    z = 1.10 - 0.05 * e_out(prog(t, 0, 1.04)) if t < 1.04 else 1.30 - 0.03 * prog(t, 1.04, 2.48)
    c = aroll(t, t, z, (640, 980))
    brand_tag(c, t)
    return c

def sc2(t):
    c = bg_tour(t)
    cam = kf(t, [(2.40, (540, 880, 0.57, 10, 18, -3), lin), (5.40, (540, 880, 0.70, 4, -8, 1), e_io)])
    draw_phone(c, chat_screen(t), *cam)
    return c

CH_RES = chip('📅', 'Reservar', 'white', 46)
CH_BUS = chip('🔎', 'Buscar dónde quedarse', 'white', 46)
def sc3(t):
    z = 1.17 if t < 6.46 else 1.36 - 0.03 * prog(t, 6.46, 7.63)
    c = aroll(t, t, z, (640, 980))
    chip_anim(c, t, 5.40, CH_RES, 290, 700, t1=7.45)
    chip_anim(c, t, 6.02, CH_BUS, 600, 520, t1=7.50)
    return c

CH_HORAS = chip('⏳', 'Horas y horas de búsqueda', 'lime', 46)
def sc4(t):
    c = bg_dark(t)
    i = int(round(t * FPS))
    f = raw(i).astype(np.float32) / 255
    m = mask(i)[..., None]
    z = 1.13 + 0.07 * (1 - e_out(prog(t, 7.63, 7.9)))
    M = np.array([[z, 0, 540 * (1 - z)], [0, z, 1920 * (1 - z) + 30]], np.float32)
    fw = cv2.warpAffine(f * m, M, (W, H), flags=cv2.INTER_LINEAR)
    mw = cv2.warpAffine(m[..., 0], M, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    # soft drop shadow
    sh = cv2.GaussianBlur(cv2.warpAffine(mw[..., 0], np.float32([[1, 0, 26], [0, 1, 14]]), (W, H)), (0, 0), 22)[..., None] * 0.45
    c *= (1 - sh)
    c *= (1 - mw); c += grade(fw / np.maximum(mw, 1e-4)) * mw
    # 3D flip label
    if t >= 8.62:
        p = prog(t, 8.62, 9.0)
        rx = 90 * (1 - e_back(p, 1.6))
        h, w = CH_HORAS.shape[:2]
        q = quad3d(w, h, 540, 1300, 1.0, rx, 0, -3)
        warp(c, CH_HORAS, q, clamp(p * 4))
        if t >= 9.62:
            s = e_io(prog(t, 9.62, 9.9))
            x0, x1 = 540 - (w - 72) / 2 + 30, 540 + (w - 72) / 2 - 30
            xe = x0 + (x1 - x0) * s
            ov = (np.ascontiguousarray(c * 255)).astype(np.uint8)
            cv2.line(ov, (int(x0), 1300 + 18), (int(xe), 1300 - 18), (2, 59, 40), 9, cv2.LINE_AA)
            c[:] = ov.astype(np.float32) / 255
    return c

TILES = [('caba_a_mariposa.webp', 'Cabaña Mariposa', '$120 / noche'), ('villa_diana.webp', 'Villa Diana', 'desde $30'),
         ('harmony_gates.webp', 'Harmony Gates', '$25 / persona'), ('casa_vacacional_bocas_del_toro.webp', 'Bocas del Toro', '$350 / noche'),
         ('caba_a_gemela.webp', 'Cabaña Gemela', '$110 / noche'), ('caba_a_los_quetzales.webp', 'Los Quetzales', '$25 / persona'),
         ('casa_volcan.webp', 'Casa Volcán', '$90 / noche'), ('villa_de_luis.webp', 'Villa de Luis', '$75 / noche'),
         ('la_planta_alta_paso_ancho_black_mountain.webp', 'La Planta Alta', '$150 / noche'), ('baru_1.webp', 'Barú 1', '$40 / noche'),
         ('caba_a_rancho_me_a.webp', 'Rancho Meña', '$150 / noche'), ('boquete_alto_estate.webp', 'Boquete Alto', '$130 / noche'),
         ('caba_a_alpina.webp', 'Cabaña Alpina', '$150 / noche'), ('villa_pau.webp', 'Villa Pau', '$120 / noche'),
         ('casa_boquete.webp', 'Casa Boquete', '$120 / noche'), ('caba_as_vista_hermosa.webp', 'Vista Hermosa', '$85 / noche'),
         ('finca_ngel_blanco.webp', 'Finca Ángel Blanco', '$150 / noche'), ('caba_a_perla.webp', 'Cabaña Perla', '$95 / noche'),
         ('casa_caballero.webp', 'Casa Caballero', '$130 / noche'), ('bambito_hosting.webp', 'Bambito', '$150 / noche'),
         ('caba_a_paradise.webp', 'Cabaña Paradise', '$150 / noche'), ('hotel_la_serrania.webp', 'La Serranía', '$129 / noche'),
         ('caba_a_colibri.webp', 'Cabaña Colibrí', '$25 / persona'), ('casa_billar.webp', 'Casa Billar', '$30 / persona')]

def sc5(t):
    inner = sc4(t)
    z = kf(t, [(10.10, 1.0, lin), (10.85, 0.37, e_io5), (12.6, 0.33, lin)])
    rz = kf(t, [(10.10, 0.0, lin), (10.85, -4.0, e_io), (12.6, -2.0, lin)])
    c = bg_dark(t)
    g = 80
    R = rotm(0, 0, rz)[:2, :2]
    k = 0
    for col in range(-2, 3):
        drift = (t - 10.1) * 140 * (1 if col % 2 else -1) if col else 0
        for row in range(-2, 3):
            X = col * (1080 + g); Y = row * (1920 + g) + drift
            if col == 0 and row == 0: continue
            img, nm, pr = TILES[k % len(TILES)]; k += 1
            px, py = R @ np.array([X * z, Y * z])
            tl = tile(img, nm, pr)
            paste(c, tl, 540 + px, 960 + py, z * 1080 / tl.shape[1], rz)
    # center tile = live scene
    rr = int(max(10, 90 * z / 0.37 * 0.37))
    m = np.asarray(rounded_mask(W, H, 110)).astype(np.float32)[..., None] / 255
    layer = np.concatenate([inner * m, m], -1)
    paste(c, layer, 540, 960, z, rz)
    return c

# --- phone tour ---------------------------------------------------------
def cam_phone(c, scr, cam, shadow=0.38):
    cx, cy, s, rx, ry, rz, ax, ay = cam
    return draw_phone(c, scr, cx, cy, s, rx, ry, rz, ax, ay, shadow=shadow)

FULL = lambda s=0.6, rx=8, ry=0, rz=0, cy=900: (540, cy, s, rx, ry, rz, 0.5, 0.5)
RES_BOX = (14, 734, 870, 970)
CH_URL = chip('🌐', 'cabanypanama.com', 'dark', 48)

def sc6(t):
    c = bg_tour(t)
    ax, ay = axs(442), ays(850)
    cam = kf(t, [(12.55, (540, 1750, 0.52, 60, -24, 10, .5, .5), lin),
                 (12.98, (540, 900, 0.62, 10, -12, -2, .5, .5), e_out5),
                 (13.30, (540, 900, 0.63, 7, -8, -1, .5, .5), lin),
                 (13.68, (540, 820, 1.12, 3, -3, 0, ax, ay), e_io5),
                 (14.40, (540, 820, 1.20, 2, 1, 0, ax, ay), lin)])
    scr = screen_t(min(max(t, 12.62), 13.60))
    scr = overlay_box(scr, RES_BOX, prog(t, 13.50, 13.80))
    scr = overlay_tap(scr, 322, 905, prog(t, 14.02, 14.45))
    cam_phone(c, scr, cam)
    chip_anim(c, t, 13.34, CH_URL, 540, 330, t1=14.30)
    return c

CATS = [('🏡', 'Cabañas', 190, 540), ('🏠', 'Casas', 900, 650), ('⭐', 'Premium', 180, 860),
        ('🏊', 'Piscinas', 895, 1010), ('📶', 'Buen Wifi', 200, 1180), ('🌿', 'Naturaleza', 870, 1330)]
def sc7(t):
    c = bg_tour(t)
    ax, ay = axs(442), ays(850)
    cam = kf(t, [(14.40, (540, 820, 1.20, 2, 1, 0, ax, ay), lin),
                 (14.72, (540, 900, 0.60, 8, 20, 2, .5, .5), e_out5),
                 (16.50, (540, 900, 0.63, 8, -12, -1, .5, .5), e_io)])
    st = 15.05 + (t - 14.40) * (16.5 - 15.05) / (16.5 - 14.40)
    cam_phone(c, screen_t(st), cam)
    for k, (e, txt, x, y) in enumerate(CATS):
        chip_anim(c, t, 15.10 + 0.17 * k, chip(e, txt, 'white', 42), x, y, t1=16.30 + 0.03 * k)
    return c

FILTERS = [('✅', 'Cabañas', 290, 270), ('✅', 'Piscina', 790, 270), ('✅', 'Buen Wifi', 540, 385)]
CARDS = [(('caba_a_mariposa.webp', 'Cabaña Mariposa', 'Volcán', '$120', '/ noche', 'Cabaña'), 17.68, 250, 650, -6),
         (('villa_diana.webp', 'Villa Diana', 'Boquete', 'desde $30', '/ noche', 'Hotel'), 18.02, 835, 800, 5),
         (('harmony_gates.webp', 'Harmony Gates', 'Volcán', '$25', '/ persona', 'Glamping'), 18.36, 245, 1110, 4),
         (('caba_a_gemela.webp', 'Cabaña Gemela', 'Boquete', '$110', '/ noche', 'Cabaña'), 18.70, 835, 1230, -5)]
def sc8(t):
    c = bg_tour(t)
    cam = kf(t, [(16.50, (540, 900, 0.63, 8, -12, -1, .5, .5), lin),
                 (19.60, (540, 900, 0.67, 6, 16, 1, .5, .5), e_io)])
    q = cam_phone(c, screen_t(t), cam)
    for k, (e, txt, x, y) in enumerate(FILTERS):
        chip_anim(c, t, 16.74 + 0.15 * k, chip(e, txt, 'lime', 42), x, y, t1=17.62 + 0.04 * k)
    for args, t0, x, y, rot in CARDS:
        if t < t0: continue
        card = listing_card(*args)
        p = e_out5(prog(t, t0, t0 + 0.45))
        sc = 0.12 + (0.56 - 0.12) * e_back(prog(t, t0, t0 + 0.45), 1.6)
        xx = 540 + (x - 540) * p; yy = 900 + (y - 900) * p + 6 * math.sin((t - t0) * 2.4)
        op = clamp((t - t0) / 0.1)
        if t > 19.35:
            qq = e_in(prog(t, 19.35, 19.62)); xx += (x - 540) * 1.4 * qq; yy += (y - 900) * 0.6 * qq; op *= 1 - qq
        h, w = card.shape[:2]
        warp(c, card, quad3d(w, h, xx, yy, sc, 0, 30 * (1 - p) * (1 if x < 540 else -1), rot), op)
    return c

LCS_BOX = (446, 720, 862, 1274)
LCS_CARD = ('luxury_canyon_suites.webp', 'Luxury Canyon Suites', 'Alto Boquete', 'desde $150', '/ noche', None)
def sc9(t):
    c = bg_tour(t)
    ax, ay = axs(654), ays(997)
    if t < 20.86:
        cam = kf(t, [(19.60, (540, 900, 0.67, 6, 16, 1, .5, .5), lin),
                     (20.86, (540, 900, 0.80, 3, -4, 0, .5, .5), e_io)])
        scr = screen_t(t)
    else:
        cam = kf(t, [(20.86, (540, 880, 1.70, 0, 0, 0, ax, ay), lin), (22.64, (540, 880, 1.86, 0, -2, 0, ax, ay), lin)])
        scr = screen_t(21.60)
        scr = overlay_box(scr, LCS_BOX, prog(t, 20.98, 21.25), radius=44)
        scr = overlay_tap(scr, 654, 870, prog(t, 21.40, 21.85))
    q = cam_phone(c, scr, cam)
    if t >= 21.88:
        p = prog(t, 21.88, 22.40)
        k = e_io5(p)
        dim = 0.35 * k
        c[:] = gblur(c, 14 * k) * (1 - dim) + np.array(GREEN, np.float32) / 255 * dim
        card = lcs_card(0)
        h, w = card.shape[:2]
        x0, y0 = screen_pt(q, 654, 997)
        sw = np.linalg.norm(np.array(screen_pt(q, 862, 997)) - np.array(screen_pt(q, 446, 997)))
        s0 = sw / (w - 120); s1 = 1.12
        xx = x0 + (540 - x0) * k; yy = y0 + (860 - y0) * k
        s = s0 + (s1 - s0) * k
        ry = -14 * math.sin(math.pi * p) - 6 * k
        warp(c, card, quad3d(w, h, xx, yy, s, 6 * k, ry, 0), clamp(p * 6))
    return c

@functools.lru_cache(maxsize=2)
def lcs_card(hf):
    return listing_card(*LCS_CARD, w=640, ih=600, heart_fill=hf, badge='Hotel · 7 tipos')

CH_FAV = chip('❤️', 'Tu favorita', 'white', 46)
def sc10(t):
    c = bg_tour(t)
    c[:] = c * 0.65 + np.array(GREEN, np.float32) / 255 * 0.35
    hf = 1.0 if t >= 24.40 else 0.0
    card = lcs_card(hf)
    h, w = card.shape[:2]
    rx = kf(t, [(22.40, 6, lin), (25.2, -4, e_io)])
    ry = kf(t, [(22.40, -6, lin), (25.2, 12, e_io)])
    s = kf(t, [(22.40, 1.12, lin), (24.38, 1.17, e_io), (24.48, 1.21, e_out), (24.70, 1.17, e_io), (25.2, 1.2, lin)])
    q = quad3d(w, h, 540, 860, s, rx, ry, 0)
    warp(c, card, q)
    # heart burst
    if 24.40 <= t <= 25.0:
        src = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
        M = cv2.getPerspectiveTransform(src, q.astype(np.float32))
        hp = M @ np.array([60 + 640 - 70, 60 + 70, 1.0]); hx, hy = hp[0] / hp[2], hp[1] / hp[2]
        p = prog(t, 24.40, 24.95)
        ov = (c * 255).astype(np.uint8)
        for k in range(12):
            a = k / 12 * 2 * math.pi + 0.3
            r = 40 + 150 * e_out(p)
            col = [(239, 68, 68), (169, 233, 58), (255, 255, 255)][k % 3]
            cv2.circle(ov, (int(hx + r * math.cos(a)), int(hy + r * math.sin(a))), int(14 * (1 - p)) + 1, col, -1, cv2.LINE_AA)
        cv2.circle(ov, (int(hx), int(hy)), int(30 + 120 * e_out(p)), (239, 68, 68), max(1, int(8 * (1 - p))), cv2.LINE_AA)
        c[:] = ov.astype(np.float32) / 255
    chip_anim(c, t, 24.42, CH_FAV, 720, 330, t1=25.05)
    return c

PHOTOS = [('lcs_2.webp', 230, 560, -10), ('lcs_3.webp', 850, 610, 9), ('lcs_4.webp', 215, 1140, 7), ('lcs_5.webp', 860, 1190, -8)]
CH_AMEN = chip('✨', 'Amenidades', 'lime', 46)
def sc11(t):
    c = bg_tour(t)
    cam = kf(t, [(25.14, (540, 860, 1.9, 0, 0, 0, .5, .42), lin),
                 (25.50, (540, 900, 0.62, 8, 14, 1, .5, .5), e_out5),
                 (26.42, (540, 900, 0.63, 6, 6, 0, .5, .5), lin),
                 (26.62, (540, 900, 0.64, 6, -16, -1, .5, .5), e_io),
                 (28.10, (540, 900, 0.66, 6, -6, -1, .5, .5), e_io)])
    if t < 26.5:
        st = 25.55 + (t - 25.14) * (27.70 - 25.55) / (26.5 - 25.14)
    else:
        st = 28.0 + (t - 26.5) * (29.4 - 28.0) / (28.04 - 26.5)
    cam_phone(c, screen_t(st), cam)
    for k, (img, x, y, rot) in enumerate(PHOTOS):
        t0 = 26.70 + 0.12 * k
        if t < t0: continue
        pc = photo_card(img)
        p = prog(t, t0, t0 + 0.42)
        k5 = e_out5(p)
        sc = 0.12 + (0.6 - 0.12) * e_back(p, 1.7)
        xx = 540 + (x - 540) * k5; yy = 900 + (y - 900) * k5 + 6 * math.sin((t - t0) * 2.5)
        op = clamp((t - t0) / 0.1)
        if t > 27.80:
            qq = e_in(prog(t, 27.80, 28.06)); xx += (x - 540) * 1.5 * qq; yy -= 300 * qq; op *= 1 - qq
        h, w = pc.shape[:2]
        warp(c, pc, quad3d(w, h, xx, yy, sc, 0, 25 * (1 - k5) * (1 if x < 540 else -1), rot * k5), op)
    chip_anim(c, t, 27.40, CH_AMEN, 540, 300, t1=28.0)
    return c

AMEN = [('WiFi', 800, 560), ('Cocina', 800, 700), ('TV por cable', 770, 840),
        ('Aire acondicionado', 690, 980), ('Estacionamiento', 735, 1120), ('Piscina', 805, 1260)]
def sc12(t):
    c = bg_tour(t)
    st = 29.45 + (t - 28.04) * (31.45 - 29.45) / (30.94 - 28.04)
    ax, ay = axs(200), ays(1000)
    cam = kf(t, [(28.04, (330, 980, 0.95, 4, 14, 0, ax, ay), lin), (30.94, (350, 960, 1.06, 2, 4, 0, ax, ay), e_io)])
    cam_phone(c, screen_t(st), cam)
    for k, (txt, x, y) in enumerate(AMEN):
        chip_anim(c, t, 28.38 + 0.30 * k, chip('✅', txt, 'lime', 42), x, y, t1=30.80)
    return c

CH_IN = chip('📅', 'Llegada · 10 dic', 'white', 44)
CH_OUT = chip('📅', 'Salida · 13 dic', 'white', 44)
def sc13(t):
    c = bg_tour(t)
    if t < 33.0:
        st = 31.60 + (t - 30.94) * (32.90 - 31.60) / (33.0 - 30.94)
    else:
        st = 33.30 + (t - 33.0) * 0.5
    ax, ay = axs(442), ays(1180)
    cam = kf(t, [(30.94, (540, 880, 0.84, 8, -12, 0, ax, ay), lin), (32.95, (540, 880, 0.98, 4, 6, 0, ax, ay), e_io),
                 (33.15, (540, 900, 0.80, 6, 10, 0, axs(442), ays(900)), e_io5), (33.6, (540, 900, 0.82, 6, 12, 0, axs(442), ays(900)), lin)])
    cam_phone(c, screen_t(st), cam)
    chip_anim(c, t, 32.26, CH_IN, 300, 330, t1=33.55)
    chip_anim(c, t, 33.10, CH_OUT, 780, 440, t1=33.58)
    return c

CH_PEOPLE = chip('👥', '2 huéspedes', 'white', 46)
def sc14(t):
    c = bg_tour(t)
    st = 34.0 + (t - 33.6)
    ax, ay = axs(462), ays(1250)
    cam = kf(t, [(33.6, (540, 860, 0.95, 6, 8, 0, ax, ay), lin), (35.5, (540, 860, 1.12, 3, -4, 0, ax, ay), e_io)])
    scr = screen_t(st)
    scr = overlay_tap(scr, 702, 1208, prog(t, 34.86, 35.30))
    cam_phone(c, scr, cam)
    chip_anim(c, t, 34.68, CH_PEOPLE, 540, 340, t1=35.45)
    return c

TOTAL_BOX = (52, 902, 580, 994)
BTN_BOX = (66, 676, 818, 796)
def sc15_16(t):
    c = bg_tour(t)
    scr = screen_t(36.45)
    cam = kf(t, [(35.50, (540, 880, 0.90, 8, 14, 0, axs(316), ays(948)), lin),
                 (35.80, (520, 820, 1.32, 6, 10, 0, axs(316), ays(948)), e_out5),
                 (36.70, (520, 820, 1.40, 4, 4, 0, axs(316), ays(948)), lin),
                 (37.05, (540, 860, 1.08, 6, -10, 0, axs(442), ays(736)), e_io5),
                 (38.6, (540, 860, 1.16, 4, -4, 0, axs(442), ays(736)), lin)])
    scr = overlay_box(scr, TOTAL_BOX, prog(t, 35.95, 36.25), radius=24)
    scr = overlay_box(scr, BTN_BOX, prog(t, 37.05, 37.30), radius=60, fill_alpha=0.0)
    scr = overlay_tap(scr, 442, 736, prog(t, 37.30, 37.75))
    cam_phone(c, scr, cam)
    if 36.10 <= t <= 36.95:
        v = 85.60 * e_out(prog(t, 36.14, 36.55))
        ch = chip('💳', f'Total: ${v:,.2f} USD', 'dark', 52)
        chip_anim(c, t, 36.12, ch, 540, 1210, t1=36.80)
    if t >= 37.86:
        success(c, t)
    return c

def success(c, t):
    p = prog(t, 37.86, 38.10)
    c[:] = c * (1 - 0.72 * p) + np.array(GREEN_D, np.float32) / 255 * 0.72 * p
    ov = Image.fromarray((c * 255).astype(np.uint8)).convert('RGBA')
    from PIL import ImageDraw
    d = ImageDraw.Draw(ov)
    cx, cy = 540, 840
    rng = np.random.default_rng(7)
    g = prog(t, 38.1, 38.9)
    if g > 0:
        for k in range(46):
            a = rng.uniform(0, 2 * math.pi); v = rng.uniform(380, 900)
            tt = (t - 38.1)
            x = cx + math.cos(a) * v * tt; y = cy + math.sin(a) * v * tt + 900 * tt * tt
            col = [LIME_B, (255, 255, 255), rgb('F8D24A'), LIME][k % 4]
            s = rng.uniform(8, 16)
            d.rectangle([x - s, y - s * 0.6, x + s, y + s * 0.6], fill=col + (int(255 * (1 - g)),))
    q = prog(t, 37.95, 38.35)
    r = 170 * e_back(q, 2.2)
    if r > 1:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=LIME_B + (255,))
        k = e_out(prog(t, 38.10, 38.34))
        if k > 0:
            P = [(cx - 78, cy + 2), (cx - 22, cy + 60), (cx + 84, cy - 62)]
            L1 = math.dist(P[0], P[1]); L2 = math.dist(P[1], P[2]); L = (L1 + L2) * k
            path = [P[0]]
            if L <= L1:
                path.append((P[0][0] + (P[1][0] - P[0][0]) * L / L1, P[0][1] + (P[1][1] - P[0][1]) * L / L1))
            else:
                e = (L - L1) / L2
                path += [P[1], (P[1][0] + (P[2][0] - P[1][0]) * e, P[1][1] + (P[2][1] - P[1][1]) * e)]
            d.line(path, fill=GREEN + (255,), width=38, joint='curve')
            for pp in (path[0], path[-1]): d.ellipse([pp[0] - 19, pp[1] - 19, pp[0] + 19, pp[1] + 19], fill=GREEN + (255,))
    c[:] = np.asarray(ov.convert('RGB')).astype(np.float32) / 255
    tx = success_text()
    pt = prog(t, 38.12, 38.40)
    paste(c, tx, 540, 1110 + 30 * (1 - e_out(pt)), 1.0, 0, pt)

@functools.lru_cache(maxsize=1)
def success_text():
    from PIL import ImageDraw
    im = Image.new('RGBA', (900, 140), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((450, 70), '¡Reserva lista!', font=font(900, 86), fill=(255, 255, 255, 255), anchor='mm')
    im, _ = add_shadow(im, blur=12, off=(0, 6), alpha=0.4, pad=30)
    return pil_premul(im)

def sc17(t):
    if t < 39.38: z = 1.07 + 0.08 * (1 - e_out(prog(t, 38.57, 38.85)))
    elif t < 40.20: z = 1.24
    elif t < 40.94: z = 1.08
    else: z = 1.27 + 0.03 * prog(t, 40.94, 42.4)
    return aroll(t, min(t, 42.4), z, (540, 1050))

@functools.lru_cache(maxsize=1)
def tagline():
    from PIL import ImageDraw
    im = Image.new('RGBA', (1000, 80), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((500, 40), 'Descubre, reserva y vive Tierras Altas', font=font(600, 42), fill=(255, 255, 255, 255), anchor='mm')
    return pil_premul(im)

def sc18(t, under):
    c = under
    yy, xx = None, None
    r1 = 1250 * e_io(prog(t, 42.08, 42.40)); r2 = 1250 * e_io(prog(t, 42.18, 42.52))
    fin = bg_dark(t)
    m1 = circle_mask(r1); m2 = circle_mask(r2)
    c = c * (1 - m1) + np.array(LIME_B, np.float32) / 255 * m1
    c = c * (1 - m2) + fin * m2
    if t >= 42.32:
        p = prog(t, 42.32, 42.80)
        paste(c, logo('white', 640), 540, 820, 0.4 + 0.6 * e_back(p, 1.8), 0, clamp(p * 3))
    if t >= 42.62:
        p = prog(t, 42.62, 43.0)
        paste(c, tagline(), 540, 1030 + 40 * (1 - e_out(p)), 1.0, 0, p)
    chip_anim(c, t, 42.95, chip(None, 'cabanypanama.com', 'lime', 50), 540, 1175, float_amp=4)
    return c

def circle_mask(r):
    if r <= 0: return np.zeros((H, W, 1), np.float32)
    sc = 0.25
    m = np.zeros((int(H * sc), int(W * sc)), np.float32)
    cv2.circle(m, (int(540 * sc), int(960 * sc)), int(r * sc), 1.0, -1, cv2.LINE_AA)
    return cv2.resize(m, (W, H))[..., None]

# ---------------------------------------------------------------- master
def scene(t):
    if t < 2.48: return sc1(t)
    if t < 5.34: return sc2(t)
    if t < 7.63: return sc3(t)
    if t < 10.10: return sc4(t)
    if t < 12.60: return sc5(t)
    if t < 14.40: return sc6(t)
    if t < 16.50: return sc7(t)
    if t < 19.60: return sc8(t)
    if t < 22.64: return sc9(t)
    if t < 25.14: return sc10(t)
    if t < 28.04: return sc11(t)
    if t < 30.94: return sc12(t)
    if t < 33.60: return sc13(t)
    if t < 35.50: return sc14(t)
    if t < 38.57: return sc15_16(t)
    return sc17(t)

def whip(t, a_fn, b_fn, tc, half=0.11, axis='x', dist=None):
    """Push transition centred at tc."""
    p = prog(t, tc - half, tc + half)
    k = e_io(p)
    D = (W if axis == 'x' else H) if dist is None else dist
    A = a_fn(min(t, tc - 1e-3)); B = b_fn(max(t, tc))
    if axis == 'x':
        A = shift_img(A, -D * k, 0); B = shift_img(B, D * (1 - k), 0)
        cut = int(W * (1 - k))
        out = A.copy(); out[:, cut:] = B[:, cut:]
        bl = 120 * math.sin(math.pi * p)
        return motion_blur(out, bl, 0)
    A = shift_img(A, 0, -D * k); B = shift_img(B, 0, D * (1 - k))
    cut = int(H * (1 - k))
    out = A.copy(); out[cut:] = B[cut:]
    return motion_blur(out, 0, 140 * math.sin(math.pi * p))

def zoomblur_tr(t, a_fn, b_fn, tc, half=0.12, amt=0.32):
    if t < tc:
        p = e_in(prog(t, tc - half, tc))
        img = a_fn(t)
        return zoom_blur(shift_img(img, 0, 0, 1 + 0.25 * p), amt * p)
    p = 1 - e_out(prog(t, tc, tc + half))
    img = b_fn(t)
    return zoom_blur(shift_img(img, 0, 0, 1 + 0.18 * p), amt * p)

def frame(t):
    if 2.37 <= t <= 2.59:
        c = whip(t, sc1, sc2, 2.48)
    elif 5.22 <= t <= 5.46:
        c = zoomblur_tr(t, sc2, sc3, 5.34)
    elif 12.46 <= t <= 12.66:
        c = whip(t, sc5, sc6, 12.56, half=0.10, axis='y')
    elif 24.92 <= t <= 25.34:
        c = zoomblur_tr(t, sc10, sc11, 25.14, half=0.2, amt=0.45)
    elif 27.95 <= t <= 28.13:
        c = whip(t, sc11, sc12, 28.04, half=0.09)
    elif 30.85 <= t <= 31.03:
        c = whip(t, sc12, sc13, 30.94, half=0.09)
    elif 33.48 <= t <= 33.72:
        c = zoomblur_tr(t, sc13, sc14, 33.60)
    elif 35.40 <= t <= 35.60:
        c = zoomblur_tr(t, sc14, sc15_16, 35.50, half=0.1)
    else:
        c = scene(t)
    c = push_motion(c, t, [(14.38, 14.62, 90, 0), (26.40, 26.64, 110, 0), (12.58, 12.80, 0, 90)])
    if 38.42 <= t <= 38.74:
        a = 1 - abs(t - 38.57) / 0.16
        c = c * (1 - clamp(a)) + clamp(a)
    if t >= 42.08:
        c = sc18(t, c)
    else:
        draw_captions(c, t)
    if t < 42.30:
        watermark(c)
    return np.clip(c, 0, 1)

def save(c, path, q=93):
    cv2.imwrite(path, cv2.cvtColor((c * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, q])

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'test':
        os.makedirs(f'{ROOT}/test', exist_ok=True)
        for a in sys.argv[2:]:
            t = float(a); save(frame(t), f'{ROOT}/test/t_{t:06.2f}.jpg')
    elif cmd == 'render':
        a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        os.makedirs(out, exist_ok=True)
        for i in range(a, b):
            p = f'{out}/{i:05d}.jpg'
            if os.path.exists(p): continue
            save(frame(i / FPS), p, 95)

def render_worker(k, n, out):
    os.makedirs(out, exist_ok=True)
    total = int(DUR * FPS)
    for i in range(k, total, n):
        p = f'{out}/{i:05d}.jpg'
        if os.path.exists(p): continue
        save(frame(i / FPS), p, 95)
