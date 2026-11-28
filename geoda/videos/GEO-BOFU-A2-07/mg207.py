#!/usr/bin/env python3
"""A2-07 · piezas locales con el recorte REAL de GEODA:
  palma (hook B): tres GEODA caen una por una en la palma abierta (foto) y rebotan; cada una con un 'pop'.
  abanico (B3): tres GEODA en abanico sobre el mesón del baño desenfocado (sin caras detrás del texto), entran una por una.
uso: mg207.py palma|abanico dur -> tmp/m7_<escena>.mp4"""
import os, sys, math, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageOps
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
W, H, FPS = 1080, 1920, 30
T = f'{G}/a207/tmp'
ease = lambda u: 1 - (1 - max(0, min(1, u))) ** 3
STICK = Image.open(f'{KIT}/producto/producto_cut.png').convert('RGBA').crop((0, 0, 253, 603))
def stick(h, ang=0):
    s = STICK.resize((int(STICK.width * h / STICK.height), h), Image.LANCZOS)
    return s.rotate(ang, resample=Image.BICUBIC, expand=True) if ang else s
def shadowed(s, blur=10, op=90, dy=14):
    out = Image.new('RGBA', (s.width + 60, s.height + 60), (0, 0, 0, 0)); sh = Image.new('RGBA', out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, op), (30, 30 + dy), s.getchannel('A')); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur))); out.alpha_composite(s, (30, 30)); return out

def fill(im, z=1.0, fx=0.5, fy=0.5):
    w, h = int(W * z), int(H * z); b = im.resize((w, h), Image.LANCZOS); ox, oy = int((w - W) * fx), int((h - H) * fy); return b.crop((ox, oy, ox + W, oy + H))

PALMA = ImageOps.mirror(Image.open(f'{T}/palma.png').convert('RGB')).resize((W, H), Image.LANCZOS)   # palma a la izquierda
PALM_C = (int(0.18 * W), int(0.60 * H))
def s_palma(t, d):
    z = 1.35 + 0.05 * t / d   # acercada a la palma
    im = fill(PALMA, z, 0.10, 0.62).convert('RGBA')
    # dónde descansan en la palma (medido sobre el cuadro ya acercado)
    for i, (x_c, ang) in enumerate([(470, -12), (720, 12), (595, 0)]):   # la del centro cae de última, adelante
        t0 = 0.15 + 0.5 * i; u = (t - t0) / 0.32
        if u < 0: continue
        s = shadowed(stick(300, ang + (1 - min(1, u)) * 30))
        y_end = 1215 - s.height + 30; y = -400 + (y_end + 400) * min(1, u) ** 2
        if u >= 1:   # rebote
            v = t - t0 - 0.32; y = y_end - 40 * math.exp(-9 * v) * abs(math.sin(v * 18))
        im.alpha_composite(s, (int(x_c - s.width / 2), int(y)))
    return im.convert('RGB')

FONDO = Image.open(f'{KIT}/fondos/p_banofondo_0.png').convert('RGB').resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(14))   # sin personas detrás del texto
FONDO = Image.blend(FONDO, Image.new('RGB', (W, H), (250, 236, 226)), 0.25)
def s_abanico(t, d):
    im = fill(FONDO, 1.0 + 0.08 * t / d).convert('RGBA')
    for i, (dx, ang, h) in enumerate([(-240, 16, 500), (240, -16, 500), (0, 0, 580)]):   # el del centro adelante
        u = ease((t - 0.1 - 0.35 * i) / 0.4)
        if u <= 0: continue
        s = shadowed(stick(h, ang * u)); bob = 8 * math.sin(t * 2.6 + i)
        x = 540 + dx * u - s.width / 2; y = 1360 - s.height + 60 + (1 - u) * 300 + bob
        im.alpha_composite(s, (int(x), int(y)))
    return im.convert('RGB')

SC = dict(palma=s_palma, abanico=s_abanico)
if __name__ == '__main__':
    name, dur = sys.argv[1], float(sys.argv[2]); n = round(dur * FPS); out = f'{T}/m7_{name}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(n): p.stdin.write(SC[name](k / FPS, dur).tobytes())
    p.stdin.close(); p.wait(); print('ok', out, dur)
