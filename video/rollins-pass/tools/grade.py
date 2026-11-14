"""Builds edit/rp_grade.json: the old Moffat Road grade over Rollins Pass from USGS roads (MOFFAT ROAD / GILPIN COUNTY 16)."""
import json, heapq, math, numpy as np
segs = []
for ft in json.load(open("/home/user/rp/assets/map/rp/r_32.geojson"))["features"]:
    n = (ft["properties"].get("name") or "").upper()
    if n in ("MOFFAT ROAD", "GILPIN COUNTY 16"):
        g = ft["geometry"]
        for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            segs.append([tuple(p[:2]) for p in ln])
key = lambda p: (round(p[0] / 3e-4), round(p[1] / 3e-4))
adj, coord = {}, {}
def add(a, b):
    ka, kb = key(a), key(b)
    if ka == kb: return
    coord.setdefault(ka, a); coord.setdefault(kb, b)
    d = math.hypot((a[0] - b[0]) * math.cos(math.radians(39.9)), a[1] - b[1])
    adj.setdefault(ka, {})[kb] = d; adj.setdefault(kb, {})[ka] = d
for s in segs:
    for a, b in zip(s, s[1:]):
        add(a, b)
def comps():
    seen, out = set(), []
    for k in adj:
        if k in seen: continue
        st, c = [k], set([k])
        while st:
            u = st.pop()
            for v in adj[u]:
                if v not in c: c.add(v); st.append(v)
        seen |= c; out.append(c)
    return out
while True:  # bridge small gaps in the USGS data (< 350 m) between components
    cs = comps()
    best = None
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            for a in cs[i]:
                for b in cs[j]:
                    d = math.hypot((coord[a][0] - coord[b][0]) * 85.2, (coord[a][1] - coord[b][1]) * 111.0)
                    if best is None or d < best[0]: best = (d, a, b)
    if best is None or best[0] > 0.35: break
    print("bridge", round(best[0] * 1000), "m", coord[best[1]])
    add(coord[best[1]], coord[best[2]])
def path(a, b):
    ka = min(coord, key=lambda k: math.hypot(coord[k][0] - a[0], coord[k][1] - a[1]))
    kb = min(coord, key=lambda k: math.hypot(coord[k][0] - b[0], coord[k][1] - b[1]))
    dist, prev, q = {ka: 0}, {}, [(0, ka)]
    while q:
        d, u = heapq.heappop(q)
        if u == kb: break
        if d > dist[u]: continue
        for v, w in adj[u].items():
            if d + w < dist.get(v, 1e9):
                dist[v] = d + w; prev[v] = u; heapq.heappush(q, (d + w, v))
    out, u = [kb], kb
    while u != ka:
        u = prev[u]; out.append(u)
    return [coord[k] for k in out[::-1]]
west = path((-105.7695, 39.8976), (-105.6799, 39.9347))
east = path((-105.6624, 39.9413), (-105.5765, 39.9067))
gap = [(-105.6765, 39.9362), (-105.6720, 39.9382), (-105.6672, 39.9400)]  # summit to Needle's Eye (closed, approximate)
full = west + gap + east
km = sum(math.hypot((a[0] - b[0]) * 85.2, (a[1] - b[1]) * 111.0) for a, b in zip(full, full[1:]))
print(len(west), len(east), len(full), round(km, 1), "km")
json.dump({"west": west, "gap": gap, "east": east, "full": full}, open("/home/user/rp/edit/rp_grade.json", "w"))
