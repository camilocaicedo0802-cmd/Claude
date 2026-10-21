"""Render the 15s organic vertical edit: jump-cut zooms, punch transitions,
reference-style title box, small white subs, big cream keywords, sparkles."""
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]
OUT = sys.argv[2]
PREVIEW = len(sys.argv) > 3 and sys.argv[3] == 'preview'
SRC = f'{S}/raw/ORNAMENTS.MOV'
W, H, FPS = 1080, 1920, 30
SPEED = 1.033
F = f'{S}/fonts'
SUB_FONT = ImageFont.truetype(f'{F}/tiktok-sans-latin-600-normal.woff', 44)
TITLE_FONT = ImageFont.truetype(f'{F}/tiktok-sans-latin-600-normal.woff', 66)
KEY_FONT_PATH = f'{F}/outfit-latin-700-normal.woff'
CREAM = (236, 252, 194)
BOX = (255, 253, 214)

# (src_in, src_out, base_zoom, zoom_center(x,y), transition_into)
SEGS = [
    (5.73, 7.85, 1.00, (0.50, 0.34), None),
    (8.60, 9.46, 1.16, (0.50, 0.30), 'cut'),
    (25.76, 30.50, 1.04, (0.50, 0.42), 'whip'),
    (13.42, 15.54, 1.10, (0.50, 0.40), 'whip'),
    (33.62, 36.60, 1.00, (0.50, 0.42), 'punch'),
    (44.72, 46.74, 1.14, (0.50, 0.42), 'whip'),
    (56.76, 57.44, 1.08, (0.50, 0.42), 'punch'),
]

# timeline mapping
starts, t = [], 0.0
for a, b, *_ in SEGS:
    starts.append(t); t += (b - a) / SPEED
TOTAL = t
NFRAMES = int(round(TOTAL * FPS))

def to_out(src_t):
    for (a, b, *_), st in zip(SEGS, starts):
        if a - 0.05 <= src_t <= b + 0.05:
            return st + (min(max(src_t, a), b) - a) / SPEED
    raise ValueError(src_t)

# subtitles (source times, exact text)
SUBS = [
    (5.73, 6.88, 'when something this beautiful'),
    (6.88, 7.85, 'just arrived'),
    (8.60, 9.46, 'I have to share it'),
    (25.76, 27.74, 'these are ceramic ornaments'),
    (27.74, 29.76, 'each hand painted by Cecilia'),
    (29.76, 30.50, 'in Mexico'),
    (13.42, 15.54, 'each one is one-of-a-kind'),
    (33.62, 35.24, "I'm gonna start hanging these"),
    (35.24, 36.60, 'on every single gift bag'),
    (44.72, 46.74, "I can't decide which one's my favorite"),
    (56.76, 57.44, 'get one'),
]
SUBS = [(to_out(a), to_out(b), s) for a, b, s in SUBS]

# big keywords (source start/end)
KEYS = [
    (6.50, 7.30, 'beautiful'),
    (9.06, 9.46, 'share'),
    (26.26, 26.94, 'ceramic'),
    (26.94, 27.82, 'ornaments'),
    (28.10, 29.02, 'hand painted'),
    (29.10, 29.80, 'Cecilia'),
    (30.06, 30.50, 'Mexico'),
    (14.64, 15.54, 'one-of-a-kind'),
    (36.02, 36.60, 'gift bag'),
    (46.24, 46.74, 'favorite'),
    (56.84, 57.44, 'Get one'),
]
KEYS = [(to_out(a), to_out(b), s) for a, b, s in KEYS]

TITLE = (0.0, to_out(26.00), ['Hand-painted ornaments', 'just arrived from Mexico'])
# sparkle bursts (out time, duration)
SPARKS = [(to_out(14.64), 0.9), (to_out(56.84), 0.75)]

# ---------------- text rendering helpers ----------------
def text_w(font, s):
    b = font.getbbox(s); return b[2] - b[0]

def wrap(font, s, maxw):
    words, lines, cur = s.split(), [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if text_w(font, test) <= maxw or not cur: cur = test
        else: lines.append(cur); cur = w
    lines.append(cur)
    return lines

def draw_subs(img, s):
    d = ImageDraw.Draw(img)
    lines = wrap(SUB_FONT, s, 600)
    lh = 52; y0 = int(H * 0.835) - (len(lines) - 1) * lh // 2
    for i, ln in enumerate(lines):
        x = W // 2 - text_w(SUB_FONT, ln) // 2
        d.text((x, y0 + i * lh), ln, font=SUB_FONT, fill=(255, 255, 255),
               stroke_width=3, stroke_fill=(0, 0, 0))

def title_layer(lines):
    """Cream boxed title like the reference (per-line rounded boxes merged)."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    lh, pad_x, pad_y = 78, 26, 10
    y0 = int(H * 0.665)
    for i, ln in enumerate(lines):
        tw = text_w(TITLE_FONT, ln)
        x0 = W // 2 - tw // 2 - pad_x; x1 = W // 2 + tw // 2 + pad_x
        y = y0 + i * lh
        d.rounded_rectangle((x0, y - pad_y + 4, x1, y + lh + pad_y - 2), radius=18, fill=BOX + (255,))
    for i, ln in enumerate(lines):
        tw = text_w(TITLE_FONT, ln); b = TITLE_FONT.getbbox(ln)
        d.text((W // 2 - tw // 2 - b[0], y0 + i * lh + 6), ln, font=TITLE_FONT, fill=(18, 18, 18))
    return lay

_key_cache = {}
def key_layer(s):
    if s in _key_cache: return _key_cache[s]
    size = 150
    font = ImageFont.truetype(KEY_FONT_PATH, size)
    while text_w(font, s) > W * 0.86:
        size -= 6; font = ImageFont.truetype(KEY_FONT_PATH, size)
    b = font.getbbox(s); tw, th = b[2] - b[0], b[3] - b[1]
    pad = 40
    lay = Image.new('RGBA', (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('L', lay.size, 0)
    ImageDraw.Draw(sh).text((pad - b[0], pad - b[1] + 6), s, font=font, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    lay = Image.composite(Image.new('RGBA', lay.size, (20, 20, 10, 255)), Image.new('RGBA', lay.size, (0, 0, 0, 0)), sh)
    ImageDraw.Draw(lay).text((pad - b[0], pad - b[1]), s, font=font, fill=CREAM + (255,),
                             stroke_width=2, stroke_fill=(60, 64, 40, 120))
    _key_cache[s] = lay
    return lay

def ease_out_back(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def sparkle(d, cx, cy, r, alpha):
    pts = []
    for k in range(8):
        ang = k * math.pi / 4 - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.22
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=CREAM + (int(255 * alpha),))

SPARK_POS = [(0.20, 0.30, 46, 0.00), (0.82, 0.26, 36, 0.10), (0.86, 0.50, 52, 0.20),
             (0.14, 0.55, 34, 0.28), (0.74, 0.62, 30, 0.36)]

# ---------------- video frames ----------------
def seg_frames(i):
    a, b = SEGS[i][0], SEGS[i][1]
    n_out = int(round((starts[i] + (b - a) / SPEED) * FPS)) - int(round(starts[i] * FPS))
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-i', SRC, '-t', f'{(b - a) + 0.2:.3f}',
           '-vf', f'setpts=(PTS-STARTPTS)/{SPEED},fps={FPS},scale={W}:{H}', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    last = None
    for _ in range(n_out):
        buf = p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3: last = buf
        yield Image.frombytes('RGB', (W, H), last)
    p.stdout.close(); p.wait()

def zoom(img, z, cx, cy, blur=0):
    cw, ch = W / z, H / z
    x0 = min(max(cx * W - cw / 2, 0), W - cw); y0 = min(max(cy * H - ch / 2, 0), H - ch)
    out = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    if blur: out = out.filter(ImageFilter.BoxBlur(blur))
    return out

def main():
    enc = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-vf', 'eq=contrast=1.06:saturation=1.14:brightness=0.01', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
           '-pix_fmt', 'yuv420p', OUT]
    pe = subprocess.Popen(enc, stdin=subprocess.PIPE)
    title = title_layer(TITLE[2])
    fidx = 0
    for i, (a, b, z0, (cx, cy), tr) in enumerate(SEGS):
        seg_dur = (b - a) / SPEED
        for k, fr in enumerate(seg_frames(i)):
            T = fidx / FPS; lt = k / FPS
            # slow push-in on every shot, like the reference's subtle drift
            z = z0 + 0.035 * (lt / max(seg_dur, 0.5))
            blur = 0
            if tr in ('whip', 'punch') and lt < 0.22:
                x = lt / 0.22; e = 1 - (1 - x) ** 3
                z += (0.22 if tr == 'whip' else 0.12) * (1 - e)
                if tr == 'whip': blur = int(10 * (1 - e))
            img = zoom(fr, z, cx, cy, blur)
            # white flash on the product reveal
            if i == 2 and lt < 0.10:
                img = Image.blend(img, Image.new('RGB', (W, H), (255, 255, 250)), 0.55 * (1 - lt / 0.10))
            img = img.convert('RGBA')
            # title box
            if TITLE[0] <= T < TITLE[1]:
                if T < 0.18:
                    s = max(0.3, 0.3 + 0.7 * ease_out_back(T / 0.18)); tl = title.resize((int(W * s), int(H * s)))
                    lay = Image.new('RGBA', (W, H)); lay.paste(tl, ((W - tl.width) // 2, int(H * 0.72) - int(H * 0.72 * s)))
                    img.alpha_composite(lay)
                else:
                    img.alpha_composite(title)
            # big keyword
            for ks, ke, s in KEYS:
                if ks <= T < ke + 0.12:
                    lay = key_layer(s); x = min(1, (T - ks) / 0.12); sc = 0.8 + 0.2 * ease_out_back(x)
                    l2 = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))))
                    img.alpha_composite(l2, (W // 2 - l2.width // 2, int(H * 0.165) - l2.height // 2))
                    break
            # sparkles
            for st, du in SPARKS:
                if st <= T < st + du:
                    d = ImageDraw.Draw(img)
                    for px, py, r, delay in SPARK_POS:
                        u = (T - st - delay * du) / (du * 0.55)
                        if 0 <= u <= 1:
                            sparkle(d, px * W, py * H, r * math.sin(math.pi * u), math.sin(math.pi * u))
            # subtitles
            for ss, se, s in SUBS:
                if ss <= T < se:
                    draw_subs(img, s); break
            pe.stdin.write(img.convert('RGB').tobytes())
            fidx += 1
            if PREVIEW and k == 0: img.convert('RGB').save(f'{S}/work/prev_{i}.jpg')
    pe.stdin.close(); pe.wait()
    json.dump({'total': TOTAL, 'starts': starts, 'frames': fidx,
               'keys': KEYS, 'sparks': SPARKS}, open(f'{S}/work/timeline.json', 'w'))
    print('frames', fidx, 'dur', TOTAL)

main()
