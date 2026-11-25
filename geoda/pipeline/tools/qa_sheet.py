#!/usr/bin/env python3
"""Hoja de QA: cuadros cada `step` s con las guías de zona segura del brief (250 arriba, 670 abajo, 140 derecha).
uso: qa_sheet.py video.mp4 salida.jpg [step] [cols]"""
import sys, subprocess
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
step = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 8
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src],
                           capture_output=True, text=True).stdout)
w, h = 216, 384; s = w / 1080
ts = [round(i * step, 2) for i in range(int(dur / step) + 1)]
rows = (len(ts) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * h), 'white')
for i, t in enumerate(ts):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(min(t, dur - 0.05)), '-i', src, '-frames:v', '1', '-vf', f'scale={w}:{h}',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    if len(raw) < w * h * 3:
        continue
    im = Image.frombytes('RGB', (w, h), raw[:w * h * 3]); d = ImageDraw.Draw(im)
    d.line([(0, 250 * s), (w, 250 * s)], fill=(255, 0, 255)); d.line([(0, (1920 - 670) * s), (w, (1920 - 670) * s)], fill=(255, 0, 255))
    d.line([((1080 - 140) * s, 0), ((1080 - 140) * s, h)], fill=(255, 0, 255))
    d.rectangle([0, 0, 44, 12], fill=(0, 0, 0)); d.text((2, 0), f'{t:.1f}s', fill=(255, 255, 0))
    sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(out, quality=88)
print(out, len(ts), 'cuadros')
