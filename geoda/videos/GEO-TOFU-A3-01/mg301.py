#!/usr/bin/env python3
"""A3-01 · piezas locales (sin costo):
  nubes (B3): el frasco genérico (foto del A2-06) con una nube gris 'olor' que sube y una nube rosada 'perfume' que la tapa.
  rebote (B6): GEODA real (recorte) cae sobre la cama y rebota sin daño.
uso: mg301.py nubes|rebote dur -> tmp/m31_<escena>.mp4"""
import os, sys, math, subprocess, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102'); sys.path.insert(0, G)
from build_a102 import render_runs, FONT_BLACK, WHITE
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
W, H, FPS = 1080, 1920, 30
T = f'{G}/a301/tmp'
ease = lambda u: 1 - (1 - max(0, min(1, u))) ** 3
def fill(im, z=1.0, fx=0.5, fy=0.5):
    w, h = int(W * z), int(H * z); b = im.resize((w, h), Image.LANCZOS); ox, oy = int((w - W) * fx), int((h - H) * fy); return b.crop((ox, oy, ox + W, oy + H))

FR = Image.open(f'{T}/frasco.png').convert('RGB').resize((W, H), Image.LANCZOS)
def cloud(col, r=260, seed=1, alpha=200):
    rnd = random.Random(seed); im = Image.new('RGBA', (r * 4, r * 3), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for _ in range(14):
        x = rnd.uniform(r * 0.8, r * 3.2); y = rnd.uniform(r * 0.9, r * 2.1); rr = rnd.uniform(r * 0.45, r * 0.8)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (alpha,))
    return im.filter(ImageFilter.GaussianBlur(28))
GRIS, ROSA = cloud((120, 120, 125), seed=3), cloud((255, 140, 190), seed=7, alpha=215)
def label(t, col):
    return render_runs(t, 70, col, FONT_BLACK, stroke=8, stroke_color=(30, 30, 40))
L_OLOR, L_PERF = label('olor', (230, 230, 230)), label('perfume', (255, 205, 225))
def s_nubes(t, d):
    im = fill(FR, 1.0 + 0.28 * t / d, 0.5, 0.42).convert('RGBA')
    u = ease(t / 0.6); y = 980 - 160 * u - 40 * t + 18 * math.sin(t * 3)
    g = GRIS.copy(); g.putalpha(g.getchannel('A').point(lambda a: int(a * min(1, u * 1.3)))); im.alpha_composite(g, (int(540 - g.width / 2), int(y - g.height / 2)))
    if u > 0.5: im.alpha_composite(L_OLOR, (int(540 - L_OLOR.width / 2), int(y - 40)))
    v = ease((t - 0.9) / 0.7)
    if v > 0:
        yy = 1300 - 470 * v - 30 * t + 20 * math.sin(t * 3.4); sc = 0.7 + 0.45 * v + 0.08 * t
        p = ROSA.resize((int(ROSA.width * sc), int(ROSA.height * sc)), Image.LANCZOS); im.alpha_composite(p, (int(560 - p.width / 2), int(yy - p.height / 2)))
        if v > 0.6: im.alpha_composite(L_PERF, (int(560 - L_PERF.width / 2), int(yy - 30)))
    return im.convert('RGB')

CAMA = Image.open(f'{T}/cama.png').convert('RGB').resize((W, H), Image.LANCZOS)
STICK = Image.open(f'{KIT}/producto/producto_cut.png').convert('RGBA').crop((0, 0, 253, 603))
def s_rebote(t, d):
    im = fill(CAMA, 1.0 + 0.08 * t / d, 0.5, 0.6).convert('RGBA')
    h = 560; s = STICK.resize((int(STICK.width * h / STICK.height), h), Image.LANCZOS)
    base = 1400; t0 = 0.15; u = (t - t0) / 0.42
    if u < 1: y = base - h - 900 * (1 - max(0, u)) ** 2; ang = 35 * (1 - max(0, u))
    else:
        v = t - t0 - 0.42; y = base - h - 120 * math.exp(-5 * v) * abs(math.sin(v * 9)); ang = 6 * math.exp(-4 * v) * math.sin(v * 9)
    r = s.rotate(ang, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); k = max(0.3, 1 - (base - h - y) / 900)
    ImageDraw.Draw(sh).ellipse([540 - 150 * k, base - 18, 540 + 150 * k, base + 22], fill=(0, 0, 0, int(110 * k))); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    im.alpha_composite(r, (int(540 - r.width / 2), int(y)))
    return im.convert('RGB')

SC = dict(nubes=s_nubes, rebote=s_rebote)
if __name__ == '__main__':
    name, dur = sys.argv[1], float(sys.argv[2]); n = round(dur * FPS); out = f'{T}/m31_{name}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(n): p.stdin.write(SC[name](k / FPS, dur).tobytes())
    p.stdin.close(); p.wait(); print('ok', out, dur)
