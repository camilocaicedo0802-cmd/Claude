"""python3 usgs.py SERVICE_URL LAYER lon0,lat0,lon1,lat1 OUT.geojson [where]  -- paged ArcGIS query to GeoJSON"""
import sys, json, time, urllib.request, urllib.parse
url, layer, bbox, out = sys.argv[1:5]
where = sys.argv[5] if len(sys.argv) > 5 else "1=1"
feats, off = [], 0
while True:
    q = urllib.parse.urlencode({"where": where, "geometry": bbox, "geometryType": "esriGeometryEnvelope", "inSR": 4326,
                                "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "outSR": 4326, "f": "geojson",
                                "resultOffset": off, "resultRecordCount": 1000})
    for k in range(4):
        try:
            with urllib.request.urlopen(f"{url}/{layer}/query?{q}", timeout=120) as r:
                d = json.load(r)
            break
        except Exception as e:
            print("retry", e, flush=True); time.sleep(5 * (k + 1))
    else:
        sys.exit("failed")
    fs = d.get("features", [])
    feats += fs
    if len(fs) < 1000 and not d.get("exceededTransferLimit") and not d.get("properties", {}).get("exceededTransferLimit"):
        break
    off += len(fs)
json.dump({"type": "FeatureCollection", "features": feats}, open(out, "w"))
print(out, len(feats))
