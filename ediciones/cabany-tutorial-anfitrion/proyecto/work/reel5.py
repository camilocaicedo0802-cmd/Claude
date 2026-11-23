"""Cabany tutorial reel: 'Publica tu cabaña y conviértela en ingresos' — timeline + renderer.
Narration: Gemini TTS (voice Sulafat). Visuals: animated recreations of the official host-flow graphics."""
import sys, os, json, math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
from lib import *
from fx3 import get, put, pop_state, caption, num_circle, cursor_img, pfont, STY
import ui5 as U

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
    xs = [50 + k * 90 for k in range(5)]
    d.line([(xs[0] * 2, 70), (xs[-1] * 2, 70)], fill=(255, 255, 255, 70), width=6)
    if step > 1: d.line([(xs[0] * 2, 70), (xs[step - 1] * 2, 70)], fill=LIME_B + (255,), width=6)
    f = pfont(800, False, 34)
    for k, x in enumerate(xs):
        n = k + 1; r = 30 if n == step else 24
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

# ------------------------------------------------------------------ scenes
def sc_hook(t):
    s = 1.12 + 0.05 * t
    c = photo_bg('caba_a_alpina.webp', 0)
    c = shift_img(c, -30 * t, 0, s)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    c = c * (1 - 0.55 * np.clip((yy - 0.25) / 0.5, 0, 1)) * 0.92
    text_at(c, t, '¿Tienes una', 'wb', 760, T_(0), T_(3) - 0.05, 78)
    text_at(c, t, 'cabaña?', 'big', 900, T_(2), T_(3) - 0.05, 170)
    text_at(c, t, 'Conviértela en', 'wb', 760, T_(3), 3.54, 74)
    text_at(c, t, 'ingresos', 'big', 900, T_(5), 3.54, 170)
    for k, (e, x, y) in enumerate([('💵', 200, 560), ('💰', 870, 620), ('💵', 860, 1120), ('🪙', 220, 1080)]):
        pop_item(c, t, T_(5) + 0.06 * k, emoji_arr(e, 150), x, y, t1=3.45)
    if t >= T_(7) - 0.05:
        p = prog(t, T_(7) - 0.05, T_(7) + 0.3)
        lg = logo_arr('white', 520)
        paste(c, lg, 540, 1100, 0.6 + 0.4 * e_back(p, 2.0), 0, clamp(p * 3))
    return c

@functools.lru_cache(maxsize=4)
def logo_arr(kind, width):
    im = Image.open(f'{ROOT}/brand/logo-{kind}.png').convert('RGBA'); im = im.crop(im.getbbox())
    return pil_premul(im.resize((width, int(im.height * width / im.width)), Image.LANCZOS))

NOTIFS = [('¡Nueva reserva!', 'María (Panamá) · 2 noches'), ('¡Nueva reserva!', 'John (USA) · 3 noches'), ('¡Nueva reserva!', 'Familia Gómez · 5 huéspedes')]
def sc_intro(t):
    c = bg(t, 'lcs_1.webp')
    t0 = 3.54
    text_at(c, t, 'Publica tu', 'wb', 330, T_(11), 8.9, 70)
    text_at(c, t, 'alojamiento', 'g', 420, T_(13), 8.9, 96)
    cam = cam_kf(t, [(t0, (540, 1400, 520, 30, -20, 6, .5, .5), lin), (t0 + 0.5, (540, 850, 640, 8, -10, -2, .5, .5), e_out5), (8.95, (540, 830, 660, 4, 8, 1, .5, .5))])
    q = card(c, ui('status_card', 1, 0), cam)
    for k, (a, b) in enumerate(NOTIFS):
        tk = T_(17) + k * 0.5
        if t < tk: continue
        p = prog(t, tk, tk + 0.35)
        y = 1290 + k * 175 + 40 * (1 - e_back(p, 1.6))
        paste(c, ui('notif', a, b), 540, y, 1.0 * (0.7 + 0.3 * e_back(p, 2)), 0, clamp(p * 4))
    if t >= T_(25) - 0.05:
        p = prog(t, T_(25) - 0.05, T_(25) + 0.3)
        paste(c, pill('Turistas en Panamá', '🇵🇦'), 540, 560, 0.5 + 0.5 * e_back(p, 2.2), 0, clamp(p * 3))
    return c

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

def sc_steps(t):
    c = bg(t)
    text_at(c, t, '¿Cómo', 'wb', 720, 8.95, 11.14, 86)
    text_at(c, t, 'funciona?', 'big', 870, 9.05, 11.14, 170)
    text_at(c, t, 'paso a paso', 'w', 1010, T_(30), 11.14, 62)
    for k in range(5):
        tk = T_(30) + 0.12 * k
        pop_item(c, t, tk, num_circle(k + 1, 150), 540 + (k - 2) * 180, 1240, t1=11.05)
    return c

def sc_s1(t):
    c = bg(t, 'caba_a_alpina.webp', 0.22)
    url_n = int(round(16 * prog(t, T_(37) - 0.1, T_(38) + 0.5)))
    t_click = T_(43)
    hover = T_(42) - 0.3 <= t < t_click
    pressed = t_click <= t < t_click + 0.16
    arr = ui('browser_home', url_n, hover or t >= t_click + 0.16, pressed)
    cam = cam_kf(t, [(11.14, (540, 1700, 760, 40, -22, 8, .5, .5), lin), (11.6, (540, 1100, 1020, 10, -12, -2, .5, .5), e_out5),
                     (13.4, (540, 1100, 1040, 6, 6, 0, .5, .5)), (14.1, (540, 1060, 2000, 2, -3, 0, .80, .135), e_io5),
                     (15.6, (540, 1060, 2100, 1, 2, 0, .80, .135)), (16.3, (540, 1080, 1000, 6, -8, 0, .5, .5), e_io5), (17.48, (540, 1080, 1040, 4, 6, 0, .5, .5))])
    q = card(c, arr, cam)
    bx, by = card_pt(q, arr, 847, 86)
    cursor(c, t, [(13.9, 760, 1500), (14.75, bx + 70, by + 18), (15.6, bx + 70, by + 18)], t_click)
    ripple(c, t, t_click, bx, by)
    if t >= 16.3:
        pop_item(c, t, 16.3, pill('Cuenta de anfitrión', '🏡'), 540, 1500, t1=17.4)
    header(c, t, 1, 11.14, 17.42, 'Regístrate', 'como anfitrión')
    return c

def type_n(t, t0, t1, n): return int(round(n * prog(t, t0, t1)))

def sc_s2(t):
    c = bg(t, 'lcs_2.webp', 0.2)
    wins = [(T_(55), T_(55) + 0.5), (T_(56), T_(56) + 0.5), (T_(57), T_(57) + 0.45), (T_(60), T_(61) + 0.4)]
    typed = tuple(type_n(t, a, b, len(U.FORM_FIELDS[k][2])) for k, (a, b) in enumerate(wins))
    active = -1
    for k, (a, b) in enumerate(wins):
        if a - 0.15 <= t < b + 0.05: active = k
    if t < wins[0][0] - 0.15 and t >= 18.3: active = 0
    t_btn = T_(63)
    pressed = t_btn <= t < t_btn + 0.15
    done = t >= t_btn + 0.15
    arr = ui('form_card', typed, active, pressed, done)
    fy = [130 + 41 + k * 102 for k in range(4)]
    target = 340 if active < 0 else fy[active]
    if t >= T_(62): target = 560
    ay = kf(t, [(17.48, 0.5, lin), (18.4, 0.42, e_io)] + [(a - 0.12, fy[k] / 640, e_io) for k, (a, b) in enumerate(wins)] + [(T_(62) - 0.1, fy[3] / 640, lin), (T_(62) + 0.2, 560 / 640, e_io)])
    dw = kf(t, [(17.48, 600, lin), (17.95, 820, e_out5), (18.9, 840, lin), (19.15, 1060, e_io), (22.0, 1080, lin), (22.4, 1000, e_io)])
    ry = 8 * math.sin((t - 17.48) * 0.9)
    q = card(c, arr, (540, 1080 if t > 18.9 else kf(t, [(17.48, 1500, lin), (17.95, 1060, e_out5)]), dw, 6, ry, 0, .5, ay))
    bx, by = card_pt(q, arr, 230, 563)
    cursor(c, t, [(T_(62) - 0.2, 800, 1550), (t_btn - 0.05, bx + 60, by), (23.0, bx + 60, by)], t_btn)
    ripple(c, t, t_btn, bx + 60, by)
    if done: confetti(c, t, t_btn + 0.15, bx, by, 30, 5)
    header(c, t, 2, 17.48, 22.98, 'Completa', 'tus datos')
    return c

SEC_T = [('photos', T_(72)), ('loc', T_(74)), ('cap', T_(76)), ('serv', T_(78)), ('price', T_(80)), ('avail', T_(83))]
LABELS = [('📸', 'Fotografías'), ('📍', 'Ubicación'), ('👥', 'Capacidad'), ('✅', 'Servicios'), ('💲', 'Precio'), ('📅', 'Disponibilidad')]
def sc_s3(t):
    c = bg(t, 'lcs_3.webp', 0.2)
    n_ph = min(4, int(max(0, t - T_(72) + 0.05) / 0.22) + (1 if t >= T_(72) else 0)) if t >= T_(72) else 0
    loc_n = type_n(t, T_(74), T_(74) + 0.7, len(U.LOC))
    cap_on = t >= T_(76) + 0.2
    n_serv = min(6, int(max(0, t - T_(78)) / 0.11) + 1) if t >= T_(78) else 0
    price_n = type_n(t, T_(80), T_(80) + 0.55, len(U.PRICE))
    n_av = int(round(len(U.AVAIL) * prog(t, T_(83), T_(83) + 0.75)))
    focus = None
    for k, (sec, ts) in enumerate(SEC_T):
        if t >= ts - 0.2: focus = sec
    arr = ui('panel_card', n_ph, loc_n, cap_on, n_serv, price_n, n_av, focus or '', False)
    H_log = 1095
    keys = [(23.02, 0.42, lin), (24.3, 0.30, e_io)] + [(ts - 0.25, U.panel_y(sec) / H_log, e_io) for sec, ts in SEC_T]
    ay = kf(t, keys)
    dw = kf(t, [(23.02, 560, lin), (23.5, 820, e_out5), (24.4, 880, lin), (24.8, 1060, e_io), (30.5, 1080, lin)])
    ry = 7 * math.sin((t - 23) * 0.8); rx = 6
    cy = kf(t, [(23.02, 1600, lin), (23.5, 1120, e_out5)])
    card(c, arr, (540, cy, dw, rx, ry, 0, .5, ay))
    for k, (sec, ts) in enumerate(SEC_T):
        t1 = SEC_T[k + 1][1] - 0.05 if k + 1 < len(SEC_T) else 30.45
        if ts - 0.05 <= t < t1 + 0.18:
            pop_item(c, t, ts - 0.05, pill(LABELS[k][1], LABELS[k][0], 44, 'lime'), 540, 1720, t1=t1, float_amp=3)
    header(c, t, 3, 23.02, 30.5, 'Publica', 'tu cabaña')
    return c

def sc_s4(t):
    c = bg(t, 'lcs_4.webp', 0.2)
    oks = [T_(88), T_(89) + 0.05, T_(90) + 0.1, T_(90) + 0.32]
    n_ok = sum(t >= x for x in oks)
    t_send = T_(92)
    pressed = t_send <= t < t_send + 0.15
    sent = t >= t_send + 0.15
    arr = ui('review_card', n_ok, pressed, sent)
    ay = kf(t, [(30.56, 0.5, lin), (31.4, 0.46, e_io), (32.45, 0.78, e_io)])
    dw = kf(t, [(30.56, 560, lin), (31.0, 840, e_out5), (32.3, 860, lin), (32.65, 1040, e_io)])
    cy = kf(t, [(30.56, 1600, lin), (31.0, 1090, e_out5)])
    q = card(c, arr, (540, cy, dw, 6, 6 * math.sin(t - 30.5), 0, .5, ay))
    bx, by = card_pt(q, arr, 240, 562)
    cursor(c, t, [(32.2, 850, 1650), (t_send - 0.05, bx + 70, by), (34.4, bx + 70, by)], t_send)
    ripple(c, t, t_send, bx + 70, by)
    if t >= t_send + 0.15:  # paper plane flies away
        p = prog(t, t_send + 0.15, t_send + 0.9)
        x = bx - 120 + 900 * e_in(p); y = by - 700 * e_in(p) - 60 * math.sin(p * math.pi)
        paste(c, emoji_arr('✈️', 120), x, y, 1.0 - 0.4 * p, -30, 1 - clamp((p - 0.8) / 0.2))
    header(c, t, 4, 30.56, 34.48, 'Revisa y envía', 'tu solicitud')
    return c

def sc_s5(t):
    c = bg(t, 'lcs_5.webp', 0.2)
    t_ok = T_(107)
    t_grid = T_(110) - 0.1
    if t < t_grid:
        if t < t_ok:
            arr = ui('status_card', 0, round(((t * 1.4) % 1) * 12) / 12)
            rx = 0
        else:
            p = prog(t, t_ok, t_ok + 0.35)
            arr = ui('status_card', 1, 0); rx = 80 * (1 - e_back(p, 1.5))
        dw = kf(t, [(34.52, 520, lin), (35.0, 860, e_out5), (37.3, 900, lin)])
        cy = kf(t, [(34.52, 1600, lin), (35.0, 1080, e_out5)])
        q = card(c, arr, (540, cy, dw, 6 + rx, 6 * math.sin(t - 34.5), 0, .5, .5))
        if t >= t_ok: confetti(c, t, t_ok, 540, 900, 50, 7)
        if 35.6 <= t < t_ok:
            pop_item(c, t, T_(101), pill('Revisión del equipo', '🔍', 40, 'white'), 540, 1460, t1=t_ok - 0.05)
    else:
        show = t >= T_(110) + 0.15
        arr = ui('listing_grid', show)
        p = prog(t, t_grid, t_grid + 0.4)
        q = card(c, arr, (540, 1090, 700 + 180 * e_out5(p), 8, -10 + 16 * e_io(prog(t, t_grid, 40.1)), 0, .5, .5), op=clamp(p * 4))
        if show:
            x, y = card_pt(q, arr, 135, 476)
            ripple(c, t, T_(110) + 0.15, x, y)
            pop_item(c, t, T_(111), pill('¡Ya estás en la plataforma!', '🎉', 38, 'lime'), 540, 1700, t1=40.05)
    header(c, t, 5, 34.52, 40.08, 'Verificamos', 'y aprobamos')
    return c

def sc_pay(t):
    c = bg(t, 'lcs_1.webp', 0.16)
    if t < T_(119) - 0.05:
        text_at(c, t, '¿Cómo recibes', 'wb', 760, T_(114), T_(119) - 0.08, 80)
        text_at(c, t, 'tus pagos?', 'big', 900, T_(117), T_(119) - 0.08, 150)
        pop_item(c, t, T_(118), emoji_arr('💳', 220), 540, 1190, t1=T_(119) - 0.1)
        return c
    if t < T_(126) - 0.05:
        text_at(c, t, 'CABANY', 'g', 600, T_(119), T_(126) - 0.08, 104)
        text_at(c, t, 'gestiona el cobro', 'wb', 700, T_(120), T_(126) - 0.08, 64)
        stage = 1 if t >= T_(122) else 0
        p = prog(t, T_(119), T_(119) + 0.4)
        card(c, ui('booking_card', stage), (540, 1200 + 300 * (1 - e_out5(p)), 940, 6, 6 * math.sin(t - 41), 0, .5, .5), op=clamp(p * 4))
        if stage: ripple(c, t, T_(122), 540, 1360)
        return c
    if t < T_(138) - 0.05:
        text_at(c, t, 'Cortes de pago', 'wb', 520, T_(126), T_(138) - 0.08, 72)
        text_at(c, t, 'todos los lunes', 'g', 615, T_(132), T_(138) - 0.08, 92)
        n_mon = min(5, int(max(0, t - T_(132)) / 0.16) + 1) if t >= T_(132) else 0
        p = prog(t, T_(126), T_(126) + 0.4)
        card(c, ui('calendar_card', n_mon), (540, 1260 + 300 * (1 - e_out5(p)), 940, 6, -6 * math.sin(t - 43.6), 0, .5, .5), op=clamp(p * 4))
        return c
    # transaction timeline
    text_at(c, t, 'Hasta', 'wb', 520, T_(141), 51.6, 72)
    text_at(c, t, '4 días hábiles' if False else '4 días', 'big', 660, T_(142), 51.6, 150)
    text_at(c, t, 'para hacerse efectivas', 'w', 745, T_(145), 51.6, 54)
    pq = int(round(60 * prog(t, T_(138), T_(155) + 0.2)))
    nodes = 1 + (t >= T_(140)) + (t >= T_(143)) + (t >= T_(155))
    p = prog(t, T_(138), T_(138) + 0.4)
    q = card(c, ui('timeline_card', pq, nodes), (540, 1250 + 300 * (1 - e_out5(p)), 980, 6, 5 * math.sin(t - 46), 0, .5, .5), op=clamp(p * 4))
    if t >= T_(155):
        x, y = card_pt(q, ui('timeline_card', pq, nodes), 430, 128)
        ripple(c, t, T_(155), x, y)
        pop_item(c, t, T_(155) + 0.05, pill('Pago disponible', '✅', 42, 'lime'), 540, 1720, t1=51.6)
    return c

@functools.lru_cache(maxsize=2)
def stamp():
    w, h = 560, 200
    im = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([12, 12, w * 2 - 12, h * 2 - 12], 40, outline=LIME_B + (255,), width=20)
    d.text((w, h + 4), 'GRATIS', font=pfont(900, False, 190), fill=LIME_B + (255,), anchor='mm')
    im = im.resize((w, h), Image.LANCZOS)
    return pil_premul(im)

def sc_free(t):
    c = bg(t)
    text_at(c, t, 'Y lo mejor…', 'w', 470, T_(156), 54.08, 64)
    text_at(c, t, 'Publicar tu propiedad', 'wb', 640, T_(159), 54.08, 70)
    text_at(c, t, 'no tiene costo', 'big', 790, T_(162), 54.08, 130)
    if t >= T_(162) + 0.1:
        p = prog(t, T_(162) + 0.1, T_(162) + 0.35)
        s = 2.2 - 1.2 * e_out(p)
        paste(c, stamp(), 540, 1130, s, -8, clamp(p * 3))
        if p >= 1: confetti(c, t, T_(162) + 0.35, 540, 1130, 40, 11)
    return c

def sc_guests(t):
    c = bg(t)
    # top: the cabin (you), bottom: guests (us)
    p = prog(t, 54.08, 54.5)
    top = photo_bg('caba_a_alpina.webp', 0)
    ph = cv2.resize(top, (900, 1600))[300:860]
    arr = np.concatenate([ph, np.ones(ph.shape[:2] + (1,), np.float32)], -1)
    m = np.asarray(rounded_mask(900, 560, 46)).astype(np.float32)[..., None] / 255
    arr = arr * m
    q = card(c, arr, (540, 700 - 200 * (1 - e_out5(p)), 940, 6, -6, 0, .5, .5), op=clamp(p * 4))
    text_at(c, t, 'Tú tienes la cabaña', 'wb', 1080, T_(165), 57.0, 60)
    text_at(c, t, 'Nosotros te conseguimos', 'wb', 1250, T_(169), 57.0, 60)
    text_at(c, t, 'huéspedes', 'big', 1395, T_(174), 57.0, 140)
    for k, e in enumerate(['🧳', '👪', '🧑‍🤝‍🧑', '🎒']):
        pop_item(c, t, T_(171) + 0.12 * k, emoji_arr(e, 130), 230 + k * 210, 1620, t1=57.0)
    return c

def sc_cta(t):
    c = bg(t, 'caba_a_alpina.webp', 0.28)
    text_at(c, t, 'Regístrate', 'big', 640, T_(175), 59.6, 150)
    text_at(c, t, 'hoy', 'wb', 760, T_(176), 59.6, 80)
    n = type_n(t, T_(178) - 0.1, T_(179) + 0.3, 16)
    arr = ui('browser_home', n, t >= 58.95, 58.95 <= t < 59.1)
    p = prog(t, T_(175), T_(175) + 0.4)
    q = card(c, arr, (540, 1250 + 300 * (1 - e_out5(p)), 960, 8, -8 + 6 * math.sin(t - 57), 0, .5, .5), op=clamp(p * 4))
    return c

def sc_end(t):
    c = bg(t, 'caba_a_alpina.webp', 0.18)
    p = prog(t, 59.64, 60.0)
    paste(c, logo_arr('white', 640), 540, 760, 0.6 + 0.4 * e_back(p, 1.8), 0, clamp(p * 3))
    for wd, wi, y, st in [('Descubre', 181, 990, 'wb'), ('reserva', 182, 1090, 'wb'), ('y vive Panamá', 184, 1200, 'g')]:
        text_at(c, t, wd, st, y, T_(wi), DUR + 1, 72 if st == 'wb' else 92)
    if t >= 61.9: pop_item(c, t, 61.9, pill('cabanypanama.com', '🌐', 44, 'lime'), 540, 1400, float_amp=3)
    return c

SCENES = [(0.0, sc_hook), (3.54, sc_intro), (8.95, sc_steps), (11.14, sc_s1), (17.48, sc_s2), (23.02, sc_s3), (30.56, sc_s4),
          (34.52, sc_s5), (40.12, sc_pay), (51.66, sc_free), (54.12, sc_guests), (57.06, sc_cta), (59.64, sc_end)]
CUTS = [s[0] for s in SCENES[1:]]

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
    if t < 59.4:
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
