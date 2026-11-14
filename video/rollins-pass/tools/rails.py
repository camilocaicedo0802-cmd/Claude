"""Builds edit/rp_routes.json: rail routes along USGS rail lines (1M-scale national rail for the region, The National Map
railroads for the Front Range), via waypoints, by shortest path on the line network."""
import json, heapq, math
def graph(files, snap):
    adj, coord = {}, {}
    key = lambda p: (round(p[0] / snap), round(p[1] / snap))
    for fn in files:
        for ft in json.load(open(fn))["features"]:
            g = ft["geometry"]
            if not g: continue
            for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                for a, b in zip(ln, ln[1:]):
                    ka, kb = key(a), key(b)
                    if ka == kb: continue
                    coord.setdefault(ka, tuple(a[:2])); coord.setdefault(kb, tuple(b[:2]))
                    d = math.hypot((a[0] - b[0]) * 0.77, a[1] - b[1])
                    adj.setdefault(ka, {})[kb] = d; adj.setdefault(kb, {})[ka] = d
    return adj, coord
def sp(adj, coord, a, b):
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
    if kb not in prev and kb != ka:
        print("NO PATH", a, b); return [a, b]
    out, u = [kb], kb
    while u != ka:
        u = prev[u]; out.append(u)
    return [coord[k] for k in out[::-1]]
def route(adj, coord, wps):
    pts = []
    for a, b in zip(wps, wps[1:]):
        seg = sp(adj, coord, a, b)
        pts += seg if not pts else seg[1:]
    km = sum(math.hypot((p[0] - q[0]) * 85, (p[1] - q[1]) * 111) for p, q in zip(pts, pts[1:]))
    return pts, round(km)
A, C = graph(["/home/user/rp/assets/map/rp/reg_rail.geojson"], 0.002)
DEN, SLC = (-104.9990, 39.7530), (-111.905, 40.762)
R = {}
R["overland"] = route(A, C, [DEN, (-104.8202, 41.14), (-105.5911, 41.3114), (-107.2387, 41.791), (-109.4662, 41.5286), (-111.9738, 41.223), SLC])
R["drg_south"] = route(A, C, [DEN, (-104.8214, 38.8339), (-104.6139, 38.2556), (-105.2422, 38.4406), (-105.9986, 38.5347), (-106.3111, 39.3625), (-107.0656, 39.6447), (-107.3248, 39.5505), (-108.5506, 39.0639), (-110.8541, 39.684), (-111.0829, 39.9285), (-111.6585, 40.2338), SLC])
R["moffat_craig"] = route(A, C, [DEN, (-105.6445, 39.9033), (-105.9194, 40.0647), (-106.3728, 40.055), (-106.6956, 39.8725), (-106.8164, 40.4728), (-107.5553, 40.5169)])
R["dotsero"] = route(A, C, [(-106.6956, 39.8725), (-107.0656, 39.6447)])
R["dotsero_slc"] = route(A, C, [(-107.0656, 39.6447), (-107.3248, 39.5505), (-108.5506, 39.0639), (-110.8541, 39.684), (-111.0829, 39.9285), (-111.6585, 40.2338), SLC])
R["den_chey"] = route(A, C, [DEN, (-104.8202, 41.14)])
for k, (p, km) in R.items(): print(k, len(p), km, "km", round(km / 1.609), "mi")
A2, C2 = graph(["/home/user/rp/assets/map/rp/mid_38.geojson", "/home/user/rp/assets/map/rp/r_38.geojson"], 0.0003)
R["front"] = route(A2, C2, [DEN, (-105.0875, 39.8028), (-105.4336, 39.9297), (-105.5011, 39.9172), (-105.5892, 39.905), (-105.6445, 39.9033)])
R["tunnel"] = route(A2, C2, [(-105.6445, 39.9033), (-105.7633, 39.888), (-105.8172, 39.945)])
for k in ("front", "tunnel"): print(k, len(R[k][0]), R[k][1], "km")
json.dump({k: v[0] for k, v in R.items()}, open("/home/user/rp/edit/rp_routes.json", "w"))
