import math, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
def deg2num(lat, lon, z):
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
jobs = []
for z, (lon0, lat0, lon1, lat1) in [(8, (-74.9, 40.3, -70.5, 42.85)), (12, (-74.10, 40.60, -73.82, 40.80)),
                                     (15, (-74.008, 40.676, -73.970, 40.700))]:
    x0, y0 = deg2num(lat1, lon0, z); x1, y1 = deg2num(lat0, lon1, z)
    jobs += [(z, x, y) for x in range(int(x0), int(x1) + 1) for y in range(int(y0), int(y1) + 1)]
os.makedirs("tiles", exist_ok=True)
def get(j):
    z, x, y = j
    p = f"tiles/{z}_{x}_{y}.png"
    if os.path.exists(p): return
    for k in range(4):
        try:
            urllib.request.urlretrieve(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x % (2 ** z)}/{y}.png", p); return
        except Exception:
            time.sleep(2)
    print("fail", j)
with ThreadPoolExecutor(8) as ex: list(ex.map(get, jobs))
print("tiles", len(jobs))
