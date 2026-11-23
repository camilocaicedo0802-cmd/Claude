"""Helpers for the Cabany reel: easing, 3D projection, layer compositing, text."""
import math, os, re, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30

# ---------- brand ----------
def rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
GREEN = rgb('023B28')      # theme-color / header
GREEN_D = rgb('012A1C')
GREEN_M = rgb('0B5A3D')
LIME = rgb('86CB2C')       # "DESCUBRE PANAMÁ" in the logo
LIME_B = rgb('A9E93A')     # site accent
CREAM = rgb('F8F5F2')
WHITE = (255, 255, 255)
INK = rgb('0F172A')        # site text

FONT_DIR = f'{ROOT}/fonts'
def font(w, size):
    return _font(int(w), int(round(size)))
@functools.lru_cache(maxsize=256)
def _font(w, size):
    return ImageFont.truetype(f'{FONT_DIR}/Montserrat-{w}.ttf', size)
EMOJI_FONT = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lin(p): return p
def e_out(p): return 1 - (1 - p) ** 3
def e_in(p): return p ** 3
def e_io(p): return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2
def e_out5(p): return 1 - (1 - p) ** 5
def e_io5(p): return 16 * p ** 5 if p < .5 else 1 - (-2 * p + 2) ** 5 / 2
def e_back(p, s=1.9):
    p -= 1; return p * p * ((s + 1) * p + s) + 1
def e_elastic(p):
    if p <= 0: return 0.0
    if p >= 1: return 1.0
    return 2 ** (-10 * p) * math.sin((p * 10 - 0.75) * (2 * math.pi) / 3) + 1
def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)

def kf(t, keys):
    """keys: [(time, value, ease_into_this_key)] ; value scalar or tuple."""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0, _), (t1, v1, e) in zip(keys, keys[1:]):
        if t <= t1:
            p = e(prog(t, t0, t1))
            if isinstance(v0, (tuple, list)):
                return tuple(a + (b - a) * p for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * p
    return keys[-1][1]

# ---------- image utils ----------
def to_premul(rgba_u8):
    a = rgba_u8[..., 3:4].astype(np.float32) / 255.0
    rgb_ = rgba_u8[..., :3].astype(np.float32) / 255.0
    return np.concatenate([rgb_ * a, a], -1)

def pil_premul(im):
    return to_premul(np.asarray(im.convert('RGBA')))

def rounded_mask(w, h, r, ss=3):
    m = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)

def cover(img, w, h, fx=0.5, fy=0.5):
    """PIL cover-crop."""
    iw, ih = img.size
    s = max(w / iw, h / ih)
    nw, nh = int(math.ceil(iw * s)), int(math.ceil(ih * s))
    im = img.resize((nw, nh), Image.LANCZOS)
    x = int((nw - w) * fx); y = int((nh - h) * fy)
    return im.crop((x, y, x + w, y + h))

def add_shadow(im, blur=28, off=(0, 18), alpha=0.35, pad=60, color=(0, 20, 12)):
    """Return new RGBA with baked soft shadow; also returns pad offset."""
    w, h = im.size
    out = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: int(v * alpha))
    sh = Image.new('RGBA', out.size, color + (0,))
    sm = Image.new('L', out.size, 0); sm.paste(a, (pad + off[0], pad + off[1]))
    sm = sm.filter(ImageFilter.GaussianBlur(blur))
    sh.putalpha(sm)
    out = Image.alpha_composite(out, sh)
    out.alpha_composite(im, (pad, pad))
    return out, pad

# ---------- 3D projection / warping ----------
def rotm(rx, ry, rz):
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def quad3d(w, h, cx, cy, s=1.0, rx=0, ry=0, rz=0, ax=0.5, ay=0.5, f=2400, z=0):
    pts = np.array([[-ax * w, -ay * h, 0], [(1 - ax) * w, -ay * h, 0],
                    [(1 - ax) * w, (1 - ay) * h, 0], [-ax * w, (1 - ay) * h, 0]], np.float64) * s
    p = pts @ rotm(rx, ry, rz).T
    zz = p[:, 2] + z
    k = f / np.maximum(f + zz, 1)
    return np.stack([cx + p[:, 0] * k, cy + p[:, 1] * k], 1)

def quad_scale(q, w, h):
    sx = max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3])) / w
    sy = max(np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1])) / h
    return max(sx, sy)

def warp(canvas, layer, q, opacity=1.0):
    """Composite premultiplied RGBA float layer onto float RGB canvas, mapped to quad q."""
    if opacity <= 0.003: return
    h, w = layer.shape[:2]
    x0 = int(max(0, math.floor(q[:, 0].min()))); x1 = int(min(canvas.shape[1], math.ceil(q[:, 0].max()) + 1))
    y0 = int(max(0, math.floor(q[:, 1].min()))); y1 = int(min(canvas.shape[0], math.ceil(q[:, 1].max()) + 1))
    if x1 <= x0 or y1 <= y0: return
    src = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    sc = quad_scale(q, w, h)
    if sc < 0.75:
        f = max(sc * 1.25, 0.02)
        nw, nh = max(2, int(w * f)), max(2, int(h * f))
        layer = cv2.resize(layer, (nw, nh), interpolation=cv2.INTER_AREA)
        src = np.array([[0, 0], [nw, 0], [nw, nh], [0, nh]], np.float32)
    dst = (q - np.array([x0, y0])).astype(np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(layer, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    if opacity < 1: out = out * opacity
    reg = canvas[y0:y1, x0:x1]
    reg *= (1 - out[..., 3:4]); reg += out[..., :3]

def paste(canvas, layer, cx, cy, s=1.0, rot=0.0, opacity=1.0, rx=0, ry=0):
    h, w = layer.shape[:2]
    warp(canvas, layer, quad3d(w, h, cx, cy, s, rx, ry, rot), opacity)

def shadow_quad(canvas, q, blur=40, alpha=0.35, off=(0, 30), color=(0.0, 0.08, 0.05)):
    sc = 0.25
    m = np.zeros((int(H * sc), int(W * sc)), np.float32)
    pts = ((q + np.array(off)) * sc * 16).astype(np.int32)
    cv2.fillConvexPoly(m, pts, 1.0, lineType=cv2.LINE_AA, shift=4)
    k = int(blur * sc) * 2 + 1
    m = cv2.GaussianBlur(m, (k, k), 0)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)[..., None] * alpha
    canvas *= (1 - m); canvas += m * np.array(color, np.float32)

# ---------- emoji + text ----------
@functools.lru_cache(maxsize=128)
def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
    bb = im.getbbox() or (0, 0, 1, 1)
    im = im.crop(bb)
    s = size / max(im.size)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)

def text_size(txt, fnt):
    bb = fnt.getbbox(txt)
    return bb[2] - bb[0], bb

def draw_text(im, xy, txt, fnt, fill, anchor='la'):
    ImageDraw.Draw(im).text(xy, txt, font=fnt, fill=fill, anchor=anchor)

# ---------- backgrounds ----------
@functools.lru_cache(maxsize=4)
def grad_bg(kind):
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    x = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
    if kind == 'tour':
        c0 = np.array(CREAM, np.float32) / 255; c1 = np.array(rgb('DDEFC7'), np.float32) / 255
        c2 = np.array(rgb('0E6644'), np.float32) / 255; c3 = np.array(GREEN, np.float32) / 255
        p = y
        a = np.clip(p / 0.42, 0, 1); b = np.clip((p - 0.42) / 0.33, 0, 1); c = np.clip((p - 0.75) / 0.25, 0, 1)
        col = c0 * (1 - a) + c1 * a
        col = col * (1 - b) + c2 * b
        col = col * (1 - c) + c3 * c
        return np.broadcast_to(col, (H, W, 3)).copy()
    if kind == 'dark':
        d = np.sqrt(((x - 0.5) * 1.0) ** 2 + ((y - 0.42) * 0.62) ** 2)
        p = np.clip(d / 0.62, 0, 1) ** 1.2
        c0 = np.array(rgb('137352'), np.float32) / 255; c1 = np.array(GREEN_D, np.float32) / 255
        return (c0 * (1 - p) + c1 * p).astype(np.float32)
    raise ValueError(kind)

def blobs(canvas, t, specs, sc=0.125):
    """specs: [(cx, cy, r, color(0-1), alpha, phase)] drawn soft, drifting."""
    h, w = int(H * sc), int(W * sc)
    acc = np.zeros((h, w, 3), np.float32); am = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for cx, cy, r, col, al, ph in specs:
        cx2 = (cx + 40 * math.sin(t * 0.7 + ph)) * sc; cy2 = (cy + 30 * math.cos(t * 0.55 + ph * 1.3)) * sc
        d = np.sqrt((xx - cx2) ** 2 + (yy - cy2) ** 2) / (r * sc)
        m = np.clip(1 - d, 0, 1); m = (m * m * (3 - 2 * m)) * al
        acc += m[..., None] * np.array(col, np.float32); am += m
    acc = cv2.resize(acc, (W, H)); am = cv2.resize(am, (W, H))[..., None]
    am = np.clip(am, 0, 1)
    canvas *= (1 - am); canvas += np.clip(acc, 0, 1)

# ---------- post effects ----------
def zoom_blur(img, amount, cx=W / 2, cy=H / 2, n=9):
    if amount <= 0.002: return img
    acc = np.zeros_like(img)
    for i in range(n):
        s = 1 + amount * i / (n - 1)
        M = np.array([[s, 0, cx * (1 - s)], [0, s, cy * (1 - s)]], np.float32)
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / n

def motion_blur(img, dx, dy):
    L = int(max(abs(dx), abs(dy)))
    if L < 2: return img
    k = np.zeros((L * 2 + 1, L * 2 + 1), np.float32)
    cv2.line(k, (L - int(dx / 2), L - int(dy / 2)), (L + int(dx / 2), L + int(dy / 2)), 1.0, 1)
    k /= k.sum()
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_REFLECT)

def gblur(img, sigma):
    if sigma < 0.3: return img
    return cv2.GaussianBlur(img, (0, 0), sigma)

def shift_img(img, dx, dy, s=1.0, cx=W / 2, cy=H / 2):
    M = np.array([[s, 0, cx * (1 - s) + dx], [0, s, cy * (1 - s) + dy]], np.float32)
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT)
