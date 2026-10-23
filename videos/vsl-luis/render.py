#!/usr/bin/env python3
"""Render the VSL in the reference's sober style.

Part 1 (the pitch): 9:16 canvas, the horizontal take in a band with black above and below,
white two-tier subtitles beside the face, the proof screenshots as B-roll inside the band and
"Más info en mi perfil" in the black area below. Part 2: the client's testimonial, condensed,
full-screen vertical. Then a short black card with "Más info en mi perfil".

Usage:
    python3 render.py --work <dir> --assets <dir> --out video.mp4 [--frames 2.6,40.1]

<work> holds mezz.mp4 (part 1, 1920x1080 30 fps), testi.mp4 (part 2, 1080x1920 30 fps),
words.json, faces.json and testi_words.json. <assets> holds fonts/ and the screenshots.
With --frames it only writes PNG previews of those timestamps.
"""
import argparse
import json
import os
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

# Raw takes kept from the pitch; the 1.27 s pause between them is cut.
CUTS = [(0.70, 17.98), (19.25, 34.73)]
MAIN_LEN = 983 / FPS  # frames in mezz.mp4
# Testimonial excerpts, frame-aligned (k/30 s) on the raw testimonial timeline.
T_CUTS = [(34 / 30, 103 / 30), (213 / 30, 404 / 30), (1434 / 30, 1595 / 30), (1608 / 30, 1701 / 30),
          (1824 / 30, 1886 / 30)]
TESTI_LEN = sum(b - a for a, b in T_CUTS)
TESTI_END = MAIN_LEN + TESTI_LEN
END_LEN = 42 / FPS  # closing card: black with "Más info en mi perfil"
TOTAL = TESTI_END + END_LEN

WHITE = (255, 255, 255)
CTA_Y = 1440
SUB_COL_X = 30
SUB_COL_CY = BAND_Y + 330
BROLL_SUB_TOP = 1178
TESTI_SUB_TOP = 1325  # the client's chin reaches y≈1260

# B-roll inside the band (edit timeline): screenshots 2+3 on "views estancadas", 1 on "300 mil".
BROLL = [(17.28, 21.05, "recurso23.jpeg", (0.50, 0.93), 1.22), (21.05, 24.45, "recurso1.jpeg", (0.28, 0.93), 1.40)]


def raw_to_edit(t, cuts, base=0.0):
    off = 0.0
    for a, b in cuts:
        if t < b + 0.05:
            return base + max(0.0, t - a) + off
        off += b - a
    return base + off


def edit_to_raw(t):
    for a, b in CUTS:
        if t <= b - a:
            return a + t
        t -= b - a
    return CUTS[-1][1]


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_in_out(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


class Fonts:
    def __init__(self, folder):
        self.folder = folder
        self.cache = {}

    def get(self, name, size):
        key = (name, int(size))
        if key not in self.cache:
            self.cache[key] = ImageFont.truetype(os.path.join(self.folder, name), int(size))
        return self.cache[key]


def add_shadow(img, offset=(0, 4), blur=7, alpha=0.75):
    pad = blur * 2 + max(abs(offset[0]), abs(offset[1]))
    out = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    out.alpha_composite(sh, (pad + offset[0], pad + offset[1]))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(img, (pad, pad))
    return out, pad


def text_sprite(text, font, stroke=2):
    """White text with a thin dark edge and soft shadow; returns (sprite, ox, oy) where
    (ox, oy) is the text's left-baseline origin inside the sprite."""
    l, t, r, b = font.getbbox(text, anchor="ls", stroke_width=stroke)
    pad = 4
    img = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad))
    ImageDraw.Draw(img).text((pad - l, pad - t), text, font=font, fill=WHITE, anchor="ls",
                             stroke_width=stroke, stroke_fill=(20, 20, 20))
    img, sp = add_shadow(img)
    return img, pad - l + sp, pad - t + sp


def paste(canvas, sprite, x, y, alpha=1.0, scale=1.0):
    """Composite sprite centred at (x, y)."""
    if alpha <= 0.01:
        return
    img = sprite
    if abs(scale - 1) > 0.004:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BICUBIC)
    if alpha < 0.999:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    px, py = int(round(x - img.width / 2)), int(round(y - img.height / 2))
    canvas.alpha_composite(img, (max(0, px), max(0, py)), (max(0, -px), max(0, -py)))


# ---------------------------------------------------------------- subtitles
# Reference style: short lowercase lines, plus an optional bigger second line for emphasis.
# "/" splits lines and "^" marks the big line. Words map 1:1 onto the whisper words.
MAIN_CHUNKS = [
    "lo más / importante^", "en un servicio", "es la / puntualidad^", "y el / compromiso^", "y si tú",
    "trabajas con", "un editor / de video^", "que no tiene", "nada de eso", "y de paso",
    "no te ha / resultado^", "dime con quién", "estás trabajando", "y es / súper loco^", "porque hace",
    "un momento", "estaba hablando", "con un cliente", "que comenzó", "que tenía",
    "las views / estancadas^", "no crecía", "para nada", "ya pegamos", "un video",
    "por más de / 300 mil vistas^", "crecimiento^", "impacto^", "y solamente", "tenemos / 15 días^",
    "trabajando", "hermano", "van a ver", "cómo crece", "esa persona",
    "y cómo todo", "sigue / creciendo^", "a otro / nivel^",
]
TESTI_CHUNKS = [
    "solo tengo", "palabras de / agradecimiento^", "lo que hiciste", "con mi cuenta", "y llevamos ¿qué?",
    "19, 20 días^", "publicando", "y una / total locura^", "mira lo que", "este muchacho",
    "ha logrado", "con mi cuenta", "o sea", "sabe / lo que hace^", "y sin duda alguna",
    "100 por ciento / recomendado^", "se vienen / niveles^", "let's go",
]


def build_chunks(specs, words, to_edit, end_time):
    chunks, i = [], 0
    for spec in specs:
        lines = []
        for raw_line in spec.split("/"):
            raw_line = raw_line.strip()
            big = raw_line.endswith("^")
            text = raw_line.rstrip("^").strip()
            n = len(text.split())
            ws = words[i:i + n]
            i += n
            lines.append({"text": text, "big": big, "t": to_edit(ws[0]["s"]), "end": to_edit(ws[-1]["e"])})
        chunks.append({"lines": lines, "t0": lines[0]["t"], "last": lines[-1]["end"]})
    assert i == len(words), (i, len(words))
    for a, b in zip(chunks, chunks[1:]):
        a["t1"] = min(b["t0"], a["last"] + 0.6)
    chunks[-1]["t1"] = end_time
    return chunks


class Subtitles:
    def __init__(self, fonts):
        self.fonts = fonts
        self.chunks = []

    def add(self, chunks, place):
        """place(chunk) -> (centre x, max width, top y or None for vertical centring, size scale)."""
        for ch in chunks:
            cx, max_w, top, k = place(ch)
            placed = []
            for line in ch["lines"]:
                name = "Poppins-ExtraBold.ttf" if line["big"] else "Poppins-SemiBold.ttf"
                size = int((70 if line["big"] else 44) * k)
                while True:
                    f = self.fonts.get(name, size)
                    if f.getlength(line["text"]) <= max_w or size <= 26:
                        break
                    size -= 2
                l, t, r, b = f.getbbox(line["text"], anchor="ls")
                placed.append((line, f, -t, max(b, 0), size))
            gap = 6
            total = sum(a + d for _, _, a, d, _ in placed) + gap * (len(placed) - 1)
            y = top if top is not None else SUB_COL_CY - total / 2
            for idx, (line, f, asc, desc, size) in enumerate(placed):
                if idx:
                    y += gap
                base = y + asc
                spr, ox, oy = text_sprite(line["text"], f, stroke=2 if size < 60 else 3)
                x0 = cx - f.getlength(line["text"]) / 2
                line["sprite"] = (spr, x0 + spr.width / 2 - ox, base + spr.height / 2 - oy)
                y = base + desc
            self.chunks.append(ch)

    def draw(self, canvas, t):
        for ch in self.chunks:
            if not (ch["t0"] - 0.03 <= t < ch["t1"]):
                continue
            for line in ch["lines"]:
                u = (t - line["t"] + 0.03) / 0.1
                if u <= 0:
                    continue
                spr, x, y = line["sprite"]
                paste(canvas, spr, x, y, alpha=clamp(u * 1.5), scale=1 + 0.05 * (1 - ease_in_out(u)))


# ---------------------------------------------------------------- renderer
class Renderer:
    def __init__(self, work, assets):
        self.fonts = Fonts(os.path.join(assets, "fonts"))
        self.assets = assets
        words = json.load(open(os.path.join(work, "words.json")))
        words[0]["s"] = 0.80  # whisper stretches the first word over the leading silence
        faces = json.load(open(os.path.join(work, "faces.json")))
        self.face_t = np.array([f["t"] for f in faces])
        fl = np.array([f["x"] if f["x"] is not None else np.nan for f in faces], float)
        idx = np.arange(len(fl))
        good = ~np.isnan(fl)
        self.face_l = np.interp(idx, idx[good], fl[good])

        tw = json.load(open(os.path.join(work, "testi_words.json")))
        tw = [w for w in tw if any(a - 0.05 <= w["s"] < b for a, b in T_CUTS)]
        tw[0]["s"] = max(tw[0]["s"], T_CUTS[0][0])

        self.subs = Subtitles(self.fonts)
        main = build_chunks(MAIN_CHUNKS, words, lambda t: raw_to_edit(t, CUTS), MAIN_LEN)
        testi = build_chunks(TESTI_CHUNKS, tw, lambda t: raw_to_edit(t, T_CUTS, MAIN_LEN), TESTI_END)
        for ch in main:  # a line never outlives the shot it was laid out for
            for t0, t1, *_ in BROLL:
                for edge in (t0, t1):
                    if ch["t0"] < edge < ch["t1"]:
                        ch["t1"] = edge
        self.subs.add(main, self.place_main)
        self.subs.add(testi, lambda ch: (W / 2, 900, TESTI_SUB_TOP, 1.15))  # on the chest, below the face

        self.broll = []
        for t0, t1, name, focus, zmax in BROLL:
            self.broll.append((t0, t1, self.make_broll(name), focus, zmax))
        self.cta = self.make_cta()
        # (start time, zoom): cuts between a wide and a tight framing, as in the reference
        self.zoom_keys = [(0.0, 1.08), (4.42, 1.20), (9.92, 1.08), (11.30, 1.20), (13.06, 1.08),
                          (24.55, 1.20), (25.55, 1.08), (27.67, 1.20), (28.71, 1.08)]
        self.testi_zoom = [1.0, 1.07, 1.0, 1.07, 1.0]

    # -- layout helpers ----------------------------------------------------
    def face_left_canvas(self, t):
        fl = np.interp(edit_to_raw(min(t, MAIN_LEN)), self.face_t, self.face_l) * SRC_W
        return PIVOT[0] + (fl - ANCHOR[0]) * _s0

    def in_broll(self, t):
        return any(t0 <= t < t1 for t0, t1, *_ in BROLL)

    def place_main(self, ch):
        if self.in_broll(ch["t0"] + 0.02):
            return W / 2, 900, BROLL_SUB_TOP, 1.0
        ts = np.arange(ch["t0"], ch["t1"] + 0.01, 0.1)
        right = min(self.face_left_canvas(t) for t in ts) - 4
        width = clamp(right - SUB_COL_X, 260, 380)
        return SUB_COL_X + width / 2, width, None, 1.0

    def make_broll(self, name):
        img = Image.open(os.path.join(self.assets, name)).convert("RGB")
        bg = img.resize((W // 8, BAND_H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4))
        bg = Image.blend(bg.resize((W, BAND_H), Image.BICUBIC), Image.new("RGB", (W, BAND_H)), 0.55)
        return {"img": img, "bg": bg}

    def make_cta(self):
        f = self.fonts.get("Poppins-SemiBold.ttf", 44)
        label = "Más info en mi perfil"
        tw = f.getlength(label)
        pw, ph = int(tw + 76), 92
        img = Image.new("RGBA", (pw, ph))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((1, 1, pw - 2, ph - 2), ph // 2, outline=(255, 255, 255, 235), width=3)
        d.text((pw / 2, ph / 2 + 2), label, font=f, fill=WHITE, anchor="mm")
        return add_shadow(img, blur=8, alpha=0.6)[0]

    # -- per-frame ----------------------------------------------------------
    def zoom_at(self, t):
        z, t_key = self.zoom_keys[0][1], 0.0
        for t0, z0 in self.zoom_keys:
            if t >= t0:
                z, t_key = z0, t0
        drift = 1 + 0.012 * min(t - t_key, 4.0)  # slow push between cuts
        if t >= 28.71:  # final build: steady push to the end of the pitch
            drift = 1 + 0.10 * ease_in_out((t - 28.71) / (MAIN_LEN - 28.71))
        return z * drift

    def band_main(self, frame, t):
        s = COVER * self.zoom_at(t)
        sw, sh = W / s, BAND_H / s
        x0 = clamp(ANCHOR[0] - PIVOT[0] / s, 0, SRC_W - sw)
        y0 = clamp(ANCHOR[1] - PIVOT[1] / s, 0, SRC_H - sh)
        return frame.resize((W, BAND_H), Image.BICUBIC, box=(x0, y0, x0 + sw, y0 + sh))

    def band_broll(self, t):
        for t0, t1, br, focus, zmax in self.broll:
            if t0 <= t < t1:
                band = br["bg"].copy()
                img = br["img"]
                u = ease_in_out((t - t0) / (t1 - t0))
                z = 1 + (zmax - 1) * u
                fit = (BAND_H - 40) / img.height
                # crop window that zooms toward `focus` (fractions of the screenshot)
                cw, chh = img.width / z, img.height / z
                fx, fy = focus[0] * img.width, focus[1] * img.height
                x0 = clamp(fx - cw * focus[0], 0, img.width - cw)
                y0 = clamp(fy - chh * focus[1], 0, img.height - chh)
                ow, oh = int(img.width * fit), int(img.height * fit)
                shot = img.resize((ow, oh), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + chh))
                mask = Image.new("L", (ow, oh), 0)
                ImageDraw.Draw(mask).rounded_rectangle((0, 0, ow - 1, oh - 1), 18, fill=255)
                band.paste(shot, ((W - ow) // 2, (BAND_H - oh) // 2), mask)
                return band
        return None

    def compose(self, frame, t):
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        if t < MAIN_LEN:
            band = self.band_broll(t) or self.band_main(frame, t)
            canvas.paste(band, (0, BAND_Y))
        elif t < TESTI_END:
            canvas.paste(self.testi_frame(frame, t), (0, 0))
            canvas.alpha_composite(self.bottom_shade())
        self.subs.draw(canvas, t)
        fade = clamp((t - (TESTI_END - 0.45)) / 0.45)
        if 0 < fade < 1:
            canvas = Image.blend(canvas, Image.new("RGBA", (W, H), (0, 0, 0, 255)), fade)
        if t < TESTI_END:  # in the black area of the pitch; out of the way during the testimonial
            paste(canvas, self.cta, W / 2, CTA_Y, alpha=clamp((t - 0.3) / 0.4) * (1 - clamp((t - MAIN_LEN) / 0.25)))
        else:
            u = (t - TESTI_END - 0.1) / 0.35
            paste(canvas, self.cta, W / 2, H / 2, alpha=clamp(u) * (1 - clamp((t - TOTAL + 0.3) / 0.3)),
                  scale=1.18 - 0.04 * ease_in_out(u))
        return canvas.convert("RGB")

    def testi_frame(self, frame, t):
        rel = t - MAIN_LEN
        acc = 0.0
        for i, (a, b) in enumerate(T_CUTS):
            if rel < acc + (b - a) or i == len(T_CUTS) - 1:
                z = self.testi_zoom[i] * (1 + 0.012 * min(rel - acc, 4.0))
                break
            acc += b - a
        if z <= 1.001:
            return frame
        cw, chh = W / z, H / z
        cx, cy = W * 0.5, H * 0.65  # pivot on the chin so the face grows upward, away from the subtitles
        x0 = clamp(cx - cw / 2, 0, W - cw)
        y0 = clamp(cy - chh / 2, 0, H - chh)
        return frame.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + chh))

    _shade = None

    def bottom_shade(self):
        if self._shade is None:
            y = np.linspace(0, 1, H)
            a = (np.clip((y - 0.52) / 0.48, 0, 1) ** 1.2 * 0.62 * 255).astype(np.uint8)
            s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            s.putalpha(Image.fromarray(np.repeat(a[:, None], W, axis=1), "L"))
            self._shade = s
        return self._shade


EQ = "eq=contrast=1.05:saturation=1.08"


def frames_from(path, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", EQ, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    size = w * h * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield Image.frombuffer("RGB", (w, h), buf, "raw", "RGB", 0, 1)


def grab(path, t, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-vf", EQ, out],
                   check=True)
    return Image.open(out).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--assets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", default="")
    args = ap.parse_args()
    r = Renderer(args.work, args.assets)
    mezz = os.path.join(args.work, "mezz.mp4")
    testi = os.path.join(args.work, "testi.mp4")

    if args.frames:
        os.makedirs(args.out, exist_ok=True)
        tmp = os.path.join(args.out, "_src.png")
        for t in sorted(float(x) for x in args.frames.split(",")):
            frame = grab(mezz, t, tmp) if t < MAIN_LEN else grab(testi, t - MAIN_LEN, tmp) if t < TESTI_END else None
            r.compose(frame, t).save(os.path.join(args.out, f"t_{t:06.2f}.png"))
        return

    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.out], stdin=subprocess.PIPE)
    n = 0
    for path, size, limit in ((mezz, (SRC_W, SRC_H), MAIN_LEN), (testi, (W, H), TESTI_END)):
        for frame in frames_from(path, *size):
            if n >= round(limit * FPS):
                break
            enc.stdin.write(r.compose(frame, n / FPS).tobytes())
            n += 1
            if n % 150 == 0:
                print(f"{n}/{round(TOTAL * FPS)}", flush=True)
    while n < round(TOTAL * FPS):
        enc.stdin.write(r.compose(None, n / FPS).tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    print("done", n, "frames")


if __name__ == "__main__":
    main()
