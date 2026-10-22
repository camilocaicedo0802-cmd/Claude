"""Per-frame bounding box of the matcha can (the product) in source pixels.

SIFT matching against templates of the closed and the open can, cut from the footage itself,
then gaps (motion blur) are interpolated and the track is smoothed within each shot.

Usage: python3 cantrack.py <source.mov> <cans.json>
"""
import json, subprocess, sys
import cv2
import numpy as np

SRC, OUT = sys.argv[1:3]
W, H, FPS = 1080, 1920, 30
T0, T1 = 21.8, 41.62                     # the can is only on screen in the last part of the video
CUTS = [22.133, 26.533, 29.3, 35.933]
TEMPLATES = [(915, (205, 760, 445, 1075)),   # closed can, front label (30.5 s)
             (690, (230, 770, 460, 1060)),   # closed can (23.0 s)
             (812, (355, 1050, 605, 1400))]  # open can with the powder (27.07 s)
S = 0.5                                  # detect at half resolution

def frames():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H)
        if len(b) < W * H: break
        yield np.frombuffer(b, np.uint8).reshape(H, W)

sift = cv2.SIFT_create(nfeatures=2500)
bf = cv2.BFMatcher(cv2.NORM_L2)
all_frames = {}
need = {k for k, _ in TEMPLATES}
lo, hi = int(T0 * FPS), int(T1 * FPS)
for i, g in enumerate(frames()):
    if i in need or lo <= i <= hi:
        all_frames[i] = cv2.resize(g, None, fx=S, fy=S, interpolation=cv2.INTER_AREA)
tpls = []
for k, (x0, y0, x1, y1) in TEMPLATES:
    crop = all_frames[k][int(y0 * S):int(y1 * S), int(x0 * S):int(x1 * S)]
    kp, des = sift.detectAndCompute(crop, None)
    tpls.append((crop.shape, kp, des))

raw = {}
for i in range(lo, hi + 1):
    g = all_frames[i]
    kp, des = sift.detectAndCompute(g, None)
    if des is None or len(kp) < 10: continue
    best = None
    for (th, tw), tkp, tdes in tpls:
        m = bf.knnMatch(tdes, des, k=2)
        good = [a for a, b in (x for x in m if len(x) == 2) if a.distance < 0.75 * b.distance]
        if len(good) < 10: continue
        src = np.float32([tkp[a.queryIdx].pt for a in good]).reshape(-1, 1, 2)
        dst = np.float32([kp[a.trainIdx].pt for a in good]).reshape(-1, 1, 2)
        Hm, mask = cv2.findHomography(src, dst, cv2.RANSAC, 4.0)
        if Hm is None: continue
        inl = int(mask.sum())
        corners = cv2.perspectiveTransform(np.float32([[0, 0], [tw, 0], [tw, th], [0, th]]).reshape(-1, 1, 2), Hm)
        x0, y0 = corners[:, 0, 0].min() / S, corners[:, 0, 1].min() / S
        x1, y1 = corners[:, 0, 0].max() / S, corners[:, 0, 1].max() / S
        area = (x1 - x0) * (y1 - y0); ta = tw * th / S / S
        if inl < 10 or not (0.35 < area / ta < 3.0) or not (0.5 < (x1 - x0) / max(1, y1 - y0) < 1.6): continue
        if best is None or inl > best[0]: best = (inl, [x0, y0, x1, y1])
    if best: raw[i] = best[1]
print("detected", len(raw), "of", hi - lo + 1, "frames")

# drop detections that disagree with their neighbours (centre jump or size change)
ks = sorted(raw)
arr = np.array([raw[k] for k in ks], float)
ctr = np.stack([(arr[:, 0] + arr[:, 2]) / 2, (arr[:, 1] + arr[:, 3]) / 2, arr[:, 2] - arr[:, 0]], 1)
good = {}
for j, k in enumerate(ks):
    near = [m for m in range(len(ks)) if abs(ks[m] - k) <= 6 and m != j]
    if len(near) < 2: continue
    med = np.median(ctr[near], axis=0)
    if np.hypot(*(ctr[j, :2] - med[:2])) < 90 and abs(ctr[j, 2] - med[2]) < 0.35 * med[2]:
        good[k] = raw[k]
print("kept", len(good), "after temporal check")
raw = good

# fill the frames SIFT missed (motion blur) by template correlation from the nearest detection,
# walking forward and backward inside each shot; whatever is still missing gets interpolated
def ncc_step(ref_img, ref_box, img, prev_box):
    x0, y0, x1, y1 = [int(v * S) for v in ref_box]
    tpl = ref_img[y0:y1, x0:x1]
    if tpl.size == 0: return None
    px0, py0, px1, py1 = [v * S for v in prev_box]
    best = None
    for sc in (0.9, 1.0, 1.1):
        t = cv2.resize(tpl, None, fx=sc, fy=sc)
        th, tw = t.shape
        sx0, sy0 = int(max(0, px0 - 90)), int(max(0, py0 - 90))
        sx1, sy1 = int(min(img.shape[1], px1 + 90)), int(min(img.shape[0], py1 + 90))
        win = img[sy0:sy1, sx0:sx1]
        if win.shape[0] <= th or win.shape[1] <= tw: continue
        r = cv2.matchTemplate(win, t, cv2.TM_CCOEFF_NORMED)
        _, mv, _, ml = cv2.minMaxLoc(r)
        if best is None or mv > best[0]:
            best = (mv, [(sx0 + ml[0]) / S, (sy0 + ml[1]) / S, (sx0 + ml[0] + tw) / S, (sy0 + ml[1] + th) / S])
    return best[1] if best and best[0] > 0.5 else None

bounds0 = [lo] + [int(round(c * FPS)) for c in CUTS] + [hi + 1]
prop = {}
for a, b in zip(bounds0[:-1], bounds0[1:]):
    det = sorted(k for k in raw if a <= k < b)
    if not det: continue
    for direction in (1, -1):
        for k0 in det:
            ref_box, box = raw[k0], raw[k0]
            k = k0 + direction
            while a <= k < b and k not in raw:
                nb = ncc_step(all_frames[k0], ref_box, all_frames[k], box)
                if nb is None: break
                if k not in prop: prop[k] = nb
                box = nb; k += direction
filled = dict(raw); filled.update({k: v for k, v in prop.items() if k not in raw})
print("filled by correlation", len(filled) - len(raw))
raw_detected = set(raw)
raw = filled

# fill gaps within each shot by interpolation; hold the edge value up to 0.4 s outside the track
bounds = [lo] + [int(round(c * FPS)) for c in CUTS] + [hi + 1]
out = {}
for a, b in zip(bounds[:-1], bounds[1:]):
    ks = sorted(k for k in raw if a <= k < b)
    if not ks: continue
    arr = np.array([raw[k] for k in ks], float)
    med = np.median(arr, axis=0)
    keep = [j for j, k in enumerate(ks) if abs((arr[j, 0] + arr[j, 2]) / 2 - (med[0] + med[2]) / 2) < 420]
    ks = [ks[j] for j in keep]; arr = arr[keep]
    idx = np.arange(max(a, ks[0] - 12), min(b, ks[-1] + 13))
    full = np.stack([np.interp(idx, ks, arr[:, c]) for c in range(4)], 1)
    r = np.arange(-4, 5); kern = np.exp(-r ** 2 / 8.0); kern /= kern.sum()
    pad = np.pad(full, ((4, 4), (0, 0)), mode="edge")
    sm = np.stack([np.convolve(pad[:, c], kern, mode="valid") for c in range(4)], 1)
    for j, k in enumerate(idx):    # 5th value: 1 SIFT detection, 2 correlation, 0 interpolated/held
        out[int(k)] = [round(float(v), 1) for v in sm[j]] + [1 if k in raw_detected else (2 if k in raw else 0)]
json.dump(out, open(OUT, "w"))
print("track frames", len(out))
