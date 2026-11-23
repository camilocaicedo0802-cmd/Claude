"""Crisp, animatable recreations of the Cabany host flow (based on the client's official step graphics).
Every builder returns a PIL RGBA image rendered at RS x its logical size; results are cached by state."""
import math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from lib import ROOT, rgb, GREEN, GREEN_D, LIME_B, WHITE, INK, rounded_mask, cover, add_shadow, emoji_img

RS = 2
G_DARK = rgb('0B4A33')
G_MID = rgb('2E8B57')
G_LIGHT = rgb('E8F5E4')
G_LINE = rgb('D5E3D2')
GREY = rgb('6B7280')
GREY_L = rgb('9CA3AF')
BG = rgb('F6F8F5')

@functools.lru_cache(maxsize=128)
def mf(w, size):
    return ImageFont.truetype(f'{ROOT}/fonts/Montserrat-{w}.ttf', int(round(size * RS)))

def S(v): return int(round(v * RS))

class Canvas:
    def __init__(self, w, h, bg=WHITE + (255,), radius=28):
        self.w, self.h = w, h
        self.im = Image.new('RGBA', (S(w), S(h)), (0, 0, 0, 0))
        m = rounded_mask(S(w), S(h), S(radius)) if radius else None
        base = Image.new('RGBA', (S(w), S(h)), bg)
        self.im.paste(base, (0, 0), m)
        self.d = ImageDraw.Draw(self.im)
    def rr(self, box, r, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        self.d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], S(r), fill=fill, outline=outline, width=S(width) if outline else 0)
    def text(self, xy, s, w=600, size=14, fill=INK, anchor='la'):
        self.d.text((S(xy[0]), S(xy[1])), s, font=mf(w, size), fill=fill, anchor=anchor)
    def tlen(self, s, w=600, size=14):
        return mf(w, size).getlength(s) / RS
    def line(self, pts, fill, width=2):
        self.d.line([(S(x), S(y)) for x, y in pts], fill=fill, width=S(width), joint='curve')
    def ellipse(self, box, fill=None, outline=None, width=1):
        self.d.ellipse([S(v) for v in box], fill=fill, outline=outline, width=S(width) if outline else 0)
    def photo(self, img, box, r=12):
        x0, y0, x1, y1 = box
        ph = cover(Image.open(f'{ROOT}/site/img/{img}').convert('RGB'), S(x1 - x0), S(y1 - y0))
        self.im.paste(ph, (S(x0), S(y0)), rounded_mask(S(x1 - x0), S(y1 - y0), S(r)))
    def logo(self, kind, x, y, width):
        lg = _logo(kind, S(width)); self.im.alpha_composite(lg, (S(x), S(y)))

@functools.lru_cache(maxsize=8)
def _logo(kind, width):
    im = Image.open(f'{ROOT}/brand/logo-{kind}.png').convert('RGBA'); im = im.crop(im.getbbox())
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)

# ------------------------------------------------------------------ tiny line icons
def icon(c, name, cx, cy, size, col, width=2.2):
    s = size / 2
    L = lambda pts: c.line([(cx + x * s, cy + y * s) for x, y in pts], col, width)
    E = lambda x0, y0, x1, y1: c.ellipse((cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s), outline=col, width=width)
    if name == 'user':
        E(-.4, -.95, .4, -.15); L([(-.85, .9), (-.7, .35), (-.3, .1), (.3, .1), (.7, .35), (.85, .9)])
    elif name == 'mail':
        c.rr((cx - s * .95, cy - s * .65, cx + s * .95, cy + s * .65), s * .15, outline=col, width=width); L([(-.95, -.6), (0, .1), (.95, -.6)])
    elif name == 'phone':
        c.rr((cx - s * .5, cy - s * .95, cx + s * .5, cy + s * .95), s * .2, outline=col, width=width); L([(-.15, .7), (.15, .7)])
    elif name == 'lock':
        c.rr((cx - s * .75, cy - s * .1, cx + s * .75, cy + s * .9), s * .15, outline=col, width=width)
        L([(-.45, -.1), (-.45, -.45), (-.3, -.8), (0, -.92), (.3, -.8), (.45, -.45), (.45, -.1)])
    elif name == 'pin':
        L([(0, .95), (-.6, .1), (-.7, -.35), (-.45, -.8), (0, -.95), (.45, -.8), (.7, -.35), (.6, .1), (0, .95)]); E(-.22, -.55, .22, -.11)
    elif name == 'users':
        E(-.75, -.9, -.15, -.3); E(.15, -.9, .75, -.3); L([(-1, .8), (-.85, .1), (-.45, -.1), (-.1, .1), (0, .8)]); L([(0, .8), (.1, .1), (.45, -.1), (.85, .1), (1, .8)])
    elif name == 'tag':
        L([(-.9, -.15), (-.15, -.9), (.85, -.9), (.85, .1), (.1, .85), (-.9, -.15)]); E(.35, -.6, .6, -.35)
    elif name == 'cal':
        c.rr((cx - s * .9, cy - s * .75, cx + s * .9, cy + s * .9), s * .15, outline=col, width=width); L([(-.9, -.3), (.9, -.3)]); L([(-.45, -.95), (-.45, -.6)]); L([(.45, -.95), (.45, -.6)])
    elif name == 'camera':
        c.rr((cx - s * .95, cy - s * .55, cx + s * .95, cy + s * .8), s * .15, outline=col, width=width); E(-.35, -.3, .35, .4); L([(-.35, -.55), (-.2, -.8), (.2, -.8), (.35, -.55)])
    elif name == 'home':
        L([(-.95, -.05), (0, -.9), (.95, -.05)]); L([(-.7, -.25), (-.7, .9), (.7, .9), (.7, -.25)])
    elif name == 'check':
        L([(-.65, .05), (-.2, .5), (.7, -.5)])
    elif name == 'send':
        L([(-.9, -.1), (.9, -.85), (.3, .9), (.0, .2), (-.9, -.1)]); L([(.0, .2), (.9, -.85)])
    elif name == 'clock':
        E(-.9, -.9, .9, .9); L([(0, -.5), (0, 0), (.4, .25)])
    elif name == 'plus':
        L([(-.6, 0), (.6, 0)]); L([(0, -.6), (0, .6)])
    elif name == 'search':
        E(-.8, -.8, .35, .35); L([(.25, .25), (.85, .85)])
    elif name == 'wallet':
        c.rr((cx - s * .95, cy - s * .65, cx + s * .95, cy + s * .8), s * .18, outline=col, width=width); c.rr((cx + s * .35, cy - s * .1, cx + s * .95, cy + s * .35), s * .1, outline=col, width=width)
    elif name == 'eye':
        L([(-.95, 0), (-.5, -.5), (0, -.65), (.5, -.5), (.95, 0), (.5, .5), (0, .65), (-.5, .5), (-.95, 0)]); E(-.25, -.25, .25, .25)

def cursor_blink(t): return int(t * 2.2) % 2 == 0

# ------------------------------------------------------------------ 1. browser home
@functools.lru_cache(maxsize=24)
def browser_home(url_n, hover, pressed):
    W_, H_ = 1000, 640
    c = Canvas(W_, H_, bg=rgb('E9EDEA') + (255,), radius=22)
    # chrome
    for k, col in enumerate([rgb('FF5F57'), rgb('FEBC2E'), rgb('28C840')]):
        c.ellipse((22 + k * 22, 18, 36 + k * 22, 32), fill=col + (255,))
    c.rr((120, 10, 880, 40), 15, fill=WHITE + (255,))
    icon(c, 'lock', 140, 25, 13, GREY + (255,), 1.8)
    url = 'cabanypanama.com'[:url_n]
    c.text((156, 25), url, 600, 14, INK + (255,), 'lm')
    if url_n < 16:
        x = 156 + c.tlen(url, 600, 14) + 2
        c.line([(x, 16), (x, 34)], INK + (255,), 1.6)
    # page
    page = Image.new('RGBA', (S(W_), S(H_ - 50)), WHITE + (255,))
    c.im.paste(page, (0, S(50)))
    # hero
    c.photo('caba_a_alpina.webp', (0, 50, W_, H_), r=0)
    shade = Image.new('RGBA', (S(W_), S(H_ - 50)), (0, 20, 12, 120))
    c.im.alpha_composite(shade, (0, S(50)))
    # bottom radius fix
    m = rounded_mask(S(W_), S(H_), S(22)); a = np.asarray(c.im)[..., 3].astype(np.float32) * (np.asarray(m).astype(np.float32) / 255)
    c.im.putalpha(Image.fromarray(a.astype(np.uint8)))
    c.d = ImageDraw.Draw(c.im)
    # header
    c.logo('white', 30, 70, 120)
    for k, it in enumerate(['Explorar', 'Descubre', 'Blog', 'Mapa']):
        c.text((205 + k * 92, 86), it, 600, 13, WHITE + (235,), 'lm')
    c.text((630, 86), 'Hazte Anfitrión', 700, 13, WHITE + (255,), 'lm')
    bx0, bx1 = 778, 916
    if hover or pressed:
        c.rr((bx0 - 6, 64, bx1 + 6, 108), 24, outline=LIME_B + (255,), width=3)
    c.rr((bx0, 70, bx1, 102), 16, fill=(LIME_B if pressed else WHITE) + (255,))
    icon(c, 'user', bx0 + 20, 86, 13, GREEN + (255,), 1.8)
    c.text((bx0 + 34, 86), 'Registrarse', 700, 13, GREEN + (255,), 'lm')
    c.rr((932, 70, 966, 102), 16, outline=WHITE + (200,), width=1.6)
    for y in (80, 86, 92): c.line([(941, y), (957, y)], WHITE + (230,), 1.6)
    # hero copy
    c.text((W_ / 2, 300), 'Descubre. Reserva. Vive Panamá', 800, 38, WHITE + (255,), 'mm')
    c.text((W_ / 2, 345), 'Hospedajes, tours y experiencias para descubrir lo mejor de Panamá.', 500, 15, WHITE + (230,), 'mm')
    c.rr((170, 400, 830, 470), 35, fill=WHITE + (255,))
    for k, (a, b) in enumerate([('Dónde', 'Explorar destinos'), ('Cuándo', 'Añade fechas'), ('Quién', '1 huésped')]):
        x = 205 + k * 185
        c.text((x, 423), a, 700, 13, INK + (255,), 'lm'); c.text((x, 446), b, 500, 12, GREY + (255,), 'lm')
    c.rr((725, 410, 815, 460), 25, fill=GREEN + (255,))
    c.text((770, 435), 'Buscar', 700, 13, WHITE + (255,), 'mm')
    return c.im

# ------------------------------------------------------------------ 2. registration form
FORM_FIELDS = [('Nombre completo', 'user', 'Juan Pérez'), ('Correo electrónico', 'mail', 'juan@correo.com'),
               ('Teléfono', 'phone', '6838-1222'), ('Contraseña', 'lock', '••••••••••')]

@functools.lru_cache(maxsize=96)
def form_card(typed, active, pressed, done):
    """typed: tuple of chars typed per field; active: field index with focus (-1 none)."""
    W_, H_ = 460, 640
    c = Canvas(W_, H_, radius=30)
    c.rr((28, 28, 92, 92), 18, fill=G_LIGHT + (255,))
    icon(c, 'home', 60, 61, 30, GREEN + (255,), 2.6)
    c.text((110, 48), 'Registro de Anfitrión', 800, 21, INK + (255,), 'lm')
    c.text((110, 76), 'Crea tu cuenta y publica tu', 500, 13, GREY + (255,), 'lm')
    c.text((110, 94), 'propiedad en CABANY.', 500, 13, GREY + (255,), 'lm')
    y = 130
    for k, (lab, ic, val) in enumerate(FORM_FIELDS):
        c.text((28, y), lab, 700, 14, INK + (255,), 'lm'); c.text((28 + c.tlen(lab, 700, 14) + 4, y), '*', 700, 14, rgb('EF4444') + (255,), 'lm')
        fy0, fy1 = y + 16, y + 66
        foc = (k == active)
        c.rr((28, fy0, W_ - 28, fy1), 14, fill=(rgb('F3FBF1') if foc else WHITE) + (255,), outline=(G_MID if foc else G_LINE) + (255,), width=2.4 if foc else 1.6)
        icon(c, ic, 56, (fy0 + fy1) / 2, 17, (GREEN if foc or typed[k] else GREY_L) + (255,), 2)
        n = typed[k]
        if n:
            s = val[:n]
            c.text((80, (fy0 + fy1) / 2), s, 600, 16, INK + (255,), 'lm')
            if foc and n < len(val):
                x = 80 + c.tlen(s, 600, 16) + 2; c.line([(x, fy0 + 14), (x, fy1 - 14)], GREEN + (255,), 2)
        else:
            ph = {'Nombre completo': 'Ej. Juan Pérez', 'Correo electrónico': 'Ej. juan@correo.com', 'Teléfono': 'Ej. 6838-1222', 'Contraseña': 'Crea una contraseña segura'}[lab]
            c.text((80, (fy0 + fy1) / 2), ph, 500, 15, GREY_L + (255,), 'lm')
            if foc:
                c.line([(80, fy0 + 14), (80, fy1 - 14)], GREEN + (255,), 2)
        if ic == 'lock': icon(c, 'eye', W_ - 58, (fy0 + fy1) / 2, 18, GREY_L + (255,), 1.8)
        if n == len(val) and not foc:
            c.ellipse((W_ - 62 - (30 if ic == 'lock' else 0), (fy0 + fy1) / 2 - 11, W_ - 40 - (30 if ic == 'lock' else 0), (fy0 + fy1) / 2 + 11), fill=G_MID + (255,))
            icon(c, 'check', W_ - 51 - (30 if ic == 'lock' else 0), (fy0 + fy1) / 2, 12, WHITE + (255,), 2.2)
        y += 102
    by0, by1 = y + 4, y + 62
    col = G_DARK if pressed else GREEN
    if done:
        c.rr((28, by0, W_ - 28, by1), 18, fill=G_MID + (255,))
        icon(c, 'check', W_ / 2 - 78, (by0 + by1) / 2, 18, WHITE + (255,), 3)
        c.text((W_ / 2 + 12, (by0 + by1) / 2), '¡Cuenta creada!', 800, 17, WHITE + (255,), 'mm')
    else:
        c.rr((28 + (4 if pressed else 0), by0 + (2 if pressed else 0), W_ - 28 - (4 if pressed else 0), by1 - (2 if pressed else 0)), 18, fill=col + (255,))
        c.text((W_ / 2, (by0 + by1) / 2), 'Crear cuenta', 800, 17, WHITE + (255,), 'mm')
    return c.im

# ------------------------------------------------------------------ 3. publish panel
PHOTOS = ['caba_a_alpina.webp', 'lcs_3.webp', 'lcs_4.webp', 'lcs_2.webp']
SERVICES = ['Wi-Fi', 'Piscina', 'Cocina equipada', 'Estacionamiento', 'Jardín', 'Pet friendly']
LOC = 'Volcán, Chiriquí'; CAP = 'Hasta 8 personas'; PRICE = 'B/. 120.00'
AVAIL = [(r, c_) for r in range(5) for c_ in range(7) if 1 <= r * 7 + c_ - 1 <= 30]

@functools.lru_cache(maxsize=128)
def panel_card(n_photos, loc_n, cap_on, n_serv, price_n, n_avail, focus, pressed):
    W_, H_ = 520, 1095
    c = Canvas(W_, H_, bg=WHITE + (255,), radius=30)
    c.rr((0, 0, W_, 72), 30, fill=GREEN + (255,)); c.rr((0, 40, W_, 72), 0, fill=GREEN + (255,))
    c.logo('white', 24, 22, 96)
    c.text((W_ - 24, 37), 'PANEL ANFITRIÓN', 700, 11, LIME_B + (255,), 'rm')
    c.text((24, 104), 'Agregar nueva propiedad', 800, 22, INK + (255,), 'lm')
    def label(y, s): c.text((24, y), s, 700, 13, INK + (255,), 'lm')
    def box(y0, y1, foc): c.rr((24, y0, W_ - 24, y1), 12, fill=(rgb('F3FBF1') if foc else WHITE) + (255,), outline=(G_MID if foc else G_LINE) + (255,), width=2.4 if foc else 1.5)
    # photos
    label(146, 'Fotografías *')
    tw = (W_ - 48 - 4 * 10) / 5
    for k in range(5):
        x0 = 24 + k * (tw + 10); y0, y1 = 162, 162 + tw
        if k == 0:
            c.rr((x0, y0, x0 + tw, y1), 12, fill=BG + (255,), outline=(G_MID if focus == 'photos' else G_LINE) + (255,), width=2)
            icon(c, 'plus', x0 + tw / 2, y0 + tw / 2 - 8, 18, GREEN + (255,), 2.2)
            c.text((x0 + tw / 2, y0 + tw / 2 + 18), 'Subir', 600, 11, GREY + (255,), 'mm')
        elif k - 1 < n_photos:
            c.photo(PHOTOS[k - 1], (x0, y0, x0 + tw, y1), 12)
        else:
            c.rr((x0, y0, x0 + tw, y1), 12, outline=G_LINE + (255,), width=1.5)
    y = 162 + tw + 26
    label(y, 'Nombre de la cabaña *'); box(y + 14, y + 58, False)
    c.text((40, y + 36), 'Cabaña Brisas del Volcán', 600, 15, INK + (255,), 'lm')
    y += 82
    label(y, 'Ubicación *'); box(y + 14, y + 58, focus == 'loc')
    icon(c, 'pin', 44, y + 36, 16, (GREEN if loc_n else GREY_L) + (255,), 2)
    s = LOC[:loc_n]
    c.text((62, y + 36), s if loc_n else 'Ej. Volcán, Chiriquí', 600 if loc_n else 500, 15, (INK if loc_n else GREY_L) + (255,), 'lm')
    if focus == 'loc' and loc_n < len(LOC):
        x = 62 + (c.tlen(s, 600, 15) if loc_n else 0) + 2; c.line([(x, y + 24), (x, y + 48)], GREEN + (255,), 2)
    y += 82
    label(y, 'Capacidad *'); box(y + 14, y + 58, focus == 'cap')
    icon(c, 'users', 46, y + 36, 16, (GREEN if cap_on else GREY_L) + (255,), 1.8)
    c.text((66, y + 36), CAP if cap_on else 'Selecciona', 600 if cap_on else 500, 15, (INK if cap_on else GREY_L) + (255,), 'lm')
    c.line([(W_ - 52, y + 31), (W_ - 44, y + 39), (W_ - 36, y + 31)], GREY + (255,), 2)
    y += 82
    label(y, 'Servicios / Amenidades *')
    for k, sv in enumerate(SERVICES):
        col, row = k % 2, k // 2
        x0 = 24 + col * ((W_ - 48) / 2); y0 = y + 18 + row * 36
        on = k < n_serv
        c.rr((x0, y0, x0 + 22, y0 + 22), 6, fill=(G_MID if on else WHITE) + (255,), outline=(G_MID if on else G_LINE) + (255,), width=1.8)
        if on: icon(c, 'check', x0 + 11, y0 + 11, 12, WHITE + (255,), 2.2)
        c.text((x0 + 32, y0 + 11), sv, 600, 13, (INK if on else GREY) + (255,), 'lm')
    if focus == 'serv':
        c.rr((16, y + 8, W_ - 16, y + 18 + 3 * 36 + 6), 14, outline=G_MID + (255,), width=2.2)
    y += 18 + 3 * 36 + 22
    label(y, 'Precio por noche *'); box(y + 14, y + 58, focus == 'price')
    icon(c, 'tag', 44, y + 36, 16, (GREEN if price_n else GREY_L) + (255,), 1.8)
    s = PRICE[:price_n]
    c.text((62, y + 36), s if price_n else 'B/. 0.00', 700 if price_n else 500, 15, (INK if price_n else GREY_L) + (255,), 'lm')
    if focus == 'price' and price_n < len(PRICE):
        x = 62 + (c.tlen(s, 700, 15) if price_n else 0) + 2; c.line([(x, y + 24), (x, y + 48)], GREEN + (255,), 2)
    y += 82
    label(y, 'Disponibilidad *')
    cy0 = y + 18
    c.rr((24, cy0, W_ - 24, cy0 + 214), 14, outline=(G_MID if focus == 'avail' else G_LINE) + (255,), width=2.2 if focus == 'avail' else 1.5)
    c.text((W_ / 2, cy0 + 22), 'Diciembre 2026', 700, 13, INK + (255,), 'mm')
    cw = (W_ - 72) / 7
    for k, dname in enumerate(['L', 'M', 'M', 'J', 'V', 'S', 'D']):
        c.text((36 + cw * k + cw / 2, cy0 + 48), dname, 700, 11, GREY + (255,), 'mm')
    for idx, (r, col) in enumerate(AVAIL):
        day = r * 7 + col - 1
        cx_, cy_ = 36 + cw * col + cw / 2, cy0 + 76 + r * 30
        on = idx < n_avail
        if on: c.ellipse((cx_ - 13, cy_ - 13, cx_ + 13, cy_ + 13), fill=G_LIGHT + (255,), outline=G_MID + (255,), width=1.5)
        c.text((cx_, cy_), str(day), 700 if on else 500, 12, (GREEN if on else INK) + (255,), 'mm')
    y = cy0 + 236
    c.rr((24, y, W_ / 2 - 8, y + 50), 16, outline=G_LINE + (255,), width=1.6)
    c.text((W_ / 4 + 8, y + 25), 'Cancelar', 700, 14, GREY + (255,), 'mm')
    c.rr((W_ / 2 + 8, y, W_ - 24, y + 50), 16, fill=(G_DARK if pressed else GREEN) + (255,))
    c.text((W_ * 3 / 4 - 8, y + 25), 'Publicar propiedad', 700, 14, WHITE + (255,), 'mm')
    return c.im

def panel_y(section):
    """logical y centre of each panel section (for camera targets)."""
    tw = (520 - 48 - 40) / 5
    base = 162 + tw + 26
    return {'photos': 162 + tw / 2, 'name': base + 36, 'loc': base + 82 + 36, 'cap': base + 164 + 36,
            'serv': base + 246 + 70, 'price': base + 246 + 18 + 108 + 22 + 36,
            'avail': base + 246 + 18 + 108 + 22 + 82 + 18 + 107, 'buttons': base + 246 + 18 + 108 + 22 + 82 + 18 + 236 + 25}[section]

# ------------------------------------------------------------------ 4. final review
REVIEW = ['Información del alojamiento', 'Fotos y descripción', 'Precio y calendario', 'Servicios y reglas']

@functools.lru_cache(maxsize=32)
def review_card(n_ok, pressed, sent):
    W_, H_ = 480, 720
    c = Canvas(W_, H_, radius=30)
    c.text((28, 44), 'Revisión final', 800, 22, INK + (255,), 'lm')
    c.rr((28, 76, W_ - 28, 230), 18, fill=BG + (255,))
    c.photo('caba_a_alpina.webp', (40, 88, 190, 218), 14)
    c.text((206, 104), 'Cabaña Brisas del Volcán', 800, 15, INK + (255,), 'lm')
    icon(c, 'pin', 212, 128, 12, GREY + (255,), 1.6); c.text((224, 128), 'Volcán, Chiriquí', 500, 12, GREY + (255,), 'lm')
    for k, (ic, s) in enumerate([('users', 'Capacidad: 8 personas'), ('home', 'Habitaciones: 3 · Baños: 2'), ('tag', 'B/. 120.00 por noche')]):
        icon(c, ic, 212, 158 + k * 24, 12, GREEN + (255,), 1.6); c.text((228, 158 + k * 24), s, 600, 12, INK + (255,), 'lm')
    c.text((28, 266), 'Datos de la solicitud', 700, 14, INK + (255,), 'lm')
    for k, s in enumerate(REVIEW):
        y = 302 + k * 52
        on = k < n_ok
        c.rr((28, y - 20, W_ - 28, y + 20), 12, fill=(rgb('F3FBF1') if on else WHITE) + (255,), outline=(G_MID if on else G_LINE) + (255,), width=1.6)
        c.ellipse((40, y - 12, 64, y + 12), fill=(G_MID if on else WHITE) + (255,), outline=(G_MID if on else G_LINE) + (255,), width=1.6)
        if on: icon(c, 'check', 52, y, 12, WHITE + (255,), 2.4)
        c.text((76, y), s, 600, 14, (INK if on else GREY) + (255,), 'lm')
    by0, by1 = 530, 594
    if sent:
        c.rr((28, by0, W_ - 28, by1), 22, fill=G_MID + (255,))
        icon(c, 'check', 120, (by0 + by1) / 2, 20, WHITE + (255,), 3)
        c.text((W_ / 2 + 16, (by0 + by1) / 2), 'Solicitud enviada', 800, 17, WHITE + (255,), 'mm')
    else:
        p = 4 if pressed else 0
        c.rr((28 + p, by0 + p / 2, W_ - 28 - p, by1 - p / 2), 22, fill=(G_DARK if pressed else GREEN) + (255,))
        icon(c, 'send', 104, (by0 + by1) / 2, 20, WHITE + (255,), 2.4)
        c.text((W_ / 2 + 18, (by0 + by1) / 2), 'Enviar para verificación', 800, 16, WHITE + (255,), 'mm')
    c.text((W_ / 2, 640), 'Verifica que todos los datos sean correctos', 500, 12, GREY + (255,), 'mm')
    c.text((W_ / 2, 660), 'antes de enviarla.', 500, 12, GREY + (255,), 'mm')
    return c.im

# ------------------------------------------------------------------ 5. status card
@functools.lru_cache(maxsize=40)
def status_card(phase, spin):
    """phase 0 pending, 1 approved."""
    W_, H_ = 460, 420
    c = Canvas(W_, H_, radius=34)
    if phase == 0:
        c.rr((W_ / 2 - 46, 40, W_ / 2 + 46, 132), 26, fill=G_LIGHT + (255,))
        icon(c, 'home', W_ / 2, 86, 46, GREEN + (255,), 3)
        c.text((W_ / 2, 176), 'Solicitud en revisión', 800, 24, INK + (255,), 'mm')
        c.rr((40, 214, W_ - 40, 330), 22, fill=rgb('F3FBF1') + (255,), outline=G_LINE + (255,), width=1.5)
        cx_, cy_ = 96, 272
        c.ellipse((cx_ - 26, cy_ - 26, cx_ + 26, cy_ + 26), outline=G_LINE + (255,), width=4)
        a0 = spin * 360
        c.d.arc([S(cx_ - 26), S(cy_ - 26), S(cx_ + 26), S(cy_ + 26)], a0, a0 + 100, fill=G_MID + (255,), width=S(4))
        c.text((140, 256), 'Pendiente de aprobación', 600, 15, INK + (255,), 'lm')
        c.text((140, 284), 'por el equipo CABANY', 800, 15, GREEN + (255,), 'lm')
        c.text((W_ / 2, 372), 'Te notificaremos cuando tu cabaña sea aprobada.', 500, 12, GREY + (255,), 'mm')
    else:
        c.ellipse((W_ / 2 - 52, 34, W_ / 2 + 52, 138), fill=G_MID + (255,))
        icon(c, 'check', W_ / 2, 86, 52, WHITE + (255,), 5)
        c.text((W_ / 2, 178), '¡Propiedad aprobada!', 800, 25, INK + (255,), 'mm')
        c.rr((40, 214, W_ - 40, 330), 22, fill=rgb('F3FBF1') + (255,), outline=G_MID + (255,), width=2)
        c.photo('caba_a_alpina.webp', (56, 228, 150, 316), 14)
        c.text((166, 250), 'Cabaña Brisas del Volcán', 800, 14, INK + (255,), 'lm')
        c.rr((166, 268, 290, 294), 13, fill=G_MID + (255,)); c.text((228, 281), 'PUBLICADA', 800, 11, WHITE + (255,), 'mm')
        c.text((166, 310), 'Visible en cabanypanama.com', 500, 11, GREY + (255,), 'lm')
        c.text((W_ / 2, 372), 'Ya puedes recibir reservas.', 600, 13, GREEN + (255,), 'mm')
    return c.im

# ------------------------------------------------------------------ 6. payments
@functools.lru_cache(maxsize=16)
def calendar_card(n_mon):
    W_, H_ = 480, 460
    c = Canvas(W_, H_, radius=30)
    c.rr((0, 0, W_, 74), 30, fill=GREEN + (255,)); c.rr((0, 40, W_, 74), 0, fill=GREEN + (255,))
    icon(c, 'cal', 46, 38, 24, WHITE + (255,), 2.4)
    c.text((76, 38), 'Calendario de cortes', 800, 18, WHITE + (255,), 'lm')
    cw = (W_ - 56) / 7
    for k, dname in enumerate(['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']):
        c.text((28 + cw * k + cw / 2, 104), dname, 700, 13, (GREEN if k == 0 else GREY) + (255,), 'mm')
    mondays = 0
    for day in range(1, 32):
        r, col = (day - 1) // 7, (day - 1) % 7
        cx_, cy_ = 28 + cw * col + cw / 2, 146 + r * 58
        if col == 0:
            on = mondays < n_mon; mondays += 1
            if on:
                c.rr((cx_ - 24, cy_ - 22, cx_ + 24, cy_ + 22), 12, fill=G_MID + (255,))
                c.text((cx_, cy_), str(day), 800, 16, WHITE + (255,), 'mm'); continue
        c.text((cx_, cy_), str(day), 600, 15, INK + (255,), 'mm')
    return c.im

TL = [('Lunes', 'Corte de pago'), ('1–2 días', 'En validación'), ('Hasta 4 días', 'Transacción efectiva'), ('Pago', 'disponible')]
@functools.lru_cache(maxsize=64)
def timeline_card(prog_q, n_nodes):
    """prog_q: progress 0..60 (quantised); n_nodes: nodes reached."""
    W_, H_ = 500, 360
    c = Canvas(W_, H_, radius=30)
    c.text((W_ / 2, 40), 'Ejemplo de una transacción', 800, 17, INK + (255,), 'mm')
    xs = [70, 190, 310, 430]; y = 128
    c.line([(xs[0], y), (xs[-1], y)], G_LINE + (255,), 6)
    p = prog_q / 60
    c.line([(xs[0], y), (xs[0] + (xs[-1] - xs[0]) * p, y)], G_MID + (255,), 6)
    for k, (x, (a, b)) in enumerate(zip(xs, TL)):
        on = k < n_nodes
        last = k == 3
        r = 34
        c.ellipse((x - r, y - r, x + r, y + r), fill=((G_MID if not last else LIME_B) if on else WHITE) + (255,), outline=(G_MID if on else G_LINE) + (255,), width=3)
        icn = ['cal', 'clock', 'wallet', 'check'][k]
        icon(c, icn, x, y, 26, ((WHITE if not last else GREEN) if on else GREY_L) + (255,), 2.6)
        c.text((x, y + 60), a, 800, 14, (INK if on else GREY) + (255,), 'mm')
        c.text((x, y + 82), b, 500, 11, GREY + (255,), 'mm')
    c.rr((28, 262, W_ - 28, 330), 18, fill=GREEN + (255,))
    c.text((W_ / 2, 285), 'El pago se procesa después de que', 600, 13, WHITE + (255,), 'mm')
    c.text((W_ / 2, 307), 'la transacción sea efectiva.', 600, 13, LIME_B + (255,), 'mm')
    return c.im

@functools.lru_cache(maxsize=8)
def booking_card(stage):
    """reservation charged by Cabany. stage 0 new booking, 1 charged."""
    W_, H_ = 460, 250
    c = Canvas(W_, H_, radius=28)
    c.photo('caba_a_alpina.webp', (20, 20, 140, 140), 16)
    c.text((158, 40), 'Nueva reserva', 800, 17, INK + (255,), 'lm')
    c.text((158, 66), 'Cabaña Brisas del Volcán', 600, 13, GREY + (255,), 'lm')
    c.text((158, 90), '3 noches · 4 huéspedes', 600, 13, GREY + (255,), 'lm')
    c.text((158, 122), 'B/. 360.00', 800, 20, INK + (255,), 'lm')
    if stage:
        c.rr((20, 164, W_ - 20, 226), 18, fill=G_MID + (255,))
        icon(c, 'check', 64, 195, 18, WHITE + (255,), 3)
        c.text((W_ / 2 + 14, 195), 'Cobro gestionado por CABANY', 800, 14, WHITE + (255,), 'mm')
    else:
        c.rr((20, 164, W_ - 20, 226), 18, fill=BG + (255,), outline=G_LINE + (255,), width=1.6)
        c.text((W_ / 2, 195), 'Procesando cobro…', 600, 14, GREY + (255,), 'mm')
    return c.im

@functools.lru_cache(maxsize=8)
def notif(title, sub):
    W_, H_ = 440, 92
    c = Canvas(W_, H_, bg=(255, 255, 255, 245), radius=26)
    c.rr((14, 14, 78, 78), 18, fill=GREEN + (255,))
    c.logo('white', 20, 36, 52)
    c.text((94, 34), title, 800, 15, INK + (255,), 'lm')
    c.text((94, 60), sub, 500, 12, GREY + (255,), 'lm')
    c.text((W_ - 22, 34), 'ahora', 500, 11, GREY_L + (255,), 'rm')
    return c.im

def shadowed(im, blur=30, alpha=0.35, off=(0, 24), pad=70):
    out, _ = add_shadow(im, blur=blur * RS / 2, off=(off[0] * RS // 2, off[1] * RS // 2), alpha=alpha, pad=pad)
    return out


GRID = [('caba_a_mariposa.webp', 'Cabaña Mariposa', 'Volcán', '$120'), ('villa_diana.webp', 'Villa Diana', 'Boquete', '$30'),
        ('caba_a_alpina.webp', 'Cabaña Brisas del Volcán', 'Volcán, Chiriquí', 'B/. 120'), ('harmony_gates.webp', 'Harmony Gates', 'Volcán', '$25')]
@functools.lru_cache(maxsize=4)
def listing_grid(show_new):
    W_, H_ = 500, 640
    c = Canvas(W_, H_, radius=30)
    c.rr((0, 0, W_, 64), 30, fill=WHITE + (255,))
    c.logo('green', 24, 20, 104)
    c.text((W_ - 24, 34), 'Hazte Anfitrión', 700, 12, GREEN + (255,), 'rm')
    c.line([(0, 66), (W_, 66)], G_LINE + (255,), 1.5)
    c.text((24, 98), 'Nuevos descubrimientos', 800, 18, INK + (255,), 'lm')
    tw, th = (W_ - 60) / 2, 220
    for k, (img, name, loc, price) in enumerate(GRID):
        col, row = k % 2, k // 2
        x0, y0 = 20 + col * (tw + 20), 126 + row * (th + 40)
        if k == 2 and not show_new:
            c.rr((x0, y0, x0 + tw, y0 + th), 16, outline=G_LINE + (255,), width=1.5)
            continue
        c.photo(img, (x0, y0, x0 + tw, y0 + th - 70), 16)
        if k == 2:
            c.rr((x0 + 10, y0 + 10, x0 + 84, y0 + 36), 13, fill=LIME_B + (255,)); c.text((x0 + 47, y0 + 23), 'Nuevo', 800, 11, GREEN + (255,), 'mm')
        nm = name if c.tlen(name, 800, 12) < tw - 6 else name[:17] + '…'
        c.text((x0 + 4, y0 + th - 52), nm, 800, 12, INK + (255,), 'lm')
        c.text((x0 + 4, y0 + th - 32), loc, 500, 11, GREY + (255,), 'lm')
        c.text((x0 + 4, y0 + th - 10), price + ' / noche', 700, 12, INK + (255,), 'lm')
    return c.im
