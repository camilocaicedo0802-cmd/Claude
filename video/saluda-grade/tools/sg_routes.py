"""edit/sg_route.json: the Asheville-Spartanburg line (Saluda Grade) from the FRA/USGS rail network, and the Pacolet River."""
import json, heapq, math
src = "/home/user/sg/assets/map/sg/"
def graph(fn, filt=None, snap=2e-4):
    A, C = {}, {}
    k = lambda p: (round(p[0] / snap), round(p[1] / snap))
    for ft in json.load(open(src + fn))["features"]:
        g = ft["geometry"]
        if not g or (filt and not filt(ft["properties"])): continue
        for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            for a, b in zip(ln, ln[1:]):
                ka, kb = k(a), k(b)
                if ka == kb: continue
                C.setdefault(ka, tuple(a[:2])); C.setdefault(kb, tuple(b[:2]))
                d = math.hypot((a[0] - b[0]) * 0.82, a[1] - b[1])
                A.setdefault(ka, {})[kb] = d; A.setdefault(kb, {})[ka] = d
    return A, C
def bridge(A, C, maxkm):
    while True:
        seen, cs = set(), []
        for k0 in A:
            if k0 in seen: continue
            st, c = [k0], {k0}
            while st:
                u = st.pop()
                for v in A[u]:
                    if v not in c: c.add(v); st.append(v)
            seen |= c; cs.append(c)
        if len(cs) < 2: return
        ends = [[k for k in c if len(A[k]) == 1] or list(c)[:50] for c in cs]
        best = None
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                for a in ends[i]:
                    for b in ends[j]:
                        d = math.hypot((C[a][0] - C[b][0]) * 91.0, (C[a][1] - C[b][1]) * 111.0)
                        if best is None or d < best[0]: best = (d, a, b)
        if best is None or best[0] > maxkm: return
        d = math.hypot((C[best[1]][0] - C[best[2]][0]) * 0.82, C[best[1]][1] - C[best[2]][1])
        A[best[1]][best[2]] = d; A[best[2]][best[1]] = d
def sp(A, C, a, b):
    ka = min(C, key=lambda k: math.hypot(C[k][0] - a[0], C[k][1] - a[1]))
    kb = min(C, key=lambda k: math.hypot(C[k][0] - b[0], C[k][1] - b[1]))
    dist, prev, q = {ka: 0}, {}, [(0, ka)]
    while q:
        d, u = heapq.heappop(q)
        if u == kb: break
        if d > dist[u]: continue
        for v, w in A[u].items():
            if d + w < dist.get(v, 1e9): dist[v] = d + w; prev[v] = u; heapq.heappush(q, (d + w, v))
    if kb != ka and kb not in prev: print("NO PATH", a, b); return [a, b]
    out, u = [kb], kb
    while u != ka: u = prev[u]; out.append(u)
    return [C[k] for k in out[::-1]]
km = lambda r: sum(math.hypot((p[0] - q[0]) * 91.0, (p[1] - q[1]) * 111.0) for p, q in zip(r, r[1:]))
A, C = graph("r_38.geojson"); bridge(A, C, 0.6)
WP = [(-82.554, 35.589), (-82.50, 35.43), (-82.461, 35.318), (-82.4207, 35.2801), (-82.3493, 35.2362), (-82.3226, 35.2196), (-82.2385, 35.2082),
      (-82.1893, 35.1751), (-82.0901, 35.0471), (-81.932, 34.9496)]
line = []
for a, b in zip(WP, WP[1:]):
    s = sp(A, C, a, b); line += s if not line else s[1:]
grade = sp(A, C, (-82.3493, 35.2362), (-82.3226, 35.2196))
print("line", len(line), round(km(line), 1), "km", round(km(line) / 1.609, 1), "mi"); print("grade Saluda-Melrose", len(grade), round(km(grade), 2), "km", round(km(grade) / 1.609, 2), "mi")
cr = json.load(open(src + "creeks.geojson"))["features"]
pac = []
for f in cr:
    nm = f["properties"].get("GNIS_NAME") or f["properties"].get("gnis_name")
    if nm in ("North Pacolet River", "Pacolet River"):
        g = f["geometry"]; pac += (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]])
print("pacolet segs", len(pac))
json.dump({"line": line, "grade": grade, "pacolet": [[[round(x, 5), round(y, 5)] for x, y, *_ in l] for l in pac]}, open("/home/user/sg/edit/sg_route.json", "w"))
