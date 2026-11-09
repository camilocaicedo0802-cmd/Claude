"""Estilo "misterio" (referencia): tipografía condensada con brillo rojo/amarillo, máquina de escribir,
cajas de neón, anillos, cifras grandes, fotos enmarcadas, luz procedimental y post-efectos."""
import functools
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from engine import (FPS, H, W, Sprite, blend, clamp, darken, ease_back, ease_in, ease_io, ease_out, font, kb_frame,
                    lerp, load_image, over, over_center, prog, text_sprite)
from gfx import Base, Overlay, fade_env

RED = (226, 30, 42)
RED_D = (150, 12, 20)
YEL = (255, 214, 10)
WHT = (245, 242, 236)
BLK = (8, 8, 9)


# ------------------------------------------------------------------ sprites con brillo
@functools.lru_cache(maxsize=1024)
def glow_text(txt, fname, size, color=WHT, glow=None, glow_r=18, glow_a=0.9, tracking=0, stroke=0):
    """Texto con halo luminoso (glow) del color indicado. Devuelve Sprite."""
    f = font(fname, size)
    pad = int(glow_r * 2.2) + 8
    tw = int(f.getlength(txt)) + (tracking * max(0, len(txt) - 1))
    asc, desc = f.getmetrics()
    im = Image.new("RGBA", (tw + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def put(dr, col, sw=0):
        if tracking:
            x = pad
            for c in txt:
                dr.text((x, pad), c, font=f, fill=col, stroke_width=sw, stroke_fill=col)
                x += f.getlength(c) + tracking
        else:
            dr.text((pad, pad), txt, font=f, fill=col, stroke_width=sw, stroke_fill=col)

    base = Image.new("RGBA", im.size, (0, 0, 0, 0))
    put(ImageDraw.Draw(base), color + (255,), stroke)
    # sombra oscura para legibilidad
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    put(ImageDraw.Draw(sh), (0, 0, 0, 230), 2)
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    im = Image.alpha_composite(im, sh)
    if glow:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        put(ImageDraw.Draw(g), glow + (int(255 * glow_a),), 3)
        g1 = g.filter(ImageFilter.GaussianBlur(glow_r))
        g2 = g.filter(ImageFilter.GaussianBlur(glow_r * 0.4))
        im = Image.alpha_composite(im, g1)
        im = Image.alpha_composite(im, g2)
    im = Image.alpha_composite(im, base)
    return Sprite.from_pil(im), pad


def word_width(txt, fname, size):
    return font(fname, size).getlength(txt)


# ------------------------------------------------------------------ overlays de texto
class TypeLine(Overlay):
    """Línea tipo máquina de escribir (Special Elite / mono) que aparece letra a letra con cursor."""

    def __init__(self, text, t0=0.1, y=0.5, x=0.5, color=RED, size=46, fname="type", cps=16, t1=None, glow=True,
                 align="center"):
        self.text, self.t0, self.y, self.x, self.color, self.size = text, t0, y, x, color, size
        self.fname, self.cps, self.t1, self.glow, self.align = fname, cps, t1, glow, align

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        a = fade_env(t, dur, self.t0, self.t1, fin=0.05, fout=0.25)
        n = int((t - self.t0) * self.cps) + 1
        full_w = word_width(self.text, self.fname, self.size)
        sub = self.text[:n]
        if not sub.strip():
            return
        sp, pad = glow_text(sub, self.fname, self.size, self.color, self.color if self.glow else None, 14, 0.55)
        x0 = self.x * W - (full_w / 2 if self.align == "center" else 0)
        y0 = self.y * H - self.size * 0.6
        over(img, sp, x0 - pad, y0 - pad, a)
        if n <= len(self.text) or int(t * 2.5) % 2 == 0:
            cx = x0 + word_width(sub, self.fname, self.size) + 6
            cv2.rectangle(img, (int(cx), int(y0 + self.size * 0.15)), (int(cx + self.size * 0.45), int(y0 + self.size * 1.05)),
                          tuple(int(c * a) for c in self.color), -1)


class Kinetic(Overlay):
    """Titular condensado en mayúsculas, palabra a palabra, con brillo.
    lines: lista de líneas; cada línea es lista de (texto, estilo) o un str.
    estilos: 'w' blanco, 'r' rojo, 'y' amarillo, 's' cursiva serif roja (acento), 'sy' cursiva amarilla,
             'k' pequeño blanco (sans)."""

    STY = {
        "w": ("bebas", 1.0, WHT, RED, 0.35),
        "r": ("bebas", 1.0, RED, RED, 0.9),
        "y": ("bebas", 1.0, YEL, YEL, 0.6),
        "s": ("serif_it", 0.92, RED, RED, 0.8),
        "sy": ("serif_it", 0.92, YEL, YEL, 0.6),
        "sw": ("serif_it", 0.92, WHT, None, 0),
        "k": ("sans", 0.36, WHT, None, 0),
        "kr": ("sans_bold", 0.36, RED, None, 0),
    }

    def __init__(self, lines, t0=0.15, step=0.16, x=0.5, y=0.5, size=120, lh=1.0, t1=None, anim="up", align="center",
                 dim=0.0):
        self.lines = [[(l, "w")] if isinstance(l, str) else l for l in lines]
        self.t0, self.step, self.x, self.y, self.size, self.lh = t0, step, x, y, size, lh
        self.t1, self.anim, self.align, self.dim = t1, anim, align, dim
        self._lay = None

    def layout(self):
        lay = []
        y = 0
        k = 0
        heights = []
        for line in self.lines:
            items = []
            for txt, sty in line:
                for wd in txt.split(" "):
                    if wd:
                        items.append((wd, sty))
            hmax = max(self.size * self.STY[s][1] for _, s in items)
            heights.append(hmax)
            lay.append(items)
        total_h = sum(h * self.lh for h in heights)
        out = []
        cy = self.y * H - total_h / 2
        for items, hmax in zip(lay, heights):
            widths = []
            for wd, sty in items:
                fn, sc, *_ = self.STY[sty]
                widths.append(word_width(wd, fn, int(self.size * sc)))
            gap = self.size * 0.22
            lw = sum(widths) + gap * (len(items) - 1)
            x = self.x * W - (lw / 2 if self.align == "center" else 0 if self.align == "left" else lw)
            for (wd, sty), ww in zip(items, widths):
                fn, sc, col, gl, ga = self.STY[sty]
                sz = int(self.size * sc)
                # alinear base: palabras pequeñas centradas verticalmente
                yy = cy + (hmax - sz) * (0.5 if sc < 0.5 else 0.8)
                out.append((wd, fn, sz, col, gl, ga, x, yy, k))
                x += ww + gap
                k += 1
            cy += hmax * self.lh
        self._lay = out

    def draw(self, img, t, dur):
        if self._lay is None:
            self.layout()
        if self.dim and t >= self.t0:
            a = fade_env(t, dur, self.t0, self.t1, 0.3, 0.3) * self.dim
            img[:] = (img.astype(np.float32) * (1 - a)).astype(np.uint8)
        for wd, fn, sz, col, gl, ga, x, y, k in self._lay:
            ts = self.t0 + k * self.step
            if t < ts:
                continue
            a = fade_env(t, dur, ts, self.t1, fin=0.18, fout=0.3)
            sp, pad = glow_text(wd, fn, sz, col, gl, max(8, sz // 7), ga)
            p = ease_out(prog(t, ts, 0.35))
            dy = 0
            sc = 1.0
            if self.anim == "up":
                dy = (1 - p) * sz * 0.35
            elif self.anim == "pop":
                sc = lerp(1.35, 1.0, ease_back(prog(t, ts, 0.3)))
            elif self.anim == "blur":
                sc = lerp(1.12, 1.0, p)
            if sc != 1.0:
                over_center(img, sp, x - pad + sp.w / 2, y - pad + sp.h / 2 + dy, a, sc)
            else:
                over(img, sp, x - pad, y - pad + dy, a)


class NeonBox(Overlay):
    """Caja roja con texto blanco (estilo "Y ESO NO CUADRA"), con brillo y ligera inclinación."""

    def __init__(self, text, t0=0.2, pos=(0.5, 0.5), size=64, color=RED, txt=WHT, t1=None, angle=0, fname="sans_xb"):
        self.text, self.t0, self.pos, self.size, self.color, self.txt = text, t0, pos, size, color, txt
        self.t1, self.angle, self.fname = t1, angle, fname
        self.sp = None

    def build(self):
        f = font(self.fname, self.size)
        tw = int(f.getlength(self.text))
        asc, desc = f.getmetrics()
        px, py = int(self.size * 0.45), int(self.size * 0.22)
        bw, bh = tw + px * 2, asc + desc + py * 2
        pad = 60
        im = Image.new("RGBA", (bw + pad * 2, bh + pad * 2), (0, 0, 0, 0))
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).rectangle([pad, pad, pad + bw, pad + bh], fill=self.color + (200,))
        g = g.filter(ImageFilter.GaussianBlur(26))
        im = Image.alpha_composite(im, g)
        d = ImageDraw.Draw(im)
        d.rectangle([pad, pad, pad + bw, pad + bh], fill=self.color + (240,))
        d.text((pad + px, pad + py - 2), self.text, font=f, fill=self.txt + (255,))
        if self.angle:
            im = im.rotate(self.angle, resample=Image.BICUBIC, expand=True)
        self.sp = Sprite.from_pil(im)

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        if self.sp is None:
            self.build()
        a = fade_env(t, dur, self.t0, self.t1, 0.08, 0.25)
        p = prog(t, self.t0, 0.28)
        sc = lerp(1.25, 1.0, ease_out(p))
        # parpadeo de neón al encender
        if p < 1 and int(t * 30) % 3 == 1:
            a *= 0.45
        over_center(img, self.sp, self.pos[0] * W, self.pos[1] * H, a, sc)


class Rings(Overlay):
    """Anillos rojos concéntricos que se expanden (círculo de la referencia)."""

    def __init__(self, t0=0.0, pos=(0.5, 0.5), color=RED, r0=0.18, r1=0.42, period=2.6, n=2, width=5, t1=None,
                 alpha=0.85):
        self.t0, self.pos, self.color, self.r0, self.r1, self.period = t0, pos, color, r0, r1, period
        self.n, self.width, self.t1, self.alpha = n, width, t1, alpha

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        env = fade_env(t, dur, self.t0, self.t1, 0.4, 0.4) * self.alpha
        layer = np.zeros_like(img)
        cx, cy = int(self.pos[0] * W), int(self.pos[1] * H)
        for i in range(self.n):
            ph = ((t - self.t0) / self.period + i / self.n) % 1.0
            r = int(lerp(self.r0, self.r1, ease_out(ph)) * H)
            aa = (1 - ph) * env
            cv2.circle(layer, (cx, cy), r, tuple(int(c * aa) for c in self.color), self.width, cv2.LINE_AA)
        glow = cv2.GaussianBlur(layer, (0, 0), 9)
        np.copyto(img, np.clip(img.astype(np.int16) + layer + glow, 0, 255).astype(np.uint8))


class BigNumber(Overlay):
    """Cifra grande (Bebas) con leyenda pequeña debajo, opcionalmente contando."""

    def __init__(self, text, caption="", t0=0.2, pos=(0.5, 0.45), size=260, color=WHT, glow=RED, count=None,
                 fmt="{:,.0f}", t1=None, cap_color=WHT):
        self.text, self.caption, self.t0, self.pos, self.size = text, caption, t0, pos, size
        self.color, self.glow, self.count, self.fmt, self.t1, self.cap_color = color, glow, count, fmt, t1, cap_color

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        a = fade_env(t, dur, self.t0, self.t1, 0.25, 0.3)
        txt = self.text
        if self.count:
            v0, v1, cd = self.count
            v = lerp(v0, v1, ease_out(prog(t, self.t0, cd)))
            txt = self.fmt.format(v).replace(",", ".") + self.text
        sp, pad = glow_text(txt, "bebas", self.size, self.color, self.glow, 26, 0.75)
        sc = lerp(1.15, 1.0, ease_out(prog(t, self.t0, 0.5)))
        over_center(img, sp, self.pos[0] * W, self.pos[1] * H, a, sc)
        if self.caption:
            ca = fade_env(t, dur, self.t0 + 0.4, self.t1, 0.3, 0.3)
            cs, cp = glow_text(self.caption, "sans", 38, self.cap_color, None)
            over_center(img, cs, self.pos[0] * W, self.pos[1] * H + self.size * 0.52 + 10, ca)


class Polaroid(Overlay):
    """Foto enmarcada (borde blanco, sombra) que cae girada, con leyenda opcional."""

    def __init__(self, path, t0=0.2, pos=(0.5, 0.48), w=0.36, angle=-4, caption=None, t1=None, grade="dark",
                 border=14, frame=WHT, crop=None):
        self.path, self.t0, self.pos, self.w, self.angle, self.caption = path, t0, pos, w, angle, caption
        self.t1, self.grade, self.border, self.frame, self.crop = t1, grade, border, frame, crop
        self.sp = None

    def build(self):
        src = load_image(self.path, self.grade)
        h0, w0 = src.shape[:2]
        if self.crop:
            x0, y0, x1, y1 = self.crop
            src = src[int(y0 * h0):int(y1 * h0), int(x0 * w0):int(x1 * w0)]
            h0, w0 = src.shape[:2]
        pw = int(self.w * W)
        ph = int(pw * h0 / w0)
        ph = min(ph, int(H * 0.72))
        pw2 = int(ph * w0 / h0)
        im = cv2.resize(src, (pw2, ph), interpolation=cv2.INTER_AREA)
        b = self.border
        capb = 70 if self.caption else 0
        card = Image.new("RGBA", (pw2 + 2 * b, ph + 2 * b + capb), self.frame + (255,))
        card.paste(Image.fromarray(im), (b, b))
        if self.caption:
            d = ImageDraw.Draw(card)
            f = font("type", 34)
            tw = f.getlength(self.caption)
            d.text(((card.width - tw) / 2, ph + b + 14), self.caption, font=f, fill=(25, 22, 20, 255))
        pad = 50
        full = Image.new("RGBA", (card.width + pad * 2, card.height + pad * 2), (0, 0, 0, 0))
        sh = Image.new("RGBA", full.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([pad + 10, pad + 16, pad + card.width + 10, pad + card.height + 16], fill=(0, 0, 0, 200))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        full = Image.alpha_composite(full, sh)
        full.paste(card, (pad, pad), card)
        full = full.rotate(self.angle, resample=Image.BICUBIC, expand=True)
        self.sp = Sprite.from_pil(full)

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        if self.sp is None:
            self.build()
        a = fade_env(t, dur, self.t0, self.t1, 0.2, 0.3)
        p = ease_out(prog(t, self.t0, 0.55))
        sc = lerp(1.18, 1.0, p) * (1 + 0.025 * (t - self.t0) / max(dur, 1))
        over_center(img, self.sp, self.pos[0] * W, self.pos[1] * H + (1 - p) * 40, a, sc)


class Quote(Overlay):
    """Cita: texto amarillo tipo máquina de escribir sobre caja negra translúcida."""

    def __init__(self, lines, t0=0.2, pos=(0.5, 0.78), size=60, color=YEL, cps=26, t1=None):
        self.lines, self.t0, self.pos, self.size, self.color, self.cps, self.t1 = lines, t0, pos, size, color, cps, t1

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        a = fade_env(t, dur, self.t0, self.t1, 0.15, 0.3)
        f = font("type", self.size)
        lw = max(f.getlength(l) for l in self.lines)
        lh = self.size * 1.25
        bw, bh = lw + 50, lh * len(self.lines) + 30
        x0, y0 = self.pos[0] * W - bw / 2, self.pos[1] * H - bh / 2
        sub = img[int(max(0, y0)):int(min(H, y0 + bh)), int(max(0, x0)):int(min(W, x0 + bw))]
        sub[:] = (sub.astype(np.float32) * (1 - 0.72 * a)).astype(np.uint8)
        n = int((t - self.t0) * self.cps)
        for i, l in enumerate(self.lines):
            s = l[:max(0, n)]
            n -= len(l)
            if s:
                sp, pad = glow_text(s, "type", self.size, self.color, self.color, 10, 0.35)
                over(img, sp, x0 + 25 - pad, y0 + 15 + i * lh - pad, a)


class Bar(Overlay):
    """Barra roja translúcida con texto grande y subtítulos por categorías (estilo '167 | científicos')."""

    def __init__(self, text, subs=(), t0=0.2, y=0.5, t1=None, size=70):
        self.text, self.subs, self.t0, self.y, self.t1, self.size = text, subs, t0, y, t1, size

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        a = fade_env(t, dur, self.t0, self.t1, 0.25, 0.3)
        p = ease_out(prog(t, self.t0, 0.45))
        bw = int(W * 0.46 * p)
        bh = int(self.size * 1.9)
        x0, y0 = int(W / 2 - bw / 2), int(self.y * H - bh / 2)
        sub = img[y0:y0 + bh, x0:x0 + bw].astype(np.float32)
        col = np.array(RED, np.float32)
        img[y0:y0 + bh, x0:x0 + bw] = (sub * (1 - 0.62 * a) + col * 0.62 * a).astype(np.uint8)
        sp, pad = glow_text(self.text, "bebas", self.size, WHT, None)
        over_center(img, sp, W / 2, self.y * H - bh * 0.12, a * p)
        if self.subs:
            k = int((t - self.t0 - 0.5) / 0.45) + 1
            s = "  |  ".join(self.subs[:max(0, k)])
            if s:
                cs, _ = glow_text(s, "mono", 26, WHT, None)
                over_center(img, cs, W / 2, self.y * H + bh * 0.3, a)


class LowerName(Overlay):
    """Nombre en cursiva bold blanca abajo a la izquierda (estilo 'NAPOLEÓN BONAPARTE')."""

    def __init__(self, text, t0=0.3, pos=(0.08, 0.86), t1=None, size=40):
        self.text, self.t0, self.pos, self.t1, self.size = text, t0, pos, t1, size

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        a = fade_env(t, dur, self.t0, self.t1, 0.25, 0.3)
        sp, pad = glow_text(self.text, "sans_xb", self.size, WHT, None)
        dx = (1 - ease_out(prog(t, self.t0, 0.4))) * -30
        over(img, sp, self.pos[0] * W - pad + dx, self.pos[1] * H - pad, a)
        cv2.line(img, (int(self.pos[0] * W), int(self.pos[1] * H - 12)),
                 (int(self.pos[0] * W + 90 * prog(t, self.t0, 0.5)), int(self.pos[1] * H - 12)), RED, 4, cv2.LINE_AA)


class Flicker(Overlay):
    """Destello / fuga de luz cálida o roja durante un tramo."""

    def __init__(self, t0=0.0, dur=0.4, color=(255, 255, 255), peak=0.8):
        self.t0, self.d, self.color, self.peak = t0, dur, color, peak

    def draw(self, img, t, dur):
        k = prog(t, self.t0, self.d)
        if 0 < k < 1:
            w = math.sin(math.pi * k) ** 1.5 * self.peak
            np.copyto(img, blend(img, np.full_like(img, self.color, dtype=np.uint8), w))


class Tint(Overlay):
    """Tinte de color multiplicativo (rojo sangre, etc.), con rampa."""

    def __init__(self, color=(1.15, 0.55, 0.5), k=1.0, t0=0.0, ramp=0.5, t1=None):
        self.color, self.k, self.t0, self.ramp, self.t1 = np.array(color, np.float32), k, t0, ramp, t1

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        a = fade_env(t, dur, self.t0, self.t1, self.ramp, self.ramp) * self.k
        f = img.astype(np.float32)
        np.copyto(img, np.clip(f * (1 - a) + f * self.color * a, 0, 255).astype(np.uint8))


class Dim(Overlay):
    def __init__(self, k=0.5, t0=0.0, ramp=0.4, t1=None):
        self.k, self.t0, self.ramp, self.t1 = k, t0, ramp, t1

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        a = fade_env(t, dur, self.t0, self.t1, self.ramp, self.ramp) * self.k
        np.copyto(img, (img.astype(np.float32) * (1 - a)).astype(np.uint8))


class Letterbox(Overlay):
    def __init__(self, k=0.11):
        self.k = k

    def draw(self, img, t, dur):
        h = int(H * self.k)
        img[:h] = 0
        img[H - h:] = 0


class Blur(Overlay):
    """Desenfoque que entra o sale (recuerdos que se desvanecen)."""

    def __init__(self, r0=0, r1=18, t0=0.0, t1=None):
        self.r0, self.r1, self.t0, self.t1 = r0, r1, t0, t1

    def draw(self, img, t, dur):
        t1 = self.t1 if self.t1 is not None else dur
        r = lerp(self.r0, self.r1, ease_io(prog(t, self.t0, t1 - self.t0)))
        if r > 0.6:
            np.copyto(img, cv2.GaussianBlur(img, (0, 0), r))


# ------------------------------------------------------------------ post-efectos
def chroma(amount=4):
    def post(fr, t, dur):
        a = int(amount)
        out = fr.copy()
        out[..., 0] = np.roll(fr[..., 0], a, 1)
        out[..., 2] = np.roll(fr[..., 2], -a, 1)
        return out
    return post


def heartbeat(bpm=60, depth=0.06):
    def post(fr, t, dur):
        ph = (t * bpm / 60) % 1
        k = math.exp(-ph * 9) + 0.6 * math.exp(-max(0, ph - 0.18) * 9) * (ph > 0.18)
        z = 1 + depth * k
        return kb_frame(fr, 0.5, 0.5, z)
    return post


def shake(n=1.0):
    def post(fr, t, dur):
        dx = int(math.sin(t * 37) * 6 * n + math.sin(t * 61) * 3 * n)
        dy = int(math.cos(t * 43) * 5 * n)
        return np.roll(np.roll(fr, dx, 1), dy, 0)
    return post


def chain(*fs):
    def post(fr, t, dur):
        for f in fs:
            fr = f(fr, t, dur)
        return fr
    return post


# ------------------------------------------------------------------ bases procedimentales
class LightTunnel(Base):
    """Túnel de luz: anillos que avanzan hacia una luz blanca central con rayos y polvo."""

    def __init__(self, intensity=(0.4, 1.0), warm=True, speed=1.0, seed=3):
        self.i0, self.i1 = intensity
        self.warm, self.speed = warm, speed
        rng = np.random.default_rng(seed)
        self.pts = rng.uniform(-1, 1, (260, 3))
        yy, xx = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32)
        self.dx, self.dy = (xx - W / 4) / (H / 4), (yy - H / 4) / (H / 4)
        self.r = np.sqrt(self.dx ** 2 + self.dy ** 2) + 1e-4
        self.ang = np.arctan2(self.dy, self.dx)

    def frame(self, t):
        k = ease_io(t / max(self.dur, 1e-3))
        I = lerp(self.i0, self.i1, k)
        r, ang = self.r, self.ang
        depth = 1.0 / r
        rings = 0.5 + 0.5 * np.cos(depth * 3.2 - t * 6 * self.speed)
        rings = rings ** 6 * np.clip(1 - r * 0.6, 0, 1) * 0.35
        rays = (0.5 + 0.5 * np.cos(ang * 9 + np.sin(t * 0.7) * 2)) * (0.5 + 0.5 * np.cos(ang * 23 - t * 0.4))
        core = np.exp(-(r / (0.18 + 0.32 * I)) ** 2) * (0.7 + 0.6 * I)
        halo = np.exp(-r / (0.35 + 0.5 * I)) * 0.55 * I
        walls = np.clip(r * 0.9, 0, 1) ** 2 * 0.10
        lum = core + halo * (0.6 + 0.4 * rays) + rings * (0.4 + I) + walls
        lum = np.clip(lum, 0, 1.6)
        if self.warm:
            col = np.stack([lum * 1.0, lum * 0.93, lum * 0.82], -1)
        else:
            col = np.stack([lum * 0.9, lum * 0.95, lum * 1.0], -1)
        img = np.clip(col * 255, 0, 255).astype(np.uint8)
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_LINEAR)
        # polvo que viaja hacia la cámara
        for p in self.pts:
            z = (p[2] + 1 - (t * 0.25 * self.speed)) % 2 + 0.05
            x = int(W / 2 + p[0] * W * 0.35 / z)
            y = int(H / 2 + p[1] * H * 0.35 / z)
            if 0 <= x < W and 0 <= y < H:
                v = int(min(255, 90 / z))
                cv2.circle(img, (x, y), max(1, int(2.2 / z)), (v, v, int(v * 0.9)), -1, cv2.LINE_AA)
        return img


class Embers(Base):
    """Fondo negro/rojo con partículas flotantes (para tarjetas de texto)."""

    def __init__(self, color=(150, 20, 26), seed=5, n=140, glow=0.55):
        rng = np.random.default_rng(seed)
        self.p = rng.uniform(0, 1, (n, 4))
        self.color, self.glow = color, glow
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
        r = np.sqrt(((xx - W / 8) / (W / 8)) ** 2 + ((yy - H / 8) / (H / 8)) ** 2)
        g = np.exp(-r ** 2 * 1.3) * glow
        bg = np.stack([g * color[0], g * color[1], g * color[2]], -1)
        self.bg = cv2.resize(bg.astype(np.float32), (W, H))

    def frame(self, t):
        img = self.bg.copy()
        lay = np.zeros((H, W, 3), np.float32)
        for x, y, s, ph in self.p:
            yy = (y - t * (0.015 + s * 0.03)) % 1.0
            xx = x + 0.01 * math.sin(t * 0.8 + ph * 6)
            a = (0.5 + 0.5 * math.sin(t * (1 + s) + ph * 9)) * (0.3 + 0.7 * s)
            cv2.circle(lay, (int(xx * W), int(yy * H)), int(1 + s * 2.5), (255 * a, 120 * a, 80 * a), -1, cv2.LINE_AA)
        lay = lay + cv2.GaussianBlur(lay, (0, 0), 6) * 1.5
        return np.clip(img + lay, 0, 255).astype(np.uint8)


class Corridor(Base):
    """Pasillo infinito de puertas (perspectiva de un punto) que avanza; algunas puertas brillan."""

    def __init__(self, speed=0.35, seed=11, lit=(3, 7, 12)):
        self.speed, self.lit = speed, lit

    def frame(self, t):
        img = np.zeros((H, W, 3), np.uint8)
        cx, cy = W / 2, H * 0.52
        z0 = (t * self.speed) % 1.0
        # suelo y techo con gradiente
        for i in range(40, 0, -1):
            z = i - z0
            if z <= 0.15:
                continue
            s = 1.0 / z
            hw, hh = W * 0.55 * s, H * 0.62 * s
            c = int(max(0, 70 - z * 2.2))
            cv2.rectangle(img, (int(cx - hw), int(cy - hh)), (int(cx + hw), int(cy + hh)), (c, int(c * 0.8), int(c * 0.7)), 2,
                          cv2.LINE_AA)
            if i % 2 == 0:
                for side in (-1, 1):
                    dx0 = cx + side * hw
                    s2 = 1.0 / (z + 0.6)
                    dx1 = cx + side * W * 0.55 * s2
                    top0, bot0 = cy - hh * 0.75, cy + hh
                    top1, bot1 = cy - H * 0.62 * s2 * 0.75, cy + H * 0.62 * s2
                    pts = np.array([[dx0, top0], [dx1, top1], [dx1, bot1], [dx0, bot0]], np.int32)
                    litk = (int(i + math.floor(t * self.speed)) % 13) in self.lit
                    col = (int(min(255, 255 / z * 2)), int(min(220, 200 / z * 2)), int(min(160, 140 / z * 2))) if litk else \
                        (int(30 + 40 / z), int(18 + 25 / z), int(14 + 20 / z))
                    cv2.fillConvexPoly(img, pts, col, cv2.LINE_AA)
        glow = np.exp(-(((np.arange(W) - cx) / (W * 0.08)) ** 2))[None, :] * \
            np.exp(-(((np.arange(H) - cy) / (H * 0.1)) ** 2))[:, None]
        img = np.clip(img.astype(np.float32) + glow[..., None] * np.array([255, 235, 200]) * 0.9, 0, 255).astype(np.uint8)
        return cv2.GaussianBlur(img, (0, 0), 1.2)


# ------------------------------------------------------------------ diagramas del episodio
class ECG(Overlay):
    """Monitor cardíaco: línea verde/roja con latidos que se van espaciando hasta quedar plana."""

    def __init__(self, t0=0.0, flat_at=2.6, color=(255, 40, 50), y=0.55, bpm=70):
        self.t0, self.flat_at, self.color, self.y, self.bpm = t0, flat_at, color, y, bpm

    def beat(self, ph):
        # forma PQRST simplificada, ph 0..1
        g = lambda c, w, a: a * math.exp(-((ph - c) / w) ** 2)  # noqa
        return g(0.18, 0.025, 0.12) - g(0.29, 0.01, 0.15) + g(0.31, 0.012, 1.0) - g(0.335, 0.012, 0.3) + g(0.52, 0.05, 0.22)

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        layer = np.zeros_like(img)
        speed = W / 3.2  # px/s
        head = (t - self.t0) * speed
        pts = []
        x0 = max(0, head - W * 0.95)
        for x in np.arange(x0, head, 3):
            ts = x / speed
            period = 60 / self.bpm * (1 + 0.8 * max(0, ts - self.flat_at + 1.5))
            v = 0.0
            if ts < self.flat_at:
                v = self.beat((ts / period) % 1.0)
            px = int(x - x0 + (W * 0.05 if head < W * 0.95 else W * 0.05))
            pts.append((int(px), int(self.y * H - v * H * 0.22)))
        if len(pts) > 1:
            cv2.polylines(layer, [np.array(pts, np.int32)], False, self.color, 4, cv2.LINE_AA)
            cv2.circle(layer, pts[-1], 7, (255, 255, 255), -1, cv2.LINE_AA)
        glow = cv2.GaussianBlur(layer, (0, 0), 10)
        np.copyto(img, np.clip(img.astype(np.int16) + layer + glow * 2, 0, 255).astype(np.uint8))


class Cycle(Overlay):
    """Ciclo MUERTE -> NACIMIENTO: anillo con dos nodos y flechas girando."""

    def __init__(self, t0=0.2, a="MUERTE", b="NACIMIENTO", speed=0.35, r=0.3, crack=None):
        self.t0, self.a, self.b, self.speed, self.r, self.crack = t0, a, b, speed, r, crack

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        env = fade_env(t, dur, self.t0, None, 0.4, 0.3)
        cx, cy, R = W // 2, H // 2, int(self.r * H)
        layer = np.zeros_like(img)
        p = ease_out(prog(t, self.t0, 1.2))
        cv2.ellipse(layer, (cx, cy), (R, R), -90, 0, 360 * p, RED, 5, cv2.LINE_AA)
        rot = (t - self.t0) * self.speed * 2 * math.pi
        for k in range(3):
            an = rot + k * 2 * math.pi / 3
            x, y = cx + R * math.cos(an), cy + R * math.sin(an)
            tx, ty = -math.sin(an), math.cos(an)
            tip = (int(x + tx * 22), int(y + ty * 22))
            cv2.fillConvexPoly(layer, np.array([tip, (int(x - tx * 14 + math.cos(an) * 14), int(y - ty * 14 + math.sin(an) * 14)),
                                                (int(x - tx * 14 - math.cos(an) * 14), int(y - ty * 14 - math.sin(an) * 14))], np.int32),
                               (255, 255, 255), cv2.LINE_AA)
        glow = cv2.GaussianBlur(layer, (0, 0), 8)
        np.copyto(img, np.clip(img.astype(np.float32) * (1 - 0.25 * env) + (layer + glow) * env, 0, 255).astype(np.uint8))
        for lab, ang, tt in ((self.a, -90, 0.5), (self.b, 90, 1.0)):
            a = fade_env(t, dur, self.t0 + tt, None, 0.3, 0.3)
            x, y = cx + R * math.cos(math.radians(ang)), cy + R * math.sin(math.radians(ang))
            cv2.circle(img, (int(x), int(y)), int(16 * a), WHT, -1, cv2.LINE_AA)
            sp, pad = glow_text(lab, "bebas", 78, WHT, RED, 14, 0.7)
            over_center(img, sp, x, y + (-70 if ang < 0 else 70), a)


class TimeArrow(Overlay):
    """Flecha del tiempo PASADO -> PRESENTE -> FUTURO; si bend, la flecha se enrosca en un bucle."""

    def __init__(self, t0=0.2, labels=("PASADO", "PRESENTE", "FUTURO"), step=0.9, y=0.55, bend_at=None):
        self.t0, self.labels, self.step, self.y, self.bend_at = t0, labels, step, y, bend_at

    def draw(self, img, t, dur):
        if t < self.t0:
            return
        env = fade_env(t, dur, self.t0, None, 0.3, 0.3)
        x0, x1, y = int(W * 0.12), int(W * 0.88), int(self.y * H)
        p = ease_io(prog(t, self.t0, self.step * len(self.labels)))
        layer = np.zeros_like(img)
        xe = int(lerp(x0, x1, p))
        cv2.line(layer, (x0, y), (xe, y), WHT, 4, cv2.LINE_AA)
        cv2.fillConvexPoly(layer, np.array([(xe + 26, y), (xe, y - 16), (xe, y + 16)], np.int32), WHT, cv2.LINE_AA)
        np.copyto(img, np.clip(img.astype(np.int16) + (layer * env).astype(np.int16), 0, 255).astype(np.uint8))
        n = len(self.labels)
        for i, lab in enumerate(self.labels):
            ts = self.t0 + self.step * (i + 0.5)
            if t < ts:
                continue
            a = fade_env(t, dur, ts, None, 0.25, 0.3)
            x = lerp(x0, x1, (i + 0.5) / n)
            cv2.circle(img, (int(x), y), 12, RED, -1, cv2.LINE_AA)
            sp, pad = glow_text(lab, "bebas", 84, WHT if i != 1 else RED, RED, 14, 0.6)
            over_center(img, sp, x, y - 80, a)
