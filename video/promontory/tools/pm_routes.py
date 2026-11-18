"""edit/pm_route.json: Promontory line (1869-1942) from USGS roads on the old grade, Lucin Cutoff from USGS railroads,
1869 Central Pacific / Union Pacific routes (waypoints), Kelton stage road (schematic)."""
import json, heapq, math
src = "/home/user/pm/assets/map/pm/"
def graph(files, names=None, snap=2e-4):
    A, C = {}, {}
    k = lambda p: (round(p[0] / snap), round(p[1] / snap))
    for fn in files:
        for ft in json.load(open(src + fn))["features"]:
            nm = (ft["properties"].get("name") or ft["properties"].get("NAME") or "")
            if names and nm not in names: continue
            g = ft["geometry"]
            if not g: continue
            for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                for a, b in zip(ln, ln[1:]):
                    ka, kb = k(a), k(b)
                    if ka == kb: continue
                    C.setdefault(ka, tuple(a[:2])); C.setdefault(kb, tuple(b[:2]))
                    d = math.hypot((a[0] - b[0]) * 0.75, a[1] - b[1])
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
        ends = [[k for k in c if len(A[k]) == 1] or list(c) for c in cs]
        best = None
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                for a in ends[i]:
                    for b in ends[j]:
                        d = math.hypot((C[a][0] - C[b][0]) * 83.5, (C[a][1] - C[b][1]) * 111.0)
                        if best is None or d < best[0]: best = (d, a, b)
        if best[0] > maxkm: return
        d = math.hypot((C[best[1]][0] - C[best[2]][0]) * 0.75, C[best[1]][1] - C[best[2]][1])
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
def km(r): return sum(math.hypot((p[0] - q[0]) * 83.5, (p[1] - q[1]) * 111.0) for p, q in zip(r, r[1:]))
def ends(A, C):
    xs = sorted(C.values()); return xs[0], xs[-1]
# --- old line: Old Railroad Grade Rd (Terrace -> Monument), Golden Spike Loop/Drive (over the summit)
A, C = graph(["q_32.geojson"], ("Old Railroad Grade Rd",)); bridge(A, C, 6.0)
w0, e0 = ends(A, C); grade_w = sp(A, C, w0, e0)
A2, C2 = graph(["q_32.geojson"], ("Golden Spike Loop", "Golden Spike Drive", "Golden Spike Loop Rd")); bridge(A2, C2, 3.0)
w1 = min(C2.values()); e1 = max((p for p in C2.values() if p[0] < -112.40), key=lambda p: p[0]); summit = sp(A2, C2, w1, (-112.5483, 41.6185)) + sp(A2, C2, (-112.5483, 41.6185), e1)[1:]
LUCIN, TERRACE, KELTON, ROZEL, PROM, CORINNE, OGDEN = (-113.9105, 41.3483), (-113.533, 41.502), (-113.1064, 41.746), (-112.6467, 41.586), (-112.5483, 41.6185), (-112.1102, 41.5510), (-111.9740, 41.2230)
old = [LUCIN, (-113.80, 41.39), (-113.69, 41.45)] + grade_w + [(-112.80, 41.69), (-112.72, 41.64), ROZEL] + summit + [(-112.33, 41.60), (-112.20, 41.56), CORINNE, (-112.05, 41.40), OGDEN]
print("grade_w", len(grade_w), round(km(grade_w), 1), "km", grade_w[0], grade_w[-1]); print("summit", len(summit), summit[0], summit[-1])
print("old", round(km(old), 1), "km", round(km(old) / 1.609, 1), "mi")
# --- Lucin Cutoff: current railroad network Ogden -> Lucin
A3, C3 = graph(["r_38.geojson"], snap=3e-4); bridge(A3, C3, 0.8)
cut = sp(A3, C3, OGDEN, LUCIN)
print("cutoff", len(cut), round(km(cut), 1), "km", round(km(cut) / 1.609, 1), "mi")
# Ogden -> Promontory (the old way, east part) for comparison
cp1869 = [(-121.494, 38.582), (-121.288, 38.752), (-120.953, 39.101), (-120.668, 39.297), (-120.33, 39.316), (-120.183, 39.328), (-119.813, 39.530),
          (-119.284, 39.632), (-118.473, 40.179), (-117.736, 40.973), (-116.934, 40.642), (-116.104, 40.714), (-115.763, 40.832), (-114.965, 41.112),
          (-114.193, 41.262), LUCIN, TERRACE, KELTON, (-112.843, 41.706), ROZEL, PROM]
up1869 = [(-95.934, 41.257), (-96.498, 41.433), (-97.368, 41.430), (-98.342, 40.925), (-99.081, 40.699), (-100.765, 41.124), (-102.264, 40.988),
          (-102.978, 41.143), (-104.820, 41.140), (-105.39, 41.13), (-105.591, 41.311), (-106.201, 41.896), (-107.238, 41.791), (-109.203, 41.587),
          (-109.466, 41.529), (-109.965, 41.594), (-110.963, 41.268), (-111.441, 40.973), (-111.495, 41.020), (-111.547, 41.06), (-111.677, 41.036),
          (-111.92, 41.14), OGDEN, CORINNE, (-112.33, 41.60), PROM]
stage = [KELTON, (-113.30, 41.92), (-113.65, 42.08), (-113.88, 42.23), (-114.33, 42.44), (-114.76, 42.62), (-115.35, 42.95), (-115.69, 43.13), (-116.202, 43.615),
         (-116.95, 44.08), (-117.834, 44.775), (-118.088, 45.325), (-118.788, 45.672), (-118.343, 46.065)]
json.dump({"old": old, "cutoff": cut, "cp": cp1869, "up": up1869, "stage": stage}, open("/home/user/pm/edit/pm_route.json", "w"))
