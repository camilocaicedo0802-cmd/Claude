#!/usr/bin/env python3
"""Render the VSL: 9:16 canvas, the horizontal talking head in a band, subtitles stacked
beside the face, stickers, proof screenshots, counter and a fixed "Más info en mi perfil" CTA.

Usage:
    python3 render.py --work <dir> --assets <dir> --out video.mp4 [--frames 2.6,18.9]

<work> holds mezz.mp4 (edited 30 fps cut), words.json (whisper words, raw timeline) and
faces.json (face boxes, raw timeline). <assets> holds fonts/ and the resource images.
With --frames it only writes PNG previews of those timestamps.
"""
import argparse
import json
import math
import os
import random
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
BAND_Y, BAND_H = 510, 640
SRC_W, SRC_H = 1920, 1080
COVER = max(W / SRC_W, BAND_H / SRC_H)
BASE_Z = 1.08
# Zooms pivot on the left edge of the face so the subtitle column beside it never shrinks.
ANCHOR = (0.30 * SRC_W, 0.40 * SRC_H)
_s0 = COVER * BASE_Z
_y0 = (SRC_H - BAND_H / _s0) / 2
PIVOT = (ANCHOR[0] * _s0, (ANCHOR[1] - _y0) * _s0)

# Raw takes kept from the original file; the 1.27 s pause between them is cut.
CUTS = [(0.70, 17.98), (19.25, 34.73)]
EDIT_LEN = sum(b - a for a, b in CUTS)
OUTRO = 1.6
TOTAL = EDIT_LEN + OUTRO

YELLOW = (255, 212, 0)
RED = (255, 59, 48)
GREEN = (34, 224, 107)
WHITE = (255, 255, 255)

CTA_Y = 1440
SUB_COL_X = 30
SUB_COL_CY = BAND_Y + 330
OVERLAY_SUB_TOP = 1192


def raw_to_edit(t):
    off = 0.0
    for a, b in CUTS:
        if t < b + 0.05:
            return max(0.0, t - a) + off
        off += b - a
    return off


def edit_to_raw(t):
    for a, b in CUTS:
        if t <= b - a:
            return a + t
        t -= b - a
    return CUTS[-1][1]


# ---------------------------------------------------------------- easing helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out_back(u, c1=1.9):
    u = clamp(u)
    c3 = c1 + 1
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2


def ease_out_cubic(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ease_in_out(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def window(t, t0, t1, fin=0.12, fout=0.12):
    """0..1 visibility with fades at both ends."""
    if t < t0 or t > t1:
        return 0.0
    return min(clamp((t - t0) / fin) if fin else 1.0, clamp((t1 - t) / fout) if fout else 1.0)


# ---------------------------------------------------------------- drawing helpers
class Fonts:
    def __init__(self, folder):
        self.folder = folder
        self.cache = {}

    def get(self, name, size):
        key = (name, int(size))
        if key not in self.cache:
            self.cache[key] = ImageFont.truetype(os.path.join(self.folder, name), int(size))
        return self.cache[key]


def add_shadow(img, offset=(0, 7), blur=9, alpha=0.6, spread=0):
    pad = blur * 2 + max(abs(offset[0]), abs(offset[1])) + spread
    out = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad))
    a = img.getchannel("A")
    if spread:
        a = a.filter(ImageFilter.MaxFilter(spread * 2 + 1))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha)))
    out.alpha_composite(sh, (pad + offset[0], pad + offset[1]))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(img, (pad, pad))
    return out, pad


def text_sprite(text, font, fill, stroke=0, stroke_fill=(0, 0, 0), shadow=True):
    """Return (sprite, ox, oy): sprite with the text's left-baseline origin at (ox, oy)."""
    l, t, r, b = font.getbbox(text, anchor="ls", stroke_width=stroke)
    pad = 4
    img = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad))
    ImageDraw.Draw(img).text((pad - l, pad - t), text, font=font, fill=fill, anchor="ls",
                             stroke_width=stroke, stroke_fill=stroke_fill)
    ox, oy = pad - l, pad - t
    if shadow:
        img, sp = add_shadow(img)
        ox, oy = ox + sp, oy + sp
    return img, ox, oy


def paste_scaled(canvas, sprite, cx, cy, scale=1.0, alpha=1.0, angle=0.0):
    """Composite sprite centred at (cx, cy)."""
    if alpha <= 0.01 or scale <= 0.01:
        return
    img = sprite
    if abs(scale - 1) > 0.005:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BICUBIC)
    if abs(angle) > 0.05:
        img = img.rotate(angle, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img = img.copy()
        img.putalpha(a)
    x, y = int(round(cx - img.width / 2)), int(round(cy - img.height / 2))
    canvas.alpha_composite(img, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))


def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def emoji_sprite(ch, size, outline=12):
    font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
    img = Image.new("RGBA", (160, 160))
    ImageDraw.Draw(img).text((80, 80), ch, font=font, embedded_color=True, anchor="mm")
    img = img.crop(img.getbbox())
    img = img.resize((size, int(size * img.height / img.width)), Image.LANCZOS)
    if not outline:
        return add_shadow(img, offset=(0, 8), blur=10, alpha=0.5)[0]
    # die-cut sticker look: white border + soft shadow
    pad = outline + 4
    base = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad))
    base.paste(img, (pad, pad))
    a = base.getchannel("A").point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(outline * 2 + 1))
    border = Image.new("RGBA", base.size, WHITE + (0,))
    border.putalpha(a.filter(ImageFilter.GaussianBlur(1)))
    border.alpha_composite(base)
    out, _ = add_shadow(border, offset=(0, 10), blur=12, alpha=0.55)
    return out


# ---------------------------------------------------------------- subtitles
KEY_COLORS = {"*": YELLOW, "!": RED, "+": GREEN, "#": YELLOW}

# Each chunk lists its lines; "/" splits lines. A trailing marker makes the line a key line
# in Anton: * yellow, # yellow box, ! red, + green. Words map 1:1 onto the whisper words.
CHUNKS = [
    "Lo más / IMPORTANTE*",
    "en un / SERVICIO#",
    "es la / PUNTUALIDAD*",
    "y el / COMPROMISO#",
    "y si tú / trabajas con",
    "un / EDITOR* / de video",
    "que no / tiene / NADA DE ESO!",
    "y de paso / no te ha / RESULTADO!",
    "dime con / QUIÉN*",
    "estás / TRABAJANDO#",
    "y es / SÚPER LOCO*",
    "porque / hace un / momento",
    "estaba / hablando",
    "con un / CLIENTE#",
    "que / comenzó",
    "que tenía las views / ESTANCADAS!",
    "no crecía / PARA NADA!",
    "ya pegamos / un video",
    "por más de / 300 MIL VISTAS+",
    "CRECIMIENTO+",
    "IMPACTO#",
    "y solamente / tenemos",
    "15 DÍAS*",
    "trabajando / HERMANO*",
    "van a ver / cómo / CRECE+",
    "esa / PERSONA*",
    "y cómo / todo sigue / CRECIENDO+",
    "a otro / NIVEL*",
]


def build_chunks(words):
    chunks, i = [], 0
    for spec in CHUNKS:
        lines = []
        for raw_line in spec.split("/"):
            raw_line = raw_line.strip()
            style = raw_line[-1] if raw_line[-1] in KEY_COLORS else ""
            text = raw_line[:-1] if style else raw_line
            toks = []
            for tok in text.split():
                w = words[i]
                toks.append({"text": tok, "t": raw_to_edit(w["s"]), "end": raw_to_edit(w["e"])})
                i += 1
            lines.append({"style": style, "words": toks})
        first = lines[0]["words"][0]["t"]
        last = lines[-1]["words"][-1]["end"]
        chunks.append({"lines": lines, "t0": first, "last": last})
    assert i == len(words), (i, len(words))
    for a, b in zip(chunks, chunks[1:]):
        a["t1"] = min(b["t0"], a["last"] + 0.7)
    chunks[-1]["t1"] = EDIT_LEN + 0.12  # clears before the CTA moves to the centre
    return chunks


class Subtitles:
    def __init__(self, fonts, chunks, face_left, overlay_mode):
        self.fonts = fonts
        self.chunks = chunks
        for ch in chunks:
            mid = ch["t0"] + 0.05
            overlay = overlay_mode(mid)
            if overlay:
                self.layout(ch, max_w=960, cx=W / 2, top=OVERLAY_SUB_TOP, centered=True,
                            normal_size=46, key_max=104)
            else:
                ts = np.arange(ch["t0"], ch["t1"] + 0.01, 0.1)
                # the face box includes the ears, so the column may run up to its edge
                right = min(face_left(t) for t in ts) - 4
                max_w = clamp(right - SUB_COL_X, 260, 380)
                self.layout(ch, max_w=max_w, cx=SUB_COL_X, top=None, centered=False,
                            normal_size=56, key_max=150)

    def line_font(self, line, size):
        if line["style"]:
            return self.fonts.get("Anton-Regular.ttf", size)
        return self.fonts.get("Poppins-SemiBold.ttf", size)

    def layout(self, ch, max_w, cx, top, centered, normal_size, key_max):
        placed = []
        for line in ch["lines"]:
            text = " ".join(w["text"] for w in line["words"])
            key = bool(line["style"])
            size = key_max if key else normal_size
            box_pad = 18 if line["style"] == "#" else 0
            while True:
                f = self.line_font(line, size)
                if f.getlength(text) + 2 * box_pad <= max_w or size <= 30:
                    break
                size -= 2
            l, t, r, b = f.getbbox(text, anchor="ls")
            placed.append({"line": line, "font": f, "size": size, "w": f.getlength(text),
                           "asc": -t, "desc": max(b, 0), "box_pad": box_pad})
        gaps = [max(8, int(0.16 * p["size"])) + (10 if p["box_pad"] else 0) for p in placed]
        total = sum(p["asc"] + p["desc"] for p in placed) + sum(gaps[1:])
        y = top if top is not None else SUB_COL_CY - total / 2
        for idx, p in enumerate(placed):
            if idx:
                y += gaps[idx]
            base = y + p["asc"]
            x0 = cx - p["w"] / 2 if centered else cx + p["box_pad"]
            line = p["line"]
            color = KEY_COLORS.get(line["style"], WHITE)
            if line["style"] == "#":
                color = (0, 0, 0)
            stroke = 0 if line["style"] == "#" else (6 if line["style"] else 5)
            x = x0
            line["sprites"] = []
            if line["style"] == "#":
                bw = p["w"] + 2 * p["box_pad"]
                bh = p["asc"] + p["desc"] + 22
                box = Image.new("RGBA", (int(bw), int(bh)))
                ImageDraw.Draw(box).rounded_rectangle((0, 0, bw - 1, bh - 1), 14, fill=YELLOW)
                box, sp = add_shadow(box, blur=10, alpha=0.5)
                line["box"] = (box, x0 - p["box_pad"] + bw / 2, base - p["asc"] - 11 + bh / 2)
                line["box_t"] = line["words"][0]["t"]
            for w in line["words"]:
                spr, ox, oy = text_sprite(w["text"], p["font"], color, stroke=stroke,
                                          shadow=line["style"] != "#")
                cxw = x + (spr.width / 2 - ox)
                cyw = base + (spr.height / 2 - oy)
                line["sprites"].append((w, spr, cxw, cyw))
                x += p["font"].getlength(w["text"] + " ")
            y = base + p["desc"]

    def draw(self, canvas, t):
        for ch in self.chunks:
            if not (ch["t0"] - 0.04 <= t < ch["t1"]):
                continue
            out = clamp((ch["t1"] - t) / 0.06)
            for line in ch["lines"]:
                key = bool(line["style"])
                if "box" in line:
                    u = (t - line["box_t"] + 0.04) / 0.22
                    if u > 0:
                        box, bx, by = line["box"]
                        paste_scaled(canvas, box, bx, by, scale=0.3 + 0.7 * ease_out_back(u),
                                     alpha=out * clamp(u * 3), angle=-2.0)
                for w, spr, cx, cy in line["sprites"]:
                    u = (t - w["t"] + 0.04) / (0.24 if key else 0.18)
                    if u <= 0:
                        continue
                    e = ease_out_back(u, 2.4 if key else 1.7)
                    s = (0.35 if key else 0.6) + (0.65 if key else 0.4) * e
                    ang = (-2.0 if line["style"] == "#" else 0.0) + (1 - clamp(u)) * (6 if key else 0)
                    paste_scaled(canvas, spr, cx, cy + (1 - e) * 14, scale=s, alpha=out * clamp(u * 3), angle=ang)


# ---------------------------------------------------------------- main renderer
class Renderer:
    def __init__(self, work, assets):
        self.fonts = Fonts(os.path.join(assets, "fonts"))
        words = json.load(open(os.path.join(work, "words.json")))
        fixes = {"vídeo": "video", "tancadas,": "estancadas"}
        for w in words:
            w["w"] = fixes.get(w["w"], w["w"])
        words[0]["s"] = 0.80  # whisper stretches the first word over the leading silence
        self.faces = json.load(open(os.path.join(work, "faces.json")))
        self.face_t = np.array([f["t"] for f in self.faces])
        fl = np.array([f["x"] if f["x"] is not None else np.nan for f in self.faces], float)
        idx = np.arange(len(fl))
        good = ~np.isnan(fl)
        self.face_l = np.interp(idx, idx[good], fl[good])

        self.chunks = build_chunks(words)
        self.subs = Subtitles(self.fonts, self.chunks, self.face_left_canvas, self.overlay_mode)
        self.load_assets(assets)
        self.build_timeline()

    # -- face / zoom ------------------------------------------------------
    def face_left_canvas(self, t):
        fl = np.interp(edit_to_raw(min(t, EDIT_LEN)), self.face_t, self.face_l) * SRC_W
        return PIVOT[0] + (fl - ANCHOR[0]) * _s0

    def overlay_mode(self, t):
        return 17.28 <= t < 24.50

    def build_timeline(self):
        # (time, zoom, transition seconds)
        self.zoom_keys = [
            (0.00, 1.08, 0.0), (2.62, 1.20, 0.09), (3.84, 1.08, 0.09), (5.40, 1.15, 0.6),
            (7.62, 1.08, 0.09), (8.78, 1.22, 0.09), (9.92, 1.28, 0.09), (11.30, 1.10, 0.09),
            (13.06, 1.08, 0.09), (14.30, 1.17, 0.09), (15.38, 1.08, 0.09), (17.28, 1.08, 0.0),
            (24.55, 1.24, 0.08), (25.25, 1.36, 0.06), (25.55, 1.08, 0.10), (26.47, 1.16, 0.09),
            (27.67, 1.08, 0.09), (28.71, 1.30, 3.3), (32.07, 1.42, 0.08),
        ]
        self.shakes = [(11.76, 14, 0.45), (25.25, 18, 0.4), (32.07, 20, 0.5), (18.73, 0, 0)]
        self.flashes = [(21.17, 0.75, 0.28), (25.25, 0.35, 0.18), (32.07, 0.6, 0.3), (24.50, 0.35, 0.16)]
        self.stickers = [
            ("⏰", 2.62, 3.80, -8), ("🤝", 3.84, 5.30, 7), ("📉", 8.78, 9.90, -6),
            ("🤯", 11.76, 13.00, 8), ("💬", 14.50, 15.90, -7), ("📈", 24.55, 25.22, 6),
            ("💥", 25.25, 26.30, -8), ("CAL", 26.47, 27.95, 6), ("🚀", 29.21, 30.40, -6),
            ("🔥", 32.07, TOTAL, 7),
        ]
        self.sticker_sprites = {}
        for s in self.stickers:
            if s[0] == "CAL":
                self.sticker_sprites["CAL"] = self.calendar_sprite()
            else:
                self.sticker_sprites[s[0]] = emoji_sprite(s[0], 170)

    def zoom_at(self, t):
        z = self.zoom_keys[0][1]
        for (t0, z0, d) in self.zoom_keys:
            if t < t0:
                break
            prev = z
            u = 1.0 if d == 0 else ease_in_out((t - t0) / d) if d > 0.3 else ease_out_cubic((t - t0) / d)
            z = prev + (z0 - prev) * u
        return z

    def shake_at(self, t):
        dx = dy = 0.0
        for (t0, amp, d) in self.shakes:
            if t0 <= t < t0 + d:
                k = 1 - (t - t0) / d
                dx += amp * k * math.sin((t - t0) * 70)
                dy += amp * k * math.cos((t - t0) * 53)
        return dx, dy

    # -- assets -----------------------------------------------------------
    def load_assets(self, assets):
        r23 = Image.open(os.path.join(assets, "recurso23.jpeg")).convert("RGB")
        r1 = Image.open(os.path.join(assets, "recurso1.jpeg")).convert("RGB")
        self.card_r2 = self.make_card(r23.crop((0, 0, 400, r23.height)), 700, ring=(22, 640, 150, 690))
        self.card_r3 = self.make_card(r23.crop((403, 0, r23.width, r23.height)), 700, ring=(20, 640, 150, 690))
        self.card_r1 = self.make_card(r1, 740, ring=(20, 636, 212, 694), color=GREEN)

        f = self.fonts
        a1 = f.get("Anton-Regular.ttf", 112)
        self.head_cuenta = text_sprite("¿CUENTA", a1, WHITE, stroke=6)
        self.head_estancada = text_sprite("ESTANCADA?", a1, RED, stroke=6)
        self.head_vistas = text_sprite("VISTAS EN UN SOLO VIDEO", f.get("Poppins-ExtraBold.ttf", 50), WHITE, stroke=5)
        self.counter_font = f.get("Anton-Regular.ttf", 168)

        # CTA pill: profile icon + label
        cf = f.get("Poppins-ExtraBold.ttf", 50)
        label = "Más info en mi perfil"
        tw = cf.getlength(label)
        ph, icon = 108, 76
        pw = int(tw + icon + 86)
        pill = Image.new("RGBA", (pw, ph))
        d = ImageDraw.Draw(pill)
        d.rounded_rectangle((0, 0, pw - 1, ph - 1), ph // 2, fill=YELLOW)
        ix, iy = 16, (ph - icon) // 2
        d.ellipse((ix, iy, ix + icon, iy + icon), fill=(0, 0, 0))
        cx = ix + icon / 2
        d.ellipse((cx - 13, iy + 15, cx + 13, iy + 41), fill=YELLOW)
        d.chord((cx - 25, iy + 45, cx + 25, iy + 95), 180, 360, fill=YELLOW)
        d.text((ix + icon + 22, ph / 2 + 2), label, font=cf, fill=(0, 0, 0), anchor="lm")
        self.cta_plain = pill
        self.cta_size = (pw, ph)

        self.export_card = self.make_export_card()

    def make_card(self, img, height, ring=None, color=RED):
        scale = height / img.height
        img = img.resize((int(img.width * scale), height), Image.LANCZOS)
        card = rounded(img, 30)
        border = Image.new("RGBA", (card.width + 12, card.height + 12))
        ImageDraw.Draw(border).rounded_rectangle((0, 0, border.width - 1, border.height - 1), 36, fill=WHITE)
        border.alpha_composite(card, (6, 6))
        out, pad = add_shadow(border, offset=(0, 18), blur=22, alpha=0.7)
        ring_box = None
        if ring:
            x0, y0, x1, y1 = [v * scale for v in ring]
            ring_box = (x0 + pad + 6, y0 + pad + 6, x1 + pad + 6, y1 + pad + 6)
        return {"img": out, "ring": ring_box, "color": color}

    def card_with_ring(self, card, progress, glow=False):
        img = card["img"]
        if card["ring"] is None or progress <= 0:
            return img
        img = img.copy()
        x0, y0, x1, y1 = card["ring"]
        x0, y0, x1, y1 = x0 - 14, y0 - 12, x1 + 14, y1 + 12
        layer = Image.new("RGBA", img.size)
        d = ImageDraw.Draw(layer)
        if glow:
            d.rounded_rectangle((x0, y0, x1, y1), 30, fill=card["color"] + (90,))
        d.arc((x0, y0, x1, y1), -200, -200 + 360 * clamp(progress), fill=card["color"] + (255,), width=9)
        img.alpha_composite(layer)
        return img

    def make_export_card(self):
        f = self.fonts
        cw, chh = 880, 300
        card = Image.new("RGBA", (cw, chh))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, cw - 1, chh - 1), 30, fill=(22, 22, 26), outline=(58, 58, 66), width=3)
        for i, c in enumerate([(255, 95, 87), (255, 189, 46), (40, 200, 64)]):
            d.ellipse((34 + i * 34, 30, 56 + i * 34, 52), fill=c)
        d.text((150, 42), "Exportando video...", font=f.get("Poppins-SemiBold.ttf", 34), fill=WHITE, anchor="lm")
        # timeline strip
        rnd = random.Random(4)
        x = 40
        for row, colors in enumerate([[(88, 86, 214), (94, 92, 230)], [(52, 199, 89), (48, 176, 80)]]):
            x = 40
            while x < cw - 60:
                w = rnd.randint(70, 170)
                d.rounded_rectangle((x, 86 + row * 34, min(x + w, cw - 40), 112 + row * 34), 6,
                                    fill=colors[rnd.randint(0, 1)])
                x += w + 6
        return card

    def calendar_sprite(self):
        f = self.fonts
        w, h = 210, 220
        img = Image.new("RGBA", (w, h))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=WHITE)
        d.rounded_rectangle((0, 0, w - 1, 70), 30, fill=RED)
        d.rectangle((0, 40, w - 1, 70), fill=RED)
        d.text((w / 2, 37), "DÍAS", font=f.get("Poppins-ExtraBold.ttf", 38), fill=WHITE, anchor="mm")
        d.text((w / 2, 150), "15", font=f.get("Anton-Regular.ttf", 120), fill=(17, 17, 17), anchor="mm")
        for x in (55, w - 55):
            d.rounded_rectangle((x - 8, -6, x + 8, 22), 8, fill=(40, 40, 40))
        out, _ = add_shadow(img, offset=(0, 10), blur=12, alpha=0.55)
        return out

    # -- per-frame layers ---------------------------------------------------
    def band_image(self, frame, t):
        z = self.zoom_at(t)
        s = COVER * z
        sw, sh = W / s, BAND_H / s
        x0 = ANCHOR[0] - PIVOT[0] / s
        y0 = ANCHOR[1] - PIVOT[1] / s
        dx, dy = self.shake_at(t)
        x0 -= dx / s
        y0 -= dy / s
        x0 = clamp(x0, 0, SRC_W - sw)
        y0 = clamp(y0, 0, SRC_H - sh)
        return frame.resize((W, BAND_H), Image.BICUBIC, box=(x0, y0, x0 + sw, y0 + sh))

    def draw_stickers(self, canvas, t):
        for i, (key, t0, t1, tilt) in enumerate(self.stickers):
            if not (t0 <= t < t1):
                continue
            spr = self.sticker_sprites[key]
            u = (t - t0) / 0.3
            e = ease_out_back(u, 2.6)
            out = clamp((t1 - t) / 0.12)
            wob = math.sin((t - t0) * 9) * 6 * math.exp(-(t - t0) * 3)
            bob = math.sin((t - t0) * 4) * 6
            paste_scaled(canvas, spr, 912, BAND_Y + 18 + bob, scale=e * (0.6 + 0.4 * out),
                         alpha=clamp(u * 4) * out, angle=tilt + wob)

    def draw_export(self, canvas, t):
        t0, t1 = 5.40, 7.70
        if not (t0 <= t < t1):
            return
        u = (t - t0) / 0.32
        e = ease_out_back(u, 1.6)
        out = clamp((t1 - t) / 0.15)
        card = self.export_card.copy()
        d = ImageDraw.Draw(card)
        f = self.fonts
        p = 0.72 + 0.27 * ease_out_cubic((t - t0 - 0.1) / 1.0)
        bx0, bx1, by = 40, 840, 196
        d.rounded_rectangle((bx0, by, bx1, by + 28), 14, fill=(50, 50, 58))
        d.rounded_rectangle((bx0, by, bx0 + (bx1 - bx0) * p, by + 28), 14, fill=YELLOW)
        blink = p > 0.985 and int(t * 4) % 2 == 0
        d.text((bx1, 42), f"{int(p * 100)}%", font=f.get("Anton-Regular.ttf", 54),
               fill=RED if blink else WHITE, anchor="rm")
        late = 6.98
        if t >= late:
            k = ease_out_back((t - late) / 0.25, 2.2)
            tag = "ENTREGA ATRASADA"
            tf = f.get("Poppins-ExtraBold.ttf", 28)
            tw = tf.getlength(tag) + 40
            tagimg = Image.new("RGBA", (int(tw), 46))
            ImageDraw.Draw(tagimg).rounded_rectangle((0, 0, tw - 1, 45), 23, fill=RED)
            ImageDraw.Draw(tagimg).text((tw / 2, 24), tag, font=tf, fill=WHITE, anchor="mm")
            tagimg = tagimg.resize((max(1, int(tagimg.width * k)), max(1, int(tagimg.height * k))))
            card.alpha_composite(tagimg, (int(440 - tagimg.width / 2), int(262 - tagimg.height / 2)))
        card, _ = add_shadow(card, offset=(0, 12), blur=16, alpha=0.6)
        paste_scaled(canvas, card, W / 2, 300 - (1 - e) * 60, scale=0.85 + 0.15 * e, alpha=clamp(u * 3) * out)

    def draw_cards(self, canvas, t):
        # Recurso 2 and 3: low views, then the 300k screenshot (Recurso 1).
        t_in2, t_in3, t_ring, t_out = 17.30, 18.05, 18.73, 20.92
        if t_in2 <= t < t_out + 0.2:
            out = 1 - ease_in_out((t - t_out) / 0.2) if t >= t_out else 1.0
            gray = clamp((t - 19.43) / 0.5) * 0.65
            for card, t0, cx, ang, fromx in ((self.card_r2, t_in2, 300, -5, -500), (self.card_r3, t_in3, 780, 5, 500)):
                if t < t0:
                    continue
                e = ease_out_back((t - t0) / 0.38, 1.5)
                img = self.card_with_ring(card, (t - t_ring) / 0.35)
                if gray > 0:
                    g = img.convert("LA").convert("RGBA")
                    img = Image.blend(img, g, gray)
                sx, sy = self.shake_xy(t, t_ring, 16, 0.35)
                x = cx + (1 - e) * fromx + out * 0 + (1 - out) * (fromx * 0.6)
                paste_scaled(canvas, img, x + sx, 800 + sy + (1 - e) * 120, scale=0.9 + 0.1 * e,
                             alpha=clamp((t - t0) * 8) * out, angle=ang * e)
            # headline
            hu = (t - 17.35) / 0.3
            if hu > 0:
                e = ease_out_back(hu, 2.0)
                sx, sy = self.shake_xy(t, t_ring, 14, 0.35)
                spr, ox, oy = self.head_cuenta
                spr2, ox2, oy2 = self.head_estancada
                total = spr.width + spr2.width - 30
                xa = W / 2 - total / 2 + spr.width / 2
                xb = W / 2 + total / 2 - spr2.width / 2
                paste_scaled(canvas, spr, xa + sx, 300 + sy, scale=0.5 + 0.5 * e, alpha=clamp(hu * 3) * out)
                e2 = ease_out_back((t - 17.55) / 0.3, 2.4)
                if t > 17.55:
                    paste_scaled(canvas, spr2, xb + sx, 300 + sy, scale=0.4 + 0.6 * e2,
                                 alpha=clamp((t - 17.55) * 10) * out, angle=(1 - clamp((t - 17.55) / 0.3)) * -8)

        t1_in, t1_out = 21.17, 24.50
        if t1_in <= t < t1_out + 0.18:
            out = 1 - ease_in_out((t - t1_out) / 0.18) if t >= t1_out else 1.0
            e = ease_out_back((t - t1_in) / 0.42, 1.7)
            ring = (t - 23.09) / 0.4
            img = self.card_with_ring(self.card_r1, ring, glow=ring > 0)
            glow = self.glow_sprite()
            paste_scaled(canvas, glow, W / 2, 800, scale=0.8 + 0.25 * e + 0.03 * math.sin(t * 6),
                         alpha=0.85 * clamp((t - t1_in) * 4) * out)
            paste_scaled(canvas, img, W / 2, 800 + (1 - e) * 200, scale=(0.7 + 0.3 * e) * (1 + 0.012 * (t - t1_in)),
                         alpha=clamp((t - t1_in) * 8) * out, angle=(1 - e) * 10)
            # counter
            cu = clamp((t - 21.30) / 1.75)
            val = int(round(321000 * ease_out_cubic(cu) / 1000.0)) * 1000 if cu < 1 else 321000
            txt = f"{val:,}".replace(",", ".")
            spr, ox, oy = text_sprite(txt, self.counter_font, GREEN, stroke=7)
            pop = 1 + 0.12 * math.exp(-(t - 23.05) * 8) if t >= 23.05 else 1.0
            paste_scaled(canvas, spr, W / 2, 228, scale=(0.6 + 0.4 * ease_out_back((t - 21.25) / 0.3)) * pop,
                         alpha=clamp((t - 21.25) * 6) * out)
            vs, _, _ = self.head_vistas
            paste_scaled(canvas, vs, W / 2, 352, scale=0.6 + 0.4 * ease_out_back((t - 21.45) / 0.3),
                         alpha=clamp((t - 21.45) * 6) * out)
            self.draw_confetti(canvas, t, 21.17)

    _glow = None
    _vig = None

    def vignette(self):
        if self._vig is None:
            x = np.linspace(0, 1, W)
            a = np.clip(1 - x / 0.42, 0, 1) ** 1.6 * 0.42
            alpha = (np.tile(a, (BAND_H, 1)) * 255).astype(np.uint8)
            v = Image.new("RGBA", (W, BAND_H), (0, 0, 0, 0))
            v.putalpha(Image.fromarray(alpha, "L"))
            self._vig = v
        return self._vig

    def glow_sprite(self):
        if self._glow is None:
            g = Image.new("RGBA", (900, 1100))
            ImageDraw.Draw(g).ellipse((150, 150, 750, 950), fill=GREEN + (150,))
            self._glow = g.filter(ImageFilter.GaussianBlur(110))
        return self._glow

    def shake_xy(self, t, t0, amp, d):
        if t0 <= t < t0 + d:
            k = 1 - (t - t0) / d
            return amp * k * math.sin((t - t0) * 80), amp * k * 0.5 * math.cos((t - t0) * 61)
        return 0.0, 0.0

    _confetti = None

    def draw_confetti(self, canvas, t, t0):
        dt = t - t0
        if dt < 0 or dt > 2.2:
            return
        if self._confetti is None:
            rnd = random.Random(7)
            self._confetti = [(rnd.uniform(-1, 1), rnd.uniform(0.4, 1.3), rnd.choice([YELLOW, GREEN, WHITE]),
                               rnd.uniform(0, 6.28), rnd.uniform(-9, 9), rnd.uniform(10, 22)) for _ in range(90)]
        layer = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(layer)
        fade = clamp((2.2 - dt) / 0.6)
        for vx, vy, c, a0, spin, size in self._confetti:
            x = W / 2 + vx * 900 * dt * (1 - 0.25 * dt)
            y = 300 - vy * 1500 * dt + 1400 * dt * dt
            ang = a0 + spin * dt
            pts = [(x + math.cos(ang + k * math.pi / 2 + (0.5 if k % 2 else 0)) * size * (0.5 if k % 2 else 0.9),
                    y + math.sin(ang + k * math.pi / 2 + (0.5 if k % 2 else 0)) * size * (0.5 if k % 2 else 0.9))
                   for k in range(4)]
            d.polygon(pts, fill=c + (int(255 * fade),))
        canvas.alpha_composite(layer)

    def draw_cta(self, canvas, t):
        a = clamp((t - 0.25) / 0.3)
        if a <= 0:
            return
        beat = (t % 2.0) / 2.0
        pulse = 1 + 0.045 * math.sin(math.pi * clamp(beat / 0.25)) if beat < 0.25 else 1.0
        outro = ease_in_out((t - EDIT_LEN - 0.1) / 0.5) if t > EDIT_LEN + 0.1 else 0.0
        scale = (0.7 + 0.3 * ease_out_back((t - 0.25) / 0.4)) * pulse * (1 + 0.22 * outro)
        cy = CTA_Y + (BAND_Y + BAND_H / 2 - CTA_Y) * outro
        pill = self.cta_plain.copy()
        # light sweep every 3 s
        ph = (t % 3.0) / 0.7
        if ph < 1:
            pw, hh = self.cta_size
            shine = Image.new("RGBA", pill.size)
            x = -120 + (pw + 240) * ph
            ImageDraw.Draw(shine).polygon([(x, 0), (x + 60, 0), (x + 20, hh), (x - 40, hh)], fill=(255, 255, 255, 150))
            mask = pill.getchannel("A")
            shine.putalpha(Image.composite(shine.getchannel("A"), Image.new("L", pill.size, 0), mask))
            pill.alpha_composite(shine)
        pill, _ = add_shadow(pill, offset=(0, 8), blur=14, alpha=0.6)
        paste_scaled(canvas, pill, W / 2, cy, scale=scale, alpha=a)

    def compose(self, frame, t):
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        band = self.band_image(frame, t)
        dim = 0.0
        if self.overlay_mode(t) or (24.50 <= t < 24.70) or (17.10 <= t < 17.28):
            k = 1.0
            if t < 17.28:
                k = clamp((t - 17.10) / 0.18)
            elif t >= 24.50:
                k = 1 - clamp((t - 24.50) / 0.2)
            small = band.resize((W // 6, BAND_H // 6), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
            blurred = small.resize((W, BAND_H), Image.BILINEAR)
            band = Image.blend(band, blurred, k)
            dim = 0.55 * k
        if t > EDIT_LEN:
            dim = max(dim, 0.55 * clamp((t - EDIT_LEN) / 0.5))
        if dim:
            band = Image.blend(band, Image.new("RGB", band.size, (0, 0, 0)), dim)
        canvas.paste(band, (0, BAND_Y))
        if not self.overlay_mode(t):
            canvas.alpha_composite(self.vignette(), (0, BAND_Y))
        self.draw_stickers(canvas, t)
        self.draw_export(canvas, t)
        self.draw_cards(canvas, t)
        self.subs.draw(canvas, t)
        self.draw_cta(canvas, t)
        for (t0, amt, d) in self.flashes:
            if t0 <= t < t0 + d:
                k = amt * (1 - (t - t0) / d) ** 2
                canvas = Image.blend(canvas, Image.new("RGBA", (W, H), (255, 255, 255, 255)), k)
        return canvas.convert("RGB")


def frames_from(path):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", "eq=contrast=1.06:saturation=1.14:gamma=0.98",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = SRC_W * SRC_H * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield Image.frombuffer("RGB", (SRC_W, SRC_H), buf, "raw", "RGB", 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--assets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", default="")
    args = ap.parse_args()
    r = Renderer(args.work, args.assets)
    mezz = os.path.join(args.work, "mezz.mp4")

    if args.frames:
        wanted = sorted(float(x) for x in args.frames.split(","))
        os.makedirs(args.out, exist_ok=True)
        for t in wanted:
            src_t = min(t, EDIT_LEN - 1 / FPS)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{src_t:.3f}", "-i", mezz, "-frames:v", "1",
                            "-vf", "eq=contrast=1.06:saturation=1.14:gamma=0.98", os.path.join(args.out, "_src.png")],
                           check=True)
            frame = Image.open(os.path.join(args.out, "_src.png")).convert("RGB")
            r.compose(frame, t).save(os.path.join(args.out, f"t_{t:06.2f}.png"))
        return

    n_total = int(round(TOTAL * FPS))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.out], stdin=subprocess.PIPE)
    last = None
    n = 0
    for frame in frames_from(mezz):
        if n >= n_total:
            break
        enc.stdin.write(r.compose(frame, n / FPS).tobytes())
        last = frame
        n += 1
        if n % 150 == 0:
            print(f"{n}/{n_total}", flush=True)
    while n < n_total:
        enc.stdin.write(r.compose(last, n / FPS).tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    print("done", n, "frames")


if __name__ == "__main__":
    main()
