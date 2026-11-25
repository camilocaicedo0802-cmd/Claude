#!/usr/bin/env python3
"""A1-07 · motion graphics (faceless). Cada escena es un clip 1080x1920 a 30 fps, siempre en movimiento:
fondo con manchas suaves que se desplazan + animación propia. El producto es el RECORTE REAL de la landing (etiqueta real).
uso: mg.py <escena> <duración>  |  mg.py todas <json con duraciones>   -> tmp/mg_<escena>.mp4"""
import os, sys, math, json, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102'); sys.path.insert(0, G)
from build_a102 import render_runs, box_text, FONT_BLACK, NAVY, TEAL, YEL, WHITE
A = f'{G}/a107'; T = f'{A}/tmp'; os.makedirs(T, exist_ok=True)
W, H, FPS = 1080, 1920, 30
RED, GREEN, SKIN, GRAY = (226, 46, 46), (40, 170, 90), (214, 160, 120), (150, 156, 160)
BG = (246, 245, 240)

def ease(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def back(x):  # sale con rebote
    x = min(max(x, 0.0), 1.0); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------------------------------------------------------------- recursos
PROD = Image.open(f'{G}/v2frames/producto_cut.png').convert('RGBA')
TUBE = PROD.crop((0, 0, 262, PROD.height)); _a = np.array(TUBE.getchannel('A'))
_a[:, 252:] = (_a[:, 252:] * np.linspace(1, 0, _a.shape[1] - 252)[None, :]).astype(np.uint8)
TUBE.putalpha(Image.fromarray(_a)); TUBE = TUBE.crop(TUBE.getbbox())
def scaled(im, h): return im.resize((max(1, int(im.width * h / im.height)), int(h)), Image.LANCZOS)

_blob = Image.new('L', (900, 900), 0); ImageDraw.Draw(_blob).ellipse([150, 150, 750, 750], fill=255); _blob = _blob.filter(ImageFilter.GaussianBlur(120))
def background(t, tint=None):
    im = Image.new('RGB', (W, H), BG)
    for (bx, by, ax, ay, sp, col, a) in ((200, 500, 120, 90, 0.35, TEAL, 0.18), (880, 1400, 110, 140, 0.28, YEL, 0.22), (700, 300, 90, 80, 0.4, (160, 210, 230), 0.25)):
        x = int(bx + ax * math.sin(t * sp * 2 * math.pi)) - 450; y = int(by + ay * math.cos(t * sp * 2 * math.pi)) - 450
        layer = Image.new('RGB', (900, 900), col); im.paste(layer, (x, y), _blob.point(lambda v: int(v * a)))
    if tint is not None:
        col, a = tint; im = Image.blend(im, Image.new('RGB', (W, H), col), a)
    im = im.convert('RGBA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    for (x0, y0, r, v, ph, col) in PARTS:   # burbujas/minerales que suben todo el tiempo: el fondo nunca queda quieto
        y = (y0 - v * t) % (H + 200) - 100; x = x0 + 40 * math.sin(t * 1.3 + ph)
        dd.ellipse([x - r, y - r, x + r, y + r], fill=col)
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))
    return im

_pr = random.Random(7)
PARTS = [(_pr.uniform(0, W), _pr.uniform(0, H), _pr.uniform(14, 42), _pr.uniform(160, 360), _pr.uniform(0, 6),
          (TEAL + (95,)) if k % 3 == 0 else ((YEL + (110,)) if k % 3 == 1 else (160, 210, 230, 130))) for k in range(34)]

def paste(im, src, cx, cy, scale=1.0, angle=0.0, alpha=1.0):
    s = src
    if scale != 1.0: s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.LANCZOS)
    if angle: s = s.rotate(angle, expand=True, resample=Image.BICUBIC)
    if alpha < 1.0:
        a = s.getchannel('A').point(lambda v: int(v * alpha)); s = s.copy(); s.putalpha(a)
    im.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

def shadow_under(im, cx, base, w):
    sh = Image.new('L', (int(w * 1.2), 60), 0); ImageDraw.Draw(sh).ellipse([10, 10, int(w * 1.2) - 10, 50], fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(14)); lay = Image.new('RGBA', sh.size, (40, 40, 50, 255)); lay.putalpha(sh)
    im.alpha_composite(lay, (int(cx - sh.width / 2), int(base - 30)))

def product(im, cx, cy, h, angle=0.0, tube=False, shadow=True):
    p = scaled(TUBE if tube else PROD, h)
    if shadow and not angle: shadow_under(im, cx, cy + h / 2, p.width)
    paste(im, p, cx, cy, angle=angle)
    return p.width

def bob(t, amp=7, f=0.45): return amp * math.sin(2 * math.pi * f * t)

def shine(im, t, cx, cy, h, period=2.2, t0=0.6, tube=False):
    src = scaled(TUBE if tube else PROD, h); u = ((t - t0) % period) / 0.6
    if t < t0 or u > 1: return
    lay = Image.new('L', (W, H), 0); ld = ImageDraw.Draw(lay)
    c = cx - src.width / 2 - 150 + u * (src.width + 300)
    ld.polygon([(c, cy - h / 2), (c + 70, cy - h / 2), (c - 80, cy + h / 2), (c - 150, cy + h / 2)], fill=int(120 * math.sin(math.pi * u)))
    pm = Image.new('L', (W, H), 0); pm.paste(src.getchannel('A'), (int(cx - src.width / 2), int(cy - h / 2)))
    lay = Image.fromarray(np.minimum(np.array(lay), np.array(pm))).filter(ImageFilter.GaussianBlur(8))
    wl = Image.new('RGBA', (W, H), (255, 255, 255, 255)); wl.putalpha(lay); im.alpha_composite(wl)

def big_x(size, width=None):
    S = 2; s = size * S; w = width or int(s * 0.17)
    im = Image.new('RGBA', (s + 60, s + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im); o = 30
    for col, ww in (((255, 255, 255, 255), w + 26), (RED + (255,), w)):
        d.line([o, o, o + s, o + s], fill=col, width=ww); d.line([o + s, o, o, o + s], fill=col, width=ww)
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)
X300 = big_x(300)

def make_arm():   # antebrazo con volumen (degradado y sombra suave), sin marcas
    w, h = 1300, 230; g = np.zeros((h, w, 4), np.uint8)
    y = np.linspace(-1, 1, h)[:, None]; shade = 1.0 - 0.22 * (y ** 2) - 0.08 * y
    for k, c in enumerate(SKIN): g[..., k] = np.clip(c * shade, 0, 255)
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w, h], 115, fill=255)
    g[..., 3] = np.array(m); arm = Image.fromarray(g, 'RGBA')
    out = Image.new('RGBA', (w + 80, h + 80), (0, 0, 0, 0)); sh = Image.new('RGBA', (w, h), (60, 40, 30, 70)); sh.putalpha(m.point(lambda v: v * 70 // 255))
    out.alpha_composite(sh, (40, 60)); out = out.filter(ImageFilter.GaussianBlur(14)); out.alpha_composite(arm, (40, 40))
    return out.rotate(-6, expand=True, resample=Image.BICUBIC)
ARM = make_arm()

def badge(text, col=RED, size=92):
    return box_text(text, size, WHITE, col, maxw=860, pad=(40, 20))

def emoji(e, size=200):
    return render_runs(e, size, WHITE, FONT_BLACK)

def shake(t, t0, amp=18, d=0.35):
    u = t - t0
    if 0 <= u < d:
        a = amp * (1 - u / d) ** 2; return a * math.sin(u * 90), a * math.cos(u * 70)
    return 0.0, 0.0

def write(name, dur, fn):
    nf = round(dur * FPS); out = f'{T}/mg_{name}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-frames:v', str(nf), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', '-an', out], stdin=subprocess.PIPE)
    for k in range(nf):
        im = fn(k / FPS, dur)
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('ok', out, dur)

def offset(im, dx, dy):
    if not dx and not dy: return im
    out = Image.new('RGBA', im.size, BG + (255,)); out.alpha_composite(im, (int(dx), int(dy))); return out

# ---------------------------------------------------------------- escenas
def s_ha(t, d):   # tres X rojas caen alrededor de la piedra (sin tapar la etiqueta)
    im = background(t); pts = [(0.25, 215, 1060, -12), (0.75, 865, 1060, 10), (1.25, 540, 1615, 0)]
    dx = dy = 0
    for t0, *_ in pts:
        a, b = shake(t, t0 + 0.18); dx += a; dy += b
    product(im, 540, 1130 + bob(t), 640, tube=True, shadow=True)
    for t0, x, y, rot in pts:
        u = (t - t0) / 0.18
        if u < 0: continue
        yy = -300 + (y + 300) * ease(min(1, u)); sc = 1.5 - 0.5 * ease(min(1, u)) + (0.06 * math.exp(-8 * (t - t0 - 0.18)) + 0.06 * math.sin((t - t0) * 7) if u >= 1 else 0)
        paste(im, X300, x, yy, scale=sc, angle=rot * (1 - min(1, u)))
    return offset(im, dx, dy)

def s_hb(t, d):   # alarma roja: sirena con haces que giran + destello rojo
    pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 2.2)
    im = background(t, tint=(RED, 0.10 + 0.18 * pulse))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    cx, cy = 540, 700
    for k in range(2):
        a0 = (t * 260 + k * 180) % 360
        dd.pieslice([cx - 900, cy - 900, cx + 900, cy + 900], a0 - 14, a0 + 14, fill=(255, 80, 60, int(70 + 60 * pulse)))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6)))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([cx - 150, cy + 80, cx + 150, cy + 130], 18, fill=(60, 60, 70))
    dd.pieslice([cx - 130, cy - 130, cx + 130, cy + 130], 180, 360, fill=(int(200 + 55 * pulse), 30, 30))
    dd.rectangle([cx - 130, cy, cx + 130, cy + 85], fill=(int(200 + 55 * pulse), 30, 30))
    dd.ellipse([cx - 60, cy - 80, cx - 20, cy - 20], fill=(255, 220, 220))
    sx, sy = 8 * math.sin(t * 40), 0
    product(im, 540 + sx, 1300, 520)
    return im

def s_b1(t, d):   # ERROR 1: seca -> raspa sobre el brazo, chispas (el brazo queda limpio)
    im = background(t); dd = ImageDraw.Draw(im)
    paste(im, ARM, 540, 1290)
    x = 540 + 210 * math.sin(t * 2 * math.pi * 1.6)
    tip = (x - 250, 1225)
    product(im, x, 1150, 430, angle=90, tube=True, shadow=False)
    rnd = random.Random(int(t * FPS)); dd = ImageDraw.Draw(im)
    for _ in range(14):   # chispas de fricción
        ang = rnd.uniform(-2.6, -0.5); r = rnd.uniform(20, 120)
        px, py = tip[0] + r * math.cos(ang), tip[1] + r * math.sin(ang)
        dd.line([tip[0], tip[1], px, py], fill=(255, rnd.randint(150, 220), 40), width=rnd.randint(3, 6))
    paste(im, badge('ERROR 1: SECA', size=84), 540, 560, scale=back((t - 0.05) / 0.3) if t < 0.35 else 1.0 + 0.03 * math.sin(t * 6))
    return im

def s_b2(t, d):   # gotas caen SOLO en la punta de la piedra y brilla
    im = background(t); h = 640; cy = 1170 + bob(t); pw = product(im, 540, cy, h)
    top = cy - h / 2 + 18; dd = ImageDraw.Draw(im)
    tipx = 540 - pw * 0.27
    for k in range(int(d / 0.28) + 1):
        t0 = 0.1 + k * 0.28; u = (t - t0) / 0.45
        if 0 <= u < 1:
            y = 320 + (top - 320) * u * u
            dd.ellipse([tipx - 16, y - 26, tipx + 16, y + 18], fill=(90, 170, 230))
            dd.ellipse([tipx - 7, y - 14, tipx + 1, y - 2], fill=(220, 240, 255))
        v = (t - t0 - 0.45) / 0.25
        if 0 <= v < 1:
            for s in (-1, 1):
                dd.ellipse([tipx + s * 40 * v - 7, top - 30 * v * (1 - v) * 4 - 7, tipx + s * 40 * v + 7, top - 30 * v * (1 - v) * 4 + 7], fill=(120, 190, 240))
    g = (t % 1.0) / 0.4
    if g <= 1:   # destello en la piedra mojada
        a = math.sin(math.pi * g); r = 60 * a
        dd.line([tipx - r, top + 30, tipx + r, top + 30], fill=(255, 255, 255), width=5)
        dd.line([tipx, top + 30 - r, tipx, top + 30 + r], fill=(255, 255, 255), width=5)
    return im

CAL_RED = {3, 4, 10, 16, 17, 24}
def calendar(im, t, d, mode):
    x0, y0, cw, ch = 130, 800, 117, 116; dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([x0 - 30, y0 - 130, x0 + 7 * cw + 30, y0 + 4 * ch + 30], 40, fill=(255, 255, 255), outline=(220, 220, 215), width=4)
    dd.rounded_rectangle([x0 - 30, y0 - 130, x0 + 7 * cw + 30, y0 - 40], 40, fill=NAVY)
    f = ImageFont.truetype(FONT_BLACK, 40)
    for i, l in enumerate('LMMJVSD'):
        dd.text((x0 + i * cw + cw / 2, y0 - 85), l, font=f, fill=(255, 255, 255), anchor='mm')
    n = 28; speed = (d - 0.3) / n
    for i in range(n):
        cx, cy = x0 + (i % 7) * cw + cw / 2, y0 + (i // 7) * ch + ch / 2
        dd.rounded_rectangle([cx - 48, cy - 48, cx + 48, cy + 48], 18, fill=(244, 244, 240))
        u = (t - 0.15 - i * speed) / 0.18
        if u >= 0:
            s = back(min(1, u))
            if mode == 'huecos' and (i + 1) in CAL_RED:
                dd.rounded_rectangle([cx - 48 * s, cy - 48 * s, cx + 48 * s, cy + 48 * s], 18, fill=(255, 225, 225), outline=RED, width=5)
                dd.line([cx - 22 * s, cy - 22 * s, cx + 22 * s, cy + 22 * s], fill=RED, width=9); dd.line([cx + 22 * s, cy - 22 * s, cx - 22 * s, cy + 22 * s], fill=RED, width=9)
            else:
                dd.rounded_rectangle([cx - 48 * s, cy - 48 * s, cx + 48 * s, cy + 48 * s], 18, fill=(220, 245, 228))
                dd.line([cx - 24 * s, cy, cx - 6 * s, cy + 20 * s, cx + 26 * s, cy - 20 * s], fill=GREEN, width=10, joint='curve')

def s_b3(t, d):
    im = background(t); calendar(im, t, d, 'huecos')
    paste(im, badge('ERROR 2'), 540, 340, scale=back((t - 0.05) / 0.3) if t < 0.35 else 1.0 + 0.03 * math.sin(t * 6)); return im

def s_b5(t, d):
    im = background(t); calendar(im, t, d, 'completo'); rnd = random.Random(5); dd = ImageDraw.Draw(im)
    if t > d * 0.6:
        for _ in range(60):
            x0 = rnd.uniform(80, 1000); v = rnd.uniform(300, 700); c = rnd.choice([TEAL, YEL, GREEN, RED])
            y = 400 + (t - d * 0.6) * v + rnd.uniform(-200, 0); dd.rectangle([x0, y, x0 + 16, y + 26], fill=c)
    return im

def s_b4(t, d):   # comentario de foro (parafraseado, sin marca ni cliente)
    im = background(t); u = ease(t / 0.4); y = 900 + (1 - u) * 600
    card = Image.new('RGBA', (900, 470), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, 900, 470], 40, fill=(255, 255, 255), outline=(215, 215, 210), width=4)
    cd.ellipse([40, 40, 130, 130], fill=(200, 205, 210)); cd.ellipse([68, 58, 102, 92], fill=(255, 255, 255))
    f1 = ImageFont.truetype(FONT_BLACK, 40); f2 = ImageFont.truetype(FONT_BLACK, 58)
    cd.text((155, 62), 'Comentario en un foro', font=f1, fill=(120, 125, 130))
    full = '"Si la dejo 2 días, vuelve el olor"'; n = int(len(full) * min(1, max(0, (t - 0.35) / 1.4)))
    txt = full[:n]; words = txt.split(' '); lines, cur = [], ''
    for w in words:
        if cd.textlength((cur + ' ' + w).strip(), font=f2) > 800: lines.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    lines.append(cur)
    for i, ln in enumerate(lines): cd.text((50, 170 + i * 76), ln, font=f2, fill=NAVY)
    votes = int(120 + 228 * min(1, max(0, (t - 0.6) / (d - 0.8))))
    cd.polygon([(60, 430), (85, 395), (110, 430)], fill=(255, 120, 40)); cd.text((125, 412), f'{votes}', font=f1, fill=(255, 120, 40), anchor='lm')
    im.alpha_composite(card.rotate(1.5 * math.sin(t * 2.2), expand=True, resample=Image.BICUBIC), (80, int(y + 10 * math.sin(t * 2.6))))
    return im

def s_b6(t, d):   # ERROR 3: guardada mojada en la ducha
    im = background(t, tint=((150, 180, 200), 0.18)); dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([640, 330, 900, 380], 20, fill=(150, 155, 160)); dd.rounded_rectangle([860, 250, 900, 380], 15, fill=(150, 155, 160))
    dd.ellipse([600, 360, 800, 440], fill=(170, 175, 180))
    rnd = random.Random(int(t * FPS))
    for _ in range(140):
        x = rnd.uniform(540, 880); y = 440 + ((t * 1400 + rnd.uniform(0, 1400)) % 1100)
        dd.line([x - (y - 440) * 0.25, y, x - (y - 440) * 0.25 - 6, y + 40], fill=(110, 170, 220), width=4)
    dd.rounded_rectangle([200, 1460, 880, 1500], 12, fill=(170, 160, 150))
    h = 560; pw = product(im, 540, 1460 - h / 2, h, shadow=False)
    rnd2 = random.Random(3)
    for _ in range(26):   # gotas sobre el tubo
        x = 540 + rnd2.uniform(-pw / 2 + 20, pw / 2 - 20); y = 1460 - h + rnd2.uniform(60, h - 40)
        dd.ellipse([x - 8, y - 11, x + 8, y + 11], fill=(150, 200, 235)); dd.ellipse([x - 4, y - 8, x, y - 3], fill=(235, 245, 255))
    paste(im, badge('ERROR 3'), 330, 560, scale=back((t - 0.05) / 0.3) if t < 0.35 else 1.0 + 0.03 * math.sin(t * 6))
    return im

def s_b7(t, d):   # zoom a la piedra y grieta animada
    im = background(t); z = 2.4 + 0.15 * t / d
    p = scaled(PROD, 620 * z); top = PROD.crop((0, 0, 262, 230)); top = top.resize((int(262 * z * 620 / 603 * 1.0), int(230 * z * 620 / 603)), Image.LANCZOS)
    dx, dy = shake(t, 0.35, 22, 0.45)
    paste(im, top, 540 + dx, 1000 + dy)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    pts = [(420, 760), (480, 860), (455, 930), (540, 1010), (520, 1080), (610, 1160), (600, 1230)]
    br = [[(480, 860), (560, 880), (600, 850)], [(540, 1010), (460, 1060)], [(610, 1160), (680, 1150)]]
    u = min(1, max(0, (t - 0.3) / 0.35)); n = max(2, int(len(pts) * u))
    if t >= 0.3:
        dd.line([(x + dx, y + dy) for x, y in pts[:n]], fill=(60, 60, 70, 255), width=9, joint='curve')
        dd.line([(x + dx + 4, y + dy) for x, y in pts[:n]], fill=(255, 255, 255, 200), width=3)
        if u >= 1:
            for b in br: dd.line([(x + dx, y + dy) for x, y in b], fill=(60, 60, 70, 255), width=6)
    im.alpha_composite(lay); dd = ImageDraw.Draw(im); fr = random.Random(11)
    for k in range(18):   # fragmentos que se desprenden de la grieta
        t0 = 0.6 + fr.uniform(0, 1.2); u = t - t0
        if u > 0:
            x, y0 = pts[fr.randint(1, 6)]; x += dx + fr.uniform(-20, 20) + 60 * u * fr.choice([-1, 1]); y = y0 + dy + 900 * u * u
            r = fr.uniform(6, 14); dd.polygon([(x - r, y), (x, y - r), (x + r * 0.8, y + r * 0.4)], fill=(235, 235, 232), outline=(190, 190, 188))
    if t > 0.55: paste(im, emoji('💔', 200), 840, 420, scale=back((t - 0.55) / 0.3) if t < 0.85 else 1.0)
    return im

ICONS = [('💧', 'Mojar'), ('✋', 'Aplicar'), ('💨', 'Secar'), (None, 'Guardar')]   # 4: el producto real tapado
def s_b8(t, d):
    im = background(t); f = ImageFont.truetype(FONT_BLACK, 58)
    times = [0.05, 0.75, 1.55, 2.3]
    for i, ((e, lab), t0) in enumerate(zip(ICONS, times)):
        cx, cy = (300 if i % 2 == 0 else 780), (760 if i < 2 else 1160)
        u = (t - t0) / 0.3
        if u < 0: continue
        s = back(min(1, u)); tile = Image.new('RGBA', (400, 360), (0, 0, 0, 0)); td = ImageDraw.Draw(tile)
        td.rounded_rectangle([0, 0, 400, 360], 50, fill=(255, 255, 255), outline=TEAL, width=8)
        ic = emoji(e, 150) if e else scaled(PROD, 190); tile.alpha_composite(ic, ((400 - ic.width) // 2, 40 if e else 30))
        td.text((200, 300), f'{i + 1}. {lab}', font=f, fill=NAVY, anchor='mm')
        paste(im, tile, cx, cy + 6 * math.sin(t * 3 + i), scale=s * (1 + 0.015 * math.sin(t * 4 + i)))
    return im

def s_b10(t, d):   # sello de garantía 14 días + producto real con brillo
    im = background(t); h = 560; py = 1340 + bob(t); product(im, 540, py, h); shine(im, t, 540, py, h)
    seal = Image.new('RGBA', (520, 520), (0, 0, 0, 0)); sd = ImageDraw.Draw(seal)
    sd.ellipse([0, 0, 520, 520], fill=TEAL + (255,)); sd.ellipse([24, 24, 496, 496], outline=(255, 255, 255, 255), width=8)
    for k in range(36):
        a = k * math.pi / 18; sd.ellipse([260 + 236 * math.cos(a) - 6, 260 + 236 * math.sin(a) - 6, 260 + 236 * math.cos(a) + 6, 260 + 236 * math.sin(a) + 6], fill=YEL + (255,))
    sd.text((260, 210), '14', font=ImageFont.truetype(FONT_BLACK, 190), fill=(255, 255, 255), anchor='mm')
    sd.text((260, 345), 'DÍAS', font=ImageFont.truetype(FONT_BLACK, 70), fill=YEL, anchor='mm')
    sd.text((260, 420), 'GARANTÍA', font=ImageFont.truetype(FONT_BLACK, 48), fill=(255, 255, 255), anchor='mm')
    u = (t - 0.1) / 0.3; dx, dy = shake(t, 0.4, 14, 0.3)
    if u >= 0:
        sc = 2.2 - 1.2 * ease(min(1, u)); ang = -25 * (1 - ease(min(1, u))) + 4 * math.sin(t * 2)
        paste(im, seal, 540 + dx, 640 + dy, scale=sc * 0.8, angle=ang, alpha=min(1, u * 2))
    return im

def generic_bottle(h=330):
    S = 2; b = Image.new('RGBA', (130 * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
    d.rounded_rectangle([20 * S, 40 * S, 110 * S, h * S - 2], 22 * S, fill=(190, 196, 202, 255))
    d.rounded_rectangle([38 * S, 0, 92 * S, 52 * S], 12 * S, fill=(150, 156, 162, 255))
    d.rounded_rectangle([30 * S, 110 * S, 100 * S, 200 * S], 10 * S, fill=(225, 228, 232, 255))
    return b.resize((130, h), Image.LANCZOS)
GB = generic_bottle()

def s_b11(t, d):   # CTA: GEODA real junto a una fila de frascos genéricos tachados
    im = background(t); py = 1180 + bob(t); product(im, 290, py, 640); shine(im, t, 290, py, 640, t0=1.6)
    for i in range(6):
        cx, cy = 620 + (i % 3) * 150, 980 + (i // 3) * 400
        paste(im, GB, cx, cy, scale=1.0 + 0.02 * math.sin(t * 3 + i))
        u = (t - 0.25 - i * 0.22) / 0.2
        if u >= 0:
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay); v = ease(min(1, u))
            dd.line([cx - 75, cy - 170, cx - 75 + 150 * v, cy - 170 + 340 * v], fill=(255, 255, 255, 255), width=24)
            dd.line([cx - 75, cy - 170, cx - 75 + 150 * v, cy - 170 + 340 * v], fill=RED + (255,), width=14)
            im.alpha_composite(lay)
    return im

def s_b9(t, d):   # (no se usa: el plano real va con el clip k_tapa del kit)
    return background(t)

SCENES = dict(ha=s_ha, hb=s_hb, b1=s_b1, b2=s_b2, b3=s_b3, b4=s_b4, b5=s_b5, b6=s_b6, b7=s_b7, b8=s_b8, b10=s_b10, b11=s_b11)

def sfx():
    o = f'{G}/audio'
    def mk(name, expr, dur, af=None):
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f"aevalsrc='{expr}':s=48000:d={dur}"]
        if af: cmd += ['-af', af]
        subprocess.run(cmd + [f'{o}/{name}.wav'], check=True)
    mk('sfx_alarma', '0.30*sin(2*PI*(700+250*sin(2*PI*2.2*t))*t)', 3.0, 'afade=t=out:st=2.5:d=0.5')
    mk('sfx_crack', '0.9*(random(0)-0.5)*exp(-35*t)+0.6*sin(2*PI*90*t)*exp(-20*t)', 0.5)
    mk('sfx_drip', '0.35*sin(2*PI*(1300-900*t)*t)*exp(-25*t)', 0.25)
    mk('sfx_scratch', '0.5*(random(0)-0.5)*(0.6+0.4*sin(2*PI*10*t))', 1.6, 'highpass=f=1800,afade=t=in:d=0.05,afade=t=out:st=1.3:d=0.3')
    mk('sfx_type', '0.4*(random(0)-0.5)*exp(-80*mod(t,0.09))', 1.4, 'highpass=f=2500')
    mk('sfx_chime', '0.25*(sin(2*PI*1319*t)+sin(2*PI*1760*t)+0.6*sin(2*PI*2637*t))*exp(-3*t)', 1.2)
    print('sfx ok')

if __name__ == '__main__':
    if sys.argv[1] == 'sfx': sfx()
    elif sys.argv[1] == 'todas':
        durs = json.load(open(sys.argv[2]))
        for k, v in durs.items(): write(k, v, SCENES[k])
    else:
        write(sys.argv[1], float(sys.argv[2]), SCENES[sys.argv[1]])
