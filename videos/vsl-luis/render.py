#!/usr/bin/env python3
"""Render the VSL in the reference's sober style.

Part 1 (the pitch): 9:16 canvas, the horizontal take in a band with black above and below,
white subtitles beside the face (kept clear of the left edge, which phones crop), the proof
screenshots as B-roll inside the band. Part 2: the client's testimonial, condensed and cropped
1:1 in the same black frame, closing on "100% recomendado".

Usage:
    python3 render.py --work <dir> --assets <dir> --out video.mp4 [--frames 2.6,40.1]

<work> holds mezz.mp4 (part 1, 1920x1080 30 fps), testi.mp4 (part 2, 1080x1920 30 fps),
words.json, faces.json and testi_words.json. <assets> holds fonts/Coolvetica-Rg.otf and the
screenshots. With --frames it only writes PNG previews of those timestamps.
"""
import argparse
import json
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
FONT = "Coolvetica-Rg.otf"

# Pitch excerpts as 30 fps frame ranges of the raw take (same list as build.sh). Dropped:
# the leading silence, a pause after "un momento", the false start "que comenzó…" and "hermano".
CUTS_F = [(21, 430), (442, 494), (581, 886), (915, 1042)]
# Testimonial excerpts (frame ranges, same list as build.sh). Dropped: "¿qué? 19," (keeps "llevamos
# 20 días"), hesitation pauses, "o sea" and everything after "100% recomendado", which closes the video.
T_CUTS_F = [(34, 103), (213, 275), (306, 345), (358, 404), (1434, 1454), (1461, 1489), (1502, 1546),
            (1565, 1595), (1607, 1716)]
CUTS = [(a / FPS, b / FPS) for a, b in CUTS_F]
T_CUTS = [(a / FPS, b / FPS) for a, b in T_CUTS_F]
MAIN_LEN = sum(b - a for a, b in CUTS_F) / FPS
TESTI_LEN = sum(b - a for a, b in T_CUTS_F) / FPS
HOLD = 18 / FPS  # last testimonial frame held under "100% recomendado" before the fade
TESTI_END = MAIN_LEN + TESTI_LEN
TOTAL = TESTI_END + HOLD

# Pitch band
BAND_Y, BAND_H = 470, 720
SRC_W, SRC_H = 1920, 1080
COVER = max(W / SRC_W, BAND_H / SRC_H)
WIDE, TIGHT = 1.18, 1.30  # zoom over "cover"; the crop is pinned to the left edge of the take,
# so zooming pushes the face right and the subtitle column keeps its room.
SAFE_X = 180  # text never starts closer to the left edge (tall phones crop ~100 px per side)
COL_CY = BAND_Y + BAND_H / 2

# Testimonial square: 1:1 crop of the vertical take, without the out-of-focus corner at the bottom.
SQ_Y = BAND_Y + BAND_H // 2 - W // 2
SQ_SRC_CY = 880
TESTI_SUB_TOP = SQ_Y + W + 26
BROLL_SUB_TOP = BAND_Y + BAND_H + 24

WHITE = (255, 255, 255)

# Whisper timings corrected against the waveform where a cut depends on them (raw seconds).
WORD_FIXES = {47: (14.76, 15.20), 51: (16.08, 16.44), 54: (19.42, 20.02), 80: (28.96, 29.50),
              81: (29.84, 30.24), 82: (30.54, 30.76)}

# Subtitles. "/" splits lines, "^" marks the big line, "{n}" makes a display token stand for n
# spoken words. Otherwise words map 1:1 onto the whisper words that survive the cuts.
MAIN_CHUNKS = [
    "lo más / importante^", "en un servicio", "es la / puntualidad^", "y el / compromiso^", "y si tú",
    "trabajas con", "un editor / de video^", "que no tiene", "nada de eso", "y de paso",
    "no te da / resultados^", "dime con quién", "estás trabajando", "y es / súper loco^", "porque hace",
    "un momento", "estaba hablando", "con un cliente", "que tenía", "las views / estancadas^",
    "no crecía", "para nada", "ya pegamos", "un video", "por más de / 300 mil vistas^",
    "crecimiento^", "impacto^", "y solamente", "tenemos / 15 días^", "trabajando",
    "van a ver", "cómo crece", "esa persona", "y cómo todo", "sigue / creciendo^",
    "a otro / nivel^",
]
TESTI_CHUNKS = [
    "solo tengo", "palabras de / agradecimiento^", "lo que hiciste", "con mi cuenta", "y llevamos",
    "20 días^", "publicando", "y una / total locura^", "mira lo que", "este muchacho",
    "ha logrado", "con mi cuenta", "sabe / lo que hace^", "y sin duda alguna", "100%{3} recomendado^",
]
# Framing per pitch chunk index (wide/tight), switching on the cuts so jumps read as edits.
FRAMING = {0: WIDE, 4: TIGHT, 11: WIDE, 13: TIGHT, 14: WIDE, 16: TIGHT, 25: TIGHT, 27: WIDE, 30: TIGHT, 33: WIDE}
PUSH_FROM = 33  # from this chunk the pitch pushes in slowly until it ends
# B-roll: screenshots 2+3 from the cut before "que tenía", screenshot 1 from "ya pegamos",
# back to the speaker at "crecimiento".
BROLL_CHUNKS = (22, 25)
TESTI_ZOOM = [1.0, 1.08, 1.0, 1.08, 1.0, 1.08, 1.0, 1.08, 1.0]


def to_edit(t, cuts, base=0.0):
    off = 0.0
    for a, b in cuts:
        if t < b:
            return base + max(0.0, t - a) + off
        off += b - a
    return base + off


def edit_to_raw(t):
    for a, b in CUTS:
        if t <= b - a:
            return a + t
        t -= b - a
    return CUTS[-1][1]


def kept(words, cuts):
    return [w for w in words if any(a <= (w["s"] + w["e"]) / 2 < b for a, b in cuts)]


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_in_out(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


class Fonts:
    def __init__(self, folder):
        self.folder = folder
        self.cache = {}

    def get(self, size):
        size = int(size)
        if size not in self.cache:
            self.cache[size] = ImageFont.truetype(os.path.join(self.folder, FONT), size)
        return self.cache[size]


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


def build_chunks(specs, words, to_edit_fn, end_time):
    chunks, i = [], 0
    for spec in specs:
        lines = []
        for raw_line in spec.split("/"):
            raw_line = raw_line.strip()
            big = raw_line.endswith("^")
            toks = raw_line.rstrip("^").split()
            n = 0
            for tok in toks:
                n += int(tok[tok.index("{") + 1:-1]) if "{" in tok else 1
            text = " ".join(tok.split("{")[0] for tok in toks)
            ws = words[i:i + n]
            i += n
            lines.append({"text": text, "big": big, "t": to_edit_fn(ws[0]["s"]), "end": to_edit_fn(ws[-1]["e"])})
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

    def add(self, ch, cx, max_w, top, small, big):
        """Lay out a chunk centred on cx; top=None centres it vertically on the band."""
        placed = []
        for line in ch["lines"]:
            size = big if line["big"] else small
            while True:
                f = self.fonts.get(size)
                if f.getlength(line["text"]) <= max_w or size <= 26:
                    break
                size -= 2
            l, t, r, b = f.getbbox(line["text"], anchor="ls")
            placed.append((line, f, -t, max(b, 0), size))
        gap = 8
        total = sum(a + d for _, _, a, d, _ in placed) + gap * (len(placed) - 1)
        y = top if top is not None else COL_CY - total / 2
        for idx, (line, f, asc, desc, size) in enumerate(placed):
            if idx:
                y += gap
            base = y + asc
            spr, ox, oy = text_sprite(line["text"], f, stroke=2 if size < 70 else 3)
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
                paste(canvas, spr, x, y, alpha=clamp(u * 1.5), scale=1 + 0.04 * (1 - ease_in_out(u)))


class Renderer:
    def __init__(self, work, assets):
        self.fonts = Fonts(os.path.join(assets, "fonts"))
        self.assets = assets
        words = json.load(open(os.path.join(work, "words.json")))
        for i, (s, e) in WORD_FIXES.items():
            words[i]["s"], words[i]["e"] = s, e
        words[0]["s"] = 0.80  # whisper stretches the first word over the leading silence
        words = kept(words, CUTS)
        faces = json.load(open(os.path.join(work, "faces.json")))
        self.face_t = np.array([f["t"] for f in faces])
        fl = np.array([f["x"] if f["x"] is not None else np.nan for f in faces], float)
        idx = np.arange(len(fl))
        good = ~np.isnan(fl)
        self.face_l = np.interp(idx, idx[good], fl[good])
        tw = kept(json.load(open(os.path.join(work, "testi_words.json"))), T_CUTS)

        main = build_chunks(MAIN_CHUNKS, words, lambda t: to_edit(t, CUTS), MAIN_LEN)
        testi = build_chunks(TESTI_CHUNKS, tw, lambda t: to_edit(t, T_CUTS, MAIN_LEN), TOTAL)
        self.cut_times = [sum(b - a for a, b in CUTS[:k]) for k in range(len(CUTS))]

        # framing keys (time, zoom), snapped onto a cut when a chunk starts right after one
        self.zoom_keys = []
        for ci, z in sorted(FRAMING.items()):
            t = main[ci]["t0"] - 0.03
            for c in self.cut_times:
                if 0 <= t - c < 0.25:
                    t = c
            self.zoom_keys.append((max(0.0, t), z))
        self.push_t = main[PUSH_FROM]["t0"]

        t_b1 = max(c for c in self.cut_times if c <= main[18]["t0"])
        t_b2 = main[BROLL_CHUNKS[0]]["t0"] - 0.05
        t_b3 = main[BROLL_CHUNKS[1]]["t0"] - 0.05
        r23 = Image.open(os.path.join(assets, "recurso23.jpeg")).convert("RGB")
        # the two screenshots are joined by a 3 px dark seam at x=400..402
        shots23 = [r23.crop((0, 0, 400, r23.height)), r23.crop((403, 0, r23.width, r23.height))]
        r1 = Image.open(os.path.join(assets, "recurso1.jpeg")).convert("RGB")
        self.broll = [(t_b1, t_b2, shots23), (t_b2, t_b3, [r1])]

        self.subs = Subtitles(self.fonts)
        for ch in main:
            for t0, t1, *_ in self.broll:
                for edge in (t0, t1):
                    if ch["t0"] < edge < ch["t1"]:
                        ch["t1"] = edge
            if self.in_broll(ch["t0"] + 0.02):
                self.subs.add(ch, W / 2, 860, BROLL_SUB_TOP, 50, 80)
            else:
                ts = np.arange(ch["t0"], ch["t1"] + 0.01, 0.1)
                right = min(self.face_left_canvas(t) for t in ts) - 14
                width = clamp(right - SAFE_X, 200, 360)
                self.subs.add(ch, SAFE_X + width / 2, width, None, 46, 78)
        for ch in testi:
            self.subs.add(ch, W / 2, 860, TESTI_SUB_TOP, 52, 96)

    # -- pitch -------------------------------------------------------------
    def zoom_at(self, t):
        z = self.zoom_keys[0][1]
        t_key = 0.0
        for t0, z0 in self.zoom_keys:
            if t >= t0:
                z, t_key = z0, t0
        if t >= self.push_t:  # final build: steady push to the end of the pitch
            return z * (1 + 0.10 * ease_in_out((t - self.push_t) / (MAIN_LEN - self.push_t)))
        return z * (1 + 0.01 * min(t - t_key, 4.0))  # slow drift between cuts

    def crop_box(self, t):
        s = COVER * self.zoom_at(t)
        sw, sh = W / s, BAND_H / s
        y0 = clamp(SRC_H * 0.5 - sh / 2, 0, SRC_H - sh)
        return s, (0.0, y0, sw, y0 + sh)

    def face_left_canvas(self, t):
        fl = np.interp(edit_to_raw(min(t, MAIN_LEN)), self.face_t, self.face_l) * SRC_W
        return fl * self.crop_box(t)[0]

    def in_broll(self, t):
        return any(t0 <= t < t1 for t0, t1, *_ in self.broll)

    def band_broll(self, t):
        for t0, t1, shots in self.broll:
            if not (t0 <= t < t1):
                continue
            band = Image.new("RGB", (W, BAND_H))  # plain black: the screenshots alone, uncropped
            z = 1 + 0.03 * ease_in_out((t - t0) / (t1 - t0))  # gentle push, whole screenshot stays visible
            h = int(round(680 * z))
            sized = [s.resize((int(round(s.width * h / s.height)), h), Image.LANCZOS) for s in shots]
            gap = int(36 * z)
            x = (W - sum(s.width for s in sized) - gap * (len(sized) - 1)) // 2
            for s in sized:
                band.paste(s, (x, (BAND_H - h) // 2))
                x += s.width + gap
            return band
        return None

    def band_main(self, frame, t):
        _, box = self.crop_box(t)
        return frame.resize((W, BAND_H), Image.BICUBIC, box=box)

    # -- testimonial ----------------------------------------------------------
    def testi_square(self, frame, t):
        rel = min(t - MAIN_LEN, TESTI_LEN - 1e-6)
        acc = 0.0
        for i, (a, b) in enumerate(T_CUTS):
            if rel < acc + (b - a):
                break
            acc += b - a
        z = TESTI_ZOOM[i] * (1 + 0.01 * min(rel - acc, 4.0))
        if i == len(T_CUTS) - 1:  # closing line: slow push on "100% recomendado"
            z *= 1 + 0.06 * ease_in_out((t - MAIN_LEN - acc) / (TOTAL - MAIN_LEN - acc))
        size = W / z
        x0 = (W - size) / 2
        y0 = clamp(SQ_SRC_CY - size / 2, 0, H - size)
        return frame.resize((W, W), Image.BICUBIC, box=(x0, y0, x0 + size, y0 + size))

    # -- frame ----------------------------------------------------------------
    def compose(self, frame, t):
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        if t < MAIN_LEN:
            band = self.band_broll(t) or self.band_main(frame, t)
            canvas.paste(band, (0, BAND_Y))
        else:
            canvas.paste(self.testi_square(frame, t), (0, SQ_Y))
        self.subs.draw(canvas, t)
        fade = clamp((t - (TOTAL - 0.5)) / 0.5)
        if fade > 0:
            canvas = Image.blend(canvas, Image.new("RGBA", (W, H), (0, 0, 0, 255)), fade)
        return canvas.convert("RGB")


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
            src_t = t if t < MAIN_LEN else min(t - MAIN_LEN, TESTI_LEN - 1 / FPS)
            frame = grab(mezz if t < MAIN_LEN else testi, src_t, tmp)
            r.compose(frame, t).save(os.path.join(args.out, f"t_{t:06.2f}.png"))
        return

    n_total = round(TOTAL * FPS)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.out], stdin=subprocess.PIPE)
    n, last = 0, None
    for path, size, limit in ((mezz, (SRC_W, SRC_H), MAIN_LEN), (testi, (W, H), TESTI_END)):
        for frame in frames_from(path, *size):
            if n >= round(limit * FPS):
                break
            enc.stdin.write(r.compose(frame, n / FPS).tobytes())
            last = frame
            n += 1
            if n % 150 == 0:
                print(f"{n}/{n_total}", flush=True)
    while n < n_total:  # hold the last testimonial frame
        enc.stdin.write(r.compose(last, n / FPS).tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    print("done", n, "frames")


if __name__ == "__main__":
    main()
