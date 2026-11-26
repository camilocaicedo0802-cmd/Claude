#!/usr/bin/env python3
"""A2-05 · B10 'Día catorce': hoja de calendario pegada al espejo (mismo estilo del hook B) con 'chulos' rojos en los días 1-13;
el 14 recibe su 'chulo' en vivo con marcador rojo. Fondo = el baño del hook B desenfocado; la cámara empuja suave.
uso: cal14.py <dur> -> tmp/cal14.mp4"""
import os, sys, math, random, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
W, H, FPS = 1080, 1920, 30
AQUI = os.path.dirname(os.path.abspath(__file__)); T = f'{G}/a205/tmp'; os.makedirs(T, exist_ok=True)
F = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Light.otf', 92) if os.path.exists('/usr/share/fonts/opentype/inter/Inter-Light.otf') else ImageFont.truetype('DejaVuSans.ttf', 92)
RED = (214, 30, 40)
bg = Image.open(f'{G}/hf/d_hb_0.png').convert('RGB')
bg = bg.crop((0, 0, bg.width, bg.width * 16 // 9 if bg.width * 16 // 9 <= bg.height else bg.height)).resize((W, H)).filter(ImageFilter.GaussianBlur(28))
bg = Image.blend(bg, Image.new('RGB', (W, H), (235, 232, 226)), 0.25)
PW, PH = 960, 760; X0, Y0 = (W - PW) // 2, 560
paper = Image.new('RGBA', (PW, PH), (250, 250, 247, 255)); pd = ImageDraw.Draw(paper)
gx0, gy0, cw, chh = 40, 70, (PW - 80) / 7, 300
rnd = random.Random(7)
for r in range(3):
    pd.line([(gx0, gy0 + r * chh), (PW - 40, gy0 + r * chh)], fill=(30, 30, 30), width=4)
for c in range(8):
    pd.line([(gx0 + c * cw, gy0), (gx0 + c * cw, gy0 + 2 * chh)], fill=(30, 30, 30), width=4)
cells = []
for i in range(14):
    r, c = divmod(i, 7); cx, cy = gx0 + c * cw + cw / 2, gy0 + r * chh + chh / 2
    pd.text((cx + rnd.uniform(-5, 5), cy - 62 + rnd.uniform(-6, 6)), str(i + 1), font=F, fill=(25, 25, 25), anchor='mm')
    cells.append((cx, cy))
sh = Image.new('RGBA', (PW + 80, PH + 80), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([40, 50, PW + 40, PH + 50], fill=(0, 0, 0, 70))
sh = sh.filter(ImageFilter.GaussianBlur(16))
tape = Image.new('RGBA', (150, 60), (235, 235, 225, 150))

def xmark(d, cx, cy, u, w=10):   # 'chulo' rojo bajo el número; u: 0-1 avance del trazo (dos líneas)
    cy += 62
    p1 = [(cx - 40, cy - 4), (cx - 10, cy + 34)]; p2 = [(cx - 10, cy + 34), (cx + 44, cy - 46)]
    for k, (s, e) in enumerate([p1, p2]):
        v = max(0.0, min(1.0, u * 2 - k))
        if v > 0: d.line([s, (s[0] + (e[0] - s[0]) * v, s[1] + (e[1] - s[1]) * v)], fill=RED, width=w)

def frame(t, dur):
    im = bg.copy().convert('RGBA'); p = paper.copy(); d = ImageDraw.Draw(p)
    for i in range(13): xmark(d, *cells[i], 1.0)
    u = min(1.0, max(0.0, (t - 0.08) / 0.5)); xmark(d, *cells[13], u, w=12)
    im.alpha_composite(sh, (X0 - 40, Y0 - 40)); im.alpha_composite(p, (X0, Y0))
    for tx, ty, ang in [(X0 - 40, Y0 - 20, 35), (X0 + PW - 110, Y0 - 20, -35)]:
        tp = tape.rotate(ang, expand=True); im.alpha_composite(tp, (int(tx), int(ty)))
    z = 1.0 + 0.06 * (t / dur); cx, cy = W / 2, Y0 + PH / 2
    im = im.convert('RGB').resize((int(W * z), int(H * z)), Image.LANCZOS)
    ox, oy = int(cx * z - cx), int(cy * z - cy)
    return im.crop((ox, oy, ox + W, oy + H))

if __name__ == '__main__':
    dur = float(sys.argv[1]); n = round(dur * FPS); out = f'{T}/cal14.mp4'
    pr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(n): pr.stdin.write(frame(k / FPS, dur).tobytes())
    pr.stdin.close(); pr.wait(); print('ok', out)
