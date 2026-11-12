"""Compositor v2: talking head is the base layer; b-roll only lives in support cards.

usage: python3 compose2.py <work> <render> <out.mp4> [f0 f1] [--preview]
"""
import json, math, os, subprocess, sys
import numpy as np
import cv2

W, R, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
args = [a for a in sys.argv[4:] if not a.startswith("--")]
PREVIEW = "--preview" in sys.argv
T = json.load(open(os.path.join(W, "timeline.json")))
L = json.load(open(os.path.join(W, "layout.json")))
A = json.load(open(os.path.join(W, "assets.json")))
TF = json.load(open(os.path.join(W, "talk_faces.json")))
FPS, WD, HT = 30, 1080, 1920
N = L["n"]
F0, F1 = (int(args[0]), int(args[1])) if len(args) >= 2 else (0, N)
OVL = os.path.join(R, "ovl")
FX = os.path.join(W, "res", "fx")
FACE_Y = 840          # where the face centre sits on screen (clear of the text band and the card)

clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
lerp = lambda a, b, e: a + (b - a) * e
def e_out_cubic(x): x = clamp(x); return 1 - (1 - x) ** 3
def e_in_cubic(x): x = clamp(x); return x * x * x
def e_in_out_cubic(x):
    x = clamp(x); return 4 * x * x * x if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


# ------------------------------------------------------------------ grading (shared with v1)
def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

GRADE = {"hook": (0.36, 0.35, 1.04), "talk": (0.50, 0.55, 0.97),
         "s2_spray": (0.42, 0.35, 1.03), "s5_barrier": (0.42, 0.35, 1.02), "s8_consult": (0.42, 0.35, 1.02),
         "p5_hands": (0.42, 0.35, 1.02), "p3_dry": (0.40, 0.0, 1.0), "p2_asap": (0.55, 0.0, 0.96),
         "p6_vacation": (0.55, 0.0, 0.98), "p7_event": (0.55, 0.2, 1.0), "s4_moisturize": (0.48, 0.2, 1.0),
         "s3_exfoliate": (0.48, 0.25, 1.0), "s3_exfoliate2": (0.48, 0.25, 1.0), "p4_fading": (0.50, 0.15, 1.0),
         "s7_spray": (0.42, 0.35, 1.03)}

def make_grade(aid, img):
    tl, wbs, sat = GRADE.get(aid, (0.48, 0.5, 1.0))
    f = img.astype(np.float32) / 255.0
    b, g, r = f[..., 0], f[..., 1], f[..., 2]
    luma = 0.0722 * b + 0.7152 * g + 0.2126 * r
    m = (luma > 0.18) & (luma < 0.85)
    if m.sum() < 1000:
        m = luma >= 0
    mb, mg, mr = b[m].mean(), g[m].mean(), r[m].mean()
    target = np.array([0.90, 1.0, 1.06]) * mg
    gains = np.clip((target / np.array([mb, mg, mr])) ** wbs, 0.90, 1.10)
    L_ = float(luma.mean())
    gamma = float(np.clip(math.log(tl) / math.log(max(L_, 1e-3)), 0.80, 1.15))
    x = np.linspace(0, 1, 256, dtype=np.float32)
    luts = []
    for c in range(3):
        y = np.clip(x * gains[c], 0, 1) ** gamma
        y = y + 0.12 * (smoothstep(0, 1, y) - y)
        y = 0.016 + y * (0.985 - 0.016)
        hl = smoothstep(0.55, 1.0, y)
        if c == 2: y = y + 0.010 * hl
        if c == 0: y = y - 0.012 * hl
        luts.append(np.clip(y * 255 + 0.5, 0, 255).astype(np.uint8))
    return np.stack(luts, axis=1).reshape(256, 1, 3), sat

def apply_grade(img, grade):
    lut, sat = grade
    out = cv2.LUT(img, lut)
    if abs(sat - 1.0) > 0.005:
        hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV)
        hsv[..., 1] = cv2.convertScaleAbs(hsv[..., 1], alpha=sat)
        out = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return out


# ------------------------------------------------------------------ readers
class Video:
    def __init__(self, path, w, h):
        self.path, self.w, self.h = path, w, h
        self.proc, self.pos, self.last = None, -1, None
        n = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                            "stream=nb_read_packets", "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
        self.n = int(n)

    def _open(self):
        if self.proc:
            self.proc.kill(); self.proc.wait()
        self.proc = subprocess.Popen(["ffmpeg", "-v", "quiet", "-i", self.path, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=self.w * self.h * 3 * 2)
        self.pos, self.last = -1, None

    def frame(self, i):
        i = int(clamp(i, 0, self.n - 1))
        if self.proc is None or i < self.pos:
            self._open()
        while self.pos < i:
            buf = self.proc.stdout.read(self.w * self.h * 3)
            if len(buf) < self.w * self.h * 3:
                break
            self.last = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
            self.pos += 1
        return self.last

    def close(self):
        if self.proc:
            self.proc.kill(); self.proc.wait(); self.proc = None


SIZE = {"full": (1188, 2112), "half": (1188, 1056), "card": (1092, 490), "pol": (317, 363), "tile": (330, 336)}
_cache = {}
TALK_GRADE = None

def asset(aid):
    if aid not in _cache:
        a = A[aid]
        w, h = SIZE[a["out"]]
        if a["type"] == "video":
            obj = Video(a["file"], w, h)
            first = obj.frame(min(obj.n - 1, obj.n // 2)).copy()
            obj._open()
            _cache[aid] = ("video", obj, make_grade(aid, first), {})
        else:
            img = cv2.imread(a["file"], cv2.IMREAD_COLOR)
            g = make_grade(aid, img)
            _cache[aid] = ("photo", apply_grade(img, g), g, {})
    return _cache[aid]

def asset_frame(aid, lt):
    kind, obj, grade, memo = asset(aid)
    if kind == "photo":
        return obj
    i = int(clamp(round(lt * FPS), 0, obj.n - 1))
    if memo.get("i") != i:
        memo["i"], memo["img"] = i, apply_grade(obj.frame(i), grade)
    return memo["img"]

_talk = {}
def talk_frame(seg, src_rel):
    global TALK_GRADE
    if seg not in _talk:
        for k in list(_talk):          # keep at most 2 decoders alive
            if k != seg and len(_talk) >= 2:
                _talk[k][0].close(); del _talk[k]
        _talk[seg] = (Video(TF[seg]["file"], 1620, 2880), {})
    v, memo = _talk[seg]
    if TALK_GRADE is None:
        ref = Video(TF["C1"]["file"], 1620, 2880)
        TALK_GRADE = make_grade("talk", ref.frame(30).copy()); ref.close()
    i = int(clamp(round(src_rel * FPS), 0, v.n - 1))
    if memo.get("i") != i:
        memo["i"], memo["img"] = i, apply_grade(v.frame(i), TALK_GRADE)
    return memo["img"]


_masks = {}
def talk_mask(seg, src_rel):
    if seg not in _masks:
        p = os.path.join(W, "talk", seg + "_mask.npy")
        _masks.clear()
        _masks[seg] = np.load(p, mmap_mode="r") if os.path.exists(p) else None
    m = _masks[seg]
    if m is None:
        return None
    i = int(clamp(round(src_rel * FPS), 0, len(m) - 1))
    return m[i]


def defocus_bg(img, mask_small):
    """Portrait-mode style: blur only the wall behind her (normalised so her hair doesn't bleed into it)."""
    h, w = img.shape[:2]
    m = cv2.resize(mask_small.astype(np.float32) / 255.0, (w, h), interpolation=cv2.INTER_LINEAR)
    m = np.clip((m - 0.35) / 0.4, 0, 1)                       # firm up the edge a little
    m = cv2.GaussianBlur(m, (0, 0), 2.0)
    q = (w // 6, h // 6)
    bg = 1.0 - cv2.resize(m, q, interpolation=cv2.INTER_AREA)
    sm = cv2.resize(img, q, interpolation=cv2.INTER_AREA).astype(np.float32)
    num = cv2.GaussianBlur(sm * bg[..., None], (0, 0), 7.0)
    den = cv2.GaussianBlur(bg, (0, 0), 7.0)[..., None] + 1e-4
    blur = cv2.resize(num / den, (w, h), interpolation=cv2.INTER_CUBIC)
    blur = blur * 0.94 + 255 * 0.06                            # a touch lighter / airier
    out = img.astype(np.float32) * m[..., None] + blur * (1 - m[..., None])
    return np.clip(out, 0, 255).astype(np.uint8)


def view(img, ow, oh, z, cx=0.5, cy=0.5):
    h, w = img.shape[:2]
    ww, wh = w / z, h / z
    x0 = clamp(cx * w - ww / 2, 0, w - ww)
    y0 = clamp(cy * h - wh / 2, 0, h - wh)
    return crop_resize(img, x0, y0, ww, wh, ow, oh)

def crop_resize(img, x0, y0, ww, wh, ow, oh):
    sx, sy = ow / ww, oh / wh
    if sx < 0.98:
        xi, yi = int(x0), int(y0)
        crop = img[yi:yi + int(math.ceil(wh)) + 2, xi:xi + int(math.ceil(ww)) + 2]
        crop = cv2.resize(crop, (int(round(crop.shape[1] * sx)), int(round(crop.shape[0] * sy))), interpolation=cv2.INTER_AREA)
        fx, fy = (x0 - xi) * sx, (y0 - yi) * sy
        M = np.float32([[1, 0, -fx], [0, 1, -fy]])
        return cv2.warpAffine(crop, M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    M = np.float32([[sx, 0, -x0 * sx], [0, sy, -y0 * sy]])
    return cv2.warpAffine(img, M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def kb(aid, lt, span):
    z0, z1 = A[aid].get("kb", [1.0, 1.05])
    return lerp(z0, z1, clamp(lt / max(span, 0.1)))


# ------------------------------------------------------------------ base layers
def render_hook(t):
    return view(asset_frame("hook", t), WD, HT, kb("hook", t, T["hook"]["end"] + 0.3))

def render_talk(b):
    img = talk_frame(b["seg"], b["src"])
    mk = talk_mask(b["seg"], b["src"])
    z = b["zoom"] * b["punch"]
    fx, fy, fw = b["face"]
    h, w = img.shape[:2]
    ww, wh = w / z, h / z
    x0 = clamp(fx * w - (WD / 2) * (ww / WD), 0, w - ww)
    y0 = clamp(fy * h - FACE_Y * (wh / HT), 0, h - wh)
    out = crop_resize(img, x0, y0, ww, wh, WD, HT)
    if mk is not None:
        mh, mw = mk.shape
        sx_, sy_ = mw / w, mh / h
        msub = crop_resize(np.ascontiguousarray(mk)[..., None].repeat(3, axis=2), x0 * sx_, y0 * sy_, ww * sx_, wh * sy_, WD // 4, HT // 4)[..., 0]
        out = defocus_bg(out, msub)
    if b["punch"] > 1.02:
        k = int((b["punch"] - 1) * 60) | 1
        out = cv2.GaussianBlur(out, (k, k), 0)
    return out


# ------------------------------------------------------------------ cards
def rounded_mask(w, h, r):
    m = np.zeros((h * 4, w * 4), np.uint8)
    cv2.rectangle(m, (r * 4, 0), (w * 4 - r * 4, h * 4), 255, -1)
    cv2.rectangle(m, (0, r * 4), (w * 4, h * 4 - r * 4), 255, -1)
    for cx, cy in [(r, r), (w - r, r), (r, h - r), (w - r, h - r)]:
        cv2.circle(m, (cx * 4, cy * 4), r * 4, 255, -1)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0

_chrome = {}
def card_chrome(w, h, r=26, border=0):
    key = (w, h, r, border)
    if key not in _chrome:
        mask = rounded_mask(w, h, r)
        ring = None
        pad = 70
        sh = np.zeros((h + 2 * pad, w + 2 * pad), np.float32)
        sh[pad + 12:pad + 12 + h, pad:pad + w] = mask
        sh = cv2.GaussianBlur(sh, (0, 0), 24) * 0.28
        _chrome[key] = (mask, ring, sh, pad)
    return _chrome[key]

def blend_layer(canvas, layer, alpha, x, y):
    """alpha-blend layer (h,w,3 uint8/float) with alpha (h,w float 0..1) at x,y with clipping."""
    h, w = alpha.shape
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(WD, x + w), min(HT, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    a = alpha[y0 - y:y1 - y, x0 - x:x1 - x][..., None]
    roi = canvas[y0:y1, x0:x1].astype(np.float32)
    if layer is None:
        roi = roi * (1 - a)
    else:
        lay = layer[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
        roi = roi * (1 - a) + lay * a
    canvas[y0:y1, x0:x1] = np.clip(roi, 0, 255).astype(np.uint8)

def card_content(c, w, h):
    aid = c["asset"]
    img = view(asset_frame(aid, c["lt"]), w, h, kb(aid, c["lt"], 6.0))
    if c.get("asset2"):
        a2 = c["asset2"]
        img2 = view(asset_frame(a2, c["lt2"]), w, h, kb(a2, c["lt2"], 4.0))
        e = e_in_out_cubic(c["mix"])
        if e >= 1:
            img = img2
        else:
            dx = int(round(w * e))
            mix = np.empty_like(img)
            mix[:, :w - dx] = img[:, dx:]
            mix[:, w - dx:] = img2[:, :dx]
            img = mix
            if 0.05 < e < 0.95:
                img = cv2.blur(img, (31, 1))
    if c.get("dim", 0) > 0.001:
        img = cv2.convertScaleAbs(img, alpha=1 - c["dim"])
    return img

def draw_card(canvas, c):
    x, y, w, h = int(round(c["x"])), int(round(c["y"])), c["w"], c["h"]
    mask, ring, sh, pad = card_chrome(w, h)
    blend_layer(canvas, None, sh, x - pad, y - pad)
    img = card_content(c, w, h)
    blend_layer(canvas, img, mask, x, y)


POL_W, POL_H, POL_IN = 316, 400, (14, 14, 288, 330)
def draw_polaroid(canvas, c):
    if c["alpha"] <= 0.01:
        return
    px, py, pw, ph = POL_IN
    card = np.full((POL_H, POL_W, 3), 248, np.uint8)
    photo = view(asset_frame(c["asset"], c["lt"]), pw, ph, kb(c["asset"], c["lt"], 3.0))
    fl = clamp(1 - c["lt"] / 0.16) * 0.8                    # camera flash on the photo
    if fl > 0:
        photo = cv2.addWeighted(photo, 1 - fl, np.full_like(photo, 255), fl, 0)
    card[py:py + ph, px:px + pw] = photo
    mask = rounded_mask(POL_W, POL_H, 8)
    pad = 60
    big = np.zeros((POL_H + 2 * pad, POL_W + 2 * pad, 3), np.uint8)
    big[pad:pad + POL_H, pad:pad + POL_W] = card
    am = np.zeros((POL_H + 2 * pad, POL_W + 2 * pad), np.float32)
    am[pad:pad + POL_H, pad:pad + POL_W] = mask
    shadow = cv2.GaussianBlur(np.roll(am, 14, axis=0), (0, 0), 16) * 0.40
    cxy = ((POL_W + 2 * pad) / 2, (POL_H + 2 * pad) / 2)
    M = cv2.getRotationMatrix2D(cxy, -c["rot"], c["scale"])
    M[0, 2] += c["cx"] - cxy[0]
    M[1, 2] += c["cy"] - cxy[1]
    rgb = cv2.warpAffine(big, M, (WD, HT), flags=cv2.INTER_LINEAR)
    a = cv2.warpAffine(am, M, (WD, HT), flags=cv2.INTER_LINEAR) * c["alpha"]
    s = cv2.warpAffine(shadow, M, (WD, HT), flags=cv2.INTER_LINEAR) * c["alpha"]
    ys, xs = np.nonzero(s > 0.002)
    if len(ys) == 0:
        return
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    roi = canvas[y0:y1, x0:x1].astype(np.float32)
    roi *= (1 - s[y0:y1, x0:x1, None])
    aa = a[y0:y1, x0:x1, None]
    roi = roi * (1 - aa) + rgb[y0:y1, x0:x1].astype(np.float32) * aa
    canvas[y0:y1, x0:x1] = np.clip(roi, 0, 255).astype(np.uint8)


_yy = np.arange(560, dtype=np.float32)
TOP_MASK = np.clip((480 - _yy) / 90.0, 0, 1)[:, None, None]   # 1 above y=390, 0 below y=480 (never on her hair)

def soften_top(img):
    """Defocus the wall behind the top text band so the printed wall text doesn't compete."""
    band = img[:560]
    sm = cv2.resize(band, (WD // 4, 140), interpolation=cv2.INTER_AREA)
    sm = cv2.GaussianBlur(sm, (0, 0), 4.5)
    bl = cv2.resize(sm, (WD, 560), interpolation=cv2.INTER_LINEAR).astype(np.float32)
    img[:560] = (band.astype(np.float32) * (1 - TOP_MASK) + bl * TOP_MASK).astype(np.uint8)
    return img


def render_scene(f):
    fr = L["frames"][min(f, N - 1)]
    b = fr["base"]
    img = np.ascontiguousarray(render_talk(b))
    pass
    for c in fr["cards"]:
        if c["slot"] == "pol":
            draw_polaroid(img, c)
        else:
            draw_card(img, c)
    return img


# ------------------------------------------------------------------ hook -> talk transition, finishing
HOOK_END = T["hook"]["end"]
def render(f):
    return render_scene(f)


yy, xx = np.mgrid[0:HT, 0:WD].astype(np.float32)
vig = 1 - 0.10 * np.clip(((xx - WD / 2) / (WD * 0.62)) ** 2 + ((yy - HT / 2) / (HT * 0.60)) ** 2 - 0.35, 0, 1) ** 1.2
VIG = np.dstack([vig] * 3).astype(np.float32)
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 1.5, (HT // 2, WD // 2)).astype(np.float32) for _ in range(6)]
LEAK = None

def finish(img, f):
    t = f / FPS
    out = img.astype(np.float32) * VIG
    out += cv2.resize(GRAIN[f % len(GRAIN)], (WD, HT), interpolation=cv2.INTER_LINEAR)[..., None]
    if LEAK is not None:
        lt = t - (HOOK_END - 0.10)
        if 0 <= lt < 0.45:
            fr = LEAK.frame(int(lt / 0.45 * (LEAK.n - 1))).astype(np.float32)
            fr = fr.mean(axis=2, keepdims=True) * np.array([0.55, 0.85, 1.0], np.float32)
            env = math.sin(math.pi * clamp(lt / 0.45)) * 0.28
            out = 255 - (255 - np.clip(out, 0, 255)) * (255 - fr * env) / 255
    fo = clamp((T["duration"] - t) / 0.35)
    if fo < 1:
        out *= fo
    return np.clip(out, 0, 255).astype(np.uint8)

def overlay(img, f):
    p = os.path.join(OVL, f"{f:05d}.png")
    if not os.path.exists(p):
        return img
    ov = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if ov is None or ov.shape[2] < 4:
        return img
    a = ov[..., 3:4].astype(np.uint16)
    if a.max() == 0:
        return img
    return ((ov[..., :3].astype(np.uint16) * a + img.astype(np.uint16) * (255 - a) + 127) // 255).astype(np.uint8)


def main():
    enc = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{WD}x{HT}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p"]
    enc += (["-preset", "veryfast", "-crf", "22"] if PREVIEW else ["-preset", "slow", "-crf", "16", "-tune", "film",
            "-x264-params", "aq-mode=3", "-profile:v", "high", "-level", "4.2"])
    enc += ["-movflags", "+faststart", OUT]
    pr = subprocess.Popen(enc, stdin=subprocess.PIPE)
    for f in range(F0, F1):
        img = overlay(finish(render(f), f), f)
        pr.stdin.write(img.tobytes())
        if f % 150 == 0:
            print(f"frame {f}/{F1}", flush=True)
    pr.stdin.close()
    pr.wait()


if __name__ == "__main__":
    main()
