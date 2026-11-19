"""Frame engine: image/video sources, Ken Burns, grading, text sprites, compositing, grain."""
import functools
import math
import os
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
IMG = os.path.join(ASSETS, "img")
VID = os.path.join(ASSETS, "vid")
FONT_DIR = os.path.join(ASSETS, "fonts")

YELLOW = (244, 196, 48)
RED = (215, 38, 61)
WHITE = (242, 239, 232)
BLACK = (11, 11, 12)
STEEL = (120, 150, 175)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_io(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def ease_back(t, s=1.6):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def lerp(a, b, t):
    return a + (b - a) * t


def prog(t, start, dur):
    """0..1 progress of an animation that starts at `start` and lasts `dur`."""
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return clamp((t - start) / dur)


# ---------------------------------------------------------------- fonts
FONT_FILES = {
    "serif": ("PlayfairDisplay.ttf", "Bold"),
    "serif_black": ("PlayfairDisplay.ttf", "Black"),
    "serif_it": ("PlayfairDisplay-Italic.ttf", "Bold Italic"),
    "sans": ("Poppins-SemiBold.ttf", None),
    "sans_med": ("Poppins-Medium.ttf", None),
    "sans_bold": ("Poppins-Bold.ttf", None),
    "sans_xb": ("Poppins-ExtraBold.ttf", None),
    "bebas": ("BebasNeue.ttf", None),
    "mono": ("JetBrainsMono.ttf", "Bold"),
    "mono_reg": ("JetBrainsMono.ttf", "Regular"),
    "type": ("SpecialElite.ttf", None),
    "oswald": ("Oswald.ttf", "Bold"),
}


@functools.lru_cache(maxsize=256)
def font(name, size):
    fn, var = FONT_FILES[name]
    f = ImageFont.truetype(os.path.join(FONT_DIR, fn), size)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


# ---------------------------------------------------------------- grading
def _lut(fn):
    x = np.arange(256, dtype=np.float32) / 255.0
    return np.clip(fn(x) * 255.0, 0, 255).astype(np.uint8)


def s_curve(amount=0.25, lift=0.0, gain=1.0):
    def f(x):
        y = x + amount * (x - 0.5) * (1 - np.abs(2 * x - 1)) * 2 * 0.5
        y = 0.5 + (y - 0.5) * (1 + amount)
        return np.clip(lift + y * (gain - lift), 0, 1)
    return f


def grade(img, kind):
    """img RGB uint8 -> graded RGB uint8."""
    if kind in (None, "none"):
        return img
    if kind in ("bw", "archival", "sepia", "cold_bw"):
        g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        g = cv2.LUT(g, _lut(s_curve(0.18, lift=0.05, gain=0.96)))
        if kind == "bw":
            return cv2.merge([g, g, g])
        gf = g.astype(np.float32) / 255.0
        if kind == "archival":
            tint = (1.04, 1.0, 0.90)
        elif kind == "cold_bw":
            tint = (0.93, 0.98, 1.06)
        else:
            tint = (1.10, 0.98, 0.78)
        out = np.stack([gf * tint[0], gf * tint[1], gf * tint[2]], -1)
        return np.clip(out * 255, 0, 255).astype(np.uint8)
    f = img.astype(np.float32) / 255.0
    if kind == "doc":  # documentary teal/orange, slightly desaturated, crushed
        gray = f.mean(-1, keepdims=True)
        f = gray + (f - gray) * 0.82
        f = 0.5 + (f - 0.5) * 1.12
        f[..., 0] *= 1.02
        f[..., 2] = f[..., 2] * 0.95 + 0.03 * (1 - gray[..., 0])
    elif kind == "cold":
        gray = f.mean(-1, keepdims=True)
        f = gray + (f - gray) * 0.65
        f = f * np.array([0.92, 0.99, 1.08], np.float32)
        f = 0.5 + (f - 0.5) * 1.1
    elif kind == "warm":
        f = f * np.array([1.08, 1.0, 0.86], np.float32)
        f = 0.5 + (f - 0.5) * 1.06
    elif kind == "faded":  # vintage colour (postcards, 60s)
        gray = f.mean(-1, keepdims=True)
        f = gray + (f - gray) * 0.75
        f = 0.06 + f * 0.9
        f = f * np.array([1.05, 1.0, 0.88], np.float32)
    elif kind == "dark":
        gray = f.mean(-1, keepdims=True)
        f = gray + (f - gray) * 0.7
        f = (0.5 + (f - 0.5) * 1.15) * 0.72
    elif kind == "night":
        gray = f.mean(-1, keepdims=True)
        f = gray + (f - gray) * 0.55
        f = f * np.array([0.82, 0.95, 1.1], np.float32) * 0.8
    return np.clip(f * 255, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- image loading
@functools.lru_cache(maxsize=48)
def load_image(path, grade_kind="none", max_side=3000):
    if not os.path.isabs(path):
        path = os.path.join(IMG, path)
    im = Image.open(path)
    im = im.convert("RGB")
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.LANCZOS)
    arr = np.asarray(im).copy()
    return grade(arr, grade_kind)


def cover_scale(w, h, ow=W, oh=H):
    return max(ow / w, oh / h)


def kb_frame(src, cx, cy, zoom, rot=0.0, ow=W, oh=H):
    """Render src so that normalized point (cx,cy) is centred, zoom 1 = cover."""
    h0, w0 = src.shape[:2]
    s = cover_scale(w0, h0, ow, oh) * zoom
    # clamp centre so we never show outside the image
    half_w = ow / (2 * s) / w0
    half_h = oh / (2 * s) / h0
    cx = clamp(cx, half_w, 1 - half_w) if half_w < 0.5 else 0.5
    cy = clamp(cy, half_h, 1 - half_h) if half_h < 0.5 else 0.5
    if rot:
        M = cv2.getRotationMatrix2D((cx * w0, cy * h0), rot, s)
        M[0, 2] += ow / 2 - cx * w0
        M[1, 2] += oh / 2 - cy * h0
    else:
        M = np.array([[s, 0, ow / 2 - s * cx * w0], [0, s, oh / 2 - s * cy * h0]], np.float32)
    interp = cv2.INTER_AREA if s < 0.5 else cv2.INTER_LINEAR
    return cv2.warpAffine(src, M, (ow, oh), flags=interp, borderMode=cv2.BORDER_REFLECT)


def fit_into(src, bw, bh):
    h0, w0 = src.shape[:2]
    s = min(bw / w0, bh / h0)
    return cv2.resize(src, (max(1, int(w0 * s)), max(1, int(h0 * s))), interpolation=cv2.INTER_AREA)


@functools.lru_cache(maxsize=24)
def blurred_bg(path, grade_kind, darken=0.45):
    src = load_image(path, grade_kind)
    small = kb_frame(src, 0.5, 0.5, 1.0, ow=W // 4, oh=H // 4)
    small = cv2.GaussianBlur(small, (0, 0), 9)
    big = cv2.resize(small, (W + 120, H + 68), interpolation=cv2.INTER_LINEAR)
    return (big.astype(np.float32) * darken).astype(np.uint8)


# ---------------------------------------------------------------- video reading
class VideoReader:
    """Sequential frame reader through ffmpeg; frames covered to W x H."""

    def __init__(self, path, start=0.0, speed=1.0, grade_kind="none", ow=W, oh=H, reverse=False):
        if not os.path.isabs(path):
            path = os.path.join(VID, path)
        self.path, self.speed, self.grade_kind = path, speed, grade_kind
        self.ow, self.oh = ow, oh
        vf = []
        if speed != 1.0:
            vf.append(f"setpts=PTS/{speed}")
        vf += [f"fps={FPS}", f"scale={ow}:{oh}:force_original_aspect_ratio=increase:flags=bicubic",
               f"crop={ow}:{oh}"]
        if reverse:
            vf.append("reverse")
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0.0, start):.3f}", "-i", path, "-an",
               "-vf", ",".join(vf), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=ow * oh * 3 * 4)
        self.last = np.zeros((oh, ow, 3), np.uint8)
        self.n = 0

    def read(self):
        buf = self.p.stdout.read(self.ow * self.oh * 3)
        if len(buf) == self.ow * self.oh * 3:
            fr = np.frombuffer(buf, np.uint8).reshape(self.oh, self.ow, 3)
            self.last = grade(fr, self.grade_kind) if self.grade_kind not in (None, "none") else fr.copy()
        self.n += 1
        return self.last

    def close(self):
        try:
            self.p.stdout.close()
            self.p.kill()
        except Exception:
            pass


# ---------------------------------------------------------------- sprites / compositing
class Sprite:
    """Premultiplied RGBA float sprite."""

    def __init__(self, rgba):
        a = rgba[..., 3:4].astype(np.float32) / 255.0
        self.rgb = rgba[..., :3].astype(np.float32) * a
        self.a = a
        self.h, self.w = rgba.shape[:2]

    @classmethod
    def from_pil(cls, im):
        return cls(np.asarray(im.convert("RGBA")))


def over(dst, sp, x, y, alpha=1.0, scale=1.0):
    """Composite Sprite onto dst (uint8 RGB, modified in place) with top-left at (x,y)."""
    if alpha <= 0.002:
        return dst
    rgb, a = sp.rgb, sp.a
    if abs(scale - 1.0) > 1e-3:
        nw, nh = max(1, int(sp.w * scale)), max(1, int(sp.h * scale))
        rgb = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_LINEAR)
        a = cv2.resize(a, (nw, nh), interpolation=cv2.INTER_LINEAR)
        if a.ndim == 2:
            a = a[..., None]
    h, w = a.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return dst
    sx0, sy0 = x0 - x, y0 - y
    s_rgb = rgb[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    s_a = a[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)] * alpha
    d = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = np.clip(d * (1 - s_a) + s_rgb * alpha, 0, 255).astype(np.uint8)
    return dst


def over_center(dst, sp, cx, cy, alpha=1.0, scale=1.0):
    return over(dst, sp, cx - sp.w * scale / 2, cy - sp.h * scale / 2, alpha, scale)


def blend(a, b, t):
    if t <= 0:
        return a
    if t >= 1:
        return b
    return cv2.addWeighted(a, 1 - t, b, t, 0)


def darken(img, k):
    return (img.astype(np.float32) * k).clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- text sprites
def text_size(txt, f):
    l, t, r, b = f.getbbox(txt)
    return r - l, b - t, l, t


@functools.lru_cache(maxsize=512)
def text_sprite(txt, fname, size, color=WHITE, shadow=True, stroke=0, stroke_color=BLACK, tracking=0, pad=24):
    f = font(fname, size)
    if tracking:
        widths = [text_size(c, f)[0] if c != " " else size * 0.28 for c in txt]
        tw = int(sum(widths) + tracking * (len(txt) - 1))
    else:
        tw = int(f.getlength(txt))
    asc, desc = f.getmetrics()
    th = asc + desc
    im = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def draw_at(dx, dy, col, sw=0):
        if tracking:
            x = pad + dx
            for c, wdt in zip(txt, widths):
                d.text((x, pad + dy), c, font=f, fill=col, stroke_width=sw, stroke_fill=col)
                x += wdt + tracking
        else:
            d.text((pad + dx, pad + dy), txt, font=f, fill=col, stroke_width=sw, stroke_fill=col)

    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d2 = ImageDraw.Draw(sh)
        if tracking:
            x = pad
            for c, wdt in zip(txt, widths):
                d2.text((x + 3, pad + 4), c, font=f, fill=(0, 0, 0, 200))
                x += wdt + tracking
        else:
            d2.text((pad + 3, pad + 4), txt, font=f, fill=(0, 0, 0, 200))
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        im = Image.alpha_composite(sh, im)
        d = ImageDraw.Draw(im)
    if stroke:
        if tracking:
            x = pad
            for c, wdt in zip(txt, widths):
                d.text((x, pad), c, font=f, fill=color + (255,), stroke_width=stroke, stroke_fill=stroke_color + (255,))
                x += wdt + tracking
        else:
            d.text((pad, pad), txt, font=f, fill=color + (255,), stroke_width=stroke, stroke_fill=stroke_color + (255,))
    else:
        draw_at(0, 0, color + (255,))
    return Sprite.from_pil(im)


def rounded_rect_sprite(w, h, color, radius=10, alpha=255, border=0, border_color=None):
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=color + (alpha,),
                        outline=(border_color + (255,)) if border else None, width=border)
    return Sprite.from_pil(im)


# ---------------------------------------------------------------- film texture
class Texture:
    def __init__(self, seed=7):
        rng = np.random.default_rng(seed)
        self.grain = []
        for _ in range(12):
            g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
            g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
            self.grain.append(g)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        self.vig = np.clip(1.0 - 0.42 * np.clip(r - 0.35, 0, None) ** 1.6, 0.35, 1.0)[..., None].astype(np.float32)
        self.scratch_rng = np.random.default_rng(seed + 1)

    def apply(self, img, frame_idx, grain=6.0, vignette=1.0, dust=0.0, flicker=0.0):
        f = img.astype(np.float32)
        if vignette > 0:
            v = 1 - (1 - self.vig) * vignette
            f *= v
        if flicker > 0:
            f *= 1 + flicker * math.sin(frame_idx * 1.7) * 0.5 + flicker * (((frame_idx * 7919) % 13) / 13 - 0.5)
        if grain > 0:
            f += self.grain[frame_idx % len(self.grain)][..., None] * grain
        out = np.clip(f, 0, 255).astype(np.uint8)
        if dust > 0:
            rng = np.random.default_rng(frame_idx * 31 + 5)
            n = rng.poisson(dust * 6)
            for _ in range(n):
                x, y = int(rng.uniform(0, W)), int(rng.uniform(0, H))
                rr = int(rng.uniform(1, 3))
                col = 235 if rng.random() < 0.5 else 20
                cv2.circle(out, (x, y), rr, (col, col, col), -1, lineType=cv2.LINE_AA)
            if rng.random() < dust * 0.35:
                x = int(rng.uniform(0.1, 0.9) * W)
                cv2.line(out, (x, 0), (x + int(rng.uniform(-8, 8)), H), (200, 200, 200), 1, lineType=cv2.LINE_AA)
        return out


TEX = None


def texture():
    global TEX
    if TEX is None:
        TEX = Texture()
    return TEX
