"""Descarga las capas de Natural Earth (dominio público) que usa maps.py y extrae las carreteras de una zona.

usage: python natural_earth.py CARPETA_MAP [PREFIJO lon0,lat0,lon1,lat1]
ej.:   python natural_earth.py assets/map dp -125,32,-110,45   -> assets/map/roads_dp.geojson
maps.py elige el archivo de carreteras por el prefijo del nombre del mapa (cg_ -> roads_cg.geojson, …):
añade el prefijo nuevo en BaseMap._draw_vectors y en la capa "road" de MapScene."""
import json, os, sys, urllib.request

BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
LAYERS = ["ne_10m_admin_1_states_provinces_lakes", "ne_10m_lakes", "ne_10m_rivers_lake_centerlines", "ne_10m_coastline",
          "ne_10m_populated_places_simple", "ne_10m_roads"]
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for name in LAYERS:
    p = os.path.join(out, name + ".geojson")
    if not (os.path.exists(p) and os.path.getsize(p) > 0):
        urllib.request.urlretrieve(BASE + name + ".geojson", p)
    print(name, os.path.getsize(p) // 1024, "KB")
if len(sys.argv) > 3:
    pre = sys.argv[2]
    lon0, lat0, lon1, lat1 = map(float, sys.argv[3].split(","))
    fc = json.load(open(os.path.join(out, "ne_10m_roads.geojson")))
    keep = []
    for f in fc["features"]:
        pr, g = f["properties"], f["geometry"]
        if pr.get("sov_a3") != "USA" or pr.get("level") not in ("Interstate", "Federal") or not g:
            continue
        lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        if any(lon0 <= x <= lon1 and lat0 <= y <= lat1 for ln in lines for x, y in ln):
            keep.append({"type": "Feature", "properties": {"name": pr.get("name"), "level": pr.get("level")}, "geometry": g})
    json.dump({"type": "FeatureCollection", "features": keep}, open(os.path.join(out, f"roads_{pre}.geojson"), "w"))
    print(f"roads_{pre}.geojson:", len(keep), "tramos")
