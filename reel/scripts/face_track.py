"""Detecta la cara del presentador (Haar cascade de OpenCV) a 5 fps y guarda su centro y tamaño normalizados.
Uso: python3 face_track.py <video> <salida.json>
"""
import json, subprocess, sys
import cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]
W, H, FPS = 540, 960, 5
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo",
                      "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
res, k = [], 0
while True:
    buf = p.stdout.read(W * H)
    if len(buf) < W * H:
        break
    img = np.frombuffer(buf, np.uint8).reshape(H, W)
    faces = casc.detectMultiScale(img, 1.1, 5, minSize=(30, 30))
    if len(faces):
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        res.append({"t": round(k / FPS, 2), "x": round((x + w / 2) / W, 4), "y": round((y + h / 2) / H, 4), "s": round(h / H, 4)})
    else:
        res.append({"t": round(k / FPS, 2), "x": None, "y": None, "s": None})
    k += 1
json.dump(res, open(out, "w"))
ok = [r for r in res if r["x"] is not None]
print(f"{len(ok)}/{len(res)} frames con cara")
for r in res[:: FPS * 3]:
    print(r)
