"""edit/rr_route.json: the 1915 Ridge Route from USGS roads (Ridge Route Rd / Old Ridge Rte) and USFS road 8N04 (Old Ridge Route)."""
import json, heapq, math
src = "/home/user/rr/assets/map/rr/"
segs = []
for fn, key, names in (("r_32.geojson", "name", ("RIDGE ROUTE RD", "OLD RIDGE RTE")), ("r_31.geojson", "name", ("OLD RIDGE RTE", "RIDGE ROUTE RD")),
                       ("fs_roads.geojson", "id", ("8N04",)), ("fs_closed.geojson", "id", ("8N04",))):
    for ft in json.load(open(src + fn))["features"]:
        if (ft["properties"].get(key) or "").upper().strip() in names:
            g = ft["geometry"]
            for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                segs.append([tuple(p[:2]) for p in ln])
key = lambda p: (round(p[0] / 2e-4), round(p[1] / 2e-4))
adj, coord = {}, {}
def add(a, b):
    ka, kb = key(a), key(b)
    if ka == kb: return
    coord.setdefault(ka, a); coord.setdefault(kb, b)
    d = math.hypot((a[0] - b[0]) * 0.82, a[1] - b[1])
    adj.setdefault(ka, {})[kb] = d; adj.setdefault(kb, {})[ka] = d
for s in segs:
    for a, b in zip(s, s[1:]): add(a, b)
def comps():
    seen, out = set(), []
    for k in adj:
        if k in seen: continue
        st, c = [k], {k}
        while st:
            u = st.pop()
            for v in adj[u]:
                if v not in c: c.add(v); st.append(v)
        seen |= c; out.append(c)
    return out
while True:
    cs = comps(); best = None
    ends = [[k for k in c if len(adj[k]) == 1] or list(c) for c in cs]
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            for a in ends[i]:
                for b in ends[j]:
                    d = math.hypot((coord[a][0] - coord[b][0]) * 91.6, (coord[a][1] - coord[b][1]) * 111.0)
                    if best is None or d < best[0]: best = (d, a, b)
    if best is None or best[0] > 2.5: break
    print("bridge", round(best[0] * 1000), "m", coord[best[1]], coord[best[2]])
    add(coord[best[1]], coord[best[2]])
def sp(a, b):
    ka = min(coord, key=lambda k: math.hypot(coord[k][0] - a[0], coord[k][1] - a[1]))
    kb = min(coord, key=lambda k: math.hypot(coord[k][0] - b[0], coord[k][1] - b[1]))
    dist, prev, q = {ka: 0}, {}, [(0, ka)]
    while q:
        d, u = heapq.heappop(q)
        if u == kb: break
        if d > dist[u]: continue
        for v, w in adj[u].items():
            if d + w < dist.get(v, 1e9): dist[v] = d + w; prev[v] = u; heapq.heappush(q, (d + w, v))
    out, u = [kb], kb
    while u != ka: u = prev[u]; out.append(u)
    return [coord[k] for k in out[::-1]]
route = sp((-118.6212, 34.4930), (-118.7300, 34.7650))
km = sum(math.hypot((p[0] - q[0]) * 91.6, (p[1] - q[1]) * 111.0) for p, q in zip(route, route[1:]))
print(len(segs), "segs", len(route), "pts", round(km, 1), "km", round(km / 1.609, 1), "mi", route[0], route[-1])
json.dump({"ridge": route}, open("/home/user/rr/edit/rr_route.json", "w"))

# north end: Sandberg -> Quail Lake -> Gorman along local roads (USGS), then down the Grapevine along I-5 (old grade is under it)
import sys
sys.path.insert(0, "/home/user/rr/work")
def graph(files, names=None, snap=3e-4):
    A, C = {}, {}
    k = lambda p: (round(p[0] / snap), round(p[1] / snap))
    for fn in files:
        for ft in json.load(open(src + fn))["features"]:
            if names and (ft["properties"].get("name") or "").upper() not in names: continue
            g = ft["geometry"]
            if not g: continue
            for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                for a, b in zip(ln, ln[1:]):
                    ka, kb = k(a), k(b)
                    if ka == kb: continue
                    C.setdefault(ka, tuple(a[:2])); C.setdefault(kb, tuple(b[:2]))
                    d = math.hypot((a[0] - b[0]) * 0.82, a[1] - b[1])
                    A.setdefault(ka, {})[kb] = d; A.setdefault(kb, {})[ka] = d
    return A, C
def sp2(A, C, a, b):
    ka = min(C, key=lambda k: math.hypot(C[k][0] - a[0], C[k][1] - a[1]))
    kb = min(C, key=lambda k: math.hypot(C[k][0] - b[0], C[k][1] - b[1]))
    dist, prev, q = {ka: 0}, {}, [(0, ka)]
    while q:
        d, u = heapq.heappop(q)
        if u == kb: break
        if d > dist[u]: continue
        for v, w in A[u].items():
            if d + w < dist.get(v, 1e9): dist[v] = d + w; prev[v] = u; heapq.heappush(q, (d + w, v))
    if kb not in prev: print("NO PATH", a, b); return [a, b]
    out, u = [kb], kb
    while u != ka: u = prev[u]; out.append(u)
    return [C[k] for k in out[::-1]]
A, C = graph(["r_32.geojson", "r_31.geojson", "r_30.geojson"])
north = sp2(A, C, route[-1], (-118.8526, 34.7961))
A2, C2 = graph(["mid_29.geojson"], ("GOLDEN STATE FWY", "GOLDEN STATE HWY", "I- 5", "I-5"))
grape = sp2(A2, C2, (-118.8526, 34.7961), (-118.9235, 34.9380))
full = route + north[1:] + grape[1:]
km = sum(math.hypot((p[0] - q[0]) * 91.6, (p[1] - q[1]) * 111.0) for p, q in zip(full, full[1:]))
print("full", len(full), round(km, 1), "km", round(km / 1.609, 1), "mi")
# I-5 corridor, piecewise between waypoints (the freeway has split carriageways)
A3, C3 = graph(["mid_29.geojson"], ("GOLDEN STATE FWY", "GOLDEN STATE HWY", "I- 5", "I-5"), snap=6e-4)
wps = [(-118.6060, 34.4700), (-118.660, 34.560), (-118.7316, 34.6100), (-118.7664, 34.6650), (-118.8000, 34.7400), (-118.8526, 34.7961), (-118.9235, 34.9380)]
i5 = []
for a_, b_ in zip(wps, wps[1:]):
    s_ = sp2(A3, C3, a_, b_); i5 += s_ if not i5 else s_[1:]
json.dump({"ridge": route, "ridge_full": full, "i5": i5}, open("/home/user/rr/edit/rr_route.json", "w"))
print("i5", len(i5))
