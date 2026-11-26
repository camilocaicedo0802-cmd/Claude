#!/usr/bin/env python3
"""A2-03 · cierre K6 'Envío gratis a toda Colombia': mapa de Colombia (ilustración) con pines que se encienden ciudad por
ciudad y un camioncito que recorre la ruta, + el producto REAL (recorte de la landing) a la derecha con brillo.
Todo se mueve. Los textos los pone el montador (tarjeta CTA arriba). uso: mapa.py duración -> tmp/cta_mapa.mp4"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102')
from build_a102 import render_runs, FONT_BLACK, WHITE
W, H, FPS = 1080, 1920, 30
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
OUT = f'{G}/a203/tmp/cta_mapa.mp4'
BG = (252, 246, 236)
src = Image.open(f'{G}/hf/d_map_0.png').convert('RGB')
a = np.array(src).astype(int); bgc = a[5, 5]; m = (np.abs(a - bgc).sum(2) > 40)
mask = Image.fromarray((m * 255).astype(np.uint8)).crop((0, 103, 656, 1081))
mapa = src.crop((0, 103, 656, 1081)).convert('RGBA'); mapa.putalpha(mask)
S = 0.80; mapa = mapa.resize((int(mapa.width * S), int(mapa.height * S)), Image.LANCZOS); MX, MY = 40, 700
CITIES = [('Bogotá', 291, 538), ('Medellín', 179, 414), ('Cali', 123, 638), ('Barranquilla', 250, 190), ('Cartagena', 213, 224),
          ('Bucaramanga', 336, 392), ('Santa Marta', 302, 179), ('Pereira', 168, 526), ('Cúcuta', 392, 358), ('Villavicencio', 347, 582),
          ('Pasto', 90, 750), ('Neiva', 224, 672), ('Leticia', 459, 1053)]
P = [(MX + x * S, MY + (y - 103) * S) for _, x, y in CITIES]
prod = Image.open(f'{G}/v2frames/producto_cut.png').convert('RGBA')
tube = prod.crop((0, 0, 262, prod.height)); al = np.array(tube.getchannel('A'))
al[:, 252:] = (al[:, 252:] * np.linspace(1, 0, al.shape[1] - 252)[None, :]).astype(np.uint8); tube.putalpha(Image.fromarray(al)); tube = tube.crop(tube.getbbox())
PH = 600; tube = tube.resize((int(tube.width * PH / tube.height), PH), Image.LANCZOS); PX, PY = 770 - tube.width // 2, 960
TRUCK = render_runs('🚚', 120, WHITE, FONT_BLACK)
_blob = Image.new('L', (700, 700), 0); ImageDraw.Draw(_blob).ellipse([120, 120, 580, 580], fill=255); _blob = _blob.filter(ImageFilter.GaussianBlur(90))

def pin(scale):
    s = 2; w, h = int(46 * scale * s), int(64 * scale * s)
    im = Image.new('RGBA', (max(w, 2), max(h, 2)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, w, w], fill=(226, 46, 46, 255)); d.polygon([(w * 0.18, w * 0.75), (w * 0.82, w * 0.75), (w / 2, h)], fill=(226, 46, 46, 255))
    d.ellipse([w * 0.32, w * 0.32, w * 0.68, w * 0.68], fill=(255, 255, 255, 255))
    return im.resize((max(1, w // s), max(1, h // s)), Image.LANCZOS)

def frame(t):
    im = Image.new('RGB', (W, H), BG)
    for bx, by, ax, ay, sp, col in ((260, 420, 160, 110, 0.45, (170, 220, 215)), (900, 1500, 150, 170, 0.4, (255, 220, 150)), (620, 900, 180, 120, 0.35, (200, 230, 240))):
        x = int(bx + ax * math.sin(t * sp * 6.28)) - 350; y = int(by + ay * math.cos(t * sp * 6.28)) - 350
        im.paste(Image.new('RGB', (700, 700), col), (x, y), _blob.point(lambda v: int(v * 0.55)))
    im = im.convert('RGBA'); z = 1 + 0.10 * t / dur
    mp = mapa.resize((int(mapa.width * z), int(mapa.height * z)), Image.LANCZOS); im.alpha_composite(mp, (int(MX - (z - 1) * 200), int(MY - (z - 1) * 300)))
    d = ImageDraw.Draw(im)
    # ruta del camión: Bogotá -> ciudades en orden
    for i, (x, y) in enumerate(P):
        t0 = 0.15 + i * 0.28; u = (t - t0) / 0.25
        if u < 0: continue
        x = MX + (x - MX) * z - (z - 1) * 200; y = MY + (y - MY) * z - (z - 1) * 300
        if i > 0:
            px, py = P[0]; px = MX + (px - MX) * z - (z - 1) * 200; py = MY + (py - MY) * z - (z - 1) * 300
            v = min(1, u); d.line([(px, py), (px + (x - px) * v, py + (y - py) * v)], fill=(18, 160, 140, 150), width=3)
        r = (t - t0) % 1.2
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([x - 8 - 75 * r, y - 8 - 75 * r, x + 8 + 75 * r, y + 8 + 75 * r], outline=(226, 46, 46, int(190 * (1 - r / 1.2))), width=6); im.alpha_composite(ov)
        sc = (1.3 - 0.3 * min(1, u)) if u < 1 else 1.0
        if u < 1: sc *= min(1, u * 1.5)
        pn = pin((1.25 if i == 0 else 0.85) * max(sc, 0.05)); im.alpha_composite(pn, (int(x - pn.width / 2), int(y - pn.height)))
    # camioncito que va de ciudad en ciudad
    k = min(len(P) - 1, int(t / 0.45)); f = (t / 0.45) % 1 if k < len(P) - 1 else 1
    (x0, y0), (x1, y1) = P[k], P[min(k + 1, len(P) - 1)]
    tx = MX + (x0 + (x1 - x0) * f - MX) * z - (z - 1) * 200; ty = MY + (y0 + (y1 - y0) * f - MY) * z - (z - 1) * 300
    im.alpha_composite(TRUCK, (int(tx - TRUCK.width / 2), int(ty - TRUCK.height - 30)))
    # producto real con sombra y brillo que barre
    sh = Image.new('L', (tube.width + 120, 70), 0); ImageDraw.Draw(sh).ellipse([10, 10, tube.width + 110, 60], fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(16)); lay = Image.new('RGBA', sh.size, (60, 50, 40, 255)); lay.putalpha(sh)
    bob = 14 * math.sin(t * 2.6); im.alpha_composite(lay, (PX - 60, PY + PH - 30)); im.alpha_composite(tube, (PX, int(PY + bob)))
    u = ((t - 0.8) % 2.0) / 0.6
    if t > 0.8 and u <= 1:
        L = Image.new('L', (W, H), 0); c = PX - 120 + u * (tube.width + 240)
        ImageDraw.Draw(L).polygon([(c, PY), (c + 60, PY), (c - 70, PY + PH), (c - 130, PY + PH)], fill=int(120 * math.sin(math.pi * u)))
        pm = Image.new('L', (W, H), 0); pm.paste(tube.getchannel('A'), (PX, int(PY + bob)))
        L = Image.fromarray(np.minimum(np.array(L), np.array(pm))).filter(ImageFilter.GaussianBlur(8))
        wl = Image.new('RGBA', (W, H), (255, 255, 255, 255)); wl.putalpha(L); im.alpha_composite(wl)
    return im.convert('RGB')

p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
for k in range(round(dur * FPS)): p.stdin.write(frame(k / FPS).tobytes())
p.stdin.close(); p.wait(); print('ok', OUT, 'producto', (PX, PY, PX + tube.width, PY + PH))
