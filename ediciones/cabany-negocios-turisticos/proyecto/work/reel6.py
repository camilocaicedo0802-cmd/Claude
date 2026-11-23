"""Cabany reel: 'Haz crecer tu negocio turístico' (tour businesses) — timeline + renderer.
Narration: Gemini TTS (male voice Puck). Visuals: animated recreations of the official business-registration graphics."""
import sys, os, json, math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
from lib import *
from fx3 import get, put, pop_state, caption, num_circle, cursor_img, pfont, STY
import ui6 as U
import ui5

WORDS = []
for seg in json.load(open(f'{ROOT}/voice/words.json')):
    for w in seg['words']: WORDS.append((w['w'].strip(), w['s'], w['e']))
def T_(i): return WORDS[i][1]
VOICE_END = WORDS[-1][2]
DUR = round(VOICE_END + 1.6, 2)
LIMEf = tuple(v / 255 for v in LIME_B)

# ------------------------------------------------------------------ helpers
@functools.lru_cache(maxsize=14)
def ui(name, *state):
    return pil_premul(getattr(U, name)(*state))

def card(c, arr, cam, op=1.0, shadow=0.42):
    cx, cy, dw, rx, ry, rz, ax, ay = cam
    h, w = arr.shape[:2]
    q = quad3d(w, h, cx, cy, dw / w, rx, ry, rz, ax, ay)
    if shadow > 0 and op > 0.05:
        sc = quad_scale(q, w, h)
        shadow_quad(c, q, blur=50 + 30 * sc, alpha=shadow * op, off=(14, 34))
    warp(c, arr, q, op)
    return q

def card_pt(q, arr, x, y):
    h, w = arr.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), q.astype(np.float32))
    p = M @ np.array([x * U.RS, y * U.RS, 1.0])
    return p[0] / p[2], p[1] / p[2]

def cam_kf(t, keys):
    return kf(t, [(k[0], k[1], k[2] if len(k) > 2 else e_io) for k in keys])

@functools.lru_cache(maxsize=8)
def photo_bg(img, blur):
    im = cover(Image.open(f'{ROOT}/site/img/{img}').convert('RGB'), W, H)
    a = np.asarray(im).astype(np.float32) / 255
    return cv2.GaussianBlur(a, (0, 0), blur) if blur else a

BLOBS = [(160, 420, 360, LIMEf, 0.16, 0.5), (940, 1300, 360, LIMEf, 0.12, 2.5), (880, 360, 220, LIMEf, 0.08, 4.2)]
def bg(t, photo=None, mix=0.30):
    c = grad_bg('dark').copy()
    if photo:
        c = c * (1 - mix) + photo_bg(photo, 26) * mix
    blobs(c, t, BLOBS)
    return c

def text_at(c, t, text, style, y, t0, t1, size=None, x=540, out=0.07):
    img = get(text, style, size)
    sz = size or STY[style]['size']
    while img[3] > 980 and sz > 40:
        sz = int(sz * 0.92); img = get(text, style, sz)
    ps = pop_state(t, t0, t1, out=out)
    if ps: put(c, img, x - img[3] / 2, y, ps[0], ps[1], ps[2])
    return img

@functools.lru_cache(maxsize=32)
def emoji_arr(ch, size): return pil_premul(emoji_img(ch, size))

def pop_item(c, t, t0, arr, x, y, t1=None, s=1.0, float_amp=6, rot=0):
    if t < t0: return
    p = prog(t, t0, t0 + 0.3)
    sc = s * (0.25 + 0.75 * e_back(p, 2.4)) if p < 1 else s
    op = clamp((t - t0) / 0.06)
    if t1 is not None and t >= t1:
        q = prog(t, t1, t1 + 0.18); sc *= 1 - 0.6 * e_in(q); op *= 1 - q
        if q >= 1: return
    paste(c, arr, x, y + float_amp * math.sin((t - t0) * 2.7 + x * 0.01), sc, rot, op)

def ripple(c, t, t0, x, y, col=(0.66, 0.91, 0.23)):
    p = prog(t, t0, t0 + 0.45)
    if p <= 0 or p >= 1: return
    ov = (c * 255).astype(np.uint8)
    cv2.circle(ov, (int(x), int(y)), int(18 + 70 * e_out(p)), tuple(int(v * 255) for v in col), max(2, int(9 * (1 - p))), cv2.LINE_AA)
    a = 1 - p
    c[:] = c * (1 - a) + ov.astype(np.float32) / 255 * a

def cursor(c, t, path, t_click=None):
    """path: [(t, x, y)] — cursor glides between points; pressed briefly at t_click."""
    if t < path[0][0] or t > path[-1][0]: return
    x, y = kf(t, [(pt[0], (pt[1], pt[2]), e_io) for pt in path])
    s = 1.25
    if t_click is not None and t_click <= t < t_click + 0.12: s = 1.05
    paste(c, cursor_img(), x + 18 * s, y + 22 * s, s, 0, 1.0)

def confetti(c, t, t0, cx, cy, n=46, seed=3):
    g = t - t0
    if g < 0 or g > 1.1: return
    rng = np.random.default_rng(seed)
    ov = (c * 255).astype(np.uint8)
    cols = [(169, 233, 58), (255, 255, 255), (248, 210, 74), (46, 139, 87)]
    for k in range(n):
        a = rng.uniform(0, 2 * math.pi); v = rng.uniform(420, 980)
        x = cx + math.cos(a) * v * g; y = cy + math.sin(a) * v * g + 1100 * g * g
        s = rng.uniform(7, 14); r = rng.uniform(0, 3.14) + g * 8
        pts = cv2.boxPoints(((x, y), (s * 2, s * 1.2), math.degrees(r))).astype(np.int32)
        cv2.fillConvexPoly(ov, pts, cols[k % 4], cv2.LINE_AA)
    a = 1 - clamp((g - 0.7) / 0.4)
    c[:] = c * (1 - a) + ov.astype(np.float32) / 255 * a

# ------------------------------------------------------------------ step header
@functools.lru_cache(maxsize=8)
def tracker(step):
    w, h = 460, 70
    im = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    xs = [40 + k * 76 for k in range(6)]
    d.line([(xs[0] * 2, 70), (xs[-1] * 2, 70)], fill=(255, 255, 255, 70), width=6)
    if step > 1: d.line([(xs[0] * 2, 70), (xs[step - 1] * 2, 70)], fill=LIME_B + (255,), width=6)
    f = pfont(800, False, 34)
    for k, x in enumerate(xs):
        n = k + 1; r = 30 if n == step else 22
        if n < step:
            d.ellipse([x * 2 - r * 2 // 2 * 1, 70 - r, x * 2 + r, 70 + r], fill=LIME_B + (255,))
            d.line([(x * 2 - 11, 70), (x * 2 - 3, 79), (x * 2 + 12, 61)], fill=GREEN + (255,), width=6)
        elif n == step:
            d.ellipse([x * 2 - r, 70 - r, x * 2 + r, 70 + r], fill=LIME_B + (255,))
            d.text((x * 2, 72), str(n), font=f, fill=GREEN + (255,), anchor='mm')
        else:
            d.ellipse([x * 2 - r, 70 - r, x * 2 + r, 70 + r], fill=GREEN_D + (255,), outline=(255, 255, 255, 110), width=4)
            d.text((x * 2, 72), str(n), font=f, fill=(255, 255, 255, 150), anchor='mm')
    return pil_premul(im.resize((w, h), Image.LANCZOS))

@functools.lru_cache(maxsize=8)
def badge(text):
    f = pfont(800, False, 30); tw = f.getlength(text)
    w, h = int(tw + 64), 62
    im = Image.new('RGBA', (w * 3, h * 3), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * 3 - 1, h * 3 - 1], h * 3 // 2, fill=LIME_B + (255,))
    im = im.resize((w, h), Image.LANCZOS)
    ImageDraw.Draw(im).text((w / 2, h / 2 + 1), text, font=f, fill=GREEN + (255,), anchor='mm')
    im, _ = add_shadow(im, blur=12, off=(0, 8), alpha=0.35, pad=30)
    return pil_premul(im)

@functools.lru_cache(maxsize=1)
def band_alpha():
    y = np.arange(H, dtype=np.float32)
    return np.clip(1 - (y - 470) / 110, 0, 1)[:, None, None]

def header(c, t, step, t0, t1, l1, l2):
    if not (t0 - 0.01 <= t < t1 + 0.1): return
    op = clamp((t - t0) / 0.15) * (1 - clamp((t - t1) / 0.1))
    a = band_alpha()[:600] * 0.96
    top = grad_bg('dark')[:600]
    c[:600] = c[:600] * (1 - a) + top * a
    paste(c, tracker(step), 540, 172, 1.0, 0, op)
    p = prog(t, t0 + 0.05, t0 + 0.35)
    paste(c, badge(f'PASO {step}'), 540, 262, 0.6 + 0.4 * e_back(p, 2.2), 0, op * clamp(p * 4))
    text_at(c, t, l1, 'wb', 372, t0 + 0.12, t1, 66)
    text_at(c, t, l2, 'g', 452, t0 + 0.22, t1, 80)


@functools.lru_cache(maxsize=4)
def logo_arr(kind, width):
    im = Image.open(f'{ROOT}/brand/logo-{kind}.png').convert('RGBA'); im = im.crop(im.getbbox())
    return pil_premul(im.resize((width, int(im.height * width / im.width)), Image.LANCZOS))

NOTIFS = [('¡Nueva reserva!', 'María (Panamá) · 2 noches'), ('¡Nueva reserva!', 'John (USA) · 3 noches'), ('¡Nueva reserva!', 'Familia Gómez · 5 huéspedes')]
@functools.lru_cache(maxsize=24)
def pill(text, emo=None, size=40, style='lime'):
    f = pfont(700, False, size); tw = f.getlength(text)
    h = int(size * 2.0); ic = int(h * 0.62) if emo else 0
    w = int(tw + h * 0.9 + (ic + h * 0.2 if emo else 0))
    bgc, fg = {'lime': (LIME_B, GREEN), 'white': (WHITE, GREEN), 'dark': (GREEN, WHITE)}[style]
    im = Image.new('RGBA', (w * 3, h * 3), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * 3 - 1, h * 3 - 1], h * 3 // 2, fill=bgc + (255,))
    im = im.resize((w, h), Image.LANCZOS); d = ImageDraw.Draw(im)
    x = h * 0.45
    if emo:
        e = emoji_img(emo, ic); im.alpha_composite(e, (int(x), int(h / 2 - e.height / 2))); x += ic + h * 0.2
    d.text((x, h / 2 + 1), text, font=f, fill=fg + (255,), anchor='lm')
    im, _ = add_shadow(im, blur=14, off=(0, 9), alpha=0.33, pad=34)
    return pil_premul(im)

@functools.lru_cache(maxsize=2)
def stamp():
    w, h = 560, 200
    im = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([12, 12, w * 2 - 12, h * 2 - 12], 40, outline=LIME_B + (255,), width=20)
    d.text((w, h + 4), 'GRATIS', font=pfont(900, False, 190), fill=LIME_B + (255,), anchor='mm')
    im = im.resize((w, h), Image.LANCZOS)
    return pil_premul(im)


# ================================================================== reel 6 scenes
@functools.lru_cache(maxsize=8)
def notif_arr(title, sub): return pil_premul(ui5.notif(title, sub))

@functools.lru_cache(maxsize=8)
def icon_disc(emo, size=150):
    im = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, size * 2 - 1, size * 2 - 1], fill=LIME_B + (255,))
    im = im.resize((size, size), Image.LANCZOS)
    e = emoji_img(emo, int(size * 0.56)); im.alpha_composite(e, (size // 2 - e.width // 2, size // 2 - e.height // 2))
    im, _ = add_shadow(im, blur=16, off=(0, 10), alpha=0.35, pad=36)
    return pil_premul(im)

def photo_scene(t, img, t0, l1, l2, big_t, emo, pan=1):
    s = 1.12 + 0.06 * (t - t0)
    c = photo_bg(img, 0)
    c = shift_img(c, pan * 40 * (t - t0), 0, s)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    c = c * (1 - 0.62 * np.clip((yy - 0.35) / 0.45, 0, 1)) * 0.92
    c = c * (1 - 0.35 * np.clip((0.18 - yy) / 0.18, 0, 1))
    text_at(c, t, l1, 'wb', 1200, t0, t0 + 9, 74)
    text_at(c, t, l2, 'big', 1350, big_t, t0 + 9, 140)
    pop_item(c, t, t0 + 0.05, icon_disc(emo, 170), 540, 960, s=1.0)
    return c

def sc_h1(t): return photo_scene(t, 'stock_agencia.jpg', 0.0, '¿Tienes una agencia', 'de viajes?', T_(2), '🧳', 1)
def sc_h2(t): return photo_scene(t, 'stock_tour.jpg', T_(5), '¿Eres', 'tour operador?', T_(6), '🗺️', -1)
def sc_h3(t): return photo_scene(t, 'stock_guia.jpg', T_(8), '¿Guía', 'turístico?', T_(8) + 0.1, '🥾', 1)
def sc_h4(t): return photo_scene(t, 'stock_transporte.jpg', T_(10), '¿O tienes', 'transporte?', T_(13), '🚐', -1)

NOTIFS6 = [('¡Nueva reserva!', 'Tour Volcán Barú · 4 personas'), ('¡Nueva reserva!', 'Traslado aeropuerto · 6 personas'), ('¡Nueva reserva!', 'Sendero Los Quetzales · 2 personas')]
def sc_intro(t):
    c = photo_bg('stock_montana.jpg', 0)
    c = shift_img(c, 0, -30 * (t - 5.8), 1.1 + 0.03 * (t - 5.8))
    c = c * 0.55 + grad_bg('dark') * 0.45
    if t < T_(24) - 0.05:
        text_at(c, t, 'Haz crecer', 'wb', 640, T_(16), T_(24) - 0.08, 84)
        text_at(c, t, 'tu negocio turístico', 'big', 790, T_(19), T_(24) - 0.08, 120)
        if t >= T_(22) - 0.05:
            p = prog(t, T_(22) - 0.05, T_(22) + 0.3)
            paste(c, logo_arr('white', 560), 540, 1080, 0.6 + 0.4 * e_back(p, 2.0), 0, clamp(p * 3))
        return c
    text_at(c, t, 'Forma parte de', 'wb', 440, T_(24), 12.42, 70)
    text_at(c, t, 'nuestra plataforma', 'g', 540, T_(27), 12.42, 92)
    for k, (a, b) in enumerate(NOTIFS6):
        tk = T_(28) + k * 0.5
        if t < tk: continue
        p = prog(t, tk, tk + 0.35)
        y = 820 + k * 175 + 40 * (1 - e_back(p, 1.6))
        paste(c, notif_arr(a, b), 540, y, 0.7 + 0.3 * e_back(p, 2), 0, clamp(p * 4))
    pop_item(c, t, T_(32), pill('Llega a más viajeros', '✈️', 46, 'lime'), 540, 1460)
    return c

def sc_how(t):
    c = bg(t)
    text_at(c, t, '¿Cómo', 'wb', 720, 12.42, 14.72, 86)
    text_at(c, t, 'funciona?', 'big', 870, T_(37), 14.72, 170)
    text_at(c, t, 'en 6 pasos', 'w', 1010, T_(42), 14.72, 62)
    for k in range(6):
        tk = T_(42) - 0.1 + 0.08 * k
        pop_item(c, t, tk, num_circle(k + 1, 130), 540 + (k - 2.5) * 160, 1240, t1=14.65)
    return c

def sc_s1(t):
    c = bg(t, 'stock_montana.jpg', 0.22)
    t_click = T_(53)
    if t < 19.3:
        url_n = int(round(16 * prog(t, T_(50) - 0.1, T_(51) + 0.5)))
        hover = T_(52) <= t < t_click
        pressed = t_click <= t < t_click + 0.16
        arr = ui('browser_home', url_n, hover or t >= t_click + 0.16, pressed)
        cam = cam_kf(t, [(14.72, (540, 1700, 760, 40, -22, 8, .5, .5), lin), (15.2, (540, 1100, 1020, 10, -12, -2, .5, .5), e_out5),
                         (17.9, (540, 1100, 1040, 6, 6, 0, .5, .5)), (18.4, (540, 1080, 1900, 2, -3, 0, .796, .135), e_io5),
                         (19.3, (540, 1080, 2000, 1, 2, 0, .796, .135))])
        q = card(c, arr, cam)
        bx, by = card_pt(q, arr, 796, 86)
        cursor(c, t, [(18.1, 760, 1500), (18.7, bx + 40, by + 16), (19.3, bx + 40, by + 16)], t_click)
        ripple(c, t, t_click, bx, by)
    else:
        w = [(19.30, 19.55, 13), (19.55, 19.85, 22), (19.85, 20.05, 9), (20.05, 20.30, 10)]
        typed = tuple(int(round(n * prog(t, a, b))) for a, b, n in w)
        active = next((k for k, (a, b, n) in enumerate(w) if a <= t < b + 0.02), -1)
        t_btn = 20.42
        arr = ui('account_card', typed, active, t_btn <= t < t_btn + 0.14, t >= t_btn + 0.14)
        p = prog(t, 19.3, 19.6)
        q = card(c, arr, (540, 1150 + 300 * (1 - e_out5(p)), 860, 6, 6 * math.sin(t - 19), 0, .5, .5), op=clamp(p * 4))
        bx, by = card_pt(q, arr, 230, 563)
        cursor(c, t, [(20.1, 820, 1700), (t_btn - 0.05, bx + 60, by), (20.8, bx + 60, by)], t_btn)
        ripple(c, t, t_btn, bx + 60, by)
    if T_(47) <= t < 18.2:
        pop_item(c, t, T_(47), pill('Registro gratis', '✅', 48, 'lime'), 540, 1660, t1=18.1)
    header(c, t, 1, 14.72, 20.76, 'Regístrate', 'gratis')
    return c

def sc_s2(t):
    c = bg(t, 'stock_tour.jpg', 0.2)
    checked = (False, t >= T_(70) + 0.05, t >= T_(71) + 0.05, t >= T_(73) + 0.05)
    hl = -1
    for k, ts, te in [(0, T_(68), T_(70)), (1, T_(70), T_(71)), (2, T_(71), T_(73)), (3, T_(73), T_(74))]:
        if ts <= t < te: hl = k
    t_btn = 28.45
    arr = ui('tipo_card', checked, t_btn <= t < t_btn + 0.15, hl)
    p = prog(t, 20.8, 21.3)
    ay = kf(t, [(20.8, 0.5, lin), (T_(68) - 0.2, 0.40, e_io), (T_(73), 0.62, e_io), (T_(74) + 0.4, 0.55, e_io), (28.2, 0.8, e_io)])
    q = card(c, arr, (540, 1150 + 400 * (1 - e_out5(p)), 900, 6, 7 * math.sin(t - 21), 0, .5, ay), op=clamp(p * 4))
    for k, tk in [(1, T_(70)), (2, T_(71)), (3, T_(73))]:
        x, y = card_pt(q, arr, 53, 276 + k * 98 + 42)
        ripple(c, t, tk + 0.05, x, y)
    if t >= T_(74):
        pop_item(c, t, T_(75), pill('Más de una categoría', '✅', 44, 'lime'), 540, 1720, t1=28.8, float_amp=3)
    bx, by = card_pt(q, arr, 408, 711)
    cursor(c, t, [(27.9, 700, 1650), (t_btn - 0.05, bx, by), (28.9, bx, by)], t_btn)
    header(c, t, 2, 20.8, 28.86, 'Selecciona', 'tu negocio')
    return c

DW = [(T_(86), 0.5, 19), (T_(91), 0.7, 40), (T_(93), 0.45, 17), (T_(96), 0.28, 14), (T_(96) + 0.3, 0.28, 20), (T_(96) + 0.6, 0.28, 14)]
LBL3 = [('🏪', 'Nombre del negocio'), ('📝', 'Descripción'), ('📍', 'Ubicación'), ('📞', 'Contacto')]
def sc_s3(t):
    c = bg(t, 'stock_guia.jpg', 0.2)
    typed = tuple(int(round(n * prog(t, a, a + d))) for a, d, n in DW)
    focus = -1
    for k, (a, d, n) in enumerate(DW):
        if a - 0.1 <= t < a + d + 0.15: focus = k
    arr = ui('datos_card', typed, focus, False)
    p = prog(t, 28.9, 29.4)
    keys = [(28.9, 0.42, lin), (29.9, 0.38, e_io)] + [(a - 0.2, U.datos_y(k) / 860, e_io) for k, (a, d, n) in enumerate(DW)]
    ay = kf(t, keys)
    dw = kf(t, [(28.9, 760, lin), (29.6, 960, e_out5)])
    card(c, arr, (540, 1170 + 400 * (1 - e_out5(p)), dw, 6, 6 * math.sin(t - 29), 0, .5, ay), op=clamp(p * 4))
    seq = [T_(86), T_(91), T_(93), T_(96)]
    for k, ts in enumerate(seq):
        t1 = seq[k + 1] - 0.05 if k + 1 < len(seq) else 34.8
        if ts - 0.05 <= t < t1 + 0.18:
            pop_item(c, t, ts - 0.05, pill(LBL3[k][1], LBL3[k][0], 44, 'lime'), 540, 1760, t1=t1, float_amp=3)
    header(c, t, 3, 28.9, 34.8, 'Completa', 'tus datos')
    return c

UP = [(T_(105) - 0.05, 0.55), (T_(107) + 0.1, 0.6), (T_(113) - 0.05, 0.5)]
def sc_s4(t):
    c = bg(t, 'stock_agencia.jpg', 0.2)
    progress = tuple(int(round(20 * prog(t, a, a + d))) for a, d in UP)
    arr = ui('cred_card', progress, False)
    p = prog(t, 34.84, 35.3)
    ay = kf(t, [(34.84, 0.5, lin), (UP[0][0] - 0.2, 0.47, e_io), (UP[2][0], 0.62, e_io)])
    q = card(c, arr, (540, 1150 + 400 * (1 - e_out5(p)), 920, 6, 6 * math.sin(t - 35), 0, .5, ay), op=clamp(p * 4))
    for k, (a, d) in enumerate(UP):
        x, y = card_pt(q, arr, 450, 274 + k * 118 + 52)
        ripple(c, t, a + d, x, y)
    labels = [('📄', 'RUC'), ('🪪', 'Licencia ATP'), ('🛡️', 'Seguro vigente')]
    for k, (a, d) in enumerate(UP):
        t1 = UP[k + 1][0] - 0.05 if k + 1 < 3 else 39.65
        if a <= t < t1 + 0.18:
            pop_item(c, t, a, pill(labels[k][1], labels[k][0], 46, 'lime'), 540, 1760, t1=t1, float_amp=3)
    header(c, t, 4, 34.84, 39.66, 'Sube tus', 'documentos')
    return c

def sc_s5(t):
    c = bg(t, 'stock_transporte.jpg', 0.2)
    t_send = T_(119) + 0.2
    if t < T_(120):
        n_ok = sum(t >= x for x in (39.95, 40.15, 40.35, 40.55))
        arr = ui('rev_card', n_ok, t_send <= t < t_send + 0.15, t >= t_send + 0.15)
        p = prog(t, 39.7, 40.15)
        ay = kf(t, [(39.7, 0.5, lin), (40.2, 0.55, e_io), (40.8, 0.82, e_io)])
        q = card(c, arr, (540, 1150 + 400 * (1 - e_out5(p)), 900, 6, 6 * math.sin(t - 40), 0, .5, ay), op=clamp(p * 4))
        bx, by = card_pt(q, arr, 260, 694)
        cursor(c, t, [(40.5, 820, 1750), (t_send - 0.05, bx + 60, by), (41.6, bx + 60, by)], t_send)
        ripple(c, t, t_send, bx + 60, by)
        if t >= t_send + 0.15:
            pp = prog(t, t_send + 0.15, t_send + 0.6)
            paste(c, emoji_arr('✈️', 120), bx - 80 + 900 * e_in(pp), by - 700 * e_in(pp), 1.0 - 0.4 * pp, -30, 1 - clamp((pp - 0.8) / 0.2))
    else:
        t_ok = T_(129)
        if t < t_ok:
            arr = ui('status6', 0, round(((t * 1.2) % 1) * 12) / 12); rx = 0
        else:
            pp = prog(t, t_ok, t_ok + 0.35); arr = ui('status6', 1, 0); rx = 80 * (1 - e_back(pp, 1.5))
        p = prog(t, T_(120), T_(120) + 0.4)
        card(c, arr, (540, 1100 + 300 * (1 - e_out5(p)), 860, 6 + rx, 6 * math.sin(t - 42), 0, .5, .5), op=clamp(p * 4))
        if T_(122) <= t < t_ok:
            pop_item(c, t, T_(122), pill('Revisión y verificación', '🔍', 42, 'white'), 540, 1660, t1=t_ok - 0.05)
        if t >= t_ok:
            confetti(c, t, t_ok, 540, 1000, 50, 7)
            pop_item(c, t, t_ok + 0.1, pill('¡Aprobado!', '🎉', 50, 'lime'), 540, 1660, t1=45.1)
    header(c, t, 5, 39.7, 45.12, 'Envía tu', 'solicitud')
    return c

FEAT = [(T_(155), '📅', 'Reservas', 230), (T_(157), '🗓️', 'Disponibilidad', 540), (T_(160), '👥', 'Clientes', 850)]
def sc_s6(t):
    c = bg(t, 'stock_montana.jpg', 0.2)
    if t < T_(137) - 0.05:
        text_at(c, t, '¡Comienza', 'wb', 900, 45.3, T_(137) - 0.08, 96)
        text_at(c, t, 'a crecer!', 'big', 1060, T_(134) + 0.12, T_(137) - 0.08, 170)
        pop_item(c, t, T_(134), emoji_arr('🚀', 200), 540, 1300, t1=T_(137) - 0.1)
        return c
    k = int(round(24 * prog(t, T_(137), T_(139) + 1.6)))
    arr = ui('dash_card', k)
    p = prog(t, T_(137), T_(137) + 0.45)
    ay = kf(t, [(T_(137), 0.5, lin), (T_(149) - 0.1, 0.5, lin), (T_(149) + 0.3, 0.22, e_io), (T_(153), 0.22, lin), (T_(153) + 0.4, 0.5, e_io)])
    dw = kf(t, [(T_(137), 600, lin), (T_(137) + 0.45, 720, e_out5), (T_(149) - 0.1, 740, lin), (T_(149) + 0.3, 1000, e_io), (T_(153), 1000, lin), (T_(153) + 0.4, 700, e_io)])
    card(c, arr, (540, 1100 + 400 * (1 - e_out5(p)), dw, 6, 7 * math.sin(t - 47), 0, .5, ay), op=clamp(p * 4))
    if T_(146) <= t < T_(153):
        pop_item(c, t, T_(149), pill('Tu panel de administración', '💻', 42, 'lime'), 540, 1740, t1=T_(153) - 0.05, float_amp=3)
    for ts, e, lab, x in FEAT:
        pop_item(c, t, ts, pill(lab, e, 32, 'lime'), x, 1700, float_amp=4)
    if t >= T_(161):
        text_at(c, t, 'desde un solo lugar', 'g', 1830, T_(161), 55.2, 64)
    header(c, t, 6, 45.16, 55.16, '¡Comienza', 'a crecer!')
    return c

def sc_cta(t):
    c = bg(t, 'stock_montana.jpg', 0.28)
    text_at(c, t, 'Comienza tu', 'wb', 560, T_(165), 57.8, 84)
    text_at(c, t, 'registro hoy', 'big', 700, T_(167), 57.8, 150)
    n = int(round(16 * prog(t, T_(170) - 0.1, T_(171) + 0.3)))
    arr = ui('browser_home', n, t >= 57.45, 57.45 <= t < 57.6)
    p = prog(t, T_(165), T_(165) + 0.4)
    card(c, arr, (540, 1260 + 300 * (1 - e_out5(p)), 960, 8, -8 + 6 * math.sin(t - 55), 0, .5, .5), op=clamp(p * 4))
    return c

def sc_end(t):
    c = bg(t, 'stock_montana.jpg', 0.2)
    p = prog(t, T_(172), T_(172) + 0.36)
    paste(c, logo_arr('white', 640), 540, 760, 0.6 + 0.4 * e_back(p, 1.8), 0, clamp(p * 3))
    for wd, wi, y, st in [('Descubre', 173, 990, 'wb'), ('reserva', 174, 1090, 'wb'), ('y vive Panamá', 176, 1200, 'g')]:
        text_at(c, t, wd, st, y, T_(wi), DUR + 1, 72 if st == 'wb' else 92)
    if t >= T_(177) + 0.2: pop_item(c, t, T_(177) + 0.2, pill('cabanypanama.com', '🌐', 44, 'lime'), 540, 1400, float_amp=3)
    return c

SCENES = [(0.0, sc_h1), (T_(5), sc_h2), (T_(8), sc_h3), (T_(10), sc_h4), (5.80, sc_intro), (12.42, sc_how), (14.72, sc_s1),
          (20.80, sc_s2), (28.90, sc_s3), (34.84, sc_s4), (39.70, sc_s5), (45.16, sc_s6), (55.20, sc_cta), (57.84, sc_end)]
CUTS = [s[0] for s in SCENES[1:]]
END_T = 57.84

def scene(t):
    fn = SCENES[0][1]
    for t0, f in SCENES:
        if t >= t0: fn = f
    return fn(t)

def frame(t):
    c = None
    for k, tc in enumerate(CUTS):
        if abs(t - tc) < 0.12:
            if k % 3 == 1:  # whip
                p = prog(t, tc - 0.12, tc + 0.12); kk = e_io(p)
                A = scene(min(t, tc - 1e-3)); B = scene(max(t, tc))
                A = shift_img(A, -W * kk, 0); B = shift_img(B, W * (1 - kk), 0)
                cut = int(W * (1 - kk)); c = A.copy(); c[:, cut:] = B[:, cut:]
                c = motion_blur(c, 120 * math.sin(math.pi * p), 0)
            elif k % 3 == 0:  # zoom blur
                if t < tc: p = e_in(prog(t, tc - 0.12, tc)); c = zoom_blur(shift_img(scene(t), 0, 0, 1 + 0.2 * p), 0.3 * p)
                else: p = 1 - e_out(prog(t, tc, tc + 0.12)); c = zoom_blur(shift_img(scene(t), 0, 0, 1 + 0.15 * p), 0.3 * p)
            else:  # flash
                kk = 1 - abs(t - tc) / 0.12
                c = scene(t); b = gblur(c, 2 + 24 * kk); c = np.clip((b * (1 - 0.5 * kk) + 0.5 * kk) * (1 + 0.4 * kk), 0, 1)
            break
    if c is None: c = scene(t)
    if t < END_T - 0.2:
        paste(c, logo_arr('white', 150), 950, 76, 1.0, 0, 0.55)
    if t > DUR - 0.3: c = c * clamp((DUR - t) / 0.3)
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
