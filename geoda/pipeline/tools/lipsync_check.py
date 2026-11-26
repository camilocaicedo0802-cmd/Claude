#!/usr/bin/env python3
"""Mide la sincronía labios-voz: movimiento de la boca (cara detectada, tercio inferior) vs energía de la voz.
uso: lipsync_check.py video.mp4 [inicio fin] [voz.wav desfase_voz]  -> desfase (s): >0 = la boca va DESPUÉS de la voz"""
import sys, subprocess, numpy as np, cv2
v = sys.argv[1]; t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0; t1 = float(sys.argv[3]) if len(sys.argv) > 3 else None
aud = sys.argv[4] if len(sys.argv) > 4 else v; aoff = float(sys.argv[5]) if len(sys.argv) > 5 else t0
FPS = 30
cmd = ['ffmpeg', '-v', 'error', '-ss', str(t0)] + (['-t', str(t1 - t0)] if t1 else []) + ['-i', v, '-vf', 'fps=30,scale=540:960', '-f', 'rawvideo', '-pix_fmt', 'gray', '-']
fr = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.uint8).reshape(-1, 960, 540)
casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
boxes = []
for g in fr[:: max(1, len(fr) // 8)]:
    f = casc.detectMultiScale(g, 1.1, 6, minSize=(40, 40))
    if len(f): boxes.append(max(f, key=lambda b: b[2] * b[3]))
if not boxes: print('sin cara'); sys.exit()
x, y, w, h = np.median(np.array(boxes), 0).astype(int)
roi = fr[:, y + int(h * 0.62): y + int(h * 0.98), x + int(w * 0.22): x + int(w * 0.78)].astype(float)
mot = np.r_[0, np.abs(np.diff(roi, axis=0)).mean((1, 2))]          # cuánto cambia la boca cuadro a cuadro
sr = 16000
dur = len(fr) / FPS
ac = ['ffmpeg', '-v', 'error', '-ss', str(aoff), '-t', str(dur), '-i', aud, '-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
a = np.frombuffer(subprocess.run(ac, capture_output=True).stdout, np.float32)
hop = sr // FPS; n = min(len(a) // hop, len(mot))
e = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)); m = mot[:n]
e = np.convolve(e, np.ones(3) / 3, 'same'); m = np.convolve(m, np.ones(3) / 3, 'same')
e = (e - e.mean()) / (e.std() + 1e-9); m = (m - m.mean()) / (m.std() + 1e-9)
best = max(range(-15, 16), key=lambda L: np.mean(e[max(0, -L):n - max(0, L)] * m[max(0, L):n - max(0, -L)]))
corr = np.mean(e[max(0, -best):n - max(0, best)] * m[max(0, best):n - max(0, -best)])
print(f'{v.split("/")[-1]} {t0:.2f}-{t0+dur:.2f}s  cara {w}px  desfase {best / FPS:+.2f} s ({best:+d} cuadros)  correlación {corr:.2f}')
