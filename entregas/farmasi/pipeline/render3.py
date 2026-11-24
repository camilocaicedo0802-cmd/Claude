"""v2: motion-graphics style after the reference (text behind subject, kinetic type,
glass chart card, full-screen scene with photo cards, light leak / zoom-blur transitions)."""
import subprocess, sys, os, math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import edl2 as edl

SP = sys.argv[1]
OUT = sys.argv[2]
ONLY = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
os.chdir(SP)
sys.path.insert(0, "scripts")
import matte  # noqa: E402

W, H, FPS = edl.W, edl.H, edl.FPS
T = edl.src_to_out
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

WHITE = (255, 255, 255)
INK = (40, 18, 52)
RED = (255, 64, 76)
LILAC_LIGHT = ((206, 150, 255), (126, 56, 204))   # gradient top/bottom on dark-ish bg
LILAC_DARK = ((150, 84, 214), (84, 30, 140))       # gradient on white walls
RED_G = ((255, 120, 120), (220, 30, 50))
WHITE_G = ((255, 255, 255), (232, 228, 240))
LINE_RED = (255, 76, 90)
LINE_LILAC = (196, 140, 255)


@functools.lru_cache(None)
def font(name, size):
    return ImageFont.truetype("fonts/" + name, size)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def ease_out_back(x, s=1.7):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


# ---------------------------------------------------------------- sources
TM = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=100,format=gbrpf32le,"
      "zscale=p=bt709,tonemap=tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
      "")
TH_GRADE = "null"


def ffmpeg_frames(args, w, h, n):
    p = subprocess.Popen(["ffmpeg", "-v", "error"] + args + ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    out = []
    for _ in range(n):
        b = p.stdout.read(w * h * 3)
        if len(b) < w * h * 3:
            out.append(out[-1] if out else np.zeros((h, w, 3), np.uint8))
            continue
        out.append(np.frombuffer(b, np.uint8).reshape(h, w, 3))
    p.stdout.close()
    p.wait()
    return out


def zoom_frame(arr, z, center):
    h, w = arr.shape[:2]
    cw, ch = w / z, h / z
    x0 = clamp(center[0] * w - cw / 2, 0, w - cw)
    y0 = clamp(center[1] * h - ch / 2, 0, h - ch)
    return Image.fromarray(arr).resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def fr(t):
    return int(round(t * FPS))


C = edl.CUT
SHOTS = [
    dict(id="S1", kind="th", seg="A", f0=0, f1=fr(C["S2"]), zoom=(1.04, 1.10), center=(0.47, 0.55)),
    dict(id="S2", kind="broll", src="raw/apoyo2.mov", start=5.85, speed=0.62,
         f0=fr(C["S2"]), f1=fr(C["S3"]), zoom=1.08, center=(0.5, 0.62)),
    dict(id="S3", kind="scene", f0=fr(C["S3"]), f1=fr(C["S4"])),
    dict(id="S4", kind="th", seg="C1", f0=fr(C["S4"]), f1=fr(C["S5"]), zoom=(1.10, 1.15), center=(0.47, 0.56)),
    dict(id="S5", kind="broll", src="raw/apoyo3.mov", start=0.0, speed=0.75,
         f0=fr(C["S5"]), f1=fr(C["S6"]), zoom=1.06, center=(0.5, 0.55), matte="birefnet"),
    dict(id="S6", kind="broll", src="raw/apoyo1.mov", start=11.95, speed=0.85,
         f0=fr(C["S6"]), f1=fr(C["S7a"]), zoom=1.30, center=(0.44, 0.62)),
    dict(id="S7a", kind="th", seg="C2", f0=fr(C["S7a"]), f1=fr(C["S7b"]), zoom=(1.02, 1.05), center=(0.47, 0.56)),
    dict(id="S7b", kind="th", seg="F", f0=fr(C["S7b"]), f1=fr(C["S7c"]), zoom=(1.12, 1.15), center=(0.47, 0.56)),
    dict(id="S7c", kind="th", seg="F", f0=fr(C["S7c"]), f1=edl.NFRAMES, zoom=(1.16, 1.24), center=(0.47, 0.63)),
]
SH = {s["id"]: s for s in SHOTS}


def load_shot(s):
    n = s["f1"] - s["f0"]
    if s["kind"] == "th":
        src0 = edl.out_to_src(s["seg"], s["f0"] / FPS)
        args = ["-ss", f"{src0:.4f}", "-i", "raw/toma_ugc.mov", "-an", "-vf",
                f"setpts=(PTS-STARTPTS)/{edl.SPEED},fps={FPS},{TH_GRADE}", "-frames:v", str(n)]
        return ffmpeg_frames(args, 720, 1280, n)
    if s["kind"] == "broll":
        z, (cx, cy) = s["zoom"], s["center"]
        args = ["-ss", f"{s['start']:.4f}", "-i", s["src"], "-an", "-vf",
                f"setpts=(PTS-STARTPTS)/{s['speed']},fps={FPS},"
                f"crop=w=iw/{z}:h=ih/{z}:x=(iw-iw/{z})*{cx}:y=(ih-ih/{z})*{cy},{TM},"
                f"scale={W}:{H}:flags=lanczos", "-frames:v", str(n)]
        return ffmpeg_frames(args, W, H, n)
    return [None] * n


# ---------------------------------------------------------------- matte cache
os.makedirs("work/mattes3", exist_ok=True)


def get_matte(shot_id, f, im, kind="modnet"):
    p = f"work/mattes3/{shot_id}_{f:03d}_{kind}.png"
    if os.path.exists(p):
        return Image.open(p)
    a = matte.modnet(im) if kind == "modnet" else matte.birefnet(im)
    a.save(p)
    return a


# ---------------------------------------------------------------- typography
def grad_text(text, fnt, grad, tracking=0, glow=0):
    """Text filled with a vertical gradient. Returns RGBA (tight + padding)."""
    asc, desc = fnt.getmetrics()
    widths = [fnt.getlength(c) for c in text]
    tw = int(sum(widths) + tracking * (len(text) - 1))
    pad = 40
    m = Image.new("L", (tw + pad * 2, asc + desc + pad * 2), 0)
    d = ImageDraw.Draw(m)
    x = pad
    for c, w in zip(text, widths):
        d.text((x, pad), c, font=fnt, fill=255)
        x += w + tracking
    bb = m.getbbox()
    mg = 12 + glow * 3
    m2 = Image.new("L", (bb[2] - bb[0] + 2 * mg, bb[3] - bb[1] + 2 * mg), 0)
    m2.paste(m.crop(bb), (mg, mg))
    m = m2
    top, bot = grad
    g = np.linspace(0, 1, m.height)[:, None, None]
    col = (np.array(top)[None, None] * (1 - g) + np.array(bot)[None, None] * g)
    col = np.repeat(col, m.width, axis=1).astype(np.uint8)
    im = Image.fromarray(col, "RGB").convert("RGBA")
    im.putalpha(m)
    if glow:
        gl = Image.new("RGBA", im.size, tuple(bot) + (0,))
        gl.putalpha(m.filter(ImageFilter.GaussianBlur(glow)).point(lambda v: int(v * 0.55)))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.alpha_composite(gl)
        out.alpha_composite(im)
        return out
    return im


@functools.lru_cache(None)
def big_word(text, size, grad_key, maxw=1000):
    grad = {"lilac": LILAC_LIGHT, "lilacd": LILAC_DARK, "red": RED_G, "white": WHITE_G}[grad_key]
    s = size
    while True:
        im = grad_text(text, font("Anton.ttf", s), grad, tracking=2, glow=18 if grad_key != "lilacd" else 0)
        if im.width <= maxw + 40 or s < 80:
            return im
        s = int(s * 0.94)


@functools.lru_cache(None)
def small_word(text, size, color, weight="Inter-Medium.otf", shadow=True):
    f = font(weight, size)
    asc, desc = f.getmetrics()
    w = int(f.getlength(text)) + 40
    im = Image.new("RGBA", (w, asc + desc + 40), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20, 20), text, font=f, fill=color)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(7)).point(lambda v: min(255, int(v * 0.85))))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.alpha_composite(sh, (0, 3))
        out.alpha_composite(im)
        return out
    return im


def put(base, im, cx, cy, alpha=1.0, scale=1.0, blur=0.0, anchor="c"):
    if alpha <= 0.01:
        return
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if blur > 0.4:
        pad = int(blur * 3)
        tmp = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        tmp.alpha_composite(im, (pad, pad))
        im = tmp.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 0.999:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    if anchor == "c":
        x, y = cx - im.width / 2, cy - im.height / 2
    elif anchor == "l":
        x, y = cx, cy - im.height / 2
    else:
        x, y = cx - im.width, cy - im.height / 2
    base.alpha_composite(im, (int(x), int(y)))


def reveal(t, t0, dur=0.22):
    """progress 0..1 -> (alpha, blur, dy, scale)"""
    k = clamp((t - t0) / dur)
    e = ease_out(k)
    return e, 9 * (1 - e), 28 * (1 - e), 1.0


def big_reveal(base, word, size, grad, cx, cy, t, t0, maxw=1000):
    if t < t0:
        return
    im = big_word(word, size, grad, maxw)
    k = clamp((t - t0) / 0.38)
    e = ease_out(k)
    # vertical wipe from the bottom + blur + slight scale
    if k < 1:
        im = im.copy()
        h = im.height
        cut = int(h * (1 - e))
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rectangle((0, cut, im.width, h), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(14))
        im.putalpha(ImageChops.multiply(im.getchannel("A"), mask))
    put(base, im, cx, cy + 20 * (1 - e), alpha=min(1, e * 1.5), scale=1.06 - 0.06 * e, blur=7 * (1 - e))


def kinetic_line(base, words, cx, cy, t, size=44, color=WHITE, gap=14, shadow=True):
    """words: list of (text, t_in). Centered line; each word blurs/slides in at its time."""
    imgs = [small_word(w, size, color, shadow=shadow) for w, _ in words]
    tw = sum(i.width - 40 for i in imgs) + gap * (len(imgs) - 1)
    x = cx - tw / 2
    for (w, t0), im in zip(words, imgs):
        if t >= t0:
            a, b, dy, _ = reveal(t, t0, 0.28)
            put(base, im, x - 20, cy + dy, alpha=a, blur=b, anchor="l")
        x += im.width - 40 + gap


# ---------------------------------------------------------------- glass chart card
CARD_W, CARD_H = 820, 360
BASE = 0.16


def red_curve(x):
    u = max(x, 1e-6) / 0.30
    return BASE + 0.74 * (u ** 1.2) * math.exp(1.2 * (1 - u))


def lilac_curve(x):
    u = max(x, 1e-6) / 0.27
    return BASE + 0.40 * (u ** 2.4) * math.exp(2.4 * (1 - u))


@functools.lru_cache(None)
def card_bg():
    S = 2
    im = Image.new("RGBA", (CARD_W * S, CARD_H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, CARD_W * S - 1, CARD_H * S - 1), radius=34 * S, fill=(22, 14, 40, 212),
                        outline=(255, 255, 255, 70), width=2 * S)
    # top sheen
    sheen = Image.new("L", im.size, 0)
    ImageDraw.Draw(sheen).rounded_rectangle((0, 0, CARD_W * S - 1, CARD_H * S - 1), radius=34 * S, fill=40)
    g = np.linspace(1, 0, im.height)[:, None] ** 2
    sheen = Image.fromarray((np.asarray(sheen) * g).astype(np.uint8))
    white = Image.new("RGBA", im.size, (255, 255, 255, 0))
    white.putalpha(sheen)
    im.alpha_composite(white)
    im = im.resize((CARD_W, CARD_H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.text((34, 24), "Glucosa", font=font("Inter-SemiBold.otf", 34), fill=(255, 255, 255, 235))
    d.text((34, 66), "después de comer", font=font("Inter-Regular.otf", 22), fill=(255, 255, 255, 140))
    for i in range(1, 4):
        y = 120 + i * 52
        d.line((34, y, CARD_W - 34, y), fill=(255, 255, 255, 22), width=2)
    return im


PL, PR, PT, PB = 40, CARD_W - 40, 120, 320


def curve_pts(fn, p):
    n = max(2, int(160 * p))
    return [(PL + (PR - PL) * p * i / (n - 1), PB - (PB - PT) * fn(p * i / (n - 1))) for i in range(n)]


def glow_line(card, pts, color, width=6, alpha=255):
    if len(pts) < 2:
        return
    S = 2
    lay = Image.new("RGBA", (CARD_W * S, CARD_H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    sp = [(x * S, y * S) for x, y in pts]
    d.line(sp, fill=color + (alpha,), width=width * S, joint="curve")
    lay = lay.resize((CARD_W, CARD_H), Image.LANCZOS)
    glow = lay.filter(ImageFilter.GaussianBlur(10))
    card.alpha_composite(glow)
    card.alpha_composite(glow)
    card.alpha_composite(lay)
    x, y = pts[-1]
    dd = ImageDraw.Draw(card)
    dd.ellipse((x - 9, y - 9, x + 9, y + 9), fill=WHITE, outline=color, width=4)


@functools.lru_cache(None)
def legend(text, color):
    f = font("Inter-Medium.otf", 23)
    w = int(f.getlength(text)) + 46
    im = Image.new("RGBA", (w, 38), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 35), radius=18, fill=(255, 255, 255, 18), outline=color + (150,), width=2)
    d.ellipse((12, 12, 24, 24), fill=color)
    d.text((32, 6), text, font=f, fill=(255, 255, 255, 220))
    return im


def find_coeffs(pa, pb):
    A = []
    for p1, p2 in zip(pa, pb):
        A.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        A.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.array(A, float)
    B = np.array(pb, float).reshape(8)
    return np.linalg.solve(A, B).tolist()


def tilt(im, k=0.05):
    """slight 3D tilt (top edge narrower)"""
    w, h = im.size
    pad = 0
    dst = [(w * k, 0), (w * (1 - k), 0), (w, h), (0, h)]
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    c = find_coeffs(dst, src)
    return im.transform((w, h + pad), Image.PERSPECTIVE, c, Image.BICUBIC)


@functools.lru_cache(None)
def card_shadow():
    im = Image.new("RGBA", (CARD_W + 120, CARD_H + 120), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((60, 70, 60 + CARD_W, 70 + CARD_H), radius=34, fill=(0, 0, 0, 120))
    return im.filter(ImageFilter.GaussianBlur(26))


def draw_card(base, t, cy, t_in, red_p, lil_p, show_lilac_legend, exit_k=0.0, red_alpha=255):
    k = ease_out((t - t_in) / 0.35)
    if k <= 0:
        return
    card = card_bg().copy()
    card.alpha_composite(legend("sin vinagre", LINE_RED), (CARD_W - 34 - legend("sin vinagre", LINE_RED).width
                                                           - (legend("con vinagre de manzana", LINE_LILAC).width + 10
                                                              if show_lilac_legend else 0), 30))
    if show_lilac_legend:
        lg = legend("con vinagre de manzana", LINE_LILAC)
        card.alpha_composite(lg, (CARD_W - 34 - lg.width, 30))
    if red_p > 0:
        glow_line(card, curve_pts(red_curve, red_p), LINE_RED, 6, red_alpha)
    if lil_p > 0:
        glow_line(card, curve_pts(lilac_curve, lil_p), LINE_LILAC, 7)
    card = tilt(card, 0.035)
    bob = 6 * math.sin(t * 2.2)
    a = k * (1 - exit_k)
    blur = 8 * (1 - k) + 10 * exit_k
    sc = 0.92 + 0.08 * k + 0.05 * exit_k
    put(base, card_shadow(), W / 2, cy + 30 * (1 - k) + bob + 14, alpha=a * 0.8, scale=sc)
    put(base, card, W / 2, cy + 40 * (1 - k) + bob, alpha=a, blur=blur, scale=sc)


# ---------------------------------------------------------------- full-screen scene (S3)
@functools.lru_cache(None)
def scene_bg():
    y = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array([232, 219, 246]), np.array([251, 248, 253])
    bg = (top * (1 - y) + bot * y).repeat(W, axis=1)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / 520) ** 2 + ((yy - 1000) / 640) ** 2)
    glow = np.clip(1 - r, 0, 1)[..., None] ** 2
    bg = bg * (1 - glow * 0.5) + np.array([214, 182, 244]) * glow * 0.5
    return Image.fromarray(bg.astype(np.uint8), "RGB").convert("RGBA")


@functools.lru_cache(None)
def photo_card(path, title, chip, chip_color, crop_y=0.4):
    pw, ph = 440, 520
    im = Image.open(path).convert("RGB")
    sc = pw / im.width
    im = im.resize((pw, int(im.height * sc)), Image.LANCZOS)
    y0 = int((im.height - ph) * crop_y)
    im = im.crop((0, y0, pw, y0 + ph))
    fh = 118
    S = 2
    card = Image.new("RGBA", ((pw + 24) * S, (ph + fh + 24) * S), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=30 * S, fill=WHITE)
    card = card.resize((pw + 24, ph + fh + 24), Image.LANCZOS)
    m = Image.new("L", (pw * S, ph * S), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, pw * S - 1, ph * S - 1), radius=22 * S, fill=255)
    m = m.resize((pw, ph), Image.LANCZOS)
    card.paste(im, (12, 12), m)
    d = ImageDraw.Draw(card)
    d.text((26, ph + 28), title, font=font("Inter-SemiBold.otf", 28), fill=INK)
    f = font("Inter-SemiBold.otf", 21)
    cw = int(f.getlength(chip)) + 30
    d.rounded_rectangle((26, ph + 76, 26 + cw, ph + 112), radius=18, fill=(255, 226, 230))
    d.text((41, ph + 82), chip, font=f, fill=chip_color)
    d.text((26 + cw + 14, ph + 82), "después de comer", font=f, fill=(140, 128, 156))
    sh = Image.new("RGBA", (card.width + 120, card.height + 120), (0, 0, 0, 0))
    shm = Image.new("L", sh.size, 0)
    ImageDraw.Draw(shm).rounded_rectangle((60, 80, 60 + card.width, 80 + card.height), radius=30, fill=110)
    sh.putalpha(shm.filter(ImageFilter.GaussianBlur(28)))
    sh2 = Image.new("RGBA", sh.size, (60, 20, 90, 0))
    sh2.putalpha(sh.getchannel("A"))
    out = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    out.alpha_composite(sh2)
    out.alpha_composite(card, (60, 60))
    return out


def draw_scene(t):
    s = SH["S3"]
    t0 = s["f0"] / FPS
    lt = t - t0
    base = scene_bg().copy()
    k = ease_out_back(lt / 0.42, 1.4)
    ke = ease_out(lt / 0.42)
    cards = [
        ("stock/cgm.jpg", "Monitor de glucosa", "↑ sube", RED, -1, 0.15),
        ("stock/glucometro_prueba.jpg", "Prueba en casa", "↑ sube", RED, 1, 0.35),
    ]
    for path, title, chip, col, side, cy_ in cards:
        im = photo_card(path, title, chip, col, cy_)
        ang = -side * 9 * ke
        im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
        x = W / 2 + side * 290 * k
        put(base, im, x, 1010 + 20 * (1 - ke), alpha=ke, scale=0.92, blur=1.2)
    front = photo_card("stock/glucometro_lectura.jpg", "Medición de glucosa", "↑ 8.4 mmol/L", RED, 0.38)
    put(base, front, W / 2, 990 + 50 * (1 - ke), alpha=min(1, lt / 0.12), scale=1.0 + 0.1 * k)
    kinetic_line(base, [("la", C["S3"] + 0.04)], W / 2, 300, t, size=46, color=INK, shadow=False)
    big_reveal(base, "GLUCOSA", 250, "lilacd", W / 2, 430, t, C["S3"] + 0.12)
    if t >= T(35.85):
        big_reveal(base, "SUBE", 300, "red", W / 2 + 80, 1640, t, T(35.85))
        # arrow
        ka = ease_out((t - T(35.85)) / 0.35)
        ar = arrow_img()
        put(base, ar, W / 2 - 250, 1640 + 60 * (1 - ka) - 10, alpha=ka)
    # slow push-in on the whole scene
    z = 1.0 + 0.045 * ease_in_out(lt / 1.6)
    im = base.convert("RGB")
    if z > 1.001:
        cw, ch = W / z, H / z
        im = im.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
    return im.convert("RGBA")


@functools.lru_cache(None)
def arrow_img():
    S = 2
    w, h = 130, 200
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(w / 2 * S, 0), (w * S, 80 * S), (78 * S, 80 * S), (78 * S, h * S), (52 * S, h * S),
               (52 * S, 80 * S), (0, 80 * S)], fill=(236, 40, 58))
    return im.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- transitions
def light_leak(img, strength, phase):
    """additive warm light leak"""
    if strength <= 0.01:
        return img
    yy, xx = np.mgrid[0:H:4, 0:W:4]
    acc = np.zeros(xx.shape + (3,), np.float32)
    blobs = [((0.15 + 0.9 * phase) * W, 0.35 * H, 520, (255, 120, 40)),
             ((1.0 - 0.7 * phase) * W, 0.7 * H, 600, (255, 60, 120)),
             ((0.5 + 0.2 * math.sin(phase * 3)) * W, 0.15 * H, 420, (255, 220, 160))]
    for bx, by, r, col in blobs:
        d = np.sqrt((xx - bx) ** 2 + (yy - by) ** 2) / r
        acc += np.clip(1 - d, 0, 1)[..., None] ** 1.6 * np.array(col, np.float32)
    acc = np.clip(acc * strength, 0, 255).astype(np.uint8)
    leak = Image.fromarray(acc, "RGB").resize((W, H), Image.BILINEAR)
    return ImageChops.screen(img.convert("RGB"), leak).convert("RGBA")


def zoom_blur(img, amount):
    if amount <= 0.01:
        return img
    rgb = np.asarray(img.convert("RGB"), np.float32)
    acc = rgb.copy()
    n = 6
    for i in range(1, n):
        z = 1 + amount * 0.12 * i / n
        cw, ch = W / z, H / z
        acc += np.asarray(img.convert("RGB").resize((W, H), Image.BILINEAR,
                                                    box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2)),
                          np.float32)
    return Image.fromarray((acc / n).astype(np.uint8), "RGB").convert("RGBA")


def darken_top(img, strength=0.5):
    g = np.clip(1 - np.linspace(0, 1, H) / 0.55, 0, 1) ** 1.4
    a = (g * 255 * strength).astype(np.uint8)
    mask = Image.fromarray(np.repeat(a[:, None], W, axis=1), "L")
    over = Image.new("RGBA", (W, H), (26, 14, 38, 0))
    over.putalpha(mask)
    img.alpha_composite(over)
    return img


@functools.lru_cache(None)
def vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.5) / (H * 0.62)) ** 2)
    a = (np.clip(r - 0.55, 0, 1) * 200).astype(np.uint8)
    v = Image.new("RGBA", (W, H), (10, 6, 16, 0))
    v.putalpha(Image.fromarray(a, "L"))
    return v


# ---------------------------------------------------------------- per-shot design
def stag(words, t0, step=0.10):
    return [(w, t0 + i * step) for i, w in enumerate(words)]


def layers_for(sid, t):
    """phrase-level cues: every phrase appears at once (short stagger) and holds for the whole shot"""
    def behind(b):
        if sid == "S1":
            big_reveal(b, "COME", 380, "lilac", W / 2, 640, t, C["S1"] + 0.12)
        elif sid == "S4":
            big_reveal(b, "TIEMPO", 360, "lilac", W / 2, 610, t, C["S4"] + 0.35)
        elif sid == "S5":
            big_reveal(b, "LE AYUDA", 300, "lilacd", W / 2, 520, t, C["S5"] + 0.14)
        elif sid == "S7a":
            big_reveal(b, "GLUCOSA", 330, "lilac", W / 2, 660, t, C["S7a"] + 0.18)
        elif sid == "S7b":
            big_reveal(b, "ARRIBA", 360, "red", W / 2, 520, t, T(43.92))
        elif sid == "S7c":
            ex = ease_out((t - T(46.15)) / 0.22)
            if ex < 1:
                bb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                big_reveal(bb, "BAJE", 400, "lilac", W / 2, 470, t, C["S7c"] + 0.2)
                if ex > 0:
                    bb.putalpha(bb.getchannel("A").point(lambda v: int(v * (1 - ex))))
                b.alpha_composite(bb)

    def front(b):
        if sid == "S1":
            kinetic_line(b, stag(["cuando"], C["S1"] + 0.03), W / 2, 430, t, size=50)
        elif sid == "S5":
            kinetic_line(b, stag(["¿qué", "es", "lo", "que"], C["S5"] + 0.03, 0.07), W / 2, 330, t, size=50,
                         color=INK, shadow=False)
        elif sid == "S7a":
            kinetic_line(b, stag(["a", "que", "esa"], C["S7a"] + 0.03, 0.08), W / 2, 450, t, size=50)
        if sid == "S4":
            kinetic_line(b, stag(["y", "demora", "mucho"], C["S4"] + 0.06), W / 2, 400, t, size=50)
        if sid == "S7b":
            kinetic_line(b, stag(["no", "quede", "por", "tanto", "tiempo"], C["S7b"] + 0.05, 0.09), W / 2, 300, t,
                         size=48)
        if sid == "S7c" and t < T(46.15) + 0.22:
            ex = ease_out((t - T(46.15)) / 0.22)
            bb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            kinetic_line(bb, stag(["sino", "que"], C["S7c"] + 0.03), W / 2, 260, t, size=48)
            if ex > 0:
                bb.putalpha(bb.getchannel("A").point(lambda v: int(v * (1 - ex))))
            b.alpha_composite(bb)
        if sid == "S2":
            big_reveal(b, "CUALQUIER", 240, "lilacd", W / 2, 290, t, C["S2"] + 0.04)
            big_reveal(b, "COSA", 240, "lilacd", W / 2, 545, t, C["S2"] + 0.18)
            kinetic_line(b, stag(["que", "coma"], C["S2"] + 0.34), W / 2, 725, t, size=52, color=INK, shadow=False)
        elif sid == "S4":
            rp = ease_in_out((t - (C["S4"] + 0.12)) / 1.9)
            draw_card(b, t, 1440, C["S4"] + 0.02, rp, 0, False)
        elif sid == "S6":
            kinetic_line(b, stag(["la"], C["S6"] + 0.03), W / 2, 300, t, size=52, color=INK, shadow=False)
            big_reveal(b, "SIDRA DE", 230, "lilacd", W / 2, 440, t, C["S6"] + 0.10)
            big_reveal(b, "MANZANA?", 230, "lilacd", W / 2, 650, t, C["S6"] + 0.24)
        elif sid in ("S7b", "S7c"):
            t_in = C["S7b"]
            g1 = 0.44 * ease_out((t - t_in) / (C["S7c"] - t_in))
            g2 = 0.56 * ease_in_out((t - (C["S7c"] + 0.08)) / 1.35)
            ex = ease_out((t - T(46.15)) / 0.22)
            if ex < 1:
                draw_card(b, t, 1480, t_in + 0.02, 1.0, g1 + g2, True, ex, 170)
            if sid == "S7c" and t >= T(46.15) + 0.04:
                kinetic_line(b, stag(["mucho"], T(46.15) + 0.04), W / 2, 1180, t, size=54)
                big_reveal(b, "MÁS RÁPIDO", 260, "white", W / 2, 1390, t, T(46.15) + 0.16, maxw=960)
    return behind, front


# ---------------------------------------------------------------- main
def main():
    need = set(ONLY) if ONLY else None
    enc = None
    if not ONLY:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "work/mix3.wav",
                                "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                                "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                                "-shortest", OUT], stdin=subprocess.PIPE)
    cut_frames = [s["f0"] for s in SHOTS[1:]]
    for s in SHOTS:
        rng = range(s["f0"], s["f1"])
        if need is not None and not any(f in need for f in rng):
            continue
        src = load_shot(s)
        n = s["f1"] - s["f0"]
        prev_a = None
        for i, f in enumerate(rng):
            if need is not None and f not in need and s["kind"] != "th":
                continue
            t = f / FPS
            k = i / max(1, n - 1)
            punch = 1 + 0.06 * (1 - ease_out(i / 6)) if s["id"] != "S1" else 1.0
            sid = s["id"]
            behind, front = layers_for(sid, t)
            if s["kind"] == "scene":
                base = draw_scene(t)
            else:
                if s["kind"] == "th":
                    z0, z1 = s["zoom"]
                    z = (z0 + (z1 - z0) * ease_in_out(k)) * punch
                    im = zoom_frame(src[i], z, s["center"])
                else:
                    im = zoom_frame(src[i], punch, (0.5, 0.5)) if punch > 1.0005 else Image.fromarray(src[i])
                base = im.convert("RGBA")
                person = None
                mk = "modnet" if s["kind"] == "th" else s.get("matte")
                if mk:
                    a = get_matte(sid, f, im, mk)
                    if prev_a is not None and mk == "modnet":
                        a = Image.blend(prev_a, a, 0.7)
                    prev_a = a
                    person = im.convert("RGBA")
                    person.putalpha(a)
                behind(base)
                if person is not None:
                    base.alpha_composite(person)
            if need is not None and f not in need:
                continue
            front(base)
            # transitions
            for cf in cut_frames:
                d = f - cf
                if -3 <= d <= 3 and cf in (SH["S3"]["f0"], SH["S4"]["f0"], SH["S7a"]["f0"]):
                    base = zoom_blur(base, 1 - abs(d) / 4)
            lk0 = SH["S5"]["f0"]
            if lk0 - 4 <= f <= lk0 + 7:
                ph = (f - (lk0 - 4)) / 11
                base = light_leak(base, math.sin(math.pi * ph) * 1.25, ph)
            rgb = base.convert("RGB")
            if ONLY:
                rgb.save(f"{OUT}_{f:03d}.png")
            else:
                enc.stdin.write(rgb.tobytes())
        print(s["id"], "done", flush=True)
    if enc:
        enc.stdin.close()
        enc.wait()


main()
