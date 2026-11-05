"""Descarga teselas de relieve Mapzen/Tilezen (terrarium, Amazon Open Data) para los mapas base.

usage: python fetch_tiles.py CARPETA_MAP z:lon0,lat0,lon1,lat1 [z:lon0,lat0,lon1,lat1 ...]
ej.:   python fetch_tiles.py assets/map 10:-74.9,40.3,-70.5,42.85 12:-74.10,40.60,-73.82,40.80"""
import math, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor


def deg2num(lat, lon, z):
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n


out_dir = sys.argv[1]
os.makedirs(os.path.join(out_dir, "tiles"), exist_ok=True)
jobs = []
for spec in sys.argv[2:]:
    z, bb = spec.split(":")
    z = int(z)
    lon0, lat0, lon1, lat1 = map(float, bb.split(","))
    x0, y0 = deg2num(lat1, lon0, z)
    x1, y1 = deg2num(lat0, lon1, z)
    jobs += [(z, x, y) for x in range(int(x0), int(x1) + 1) for y in range(int(y0), int(y1) + 1)]


def get(j):
    z, x, y = j
    p = os.path.join(out_dir, "tiles", f"{z}_{x}_{y}.png")
    if os.path.exists(p):
        return
    for _ in range(4):
        try:
            urllib.request.urlretrieve(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x % (2 ** z)}/{y}.png", p)
            return
        except Exception:
            time.sleep(2)
    print("fallo", j)


with ThreadPoolExecutor(8) as ex:
    list(ex.map(get, jobs))
print("teselas", len(jobs))
