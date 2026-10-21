"""Pinktober 15s promo: beat-synced cuts (190 BPM), neon kinetic type, pink grade, Tranqui end card."""
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

S = sys.argv[1]; OUT = sys.argv[2]
PREVIEW = 'preview' in sys.argv[3:]
R = f'{S}/raw/Pinktober'
FD = f'{S}/../fonts'
W, H, FPS = 1080, 1920, 30
TOTAL = 15.0
NF = int(TOTAL * FPS)
BEAT = 60 / 190

PINK = (255, 84, 176)
PINK_GLOW = (255, 20, 140)
NEON_CORE = (255, 214, 236)
WHITE = (255, 255, 255)

def font(name, size):
    return ImageFont.truetype(f'{FD}/{name}-latin-{"400" if name in ("allura", "archivo-black") else name.split(":")[1] if ":" in name else "400"}-normal.woff', size)

def F(kind, size):
    path = {'thin': 'josefin-sans-latin-300', 'reg': 'josefin-sans-latin-400', 'semi': 'josefin-sans-latin-600',
            'bold': 'josefin-sans-latin-700', 'heavy': 'archivo-black-latin-400', 'script': 'allura-latin-400'}[kind]
    return ImageFont.truetype(f'{FD}/{path}-normal.woff', size)

# ---------------- shots: (clip, src_in, beat_start, beat_end, transition_in, focus_y) ----------------
C = {1: '1eadec44-afd0-4d1e-bf9e-2019d2ed1c07.mp4', 2: '334d12d1-429c-441a-b563-08d24307aa87.mp4',
     3: '3aa3bebc-bb92-48f2-b963-a8091720cbfa.mp4', 4: '6e8f11c7-7848-4c23-adb9-fe8d6d40b9eb.mp4',
     5: '8fa9b502-0a99-463f-ab64-52ace2b73e4f.mp4', 6: '915b9ae4-e0db-4c3e-8fc5-4ce3187e299d.mp4',
     7: 'IMG_2091.MOV', 8: 'IMG_2157.MOV', 9: 'IMG_2161.MOV'}
SHOTS = [
    (4, 7.0, 0, 4, 'flash'),      # DANCE for a cause
    (8, 10.0, 4, 6, 'punch'),     # salsa
    (5, 5.2, 6, 8, 'whip'),       # bachata
    (6, 12.0, 8, 11, 'glitch'),   # latin dance
    (7, 4.0, 11, 14, 'punch'),    # social party
    (1, 12.5, 14, 17, 'whip'),    # join us for the
    (2, 52.3, 17, 22, 'punch'),   # 8th annual Pinktober
    (4, 12.0, 22, 24, 'flash'),   # Saturday
    (3, 20.0, 24, 27, 'glitch'),  # October 24th
    (2, 26.0, 27, 30, 'whip'),    # raising funds for the
    (4, 27.0, 30, 32, 'punch'),   # Pink Program
    (1, 28.5, 32, 35, 'whip'),    # bringing dance
    (9, 20.0, 35, 37, 'punch'),   # wellness
    (3, 93.0, 37, 40, 'glitch'),  # to breast cancer survivors
    (6, 15.0, 40, 43, 'whip'),    # and thrivers
]
END_T = 43 * BEAT

# ---------------- kinetic text: (t_in, t_out, kind, size, text, color, y, anim) ----------------
# VO sits at t = src - 0.48; word starts from the transcription
def v(src): return src - 0.48
TEXT = [
    (v(0.84), v(2.02), 'thin', 160, 'DANCE', WHITE, 0.43, 'ghost', 24),
    (v(1.18), v(2.02), 'script', 200, 'for a cause', PINK, 0.515, 'ghost', 0),
    (v(2.36), v(3.26), 'heavy', 150, 'SALSA &', WHITE, 0.44, 'pop', 0),
    (v(2.90), v(3.26), 'heavy', 165, 'BACHATA', PINK, 0.525, 'pop', 0),
    (v(3.26), v(4.82), 'thin', 96, 'LATIN DANCE', WHITE, 0.40, 'ghost', 18),
    (v(3.94), v(4.82), 'heavy', 175, 'SOCIAL', WHITE, 0.48, 'pop', 0),
    (v(4.40), v(4.82), 'heavy', 175, 'PARTY', PINK, 0.565, 'pop', 0),
    (v(5.24), v(6.06), 'bold', 150, 'join us', WHITE, 0.45, 'bounce', 0),
    (v(5.74), v(6.06), 'semi', 110, 'for the', WHITE, 0.525, 'bounce', 0),
    (v(6.10), v(7.50), 'bold', 100, '8TH ANNUAL', WHITE, 0.39, 'ghost', 16),
    (v(6.86), v(7.50), 'script', 300, 'Pinktober', PINK, 0.49, 'neonpop', 0),
    (v(7.62), v(8.94), 'thin', 124, 'SATURDAY', WHITE, 0.42, 'ghost', 20),
    (v(7.84), v(8.94), 'date', 128, 'October|24|th', WHITE, 0.505, 'ghost', 0),
    (v(8.94), v(10.66), 'bold', 112, 'raising funds', WHITE, 0.40, 'bounce', 0),
    (v(9.74), v(10.66), 'semi', 96, 'for the', WHITE, 0.46, 'bounce', 0),
    (v(10.10), v(10.66), 'heavy', 175, 'PINK', PINK, 0.535, 'pop', 0),
    (v(10.26), v(10.66), 'heavy', 140, 'PROGRAM', PINK, 0.61, 'pop', 0),
    (v(10.66), v(12.02), 'bold', 112, 'bringing', WHITE, 0.41, 'bounce', 0),
    (v(11.26), v(12.02), 'heavy', 165, 'DANCE', WHITE, 0.49, 'pop', 0),
    (v(11.72), v(12.02), 'script', 230, 'wellness', PINK, 0.575, 'neonpop', 0),
    (v(12.02), END_T, 'bold', 100, 'to breast cancer', WHITE, 0.385, 'bounce', 0),
    (v(12.74), END_T, 'heavy', 140, 'SURVIVORS', WHITE, 0.46, 'pop', 0),
    (v(13.20), END_T, 'heavy', 140, '& THRIVERS', PINK, 0.535, 'pop', 0),
]
# end card
END_TEXT = [
    (END_T + 0.05, TOTAL, 'script', 230, 'Pinktober', PINK, 0.235, 'neonpop', 0),
    (END_T + 0.20, TOTAL, 'bold', 54, 'SATURDAY · OCTOBER 24TH', WHITE, 0.315, 'ghost', 10),
    (END_T + 0.45, TOTAL, 'semi', 76, 'Harnessing Wellness', WHITE, 0.665, 'ghost', 0),
    (END_T + 0.55, TOTAL, 'semi', 76, 'Through Dance', WHITE, 0.715, 'ghost', 0),
]

# ---------------- text rendering ----------------
def text_img(kind, size, text, color, tracking):
    """RGBA element with neon glow (glow strength by style)."""
    if kind == 'date':  # "October 24th": October white, 24 pink, th superscript pink
        a, b, c = text.split('|')
        fA, fB, fC = F('bold', size), F('bold', size), F('bold', int(size * 0.5))
        wa = fA.getlength(a + ' '); wb = fB.getlength(b); wc = fC.getlength(c)
        tw = int(wa + wb + wc) + 4; th = int(size * 1.3)
        core = Image.new('RGBA', (tw, th), (0, 0, 0, 0)); d = ImageDraw.Draw(core)
        asc = fA.getmetrics()[0]
        d.text((0, 0), a, font=fA, fill=WHITE + (255,))
        d.text((wa, 0), b, font=fB, fill=PINK + (255,))
        d.text((wa + wb + 2, asc - fC.getmetrics()[0] - int(size * 0.28)), c, font=fC, fill=PINK + (255,))
        return glowify(core, PINK_GLOW, 0.75)
    f = F(kind, size)
    if tracking:
        widths = [f.getlength(ch) for ch in text]
        tw = int(sum(widths) + tracking * (len(text) - 1)) + 8
    else:
        tw = int(f.getlength(text)) + 8
    asc, desc = f.getmetrics()
    th = asc + desc + (int(size * 0.35) if kind == 'script' else 6)
    pad_x = int(size * 0.25) if kind == 'script' else 0
    core = Image.new('RGBA', (tw + 2 * pad_x, th), (0, 0, 0, 0)); d = ImageDraw.Draw(core)
    if tracking:
        x = pad_x
        for ch, wch in zip(text, widths):
            d.text((x, 0), ch, font=f, fill=color + (255,)); x += wch + tracking
    else:
        d.text((pad_x, int(size * 0.12) if kind == 'script' else 0), text, font=f, fill=color + (255,))
    if kind == 'script':  # neon tube: thicker stroke, near-white core, pink halo
        a = core.getchannel('A').filter(ImageFilter.MaxFilter(5))
        core = Image.new('RGBA', core.size, (NEON_CORE if color == PINK else WHITE) + (0,)); core.putalpha(a)
        return glowify(core, PINK_GLOW, 1.5)
    strength = 1.2 if color == PINK else 0.55
    return glowify(core, PINK_GLOW if color == PINK else (255, 200, 235), strength)

def glowify(core, gcol, strength):
    pad = 60
    W2, H2 = core.width + 2 * pad, core.height + 2 * pad
    out = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    a = Image.new('L', (W2, H2), 0); a.paste(core.getchannel('A'), (pad, pad))
    for r, k in [(28, 0.55), (12, 0.75), (4, 0.6)]:
        g = a.filter(ImageFilter.GaussianBlur(r)).point(lambda p, k=k: min(255, int(p * k * strength * 1.6)))
        lay = Image.new('RGBA', (W2, H2), gcol + (0,)); lay.putalpha(g)
        out.alpha_composite(lay)
    # dark halo so the type separates from bright shirts and pink outfits
    light = gcol != PINK_GLOW
    sh = a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(16 if light else 12)).point(
        lambda p: min(255, int(p * (1.25 if light else 0.75))))
    shadow = Image.new('RGBA', (W2, H2), (18, 0, 14, 0)); shadow.putalpha(sh)
    base = Image.new('RGBA', (W2, H2), (0, 0, 0, 0)); base.alpha_composite(shadow)
    if not light: base.alpha_composite(out)
    base.alpha_composite(core, (pad, pad))
    return base

_cache = {}
def element(e):
    key = e[2:5] + (e[8],)
    if key not in _cache: _cache[key] = text_img(e[2], e[3], e[4], e[5], e[8])
    return _cache[key]

def ease_out(x): return 1 - (1 - x) ** 3
def ease_back(x, s=1.9): return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2

def draw_element(frame, e, T):
    t_in, t_out, kind, size, text, color, y, anim, _ = e
    if not (t_in <= T < t_out): return
    img = element(e); u = (T - t_in)
    dur = 0.18 if anim in ('ghost',) else 0.14
    x = min(1, u / dur)
    blur = 0; alpha = 1.0; sc = 1.0; dy = 0
    if anim == 'ghost':     # blur-in from larger, like the reference's soft fades
        sc = 1.25 - 0.25 * ease_out(x); alpha = ease_out(x); blur = int(14 * (1 - x))
    elif anim == 'pop':     # punchy overshoot
        sc = 0.55 + 0.45 * ease_back(x); alpha = min(1, x * 2.5)
    elif anim == 'bounce':  # drop in from above with bounce
        dy = -60 * (1 - ease_back(x, 2.4)); alpha = min(1, x * 2)
    elif anim == 'neonpop': # neon flicker + pop
        sc = 0.7 + 0.3 * ease_back(x, 1.4); alpha = 1.0 if (u > 0.2 or int(u * 30) % 3 != 1) else 0.35
    # exit: quick fade in the last 2 frames
    if t_out - T < 2 / FPS and t_out < TOTAL - 0.01: alpha *= 0.5
    if sc != 1.0: img = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BILINEAR)
    if blur: img = img.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1:
        img = img.copy(); img.putalpha(img.getchannel('A').point(lambda p: int(p * alpha)))
    frame.alpha_composite(img, (W // 2 - img.width // 2, int(H * y - img.height / 2 + dy)))

# ---------------- footage ----------------
VIGNETTE = None
def vignette():
    """Edge vignette plus a soft dark band where the type sits, so pink words read over pink outfits."""
    global VIGNETTE
    if VIGNETTE is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        vg = np.clip(1.05 - 0.42 * r ** 2.2, 0.45, 1.0)
        band = 1 - 0.38 * np.exp(-((yy / H - 0.49) / 0.13) ** 2)
        VIGNETTE = (vg * band * 0.92)[..., None].astype(np.float32)
    return VIGNETTE

GRADE = ('eq=contrast=1.10:saturation=1.38:gamma=0.96,'
         'colorbalance=rs=0.05:gs=-0.04:bs=0.04:rm=0.06:gm=-0.05:bm=0.03:rh=0.03:gh=-0.02:bh=0.02')

def shot_frames(clip, src_in, n):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{src_in:.3f}', '-i', f'{R}/{C[clip]}', '-t', f'{n / FPS + 0.3:.3f}',
           '-vf', f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},{GRADE}',
           '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE); last = None
    for _ in range(n):
        buf = p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3: last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        yield last
    p.stdout.close(); p.wait()

def zoom(img, z, cx=0.5, cy=0.5):
    if abs(z - 1) < 1e-3: return img
    cw, ch = W / z, H / z
    x0 = min(max(cx * W - cw / 2, 0), W - cw); y0 = min(max(cy * H - ch / 2, 0), H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))

def footage_frame(arr, lt, sdur, tr, T):
    img = Image.fromarray(arr)
    z = 1.03 + 0.07 * (lt / sdur)            # steady push-in
    # on-beat pulse: tiny zoom kick on every beat
    bp = (T % BEAT) / BEAT; z += 0.018 * max(0, 1 - bp * 4)
    if tr in ('punch', 'flash', 'glitch') and lt < 0.16:
        z += 0.16 * (1 - ease_out(lt / 0.16))
    if tr == 'whip' and lt < 0.14:
        z += 0.25 * (1 - ease_out(lt / 0.14))
    img = zoom(img, z)
    if tr == 'whip' and lt < 0.12:
        k = int(28 * (1 - lt / 0.12)); a = np.asarray(img).astype(np.float32)
        acc = sum(np.roll(a, s, axis=0) for s in range(-k, k + 1, max(1, k // 6))) / len(range(-k, k + 1, max(1, k // 6)))
        img = Image.fromarray(acc.astype(np.uint8))
    a = np.asarray(img).astype(np.float32) * vignette()
    if tr == 'glitch' and lt < 0.12:          # RGB split
        s = int(26 * (1 - lt / 0.12)); a[..., 0] = np.roll(a[..., 0], s, axis=1); a[..., 2] = np.roll(a[..., 2], -s, axis=1)
    if tr == 'flash' and lt < 0.1:
        a = a + (255 - a) * (0.85 * (1 - lt / 0.1))
    # bar downbeat light pump
    bar = (T % (4 * BEAT)) / (4 * BEAT); a *= 1 + 0.07 * max(0, 1 - bar * 8)
    return np.clip(a, 0, 255).astype(np.uint8)

# ---------------- end card ----------------
LOGO = Image.open(f'{S}/work/tranqui_logo.png').convert('RGBA')
def end_card(T, bgsrc):
    u = T - END_T
    yy, xx = np.mgrid[0:H:4, 0:W:4].astype(np.float32)
    bg = np.zeros((H // 4, W // 4, 3), np.float32)
    for (cx, cy, r, col, sp) in [(0.25, 0.25, 0.55, (255, 40, 150), 0.6), (0.8, 0.75, 0.6, (170, 20, 120), -0.5), (0.6, 0.45, 0.35, (255, 120, 200), 0.9)]:
        cx2 = cx + 0.08 * math.sin(u * sp * 2); cy2 = cy + 0.06 * math.cos(u * sp * 2)
        d = np.sqrt(((xx / W - cx2) / r) ** 2 + ((yy / H - cy2) / r) ** 2)
        bg += np.array(col, np.float32) * np.clip(1 - d, 0, 1)[..., None] ** 2 * 0.75
    bg = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    foot = Image.fromarray(bgsrc).filter(ImageFilter.GaussianBlur(18))
    img = Image.blend(Image.fromarray((np.asarray(foot) * 0.32).astype(np.uint8)), bg, 0.6).convert('RGBA')
    if u < 0.1:
        a = np.asarray(img.convert('RGB')).astype(np.float32); a += (255 - a) * 0.9 * (1 - u / 0.1)
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
    # logo pop + glow ring
    x = min(1, u / 0.22); sc = 0.4 + 0.6 * ease_back(x, 1.6); size = int(400 * sc)
    lg = LOGO.resize((size, size), Image.LANCZOS)
    glow = Image.new('RGBA', (size + 160, size + 160), (0, 0, 0, 0))
    m = Image.new('L', glow.size, 0); ImageDraw.Draw(m).ellipse((80, 80, 80 + size, 80 + size), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(30)).point(lambda p: int(p * 0.8 * min(1, x * 2)))
    gl = Image.new('RGBA', glow.size, (255, 60, 170, 0)); gl.putalpha(m)
    cy = int(H * 0.49)
    img.alpha_composite(gl, (W // 2 - glow.width // 2, cy - glow.height // 2))
    lg.putalpha(lg.getchannel('A').point(lambda p: int(p * min(1, x * 3))))
    img.alpha_composite(lg, (W // 2 - size // 2, cy - size // 2))
    # sparkle glint on the ring (like the reference)
    st = u - 0.75
    if 0 <= st < 0.45:
        k = math.sin(math.pi * st / 0.45); d = ImageDraw.Draw(img)
        gx, gy = W // 2 + int(0.33 * 400), cy - int(0.36 * 400); r = int(70 * k)
        for ang, rr in [(0, r), (90, r), (45, r * 0.4), (135, r * 0.4)]:
            dx, dy = rr * math.cos(math.radians(ang)), rr * math.sin(math.radians(ang))
            d.line((gx - dx, gy - dy, gx + dx, gy + dy), fill=(255, 255, 255, int(255 * k)), width=4)
        d.ellipse((gx - 9, gy - 9, gx + 9, gy + 9), fill=(255, 255, 255, int(255 * k)))
    for e in END_TEXT: draw_element(img, e, T)
    return img

def main():
    enc = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', OUT]
    pe = subprocess.Popen(enc, stdin=subprocess.PIPE)
    fidx = 0; last_arr = None
    for si, (clip, src_in, b0, b1, tr) in enumerate(SHOTS):
        f0, f1 = int(round(b0 * BEAT * FPS)), int(round(b1 * BEAT * FPS))
        sdur = (f1 - f0) / FPS
        for k, arr in enumerate(shot_frames(clip, src_in, f1 - f0)):
            T = fidx / FPS
            frame = Image.fromarray(footage_frame(arr, k / FPS, sdur, tr, T)).convert('RGBA')
            for e in TEXT: draw_element(frame, e, T)
            pe.stdin.write(frame.convert('RGB').tobytes()); fidx += 1; last_arr = arr
            if PREVIEW and k == (f1 - f0) // 2: frame.convert('RGB').save(f'{S}/work/p_{si:02d}.jpg', quality=85)
    # end card over blurred pink-dress footage
    n_end = NF - fidx
    for k, arr in enumerate(shot_frames(4, 22.0, n_end)):
        T = fidx / FPS
        frame = end_card(T, arr)
        pe.stdin.write(frame.convert('RGB').tobytes()); fidx += 1
        if PREVIEW and k in (12, n_end - 2): frame.convert('RGB').save(f'{S}/work/p_end{k}.jpg', quality=85)
    pe.stdin.close(); pe.wait()
    json.dump({'end_t': END_T, 'beat': BEAT, 'cuts': [s[2] * BEAT for s in SHOTS], 'trans': [s[4] for s in SHOTS],
               'pinktober': v(6.86), 'frames': fidx}, open(f'{S}/work/timeline.json', 'w'))
    print('frames', fidx)

main()
