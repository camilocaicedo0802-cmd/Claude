#!/usr/bin/env python3
"""Planos propios del A1-06 (POV).
ha   : cajón empolvado; se sopla el polvo de la piedra hacia la cámara (partículas que crecen y se van) + cámara en mano.
b8   : producto REAL (recorte de la landing) seco sobre el lavamanos (tools/endcard_real.py).
cta  : estante casi vacío con 3 unidades REALES (solo el tubo del recorte) -> 'últimas unidades'.
sfx  : ducha (ruido rosa filtrado), bus (rumor grave) y soplido."""
import os, sys, math, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageFilter, ImageDraw
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102')
from motion_v3 import cover, writer, ease
A = f'{G}/a106'; T = f'{A}/tmp'; os.makedirs(T, exist_ok=True)
W, H, FPS = 1080, 1920, 30

def ha(dur=3.1):
    base = cover(f'{G}/hf/j_cajon_0.png').astype(np.float32)
    rnd = random.Random(3)
    # partículas: salen de la piedra (555,740) y del borde del cajón, vuelan hacia la cámara (crecen, se desenfocan, se van)
    P = []
    for _ in range(260):
        ox, oy = rnd.gauss(555, 70), rnd.gauss(760, 45)
        ang = rnd.uniform(0, 2 * math.pi); sp = rnd.uniform(250, 900)
        P.append((ox, oy, math.cos(ang) * sp, math.sin(ang) * sp * 0.8 - 120, rnd.uniform(0.25, 0.55), rnd.uniform(1.5, 5.5), rnd.uniform(0.5, 1.0)))
    nf = round(dur * FPS); p = writer(f'{T}/ha.mp4', nf)
    for k in range(nf):
        t = k / FPS
        z = 1.04 + 0.05 * ease(t / dur)
        sx = 6 * math.sin(t * 7.1) + 3 * math.sin(t * 13.3); sy = 5 * math.cos(t * 6.3)
        M = np.float32([[z, 0, -(z - 1) * 555 + sx], [0, z, -(z - 1) * 760 + sy]])
        fr = cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        lay = np.zeros((H, W), np.float32)
        for ox, oy, vx, vy, t0, r0, a0 in P:
            u = t - t0
            if u <= 0 or u > 1.6:
                continue
            g = 1 + 2.2 * u                                   # se acerca a la cámara: se separa del centro y crece
            x = 540 + (ox - 540) * g + vx * u; y = 900 + (oy - 900) * g + vy * u
            r = r0 * (1 + 5 * u); al = a0 * min(1, u * 6) * max(0, 1 - u / 1.6)
            if -50 < x < W + 50 and -50 < y < H + 50:
                cv2.circle(lay, (int(x), int(y)), max(1, int(r)), al, -1, cv2.LINE_AA)
        haze = np.zeros((H, W), np.float32)
        if 0.22 < t < 1.9:                                    # nube suave del soplido
            u = (t - 0.22) / 1.68
            cv2.ellipse(haze, (555, int(760 - 120 * u)), (int(120 + 520 * u), int(80 + 380 * u)), 0, 0, 360, (1 - u) * 0.38, -1)
            haze = cv2.GaussianBlur(haze, (0, 0), 60)
        lay = cv2.GaussianBlur(lay, (0, 0), 1.6) + haze
        col = np.float32([170, 190, 205])                      # polvo gris cálido iluminado por la ventana (BGR)
        fr = fr * (1 - np.clip(lay, 0, 0.9)[..., None]) + col * np.clip(lay, 0, 0.9)[..., None]
        p.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait(); print('ha ok')

def b8():
    r = subprocess.run(['python3', f'{G}/tools/endcard_real.py', f'{G}/hf/j_lavamanos_0.png', f'{T}/b8_lavamanos.png', '400', '1430'],
                       capture_output=True, text=True); print(r.stdout.strip(), r.stderr[-300:])

def cta():
    bg = cover(f'{G}/hf/j_estante_0.png')[:, :, ::-1]
    comp = Image.fromarray(bg.copy()).convert('RGBA')
    prod = Image.open(f'{G}/v2frames/producto_cut.png').convert('RGBA')
    tube = prod.crop((0, 0, 262, prod.height))               # solo el tubo (sin la tapa al lado)
    a = np.array(tube.getchannel('A')); a[:, 252:] = (a[:, 252:] * np.linspace(1, 0, a.shape[1] - 252)[None, :]).astype(np.uint8)
    tube.putalpha(Image.fromarray(a)); tube = tube.crop(tube.getbbox())
    ph, base = 430, 1236
    t = tube.resize((int(tube.width * ph / tube.height), ph), Image.LANCZOS)
    boxes = []
    for cx in (330, 560, 820):
        x0 = cx - t.width // 2; y0 = base - ph
        sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse([x0 + 8, base - 16, x0 + t.width - 8, base + 12], fill=150)
        sh = sh.filter(ImageFilter.GaussianBlur(9))
        dark = Image.new('RGBA', (W, H), (40, 34, 30, 255)); dark.putalpha(sh); comp = Image.alpha_composite(comp, dark)
        comp.alpha_composite(t, (x0, y0)); boxes.append((x0, y0, x0 + t.width, base))
    comp.convert('RGB').save(f'{T}/cta_estante.png', quality=95)
    print('cta ok', boxes)

def sfx():
    o = f'{G}/audio'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anoisesrc=color=pink:duration=3.2:amplitude=0.5',
                    '-af', 'highpass=f=700,lowpass=f=7000,afade=t=in:d=0.3,afade=t=out:st=2.6:d=0.6,volume=0.5', f'{o}/amb_ducha.wav'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anoisesrc=color=brown:duration=3.0:amplitude=0.9',
                    '-af', 'lowpass=f=260,tremolo=f=1.3:d=0.35,afade=t=in:d=0.2,afade=t=out:st=2.5:d=0.5,volume=1.2', f'{o}/amb_bus.wav'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anoisesrc=color=white:duration=0.9:amplitude=0.6',
                    '-af', 'bandpass=f=1400:w=1800,afade=t=in:d=0.08,afade=t=out:st=0.25:d=0.65,volume=0.6', f'{o}/sfx_soplo.wav'], check=True)
    print('sfx ok')

if __name__ == '__main__':
    for job in sys.argv[1:] or ['ha', 'b8', 'cta', 'sfx']:
        globals()[job]()
