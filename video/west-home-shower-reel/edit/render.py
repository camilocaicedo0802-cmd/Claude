"""Frame renderer. usage: render.py out.mp4 [--from t] [--to t] [--stills t1,t2,...]"""
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
ap.add_argument('--masks', action='store_true', help='compute person masks only')
args = ap.parse_args()

PLAN = json.load(open(C.ROOT + 'edit/int_plan.json'))
VIG = C.vignette(T.W, T.H, 0.20)[..., None]
MASK_DIR = C.ROOT + 'masks/'
os.makedirs(MASK_DIR, exist_ok=True)


class ShotR:
    def __init__(self, i, s):
        self.i, self.s = i, s
        src, a, b = PLAN[str(i)]
        self.reader = C.Reader(C.int_name(src, a, b), a, C.probe_fps(src))
        self.f, self.sp = C.srcmap(s)

    def frame(self, t, extra_scale=1.0, rot=0.0, dx=0.0, dy=0.0):
        s = self.s
        st = max(0.0, self.f(t))
        v = self.sp(t)
        if v > 1.25:
            half = v * 0.5 / T.FPS / 2
            img = self.reader.blended(st - half, st + half)
        else:
            img = self.reader.at(st)
        u = C.clamp((t - s['t0']) / (s['t1'] - s['t0']))
        z = C.kf(s.get('zoom', 1.0), u) * extra_scale
        M = C.affine(z, rot, dx, dy, img.shape[1], img.shape[0], T.W, T.H, s.get('cx', 0.0), s.get('cy', 0.0))
        out = cv2.warpAffine(img, M, (T.W, T.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        out = C.grade(out, s.get('grade', 'talk'))
        dim = s.get('dim', 0.0)
        if 'dim_ramp' in s:
            dim = C.kf(s['dim_ramp'], u)
        if dim:
            out = (out.astype(np.float32) * (1 - dim)).astype(np.uint8)
        return out


SH = [ShotR(i, s) for i, s in enumerate(T.SHOTS)]


def shot_at(t):
    for k, s in enumerate(T.SHOTS):
        if s['t0'] - 1e-6 <= t < s['t1'] - 1e-6:
            return k
    return len(T.SHOTS) - 1


def base_frame(t):
    """picture for time t including transitions; returns float32 BGR and a flash amount."""
    k = shot_at(t)
    flash = 0.0
    # transition into k (near its start) or into k+1 (near its end)
    cand = []
    if k + 1 < len(T.SHOTS):
        cand.append(k + 1)
    cand.append(k)
    for j in cand:
        s = T.SHOTS[j]
        tin = s.get('tin', ('cut',))
        if tin[0] == 'cut' or j == 0:
            continue
        d = tin[2]
        tc = s['t0']
        if abs(t - tc) > d / 2 + 1e-6:
            continue
        typ, dr = tin[0], tin[1]
        if t < tc:   # outgoing: shot j-1, accelerating
            p = (t - (tc - d / 2)) / (d / 2); e = C.ease_in_cubic(p)
            sh = SH[j - 1]
            vel = 3 * p * p / (d / 2) / T.FPS     # fraction of travel per frame
            return render_trans(sh, t, typ, dr, e, vel, outgoing=True), flash_amt(typ, t, tc, d)
        else:        # incoming: shot j, decelerating
            q = (t - tc) / (d / 2); e = 1 - C.ease_out_cubic(q)
            sh = SH[j]
            vel = 3 * (1 - q) ** 2 / (d / 2) / T.FPS
            return render_trans(sh, t, typ, dr, e, vel, outgoing=False), flash_amt(typ, t, tc, d)
    return SH[k].frame(t).astype(np.float32), 0.0


def flash_amt(typ, t, tc, d):
    if typ == 'flash':
        return math.exp(-((t - tc) / (d * 0.32)) ** 2)
    if typ == 'zoom':
        return 0.55 * math.exp(-((t - tc) / (d * 0.22)) ** 2)
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
        img = C.motion_blur(img, dirv[0] * blur, dirv[1] * blur)
        return img.astype(np.float32)
    if typ == 'spin':
        ang = 32 * e * (sign if dr == 'cw' else -sign)
        img = sh.frame(t, extra_scale=1.12 + 0.35 * e, rot=ang)
        img = C.zoom_blur(img, 0.10 * e + 0.25 * min(1, vel * 6))
        # angular smear approximation: blend two slightly rotated copies
        if e > 0.05:
            img2 = sh.frame(t, extra_scale=1.12 + 0.35 * e, rot=ang + (6 * e if dr == 'cw' else -6 * e) * sign)
            img = cv2.addWeighted(img, 0.5, img2, 0.5, 0)
        return img.astype(np.float32)
    if typ == 'zoom':
        z = 1 + (0.55 if outgoing else 0.35) * e
        img = sh.frame(t, extra_scale=z)
        img = C.zoom_blur(img, 0.06 + 0.22 * e)
        return img.astype(np.float32)
    if typ == 'flash':
        return sh.frame(t, extra_scale=1 + 0.08 * e).astype(np.float32)
    return sh.frame(t).astype(np.float32)


# ------------------------------------------------------------------ person masks (text behind people)
_seg = None


def segment(img):
    global _seg
    import onnxruntime as ort
    if _seg is None:
        _seg = ort.InferenceSession(C.ROOT + 'models/u2net_human_seg.onnx', providers=['CPUExecutionProvider'])
    x = cv2.resize(img, (320, 320), interpolation=cv2.INTER_AREA)[:, :, ::-1].astype(np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    o = _seg.run(None, {_seg.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
    o = (o - o.min()) / (o.max() - o.min() + 1e-6)
    o = cv2.resize(o, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC)
    o = np.clip((o - 0.35) / 0.4, 0, 1)
    return cv2.GaussianBlur(o, (0, 0), 1.5)


def mask_path(n):
    return MASK_DIR + f'{n:05d}.png'


ELS = O.build()


def behind_needed(t):
    return any(getattr(e, 'behind', False) and e.active(t) for e in ELS)


def flash_overlay(canvas, amt):
    if amt <= 0.003:
        return
    # warm light leak: orange outer glow + white core
    if not hasattr(flash_overlay, 'g'):
        yy, xx = np.mgrid[0:T.H, 0:T.W].astype(np.float32)
        d = np.sqrt(((xx - T.W * 0.3) / T.W) ** 2 + ((yy - T.H * 0.35) / T.H) ** 2)
        flash_overlay.g = np.clip(1 - d / 0.9, 0, 1)[..., None]
    g = flash_overlay.g
    col = np.array([40, 120, 255], np.float32)      # BGR warm orange
    canvas[:] = canvas + (col * g * 0.9 + 255 * g ** 2 * 0.6) * amt
    np.clip(canvas, 0, 255, out=canvas)


def render_frame(n):
    t = n / T.FPS
    base, fl = base_frame(t)
    base *= VIG
    canvas = base.copy()
    mask = None
    if behind_needed(t):
        mp = mask_path(n)
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
    if args.masks:
        for n in range(n0, n1):
            t = n / T.FPS
            if behind_needed(t) and not os.path.exists(mask_path(n)):
                base, _ = base_frame(t)
                base *= VIG
                m = segment(np.clip(base, 0, 255).astype(np.uint8))
                cv2.imwrite(mask_path(n), (m * 255).astype(np.uint8))
        print('masks done'); sys.exit()
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
