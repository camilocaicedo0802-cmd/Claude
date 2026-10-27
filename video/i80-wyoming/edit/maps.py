"""Dark relief basemaps (Mapzen terrain tiles + Natural Earth) and animated map scenes."""
import functools
import json
import math
import os

import cv2
import numpy as np
from PIL import Image

from engine import (ASSETS, BLACK, FPS, H, RED, W, WHITE, YELLOW, clamp, ease_back, ease_io, ease_out, lerp, over, prog,
                    rounded_rect_sprite, text_sprite)
from gfx import Base

MAPDIR = os.path.join(ASSETS, "map")
COORDS = {
    # Wyoming
    "laramie": (-105.591, 41.311), "cheyenne": (-104.820, 41.140), "rawlins": (-107.239, 41.791),
    "sinclair": (-107.112, 41.780), "walcott": (-106.848, 41.762), "arlington": (-106.209, 41.595),
    "elk_mtn": (-106.5375, 41.6355), "elk_town": (-106.413, 41.688), "medicine_bow": (-106.204, 41.899),
    "rock_river": (-105.974, 41.738), "hanna": (-106.564, 41.870), "bosler": (-105.697, 41.576),
    "wamsutter": (-107.979, 41.671), "rock_springs": (-109.203, 41.588), "wagonhound": (-106.30, 41.62),
    "summit": (-105.437, 41.246), "casper": (-106.313, 42.867), "evanston": (-110.963, 41.268),
    # US
    "sf": (-122.419, 37.775), "nyc": (-74.006, 40.713), "dc": (-77.037, 38.895), "chicago": (-87.630, 41.878),
    "omaha": (-95.934, 41.257), "salt_lake": (-111.891, 40.761), "reno": (-119.813, 39.530),
    "teaneck": (-74.016, 40.888), "denver": (-104.990, 39.739),
}


def deg2px(lon, lat, z):
    n = 256 * 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y


class BaseMap:
    def __init__(self, name, z, bbox, exaggerate=1.0, elo=0.0, ehi=900.0, lat_c=41.0):
        self.name, self.z = name, z
        self.elo, self.ehi, self.lat_c = elo, ehi, lat_c
        lon0, lat0, lon1, lat1 = bbox
        x0, y0 = deg2px(lon0, lat1, z)
        x1, y1 = deg2px(lon1, lat0, z)
        self.tx0, self.ty0 = int(x0 // 256), int(y0 // 256)
        self.tx1, self.ty1 = int(x1 // 256), int(y1 // 256)
        self.ox, self.oy = self.tx0 * 256, self.ty0 * 256
        self.exaggerate = exaggerate
        cache = os.path.join(MAPDIR, f"base_{name}.png")
        if os.path.exists(cache):
            self.img = np.asarray(Image.open(cache).convert("RGB")).copy()
        else:
            self.img = self.build()
            Image.fromarray(self.img).save(cache)

    def px(self, lon, lat):
        x, y = deg2px(lon, lat, self.z)
        return x - self.ox, y - self.oy

    def build(self):
        nx, ny = self.tx1 - self.tx0 + 1, self.ty1 - self.ty0 + 1
        elev = np.zeros((ny * 256, nx * 256), np.float32)
        for i in range(nx):
            for j in range(ny):
                p = os.path.join(MAPDIR, "tiles", f"{self.z}_{self.tx0 + i}_{self.ty0 + j}.png")
                if not os.path.exists(p):
                    continue
                a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
                elev[j * 256:(j + 1) * 256, i * 256:(i + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
        water = elev <= 0.5
        res = 156543.03 * math.cos(math.radians(self.lat_c)) / 2 ** self.z
        e = cv2.GaussianBlur(elev, (0, 0), 0.8) * self.exaggerate
        gy, gx = np.gradient(e, res)
        slope = np.arctan(np.hypot(gx, gy) * 2.2)
        aspect = np.arctan2(-gx, gy)
        az, alt = math.radians(315), math.radians(40)
        shade = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
        shade = np.clip(shade, 0, 1)
        en = np.clip((elev - self.elo) / (self.ehi - self.elo), 0, 1)
        low = np.array([30, 36, 40], np.float32)
        high = np.array([78, 78, 70], np.float32)
        col = low + (high - low) * en[..., None]
        col = col * (0.45 + 1.45 * shade[..., None])
        col[water] = (14, 22, 32)
        col = np.clip(col, 0, 255).astype(np.uint8)
        self._draw_vectors(col)
        return col

    def _poly_px(self, coords):
        return np.array([self.px(lon, lat) for lon, lat in coords], np.float32)

    def _draw_vectors(self, img):
        with open(os.path.join(MAPDIR, "ne_10m_rivers_lake_centerlines.geojson")) as f:
            rivers = json.load(f)
        for ft in rivers["features"]:
            g = ft["geometry"]
            lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
            for ln in lines:
                pts = self._poly_px(ln)
                if not len(pts):
                    continue
                cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, (52, 84, 112), 2, cv2.LINE_AA, shift=2)
        with open(os.path.join(MAPDIR, "ne_10m_lakes.geojson")) as f:
            lakes = json.load(f)
        for ft in lakes["features"]:
            g = ft["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for poly in polys:
                pts = self._poly_px(poly[0])
                cv2.fillPoly(img, [np.round(pts * 4).astype(np.int32)], (14, 22, 32), cv2.LINE_AA, shift=2)
        with open(os.path.join(MAPDIR, "roads_i80.geojson")) as f:
            roads = json.load(f)
        for ft in roads["features"]:
            g = ft["geometry"]
            col, w = ((120, 116, 104), 3) if ft["properties"]["name"] == "80" else ((92, 92, 88), 2)
            for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                pts = self._poly_px(ln)
                cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, col, w, cv2.LINE_AA, shift=2)
        with open(os.path.join(MAPDIR, "ne_10m_admin_1_states_provinces_lakes.geojson")) as f:
            states = json.load(f)
        self.states = {}
        for ft in states["features"]:
            pr = ft["properties"]
            if pr.get("adm0_a3") not in ("USA", "CAN"):
                continue
            g = ft["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            arrs = [self._poly_px(p[0]) for p in polys]
            self.states[pr.get("name")] = arrs
            for pts in arrs:
                cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], True, (95, 98, 100), 2, cv2.LINE_AA, shift=2)


@functools.lru_cache(maxsize=4)
def basemap(name):
    if name == "us":
        return BaseMap("us", 6, (-126.0, 23.0, -65.0, 51.0), 2.2, 0.0, 3200.0, 38.0)
    if name == "wy":
        return BaseMap("wy", 9, (-111.6, 40.4, -103.6, 45.3), 1.2, 1100.0, 3800.0, 42.8)
    if name == "loc":
        return BaseMap("loc", 11, (-107.7, 40.95, -105.1, 42.25), 1.0, 1850.0, 3400.0, 41.6)
    raise KeyError(name)


@functools.lru_cache(maxsize=4)
def state_outline(name, mapname):
    bm = basemap(mapname)
    with open(os.path.join(MAPDIR, "ne_10m_admin_1_states_provinces_lakes.geojson")) as f:
        states = json.load(f)
    for ft in states["features"]:
        if ft["properties"].get("name") == name and ft["properties"].get("adm0_a3") == "USA":
            g = ft["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            return [bm._poly_px(p[0]) for p in polys]
    return []


@functools.lru_cache(maxsize=16)
def road_chain(name, bbox=(-180, -90, 180, 90), level=None):
    """Stitch the Natural Earth pieces of one highway into a single west-to-east lon/lat polyline inside bbox."""
    lon0, lat0, lon1, lat1 = bbox
    with open(os.path.join(MAPDIR, "roads_i80.geojson")) as f:
        fc = json.load(f)
    segs = []
    for ft in fc["features"]:
        pr = ft["properties"]
        if pr["name"] != name or (level and pr["level"] != level):
            continue
        g = ft["geometry"]
        for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            a = np.array(ln, np.float64)
            inside = (a[:, 0] >= lon0) & (a[:, 0] <= lon1) & (a[:, 1] >= lat0) & (a[:, 1] <= lat1)
            if inside.any():
                segs.append(a)
    if not segs:
        return np.zeros((0, 2))
    k = min(range(len(segs)), key=lambda i: min(segs[i][0, 0], segs[i][-1, 0]))
    cur = segs.pop(k)
    if cur[-1, 0] < cur[0, 0]:
        cur = cur[::-1]
    out = [cur]
    while segs:
        end = out[-1][-1]
        best, bi, rev = 1e9, -1, False
        for i, sg in enumerate(segs):
            for r, p in ((False, sg[0]), (True, sg[-1])):
                d = math.hypot(*(p - end))
                if d < best:
                    best, bi, rev = d, i, r
        if best > 0.6:
            break
        sg = segs.pop(bi)
        out.append(sg[::-1] if rev else sg)
    pts = np.vstack(out)
    inside = (pts[:, 0] >= lon0) & (pts[:, 0] <= lon1) & (pts[:, 1] >= lat0) & (pts[:, 1] <= lat1)
    return pts[inside]


def catmull(points, n=24):
    pts = np.array(points, np.float64)
    if len(pts) < 3:
        return pts
    P = np.vstack([pts[0], pts, pts[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return np.array(out)


def partial(path, frac):
    if frac >= 1:
        return path
    seg = np.hypot(*np.diff(path, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    L = cum[-1] * frac
    k = np.searchsorted(cum, L)
    if k <= 0:
        return path[:1]
    a = (L - cum[k - 1]) / max(seg[k - 1], 1e-6)
    return np.vstack([path[:k], path[k - 1] + (path[k] - path[k - 1]) * a])


class MapScene(Base):
    """cam: list of (time, lon, lat, zoom) keyframes (zoom 1 = 1 basemap px per screen px).
    layers: list of dicts {type: route|pin|label|state|rail|marker, ...} with appear times."""

    def __init__(self, mapname, cams, layers=(), title=None, grade_dark=1.0):
        self.mapname, self.cams, self.layers, self.title = mapname, cams, layers, title

    def _cam(self, t):
        cs = self.cams
        if t <= cs[0][0]:
            return cs[0][1:]
        for a, b in zip(cs, cs[1:]):
            if t <= b[0]:
                k = ease_io((t - a[0]) / max(b[0] - a[0], 1e-6))
                # zoom interpolated geometrically
                z = math.exp(lerp(math.log(a[3]), math.log(b[3]), k))
                return lerp(a[1], b[1], k), lerp(a[2], b[2], k), z
        return cs[-1][1:]

    def frame(self, t):
        bm = basemap(self.mapname)
        lon, lat, z = self._cam(t)
        cx, cy = bm.px(lon, lat)
        M = np.array([[z, 0, W / 2 - z * cx], [0, z, H / 2 - z * cy]], np.float32)
        out = cv2.warpAffine(bm.img, M, (W, H), flags=cv2.INTER_LINEAR if z >= 0.7 else cv2.INTER_AREA,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(14, 22, 32))

        def scr(pts):
            return np.stack([pts[:, 0] * z + M[0, 2], pts[:, 1] * z + M[1, 2]], 1)

        for L in self.layers:
            typ = L["type"]
            t0 = L.get("t0", 0.0)
            if t < t0 or (L.get("t1") is not None and t > L["t1"] + 0.4):
                continue
            fade = 1.0 if L.get("t1") is None else 1 - prog(t, L["t1"], 0.4)
            if typ == "state":
                arrs = state_outline(L["name"], self.mapname)
                a = ease_io(prog(t, t0, 0.6)) * fade
                layer = out.copy()
                for pts in arrs:
                    sp = np.round(scr(pts) * 4).astype(np.int32)
                    if L.get("fill"):
                        cv2.fillPoly(layer, [sp], L.get("fill"), cv2.LINE_AA, shift=2)
                for pts in arrs:
                    sp = np.round(scr(pts) * 4).astype(np.int32)
                    cv2.polylines(layer, [sp], True, L.get("color", YELLOW), L.get("width", 4), cv2.LINE_AA, shift=2)
                out = cv2.addWeighted(layer, a * L.get("alpha", 1.0), out, 1 - a * L.get("alpha", 1.0), 0)
            elif typ in ("route", "rail", "road"):
                if typ == "road":
                    ll = road_chain(L["name"], tuple(L.get("bbox", (-180, -90, 180, 90))), L.get("level"))
                    if L.get("reverse"):
                        ll = ll[::-1]
                    path = np.array([bm.px(lon, lat) for lon, lat in ll])
                else:
                    pts = np.array([bm.px(*COORDS[n]) if isinstance(n, str) else bm.px(*n) for n in L["path"]])
                    path = catmull(pts, 20)
                frac = ease_io(prog(t, t0, L.get("draw", 2.0)))
                part = scr(partial(path, frac))
                if len(part) >= 2:
                    col = L.get("color", YELLOW)
                    w = L.get("width", 6)
                    layer = out.copy()
                    if L.get("dash"):
                        seg = np.hypot(*np.diff(part, axis=0).T)
                        cum = np.concatenate([[0], np.cumsum(seg)])
                        on = (cum // L["dash"]) % 2 == 0
                        for k in range(len(part) - 1):
                            if on[k]:
                                p0, p1 = part[k], part[k + 1]
                                cv2.line(layer, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), col, w, cv2.LINE_AA)
                    else:
                        ip = np.round(part * 4).astype(np.int32)
                        cv2.polylines(layer, [ip], False, (0, 0, 0), w + 6, cv2.LINE_AA, shift=2)
                        cv2.polylines(layer, [ip], False, col, w, cv2.LINE_AA, shift=2)
                    if L.get("traffic"):
                        full = scr(path)
                        seg = np.hypot(*np.diff(full, axis=0).T)
                        cum = np.concatenate([[0], np.cumsum(seg)])
                        n = L["traffic"]
                        for j in range(n):
                            d = ((t - t0) * L.get("speed", 140) + j * cum[-1] / n) % cum[-1]
                            k = min(max(int(np.searchsorted(cum, d)), 1), len(full) - 1)
                            p = full[k - 1] + (full[k] - full[k - 1]) * (d - cum[k - 1]) / max(seg[k - 1], 1e-6)
                            cv2.circle(layer, (int(p[0]), int(p[1])), max(4, w), WHITE, -1, cv2.LINE_AA)
                    if typ == "rail":  # cross ties
                        seg = np.hypot(*np.diff(part, axis=0).T)
                        cum = np.concatenate([[0], np.cumsum(seg)])
                        step = 22
                        for d in np.arange(step, cum[-1], step):
                            k = np.searchsorted(cum, d)
                            if k <= 0 or k >= len(part):
                                continue
                            p = part[k - 1] + (part[k] - part[k - 1]) * (d - cum[k - 1]) / max(seg[k - 1], 1e-6)
                            v = part[k] - part[k - 1]
                            nrm = np.array([-v[1], v[0]]) / max(np.hypot(*v), 1e-6) * 9
                            a1, a2 = (p + nrm).astype(int), (p - nrm).astype(int)
                            cv2.line(layer, tuple(a1), tuple(a2), col, 3, cv2.LINE_AA)
                    head = part[-1]
                    if frac < 1:
                        cv2.circle(layer, (int(head[0]), int(head[1])), w + 5, WHITE, -1, cv2.LINE_AA)
                    out = cv2.addWeighted(layer, fade, out, 1 - fade, 0)
            elif typ == "pin":
                x, y = scr(np.array([bm.px(*COORDS[L["at"]]) if isinstance(L["at"], str) else bm.px(*L["at"])]))[0]
                k = ease_out(prog(t, t0, 0.35))
                col = L.get("color", YELLOW)
                r = L.get("r", 11)
                if L.get("pulse", True):
                    ph = ((t - t0) * 1.2) % 1.0
                    rr = int(r + 40 * ph)
                    layer = out.copy()
                    cv2.circle(layer, (int(x), int(y)), rr, col, 3, cv2.LINE_AA)
                    out = cv2.addWeighted(layer, (1 - ph) * k * fade, out, 1 - (1 - ph) * k * fade, 0)
                cv2.circle(out, (int(x), int(y)), int(r * k) + 4, (0, 0, 0), -1, cv2.LINE_AA)
                cv2.circle(out, (int(x), int(y)), int(r * k), col, -1, cv2.LINE_AA)
                if L.get("label"):
                    self._label(out, L["label"], x, y, t, t0 + 0.15, L.get("side", "r"), fade, L.get("size", 40),
                                L.get("box", False))
            elif typ == "label":
                x, y = scr(np.array([bm.px(*COORDS[L["at"]]) if isinstance(L["at"], str) else bm.px(*L["at"])]))[0]
                self._label(out, L["text"], x + L.get("dx", 0), y + L.get("dy", 0), t, t0, L.get("side", "c"), fade,
                            L.get("size", 40), L.get("box", False), L.get("color", WHITE))
            elif typ in ("gate", "xmark"):
                x, y = scr(np.array([bm.px(*COORDS[L["at"]]) if isinstance(L["at"], str) else bm.px(*L["at"])]))[0]
                k = ease_back(prog(t, t0, 0.35)) * fade
                if k > 0:
                    s = L.get("size", 34) * k
                    if typ == "xmark":
                        for sg in (1, -1):
                            cv2.line(out, (int(x - s), int(y - s * sg)), (int(x + s), int(y + s * sg)), (0, 0, 0), 16, cv2.LINE_AA)
                            cv2.line(out, (int(x - s), int(y - s * sg)), (int(x + s), int(y + s * sg)), RED, 10, cv2.LINE_AA)
                    else:
                        cv2.rectangle(out, (int(x - s * 1.6), int(y - s * 0.35)), (int(x + s * 1.6), int(y + s * 0.35)), (0, 0, 0), -1)
                        for q in range(4):
                            xa = x - s * 1.5 + q * s * 0.75
                            cv2.rectangle(out, (int(xa), int(y - s * 0.25)), (int(xa + s * 0.75), int(y + s * 0.25)),
                                          RED if q % 2 == 0 else WHITE, -1)
                        cv2.line(out, (int(x - s * 1.6), int(y)), (int(x - s * 1.6), int(y + s * 1.2)), WHITE, 5, cv2.LINE_AA)
                    if L.get("label"):
                        self._label(out, L["label"], x, y + (s + 30 if L.get("side") == "b" else 0), t, t0 + 0.15,
                                    L.get("side", "r"), fade, L.get("size_txt", 40), L.get("box", False))
            elif typ == "marker":  # tunnel marker: small yellow rectangle arch
                x, y = scr(np.array([bm.px(*COORDS[L["at"]])]))[0]
                k = ease_out(prog(t, t0, 0.3))
                if k > 0:
                    s = 19 * k
                    col = L.get("color", YELLOW)
                    cv2.rectangle(out, (int(x - s), int(y - s)), (int(x + s), int(y + s)), (0, 0, 0), -1)
                    cv2.rectangle(out, (int(x - s + 3), int(y - s + 3)), (int(x + s - 3), int(y + s - 3)), col, -1)
                    if L.get("num"):
                        n = text_sprite(str(L["num"]), "bebas", 38, BLACK, False)
                        over(out, n, x - n.w / 2, y - n.h / 2 + 2, k)
        if self.title:
            a = 1 - prog(t, self.dur - 0.3, 0.3)
            tt = text_sprite(self.title, "bebas", 46, WHITE, True, tracking=3)
            over(out, tt, 70 - 24, H - 130, a * ease_out(prog(t, 0.2, 0.4)))
            cv2.rectangle(out, (70, H - 58), (70 + int((tt.w - 48) * ease_out(prog(t, 0.2, 0.6))), H - 52), YELLOW, -1)
        return out

    def _label(self, out, text, x, y, t, t0, side, fade, size=40, box=False, color=WHITE):
        k = ease_out(prog(t, t0, 0.35)) * fade
        if k <= 0:
            return
        if box:
            sp = text_sprite(text, "bebas", size, BLACK, False, tracking=1)
            bx = rounded_rect_sprite(sp.w - 30, sp.h - 40, YELLOW, 4, 255)
        else:
            sp = text_sprite(text, "bebas", size, color, True, tracking=1)
            bx = None
        if side == "r":
            px, py = x + 22, y - sp.h / 2
        elif side == "l":
            px, py = x - sp.w + 2, y - sp.h / 2
        elif side == "t":
            px, py = x - sp.w / 2, y - sp.h + 6
        elif side == "b":
            px, py = x - sp.w / 2, y - 4
        else:
            px, py = x - sp.w / 2, y - sp.h / 2
        if bx is not None:
            over(out, bx, px + 15, py + 20, k)
        over(out, sp, px, py, k)
