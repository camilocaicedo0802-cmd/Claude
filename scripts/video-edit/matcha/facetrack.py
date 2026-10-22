"""Per-frame face centre (x, y, width) in source pixels, smoothed within each shot.

Usage: python3 facetrack.py <source.mov> <faces.json>
"""
import cv2, numpy as np, json, sys
src, out = sys.argv[1], sys.argv[2]
cuts = [0, 2.733, 4.633, 9.467, 12.567, 15.1, 19.267, 22.133, 26.533, 29.3, 35.933, 99]
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(src); fps = 30.0
raw = []
i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    g = cv2.cvtColor(cv2.resize(f, (360, 640)), cv2.COLOR_BGR2GRAY)
    g = cv2.equalizeHist(g)
    fs = cas.detectMultiScale(g, 1.1, 5, minSize=(45, 45))
    if len(fs):
        x, y, w, h = max(fs, key=lambda r: r[2] * r[3])
        raw.append([(x + w / 2) * 3, (y + h / 2) * 3, w * 3])
    else:
        raw.append(None)
    i += 1
n = len(raw)
print("frames", n, "detected", sum(r is not None for r in raw))
res = [None] * n
for a, b in zip(cuts[:-1], cuts[1:]):
    idx = [k for k in range(n) if a <= k / fps < b]
    pts = [(k, raw[k]) for k in idx if raw[k] is not None]
    if not pts:
        for k in idx: res[k] = [540, 800, 300]
        continue
    ks = np.array([p[0] for p in pts]); vals = np.array([p[1] for p in pts], float)
    # keep detections that agree with their neighbours (she can cross the frame within a shot)
    good = []
    for j in range(len(ks)):
        near = [m for m in range(len(ks)) if abs(ks[m] - ks[j]) <= 5 and m != j]
        if len(near) < 2: continue
        med = np.median(vals[near], axis=0)
        if np.hypot(*(vals[j, :2] - med[:2])) < 120 and abs(vals[j, 2] - med[2]) < 0.35 * med[2]:
            good.append(j)
    if good:
        ks, vals = ks[good], vals[good]
    full = np.stack([np.interp(idx, ks, vals[:, c]) for c in range(3)], 1)
    # smooth (gaussian, sigma 3 frames) within shot
    sig = 3; r = np.arange(-9, 10); kern = np.exp(-r**2 / (2 * sig**2)); kern /= kern.sum()
    pad = np.pad(full, ((9, 9), (0, 0)), mode="edge")
    sm = np.stack([np.convolve(pad[:, c], kern, mode="valid") for c in range(3)], 1)
    for j, k in enumerate(idx): res[k] = [round(float(v), 1) for v in sm[j]]
json.dump(res, open(out, "w"))
for t in [0.5, 3.5, 6, 11, 14, 17, 20, 24, 28, 32, 38, 41]:
    print(t, res[int(t * fps)])
