"""Render the luxury intro edit from raw.mov following edl.py."""
import sys, subprocess, math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl import EDL, BEAT, MUSIC_START

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.environ.get("JET_WORKDIR", os.path.join(HERE, "work"))  # raw/raw.mov, music/364.mp3, fonts2/*.ttf
RAW = f'{S}/raw/raw.mov'
FONT_BIG = f'{S}/fonts2/Syncopate.ttf'
FONT_SERIF = f'{S}/fonts2/Playfair.ttf'
W, H, FPS, SRC_FPS = 1920, 1080, 30, 60
VERT_X0, VERT_X1 = 656, 1264
OUT_V = f'{S}/video_noaudio.mp4'
PREVIEW = '--preview' in sys.argv          # half-res fast pass
if PREVIEW:
    OUT_V = f'{S}/preview_noaudio.mp4'
RNG = np.random.default_rng(7)

# ---------- timing ----------
starts, t = [], 0.0
for c in EDL:
    c['t0'] = t
    c['f0'] = round(t * BEAT * FPS)
    t += c['beats']
    c['f1'] = round(t * BEAT * FPS)
TOTAL_F = EDL[-1]['f1']

# ---------- static assets ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIGNETTE = np.clip(1.0 - 0.38 * np.clip(r - 0.55, 0, None) ** 1.6, 0, 1)[..., None].astype(np.float32)
GRAIN = [cv2.resize(RNG.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (W, H))[..., None] for _ in range(6)]


def curve(x, contrast):
    # smooth S-curve around mid grey, x in 0..1
    return np.clip(0.5 + (x - 0.5) * contrast + 0.0, 0, 1) if contrast == 1 else \
        np.clip(1 / (1 + np.exp(-contrast * (x - 0.5) * 4)) * 1.0, 0, 1)


def lut_s(contrast, lift=0.0, gain=1.0):
    x = np.linspace(0, 1, 256)
    s = 1 / (1 + np.exp(-contrast * (x - 0.5)))
    s = (s - s.min()) / (s.max() - s.min())
    s = lift + s * (gain - lift)
    return np.clip(s * 255, 0, 255).astype(np.uint8)


LUT_BW = lut_s(7.5, 0.0, 1.0)
LUT_SOFT = lut_s(4.2, 0.02, 0.98)


def grade(img, look):
    """img uint8 BGR -> float32 0..1 BGR"""
    if look in ('bw', 'neg'):
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        g = cv2.LUT(g, LUT_BW).astype(np.float32) / 255
        out = np.repeat(g[..., None], 3, axis=2)
        if look == 'neg':
            out = 1.0 - out
            out = out * np.array([1.0, 0.97, 0.93], np.float32)  # cold paper tint
        return out
    f = cv2.LUT(img, LUT_SOFT).astype(np.float32) / 255
    lum = (0.114 * f[..., 0] + 0.587 * f[..., 1] + 0.299 * f[..., 2])[..., None]
    sat = 1.18 if look == 'lux' else 1.25
    f = lum + (f - lum) * sat
    if look == 'lux':      # teal shadows, warm highlights
        sh = np.array([0.06, 0.035, -0.02], np.float32)
        hi = np.array([-0.05, 0.0, 0.06], np.float32)
    else:                  # warm golden
        sh = np.array([0.02, 0.0, -0.01], np.float32)
        hi = np.array([-0.08, 0.0, 0.08], np.float32)
    f = f + sh * (1 - lum) ** 2 + hi * lum ** 2
    return np.clip(f, 0, 1)


def zoom_shift(img, z, dx=0.0, dy=0.0):
    M = np.float32([[z, 0, (1 - z) * W / 2 + dx], [0, z, (1 - z) * H / 2 + dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def vertical_fill(img):
    fg = img[:, VERT_X0:VERT_X1]
    bg = cv2.resize(fg, (W, int(W * fg.shape[0] / fg.shape[1])))
    oy = (bg.shape[0] - H) // 2
    bg = bg[oy:oy + H]
    bg = cv2.GaussianBlur(cv2.resize(bg, (W // 8, H // 8)), (0, 0), 3)
    bg = (cv2.resize(bg, (W, H)) * 0.55).astype(np.uint8)
    # foreground scaled up a bit, with a soft drop shadow
    fh = H
    fw = int(fg.shape[1] * fh / fg.shape[0])
    fg2 = cv2.resize(fg, (fw, fh))
    x0 = (W - fw) // 2
    bg[:, x0:x0 + fw] = fg2
    return bg


# ---------- text ----------
def font(path, size):
    return ImageFont.truetype(path, size)


def draw_tracked(draw, xy, text, fnt, tracking, fill):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def tracked_width(text, fnt, tracking):
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    return sum(d.textlength(ch, font=fnt) + tracking for ch in text) - tracking


F_BIG = font(FONT_BIG, 104)
F_BIG2 = font(FONT_BIG, 128)
F_SERIF = font(FONT_SERIF, 40)
F_SERIF2 = font(FONT_SERIF, 44)
F_LETS = font(FONT_BIG, 96)
BIG1_W = tracked_width('JET PRIVADO', F_BIG, 14)
print('title1 width', BIG1_W, 'title2 width', tracked_width('JET PRIVADO', F_BIG2, 16))


def text_layer(fn):
    im = Image.new('L', (W, H), 0)
    fn(ImageDraw.Draw(im))
    return np.asarray(im, np.float32)[..., None] / 255


def title1_layer(tt, dur):
    """'VUELO EN' small serif left, 'JET PRIVADO' typed on the right (like the reference)."""
    small, big = 'VUELO EN', 'JET PRIVADO'
    n_small = min(len(small), int(tt / 0.035) + 1)
    t_big = tt - 0.30
    n_big = 0 if t_big < 0 else min(len(big), int(t_big / (BEAT / 2.4)) + 1)
    ticks = n_small + n_big

    def fn(d):
        draw_tracked(d, (120, 512), small[:n_small], F_SERIF, 8, 255)
        if n_big:
            draw_tracked(d, (W - 120 - BIG1_W, 488), big[:n_big], F_BIG, 14, 255)
    return text_layer(fn), ticks


def letsdo_layer(tt):
    lines = ["LET'S", 'DO', 'IT']
    n = min(3, int(tt / (BEAT * 0.5)) + 1)

    def fn(d):
        for i, ln in enumerate(lines[:n]):
            draw_tracked(d, (90, 60 + i * 124), ln, F_LETS, 20, 255)
    a = text_layer(fn)
    return np.maximum(a, a[::-1, ::-1])  # mirrored copy bottom-right, as in the reference


def title2_layer(tt, dur):
    big = 'JET PRIVADO'
    k = min(1.0, tt / 0.9)
    e = 1 - (1 - k) ** 3
    track = 60 - 44 * e
    alpha = min(1.0, tt / 0.45)
    wbig = tracked_width(big, F_BIG2, track)

    def fn(d):
        draw_tracked(d, ((W - wbig) / 2, 440), big, F_BIG2, track, int(255 * alpha))
        if tt > 0.5:
            a2 = int(255 * min(1, (tt - 0.5) / 0.4))
            ws = tracked_width('VUELO EN', F_SERIF2, 22)
            draw_tracked(d, ((W - ws) / 2, 360), 'VUELO EN', F_SERIF2, 22, a2)
    a = text_layer(fn)
    glow = cv2.GaussianBlur(a, (0, 0), 14)[..., None] * 0.6
    return a, glow


# ---------- light leak ----------
def light_leak(phase, strength):
    """Warm moving blobs, returns float32 additive layer (screen blended later)."""
    sw, sh = W // 8, H // 8
    y, x = np.mgrid[0:sh, 0:sw].astype(np.float32)
    lay = np.zeros((sh, sw, 3), np.float32)
    blobs = [(-0.2 + phase * 1.3, 0.35, 0.55, (0.05, 0.35, 1.0)),
             (0.1 + phase * 0.9, 0.8, 0.45, (0.0, 0.12, 0.95)),
             (1.1 - phase * 0.8, 0.2, 0.40, (0.25, 0.6, 1.0))]
    for bx, by, rad, col in blobs:
        d2 = ((x / sw - bx) ** 2 + (y / sh - by) ** 2) / rad ** 2
        lay += np.exp(-d2 * 2.2)[..., None] * np.array(col, np.float32)
    return cv2.resize(lay, (W, H)) * strength


# ---------- source reading ----------
def read_frames(src, idxs):
    """Return dict idx->frame for source frame offsets (at 60fps) starting at src seconds."""
    need = sorted(set(idxs))
    n = need[-1] + 1
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{src:.3f}', '-i', RAW, '-frames:v', str(n),
           '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, want, i = {}, set(need), 0
    fsz = W * H * 3
    while i < n:
        buf = p.stdout.read(fsz)
        if len(buf) < fsz:
            break
        if i in want:
            out[i] = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        i += 1
    p.stdout.close(); p.wait()
    last = out[max(out)]
    return {k: out.get(k, last) for k in need}


def ease_io(x):
    return x * x * (3 - 2 * x)


# ---------- main render ----------
enc_w, enc_h = (W // 2, H // 2) if PREVIEW else (W, H)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                        '-s', f'{enc_w}x{enc_h}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'veryfast' if PREVIEW else 'slow',
                        '-crf', '23' if PREVIEW else '16', '-pix_fmt', 'yuv420p',
                        '-movflags', '+faststart', OUT_V], stdin=subprocess.PIPE)

events = []   # (time_sec, kind) for SFX
for ci, c in enumerate(EDL):
    nf = c['f1'] - c['f0']
    dur = nf / FPS
    step = SRC_FPS / FPS * c['speed']
    idxs = [int(round(k * step)) for k in range(nf)]
    frames = read_frames(c['src'], idxs)
    fx = c['fx']
    T0 = c['f0'] / FPS
    if 'punch' in fx or 'flashin' in fx:
        events.append((T0, 'whoosh' if c['beats'] >= 1 else 'tick'))
    if ci > 0 and c['t0'] == 16:
        events.append((T0, 'impact'))
    last_ticks = 0
    for k in range(nf):
        tt = k / FPS
        u = k / max(1, nf - 1)
        img = frames[idxs[k]]
        if c['vert']:
            img = vertical_fill(img)
        # geometry
        z0, z1 = c['zoom']
        z = z0 + (z1 - z0) * ease_io(u)
        dx = dy = 0.0
        if 'punch' in fx and k < 6:
            z *= 1 + 0.16 * math.exp(-k / 1.6)
        if 'shake' in fx:
            amp = 26 * math.exp(-tt / 0.3) + 7 * math.exp(-((tt % BEAT) / 0.12))
            dx, dy = RNG.normal(0, amp, 2)
            z *= 1.03
        g = zoom_shift(img, z, dx, dy)
        if 'punch' in fx and k < 3:  # zoom motion blur on the cut
            acc = g.astype(np.float32)
            for j in (1, 2, 3):
                acc += zoom_shift(img, z * (1 + 0.025 * j * (3 - k)), dx, dy)
            g = (acc / 4).astype(np.uint8)
        f = grade(g, c['look'])

        # chromatic aberration
        if 'rgb' in fx and k < 5 or ('shake' in fx and tt < 0.25):
            sft = int(14 * math.exp(-k / 2.0)) + 2
            f[..., 2] = np.roll(f[..., 2], sft, axis=1)
            f[..., 0] = np.roll(f[..., 0], -sft, axis=1)

        # negative flicker (build into the drop)
        if 'negflick' in fx and tt > dur - BEAT * 1.0:
            if int((tt - (dur - BEAT)) / (BEAT / 4)) % 2 == 0:
                f = 1.0 - cv2.cvtColor((f * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)[..., None].repeat(3, 2) / 255.0
                f = f.astype(np.float32)

        # titles
        if 'title1' in fx:
            f = f ** 1.6 * 0.62
            a, ticks = title1_layer(tt, dur)
            if ticks > last_ticks:
                events.append((T0 + tt, 'type'))
                last_ticks = ticks
            f = f * (1 - a) + a
            bt = tt / BEAT
            # inverted flash on beat 2 and 4 (white background, black tower like the reference)
            if 2.0 <= bt < 2.35 or 4.0 <= bt < 4.6:
                f = 1.0 - f
            if 3.0 <= bt < 3.2:   # golden flicker
                lum = f.mean(2, keepdims=True)
                f = np.clip(lum * np.array([0.25, 0.75, 1.15], np.float32) * 1.3, 0, 1)
        if 'letsdoit' in fx:
            a = letsdo_layer(tt)
            sh = cv2.GaussianBlur(a, (0, 0), 6)[..., None] * 0.55
            f = f * (1 - sh) 
            f = f * (1 - a) + a
            if int(tt / BEAT) != int((tt - 1 / FPS) / BEAT) and tt > 0.05:
                events.append((T0 + tt, 'type'))
        if 'title2' in fx:
            f = f * (0.55 + 0.45 * (yy[..., None] / H) ** 0.7) * 0.85
            a, glow = title2_layer(tt, dur)
            f = np.clip(f * (1 - a * 0.9) + a + glow * np.array([0.6, 0.85, 1.0], np.float32), 0, 1)

        # light leak
        if 'leak' in fx:
            env = math.exp(-((tt - 0.18) / 0.22) ** 2) * 0.95 + 0.12 * max(0, 1 - tt / dur)
            if env > 0.01:
                L = light_leak(tt / max(dur, 0.3), env)
                f = 1 - (1 - f) * (1 - np.clip(L, 0, 1))

        # white flashes
        if 'flashin' in fx and k < 6:
            w = math.exp(-k / 1.7)
            f = f * (1 - w) + w
        if 'flashout' in fx and k >= nf - 3:
            w = [0.35, 0.7, 1.0][k - (nf - 3)]
            f = f * (1 - w) + w

        # finishing: vignette + grain
        f = f * VIGNETTE
        gs = 0.045 if c['look'] in ('bw', 'neg') else 0.022
        f = f + GRAIN[(c['f0'] + k) % len(GRAIN)] * gs
        if 'fadeout' in fx and tt > dur - 0.9:
            f = f * max(0.0, (dur - tt) / 0.9)
        out = np.clip(f * 255, 0, 255).astype(np.uint8)
        if PREVIEW:
            out = cv2.resize(out, (enc_w, enc_h), interpolation=cv2.INTER_AREA)
        enc.stdin.write(out.tobytes())
    print(f'clip {ci:02d} src={c["src"]} frames={nf}', flush=True)

enc.stdin.close(); enc.wait()
np.save(f'{S}/events.npy', np.array([(t, {'whoosh': 0, 'tick': 1, 'impact': 2, 'type': 3}[k]) for t, k in events]))
print('total frames', TOTAL_F, 'sec', TOTAL_F / FPS)
