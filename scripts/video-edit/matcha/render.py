"""Matcha UGC re-edit: zooms, transitions, B-roll inserts, motion graphics and new captions.

Usage: python3 render.py <work_dir> <assets_dir> <source.mov> <out_video_noaudio.mp4> [--frames 0,90,300] [--check]

Every visual decision lives in the EDIT TIMELINE section below; the rest is the engine.
"""
import json, math, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WORK, ASSETS, SRC, OUT = sys.argv[1:5]
ARGS = sys.argv[5:]
W, H, FPS = 1080, 1920, 30
SRC_LAST = 1248            # last source frame used (41.6 s): she has just left the frame
DUR = 43.4                 # 41.6 s of footage + end card
NF = int(round(DUR * FPS))
SUB_BAND_BOTTOM = 300      # burned-in subtitles live in source rows ~205-262: never show rows above this

FONT = lambda n: os.path.join(ASSETS, "fonts", n)
F_BLACK = FONT("Montserrat-Black.ttf")
F_XBOLD = FONT("Montserrat-ExtraBold.ttf")
F_ANTON = FONT("Anton.ttf")

LIME = (190, 245, 60)
DEEP = (10, 52, 26)
WHITE = (255, 255, 255)
INK = (14, 22, 12)

# ----------------------------------------------------------------------------------------------
# easing
# ----------------------------------------------------------------------------------------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def e_out3(p): p = clamp(p); return 1 - (1 - p) ** 3
def e_in3(p): p = clamp(p); return p ** 3
def e_io(p): p = clamp(p); return p * p * (3 - 2 * p)
def e_back(p, s=1.9):
    p = clamp(p) - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2
def lerp(a, b, p): return a + (b - a) * p

# ----------------------------------------------------------------------------------------------
# EDIT TIMELINE
# ----------------------------------------------------------------------------------------------
CUTS = [  # (time of first frame of the new shot, transition)
    (2.733, "whip_l"), (4.633, "zoom"), (9.467, "flash_glitch"), (12.567, "whip_u"),
    (15.100, "spin"), (19.267, "glitch"), (22.133, "whip_r"), (26.533, "zoom"),
    (29.300, "flash"), (35.933, "whip_l"),
]
# extra transitions around inserts (not camera cuts)
INSERT_CUTS = [(5.30, "zoom"), (6.15, "whip_l"), (8.40, "flash")]

SHOT_BOUNDS = [0.0] + [c for c, _ in CUTS] + [99.0]
SHOT_ZOOM = [(1.22, 1.28), (1.24, 1.32), (1.22, 1.30), (1.20, 1.27), (1.27, 1.20), (1.20, 1.28),
             (1.24, 1.31), (1.22, 1.30), (1.22, 1.28), (1.20, 1.32), (1.25, 1.33)]

PUNCHES = [  # (t0, t1, extra zoom, focus point in source px or None, focus weight)
    (1.68, 2.70, 0.20, None, 0),          # ¿sabes por qué?
    (3.94, 4.44, 0.14, None, 0),          # cualquiera
    (7.84, 8.40, 0.10, None, 0),          # mucho más
    (10.18, 10.80, 0.16, None, 0),        # cafeína
    (11.34, 12.08, 0.12, None, 0),        # súper diferente
    (13.66, 14.80, 0.16, None, 0),        # tan fan de la cafeína
    (16.32, 17.05, 0.20, None, 0),        # súper suavecito
    (20.32, 21.30, 0.16, None, 0),        # no sabe a pasto
    (22.98, 24.20, 0.22, (350, 900), 0.6),    # comprueba 100%  -> toward the can
    (24.66, 25.40, 0.10, None, 0),        # originales
    (27.30, 28.10, 0.12, (480, 1160), 0.5),   # súper vivo -> toward the powder
    (28.12, 29.00, 0.12, None, 0),        # cero opaco
    (29.76, 30.70, 0.16, None, 0),        # antioxidantes
    (32.76, 33.20, 0.10, None, 0),        # algo rico
    (34.30, 35.50, 0.12, None, 0),        # claramente lo preparan
    (36.36, 37.10, 0.12, None, 0),        # todos prefieren
    (38.14, 39.05, 0.22, (330, 880), 0.6),    # Laboratorios Outlet -> toward the can
    (40.16, 40.70, 0.16, None, 0),        # claramente
]
SHAKES = [(17.95, 18.80, 22.0)]           # "los otros me dejan como..." (caffeine jitters)

# B-roll: powder close-up taken from the moment she opens the can (framed so the can sits above the captions)
BROLL = dict(t0=5.30, t1=6.15, src_t=27.0, center=(470, 1200), z0=1.90, z1=2.05)

# Nothing drawn may touch her head/face or the product (the can). The head never goes below
# HEAD_LIMIT (zooms are capped), which keeps the lower band free for the caption stack.
HEAD_LIMIT = 1130
HEAD_PAD, CAN_PAD = 34, 24       # clearance used when placing elements (output px)
CHECK_PAD = 6                    # anything closer than this counts as touching in --check
# kinetic insert "HOJA COMPLETA"
INSERT = dict(t0=8.40, t1=9.467)

SECTIONS = [  # number, slam time, chip text, section end
    (1, 2.84, "NO ES UN TÉ CUALQUIERA", 4.44),
    (2, 4.44, "ES TÉ VERDE EN POLVO", 8.30),
    (3, 9.50, "CAFEÍNA… PERO DIFERENTE", 18.84),
    (4, 18.84, "NO SABE A PASTO", 21.88),
    (5, 21.88, "COLOR 100% ORIGINAL", 29.06),
    (6, 29.30, "TIENE ANTIOXIDANTES", 35.30),
]

STICKERS = [  # (t0, dur, emoji name(s), preferred x, preferred y, size) — moved if that spot is taken
    (1.10, 0.95, ["fire"], 900, 800, 180),
    (2.36, 0.40, ["eyes"], 180, 800, 160),
    (3.94, 0.50, ["x"], 880, 1110, 150),
    (5.88, 0.27, ["matcha"], 870, 1100, 190),
    (10.18, 0.80, ["zap"], 880, 1100, 180),
    (11.64, 0.80, ["sparkles"], 190, 1100, 170),
    (13.84, 1.00, ["coffee", "x"], 870, 1090, 180),
    (16.54, 0.55, ["relieved"], 880, 1100, 170),
    (18.12, 0.72, ["dizzy"], 860, 600, 210),
    (20.88, 0.95, ["herb", "x"], 190, 1090, 180),
    (23.36, 0.85, ["100"], 870, 1090, 190),
    (24.74, 0.68, ["check"], 190, 1100, 160),
    (27.60, 0.52, ["greenheart"], 880, 1100, 170),
    (28.66, 0.40, ["sparkles"], 190, 1100, 160),
    (29.96, 0.76, ["muscle"], 880, 1100, 180),
    (32.92, 0.30, ["hearteyes"], 880, 1100, 160),
    (34.04, 0.26, ["greenheart"], 190, 1100, 150),
    (36.36, 0.80, ["trophy"], 880, 1100, 170),
    (40.16, 0.55, ["starstruck"], 880, 1100, 170),
]

KEYWORDS = {"matcha", "moda", "qué", "primero", "cualquiera", "segundo", "polvo", "completa", "hoja",
            "tercero", "cafeína", "diferente", "fan", "suavecito", "cuarto", "pasto", "quinto",
            "color", "100%", "originales", "vivo", "opaco", "sexto", "antioxidantes", "rico", "bien",
            "todos", "laboratorios", "outlet", "claramente", "muestro"}
SOLO = {"primero", "segundo", "tercero", "cuarto", "quinto", "sexto", "100%", "antioxidantes", "originales"}

END_T = SRC_LAST / FPS     # 41.6

# SFX cue sheet consumed by mix_audio.py (time, file, gain dB)
SFX = [
    (0.00, "impact", -6), (0.02, "whoosh3", -10), (0.45, "pop1", -12), (1.10, "pop2", -14),
    (2.36, "pop3", -15), (2.55, "whoosh1", -9), (2.84, "impact", -13), (2.84, "click", -10),
    (3.40, "whoosh3", -16), (3.94, "pop1", -15), (4.44, "impact", -13), (4.44, "click", -10),
    (4.50, "whoosh2", -11), (5.00, "whoosh3", -16), (5.18, "whoosh1", -10), (5.88, "pop2", -15),
    (6.02, "whoosh3", -11), (8.30, "whoosh1", -10), (8.45, "shimmer", -12), (8.62, "pop1", -12),
    (9.40, "glitch", -14), (9.47, "impact", -10), (9.50, "click", -10), (10.05, "whoosh3", -16),
    (10.18, "pop3", -15), (11.64, "pop1", -15), (12.43, "whoosh2", -11), (13.84, "pop2", -14),
    (14.98, "whoosh1", -10), (16.54, "pop3", -15), (17.95, "wobble", -12), (18.12, "pop1", -14),
    (18.84, "impact", -13), (18.84, "click", -10), (19.20, "glitch", -13), (19.40, "whoosh3", -16),
    (20.88, "pop2", -14), (21.88, "impact", -13), (21.88, "click", -10), (22.00, "whoosh2", -11),
    (22.45, "whoosh3", -16), (23.36, "ding", -13), (24.74, "pop1", -15), (26.40, "whoosh1", -10),
    (27.30, "shimmer", -11), (27.60, "pop3", -15), (28.66, "pop2", -16), (29.28, "impact", -11),
    (29.30, "click", -10), (29.60, "whoosh3", -16), (29.96, "pop1", -14),
    (32.92, "pop2", -16), (34.04, "pop3", -16), (34.73, "riser", -12), (35.80, "whoosh2", -9),
    (35.93, "impact", -9), (36.36, "pop1", -15), (37.30, "whoosh3", -12), (38.14, "ding", -12),
    (38.20, "shimmer", -12), (40.16, "pop2", -15), (41.10, "whoosh2", -10), (41.60, "impact", -8),
    (41.65, "shimmer", -11), (41.85, "pop1", -12), (42.15, "pop2", -12), (42.45, "ding_low", -12),
]

# ----------------------------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------------------------
WORDS = json.load(open(os.path.join(WORK, "words.json")))
FACES = json.load(open(os.path.join(WORK, "faces.json")))
CANS = {int(k): v for k, v in json.load(open(os.path.join(WORK, "cans.json"))).items()}  # x0,y0,x1,y1,kind

def norm(w): return w.lower().strip(",.¿?¡!…").replace("...", "")

def build_groups():
    groups, cur = [], []
    for i, w in enumerate(WORDS):
        n = norm(w["w"])
        start_new = False
        if cur:
            prev = cur[-1]
            text_len = sum(len(x["w"]) for x in cur) + len(w["w"])
            if prev["w"].endswith((",", ".", "?", "…", "...")) or len(cur) >= 3 or text_len > 15 \
                    or w["s"] - prev["e"] > 0.35 or n in SOLO or norm(prev["w"]) in SOLO \
                    or (w["w"][0].isupper() and n not in ("laboratorios", "outlet")):
                start_new = True
        if start_new:
            groups.append(cur); cur = []
        cur.append(w)
    groups.append(cur)
    out = []
    for gi, g in enumerate(groups):
        nxt = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else g[-1]["e"] + 0.6
        end = nxt if nxt - g[-1]["e"] < 0.6 else g[-1]["e"] + 0.3
        out.append(dict(words=g, s=g[0]["s"], e=end))
    return out

GROUPS = build_groups()

def shot_index(t):
    for k in range(len(SHOT_BOUNDS) - 1):
        if SHOT_BOUNDS[k] <= t < SHOT_BOUNDS[k + 1]: return k
    return len(SHOT_BOUNDS) - 2

# ----------------------------------------------------------------------------------------------
# sprites
# ----------------------------------------------------------------------------------------------
class Sprite:
    def __init__(self, pil):
        a = np.asarray(pil.convert("RGBA")).astype(np.float32) / 255.0
        a[..., :3] *= a[..., 3:4]
        self.img = a
        self.h, self.w = a.shape[:2]
        ys, xs = np.nonzero(a[..., 3] > 0.6)          # visible content, without the soft shadow
        self.content = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else (0, 0, self.w, self.h)

def sprite_matrix(spr, cx, cy, scale, rot):
    M = cv2.getRotationMatrix2D((spr.w / 2, spr.h / 2), rot, scale)
    M[0, 2] += cx - spr.w / 2; M[1, 2] += cy - spr.h / 2
    return M

def box(spr, cx, cy, scale=1.0, rot=0.0):
    """Axis-aligned bounds of the sprite's visible content once placed."""
    x0, y0, x1, y1 = spr.content
    c = sprite_matrix(spr, cx, cy, scale, rot) @ np.array([[x0, x1, x0, x1], [y0, y0, y1, y1], [1, 1, 1, 1]], np.float64)
    return (c[0].min(), c[1].min(), c[0].max(), c[1].max())

def hits(b, head, pad):
    """True when box b comes within pad px of the head ellipse."""
    if b is None or head is None: return False
    hx, hy, a, bb = head
    a += pad; bb += pad
    px, py = clamp(hx, b[0], b[2]), clamp(hy, b[1], b[3])
    return ((px - hx) / a) ** 2 + ((py - hy) / bb) ** 2 < 1.0

RECORD = None    # when a list, draw() only records (tag, content box) — used by the layout check

def draw(frame, spr, cx, cy, scale=1.0, rot=0.0, alpha=1.0, tag="graphic"):
    if alpha <= 0.004 or scale <= 0.02: return
    if RECORD is not None:
        RECORD.append((tag, box(spr, cx, cy, scale, rot))); return
    M = sprite_matrix(spr, cx, cy, scale, rot)
    c = M @ np.array([[0, spr.w, 0, spr.w], [0, 0, spr.h, spr.h], [1, 1, 1, 1]], np.float64)
    x0, x1 = int(max(0, math.floor(c[0].min()))), int(min(W, math.ceil(c[0].max())))
    y0, y1 = int(max(0, math.floor(c[1].min()))), int(min(H, math.ceil(c[1].max())))
    if x1 <= x0 or y1 <= y0: return
    M[0, 2] -= x0; M[1, 2] -= y0
    wp = cv2.warpAffine(spr.img, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    if alpha < 1: wp *= alpha
    roi = frame[y0:y1, x0:x1]
    roi *= 1.0 - wp[..., 3:4]
    roi += wp[..., :3]

def text_img(text, font, size, fill=WHITE, stroke=0, stroke_fill=INK, shadow=0.55, box=None,
             pad=(22, 10), radius=18, margin=30):
    f = ImageFont.truetype(font, size)
    l, t, r, b = f.getbbox(text, stroke_width=stroke)
    tw, th = r - l, b - t
    bw, bh = tw + (2 * pad[0] if box else 0), th + (2 * pad[1] if box else 0)
    Wc, Hc = bw + 2 * margin, bh + 2 * margin
    img = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    ox = margin + (pad[0] if box else 0) - l
    oy = margin + (pad[1] if box else 0) - t
    if shadow:
        sh = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
        if box:
            d.rounded_rectangle([margin, margin + 8, margin + bw, margin + bh + 8], radius, fill=(0, 0, 0, int(255 * shadow)))
        else:
            d.text((ox, oy + 7), text, font=f, fill=(0, 0, 0, int(255 * shadow)), stroke_width=stroke,
                   stroke_fill=(0, 0, 0, int(255 * shadow)))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(7)))
    d = ImageDraw.Draw(img)
    if box:
        d.rounded_rectangle([margin, margin, margin + bw, margin + bh], radius, fill=box)
    d.text((ox, oy), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return img, (tw if not box else bw), (th if not box else bh)

EMOJI = {}
def emoji(name, size):
    key = (name, size)
    if key not in EMOJI:
        im = Image.open(os.path.join(ASSETS, "emoji", name + ".png")).convert("RGBA")
        s = size / max(im.size)
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
        # soft drop shadow for depth
        pad = 24
        c = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
        a = im.split()[3].point(lambda v: int(v * 0.45))
        sh.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (pad, pad + 8), a)
        c = Image.alpha_composite(c, sh.filter(ImageFilter.GaussianBlur(6)))
        c.alpha_composite(im, (pad, pad))
        EMOJI[key] = c
    return EMOJI[key]

def combo(names, size):
    base = emoji(names[0], size)
    if len(names) == 1: return Sprite(base)
    over = emoji(names[1], int(size * 0.62))
    c = base.copy()
    c.alpha_composite(over, (c.width - over.width, c.height - over.height))
    return Sprite(c)

# ----------------------------------------------------------------------------------------------
# camera
# ----------------------------------------------------------------------------------------------
def punch_env(t, p):
    t0, t1 = p[0], p[1]
    if t < t0 or shot_index(t) != shot_index(t0): return 0.0
    if t < t1: return e_back((t - t0) / 0.13, 1.6)
    return 1.0 - e_io((t - t1) / 0.22)

def camera(t, fidx):
    k = shot_index(t)
    a, b = SHOT_BOUNDS[k], min(SHOT_BOUNDS[k + 1], END_T)
    z0, z1 = SHOT_ZOOM[k]
    z = lerp(z0, z1, e_io((t - a) / max(0.01, b - a)))
    if t < 0.5:   # opening punch-out
        z += (1.80 - z) * (1 - e_out3(t / 0.42))
    fx, fy, fw = FACES[min(fidx, len(FACES) - 1)]
    tx, ty = fx, fy
    wsum = 0.0; fxs = fys = 0.0
    for p in PUNCHES:
        e = punch_env(t, p)
        if e <= 0: continue
        z += p[2] * e
        if p[3] is not None:
            w = p[4] * clamp(e)
            fxs += p[3][0] * w; fys += p[3][1] * w; wsum += w
    z = max(1.20, z)

    def framing(z):
        cy_face = ty + 192.0 / z       # face lands at 40 % of the frame height
        cx, cy = tx, cy_face
        if wsum > 0:                   # pull the framing toward the punch focus point
            wb = min(wsum, 0.95)
            cx = lerp(tx, fxs / wsum, wb)
            cy = lerp(cy_face, fys / wsum, wb)
        return cx, cy

    def head_bottom(z):
        cx, cy = clamp_center(z, *framing(z), 0)
        return (fy + 0.62 * fw - cy) * z + H / 2

    if head_bottom(z) > HEAD_LIMIT:    # cap the zoom so the head stays out of the text band
        lo_z, hi_z = 1.20, z
        for _ in range(18):
            mid = (lo_z + hi_z) / 2
            if head_bottom(mid) <= HEAD_LIMIT: lo_z = mid
            else: hi_z = mid
        z = lo_z
    cx, cy = framing(z)
    dx = dy = rot = 0.0
    for s0, s1, amp in SHAKES:
        if s0 <= t < s1:
            env = math.sin(math.pi * (t - s0) / (s1 - s0))
            dx += amp * env * (math.sin(t * 71.0) + 0.6 * math.sin(t * 113.0 + 1.3))
            dy += amp * env * (math.sin(t * 89.0 + 0.7) + 0.5 * math.sin(t * 131.0))
            rot += 2.2 * env * math.sin(t * 57.0)
    return z, cx, cy, rot, dx, dy

def clamp_center(z, cx, cy, rot):
    margin = abs(math.sin(math.radians(rot))) * W * 0.5
    hw, hh = W / 2 / z, H / 2 / z
    cx = clamp(cx, hw, W - hw)
    lo = SUB_BAND_BOTTOM + hh + margin / z
    cy = clamp(cy, lo, max(lo, H - hh))
    return cx, cy

def view(t, i):
    """Resting camera for output frame i (no transition effects): source frame index and framing."""
    if BROLL["t0"] <= t < BROLL["t1"]:
        q = (t - BROLL["t0"]) / (BROLL["t1"] - BROLL["t0"])
        k = int(round(BROLL["src_t"] * FPS)) + int(round((t - BROLL["t0"]) * FPS))
        return k, lerp(BROLL["z0"], BROLL["z1"], q), BROLL["center"][0], BROLL["center"][1] + 20 * q, 0.0, 0.0, 0.0
    z, cx, cy, rot, dx, dy = camera(t, i)
    return i, z, cx, cy, rot, dx, dy

def subjects(i):
    """Head ellipse (cx, cy, a, b) and can box (x0, y0, x1, y1, kind) in output px for frame i."""
    t = i / FPS
    if t >= END_T or INSERT["t0"] <= t < INSERT["t1"]: return None, None
    k, z, cx, cy, rot, dx, dy = view(t, i)
    cx, cy = clamp_center(z, cx, cy, rot)
    out = lambda x, y: ((x - cx) * z + W / 2 + dx, (y - cy) * z + H / 2 + dy)
    fx, fy, fw = FACES[min(k, len(FACES) - 1)]
    hx, hy = out(fx, fy - 0.08 * fw)
    head = (hx, hy, 0.62 * fw * z, 0.70 * fw * z)
    can = None
    if k in CANS:
        c = CANS[k]
        (x0, y0), (x1, y1) = out(c[0], c[1]), out(c[2], c[3])
        can = (x0, y0, x1, y1, c[4])
    return head, can

def warp_src(src, z, cx, cy, rot=0.0, dx=0.0, dy=0.0, border=cv2.BORDER_REFLECT101):
    cx, cy = clamp_center(z, cx, cy, rot)
    M = cv2.getRotationMatrix2D((cx, cy), rot, z)
    M[0, 2] += W / 2 + dx - cx; M[1, 2] += H / 2 + dy - cy
    return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=border)

# ----------------------------------------------------------------------------------------------
# look
# ----------------------------------------------------------------------------------------------
_x = np.arange(256) / 255.0
_s = 1 / (1 + np.exp(-(_x - 0.5) * 6.0)); _s = (_s - _s.min()) / (_s.max() - _s.min())
_curve = 0.78 * _x + 0.22 * _s
LUT_R = np.clip((_curve * 1.02 + 0.004) * 255, 0, 255).astype(np.uint8)
LUT_G = np.clip((_curve * 1.01 + 0.002) * 255, 0, 255).astype(np.uint8)
LUT_B = np.clip((_curve * 0.98) * 255, 0, 255).astype(np.uint8)
SAT_LUT = np.clip(np.arange(256) * 1.14, 0, 255).astype(np.uint8)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1.0 - 0.28 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2, 0, 1) ** 1.6)[..., None]
del yy, xx

def grade(img):
    r, g, b = cv2.split(img)
    img = cv2.merge([cv2.LUT(r, LUT_R), cv2.LUT(g, LUT_G), cv2.LUT(b, LUT_B)])
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hsv[..., 1] = cv2.LUT(hsv[..., 1], SAT_LUT)
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    bl = cv2.GaussianBlur(img, (0, 0), 1.6)
    return cv2.addWeighted(img, 1.45, bl, -0.45, 0)

# ----------------------------------------------------------------------------------------------
# transitions
# ----------------------------------------------------------------------------------------------
TD = 4 / FPS
ALL_CUTS = sorted(CUTS + INSERT_CUTS)

def transition_at(t):
    """Return (kind, phase, p) where phase is 'out' (before cut) or 'in'. p in (0,1] = intensity."""
    for c, kind in ALL_CUTS:
        if c - TD - 1e-6 <= t < c:
            return kind, "out", (t - (c - TD)) / TD + 0.25
        if c <= t < c + TD:
            return kind, "in", 1.0 - (t - c) / TD
    return None, None, 0.0

def motion_blur(img, length, vertical=False):
    L = int(length / 4)
    if L < 2: return img
    sm = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    sm = cv2.blur(sm, (1, L) if vertical else (L, 1), borderType=cv2.BORDER_REFLECT)
    return cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR)

def zoom_blur(img, strength):
    if strength < 0.05: return img
    sw, sh = W // 3, H // 3
    sm = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA).astype(np.float32)
    acc = sm.copy()
    for k in range(1, 8):
        M = cv2.getRotationMatrix2D((sw / 2, sh * 0.45), 0, 1 + strength * 0.16 * k / 7)
        acc += cv2.warpAffine(sm, M, (sw, sh), borderMode=cv2.BORDER_REFLECT)
    bl = cv2.resize((acc / 8).astype(np.uint8), (W, H), interpolation=cv2.INTER_LINEAR)
    a = clamp(strength * 1.4)
    return cv2.addWeighted(img, 1 - a, bl, a, 0)

def rgb_glitch(img, amt, seed):
    rng = np.random.default_rng(seed)
    d = int(10 + 26 * amt)
    out = img.copy()
    out[..., 0] = np.roll(img[..., 0], d, axis=1)
    out[..., 2] = np.roll(img[..., 2], -d, axis=1)
    for _ in range(int(3 + 6 * amt)):
        y0 = int(rng.integers(0, H - 60)); hgt = int(rng.integers(20, 140))
        out[y0:y0 + hgt] = np.roll(out[y0:y0 + hgt], int(rng.integers(-90, 90) * amt), axis=1)
    return out

# ----------------------------------------------------------------------------------------------
# source frames
# ----------------------------------------------------------------------------------------------
def decoder():
    cmd = ["ffmpeg", "-v", "error", "-i", SRC, "-vf", "scale=in_color_matrix=bt709:in_range=tv,format=rgb24",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)
    n = W * H * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n: break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    p.wait()

broll_idx0 = int(round(BROLL["src_t"] * FPS))
broll_n = int(math.ceil((BROLL["t1"] - BROLL["t0"]) * FPS)) + 2
NEEDED = set(range(broll_idx0, broll_idx0 + broll_n)) | {915, SRC_LAST}
STORE = {}
for i, fr in enumerate(decoder()):
    if i in NEEDED: STORE[i] = fr.copy()
print("stored", len(STORE), "frames", flush=True)

# ----------------------------------------------------------------------------------------------
# static sprites
# ----------------------------------------------------------------------------------------------
def make_number(n):
    lab, lw, lh = text_img("RAZÓN", F_BLACK, 70, WHITE, stroke=9, stroke_fill=INK)
    num, nw, nh = text_img(f"#{n}", F_ANTON, 330, LIME, stroke=14, stroke_fill=DEEP)
    c = Image.new("RGBA", (max(lab.width, num.width), lab.height + num.height - 70), (0, 0, 0, 0))
    c.alpha_composite(num, ((c.width - num.width) // 2, lab.height - 70))
    c.alpha_composite(lab, ((c.width - lab.width) // 2, 0))
    return Sprite(c)

def make_chip(n, text):
    f = ImageFont.truetype(F_XBOLD, 46)
    l, t, r, b = f.getbbox(text)
    hgt, circ = 112, 88
    wid = 14 + circ + 22 + (r - l) + 40
    m = 30
    img = Image.new("RGBA", (wid + 2 * m, hgt + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([m, m + 10, m + wid, m + hgt + 10], hgt // 2, fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([m, m, m + wid, m + hgt], hgt // 2, fill=DEEP + (240,), outline=LIME + (255,), width=4)
    cx0 = m + 12
    d.ellipse([cx0, m + (hgt - circ) // 2, cx0 + circ, m + (hgt + circ) // 2], fill=LIME + (255,))
    fn = ImageFont.truetype(F_ANTON, 62)
    d.text((cx0 + circ / 2, m + hgt / 2 + 2), str(n), font=fn, fill=INK, anchor="mm")
    d.text((cx0 + circ + 22 - l, m + (hgt - (b - t)) / 2 - t), text, font=f, fill=WHITE)
    return Sprite(img)

NUMBERS = {n: make_number(n) for n, *_ in SECTIONS}
CHIPS = {n: make_chip(n, txt) for n, _, txt, _ in SECTIONS}

HOOK_A = Sprite(text_img("6 RAZONES", F_ANTON, 210, LIME, stroke=14, stroke_fill=DEEP)[0])
HOOK_B = Sprite(text_img("PARA TOMAR MATCHA", F_BLACK, 66, INK, box=WHITE + (255,), pad=(26, 12), radius=20)[0])

INS_A = Sprite(text_img("HOJA", F_ANTON, 300, LIME, stroke=14, stroke_fill=DEEP)[0])
INS_B = Sprite(text_img("COMPLETA", F_BLACK, 120, WHITE, stroke=12, stroke_fill=INK)[0])
LEAF = Sprite(emoji("herb", 300))
SPARK = Sprite(emoji("sparkles", 160))

BRAND_A = Sprite(text_img("TÉ MATCHA", F_ANTON, 150, LIME, stroke=12, stroke_fill=DEEP)[0])
BRAND_B = Sprite(text_img("LABORATORIOS OUTLET", F_BLACK, 56, WHITE, box=DEEP + (245,), pad=(28, 14), radius=22)[0])

def make_can_card():
    fr = STORE[915]
    crop = Image.fromarray(fr[742:1092, 196:456])           # can held to camera at 30.5 s
    crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(3, 90, 2))
    bw = 16; m = 40
    card = Image.new("RGBA", (crop.width + 2 * bw + 2 * m, crop.height + 2 * bw + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([m, m + 18, card.width - m, card.height - m + 18], 44, fill=(0, 0, 0, 150))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(card).rounded_rectangle([m, m, card.width - m, card.height - m], 44, fill=WHITE + (255,))
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, crop.width, crop.height], 32, fill=255)
    card.paste(crop, (m + bw, m + bw), mask)
    return Sprite(card)

CAN_CARD = make_can_card()
END_A = Sprite(text_img("TÉ MATCHA", F_ANTON, 190, LIME, stroke=14, stroke_fill=DEEP)[0])
END_B = Sprite(text_img("LABORATORIOS OUTLET", F_BLACK, 62, WHITE, stroke=8, stroke_fill=INK)[0])
END_C = Sprite(text_img("GRADO CEREMONIAL PREMIUM", F_XBOLD, 40, WHITE, box=(255, 255, 255, 46), pad=(26, 12), radius=30, shadow=0)[0])
END_D = Sprite(text_img("¡PRUÉBALO HOY!", F_BLACK, 72, INK, box=LIME + (255,), pad=(40, 18), radius=48)[0])
END_E = combo(["matcha"], 200)

def end_background():
    fr = STORE[SRC_LAST]
    img = warp_src(fr, 1.25, 540, 1100)
    img = cv2.GaussianBlur(img, (0, 0), 22).astype(np.float32) / 255.0
    tint = np.array([0.06, 0.24, 0.10], np.float32)
    img = img * 0.42 + tint * 0.30
    return np.clip(img, 0, 1)

END_BG = end_background()

# captions ------------------------------------------------------------------------------------
ORDINALS = {"primero", "segundo", "tercero", "cuarto", "quinto", "sexto"}
LINE_H = 112
CAP_CACHE = {}
def caption_layout(gi):
    if gi in CAP_CACHE: return CAP_CACHE[gi]
    g = GROUPS[gi]
    items = []
    for w in g["words"]:
        raw = w["w"].upper().rstrip(",.").replace("...", "…")
        kw = norm(w["w"]) in KEYWORDS
        if kw:
            img, tw, th = text_img(raw, F_BLACK, 84, INK, box=LIME + (255,), pad=(20, 8), radius=18, margin=30)
        else:
            img, tw, th = text_img(raw, F_BLACK, 84, WHITE, stroke=10, stroke_fill=INK, margin=30)
        items.append(dict(spr=Sprite(img), w=tw, h=th, kw=kw, s=w["s"]))
    gap = 22
    lines, cur, cw = [], [], 0
    for it in items:
        add = it["w"] + (gap if cur else 0)
        if cur and cw + add > 900:
            lines.append(cur); cur, cw = [], 0; add = it["w"]
        cur.append(it); cw += add
    lines.append(cur)
    for li, ln in enumerate(lines):
        tot = sum(it["w"] for it in ln) + gap * (len(ln) - 1)
        x = W / 2 - tot / 2
        for it in ln:
            it["cx"] = x + it["w"] / 2
            it["line"] = li
            x += it["w"] + gap
    for k, it in enumerate(items):
        it["rot"] = (-3 if k % 2 == 0 else 3) if it["kw"] else 0
    CAP_CACHE[gi] = items
    return items

def caption_hidden(gi, t):
    g = GROUPS[gi]
    if len(g["words"]) == 1 and norm(g["words"][0]["w"]) in ORDINALS: return True   # the "RAZÓN #N" slam says it
    return INSERT["t0"] <= t < INSERT["t1"] or t >= 40.95

def word_pose(it, t, top):
    sc = pop_scale(t, it["s"] - 0.02, 0.15, 2.2 if it["kw"] else 1.4)
    return it["cx"], top + LINE_H / 2 + it["line"] * LINE_H, sc, it["rot"]

# ----------------------------------------------------------------------------------------------
# frame composition
# ----------------------------------------------------------------------------------------------
def base_frame(t, i, src):
    kind, phase, p = transition_at(t)
    ez = 1.0; erot = 0.0; edx = edy = 0.0
    if kind in ("zoom",):
        ez = 1 + 0.55 * p ** 2
    elif kind == "spin":
        ez = 1 + 0.3 * p ** 2; erot = (22 if phase == "out" else -22) * p ** 2
    elif kind and kind.startswith("whip"):
        sgn = {"whip_l": -1, "whip_r": 1, "whip_u": -1}[kind]
        amt = 0.5 * p ** 2 * (1 if phase == "out" else -1) * sgn
        if kind == "whip_u": edy = amt * H * 0.6
        else: edx = amt * W

    k, z, cx, cy, rot, dx, dy = view(t, i)
    fr = src if k == i else STORE[k]
    img = warp_src(fr, z * ez, cx, cy, rot + erot, dx + edx, dy + edy)

    img = grade(img)
    if kind and kind.startswith("whip"):
        img = motion_blur(img, 340 * p ** 1.1, vertical=(kind == "whip_u"))
    elif kind in ("zoom", "spin"):
        img = zoom_blur(img, p)
    if kind in ("glitch", "flash_glitch") and p > 0.2:
        img = rgb_glitch(img, p, i)
    return img

def flash_alpha(t):
    a = 0.0
    for c, kind in ALL_CUTS:
        if "flash" in kind:
            d = (t - c) * FPS
            if -2.5 <= d < 4: a = max(a, [0.25, 0.6, 0.95, 0.6, 0.32, 0.12][int(math.floor(d)) + 2] if -2 <= d else 0.15)
    if 0 <= t < 0.12: a = max(a, 0.9 - t * 7)
    if 41.55 <= t < 41.8: a = max(a, 0.7 * (1 - (t - 41.55) / 0.25))
    return a

def pop_scale(t, t0, dur=0.16, over=1.7):
    return e_back((t - t0) / dur, over)

STK = {(t0, tuple(n)): combo(n, size) for t0, d, n, x, y, size in STICKERS}

# poses: (x, y, scale, rot, alpha) for each animated element at time t --------------------------
def hook_poses(t):
    out = e_in3((t - 2.62) / 0.16); sx = -out * 900; a = 1 - out * 0.3
    res = []
    if t >= 0.04:
        s = 1 + 0.6 * (1 - e_out3((t - 0.04) / 0.16)) if t < 0.2 else 1
        res.append((HOOK_A, 540 + sx, 1035, s, -4, a * clamp((t - 0.04) / 0.05)))
    if t >= 0.42: res.append((HOOK_B, 540 + sx, 1175, pop_scale(t, 0.42), 2, a))
    return res

def chip_pose(n, t, pos, run_start, chip_end):
    sc = e_back((t - run_start) / 0.28, 1.6) * (1 - e_in3((t - (chip_end - 0.16)) / 0.16))
    return pos[0], pos[1], sc, 0, 1

def slam_end(ts):
    """The slam lives while the ordinal word is spoken, so it is gone before the next caption."""
    w = [w for w in WORDS if norm(w["w"]) in ORDINALS and w["s"] <= ts + 0.3 and w["e"] > ts - 0.3]
    return max(ts + 0.45, (w[0]["e"] + 0.05) if w else ts + 0.75)

def slam_pose(t, ts, pos):
    p = t - ts; base = pos[2]; hold = slam_end(ts) - ts - 0.18
    if p < hold: return pos[0], pos[1], base * (1 + 0.45 * (1 - e_out3(p / 0.14))), -7, clamp(p / 0.05)
    q = e_in3((p - hold) / 0.18)
    return pos[0], pos[1], base * (1 - 0.8 * q), -7, 1 - q

def sticker_pose(t, t0, d, pos):
    s = pos[2] * pop_scale(t, t0, 0.18, 2.6) * (1 - e_in3((t - (t0 + d - 0.1)) / 0.1))
    return pos[0], pos[1] - 30 * (t - t0), s, 9 * math.sin((t - t0) * 9), 1

BRAND_T0, BRAND_T1, BRAND_TB = 37.36, 41.0, 38.14
def brand_poses(t, ya):
    out = e_in3((t - 40.75) / 0.25)
    res = [(BRAND_A, 540, ya, pop_scale(t, BRAND_T0, 0.2, 2.0) * (1 - out), -3, 1)]
    if t >= BRAND_TB: res.append((BRAND_B, 540, ya + 140, pop_scale(t, BRAND_TB, 0.18, 2.4) * (1 - out), 2, 1))
    return res

BRAND_SPARKS = [(120, -30), (960, 0), (180, 190)]   # offsets from the brand lockup
def brand_spark_pose(t, k, ya):
    t0 = 38.18 + 0.07 * k
    sx, oy = BRAND_SPARKS[k]
    s = pop_scale(t, t0, 0.2, 2.5) * (1 - e_in3((t - 39.1) / 0.2))
    return sx, ya + oy, s, 15 * math.sin(t * 6 + k), 1

# ----------------------------------------------------------------------------------------------
# layout: every element looks for a spot that stays clear of the head and the can for its whole
# life on screen; captions and stickers also avoid the other graphics
# ----------------------------------------------------------------------------------------------
SUBJ = [subjects(i) for i in range(NF)]
SOFT = [[] for _ in range(NF)]          # boxes of already placed graphics, per frame

def frames_in(a, b): return range(max(0, int(math.ceil(a * FPS - 1e-6))), min(NF, int(math.ceil(b * FPS - 1e-6))))

def hard_hit(b, i, pad_head=HEAD_PAD, pad_can=CAN_PAD):
    head, can = SUBJ[i]
    if hits(b, head, pad_head): return True
    if can is not None:
        p = pad_can + (16 if can[4] == 0 else 0)          # interpolated can positions get extra room
        if b[0] < can[2] + p and b[2] > can[0] - p and b[1] < can[3] + p and b[3] > can[1] - p: return True
    return False

def soft_hit(b, i):
    return any(b[0] < s[2] + 14 and b[2] > s[0] - 14 and b[1] < s[3] + 14 and b[3] > s[1] - 14 for s in SOFT[i])

def choose(cands, test):
    """First candidate whose test passes on hard+soft obstacles, else on hard only, else the least bad."""
    scored = []
    for c in cands:
        h, s = test(c)
        if h == 0 and s == 0: return c
        scored.append((h, s, c))
    ok_hard = [x for x in scored if x[0] == 0]
    if ok_hard: return min(ok_hard, key=lambda x: x[1])[2]
    return min(scored, key=lambda x: (x[0], x[1]))[2]

def mark(i, boxes):
    SOFT[i].extend(boxes)

# hook (fixed)
for i in frames_in(0, 2.80):
    mark(i, [box(s, x, y, sc, r) for s, x, y, sc, r, a in hook_poses(i / FPS)])

# section chips: one position per run of shots, popped in at the start of each run
LOWER_YS = list(range(1222, 1421, 14))
CHIP_RUNS = {}
for n, ts, txt, te in SECTIONS:
    spr = CHIPS[n]
    cw = spr.content[2] - spr.content[0]
    c_top_l, c_top_r = (40 + cw / 2, 262), (1040 - cw / 2, 262)
    a0, a1 = slam_end(ts), te + 0.2      # the chip enters once the "RAZÓN #N" slam is gone
    hidden = [(BROLL["t0"], BROLL["t1"]), (INSERT["t0"], INSERT["t1"])]
    cuts = sorted({a0, a1} | {c for c in SHOT_BOUNDS if a0 < c < a1} | {x for h in hidden for x in h if a0 < x < a1})
    segs = [(a, b) for a, b in zip(cuts[:-1], cuts[1:]) if not any(h0 <= a < h1 for h0, h1 in hidden)]
    lower = [(x, y) for y in LOWER_YS for x in (540, 420, 660, 320, 760) if 20 <= x - cw / 2 and x + cw / 2 <= 1060]
    lower.sort(key=lambda c: (c[1] - LOWER_YS[0]) + 1.6 * abs(c[0] - 540))
    cands = [c_top_l, c_top_r] + lower
    def test_chip(pos, frames):
        h = s = 0
        for i in frames:
            b = box(spr, pos[0], pos[1], 1.06, 0)
            h += hard_hit(b, i); s += soft_hit(b, i)
        return h, s
    whole = [i for a, b in segs for i in frames_in(a, b)]
    pos_all = choose(cands, lambda p: test_chip(p, whole))
    if test_chip(pos_all, whole)[0] == 0:
        plan = [(a, b, pos_all) for a, b in segs]
    else:   # split into the longest stretches that share a free spot; hide it where nothing is free
        plan = []
        for a, b in segs:
            fr_ab = list(frames_in(a, b))
            ok = [[c for c in cands if not hard_hit(box(spr, c[0], c[1], 1.06, 0), i)] for i in fr_ab]
            j = 0
            while j < len(fr_ab):
                common, k = ok[j], j
                while k + 1 < len(fr_ab) and [c for c in common if c in ok[k + 1]]:
                    common = [c for c in common if c in ok[k + 1]]; k += 1
                if common and k - j + 1 >= 18:                 # at least 0.6 s on screen
                    plan.append((fr_ab[j] / FPS, (fr_ab[k] + 1) / FPS, common[0]))
                j = k + 1
    runs = []
    for a, b, pos in plan:
        if runs and runs[-1][2] == pos and abs(runs[-1][1] - a) < 1e-6: runs[-1][1] = b
        else: runs.append([a, b, pos])
    runs = [r for r in runs if r[1] - r[0] >= 0.5]   # no blink-length appearances
    CHIP_RUNS[n] = (runs, a1)
    for a, b, pos in runs:
        for i in frames_in(a, b):
            x, y, sc, r, al = chip_pose(n, i / FPS, pos, a, a1)
            mark(i, [box(spr, x, y, max(sc, 0.01), r)])

# brand lockup: top if the head allows it, otherwise in the lower stack
def test_brand(ya):
    h = s = 0
    for i in frames_in(BRAND_T0, BRAND_T1):
        for spr, x, y, sc, r, a in brand_poses(i / FPS, ya):
            b = box(spr, x, y, max(sc, 0.01), r)
            h += hard_hit(b, i); s += soft_hit(b, i)
    return h, s
BRAND_Y = choose([330] + list(range(1160, 1640, 14)), test_brand)
for i in frames_in(BRAND_T0, BRAND_T1):
    mark(i, [box(spr, x, y, max(sc, 0.01), r) for spr, x, y, sc, r, a in brand_poses(i / FPS, BRAND_Y)])
BRAND_SPARK_ON = []
for k in range(len(BRAND_SPARKS)):
    ok = all(not hard_hit(box(SPARK, *brand_spark_pose(i / FPS, k, BRAND_Y)[:4]), i)
             for i in frames_in(38.18 + 0.07 * k, 39.3))
    BRAND_SPARK_ON.append(ok)

# "RAZÓN #N" slams
SLAM_POS = {}
for n, ts, txt, te in SECTIONS:
    spr = NUMBERS[n]
    cands = [(270, 760, 0.85), (810, 760, 0.85), (270, 980, 0.85), (810, 980, 0.85)] + \
            [(540, y, 0.7) for y in range(1330, 1700, 20)] + [(250, y, 0.6) for y in range(1300, 1700, 40)] + \
            [(830, y, 0.6) for y in range(1300, 1700, 40)]
    def test_slam(pos):
        h = s = 0
        for i in frames_in(ts, slam_end(ts)):
            x, y, sc, r, a = slam_pose(i / FPS, ts, pos)
            b = box(spr, x, y, sc, r)
            h += hard_hit(b, i); s += soft_hit(b, i)
        return h, s
    SLAM_POS[n] = choose(cands, test_slam)
    for i in frames_in(ts, slam_end(ts)):
        x, y, sc, r, a = slam_pose(i / FPS, ts, SLAM_POS[n])
        mark(i, [box(spr, x, y, sc, r)])

# captions: block top as close as possible to the default line, moving down when needed
CAP_TOP = {}
for gi, g in enumerate(GROUPS):
    fr = [i for i in frames_in(g["s"] - 0.02, g["e"]) if not caption_hidden(gi, i / FPS)]
    if not fr: continue
    items = caption_layout(gi)
    base = 1294 if g["s"] < 2.733 else 1244
    ext = [box(it["spr"], *word_pose(it, 99, 0)) for it in items]
    dx_lo, dx_hi = 30 - min(b[0] for b in ext), 1050 - max(b[2] for b in ext)
    cands = [(top, dx) for top in range(base, 1601, 12) for dx in (0, 110, -110, 200, -200) if dx_lo <= dx <= dx_hi]
    cands.sort(key=lambda c: (c[0] - base) + 1.6 * abs(c[1]))
    def test_cap(c):
        h = s = 0
        for i in fr:
            t = i / FPS
            for it in items:
                if t < it["s"] - 0.02: continue
                x, y, sc, r = word_pose(it, t, c[0])
                b = box(it["spr"], x + c[1], y, max(sc, 1.0), r)
                h += hard_hit(b, i); s += soft_hit(b, i)
        return h, s
    CAP_TOP[gi] = choose(cands, test_cap)
    for i in fr:
        t = i / FPS
        top, dx = CAP_TOP[gi]
        mark(i, [box(it["spr"], word_pose(it, t, top)[0] + dx, *word_pose(it, t, top)[1:]) for it in items if t >= it["s"] - 0.02])

# stickers
STK_POS = {}
for t0, d, names, px, py, size in STICKERS:
    spr = STK[(t0, tuple(names))]
    cands = [(px, py, 1.0)] + [(x, y, 1.0) for y in (1000, 860, 720, 580, 440, 1150, 1300, 1450, 1600) for x in (905, 175)] \
        + [(x, y, sc) for sc in (0.85, 0.7) for y in range(1000, 1660, 50) for x in (125, 955)]
    def test_stk(pos):
        h = s = 0
        for i in frames_in(t0, t0 + d):
            x, y, sc, r, a = sticker_pose(i / FPS, t0, d, pos)
            b = box(spr, x, y, sc, r)
            h += hard_hit(b, i); s += soft_hit(b, i)
        return h, s
    pos = choose(cands, test_stk)
    if test_stk(pos) != (0, 0): continue          # decoration only: skip it rather than cover anything
    STK_POS[t0] = pos
    for i in frames_in(t0, t0 + d):
        x, y, sc, r, a = sticker_pose(i / FPS, t0, d, STK_POS[t0])
        mark(i, [box(spr, x, y, sc, r)])

# ----------------------------------------------------------------------------------------------
# overlays
# ----------------------------------------------------------------------------------------------
def overlays(f, t, i):
    if t < 2.80:
        for spr, x, y, sc, r, a in hook_poses(t):
            draw(f, spr, x, y, sc, r, a, tag="hook")
    for gi, g in enumerate(GROUPS):
        if g["s"] - 0.02 <= t < g["e"] and gi in CAP_TOP and not caption_hidden(gi, t):
            for it in caption_layout(gi):
                if t < it["s"] - 0.02: continue
                top, dx = CAP_TOP[gi]
                x, y, sc, r = word_pose(it, t, top)
                draw(f, it["spr"], x + dx, y, sc, r, clamp((t - it["s"] + 0.02) / 0.05), tag="caption")
    for n, ts, txt, te in SECTIONS:
        if ts <= t < slam_end(ts):
            x, y, sc, r, a = slam_pose(t, ts, SLAM_POS[n])
            draw(f, NUMBERS[n], x, y, sc, r, a, tag="number")
        runs, chip_end = CHIP_RUNS[n]
        for a0, a1, pos in runs:
            if a0 <= t < a1:
                x, y, sc, r, a = chip_pose(n, t, pos, a0, chip_end)
                draw(f, CHIPS[n], x, y, sc, r, a, tag="chip")
    for t0, d, names, px, py, size in STICKERS:
        if t0 <= t < t0 + d and t0 in STK_POS:
            x, y, sc, r, a = sticker_pose(t, t0, d, STK_POS[t0])
            draw(f, STK[(t0, tuple(names))], x, y, sc, r, a, tag="sticker")
    # kinetic insert "HOJA COMPLETA" (full-screen graphic, nobody on screen)
    if INSERT["t0"] <= t < INSERT["t1"]:
        p = t - INSERT["t0"]
        draw(f, LEAF, 540, 700, pop_scale(t, INSERT["t0"] + 0.04, 0.22, 1.8), -25 + 50 * p, 1, tag="insert")
        draw(f, INS_A, 540, 1010, pop_scale(t, INSERT["t0"] + 0.12, 0.16, 2.2), -3, 1, tag="insert")
        if t >= INSERT["t0"] + 0.30:
            draw(f, INS_B, 540, 1215, pop_scale(t, INSERT["t0"] + 0.30, 0.16, 2.0), 2, 1, tag="insert")
        for k, (sx, sy) in enumerate([(250, 560), (820, 640), (300, 1330), (800, 1380)]):
            t0 = INSERT["t0"] + 0.1 + 0.08 * k
            if t >= t0:
                draw(f, SPARK, sx, sy, pop_scale(t, t0, 0.2, 2.5) * (0.8 + 0.2 * math.sin(t * 12 + k)), 15 * math.sin(t * 5 + k), 1, tag="insert")
    if BRAND_T0 <= t < BRAND_T1:
        for spr, x, y, sc, r, a in brand_poses(t, BRAND_Y):
            draw(f, spr, x, y, sc, r, a, tag="brand")
        for k in range(len(BRAND_SPARKS)):
            if BRAND_SPARK_ON[k] and 38.18 + 0.07 * k <= t < 39.3:
                draw(f, SPARK, *brand_spark_pose(t, k, BRAND_Y), tag="sparkle")
    if t >= END_T:
        p = t - END_T
        draw(f, CAN_CARD, *end_card_pose(t), tag="product")
        draw(f, END_E, 930, 300, pop_scale(t, END_T + 0.35, 0.2, 2.5), 12 * math.sin(p * 5), 1, tag="end")
        if p >= 0.30: draw(f, END_A, 540, 1300, pop_scale(t, END_T + 0.30, 0.18, 2.0), -3, 1, tag="end")
        if p >= 0.48: draw(f, END_B, 540, 1458, pop_scale(t, END_T + 0.48, 0.16, 2.0), 0, 1, tag="end")
        if p >= 0.66: draw(f, END_C, 540, 1553, pop_scale(t, END_T + 0.66, 0.16, 1.6), 0, 1, tag="end")
        if p >= 0.85:
            pulse = 1 + 0.04 * math.sin((p - 0.85) * 8)
            draw(f, END_D, 540, 1698, pop_scale(t, END_T + 0.85, 0.2, 2.2) * pulse, -2, 1, tag="end")
        for k, (sx, sy) in enumerate([(130, 470), (950, 980), (112, 1075)]):
            t0 = END_T + 0.25 + 0.1 * k
            if t >= t0:
                draw(f, SPARK, sx, sy, pop_scale(t, t0, 0.2, 2.5) * (0.85 + 0.15 * math.sin(t * 7 + k)), 20 * math.sin(t * 4 + k), 1, tag="end")

def end_card_pose(t):
    p = t - END_T
    return 540, 760 + 10 * math.sin(p * 3), pop_scale(t, END_T + 0.02, 0.3, 1.8) * 0.92, -5 + 2 * math.sin(p * 2.2), 1

def insert_background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2) / 0.62
    r = np.clip(r, 0, 1)[..., None]
    inner = np.array([66, 128, 52], np.float32) / 255
    outer = np.array([7, 34, 16], np.float32) / 255
    return inner * (1 - r) + outer * r

INS_BG = insert_background()

def render_frame(i, src):
    t = i / FPS
    if t >= END_T:
        f = END_BG.copy()
    elif INSERT["t0"] <= t < INSERT["t1"]:
        f = INS_BG.copy()
    else:
        img = base_frame(t, i, src)
        if t >= 41.25:   # she walks out of frame: blur into the end card
            k = (t - 41.25) / (END_T - 41.25)
            img = cv2.GaussianBlur(img, (0, 0), 0.1 + 20 * k * k)
        f = img.astype(np.float32) / 255.0
        f *= VIG
    a = flash_alpha(t)
    if a > 0: f = f * (1 - a) + a
    overlays(f, t, i)
    return (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)

def check_layout():
    """Every drawn graphic vs the head and the can, frame by frame. Returns the list of contacts."""
    global RECORD
    bad = []
    for i in range(NF):
        t = i / FPS
        RECORD = []
        overlays(None, t, i)
        rec, RECORD = RECORD, None
        head, can = SUBJ[i]
        if t >= END_T:
            prod = box(CAN_CARD, *end_card_pose(t)[:4])
            can = (prod[0], prod[1], prod[2], prod[3], 1)
        for tag, b in rec:
            if tag == "product": continue
            if hits(b, head, CHECK_PAD): bad.append((i, tag, "head"))
            if can is not None and b[0] < can[2] + CHECK_PAD and b[2] > can[0] - CHECK_PAD \
                    and b[1] < can[3] + CHECK_PAD and b[3] > can[1] - CHECK_PAD:
                bad.append((i, tag, "can"))
    return bad

# ----------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------
if "--check" in ARGS:
    bad = check_layout()
    print("contacts:", len(bad))
    for i, tag, what in bad: print(f"  frame {i} t={i / FPS:.2f} {tag} touches {what}")
    sys.exit(1 if bad else 0)

if "--frames" in ARGS:
    want = sorted(int(x) for x in ARGS[ARGS.index("--frames") + 1].split(","))
    os.makedirs(OUT, exist_ok=True)
    last = None
    for i, fr in enumerate(decoder()):
        if i in want:
            Image.fromarray(render_frame(i, fr)).save(os.path.join(OUT, f"f{i:04d}.jpg"), quality=88)
        last = fr
    for i in want:
        if i > SRC_LAST:
            Image.fromarray(render_frame(i, last)).save(os.path.join(OUT, f"f{i:04d}.jpg"), quality=88)
    sys.exit(0)

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-profile:v", "high",
                        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                        "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
last = None
i = 0
for fr in decoder():
    if i > SRC_LAST: break
    enc.stdin.write(render_frame(i, fr).tobytes()); last = fr; i += 1
    if i % 60 == 0: print("frame", i, flush=True)
while i < NF:
    enc.stdin.write(render_frame(i, last).tobytes()); i += 1
enc.stdin.close(); enc.wait()
json.dump(SFX, open(os.path.join(WORK, "sfx_cues.json"), "w"))
print("done", NF, "frames")
