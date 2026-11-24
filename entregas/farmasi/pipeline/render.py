"""Frame compositor: shots + zooms + hook title + glucose chart + product tag + pop captions."""
import subprocess, sys, os, math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edl

SP = sys.argv[1]
OUT = sys.argv[2]
ONLY = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None  # preview frames
os.chdir(SP)
W, H, FPS = edl.W, edl.H, edl.FPS
F = "fonts/"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

WHITE = (255, 255, 255)
YELLOW = (255, 225, 64)
RED = (255, 72, 72)
GREEN = (120, 226, 92)
INK = (30, 18, 44)
MAUVE = (94, 44, 98)
CHART_RED = (236, 56, 64)
CHART_GREEN = (46, 184, 92)


@functools.lru_cache(None)
def font(name, size):
    return ImageFont.truetype(F + name, size)


@functools.lru_cache(None)
def emoji_img(ch, h):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


# ---------------- easing ----------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_back(x, s=1.9):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


# ---------------- sources ----------------
TM = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=100,format=gbrpf32le,"
      "zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
      "eq=saturation=0.86:contrast=1.03:brightness=0.015")


def ffmpeg_frames(args, w, h, n):
    p = subprocess.Popen(["ffmpeg", "-v", "error"] + args + ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    frames = []
    for _ in range(n):
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            frames.append(frames[-1] if frames else np.zeros((h, w, 3), np.uint8))
            continue
        frames.append(np.frombuffer(buf, np.uint8).reshape(h, w, 3))
    p.stdout.close()
    p.wait()
    return frames


def load_shot(s):
    n = s["f1"] - s["f0"]
    if s["kind"] == "th":
        t0 = s["f0"] / FPS
        src0 = edl.out_to_src(s["seg"], t0)
        args = ["-ss", f"{src0:.4f}", "-i", "raw/toma_ugc.mov", "-an", "-vf",
                f"setpts=(PTS-STARTPTS)/{edl.SPEED},fps={FPS},"
                "eq=contrast=1.07:saturation=1.10:brightness=0.025:gamma=1.03",
                "-frames:v", str(n)]
        return ffmpeg_frames(args, 720, 1280, n)
    if s["kind"] == "broll":
        z = s["zoom"]
        cx, cy = s["center"]
        args = ["-ss", f"{s['start']:.4f}", "-i", s["src"], "-an", "-vf",
                f"setpts=(PTS-STARTPTS)/{s['speed']},fps={FPS},"
                f"crop=w=iw/{z}:h=ih/{z}:x=(iw-iw/{z})*{cx}:y=(ih-ih/{z})*{cy},{TM},"
                f"scale={W}:{H}:flags=lanczos", "-frames:v", str(n)]
        return ffmpeg_frames(args, W, H, n)
    if s["kind"] == "image":
        im = Image.open(s["src"]).convert("RGB")
        # cover-crop to 9:16
        sc = H / im.height
        im = im.resize((int(im.width * sc), H), Image.LANCZOS)
        x0 = int((im.width - W) * 0.42)
        im = im.crop((x0, 0, x0 + W, H))
        return [np.asarray(im)] * n
    raise ValueError(s)


def zoom_frame(arr, z, center, out=(W, H)):
    """Crop arr around center (rel) by zoom z and resize to out (float box -> smooth)."""
    h, w = arr.shape[:2]
    cw, ch = w / z, h / z
    cx, cy = center
    x0 = clamp(cx * w - cw / 2, 0, w - cw)
    y0 = clamp(cy * h - ch / 2, 0, h - ch)
    im = Image.fromarray(arr)
    return im.resize(out, Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


# ---------------- text helpers ----------------
def text_layer(lines, fnt, colors, stroke=10, line_gap=6, emoji=None):
    """lines: list of list of (word, color). Returns RGBA image with stroke + soft shadow."""
    space = fnt.getlength(" ")
    asc, desc = fnt.getmetrics()
    lh = asc + desc
    widths = []
    for ln in lines:
        wd = sum(fnt.getlength(w) for w, _ in ln) + space * (len(ln) - 1)
        widths.append(wd)
    eh = int(lh * 0.82)
    em = emoji_img(emoji, eh) if emoji else None
    if em is not None:
        widths[-1] += space * 0.6 + em.width
    pad = stroke + 24
    Wl = int(max(widths) + pad * 2)
    Hl = int(len(lines) * lh + (len(lines) - 1) * line_gap + pad * 2)
    txt = Image.new("RGBA", (Wl, Hl), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    y = pad
    for li, ln in enumerate(lines):
        x = (Wl - widths[li]) / 2
        for w, c in ln:
            d.text((x, y), w, font=fnt, fill=c, stroke_width=stroke, stroke_fill=(0, 0, 0))
            x += fnt.getlength(w) + space
        if em is not None and li == len(lines) - 1:
            txt.alpha_composite(em, (int(x - space + space * 0.6), int(y + (lh - eh) / 2 - 2)))
        y += lh + line_gap
    # shadow
    a = txt.getchannel("A").filter(ImageFilter.GaussianBlur(10))
    sh = Image.new("RGBA", txt.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * 0.55)))
    out = Image.new("RGBA", txt.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 8))
    out.alpha_composite(txt)
    return out


def paste_scaled(base, layer, cx, cy, scale=1.0, alpha=1.0, angle=0.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    lw, lh = layer.size
    im = layer
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(lw * scale)), max(1, int(lh * scale))), Image.BICUBIC)
    if abs(angle) > 1e-3:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


# ---------------- captions ----------------
CAP_Y = 1470
MAXW = 900


def build_captions():
    groups = []
    for gi, g in enumerate(edl.CAPTIONS):
        words = []
        for w in g:
            text, src = w[0], w[1]
            style = w[2] if len(w) > 2 else None
            emo = w[3] if len(w) > 3 else None
            words.append(dict(text=text, t=edl.src_to_out(src), style=style, emoji=emo))
        groups.append(words)
    out = []
    for gi, words in enumerate(groups):
        t0 = words[0]["t"]
        t1 = groups[gi + 1][0]["t"] if gi + 1 < len(groups) else edl.TOTAL + 1
        out.append(dict(words=words, t0=t0, t1=t1))
    return out


CAPS = build_captions()


@functools.lru_cache(None)
def caption_img(gi, active):
    g = CAPS[gi]["words"]
    single = len(g) == 1
    fnt = font("Montserrat-Black.ttf", 118 if single else 84)
    toks = []
    for wi, w in enumerate(g):
        if w["style"] == "red":
            c = RED
        elif w["style"] == "green":
            c = GREEN
        elif wi == active:
            c = YELLOW
        else:
            c = WHITE
        for part in w["text"].split(" "):
            toks.append((part, c))
    # greedy wrap
    lines, cur = [], []
    for tk in toks:
        trial = cur + [tk]
        wd = sum(fnt.getlength(t) for t, _ in trial) + fnt.getlength(" ") * (len(trial) - 1)
        if cur and wd > MAXW:
            lines.append(cur)
            cur = [tk]
        else:
            cur = trial
    lines.append(cur)
    emo = g[-1]["emoji"]
    return text_layer(lines, fnt, None, stroke=11 if single else 10, emoji=emo)


def draw_captions(base, t):
    for gi, c in enumerate(CAPS):
        if c["t0"] <= t < c["t1"]:
            active = 0
            for wi, w in enumerate(c["words"]):
                if t >= w["t"]:
                    active = wi
            img = caption_img(gi, active)
            k = (t - c["t0"]) / 0.16
            sc = 0.72 + 0.28 * ease_out_back(k)
            al = clamp((t - c["t0"]) / 0.05)
            # tiny bounce when a new word lights up
            wt = c["words"][active]["t"]
            if active > 0:
                sc *= 1 + 0.05 * math.sin(math.pi * clamp((t - wt) / 0.12))
            paste_scaled(base, img, W / 2, CAP_Y, sc, al)
            break


# ---------------- hook title ----------------
@functools.lru_cache(None)
def hook_img():
    fnt = font("Montserrat-Black.ttf", 66)
    lines = [[("¿QUÉ", INK), ("PASA", INK), ("CON", INK), ("TU", INK)],
             [("GLUCOSA", CHART_RED)],
             [("DESPUÉS", INK), ("DE", INK), ("COMER?", INK)]]
    space = fnt.getlength(" ")
    asc, desc = fnt.getmetrics()
    lh = asc + desc - 6
    widths = [sum(fnt.getlength(w) for w, _ in ln) + space * (len(ln) - 1) for ln in lines]
    em = emoji_img("🤔", 74)
    padx, pady = 46, 30
    bw = int(max(widths) + padx * 2)
    bh = int(lh * len(lines) + pady * 2)
    S = 2
    box = Image.new("RGBA", (bw * S + 80, bh * S + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    d.rounded_rectangle((40, 40, 40 + bw * S, 40 + bh * S), radius=34 * S, fill=(255, 255, 255, 255))
    box = box.resize((box.width // S, box.height // S), Image.LANCZOS)
    d = ImageDraw.Draw(box)
    y = 20 + pady
    for li, ln in enumerate(lines):
        x = 20 + (bw - widths[li]) / 2
        for w, c in ln:
            d.text((x, y), w, font=fnt, fill=c)
            x += fnt.getlength(w) + space
        y += lh
    box.alpha_composite(em, (20 + bw - em.width + 26, 20 + bh - em.height + 22))
    a = box.getchannel("A").filter(ImageFilter.GaussianBlur(14))
    out = Image.new("RGBA", (box.width + 40, box.height + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", box.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * 0.35)))
    out.alpha_composite(sh, (20, 34))
    out.alpha_composite(box, (20, 20))
    return out


HOOK_END = edl.OFFS["B"][0]


def draw_hook(base, t):
    if t >= HOOK_END:
        return
    k = t / 0.22
    sc = 0.86 + 0.14 * ease_out_back(k)
    out_k = clamp((HOOK_END - t) / 0.12)
    sc *= 0.6 + 0.4 * ease_out(out_k)
    wob = -3.0 + 1.2 * math.sin(t * 5.0)
    paste_scaled(base, hook_img(), W / 2, 395, sc, min(1, 0.4 + k) * out_k, wob)


# ---------------- product tag ----------------
@functools.lru_cache(None)
def tag_img():
    f1 = font("Montserrat-ExtraBold.ttf", 40)
    f2 = font("Montserrat-SemiBold.ttf", 27)
    t1, t2 = "Gomitas de vinagre de manzana", "Nutriplus · Farmasi"
    em = emoji_img("🍎", 64)
    tw = max(f1.getlength(t1), f2.getlength(t2))
    bw, bh = int(tw + em.width + 100), 132
    S = 2
    im = Image.new("RGBA", (bw * S, bh * S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, bw * S - 1, bh * S - 1), radius=30 * S, fill=MAUVE + (240,))
    im = im.resize((bw, bh), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    im.alpha_composite(em, (28, (bh - em.height) // 2))
    x = 28 + em.width + 22
    d.text((x, 22), t1, font=f1, fill=WHITE)
    d.text((x, 76), t2, font=f2, fill=(240, 214, 236))
    out = Image.new("RGBA", (bw + 40, bh + 50), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.35)))
    out.alpha_composite(sh, (20, 32))
    out.alpha_composite(im, (20, 20))
    return out


SH = {s["id"]: s for s in edl.SHOTS}
TAG_T0 = SH["S5"]["f0"] / FPS
TAG_T1 = SH["S6"]["f1"] / FPS


def draw_tag(base, t):
    if not (TAG_T0 <= t < TAG_T1):
        return
    im = tag_img()
    k = ease_out((t - TAG_T0) / 0.22)
    x = -im.width / 2 + (W / 2 + im.width / 2) * k
    paste_scaled(base, im, x, 300, 1.0, k)


# ---------------- glucose chart ----------------
CX, CY, CW, CH = 50, 118, 980, 650
S = 2  # supersample
PX0, PX1, PY0, PY1 = 96, 940, 190, 506  # plot box in card coords
BASE = 0.18


def red_curve(x):
    u = max(x, 1e-6) / 0.30
    return BASE + 0.72 * (u ** 1.2) * math.exp(1.2 * (1 - u))


def green_curve(x):
    u = max(x, 1e-6) / 0.27
    return BASE + 0.40 * (u ** 2.4) * math.exp(2.4 * (1 - u))


def to_px(x, v):
    return ((PX0 + (PX1 - PX0) * x) * S, (PY1 - (PY1 - PY0) * v) * S)


@functools.lru_cache(None)
def chart_static():
    im = Image.new("RGBA", (CW * S, CH * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, CW * S - 1, CH * S - 1), radius=40 * S, fill=(255, 255, 255, 246))
    # title
    ft = font("Montserrat-ExtraBold.ttf", 40 * S)
    em = emoji_img("🩸", 44 * S)
    im.alpha_composite(em, (40 * S, 30 * S))
    d.text((40 * S + em.width + 14 * S, 30 * S), "TU GLUCOSA DESPUÉS DE COMER", font=ft, fill=INK)
    # axes
    ax = (214, 208, 224)
    d.line([to_px(0, 0), to_px(1, 0)], fill=ax, width=4 * S)
    d.line([to_px(0, 0), to_px(0, 1.02)], fill=ax, width=4 * S)
    # baseline dashed
    x = 0.0
    while x < 1:
        d.line([to_px(x, BASE), to_px(min(1, x + 0.018), BASE)], fill=(170, 162, 184), width=3 * S)
        x += 0.034
    fs = font("Montserrat-SemiBold.ttf", 21 * S)
    d.text(to_px(0.80, BASE + 0.035), "nivel normal", font=fs, fill=(150, 142, 166))
    # axis labels
    fl = font("Montserrat-ExtraBold.ttf", 22 * S)
    lab = Image.new("RGBA", (220 * S, 40 * S), (0, 0, 0, 0))
    ImageDraw.Draw(lab).text((0, 0), "GLUCOSA ↑", font=fl, fill=(122, 112, 136))
    lab = lab.rotate(90, expand=True)
    im.alpha_composite(lab, (40 * S, int(to_px(0, 0.5)[1] - 110 * S)))
    tx = "TIEMPO DESPUÉS DE COMER →"
    d.text((PX1 * S - fl.getlength(tx), (PY1 + 14) * S), tx, font=fl, fill=(122, 112, 136))
    # footnote
    ff = font("Montserrat-SemiBold.ttf", 19 * S)
    d.text((40 * S, 584 * S), "*Gráfica ilustrativa. Estudios pequeños indican que el vinagre puede moderar",
           font=ff, fill=(140, 132, 154))
    d.text((40 * S, 609 * S), "la subida de glucosa después de comer. No reemplaza tratamiento médico.",
           font=ff, fill=(140, 132, 154))
    return im


@functools.lru_cache(None)
def legend_chip(text, color):
    f = font("Montserrat-ExtraBold.ttf", 24 * S)
    w = int(f.getlength(text) + 70 * S)
    h = 46 * S
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=color + (34,))
    d.ellipse((16 * S, 13 * S, 36 * S, 33 * S), fill=color)
    d.text((46 * S, 8 * S), text, font=f, fill=tuple(int(c * 0.78) for c in color))
    return im


@functools.lru_cache(None)
def pill(text, color, emoji):
    f = font("Montserrat-Black.ttf", 30 * S)
    em = emoji_img(emoji, 36 * S)
    w = int(f.getlength(text) + em.width + 64 * S)
    h = 62 * S
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=color)
    im.alpha_composite(em, (22 * S, (h - em.height) // 2))
    d.text((22 * S + em.width + 12 * S, 12 * S), text, font=f, fill=WHITE)
    return im


def draw_curve(d, fn, p, color, alpha=255, width=11):
    if p <= 0.002:
        return None
    n = max(2, int(220 * p))
    pts = [to_px(p * i / (n - 1), fn(p * i / (n - 1))) for i in range(n)]
    # area fill
    poly = [to_px(0, 0)] + pts + [(pts[-1][0], to_px(0, 0)[1])]
    d.polygon(poly, fill=color + (int(38 * alpha / 255),))
    d.line(pts, fill=color + (alpha,), width=width * S, joint="curve")
    r = width * S / 2
    for (x, y) in (pts[0],):
        d.ellipse((x - r, y - r, x + r, y + r), fill=color + (alpha,))
    return pts[-1]


def head_dot(layer, pt, color, t):
    d = ImageDraw.Draw(layer)
    x, y = pt
    pulse = 0.5 + 0.5 * math.sin(t * 12)
    rr = (16 + 8 * pulse) * S
    d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=color + (int(70 + 40 * pulse),))
    r = 11 * S
    d.ellipse((x - r, y - r, x + r, y + r), fill=WHITE, outline=color, width=5 * S)


T_S4 = SH["S4"]["f0"] / FPS
T_S4_END = SH["S4"]["f1"] / FPS
T_S7 = SH["S7a"]["f0"] / FPS
T_STAY = edl.src_to_out(38.98)
T_ARRIBA = edl.src_to_out(44.64)
T_BAJE = edl.src_to_out(45.62)


def chart_state(t):
    if T_S4 <= t < T_S4_END:
        st = dict(enter=(t - T_S4) / 0.24,
                  red=ease_in_out((t - (T_S4 + 0.06)) / 1.75), red_a=255, green=0.0,
                  pill_red=(t - T_STAY) / 0.2 if t >= T_STAY else None, pill_green=None, legend_g=0)
        return st
    if t >= T_S7:
        g1 = 0.44 * ease_out((t - T_S7) / (T_ARRIBA - T_S7))
        g2 = 0.56 * ease_in_out((t - (T_ARRIBA + 0.05)) / 1.9)
        return dict(enter=(t - T_S7) / 0.16, red=1.0, red_a=150, green=g1 + g2,
                    pill_red=None, pill_green=(t - T_BAJE) / 0.2 if t >= T_BAJE else None,
                    legend_g=clamp((t - T_S7) / 0.2))
    return None


def draw_chart(base, t):
    st = chart_state(t)
    if st is None:
        return
    layer = chart_static().copy()
    d = ImageDraw.Draw(layer)
    # legend
    lr = legend_chip("SIN vinagre", CHART_RED)
    layer.alpha_composite(lr, (40 * S, 100 * S))
    if st["legend_g"] > 0:
        lg = legend_chip("CON vinagre de manzana", CHART_GREEN)
        if st["legend_g"] < 1:
            lg = lg.copy()
            lg.putalpha(lg.getchannel("A").point(lambda v: int(v * st["legend_g"])))
        layer.alpha_composite(lg, (40 * S + lr.width + 14 * S, 100 * S))
    curve_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(curve_layer)
    hr = draw_curve(dc, red_curve, st["red"], CHART_RED, st["red_a"])
    layer.alpha_composite(curve_layer)
    if st["green"] > 0:
        gl = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        hg = draw_curve(ImageDraw.Draw(gl), green_curve, st["green"], CHART_GREEN, 255, 12)
        layer.alpha_composite(gl)
        if hg and st["green"] < 0.999:
            head_dot(layer, hg, CHART_GREEN, t)
    elif hr and st["red"] < 0.999:
        head_dot(layer, hr, CHART_RED, t)
    for key, txt, col, em in (("pill_red", "SE QUEDA ARRIBA", CHART_RED, "⏳"),
                              ("pill_green", "BAJA MÁS RÁPIDO", CHART_GREEN, "⬇")):
        k = st[key]
        if k is not None:
            p = pill(txt, col, em)
            sc = 0.6 + 0.4 * ease_out_back(k)
            pw, ph = int(p.width * sc), int(p.height * sc)
            pr = p.resize((pw, ph), Image.BICUBIC)
            cx_, cy_ = (PX1 - 10) * S - p.width / 2, (PY0 - 2) * S
            layer.alpha_composite(pr, (int(cx_ - pw / 2), int(cy_ - ph / 2)))
    card = layer.resize((CW, CH), Image.LANCZOS)
    k = st["enter"]
    sc = 0.88 + 0.12 * ease_out_back(k)
    al = clamp(k * 1.6)
    paste_scaled(base, card_shadow(), CX + CW / 2, CY + CH / 2 + 18, sc, al * 0.5)
    paste_scaled(base, card, CX + CW / 2, CY + CH / 2, sc, al)


@functools.lru_cache(None)
def card_shadow():
    im = Image.new("RGBA", (CW + 120, CH + 120), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((60, 60, 60 + CW, 60 + CH), radius=40, fill=(0, 0, 0, 150))
    return im.filter(ImageFilter.GaussianBlur(22))


# ---------------- flash on "SUBE" ----------------
T_SUBE = edl.src_to_out(35.98)


def draw_flash(base, t):
    if T_SUBE <= t < T_SUBE + 0.35:
        a = int(70 * (1 - (t - T_SUBE) / 0.35))
        base.alpha_composite(Image.new("RGBA", (W, H), (255, 40, 40, a)))


# ---------------- main loop ----------------
def main():
    frames_needed = set(ONLY) if ONLY else None
    enc = None
    if not ONLY:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "work/mix.wav",
                                "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                                "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                                "-shortest", OUT], stdin=subprocess.PIPE)
    for s in edl.SHOTS:
        rng = range(s["f0"], s["f1"])
        if frames_needed is not None and not any(f in frames_needed for f in rng):
            continue
        src = load_shot(s)
        n = s["f1"] - s["f0"]
        for i, f in enumerate(rng):
            if frames_needed is not None and f not in frames_needed:
                continue
            t = f / FPS
            k = i / max(1, n - 1)
            arr = src[i]
            punch = 1 + 0.07 * (1 - ease_out(i / 5)) if s["id"] not in ("S1",) else 1.0
            if s["kind"] == "th":
                z0, z1 = s["zoom"]
                z = (z0 + (z1 - z0) * ease_in_out(k)) * punch
                im = zoom_frame(arr, z, s["center"]).filter(ImageFilter.UnsharpMask(1.4, 55, 2))
            elif s["kind"] == "image":
                z0, z1 = s["zoom"]
                z = (z0 + (z1 - z0) * ease_out(k)) * punch
                im = zoom_frame(arr, z, s["center"])
            else:
                im = zoom_frame(arr, punch, (0.5, 0.5)) if punch > 1.0005 else Image.fromarray(arr)
            base = im.convert("RGBA")
            draw_flash(base, t)
            draw_chart(base, t)
            draw_tag(base, t)
            draw_hook(base, t)
            draw_captions(base, t)
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
