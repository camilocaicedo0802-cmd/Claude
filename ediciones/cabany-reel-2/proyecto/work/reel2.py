"""Cabany reel #2 ('Video de referencia Cabany' style) — timeline + renderer."""
import sys, os, json, math
import numpy as np, cv2
from PIL import Image
from lib import *
from assets2 import *
from typo3 import *

DUR = 33.0
LIMEf = tuple(v / 255 for v in LIME_B)
WHITEf = (1.0, 1.0, 1.0)
def axs(sx): return (sx + PB) / PW
def ays(sy): return (sy + BAR + PB) / PH   # raw-frame y -> phone anchor (status bar added on top)

# ------------------------------------------------------------------ talking shots
SHOTS = {'door': dict(ht=750, cy=1050), 'balcony': dict(ht=790, cy=1060), 'selfie': dict(ht=576, cy=1100)}

def win(cx, cy, z):
    w, h = W / z, H / z
    return clamp(cx - w / 2, 0, W - w), clamp(cy - h / 2, 0, H - h)

def grade(img):
    img = (img - 0.5) * 1.07 + 0.5
    g = img.mean(-1, keepdims=True)
    return np.clip(g + (img - g) * 1.06, 0, 1)

def aroll(src_t, cx, cy, z):
    i = int(round(src_t * FPS))
    f = grade(raw(i).astype(np.float32) / 255)
    x0, y0 = win(cx, cy, z)
    M = np.array([[z, 0, -x0 * z], [0, z, -y0 * z]], np.float32)
    img = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    pm = None
    if os.path.exists(f'{ROOT}/masks/{i:04d}.png'):
        pm = cv2.warpAffine(mask(i), M, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    return img, pm, (x0, y0)

def cut_params(t, cuts):
    """cuts: [(t, z, cx)] -> current (z, cx, t_cut); slow push-in inside every cut."""
    cur = cuts[0]
    for c_ in cuts:
        if t >= c_[0]: cur = c_
    z = cur[1] * (1 + 0.03 * (t - cur[0]))
    # punch-in pop at each cut
    z *= 1 + 0.05 * (1 - e_out(prog(t, cur[0], cur[0] + 0.18)))
    return z, cur[2], cur[0]

@functools.lru_cache(maxsize=64)
def mask_top(i, default):
    p = f'{ROOT}/masks/{i:04d}.png'
    if not os.path.exists(p): return default
    m = cv2.imread(p, 0)[:, 250:850] > 128
    rows = np.where(m.sum(1) > 25)[0]
    return int(rows.min()) if len(rows) else default

def talking(t, shot, cuts, heads=(), chests=(), extras=None, src_t=None):
    z, cx, tc = cut_params(t, cuts)
    S = SHOTS[shot]
    st = t if src_t is None else src_t
    img, pm, (x0, y0) = aroll(st, cx, S['cy'], z)
    c = img.copy()
    ht_src = S['ht'] if shot == 'selfie' else max(mask_top(int(round(max(tc, st - 0.4) * FPS)), S['ht']), S['ht'] - 90)
    head_top = (ht_src - y0) * z
    hs = []
    for h in heads:
        hh = dict(h); hh['y'] = head_top + h.get('dy', 6)
        headline(c, t, hh, 'behind'); hs.append(hh)
    if pm is not None:   # big words sit behind the head
        c = c * (1 - pm) + img * pm
    for hh in hs:
        headline(c, t, hh, 'front')
    chest_y = head_top + 520 * z * 0.92
    for it in chests:
        chest(c, t, chest_y, [it])
    if extras: extras(c, t, head_top, chest_y)
    return c

# ------------------------------------------------------------------ scenes
def scA(t):  # door — "te muestro cómo buscar tu próxima cabaña"
    heads = [dict(t0=0.0, t1=1.40, thin=('te muestro cómo', [0.0, 0.46, 0.74]), big=[('buscar', 0.98)], kind='rise'),
             dict(t0=1.40, t1=2.62, thin=('tu próxima', [1.40, 1.68]), big=[('cabaña', 2.06)], kind='whip')]
    def ex(c, t, ht, cy):
        line_icon_anim(c, t, 2.08, 2.62, 'cabin', 865, ht + 190, 230)
    return talking(t, 'door', [(0.0, 1.10, 585), (0.98, 1.32, 590), (1.40, 1.16, 585)], heads, (), ex, src_t=min(t, 2.44))

def scB(t):  # balcony
    heads = [dict(t0=2.62, t1=4.46, thin=('si estás pensando en', [2.48, 2.72, 2.94, 3.28]), big=[('escaparte', 3.48)],
                  heavy=('a Chiriquí', [3.86, 4.02]), kind='whip', size=180),
             dict(t0=4.46, t1=4.98, big=[('mira', 4.46), ('esto', 4.74)], kind='rise', size=200, dy=-20),
             dict(t0=5.94, t1=7.38, big=[('organizar', 5.96)], heavy=('tu próximo viaje', [6.42, 6.64, 7.04]), kind='rise', size=175)]
    chests = [('porque', 'chest', 4.98, 5.22), ('te puede', 'chest', 5.22, 5.56), ('ayudar a', 'chesti', 5.56, 5.94)]
    def ex(c, t, ht, cy):
        line_icon_anim(c, t, 4.04, 4.42, 'mountain', 200, ht + 170, 220)
        banner(c, t, 6.50, 7.34, 'Viaje a Chiriquí', 'Organízalo en cabanypanama.com', y=300)
    return talking(t, 'balcony', [(2.62, 1.26, 700), (4.46, 1.48, 705), (4.98, 1.26, 700), (5.94, 1.40, 700)], heads, chests, ex, src_t=max(t, 2.92))

def scC(t):  # "paso 1" title moment
    f, _, _ = aroll(min(t, 7.6), 700, 1060, 1.5 + 0.2 * prog(t, 7.36, 8.1))
    c = gblur(f, 16) * 0.62 + np.array(GREEN_D, np.float32) / 255 * 0.38
    blobs(c, t, [(200, 600, 380, LIMEf, 0.22, 0.0), (900, 1300, 360, LIMEf, 0.18, 2.0)])
    st = enter(t, 7.36, 8.2, 'rise', 0.05)
    if st:
        img = big_word('paso', 200)
        put(c, img, 540 - img[3] / 2 - 120 + st[2], 860 + st[3], st[0], st[1], st[4])
    st = enter(t, 7.70, 8.2, 'pop', 0.08)
    if st:
        img = big_word('1', 520)
        put(c, img, 690 - img[3] / 2, 1120, st[0], st[1])
    line_icon_anim(c, t, 7.40, 8.1, 'search', 540, 1330, 200)
    return c

BLOBS_TOUR = [(140, 520, 340, LIMEf, 0.34, 0.0), (960, 1080, 300, LIMEf, 0.26, 2.0),
              (860, 300, 240, WHITEf, 0.55, 4.0), (180, 1560, 300, LIMEf, 0.20, 1.0)]
def bg_tour(t):
    c = grad_bg('tour').copy(); blobs(c, t, BLOBS_TOUR); return c

def cam_phone(c, scr, cam, shadow=0.38):
    cx, cy, s, rx, ry, rz, ax, ay = cam
    return draw_phone(c, scr, cx, cy, s, rx, ry, rz, ax, ay, shadow=shadow)

def typed_pill(c, t, t0, t1, text, t_type0, t_type1, x, y):
    n = int(round(len(text) * prog(t, t_type0, t_type1)))
    shown = text[:max(1, n)] + ('|' if n < len(text) and int(t * 6) % 2 == 0 else '')
    glass_pill(c, t, t0, t1, shown, x, y, 56, '🌐')

CARDS = [(('caba_a_mariposa.webp', 'Cabaña Mariposa', 'Volcán', '$120', '/ noche', 'Cabaña'), 11.10, 250, 640, -6),
         (('villa_diana.webp', 'Villa Diana', 'Boquete', 'desde $30', '/ noche', 'Hotel'), 11.54, 835, 800, 5),
         (('harmony_gates.webp', 'Harmony Gates', 'Volcán', '$25', '/ persona', 'Glamping'), 11.80, 245, 1120, 4)]

def scD(t):  # home + listings (8.06 - 12.33)
    c = bg_tour(t)
    if t < 10.90:
        st = 8.62 + (t - 8.06) * (10.85 - 8.62) / (10.90 - 8.06)
        cam = kf(t, [(8.00, (540, 1750, 0.50, 55, -22, 9, .5, .5), lin), (8.45, (540, 920, 0.60, 10, -12, -2, .5, .5), e_out5),
                     (9.20, (540, 900, 0.62, 6, -6, -1, .5, .5), lin), (9.70, (540, 860, 1.05, 3, -2, 0, axs(540), ays(330)), e_io5),
                     (10.90, (540, 860, 1.10, 2, 2, 0, axs(540), ays(330)), lin)])
        scr = screen_t(st)
        scr = overlay_box(scr, (60, 255 + BAR, 1020, 345 + BAR), prog(t, 9.75, 10.05), radius=46, fill_alpha=0.06)
    else:
        st = 10.85 + (t - 10.90) * (12.3 - 10.85) / (12.33 - 10.90)
        cam = kf(t, [(10.90, (540, 860, 1.10, 2, 2, 0, axs(540), ays(330)), lin), (11.20, (540, 900, 0.62, 8, 16, 1, .5, .5), e_out5),
                     (12.33, (540, 900, 0.66, 6, -10, -1, .5, .5), e_io)])
        scr = screen_t(st)
    cam_phone(c, scr, cam)
    typed_pill(c, t, 8.56, 10.85, 'cabanypanama.com', 8.58, 10.66, 540, 300)
    for args, t0, x, y, rot in CARDS:
        if t < t0: continue
        card = listing_card(*args)
        p = e_out5(prog(t, t0, t0 + 0.45))
        sc = 0.12 + (0.56 - 0.12) * e_back(prog(t, t0, t0 + 0.45), 1.6)
        xx = 540 + (x - 540) * p; yy = 900 + (y - 900) * p + 6 * math.sin((t - t0) * 2.4)
        op = clamp((t - t0) / 0.1)
        if t > 12.10:
            qq = e_in(prog(t, 12.10, 12.33)); xx += (x - 540) * 1.4 * qq; op *= 1 - qq
        h, w = card.shape[:2]
        warp(c, card, quad3d(w, h, xx, yy, sc, 0, 30 * (1 - p) * (1 if x < 540 else -1), rot), op)
    chip_anim(c, t, 11.74, chip('🏡', 'Alojamientos', 'lime', 44), 540, 300, t1=12.25)
    return c

PHOTOS = [('lcs_2.webp', 220, 520, -10), ('lcs_3.webp', 860, 560, 9), ('lcs_4.webp', 200, 1180, 7), ('lcs_5.webp', 870, 1220, -8)]
def scE(t):  # phone-in-hand b-roll (12.33 - 15.33)
    z = 1.16 * (1 + 0.06 * (t - 12.33)) if t < 13.56 else 1.36 * (1 + 0.04 * (t - 13.56))
    z *= 1 + 0.05 * (1 - e_out(prog(t, 13.56, 13.74)))
    f = raw(int(round(t * FPS))).astype(np.float32) / 255
    w_, h_ = W / z, H / z
    x0 = clamp(500 - w_ / 2, 0, 975 - w_); y0 = clamp(1000 - h_ / 2, 0, H - h_)
    M = np.array([[z, 0, -x0 * z], [0, z, -y0 * z]], np.float32)
    c = grade(cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT))
    for k, (img, x, y, rot) in enumerate(PHOTOS):
        t0 = 13.98 + 0.12 * k
        if t < t0: continue
        pc = photo_card(img)
        p = prog(t, t0, t0 + 0.42); k5 = e_out5(p)
        sc = 0.12 + (0.58 - 0.12) * e_back(p, 1.7)
        xx = 540 + (x - 540) * k5; yy = 900 + (y - 900) * k5 + 6 * math.sin((t - t0) * 2.5)
        op = clamp((t - t0) / 0.1)
        if t > 15.05:
            qq = e_in(prog(t, 15.05, 15.33)); xx += (x - 540) * 1.5 * qq; yy -= 300 * qq; op *= 1 - qq
        h, w = pc.shape[:2]
        warp(c, pc, quad3d(w, h, xx, yy, sc, 0, 25 * (1 - k5) * (1 if x < 540 else -1), rot * k5), op)
    glass_pill(c, t, 12.40, 13.50, 'Alojamientos publicados', 540, 300, 52, '✨')
    return c

def scF(t):  # gallery + lightbox (15.33 - 18.77)
    c = bg_tour(t)
    if t < 17.73:
        st = 15.42 + (t - 15.33) * (17.70 - 15.42) / (17.73 - 15.33)
        cam = kf(t, [(15.33, (540, 880, 1.7, 0, 0, 0, .5, .45), lin), (15.66, (540, 900, 0.62, 8, 14, 1, .5, .5), e_out5),
                     (17.73, (540, 900, 0.66, 6, -10, -1, .5, .5), e_io)])
    else:
        st = 17.76 + (t - 17.73)
        cam = kf(t, [(17.73, (540, 900, 0.66, 6, -10, -1, .5, .5), lin), (18.0, (540, 860, 1.12, 2, 4, 0, axs(540), ays(850)), e_io5),
                     (18.77, (540, 860, 1.18, 1, -2, 0, axs(540), ays(850)), lin)])
    cam_phone(c, screen_t(st), cam)
    chip_anim(c, t, 15.40, chip('👥', 'Capacidad', 'white', 44), 250, 330, t1=17.0)
    chip_anim(c, t, 15.62, chip('💲', 'Precios', 'white', 44), 830, 450, t1=17.05)
    chip_anim(c, t, 15.96, chip('✅', 'Disponibles', 'lime', 44), 290, 1330, t1=17.1)
    if t >= 18.28:
        chip_anim(c, t, 18.28, chip('❤️', 'Te gusta', 'white', 48), 540, 330, t1=18.74)
        p = prog(t, 18.28, 18.75)
        if p < 1:
            ov = (c * 255).astype(np.uint8)
            hx, hy = 540, 860
            for k in range(12):
                a = k / 12 * 2 * math.pi + 0.3; r = 60 + 230 * e_out(p)
                col = [(239, 68, 68), (169, 233, 58), (255, 255, 255)][k % 3]
                cv2.circle(ov, (int(hx + r * math.cos(a)), int(hy + r * math.sin(a))), int(16 * (1 - p)) + 1, col, -1, cv2.LINE_AA)
            c[:] = ov.astype(np.float32) / 255
    return c

ROOM_BOX = (52, 785 + BAR, 1062, 968 + BAR)
BTN_BOX = (78, 988 + BAR, 990, 1062 + BAR)
CANCEL_BOX = (24, 1280 + BAR, 1060, 1372 + BAR)
def scG(t):  # LCS page, room types, booking box (18.77 - 21.64)
    c = bg_tour(t)
    if t < 19.40: st = 18.80 + (t - 18.77) * (19.50 - 18.80) / (19.40 - 18.77)
    elif t < 20.10: st = 19.50
    else: st = 19.50 + (t - 20.10) * (21.50 - 19.50) / (21.64 - 20.10)
    if t < 19.40:
        cam = kf(t, [(18.77, (540, 900, 0.64, 8, 14, 1, .5, .5), lin), (19.40, (540, 900, 0.66, 6, 6, 0, .5, .5), lin)])
    elif t < 20.30:
        cam = kf(t, [(19.40, (540, 900, 0.66, 6, 6, 0, .5, .5), lin), (19.65, (540, 880, 1.10, 3, -3, 0, axs(556), ays(876)), e_io5),
                     (20.30, (540, 880, 1.16, 2, 2, 0, axs(556), ays(876)), lin)])
    else:
        cam = kf(t, [(20.30, (540, 880, 1.16, 2, 2, 0, axs(556), ays(876)), lin), (20.70, (540, 900, 0.68, 8, -14, -1, .5, .5), e_io5),
                     (21.64, (540, 900, 0.70, 6, 8, 0, .5, .5), e_io)])
    scr = screen_t(st)
    if 19.40 <= t < 20.10: scr = overlay_box(scr, ROOM_BOX, prog(t, 19.62, 19.90), radius=40)
    cam_phone(c, scr, cam)
    chip_anim(c, t, 19.32, chip('📅', 'Fechas', 'white', 44), 260, 330, t1=21.55)
    chip_anim(c, t, 19.96, chip('📋', 'Detalles', 'white', 44), 820, 450, t1=21.58)
    chip_anim(c, t, 21.04, chip('✅', 'Disponibilidad', 'lime', 46), 540, 1330, t1=21.60)
    return c

def scH(t):  # "es súper sencillo ... completa tu reserva" (21.64 - 25.60)
    c = bg_tour(t)
    if t < 22.40: st = 21.50 + (t - 21.64) * (22.25 - 21.50) / (22.40 - 21.64)
    elif t < 23.95: st = 23.86
    else: st = 23.86 + (t - 23.95) * (25.50 - 23.86) / (25.60 - 23.95)
    cam = kf(t, [(21.64, (540, 900, 0.70, 6, 8, 0, .5, .5), lin), (22.40, (540, 900, 0.70, 6, -12, 0, .5, .5), e_io),
                 (22.60, (540, 880, 1.12, 3, 3, 0, axs(534), ays(1025)), e_io5), (23.90, (540, 880, 1.18, 2, -2, 0, axs(534), ays(1025)), lin),
                 (24.20, (540, 880, 0.72, 8, 12, 1, .5, .5), e_io5), (25.60, (540, 880, 0.76, 6, -6, 0, .5, .5), lin)])
    scr = screen_t(st)
    if 22.40 <= t < 23.95:
        scr = overlay_box(scr, BTN_BOX, prog(t, 22.70, 22.95), radius=60, fill_alpha=0.0)
        scr = overlay_tap(scr, 534, 1025 + BAR, prog(t, 23.30, 23.75))
    cam_phone(c, scr, cam)
    glass_pill(c, t, 22.28, 23.40, 'Súper sencillo', 540, 300, 58, '✨')
    chip_anim(c, t, 23.46, chip('👆', 'Sigue las indicaciones', 'white', 44), 540, 300, t1=24.6)
    chip_anim(c, t, 24.18, chip('📱', 'Todo en la plataforma', 'lime', 44), 540, 1360, t1=25.1)
    if t >= 25.08: success(c, t, 25.08)
    return c

def success(c, t, t0):
    p = prog(t, t0, t0 + 0.2)
    c[:] = c * (1 - 0.70 * p) + np.array(GREEN_D, np.float32) / 255 * 0.70 * p
    from PIL import ImageDraw
    ov = Image.fromarray((c * 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(ov)
    cx, cy = 540, 860
    q = prog(t, t0 + 0.05, t0 + 0.35); r = 160 * e_back(q, 2.2)
    if r > 1:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=LIME_B + (255,))
        k = e_out(prog(t, t0 + 0.15, t0 + 0.38))
        if k > 0:
            P = [(cx - 72, cy + 2), (cx - 20, cy + 56), (cx + 78, cy - 58)]
            L1 = math.dist(P[0], P[1]); L2 = math.dist(P[1], P[2]); L = (L1 + L2) * k
            path = [P[0]]
            if L <= L1: path.append((P[0][0] + (P[1][0] - P[0][0]) * L / L1, P[0][1] + (P[1][1] - P[0][1]) * L / L1))
            else:
                e = (L - L1) / L2; path += [P[1], (P[1][0] + (P[2][0] - P[1][0]) * e, P[1][1] + (P[2][1] - P[1][1]) * e)]
            d.line(path, fill=GREEN + (255,), width=36, joint='curve')
            for pp in (path[0], path[-1]): d.ellipse([pp[0] - 18, pp[1] - 18, pp[0] + 18, pp[1] + 18], fill=GREEN + (255,))
    c[:] = np.asarray(ov.convert('RGB')).astype(np.float32) / 255
    st = enter(t, t0 + 0.18, 26.0, 'rise', 0.04)
    if st:
        img = big_word('¡Reserva lista!', 120)
        put(c, img, 540 - img[3] / 2 + st[2], 1140 + st[3], st[0], st[1], st[4])

def scJ(t):  # selfie (25.60 - 30.95)
    heads = [dict(t0=25.60, t1=27.22, thin=('así que', [25.82, 26.04]), big=[('guarda', 26.26)], heavy=('este tutorial', [26.54, 26.70]), kind='rise', size=185),
             dict(t0=27.24, t1=28.20, big=[('compártelo', 27.24)], kind='whip', size=170),
             dict(t0=28.22, t1=29.04, big=[('compañeros', 28.22)], heavy=('de viaje', [28.64, 28.84]), kind='rise', size=165),
             dict(t0=30.34, t1=31.10, big=[('Cabany', 30.34)], kind='rise', size=200)]
    chests = [('con tus', 'chest', 27.86, 28.20), ('e inicia', 'chesti', 29.06, 29.64), ('a buscar', 'chest', 29.64, 30.04), ('en', 'chest', 30.04, 30.34)]
    def ex(c, t, ht, cy):
        line_icon_anim(c, t, 26.28, 27.15, 'bookmark', 860, ht + 230, 200)
        line_icon_anim(c, t, 27.26, 28.15, 'share', 215, ht + 230, 200)
        glass_pill(c, t, 30.45, 31.2, 'cabanypanama.com', 540, cy + 40, 54, '🌐')
    cuts = [(25.60, 1.00, 520), (26.26, 1.12, 515), (27.24, 1.0, 520), (28.22, 1.14, 515), (29.06, 1.03, 520), (30.34, 1.16, 515)]
    return talking(t, 'selfie', cuts, heads, chests, ex, src_t=min(t, 31.05))

def scK(t, under):  # end card on blurred background (ref ends on a blurred profile card)
    p = e_io(prog(t, 30.90, 31.35))
    base = gblur(scJ(min(t, 31.05)) if under is None else under, 4 + 26 * p)
    c = base * (1 - 0.45 * p) + np.array(GREEN_D, np.float32) / 255 * 0.45 * p
    if t >= 31.05:
        q = prog(t, 31.05, 31.5)
        card = end_card()
        paste(c, card, 540, 900 + 60 * (1 - e_out(q)), 0.9 + 0.1 * e_back(q, 1.6), 0, clamp(q * 3))
    return c

@functools.lru_cache(maxsize=1)
def end_card():
    from PIL import ImageDraw
    w, h = 760, 560
    ss = 2
    im = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], 56 * ss, fill=(255, 255, 255, 38), outline=(255, 255, 255, 90), width=3 * ss)
    im = im.resize((w, h), Image.LANCZOS); d = ImageDraw.Draw(im)
    lg = Image.open(f'{ROOT}/brand/logo-white.png').convert('RGBA'); lg = lg.crop(lg.getbbox())
    lw = 520; lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    im.alpha_composite(lg, ((w - lw) // 2, 70))
    d.text((w // 2, 300), 'Descubre, reserva y vive', font=ufont(500, False, 40), fill=(255, 255, 255, 255), anchor='mm')
    d.text((w // 2, 352), 'Tierras Altas', font=ufont(800, False, 48), fill=LIME_B + (255,), anchor='mm')
    f = ufont(700, False, 40); tw = f.getlength('cabanypanama.com')
    d.rounded_rectangle([w / 2 - tw / 2 - 40, 420, w / 2 + tw / 2 + 40, 500], 40, fill=LIME_B + (255,))
    d.text((w // 2, 461), 'cabanypanama.com', font=f, fill=GREEN_D + (255,), anchor='mm')
    im, _ = add_shadow(im, blur=30, off=(0, 20), alpha=0.35, pad=60)
    return pil_premul(im)

# ------------------------------------------------------------------ watermark
@functools.lru_cache(maxsize=2)
def url_text(mode):
    from PIL import ImageDraw
    im = Image.new('RGBA', (300, 40), (0, 0, 0, 0))
    col = (255, 255, 255, 255) if mode == 'light' else GREEN + (255,)
    ImageDraw.Draw(im).text((150, 20), 'cabanypanama.com', font=ufont(600, False, 24), fill=col, anchor='mm')
    return pil_premul(im)

def watermark(c):
    reg = c[120:230, 800:1060]
    lum = float((reg * np.array([0.3, 0.59, 0.11], np.float32)).sum(-1).mean())
    k = clamp((lum - 0.45) / 0.25)
    if k < 1: paste(c, logo('white', 170), 935, 160, 1.0, 0, 0.62 * (1 - k))
    if k > 0: paste(c, logo('green', 170), 935, 160, 1.0, 0, 0.62 * k)
    paste(c, url_text('dark' if k > 0.5 else 'light'), 935, 222, 1.0, 0, 0.55)

# ------------------------------------------------------------------ master
def scene(t):
    if t < 2.62: return scA(t)
    if t < 7.36: return scB(t)
    if t < 8.06: return scC(t)
    if t < 12.33: return scD(t)
    if t < 15.33: return scE(t)
    if t < 18.77: return scF(t)
    if t < 21.64: return scG(t)
    if t < 25.60: return scH(t)
    return scJ(t)

def flash_mix(img, k):
    if k <= 0.003: return img
    b = gblur(img, 2 + 26 * k)
    return np.clip((b * (1 - 0.55 * k) + 0.55 * k) * (1 + 0.5 * k), 0, 1)

def flash_tr(t, a_fn, b_fn, tc, half=0.12):
    if t < tc: return flash_mix(a_fn(t), e_in(prog(t, tc - half, tc)))
    return flash_mix(b_fn(t), 1 - e_out(prog(t, tc, tc + half * 1.2)))

def zoomblur_tr(t, a_fn, b_fn, tc, half=0.12, amt=0.32):
    if t < tc:
        p = e_in(prog(t, tc - half, tc)); return zoom_blur(shift_img(a_fn(t), 0, 0, 1 + 0.25 * p), amt * p)
    p = 1 - e_out(prog(t, tc, tc + half)); return zoom_blur(shift_img(b_fn(t), 0, 0, 1 + 0.18 * p), amt * p)

def whip(t, a_fn, b_fn, tc, half=0.10):
    p = prog(t, tc - half, tc + half); k = e_io(p)
    A = a_fn(min(t, tc - 1e-3)); B = b_fn(max(t, tc))
    A = shift_img(A, -W * k, 0); B = shift_img(B, W * (1 - k), 0)
    cut = int(W * (1 - k)); out = A.copy(); out[:, cut:] = B[:, cut:]
    return motion_blur(out, 120 * math.sin(math.pi * p), 0)

def frame(t):
    if 2.40 <= t <= 2.88: c = flash_tr(t, scA, scB, 2.62, half=0.22)
    elif 7.24 <= t <= 7.50: c = flash_tr(t, scB, scC, 7.36)
    elif 7.94 <= t <= 8.20: c = zoomblur_tr(t, scC, scD, 8.06)
    elif 12.23 <= t <= 12.43: c = whip(t, scD, scE, 12.33)
    elif 15.21 <= t <= 15.47: c = zoomblur_tr(t, scE, scF, 15.33)
    elif 25.48 <= t <= 25.76: c = flash_tr(t, scH, scJ, 25.60, half=0.14)
    else: c = scene(t)
    c = push_motion(c, t, [(17.70, 17.80, 60, 0), (20.28, 20.42, 90, 0), (22.36, 22.46, 90, 0), (24.16, 24.30, 80, 0)])
    if t >= 30.90:
        c = scK(t, c)
    if t < 31.0: watermark(c)
    return np.clip(c, 0, 1)

def push_motion(img, t, windows):
    for a, b, dx, dy in windows:
        if a <= t <= b:
            k = math.sin(math.pi * prog(t, a, b)); return motion_blur(img, dx * k, dy * k)
    return img

def save(c, path, q=93):
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
