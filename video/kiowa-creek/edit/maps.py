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
    # Cumberland Gap
    "gap": (-83.6737, 36.6041), "middlesboro": (-83.7166, 36.6084), "cg_town": (-83.6655, 36.5948),
    "pinnacle": (-83.6609, 36.6082), "harrogate": (-83.6569, 36.5823), "gap_cave": (-83.6698, 36.6027),
    "pineville": (-83.6950, 36.7620), "flat_lick": (-83.7650, 36.8240), "hazel_patch": (-84.1240, 37.2050),
    "rockcastle": (-84.2000, 37.3700), "boonesborough": (-84.2650, 37.9010), "harrodsburg": (-84.8433, 37.7623),
    "lexington": (-84.5037, 38.0406), "knoxville": (-83.9207, 35.9606), "louisville": (-85.7585, 38.2527),
    "powell_valley": (-82.9400, 36.7100), "cincinnati": (-84.5120, 39.1031), "columbus": (-82.9988, 39.9612),
    "detroit": (-83.0458, 42.3314), "atlanta": (-84.3880, 33.7490), "daytona": (-81.0228, 29.2108),
    "miami": (-80.1918, 25.7617), "jacksonville": (-81.6557, 30.3322), "new_orleans": (-90.0715, 29.9511),
    "philadelphia": (-75.1652, 39.9526), "richmond": (-77.4360, 37.5407), "st_louis": (-90.1994, 38.6270),
    "pittsburgh": (-79.9959, 40.4406), "charleston": (-79.9311, 32.7765), "boston": (-71.0589, 42.3601),
    "chattanooga": (-85.3097, 35.0456), "ewing": (-83.4335, 36.6365),
    # Donner Pass
    "tunnel6": (-120.3196, 39.3166), "donner_lake": (-120.2668, 39.3236), "truckee": (-120.1833, 39.3280),
    "cisco": (-120.5450, 39.3080), "norden": (-120.3570, 39.3200), "yuba_gap": (-120.6160, 39.3220),
    "china_wall": (-120.3135, 39.3178), "summit_camp": (-120.3240, 39.3150), "sacramento": (-121.4944, 38.5816),
    "reno": (-119.8138, 39.5296), "promontory": (-112.5510, 41.6180), "ogden": (-111.9738, 41.2230),
    "winnemucca": (-117.7357, 40.9730), "elko": (-115.7631, 40.8324), "cheyenne": (-104.8202, 41.1400),
    "north_platte": (-100.7654, 41.1403), "council_bluffs": (-95.8608, 41.2619), "colfax": (-120.9530, 39.1007),
    "emigrant_gap": (-120.6688, 39.2963), "hongkong": (114.1694, 22.3193), "taishan": (112.7940, 22.2520),
    "dutch_flat": (-120.8380, 39.2060),
    # Atlantic Avenue (street points from NYC street centerlines)
    "furman": (-74.000192, 40.691905), "columbia": (-73.999514, 40.69166), "hicks": (-73.997771, 40.691203),
    "henry": (-73.996234, 40.690766), "clinton": (-73.994362, 40.690248), "court": (-73.992365, 40.689698),
    "boerum": (-73.990708, 40.689145), "smith": (-73.989169, 40.688624), "bond": (-73.984831, 40.686938),
    "flatbush": (-73.977459, 40.684061), "borough_hall": (-73.9899, 40.6928), "pier_bk": (-74.0012, 40.6922),
    "whitehall": (-74.0129, 40.7013), "brooklyn_ctr": (-73.985, 40.690), "hunters_point": (-73.9552, 40.7425),
    "red_hook": (-74.0090, 40.6760), "flatbush_home": (-73.9590, 40.6430), "pratt": (-73.9634, 40.6911),
    "east_ny": (-73.8960, 40.6780), "jamaica": (-73.8080, 40.7020), "hicksville": (-73.5251, 40.7684),
    "ronkonkoma": (-73.1123, 40.8087), "riverhead": (-72.6622, 40.9170), "greenport": (-72.3593, 41.1034),
    "stonington": (-71.9059, 41.3359), "providence": (-71.4128, 41.8240), "albany": (-73.7562, 42.6526),
    "new_haven": (-72.9279, 41.3083), "hartford": (-72.6851, 41.7637), "springfield": (-72.5898, 42.1015),
    "worcester": (-71.8023, 42.2626), "manhattan": (-73.9857, 40.7484), "bridgeport": (-73.1952, 41.1792),
    # Road to Nowhere (Swain County, NC)
    "bryson": (-83.4474, 35.4282), "fontana_dam": (-83.8048, 35.4517), "proctor": (-83.7170, 35.4670),
    "tunnel": (-83.5405, 35.4597), "noland": (-83.5265, 35.4572), "lv_start": (-83.4775, 35.4491),
    "lv_end": (-83.5379, 35.4589), "lv_west": (-83.8100, 35.4570), "alcoa": (-83.9740, 35.7890),
    "oak_ridge": (-84.2700, 36.0100), "asheville": (-82.5515, 35.5951), "raleigh": (-78.6382, 35.7796),
    "charlotte": (-80.8431, 35.2271), "nashville": (-86.7816, 36.1627), "maryville": (-83.9705, 35.7565),
    "cherokee": (-83.3149, 35.4743), "gatlinburg": (-83.5102, 35.7143), "hazel_mouth": (-83.7230, 35.4610),
    # Richmond, Church Hill (USGS street intersections)
    "rich": (-77.4360, 37.5407), "west_portal": (-77.42450, 37.53580), "east_portal": (-77.41430, 37.52750),
    "st_john": (-77.41925, 37.53175), "jefferson_park": (-77.42080, 37.53480), "libby_hill": (-77.41780, 37.52660),
    "grace_hosp": (-77.4440, 37.5455), "docks": (-77.4170, 37.5228), "collapse": (-77.42380, 37.53550),
    "cliftonforge": (-79.8270, 37.8162), "charleston_wv": (-81.6326, 38.3498), "newport_news": (-76.4730, 36.9790),
    "huntington": (-82.4452, 38.4192), "white_sulphur": (-80.2973, 37.7965),
    # Kiowa Creek (Bennett, Colorado) and the Kansas Pacific line
    "kc_cross": (-104.4084, 39.7525), "bennett": (-104.4277, 39.7589), "strasburg": (-104.3230, 39.7383),
    "comanche": (-104.3190, 39.7400), "kansas_city": (-94.5786, 39.0997), "lawrence": (-95.2353, 38.9717),
    "topeka": (-95.6890, 39.0558), "manhattan_ks": (-96.5717, 39.1836), "junction_city": (-96.8314, 39.0286),
    "abilene": (-97.2142, 38.9172), "salina": (-97.6114, 38.8403), "ellsworth": (-98.2281, 38.7306),
    "hays": (-99.3268, 38.8792), "ellis": (-99.5607, 38.9381), "wakeeney": (-99.8793, 39.0250),
    "oakley": (-100.8638, 39.1333), "sharon_springs": (-101.7516, 38.8978), "cheyenne_wells": (-102.3530, 38.8211),
    "kit_carson": (-102.7924, 38.7633), "hugo": (-103.4697, 39.1361), "limon": (-103.6922, 39.2639),
    "agate": (-103.9433, 39.4619), "deer_trail": (-104.0433, 39.6155), "byers": (-104.2280, 39.7114),
    "black_forest": (-104.7008, 39.0130), "kiowa_town": (-104.4644, 39.3472), "elizabeth": (-104.5967, 39.3600),
    "philadelphia_pa": (-75.1652, 39.9526), "brighton": (-104.8205, 39.9853), "fort_morgan": (-103.7999, 40.2503),
    "platte_mouth": (-104.1350, 40.2700), "colorado_springs": (-104.8214, 38.8339), "aurora": (-104.8319, 39.7294),
    "watkins": (-104.6033, 39.7522),
}


def deg2px(lon, lat, z):
    n = 256 * 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y


class BaseMap:
    def __init__(self, name, z, bbox, exaggerate=1.0, elo=0.0, ehi=900.0, lat_c=41.0, tz=None):
        self.name, self.z, self.tz = name, z, tz or z
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
        if self.name == "dp_pacific" and lon < 0:
            lon += 360.0
        x, y = deg2px(lon, lat, self.z)
        return x - self.ox, y - self.oy

    def build(self):
        nx, ny = self.tx1 - self.tx0 + 1, self.ty1 - self.ty0 + 1
        f = 2 ** (self.z - self.tz)  # terrain read at a coarser zoom and upsampled (flat cities)
        tx0, ty0 = self.tx0 // f, self.ty0 // f
        mx, my = self.tx1 // f - tx0 + 1, self.ty1 // f - ty0 + 1
        elev = np.zeros((my * 256, mx * 256), np.float32)
        for i in range(mx):
            for j in range(my):
                p = os.path.join(MAPDIR, "tiles", f"{self.tz}_{tx0 + i}_{ty0 + j}.png")
                if not os.path.exists(p):
                    continue
                a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
                elev[j * 256:(j + 1) * 256, i * 256:(i + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
        if f > 1:
            elev = cv2.resize(elev, (mx * 256 * f, my * 256 * f), interpolation=cv2.INTER_CUBIC)
            ox, oy = (self.tx0 - tx0 * f) * 256, (self.ty0 - ty0 * f) * 256
            elev = np.ascontiguousarray(elev[oy:oy + ny * 256, ox:ox + nx * 256])
        water = elev <= 0.5
        if self.name in ("aa_nyc", "aa_loc"):  # NYC shoreline from the city's borough polygons
            land = np.zeros(elev.shape, np.uint8)
            for pts in self._boroughs():
                cv2.fillPoly(land, [np.round(pts * 4).astype(np.int32)], 1, cv2.LINE_AA, shift=2)
            if self.name == "aa_nyc":  # inside the city limits (water included) the shoreline polygons decide
                city = np.zeros(elev.shape, np.uint8)
                for pts in self._boroughs("boroughs_water.geojson"):
                    cv2.fillPoly(city, [np.round(pts * 4).astype(np.int32)], 1, cv2.LINE_AA, shift=2)
                water = np.where(city > 0, land == 0, water)
            else:
                water = land == 0
            if self.name == "aa_loc":
                elev[:] = 12.0
        if self.name == "dp_loc":  # Donner Lake: flat water surface at ~1,806 m, flood-filled from its centre
            cx, cy = self.px(-120.2668, 39.3236)
            mask = np.zeros((elev.shape[0] + 2, elev.shape[1] + 2), np.uint8)
            e32 = cv2.GaussianBlur(elev, (0, 0), 0.6).astype(np.float32)
            cv2.floodFill(e32.copy(), mask, (int(cx), int(cy)), 0, 1.2, 1.2, cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | (255 << 8))
            water |= mask[1:-1, 1:-1] > 0
        if self.name == "rc_loc":
            riv = np.zeros(elev.shape, np.uint8)
            with open(os.path.join(MAPDIR, "rc", "river_9.geojson")) as f:
                fc = json.load(f)
            for ft in fc["features"]:
                g = ft["geometry"]
                for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
                    cv2.fillPoly(riv, [np.round(self._poly_px([q[:2] for q in p[0]]) * 4).astype(np.int32)], 1, cv2.LINE_AA, shift=2)
                    for hole in p[1:]:
                        cv2.fillPoly(riv, [np.round(self._poly_px([q[:2] for q in hole]) * 4).astype(np.int32)], 0, cv2.LINE_AA, shift=2)
            water = riv > 0
        if self.name.startswith("rn_") and self.name != "rn_valley":
            lakes = np.zeros(elev.shape, np.uint8)
            for pts in rn_lake_polys(self):
                cv2.fillPoly(lakes, [np.round(pts * 4).astype(np.int32)], 1, cv2.LINE_AA, shift=2)
            water |= lakes > 0
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
        if self.name == "aa_loc":
            col[:] = (30, 33, 36)
        col[water] = (14, 22, 32)
        col = np.clip(col, 0, 255).astype(np.uint8)
        self._draw_vectors(col)
        return col

    def _poly_px(self, coords):
        return np.array([self.px(lon, lat) for lon, lat in coords], np.float32)

    def _boroughs(self, src="boroughs.geojson"):
        with open(os.path.join(MAPDIR, "nyc", src)) as f:
            fc = json.load(f)
        out = []
        for ft in fc["features"]:
            for poly in ft["geometry"]["coordinates"]:
                out.append(self._poly_px(poly[0]))
        return out

    def _draw_streets(self, img):
        src = "streets.geojson" if self.name == "aa_loc" else "streets_big.geojson"
        with open(os.path.join(MAPDIR, "nyc", src)) as f:
            fc = json.load(f)
        res = 156543.03 * math.cos(math.radians(self.lat_c)) / 2 ** self.z
        layer = img.copy()
        for ft in fc["features"]:
            g, pr = ft["geometry"], ft["properties"]
            if not g or pr.get("rw_type") not in ("1", "2", "3", "4", "9", "10", "13"):
                continue
            if self.name == "aa_loc":
                w = max(2, int(float(pr.get("streetwidth") or 30) * 0.3048 / res))
                col = (74, 75, 76)
            else:
                w = 2 if pr.get("rw_type") in ("2", "3", "4") else 1
                col = (66, 68, 68) if w == 2 else (54, 57, 58)
            for ln in g["coordinates"]:
                pts = self._poly_px(ln)
                cv2.polylines(layer, [np.round(pts * 4).astype(np.int32)], False, col, w, cv2.LINE_AA, shift=2)
        img[:] = layer

    def _draw_rn_local(self, img):
        """Swain County detail: NHD rivers and creeks, USGS roads (all public domain)."""
        rd = os.path.join(MAPDIR, "rn")
        with open(os.path.join(rd, "rivers.geojson")) as f:
            rivers = json.load(f)
        for ft in rivers["features"]:
            g = ft["geometry"]
            big = ft["properties"]["GNIS_NAME"] in ("Little Tennessee River", "Tuckasegee River")
            if self.name != "rn_valley" and big:
                pass
            for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                pts = self._poly_px(ln)
                cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, (52, 84, 112),
                              (5 if big else 2) if self.name == "rn_valley" else 2, cv2.LINE_AA, shift=2)
        if self.name != "rn_valley":
            for pts in rn_lake_polys(self):
                cv2.fillPoly(img, [np.round(pts * 4).astype(np.int32)], (14, 22, 32), cv2.LINE_AA, shift=2)
                cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], True, (40, 62, 82), 2, cv2.LINE_AA, shift=2)
        for L, col, w in ((31, (92, 92, 88), 2), (30, (104, 100, 92), 3), (29, (104, 100, 92), 3)):
            with open(os.path.join(rd, f"r_{L}.geojson")) as f:
                fc = json.load(f)
            for ft in fc["features"]:
                g = ft["geometry"]
                for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                    pts = self._poly_px(ln)
                    cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, col, w, cv2.LINE_AA, shift=2)

    def _draw_rc_local(self, img):
        """Church Hill streets (USGS The National Map, public domain) and the James River."""
        rd = os.path.join(MAPDIR, "rc")
        for L, col, w in ((32, (64, 66, 68), 2), (31, (84, 84, 82), 3), (30, (96, 94, 88), 4), (29, (104, 100, 92), 5)):
            with open(os.path.join(rd, f"r_{L}.geojson")) as f:
                fc = json.load(f)
            for ft in fc["features"]:
                g = ft["geometry"]
                if not g:
                    continue
                for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                    pts = self._poly_px([p[:2] for p in ln])
                    cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, col, w, cv2.LINE_AA, shift=2)
        with open(os.path.join(rd, "r_38.geojson")) as f:
            fc = json.load(f)
        for ft in fc["features"]:
            g = ft["geometry"]
            if not g:
                continue
            for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                pts = self._poly_px([p[:2] for p in ln])
                cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, (70, 70, 84), 2, cv2.LINE_AA, shift=2)

    def _draw_kc_local(self, img):
        """Kiowa Creek at Bennett: NHD creeks, USGS roads and railroad (public domain)."""
        rd = os.path.join(MAPDIR, "kc")
        res = 156543.03 * math.cos(math.radians(self.lat_c)) / 2 ** self.z
        self._kc_creeks(img, 3, 7)
        for L, col, w in ((32, (60, 62, 62), 2), (31, (82, 82, 80), 3), (30, (92, 90, 86), 4), (29, (104, 100, 92), 6)):
            fp = os.path.join(rd, f"r_{L}.geojson")
            if not os.path.exists(fp):
                continue
            with open(fp) as f:
                fc = json.load(f)
            for ft in fc["features"]:
                g = ft["geometry"]
                if not g:
                    continue
                for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                    pts = self._poly_px([p[:2] for p in ln])
                    cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, col, w, cv2.LINE_AA, shift=2)
        self._kc_rail(img, "r_38.geojson", (104, 100, 128), 4)

    def _kc_creeks(self, img, w_small, w_kiowa):
        with open(os.path.join(MAPDIR, "kc", "creeks.geojson")) as f:
            fc = json.load(f)
        for ft in sorted(fc["features"], key=lambda ft: ft["properties"].get("GNIS_NAME") == "Kiowa Creek"):
            g = ft["geometry"]
            if not g:
                continue
            nm = ft["properties"].get("GNIS_NAME")
            w = w_kiowa if nm == "Kiowa Creek" else (w_small + 1 if nm == "South Platte River" else w_small)
            col = (66, 104, 136) if nm == "Kiowa Creek" else (52, 84, 112)
            for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                pts = self._poly_px([p[:2] for p in ln])
                cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, col, w, cv2.LINE_AA, shift=2)

    def _kc_rail(self, img, src, col, w):
        with open(os.path.join(MAPDIR, "kc", src)) as f:
            fc = json.load(f)
        for ft in fc["features"]:
            g = ft["geometry"]
            if not g:
                continue
            for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                pts = self._poly_px([p[:2] for p in ln])
                cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, col, w, cv2.LINE_AA, shift=2)

    def _draw_vectors(self, img):
        if self.name in ("aa_nyc", "aa_loc"):
            self._draw_streets(img)
            for pts in self._boroughs():
                cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], True, (70, 84, 96), 2, cv2.LINE_AA, shift=2)
            self.states = {}
            return
        if self.name == "dp_pacific":
            self.states = {}
            return
        if self.name in ("rn_lake", "rn_valley", "rn_loc"):
            self._draw_rn_local(img)
            self.states = {}
            return
        if self.name == "rc_loc":
            self._draw_rc_local(img)
            self.states = {}
            return
        if self.name == "kc_loc":
            self._draw_kc_local(img)
            self.states = {}
            return
        if self.z >= 13:
            self.states = {}
            return
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
        if self.name.startswith("aa_"):
            roads_file = None
        else:
            roads_file = ("roads_cg.geojson" if self.name.startswith("cg_") else
                          "roads_dp.geojson" if self.name.startswith("dp_") else
                          "roads_rn.geojson" if self.name.startswith("rn_") else "roads_rc.geojson" if self.name.startswith("rc_") else
                          "roads_kc.geojson" if self.name.startswith("kc_") else "roads_i80.geojson")
        roads = {"features": []}
        if roads_file:
            with open(os.path.join(MAPDIR, roads_file)) as f:
                roads = json.load(f)
        for ft in roads["features"]:
            g = ft["geometry"]
            if self.name == "dp_pacific":
                continue
            if self.name[:3] in ("cg_", "dp_", "rn_", "rc_", "kc_"):
                if (self.z <= 6 or (self.z <= 7 and self.name.startswith("rn_")) or (self.z <= 8 and self.name.startswith("kc_"))) and ft["properties"]["level"] != "Interstate":
                    continue
                col, w = ((86, 86, 82), 2) if ft["properties"]["level"] == "Interstate" else ((96, 92, 84), 2)
            else:
                col, w = ((120, 116, 104), 3) if ft["properties"]["name"] == "80" else ((92, 92, 88), 2)
            for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
                pts = self._poly_px(ln)
                cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, col, w, cv2.LINE_AA, shift=2)
        if self.name == "kc_mid":
            self._kc_creeks(img, 2, 4)
            self._kc_rail(img, "mid_38.geojson", (74, 74, 90), 2)
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


@functools.lru_cache(maxsize=8)
def basemap(name):
    if name == "aa_ne":
        return BaseMap("aa_ne", 10, (-74.9, 40.3, -70.5, 42.85), 2.2, 0.0, 900.0, 41.5)
    if name == "aa_nyc":
        return BaseMap("aa_nyc", 14, (-74.06, 40.62, -73.86, 40.78), 2.0, 0.0, 70.0, 40.7, tz=12)
    if name == "aa_loc":
        return BaseMap("aa_loc", 17, (-74.007, 40.677, -73.971, 40.699), 1.0, 0.0, 60.0, 40.69, tz=15)
    if name == "rc_reg":
        return BaseMap("rc_reg", 9, (-82.8, 36.5, -75.8, 39.2), 2.2, 0.0, 1400.0, 37.8)
    if name == "rc_loc":
        return BaseMap("rc_loc", 16, (-77.4400, 37.5180, -77.4000, 37.5440), 2.5, 0.0, 70.0, 37.53, tz=14)
    if name == "kc_us":
        return BaseMap("kc_us", 6, (-126.0, 24.0, -66.0, 50.0), 2.2, 0.0, 3200.0, 38.0)
    if name == "kc_reg":
        return BaseMap("kc_reg", 8, (-105.6, 36.6, -93.9, 41.4), 1.6, 200.0, 3800.0, 39.0)
    if name == "kc_mid":
        return BaseMap("kc_mid", 11, (-105.3, 38.8, -103.9, 40.4), 2.2, 1450.0, 2700.0, 39.6)
    if name == "kc_loc":
        return BaseMap("kc_loc", 14, (-104.62, 39.68, -104.28, 39.84), 3.5, 1570.0, 1780.0, 39.76)
    if name == "rn_us":
        return BaseMap("rn_us", 7, (-96.0, 27.0, -70.0, 43.0), 3.0, 0.0, 2000.0, 35.0)
    if name == "rn_reg":
        return BaseMap("rn_reg", 10, (-85.6, 34.9, -82.2, 36.4), 1.6, 150.0, 1800.0, 35.6)
    if name in ("rn_lake", "rn_valley"):
        return BaseMap(name, 13, (-83.92, 35.37, -83.38, 35.59), 1.2, 480.0, 1700.0, 35.48)
    if name == "rn_loc":
        return BaseMap("rn_loc", 14, (-83.62, 35.40, -83.42, 35.50), 1.1, 480.0, 1500.0, 35.45)
    if name == "dp_us":
        return BaseMap("dp_us", 6, (-126.0, 31.0, -88.0, 47.0), 3.0, 0.0, 3200.0, 40.0)
    if name == "dp_sierra":
        return BaseMap("dp_sierra", 10, (-121.7, 38.45, -119.6, 39.75), 1.3, 0.0, 3000.0, 39.0)
    if name == "dp_loc":
        return BaseMap("dp_loc", 13, (-120.45, 39.26, -120.15, 39.37), 1.0, 1700.0, 2700.0, 39.3)
    if name == "dp_pacific":
        return BaseMap("dp_pacific", 4, (95.0, 5.0, 255.0, 58.0), 8.0, 0.0, 3000.0, 30.0)
    if name == "cg_east":
        return BaseMap("cg_east", 6, (-106.0, 18.0, -54.0, 50.0), 6.0, 0.0, 1100.0, 36.0)
    if name == "cg_reg":
        return BaseMap("cg_reg", 9, (-87.0, 35.0, -81.0, 39.0), 1.8, 150.0, 1300.0, 37.0)
    if name == "cg_mid":
        return BaseMap("cg_mid", 11, (-84.4, 36.25, -82.9, 37.05), 1.4, 250.0, 1200.0, 36.6)
    if name == "cg_loc":
        return BaseMap("cg_loc", 14, (-83.77, 36.555, -83.59, 36.655), 1.0, 320.0, 900.0, 36.6)
    if name == "us":
        return BaseMap("us", 6, (-126.0, 23.0, -65.0, 51.0), 2.2, 0.0, 3200.0, 38.0)
    if name == "wy":
        return BaseMap("wy", 9, (-111.6, 40.4, -103.6, 45.3), 1.2, 1100.0, 3800.0, 42.8)
    if name == "loc":
        return BaseMap("loc", 11, (-107.7, 40.95, -105.1, 42.25), 1.0, 1850.0, 3400.0, 41.6)
    raise KeyError(name)


def rn_lake_polys(bm):
    """Fontana Lake (and the other TVA lakes in view) from the USGS National Hydrography Dataset, in basemap px."""
    out = []
    with open(os.path.join(MAPDIR, "rn", "wb_all.geojson")) as f:
        fc = json.load(f)
    for ft in fc["features"]:
        g = ft["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for p in polys:
            out.append(bm._poly_px(p[0]))
    return out


@functools.lru_cache(maxsize=2)
def rn_lake_lonlat():
    with open(os.path.join(MAPDIR, "rn", "wb_all.geojson")) as f:
        fc = json.load(f)
    out = []
    for ft in fc["features"]:
        if ft["properties"].get("GNIS_NAME") != "Fontana Lake":
            continue
        g = ft["geometry"]
        for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            out.append(np.array(p[0], np.float64))
    return out


@functools.lru_cache(maxsize=2)
def rn_park_lonlat():
    with open(os.path.join(MAPDIR, "rn", "grsm.geojson")) as f:
        fc = json.load(f)
    out = []
    for ft in fc["features"]:
        g = ft["geometry"]
        for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            if len(p[0]) > 50:
                out.append(np.array(p[0], np.float64))
    return out


@functools.lru_cache(maxsize=2)
def rn_lakeview():
    """Lakeview Drive East, Bryson City -> tunnel, stitched from the USGS road pieces (west of -83.477)."""
    with open(os.path.join(MAPDIR, "rn", "lakeview.geojson")) as f:
        fc = json.load(f)
    segs = []
    for ft in fc["features"]:
        if ft["properties"]["name"] != "Lakeview Drive East":
            continue
        segs.append(np.array(ft["geometry"]["coordinates"], np.float64))
    start = np.array(COORDS["lv_start"])
    k = min(range(len(segs)), key=lambda i: min(np.hypot(*(segs[i][0] - start)), np.hypot(*(segs[i][-1] - start))))
    cur = segs.pop(k)
    if np.hypot(*(cur[-1] - start)) < np.hypot(*(cur[0] - start)):
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
        if best > 0.002:
            break
        sg = segs.pop(bi)
        out.append(sg[::-1] if rev else sg)
    pts = np.vstack(out)
    return np.vstack([pts, np.array([COORDS["tunnel"]])])


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
def road_chain(name, bbox=(-180, -90, 180, 90), level=None, src="roads_i80.geojson"):
    """Stitch the Natural Earth pieces of one highway into a single west-to-east lon/lat polyline inside bbox."""
    lon0, lat0, lon1, lat1 = bbox
    with open(os.path.join(MAPDIR, src)) as f:
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


@functools.lru_cache(maxsize=4)
def kc_creek_ll(name="Kiowa Creek"):
    """Stitch the NHD pieces of one creek into a single south-to-north lon/lat polyline."""
    with open(os.path.join(MAPDIR, "kc", "creeks.geojson")) as f:
        fc = json.load(f)
    segs = []
    for ft in fc["features"]:
        if ft["properties"].get("GNIS_NAME") != name or not ft["geometry"]:
            continue
        g = ft["geometry"]
        for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            segs.append(np.array([p[:2] for p in ln], np.float64))
    k = min(range(len(segs)), key=lambda i: min(segs[i][0, 1], segs[i][-1, 1]))
    cur = segs.pop(k)
    if cur[-1, 1] < cur[0, 1]:
        cur = cur[::-1]
    out = [cur]
    while segs:
        end = out[-1][-1]
        best, bi, rev = 1e9, -1, False
        for i, sg in enumerate(segs):
            for r, q in ((False, sg[0]), (True, sg[-1])):
                d = math.hypot(*(q - end))
                if d < best:
                    best, bi, rev = d, i, r
        if best > 0.05:
            break
        sg = segs.pop(bi)
        out.append(sg[::-1] if rev else sg)
    pts = np.vstack(out)
    return tuple(map(tuple, pts[::2]))


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
        if self.mapname[:3] in ("aa_", "rn_", "rc_", "kc_"):  # keep the view inside the basemap
            bh, bw = bm.img.shape[:2]
            z = max(z, W / bw, H / bh)
            cx = min(max(cx, W / (2 * z)), bw - W / (2 * z))
            cy = min(max(cy, H / (2 * z)), bh - H / (2 * z))
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
                    ll = road_chain(L["name"], tuple(L.get("bbox", (-180, -90, 180, 90))), L.get("level"),
                                    L.get("src", "roads_cg.geojson" if self.mapname.startswith("cg_") else "roads_dp.geojson" if self.mapname.startswith("dp_") else "roads_rn.geojson" if self.mapname.startswith("rn_") else "roads_rc.geojson" if self.mapname.startswith("rc_") else "roads_kc.geojson" if self.mapname.startswith("kc_") else "roads_i80.geojson"))
                    if L.get("reverse"):
                        ll = ll[::-1]
                    path = np.array([bm.px(lon, lat) for lon, lat in ll])
                elif "ll" in L:
                    path = np.array([bm.px(lon, lat) for lon, lat in L["ll"]])
                else:
                    pts = np.array([bm.px(*COORDS[n]) if isinstance(n, str) else bm.px(*n) for n in L["path"]])
                    path = catmull(pts, 20) if L.get("smooth", True) else pts
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
            elif typ == "band":  # wide translucent stroke, e.g. a mountain chain
                pts = np.array([bm.px(*COORDS[n]) if isinstance(n, str) else bm.px(*n) for n in L["path"]])
                path = catmull(pts, 20)
                frac = ease_io(prog(t, t0, L.get("draw", 1.5)))
                part = scr(partial(path, frac))
                if len(part) >= 2:
                    layer = out.copy()
                    cv2.polylines(layer, [np.round(part * 4).astype(np.int32)], False, L.get("color", YELLOW),
                                  int(L.get("width", 40) * z), cv2.LINE_AA, shift=2)
                    a = L.get("alpha", 0.35) * fade
                    out = cv2.addWeighted(layer, a, out, 1 - a, 0)
            elif typ == "poly":  # translucent filled area (e.g. a park)
                pts = scr(np.array([bm.px(*p) for p in L["pts"]]))
                a = ease_io(prog(t, t0, 0.6)) * fade
                layer = out.copy()
                ip = np.round(pts * 4).astype(np.int32)
                cv2.fillPoly(layer, [ip], L.get("fill", (70, 140, 80)), cv2.LINE_AA, shift=2)
                cv2.polylines(layer, [ip], True, L.get("color", (120, 200, 120)), L.get("width", 3), cv2.LINE_AA, shift=2)
                out = cv2.addWeighted(layer, a * L.get("alpha", 0.45), out, 1 - a * L.get("alpha", 0.45), 0)
            elif typ == "polys":  # several lon/lat polygons (lake flooding in, park area)
                a = ease_io(prog(t, t0, L.get("fadein", 0.6))) * fade * L.get("alpha", 0.45)
                if a > 0:
                    layer = out.copy()
                    for ll in L["polys"]:
                        ip = np.round(scr(np.array([bm.px(lon, lat) for lon, lat in ll])) * 4).astype(np.int32)
                        cv2.fillPoly(layer, [ip], L.get("fill", (70, 140, 80)), cv2.LINE_AA, shift=2)
                        if L.get("width", 3):
                            cv2.polylines(layer, [ip], True, L.get("color", (120, 200, 120)), L.get("width", 3), cv2.LINE_AA, shift=2)
                    out = cv2.addWeighted(layer, a, out, 1 - a, 0)
            elif typ == "cloud":  # storm cloud with rain streaks over a lon/lat point
                x, y = scr(np.array([bm.px(*COORDS[L["at"]]) if isinstance(L["at"], str) else bm.px(*L["at"])]))[0]
                a = ease_out(prog(t, t0, 0.5)) * fade
                sc = L.get("scale", 1.0)
                layer = out.copy()
                rng = np.random.default_rng(int(t * 24))
                for _ in range(70):
                    rx = x + rng.uniform(-150, 150) * sc
                    ry = y + rng.uniform(10, 190) * sc
                    cv2.line(layer, (int(rx), int(ry)), (int(rx - 10 * sc), int(ry + 34 * sc)), (150, 190, 230), 2, cv2.LINE_AA)
                for dx, dy, r in ((-90, 0, 70), (-20, -30, 90), (70, -10, 80), (130, 15, 55), (-150, 20, 50)):
                    cv2.circle(layer, (int(x + dx * sc), int(y + dy * sc)), int(r * sc), (70, 74, 84), -1, cv2.LINE_AA)
                for dx, dy, r in ((-80, -10, 60), (-15, -40, 78), (65, -20, 68)):
                    cv2.circle(layer, (int(x + dx * sc), int(y + dy * sc)), int(r * sc), (104, 108, 118), -1, cv2.LINE_AA)
                if L.get("bolt") and ((t - t0) * 1.3) % 1.0 < 0.08:
                    pts = np.array([[x, y + 30 * sc], [x - 20 * sc, y + 90 * sc], [x + 10 * sc, y + 100 * sc], [x - 15 * sc, y + 170 * sc]])
                    cv2.polylines(layer, [pts.astype(np.int32)], False, (255, 250, 210), 5, cv2.LINE_AA)
                out = cv2.addWeighted(layer, a, out, 1 - a, 0)
                if L.get("label"):
                    self._label(out, L["label"], x, y - 150 * sc, t, t0 + 0.2, "c", fade, L.get("size", 40), True)
            elif typ == "sun":
                x, y = scr(np.array([bm.px(*COORDS[L["at"]]) if isinstance(L["at"], str) else bm.px(*L["at"])]))[0]
                a = ease_out(prog(t, t0, 0.5)) * fade
                layer = out.copy()
                r = L.get("r", 46)
                cv2.circle(layer, (int(x), int(y)), r, (250, 214, 90), -1, cv2.LINE_AA)
                for k in range(10):
                    ang = k * math.pi / 5 + t * 0.4
                    p0 = (int(x + math.cos(ang) * r * 1.35), int(y + math.sin(ang) * r * 1.35))
                    p1 = (int(x + math.cos(ang) * r * 1.85), int(y + math.sin(ang) * r * 1.85))
                    cv2.line(layer, p0, p1, (250, 214, 90), 5, cv2.LINE_AA)
                out = cv2.addWeighted(layer, a, out, 1 - a, 0)
                if L.get("label"):
                    self._label(out, L["label"], x, y + r * 2.6, t, t0 + 0.2, "c", fade, L.get("size", 40), True)
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


@functools.lru_cache(maxsize=8)
def rn_flow(names, start, stop_lon=None, tol=0.004, offset_lat=0.0):
    """Stitch NHD flowline pieces (any of `names`) into one lon/lat path starting nearest `start`, optionally stopping
    once the path goes west of stop_lon. Used for the old river bed under Fontana Lake and for Hazel Creek."""
    with open(os.path.join(MAPDIR, "rn", "rivers.geojson")) as f:
        fc = json.load(f)
    segs = []
    for ft in fc["features"]:
        if ft["properties"]["GNIS_NAME"] not in names:
            continue
        g = ft["geometry"]
        for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            segs.append(np.array(ln, np.float64)[:, :2])
    st = np.array(start, np.float64)
    k = min(range(len(segs)), key=lambda i: min(np.hypot(*(segs[i][0] - st)), np.hypot(*(segs[i][-1] - st))))
    cur = segs.pop(k)
    if np.hypot(*(cur[-1] - st)) < np.hypot(*(cur[0] - st)):
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
        if best > tol:
            break
        sg = segs.pop(bi)
        out.append(sg[::-1] if rev else sg)
    pts = np.vstack(out)
    if stop_lon is not None:
        idx = np.where(pts[:, 0] < stop_lon)[0]
        if len(idx):
            pts = pts[:idx[0] + 1]
    pts = pts.copy()
    pts[:, 1] += offset_lat
    return pts


@functools.lru_cache(maxsize=2)
def rn_old_road():
    """Approximate line of the old NC 288: the Tuckasegee from Bryson City (NHD), then the centre line of the flooded
    Little Tennessee channel (from the NHD lake polygon) west to the mouth of Hazel Creek, nudged to the north bank."""
    east = rn_flow(("Tuckasegee River",), COORDS["bryson"], None, 0.01)
    bm = basemap("rn_lake")
    mask = np.zeros(bm.img.shape[:2], np.uint8)
    for ll in rn_lake_lonlat():
        cv2.fillPoly(mask, [np.round(np.array([bm.px(*p) for p in ll]) * 4).astype(np.int32)], 1, cv2.LINE_8, shift=2)
    pts = []
    lat_prev = float(east[-1][1])
    lon0 = float(east[-1][0])
    for lon in np.arange(lon0 - 0.004, -83.722, -0.004):
        x, _ = bm.px(lon, 35.45)
        col = mask[:, int(x)]
        ys = np.where(col > 0)[0]
        if not len(ys):
            continue
        runs = np.split(ys, np.where(np.diff(ys) > 1)[0] + 1)
        cands = []
        for rr in runs:
            yc = rr.mean()
            # invert px -> lat on the Mercator basemap
            n = 256 * 2 ** bm.z
            yy = (yc + bm.oy) / n
            lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * yy))))
            cands.append((abs(lat - lat_prev) - 0.0005 * len(rr), lat))
        lat = min(cands)[1]
        if abs(lat - lat_prev) > 0.012:
            lat = lat_prev
        pts.append((lon, lat))
        lat_prev = lat
    west = np.array(pts)
    k = np.ones(5) / 5
    west[:, 1] = np.convolve(np.pad(west[:, 1], 2, mode="edge"), k, mode="valid")
    path = np.vstack([east, west, [COORDS["hazel_mouth"]]])
    path[:, 1] += 0.0015
    return path


@functools.lru_cache(maxsize=2)
def rc_viaduct():
    """The C&O riverfront line along the James at the foot of Church Hill (USGS railroads), west to east."""
    with open(os.path.join(MAPDIR, "rc", "r_38.geojson")) as f:
        fc = json.load(f)
    segs = []
    for i in (17, 57, 87, 0, 99, 66, 125):
        g = fc["features"][i]["geometry"]
        a = np.array(g["coordinates"] if g["type"] == "LineString" else g["coordinates"][0], np.float64)[:, :2]
        if segs and np.hypot(*(a[-1] - segs[-1][-1])) < np.hypot(*(a[0] - segs[-1][-1])):
            a = a[::-1]
        elif not segs and a[0, 0] > a[-1, 0]:
            a = a[::-1]
        segs.append(a)
    pts = np.vstack(segs)
    return pts[pts[:, 0] < -77.402]
