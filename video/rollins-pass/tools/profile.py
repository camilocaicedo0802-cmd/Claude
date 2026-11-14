"""edit/rp_profile.json: ground elevation (Mapzen terrarium z14 tiles) along the Moffat Tunnel line, Tolland -> Fraser valley."""
import json, math, os
import numpy as np
from PIL import Image
T = "/home/user/rp/assets/map/tiles"
def elev(lon, lat, z=14):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    tx, ty = int(x), int(y)
    p = f"{T}/{z}_{tx}_{ty}.png"
    if not os.path.exists(p):
        return None
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
    px, py = min(int((x - tx) * 256), 255), min(int((y - ty) * 256), 255)
    r, g, b = a[py, px]
    return r * 256 + g + b / 256 - 32768
pts = [(-105.5892, 39.9050), (-105.6444, 39.9022), (-105.7611, 39.8881), (-105.7950, 39.8850)]
out = []
dist = 0.0
for a, b in zip(pts, pts[1:]):
    seg = math.hypot((b[0] - a[0]) * 85.3, (b[1] - a[1]) * 111.0)
    n = int(seg / 0.05)
    for i in range(n):
        f = i / n
        lon, lat = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        e = elev(lon, lat)
        out.append([round(dist + seg * f, 3), round(e * 3.28084) if e is not None else None])
    dist += seg
km_ep = math.hypot((pts[1][0] - pts[0][0]) * 85.3, (pts[1][1] - pts[0][1]) * 111.0)
km_wp = km_ep + math.hypot((pts[2][0] - pts[1][0]) * 85.3, (pts[2][1] - pts[1][1]) * 111.0)
ys = [e for _, e in out if e]
print("km", round(dist, 1), "east portal km", round(km_ep, 2), "west portal km", round(km_wp, 2), "max ft", max(ys), "min", min(ys))
mx = max(out, key=lambda p: p[1] or 0); print("crest at km", mx)
json.dump({"prof": out, "ep_km": km_ep, "wp_km": km_wp}, open("/home/user/rp/edit/rp_profile.json", "w"))
