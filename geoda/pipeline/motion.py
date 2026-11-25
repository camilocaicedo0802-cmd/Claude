#!/usr/bin/env python3
"""Insertos animados del A1-05 (1080x1920, 30 fps) sobre el set del podcast desenfocado."""
import subprocess, math, numpy as np, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os  # carpeta de trabajo: GEODA_WORK o ~/.geoda_work (la crea setup_work.sh)
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
W, H, FPS = 1080, 1920, 30
FB = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
def bg():
    im = Image.open(f'{G}/hf/p_set_0.png').convert('RGB').resize((W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(28))
    return Image.blend(im, Image.new('RGB', (W, H), (20, 14, 10)), 0.35)
def enc(path, frames):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
def ease(x):
    x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def pop(x):  # 0->1 con rebote
    x = max(0, min(1, x)); return 1 + 2.7 * (x - 1) ** 3 + 1.7 * (x - 1) ** 2 if x < 1 else 1

def card(size, radius=60, fill=(255, 255, 255, 240)):
    c = Image.new('RGBA', size, (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius, fill=fill)
    return c

def shadow(img, off=18, blur=30, alpha=110):
    s = Image.new('RGBA', (img.width + 2 * blur, img.height + 2 * blur), (0, 0, 0, 0))
    s.paste((0, 0, 0, alpha), (blur, blur + off), img.getchannel('A'))
    return s.filter(ImageFilter.GaussianBlur(blur / 2))

def drop_img(scale=1.0):
    S = int(380 * scale); im = Image.new('RGBA', (S, int(S * 1.35)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w, h = im.size; cx, cy, r = w / 2, h * 0.62, w * 0.42
    pts = [(cx, h * 0.04)] + [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(-0.28 * math.pi, 1.28 * math.pi, 60)]
    d.polygon(pts, fill=(90, 175, 230, 255))
    hl = Image.new('RGBA', im.size, (0, 0, 0, 0)); dh = ImageDraw.Draw(hl)
    dh.ellipse([cx - r * 0.55, cy - r * 0.55, cx - r * 0.05, cy + r * 0.05], fill=(255, 255, 255, 120))
    hl = hl.filter(ImageFilter.GaussianBlur(S * 0.04))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.ellipse([cx - r * 0.2, cy + r * 0.05, cx + r * 0.95, cy + r * 0.95], fill=(20, 70, 130, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(S * 0.06))
    m = im.getchannel('A')
    out = Image.alpha_composite(im, Image.composite(sh, Image.new('RGBA', im.size, (0, 0, 0, 0)), m))
    out = Image.alpha_composite(out, Image.composite(hl, Image.new('RGBA', im.size, (0, 0, 0, 0)), m))
    return out

def insert_gota(path, dur):
    B = bg(); n = round(dur * FPS); rnd = random.Random(7)
    cardi = card((820, 820), 70, (246, 226, 208, 245))  # tono piel claro
    tex = Image.new('L', cardi.size, 0); dt = ImageDraw.Draw(tex)
    for _ in range(1800):  # textura de poros suave
        x, y = rnd.randrange(820), rnd.randrange(820); dt.ellipse([x, y, x + 3, y + 3], fill=rnd.randrange(10, 40))
    tex = tex.filter(ImageFilter.GaussianBlur(1.2))
    dots = [(rnd.uniform(120, 700), rnd.uniform(120, 700), rnd.uniform(9, 18), rnd.uniform(0.25, 0.75)) for _ in range(26)]
    dots = [p for p in dots if math.hypot(p[0] - 410, p[1] - 430) > 170]
    drop = drop_img(0.75); frames = []
    for k in range(n):
        t = k / FPS; im = B.copy().convert('RGBA')
        c = cardi.copy(); c.paste((150, 105, 80, 255), (0, 0), tex.point(lambda v: v * 1.0))
        c.putalpha(cardi.getchannel('A'))
        d = ImageDraw.Draw(c)
        for x, y, r, t0 in dots:  # puntitos que aparecen alrededor de la gota
            a = ease((t - t0 - 0.6) / 0.35)
            if a > 0:
                rr = r * pop((t - t0 - 0.6) / 0.35)
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(132, 150, 70, int(220 * a)))
        if t > 2.3:  # ondas de olor saliendo de los puntitos
            for j, (x, y, r, t0) in enumerate(dots[:8]):
                ph = (t - 2.3) * 1.6 + j * 0.3
                a = int(150 * max(0, 1 - (ph % 1.0)))
                yy = y - 60 - (ph % 1.0) * 90
                d.arc([x - 22, yy - 20, x + 22, yy + 20], 200, 340, fill=(120, 130, 60, a), width=6)
        s = 0.92 + 0.08 * ease(t / 0.5)
        cc = c.resize((int(820 * s), int(820 * s)), Image.LANCZOS)
        sh = shadow(cc); im.alpha_composite(sh, ((W - sh.width) // 2, 560 - 30 + 18 + (820 - cc.height) // 2 - 15))
        im.alpha_composite(cc, ((W - cc.width) // 2, 560 + (820 - cc.height) // 2))
        dy = int(-220 * (1 - ease(t / 0.55)))  # la gota cae y se asienta
        im.alpha_composite(drop, ((W - drop.width) // 2, 560 + 410 - drop.height // 2 - 40 + dy))
        frames.append(np.array(im.convert('RGB')))
    enc(path, frames)

def insert_calendario(path, dur):
    B = bg(); n = round(dur * FPS)
    cw, ch = 860, 860
    base = card((cw, ch), 56)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([0, 0, cw - 1, 170], 56, fill=(16, 42, 67, 255)); d.rectangle([0, 110, cw - 1, 170], fill=(16, 42, 67, 255))
    fh = ImageFont.truetype(FB, 64); fd = ImageFont.truetype(FB, 42); fs = ImageFont.truetype(FB, 30)
    d.text((cw / 2, 88), 'NOVIEMBRE', font=fh, fill=(255, 255, 255), anchor='mm')
    for i, s in enumerate('LMMJVSD'):
        d.text((70 + i * 120, 215), s, font=fs, fill=(120, 130, 140), anchor='mm')
    cells = []
    day = 1
    for r in range(5):
        for c in range(7):
            if r == 0 and c < 5:
                continue
            if day > 30:
                break
            x, y = 70 + c * 120, 300 + r * 118
            d.text((x, y), str(day), font=fd, fill=(30, 40, 50), anchor='mm'); cells.append((day, x, y)); day += 1
    skipped = {6, 7, 10}  # días saltados: sin marca, se resaltan
    frames = []
    for k in range(n):
        t = k / FPS; im = B.copy().convert('RGBA'); c = base.copy(); dc = ImageDraw.Draw(c)
        for i, (dd, x, y) in enumerate(cells[:16]):
            t0 = 0.15 + i * 0.09
            if dd in skipped:
                if t > t0:
                    a = int(140 + 100 * math.sin((t - t0) * 9))
                    dc.ellipse([x - 44, y - 44, x + 44, y + 44], outline=(245, 190, 0, a), width=7)
                continue
            a = ease((t - t0) / 0.12)
            if a > 0:
                L = 40 * a
                dc.line([x - 40, y - 40, x - 40 + 2 * L, y - 40 + 2 * L], fill=(225, 45, 45, 255), width=11)
                if a > 0.5:
                    L2 = 40 * ease((t - t0 - 0.06) / 0.1)
                    dc.line([x + 40, y - 40, x + 40 - 2 * L2, y - 40 + 2 * L2], fill=(225, 45, 45, 255), width=11)
        s = 0.92 + 0.08 * ease(t / 0.4)
        cc = c.resize((int(cw * s), int(ch * s)), Image.LANCZOS)
        sh = shadow(cc); im.alpha_composite(sh, ((W - sh.width) // 2, 520 + (ch - cc.height) // 2 - 12))
        im.alpha_composite(cc, ((W - cc.width) // 2, 520 + (ch - cc.height) // 2))
        frames.append(np.array(im.convert('RGB')))
    enc(path, frames)

if __name__ == '__main__':
    import sys
    insert_gota(f'{G}/a105/tmp/ins_gota.mp4', float(sys.argv[1]))
    insert_calendario(f'{G}/a105/tmp/ins_cal.mp4', float(sys.argv[2]))
