#!/usr/bin/env python3
"""Sincronía por APERTURA de boca: % de píxeles oscuros (interior de la boca) en la boca, cuadro a cuadro, vs energía de la voz.
uso: lip_open.py clip.mp4 voz.wav  -> desfase (s) con mejor correlación (>0 = la boca va después de la voz) y la correlación"""
import sys, subprocess, numpy as np, cv2
v, wav = sys.argv[1:3]; FPS = 30
fr = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', 'fps=30,scale=540:960', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout, np.uint8).reshape(-1, 960, 540)
c = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
op = []
last = None
for g in fr:
    f = c.detectMultiScale(g, 1.1, 5, minSize=(40, 40))
    if len(f): last = max(f, key=lambda b: b[2] * b[3])
    x, y, w, h = last
    roi = g[y + int(h * .68): y + int(h * .92), x + int(w * .30): x + int(w * .70)].astype(float)
    skin = np.median(roi); op.append((roi < skin * 0.55).mean())
op = np.array(op)
a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
hop = 16000 // FPS; n = min(len(a) // hop, len(op))
e = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)); o = op[:n]
k = np.ones(3) / 3; e = np.convolve(e, k, 'same'); o = np.convolve(o, k, 'same')
z = lambda q: (q - q.mean()) / (q.std() + 1e-9); e, o = z(e), z(o)
res = {L: np.mean(e[max(0, -L):n - max(0, L)] * o[max(0, L):n - max(0, -L)]) for L in range(-12, 13)}
best = max(res, key=res.get)
print(f'{v.split("/")[-1]:16s} desfase {best / FPS:+.2f} s  corr {res[best]:.2f}  (corr a 0: {res[0]:.2f})')
