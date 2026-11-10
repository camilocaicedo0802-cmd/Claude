"""Motor de montaje vertical (1080x1920, 30 fps) para notas de Proclama del Pacífico.

Cada plano (Shot) lee su fuente con ffmpeg ya recortada a 9:16 (con tonemapping si es HDR del iPhone),
y en Python se le aplica zoom lento. Los gráficos se componen encima cuadro a cuadro con numpy.
"""
import json
import math
import os
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
RED = (212, 24, 25)
DARKRED = (120, 8, 10)
NAVY = (14, 30, 86)
WHITE = (255, 255, 255)
ROOT = '/home/user/notas'
FD = ROOT + '/fonts/'
ASSETS = ROOT + '/work/assets'

# --------------------------------------------------------------------------------------- utilidades
_fc = {}


def font(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + name + '.ttf', size)
    return _fc[k]


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def ease_io(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_back(x, s=1.5):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                        'format=duration:stream=codec_type,width,height,color_transfer:stream_side_data=rotation',
                        '-of', 'json', path], capture_output=True, text=True)
    return json.loads(r.stdout)


def is_hlg(path):
    p = probe(path)
    return any(s.get('color_transfer') == 'arib-std-b67' for s in p['streams'] if s.get('codec_type') == 'video')


def duration(path):
    return float(probe(path)['format']['duration'])


TONEMAP = ('zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,'
           'tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=contrast=1.05:brightness=0.012:saturation=1.06')


# --------------------------------------------------------------------------------------- composición
def blend(dst, src, x, y, alpha=1.0):
    """Pega src (RGBA uint8) sobre dst (RGB uint8) en (x, y) con opacidad global."""
    if alpha <= 0.003:
        return
    h, w = src.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    a = s[:, :, 3:4].astype(np.float32) * (alpha / 255.0)
    d = dst[y0:y1, x0:x1]
    d[:] = (s[:, :, :3].astype(np.float32) * a + d.astype(np.float32) * (1 - a) + 0.5).astype(np.uint8)


def pil_rgba(im):
    return np.array(im.convert('RGBA'))


def darken(frame, amount, y0=0, y1=None):
    y1 = H if y1 is None else y1
    frame[y0:y1] = (frame[y0:y1].astype(np.float32) * (1 - amount)).astype(np.uint8)


_grad_cache = {}


def vgrad(y0, y1, a0, a1, color=(0, 0, 0)):
    """Sprite RGBA de un degradado vertical de opacidad a0 -> a1 (0..1) entre y0 y y1."""
    k = (y0, y1, a0, a1, color)
    if k not in _grad_cache:
        n = y1 - y0
        a = np.linspace(a0, a1, n)
        a = a * a * (3 - 2 * a) if a1 > a0 else a
        spr = np.zeros((n, W, 4), np.uint8)
        spr[:, :, :3] = color
        spr[:, :, 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)[:, None]
        _grad_cache[k] = spr
    return _grad_cache[k]


def blur_frame(frame, k=61, dark=0.45, tint=None):
    small = cv2.resize(frame, (W // 6, H // 6), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), k / 12)
    out = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) * (1 - dark)
    if tint is not None:
        out = out * 0.75 + np.array(tint, np.float32) * 0.25 * (1 - dark)
    return np.clip(out, 0, 255).astype(np.uint8)


# --------------------------------------------------------------------------------------- planos de video
class Shot:
    """Un plano: fuente, entrada (s), duración en la línea de tiempo (s).

    focus: punto (0..1) que queda centrado al recortar a 9:16; z0/z1: zoom inicial/final (Ken Burns);
    speed: <1 cámara lenta; crop: (x, y, w, h) en fracciones de la fuente antes de escalar;
    fit='blur' para fuentes horizontales: cuadro completo centrado sobre fondo desenfocado."""

    def __init__(self, src, t_in, dur, focus=(0.5, 0.5), focus1=None, z0=1.0, z1=1.06, speed=1.0, crop=None,
                 fit='cover', fit_y=0.42, vol=None, label=None, hflip=False, grade=None, freeze=False, post=None):
        self.src, self.t_in, self.dur = src, t_in, dur
        self.focus, self.focus1 = focus, focus1 or focus
        self.z0, self.z1, self.speed, self.crop, self.fit, self.fit_y = z0, z1, speed, crop, fit, fit_y
        self.vol, self.label, self.hflip, self.grade, self.freeze = vol, label, hflip, grade, freeze
        self.post = post
        self.n = int(round(dur * FPS))

    def _cmd(self):
        S = max(self.z0, self.z1, 1.0)
        self.ws, self.hs = int(math.ceil(W * S / 2) * 2), int(math.ceil(H * S / 2) * 2)
        vf = []
        if is_hlg(self.src):
            vf.append(TONEMAP)
        if self.crop:
            cx, cy, cw, ch = self.crop
            vf.append(f'crop=iw*{cw}:ih*{ch}:iw*{cx}:ih*{cy}')
        if self.hflip:
            vf.append('hflip')
        if self.speed != 1.0:
            vf.append(f'setpts=PTS/{self.speed}')
        vf.append(f'fps={FPS}')
        if self.fit == 'cover':
            vf.append(f'scale={self.ws}:{self.hs}:force_original_aspect_ratio=increase:flags=lanczos')
            vf.append(f'crop={self.ws}:{self.hs}:(iw-{self.ws})*0.5:(ih-{self.hs})*0.5')
        else:  # 'blur': fuente horizontal sobre fondo desenfocado
            vf.append(f'scale={self.ws}:-2:flags=lanczos')
        if self.grade:
            vf.append(self.grade)
        vf.append('format=rgb24')
        src_dur = self.dur * self.speed + 0.5
        return ['ffmpeg', '-v', 'error', '-ss', f'{self.t_in:.3f}', '-t', f'{src_dur:.3f}', '-i', self.src,
                '-vf', ','.join(vf), '-an', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']

    def frames(self):
        cmd = self._cmd()
        if self.fit == 'cover':
            fw, fh = self.ws, self.hs
        else:
            p = probe(self.src)
            vs = [s for s in p['streams'] if s.get('codec_type') == 'video'][0]
            iw, ih = vs['width'], vs['height']
            rot = 0
            for sd in vs.get('side_data_list', []) or []:
                rot = int(sd.get('rotation', 0))
            if abs(rot) == 90:
                iw, ih = ih, iw
            if self.crop:
                iw, ih = iw * self.crop[2], ih * self.crop[3]
            fw, fh = self.ws, int(round(self.ws * ih / iw / 2) * 2)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=fw * fh * 3 * 2)
        try:
            yield from self._iter(proc, fw, fh)
        finally:
            proc.stdout.close()
            proc.kill()
            proc.wait()

    def _iter(self, proc, fw, fh):
        size = fw * fh * 3
        last = None
        for i in range(self.n):
            buf = proc.stdout.read(size) if (not self.freeze or last is None) else b''
            if len(buf) == size:
                last = np.frombuffer(buf, np.uint8).reshape(fh, fw, 3)
            if last is None:
                last = np.zeros((fh, fw, 3), np.uint8)
            u = i / max(1, self.n - 1)
            z = self.z0 + (self.z1 - self.z0) * ease_io(u) if self.z1 != self.z0 else self.z0
            fx = self.focus[0] + (self.focus1[0] - self.focus[0]) * ease_io(u)
            fy = self.focus[1] + (self.focus1[1] - self.focus[1]) * ease_io(u)
            out = self._zoom(last, z, fx, fy) if self.fit == 'cover' else self._fitblur(last, z)
            yield self.post(out) if self.post else out

    def _zoom(self, img, z, fx, fy):
        fh, fw = img.shape[:2]
        S = fw / W
        cw, ch = W * S / z, H * S / z
        x0 = clamp(fx * fw - cw / 2, 0, fw - cw)
        y0 = clamp(fy * fh - ch / 2, 0, fh - ch)
        if abs(cw - W) < 0.5 and abs(ch - H) < 0.5:
            return np.ascontiguousarray(img[int(y0):int(y0) + H, int(x0):int(x0) + W])
        M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
        return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_AREA if cw > W else cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT)

    def _fitblur(self, img, z):
        fh, fw = img.shape[:2]
        bg = cv2.resize(img, (W, int(W * fh / fw)), interpolation=cv2.INTER_AREA)
        sc = H / bg.shape[0]
        bg = cv2.resize(bg, (int(bg.shape[1] * sc), H), interpolation=cv2.INTER_LINEAR)
        x0 = (bg.shape[1] - W) // 2
        bg = blur_frame(np.ascontiguousarray(bg[:, x0:x0 + W]), dark=0.5)
        fg = cv2.resize(img, (int(W * z), int(W * z * fh / fw)), interpolation=cv2.INTER_AREA)
        y = int(H * self.fit_y - fg.shape[0] / 2)
        x = (W - fg.shape[1]) // 2
        sub = fg[max(0, -y):, max(0, -x):]
        bg[max(0, y):max(0, y) + sub.shape[0], max(0, x):max(0, x) + sub.shape[1]] = sub[:H - max(0, y), :W - max(0, x)]
        return bg


class Still:
    """Imagen fija (o fondo generado) como plano."""

    def __init__(self, img, dur, z0=1.0, z1=1.05, focus=(0.5, 0.5)):
        self.img, self.dur, self.n = img, dur, int(round(dur * FPS))
        self.z0, self.z1, self.focus = z0, z1, focus
        self.vol, self.label, self.src, self.post = None, None, None, None

    def frames(self):
        base = self.img if isinstance(self.img, np.ndarray) else np.array(Image.open(self.img).convert('RGB'))
        S = max(self.z0, self.z1)
        big = cv2.resize(base, (int(W * S), int(H * S)), interpolation=cv2.INTER_AREA)
        sh = Shot.__new__(Shot)
        for i in range(self.n):
            u = i / max(1, self.n - 1)
            z = self.z0 + (self.z1 - self.z0) * ease_io(u)
            out = Shot._zoom(sh, big, z, self.focus[0], self.focus[1])
            yield self.post(out) if self.post else out


# --------------------------------------------------------------------------------------- secuencias RGBA
class Seq:
    """Secuencia de PNG RGBA (transiciones, logo, rótulo) cargada bajo demanda."""

    def __init__(self, folder, x=0, y=0):
        self.files = sorted(f for f in os.listdir(folder) if f.endswith('.png'))
        self.folder, self.x, self.y = folder, x, y
        self.cache = {}

    def __len__(self):
        return len(self.files)

    def get(self, i):
        i = int(clamp(i, 0, len(self.files) - 1))
        if i not in self.cache:
            if len(self.cache) > 90:
                self.cache.clear()
            self.cache[i] = np.array(Image.open(os.path.join(self.folder, self.files[i])).convert('RGBA'))
        return self.cache[i]


# --------------------------------------------------------------------------------------- texto
CENSOR = {}


def censor(word):
    """Aplica la censura de palabras sensibles conservando puntuación y mayúsculas."""
    core = word.strip('.,;:¿?¡!"“”()…')
    low = core.lower()
    for k, v in CENSOR.items():
        if low == k:
            rep = v.upper() if core.isupper() else (v.capitalize() if core[:1].isupper() else v)
            return word.replace(core, rep)
    return word


def tokenize(text):
    """'[palabra clave]' -> resaltada con caja roja; '{palabra}' -> color rojo. Devuelve [(texto, estilo)]."""
    out, i, cur, style = [], 0, '', 'n'
    groups = []
    while i < len(text):
        c = text[i]
        if c in '[{':
            if cur.strip():
                groups.append((cur, 'n'))
            cur = ''
            style = 'box' if c == '[' else 'red'
        elif c in ']}':
            groups.append((cur, style))
            cur, style = '', 'n'
        else:
            cur += c
        i += 1
    if cur.strip():
        groups.append((cur, 'n'))
    for g, st in groups:
        words = g.split()
        if st == 'box':
            out.append((' '.join(censor(w) for w in words), 'box'))
        else:
            for j, w in enumerate(words):
                ns = j == 0 and not g[:1].isspace() and out and out[-1][1].startswith('box')
                out.append((censor(w), st + ('_ns' if ns else '')))
    return out


def text_w(fnt, s):
    return fnt.getlength(s)


def layout(text, fnt, max_w, line_h, space=None, align='left', box_pad=(14, 4)):
    """Distribuye palabras en renglones. Devuelve [(x, y, palabra, estilo, ancho)], alto total."""
    toks = tokenize(text)
    space = space if space is not None else fnt.getlength(' ')
    lines, cur, cw = [], [], 0
    for word, st in toks:
        if word == '\\n':
            lines.append(cur)
            cur, cw = [], 0
            continue
        ns = st.endswith('_ns')
        ww = text_w(fnt, word) + (2 * box_pad[0] if st == 'box' else 0)
        if cur and not ns and cw + space + ww > max_w:
            lines.append(cur)
            cur, cw = [], 0
        cur.append((word, st, ww))
        cw += (space if len(cur) > 1 and not ns else 0) + ww
    if cur:
        lines.append(cur)
    out = []
    for li, ln in enumerate(lines):
        lw = sum(w for _, _, w in ln) + space * sum(1 for k, (_, st, _) in enumerate(ln) if k and not st.endswith('_ns'))
        x = 0 if align == 'left' else (max_w - lw) / 2 if align == 'center' else max_w - lw
        for k, (word, st, ww) in enumerate(ln):
            if k and st.endswith('_ns'):
                x -= space
            out.append((x, li * line_h, word, st.replace('_ns', ''), ww, li))
            x += ww + space
    return out, len(lines) * line_h, len(lines)


def word_sprite(word, fnt, fill=WHITE, style='n', shadow=0.55, box_color=RED, box_pad=(14, 4), line_h=None,
                stroke=0):
    """Sprite RGBA de una palabra (con sombra suave o caja roja)."""
    asc, desc = fnt.getmetrics()
    lh = line_h or (asc + desc)
    tw = int(math.ceil(text_w(fnt, word)))
    pad = 24
    bw = tw + (2 * box_pad[0] if style == 'box' else 0)
    im = Image.new('RGBA', (bw + 2 * pad, lh + 2 * pad), (0, 0, 0, 0))
    tx = pad + (box_pad[0] if style == 'box' else 0)
    ty = pad + (lh - (asc + desc)) // 2
    if style == 'box':
        d = ImageDraw.Draw(im)
        top = ty + int(asc * 0.12) - box_pad[1]
        bot = ty + asc + int(desc * 0.25) + box_pad[1]
        d.rectangle([pad, top, pad + bw, bot], fill=box_color + (255,))
    elif shadow > 0:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((tx + 2, ty + 3), word, font=fnt, fill=(0, 0, 0, int(255 * shadow)))
        sh = sh.filter(ImageFilter.GaussianBlur(5))
        im = Image.alpha_composite(im, sh)
        sh2 = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh2).text((tx, ty + 1), word, font=fnt, fill=(0, 0, 0, int(255 * shadow * 0.6)))
        im = Image.alpha_composite(im, sh2.filter(ImageFilter.GaussianBlur(1.5)))
    d = ImageDraw.Draw(im)
    col = RED if style == 'red' else fill
    d.text((tx, ty), word, font=fnt, fill=col + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
    return np.array(im), pad


class TextBlock:
    """Bloque de texto que aparece palabra por palabra (subida + fundido)."""

    def __init__(self, text, fnt, x, y, max_w, line_h, t0, t1, align='left', fill=WHITE, stagger=0.045,
                 rise=22, fade=0.22, shadow=0.55, anchor='top', out=0.25, box_color=RED, stroke=0):
        self.items, self.h, self.nlines = layout(text, fnt, max_w, line_h, align=align)
        if anchor == 'bottom':
            y = y - self.h
        elif anchor == 'middle':
            y = y - self.h / 2
        self.x, self.y, self.t0, self.t1 = x, y, t0, t1
        self.stagger, self.rise, self.fade, self.out = stagger, rise, fade, out
        self.sprites = []
        for (wx, wy, word, st, ww, li) in self.items:
            spr, pad = word_sprite(word, fnt, fill, st, shadow, box_color=box_color, line_h=line_h, stroke=stroke)
            self.sprites.append((spr, x + wx - pad, self.y + wy - pad))

    def draw(self, frame, t):
        if t < self.t0 or t > self.t1 + 0.01:
            return
        ao = 1.0 - ease_in((t - (self.t1 - self.out)) / self.out) if self.out > 0 else 1.0
        for k, (spr, sx, sy) in enumerate(self.sprites):
            u = (t - self.t0 - k * self.stagger) / self.fade
            if u <= 0:
                continue
            e = ease_out(u)
            blend(frame, spr, sx, sy + self.rise * (1 - e), alpha=clamp(u * 1.3) * ao)


def ffmpeg_writer(path, crf=17, preset='medium', extra=None):
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-preset', preset, '-crf', str(crf), '-pix_fmt', 'yuv420p',
           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-movflags', '+faststart']
    cmd += (extra or []) + [path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def blur_band(frame, y0, y1, feather=60):
    """Desenfoca una franja horizontal (para tapar textos quemados de otros medios)."""
    a, b = max(0, y0 - feather), min(H, y1 + feather)
    band = frame[a:b]
    small = cv2.resize(band, (W // 16, max(1, (b - a) // 16)), interpolation=cv2.INTER_AREA)
    bl = cv2.resize(cv2.GaussianBlur(small, (0, 0), 3), (W, b - a), interpolation=cv2.INTER_LINEAR) * 0.8
    m = np.ones(b - a, np.float32)
    ramp = np.linspace(0, 1, feather)
    m[:feather] = ramp
    m[-feather:] = ramp[::-1]
    m = m[:, None, None]
    frame[a:b] = (bl * m + band * (1 - m)).astype(np.uint8)
    return frame


def render(shots, overlays, out_path, total=None, crf=17, preset='medium', log_every=150):
    """shots: lista de (t_inicio, plano) contiguos; overlays: objetos con draw(frame, t) en orden de capa."""
    import sys
    import time
    shots = sorted(shots, key=lambda s: s[0])
    total = total or (shots[-1][0] + shots[-1][1].dur)
    n = int(round(total * FPS))
    wr = ffmpeg_writer(out_path, crf=crf, preset=preset)
    si, gen, cur = -1, None, None
    t_start = time.time()
    for i in range(n):
        t = i / FPS
        while si + 1 < len(shots) and t >= shots[si + 1][0] - 1e-6:
            si += 1
            if gen is not None:
                gen.close()
            gen = shots[si][1].frames()
        try:
            cur = next(gen)
        except StopIteration:
            pass
        frame = np.array(cur, copy=True)
        for ov in overlays:
            ov.draw(frame, t)
        wr.stdin.write(frame.tobytes())
        if i % log_every == 0:
            el = time.time() - t_start
            print(f'  {i}/{n} ({100 * i / n:.0f}%) {el:.0f}s', flush=True)
    wr.stdin.close()
    wr.wait()
    return total


def still(shots, overlays, t, path=None, scale=0.5):
    """Fotograma de revisión en el instante t (decodifica el plano hasta ese punto)."""
    for t0, s in sorted(shots, key=lambda x: x[0]):
        if t0 <= t < t0 + s.dur:
            k = int((t - t0) * FPS)
            for j, fr in enumerate(s.frames()):
                if j == k:
                    frame = np.array(fr, copy=True)
                    break
            break
    for ov in overlays:
        ov.draw(frame, t)
    im = Image.fromarray(frame)
    if scale != 1:
        im = im.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    if path:
        im.save(path)
    return im


def contact(ims, path, cols=6, label=None):
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (w * cols, h * rows), (0, 0, 0))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(path, quality=88)
