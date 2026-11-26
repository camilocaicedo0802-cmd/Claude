#!/usr/bin/env python3
"""A2-06 · piezas animadas en local (sin costo):
  vs   (hook B): pantalla partida roja/verde, frasco genérico (sin marca) vs piedra GEODA, 'VS' gigante que cae.
  cal  (B4): la piedra GEODA sobre la mesa y un calendario que pasa los 12 meses (ENE→DIC).
  cta3 (B10, K8): tres GEODA reales (recorte real) sobre el mesón del baño, las dos de los lados con moño rojo, + botón Comprar.
uso: mg206.py vs|cal|cta3 dur -> tmp/m6_<escena>.mp4"""
import os, sys, math, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102'); sys.path.insert(0, G)
from build_a102 import render_runs, FONT_BLACK, NAVY, TEAL, YEL, WHITE
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
W, H, FPS = 1080, 1920, 30
T = f'{G}/a206/tmp'; os.makedirs(T, exist_ok=True)
ease = lambda u: 1 - (1 - max(0, min(1, u))) ** 3
def back(u, s=1.7):
    u = max(0, min(1, u)) - 1; return 1 + (s + 1) * u ** 3 + s * u ** 2
def fill(path):   # imagen 9:16 a 1080x1920
    return Image.open(path).convert('RGB').resize((W, H), Image.LANCZOS)
def zoomed(im, z, fx=0.5, fy=0.5):
    w, h = int(W * z), int(H * z); big = im.resize((w, h), Image.LANCZOS)
    ox, oy = int((w - W) * fx), int((h - H) * fy); return big.crop((ox, oy, ox + W, oy + H))

# ------------------------------------------------------------------ VS
FR = fill(f'{G}/hf/c_b1_0.png'); PI = fill(f'{G}/hf/c_b2_0.png')
def half(src, cx, tint):
    im = src.crop((int(cx - 270), 0, int(cx + 270), H))
    return Image.blend(im, Image.new('RGB', im.size, tint), 0.22)
L_HALF = half(FR, 0.48 * W, (220, 40, 40)); R_HALF = half(PI, 0.44 * W, (40, 170, 90))
def vs_badge(r=118):
    S = 2; im = Image.new('RGBA', (2 * r * S + 20, 2 * r * S + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = r * S + 10
    d.ellipse([c - r * S, c - r * S, c + r * S, c + r * S], fill=(255, 255, 255, 255))
    d.ellipse([c - (r - 12) * S, c - (r - 12) * S, c + (r - 12) * S, c + (r - 12) * S], fill=NAVY + (255,))
    d.text((c, c + 6), 'VS', font=ImageFont.truetype(FONT_BLACK, int(r * 0.95 * S)), fill=YEL + (255,), anchor='mm')
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)
VS = vs_badge()
def pill(text, bg):
    t = render_runs(text, 54, WHITE, FONT_BLACK); w, h = t.width + 56, t.height + 26
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=bg + (240,))
    im.alpha_composite(t, (28, 13)); return im
P_L, P_R = pill('FRASCO', (200, 36, 40)), pill('PIEDRA', (24, 140, 80))
def s_vs(t, d):
    im = Image.new('RGB', (W, H), (30, 30, 30))
    u = 0.93 + 0.07 * ease(t / 0.3); z = 1.0 + 0.16 * t / d   # desde el cuadro 1 ya se ven frasco y piedra (solo terminan de entrar)
    lh = L_HALF.resize((int(540 * z), int(H * z))).crop((0, 0, 540, H)); rh = R_HALF.resize((int(540 * z), int(H * z))).crop((0, 0, 540, H))
    im.paste(lh, (int(-540 * (1 - u)), 0)); im.paste(rh, (int(540 + 540 * (1 - u)), 0))
    im = im.convert('RGBA'); dd = ImageDraw.Draw(im); dd.line([(540, 0), (540, H)], fill=(255, 255, 255, 255), width=10)
    v = (t - 0.35) / 0.25
    if v > 0:
        sc = 2.2 - 1.2 * ease(v) if v < 1 else 1 + 0.07 * math.sin(t * 7)
        dx = 10 * math.sin((t - 0.6) * 60) * math.exp(-8 * max(0, t - 0.6)) if t > 0.6 else 0
        b = VS.resize((int(VS.width * sc), int(VS.height * sc)), Image.LANCZOS); im.alpha_composite(b, (int(540 - b.width / 2 + dx), int(615 - b.height / 2)))
    w2 = (t - 0.7) / 0.3
    if w2 > 0:
        a = ease(w2); y = int(1185 + 40 * (1 - a))
        im.alpha_composite(P_L, (int(270 - P_L.width / 2), y)); im.alpha_composite(P_R, (int(810 - P_R.width / 2), y))
    return im.convert('RGB')

# ------------------------------------------------------------------ calendario 12 meses
MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
def card(mes, k):
    im = Image.new('RGBA', (270, 280), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 8, 270, 280], 30, fill=(0, 0, 0, 45))
    d.rounded_rectangle([0, 0, 270, 270], 30, fill=(255, 255, 255, 255), outline=(215, 215, 210, 255), width=3)
    d.rounded_rectangle([0, 0, 270, 76], 30, fill=TEAL + (255,)); d.rectangle([0, 40, 270, 76], fill=TEAL + (255,))
    d.text((135, 40), 'MES', font=ImageFont.truetype(FONT_BLACK, 40), fill=(255, 255, 255, 255), anchor='mm')
    d.text((135, 168), mes, font=ImageFont.truetype(FONT_BLACK, 104), fill=NAVY + (255,), anchor='mm')
    d.text((135, 243), f'{k}/12', font=ImageFont.truetype(FONT_BLACK, 34), fill=(150, 150, 150, 255), anchor='mm')
    return im
def s_cal(t, d):
    im = zoomed(PI, 1.0 + 0.2 * t / d, 0.45, 0.62).convert('RGBA')
    step = max(0.12, (d - 0.5) / 12); k = min(11, int(t / step)); f = (t / step) % 1 if k < 11 else 1
    c = card(MESES[k], k + 1); sc = 1 - 0.3 * math.sin(math.pi * min(1, f / 0.4)) if k < 11 else 1 + 0.08 * math.sin(t * 6)
    c = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
    im.alpha_composite(c, (int(800 - c.width / 2), int(590 - c.height / 2)))
    return im.convert('RGB')

# ------------------------------------------------------------------ cierre K8: tres piedras reales, dos con moño
BG = fill(f'{KIT}/fondos/p_banofondo_0.png')
STICK = Image.open(f'{KIT}/producto/producto_cut.png').convert('RGBA').crop((0, 0, 253, 603))
BOW = Image.open(f'{KIT}/producto/mono_rojo.png').convert('RGBA')
def stick(h):
    s = STICK.resize((int(STICK.width * h / STICK.height), h), Image.LANCZOS)
    sh = Image.new('RGBA', (s.width + 60, s.height + 60), (0, 0, 0, 0)); sh.paste((0, 0, 0, 80), (30, 42), s.getchannel('A')); sh = sh.filter(ImageFilter.GaussianBlur(12))
    out = Image.new('RGBA', sh.size, (0, 0, 0, 0)); out.alpha_composite(sh); out.alpha_composite(s, (30, 30)); return out
S_C, S_S = stick(600), stick(460)
def button(scale):
    w, h = int(420 * scale), int(112 * scale); S = 2
    im = Image.new('RGBA', (w * S + 40, h * S + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 26, 20 + w * S, 26 + h * S], h * S // 2, fill=(0, 0, 0, 60))
    d.rounded_rectangle([20, 14, 20 + w * S, 14 + h * S], h * S // 2, fill=(18, 160, 140, 255))
    tx = render_runs('Comprar', int(60 * scale * S), WHITE, FONT_BLACK); im.alpha_composite(tx, (20 + (w * S - tx.width) // 2, 14 + (h * S - tx.height) // 2))
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)
HAND = render_runs('👆', 110, WHITE, FONT_BLACK)
BASE = 1430   # apoyadas más arriba: fuera de la zona de la descripción de TikTok
def s_cta3(t, d):
    im = zoomed(BG, 1.0 + 0.14 * t / d, 0.5, 0.75).convert('RGBA')
    for side, x0 in ((-1, 245), (1, 835)):   # las de regalo entran desde los lados ("de mano en mano") y quedan detrás
        u = ease((t - (0.15 if side < 0 else 0.45)) / 0.45)
        if u <= 0: continue
        x = x0 + side * 520 * (1 - u); y = BASE - S_S.height + 30 + 10 * math.sin(t * 3.2 + side)
        im.alpha_composite(S_S, (int(x - S_S.width / 2), int(y)))
        v = (t - (0.6 if side < 0 else 0.9)) / 0.3
        if v > 0:
            sc = back(v) if v < 1 else 1; b = BOW.resize((max(1, int(150 * sc)), max(1, int(134 * sc))), Image.LANCZOS)
            im.alpha_composite(b, (int(x - b.width / 2 + side * 20), int(y + 120 - b.height / 2)))
    im.alpha_composite(S_C, (int(540 - S_C.width / 2), int(BASE - S_C.height + 30 + 8 * math.sin(t * 2.6))))
    sw = (t * 0.55) % 1.6   # barrido de luz que cruza el cuadro
    if sw < 1:
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x = -300 + sw * (W + 600)
        ImageDraw.Draw(ov).polygon([(x, 0), (x + 160, 0), (x - 340, H), (x - 500, H)], fill=(255, 255, 255, 46)); im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(30)))
    u = (t - 1.2) / 0.35
    if u > 0:
        sc = min(1, 0.3 + 0.7 * ease(u)) * (1 + 0.035 * math.sin(t * 6))
        for tap in (2.2, 3.6):
            v = t - tap
            if 0 <= v < 0.25: sc *= 1 - 0.08 * math.sin(math.pi * v / 0.25)
        b = button(sc); bx, by = 540, 700; im.alpha_composite(b, (int(bx - b.width / 2), int(by - b.height / 2)))
        for tap in (2.2, 3.6):
            v = t - tap
            if -0.45 <= v < 0.6: im.alpha_composite(HAND, (int(bx + 80), int(by + 30 + max(0, -v) * 240)))
    return im.convert('RGB')

SC = dict(vs=s_vs, cal=s_cal, cta3=s_cta3)
if __name__ == '__main__':
    name, dur = sys.argv[1], float(sys.argv[2]); n = round(dur * FPS); out = f'{T}/m6_{name}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(n): p.stdin.write(SC[name](k / FPS, dur).tobytes())
    p.stdin.close(); p.wait(); print('ok', out, dur)
