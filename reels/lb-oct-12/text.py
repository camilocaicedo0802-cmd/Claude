"""On-screen text for reel LB-OCT-12, styled after the two covers (TAN Pearl + Glacial Indifference).

Part 1 fades in slowly at the start and leaves when the kitchen scene ends;
part 2 arrives at the end of cuerpo 7 and fades out slowly at the very end of the video.
"""
import math
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import edl

W, H = edl.W, edl.H
PLUM = (72, 34, 61)
PLUM_DEEP = (46, 20, 38)
ROSE = (188, 92, 95)
CREAM = (250, 237, 205)
LAVENDER = (154, 158, 192)
PEACH = (219, 163, 111)

HAZE = (253, 247, 238)

PAD = 40  # transparent margin around every layer so blur can spread


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _canvas(w, h):
    return Image.new("RGBA", (w + 2 * PAD, h + 2 * PAD), (0, 0, 0, 0))


def text_image(font, s, fill, tracking=0.0, shear=0.0):
    """RGBA image of one line (with PAD margin). tracking is in em."""
    if tracking:
        widths = [font.getlength(c) for c in s]
        width = int(sum(widths) + tracking * font.size * (len(s) - 1)) + 4
    else:
        width = int(font.getlength(s)) + 4
    asc, desc = font.getmetrics()
    img = _canvas(width, asc + desc)
    d = ImageDraw.Draw(img)
    if tracking:
        x = PAD
        for c, cw in zip(s, widths):
            d.text((x, PAD), c, font=font, fill=fill)
            x += cw + tracking * font.size
    else:
        d.text((PAD, PAD), s, font=font, fill=fill)
    if shear:
        w, h = img.size
        # positive shear leans the glyph tops to the right, like an italic
        img = img.transform((w + int(shear * h), h), Image.AFFINE, (1, shear, -shear * h, 0, 1, 0), Image.BICUBIC)
    bbox = img.getbbox()
    return img, bbox


def _trim(img, bbox):
    """Crop a line image vertically to its ink, keeping the PAD margin."""
    return img.crop((0, bbox[1] - PAD, img.width, bbox[3] + PAD))


def pill(inner, inner_bbox, bg, pad_x, pad_y, radius):
    """Put a text image on a rounded rectangle."""
    x0, y0, x1, y1 = inner_bbox
    tw, th = x1 - x0, y1 - y0
    w, h = tw + 2 * pad_x, th + 2 * pad_y
    img = _canvas(w, h)
    ImageDraw.Draw(img).rounded_rectangle((PAD, PAD, PAD + w, PAD + h), radius=radius, fill=bg)
    img.alpha_composite(inner.crop(inner_bbox), (PAD + pad_x, PAD + pad_y))
    return img


def sparkle(size, color):
    """Four-point sparkle (astroid), like the ones on the covers."""
    s = size * 4
    img = Image.new("RGBA", (s + 2 * PAD, s + 2 * PAD), (0, 0, 0, 0))
    pts = []
    for i in range(240):
        t = 2 * math.pi * i / 240
        pts.append((PAD + s / 2 + s / 2 * math.cos(t) ** 3, PAD + s / 2 + s / 2 * math.sin(t) ** 3))
    ImageDraw.Draw(img).polygon(pts, fill=color)
    return img.resize((size + PAD // 2, size + PAD // 2), Image.LANCZOS)


class Layer:
    def __init__(self, img, cx, top, t_in, t_out, in_dur=1.4, out_dur=1.0, twinkle=None):
        a = np.asarray(img, np.float32) / 255.0
        self.rgb = a[..., :3] * a[..., 3:4] * 255.0  # premultiplied
        self.alpha = a[..., 3:4]
        self.h, self.w = self.alpha.shape[:2]
        self.x = int(round(cx - self.w / 2))
        self.y = int(round(top - PAD))
        self.t_in, self.t_out, self.in_dur, self.out_dur = t_in, t_out, in_dur, out_dur
        self.twinkle = twinkle

    def state(self, t):
        ein = ease_out((t - self.t_in) / self.in_dur)
        eout = ease_in_out((t - self.t_out) / self.out_dur)
        op = ein * (1 - eout)
        if self.twinkle and op > 0:
            phase, speed = self.twinkle
            op *= 0.55 + 0.45 * (0.5 + 0.5 * math.sin(t * speed + phase))
        dy = (1 - ein) * 26 - eout * 14
        blur = (1 - ein) * 9 + eout * 8
        return op, dy, blur

    def draw(self, frame, t):
        op, dy, blur = self.state(t)
        if op <= 0.003:
            return frame
        rgb, alpha = self.rgb, self.alpha
        if blur > 0.35:
            rgb = cv2.GaussianBlur(rgb, (0, 0), blur)
            alpha = cv2.GaussianBlur(alpha, (0, 0), blur)[..., None]
        x, y = self.x, int(round(self.y + dy))
        fx0, fy0 = max(x, 0), max(y, 0)
        fx1, fy1 = min(x + self.w, W), min(y + self.h, H)
        if fx1 <= fx0 or fy1 <= fy0:
            return frame
        sl = (slice(fy0 - y, fy1 - y), slice(fx0 - x, fx1 - x))
        region = frame[fy0:fy1, fx0:fx1]
        a = alpha[sl] * op
        frame[fy0:fy1, fx0:fx1] = region * (1 - a) + rgb[sl] * op
        return frame


class Veil:
    """Soft haze at the top of the frame (like cover A) so the plum type reads on any background."""

    def __init__(self, y_full, y_end, color, strength, layers):
        ys = np.arange(H, dtype=np.float32)
        x = np.clip((ys - y_full) / (y_end - y_full), 0, 1)
        self.prof = ((1 - x * x * (3 - 2 * x)) * strength)[:int(y_end), None, None]
        self.y1 = int(y_end)
        self.color = np.array(color, np.float32)
        self.layers = layers

    def draw(self, frame, t):
        op = max(l.state(t)[0] for l in self.layers[:2])
        if op <= 0.003:
            return frame
        a = self.prof * op
        frame[:self.y1] = frame[:self.y1] * (1 - a) + self.color * a
        return frame


class Overlay:
    def __init__(self, font_dir, shots, total):
        starts = {s["id"]: s["start"] / edl.FPS for s in shots}
        end = total / edl.FPS
        pearl = os.path.join(font_dir, "TAN-Pearl-Regular.otf")
        bold = os.path.join(font_dir, "GlacialIndifference-Bold.otf")
        f = lambda p, s: ImageFont.truetype(p, s)
        self.items = []

        # Part 1: "No todo tiene que ser productividad."  (cover A: Pearl lines + rose pill)
        t_in, t_out = 0.7, starts["2b"]  # appears with the door, leaves with the kitchen
        top = 236
        l1, b1 = text_image(f(pearl, 96), "No todo tiene", PLUM)
        l2, b2 = text_image(f(pearl, 96), "que ser", PLUM)
        p_txt, p_box = text_image(f(bold, 66), "productividad.", (255, 255, 255), tracking=0.01, shear=0.18)
        p3 = pill(p_txt, p_box, ROSE, 32, 20, 24)
        lay1 = Layer(_trim(l1, b1), W / 2, top, t_in, t_out, 1.8, 1.0)
        lay2 = Layer(_trim(l2, b2), W / 2, top + 108, t_in + 0.6, t_out + 0.1, 1.8, 1.0)
        lay3 = Layer(p3, W / 2, top + 228, t_in + 1.2, t_out + 0.2, 1.8, 1.0)
        spk = [Layer(sparkle(44, ROSE), 170, top + 165, t_in + 1.6, t_out, 1.6, 1.0, (0.0, 2.1)),
               Layer(sparkle(36, LAVENDER), 915, top + 40, t_in + 2.0, t_out, 1.6, 1.0, (1.7, 1.7)),
               Layer(sparkle(24, PEACH), 860, top + 300, t_in + 2.3, t_out, 1.6, 1.0, (3.1, 2.4))]
        self.items.append(Veil(top + 210, top + 560, HAZE, 0.62, [lay1, lay2]))
        self.items += [lay1, lay2, lay3] + spk

        # Part 2: "A veces hay que parar, respirar y dedicarte un momento."  (cover B: caps + Pearl + pill)
        t_in, t_out = starts["7c"] + 0.1, end - 2.3  # arrives at the end of cuerpo 7, fades out at the end
        top = 214
        c1, cb1 = text_image(f(bold, 36), "A VECES HAY QUE", PLUM, tracking=0.3)
        c2, cb2 = text_image(f(pearl, 86), "parar, respirar", PLUM)
        c3, cb3 = text_image(f(pearl, 86), "y dedicarte", PLUM)
        q_txt, q_box = text_image(f(pearl, 66), "un momento.", CREAM)
        q4 = pill(q_txt, q_box, PLUM, 34, 18, 24)
        m1 = Layer(_trim(c1, cb1), W / 2, top, t_in, t_out, 1.8, 1.7)
        m2 = Layer(_trim(c2, cb2), W / 2, top + 66, t_in + 0.6, t_out + 0.1, 1.8, 1.7)
        m3 = Layer(_trim(c3, cb3), W / 2, top + 170, t_in + 1.2, t_out + 0.2, 1.8, 1.7)
        m4 = Layer(q4, W / 2, top + 296, t_in + 1.8, t_out + 0.3, 1.8, 1.7)
        spk2 = [Layer(sparkle(42, PEACH), 150, top + 120, t_in + 2.2, t_out, 1.6, 1.4, (0.4, 2.0)),
                Layer(sparkle(34, LAVENDER), 930, top + 10, t_in + 2.5, t_out, 1.6, 1.4, (2.2, 1.6)),
                Layer(sparkle(24, ROSE), 845, top + 330, t_in + 2.8, t_out, 1.6, 1.4, (4.0, 2.3))]
        self.items.append(Veil(top + 250, top + 640, HAZE, 0.62, [m1, m2]))
        self.items += [m1, m2, m3, m4] + spk2

    def apply(self, frame, t):
        for item in self.items:
            frame = item.draw(frame, t)
        return frame
