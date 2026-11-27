#!/usr/bin/env python3
"""A3-08 · tarjetas del ranking sobre las tomas de la presentadora (como el reel de referencia):
producto en tarjeta blanca abajo a la izquierda + nota 'X/10' a la derecha (GEODA: recorte REAL y 10/10 en verde con destellos).
En el cierre la nota se cambia por el botón 'Comprar' y una mano 👇 que señala hacia abajo ("si ves el botón aquí abajo").
uso (desde build): componer(toma.mp4, salida.mp4, eventos) con eventos = [(t0, t1, producto, nota|'cta'|'cta_regalo'), ...]"""
import os, sys, math, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102'); sys.path.insert(0, G)
from build_a102 import render_runs, FONT_BLACK, NAVY, TEAL, YEL, WHITE
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
W, H, FPS = 1080, 1920, 30
CX0, CY0, CW = 70, 930, 300            # tarjeta del producto (x, y, lado)
BX, BY = 815, 1060                     # centro de la nota
GREEN = (24, 160, 90)

def _photo(name):
    if name == 'geoda':
        return Image.open(f'{KIT}/producto/producto_cut.png').convert('RGBA')
    src = {'aerosol': f'{G}/hf/c_b1_0.png', 'barra': f'{G}/hf/r_barra_0.png', 'rollon': f'{G}/hf/r_rollon_0.png'}[name]
    im = Image.open(src).convert('RGB')
    if name == 'aerosol':   # recorte del aerosol genérico (A2-06) centrado
        w, h = im.size; im = im.crop((int(w * 0.28), int(h * 0.22), int(w * 0.72), int(h * 0.80)))
    else:
        w, h = im.size; im = im.crop((int(w * 0.12), int(h * 0.18), int(w * 0.88), int(h * 0.86)))
    return im.convert('RGBA')

def card(name, bow=False):
    S = 2; c = Image.new('RGBA', ((CW + 40) * S, (CW + 40) * S), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle([20 * S, 28 * S, (CW + 20) * S, (CW + 28) * S], 34 * S, fill=(0, 0, 0, 70))
    c = c.filter(ImageFilter.GaussianBlur(10)); d = ImageDraw.Draw(c)
    d.rounded_rectangle([20 * S, 20 * S, (CW + 20) * S, (CW + 20) * S], 34 * S, fill=(255, 255, 255, 255))
    p = _photo(name); box = (CW - 36) * S; p.thumbnail((box, box), Image.LANCZOS)
    c.alpha_composite(p, (20 * S + (CW * S - p.width) // 2, 20 * S + (CW * S - p.height) // 2))
    if bow:
        b = Image.open(f'{KIT}/producto/mono_rojo.png').convert('RGBA'); b = b.resize((150 * S, int(150 * S * b.height / b.width)), Image.LANCZOS)
        c.alpha_composite(b, ((CW - 120) * S, 0))
    return c.resize((c.width // S, c.height // S), Image.LANCZOS)

def badge(nota):
    hi = nota.startswith('10'); S = 2; w, h = 236, 124
    im = Image.new('RGBA', ((w + 30) * S, (h + 30) * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([15 * S, 22 * S, (w + 15) * S, (h + 22) * S], 30 * S, fill=(0, 0, 0, 60))
    im = im.filter(ImageFilter.GaussianBlur(8)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([15 * S, 15 * S, (w + 15) * S, (h + 15) * S], 30 * S, fill=(GREEN + (255,)) if hi else (255, 255, 255, 240))
    d.text(((w // 2 + 15) * S, (h // 2 + 15) * S), nota, font=ImageFont.truetype(FONT_BLACK, 86 * S), fill=(WHITE + (255,)) if hi else (20, 24, 32, 255), anchor='mm')
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)

def button(scale=1.0):
    w, h = int(330 * scale), int(104 * scale); S = 2
    im = Image.new('RGBA', (w * S + 40, h * S + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 26, 20 + w * S, 26 + h * S], h * S // 2, fill=(0, 0, 0, 60))
    d.rounded_rectangle([20, 14, 20 + w * S, 14 + h * S], h * S // 2, fill=(18, 160, 140, 255))
    t = render_runs('Comprar', int(56 * scale * S), WHITE, FONT_BLACK); im.alpha_composite(t, (20 + (w * S - t.width) // 2, 14 + (h * S - t.height) // 2))
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)
HAND = render_runs('👇', 96, WHITE, FONT_BLACK)

def back(u, s=1.7):
    u = max(0.0, min(1.0, u)) - 1; return 1 + (s + 1) * u ** 3 + s * u ** 2

def paste(im, sp, cx, cy, sc=1.0):
    if sc <= 0.02: return
    s = sp.resize((max(1, int(sp.width * sc)), max(1, int(sp.height * sc))), Image.LANCZOS)
    im.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

def componer(src, out, eventos):
    cache = {}
    def get(k, f):
        if k not in cache: cache[k] = f()
        return cache[k]
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-vf', f'scale={W}:{H}:flags=lanczos,fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', src,
                            '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', out], stdin=subprocess.PIPE)
    k = 0
    while True:
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: break
        t = k / FPS; im = Image.fromarray(np.frombuffer(raw, np.uint8).reshape(H, W, 3)).convert('RGBA')
        for ev in eventos:
            t0, t1, prod, nota = ev[:4]; tb = ev[4] if len(ev) > 4 and ev[4] is not None else t0 + 0.18; pop = ev[5] if len(ev) > 5 else True
            if not (t0 <= t < t1): continue
            u = (t - t0) / 0.28; sc_in = (back(u) if u < 1 else 1.0) if pop else 1.0
            sc_out = min(1.0, (t1 - t) / 0.15)
            cd = get(('c', prod, nota == 'cta_regalo'), lambda: card(prod, bow=(nota == 'cta_regalo')))
            paste(im, cd, CX0 + CW / 2 + 20, CY0 + CW / 2 + 20, min(sc_in, sc_out) * (1 + 0.015 * math.sin(t * 3)))
            if nota.startswith('cta'):
                v = (t - t0 - 0.2) / 0.3
                if v > 0:
                    sc = (back(v) if v < 1 else 1.0) * (1 + 0.035 * math.sin(t * 6)) * sc_out
                    paste(im, get('btn', button), BX - 40, BY - 10, sc)
                    bob = 14 * abs(math.sin(t * 5)); paste(im, HAND, BX - 40, BY + 105 + bob, sc_out)
            else:
                v = (t - tb) / 0.28
                if v > 0:
                    bd = get(('b', nota), lambda: badge(nota))
                    pulse = 1 + (0.05 * math.sin(t * 6) if nota.startswith('10') else 0)
                    paste(im, bd, BX, BY, (back(v) if v < 1 else 1.0) * pulse * sc_out)
                    if nota.startswith('10'):
                        rnd = random.Random(int(t * 10)); dd = ImageDraw.Draw(im)
                        for _ in range(5):
                            a = rnd.uniform(0, 6.28); r = rnd.uniform(130, 170); x, y = BX + r * math.cos(a), BY + 0.6 * r * math.sin(a); s = rnd.uniform(6, 13)
                            dd.line([x - s, y, x + s, y], fill=(255, 236, 150, 255), width=4); dd.line([x, y - s, x, y + s], fill=(255, 236, 150, 255), width=4)
        enc.stdin.write(im.convert('RGB').tobytes()); k += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    return out

if __name__ == '__main__':   # prueba visual sobre la imagen del set
    import json
    T = f'{G}/a308/tmp'; os.makedirs(T, exist_ok=True)
    base = Image.open(f'{G}/hf/r_set_0.png').convert('RGBA').resize((W, H))
    for i, (p, n) in enumerate([('aerosol', '4/10'), ('barra', '5/10'), ('rollon', '6/10'), ('geoda', '10/10')]):
        im = base.copy(); paste(im, card(p), CX0 + CW / 2 + 20, CY0 + CW / 2 + 20); paste(im, badge(n), BX, BY); im.convert('RGB').resize((360, 640)).save(f'{T}/prev_{i}.png')
    im = base.copy(); paste(im, card('geoda', True), CX0 + CW / 2 + 20, CY0 + CW / 2 + 20); paste(im, button(), BX - 40, BY - 10); paste(im, HAND, BX - 40, BY + 105)
    im.convert('RGB').resize((360, 640)).save(f'{T}/prev_4.png')
    c = Image.new('RGB', (360 * 5, 640))
    for i in range(5): c.paste(Image.open(f'{T}/prev_{i}.png'), (i * 360, 0))
    c.save(f'{G}/lab/tarjetas.jpg'); print('ok')
