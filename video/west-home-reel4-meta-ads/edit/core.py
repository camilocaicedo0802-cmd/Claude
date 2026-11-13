import os, json, subprocess, math, hashlib
import numpy as np, cv2

ROOT = '/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/reel4/'
WEST = '/tmp/claude-0/-home-user-Claude/faa7ebf2-a7a1-5cbd-8118-c6eac51d8dd0/scratchpad/west/'
INT_DIR = ROOT + 'ints/'
IW, IH = 1242, 2208          # intermediate size (1.15x of 1080x1920) for zoom/rotation headroom
os.makedirs(INT_DIR, exist_ok=True)


# ------------------------------------------------------------------ easing / keyframes
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out_cubic(x):
    x = clamp(x); return 1 - (1 - x) ** 3


def ease_in_cubic(x):
    x = clamp(x); return x ** 3


def ease_in_out(x):
    x = clamp(x); return 3 * x * x - 2 * x * x * x


def ease_out_back(x, s=1.70158):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1


def ease_out_expo(x):
    x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0


def kf(keys, u):
    """piecewise-linear keyframes [(u, v)] with smoothstep between keys."""
    if not isinstance(keys, (list, tuple)):
        return keys
    if u <= keys[0][0]:
        return keys[0][1]
    for (u0, v0), (u1, v1) in zip(keys, keys[1:]):
        if u <= u1:
            x = (u - u0) / (u1 - u0) if u1 > u0 else 1
            return v0 + (v1 - v0) * ease_in_out(x)
    return keys[-1][1]


def kf_lin(keys, u):
    if not isinstance(keys, (list, tuple)):
        return keys
    if u <= keys[0][0]:
        return keys[0][1]
    for (u0, v0), (u1, v1) in zip(keys, keys[1:]):
        if u <= u1:
            x = (u - u0) / (u1 - u0) if u1 > u0 else 1
            return v0 + (v1 - v0) * x
    return keys[-1][1]


# ------------------------------------------------------------------ time remap
def srcmap(shot):
    """returns f(t) -> source seconds, and speed(t)."""
    t0, t1, s_in, sp = shot['t0'], shot['t1'], shot['src_in'], shot.get('speed', 1.0)
    dur = t1 - t0
    if not isinstance(sp, (list, tuple)):
        return (lambda t: s_in + (t - t0) * sp), (lambda t: sp)
    n = 2000
    us = np.linspace(0, 1, n + 1)
    spd = np.array([kf_lin(sp, u) for u in us])
    cum = np.concatenate([[0], np.cumsum((spd[1:] + spd[:-1]) / 2 * dur / n)])

    def f(t):
        u = (t - t0) / dur
        if u <= 0:
            return s_in + (t - t0) * spd[0]
        if u >= 1:
            return s_in + cum[-1] + (t - t1) * spd[-1]
        return s_in + float(np.interp(u, us, cum))

    return f, (lambda t: float(np.interp(clamp((t - t0) / dur), us, spd)))


# ------------------------------------------------------------------ intermediates
_probe = {}


def probe_fps(path):
    if path not in _probe:
        j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                       'stream=avg_frame_rate', '-of', 'json', path], capture_output=True, text=True).stdout)
        a, b = j['streams'][0]['avg_frame_rate'].split('/')
        _probe[path] = float(a) / float(b)
    return _probe[path]


def int_name(src, a, b):
    h = hashlib.md5(f'{src}|{a:.3f}|{b:.3f}'.encode()).hexdigest()[:10]
    return INT_DIR + os.path.splitext(os.path.basename(src))[0] + f'_{a:.2f}_{h}.mp4'


def extract(src, a, b):
    """extract [a,b] seconds of src to an intermediate IWxIH at native fps. returns path."""
    a = max(0.0, a)
    out = int_name(src, a, b)
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return out
    tmp = out + '.tmp.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-i', src, '-t', f'{b - a:.3f}', '-an',
                    '-vf', f'scale={IW}:{IH}:force_original_aspect_ratio=increase:flags=lanczos,crop={IW}:{IH}', '-c:v', 'libx264', '-preset', 'fast', '-crf', '9',
                    '-pix_fmt', 'yuv420p', tmp], check=True)
    os.replace(tmp, out)
    return out


class Reader:
    """forward-reading frame source over an intermediate that starts at source second `a`."""

    def __init__(self, path, a, fps):
        self.path, self.a, self.fps = path, a, fps
        self.cap = None
        self.pos = -1
        self.cache = {}
        self.n = int(cv2.VideoCapture(path).get(cv2.CAP_PROP_FRAME_COUNT))

    def _open(self):
        self.cap = cv2.VideoCapture(self.path)
        self.pos = -1

    def frame(self, idx):
        idx = int(min(max(idx, 0), self.n - 1))
        if idx in self.cache:
            return self.cache[idx]
        if self.cap is None or idx < self.pos:
            self._open()
        img = None
        while self.pos < idx:
            ok, im = self.cap.read()
            if not ok:
                break
            self.pos += 1
            self.cache[self.pos] = im
            img = im
        for k in list(self.cache):
            if k < idx - 12:
                del self.cache[k]
        return self.cache.get(idx, img if img is not None else self.cache[max(self.cache)])

    def at(self, s):
        return self.frame(round((s - self.a) * self.fps))

    def blended(self, s0, s1):
        """average of source frames between s0 and s1 (motion blur for fast speeds)."""
        i0 = round((s0 - self.a) * self.fps); i1 = round((s1 - self.a) * self.fps)
        if i1 <= i0:
            return self.frame(i0)
        idxs = list(range(i0, i1 + 1))
        if len(idxs) > 6:
            idxs = [idxs[int(round(k))] for k in np.linspace(0, len(idxs) - 1, 6)]
        acc = None
        for i in idxs:
            f = self.frame(i).astype(np.float32)
            acc = f if acc is None else acc + f
        return (acc / len(idxs)).astype(np.uint8)


# ------------------------------------------------------------------ grading
def _curve(points):
    xs, ys = zip(*points)
    return np.clip(np.interp(np.arange(256), xs, ys), 0, 255)


GRADES = {
    # curve points (input->output), per-channel gain (r,g,b), saturation, sharpen
    'talk': dict(curve=[(0, 6), (40, 36), (128, 128), (205, 204), (255, 240)], rgb=(1.03, 1.0, 0.96), sat=1.12, sharp=0.35),
    'old': dict(curve=[(0, 8), (40, 38), (128, 128), (205, 206), (255, 246)], rgb=(1.02, 1.0, 0.95), sat=0.92, sharp=0.3),
    'retro': dict(curve=[(0, 30), (60, 70), (128, 135), (205, 205), (255, 232)], rgb=(1.08, 1.0, 0.84), sat=0.55, sharp=0.0),
    'clean': dict(curve=[(0, 4), (40, 34), (128, 134), (205, 220), (255, 252)], rgb=(1.01, 1.0, 0.99), sat=1.08, sharp=0.45),
    'beige': dict(curve=[(0, 4), (40, 32), (128, 134), (205, 220), (255, 252)], rgb=(1.02, 1.0, 0.97), sat=1.06, sharp=0.45),
    'white': dict(curve=[(0, 2), (40, 30), (128, 136), (205, 224), (255, 253)], rgb=(1.0, 1.0, 1.0), sat=1.05, sharp=0.45),
    'office': dict(curve=[(0, 4), (40, 34), (128, 132), (205, 214), (255, 248)], rgb=(1.02, 1.0, 0.97), sat=1.08, sharp=0.35),
    'hlg': dict(curve=[(0, 0), (40, 30), (128, 130), (205, 218), (255, 252)], rgb=(1.0, 1.0, 1.0), sat=1.12, sharp=0.4),
}
_luts = {}


def lut_for(name):
    if name not in _luts:
        g = GRADES[name]
        base = _curve(g['curve'])
        r, gg, b = g['rgb']
        lut = np.stack([np.clip(base * b, 0, 255), np.clip(base * gg, 0, 255), np.clip(base * r, 0, 255)], 0).astype(np.uint8)  # BGR
        _luts[name] = lut
    return _luts[name]


def grade(img, name):
    g = GRADES[name]
    lut = lut_for(name)
    out = np.empty_like(img)
    for c in range(3):
        out[..., c] = cv2.LUT(img[..., c], lut[c])
    if g['sat'] != 1.0:
        f = out.astype(np.float32)
        y = f[..., 0] * 0.114 + f[..., 1] * 0.587 + f[..., 2] * 0.299
        f = y[..., None] + (f - y[..., None]) * g['sat']
        out = np.clip(f, 0, 255).astype(np.uint8)
    if g['sharp'] > 0:
        bl = cv2.GaussianBlur(out, (0, 0), 1.3)
        out = cv2.addWeighted(out, 1 + g['sharp'], bl, -g['sharp'], 0)
    return out


def vignette(w, h, strength=0.22):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
    return (1 - strength * np.clip((d - 0.45) / 0.55, 0, 1) ** 1.6).astype(np.float32)


# ------------------------------------------------------------------ geometric
def affine(scale, rot_deg, dx, dy, w, h, cw, ch, cx=0.0, cy=0.0):
    """matrix mapping an intermediate (w,h) to canvas (cw,ch): centre-crop with scale, rotation and offset.
    cx, cy shift the crop centre as a fraction of the intermediate size."""
    s = scale * cw / w   # scale 1.0 == whole source frame fills the canvas
    M = cv2.getRotationMatrix2D((w / 2 + cx * w, h / 2 + cy * h), rot_deg, s)
    M[0, 2] += cw / 2 - (w / 2 + cx * w) + dx
    M[1, 2] += ch / 2 - (h / 2 + cy * h) + dy
    return M


def motion_blur(img, dx, dy):
    """directional box blur along (dx,dy) pixels."""
    L = int(round(math.hypot(dx, dy)))
    if L < 3:
        return img
    if abs(dx) >= abs(dy):
        k = L | 1
        return cv2.blur(img, (k, 1))
    k = L | 1
    return cv2.blur(img, (1, k))


def zoom_blur(img, amount, n=5):
    """radial blur by averaging scaled copies."""
    if amount < 0.01:
        return img
    h, w = img.shape[:2]
    acc = img.astype(np.float32)
    for i in range(1, n):
        s = 1 + amount * i / (n - 1)
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, s)
        acc += cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    return (acc / n).astype(np.uint8)


class StillReader:
    """photo source with the same interface as Reader."""

    def __init__(self, path):
        self.img = cv2.imread(path)
        self.a, self.fps = 0.0, 30.0

    def frame(self, idx):
        return self.img

    def at(self, s):
        return self.img

    def blended(self, s0, s1):
        return self.img


def is_still(src):
    return src.lower().endswith('.png')


def make_reader(src, plan_entry):
    if is_still(src):
        return StillReader(src)
    s, a, b = plan_entry
    return Reader(int_name(s, a, b), a, probe_fps(s))
