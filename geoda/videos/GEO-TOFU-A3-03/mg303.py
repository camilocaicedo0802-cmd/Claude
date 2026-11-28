#!/usr/bin/env python3
"""A3-03 · piezas locales (sin costo):
  bacterias (B2): gota de sudor transparente (sin olor) vs puntitos verdes de bacterias que aparecen y forman la nube de olor.
  boca_abajo (B4): GEODA real (recorte) gira y queda boca abajo; no cae nada (contraste: gota de un frasco genérico que sí gotea).
uso: mg303.py bacterias|boca_abajo dur -> tmp/m33_<escena>.mp4"""
import os, sys, math, subprocess, random
from PIL import Image, ImageDraw, ImageFilter
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102'); sys.path.insert(0, G)
from build_a102 import render_runs, FONT_BLACK, WHITE
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
W, H, FPS = 1080, 1920, 30
T = f'{G}/a303/tmp'
ease = lambda u: 1 - (1 - max(0, min(1, u))) ** 3
def bg(t, top=(238, 246, 248), bot=(214, 232, 238)):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    for y in range(0, H, 8): k = y / H; d.rectangle([0, y, W, y + 8], fill=tuple(int(top[i] * (1 - k) + bot[i] * k) for i in range(3)))
    rnd = random.Random(5)
    for _ in range(24):
        x = rnd.uniform(0, W); y0 = rnd.uniform(0, H); r = rnd.uniform(10, 34); v = rnd.uniform(20, 60)
        y = (y0 - t * v) % H; d.ellipse([x - r, y - r, x + r, y + r], outline=(200, 225, 232), width=3)
    return im.convert('RGBA')
def drop(scale=1.0):
    S = 2; w, h = int(220 * scale), int(300 * scale); im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, h * S * 0.35, w * S, h * S], fill=(150, 205, 235, 210)); d.polygon([(w * S / 2, 0), (w * S * 0.06, h * S * 0.62), (w * S * 0.94, h * S * 0.62)], fill=(150, 205, 235, 210))
    d.ellipse([w * S * 0.25, h * S * 0.55, w * S * 0.45, h * S * 0.75], fill=(255, 255, 255, 170))
    return im.resize((w, h), Image.LANCZOS)
DROP = drop(1.3)
L_SUDOR = render_runs('sudor: sin olor', 58, (40, 90, 120), FONT_BLACK)
L_BACT = render_runs('bacterias = olor', 58, (40, 110, 60), FONT_BLACK)
def s_bacterias(t, d):
    im = bg(t); bob = 22 * math.sin(t * 4)
    x0, y0 = 540, 1000
    im.alpha_composite(DROP, (int(x0 - DROP.width / 2), int(y0 - DROP.height / 2 + bob)))
    if t < 0.6:
        l = L_SUDOR.copy(); l.putalpha(l.getchannel('A').point(lambda v: int(v * min(1, (0.6 - t) / 0.2))))
        im.alpha_composite(l, (int(540 - l.width / 2), int(y0 + 230)))
    rnd = random.Random(11); dd = ImageDraw.Draw(im)
    n = int(min(60, max(0, (t - 0.25) * 50)))
    for i in range(n):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(170, 330); ph = rnd.uniform(0, 6.28)
        x = x0 + r * math.cos(a) + 10 * math.sin(t * 4 + ph); y = y0 + r * math.sin(a) * 0.9 + 10 * math.cos(t * 3 + ph)
        s = rnd.uniform(10, 20); dd.ellipse([x - s, y - s, x + s, y + s], fill=(90, 170, 70), outline=(40, 110, 40), width=3)
        dd.ellipse([x - s * 0.35, y - s * 0.6, x - s * 0.05, y - s * 0.2], fill=(20, 60, 20))
    if t > d * 0.55:
        u = ease((t - d * 0.55) / 0.4); cl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(cl)
        for k in range(9):
            a = k * 0.7; cd.ellipse([x0 - 380 + 90 * math.cos(a), y0 - 420 + 60 * math.sin(a) - 60, x0 + 380 + 90 * math.cos(a), y0 + 60 * math.sin(a)], fill=(120, 140, 110, int(28 * u)))
        im.alpha_composite(cl.filter(ImageFilter.GaussianBlur(30)))
    return im.convert('RGB')

STICK = Image.open(f'{KIT}/producto/producto_cut.png').convert('RGBA').crop((0, 0, 253, 603))
STICK = STICK.resize((int(STICK.width * 700 / STICK.height), 700), Image.LANCZOS)
GEN = Image.open(f'{G}/a308/cut/rollon.png').convert('RGBA'); GEN = GEN.resize((int(GEN.width * 420 / GEN.height), 420), Image.LANCZOS)
def s_boca_abajo(t, d):
    im = bg(t, (244, 244, 246), (226, 228, 232))
    u = ease((t - 0.1) / 0.8); ang = 180 * u + 6 * math.sin(t * 4) * (u >= 1)
    r = STICK.rotate(ang, resample=Image.BICUBIC, expand=True); cx, cy = 600, 1000 + 8 * math.sin(t * 2.4)
    im.alpha_composite(r, (int(cx - r.width / 2), int(cy - r.height / 2)))
    # frasco genérico pequeño a la izquierda, boca abajo, goteando (contraste)
    g = GEN.rotate(180, expand=True); gx, gy = 220, 760
    im.alpha_composite(g, (int(gx - g.width / 2), int(gy - g.height / 2)))
    dd = ImageDraw.Draw(im)
    for k in range(3):
        ph = (t * 1.3 + k / 3) % 1; y = gy + g.height / 2 + ph * 420
        dd.ellipse([gx - 12, y - 18, gx + 12, y + 18], fill=(150, 205, 235, 230))
    dd.ellipse([gx - 70, 1430, gx + 70, 1460], fill=(150, 205, 235, 160))
    return im.convert('RGB')

SC = dict(bacterias=s_bacterias, boca_abajo=s_boca_abajo)
if __name__ == '__main__':
    name, dur = sys.argv[1], float(sys.argv[2]); n = round(dur * FPS); out = f'{T}/m33_{name}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(n): p.stdin.write(SC[name](k / FPS, dur).tobytes())
    p.stdin.close(); p.wait(); print('ok', out, dur)
