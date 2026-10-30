"""Core helpers: sources, grading, text rendering, overlays blit, look, transitions."""
import os, json, math, subprocess, unicodedata, re
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
# Carpeta de trabajo con assets/ (coverr, unsplash, img, music, sfx, fonts, geo, gen) y work/ (transcript.json, renders)
S = os.environ.get("VIDEO_WORKDIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "workdir")))
A = S + "/assets"
DW, DH = 2112, 1188  # decode size for video (10% headroom for Ken Burns)

FONTS = {
    "pbi": A + "/fonts/Poppins-BoldItalic.ttf",
    "psbi": A + "/fonts/Poppins-SemiBoldItalic.ttf",
    "pxbi": A + "/fonts/Poppins-ExtraBoldItalic.ttf",
    "pblki": A + "/fonts/Poppins-BlackItalic.ttf",
    "pb": A + "/fonts/Poppins-Bold.ttf",
    "psb": A + "/fonts/Poppins-SemiBold.ttf",
    "pm": A + "/fonts/Poppins-Medium.ttf",
    "anton": A + "/fonts/Anton-Regular.ttf",
    "bebas": A + "/fonts/BebasNeue-Regular.ttf",
    "script": A + "/fonts/GreatVibes-Regular.ttf",
    "pinyon": A + "/fonts/PinyonScript-Regular.ttf",
    "rye": A + "/fonts/Rye-Regular.ttf",
    "mono": A + "/fonts/ShareTechMono-Regular.ttf",
    "vt": A + "/fonts/VT323-Regular.ttf",
    "monoton": A + "/fonts/Monoton-Regular.ttf",
}


def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp01(x)
    return x ** 3


def ease_io(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


# ---------------------------------------------------------------- sources
_probe_cache = {}


def probe_dur(path):
    if path not in _probe_cache:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", path], capture_output=True, text=True).stdout
        _probe_cache[path] = float(out.strip())
    return _probe_cache[path]


def resolve(key):
    pre, _, name = key.partition(":")
    if pre == "cv":
        return A + f"/coverr/{name}.mp4"
    if pre == "us":
        return A + f"/unsplash/{name}.jpg"
    if pre == "img":
        return A + f"/img/{name}"
    if pre == "gen":
        return A + f"/gen/{name}"
    raise ValueError(key)


class VideoReader:
    """Streams frames of a (sub)shot at FPS, decoded at DWxDH cover size."""

    def __init__(self, path, ss, speed, nframes, rev=False):
        self.n = nframes
        self.rev = rev
        cd = probe_dur(path) - 0.15
        need = nframes / FPS * speed
        if need > cd:
            speed = cd / (nframes / FPS)
            need = cd
            ss = 0
        if ss + need > cd:
            ss = max(0.0, cd - need)
        self.args = (path, ss, speed)
        self.frames = []
        self.proc = None
        self.k = -1
        self.last = None
        if rev:
            self._open(0)
            while len(self.frames) < nframes:
                f = self._read()
                if f is None:
                    break
                self.frames.append(f)
            self._close()

    def _open(self, k0):
        path, ss, speed = self.args
        start = ss + k0 / FPS * speed
        vf = (f"setpts=(PTS-STARTPTS)/{speed},fps={FPS},scale={DW}:{DH}:force_original_aspect_ratio=increase,"
              f"crop={DW}:{DH}")
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", path, "-an", "-vf", vf,
               "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=DW * DH * 3 * 2)
        self.k = k0 - 1

    def _read(self):
        buf = self.proc.stdout.read(DW * DH * 3)
        if len(buf) < DW * DH * 3:
            return None
        return np.frombuffer(buf, np.uint8).reshape(DH, DW, 3)

    def _close(self):
        if self.proc:
            try:
                self.proc.stdout.close()
                self.proc.kill()
                self.proc.wait()
            except Exception:
                pass
            self.proc = None

    def get(self, k):
        if self.rev:
            if not self.frames:
                return np.zeros((DH, DW, 3), np.uint8)
            return self.frames[max(0, min(len(self.frames) - 1, self.n - 1 - k))]
        if self.proc is None or k <= self.k - 1 or k > self.k + 40:
            self._close()
            self._open(k)
        while self.k < k:
            f = self._read()
            self.k += 1
            if f is None:
                break
            self.last = f
        return self.last if self.last is not None else np.zeros((DH, DW, 3), np.uint8)

    def close(self):
        self._close()


_img_cache = {}


def load_image(path, max_long=3200):
    if path not in _img_cache:
        im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if im is None:
            raise FileNotFoundError(path)
        if im.ndim == 2:
            im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        if im.shape[2] == 4:
            a = im[:, :, 3:4].astype(np.float32) / 255
            im = (im[:, :, :3].astype(np.float32) * a).astype(np.uint8)
        h, w = im.shape[:2]
        s = min(1.0, max_long / max(w, h))
        if s < 1:
            im = cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
        _img_cache[path] = im
    return _img_cache[path]


def view_warp(src, z, px, py, rot=0.0, out=(W, H)):
    """Ken-Burns view: cover-fit 16:9 window, zoom z>=1, pan px,py in [-1,1]."""
    h, w = src.shape[:2]
    ow, oh = out
    ar = ow / oh
    if w / h > ar:
        bh, bw = h, h * ar
    else:
        bw, bh = w, w / ar
    vw, vh = bw / z, bh / z
    cx = w / 2 + px * (w - vw) / 2
    cy = h / 2 + py * (h - vh) / 2
    s = ow / vw
    M = np.array([[s, 0, -s * (cx - vw / 2)], [0, s, -s * (cy - vh / 2)]], np.float32)
    if rot:
        R = cv2.getRotationMatrix2D((ow / 2, oh / 2), rot, 1.0)
        M3 = np.vstack([M, [0, 0, 1]])
        M = (np.vstack([R, [0, 0, 1]]) @ M3)[:2].astype(np.float32)
    return cv2.warpAffine(src, M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ---------------------------------------------------------------- grading
GRADES = {
    "doc": dict(sat=0.85, con=1.12, br=1.0, ts=(0.025, 0.012, -0.01), th=(-0.02, 0.0, 0.025)),
    "night": dict(sat=0.8, con=1.15, br=0.85, ts=(0.04, 0.02, -0.01), th=(-0.01, 0.0, 0.02)),
    "cold": dict(sat=0.65, con=1.12, br=0.95, ts=(0.06, 0.03, -0.02), th=(0.03, 0.01, -0.02)),
    "warm": dict(sat=0.9, con=1.1, br=1.0, ts=(0.0, 0.0, 0.015), th=(-0.05, 0.0, 0.05)),
    "sepia": dict(sat=0.35, con=1.15, br=0.95, ts=(-0.01, 0.0, 0.02), th=(-0.07, 0.0, 0.06)),
    "bw": dict(sat=0.0, con=1.28, br=0.95, ts=(0, 0, 0), th=(0, 0, 0)),
    "vice": dict(sat=1.15, con=1.12, br=1.0, ts=(0.06, 0.0, 0.03), th=(0.0, -0.02, 0.06)),
    "raw": dict(sat=1.0, con=1.0, br=1.0, ts=(0, 0, 0), th=(0, 0, 0)),
}
MULT = {
    "red": np.array([0.45, 0.5, 1.25], np.float32),
    "green": np.array([0.6, 1.1, 0.55], np.float32),
    "blue": np.array([1.25, 0.8, 0.45], np.float32),
    "ice": np.array([1.25, 1.05, 0.8], np.float32),
}


def grade(img, name="doc", dark=1.0):
    base, _, mult = name.partition("+")
    g = GRADES.get(base, GRADES["doc"])
    x = img * (g["br"] * dark)
    gray = x[:, :, 0] * 0.114 + x[:, :, 1] * 0.587 + x[:, :, 2] * 0.299
    gray3 = gray[:, :, None]
    x = gray3 + (x - gray3) * g["sat"]
    x = (x - 0.45) * g["con"] + 0.45
    ws = (1 - np.clip(gray3, 0, 1)) ** 2
    wh = np.clip(gray3, 0, 1) ** 2
    x = x + np.array(g["ts"], np.float32) * ws + np.array(g["th"], np.float32) * wh
    if mult:
        x = x * MULT[mult]
    return np.clip(x, 0, 1)


def holo(img, t):
    """Blue hologram look with wavy scan lines (reference 3:18)."""
    gray = cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    gray = np.clip((gray - 0.08) * 1.35, 0, 1)
    out = np.stack([gray * 1.15 + 0.05, gray * 0.78 + 0.03, gray * 0.35], -1)
    yy = np.arange(H, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]
    wave = np.sin((yy + 18 * np.sin(xx / 140 + t * 2.2)) / 5.0 * math.pi)
    lines = 0.78 + 0.22 * wave
    out = out * lines[:, :, None]
    return np.clip(out, 0, 1).astype(np.float32)


# ---------------------------------------------------------------- text
_font_cache = {}


def font(name, size):
    k = (name, int(size))
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(FONTS[name], int(size))
    return _font_cache[k]


STYLES = {
    # font, rgb color, glow rgb, glow radius factor, glow strength, shadow opacity
    "w": dict(f="pbi", c=(255, 255, 255), g=(255, 255, 255), gr=0.22, gs=0.42, sh=0.75),
    "r": dict(f="pbi", c=(255, 28, 28), g=(255, 0, 0), gr=0.32, gs=1.05, sh=0.85),
    "wb": dict(f="pblki", c=(255, 255, 255), g=(255, 255, 255), gr=0.18, gs=0.35, sh=0.8),
    "rb": dict(f="pblki", c=(255, 30, 30), g=(255, 0, 0), gr=0.3, gs=1.0, sh=0.85),
    "lcd": dict(f="vt", c=(255, 40, 40), g=(255, 0, 0), gr=0.3, gs=1.2, sh=0.6),
    "lcdw": dict(f="vt", c=(235, 235, 235), g=(255, 255, 255), gr=0.2, gs=0.5, sh=0.6),
    "lcdg": dict(f="vt", c=(60, 255, 90), g=(0, 255, 60), gr=0.3, gs=1.0, sh=0.6),
    "script": dict(f="script", c=(225, 18, 25), g=(0, 0, 0), gr=0.35, gs=1.4, sh=0.9),
    "anton": dict(f="anton", c=(255, 255, 255), g=(255, 255, 255), gr=0.15, gs=0.35, sh=0.8),
    "antonr": dict(f="anton", c=(255, 30, 30), g=(255, 0, 0), gr=0.28, gs=1.0, sh=0.85),
    "rye": dict(f="rye", c=(235, 35, 30), g=(255, 0, 0), gr=0.25, gs=0.9, sh=1.0),
    "vice": dict(f="pblki", c=(255, 80, 170), grad=((255, 70, 170), (255, 175, 70)), g=(255, 40, 140), gr=0.3, gs=1.0, sh=0.7),
    "vicescript": dict(f="script", c=(255, 90, 190), grad=((255, 110, 200), (255, 190, 90)), g=(255, 40, 150), gr=0.3, gs=1.2, sh=0.7),
    "ice": dict(f="pblki", c=(220, 245, 255), g=(120, 200, 255), gr=0.3, gs=1.0, sh=0.8),
    "label": dict(f="psb", c=(240, 240, 240), g=(255, 255, 255), gr=0.2, gs=0.3, sh=0.8),
    "mono": dict(f="mono", c=(230, 230, 230), g=(255, 255, 255), gr=0.15, gs=0.25, sh=0.6),
    "monor": dict(f="mono", c=(255, 50, 50), g=(255, 0, 0), gr=0.3, gs=0.9, sh=0.6),
    "monog": dict(f="mono", c=(80, 255, 120), g=(0, 255, 80), gr=0.25, gs=0.7, sh=0.5),
    "dark": dict(f="mono", c=(20, 20, 20), g=(0, 0, 0), gr=0.0, gs=0.0, sh=0.0),
}

_word_cache = {}


def render_word(text, style, size, tracking=0.0):
    """Return (premultiplied BGRA float32 image, advance width, pad)."""
    key = (text, style, int(size), tracking)
    if key in _word_cache:
        return _word_cache[key]
    st = STYLES[style]
    f = font(st["f"], size)
    asc, desc = f.getmetrics()
    pad = int(size * 0.6) + 8
    if tracking:
        adv = sum(f.getlength(ch) for ch in text) + tracking * size * (len(text) - 1)
    else:
        adv = f.getlength(text)
    cw = int(adv + 2 * pad + size * 0.35)
    ch = int(asc + desc + 2 * pad)
    m = Image.new("L", (cw, ch), 0)
    d = ImageDraw.Draw(m)
    if tracking:
        x = pad
        for c in text:
            d.text((x, pad), c, font=f, fill=255, anchor="la")
            x += f.getlength(c) + tracking * size
    else:
        d.text((pad, pad), text, font=f, fill=255, anchor="la")
    mask = np.asarray(m, np.float32) / 255.0
    # colour layer
    if "grad" in st:
        c0 = np.array(st["grad"][0][::-1], np.float32) / 255
        c1 = np.array(st["grad"][1][::-1], np.float32) / 255
        ys = np.linspace(0, 1, ch, dtype=np.float32)[:, None, None]
        col = c0 * (1 - ys) + c1 * ys
        col = np.broadcast_to(col, (ch, cw, 3))
    else:
        col = np.broadcast_to(np.array(st["c"][::-1], np.float32) / 255, (ch, cw, 3))
    out = np.zeros((ch, cw, 4), np.float32)
    # shadow
    if st["sh"] > 0:
        sr = max(1.0, size * 0.1)
        shm = cv2.GaussianBlur(mask, (0, 0), sr)
        shm = np.roll(shm, int(size * 0.05), axis=0) * st["sh"]
        out[:, :, 3] = shm
    # glow
    if st["gs"] > 0 and st["gr"] > 0:
        gm = np.clip(cv2.GaussianBlur(mask, (0, 0), max(1.0, size * st["gr"])) * st["gs"] * 1.6, 0, 1)
        gc = np.array(st["g"][::-1], np.float32) / 255
        top = np.concatenate([gc * gm[:, :, None], gm[:, :, None]], -1)
        out = top + out * (1 - gm[:, :, None])
    top = np.concatenate([col * mask[:, :, None], mask[:, :, None]], -1)
    out = top + out * (1 - mask[:, :, None])
    res = (out.astype(np.float32), adv, pad)
    _word_cache[key] = res
    return res


def blit(frame, img, x, y, opacity=1.0, scale=1.0, cx=None, cy=None):
    """Composite premultiplied BGRA img onto frame. (x,y) top-left at scale 1, or centre (cx,cy)."""
    if opacity <= 0.003:
        return
    if scale != 1.0:
        h0, w0 = img.shape[:2]
        nw, nh = max(1, int(w0 * scale)), max(1, int(h0 * scale))
        img = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
        if cx is None:
            cx, cy = x + w0 / 2, y + h0 / 2
    if cx is not None:
        x, y = cx - img.shape[1] / 2, cy - img.shape[0] / 2
    x, y = int(round(x)), int(round(y))
    h, w = img.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    sub = img[y0 - y:y1 - y, x0 - x:x1 - x]
    a = sub[:, :, 3:4] * opacity
    frame[y0:y1, x0:x1] = sub[:, :, :3] * opacity + frame[y0:y1, x0:x1] * (1 - a)


def rgba_from_bgra_u8(im):
    """uint8 BGRA (straight alpha) -> premultiplied float."""
    f = im.astype(np.float32) / 255
    a = f[:, :, 3:4]
    return np.concatenate([f[:, :, :3] * a, a], -1)


def add_glow(img, radius, strength, color=None):
    a = img[:, :, 3]
    pad = int(radius * 3)
    img = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    a = img[:, :, 3]
    g = np.clip(cv2.GaussianBlur(a, (0, 0), radius) * strength, 0, 1)
    if color is None:
        rgb = cv2.GaussianBlur(img[:, :, :3], (0, 0), radius) * strength
    else:
        rgb = np.array(color[::-1], np.float32) / 255 * g[:, :, None]
    glow = np.concatenate([np.clip(rgb, 0, 1), g[:, :, None]], -1)
    return img + glow * (1 - img[:, :, 3:4])


# ---------------------------------------------------------------- global look
_look = {}


def _look_init():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    _look["vig"] = np.clip(1 - 0.62 * r ** 2.1, 0, 1)[:, :, None].astype(np.float32)
    _look["edge"] = (np.clip((r - 0.45) / 0.55, 0, 1) ** 1.6 * 0.9)[:, :, None].astype(np.float32)
    rng = np.random.default_rng(7)
    grains = []
    for i in range(8):
        g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
        grains.append(g[:, :, None])
    _look["grain"] = grains


def look(frame, fi, ca=0.0032, grain=0.026, vig=True, edge=True):
    if not _look:
        _look_init()
    if edge:
        small = cv2.resize(frame, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), 2.2)
        big = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
        m = _look["edge"]
        frame = frame * (1 - m) + big * m
    if ca:
        b, g, r = cv2.split(frame)
        Mr = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1 + ca)
        Mb = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1 - ca)
        r = cv2.warpAffine(r, Mr, (W, H), borderMode=cv2.BORDER_REFLECT)
        b = cv2.warpAffine(b, Mb, (W, H), borderMode=cv2.BORDER_REFLECT)
        frame = cv2.merge([b, g, r])
    if vig:
        frame = frame * _look["vig"]
    flick = 1 + 0.012 * math.sin(fi * 1.7) * math.sin(fi * 0.31)
    frame = frame * flick + _look["grain"][fi % 8] * grain
    return np.clip(frame, 0, 1)


# ---------------------------------------------------------------- transitions
def tr_effect(frame, kind, i, side, fi, direction=1):
    """i in (0,1] = intensity (1 at the cut). side: 'out' (end of shot) or 'in'."""
    if i <= 0:
        return frame
    if kind == "whip":
        sh = direction * (i ** 2) * 0.45 * W * (1 if side == "out" else -1)
        M = np.float32([[1, 0, -sh], [0, 1, 0]])
        frame = cv2.warpAffine(frame, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        L = int(8 + 160 * i)
        frame = cv2.blur(frame, (L, 1))
    elif kind == "zoom":
        s = 1 + 0.6 * i ** 2
        acc = np.zeros_like(frame)
        n = 5
        for k in range(n):
            sk = s * (1 + 0.06 * i * k / n)
            M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, sk)
            acc += cv2.warpAffine(frame, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        frame = acc / n
        frame = frame + (1 - frame) * (0.25 * i ** 2)
    elif kind == "glitch":
        frame = glitch(frame, i, fi)
    elif kind == "flash":
        k = i ** 1.6 * (0.95 if side == "in" else 0.55)
        frame = frame + (1 - frame) * k
    elif kind in ("fade", "dip"):
        frame = frame * (1 - i)
    elif kind == "redflash":
        k = i ** 1.5 * 0.8
        frame = frame * (1 - k) + np.array([0.05, 0.05, 0.9], np.float32) * k
    return frame


def glitch(frame, i, fi, seed=0):
    rng = np.random.default_rng(fi * 7919 + seed)
    out = frame.copy()
    # channel split
    s = int(30 * i)
    if s:
        out[:, :, 2] = np.roll(frame[:, :, 2], s, axis=1)
        out[:, :, 0] = np.roll(frame[:, :, 0], -s, axis=1)
    # slice displacement
    n = int(4 + 14 * i)
    for _ in range(n):
        y = int(rng.integers(0, H - 10))
        hgt = int(rng.integers(6, int(20 + 120 * i)))
        dx = int(rng.normal(0, 120 * i))
        out[y:y + hgt] = np.roll(out[y:y + hgt], dx, axis=1)
    # blocks
    for _ in range(int(6 * i)):
        x, y = int(rng.integers(0, W - 200)), int(rng.integers(0, H - 60))
        w, h = int(rng.integers(40, 300)), int(rng.integers(8, 60))
        c = rng.random()
        if c < 0.4:
            out[y:y + h, x:x + w] = 1 - out[y:y + h, x:x + w]
        elif c < 0.7:
            out[y:y + h, x:x + w] *= np.array([0.2, 0.2, 1.0], np.float32)
        else:
            out[y:y + h, x:x + w] = rng.random()
    # scan noise
    if i > 0.3:
        lines = rng.random(H).astype(np.float32)[:, None, None]
        out = out + (lines > 0.97) * 0.25 * i
    return np.clip(out, 0, 1)


# ---------------------------------------------------------------- transcript
def norm_word(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9$]", "", w)


_tw = None


def transcript_words():
    global _tw
    if _tw is None:
        d = json.load(open(S + "/work/transcript.json"))
        _tw = [(norm_word(w["w"]), w["s"], w["e"]) for s in d for w in s["words"]]
    return _tw


def word_times(words, t0, window=8.0):
    """Align a list of display words to transcript word start times near t0."""
    tw = transcript_words()
    cands = [x for x in tw if t0 - 1.2 <= x[1] <= t0 + window]
    res = []
    j = 0
    last = t0
    for w in words:
        nw = norm_word(w)
        hit = None
        for k in range(j, len(cands)):
            cw = cands[k][0]
            if nw and (cw == nw or (len(nw) > 4 and len(cw) > 4 and (cw.startswith(nw[:6]) or nw.startswith(cw[:6])))):
                hit = k
                break
        if hit is not None and cands[hit][1] - last < 3.0:
            last = cands[hit][1]
            j = hit + 1
            res.append(last)
        else:
            last = last + 0.14
            res.append(last)
    return res
