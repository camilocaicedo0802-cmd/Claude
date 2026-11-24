#!/usr/bin/env python3
"""GEO-TOFU-A1-02 (Demo de producto) - v2.
Planos según el prompt_visual_IA del brief, hook visible desde el fotograma 1 hasta el s3,
textos que nunca pisan caras (detección de rostros por plano) y producto real al frente en el cierre."""
import os, sys, json, subprocess, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_a102 as b
from build_a102 import (G, A, TMP, W, H, FPS, S, SCR, VO, run, dur_of, shot, screen_shot, render_runs, box_text,
                        pill, word_times, chunks, sub_img, pop_scale, paste_center, FONT_BLACK, NAVY, TEAL, YEL, WHITE, BLACK)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, cv2

HF = f'{G}/hf'
V2 = f'{G}/v2frames'
K_WOMAN = f'{HF}/s03_vid_v2_0.mp4'
CX = 520                      # centro horizontal de textos (deja 140 px libres a la derecha)
SAFE_TOP, SAFE_BOT = 250, 1250
HOOK_TEXT_UNTIL = 3.0
SHOW_SUBS = True
# filas donde el titular repite lo que dice la voz: se quita el titular y queda el subtítulo
REDUNDANT_HEADLINES = {'B1', 'B2', 'B3', 'B4', 'B5'}

HOOKS = {
    'HA': dict(vo='HA', l1='Se moja la piedra,', l2='NO la axila', line='¡Así es como sí se usa!', dur=2.4),
    'HB': dict(vo='HB', l1='3 pasos que', l2='nadie te explicó', line='Te lo enseño en quince segundos.', dur=2.4),
}
BODY = b.BODY

# ---------------------------------------------------------------- tarjeta final con producto real
def endcard_png():
    out = f'{TMP}/v2_endcard.png'
    bg = Image.new('RGB', (W, H))
    top, bot = np.array((232, 246, 245)), np.array((255, 255, 255))
    arr = np.linspace(top, bot, H).astype(np.uint8)[:, None, :].repeat(W, 1)
    bg = Image.fromarray(arr)
    prod = Image.open(f'{V2}/producto_cut.png')
    ph = 470
    prod = prod.resize((int(prod.width * ph / prod.height), ph), Image.LANCZOS)
    sh = Image.new('RGBA', (prod.width + 80, prod.height + 80), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 90), (40, 52), prod.getchannel('A'))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    px, py = CX - prod.width // 2, 660
    bg.paste(sh, (px - 40, py - 40), sh)
    bg.paste(prod, (px, py), prod)
    bg.save(out)
    return out, (px, py, px + prod.width, py + prod.height)

def build_shots():
    km, kt, ka, kto, kma = (f'{HF}/{n}_0.mp4' for n in ('k_macro', 'k_tres', 'k_abanico', 'k_toalla', 'k_mano'))
    ec, ec_box = endcard_png()
    s = {}
    s['HA'] = [shot('v2_ha', km, 2.4, ss=0.0, z0=1.0, z1=1.08)]
    s['HB'] = [shot('v2_hb', kt, 2.4, ss=0.2, z0=1.0, z1=1.06)]
    s['B1'] = [shot('v2_b1a', km, 1.6, ss=2.4, z0=1.08, z1=1.14),
               shot('v2_b1b', km, 1.65, ss=4.0, z0=1.32, z1=1.42, cy=0.4)]
    s['B2'] = [shot('v2_b2a', K_WOMAN, 2.0, ss=0.0, speed=0.62, z0=1.0, z1=1.04),
               shot('v2_b2b', K_WOMAN, 2.05, ss=1.24, speed=0.62, z0=1.18, z1=1.22, cy=0.45)]
    s['B3'] = [shot('v2_b3', ka, 1.95, ss=0.3, z0=1.0, z1=1.05)]
    s['B4'] = [shot('v2_b4a', f'{S}/hi_35928.mp4', 0.9, ss=5.0, z0=1.0, z1=1.06, cx=0.55),
               shot('v2_b4b', kto, 3.88, ss=0.0, z0=1.0, z1=1.06)]
    s['B5'] = [shot('v2_b5', kma, 2.6, ss=0.2, z0=1.0, z1=1.06)]
    s['B6'] = [screen_shot('v2_b6a', hold=1.4),
               shot('v2_b6b', f'{S}/hi_42137.mp4', 1.1, ss=2.0, z0=1.0, z1=1.06),
               shot('v2_b6c', ec, 1.5, still=True, z0=1.0, z1=1.04)]
    return s, ec_box

# ---------------------------------------------------------------- caras -> obstáculos por plano
CASC = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml'))
CASC_P = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, 'haarcascade_profileface.xml'))

def faces_in(path, d):
    boxes = []
    for fr in (0.1, 0.35, 0.6, 0.9):
        p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{d*fr:.2f}', '-i', path, '-frames:v', '1', '-vf', 'scale=540:960',
                            '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
        if len(p) < 540 * 960:
            continue
        g = np.frombuffer(p[:540 * 960], np.uint8).reshape(960, 540)
        for c in (CASC, CASC_P):
            for (x, y, w, h) in c.detectMultiScale(g, scaleFactor=1.1, minNeighbors=7, minSize=(95, 95)):
                boxes.append((x * 2, y * 2, (x + w) * 2, (y + h) * 2))
    if not boxes:
        return []
    x0, y0 = min(bx[0] for bx in boxes), min(bx[1] for bx in boxes)
    x1, y1 = max(bx[2] for bx in boxes), max(bx[3] for bx in boxes)
    # zona protegida: cara + pelo arriba + separación clara bajo el mentón
    return [(x0 - 80, y0 - 160, x1 + 80, y1 + 70)]

def overlaps(a, bx):
    return not (a[2] <= bx[0] or bx[2] <= a[0] or a[3] <= bx[1] or bx[3] <= a[1])

def place(img, slots, obstacles, avoid=()):
    """Primer centro-y de `slots` donde el elemento no pisa obstáculos (caras/producto) ni otros textos."""
    best, best_ov = slots[0], 1e9
    for y in slots:
        r = (CX - img.width / 2, y - img.height / 2, CX + img.width / 2, y + img.height / 2)
        if r[1] < SAFE_TOP or r[3] > (1560 if img.height < 140 else SAFE_BOT + 40):
            continue
        ov = sum(max(0, min(r[3], o[3]) - max(r[1], o[1])) for o in list(obstacles) + list(avoid) if overlaps(r, o))
        if ov == 0:
            return y
        if ov < best_ov:
            best, best_ov = y, ov
    return best

def rect_at(img, y):
    return (CX - img.width / 2, y - img.height / 2, CX + img.width / 2, y + img.height / 2)

# ---------------------------------------------------------------- variante
def build_variant(hk, shots, ec_box):
    hook = HOOKS[hk]
    seq = [(hk, hook['dur'])] + [(x[0], x[3]) for x in BODY]
    lst, shot_spans, t = f'{TMP}/v2_concat_{hk}.txt', [], 0.0
    with open(lst, 'w') as fh:
        for key, _ in seq:
            for f, d in shots[key]:
                fh.write(f"file '{f}'\n"); shot_spans.append((t, t + d, f)); t += d
    total = t
    base = f'{TMP}/v2_base_{hk}.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', base])
    rows, t = [], 0.0
    for key, d in seq:
        rows.append((key, t, d)); t += d
    rs = {k: s for k, s, _ in rows}
    cuts = [s for s, _, _ in shot_spans]

    # obstáculos (caras) por plano + producto en la tarjeta final / grabación de pantalla
    obst = []
    for s0, s1, f in shot_spans:
        o = faces_in(f, s1 - s0)
        if f.endswith('v2_b6c.mp4'):
            o = o + [ec_box]
        obst.append((s0, s1, o))
        print(f'  {os.path.basename(f):14s} {s0:5.2f}-{s1:5.2f}  caras/obstáculos: {o}')
    b6a0 = rs['B6']; b6a1 = b6a0 + shots['B6'][0][1]
    prod = Image.open(f'{G}/v2frames/producto_cut.png')
    prod = prod.resize((int(prod.width * 360 / prod.height), 360), Image.LANCZOS).rotate(6, expand=True, resample=Image.BICUBIC)
    prod_pos = (215, 1060)  # centro del producto real sobre la grabación de la landing
    prod_box = (prod_pos[0] - prod.width / 2, prod_pos[1] - prod.height / 2, prod_pos[0] + prod.width / 2, prod_pos[1] + prod.height / 2)

    def obst_range(t0, t1):
        res = []
        for s0, s1, o in obst:
            if s0 < t1 and t0 < s1:
                res += o
        return res

    # ---------------- audio
    vo_items = [(f'{VO}/{hook["vo"]}_t.wav', 0.02)] + [(f'{VO}/{x[0]}_t.wav', rs[x[0]] + 0.05) for x in BODY]
    whoosh, popsfx, click = f'{G}/audio/sfx_1489.mp3', f'{G}/audio/sfx_2357.mp3', f'{G}/audio/sfx_1109.mp3'
    splash, music = f'{G}/audio/splash_1180.mp3', f'{G}/audio/music_821.mp3'
    tap_t = b6a0 + 12 / FPS + 0.55
    inputs, filt, labels = [], [], []
    for i, (f, st) in enumerate(vo_items):
        inputs += ['-i', f]
        filt.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={int(st*1000)}|{int(st*1000)}[v{i}]')
        labels.append(f'[v{i}]')
    n = len(vo_items)
    filt.append(f'{"".join(labels)}amix=inputs={n}:normalize=0,pan=stereo|c0=c0|c1=c0[vo]')
    inputs += ['-i', music]; mi = n
    filt.append(f'[{mi}:a]aresample=48000,atrim=0:{total},volume=0.10,afade=t=out:st={total-0.6}:d=0.6[mus]')
    sfx, k = [], mi + 1
    def add(src, at, vol, trim=None):
        nonlocal k
        inputs.extend(['-i', src])
        tr = f'atrim=0:{trim},' if trim else ''
        filt.append(f'[{k}:a]aresample=48000,{tr}volume={vol},adelay={int(max(0,at)*1000)}|{int(max(0,at)*1000)}[s{k}]')
        sfx.append(f'[s{k}]'); k += 1
    for c in cuts[1:]:
        add(whoosh, c - 0.12, 0.22, 0.6)
    for key, st, _ in rows:
        add(popsfx, max(st, HOOK_TEXT_UNTIL) + 0.04 if key == 'B1' else st + 0.04, 0.35)
    if hk == 'HA':
        add(splash, 0.0, 0.5, 1.6)
    add(click, tap_t, 0.6, 0.5)
    filt.append(f'{"".join(sfx)}amix=inputs={len(sfx)}:normalize=0[sfx]')
    filt.append(f'[vo][mus][sfx]amix=inputs=3:normalize=0,atrim=0:{total},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]')
    audio = f'{TMP}/v2_audio_{hk}.m4a'
    run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]', '-c:a', 'aac', '-b:a', '192k', audio])

    # ---------------- textos con posición libre de caras
    els = []   # (img, cx, cy, t0, t1, pop)
    HSLOTS = [380, 470, 560, 700, 840, 980, 1070]
    # hook: dos líneas, dos colores, visible desde el fotograma 1 hasta el s3
    h1 = box_text(hook['l1'], 82, BLACK, WHITE, maxw=860, pad=(32, 16))
    h2 = box_text(hook['l2'], 104, BLACK, YEL, maxw=860, pad=(36, 18))
    blk_h = h1.height + h2.height - 6
    blk = Image.new('RGBA', (max(h1.width, h2.width), blk_h), (0, 0, 0, 0))
    blk.paste(h1, ((blk.width - h1.width) // 2, 0), h1); blk.paste(h2, ((blk.width - h2.width) // 2, h1.height - 6), h2)
    yh = place(blk, [420, 470, 560, 700, 860], obst_range(0, HOOK_TEXT_UNTIL))
    els.append((blk, CX, yh, 0.0, HOOK_TEXT_UNTIL, False))
    hook_rect = rect_at(blk, yh)
    if hk == 'HB':
        three = render_runs('3', 330, YEL, FONT_BLACK, stroke=12, stroke_color=NAVY)
        ty = place(three, [hook_rect[3] + three.height / 2 + 20, 760, 900], obst_range(0, hook['dur']), [hook_rect])
        els.append((three, 760, ty, 0.08, hook['dur'], True))
    head_rects = []  # (t0, t1, rect)
    for vo, line, txt, d in BODY:
        st = rs[vo]
        t0 = max(st, HOOK_TEXT_UNTIL) if vo == 'B1' else st
        if txt and vo not in REDUNDANT_HEADLINES:
            im = box_text(txt, 58, NAVY, WHITE, maxw=880, pad=(30, 16))
            y = place(im, HSLOTS, obst_range(t0, st + d))
            els.append((im, CX, y, t0, st + d, True)); head_rects.append((t0, st + d, rect_at(im, y)))
    # cierre: producto real al frente sobre la landing, luego CTA
    cta0 = b6a1
    cta = [(box_text('LLÉVALA HOY', 96, WHITE, NAVY, maxw=800, pad=(40, 22)), 360, 0.0),
           (box_text('Pagas al recibir', 64, NAVY, YEL, maxw=760), 492, 0.15),
           (pill('Pago contraentrega · Envío gratis 🚚', 40, WHITE, TEAL, alpha=235, pad=(26, 12)), 598, 0.3)]
    for im, y, dl in cta:
        els.append((im, CX, y, cta0 + dl, total, True)); head_rects.append((cta0, total, rect_at(im, y)))
    head_rects.append((0, HOOK_TEXT_UNTIL, hook_rect))

    # ---------------- subtítulos
    SSLOTS = [1450, 1490, 1400, 1350, 1300, 1250, 1190, 1130, 1010]  # subtítulos bien abajo
    subs = []
    lines = [(hook['line'], f'{VO}/{hook["vo"]}_t.wav', 0.02)] + [(x[1], f'{VO}/{x[0]}_t.wav', rs[x[0]] + 0.05) for x in BODY]
    for line, f, st in lines:
        for ch in chunks(word_times(line, st, dur_of(f))):
            subs.append(ch)
    sub_y_cache = {}
    def sub_y(ch, img):
        key = id(ch)
        if key not in sub_y_cache:
            t0, t1 = ch[0][1], ch[-1][2] + 0.05
            texts = [r for a, bb, r in head_rects if a < t1 and t0 < bb]
            sub_y_cache[key] = place(img, SSLOTS, obst_range(t0, t1), texts)
        return sub_y_cache[key]

    btn = json.load(open(f'{SCR}/btn.json'))
    bx, by = btn['btnCenterX'], btn['btnCenterY'] - 90 * W / 390
    ia_label = pill('Recreación con IA', 26, WHITE, (0, 0, 0), alpha=140)
    out = f'{A}/GEO_TOFU_A1_02_{hk}_DEMO_v2.mp4'
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', base, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', out],
                           stdin=subprocess.PIPE)
    fsz, fi = W * H * 3, 0
    while True:
        raw = dec.stdout.read(fsz)
        if len(raw) < fsz:
            break
        t = fi / FPS
        im = Image.frombytes('RGB', (W, H), raw)
        for img, cx, cy, t0, t1, pop in els:
            if t0 <= t < t1:
                paste_center(im, img, cx, cy, pop_scale(t, t0) if pop else 1.0)
        if tap_t - 0.05 <= t < tap_t + 0.45:
            p = (t - tap_t + 0.05) / 0.5
            d = ImageDraw.Draw(im, 'RGBA'); r = 40 + 70 * p
            d.ellipse([bx - r, by - r, bx + r, by + r], outline=(255, 255, 255, int(255 * (1 - p))), width=10)
            d.ellipse([bx - 34, by - 34, bx + 34, by + 34], fill=(255, 255, 255, int(170 * (1 - p * 0.6))))
        for ch in (subs if SHOW_SUBS and t < cta0 else []):  # con la tarjeta CTA en pantalla no se repite el subtítulo
            if ch[0][1] <= t < ch[-1][2] + 0.05:
                act = max([i for i, w in enumerate(ch) if w[1] <= t] or [0])
                si = sub_img(ch, act)
                paste_center(im, si, CX, sub_y(ch, si), pop_scale(t, ch[0][1], 0.12))
                break
        enc.stdin.write(im.tobytes()); fi += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print(out, f'{total:.2f}s', fi, 'frames')

if __name__ == '__main__':
    shots, ec_box = build_shots()
    for hk in sys.argv[1:] or ['HA', 'HB']:
        build_variant(hk, shots, ec_box)
