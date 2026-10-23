#!/usr/bin/env python3
"""Face box every 0.2 s of the raw take, so subtitles can sit beside the face without covering it.

Usage:
    python3 faces.py <crudo.mp4> <faces.json>

Needs `pip install "opencv-python-headless<5"` (Haar cascades left the main package in 5.x).
Coordinates are fractions of the frame, on the raw timeline.
"""
import json
import subprocess
import sys

import cv2
import numpy as np

src, out = sys.argv[1], sys.argv[2]
W, H, FPS = 960, 540, 5
proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={FPS},scale={W}:{H}",
                         "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
res, i = [], 0
while True:
    buf = proc.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    gray = cv2.cvtColor(np.frombuffer(buf, np.uint8).reshape(H, W, 3), cv2.COLOR_BGR2GRAY)
    found = cascade.detectMultiScale(gray, 1.1, 6, minSize=(120, 120))
    if len(found):
        x, y, w, h = max(found, key=lambda f: f[2] * f[3])
        res.append({"t": i / FPS, "x": x / W, "y": y / H, "w": w / W, "h": h / H})
    else:
        res.append({"t": i / FPS, "x": None})
    i += 1
json.dump(res, open(out, "w"))
print(len(res), "frames,", sum(r["x"] is not None for r in res), "with a face")
