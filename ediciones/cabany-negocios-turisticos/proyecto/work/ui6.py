"""Screens for the 'Ofrecer mis servicios' business-registration flow (based on the client's official graphics)."""
import math, functools
import numpy as np
from PIL import Image, ImageDraw
from lib import ROOT, rgb, GREEN, GREEN_D, LIME_B, WHITE, INK, rounded_mask, cover
from ui5 import Canvas, icon, mf, S, RS, G_DARK, G_MID, G_LIGHT, G_LINE, GREY, GREY_L, BG, browser_home as _bh, form_card as _fc, _logo

RED = rgb('EF4444')
AMBER = rgb('D97706'); AMBER_L = rgb('FEF3C7')

def browser_home(url_n, hover, pressed):
    """same browser as the host reel, with the 'Ofrecer mis servicios' button."""
    im = _bh(url_n, False, False).copy()
    c = Canvas.__new__(Canvas); c.w, c.h = 1000, 640; c.im = im; c.d = ImageDraw.Draw(im)
    # cover old buttons area with the hero photo strip, then draw new button
    strip = _bh(url_n, False, False).crop((S(520), S(60), S(990), S(112)))
    bl = strip.resize((8, 4), Image.BILINEAR).resize(strip.size, Image.BILINEAR)
    im.paste(bl, (S(520), S(60)))
    c.text((540, 86), 'Hazte Anfitrión', 700, 13, WHITE + (230,), 'lm')
    bx0, bx1 = 676, 916
    if hover or pressed:
        c.rr((bx0 - 6, 64, bx1 + 6, 108), 24, outline=LIME_B + (255,), width=3)
    c.rr((bx0, 70, bx1, 102), 16, fill=(LIME_B if pressed else WHITE) + (255,))
    icon(c, 'home', bx0 + 20, 86, 13, GREEN + (255,), 1.8)
    c.text((bx0 + 36, 86), 'Ofrecer mis servicios', 700, 13, GREEN + (255,), 'lm')
    c.rr((932, 70, 966, 102), 16, outline=WHITE + (200,), width=1.6)
    for y in (80, 86, 92): c.line([(941, y), (957, y)], WHITE + (230,), 1.6)
    return im

ACC_FIELDS = [('Nombre completo', 'user', 'Carlos Méndez'), ('Correo electrónico', 'mail', 'carlos@toursvolcan.com'),
              ('Teléfono', 'phone', '6512-4480'), ('Contraseña', 'lock', '••••••••••')]

@functools.lru_cache(maxsize=96)
def account_card(typed, active, pressed, done):
    import ui5
    old = ui5.FORM_FIELDS
    ui5.FORM_FIELDS = ACC_FIELDS
    try:
        im = _fc.__wrapped__(typed, active, pressed, done)
    finally:
        ui5.FORM_FIELDS = old
    # retitle
    c = Canvas.__new__(Canvas); c.w, c.h = 460, 640; c.im = im; c.d = ImageDraw.Draw(im)
    c.rr((106, 30, 446, 112), 0, fill=WHITE + (255,))
    c.text((110, 48), 'Crea tu cuenta', 800, 21, INK + (255,), 'lm')
    c.text((110, 76), 'Ofrece tus servicios turísticos', 500, 13, GREY + (255,), 'lm')
    c.text((110, 94), 'en CABANY. ¡Es gratis!', 600, 13, G_MID + (255,), 'lm')
    return im

# ------------------------------------------------------------------ panel shell
TABS = ['Tipo', 'Datos', 'Credenciales', 'Revisión']
def shell(c, W_, tab, done_upto):
    c.rr((0, 0, W_, 74), 30, fill=GREEN + (255,)); c.rr((0, 40, W_, 74), 0, fill=GREEN + (255,))
    lg = _logo('white', S(96)); c.im.alpha_composite(lg, (S(24), S(24)))
    c.text((128, 40), 'PANEL', 700, 11, LIME_B + (255,), 'lm')
    c.text((W_ - 24, 40), 'Mi negocio', 700, 13, WHITE + (255,), 'rm')
    c.rr((24, 96, 64, 136), 12, fill=G_LIGHT + (255,)); icon(c, 'shop', 44, 116, 22, GREEN + (255,), 2.2)
    c.text((76, 108), 'Ofrecer mis servicios', 800, 20, INK + (255,), 'lm')
    c.text((76, 130), 'Cuatro pasos para enviar tu negocio a revisión.', 500, 11.5, GREY + (255,), 'lm')
    x = 24
    for k, name in enumerate(TABS):
        lab = f'{k + 1}  {name}'
        w = c.tlen(lab, 700, 12.5) + 30
        act = k == tab; dn = k < done_upto
        c.rr((x, 156, x + w, 190), 17, fill=(GREEN if act else (G_LIGHT if dn else WHITE)) + (255,), outline=(GREEN if act else (G_MID if dn else G_LINE)) + (255,), width=1.5)
        c.text((x + w / 2, 173), lab, 700, 12.5, (WHITE if act else (GREEN if dn else GREY)) + (255,), 'mm')
        x += w + 8

def icon2(c, name, cx, cy, size, col, width=2.2):
    s = size / 2
    L = lambda pts: c.line([(cx + x * s, cy + y * s) for x, y in pts], col, width)
    if name == 'shop':
        L([(-.9, -.2), (-.75, -.85), (.75, -.85), (.9, -.2), (-.9, -.2)]); L([(-.75, -.2), (-.75, .9), (.75, .9), (.75, -.2)]); L([(-.2, .9), (-.2, .35), (.2, .35), (.2, .9)])
    elif name == 'bag':
        c.rr((cx - s * .9, cy - s * .45, cx + s * .9, cy + s * .85), s * .15, outline=col, width=width); L([(-.35, -.45), (-.35, -.8), (.35, -.8), (.35, -.45)])
    elif name == 'map':
        L([(-.9, -.6), (-.3, -.85), (.3, -.6), (.9, -.85), (.9, .6), (.3, .85), (-.3, .6), (-.9, .85), (-.9, -.6)]); L([(-.3, -.85), (-.3, .6)]); L([(.3, -.6), (.3, .85)])
    elif name == 'flag':
        L([(-.6, .95), (-.6, -.9)]); L([(-.6, -.85), (.8, -.55), (-.6, -.2)])
    elif name == 'bus':
        c.rr((cx - s * .85, cy - s * .8, cx + s * .85, cy + s * .55), s * .2, outline=col, width=width); L([(-.85, -.1), (.85, -.1)])
        c.ellipse((cx - s * .6, cy + s * .45, cx - s * .25, cy + s * .8), fill=col); c.ellipse((cx + s * .25, cy + s * .45, cx + s * .6, cy + s * .8), fill=col)
    elif name == 'doc':
        L([(-.65, -.9), (.3, -.9), (.7, -.5), (.7, .9), (-.65, .9), (-.65, -.9)]); L([(-.35, -.2), (.4, -.2)]); L([(-.35, .15), (.4, .15)]); L([(-.35, .5), (.15, .5)])
    elif name == 'shield':
        L([(0, -.95), (.8, -.6), (.75, .1), (.4, .6), (0, .9), (-.4, .6), (-.75, .1), (-.8, -.6), (0, -.95)]); L([(-.3, 0), (-.05, .28), (.35, -.25)])
    elif name == 'badge':
        c.ellipse((cx - s * .6, cy - s * .9, cx + s * .6, cy + s * .3), outline=col, width=width); L([(-.35, .15), (-.5, .95), (0, .7), (.5, .95), (.35, .15)])
    elif name == 'upload':
        L([(0, .5), (0, -.6)]); L([(-.4, -.25), (0, -.65), (.4, -.25)]); L([(-.8, .3), (-.8, .85), (.8, .85), (.8, .3)])
    elif name == 'whatsapp':
        c.ellipse((cx - s * .85, cy - s * .85, cx + s * .85, cy + s * .85), outline=col, width=width); L([(-.6, .55), (-.85, .95), (-.4, .78)])
    elif name == 'pdf':
        L([(-.65, -.9), (.3, -.9), (.7, -.5), (.7, .9), (-.65, .9), (-.65, -.9)])
    else:
        icon(c, name, cx, cy, size, col, width)

import ui5 as _u
_orig_icon = _u.icon
def icon(c, name, cx, cy, size, col, width=2.2):
    if name in ('shop', 'bag', 'map', 'flag', 'bus', 'doc', 'shield', 'badge', 'upload', 'whatsapp', 'pdf'):
        return icon2(c, name, cx, cy, size, col, width)
    return _orig_icon(c, name, cx, cy, size, col, width)

# ------------------------------------------------------------------ tab 1: Tipo
TYPES = [('bag', 'Agencia turística', 'Armas paquetes con hospedaje,', 'tours y traslados.'),
         ('map', 'Operador', 'Operas tours y actividades', 'con tus propios guías.'),
         ('flag', 'Guía', 'Guías personas en experiencias', 'y caminatas.'),
         ('bus', 'Transportista', 'Trasladas pasajeros entre', 'destinos.')]
@functools.lru_cache(maxsize=48)
def tipo_card(checked, pressed, hl=-1):
    W_, H_ = 520, 760
    c = Canvas(W_, H_, radius=30)
    shell(c, W_, 0, 0)
    c.text((24, 226), 'Qué vas a ofrecer', 800, 17, INK + (255,), 'lm')
    c.text((24, 250), 'Puedes marcar más de un tipo.', 500, 12, GREY + (255,), 'lm')
    for k, (ic, t, d1, d2) in enumerate(TYPES):
        y0 = 276 + k * 98; y1 = y0 + 84
        on = checked[k]
        if k == hl:
            c.rr((18, y0 - 6, W_ - 18, y1 + 6), 20, outline=LIME_B + (255,), width=4)
        c.rr((24, y0, W_ - 24, y1), 16, fill=(rgb('F3FBF1') if on else WHITE) + (255,), outline=(G_MID if on else G_LINE) + (255,), width=2.2 if on else 1.5)
        c.rr((40, y0 + 29, 66, y0 + 55), 7, fill=(G_MID if on else WHITE) + (255,), outline=(G_MID if on else GREY_L) + (255,), width=1.8)
        if on: icon(c, 'check', 53, y0 + 42, 14, WHITE + (255,), 2.4)
        c.rr((82, y0 + 18, 130, y0 + 66), 14, fill=(G_LIGHT if on else BG) + (255,))
        icon(c, ic, 106, y0 + 42, 26, (GREEN if on else GREY) + (255,), 2.2)
        c.text((146, y0 + 26), t, 800, 15, INK + (255,), 'lm')
        c.text((146, y0 + 48), d1, 500, 12, GREY + (255,), 'lm'); c.text((146, y0 + 66), d2, 500, 12, GREY + (255,), 'lm')
    by = 686
    c.rr((W_ - 200 + (3 if pressed else 0), by, W_ - 24 - (3 if pressed else 0), by + 50), 20, fill=(G_DARK if pressed else GREEN) + (255,))
    c.text((W_ - 112, by + 25), 'Continuar  →', 700, 14, WHITE + (255,), 'mm')
    return c.im

# ------------------------------------------------------------------ tab 2: Datos
DATA = [('shop', 'Nombre del negocio', 'Tours Volcán Panamá'),
        ('doc', 'Descripción del negocio', 'Tours guiados al Volcán Barú y senderos.'),
        ('pin', 'Ubicación', 'Boquete, Chiriquí'),
        ('phone', 'Teléfono', '+507 6512-4480'),
        ('mail', 'Correo', 'info@toursvolcan.com'),
        ('whatsapp', 'WhatsApp', '+507 6512-4480')]
@functools.lru_cache(maxsize=128)
def datos_card(typed, focus, pressed):
    W_, H_ = 520, 860
    c = Canvas(W_, H_, radius=30)
    shell(c, W_, 1, 1)
    c.text((24, 226), 'Datos del negocio', 800, 17, INK + (255,), 'lm')
    y = 256
    for k, (ic, lab, val) in enumerate(DATA):
        if k == 3:
            c.text((24, y + 6), 'Información de contacto', 800, 14, INK + (255,), 'lm'); y += 26
        foc = k == focus
        h = 52
        c.text((24, y + 8), lab + ' *', 700, 12.5, GREY + (255,), 'lm')
        y0, y1 = y + 20, y + 20 + h
        c.rr((24, y0, W_ - 24, y1), 12, fill=(rgb('F3FBF1') if foc else WHITE) + (255,), outline=(G_MID if foc else G_LINE) + (255,), width=2.4 if foc else 1.5)
        n = typed[k]
        icon(c, ic, 46, (y0 + y1) / 2, 17, (GREEN if n or foc else GREY_L) + (255,), 2)
        s = val[:n]
        if n:
            c.text((68, (y0 + y1) / 2), s, 600, 14, INK + (255,), 'lm')
        else:
            c.text((68, (y0 + y1) / 2), 'Ej. ' + val, 500, 14, GREY_L + (255,), 'lm')
        if foc and n < len(val):
            x = 68 + (c.tlen(s, 600, 14) if n else 0) + 2; c.line([(x, y0 + 14), (x, y1 - 14)], GREEN + (255,), 2)
        if n == len(val) and not foc:
            c.ellipse((W_ - 60, (y0 + y1) / 2 - 11, W_ - 38, (y0 + y1) / 2 + 11), fill=G_MID + (255,))
            icon(c, 'check', W_ - 49, (y0 + y1) / 2, 12, WHITE + (255,), 2.2)
        y = y1 + 14
    by = H_ - 76
    c.rr((W_ - 200 + (3 if pressed else 0), by, W_ - 24 - (3 if pressed else 0), by + 50), 20, fill=(G_DARK if pressed else GREEN) + (255,))
    c.text((W_ - 112, by + 25), 'Continuar  →', 700, 14, WHITE + (255,), 'mm')
    return c.im

def datos_y(k):
    """logical y centre of the k-th data field."""
    y = 256
    for j in range(len(DATA)):
        if j == 3: y += 26
        y0 = y + 20
        if j == k: return y0 + 26
        y = y0 + 52 + 14
    return y

# ------------------------------------------------------------------ tab 3: Credenciales
DOCS = [('doc', 'RUC', 'Registro Único de Contribuyente', 'RUC_ToursVolcan.pdf'),
        ('badge', 'Licencia ATP', 'Autoridad de Turismo de Panamá', 'Licencia_ATP_2026.pdf'),
        ('shield', 'Seguro vigente', 'Póliza de responsabilidad civil', 'Poliza_Seguro.pdf')]
@functools.lru_cache(maxsize=96)
def cred_card(progress, pressed):
    """progress: tuple of 0..20 per document (20 = uploaded)."""
    W_, H_ = 520, 700
    c = Canvas(W_, H_, radius=30)
    shell(c, W_, 2, 2)
    c.text((24, 226), 'Sube tus documentos', 800, 17, INK + (255,), 'lm')
    c.text((24, 250), 'PDF, JPG o PNG (máx. 10 MB) · según requisitos.', 500, 12, GREY + (255,), 'lm')
    for k, (ic, t, d, fn) in enumerate(DOCS):
        y0 = 274 + k * 118; y1 = y0 + 104
        p = progress[k] / 20; done = progress[k] >= 20
        c.rr((24, y0, W_ - 24, y1), 16, fill=(rgb('F3FBF1') if done else WHITE) + (255,), outline=(G_MID if done else G_LINE) + (255,), width=2 if done else 1.5)
        c.rr((40, y0 + 18, 92, y0 + 70), 14, fill=(G_LIGHT if p > 0 else BG) + (255,))
        icon(c, ic, 66, y0 + 44, 28, (GREEN if p > 0 else GREY) + (255,), 2.2)
        c.text((108, y0 + 30), t, 800, 15, INK + (255,), 'lm')
        if p == 0:
            c.text((108, y0 + 54), d, 500, 12, GREY + (255,), 'lm')
            c.rr((W_ - 150, y0 + 30, W_ - 40, y0 + 66), 18, outline=G_MID + (255,), width=1.8)
            icon(c, 'upload', W_ - 126, y0 + 48, 16, GREEN + (255,), 2)
            c.text((W_ - 82, y0 + 48), 'Subir', 700, 13, GREEN + (255,), 'mm')
        else:
            c.text((108, y0 + 54), fn, 600, 12, (GREEN if done else GREY) + (255,), 'lm')
            c.rr((108, y0 + 76, W_ - 96, y0 + 84), 4, fill=G_LINE + (255,))
            c.rr((108, y0 + 76, 108 + (W_ - 204) * p, y0 + 84), 4, fill=G_MID + (255,))
            if done:
                c.ellipse((W_ - 74, y0 + 36, W_ - 44, y0 + 66), fill=G_MID + (255,)); icon(c, 'check', W_ - 59, y0 + 51, 16, WHITE + (255,), 2.6)
            else:
                c.text((W_ - 60, y0 + 80), f'{int(p * 100)}%', 700, 12, GREEN + (255,), 'mm')
    by = H_ - 76
    c.rr((W_ - 200 + (3 if pressed else 0), by, W_ - 24 - (3 if pressed else 0), by + 50), 20, fill=(G_DARK if pressed else GREEN) + (255,))
    c.text((W_ - 112, by + 25), 'Continuar  →', 700, 14, WHITE + (255,), 'mm')
    return c.im

# ------------------------------------------------------------------ tab 4: Revisión
CHECKS = ['Tipo de negocio', 'Datos y contacto', 'Documentos (RUC, ATP, seguro)', 'Información completa']
@functools.lru_cache(maxsize=32)
def rev_card(n_ok, pressed, sent):
    W_, H_ = 520, 760
    c = Canvas(W_, H_, radius=30)
    shell(c, W_, 3, 3)
    c.text((24, 226), 'Revisión de tu solicitud', 800, 17, INK + (255,), 'lm')
    c.rr((24, 248, W_ - 24, 400), 18, fill=BG + (255,))
    c.photo('stock_tour.jpg', (38, 262, 170, 386), 14)
    c.text((186, 278), 'Tours Volcán Panamá', 800, 15, INK + (255,), 'lm')
    icon(c, 'pin', 192, 304, 12, GREY + (255,), 1.6); c.text((206, 304), 'Boquete, Chiriquí', 500, 12, GREY + (255,), 'lm')
    for k, (t, x) in enumerate([('Operador', 186), ('Guía', 286), ('Transporte', 186)]):
        yy = 336 if k < 2 else 368
        w = c.tlen(t, 700, 11) + 24
        c.rr((x, yy - 13, x + w, yy + 13), 13, fill=G_LIGHT + (255,)); c.text((x + w / 2, yy), t, 700, 11, GREEN + (255,), 'mm')
    for k, s in enumerate(CHECKS):
        y = 440 + k * 52
        on = k < n_ok
        c.rr((24, y - 20, W_ - 24, y + 20), 12, fill=(rgb('F3FBF1') if on else WHITE) + (255,), outline=(G_MID if on else G_LINE) + (255,), width=1.6)
        c.ellipse((36, y - 12, 60, y + 12), fill=(G_MID if on else WHITE) + (255,), outline=(G_MID if on else G_LINE) + (255,), width=1.6)
        if on: icon(c, 'check', 48, y, 12, WHITE + (255,), 2.4)
        c.text((72, y), s, 600, 14, (INK if on else GREY) + (255,), 'lm')
    by0, by1 = 664, 724
    if sent:
        c.rr((24, by0, W_ - 24, by1), 22, fill=G_MID + (255,)); icon(c, 'check', 140, (by0 + by1) / 2, 20, WHITE + (255,), 3)
        c.text((W_ / 2 + 16, (by0 + by1) / 2), 'Solicitud enviada', 800, 17, WHITE + (255,), 'mm')
    else:
        p = 4 if pressed else 0
        c.rr((24 + p, by0 + p / 2, W_ - 24 - p, by1 - p / 2), 22, fill=(G_DARK if pressed else GREEN) + (255,))
        icon(c, 'send', 160, (by0 + by1) / 2, 20, WHITE + (255,), 2.4)
        c.text((W_ / 2 + 18, (by0 + by1) / 2), 'Enviar solicitud', 800, 16, WHITE + (255,), 'mm')
    return c.im

# ------------------------------------------------------------------ status
@functools.lru_cache(maxsize=40)
def status6(phase, spin):
    W_, H_ = 470, 430
    c = Canvas(W_, H_, radius=34)
    if phase == 0:
        c.ellipse((W_ / 2 - 50, 34, W_ / 2 + 50, 134), fill=AMBER_L + (255,))
        c.ellipse((W_ / 2 - 30, 54, W_ / 2 + 30, 114), outline=AMBER + (255,), width=4)
        a0 = spin * 360
        c.line([(W_ / 2, 84), (W_ / 2 + 16 * math.cos(math.radians(a0 - 90)), 84 + 16 * math.sin(math.radians(a0 - 90)))], AMBER + (255,), 4)
        c.line([(W_ / 2, 84), (W_ / 2 + 10, 92)], AMBER + (255,), 4)
        c.rr((W_ / 2 - 90, 160, W_ / 2 + 90, 200), 20, fill=AMBER_L + (255,))
        c.text((W_ / 2, 180), 'En revisión', 800, 19, AMBER + (255,), 'mm')
        c.text((W_ / 2, 244), 'Tu información está siendo', 500, 15, INK + (255,), 'mm')
        c.text((W_ / 2, 268), 'validada por el equipo Cabany.', 500, 15, INK + (255,), 'mm')
        for k in range(3):
            on = (int(spin * 12) % 3) == k
            c.ellipse((W_ / 2 - 30 + k * 26, 318, W_ / 2 - 18 + k * 26, 330), fill=(AMBER if on else AMBER_L) + (255,))
        c.text((W_ / 2, 380), 'Te avisaremos cuando tu negocio sea aprobado.', 500, 12, GREY + (255,), 'mm')
    else:
        c.ellipse((W_ / 2 - 52, 30, W_ / 2 + 52, 134), fill=G_MID + (255,)); icon(c, 'check', W_ / 2, 82, 52, WHITE + (255,), 5)
        c.rr((W_ / 2 - 90, 160, W_ / 2 + 90, 200), 20, fill=G_LIGHT + (255,))
        c.text((W_ / 2, 180), 'Aprobado', 800, 19, GREEN + (255,), 'mm')
        c.text((W_ / 2, 244), '¡Tu negocio ya está confirmado', 600, 15, INK + (255,), 'mm')
        c.text((W_ / 2, 268), 'y aparecerá en nuestro catálogo!', 600, 15, INK + (255,), 'mm')
        c.rr((40, 304, W_ - 40, 350), 23, fill=G_MID + (255,)); c.text((W_ / 2, 327), 'PUBLICADO EN CABANY', 800, 13, WHITE + (255,), 'mm')
        c.text((W_ / 2, 386), 'Ya puedes recibir reservas.', 600, 13, GREEN + (255,), 'mm')
    return c.im

# ------------------------------------------------------------------ dashboard
BARS = [0.25, 0.42, 0.55, 0.38, 0.72, 0.6, 0.9]
@functools.lru_cache(maxsize=48)
def dash_card(k):
    """k: animation progress 0..24"""
    p = k / 24
    W_, H_ = 540, 820
    c = Canvas(W_, H_, bg=BG + (255,), radius=30)
    c.rr((0, 0, W_, 74), 30, fill=GREEN + (255,)); c.rr((0, 40, W_, 74), 0, fill=GREEN + (255,))
    lg = _logo('white', S(96)); c.im.alpha_composite(lg, (S(24), S(24)))
    c.text((128, 40), 'PANEL', 700, 11, LIME_B + (255,), 'lm')
    c.text((W_ - 24, 40), 'Mi negocio', 700, 13, WHITE + (255,), 'rm')
    c.text((24, 110), '¡Hola, Carlos!', 800, 22, INK + (255,), 'lm')
    c.text((24, 136), 'Aquí administras tu negocio turístico.', 500, 13, GREY + (255,), 'lm')
    e = lambda a: 1 - (1 - min(1, max(0, a))) ** 3
    tiles = [('cal', f'{int(round(12 * e(p * 1.6)))}', 'Reservas'), ('users', f'{int(round(28 * e(p * 1.6)))}', 'Clientes'),
             ('wallet', f'B/. {int(round(1240 * e(p * 1.6))):,}', 'Ingresos')]
    tw = (W_ - 48 - 24) / 3
    for j, (ic, v, lab) in enumerate(tiles):
        x0 = 24 + j * (tw + 12)
        c.rr((x0, 160, x0 + tw, 270), 16, fill=(G_LIGHT if j == 0 else WHITE) + (255,), outline=G_LINE + (255,), width=1.2)
        icon(c, ic, x0 + 30, 188, 20, GREEN + (255,), 2)
        c.text((x0 + 16, 226), v, 800, 21 if j < 2 else 17, INK + (255,), 'lm')
        c.text((x0 + 16, 252), lab, 500, 12, GREY + (255,), 'lm')
    c.rr((24, 290, W_ - 24, 520), 16, fill=WHITE + (255,), outline=G_LINE + (255,), width=1.2)
    c.text((44, 316), 'Reservas del mes', 800, 14, INK + (255,), 'lm')
    bw = (W_ - 48 - 60) / len(BARS)
    for j, h in enumerate(BARS):
        hh = 150 * h * e(p * 1.8 - j * 0.08)
        x0 = 54 + j * bw
        col = G_MID if j == len(BARS) - 1 else rgb('8BD45A')
        if hh > 1: c.rr((x0, 500 - hh, x0 + bw * 0.62, 500), 6, fill=col + (255,))
    c.rr((24, 540, W_ - 24, 790), 16, fill=WHITE + (255,), outline=G_LINE + (255,), width=1.2)
    c.text((44, 566), 'Próximas reservas', 800, 14, INK + (255,), 'lm')
    rows = [('Tour Volcán Barú', '10 Ene · 4 personas'), ('Traslado Boquete', '12 Ene · 6 personas'), ('Sendero Quetzales', '17 Ene · 2 personas')]
    for j, (a, b) in enumerate(rows):
        y = 610 + j * 60
        vis = e(p * 2 - 0.5 - j * 0.15)
        if vis <= 0: continue
        c.rr((40, y - 20, 84, y + 24), 12, fill=G_LIGHT + (255,)); icon(c, ['map', 'bus', 'flag'][j], 62, y + 2, 20, GREEN + (255,), 2)
        c.text((98, y - 4), a, 700, 14, INK + (255,), 'lm'); c.text((98, y + 16), b, 500, 12, GREY + (255,), 'lm')
        c.rr((W_ - 150, y - 10, W_ - 40, y + 16), 13, fill=G_MID + (255,)); c.text((W_ - 95, y + 3), 'Confirmada', 700, 11, WHITE + (255,), 'mm')
    return c.im
