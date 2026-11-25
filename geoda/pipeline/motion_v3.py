#!/usr/bin/env python3
"""Planos animados del A1-02 v3 (todo sobre fotos: la etiqueta no se deforma).
ha   : foto REAL del producto a contraluz; la mano lo gira rápido (giro con rebote) + destellos sobre la piedra + brillo que barre el tubo.
hb   : frasco genérico -> línea roja lo tacha -> se va -> cae el GEODA REAL en su lugar (sombra de contacto, rebote).
b1   : piedra sobre la palma con giro lento.
land : landing con scroll + dedo que toca el botón Comprar.
sfx  : error (dos tonos), destello y golpe seco sintetizados.
uso: motion_v3.py [ha hb b1 land sfx]"""
import os, sys, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
A = f'{G}/a102'; T = f'{A}/tmp3'; os.makedirs(T, exist_ok=True)
W, H, FPS = 1080, 1920, 30

def cover(path):
    im = Image.open(path).convert('RGB')
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return np.array(im.crop((x, y, x + W, y + H)))[:, :, ::-1].copy()   # BGR

def writer(out, nf):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                             '-i', '-', '-frames:v', str(nf), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14',
                             '-pix_fmt', 'yuv420p', '-an', out], stdin=subprocess.PIPE)

def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

def star(img, cx, cy, r, a):
    """destello de 4 puntas + halo (aditivo)."""
    if a <= 0.01 or r < 2:
        return
    lay = np.zeros(img.shape[:2], np.float32)
    s = int(r * 1.2)
    cv2.line(lay, (int(cx - s), int(cy)), (int(cx + s), int(cy)), 1.0, max(2, int(r * 0.05)), cv2.LINE_AA)
    cv2.line(lay, (int(cx), int(cy - s)), (int(cx), int(cy + s)), 1.0, max(2, int(r * 0.05)), cv2.LINE_AA)
    s2 = int(r * 0.45)
    cv2.line(lay, (int(cx - s2), int(cy - s2)), (int(cx + s2), int(cy + s2)), 0.6, max(1, int(r * 0.03)), cv2.LINE_AA)
    cv2.line(lay, (int(cx - s2), int(cy + s2)), (int(cx + s2), int(cy - s2)), 0.6, max(1, int(r * 0.03)), cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), max(1.0, r * 0.03)) * 1.6
    halo = np.zeros_like(lay); cv2.circle(halo, (int(cx), int(cy)), int(r * 0.35), 1.0, -1, cv2.LINE_AA)
    lay = lay + cv2.GaussianBlur(halo, (0, 0), r * 0.18) * 0.9
    img[:] = np.clip(img.astype(np.float32) + (lay * a * 255)[..., None] * np.float32([0.92, 0.97, 1.0]), 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ HA
def ha(dur=3.2):
    base = cover(f'{G}/v2frames/mano.png')
    # brillo que barre: banda diagonal limitada a la silueta del tubo/tapa (x 355-705, y 600-1400)
    mask = np.zeros((H, W), np.float32)
    cv2.rectangle(mask, (360, 606), (700, 1390), 1.0, -1)
    mask = cv2.GaussianBlur(mask, (0, 0), 6)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nf = round(dur * FPS); p = writer(f'{T}/ha.mp4', nf)
    piv = (530.0, 1000.0)
    for k in range(nf):
        t = k / FPS
        fr = base.copy()
        # barrido de brillo 0.15-0.85 s y 1.7-2.3 s
        for t0, t1 in ((0.15, 0.85), (1.75, 2.35)):
            if t0 <= t <= t1:
                u = (t - t0) / (t1 - t0)
                c = -500 + u * 1900                       # posición de la banda en x+0.6y
                band = np.exp(-((xx + 0.6 * yy - (c + 900)) / 70) ** 2) * mask * math.sin(math.pi * u) * 0.55
                fr = np.clip(fr.astype(np.float32) + band[..., None] * 255, 0, 255).astype(np.uint8)
        # destellos sobre la piedra (cúpula en ~ (470-640, 660-740))
        for t0, cx, cy, r in ((0.32, 478, 676, 120), (1.15, 612, 668, 95), (2.05, 520, 650, 130)):
            u = (t - t0) / 0.5
            if 0 <= u <= 1:
                star(fr, cx, cy, r * math.sin(math.pi * u), math.sin(math.pi * u))
        # la mano gira rápido: giro con rebote (0-1.1 s) y un segundo toque más corto (1.6-2.3 s)
        ang = 0.0
        if t < 1.1:
            u = t / 1.1; ang = -13 * math.sin(math.pi * u) * math.exp(-1.2 * u) + 7 * math.sin(2 * math.pi * u) * u * (1 - u) * 4 * 0.4
        elif 1.6 <= t < 2.3:
            u = (t - 1.6) / 0.7; ang = 8 * math.sin(math.pi * u) * (1 - u)
        z = 1.10 + 0.10 * ease(t / dur)
        M = cv2.getRotationMatrix2D(piv, ang, z)
        M[0, 2] += (W / 2 - piv[0]) * 0.0 + (540 - piv[0]); M[1, 2] += (900 - piv[1])
        fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); print('ha ok')

# ------------------------------------------------------------------ HB
def prod_layer(ph):
    prod = Image.open(f'{G}/v2frames/producto_cut.png').convert('RGBA')
    return prod.resize((int(prod.width * ph / prod.height), ph), Image.LANCZOS)

def hb(dur=3.1):
    base = cover(f'{G}/hf/p_aerosol_0.png')
    # placa limpia: se borra el frasco (x 418-682, y 592-1602) con inpainting; luego lo tapa el producto real
    m = np.zeros((H, W), np.uint8); cv2.rectangle(m, (412, 588), (688, 1612), 255, -1)
    plate = cv2.inpaint(base, m, 9, cv2.INPAINT_TELEA)
    plate = np.where(m[..., None] > 0, cv2.GaussianBlur(plate, (0, 0), 9), plate)
    bottle_rgba = np.dstack([base, m])
    ph, basey = 820, 1598
    prod = prod_layer(ph); pw = prod.width
    px = 548 - pw // 2
    PA = np.array(prod)[:, :, [2, 1, 0, 3]].astype(np.float32)
    nf = round(dur * FPS); p = writer(f'{T}/hb.mp4', nf)
    T_STRIKE0, T_STRIKE1, T_OUT0, T_OUT1, T_DROP0, T_LAND = 0.22, 0.52, 1.00, 1.22, 1.00, 1.30
    for k in range(nf):
        t = k / FPS
        fr = plate.copy().astype(np.float32)
        # frasco + línea roja (se encogen y desvanecen al salir)
        if t < T_OUT1:
            u = ease((t - T_OUT0) / (T_OUT1 - T_OUT0)) if t >= T_OUT0 else 0.0
            sc, al = 1 - 0.35 * u, 1 - u
            lay = base.copy()
            if t >= T_STRIKE0:   # línea roja diagonal que se dibuja sobre el frasco
                v = ease((t - T_STRIKE0) / (T_STRIKE1 - T_STRIKE0))
                p0 = np.array([360, 690]); p1 = np.array([740, 1500]); pe = p0 + (p1 - p0) * v
                cv2.line(lay, (int(p0[0]), int(p0[1])), (int(pe[0]), int(pe[1])), (255, 255, 255), 64, cv2.LINE_AA)
                cv2.line(lay, (int(p0[0]), int(p0[1])), (int(pe[0]), int(pe[1])), (38, 40, 230), 44, cv2.LINE_AA)
            lm = m.copy(); cv2.line(lm, (360, 690), (740, 1500), 255, 66, cv2.LINE_AA)
            # temblor al tacharlo
            dx = 10 * math.sin(t * 70) * max(0, 1 - (t - T_STRIKE1) / 0.3) if T_STRIKE1 <= t < T_STRIKE1 + 0.3 else 0
            Mb = cv2.getRotationMatrix2D((548, 1100), 0, sc); Mb[0, 2] += dx
            lw = cv2.warpAffine(lay, Mb, (W, H), flags=cv2.INTER_LINEAR)
            mw = cv2.warpAffine(lm, Mb, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32) / 255 * al
            fr = fr * (1 - mw[..., None]) + lw.astype(np.float32) * mw[..., None]
        # producto real cae en su lugar
        if t >= T_DROP0:
            if t < T_LAND:
                u = (t - T_DROP0) / (T_LAND - T_DROP0); y_bot = -60 + (basey + 60) * u * u; sq = 1.0
            else:
                u = (t - T_LAND); y_bot = basey - 34 * math.exp(-7 * u) * abs(math.sin(u * 16)); sq = 1 - 0.05 * math.exp(-9 * u) * math.cos(u * 22)
            hh = int(ph * sq); ww = int(pw * (2 - sq))
            pa = cv2.resize(PA, (ww, hh), interpolation=cv2.INTER_AREA)
            x0 = 548 - ww // 2; y0 = int(y_bot) - hh
            # sombra de contacto: crece al acercarse al mármol
            near = max(0.0, 1 - (basey - y_bot) / 600)
            if near > 0:
                sh = np.zeros((H, W), np.float32)
                cv2.ellipse(sh, (548, basey - 6), (int(ww * 0.52), 26), 0, 0, 360, 1.0, -1)
                sh = cv2.GaussianBlur(sh, (0, 0), 14) * 0.55 * near
                fr = fr * (1 - sh[..., None]) + np.float32([28, 32, 38]) * sh[..., None]
            ya, yb = max(0, y0), min(H, y0 + hh)
            if yb > ya:
                sub = pa[ya - y0:yb - y0]
                al = sub[..., 3:4] / 255
                fr[ya:yb, x0:x0 + ww] = fr[ya:yb, x0:x0 + ww] * (1 - al) + sub[..., :3] * al
        # empujón de cámara leve todo el plano
        z = 1.0 + 0.05 * t / dur
        M = np.float32([[z, 0, -(z - 1) * 548], [0, z, -(z - 1) * 1100]])
        fr = cv2.warpAffine(np.clip(fr, 0, 255).astype(np.uint8), M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); print('hb ok')

# ------------------------------------------------------------------ B1: piedra girando sobre la palma
def b1(dur=3.8):
    base = cover(f'{G}/hf/p_palma_0.png')
    nf = round(dur * FPS); p = writer(f'{T}/b1.mp4', nf)
    piv = (560.0, 880.0)
    for k in range(nf):
        t = k / FPS; u = t / dur
        ang = -5 + 10 * ease(u)                # giro lento sobre la palma
        z = 1.08 + 0.10 * u
        M = cv2.getRotationMatrix2D(piv, ang, z); M[0, 2] += 540 - piv[0]; M[1, 2] += 900 - piv[1]
        p.stdin.write(cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).tobytes())
    p.stdin.close(); p.wait(); print('b1 ok')

# ------------------------------------------------------------------ landing + toque al botón
def land(hold=1.3):
    import json
    SCR = f'{G}/screen'
    frames = sorted(f for f in os.listdir(SCR) if f.startswith('sc_') and f.endswith('.png'))[::-1]
    btn = json.load(open(f'{SCR}/btn.json')); bx, by = btn['btnCenterX'], btn['btnCenterY'] - 90 * W / 390
    DY = 220   # la landing baja 220 px: el botón y el toque quedan fuera de la barra superior de Reels/TikTok
    def shifted(f):
        im = cover(f'{SCR}/{f}'); out = np.full_like(im, 255); out[DY:] = im[:H - DY]; return out
    seq = [shifted(f) for f in frames]; by += DY
    nf = len(seq) + round(hold * FPS); p = writer(f'{T}/land.mp4', nf)
    tap = len(seq) / FPS + 0.45
    for k in range(nf):
        t = k / FPS
        fr = seq[min(k, len(seq) - 1)].copy()
        # dedo (círculo de toque) que llega y presiona
        if t >= tap - 0.35:
            u = min(1.0, (t - tap + 0.35) / 0.35)
            cx, cy = bx + 160 * (1 - ease(u)), by + 260 * (1 - ease(u))
            ov = fr.copy()
            cv2.circle(ov, (int(cx), int(cy)), 46, (255, 255, 255), -1, cv2.LINE_AA)
            fr = cv2.addWeighted(ov, 0.55, fr, 0.45, 0)
            cv2.circle(fr, (int(cx), int(cy)), 46, (255, 255, 255), 4, cv2.LINE_AA)
            if t >= tap:
                v = min(1.0, (t - tap) / 0.45)
                ov = fr.copy(); cv2.circle(ov, (int(bx), int(by)), int(50 + 90 * v), (255, 255, 255), 10, cv2.LINE_AA)
                fr = cv2.addWeighted(ov, 1 - v, fr, v, 0)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); print('land ok', nf / FPS, 'tap', tap)

def sfx():
    o = f'{G}/audio'
    # error: dos tonos graves cuadrados
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                    "aevalsrc='0.35*sgn(sin(2*PI*(if(lt(t,0.16),330,247))*t))*exp(-2*mod(t,0.16))*lt(t,0.34)':s=48000:d=0.4",
                    '-af', 'lowpass=f=2600', f'{o}/sfx_error.wav'], check=True)
    # destello: campanita aguda con decaimiento
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                    "aevalsrc='0.22*(sin(2*PI*2637*t)+0.6*sin(2*PI*3951*t)+0.4*sin(2*PI*5274*t))*exp(-7*t)':s=48000:d=0.6",
                    f'{o}/sfx_glint.wav'], check=True)
    # golpe seco (producto que cae sobre el mármol)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                    "aevalsrc='0.8*sin(2*PI*(95-40*t)*t)*exp(-16*t)+0.25*(random(0)-0.5)*exp(-60*t)':s=48000:d=0.35",
                    f'{o}/sfx_thud.wav'], check=True)
    print('sfx ok')

if __name__ == '__main__':
    for job in sys.argv[1:] or ['ha', 'hb', 'b1', 'land', 'sfx']:
        globals()[job]()
