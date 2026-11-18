"""edit/rr_profile.json: elevation (Mapzen terrarium z13) along the Ridge Route, Castaic -> Grapevine."""
import json, math, os
import numpy as np
from PIL import Image
T = "/home/user/rr/assets/map/tiles"
cache = {}
def elev(lon, lat, z=13):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    tx, ty = int(x), int(y)
    p = f"{T}/{z}_{tx}_{ty}.png"
    if p not in cache:
        cache[p] = np.asarray(Image.open(p).convert("RGB")).astype(np.float32) if os.path.exists(p) else None
    a = cache[p]
    if a is None:
        return None
    r, g, b = a[min(int((y - ty) * 256), 255), min(int((x - tx) * 256), 255)]
    return r * 256 + g + b / 256 - 32768
pts = json.load(open("/home/user/rr/edit/rr_route.json"))["ridge_full"]
out, dist = [], 0.0
for i, p in enumerate(pts):
    if i:
        q = pts[i - 1]
        dist += math.hypot((p[0] - q[0]) * 91.6, (p[1] - q[1]) * 111.0)
    if i % 4 == 0:
        e = elev(*p)
        if e is not None:
            out.append([round(dist, 3), round(e * 3.28084), round(p[0], 5), round(p[1], 5)])
mx = max(out, key=lambda r: r[1])
print(len(out), "pts", round(dist, 1), "km; max", mx, "start", out[0][1], "end", out[-1][1])
json.dump(out, open("/home/user/rr/edit/rr_profile.json", "w"))
