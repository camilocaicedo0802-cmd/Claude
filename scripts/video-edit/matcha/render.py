"""Matcha UGC re-edit: zooms, transitions, B-roll inserts, motion graphics and new captions.

Usage: python3 render.py <work_dir> <assets_dir> <source.mov> <out_video_noaudio.mp4> [--frames 0,90,300] [--preview]

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
    (22.98, 24.20, 0.38, (350, 900), 0.75),   # comprueba 100%  -> toward the can
    (24.66, 25.40, 0.10, None, 0),        # originales
    (27.30, 28.10, 0.45, (480, 1160), 0.85),  # súper vivo -> into the powder
    (28.12, 29.00, 0.12, None, 0),        # cero opaco
    (29.76, 30.70, 0.16, None, 0),        # antioxidantes
    (32.76, 33.20, 0.10, None, 0),        # algo rico
    (34.30, 35.50, 0.12, None, 0),        # claramente lo preparan
    (36.36, 37.10, 0.12, None, 0),        # todos prefieren
    (38.14, 39.05, 0.40, (330, 880), 0.7),    # Laboratorios Outlet -> toward the can
    (40.16, 40.70, 0.16, None, 0),        # claramente
]
SHAKES = [(17.95, 18.80, 22.0)]           # "los otros me dejan como..." (caffeine jitters)

# B-roll: full-screen powder close-up taken from the moment she opens the can
BROLL = dict(t0=5.30, t1=6.15, src_t=27.0, center=(470, 1140), z0=2.75, z1=3.0)
# kinetic insert "HOJA COMPLETA"
INSERT = dict(t0=8.40, t1=9.467)

SECTIONS = [  # number, slam time, chip text, section end
    (1, 2.84, "NO ES UN TÉ CUALQUIERA", 4.44),
    (2, 4.44, "ES TÉ VERDE EN POLVO", 8.30),
    (3, 9.50, "CAFEÍNA… PERO DIFERENTE", 18.84),
    (4, 18.84, "NO SABE A PASTO", 21.88),
    (5, 21.88, "COLOR 100% ORIGINAL", 29.06),
    (6, 29.06, "TIENE ANTIOXIDANTES", 35.56),
]

STICKERS = [  # (t0, dur, emoji name(s), x, y, size)
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
    (27.30, "shimmer", -11), (27.60, "pop3", -15), (28.66, "pop2", -16), (29.06, "impact", -13),
    (29.06, "click", -10), (29.28, "impact", -14), (29.60, "whoosh3", -16), (29.96, "pop1", -14),
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

def draw(frame, spr, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if alpha <= 0.004 or scale <= 0.02: return
    M = cv2.getRotationMatrix2D((spr.w / 2, spr.h / 2), rot, scale)
    M[0, 2] += cx - spr.w / 2; M[1, 2] += cy - spr.h / 2
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
    cy_face = ty + 192.0 / z           # face lands at 40 % of the frame height
    cx, cy = tx, cy_face
    if wsum > 0:                       # pull the framing toward the punch focus point
        wb = min(wsum, 0.95)
        cx = lerp(tx, fxs / wsum, wb)
        cy = lerp(cy_face, fys / wsum, wb)
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
CAP_CACHE = {}
def caption_layout(gi):
    if gi in CAP_CACHE: return CAP_CACHE[gi]
    g = GROUPS[gi]
    items = []
    for w in g["words"]:
        raw = w["w"].upper().rstrip(",.").replace("...", "…")
        if raw.endswith("…"): raw = raw[:-1] + "…"
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
    lh = 112
    for li, ln in enumerate(lines):
        tot = sum(it["w"] for it in ln) + gap * (len(ln) - 1)
        x = W / 2 - tot / 2
        for it in ln:
            it["cx"] = x + it["w"] / 2
            it["dy"] = (li - (len(lines) - 1) / 2) * lh
            x += it["w"] + gap
    for k, it in enumerate(items):
        it["rot"] = (-3 if k % 2 == 0 else 3) if it["kw"] else 0
    CAP_CACHE[gi] = items
    return items

def caption_y(t):
    if t < 2.733: return 1350
    return 1300

# chip vertical position: above the head when there is room, otherwise below the chin
CHIP_Y = {}
def chip_y(t, fidx):
    # decided once per shot from its median face and resting framing, so the chip never jumps mid-shot
    k = shot_index(t)
    if k not in CHIP_Y:
        a, b = SHOT_BOUNDS[k], min(SHOT_BOUNDS[k + 1], END_T)
        fx, fy, fw = np.median(np.array(FACES[int(a * FPS):int(b * FPS)]), axis=0)
        z = sum(SHOT_ZOOM[k]) / 2
        cxx, cyy = clamp_center(z, fx, fy + 192.0 / z, 0)
        if (fy - cyy) * z + H / 2 > 520: CHIP_Y[k] = 262       # face sits low enough: chip goes on top
        else: CHIP_Y[k] = min(1120, (fy + 0.85 * fw - cyy) * z + H / 2 + 80)
    return CHIP_Y[k]

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

    if BROLL["t0"] <= t < BROLL["t1"]:
        k = broll_idx0 + int(round((t - BROLL["t0"]) * FPS))
        fr = STORE[min(k, max(STORE))]
        q = (t - BROLL["t0"]) / (BROLL["t1"] - BROLL["t0"])
        z = lerp(BROLL["z0"], BROLL["z1"], q) * ez
        img = warp_src(fr, z, BROLL["center"][0], BROLL["center"][1] + 20 * q, erot, edx, edy)
    else:
        z, cx, cy, rot, dx, dy = camera(t, i)
        img = warp_src(src, z * ez, cx, cy, rot + erot, dx + edx, dy + edy)

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

def overlays(f, t, i):
    # hook ---------------------------------------------------------------------------------
    if t < 2.80:
        out = e_in3((t - 2.62) / 0.16)
        sx = -out * 900
        a = 1 - out * 0.3
        s = 1 + 1.6 * (1 - e_out3((t - 0.04) / 0.16)) if t < 0.2 else 1
        if t >= 0.04: draw(f, HOOK_A, 540 + sx, 1035, s, -4, a * clamp((t - 0.04) / 0.05))
        if t >= 0.42: draw(f, HOOK_B, 540 + sx, 1175, pop_scale(t, 0.42), 2, a)
    # captions -----------------------------------------------------------------------------
    hide = INSERT["t0"] <= t < INSERT["t1"] or t >= 40.95
    if not hide:
        for gi, g in enumerate(GROUPS):
            if g["s"] <= t < g["e"]:
                items = caption_layout(gi)
                y = caption_y(t)
                for it in items:
                    if t < it["s"] - 0.02: continue
                    sc = pop_scale(t, it["s"] - 0.02, 0.15, 2.2 if it["kw"] else 1.4)
                    draw(f, it["spr"], it["cx"], y + it["dy"], sc, it["rot"], clamp((t - it["s"] + 0.02) / 0.05))
    # section numbers + chips ---------------------------------------------------------------
    for n, ts, txt, te in SECTIONS:
        if ts <= t < ts + 0.75:
            p = (t - ts)
            if p < 0.55:
                s = 1 + 1.4 * (1 - e_out3(p / 0.14))
                draw(f, NUMBERS[n], 300, 900, s * 0.9, -7, clamp(p / 0.05))
            else:
                q = e_in3((p - 0.55) / 0.2)
                draw(f, NUMBERS[n], lerp(300, 150, q), lerp(900, chip_y(t, i), q), 0.9 * (1 - 0.75 * q), -7 * (1 - q), 1 - q)
        if ts + 0.5 <= t < te + 0.2 and not (INSERT["t0"] <= t < INSERT["t1"]):
            spr = CHIPS[n]
            tin = e_back((t - ts - 0.5) / 0.32, 1.3)
            tout = e_in3((t - te) / 0.2)
            x = lerp(-spr.w / 2, 40 + spr.w / 2 - 30, tin) - tout * (spr.w + 100)
            focus = max([punch_env(t, pp) * pp[4] for pp in PUNCHES if pp[3] is not None] + [0])
            draw(f, spr, x, chip_y(t, i), 1.0, 0, 1 - clamp(focus * 1.3))   # step aside during product close-ups
    # stickers ------------------------------------------------------------------------------
    for t0, d, names, x, y, size in STICKERS:
        if t0 <= t < t0 + d:
            spr = STK[(t0, tuple(names))]
            s = pop_scale(t, t0, 0.18, 2.6) * (1 - e_in3((t - (t0 + d - 0.1)) / 0.1))
            rot = 9 * math.sin((t - t0) * 9)
            draw(f, spr, x, y - 30 * (t - t0), s, rot, 1)
    # kinetic insert "HOJA COMPLETA" ---------------------------------------------------------
    if INSERT["t0"] <= t < INSERT["t1"]:
        p = t - INSERT["t0"]
        draw(f, LEAF, 540, 700, pop_scale(t, INSERT["t0"] + 0.04, 0.22, 1.8), -25 + 50 * p, 1)
        draw(f, INS_A, 540, 1010, pop_scale(t, INSERT["t0"] + 0.12, 0.16, 2.2), -3, 1)
        if t >= INSERT["t0"] + 0.30:
            draw(f, INS_B, 540, 1215, pop_scale(t, INSERT["t0"] + 0.30, 0.16, 2.0), 2, 1)
        for k, (sx, sy) in enumerate([(250, 560), (820, 640), (300, 1330), (800, 1380)]):
            t0 = INSERT["t0"] + 0.1 + 0.08 * k
            if t >= t0:
                draw(f, SPARK, sx, sy, pop_scale(t, t0, 0.2, 2.5) * (0.8 + 0.2 * math.sin(t * 12 + k)), 15 * math.sin(t * 5 + k), 1)
    # brand lockup ---------------------------------------------------------------------------
    if 37.36 <= t < 41.0:
        out = e_in3((t - 40.75) / 0.25)
        draw(f, BRAND_A, 540, 330 - out * 400, pop_scale(t, 37.36, 0.2, 2.0), -3, 1)
        if t >= 38.14:
            draw(f, BRAND_B, 540, 470 - out * 400, pop_scale(t, 38.14, 0.18, 2.4), 2, 1)
        if 38.14 <= t < 39.3:
            for k, (sx, sy) in enumerate([(120, 300), (960, 330), (180, 520)]):
                t0 = 38.18 + 0.07 * k
                if t >= t0:
                    draw(f, SPARK, sx, sy, pop_scale(t, t0, 0.2, 2.5) * (1 - e_in3((t - 39.1) / 0.2)), 15 * math.sin(t * 6 + k), 1)
    # end card -------------------------------------------------------------------------------
    if t >= END_T:
        p = t - END_T
        draw(f, CAN_CARD, 540, 760 + 10 * math.sin(p * 3), pop_scale(t, END_T + 0.02, 0.3, 1.8) * 0.92, -5 + 2 * math.sin(p * 2.2), 1)
        draw(f, END_E, 860, 420, pop_scale(t, END_T + 0.35, 0.2, 2.5), 12 * math.sin(p * 5), 1)
        draw(f, END_A, 540, 1260, pop_scale(t, END_T + 0.20, 0.18, 2.0), -3, 1)
        if p >= 0.42: draw(f, END_B, 540, 1418, pop_scale(t, END_T + 0.42, 0.16, 2.0), 0, 1)
        if p >= 0.62: draw(f, END_C, 540, 1515, pop_scale(t, END_T + 0.62, 0.16, 1.6), 0, 1)
        if p >= 0.85:
            pulse = 1 + 0.04 * math.sin((p - 0.85) * 8)
            draw(f, END_D, 540, 1665, pop_scale(t, END_T + 0.85, 0.2, 2.2) * pulse, -2, 1)
        for k, (sx, sy) in enumerate([(200, 470), (900, 980), (170, 1060)]):
            t0 = END_T + 0.25 + 0.1 * k
            if t >= t0:
                draw(f, SPARK, sx, sy, pop_scale(t, t0, 0.2, 2.5) * (0.85 + 0.15 * math.sin(t * 7 + k)), 20 * math.sin(t * 4 + k), 1)

STK = {(t0, tuple(n)): combo(n, size) for t0, d, n, x, y, size in STICKERS}

def render_frame(i, src):
    t = i / FPS
    if t >= END_T:
        f = END_BG.copy()
    else:
        img = base_frame(t, i, src)
        if INSERT["t0"] <= t < INSERT["t1"]:
            sm = cv2.resize(img, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
            sm = cv2.GaussianBlur(sm, (0, 0), 3)
            img = cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR)
            f = img.astype(np.float32) / 255.0
            f = f * 0.45 + np.array([0.04, 0.20, 0.08], np.float32) * 0.45
        else:
            if t >= 41.25:   # she walks out of frame: blur into the end card
                k = (t - 41.25) / (END_T - 41.25)
                img = cv2.GaussianBlur(img, (0, 0), 0.1 + 20 * k * k)
            f = img.astype(np.float32) / 255.0
        f *= VIG
    a = flash_alpha(t)
    if a > 0: f = f * (1 - a) + a
    overlays(f, t, i)
    return (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)

# ----------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------
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
