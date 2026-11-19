"""edit/cr_route.json: the Historic Columbia River Highway Troutdale-The Dalles traced on The National Map roads,
split into the stretches that survive as roads and the ones under I-84 (r_29), plus the I-84 itself."""
import json, heapq, math
src = "/home/user/cr/assets/map/cr/"
snap = 2e-4
k = lambda p: (round(p[0] / snap), round(p[1] / snap))
A, C, KIND = {}, {}, {}
def add(fn, factor, kind):
    for ft in json.load(open(src + fn))["features"]:
        g = ft["geometry"]
        if not g: continue
        for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            for a, b in zip(ln, ln[1:]):
                ka, kb = k(a), k(b)
                if ka == kb: continue
                C.setdefault(ka, tuple(a[:2])); C.setdefault(kb, tuple(b[:2]))
                d = math.hypot((a[0] - b[0]) * 0.70, a[1] - b[1]) * factor
                if d < A.get(ka, {}).get(kb, 1e9):
                    A.setdefault(ka, {})[kb] = d; A.setdefault(kb, {})[ka] = d
                    KIND[(ka, kb)] = KIND[(kb, ka)] = kind
add("r_29.geojson", 1.35, "i84")
for fn in ("r_30.geojson", "r_31.geojson", "r_32w.geojson", "r_32e.geojson"):
    add(fn, 1.0, "road")
# join dangling ends closer than ~120 m (ramps, data gaps)
keys = list(C)
grid = {}
for kk in keys:
    grid.setdefault((kk[0] // 6, kk[1] // 6), []).append(kk)
for kk in keys:
    if len(A.get(kk, {})) != 1: continue
    gx, gy = kk[0] // 6, kk[1] // 6
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for o in grid.get((gx + dx, gy + dy), []):
                if o == kk or o in A[kk]: continue
                d = math.hypot((C[o][0] - C[kk][0]) * 0.70, C[o][1] - C[kk][1])
                if d < 0.0011 and (best is None or d < best[0]): best = (d, o)
    if best:
        d, o = best; A[kk][o] = d * 1.5; A.setdefault(o, {})[kk] = d * 1.5; KIND[(kk, o)] = KIND[(o, kk)] = "road"
def near(p):
    return min(C, key=lambda q: math.hypot(C[q][0] - p[0], C[q][1] - p[1]))
def sp(a, b, pen=None):
    ka, kb = near(a), near(b)
    dist, prev, q = {ka: 0}, {}, [(0, ka)]
    while q:
        d, u = heapq.heappop(q)
        if u == kb: break
        if d > dist[u]: continue
        for v, w in A[u].items():
            if pen and KIND.get((u, v)) == pen: w *= 4.0
            if d + w < dist.get(v, 1e9): dist[v] = d + w; prev[v] = u; heapq.heappush(q, (d + w, v))
    if kb != ka and kb not in prev:
        print("NO PATH", a, b); return [ka, kb]
    out, u = [kb], kb
    while u != ka: u = prev[u]; out.append(u)
    return out[::-1]
km = lambda r: sum(math.hypot((p[0] - q[0]) * 78.0, (p[1] - q[1]) * 111.0) for p, q in zip(r, r[1:]))
WP = {"troutdale": (-122.3873, 45.5393), "corbett": (-122.2912, 45.5318), "crown": (-122.2443, 45.5394), "latourell": (-122.2181, 45.5369),
      "shepperd": (-122.1970, 45.5487), "bridalveil": (-122.1803, 45.5543), "multnomah": (-122.1154, 45.5761), "oneonta": (-122.0757, 45.5899),
      "ainsworth": (-122.0430, 45.6000), "bonneville": (-121.9520, 45.6360), "cascade": (-121.8906, 45.6698), "wyeth": (-121.7650, 45.6930),
      "viento": (-121.6680, 45.6990), "mitchell": (-121.6168, 45.7010), "hoodriver": (-121.5215, 45.7054),
      "mosier": (-121.3973, 45.6835), "rowena": (-121.2995, 45.6826), "dalles": (-121.1787, 45.5946)}
order = list(WP)
path, legs = [], {}
for a, b in zip(order, order[1:]):
    s = sp(WP[a], WP[b], "road" if (a, b) == ("hoodriver", "mosier") else None)
    legs[a + "-" + b] = (len(path) - (1 if path else 0), s)
    path += s if not path else s[1:]
# runs of the same kind
runs, cur, kind = [], [path[0]], None
for u, v in zip(path, path[1:]):
    kd = KIND.get((u, v), "road")
    if kind is None: kind = kd
    if kd != kind:
        runs.append((kind, cur)); cur = [u]; kind = kd
    cur.append(v)
runs.append((kind, cur))
pt = lambda ks: [[round(C[x][0], 5), round(C[x][1], 5)] for x in ks]
full = pt(path)
def between(a, b):
    i, j = near(WP[a]), near(WP[b])
    ia, ib = path.index(i), path.index(j)
    return pt(path[min(ia, ib):max(ia, ib) + 1])
i84 = []
for ft in json.load(open(src + "r_29.geojson"))["features"]:
    g = ft["geometry"]
    for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
        i84.append([[round(x, 5), round(y, 5)] for x, y, *_ in ln])
out = {"line": full, "road": [pt(r) for kd, r in runs if kd == "road"], "under": [pt(r) for kd, r in runs if kd == "i84"],
       "west": between("troutdale", "ainsworth"), "east_trail": between("hoodriver", "mosier"), "rowena": between("mosier", "dalles"),
       "mitchell_leg": between("viento", "hoodriver"), "gap": between("mitchell", "hoodriver"), "i84": i84,
       "wp": dict({kk: list(v) for kk, v in WP.items()}, twin=[-121.42357, 45.68563])}
print("line", len(full), round(km(full), 1), "km", round(km(full) / 1.609, 1), "mi")
print("road runs", len(out["road"]), round(sum(km(r) for r in out["road"]), 1), "km; under I-84", len(out["under"]), round(sum(km(r) for r in out["under"]), 1), "km")
json.dump(out, open("/home/user/cr/edit/cr_route.json", "w"))
