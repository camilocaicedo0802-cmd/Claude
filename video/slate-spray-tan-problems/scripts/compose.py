"""Composite the reel frame by frame (BGR, 1080x1920, 30 fps) and pipe it to x264.

usage: python3 compose.py <work> <render> <out.mp4> [start_frame end_frame] [--preview]
"""
import json, math, os, subprocess, sys
import numpy as np
import cv2

W, R, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
args = [a for a in sys.argv[4:] if not a.startswith("--")]
PREVIEW = "--preview" in sys.argv
T = json.load(open(os.path.join(W, "timeline.json")))
A = json.load(open(os.path.join(W, "assets.json")))
FPS, WD, HT = 30, 1080, 1920
N = int(math.ceil(T["duration"] * FPS))
F0, F1 = (int(args[0]), int(args[1])) if len(args) >= 2 else (0, N)
OVL = os.path.join(R, "ovl")
FX = os.path.join(W, "res", "fx")

clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
lerp = lambda a, b, e: a + (b - a) * e
def e_out_cubic(x): x = clamp(x); return 1 - (1 - x) ** 3
def e_out_quint(x): x = clamp(x); return 1 - (1 - x) ** 5
def e_in_out_cubic(x):
    x = clamp(x); return 4 * x * x * x if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def e_in_cubic(x): x = clamp(x); return x * x * x


# ------------------------------------------------------------------ grading
def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

GRADE_OVERRIDE = {
    # per-asset tweaks: (target luma, wb strength, saturation)
    "hook": (0.36, 0.35, 1.04), "s2_spray": (0.40, 0.35, 1.03), "s5_barrier": (0.40, 0.35, 1.02),
    "s8_consult": (0.40, 0.35, 1.02), "p5_hands": (0.40, 0.35, 1.02), "p3_dry": (0.38, 0.0, 1.0),
    "talk": (0.50, 0.55, 1.03), "p2_asap": (0.55, 0.0, 0.96), "p6_vacation": (0.55, 0.0, 0.98),
    "p7_event": (0.55, 0.2, 1.0), "s4_moisturize": (0.48, 0.2, 1.0), "s3_exfoliate": (0.48, 0.25, 1.0),
    "p4_fading": (0.50, 0.15, 1.0),
}

def make_grade(aid, img):
    tl, wbs, sat = GRADE_OVERRIDE.get(aid, (0.48, 0.5, 1.05))
    f = img.astype(np.float32) / 255.0
    b, g, r = f[..., 0], f[..., 1], f[..., 2]
    luma = 0.0722 * b + 0.7152 * g + 0.2126 * r
    m = (luma > 0.18) & (luma < 0.85)
    if m.sum() < 1000:
        m = luma >= 0
    mb, mg, mr = b[m].mean(), g[m].mean(), r[m].mean()
    target = np.array([0.90, 1.0, 1.06]) * mg              # warm-neutral (B, G, R)
    gains = np.clip((target / np.array([mb, mg, mr])) ** wbs, 0.90, 1.10)
    L = float(luma.mean())
    gamma = float(np.clip(math.log(tl) / math.log(max(L, 1e-3)), 0.80, 1.15))
    x = np.linspace(0, 1, 256, dtype=np.float32)
    luts = []
    for c in range(3):
        y = np.clip(x * gains[c], 0, 1) ** gamma
        y = y + 0.16 * (smoothstep(0, 1, y) - y)            # gentle S curve
        y = 0.016 + y * (0.985 - 0.016)                       # soft black lift / highlight roll
        hl = smoothstep(0.55, 1.0, y)
        if c == 2: y = y + 0.010 * hl                         # warm highlights
        if c == 0: y = y - 0.012 * hl
        luts.append(np.clip(y * 255 + 0.5, 0, 255).astype(np.uint8))
    lut = np.stack(luts, axis=1).reshape(256, 1, 3)
    return lut, sat


def apply_grade(img, grade):
    lut, sat = grade
    out = cv2.LUT(img, lut)
    if abs(sat - 1.0) > 0.005:
        hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV)
        hsv[..., 1] = cv2.convertScaleAbs(hsv[..., 1], alpha=sat)
        out = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return out


# ------------------------------------------------------------------ asset readers
class Video:
    def __init__(self, path, w, h):
        self.path, self.w, self.h = path, w, h
        self.proc, self.pos, self.last = None, -1, None
        n = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                            "stream=nb_read_packets", "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
        self.n = int(n)

    def _open(self):
        if self.proc: self.proc.kill()
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", self.path, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                                     stdout=subprocess.PIPE, bufsize=self.w * self.h * 3 * 2)
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


SIZE = {"full": (1188, 2112), "half": (1188, 1056)}
_cache = {}

def asset(aid):
    if aid not in _cache:
        a = A[aid]
        w, h = SIZE[a["out"]]
        if a["type"] == "video":
            obj = Video(a["file"], w, h)
            first = obj.frame(min(obj.n - 1, obj.n // 2))
            grade = make_grade(aid, first)
            obj._open()
            _cache[aid] = ("video", obj, grade, {})
        else:
            img = cv2.imread(a["file"], cv2.IMREAD_COLOR)
            grade = make_grade(aid, img)
            _cache[aid] = ("photo", apply_grade(img, grade), grade, {})
    return _cache[aid]


def asset_frame(aid, lt):
    kind, obj, grade, memo = asset(aid)
    if kind == "photo":
        return obj
    i = int(round(lt * FPS))
    i = int(clamp(i, 0, obj.n - 1))
    if memo.get("i") == i:
        return memo["img"]
    img = apply_grade(obj.frame(i), grade)
    memo["i"], memo["img"] = i, img
    return img


def view(img, ow, oh, z, cx=0.5, cy=0.5):
    """crop a window of size img/z centred at (cx, cy) and resize to (ow, oh)."""
    h, w = img.shape[:2]
    ww, wh = w / z, h / z
    x0 = clamp(cx * w - ww / 2, 0, w - ww)
    y0 = clamp(cy * h - wh / 2, 0, h - wh)
    # sub-pixel accurate crop+scale with an affine warp (smooth Ken Burns, no jitter)
    sx, sy = ow / ww, oh / wh
    M = np.float32([[sx, 0, -x0 * sx], [0, sy, -y0 * sy]])
    interp = cv2.INTER_AREA if sx < 0.98 else cv2.INTER_LINEAR
    if interp == cv2.INTER_AREA:
        # INTER_AREA is not supported by warpAffine: crop to integer box then resize
        xi, yi = int(x0), int(y0)
        crop = img[yi:yi + int(math.ceil(wh)) + 1, xi:xi + int(math.ceil(ww)) + 1]
        fx, fy = x0 - xi, y0 - yi
        M = np.float32([[sx, 0, -fx * sx], [0, sy, -fy * sy]])
        return cv2.warpAffine(crop, M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return cv2.warpAffine(img, M, (ow, oh), flags=interp, borderMode=cv2.BORDER_REFLECT)


def kb_z(aid, t, t0, t1):
    z0, z1 = A[aid].get("kb", [1.0, 1.05])
    return lerp(z0, z1, clamp((t - t0) / max(t1 - t0, 1e-3)))


# ------------------------------------------------------------------ scenes
PAIRS = T["pairs"]
OUTRO = T["outro"]
SPLIT_DUR = 0.42

def render_hook(t):
    img = asset_frame("hook", t)
    return view(img, WD, HT, kb_z("hook", t, 0, T["hook"]["end"] + 0.3))


def render_pair(p, t):
    lt = t - p["start"]
    Pimg = view(asset_frame(p["P"], lt), WD, HT, kb_z(p["P"], t, p["start"], p["end"]))
    e = e_out_quint((t - p["split"]) / SPLIT_DUR)
    if e <= 0:
        return Pimg
    top = A[p["P"]].get("top", 0.5)
    shift_max = clamp(top * HT - 480, 0, 960)
    shift = int(round(shift_max * e))
    canvas = np.empty_like(Pimg)
    canvas[:HT - shift] = Pimg[shift:]
    canvas[HT - shift:] = 0
    # de-emphasise the problem once the solution is on screen
    dim = 1 - 0.16 * e
    canvas[:960] = cv2.convertScaleAbs(canvas[:960], alpha=dim)
    S = view(asset_frame(p["S"], t - p["split"]), WD, 960, kb_z(p["S"], t, p["split"], p["end"]))
    if p.get("S2") and t >= p["s2_at"]:
        S2 = view(asset_frame(p["S2"], t - p["s2_at"]), WD, 960, kb_z(p["S2"], t, p["s2_at"], p["end"]))
        q = (t - p["s2_at"]) / 0.24
        if q >= 1:
            S = S2
        else:
            e2 = e_in_out_cubic(q)
            dx = int(round(WD * e2))
            mix = np.empty_like(S)
            mix[:, :WD - dx] = S[:, dx:]
            mix[:, WD - dx:] = S2[:, :dx]
            de = e_in_out_cubic(q + 0.5 / FPS / 0.24) - e_in_out_cubic(q - 0.5 / FPS / 0.24)
            kx = int(abs(de) * WD * 0.7)
            S = cv2.blur(mix, (kx, 1)) if kx > 2 else mix
    sy = int(round(HT - 960 * e))
    # vertical motion blur while the panel is moving fast
    v = 960 * (e_out_quint((t + 0.5 / FPS - p["split"]) / SPLIT_DUR) - e_out_quint((t - 0.5 / FPS - p["split"]) / SPLIT_DUR))
    k = int(abs(v) * 0.6)
    if k > 2:
        S = cv2.blur(S, (1, k))
    canvas[sy:] = S[:HT - sy]
    return canvas


def talk_src(t):
    m = OUTRO["talk_map"]
    if t <= m[0][0]:
        return m[0][3] - (m[0][0] - t)
    for k, (s, e, src, a) in enumerate(m):
        if s <= t <= e:
            return a + (t - s)
        if k + 1 < len(m) and e < t < m[k + 1][0]:
            ns = m[k + 1]
            return a + (e - s) if t - e < ns[0] - t else ns[3]
    s, e, src, a = m[-1]
    return a + (t - s)


def render_outro(t):
    clip = None
    for c in OUTRO["clips"]:
        if c["start"] <= t < c["end"]:
            clip = c
            break
    if clip is None:
        clip = OUTRO["clips"][-1] if t >= OUTRO["clips"][-1]["start"] else OUTRO["clips"][0]
    if clip["kind"] == "talk":
        z0, z1 = clip.get("zoom", [1.0, 1.0])
        z = lerp(z0, z1, clamp((t - clip["start"]) / (clip["end"] - clip["start"])))
        img = view(asset_frame("talk", talk_src(t)), WD, HT, z)
    else:
        aid = clip["asset"]
        lt = t - clip["start"]
        z = kb_z(aid, t, clip["start"], clip["end"])
        if clip.get("punch"):
            z *= 1 + 0.07 * (1 - e_out_cubic(lt / 0.28))
        img = view(asset_frame(aid, lt), WD, HT, z)
        if clip.get("flash"):
            a = clamp(1 - lt / 0.14) * 0.75
            if a > 0:
                img = cv2.addWeighted(img, 1 - a, np.full_like(img, 255), a, 0)
    return img


def scene_at(t):
    if t < T["hook"]["end"]:
        return ("hook", None)
    for p in PAIRS:
        if t < p["end"]:
            return ("pair", p)
    return ("outro", None)


def render_scene(sc, t):
    kind, p = sc
    if kind == "hook":
        return render_hook(t)
    if kind == "pair":
        return render_pair(p, t)
    return render_outro(t)


# ------------------------------------------------------------------ transitions
BOUNDS = []
seq = [("hook", None)] + [("pair", p) for p in PAIRS] + [("outro", None)]
ends = [T["hook"]["end"]] + [p["end"] for p in PAIRS]
for k, B in enumerate(ends):
    if k == 0 or k == len(ends) - 1:
        typ = "zoom"
    else:
        typ = "whip_left" if k % 2 == 1 else "whip_up"
    BOUNDS.append({"B": B, "type": typ, "a": seq[k], "b": seq[k + 1]})
WIN = {"whip_left": (0.15, 0.15), "whip_up": (0.15, 0.15), "zoom": (0.16, 0.24)}


def light_leak_frames():
    leaks = {}
    for k, name in [(0, "film burns(2).mp4"), (len(ends) - 1, "film burns(5).mp4")]:
        path = os.path.join(FX, name)
        if os.path.exists(path):
            leaks[k] = Video(path, 1080, 1920)
    return leaks
LEAKS = light_leak_frames()
LEAK_AT = {0: (-0.10, 0.45, 0.28), len(ends) - 1: (-0.05, 0.60, 0.20)}  # start offset, length, opacity


def screen(base, layer, op):
    l = cv2.convertScaleAbs(layer, alpha=op)
    inv = (255 - base.astype(np.uint16)) * (255 - l.astype(np.uint16)) // 255
    return (255 - inv).astype(np.uint8)


def render(t):
    for k, bd in enumerate(BOUNDS):
        pre, post = WIN[bd["type"]]
        if bd["B"] - pre <= t < bd["B"] + post:
            B = bd["B"]
            a_img = render_scene(bd["a"], min(t, B - 1.0 / FPS))
            b_img = render_scene(bd["b"], max(t, B))
            p = (t - (B - pre)) / (pre + post)
            if bd["type"].startswith("whip"):
                e = e_in_out_cubic(p)
                de = e_in_out_cubic(p + 0.5 / FPS / (pre + post)) - e_in_out_cubic(p - 0.5 / FPS / (pre + post))
                if bd["type"] == "whip_left":
                    dx = int(round(WD * e))
                    out = np.empty_like(a_img)
                    out[:, :WD - dx] = a_img[:, dx:]
                    out[:, WD - dx:] = b_img[:, :dx]
                    kx = int(abs(de) * WD * 0.7)
                    if kx > 2: out = cv2.blur(out, (kx, 1))
                else:
                    dy = int(round(HT * e))
                    out = np.empty_like(a_img)
                    out[:HT - dy] = a_img[dy:]
                    out[HT - dy:] = b_img[:dy]
                    ky = int(abs(de) * HT * 0.7)
                    if ky > 2: out = cv2.blur(out, (1, ky))
            else:  # zoom punch + flash
                if t < B:
                    q = (t - (B - pre)) / pre
                    z = 1 + 0.28 * e_in_cubic(q)
                    out = view(a_img, WD, HT, z)
                    bl = int(1 + 24 * e_in_cubic(q)) | 1
                    out = cv2.GaussianBlur(out, (bl, bl), 0) if bl > 2 else out
                    fl = 0.55 * e_in_cubic(q)
                else:
                    q = (t - B) / post
                    z = 1 + 0.22 * (1 - e_out_cubic(q))
                    out = view(b_img, WD, HT, z)
                    bl = int(1 + 20 * (1 - e_out_cubic(q))) | 1
                    out = cv2.GaussianBlur(out, (bl, bl), 0) if bl > 2 else out
                    fl = 0.55 * (1 - e_out_cubic(q * 1.2))
                if fl > 0.01:
                    out = cv2.addWeighted(out, 1 - fl, np.full_like(out, (235, 245, 255)), fl, 0)
            return out
    return render_scene(scene_at(t), t)


# ------------------------------------------------------------------ finishing
yy, xx = np.mgrid[0:HT, 0:WD].astype(np.float32)
vig = 1 - 0.10 * np.clip(((xx - WD / 2) / (WD * 0.62)) ** 2 + ((yy - HT / 2) / (HT * 0.60)) ** 2 - 0.35, 0, 1) ** 1.2
VIG = np.dstack([vig] * 3).astype(np.float32)
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 2.2, (HT // 2, WD // 2)).astype(np.float32) for _ in range(6)]


def finish(img, f, t):
    out = img.astype(np.float32) * VIG
    g = cv2.resize(GRAIN[f % len(GRAIN)], (WD, HT), interpolation=cv2.INTER_LINEAR)
    out += g[..., None]
    # light leaks
    for k, (off, ln, op) in LEAK_AT.items():
        if k in LEAKS:
            B = ends[k]
            lt = t - (B + off)
            if 0 <= lt < ln:
                lv = LEAKS[k]
                fr = lv.frame(int(lt / ln * (lv.n - 1))).astype(np.float32)
                lum = fr.mean(axis=2, keepdims=True)
                fr = lum * np.array([0.55, 0.85, 1.0], np.float32)   # BGR amber
                env = math.sin(math.pi * clamp(lt / ln)) * op
                out = 255 - (255 - np.clip(out, 0, 255)) * (255 - fr * env) / 255
    # final fade
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
        t = f / FPS
        img = render(t)
        img = finish(img, f, t)
        img = overlay(img, f)
        pr.stdin.write(img.tobytes())
        if f % 150 == 0:
            print(f"frame {f}/{F1}", flush=True)
    pr.stdin.close()
    pr.wait()


if __name__ == "__main__":
    main()
