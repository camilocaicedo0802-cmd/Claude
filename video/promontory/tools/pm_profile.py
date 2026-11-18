"""edit/pm_profile.json: ground elevation (ft) along the old Promontory line and along the Lucin Cutoff, Mapzen terrarium z10."""
import json, math
import numpy as np
from PIL import Image
T = "/home/user/pm/assets/map/tiles/"
Z = 10
cache = {}
def elev(lon, lat):
    n = 2 ** Z
    x = (lon + 180) / 360 * n * 256
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n * 256
    tx, ty = int(x // 256), int(y // 256)
    k = (tx, ty)
    if k not in cache:
        a = np.asarray(Image.open(f"{T}{Z}_{tx}_{ty}.png").convert("RGB")).astype(np.float32)
        cache[k] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    return float(cache[k][int(y) % 256, int(x) % 256])
R = json.load(open("/home/user/pm/edit/pm_route.json"))
out = {}
for key in ("old", "cutoff"):
    pts = R[key] if key == "old" else R[key][::-1]   # both from Lucin (west) to Ogden (east)
    if key == "cutoff" and pts[0][0] > pts[-1][0]: pts = pts[::-1]
    if key == "old" and pts[0][0] > pts[-1][0]: pts = pts[::-1]
    prof, d = [], 0.0
    for (a, b), (c, e) in zip(pts, pts[1:]):
        seg = math.hypot((c - a) * 83.5, (e - b) * 111.0)
        n = max(1, int(seg / 0.4))
        for i in range(n):
            lo, la = a + (c - a) * i / n, b + (e - b) * i / n
            prof.append([round(d + seg * i / n, 2), round(elev(lo, la) * 3.281), round(lo, 4), round(la, 4)])
        d += seg
    out[key] = prof
    ft = np.array([p[1] for p in prof])
    print(key, len(prof), round(d, 1), "km", ft.min(), ft.max())
json.dump(out, open("/home/user/pm/edit/pm_profile.json", "w"))
