#!/usr/bin/env python3
"""Tarjeta final con el PRODUCTO REAL (recorte de la foto de la landing) sobre un ambiente (baño).
uso: endcard_real.py fondo.png salida.png [alto_producto] [base_y]  -> imprime la caja del producto"""
import sys, numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import os  # carpeta de trabajo: GEODA_WORK o ~/.geoda_work (la crea setup_work.sh)
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
W, H = 1080, 1920
bg_p, out = sys.argv[1], sys.argv[2]
ph = int(sys.argv[3]) if len(sys.argv) > 3 else 640
base = int(sys.argv[4]) if len(sys.argv) > 4 else 1560
bg = Image.open(bg_p).convert('RGB')
s = max(W / bg.width, H / bg.height); bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H)).convert('RGBA')
prod = Image.open(f'{G}/v2frames/producto_cut.png').convert('RGBA')
prod = prod.resize((int(prod.width * ph / prod.height), ph), Image.LANCZOS)
x0 = (W - prod.width) // 2 - 10; y0 = base - prod.height
A = prod.getchannel('A')
# sombra de contacto + sombra suave hacia la derecha (luz desde la izquierda)
sh = Image.new('L', (W, H), 0)
cont = Image.new('L', (prod.width, 40), 0); from PIL import ImageDraw
ImageDraw.Draw(cont).ellipse([10, 5, prod.width - 10, 38], fill=170)
sh.paste(cont, (x0, base - 22)); sh = sh.filter(ImageFilter.GaussianBlur(10))
cast = Image.new('L', (W, H), 0); cast.paste(A.resize((prod.width, int(prod.height * 0.18))), (x0 + 40, base - 8))
cast = cast.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.35))
shadow = Image.fromarray(np.maximum(np.array(sh), np.array(cast)))
dark = Image.new('RGBA', (W, H), (40, 34, 30, 255)); dark.putalpha(shadow)
comp = Image.alpha_composite(bg, dark)
# reflejo leve en el mármol
ref = prod.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, prod.width, int(prod.height * 0.35)))
ra = np.array(ref.getchannel('A')).astype(np.float32) * np.linspace(0.16, 0, ref.height)[:, None]
ref.putalpha(Image.fromarray(ra.astype(np.uint8))); ref = ref.filter(ImageFilter.GaussianBlur(2))
comp.alpha_composite(ref, (x0, base + 2))
# producto con un toque de la luz del ambiente
p2 = ImageEnhance.Brightness(prod).enhance(1.02)
comp.alpha_composite(p2, (x0, y0))
comp.convert('RGB').save(out, quality=95)
print(f'{out} producto {x0},{y0},{x0 + prod.width},{base}')
