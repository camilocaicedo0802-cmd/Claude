#!/usr/bin/env python3
"""A2-08 · piezas locales con el recorte REAL de GEODA:
  cama (B5): tres GEODA aparecen una por una sobre la cama (foto), con rebote y sombra.
  cta_k3 (cierre K3 'Llévala hoy'): producto real (kit endcard_bano_anim) + botón Comprar que late y recibe dos toques. Sin etiqueta.
uso: mg208.py cama|cta_k3 dur -> tmp/m8_<escena>.mp4"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102'); sys.path.insert(0, G)
from build_a102 import render_runs, FONT_BLACK, WHITE
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
W, H, FPS = 1080, 1920, 30
T = f'{G}/a208/tmp'
ease = lambda u: 1 - (1 - max(0, min(1, u))) ** 3
STICK = Image.open(f'{KIT}/producto/producto_cut.png').convert('RGBA').crop((0, 0, 253, 603))
def stick(h, ang=0):
    s = STICK.resize((int(STICK.width * h / STICK.height), h), Image.LANCZOS)
    return s.rotate(ang, resample=Image.BICUBIC, expand=True) if ang else s
def shadowed(s, blur=12, op=95, dy=16):
    out = Image.new('RGBA', (s.width + 70, s.height + 70), (0, 0, 0, 0)); sh = Image.new('RGBA', out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, op), (35, 35 + dy), s.getchannel('A')); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur))); out.alpha_composite(s, (35, 35)); return out
def fill(im, z=1.0, fx=0.5, fy=0.5):
    w, h = int(W * z), int(H * z); b = im.resize((w, h), Image.LANCZOS); ox, oy = int((w - W) * fx), int((h - H) * fy); return b.crop((ox, oy, ox + W, oy + H))

CAMA = Image.open(f'{T}/cama.png').convert('RGB').resize((W, H), Image.LANCZOS)
def s_cama(t, d):
    im = fill(CAMA, 1.0 + 0.07 * t / d, 0.5, 0.6).convert('RGBA')
    for i, (x, h, base) in enumerate([(300, 430, 1300), (780, 430, 1300), (540, 500, 1380)]):   # la del centro adelante
        t0 = 0.1 + 0.4 * i; u = (t - t0) / 0.3
        if u < 0: continue
        s = shadowed(stick(h)); y_end = base - s.height + 35; y = y_end - 260 * (1 - min(1, u)) ** 2
        if u >= 1: v = t - t0 - 0.3; y = y_end - 26 * math.exp(-9 * v) * abs(math.sin(v * 16))
        im.alpha_composite(s, (int(x - s.width / 2), int(y)))
    return im.convert('RGB')

def button(scale):
    w, h = int(440 * scale), int(118 * scale); S = 2
    im = Image.new('RGBA', (w * S + 40, h * S + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 26, 20 + w * S, 26 + h * S], h * S // 2, fill=(0, 0, 0, 60))
    d.rounded_rectangle([20, 14, 20 + w * S, 14 + h * S], h * S // 2, fill=(18, 160, 140, 255))
    tx = render_runs('Comprar', int(62 * scale * S), WHITE, FONT_BLACK); im.alpha_composite(tx, (20 + (w * S - tx.width) // 2, 14 + (h * S - tx.height) // 2))
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)
HAND = render_runs('👆', 120, WHITE, FONT_BLACK)

def cta_k3(dur, out):
    src = f'{KIT}/producto/endcard_bano_anim.mp4'
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-stream_loop', '-1', '-ss', '0.5', '-i', src, '-t', str(dur), '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    k = 0
    while True:
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: break
        t = k / FPS; im = Image.fromarray(np.frombuffer(raw, np.uint8).reshape(H, W, 3)).convert('RGBA')
        u = (t - 0.5) / 0.35
        if u > 0:   # botón Comprar centrado entre la tarjeta del CTA y el producto; dos toques
            sc = min(1, 0.3 + 0.7 * ease(u)) * (1 + 0.04 * math.sin(t * 6))
            for tap in (1.8, 3.4):
                v = t - tap
                if 0 <= v < 0.25: sc *= 1 - 0.08 * math.sin(math.pi * v / 0.25)
            b = button(sc); bx, by = 540, 790; im.alpha_composite(b, (int(bx - b.width / 2), int(by - b.height / 2)))
            for tap in (1.8, 3.4):
                v = t - tap
                if -0.45 <= v < 0.6: im.alpha_composite(HAND, (int(bx + 90), int(by + 40 + max(0, -v) * 260)))
        enc.stdin.write(im.convert('RGB').tobytes()); k += 1
    enc.stdin.close(); enc.wait(); print('ok', out, k / FPS)

if __name__ == '__main__':
    name, dur = sys.argv[1], float(sys.argv[2]); out = f'{T}/m8_{name}.mp4'
    if name == 'cta_k3':
        cta_k3(dur, out)
    else:
        n = round(dur * FPS)
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for k in range(n): p.stdin.write({'cama': s_cama}[name](k / FPS, dur).tobytes())
        p.stdin.close(); p.wait(); print('ok', out, dur)
