#!/usr/bin/env python3
"""A1-08 · cierre: producto REAL (kit endcard_bano_anim) + etiqueta colgante que se balancea (BLACK FRIDAY negra / REGALO roja)
y botón 'Comprar' que late y recibe un toque. Nada tapa la etiqueta del producto (caja 259,960,801,1600).
uso: cta.py bf|navidad duración -> tmp/cta_<modo>.mp4"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102'); sys.path.insert(0, G)
from build_a102 import render_runs, FONT_BLACK, NAVY, TEAL, YEL, WHITE
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
SRC = f'{KIT}/producto/endcard_bano_anim.mp4'
W, H, FPS = 1080, 1920, 30
mode, dur = sys.argv[1], float(sys.argv[2])
OUT = f'{G}/a108/tmp/cta_{mode}.mp4'

def tag(lines, bg, w=300, h=200):
    """Etiqueta de precio colgante (agujero arriba al centro, esquinas de arriba cortadas), texto horizontal."""
    S = 2; im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = 50 * S
    d.polygon([(c, 0), (w * S - c, 0), (w * S, c), (w * S, h * S), (0, h * S), (0, c)], fill=bg)
    d.ellipse([(w // 2 - 13) * S, 14 * S, (w // 2 + 13) * S, 40 * S], fill=(235, 235, 235, 255))
    f = ImageFont.truetype(FONT_BLACK, 60 * S)
    for i, (t, col) in enumerate(lines):
        d.text((w // 2 * S, (h // 2 + 22 + (i - (len(lines) - 1) / 2) * 66) * S), t, font=f, fill=col, anchor='mm')
    return im.resize((w, h), Image.LANCZOS)

TAG = tag([('BLACK', WHITE + (255,)), ('FRIDAY', YEL + (255,))], (15, 15, 18, 255)) if mode == 'bf' else \
      tag([('REGALO', WHITE + (255,)), ('NAVIDAD', YEL + (255,))], (196, 28, 38, 255))

def button(scale):
    w, h = int(440 * scale), int(118 * scale); S = 2
    im = Image.new('RGBA', (w * S + 40, h * S + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 26, 20 + w * S, 26 + h * S], h * S // 2, fill=(0, 0, 0, 60))
    d.rounded_rectangle([20, 14, 20 + w * S, 14 + h * S], h * S // 2, fill=(18, 160, 140, 255))
    t = render_runs('Comprar', int(62 * scale * S), WHITE, FONT_BLACK)
    im.alpha_composite(t, (20 + (w * S - t.width) // 2, 14 + (h * S - t.height) // 2))
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)

HAND = render_runs('👆', 120, WHITE, FONT_BLACK)
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', '0.5', '-i', SRC, '-t', str(dur), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
k = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = k / FPS; im = Image.fromarray(np.frombuffer(raw, np.uint8).reshape(H, W, 3)).convert('RGBA'); d = ImageDraw.Draw(im)
    # etiqueta colgante a la derecha del producto: entra cayendo y se balancea
    ang = 14 * math.exp(-0.6 * t) * math.sin(t * 4.2) + 6 * math.sin(t * 2.3)
    drop = min(1, t / 0.45); py = -200 + (700 + 200) * (1 - (1 - drop) ** 3)
    px = 240   # a la izquierda, sobre la planta: no tapa el producto ni queda bajo los íconos de la derecha
    r = TAG.rotate(ang, resample=Image.BICUBIC, center=(TAG.width / 2, 27))   # gira alrededor del agujero
    d.line([(px, 520), (px, py + 27)], fill=(70, 70, 70, 255), width=4)
    im.alpha_composite(r, (int(px - r.width / 2), int(py)))
    # botón Comprar: aparece, late, y una mano lo toca dos veces
    u = (t - 0.5) / 0.35
    if u > 0:
        sc = min(1, 0.3 + 0.7 * (1 - (1 - min(1, u)) ** 3)) * (1 + 0.04 * math.sin(t * 6))
        for tap in (1.8, 3.6):
            v = t - tap
            if 0 <= v < 0.25: sc *= 1 - 0.08 * math.sin(math.pi * v / 0.25)
        b = button(sc); bx, by = 640, 800
        im.alpha_composite(b, (int(bx - b.width / 2), int(by - b.height / 2)))
        for tap in (1.8, 3.6):
            v = t - tap
            if -0.45 <= v < 0.6:
                hy = by + 40 + max(0, -v) * 260; im.alpha_composite(HAND, (int(bx + 90), int(hy)))
            if 0 <= v < 0.5:
                rr = 40 + 260 * v; a = int(160 * (1 - v / 0.5))
                ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([bx + 120 - rr, by - rr * 0.5, bx + 120 + rr, by + rr * 0.5], outline=(255, 255, 255, a), width=6)
                im.alpha_composite(ov)
    enc.stdin.write(im.convert('RGB').tobytes()); k += 1
enc.stdin.close(); enc.wait(); print('ok', OUT, k / FPS)
