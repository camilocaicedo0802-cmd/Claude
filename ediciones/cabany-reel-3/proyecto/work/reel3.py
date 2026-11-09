"""Cabany reel #3 — 'reserva desde ya' — timeline + renderer (style: Video de referencia Cabany 2)."""
import sys, os, math, functools
import numpy as np, cv2
from PIL import Image
from lib import *
from fx3 import *
import edl

FPS_SRC = 25
SW, SH = 2160, 3840
MS = SW / 720   # mask (720x1280) -> source scale
TAIL = 0.9
DUR = round(edl.DUR_EDIT + TAIL, 2)
def T_(i): return edl.WORDS[i][1]
def E_(i): return edl.WORDS[i][2]

# ------------------------------------------------------------------ subject tracking (from masks)
@functools.lru_cache(maxsize=1)
def track():
    n = len(os.listdir(f'{ROOT}/frames'))
    hx = np.full(n, np.nan); ht = np.full(n, np.nan)
    for i in range(n):
        p = f'{ROOT}/masks/{i:04d}.png'
        if not os.path.exists(p): continue
        m = cv2.imread(p, 0) > 128
        rows = np.where(m.sum(1) > 6)[0]
        if not len(rows): continue
        top = rows.min(); hy, hxx = np.where(m[top:top + 70])
        hx[i] = hxx.mean() * MS; ht[i] = top * MS
    for a in (hx, ht):
        idx = np.arange(n); ok = ~np.isnan(a)
        a[~ok] = np.interp(idx[~ok], idx[ok], a[ok])
    k = 9
    hx = np.convolve(np.pad(hx, k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), 'valid')
    ht = np.convolve(np.pad(ht, k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), 'valid')
    return hx, ht

@functools.lru_cache(maxsize=12)
def src_frame(i):
    i = int(min(max(i, 0), len(os.listdir(f'{ROOT}/frames')) - 1))
    return cv2.cvtColor(cv2.imread(f'{ROOT}/frames4k/{i:04d}.jpg'), cv2.COLOR_BGR2RGB).astype(np.float32) / 255

@functools.lru_cache(maxsize=6)
def src_mask(i):
    p = f'{ROOT}/masks/{int(i):04d}.png'
    if not os.path.exists(p): return None
    m = cv2.imread(p, 0).astype(np.float32) / 255
    return cv2.GaussianBlur(cv2.resize(m, (SW, SH)), (0, 0), 1.5)

# vignette + grade
@functools.lru_cache(maxsize=1)
def vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.42) / (H * 0.62)) ** 2)
    v = 1 - 0.42 * np.clip(d - 0.35, 0, 1) ** 1.4
    bottom = 1 - 0.35 * np.clip((yy - H * 0.78) / (H * 0.22), 0, 1)
    return (v * bottom)[..., None]

def grade(img):
    img = np.clip((img - 0.5) * 1.12 + 0.5 - 0.02, 0, 1)
    g = img.mean(-1, keepdims=True)
    img = g + (img - g) * 1.12
    img = img * np.array([1.03, 1.0, 0.95], np.float32)
    return np.clip(img * vignette(), 0, 1)

# ------------------------------------------------------------------ talking head camera
SEG_Z = [1.40, 1.62, 1.44, 1.66, 1.42, 1.60, 1.46, 1.68, 1.42, 1.62, 1.48, 1.64, 1.44, 1.60]
PUNCH = []   # filled below with (t, factor)

def seg_index(t):
    k = 0
    for j, o in enumerate(edl.OUT0):
        if t >= o: k = j
    return k

def camera(t):
    k = seg_index(t); o = edl.OUT0[k]
    z = SEG_Z[k % len(SEG_Z)] * (1 + 0.022 * (t - o))
    z *= 1 + 0.06 * (1 - e_out(prog(t, o, o + 0.2)))      # punch on every jump cut
    for tp, f in PUNCH:
        if t >= tp: z_p = f
    for tp, f in PUNCH:
        if tp <= t < tp + 0.9: z *= 1 + (f - 1) * e_out(prog(t, tp, tp + 0.14))
    return z

def talking_frame(t, want_mask=False):
    rt = edl.raw_of(min(t, edl.DUR_EDIT - 0.01)) if t < edl.DUR_EDIT else edl.SEGS[-1][1] - 0.04 + (t - edl.DUR_EDIT) * 0.0
    fi = int(round(rt * FPS_SRC))
    hx, ht = track()
    fi = min(fi, len(hx) - 1)
    z = max(camera(t), SH * 0.27 / max(ht[fi], 1) * 1.02)
    cw, ch = SW / z, SH / z
    cx = clamp(hx[fi], cw / 2, SW - cw / 2)
    y0 = clamp(ht[fi] - 0.27 * ch, 0, SH - ch); x0 = cx - cw / 2
    s = W / cw
    M = np.array([[s, 0, -x0 * s], [0, s, -y0 * s]], np.float32)
    img = cv2.warpAffine(src_frame(fi), M, (W, H), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    pm = None
    if want_mask:
        m = src_mask(fi)
        if m is not None: pm = cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    return grade(img), pm

# ------------------------------------------------------------------ captions (chest) — (t0, t1, lines)
CHEST_Y = 1230
def L(*lines): return lines
CAPS = []
def cap(t0, t1, *lines, y=None): CAPS.append(dict(t0=t0, t1=t1, lines=list(lines), y=y))

cap(T_(0), T_(3), ('w', 'Hey, ya sabes', T_(0)))
cap(T_(3), T_(6), ('w', 'reserva', T_(3)), ('gc', 'desde ya', T_(4)))
cap(T_(6), T_(9), ('w', 'www.', T_(6)), ('g', 'cabanypanama.com', T_(7)))
cap(T_(13), T_(16), ('w', 'es totalmente', T_(13)), ('g', 'fácil', T_(15)))
cap(T_(16), T_(17), ('w', 'Vas,', T_(16)))
cap(T_(19), T_(20), ('wc', 'cabaña', T_(19)))
cap(T_(20), T_(22), ('wc', 'hotel', T_(20)))
cap(T_(22), T_(24), ('w', 'La reserva', T_(22)))
cap(T_(25), T_(27), ('w', 'por', T_(25)), ('g', 'Yappy', T_(26)))
cap(T_(27), T_(31), ('w', 'o por', T_(27)), ('g', 'Visa', T_(29)))
cap(T_(31), T_(34), ('w', 'es totalmente', T_(31)), ('g', 'fácil', T_(33)))
cap(T_(34), T_(36), ('w', 'Así que', T_(34)))
cap(T_(36), T_(38), ('w', 'no esperes', T_(36)))
cap(T_(38), T_(42), ('w', 'a que llegue ya', T_(38)))
cap(T_(42), T_(43) + 0.02, ('gi', 'noviembre', T_(42)))
cap(T_(66), T_(69), ('w', 'Y muy', T_(66)), ('gc', 'importante', T_(68)))
cap(T_(69), T_(71), ('w', 'tenemos cabañas', T_(69)))
cap(T_(71), T_(74), ('w', 'para grupos', T_(71)), ('g', 'grandes', T_(73)))
cap(T_(74), T_(76), ('w', 'y también', T_(74)))
cap(T_(76), T_(79), ('w', 'para grupos', T_(76)), ('g', 'pequeños', T_(78)))
cap(T_(79), T_(83), ('w', 'Así que ya sabes', T_(79)))
cap(T_(83), T_(85), ('w', 'déjanos aquí', T_(83)))
cap(T_(85), T_(88), ('w', 'en los comentarios', T_(85)), y=1330)
# B-roll captions
BCAPS = [dict(t0=T_(61), t1=T_(63), lines=[('w', 'para poder', T_(61))]),
         dict(t0=T_(63), t1=T_(64), lines=[('g', 'reservar', T_(63))]),
         dict(t0=T_(64), t1=T_(66), lines=[('w', 'tu cabaña', T_(64))])]

PUNCH += [(T_(4), 1.10), (T_(9), 1.12), (T_(17), 1.12), (T_(24), 1.12), (T_(33), 1.08), (T_(42), 1.10), (T_(68), 1.10), (T_(73), 1.08), (T_(78), 1.08), (T_(90), 1.10)]

# ------------------------------------------------------------------ talking scene overlays
TOP_Y = 360
def overlays_talking(c, t, pm):
    # --- hook: glowing box with three houses, then numbered circles
    tb0, tb1 = T_(3) - 0.05, T_(8) + 0.25
    if glow_box(c, t, tb0, tb1, 540, TOP_Y, 520, 210) > 0:
        for k, x in enumerate((392, 540, 688)):
            drop_in(c, t, T_(3) + 0.10 * k, house_glyph(118), x, TOP_Y, t1=tb1, dy=-90)
    for k, x in enumerate((370, 540, 710)):
        drop_in(c, t, T_(8) + 0.30 + 0.16 * k, num_circle(k + 1, 132), x, TOP_Y, t1=T_(9) + 0.1, dy=-110)
    # --- steps: big number + word
    if T_(9) <= t < T_(11) + 0.1: number_word(c, t, 1, 'ENTRA', T_(9), T_(9) + 0.12, T_(11) - 0.03, CHEST_Y)
    if T_(17) <= t < T_(19) + 0.1: number_word(c, t, 2, 'ESCOGE', T_(17), T_(17) + 0.12, T_(19) - 0.02, CHEST_Y)
    if T_(24) <= t < T_(25) + 0.1: number_word(c, t, 3, 'PAGA', T_(24), T_(24) + 0.12, T_(25) - 0.02, CHEST_Y)
    # --- icon boxes row (top)
    t_off = T_(22) + 0.05
    tile_in(c, t, T_(19), icon_box('caba_a_mariposa.webp', 'Cabaña'), 410, TOP_Y, t_off)
    tile_in(c, t, T_(21), icon_box('luxury_canyon_suites.webp', 'Hotel'), 670, TOP_Y, t_off)
    t_off = T_(31) + 0.05
    tile_in(c, t, T_(26), icon_box('phonepay', 'Yappy'), 410, TOP_Y, t_off)
    tile_in(c, t, T_(29), icon_box('card', 'Visa'), 670, TOP_Y, t_off)
    tile_in(c, t, T_(42), icon_box('calendar', None, 230), 540, TOP_Y, T_(43) + 0.2)
    # --- people counter (grupos grandes / pequeños)
    people(c, t)
    # --- chest captions
    for cp in CAPS:
        caption(c, t, cp, cp['y'] or CHEST_Y)
    # --- CTA
    cta(c, t)

def tile_in(c, t, t0, img, x, y, t1):
    if t < t0 or t >= t1 + 0.18: return
    p = prog(t, t0, t0 + 0.26)
    s = 0.55 + 0.45 * e_back(p, 2.0)
    op = clamp((t - t0) / 0.05)
    if t >= t1:
        q = prog(t, t1, t1 + 0.18); op *= 1 - q; s *= 1 - 0.2 * q
    yy = y + 4 * math.sin((t - t0) * 2.6 + x)
    paste(c, img, x, yy, s, 0, op)

def ghosts_behind(c, t, img_person, pm):
    """giant translucent check marks behind the subject ('es totalmente fácil')."""
    t0, t1 = T_(13), T_(16)
    if not (t0 <= t < t1 + 0.15) or pm is None: return c
    g = ghost_check(520)
    under = c.copy()
    for k, (x, y, d) in enumerate([(250, 760, 0.0), (820, 700, 0.12), (540, 520, 0.24)]):
        if t < t0 + d: continue
        p = prog(t, t0 + d, t0 + d + 0.35)
        s = (0.6 + 0.4 * e_out(p)) * (1 + 0.05 * (t - t0))
        op = clamp(p * 3) * (1 - clamp((t - t1) / 0.15)) * 0.85
        paste(under, g, x, y - 30 * e_out(p), s, 0, op)
    return under * (1 - pm) + c * pm

PEOPLE_X = [540 + (k - 3.5) * 112 for k in range(8)]
def people(c, t):
    t0, tdown, t1 = T_(72) - 0.05, T_(78), T_(79) + 0.1
    if not (t0 <= t < t1 + 0.15): return
    ic = person_icon(96)
    for k, x in enumerate(PEOPLE_X):
        tk = t0 + 0.07 * k
        if t < tk: continue
        keep = k in (3, 4)
        p = prog(t, tk, tk + 0.18)
        s = 0.4 + 0.6 * e_back(p, 2.4)
        op = clamp((t - tk) / 0.05)
        xx = x
        if t >= tdown:
            q = e_io(prog(t, tdown, tdown + 0.28))
            if keep: xx = x + (540 + (k - 3.5) * 130 - x) * q; s *= 1 + 0.35 * q
            else: op *= 1 - q; s *= 1 - 0.4 * q
        if t >= t1: op *= 1 - clamp((t - t1) / 0.15)
        paste(c, ic, xx, TOP_Y + 6 * math.sin((t - tk) * 3 + k), s, 0, op)

def cta(c, t):
    tb = T_(85)
    if t < tb: return
    # comment bar slides up
    p = e_back(prog(t, tb, tb + 0.4), 1.4)
    n_typed = int(round(7 * prog(t, T_(89), T_(90) + 0.35)))
    typed = 'RESERVA'[:n_typed]
    t_click = T_(92) + 0.05
    sent = t >= t_click + 0.1
    bar = comment_bar(typed, sent, t_click - 0.25 <= t < t_click + 0.1)
    by = 1690 + 300 * (1 - p)
    paste(c, bar, 540, by, 1.0, 0, clamp(p * 2))
    # cursor
    if T_(90) <= t < t_click + 0.6:
        q = e_io(prog(t, T_(90) + 0.1, t_click - 0.05))
        x = 760 + (867 - 760) * q; y = 1880 + (1700 - 1880) * q
        press = 0.85 if t_click <= t < t_click + 0.12 else 1.0
        paste(c, cursor_img(), x + 20, y + 26, press, 0, 1 - clamp((t - t_click - 0.4) / 0.2))
    # big green word above + white lines
    caption(c, t, dict(t0=T_(88), t1=T_(91), lines=[('w', 'la palabra', T_(88))]), 1330)
    caption(c, t, dict(t0=T_(91), t1=T_(94), lines=[('w', 'y te mandamos', T_(91))]), 1330)
    caption(c, t, dict(t0=T_(94), t1=DUR + 1, lines=[('w', 'toda la información', T_(94))]), 1330)
    caption(c, t, dict(t0=T_(90), t1=DUR + 1, lines=[('big', 'RESERVA', T_(90))]), 1480)

# ------------------------------------------------------------------ phone insert (site)
P2F = os.path.join(os.path.dirname(ROOT), 'p2', 'frames')
def site_screen(t, t0):
    i = int(328 + (t - t0) * 30 * 1.15)
    f = cv2.cvtColor(cv2.imread(f'{P2F}/{min(i, 370):04d}.jpg'), cv2.COLOR_BGR2RGB)
    r, g, b = [f[..., k].astype(int) for k in range(3)]
    yel = ((r > 185) & (g > 165) & (b < 120)).astype(np.uint8); yel[:, :1000] = 0
    if yel.sum() > 20: f = cv2.inpaint(f, cv2.dilate(yel, np.ones((17, 17), np.uint8)), 7, cv2.INPAINT_TELEA)
    return f

@functools.lru_cache(maxsize=2)
def phone_shell(sc):
    pw, ph = int((1080 + 60) * sc), int((1920 + 60) * sc)
    im = Image.new('RGBA', (pw * 2, ph * 2), (0, 0, 0, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw * 2 - 1, ph * 2 - 1], int(150 * sc * 2), fill=(70, 74, 78, 255))
    d.rounded_rectangle([int(6 * sc * 2), int(6 * sc * 2), pw * 2 - int(6 * sc * 2), ph * 2 - int(6 * sc * 2)], int(144 * sc * 2), fill=(8, 8, 10, 255))
    im = im.resize((pw, ph), Image.LANCZOS)
    m = np.asarray(rounded_mask(int(1080 * sc), int(1920 * sc), int(110 * sc))).astype(np.float32)[..., None] / 255
    return pil_premul(im), m

def phone_scene(t, t0, t1):
    c = np.empty((H, W, 3), np.float32)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    c[:] = np.array(rgb('0B3B28'), np.float32) / 255 * (1 - yy) + np.array(rgb('010F09'), np.float32) / 255 * yy
    blobs(c, t, [(200, 500, 360, (0.66, 0.91, 0.23), 0.22, 0.0), (900, 1400, 340, (0.66, 0.91, 0.23), 0.16, 2.0)])
    sc = 0.6
    shell, m = phone_shell(sc)
    scr = cv2.resize(site_screen(t, t0), (int(1080 * sc), int(1920 * sc)), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    ph = shell.copy(); o = int(30 * sc)
    reg = ph[o:o + scr.shape[0], o:o + scr.shape[1]]
    reg[..., :3] = reg[..., :3] * (1 - m) + scr * m; reg[..., 3:] = reg[..., 3:] * (1 - m) + m
    p = prog(t, t0, t1)
    ry = 24 - 40 * e_io(p); rx = 10 - 4 * p; rz = -4 + 6 * p
    s = 1.05 + 0.12 * e_out(p)
    hh, ww = ph.shape[:2]
    q = quad3d(ww, hh, 540, 1040 + 120 * (1 - e_out(prog(t, t0, t0 + 0.3))), s, rx, ry, rz)
    shadow_quad(c, q, blur=60, alpha=0.45, off=(20, 40))
    warp(c, ph, q)
    caption(c, t, dict(t0=t0, t1=t1, lines=[('w', 'en nuestra', T_(11)), ('g', 'plataforma', T_(12))]), 300)
    return c

# ------------------------------------------------------------------ 3D pillars chart
PILLARS = [  # label, emoji, word index (appear), height, colours (front top/bottom, side, top)
    ('Fiestas Patrias', '🇵🇦', 45, 560, ((0.98, 0.98, 0.98), (0.70, 0.72, 0.72)), (0.55, 0.57, 0.57), (1.0, 1.0, 1.0)),
    ('Fin de año', '🎆', 50, 700, ((0.78, 0.95, 0.42), (0.36, 0.72, 0.17)), (0.22, 0.48, 0.12), (0.86, 1.0, 0.55)),
    ('Feria de las Flores', '🌸', 57, 840, ((0.10, 0.45, 0.30), (0.01, 0.22, 0.14)), (0.0, 0.14, 0.09), (0.18, 0.58, 0.40)),
]
def chart_scene(t, t0, t1):
    c = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H:4, 0:W:4].astype(np.float32)
    spot = np.exp(-(((xx - 600) / 700) ** 2 + ((yy - 900) / 900) ** 2)) * 0.16
    c[:] = cv2.resize(spot, (W, H))[..., None] * np.array([0.75, 0.9, 0.8], np.float32)
    p = prog(t, t0, t1)
    cam = 1.0 + 0.05 * e_io(p); pan = 0
    base_y = 1640
    w, d = 215, 145
    for k, (lab, emo, wi, hgt, fcol, scol, tcol) in enumerate(PILLARS):
        ta = T_(wi) - 0.1
        if t < ta: continue
        q = prog(t, ta, ta + 0.45)
        h = hgt * e_back(q, 1.3) * cam
        x = 110 + k * 262 + pan
        x = 540 + (x - 540) * cam
        front = pillar(c, x, base_y, w * cam, d * cam, h, lambda poly, f=fcol: vgrad(poly, f[0], f[1]), scol, tcol, cam_dx=0.15 * p)
        if front is None: continue
        ei = pil_premul(emoji_img(emo, int(110 * cam)))
        paste(c, ei, x + w * cam / 2, base_y - h + 110 * cam, 1.0, 0, clamp(q * 3))
        lb = get(lab, 'w', 40 if len(lab) < 12 else 34)
        put(c, lb, x + w * cam / 2 - lb[3] / 2, base_y - h - 60 * cam, clamp((q - 0.3) * 3), 1.0)
    # floor reflection fade
    c[base_y:] *= np.linspace(1, 0.15, H - base_y, dtype=np.float32)[:, None, None]
    # title typed word by word (reference: 'The Richest Companies on the planet')
    words = [('Temporada', t0 + 0.05), ('alta', t0 + 0.32)]
    xx0 = 110 + pan * 0.3
    for wd, tw in words:
        if t < tw: break
        img = get(wd, 'gi', 92)
        ps = pop_state(t, tw, t1)
        if ps: put(c, img, xx0, 360, ps[0], ps[1], ps[2])
        xx0 += img[3] + 24
    caption(c, t, dict(t0=T_(36), t1=t1, lines=[('w', 'reserva con tiempo', T_(43) + 0.4)]), 480)
    return c

# ------------------------------------------------------------------ B-roll cabins
BROLL = [('lcs_1.webp', 61), ('caba_a_mariposa.webp', 63), ('caba_a_rancho_me_a.webp', 64)]
def broll_scene(t):
    k = 0
    for j, (_, wi) in enumerate(BROLL):
        if t >= T_(wi) - 0.05: k = j
    img, wi = BROLL[k]
    ts = T_(wi) - 0.05
    ph = Image.open(f'{ROOT}/site/img/{img}').convert('RGB')
    s = 1.06 + 0.10 * (t - ts)
    fr = cover(ph, W, H).resize((int(W * s), int(H * s)), Image.BILINEAR)
    ox = (fr.width - W) // 2 + int((-40 if k % 2 else 40) * (t - ts)); oy = (fr.height - H) // 2
    c = np.asarray(fr.crop((ox, oy, ox + W, oy + H))).astype(np.float32) / 255
    c = grade(c) * 0.92
    for cp in BCAPS: caption(c, t, cp, 1100)
    return c

# ------------------------------------------------------------------ watermark
@functools.lru_cache(maxsize=2)
def url_text(mode):
    from PIL import ImageDraw
    im = Image.new('RGBA', (300, 40), (0, 0, 0, 0))
    col = (255, 255, 255, 255) if mode == 'light' else GREEN + (255,)
    ImageDraw.Draw(im).text((150, 20), 'cabanypanama.com', font=pfont(600, False, 22), fill=col, anchor='mm')
    return pil_premul(im)
@functools.lru_cache(maxsize=4)
def logo(kind, width):
    im = Image.open(f'{ROOT}/brand/logo-{kind}.png').convert('RGBA'); im = im.crop(im.getbbox())
    return pil_premul(im.resize((width, int(im.height * width / im.width)), Image.LANCZOS))
def watermark(c):
    paste(c, logo('white', 160), 945, 150, 1.0, 0, 0.6)
    paste(c, url_text('light'), 945, 208, 1.0, 0, 0.5)

# ------------------------------------------------------------------ master
PH0, PH1 = T_(11) - 0.06, T_(13) - 0.06
CH0, CH1 = T_(43) - 0.06, T_(61) - 0.06
BR0, BR1 = CH1, T_(66) - 0.06

def scene(t):
    if PH0 <= t < PH1: return phone_scene(t, PH0, PH1)
    if CH0 <= t < CH1: return chart_scene(t, CH0, CH1)
    if BR0 <= t < BR1: return broll_scene(t)
    img, pm = talking_frame(t, want_mask=(T_(13) <= t < T_(16) + 0.2))
    c = ghosts_behind(img, t, img, pm) if pm is not None else img
    c = np.ascontiguousarray(c, dtype=np.float32)
    overlays_talking(c, t, pm)
    return c

def zoomblur_tr(t, tc, half=0.12, amt=0.3):
    if t < tc:
        p = e_in(prog(t, tc - half, tc)); return zoom_blur(shift_img(scene(t), 0, 0, 1 + 0.2 * p), amt * p)
    p = 1 - e_out(prog(t, tc, tc + half)); return zoom_blur(shift_img(scene(t), 0, 0, 1 + 0.15 * p), amt * p)

def whip_tr(t, tc, half=0.1):
    p = prog(t, tc - half, tc + half); k = e_io(p)
    A = scene(min(t, tc - 1e-3)); B = scene(max(t, tc))
    A = shift_img(A, -W * k, 0); B = shift_img(B, W * (1 - k), 0)
    cut = int(W * (1 - k)); out = A.copy(); out[:, cut:] = B[:, cut:]
    return motion_blur(out, 120 * math.sin(math.pi * p), 0)

def frame(t):
    if abs(t - PH0) < 0.12: c = zoomblur_tr(t, PH0)
    elif abs(t - PH1) < 0.12: c = zoomblur_tr(t, PH1)
    elif abs(t - CH0) < 0.14:
        c = scene(t); k = 1 - abs(t - CH0) / 0.14
        c = c * (1 - 0.85 * k)
        c = zoom_blur(c, 0.18 * k)
    elif abs(t - BR0) < 0.1: c = whip_tr(t, BR0)
    elif abs(t - BR1) < 0.12: c = zoomblur_tr(t, BR1)
    else:
        c = scene(t)
        # micro whip-shake on some jump cuts (reference)
        for tc in edl.CUTS[1::3]:
            if 0 <= t - tc < 0.07: c = motion_blur(shift_img(c, 0, 0, 1.03), 0, 40)
    watermark(c)
    if t > DUR - 0.25: c = c * clamp((DUR - t) / 0.25)
    return np.clip(c, 0, 1)

def save(c, path, q=94):
    cv2.imwrite(path, cv2.cvtColor((c * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, q])

def render_worker(k, n, out):
    os.makedirs(out, exist_ok=True)
    for i in range(k, int(DUR * FPS), n):
        p = f'{out}/{i:05d}.jpg'
        if not os.path.exists(p): save(frame(i / FPS), p, 95)

if __name__ == '__main__':
    os.makedirs(f'{ROOT}/test', exist_ok=True)
    for a in sys.argv[1:]:
        t = float(a); save(frame(t), f'{ROOT}/test/t_{t:06.2f}.jpg')
