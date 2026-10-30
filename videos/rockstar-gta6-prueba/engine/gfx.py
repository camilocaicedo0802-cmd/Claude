"""Procedural full-frame graphics. Each class: __init__(dur, **kw); frame(tl) -> float32 BGR (H,W,3)."""
import math, json, random
import numpy as np, cv2
from PIL import Image, ImageDraw
from core import (W, H, A, render_word, blit, ease_out, ease_io, clamp01, font, glitch, load_image, resolve,
                  view_warp, rgba_from_bgra_u8, add_glow)

_cache = {}


def dark_grid(color=(0.09, 0.09, 0.11), line=0.05, step=80, persp=True):
    key = ("grid", color, line, step, persp)
    if key in _cache:
        return _cache[key]
    img = np.zeros((H, W, 3), np.float32) + np.array(color, np.float32) * 0.35
    for x in range(0, W, step):
        cv2.line(img, (x, 0), (x, H), (line, line, line + 0.01), 1, cv2.LINE_AA)
    for y in range(0, H, step):
        cv2.line(img, (0, y), (W, y), (line, line, line + 0.01), 1, cv2.LINE_AA)
    if persp:  # barrel distortion like the reference's curved grids
        img = barrel(img, 0.18)
    _cache[key] = img
    return img


_maps = {}


def barrel(img, k):
    key = (k, img.shape)
    if key not in _maps:
        h, w = img.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        nx, ny = (xx - w / 2) / (w / 2), (yy - h / 2) / (w / 2)
        r2 = nx * nx + ny * ny
        f = 1 - k * r2 * 0.5
        _maps[key] = ((nx * f) * (w / 2) + w / 2, (ny * f) * (w / 2) + h / 2)
    mx, my = _maps[key]
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def code_texture(width, height, color=(200, 40, 40), dim=(90, 20, 20), seed=1, size=22):
    key = ("code", width, height, color, seed, size)
    if key in _cache:
        return _cache[key]
    rng = random.Random(seed)
    im = Image.new("RGB", (width, height), (0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font("mono", size)
    words = ["ssh", "root@10.0.4.12", "decrypt", "--force", "0x7FFA", "ACCESS_DENIED", "auth.token", "sudo",
             "fetch", "build_srv", "dump", "/var/assets/", "git clone", "chmod 777", "PORT 443", "TLS", "AES-256",
             "payload", "exfil", "OK", "FAIL", "retry", "session_id", "sha256", "admin", "bypass", "2FA", "push"]
    y = 0
    while y < height:
        x = rng.randint(0, 40)
        line = []
        for _ in range(rng.randint(3, 12)):
            r = rng.random()
            if r < 0.45:
                line.append(" ".join("%02X" % rng.randint(0, 255) for _ in range(rng.randint(2, 6))))
            else:
                line.append(rng.choice(words))
        c = color if rng.random() < 0.18 else dim
        d.text((x, y), "  ".join(line), font=f, fill=c)
        y += int(size * 1.35)
    arr = np.asarray(im, np.float32)[:, :, ::-1] / 255
    _cache[key] = arr
    return arr


class Breach:
    """Red security-alert UI over scrolling code."""

    def __init__(self, dur, title="ALERTA DE SEGURIDAD", sub="ACCESO NO AUTORIZADO DETECTADO", bar="EXTRAYENDO ARCHIVOS"):
        self.dur = dur
        self.tex = code_texture(W, 4000, seed=3)
        self.t1 = render_word(title, "rb", 92)
        self.t2 = render_word(sub, "mono", 40)
        self.bar = bar

    def frame(self, tl):
        off = int((tl * 420) % (4000 - H))
        f = self.tex[off:off + H].copy() * 0.55
        f = f + dark_grid((0.2, 0.02, 0.02), 0.06) * 0.6
        blink = 0.75 + 0.25 * (math.sin(tl * 14) > 0)
        bx0, by0, bx1, by1 = 360, 330, 1560, 760
        f[by0:by1, bx0:bx1] = f[by0:by1, bx0:bx1] * 0.25 + np.array([0.02, 0.02, 0.16], np.float32)
        cv2.rectangle(f, (bx0, by0), (bx1, by1), (0.1, 0.1, 0.95 * blink), 4, cv2.LINE_AA)
        img, adv, pad = self.t1
        blit(f, img, 0, 0, opacity=blink, cx=W / 2, cy=440)
        img, adv, pad = self.t2
        blit(f, img, 0, 0, cx=W / 2, cy=540)
        p = clamp01(tl / (self.dur * 0.9))
        cv2.rectangle(f, (460, 610), (1460, 650), (0.25, 0.25, 0.3), 2)
        cv2.rectangle(f, (464, 614), (464 + int(992 * p), 646), (0.1, 0.1, 0.9), -1)
        img, adv, pad = render_word(f"{self.bar}... {int(p * 100)}%", "monor", 34)
        blit(f, img, 0, 0, cx=W / 2, cy=700)
        return np.clip(f, 0, 1)


class LogoGlitch:
    def __init__(self, dur, path=None, h=560, red=True, base_int=0.15):
        self.dur, self.red, self.base = dur, red, base_int
        path = path or (A + "/img/rockstar_logo.png")
        im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        s = h / im.shape[0]
        im = cv2.resize(im, (int(im.shape[1] * s), h), interpolation=cv2.INTER_AREA)
        self.logo = rgba_from_bgra_u8(im)
        self.rng = np.random.default_rng(5)

    def frame(self, tl):
        f = dark_grid((0.15, 0.02, 0.02), 0.045) * 0.8
        sc = 1.0 + 0.08 * tl / self.dur
        blit(f, self.logo, 0, 0, scale=sc, cx=W / 2, cy=H / 2)
        fi = int(tl * 30)
        spike = 1.0 if (fi % 11 in (0, 1) or fi % 17 == 3) else 0.0
        inten = self.base + 0.25 * tl / self.dur + 0.6 * spike
        f = glitch(f, min(1.0, inten), fi, seed=11)
        if self.red and (fi % 9 in (0, 4)):
            gray = f.mean(-1, keepdims=True)
            f = gray * np.array([0.25, 0.25, 1.3], np.float32)
        return np.clip(f, 0, 1)


class BigGlitchText:
    def __init__(self, dur, text="LAPSUS$", style="anton", size=300, sub=None, bg_seed=8):
        self.dur = dur
        self.img = render_word(text, style, size)
        self.sub = render_word(sub, "label", 40, tracking=0.25) if sub else None
        self.tex = code_texture(W, 3000, color=(200, 200, 200), dim=(60, 60, 60), seed=bg_seed)

    def frame(self, tl):
        off = int((tl * 260) % (3000 - H))
        f = self.tex[off:off + H].copy() * 0.28
        img, adv, pad = self.img
        sc = 1.04 - 0.04 * ease_out(tl / 0.6)
        blit(f, img, 0, 0, scale=sc, cx=W / 2, cy=H / 2 + 20)
        if self.sub:
            blit(f, self.sub[0], 0, 0, opacity=ease_out((tl - 0.2) / 0.4), cx=W / 2, cy=H / 2 - 210)
        fi = int(tl * 30)
        spike = 0.55 if fi % 10 == 0 else 0.08
        return glitch(f, spike, fi, seed=3)


class Chat:
    """Generic dark team-chat UI (no real branding) with fisheye, messages appearing."""

    MSGS = [
        ("Soporte TI", (90, 160, 255), "Recordatorio: no compartan credenciales por chat."),
        ("dev_ana", (120, 220, 140), "¿Alguien tiene acceso al servidor de builds?"),
        ("empleado_ti", (255, 170, 60), "Hola, soy de TI. Necesito validar tu cuenta."),
        ("empleado_ti", (255, 170, 60), "Envíame el código de verificación, es urgente."),
        ("dev_ana", (120, 220, 140), "Ok, te lo paso por privado."),
    ]

    def __init__(self, dur):
        self.dur = dur
        base = np.zeros((H, W, 3), np.float32) + np.array([0.13, 0.11, 0.1], np.float32)
        base[:, :360] = np.array([0.16, 0.08, 0.12], np.float32)
        base[:90, 360:] = np.array([0.15, 0.13, 0.12], np.float32)
        cv2.line(base, (360, 90), (W, 90), (0.25, 0.25, 0.25), 1)
        self.base = base
        self.side = [render_word(s, "label", 30) for s in ["CANALES", "# general", "# desarrollo", "# soporte-ti", "# builds"]]
        self.head = render_word("# soporte-ti", "label", 40)
        self.names = {}
        self.lines = []
        for n, c, txt in self.MSGS:
            self.lines.append((render_word(n, "label", 30), c, render_word(txt, "mono", 34)))

    def frame(self, tl):
        f = self.base.copy()
        for i, (img, adv, pad) in enumerate(self.side):
            blit(f, img, 40 - pad, 40 + i * 70 - pad, opacity=0.6 if i != 3 else 1.0)
        blit(f, self.head[0], 400 - self.head[2], 22 - self.head[2])
        n = min(len(self.lines), int(1 + tl / (self.dur / (len(self.lines) + 0.3))))
        y = 140
        for i in range(n):
            nm, col, txt = self.lines[i]
            cv2.circle(f, (430, y + 40), 30, tuple(c / 255 for c in col[::-1]), -1, cv2.LINE_AA)
            blit(f, nm[0], 480 - nm[2], y - nm[2])
            blit(f, txt[0], 480 - txt[2], y + 45 - txt[2])
            if self.MSGS[i][0] == "empleado_ti":
                cv2.rectangle(f, (380, y - 10), (1880, y + 110), (0.1, 0.1, 0.8), 2, cv2.LINE_AA)
            y += 150
        # typing cursor
        if (int(tl * 3) % 2) == 0:
            cv2.rectangle(f, (400, 960), (1880, 1030), (0.22, 0.2, 0.2), 2)
        zoom = 1.06 + 0.06 * tl / self.dur
        M = cv2.getRotationMatrix2D((W * 0.55, H * 0.55), 0, zoom)
        f = cv2.warpAffine(f, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
        return np.clip(barrel(f, 0.35), 0, 1)


class LeakGrid:
    def __init__(self, dur, n=90, cols=10, thumbs=None, t_fill=None):
        self.dur, self.n, self.cols = dur, n, cols
        self.t_fill = t_fill or dur * 0.65
        rows = math.ceil(n / cols)
        gw, gh = 1760, 900
        self.tw = int(gw / cols - 10)
        self.th = int(self.tw * 9 / 16)
        self.rows = rows
        rng = np.random.default_rng(2)
        self.tiles = []
        for i in range(n):
            src = thumbs[i % len(thumbs)]
            im = cv2.resize(src, (self.tw, self.th), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
            gray = im.mean(-1, keepdims=True)
            im = (gray + (im - gray) * 0.4) * 0.75
            self.tiles.append(im)
        self.order = rng.permutation(n)
        self.ox = (W - (self.tw + 10) * cols) // 2
        self.oy = 150

    def frame(self, tl):
        f = np.zeros((H, W, 3), np.float32) + 0.02
        k = int(self.n * ease_io(tl / self.t_fill))
        shown = set(self.order[:k].tolist())
        for i in range(self.n):
            r, c = divmod(i, self.cols)
            x = self.ox + c * (self.tw + 10)
            y = self.oy + r * (self.th + 10)
            if y + self.th > H:
                continue
            if i in shown:
                f[y:y + self.th, x:x + self.tw] = self.tiles[i]
                cv2.rectangle(f, (x, y), (x + self.tw - 1, y + self.th - 1), (0.1, 0.1, 0.75), 1)
                cx, cy = x + self.tw // 2, y + self.th // 2
                tri = np.array([[cx - 8, cy - 11], [cx - 8, cy + 11], [cx + 12, cy]], np.int32)
                cv2.fillPoly(f, [tri], (0.9, 0.9, 0.9), cv2.LINE_AA)
            else:
                cv2.rectangle(f, (x, y), (x + self.tw - 1, y + self.th - 1), (0.12, 0.12, 0.14), 1)
        img, adv, pad = render_word(f"VIDEOS FILTRADOS: {k:02d}", "lcd", 92)
        blit(f, img, 0, 0, cx=W / 2, cy=80)
        zoom = 1.0 + 0.1 * tl / self.dur
        M = cv2.getRotationMatrix2D((W / 2, H / 2), -1.5 * tl / self.dur, zoom)
        f = cv2.warpAffine(f, M, (W, H), borderMode=cv2.BORDER_CONSTANT)
        return np.clip(f, 0, 1)


class Years:
    def __init__(self, dur, y0=2014, y1=2026):
        self.dur, self.y0, self.y1 = dur, y0, y1

    def frame(self, tl):
        f = dark_grid((0.12, 0.02, 0.02), 0.05).copy()
        u = ease_io(tl / (self.dur * 0.75))
        yv = int(round(self.y0 + (self.y1 - self.y0) * u))
        img, adv, pad = render_word(str(yv), "lcd", 300)
        blit(f, img, 0, 0, cx=W / 2, cy=H / 2 - 60)
        x0, x1, yb = 360, 1560, 760
        cv2.line(f, (x0, yb), (x1, yb), (0.4, 0.4, 0.45), 2, cv2.LINE_AA)
        n = self.y1 - self.y0
        for i in range(n + 1):
            x = int(x0 + (x1 - x0) * i / n)
            on = (self.y0 + i) <= yv
            cv2.line(f, (x, yb - 14), (x, yb + 14), (0.15, 0.15, 0.95) if on else (0.4, 0.4, 0.45), 3, cv2.LINE_AA)
        xp = int(x0 + (x1 - x0) * (yv - self.y0) / n)
        cv2.line(f, (x0, yb), (xp, yb), (0.15, 0.15, 1.0), 6, cv2.LINE_AA)
        for yy, lab in ((self.y0, str(self.y0)), (self.y1, str(self.y1))):
            img, adv, pad = render_word(lab, "mono", 36)
            blit(f, img, 0, 0, cx=x0 + (x1 - x0) * (yy - self.y0) / n, cy=yb + 50)
        return f


class Chart:
    def __init__(self, dur, pts, color=(60, 255, 90), t_draw=None, labels=None, area=True, beep=False):
        self.dur, self.pts = dur, np.array(pts, np.float32)
        self.col = tuple(c / 255 for c in color[::-1])
        self.t_draw = t_draw or dur * 0.7
        self.labels = [render_word(l, "mono", 30) for l in (labels or [])]
        self.area = area

    def frame(self, tl):
        f = dark_grid((0.05, 0.05, 0.06), 0.06, step=90).copy()
        x0, x1, y0, y1 = 220, 1700, 860, 220
        cv2.line(f, (x0, y0), (x1, y0), (0.45, 0.45, 0.5), 2, cv2.LINE_AA)
        cv2.line(f, (x0, y0), (x0, y1), (0.45, 0.45, 0.5), 2, cv2.LINE_AA)
        for i, (img, adv, pad) in enumerate(self.labels):
            xx = x0 + (x1 - x0) * i / max(1, len(self.labels) - 1)
            blit(f, img, 0, 0, cx=xx, cy=y0 + 40)
        u = ease_io(tl / self.t_draw)
        P = self.pts
        n = len(P)
        k = u * (n - 1)
        ki = int(k)
        seg = [P[j] for j in range(min(ki + 1, n))]
        if ki < n - 1:
            seg.append(P[ki] + (P[ki + 1] - P[ki]) * (k - ki))
        pts = np.array([[x0 + (x1 - x0) * p[0], y0 + (y1 - y0) * p[1]] for p in seg], np.float32)
        if len(pts) >= 2:
            layer = np.zeros_like(f)
            if self.area:
                poly = np.vstack([pts, [[pts[-1][0], y0], [pts[0][0], y0]]]).astype(np.int32)
                cv2.fillPoly(layer, [poly], tuple(c * 0.25 for c in self.col), cv2.LINE_AA)
            cv2.polylines(layer, [pts.astype(np.int32)], False, self.col, 6, cv2.LINE_AA)
            glow = cv2.GaussianBlur(layer, (0, 0), 14) * 1.6
            f = f + glow + layer
            e = pts[-1].astype(int)
            cv2.circle(f, (int(e[0]), int(e[1])), 12, (1, 1, 1), -1, cv2.LINE_AA)
        zoom = 1.0 + 0.06 * tl / self.dur
        M = cv2.getRotationMatrix2D((W * 0.6, H * 0.45), 0, zoom)
        f = cv2.warpAffine(f, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
        return np.clip(f, 0, 1)


class Dossier:
    LINES = ["DOCUMENTO INTERNO", "", "NOMBRE CLAVE:  PROJECT AMERICAS", "INICIO:  2014",
             "ESCENARIO:  NORTEAMÉRICA + SUDAMÉRICA", "ESTADO:  EN DESARROLLO", "", "######## ##### ####", "#### ######### ##"]

    def __init__(self, dur):
        self.dur = dur
        rng = np.random.default_rng(4)
        desk = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
        desk = cv2.resize(cv2.GaussianBlur(desk, (0, 0), 3), (W, H))
        self.desk = np.stack([0.05 + desk * 0.01, 0.06 + desk * 0.012, 0.08 + desk * 0.015], -1).astype(np.float32)
        pw, ph = 1100, 1350
        paper = np.ones((ph, pw, 3), np.float32) * np.array([0.82, 0.88, 0.92], np.float32)
        nz = cv2.GaussianBlur(rng.random((ph, pw)).astype(np.float32), (0, 0), 1.5)
        paper *= (0.9 + 0.1 * nz)[:, :, None]
        self.paper = paper
        self.f = font("mono", 46)

    def frame(self, tl):
        p = self.paper.copy()
        im = Image.fromarray((p[:, :, ::-1] * 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        chars = int(tl * 38)
        y = 120
        for line in self.LINES:
            if chars <= 0:
                break
            if line.startswith("#"):
                ww = int(self.f.getlength(line[:min(len(line), chars)]))
                d.rectangle([90, y, 90 + ww, y + 46], fill=(15, 15, 15))
            else:
                d.text((90, y), line[:chars], font=self.f, fill=(25, 25, 25))
            chars -= len(line) + 3
            y += 80 if line else 40
        p = np.asarray(im, np.float32)[:, :, ::-1] / 255
        f = self.desk.copy()
        ang = -4 + 2 * tl / self.dur
        z = 0.78 + 0.12 * ease_io(tl / self.dur)
        ph, pw = p.shape[:2]
        M = cv2.getRotationMatrix2D((pw / 2, ph / 2), ang, z)
        M[0, 2] += W / 2 - pw / 2 + 60
        M[1, 2] += H / 2 - ph / 2 + 260
        mask = cv2.warpAffine(np.ones((ph, pw), np.float32), M, (W, H))
        warped = cv2.warpAffine(p, M, (W, H))
        sh = cv2.GaussianBlur(mask, (0, 0), 25)
        f = f * (1 - 0.7 * sh[:, :, None])
        f = f * (1 - mask[:, :, None]) + warped * mask[:, :, None]
        return np.clip(f, 0, 1)


# --------------------------------------------------------------- map
def _decode_topo(path, obj):
    d = json.load(open(path))
    sc, tr = d["transform"]["scale"], d["transform"]["translate"]
    arcs = []
    for arc in d["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
        arcs.append(pts)

    def ring(idx):
        out = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(a if not out else a[1:])
        return np.array(out, np.float64)

    geoms = {}
    for g in d["objects"][obj]["geometries"]:
        polys = []
        if g["type"] == "Polygon":
            polys = [[ring(r) for r in g["arcs"]]]
        elif g["type"] == "MultiPolygon":
            polys = [[ring(r) for r in p] for p in g["arcs"]]
        geoms[g.get("id")] = polys
    return geoms


NA = {"840", "124", "484", "084", "188", "222", "320", "340", "558", "591", "192", "214", "332", "388", "044", "630", "304"}
SA = {"032", "068", "076", "152", "170", "218", "328", "600", "604", "740", "858", "862", "238"}


def merc(lon, lat):
    lat = np.clip(lat, -80, 84)
    return lon, np.degrees(np.log(np.tan(np.radians(45 + lat / 2))))


class Map:
    """Americas map. mode 'unite': NA then SA light up + link. mode 'shrink': zoom into Florida."""

    def __init__(self, dur, mode="unite", t_na=1.5, t_sa=3.0, t_zoom=1.2):
        self.dur, self.mode, self.t_na, self.t_sa, self.t_zoom = dur, mode, t_na, t_sa, t_zoom
        if "geo" not in _cache:
            c = _decode_topo(A + "/geo/countries-50m.json", "countries")
            s = _decode_topo(A + "/geo/states-10m.json", "states")
            _cache["geo"] = (c, s["12"])
        self.c, self.fl = _cache["geo"]
        self.labels = {k: render_word(v, "label", 46, tracking=0.14) for k, v in
                       {"na": "NORTEAMÉRICA", "sa": "SUDAMÉRICA", "fl": "LEONIDA · INSPIRADO EN FLORIDA"}.items()}

    def _cam(self, tl):
        if self.mode == "unite":
            z = 1.0 + 0.08 * tl / self.dur
            return (-80.0, 8.0, 1.0 * z)
        u = ease_io((tl - self.t_zoom) / (self.dur - self.t_zoom - 0.3))
        lon = -80 + (-82.5 + 80) * u
        lat = 8 + (27.5 - 8) * u
        z = math.exp(math.log(1.0) + (math.log(7.0) - math.log(1.0)) * u)
        return lon, lat, z

    def _proj(self, ring, cam):
        lon0, lat0, z = cam
        x, y = merc(ring[:, 0], ring[:, 1])
        _, y0 = merc(np.array([lon0]), np.array([lat0]))
        s = 5.6 * z  # px per degree at zoom 1
        px = W / 2 + (x - lon0) * s
        py = H / 2 - (y - y0[0]) * s
        return np.stack([px, py], -1).astype(np.int32)

    def frame(self, tl):
        cam = self._cam(tl)
        f = dark_grid((0.04, 0.05, 0.06), 0.04, step=100, persp=False).copy()
        land = np.zeros((H, W), np.uint8)
        hi_na = np.zeros((H, W), np.uint8)
        hi_sa = np.zeros((H, W), np.uint8)
        borders = np.zeros((H, W), np.uint8)
        for cid, polys in self.c.items():
            for poly in polys:
                rings = [self._proj(r, cam) for r in poly]
                if max(abs(r[:, 0]).max() for r in rings) > 20000:
                    continue
                cv2.fillPoly(land, rings, 255)
                cv2.polylines(borders, rings, True, 255, 1, cv2.LINE_AA)
                if cid in NA:
                    cv2.fillPoly(hi_na, rings, 255)
                if cid in SA:
                    cv2.fillPoly(hi_sa, rings, 255)
        lf = land.astype(np.float32)[:, :, None] / 255
        f = f * (1 - lf) + np.array([0.16, 0.16, 0.17], np.float32) * lf
        f = f + borders.astype(np.float32)[:, :, None] / 255 * 0.18
        green = np.array([0.25, 1.0, 0.35], np.float32)
        if self.mode == "unite":
            base = 0.3 * ease_out((tl - 0.3) / 0.8)
            a_na = max(base, ease_out((tl - self.t_na) / 0.5))
            a_sa = max(base, ease_out((tl - self.t_sa) / 0.5))
            fade = 1.0
        else:
            a_na = a_sa = 1 - ease_out((tl - self.t_zoom) / 0.8)
            fade = 0
        for m, a in ((hi_na, a_na), (hi_sa, a_sa)):
            if a > 0:
                mm = m.astype(np.float32)[:, :, None] / 255
                glow = cv2.GaussianBlur(m, (0, 0), 18).astype(np.float32)[:, :, None] / 255
                f = f * (1 - mm * 0.75 * a) + green * mm * 0.75 * a + green * glow * 0.6 * a
        if self.mode == "unite" and a_sa > 0:
            p0 = self._proj(np.array([[-100.0, 40.0]]), cam)[0]
            p1 = self._proj(np.array([[-60.0, -12.0]]), cam)[0]
            u = ease_out((tl - self.t_sa) / 0.8)
            ctrl = ((p0 + p1) / 2 + np.array([-260, 0])).astype(np.float32)
            ts = np.linspace(0, u, 40)
            curve = np.array([(1 - t) ** 2 * p0 + 2 * (1 - t) * t * ctrl + t ** 2 * p1 for t in ts], np.int32)
            layer = np.zeros_like(f)
            cv2.polylines(layer, [curve], False, (1, 1, 1), 4, cv2.LINE_AA)
            f = f + layer + cv2.GaussianBlur(layer, (0, 0), 10)
        if self.mode == "unite":
            for key, ll, tt in (("na", (-100.0, 45.0), self.t_na), ("sa", (-60.0, -15.0), self.t_sa)):
                p = self._proj(np.array([ll]), cam)[0]
                img = self.labels[key][0]
                blit(f, img, 0, 0, opacity=ease_out((tt + 0.2 - tl) * -2.5), cx=p[0], cy=p[1])
        else:
            a_fl = ease_out((tl - self.t_zoom - 0.6) / 0.6)
            if a_fl > 0:
                m = np.zeros((H, W), np.uint8)
                for poly in self.fl:
                    cv2.fillPoly(m, [self._proj(r, cam) for r in poly], 255)
                mm = m.astype(np.float32)[:, :, None] / 255
                pink = np.array([0.55, 0.3, 1.0], np.float32)
                glow = cv2.GaussianBlur(m, (0, 0), 22).astype(np.float32)[:, :, None] / 255
                f = f * (1 - mm * 0.8 * a_fl) + pink * mm * 0.8 * a_fl + pink * glow * 0.7 * a_fl
                p = self._proj(np.array([[-82.0, 24.2]]), cam)[0]
                blit(f, self.labels["fl"][0], 0, 0, opacity=a_fl, cx=W / 2, cy=min(H - 120, p[1] + 60))
        return np.clip(f, 0, 1)
