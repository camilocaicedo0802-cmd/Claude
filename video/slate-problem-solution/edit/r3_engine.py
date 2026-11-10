"""Reel 3 (v2) effects, modelled on 'Referencia_Reel_3_Slate': presenter always on screen, problem image card
at the top (slides in from the right, leaves upwards), solution card at the bottom (slides in from the left, label
inside), problem text in mixed typography (small Poppins SemiBold + big condensed Playfair Display Italic) that
fades in word by word, warm light-leak into a closer closing shot with mixed-type captions."""
import math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw
from ps_engine import *

SANS = ("Poppins-SemiBold.ttf", None)
PLAY = ("PlayfairDisplay-Italic[wght].ttf", 500)
SMALL, BIG, PLAY_SX = 52, 112, 0.84
CREAM = "#F6EDE1"

# ---------------------------------------------------------------- card video source
class CardClip:
    """Decodes a crop of a clip at card size (+8% margin for a slow push-in). Sequential reads, restarts on seek."""
    def __init__(self, path, src, cw, ch, cx=0.5, cy=0.5, wf=1.0, grade="", push=0.06):
        self.path, self.src, self.cw, self.ch, self.cx, self.cy, self.wf, self.grade, self.push = path, src, cw, ch, cx, cy, wf, grade, push
        self.mw, self.mh = int(cw * (1 + push)) // 2 * 2, int(ch * (1 + push)) // 2 * 2
        self.p = None; self.next_t = None; self.last = None; self.k = 1.0
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
        self.avail = max(0.2, float(d.strip() or 0) - src - 0.12)

    def prepare(self, dur):
        """Slow the clip down (gentle slow motion) when it is shorter than its time on screen."""
        self.k = max(1.0, dur / self.avail)

    def _start(self, lt):
        a = self.cw / self.ch
        crop = (f"crop=w='iw*{self.wf}':h='iw*{self.wf}/{a}':x='iw*{self.cx}-iw*{self.wf}/2':y='ih*{self.cy}-iw*{self.wf}/{a}/2'")
        vf = f"setpts=PTS*{self.k:.4f},fps={FPS},{crop},scale={self.mw}:{self.mh}:flags=lanczos" + (("," + self.grade) if self.grade else "") + ",format=rgb24"
        if self.p:
            try: self.p.kill()
            except Exception: pass
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{self.src + lt / self.k:.3f}", "-i", self.path, "-vf", vf,
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.next_t = lt

    def frame(self, lt, dur):
        if self.p is None or self.next_t is None or abs(lt - self.next_t) > 0.6 / FPS:
            self._start(lt)
        b = self.p.stdout.read(self.mw * self.mh * 3)
        if len(b) == self.mw * self.mh * 3:
            self.last = np.frombuffer(b, np.uint8).reshape(self.mh, self.mw, 3).astype(np.float32) / 255
        self.next_t = lt + 1.0 / FPS
        if self.last is None: return np.zeros((self.ch, self.cw, 3), np.float32)
        z = 1 + self.push * (1 - clamp01(lt / max(dur, 0.1)))      # slow pull-back (push from 1+push to 1)
        w, h = int(self.mw / z * (self.cw / self.mw) * (1 + self.push)), int(self.mh / z * (self.ch / self.mh) * (1 + self.push))
        w, h = min(w, self.mw), min(h, self.mh)
        x0, y0 = (self.mw - w) // 2, (self.mh - h) // 2
        return cv2.resize(self.last[y0:y0 + h, x0:x0 + w], (self.cw, self.ch), interpolation=cv2.INTER_AREA)

def card_frame_masks(cw, ch, r):
    m = rounded_mask(cw, ch, r)
    ring = ring_mask(cw, ch, r, 3)
    # light streak along the top edge (brighter on the left), like the reference card highlight
    g = np.zeros((ch, cw), np.float32); xs = np.linspace(1, 0.25, cw)
    g[:int(r * 0.9), :] = xs[None, :]
    streak = ring * np.clip(g * 1.4, 0, 1)
    return m, ring, streak

def draw_card(frame, img, x, y, a, masks, mblur=(0, 0), label=None):
    """Composite a card image (cw x ch) at (x, y) with rounded corners, cream glowing border and soft shadow."""
    m, ring, streak = masks
    ch, cw = m.shape
    pad = 40
    big = np.zeros((ch + 2 * pad, cw + 2 * pad, 3), np.float32); A = np.zeros((ch + 2 * pad, cw + 2 * pad), np.float32)
    big[pad:pad + ch, pad:pad + cw] = img; A[pad:pad + ch, pad:pad + cw] = m
    # border + glow
    R = np.zeros_like(A); R[pad:pad + ch, pad:pad + cw] = np.clip(ring * 0.55 + streak, 0, 1)
    glow = blur(R, 6) * 0.9
    col = np.array(hex2rgb("#FFF1D6"), np.float32) / 255
    big = big * (1 - R[..., None]) + col * R[..., None]
    A = np.maximum(A, np.clip(glow, 0, 1) * 0.6)
    big = np.where(A[..., None] > 0, big, col)
    bx, by = mblur
    if bx > 1 or by > 1:
        k = (max(1, int(by)) | 1, max(1, int(bx)) | 1)
        big = cv2.blur(big * A[..., None], (k[1], k[0])); A = cv2.blur(A, (k[1], k[0]))
        big = np.where(A[..., None] > 1e-3, big / np.maximum(A[..., None], 1e-3), 0)
    sh = blur(np.pad(m, pad), 16) * 0.35 * a
    composite(frame, solid_layer(sh, "#000000", x - pad, y - pad + 12))
    composite(frame, Layer(np.clip(big, 0, 1), A * a, x - pad, y - pad))

class TopCard:
    """Problem image card: slides in from the right (motion blur), slow push inside, leaves upwards."""
    def __init__(self, clip, t_in, t_out, box, d_in=0.32, d_out=0.30):
        self.clip, self.t_in, self.t_out, self.d_in, self.d_out = clip, t_in, t_out, d_in, d_out
        self.x, self.y, self.cw, self.ch = box
        self.masks = card_frame_masks(self.cw, self.ch, 34)
        clip.prepare(t_out + d_out - t_in)

    def apply(self, frame, t):
        if t < self.t_in or t >= self.t_out + self.d_out: return
        lt = t - self.t_in
        img = self.clip.frame(lt, self.t_out - self.t_in)
        x, y, bx, by = self.x, self.y, 0, 0
        if lt < self.d_in:
            u = lt / self.d_in; e = ease_out(u)
            x = self.x + (W + 40 - self.x) * (1 - e); bx = 70 * (1 - u) ** 1.5
        if t >= self.t_out:
            u = (t - self.t_out) / self.d_out; e = u * u
            y = self.y + (-self.ch - 80 - self.y) * e; x = self.x - 60 * e; by = 60 * u
        draw_card(frame, img, x, y, 1.0, self.masks, (bx, by))

class BottomCard:
    """Solution card: slides in from the left (motion blur), label inside; slides out to the right at the end."""
    def __init__(self, clip, t_in, t_out, box, label, d_in=0.28, d_out=0.26, exit=True):
        self.clip, self.t_in, self.t_out, self.d_in, self.d_out, self.exit = clip, t_in, t_out, d_in, d_out, exit
        self.x, self.y, self.cw, self.ch = box
        self.masks = card_frame_masks(self.cw, self.ch, 34)
        clip.prepare(t_out + d_out - t_in)
        # label: Poppins SemiBold, 1-2 lines, centered near the card bottom, on a soft dark gradient
        f = font(SANS[0], 42, SANS[1]); lines = label.split("\n")
        L = np.zeros((self.ch, self.cw), np.float32)
        im = Image.new("L", (self.cw, self.ch), 0); d = ImageDraw.Draw(im)
        lh = 46; y0 = self.ch - 26 - lh * len(lines)
        for i, s in enumerate(lines):
            tw = f.getlength(s); d.text(((self.cw - tw) / 2, y0 + i * lh - 6), s, font=f, fill=255)
        L = np.asarray(im, np.float32) / 255
        self.lab = L; self.lab_sh = blur(L, 5) * 0.85
        grad = np.clip((np.arange(self.ch) - self.ch * 0.45) / (self.ch * 0.55), 0, 1) ** 1.4 * 0.45
        self.grad = grad[:, None]

    def apply(self, frame, t):
        end = self.t_out + (self.d_out if self.exit else 0)
        if t < self.t_in or t >= end: return
        lt = t - self.t_in
        img = self.clip.frame(lt, self.t_out - self.t_in)
        img = img * (1 - self.grad)[..., None]                      # soft dark gradient behind the label
        img = img * (1 - self.lab_sh[..., None])                     # label shadow
        img = img * (1 - self.lab[..., None]) + self.lab[..., None]  # white label
        x, bx = self.x, 0
        if lt < self.d_in:
            u = lt / self.d_in; e = ease_out(u)
            x = self.x + (-self.cw - 40 - self.x) * (1 - e); bx = 70 * (1 - u) ** 1.5
        if self.exit and t >= self.t_out:
            u = (t - self.t_out) / self.d_out; e = u * u
            x = self.x + (W + 40 - self.x) * e; bx = 70 * u
        draw_card(frame, img, x, self.y, 1.0, self.masks, (bx, 0))

# ---------------------------------------------------------------- mixed typography
def token_mask(text, style):
    if style == "S":
        f = font(PLAY[0], BIG, PLAY[1]); m, base, _ = text_mask(text, f, pad=18, sx=PLAY_SX)
    else:
        f = font(SANS[0], SMALL, SANS[1]); m, base, _ = text_mask(text, f, pad=18)
    return m, base

class MixedText:
    """Rows of (text, style[, align]) tokens; style 's' small Poppins, 'S' big Playfair Italic. Rows are stacked
    tightly like the reference ('Diente flojo o / inflamación / de encías'). Each token fades in (blur + rise)
    at its own time; the block fades out at t_out."""
    def __init__(self, rows, times, t_out, cx=W / 2, cy=0.55 * H, d_out=0.22):
        self.t_out, self.d_out = t_out, d_out
        self.items = []                                 # (mask, x, y, t_on, color)
        rowinfo = []
        k = 0
        for row in rows:
            toks = []
            for tok in row:
                text, st = tok[0], tok[1]
                m, base = token_mask(text, st); toks.append((m, base, st, times[k])); k += 1
            align = row[0][2] if len(row[0]) > 2 else "left"
            gap = SMALL * 0.30
            w = sum(m.shape[1] - 36 for m, _, _, _ in toks) + gap * (len(toks) - 1)
            has_big = any(st == "S" for _, _, st, _ in toks)
            rowinfo.append((toks, w, has_big, align))
        maxw = max(r[1] for r in rowinfo)
        # baselines: tight leading
        y = 0; bases = []
        for i, (toks, w, has_big, align) in enumerate(rowinfo):
            if i == 0: y += (BIG * 0.80 if has_big else SMALL * 0.95)
            else: y += (BIG * 0.80 if has_big else SMALL * 1.02)
            bases.append(y)
        total = bases[-1] + (BIG * 0.18 if rowinfo[-1][2] else SMALL * 0.25)
        top = cy - total / 2; left = cx - maxw / 2
        for (toks, w, has_big, align), base_y in zip(rowinfo, bases):
            x = left if align == "left" else (left + maxw - w if align == "right" else cx - w / 2)
            for m, base, st, ton in toks:
                col = CREAM if st == "S" else "#FFFFFF"
                self.items.append((m, x - 18, top + base_y - base, ton, col))
                x += m.shape[1] - 36 + SMALL * 0.30

    def layers(self, t):
        if t >= self.t_out + self.d_out: return []
        fo = 1 - clamp01((t - self.t_out) / self.d_out)
        out = []
        for m, x, y, ton, col in self.items:
            if t < ton: continue
            u = clamp01((t - ton) / 0.22); a = ease_out(u) * fo
            mm = blur(m, 5 * (1 - u)) if u < 1 else m
            out += [Layer(l.rgb, l.alpha * a, l.x, l.y) for l in
                    with_shadow(mm, col, x, y + 10 * (1 - ease_out(u)), sh_r=7, sh_dy=3, sh_op=0.55)]
        return out

class LightLeak:
    """Warm film-burn flash peaking at tc (reference transition into the closing shot)."""
    def __init__(self, tc, d_in=0.16, d_out=0.30):
        self.tc, self.d_in, self.d_out = tc, d_in, d_out
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
        g1 = np.exp(-(((xx - W / 8 * 1.5) / (W / 6)) ** 2 + ((yy - H / 8 * 1.6) / (H / 4)) ** 2))
        g2 = np.exp(-(((xx - W / 8 * 0.4) / (W / 5)) ** 2 + ((yy - H / 8 * 0.5) / (H / 5)) ** 2))
        self.g = cv2.resize(np.clip(g1 * 0.9 + g2 * 0.8, 0, 1), (W, H))

    def post(self, frame, t):
        if t < self.tc - self.d_in or t > self.tc + self.d_out: return frame
        u = (t - (self.tc - self.d_in)) / self.d_in if t < self.tc else 1 - (t - self.tc) / self.d_out
        u = clamp01(u) ** 1.3
        warm = np.array([1.0, 0.62, 0.22], np.float32); hot = np.array([1.0, 0.96, 0.88], np.float32)
        a = (self.g * u)[..., None]
        f = frame + a * warm * 1.1                      # additive warm burn
        f = f * (1 - (a * u) * 0.85) + hot * (a * u) * 0.85
        return np.clip(f, 0, 1)
