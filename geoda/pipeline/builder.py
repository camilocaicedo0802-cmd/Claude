#!/usr/bin/env python3
"""Montador genérico de los videos GEODA (9:16, 1080x1920, 30 fps).
Reglas del cliente:
- Ningún texto pisa una cara: cada plano se analiza con detector de rostros y los textos se ubican en zonas libres,
  con margen (pelo arriba, separación clara bajo el mentón).
- No se repiten textos: si el titular de una fila dice lo mismo que la voz, se quita el titular (queda el subtítulo);
  en hooks redundantes queda el texto del hook sin subtítulo; con la tarjeta CTA en pantalla no hay subtítulo.
- Hook visible desde el fotograma 1 hasta HOOK_TEXT_UNTIL.
"""
import os, sys, json, subprocess, math, re
import os  # carpeta de trabajo: GEODA_WORK o ~/.geoda_work (la crea setup_work.sh)
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, f'{G}/a102'); sys.path.insert(0, G)
import build_a102 as b
from build_a102 import (W, H, FPS, run, dur_of, render_runs, box_text, pill, word_times, chunks, sub_img, pop_scale,
                        paste_center, screen_shot, FONT_BLACK, NAVY, TEAL, YEL, WHITE, BLACK)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, cv2

CX = 520
# Zona segura del brief (Meta Reels y TikTok): libres ~250 px arriba, ~670 px abajo y ~140 px a la derecha.
SAFE_TOP, SAFE_BOT, SAFE_RIGHT = 250, 1920 - 670, 1080 - 140
SUB_SLOTS = [1190, 1150, 1100, 1040, 980, 920, 860, 800, 740, 680, 620, 560, 500, 440]  # lo más abajo posible dentro de la zona segura
PILL_CIERRE = 'Pago contraentrega · Envío gratis'   # brief: los últimos 2-3 s llevan este texto
RED = (230, 40, 40)
CASC = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml'))
CASC_P = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, 'haarcascade_profileface.xml'))

# ------------------------------------------------------------------ planos
def shot(tmp, name, src, dur, ss=0.0, speed=1.0, z0=1.0, z1=1.0, fx=0.5, fy=0.5, still=False, sharpen=False, framed=None, stopmo=False, audio=False, shake=None):
    """fx,fy: punto hacia el que se hace zoom (0-1). framed: escala (<1) del video dentro de un fondo desenfocado,
    alineado abajo, para dejar aire arriba para el texto sin tapar la cara."""
    out = f'{tmp}/{name}.mp4'
    nf = round(dur * FPS)
    if still:
        inp = ['-loop', '1', '-framerate', str(FPS), '-t', f'{dur + 0.5}', '-i', src]; pre = []
    else:
        inp = ['-ss', f'{ss}', '-t', f'{dur * speed + 0.3}', '-i', src]
        pre = [f'setpts=(PTS-STARTPTS)/{speed}', f'fps={FPS}']
    post = []
    if sharpen:
        post.append('unsharp=5:5:0.8:5:5:0.0')
    b.kb_render(out, inp, pre, nf, z0, z1, fx=fx, fy=fy, post=post, framed=framed, stopmo=stopmo, shake=shake)  # zoom subpíxel (sin saltos)
    if audio:  # voz/ambiente del propio clip (Veo), mismo tramo
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{ss}', '-t', f'{dur}', '-i', src, '-vn', '-ac', '1', '-ar', '48000',
             '-af', f'apad=whole_dur={dur}', out.replace('.mp4', '.wav')])
    return out, dur

def endcard(tmp):
    out = f'{tmp}/endcard.png'
    arr = np.linspace(np.array((232, 246, 245)), np.array((255, 255, 255)), H).astype(np.uint8)[:, None, :].repeat(W, 1)
    bg = Image.fromarray(arr)
    prod = Image.open(f'{G}/v2frames/producto_cut.png')
    ph = 470
    prod = prod.resize((int(prod.width * ph / prod.height), ph), Image.LANCZOS)
    sh = Image.new('RGBA', (prod.width + 80, prod.height + 80), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 90), (40, 52), prod.getchannel('A')); sh = sh.filter(ImageFilter.GaussianBlur(18))
    px, py = CX - prod.width // 2, 660
    bg.paste(sh, (px - 40, py - 40), sh); bg.paste(prod, (px, py), prod)
    bg.save(out)
    return out, (px, py, px + prod.width, py + prod.height)

# ------------------------------------------------------------------ caras
def faces_in(path, d, min_face=95):
    boxes = []
    for fr in (0.1, 0.35, 0.6, 0.9):
        p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{d*fr:.2f}', '-i', path, '-frames:v', '1', '-vf', 'scale=540:960',
                            '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
        if len(p) < 540 * 960:
            continue
        g = np.frombuffer(p[:540 * 960], np.uint8).reshape(960, 540)
        for c in (CASC, CASC_P):
            for (x, y, w, h) in c.detectMultiScale(g, scaleFactor=1.1, minNeighbors=7, minSize=(min_face, min_face)):
                boxes.append((x * 2, y * 2, (x + w) * 2, (y + h) * 2))
    if not boxes:
        return []
    x0, y0 = min(q[0] for q in boxes), min(q[1] for q in boxes)
    x1, y1 = max(q[2] for q in boxes), max(q[3] for q in boxes)
    return [(int(x0) - 80, int(y0) - 160, int(x1) + 80, int(y1) + 70)]

def label_boxes(path, d, margin=40):
    """Zona de la etiqueta del producto en el plano (SIFT contra la etiqueta real): los textos no la tapan."""
    import label_fix as LF
    qs = []
    for fr in (0.15, 0.5, 0.85):
        p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{d*fr:.2f}', '-i', path, '-frames:v', '1', '-f', 'rawvideo',
                            '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
        if len(p) < 1080 * 1920 * 3:
            continue
        f = np.frombuffer(p[:1080 * 1920 * 3], np.uint8).reshape(1920, 1080, 3)
        q = LF.sift_quad(cv2.resize(f, (540, 960)))
        if q is not None:
            qs.append(q * 2)
    if not qs:
        return []
    allq = np.concatenate(qs)
    x0, y0 = allq.min(0); x1, y1 = allq.max(0)
    return [(int(x0) - margin, int(y0) - margin, int(x1) + margin, int(y1) + margin)]

def protect(box):
    """Caja de cara manual (x0,y0,x1,y1 en 1080x1920) -> zona protegida con los mismos márgenes."""
    x0, y0, x1, y1 = box
    return (x0 - 80, y0 - 160, x1 + 80, y1 + 70)

def speech_span(wav):
    """Inicio y fin de la voz en un clip (detección de silencios)."""
    out = subprocess.run(['ffmpeg', '-i', wav, '-af', 'silencedetect=noise=-30dB:d=0.25', '-f', 'null', '-'], capture_output=True, text=True).stderr
    d = dur_of(wav)
    starts = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', out)]
    ends = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', out)]
    a0 = ends[0] if starts and starts[0] < 0.05 and ends else 0.0
    a1 = starts[-1] if starts and (not ends or starts[-1] > ends[-1]) else d
    return a0, max(a1, a0 + 0.5)

def overlaps(a, q):
    return not (a[2] <= q[0] or q[2] <= a[0] or a[3] <= q[1] or q[3] <= a[1])

def rect_at(img, y, cx=CX):
    return (cx - img.width / 2, y - img.height / 2, cx + img.width / 2, y + img.height / 2)

def place(img, slots, obstacles, avoid=(), cx=CX, bot=SAFE_BOT):
    best, best_ov = slots[0], 1e9
    for y in slots:
        r = rect_at(img, y, cx)
        if r[1] < SAFE_TOP or r[3] > min(bot, SAFE_BOT):
            continue   # (antes también descartaba por ancho: un bloque más ancho que la zona segura caía SIEMPRE en el primer hueco, encima de las caras)
        ov = sum(max(0, min(r[3], o[3]) - max(r[1], o[1])) for o in list(obstacles) + list(avoid) if overlaps(r, o))
        if ov == 0:
            return y
        if ov < best_ov:
            best, best_ov = y, ov
    return best

def ia_label(text='Recreación con IA', size=26):
    from PIL import ImageFont
    f = ImageFont.truetype(FONT_BLACK, size)
    tw = int(f.getlength(text)); pw, ph = tw + 28, size + 18
    im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=ph // 2, fill=(0, 0, 0, 120))
    d.text((pw / 2, ph / 2), text, font=f, fill=(255, 255, 255, 235), anchor='mm')
    return im

def stamp(text, size=130, angle=-14, color=(214, 32, 38)):
    """Sello de goma (ej. MITO): texto con borde doble, textura gastada, girado."""
    from PIL import ImageFont
    f = ImageFont.truetype(FONT_BLACK, size)
    tw = int(f.getlength(text)); th = int(size * 0.78)
    pw, ph = tw + 2 * int(size * 0.42), th + 2 * int(size * 0.36)
    im = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lw = max(6, size // 14)
    d.rounded_rectangle([lw, lw, pw - lw, ph - lw], radius=size // 5, outline=color + (255,), width=lw)
    d.rounded_rectangle([3 * lw, 3 * lw, pw - 3 * lw, ph - 3 * lw], radius=size // 7, outline=color + (255,), width=max(2, lw // 2))
    d.text((pw / 2, ph / 2), text, font=f, fill=color + (255,), anchor='mm')
    rng = np.random.default_rng(3)
    a = np.array(im.getchannel('A')).astype(np.float32)
    a *= np.clip(0.7 + 0.5 * rng.random(a.shape), 0, 1) ** 1.5      # tinta gastada
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im.rotate(angle, resample=Image.BICUBIC, expand=True)

def slam_scale(t, t0, d=0.14):
    x = (t - t0) / d
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return 1.0 + 0.9 * (1 - x) ** 2

def big_x(size=380, width=46):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    m = width
    for (a, bb) in (((m, m), (size - m, size - m)), ((size - m, m), (m, size - m))):
        d.line([a, bb], fill=(255, 255, 255, 255), width=width + 16)
    for (a, bb) in (((m, m), (size - m, size - m)), ((size - m, m), (m, size - m))):
        d.line([a, bb], fill=RED + (255,), width=width)
    return im

def fit(text, size, maxw, pad):
    """Mayor tamaño (<= size) con el que el texto cabe en una sola línea."""
    f = b.font(FONT_BLACK, size)
    while size > 40 and f.getlength(text) > maxw - 2 * pad[0] - 4:
        size -= 2; f = b.font(FONT_BLACK, size)
    return size

def hook_block(l1, l2, maxw=840):   # 840 = ancho de la zona segura con el centro en CX (520 ± 420 ≤ 940)
    # la línea blanca no baja de 64 px: si no cabe, se parte en dos renglones dentro del mismo recuadro
    # maxw < 860: bloque más angosto para ponerlo a un lado (ej. junto a una cara o la piedra)
    h1 = box_text(l1, max(56 if maxw < 840 else 64, fit(l1, 80, maxw, (32, 16))), BLACK, WHITE, maxw=maxw, pad=(32, 16))
    h2 = box_text(l2, max(56 if maxw < 840 else 0, fit(l2, 98, maxw, (36, 18))), BLACK, YEL, maxw=maxw, pad=(36, 18))
    blk = Image.new('RGBA', (max(h1.width, h2.width), h1.height + h2.height - 6), (0, 0, 0, 0))
    blk.paste(h1, ((blk.width - h1.width) // 2, 0), h1); blk.paste(h2, ((blk.width - h2.width) // 2, h1.height - 6), h2)
    return blk

# ------------------------------------------------------------------ montaje
def build(cfg, hk, shots):
    tmp = cfg['tmp']
    hook = cfg['hooks'][hk]
    rows_cfg = [dict(key=hk, **hook)] + cfg['body']
    lst, spans, t = f'{tmp}/concat_{hk}.txt', [], 0.0
    with open(lst, 'w') as fh:
        for r in rows_cfg:
            for item in shots[r['key']]:
                f, d = item[0], item[1]
                fh.write(f"file '{f}'\n"); spans.append(dict(t0=t, t1=t + d, f=f, faces=item[2] if len(item) > 2 else None)); t += d
    total = t
    base = f'{tmp}/base_{hk}.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', base])
    rs, t = {}, 0.0
    for r in rows_cfg:
        rs[r['key']] = t; t += r['dur']
    cuts = [s['t0'] for s in spans]

    obst = []
    for s in spans:
        o = s['faces'] if s['faces'] is not None else faces_in(s['f'], s['t1'] - s['t0'], cfg.get('min_face', 95))
        o = o + label_boxes(s['f'], s['t1'] - s['t0'])  # la etiqueta del producto tampoco se tapa
        obst.append((s['t0'], s['t1'], o))
        print(f"  {os.path.basename(s['f']):16s} {s['t0']:5.2f}-{s['t1']:5.2f} caras: {o}")
    def obst_range(a, bb):
        res = []
        for t0, t1, o in obst:
            if t0 < bb and a < t1:
                res += o
        return res

    # ---------------- audio
    VOD = cfg['vo_dir']
    vo_items = []
    for r in rows_cfg:
        if r.get('clip_audio'):
            t = rs[r['key']]
            for item in shots[r['key']]:
                w = item[0].replace('.mp4', '.wav')
                if os.path.exists(w):
                    vo_items.append((w, t))
                t += item[1]
        else:
            vo_items.append((f"{VOD}/{r['vo']}_t.wav", rs[r['key']] + (0.02 if r['key'] == hk else 0.05)))
    A = f'{G}/audio'
    inputs, filt, labels = [], [], []
    for i, (f, st) in enumerate(vo_items):
        inputs += ['-i', f]
        filt.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={int(st*1000)}|{int(st*1000)}[v{i}]'); labels.append(f'[v{i}]')
    n = len(vo_items)
    filt.append(f'{"".join(labels)}amix=inputs={n}:normalize=0,pan=stereo|c0=c0|c1=c0[vo]')
    inputs += ['-i', cfg.get('music', f'{A}/music_821.mp3')]; mi = n
    filt.append(f'[{mi}:a]aresample=48000,atrim=0:{total},volume={cfg.get("music_vol", 0.10)},afade=t=out:st={total-0.6}:d=0.6[mus]')
    sfx, k = [], mi + 1
    def add(src, at, vol, trim=None):
        nonlocal k
        inputs.extend(['-i', src]); tr = f'atrim=0:{trim},' if trim else ''
        filt.append(f'[{k}:a]aresample=48000,{tr}volume={vol},adelay={int(max(0,at)*1000)}|{int(max(0,at)*1000)}[s{k}]')
        sfx.append(f'[s{k}]'); k += 1
    if cfg.get('cut_sfx', True):
        for c in cuts[1:]:
            add(f'{A}/sfx_1489.mp3', c - 0.12, cfg.get('cut_sfx_vol', 0.22), 0.6)
    for r in rows_cfg:  # efectos por fila: (segundos desde el inicio de la fila, archivo, volumen)
        for off, src, vol in r.get('sfx', []):
            add(src, rs[r['key']] + off, vol)
    for at, src, vol in cfg.get('sfx', {}).get(hk, []) + cfg.get('sfx', {}).get('body', []):
        add(src, at if at >= 0 else rs[cfg['body'][0]['key']] + (-at), vol)
    filt.append(f'{"".join(sfx)}amix=inputs={len(sfx)}:normalize=0[sfx]')
    filt.append(f'[vo][mus][sfx]amix=inputs=3:normalize=0,atrim=0:{total},apad=pad_dur=1.5,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,alimiter=limit=0.84:level=false,atrim=0:{total}[out]')   # el relleno evita el pico de loudnorm al final
    audio = f'{tmp}/audio_{hk}.m4a'
    run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]', '-c:a', 'aac', '-b:a', '192k', audio])

    # ---------------- elementos visuales
    HU = cfg.get('hook_text_until', 3.0)
    els, text_rects = [], []
    blk = hook_block(*hook['text'], maxw=hook.get('hook_maxw', 860))
    HCX = hook.get('hook_cx', CX)   # centro horizontal del texto del hook
    hd = hook['dur']
    IA_RECT = None
    if cfg.get('ai_label'):   # espacio reservado del rótulo IA (nada se pone encima)
        _ia = ia_label(); IA_RECT = (48, SAFE_BOT - 8 - _ia.height, 48 + _ia.width, SAFE_BOT - 8)   # esquina inferior izquierda
        text_rects.append((0, total, (IA_RECT[0] - 10, IA_RECT[1] - 10, IA_RECT[2] + 10, IA_RECT[3] + 12)))
    yh = place(blk, hook.get('hook_slots', cfg.get('hook_slots', [360, 420, 470, 560, 700, 860, 1000, 1100])), obst_range(0, hd),
               [q for a, bb, q in text_rects], cx=HCX)
    # el texto del hook sigue hasta HU solo si no pisa caras del plano siguiente
    hook_end = HU if not any(overlaps(rect_at(blk, yh, HCX), o) for o in obst_range(hd, HU)) else hd
    els.append((blk, HCX, yh, 0.0, hook_end, False)); text_rects.append((0, hook_end, rect_at(blk, yh, HCX)))
    HU = hook_end
    for ex in hook.get('extras', []):
        if ex['type'] == 'bigx':
            im = big_x(ex.get('size', 380))
        elif ex['type'] == 'three':
            im = render_runs('3', 330, YEL, FONT_BLACK, stroke=12, stroke_color=NAVY)
        elif ex['type'] == 'text':
            im = render_runs(ex['text'], ex.get('size', 200), tuple(ex.get('color', RED)), FONT_BLACK, stroke=ex.get('stroke', 10),
                             stroke_color=tuple(ex.get('stroke_color', WHITE)))
        elif ex['type'] == 'img':   # gráfico PNG con alfa (ej. reloj gigante)
            im = Image.open(ex['path']).convert('RGBA')
        elif ex['type'] == 'stamp':
            im = stamp(ex['text'], ex.get('size', 130), ex.get('angle', -14))
        els.append((im, ex['x'], ex['y'], ex.get('t0', 0.08), ex.get('t1', hook['dur']), 'slam' if ex['type'] == 'stamp' else ex.get('pop', True)))
        text_rects.append((ex.get('t0', 0.08), ex.get('t1', hook['dur']), rect_at(im, ex['y'], ex['x'])))  # los subtítulos no tapan gráficos clave
    for r in cfg['body']:
        st = rs[r['key']]; t0 = max(st, HU) if r is cfg['body'][0] else st; t1 = st + r['dur']
        if r.get('head'):
            im = box_text(r['head'], 58, NAVY, WHITE, maxw=880, pad=(30, 16))
            y = place(im, [380, 470, 560, 700, 840, 980, 1070], obst_range(t0, t1), [q for a, bb, q in text_rects if a < t1 and t0 < bb])
            els.append((im, CX, y, t0, t1, True)); text_rects.append((t0, t1, rect_at(im, y)))
        if r.get('big'):   # número de paso grande (amarillo con borde azul), no repite la voz
            im = render_runs(r['big'], r.get('big_size', 300), YEL, FONT_BLACK, stroke=12, stroke_color=NAVY)
            ix = r.get('icon_x', 790)
            y = place(im, [440, 560, 700, 840, 980, 1100], obst_range(t0, t1), [q for a, bb, q in text_rects if a < t1 and t0 < bb], cx=ix)
            els.append((im, ix, y, t0 + 0.05, t1, 'slam')); text_rects.append((t0, t1, rect_at(im, y, ix)))
        if r.get('icon'):
            im = render_runs(r['icon'], 200, WHITE, FONT_BLACK)
            ix = r.get('icon_x', 820)
            y = place(im, [420, 560, 700, 840, 980, 1100], obst_range(t0, t1), [q for a, bb, q in text_rects if a < t1 and t0 < bb], cx=ix)
            els.append((im, ix, y, t0 + 0.05, t1, True)); text_rects.append((t0, t1, rect_at(im, y, ix)))
    cta = cfg['cta']; cta0 = rs[cta['row']] + cta.get('delay', 0.0)
    ys = [360, 492, 598]
    stack = [box_text(cta['l1'], fit(cta['l1'], 92, 860, (40, 22)), WHITE, NAVY, maxw=860, pad=(40, 22)),
             box_text(cta['l2'], fit(cta['l2'], 64, 800, (34, 20)), NAVY, YEL, maxw=800),
             pill(cta.get('pill', PILL_CIERRE), 40, WHITE, TEAL, alpha=235, pad=(26, 12))]
    for i, (im, y) in enumerate(zip(stack, ys)):
        els.append((im, CX, y, cta0 + 0.15 * i, total, True)); text_rects.append((cta0, total, rect_at(im, y)))

    subs = []
    for r in rows_cfg:
        if not r.get('subs', True):
            continue
        if r.get('words'):  # [(palabra, inicio, fin)] relativos al inicio de la fila
            subs += chunks([(re.sub(r'[,:.]$', '', wd), rs[r['key']] + a, rs[r['key']] + e) for wd, a, e in r['words']])
            continue
        if r.get('clip_audio'):
            w = shots[r['key']][r.get('speech_shot', 0)][0].replace('.mp4', '.wav')
            off = sum(it[1] for it in shots[r['key']][:r.get('speech_shot', 0)])
            a0, a1 = speech_span(w)
            subs += chunks(word_times(r['line'], rs[r['key']] + off + a0, a1 - a0))
            continue
        f = f"{VOD}/{r['vo']}_t.wav"; st = rs[r['key']] + (0.02 if r['key'] == hk else 0.05)
        subs += chunks(word_times(r['line'], st, dur_of(f)))
    sub_y, sub_x = {}, {}
    def sy(ch, img):
        if id(ch) not in sub_y:
            t0, t1 = ch[0][1], ch[-1][2] + 0.05
            fixed = [r.get('sub_y') for r in rows_cfg if r.get('sub_y') and rs[r['key']] <= t0 < rs[r['key']] + r['dur']]
            row = [r for r in rows_cfg if rs[r['key']] <= t0 < rs[r['key']] + r['dur']]
            sub_x[id(ch)] = (row[0].get('sub_cx', CX), row[0].get('sub_scale', 1.0)) if row else (CX, 1.0)
            if fixed:   # posición fija del subtítulo en esta fila (ej. bajo la etiqueta, sin tapar la piedra)
                sub_y[id(ch)] = fixed[0]; return fixed[0]
            sub_y[id(ch)] = place(img, SUB_SLOTS, obst_range(t0, t1), [q for a, bb, q in text_rects if a < t1 and t0 < bb])
        return sub_y[id(ch)]

    # rótulo 'Recreación con IA' (brief): pequeño, esquina superior izquierda dentro de la zona segura, en avatares,
    # entrevistas, podcast y testimonios generados; todo el video
    ia = ia_label() if cfg.get('ai_label') else None
    ia_until = cta0   # en la tarjeta final solo va el producto real
    out = f"{cfg['out_dir']}/{cfg['id']}_{hk}_{cfg['fmt']}_v{cfg.get('version', 1)}.mp4"
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
                paste_center(im, img, cx, cy, slam_scale(t, t0) if pop == 'slam' else (pop_scale(t, t0) if pop else 1.0))
        if t < cta0:
            for ch in subs:
                if ch[0][1] <= t < ch[-1][2] + 0.05:
                    act = max([i for i, w in enumerate(ch) if w[1] <= t] or [0])
                    si = sub_img(ch, act)
                    yy = sy(ch, si); scx, ssc = sub_x.get(id(ch), (CX, 1.0))
                    if ssc != 1.0:   # subtítulo a un lado y más pequeño (fila con sub_cx/sub_scale)
                        si = si.resize((int(si.width * ssc), int(si.height * ssc)), Image.LANCZOS)
                    paste_center(im, si, scx, yy, pop_scale(t, ch[0][1], 0.12))
                    break
        if ia is not None and t < ia_until:
            im.paste(ia, (48, SAFE_BOT - 8 - ia.height), ia)
        enc.stdin.write(im.tobytes()); fi += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    sp = cfg.get('speed', 1.0)
    if abs(sp - 1.0) > 1e-3:  # video acelerado (ej. x1.2): imagen y voz juntas, la voz sin cambiar de tono
        tmp_out = out.replace('.mp4', '_x1.mp4'); os.replace(out, tmp_out)
        run(['ffmpeg', '-v', 'error', '-y', '-i', tmp_out, '-filter_complex',
             f'[0:v]setpts=PTS/{sp},fps={FPS}[v];[0:a]atempo={sp}[a]', '-map', '[v]', '-map', '[a]',
             '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
             '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out])
        os.remove(tmp_out); total /= sp
    print(out, f'{total:.2f}s', fi, 'frames', f'(x{sp})' if sp != 1.0 else '')
    return out
