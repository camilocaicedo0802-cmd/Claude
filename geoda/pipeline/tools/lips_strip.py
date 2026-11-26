#!/usr/bin/env python3
"""Tira de la boca cada 0,1 s con la energía de la voz debajo (para revisar a ojo la sincronía).
uso: lips_strip.py clip.mp4 voz.wav salida.jpg"""
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw
v, wav, out = sys.argv[1:4]
fr = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', 'fps=10,scale=540:960', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout, np.uint8).reshape(-1, 960, 540, 3)
c = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
bx = [max(f, key=lambda b: b[2] * b[3]) for f in (c.detectMultiScale(cv2.cvtColor(g, cv2.COLOR_RGB2GRAY), 1.1, 6, minSize=(40, 40)) for g in fr[::5]) if len(f)]
x, y, w, h = np.median(np.array(bx), 0).astype(int)
a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
e = [np.sqrt((a[i * 1600:(i + 1) * 1600] ** 2).mean()) if i * 1600 < len(a) else 0 for i in range(len(fr))]
W = 80; half = (len(fr) + 1) // 2; im = Image.new('RGB', (W * half, 2 * 125), 'white'); d = ImageDraw.Draw(im)
for i, f in enumerate(fr):
    r, col = divmod(i, half)
    im.paste(Image.fromarray(f[y + int(h * .55):y + int(h * 1.05), x + int(w * .15):x + int(w * .85)]).resize((W, 56)), (col * W, r * 125))
    b = int(min(1, e[i] / .15) * 40); d.rectangle([col * W + 5, r * 125 + 100 - b, col * W + W - 5, r * 125 + 100], fill=(220, 40, 40)); d.text((col * W + 2, r * 125 + 105), f'{i / 10:.1f}', fill=(0, 0, 0))
im.save(out, quality=88)
