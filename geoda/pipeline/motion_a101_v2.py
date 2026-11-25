#!/usr/bin/env python3
"""Gráficos animados del A1-01 v2 (sobre fotos; producto real sin deformar).
clock : sticker de reloj gigante '3:00 p. m.' (PNG con alfa) para el hook A.
hb    : frasco genérico -> X roja gigante cae encima con sacudida (hook B).
b1    : reloj grande que gira de 7:00 a. m. a 3:00 p. m. sobre la oficina desenfocada.
b4    : puntitos (bacterias) que se multiplican + nube gris de olor; la nube rosa del perfume la tapa pero lo gris sigue debajo.
b5    : revelación de la piedra REAL a contraluz: de macro de la piedra a la mano con el producto, destellos.
sfx   : tic-tac que se acelera + campanita (reloj), golpe de la X."""
import os, sys, math, subprocess, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os  # carpeta de trabajo: GEODA_WORK o ~/.geoda_work (la crea setup_work.sh)
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102')
from motion_v3 import cover, writer, ease, star          # mismas utilidades del A1-02
A = f'{G}/a101'; T = f'{A}/tmp2'; os.makedirs(T, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
RED, NAVY, YEL = (230, 40, 40), (16, 50, 74), (255, 212, 59)

def clock_img(r, hh, mm, label=None, label_col=RED, ring=RED):
    """Reloj vectorial (RGBA) de radio r, con etiqueta opcional debajo."""
    S = 3; R = r * S
    lab_h = int(r * 0.62) if label else 0
    im = Image.new('RGBA', (2 * R + 40 * S, 2 * R + 40 * S + lab_h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); cx = cy = R + 20 * S
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx - R, cy - R + 10 * S, cx + R, cy + R + 10 * S], fill=(0, 0, 0, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * S)))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 255, 255, 255), outline=ring + (255,), width=int(R * 0.09))
    for k in range(12):
        a = k * math.pi / 6; r0 = R * (0.74 if k % 3 else 0.66); r1 = R * 0.84
        d.line([cx + r0 * math.sin(a), cy - r0 * math.cos(a), cx + r1 * math.sin(a), cy - r1 * math.cos(a)], fill=(30, 30, 30, 255),
               width=int(R * (0.05 if k % 3 == 0 else 0.025)))
    am = (mm / 60) * 2 * math.pi; ah = ((hh % 12) + mm / 60) / 12 * 2 * math.pi
    d.line([cx, cy, cx + R * 0.48 * math.sin(ah), cy - R * 0.48 * math.cos(ah)], fill=(20, 20, 20, 255), width=int(R * 0.075))
    d.line([cx, cy, cx + R * 0.70 * math.sin(am), cy - R * 0.70 * math.cos(am)], fill=(20, 20, 20, 255), width=int(R * 0.05))
    d.ellipse([cx - R * 0.07, cy - R * 0.07, cx + R * 0.07, cy + R * 0.07], fill=ring + (255,))
    if label:
        f = ImageFont.truetype(FONT, int(r * 0.42) * S)
        tw = d.textlength(label, font=f); ty = cy + R + 14 * S
        pad = 18 * S; bx0, bx1 = cx - tw / 2 - pad, cx + tw / 2 + pad
        d.rounded_rectangle([bx0, ty, bx1, ty + int(r * 0.56) * S], radius=14 * S, fill=label_col + (255,))
        d.text((cx, ty + int(r * 0.28) * S), label, font=f, fill=(255, 255, 255, 255), anchor='mm')
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)

def clock():
    clock_img(150, 3, 0, '3:00 p. m.').save(f'{T}/clock_sticker.png'); print('clock ok')

def big_x(size):
    S = 2; s = size * S
    im = Image.new('RGBA', (s + 60, s + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im); o = 30; w = int(s * 0.16)
    for col, ww in (((255, 255, 255, 255), w + 26), (RED + (255,), w)):
        d.line([o, o, o + s, o + s], fill=col, width=ww); d.line([o + s, o, o, o + s], fill=col, width=ww)
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)

def hb(dur=3.2):
    base = cover(f'{G}/hf/p_aerosol_0.png')
    X = big_x(560); XA = np.array(X).astype(np.float32); xh, xw = XA.shape[:2]
    cx, cy = 548, 1080; T_HIT = 0.32
    nf = round(dur * FPS); p = writer(f'{T}/hb.mp4', nf)
    for k in range(nf):
        t = k / FPS
        z = 1.12 + 0.05 * t / dur
        sx = sy = 0.0
        if T_HIT <= t < T_HIT + 0.45:   # sacudida al caer
            u = (t - T_HIT) / 0.45; a = 22 * (1 - u) ** 2
            sx, sy = a * math.sin(u * 60), a * math.cos(u * 47)
        M = np.float32([[z, 0, -(z - 1) * 548 + sx], [0, z, -(z - 1) * 1100 + sy]])
        fr = cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
        if t >= 0.02:
            if t < T_HIT:   # cae desde arriba, grande y girando
                u = (t - 0.02) / (T_HIT - 0.02); u = u * u
                sc = 1.6 - 0.6 * u; yy = -500 + (cy + 500) * u; ang = 25 * (1 - u)
            else:
                u = t - T_HIT; sc = 1.0 + 0.08 * math.exp(-10 * u) * math.cos(u * 30); yy = cy; ang = 0
            xi = cv2.resize(XA, (int(xw * sc), int(xh * sc)), interpolation=cv2.INTER_AREA)
            Mr = cv2.getRotationMatrix2D((xi.shape[1] / 2, xi.shape[0] / 2), ang, 1.0)
            xi = cv2.warpAffine(xi, Mr, (xi.shape[1], xi.shape[0]))
            x0, y0 = int(cx + sx - xi.shape[1] / 2), int(yy + sy - xi.shape[0] / 2)
            ya, yb = max(0, y0), min(H, y0 + xi.shape[0]); xa, xb = max(0, x0), min(W, x0 + xi.shape[1])
            if yb > ya and xb > xa:
                sub = xi[ya - y0:yb - y0, xa - x0:xb - x0]; al = sub[..., 3:4] / 255
                fr[ya:yb, xa:xb] = fr[ya:yb, xa:xb] * (1 - al) + sub[..., [2, 1, 0]] * al
        p.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait(); print('hb ok')

def b1(dur=3.7):
    bg = cover(f'{G}/hf/f_huele_0.png')
    bg = np.clip(cv2.GaussianBlur(bg, (0, 0), 18).astype(np.float32) * 0.78, 0, 255).astype(np.uint8)
    nf = round(dur * FPS); p = writer(f'{T}/b1.mp4', nf)
    T0, T1 = 1.05, 2.05   # giro rápido de 7:00 a 15:00 sincronizado con 'y a las tres'
    for k in range(nf):
        t = k / FPS
        u = ease((t - T0) / (T1 - T0)) if t >= T0 else 0.0
        mins = 7 * 60 + u * 8 * 60; hh, mm = int(mins // 60), mins % 60
        done = u >= 0.98
        lab, col = ('3:00 p. m.', RED) if done else (('7:00 a. m.', NAVY) if u < 0.02 else ('  ...  ', NAVY))
        ck = clock_img(260, hh, mm, lab, col, ring=RED if done else NAVY)
        pop = 1.0 + 0.10 * math.exp(-12 * max(0, t - T1)) * (t >= T1) + 0.06 * math.exp(-14 * t)
        if pop != 1.0:
            ck = ck.resize((int(ck.width * pop), int(ck.height * pop)), Image.LANCZOS)
        fr = Image.fromarray(bg[:, :, ::-1].copy()).convert('RGBA')
        fr.alpha_composite(ck, (W // 2 - 20 - ck.width // 2, 860 - ck.height // 2))
        p.stdin.write(np.array(fr.convert('RGB'))[:, :, ::-1].tobytes())
    p.stdin.close(); p.wait(); print('b1 ok')

def b4(dur=3.15):
    rnd = random.Random(7)
    bg = cover(f'{G}/hf/f_perfume_0.png')
    bg = np.clip(cv2.GaussianBlur(bg, (0, 0), 22).astype(np.float32) * 0.30 + np.float32([74, 50, 16]) * 0.55, 0, 255).astype(np.uint8)
    # 'piel' en primer plano: elipse tibia con poros
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    skin = np.exp(-(((xx - 540) / 620) ** 2 + ((yy - 1250) / 520) ** 2))
    tex = cv2.GaussianBlur(np.random.RandomState(3).rand(H, W).astype(np.float32), (0, 0), 3)
    skin_col = np.float32([128, 160, 200]) * (0.9 + 0.2 * tex[..., None])
    sm = np.clip(skin * 1.6, 0, 1)[..., None]
    base = (bg.astype(np.float32) * (1 - sm) + skin_col * sm)
    dots = [(rnd.uniform(200, 880), rnd.uniform(1000, 1500), rnd.uniform(0.0, 1.3), rnd.uniform(9, 17)) for _ in range(70)]
    puffs = [(rnd.uniform(300, 780), rnd.uniform(0, 1), rnd.uniform(70, 150)) for _ in range(14)]
    pk = [(rnd.uniform(220, 860), rnd.uniform(0, 1), rnd.uniform(90, 170)) for _ in range(12)]
    nf = round(dur * FPS); p = writer(f'{T}/b4.mp4', nf)
    for k in range(nf):
        t = k / FPS
        fr = base.copy()
        # nube gris de olor que sube
        g = np.zeros((H, W), np.float32)
        for x0, ph, r in puffs:
            age = t - 0.35 - ph * 0.6
            if age > 0:
                y = 1060 - age * 300; rr = r * (0.7 + 0.6 * age)
                cv2.circle(g, (int(x0 + 30 * math.sin(age * 2 + ph * 6)), int(y)), int(rr), min(1.0, age * 1.8), -1, cv2.LINE_AA)
        g = np.clip(cv2.GaussianBlur(g, (0, 0), 24) * 1.1, 0, 0.88)
        fr = fr * (1 - g[..., None]) + np.float32([150, 152, 158]) * g[..., None]
        # nube rosa del perfume (1.5 s en adelante) que tapa, con lo gris asomando
        if t > 1.45:
            pg = np.zeros((H, W), np.float32)
            for x0, ph, r in pk:
                age = t - 1.45 - ph * 0.35
                if age > 0:
                    cv2.circle(pg, (int(x0 - 300 + age * 330), int(520 + ph * 420)), int(r * (0.7 + 0.4 * age)), min(1.0, age * 2), -1, cv2.LINE_AA)
            pg = np.clip(cv2.GaussianBlur(pg, (0, 0), 30) * 0.8, 0, 0.72)
            fr = fr * (1 - pg[..., None]) + np.float32([205, 150, 255]) * pg[..., None]
        out = np.clip(fr, 0, 255).astype(np.uint8)
        for x0, y0, born, r in dots:   # bacterias: aparecen y se multiplican, se mueven un poco
            if t >= born:
                a = min(1.0, (t - born) * 4)
                x = x0 + 6 * math.sin(t * 3 + y0); y = y0 + 6 * math.cos(t * 2.5 + x0)
                cv2.circle(out, (int(x), int(y)), int(r * a), (60, 175, 60), -1, cv2.LINE_AA)
                cv2.circle(out, (int(x - r * 0.3), int(y - r * 0.3)), max(1, int(r * 0.3 * a)), (170, 240, 170), -1, cv2.LINE_AA)
        p.stdin.write(out.tobytes())
    p.stdin.close(); p.wait(); print('b4 ok')

def b5(dur=4.6):
    base = cover(f'{G}/v2frames/mano.png')
    mask = np.zeros((H, W), np.float32); cv2.rectangle(mask, (360, 606), (700, 1390), 1.0, -1); mask = cv2.GaussianBlur(mask, (0, 0), 6)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nf = round(dur * FPS); p = writer(f'{T}/b5.mp4', nf)
    sc0, sc1 = (540.0, 700.0), (530.0, 980.0)   # de la piedra al producto completo
    for k in range(nf):
        t = k / FPS
        u = ease(min(1.0, t / 2.4))
        z = 2.3 + (1.08 - 2.3) * u + 0.04 * max(0, t - 2.4) / (dur - 2.4)
        cx = sc0[0] + (sc1[0] - sc0[0]) * u; cy = sc0[1] + (sc1[1] - sc0[1]) * u
        fr = base.copy()
        for t0, t1 in ((2.5, 3.2),):
            if t0 <= t <= t1:
                v = (t - t0) / (t1 - t0); c = -500 + v * 1900
                band = np.exp(-((xx + 0.6 * yy - (c + 900)) / 70) ** 2) * mask * math.sin(math.pi * v) * 0.5
                fr = np.clip(fr.astype(np.float32) + band[..., None] * 255, 0, 255).astype(np.uint8)
        for t0, sx, sy, r in ((0.5, 500, 680, 90), (1.7, 615, 668, 100), (3.4, 478, 676, 130)):
            v = (t - t0) / 0.55
            if 0 <= v <= 1:
                star(fr, sx, sy, r * math.sin(math.pi * v), math.sin(math.pi * v))
        M = np.float32([[z, 0, W / 2 - z * cx], [0, z, 900 - z * cy]])
        fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        if t < 0.6:   # entra desde un poco oscuro, como al abrir la mano frente a la ventana
            fr = (fr.astype(np.float32) * (0.55 + 0.45 * ease(t / 0.6))).astype(np.uint8)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); print('b5 ok')

def sfx():
    o = f'{G}/audio'
    # tic-tac que se acelera (1.05-2.05 s) y campanita a las 3
    ticks = [0.15, 0.55, 0.95] + [1.05 + 1.0 * (1 - (1 - i / 9) ** 1.6) for i in range(10)]
    expr = '+'.join(f'0.5*sin(2*PI*{1800 if i % 2 else 1400}*(t-{tt:.3f}))*exp(-90*(t-{tt:.3f}))*gte(t,{tt:.3f})' for i, tt in enumerate(ticks))
    expr += '+0.25*(sin(2*PI*1568*(t-2.08))+0.5*sin(2*PI*2349*(t-2.08)))*exp(-4*(t-2.08))*gte(t,2.08)'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f"aevalsrc='{expr}':s=48000:d=3.2", f'{o}/sfx_clock.wav'], check=True)
    print('sfx ok')

if __name__ == '__main__':
    for job in sys.argv[1:] or ['clock', 'hb', 'b1', 'b4', 'b5', 'sfx']:
        globals()[job]()
