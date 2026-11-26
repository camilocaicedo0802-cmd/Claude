#!/usr/bin/env python3
"""A1-11 · motion graphics BOFU. Reutiliza las piezas de a107/mg.py (fondo que siempre se mueve, producto = recorte REAL,
frascos genéricos, sello 14 días, 4 pasos) y agrega las escenas nuevas de los hooks y del problema.
uso: mg11.py todas durs.json -> tmp/m11_<escena>.mp4"""
import os, sys, math, json, random, importlib.util
from PIL import Image, ImageDraw, ImageFont
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
MG = f'{G}/a107/mg.py' if os.path.exists(f'{G}/a107/mg.py') else '/home/user/Claude/geoda/videos/GEO-MOFU-A1-07/mg.py'
spec = importlib.util.spec_from_file_location('mg', MG); mg = importlib.util.module_from_spec(spec); spec.loader.exec_module(mg)
mg.T = f'{G}/a111/tmp'; os.makedirs(mg.T, exist_ok=True)
from build_a102 import render_runs, box_text, FONT_BLACK, NAVY, TEAL, YEL, WHITE
RED, GREEN = mg.RED, mg.GREEN

def write(name, dur, fn):
    mg.write('11_' + name, dur, fn)

def octagon(text, r=150, col=(214, 32, 38)):
    S = 2; im = Image.new('RGBA', (2 * r * S + 20, 2 * r * S + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = r * S + 10
    pts = [(c + r * S * math.cos(math.pi / 8 + k * math.pi / 4), c + r * S * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    d.polygon(pts, fill=(255, 255, 255, 255)); pts2 = [(c + (r - 12) * S * math.cos(math.pi / 8 + k * math.pi / 4), c + (r - 12) * S * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    d.polygon(pts2, fill=col + (255,)); f = ImageFont.truetype(FONT_BLACK, int(r * 0.62 * S))
    d.text((c, c), text, font=f, fill=(255, 255, 255, 255), anchor='mm')
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)
PARE = octagon('PARE')

def check(size=260, col=GREEN):
    S = 2; im = Image.new('RGBA', (size * S, size * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, size * S, size * S], fill=(255, 255, 255, 255)); d.ellipse([14, 14, size * S - 14, size * S - 14], fill=col + (255,))
    d.line([(size * S * .27, size * S * .52), (size * S * .44, size * S * .68), (size * S * .74, size * S * .34)], fill=(255, 255, 255, 255), width=int(size * S * .1), joint='curve')
    return im.resize((size, size), Image.LANCZOS)
CHECK = check()

def bftag(w=330, h=210, lines=(('BLACK', WHITE), ('FRIDAY', YEL)), bg=(15, 15, 18)):
    S = 2; im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = 50 * S
    d.polygon([(c, 0), (w * S - c, 0), (w * S, c), (w * S, h * S), (0, h * S), (0, c)], fill=bg + (255,))
    d.ellipse([(w // 2 - 13) * S, 14 * S, (w // 2 + 13) * S, 40 * S], fill=(235, 235, 235, 255))
    f = ImageFont.truetype(FONT_BLACK, 64 * S)
    for i, (t, col) in enumerate(lines): d.text((w // 2 * S, (h // 2 + 22 + (i - 0.5) * 70) * S), t, font=f, fill=col + (255,), anchor='mm')
    return im.resize((w, h), Image.LANCZOS)
TAG = bftag()

def s_ha(t, d):   # frascos genéricos que entran en un carrito... y un PARE frena todo; la piedra real al centro
    im = mg.background(t); mg.product(im, 540, 1180 + mg.bob(t), 600)
    stop = 0.9
    for i in range(4):
        x0 = 1250 + i * 150; x = x0 - (x0 - (690 + i * 82)) * mg.ease(min(t, stop) / stop)
        if t > stop: x += 6 * math.sin((t - stop) * 30) * math.exp(-4 * (t - stop))
        mg.paste(im, mg.GB, x, 1300 - (i % 2) * 40, scale=0.8)
    if t > stop - 0.05:
        u = (t - stop + 0.05) / 0.25; dx, dy = mg.shake(t, stop, 16, 0.35)
        mg.paste(im, PARE, 770 + dx, 850 + dy, scale=mg.back(u) if u < 1 else 1 + 0.03 * math.sin(t * 6), angle=-8)
    return im

def s_hb(t, d):   # X roja sobre la piedra que se cae y se vuelve ✓ verde
    im = mg.background(t); mg.product(im, 540, 1150 + mg.bob(t), 640)
    if t < 1.0:
        u = min(1, t / 0.2); mg.paste(im, mg.X300, 830, 860, scale=1.4 - 0.4 * mg.ease(u))
    elif t < 1.4:
        u = (t - 1.0) / 0.4; mg.paste(im, mg.X300, 830, 860 + 900 * u * u, angle=40 * u, alpha=1 - u)
    if t > 1.2:
        u = (t - 1.2) / 0.3; mg.paste(im, CHECK, 830, 860, scale=mg.back(u) if u < 1 else 1 + 0.03 * math.sin(t * 5))
        rnd = random.Random(int(t * 30)); dd = ImageDraw.Draw(im)
        for _ in range(10):
            a = rnd.uniform(0, 6.28); r = rnd.uniform(150, 230); x, y = 830 + r * math.cos(a), 860 + r * math.sin(a)
            dd.ellipse([x - 5, y - 5, x + 5, y + 5], fill=YEL)
    return im

def s_hc(t, d):   # fondo oscuro, la etiqueta BLACK FRIDAY cae junto a la piedra y llueve confeti
    im = mg.background(t, tint=((20, 20, 26), 0.78)); mg.product(im, 540, 1200 + mg.bob(t), 600)
    u = min(1, t / 0.45); y = -250 + (820 + 250) * (1 - (1 - u) ** 3)
    ang = 14 * math.exp(-0.8 * t) * math.sin(t * 5) + 4 * math.sin(t * 2.2)
    r = TAG.rotate(ang, resample=Image.BICUBIC, center=(TAG.width / 2, 27)); dd = ImageDraw.Draw(im)
    dd.line([(800, 560), (800, y + 27)], fill=(200, 200, 200), width=4); im.alpha_composite(r, (int(800 - r.width / 2), int(y)))
    rnd = random.Random(3)
    for _ in range(70):
        x0 = rnd.uniform(40, 1040); v = rnd.uniform(250, 600); c = rnd.choice([YEL, WHITE, TEAL, (226, 46, 46)])
        yy = (rnd.uniform(-1900, 0) + t * v) % 2100 - 100; dd.rectangle([x0, yy, x0 + 14, yy + 24], fill=c)
    return im

def s_hd(t, d):   # calendario que corre del 26 al 30 de noviembre + piedra real con etiqueta BF
    im = mg.background(t); dd = ImageDraw.Draw(im)
    mg.product(im, 360, 1230 + mg.bob(t), 560)
    r = TAG.rotate(5 * math.sin(t * 2.4), resample=Image.BICUBIC, center=(TAG.width / 2, 27)); im.alpha_composite(r, (int(360 + 160 - r.width / 2), 760))
    day = min(30, 26 + int(t / 0.45)); flip = (t / 0.45) % 1 if day < 30 else 1
    cx, cy = 790, 1080; card = Image.new('RGBA', (300, 330), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, 300, 330], 34, fill=(255, 255, 255, 255), outline=(220, 220, 215, 255), width=4)
    cd.rounded_rectangle([0, 0, 300, 90], 34, fill=(226, 46, 46, 255)); cd.rectangle([0, 50, 300, 90], fill=(226, 46, 46, 255))
    cd.text((150, 47), 'NOV', font=ImageFont.truetype(FONT_BLACK, 52), fill=(255, 255, 255, 255), anchor='mm')
    cd.text((150, 210), str(day), font=ImageFont.truetype(FONT_BLACK, 170), fill=NAVY + (255,), anchor='mm')
    sc = 1 - 0.12 * math.sin(math.pi * min(1, flip / 0.3)) if day < 30 else 1 + 0.04 * math.sin(t * 6)
    mg.paste(im, card, cx, cy, scale=sc)
    return im

def s_b1(t, d):   # seca (raspa con chispas) / guardada mojada (ducha) / se agrieta — sin letreros de 'error'
    a, b = d * 0.38, d * 0.70
    if t < a:
        im = mg.background(t); mg.paste(im, mg.ARM, 540, 1290); x = 540 + 210 * math.sin(t * 2 * math.pi * 1.6); tip = (x - 250, 1225)
        mg.product(im, x, 1150, 430, angle=90, tube=True, shadow=False); rnd = random.Random(int(t * 30)); dd = ImageDraw.Draw(im)
        for _ in range(14):
            an = rnd.uniform(-2.6, -0.5); rr = rnd.uniform(20, 120)
            dd.line([tip[0], tip[1], tip[0] + rr * math.cos(an), tip[1] + rr * math.sin(an)], fill=(255, rnd.randint(150, 220), 40), width=rnd.randint(3, 6))
        return im
    if t < b:
        im = mg.background(t, tint=((150, 180, 200), 0.18)); dd = ImageDraw.Draw(im)
        dd.rounded_rectangle([640, 330, 900, 380], 20, fill=(150, 155, 160)); dd.rounded_rectangle([860, 250, 900, 380], 15, fill=(150, 155, 160))
        dd.ellipse([600, 360, 800, 440], fill=(170, 175, 180)); rnd = random.Random(int(t * 30))
        for _ in range(140):
            x = rnd.uniform(540, 880); y = 440 + ((t * 1400 + rnd.uniform(0, 1400)) % 1100); dd.line([x - (y - 440) * 0.25, y, x - (y - 440) * 0.25 - 6, y + 40], fill=(110, 170, 220), width=4)
        dd.rounded_rectangle([200, 1460, 880, 1500], 12, fill=(170, 160, 150)); mg.product(im, 540, 1460 - 280, 560, shadow=False)
        return im
    return mg.s_b7(t - b, d - b)

def s_b2(t, d):   # producto real protagonista: gira suave, brillo que barre y destellos
    im = mg.background(t); py = 1130 + mg.bob(t, 10); h = 720
    mg.product(im, 540, py, h); mg.shine(im, t, 540, py, h, period=1.6, t0=0.3)
    rnd = random.Random(int(t * 12)); dd = ImageDraw.Draw(im)
    for _ in range(6):
        x, y = rnd.uniform(200, 880), rnd.uniform(700, 1500); r = rnd.uniform(6, 16)
        dd.line([x - r, y, x + r, y], fill=(255, 255, 255), width=4); dd.line([x, y - r, x, y + r], fill=(255, 255, 255), width=4)
    return im

SCENES = dict(ha=s_ha, hb=s_hb, hc=s_hc, hd=s_hd, b1=s_b1, b2=s_b2, b3=mg.s_b8, b4=mg.s_b10)
if __name__ == '__main__':
    for k, v in json.load(open(sys.argv[2])).items(): write(k, v, SCENES[k])
