"""Frame renderer for reel 2. usage: render.py out.mp4 [--from t] [--to t] [--stills t1,t2,...]"""
import sys, os, json, math, subprocess, argparse
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core as C
import timeline as T
import gfx as G
import overlays as O

ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('--from', dest='t_from', type=float, default=0.0)
ap.add_argument('--to', dest='t_to', type=float, default=T.DUR)
ap.add_argument('--stills', default='')
args = ap.parse_args()

PLAN = json.load(open(C.ROOT + 'edit/int_plan.json'))
VIG = C.vignette(T.W, T.H, 0.18)[..., None]
MASK_DIR = C.ROOT + 'masks/'
os.makedirs(MASK_DIR, exist_ok=True)
SUPER8 = cv2.imread(C.ROOT + 'dl/sfx/SFX PACK 2/RECTANGULOS SUPER 8MM/super 8 frame.png', cv2.IMREAD_UNCHANGED)
S8_HOLE = (132, 437, 947, 1503)          # x0, y0, x1, y1 of the transparent window
rng = np.random.default_rng(3)


class ShotR:
    def __init__(self, i, s):
        self.i, self.s = i, s
        self.reader = C.make_reader(s['src'], PLAN[str(i)])
        self.f, self.sp = C.srcmap(s)
        self.before = cv2.imread(s['before']) if 'before' in s else None

    def u(self, t):
        s = self.s
        return C.clamp((t - s['t0']) / (s['t1'] - s['t0']))

    def warp(self, img, t, extra_scale=1.0, rot=0.0, dx=0.0, dy=0.0):
        s = self.s; u = self.u(t)
        z = C.kf(s.get('zoom', 1.0), u) * extra_scale
        dx += C.kf(s.get('dx', 0.0), u); dy += C.kf(s.get('dy', 0.0), u)
        M = C.affine(z, rot, dx, dy, img.shape[1], img.shape[0], T.W, T.H, s.get('cx', 0.0), s.get('cy', 0.0))
        return cv2.warpAffine(img, M, (T.W, T.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    def frame(self, t, extra_scale=1.0, rot=0.0, dx=0.0, dy=0.0):
        s = self.s
        st = max(0.0, self.f(t))
        v = self.sp(t)
        if v > 1.25:
            half = v * 0.5 / T.FPS / 2
            img = self.reader.blended(st - half, st + half)
        else:
            img = self.reader.at(st)
        out = self.warp(img, t, extra_scale, rot, dx, dy)
        out = C.grade(out, s.get('grade', 'talk'))
        if self.before is not None:
            out = self.before_after(out, t, extra_scale, rot, dx, dy)
        if s.get('retro'):
            out = retro(out, t, s)
        u = self.u(t)
        dim = s.get('dim', 0.0)
        if 'dim_ramp' in s:
            dim = C.kf(s['dim_ramp'], u)
        if dim:
            out = (out.astype(np.float32) * (1 - dim)).astype(np.uint8)
        return out

    def before_after(self, after, t, extra_scale, rot, dx, dy):
        w0, w1 = self.s['wipe']
        if t >= w1:
            return after
        b = C.grade(self.warp(self.before, t, extra_scale * 1.04, rot, dx, dy), 'old')
        if t <= w0:
            return b
        p = C.ease_in_out((t - w0) / (w1 - w0))
        x = -60 + (T.W + 120) * p                       # divider position, sweeps left -> right
        xs = np.arange(T.W, dtype=np.float32)
        m = np.clip((x - xs) / 6 + 0.5, 0, 1)[None, :, None]   # left of the line shows AFTER
        out = after.astype(np.float32) * m + b.astype(np.float32) * (1 - m)
        # glowing divider
        line = np.exp(-((xs - x) / 5) ** 2) + 0.35 * np.exp(-((xs - x) / 28) ** 2)
        out = out + 255 * line[None, :, None] * 0.9
        return np.clip(out, 0, 255).astype(np.uint8)


def retro(img, t, s):
    """Super 8 / VHS look: grain, flicker, chroma shift, gate weave, inside the Super 8 frame PNG."""
    a = t - s['t0']
    f = img.astype(np.float32)
    # chroma shift (RGB split)
    sh = 6
    f[..., 2] = np.roll(f[..., 2], sh, axis=1); f[..., 0] = np.roll(f[..., 0], -sh, axis=1)
    # grain + flicker
    n = int(t * T.FPS)
    g = np.random.default_rng(n).normal(0, 14, (T.H // 2, T.W // 2)).astype(np.float32)
    g = cv2.resize(g, (T.W, T.H))
    flick = 1 + 0.06 * math.sin(n * 2.7) + 0.04 * np.random.default_rng(n + 7).uniform(-1, 1)
    f = (f + g[..., None]) * flick
    # scanlines
    f[::3] *= 0.92
    # fit into the Super 8 window with a pop-in and gate weave
    x0, y0, x1, y1 = S8_HOLE
    pop = C.ease_out_back(a / 0.18, 2.0)
    sc = 0.6 + 0.4 * C.clamp(pop, 0, 1.2)
    ww, hh = int((x1 - x0) * sc * 1.04), int((y1 - y0) * sc * 1.04)
    inner = cv2.resize(np.clip(f, 0, 255).astype(np.uint8), (ww, int(ww * T.H / T.W)), interpolation=cv2.INTER_AREA)
    yy = (inner.shape[0] - hh) // 2
    inner = inner[max(0, yy):max(0, yy) + hh]
    canvas = np.zeros((T.H, T.W, 3), np.uint8)
    canvas[:] = (12, 12, 12)
    wx = int(2 * math.sin(n * 1.9)); wy = int(2 * math.cos(n * 1.3))
    cx, cy = (x0 + x1) // 2 + wx, (y0 + y1) // 2 + wy
    X0, Y0 = cx - inner.shape[1] // 2, cy - inner.shape[0] // 2
    canvas[max(0, Y0):Y0 + inner.shape[0], max(0, X0):X0 + inner.shape[1]] = inner[max(0, -Y0):, max(0, -X0):][:T.H - max(0, Y0), :T.W - max(0, X0)]
    fr = SUPER8
    if sc < 0.999:
        fr = cv2.resize(SUPER8, None, fx=sc, fy=sc)
        pad = np.zeros_like(SUPER8); pad[..., 3] = 255
        oy, ox = (T.H - fr.shape[0]) // 2 + (cy - wy - T.H // 2), (T.W - fr.shape[1]) // 2 + (cx - wx - T.W // 2)
        oy, ox = max(0, oy), max(0, ox)
        pad[oy:oy + fr.shape[0], ox:ox + fr.shape[1]] = fr[:T.H - oy, :T.W - ox]
        fr = pad
    al = fr[..., 3:4].astype(np.float32) / 255
    out = canvas.astype(np.float32) * (1 - al) + fr[..., :3].astype(np.float32) * al
    # warm light leak flashes (film burn)
    leak = 0.0
    for c in (0.0, 0.55):
        leak += math.exp(-((a - c) / 0.07) ** 2)
    if leak > 0.01:
        yy_, xx_ = np.mgrid[0:T.H:8, 0:T.W:8].astype(np.float32)
        lm = np.clip(1 - np.sqrt(((xx_ - T.W) / T.W) ** 2 + ((yy_ - T.H * 0.2) / T.H) ** 2) / 0.8, 0, 1)
        lm = cv2.resize(lm, (T.W, T.H))[..., None]
        out = out + np.array([40, 140, 255], np.float32) * lm * leak * 0.9
    return np.clip(out, 0, 255).astype(np.uint8)


SH = [ShotR(i, s) for i, s in enumerate(T.SHOTS)]


def shot_at(t):
    for k, s in enumerate(T.SHOTS):
        if s['t0'] - 1e-6 <= t < s['t1'] - 1e-6:
            return k
    return len(T.SHOTS) - 1


def base_frame(t):
    k = shot_at(t)
    cand = ([k + 1] if k + 1 < len(T.SHOTS) else []) + [k]
    for j in cand:
        s = T.SHOTS[j]
        tin = s.get('tin', ('cut',))
        if tin[0] == 'cut' or j == 0:
            continue
        d = tin[2]; tc = s['t0']
        if abs(t - tc) > d / 2 + 1e-6:
            continue
        typ, dr = tin[0], tin[1]
        if t < tc:
            p = (t - (tc - d / 2)) / (d / 2); e = C.ease_in_cubic(p)
            vel = 3 * p * p / (d / 2) / T.FPS
            return render_trans(SH[j - 1], t, typ, dr, e, vel, True), flash_amt(typ, t, tc, d)
        q = (t - tc) / (d / 2); e = 1 - C.ease_out_cubic(q)
        vel = 3 * (1 - q) ** 2 / (d / 2) / T.FPS
        return render_trans(SH[j], t, typ, dr, e, vel, False), flash_amt(typ, t, tc, d)
    return SH[k].frame(t).astype(np.float32), 0.0


def flash_amt(typ, t, tc, d):
    if typ == 'flash':
        return math.exp(-((t - tc) / (d * 0.32)) ** 2)
    if typ == 'zoom':
        return 0.45 * math.exp(-((t - tc) / (d * 0.22)) ** 2)
    return 0.0


def render_trans(sh, t, typ, dr, e, vel, outgoing):
    sign = 1 if outgoing else -1
    if typ == 'whip':
        travel = T.W * 0.85 if dr in ('left', 'right') else T.H * 0.6
        dirv = {'left': (-1, 0), 'right': (1, 0), 'up': (0, -1), 'down': (0, 1)}[dr]
        off = travel * e * sign
        img = sh.frame(t, extra_scale=1.06 + 0.04 * e, rot=(3.0 * e * sign if dr in ('left', 'right') else 0),
                       dx=dirv[0] * off, dy=dirv[1] * off)
        blur = min(150.0, travel * vel * 0.8)
        return C.motion_blur(img, dirv[0] * blur, dirv[1] * blur).astype(np.float32)
    if typ == 'zoom':
        img = sh.frame(t, extra_scale=1 + (0.55 if outgoing else 0.35) * e)
        return C.zoom_blur(img, 0.06 + 0.22 * e).astype(np.float32)
    if typ == 'flash':
        return sh.frame(t, extra_scale=1 + 0.08 * e).astype(np.float32)
    return sh.frame(t).astype(np.float32)


_seg = None


def segment(img):
    global _seg
    import onnxruntime as ort
    if _seg is None:
        _seg = ort.InferenceSession(C.WEST + 'models/u2net_human_seg.onnx', providers=['CPUExecutionProvider'])
    x = cv2.resize(img, (320, 320), interpolation=cv2.INTER_AREA)[:, :, ::-1].astype(np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    o = _seg.run(None, {_seg.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
    o = (o - o.min()) / (o.max() - o.min() + 1e-6)
    o = cv2.resize(o, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC)
    return cv2.GaussianBlur(np.clip((o - 0.35) / 0.4, 0, 1), (0, 0), 1.5)


ELS = O.build()


def behind_needed(t):
    return any(getattr(e, 'behind', False) and e.active(t) for e in ELS)


def flash_overlay(canvas, amt):
    if amt <= 0.003:
        return
    canvas[:] = np.clip(canvas + 255 * amt, 0, 255)


def render_frame(n):
    t = n / T.FPS
    base, fl = base_frame(t)
    if not T.SHOTS[shot_at(t)].get('retro'):
        base *= VIG
    canvas = base.copy()
    mask = None
    if behind_needed(t):
        mp = MASK_DIR + f'{n:05d}.png'
        if os.path.exists(mp):
            mask = cv2.imread(mp, cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0
        else:
            mask = segment(np.clip(base, 0, 255).astype(np.uint8))
            cv2.imwrite(mp, (mask * 255).astype(np.uint8))
    for e in ELS:
        if e.active(t):
            e.draw(canvas, t, base=base, mask=mask)
    flash_overlay(canvas, fl)
    return np.clip(canvas, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    if args.stills:
        for ts in args.stills.split(','):
            n = int(round(float(ts) * T.FPS))
            cv2.imwrite(args.out.replace('.mp4', '') + f'_{float(ts):06.2f}.jpg', render_frame(n), [cv2.IMWRITE_JPEG_QUALITY, 90])
        sys.exit()
    n0, n1 = int(round(args.t_from * T.FPS)), int(round(args.t_to * T.FPS))
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{T.W}x{T.H}',
                          '-r', str(T.FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '10',
                          '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
                          args.out], stdin=subprocess.PIPE)
    import time
    t0 = time.time()
    for n in range(n0, n1):
        p.stdin.write(render_frame(n).tobytes())
        if (n - n0) % 30 == 0:
            print(f'{n}/{n1} {time.time() - t0:.0f}s', flush=True)
    p.stdin.close(); p.wait()
    print('done', time.time() - t0)
