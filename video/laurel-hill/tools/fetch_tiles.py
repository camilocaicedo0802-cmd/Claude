import math, os, sys, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
def deg2num(lat, lon, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y
jobs = []
for z, (lon0, lat0, lon1, lat1) in [(10, (-82.4, 38.4, -73.4, 43.1)), (7, (-84.5, 37.0, -69.0, 46.0)), (11, (-79.9, 39.75, -78.6, 40.45))]:
    x0, y0 = deg2num(lat1, lon0, z); x1, y1 = deg2num(lat0, lon1, z)
    for x in range(int(x0), int(x1) + 1):
        for y in range(int(y0), int(y1) + 1):
            jobs.append((z, x, y))
def get(j):
    z, x, y = j
    p = f"tiles/{z}_{x}_{y}.png"
    if os.path.exists(p): return
    for k in range(4):
        try:
            urllib.request.urlretrieve(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png", p); return
        except Exception as e:
            time.sleep(2)
    print("fail", j)
with ThreadPoolExecutor(8) as ex: list(ex.map(get, jobs))
print(len(jobs))
