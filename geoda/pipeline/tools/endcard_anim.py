#!/usr/bin/env python3
"""Tarjeta final ANIMADA con el PRODUCTO REAL: fondo de baño en video (Kling, cámara quieta, luz y hojas que se mueven) +
recorte real de la landing compuesto cuadro a cuadro (sombra de contacto, reflejo), brillo que barre el tubo y destello
en la piedra. Nada queda quieto y la etiqueta es la real.
uso: endcard_anim.py fondo.mp4 salida.mp4 [duración] [alto_producto] [base_y] [x1,x2,... centros] [tubo]   -> caja del producto
     'tubo' = solo el tubo (sin la tapa al lado), para estantes con varias unidades."""
import os, sys, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
W, H, FPS = 1080, 1920, 30
src, out = sys.argv[1], sys.argv[2]
dur = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
ph = int(sys.argv[4]) if len(sys.argv) > 4 else 640
base = int(sys.argv[5]) if len(sys.argv) > 5 else 1600
xs = [int(v) for v in sys.argv[6].split(',')] if len(sys.argv) > 6 and sys.argv[6] else None
tube = len(sys.argv) > 7 and sys.argv[7] == 'tubo'
prod = Image.open(f'{G}/v2frames/producto_cut.png').convert('RGBA')
if tube:   # solo el tubo, con borde suave donde estaba la tapa
    prod = prod.crop((0, 0, 262, prod.height)); a = np.array(prod.getchannel('A'))
    a[:, 252:] = (a[:, 252:] * np.linspace(1, 0, a.shape[1] - 252)[None, :]).astype(np.uint8)
    prod.putalpha(Image.fromarray(a)); prod = prod.crop(prod.getbbox())
prod = ImageEnhance.Brightness(prod.resize((int(prod.width * ph / prod.height), ph), Image.LANCZOS)).enhance(1.02)
xs = xs or [W // 2 - 10]
A = prod.getchannel('A')
# capa fija (en coordenadas del fondo, la cámara del fondo no se mueve): sombra + reflejo + producto(s)
lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pm = np.zeros((H, W), np.float32); boxes = []
for cx in xs:
    x0 = cx - prod.width // 2; y0 = base - prod.height
    sh = Image.new('L', (W, H), 0); cont = Image.new('L', (prod.width, 40), 0)
    ImageDraw.Draw(cont).ellipse([10, 5, prod.width - 10, 38], fill=170); sh.paste(cont, (x0, base - 22)); sh = sh.filter(ImageFilter.GaussianBlur(10))
    cast = Image.new('L', (W, H), 0); cast.paste(A.resize((prod.width, int(prod.height * 0.18))), (x0 + 40, base - 8))
    cast = cast.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.35))
    shadow = Image.fromarray(np.maximum(np.array(sh), np.array(cast)))
    dark = Image.new('RGBA', (W, H), (40, 34, 30, 255)); dark.putalpha(shadow); lay = Image.alpha_composite(lay, dark)
    ref = prod.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, prod.width, int(prod.height * 0.35)))
    ra = np.array(ref.getchannel('A')).astype(np.float32) * np.linspace(0.16, 0, ref.height)[:, None]
    ref.putalpha(Image.fromarray(ra.astype(np.uint8))); ref = ref.filter(ImageFilter.GaussianBlur(2)); lay.alpha_composite(ref, (x0, base + 2))
    lay.alpha_composite(prod, (x0, y0))
    pm[y0:base, x0:x0 + prod.width] = np.maximum(pm[y0:base, x0:x0 + prod.width], np.array(A, np.float32) / 255)
    boxes.append((x0, y0, x0 + prod.width, base))
x0, y0 = boxes[0][0], boxes[0][1]
L = np.array(lay).astype(np.float32); LA = L[..., 3:4] / 255; LC = L[..., :3][..., ::-1]      # BGR
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
stone = (x0 + int(prod.width * 0.23), y0 + int(ph * 0.09))      # cúpula de la piedra
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-stream_loop', '-1', '-i', src, '-vf',
                        f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                       stdout=subprocess.PIPE)
nf = round(dur * FPS)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-frames:v', str(nf), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', '-an', out], stdin=subprocess.PIPE)
for k in range(nf):
    fr = np.frombuffer(dec.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3).astype(np.float32)
    fr = fr * (1 - LA) + LC * LA
    t = k / FPS
    u = (t % 3.2) / 1.4                                           # brillo que barre el tubo cada 3,2 s
    if u <= 1:
        c = -300 + u * 1500
        band = np.exp(-((xx - x0 + 0.5 * (yy - y0) - c) / 55) ** 2) * pm * math.sin(math.pi * u) * 0.45
        fr = fr + band[..., None] * 255
    v = ((t + 1.2) % 3.2) / 0.5                                   # destello en la piedra
    if v <= 1:
        a = math.sin(math.pi * v); r = 70 * a
        st = np.zeros((H, W), np.float32)
        cv2.line(st, (int(stone[0] - r), stone[1]), (int(stone[0] + r), stone[1]), 1.0, 3, cv2.LINE_AA)
        cv2.line(st, (stone[0], int(stone[1] - r)), (stone[0], int(stone[1] + r)), 1.0, 3, cv2.LINE_AA)
        st = cv2.GaussianBlur(st, (0, 0), 2) * 1.5
        halo = np.zeros((H, W), np.float32); cv2.circle(halo, stone, int(22 * a) + 1, 1.0, -1, cv2.LINE_AA)
        fr = fr + (st + cv2.GaussianBlur(halo, (0, 0), 10) * 0.8)[..., None] * 255 * a
    enc.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.kill()
print(out, 'productos', boxes)
