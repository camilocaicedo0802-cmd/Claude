#!/usr/bin/env python3
"""Hoja de contacto con etiquetas de tiempo a partir de fotogramas sueltos.
Uso: hoja.py <carpeta_todos> <fps> <inicio_s> <fin_s> <paso_frames> <cols> <ancho_px> <salida.jpg>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
d, fps, t0, t1, step, cols, w, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), sys.argv[8]
files = sorted(f for f in os.listdir(d) if f.endswith(".jpg"))
idx = list(range(int(round(t0*fps)), min(int(round(t1*fps)), len(files)), step))
ims = []
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(14, w//16))
except Exception: font = ImageFont.load_default()
for i in idx:
    im = Image.open(os.path.join(d, files[i])).convert("RGB")
    h = int(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    dr = ImageDraw.Draw(im)
    label = f"{i/fps:.2f}s f{i}"
    dr.rectangle([0, 0, w, font.size + 6], fill=(0, 0, 0))
    dr.text((4, 2), label, fill=(255, 255, 0), font=font)
    ims.append(im)
rows = (len(ims) + cols - 1) // cols
H = ims[0].height
sheet = Image.new("RGB", (cols * w + (cols - 1) * 4, rows * H + (rows - 1) * 4), (40, 40, 40))
for k, im in enumerate(ims):
    sheet.paste(im, ((k % cols) * (w + 4), (k // cols) * (H + 4)))
sheet.save(out, quality=88)
print(out, sheet.size, len(ims), "frames")
