# Motor de composición para el reel vertical (1080x1920, 30 fps).
# Primitivas: curvas de animación, textos (Poppins + Playfair Display Italic), tarjetas redondeadas
# con borde luminoso, píldoras, estrellas, gradación de color y lectores de video por ffmpeg.
import os, subprocess, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
FONTS = os.path.join(PROJ, "fonts")

# ---------------------------------------------------------------- curvas
def clamp(x, a=0.0, b=1.0):
    return a if x < a else (b if x > b else x)

def ease_out(t):
    t = clamp(t); return 1 - (1 - t) ** 3

def ease_in(t):
    t = clamp(t); return t ** 3

def ease_io(t):
    t = clamp(t); return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2

def ease_back(t, s=1.7):
    t = clamp(t) - 1; return 1 + (s + 1) * t ** 3 + s * t ** 2

def prog(t, start, dur):
    return clamp((t - start) / dur) if dur > 0 else (1.0 if t >= start else 0.0)

# ---------------------------------------------------------------- color
def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

CREAM = hexrgb("#FFF8EE")
TAN = hexrgb("#E9B489")       # bronce claro (soluciones)
TAN_DEEP = hexrgb("#B9773F")
BLUSH = hexrgb("#F6DCD3")
COCOA = hexrgb("#5B3A2B")

def make_grade_lut(warm=0.0, contrast=0.0, lift=0.0, gamma=1.0, gain=1.0):
    x = np.arange(256) / 255.0
    luts = []
    for ch, wm in ((0, warm), (1, warm * 0.35), (2, -warm)):
        y = np.clip(x * gain, 0, 1) ** gamma
        y = lift + (1 - lift) * y
        # curva en S suave
        y = y + contrast * (y - 0.5) * (1 - np.abs(2 * y - 1)) * 2 * 0.5
        y = np.clip(y + wm * (1 - np.abs(2 * y - 1)), 0, 1)
        luts.append((y * 255 + .5).astype(np.uint8))
    return np.stack(luts, 1).reshape(256, 1, 3)

def grade(img, lut, sat=1.0):
    out = cv2.LUT(img, lut)
    if abs(sat - 1.0) > 1e-3:
        f = out.astype(np.float32)
        l = (f[..., 0] * .299 + f[..., 1] * .587 + f[..., 2] * .114)[..., None]
        out = np.clip(l + (f - l) * sat, 0, 255).astype(np.uint8)
    return out

LUT_AROLL = make_grade_lut(warm=0.018, contrast=0.14, lift=0.015, gamma=0.97, gain=1.02)
LUT_BROLL = make_grade_lut(warm=0.025, contrast=0.12, lift=0.0, gamma=0.98, gain=1.0)

# ---------------------------------------------------------------- lectores
class Reader:
    """Lee un video con ffmpeg desde `start` durante `dur` segundos, escalado/recortado a (w, h)."""
    def __init__(self, path, start, dur, w, h, vf_extra=None, fps=FPS):
        self.w, self.h = w, h
        vf = vf_extra or f"scale={w}:{h}:flags=lanczos"
        vf += f",fps={fps}"
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", path, "-t", f"{dur + 0.5:.3f}",
               "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=w * h * 3 * 2)
        self.last = None
        self.n = 0

    def next(self):
        b = self.p.stdout.read(self.w * self.h * 3)
        if len(b) == self.w * self.h * 3:
            self.last = np.frombuffer(b, np.uint8).reshape(self.h, self.w, 3)
            self.n += 1
        if self.last is None:
            self.last = np.zeros((self.h, self.w, 3), np.uint8)
        return self.last

    def close(self):
        try:
            self.p.stdout.close(); self.p.kill(); self.p.wait()
        except Exception:
            pass

def load_photo(path, w, h, cx=0.5, cy=0.5, zoom=1.0):
    """Carga una foto (respetando EXIF) y recorta a la proporción w:h alrededor de (cx, cy)."""
    from PIL import ImageOps
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    iw, ih = im.size
    r = w / h
    cw, ch = (iw, iw / r) if iw / ih < r else (ih * r, ih)
    cw, ch = cw / zoom, ch / zoom
    x0 = clamp(cx * iw - cw / 2, 0, iw - cw); y0 = clamp(cy * ih - ch / 2, 0, ih - ch)
    return np.asarray(im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((w, h), Image.LANCZOS))

# ---------------------------------------------------------------- sprites y mezcla
class Sprite:
    def __init__(self, rgba):
        self.rgb = rgba[..., :3].astype(np.float32)
        self.a = rgba[..., 3:4].astype(np.float32) / 255.0
        self.h, self.w = rgba.shape[:2]

    @staticmethod
    def from_pil(im):
        return Sprite(np.asarray(im.convert("RGBA")))

def over(dst, rgb, a, x, y, alpha=1.0):
    """Mezcla rgb (float32 HxWx3) con alfa a (HxWx1) sobre dst (uint8) con esquina en (x, y)."""
    if alpha <= 0.003: return
    h, w = rgb.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x1 <= x0 or y1 <= y0: return
    sr = rgb[y0 - y:y1 - y, x0 - x:x1 - x]; sa = a[y0 - y:y1 - y, x0 - x:x1 - x] * alpha
    d = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (d + (sr - d) * sa).astype(np.uint8)

def draw_sprite(dst, sp, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    """Dibuja un Sprite centrado en (cx, cy) con escala, opacidad y giro (grados)."""
    if alpha <= 0.003 or scale <= 0.01: return
    if abs(scale - 1) < 1e-3 and abs(rot) < 1e-3:
        over(dst, sp.rgb, sp.a, cx - sp.w / 2, cy - sp.h / 2, alpha); return
    if abs(rot) < 1e-3:
        nw, nh = max(1, int(sp.w * scale)), max(1, int(sp.h * scale))
        interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
        rgb = cv2.resize(sp.rgb, (nw, nh), interpolation=interp)
        a = cv2.resize(sp.a[..., 0], (nw, nh), interpolation=interp)[..., None]
        over(dst, rgb, a, cx - nw / 2, cy - nh / 2, alpha); return
    d = int(math.hypot(sp.w, sp.h) * scale) + 4
    M = cv2.getRotationMatrix2D((sp.w / 2, sp.h / 2), rot, scale)
    M[0, 2] += d / 2 - sp.w / 2; M[1, 2] += d / 2 - sp.h / 2
    rgb = cv2.warpAffine(sp.rgb, M, (d, d), flags=cv2.INTER_LINEAR)
    a = cv2.warpAffine(sp.a[..., 0], M, (d, d), flags=cv2.INTER_LINEAR)[..., None]
    over(dst, rgb, a, cx - d / 2, cy - d / 2, alpha)

# ---------------------------------------------------------------- texto
_fcache = {}
def font(name, size):
    k = (name, size)
    if k not in _fcache:
        files = {"pop": "Poppins-SemiBold.ttf", "popb": "Poppins-Bold.ttf", "popx": "Poppins-ExtraBold.ttf",
                 "popm": "Poppins-Medium.ttf", "play": "PlayfairDisplay-Italic.ttf", "playr": "PlayfairDisplay.ttf"}
        f = ImageFont.truetype(os.path.join(FONTS, files[name]), size)
        if name == "play":
            try: f.set_variation_by_name("Italic")
            except Exception: pass
        _fcache[k] = f
    return _fcache[k]

def text_sprite(txt, fname, size, color=(255, 255, 255), shadow=0.55, glow=None, tracking=0, pad=40, gradient=None):
    """Sprite de una palabra/frase con sombra suave (y brillo opcional). Devuelve (Sprite, ascent, baseline_y)."""
    f = font(fname, size)
    asc, desc = f.getmetrics()
    if tracking:
        widths = [f.getlength(c) for c in txt]
        tw = int(sum(widths) + tracking * (len(txt) - 1))
    else:
        tw = int(f.getlength(txt))
    w, h = tw + pad * 2, asc + desc + pad * 2
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    if tracking:
        x = pad
        for c, cw in zip(txt, widths):
            d.text((x, pad), c, font=f, fill=255); x += cw + tracking
    else:
        d.text((pad, pad), txt, font=f, fill=255)
    m = np.asarray(mask).astype(np.float32) / 255
    out = np.zeros((h, w, 4), np.float32)
    if shadow:
        sh = np.asarray(mask.filter(ImageFilter.GaussianBlur(size * 0.09))).astype(np.float32) / 255
        sh = np.roll(sh, (int(size * 0.035), 0), (0, 1))
        out[..., 3] = sh * shadow
    if glow:
        gc, ga, gr = glow
        g = np.asarray(mask.filter(ImageFilter.GaussianBlur(gr))).astype(np.float32) / 255 * ga
        a0 = out[..., 3:4]
        out[..., :3] = (out[..., :3] * a0 * (1 - g[..., None]) + np.array(gc, np.float32) * g[..., None]) / np.maximum(a0 * (1 - g[..., None]) + g[..., None], 1e-4)
        out[..., 3] = a0[..., 0] + g * (1 - a0[..., 0])
    if gradient:
        c0, c1 = np.array(gradient[0], np.float32), np.array(gradient[1], np.float32)
        yy = np.linspace(0, 1, h)[:, None, None]
        col = c0 + (c1 - c0) * np.clip((yy * h - pad) / max(asc, 1), 0, 1)
        col = np.broadcast_to(col, (h, w, 3))
    else:
        col = np.broadcast_to(np.array(color, np.float32), (h, w, 3))
    a0 = out[..., 3:4]; mm = m[..., None]
    rgb = (out[..., :3] * a0 * (1 - mm) + col * mm) / np.maximum(a0 * (1 - mm) + mm, 1e-4)
    alpha = a0 + mm * (1 - a0)
    rgba = np.concatenate([rgb, alpha * 255], 2).clip(0, 255).astype(np.uint8)
    return Sprite(rgba), asc, pad

class Word:
    def __init__(self, txt, style, t, size=None, color=None):
        self.txt, self.style, self.t = txt, style, t
        self.size, self.color = size, color

STYLES = {
    # nombre: (fuente, tamaño, color, sombra, brillo, tracking, degradado)
    "q_small": ("popb", 48, (255, 255, 255), 0.6, None, 0, None),
    "q_big": ("play", 104, (255, 255, 255), 0.6, None, 0, None),
    "c_small": ("popb", 48, (255, 255, 255), 0.6, None, 0, None),
    "c_big": ("play", 104, (255, 255, 255), 0.6, None, 0, None),
    "c_tan": ("play", 104, None, 0.55, ((255, 214, 170), 0.35, 16), 0, ((255, 236, 214), (233, 172, 120))),
    "a_small": ("popb", 34, (255, 255, 255), 0.75, None, 0, None),
    "a_big": ("play", 70, None, 0.75, ((255, 214, 170), 0.32, 12), 0, ((255, 238, 218), (236, 180, 128))),
    "hook_caps": ("popx", 92, (255, 255, 255), 0.65, None, 6, None),
    "hook_big": ("play", 168, (255, 255, 255), 0.6, None, 0, None),
    "hook_tan": ("play", 168, None, 0.6, ((255, 206, 160), 0.4, 20), 0, ((255, 240, 222), (232, 166, 108))),
}

_wcache = {}
def word_sprite(txt, style, size=None):
    k = (txt, style, size)
    if k not in _wcache:
        fn, sz, col, sh, gl, tr, gr = STYLES[style]
        _wcache[k] = text_sprite(txt, fn, size or sz, col or (255, 255, 255), sh, gl, tr, gradient=gr)
    return _wcache[k]

class TextBlock:
    """Bloque de líneas centrado en (cx, cy) (o con su borde inferior en cy si anchor='bottom').
    Cada línea: lista de Word. Las palabras aparecen con un 'pop' (escala con rebote + subida) en su
    tiempo t; el bloque sale entero en t_out. El interlineado usa el ascenso de la línea siguiente y
    parte del descenso de la anterior, para que una línea pequeña bajo una grande no se pise."""
    def __init__(self, lines, cx, cy, t_out, line_gap=-0.12, anim="pop", exit="fade", fit_w=960, anchor="center"):
        self.cx, self.cy, self.t_out, self.anim, self.exit = cx, cy, t_out, anim, exit
        self.items = []
        rows = []
        for line in lines:
            sps = [word_sprite(w.txt, w.style, w.size) for w in line]
            fonts_ = [font(STYLES[w.style][0], w.size or STYLES[w.style][1]) for w in line]
            asc_max = max(s[1] for s in sps)
            desc_max = max(f.getmetrics()[1] for f in fonts_)
            space = [f.getlength(" ") * 0.9 for f in fonts_]
            width = sum(s[0].w - 2 * s[2] for s in sps) + sum(space[:-1])
            rows.append((line, sps, asc_max, desc_max, space, width))
        bases = []
        b = rows[0][2]
        for i, r in enumerate(rows):
            if i > 0:
                b += r[2] * (1 + line_gap) + 0.7 * rows[i - 1][3]
            bases.append(b)
        total = bases[-1] + 0.55 * rows[-1][3]
        top = cy - total / 2 if anchor == "center" else cy - total
        self.total = total
        for (line, sps, asc_max, desc_max, space, width), base in zip(rows, bases):
            x = cx - width / 2
            base = top + base
            for w, (sp, asc, pad), spc in zip(line, sps, space):
                ww = sp.w - 2 * pad
                self.items.append((w, sp, x + ww / 2, base - asc - pad + sp.h / 2))
                x += ww + spc

    def draw(self, dst, t):
        if t >= self.t_out + 0.35: return
        ex = 1.0
        if t > self.t_out:
            ex = 1 - ease_in(prog(t, self.t_out, 0.22))
        for w, sp, x, y in self.items:
            if t < w.t: continue
            p = prog(t, w.t, 0.26)
            if self.anim == "pop":
                sc = 0.55 + 0.45 * ease_back(p, 2.2)
                dy = 18 * (1 - ease_out(p))
                al = ease_out(prog(t, w.t, 0.12))
            else:
                sc, dy, al = 1.0, 30 * (1 - ease_out(p)), ease_out(p)
            if self.exit == "fade":
                al *= ex; sc *= 1 - 0.08 * (1 - ex)
            draw_sprite(dst, sp, x, y + dy, sc, al)

# ---------------------------------------------------------------- tarjetas
def rounded_mask(w, h, r, ss=4):
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return np.asarray(m.resize((w, h), Image.LANCZOS)).astype(np.float32)[..., None] / 255

class CardFrame:
    """Marco luminoso (sombra + halo cálido + borde fino) para tarjetas de w x h."""
    def __init__(self, w, h, r=34, border=3, glow=(255, 236, 205), pad=60):
        self.w, self.h, self.r, self.pad = w, h, r, pad
        self.mask = rounded_mask(w, h, r)
        W2, H2 = w + 2 * pad, h + 2 * pad
        ss = 2
        big = Image.new("L", (W2 * ss, H2 * ss), 0)
        ImageDraw.Draw(big).rounded_rectangle((pad * ss, pad * ss, (pad + w) * ss, (pad + h) * ss), r * ss, fill=255)
        base = big.resize((W2, H2), Image.LANCZOS)
        shadow = np.asarray(base.filter(ImageFilter.GaussianBlur(22))).astype(np.float32) / 255
        shadow = np.roll(shadow, (14, 0), (0, 1)) * 0.38
        halo = np.asarray(base.filter(ImageFilter.GaussianBlur(10))).astype(np.float32) / 255 * 0.55
        ring = Image.new("L", (W2 * ss, H2 * ss), 0)
        ImageDraw.Draw(ring).rounded_rectangle((pad * ss, pad * ss, (pad + w) * ss, (pad + h) * ss), r * ss, outline=255, width=border * ss)
        ring = np.asarray(ring.resize((W2, H2), Image.LANCZOS)).astype(np.float32) / 255
        inner = np.asarray(base).astype(np.float32) / 255
        # fuera de la tarjeta: sombra oscura + halo cálido; borde: crema
        outside = 1 - inner
        a_sh = shadow * outside
        a_halo = halo * outside
        rgb = np.zeros((H2, W2, 3), np.float32)
        a = np.zeros((H2, W2), np.float32)
        # sombra
        a = a_sh
        # halo encima de la sombra
        gcol = np.array(glow, np.float32)
        rgb = gcol * (a_halo / np.maximum(a_halo + a * (1 - a_halo), 1e-4))[..., None]
        a = a_halo + a * (1 - a_halo)
        # borde encima
        rcol = np.array((255, 248, 236), np.float32)
        rgb = rgb * (1 - ring[..., None]) * (a / np.maximum(a * (1 - ring) + ring, 1e-4))[..., None] + rcol * (ring / np.maximum(a * (1 - ring) + ring, 1e-4))[..., None]
        a = ring + a * (1 - ring)
        self.under_rgb = rgb.astype(np.float32)
        self.under_a = a[..., None].astype(np.float32)

    def compose(self, content):
        """content: uint8 h x w x 3 → (rgb, a) del tamaño con margen, listo para escalar y mezclar."""
        W2, H2 = self.w + 2 * self.pad, self.h + 2 * self.pad
        rgb = self.under_rgb.copy(); a = self.under_a.copy()
        p = self.pad
        c = content.astype(np.float32)
        m = self.mask
        sub_rgb = rgb[p:p + self.h, p:p + self.w]; sub_a = a[p:p + self.h, p:p + self.w]
        sub_rgb[:] = c * m + sub_rgb * (1 - m)
        sub_a[:] = m + sub_a * (1 - m)
        return rgb, a

def draw_card(dst, frame, content, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    rgb, a = frame.compose(content)
    sp = Sprite.__new__(Sprite); sp.rgb, sp.a, sp.h, sp.w = rgb, a, rgb.shape[0], rgb.shape[1]
    draw_sprite(dst, sp, cx, cy, scale, alpha, rot)

def pill(txt, bg=(255, 255, 255), fg=(60, 40, 30), size=24, padx=20, pady=9, icon=None, grad=None):
    f = font("popb", size)
    tw = int(f.getlength(txt) + (len(txt) - 1) * 2.2)
    iw = int(size * 1.05) if icon else 0
    w, h = tw + iw + padx * 2, int(size * 1.25) + pady * 2
    ss = 3
    im = Image.new("RGBA", (w * ss + 40 * ss, h * ss + 40 * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = 20 * ss
    # sombra
    sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((o, o + 4 * ss, o + w * ss, o + h * ss + 4 * ss), h * ss // 2, fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(6 * ss))
    shadow = Image.new("RGBA", im.size, (40, 25, 15, 0)); shadow.putalpha(sh)
    im = Image.alpha_composite(im, shadow)
    body = Image.new("RGBA", im.size, (0, 0, 0, 0))
    bm = Image.new("L", im.size, 0); ImageDraw.Draw(bm).rounded_rectangle((o, o, o + w * ss, o + h * ss), h * ss // 2, fill=255)
    if grad:
        g0, g1 = np.array(grad[0], np.float32), np.array(grad[1], np.float32)
        xx = np.linspace(0, 1, im.size[0])[None, :, None]
        col = (g0 + (g1 - g0) * xx).repeat(im.size[1], 0)
        body = Image.fromarray(np.concatenate([col, np.asarray(bm)[..., None]], 2).astype(np.uint8), "RGBA")
    else:
        body = Image.new("RGBA", im.size, bg + (255,)); body.putalpha(bm)
    im = Image.alpha_composite(im, body)
    d = ImageDraw.Draw(im)
    x = o + padx * ss
    cy = o + h * ss / 2
    if icon == "check":
        s = size * ss * 0.42
        d.line([(x + s * .1, cy), (x + s * .45, cy + s * .38), (x + s * 1.05, cy - s * .45)], fill=fg, width=int(size * ss * .14), joint="curve")
        x += iw * ss
    elif icon == "x":
        s = size * ss * 0.32
        cxx = x + s * 0.8
        d.line([(cxx - s, cy - s), (cxx + s, cy + s)], fill=fg, width=int(size * ss * .13))
        d.line([(cxx - s, cy + s), (cxx + s, cy - s)], fill=fg, width=int(size * ss * .13))
        x += iw * ss
    fb = font("popb", size * ss)
    for c in txt:
        d.text((x, cy), c, font=fb, fill=fg, anchor="lm"); x += fb.getlength(c) + 2.2 * ss
    im = im.resize((im.size[0] // ss, im.size[1] // ss), Image.LANCZOS)
    return Sprite.from_pil(im)

# ---------------------------------------------------------------- estrellas
def star_sprite(size=60, color=(255, 246, 228), glow=(255, 205, 150)):
    ss = 4; S = size * 3
    im = Image.new("L", (S * ss, S * ss), 0)
    d = ImageDraw.Draw(im)
    c = S * ss / 2; R = size * ss / 2; r = R * 0.22
    pts = []
    for i in range(8):
        ang = math.pi / 2 * (i // 2) + (math.pi / 4 if i % 2 else 0) - math.pi / 2
        rad = R if i % 2 == 0 else r
        pts.append((c + rad * math.cos(ang), c + rad * math.sin(ang)))
    d.polygon(pts, fill=255)
    core = im.resize((S, S), Image.LANCZOS)
    g = np.asarray(core.filter(ImageFilter.GaussianBlur(size * 0.18))).astype(np.float32) / 255 * 0.9
    m = np.asarray(core).astype(np.float32) / 255
    rgb = np.array(glow, np.float32) * (1 - m[..., None]) + np.array(color, np.float32) * m[..., None]
    a = np.maximum(m, g)
    return Sprite(np.concatenate([rgb, a[..., None] * 255], 2).clip(0, 255).astype(np.uint8))

class Twinkle:
    """Estrella que aparece, gira un poco y se apaga."""
    def __init__(self, sp, x, y, t0, dur=0.9, s=1.0, rot=25):
        self.sp, self.x, self.y, self.t0, self.dur, self.s, self.rot = sp, x, y, t0, dur, s, rot

    def draw(self, dst, t, dx=0, dy=0):
        p = prog(t, self.t0, self.dur)
        if p <= 0 or p >= 1: return
        sc = math.sin(math.pi * p) ** 0.8 * self.s
        draw_sprite(dst, self.sp, self.x + dx, self.y + dy, sc, min(1, 2.5 * math.sin(math.pi * p)), self.rot * p)
