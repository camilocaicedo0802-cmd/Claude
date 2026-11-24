#!/usr/bin/env python3
"""Montaje GEO-TOFU-A1-02 (Demo de producto) - borrador v1.
Genera GEO_TOFU_A1_02_HA_DEMO_v1.mp4 y GEO_TOFU_A1_02_HB_DEMO_v1.mp4 (1080x1920, 30 fps)."""
import subprocess, os, json, re, math, sys
from PIL import Image, ImageDraw, ImageFont

G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
A = f'{G}/a102'
TMP = f'{A}/tmp'
os.makedirs(TMP, exist_ok=True)
W, H, FPS = 1080, 1920, 30
L, S, R, K, SCR = f'{G}/landing_vids', f'{G}/stock', f'{G}/ref', f'{G}/hf/s03_vid_v2_0.mp4', f'{G}/screen'
VO = f'{A}/vo'

FONT_BLACK = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
FONT_XB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
FONT_EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
NAVY, TEAL, YEL, WHITE, BLACK = (16, 50, 74), (25, 167, 160), (255, 212, 59), (255, 255, 255), (0, 0, 0)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(' '.join(cmd)); print(r.stderr[-2000:]); sys.exit(1)

def dur_of(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                capture_output=True, text=True).stdout.strip())

# ---------------------------------------------------------------- planos
def shot(name, src, dur, ss=0.0, speed=1.0, z0=1.0, z1=1.0, cx=0.5, cy=0.5, still=False, sharpen=False):
    out = f'{TMP}/{name}.mp4'
    nf = round(dur * FPS)
    if still:
        inp = ['-loop', '1', '-framerate', str(FPS), '-t', f'{dur + 0.5}', '-i', src]
        pre = []
    else:
        inp = ['-ss', f'{ss}', '-t', f'{dur * speed + 0.3}', '-i', src]
        pre = [f'setpts=(PTS-STARTPTS)/{speed}', f'fps={FPS}']
    vf = pre + [
        f'scale={2*W}:{2*H}:force_original_aspect_ratio=increase:flags=lanczos',
        f'crop={2*W}:{2*H}:(iw-{2*W})*{cx}:(ih-{2*H})*{cy}',
        f"zoompan=z='{z0}+({z1}-{z0})*on/{nf}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}",
    ]
    if sharpen:
        vf.append('unsharp=5:5:0.9:5:5:0.0')
    vf.append('tpad=stop_mode=clone:stop_duration=2')
    vf.append('format=yuv420p')
    run(['ffmpeg', '-v', 'error', '-y', *inp, '-vf', ','.join(vf), '-frames:v', str(nf),
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-r', str(FPS), '-an', out])
    return out, dur

def screen_shot(name, hold=1.4):
    """Scroll de la landing (12 frames) + pausa con el botón visible."""
    frames = sorted(f for f in os.listdir(SCR) if f.startswith('sc_') and f.endswith('.png'))[::-1]
    lst = f'{TMP}/{name}_list.txt'
    with open(lst, 'w') as fh:
        for f in frames:
            fh.write(f"file '{SCR}/{f}'\nduration {1/FPS:.5f}\n")
        fh.write(f"file '{SCR}/{frames[-1]}'\nduration {hold:.3f}\nfile '{SCR}/{frames[-1]}'\n")
    out = f'{TMP}/{name}.mp4'
    d = len(frames) / FPS + hold
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
         '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}:0:0,fps={FPS},format=yuv420p',
         '-frames:v', str(round(d * FPS)), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-r', str(FPS), '-an', out])
    return out, d

# ---------------------------------------------------------------- guion / timeline
HOOKS = {
    'HA': dict(vo='HA', text='Se moja la piedra,\nno la axila', line='¡Así es como sí se usa!', dur=2.4),
    'HB': dict(vo='HB', text='3 pasos que\nnadie te explicó', line='Te lo enseño en quince segundos.', dur=2.4),
}
BODY = [  # (vo, linea, texto en pantalla, duración fila)
    ('B1', 'Paso uno: moja la piedra, no la axila.', '1. Moja la piedra', 3.25),
    ('B2', 'Paso dos: pásala por la axila limpia, varias pasadas suaves.', '2. Aplica en piel limpia', 4.05),
    ('B3', 'Espera a que seque antes de vestirte.', 'Deja secar ⏱️', 1.95),
    ('B4', 'Paso tres, el que nadie hace: sécala y guárdala lejos de la ducha.', '3. Sécala y guárdala 👈', 4.78),
    ('B5', 'Así no se agrieta y te rinde mucho más.', 'Así rinde más', 2.60),
    ('B6', 'Llévala hoy: pídela ya, y la pagas cuando te llegue a la puerta.', None, 4.40),
]

def build_shots():
    s = {}
    s['HA'] = [shot('ha1', f'{S}/hi_10345.mp4', 0.9, ss=2.0, z0=1.05, z1=1.12),
               shot('ha2', f'{L}/ugc_1c.mp4', 1.5, ss=3.3, z0=1.12, z1=1.22, cy=0.55, sharpen=True)]
    s['HB'] = [shot('hb1', f'{R}/hk_t1.webp', 2.4, still=True, z0=1.0, z1=1.15, sharpen=True)]
    s['B1'] = [shot('b1a', f'{L}/ugc_2.mp4', 2.0, ss=2.2, speed=0.85, z0=1.05, z1=1.1, sharpen=True),
               shot('b1b', f'{R}/hk_r5.webp', 1.25, still=True, z0=1.0, z1=1.1, cx=0.62, sharpen=True)]
    s['B2'] = [shot('b2a', K, 3.0, ss=0.0, speed=0.83, z0=1.0, z1=1.06),
               shot('b2b', f'{L}/ugc_1c.mp4', 1.05, ss=6.0, z0=1.05, z1=1.1, sharpen=True)]
    s['B3'] = [shot('b3a', f'{S}/hi_28897.mp4', 1.95, ss=2.0, z0=1.25, z1=1.4)]
    s['B4'] = [shot('b4a', f'{L}/ugc_2.mp4', 2.2, ss=6.9, z0=1.05, z1=1.12, sharpen=True),
               shot('b4b', f'{R}/hk_z3.webp', 1.2, still=True, z0=1.0, z1=1.1, sharpen=True),
               shot('b4c', f'{R}/hk_t4.webp', 1.38, still=True, z0=1.1, z1=1.0, sharpen=True)]
    s['B5'] = [shot('b5a', f'{L}/ugc_3b.mp4', 1.5, ss=0.7, z0=1.0, z1=1.06, sharpen=True),
               shot('b5b', f'{L}/ugc_1c.mp4', 1.1, ss=8.9, z0=1.05, z1=1.1, sharpen=True)]
    s['B6'] = [screen_shot('b6a', hold=1.4),
               shot('b6b', f'{S}/hi_42137.mp4', 1.1, ss=2.0, z0=1.0, z1=1.06),
               shot('b6c', f'{L}/ugc_5.mp4', 1.5, ss=8.3, z0=1.05, z1=1.1, sharpen=True)]
    return s

# ---------------------------------------------------------------- texto
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

def is_emoji(ch):
    o = ord(ch)
    return o >= 0x2190 and not (0x2000 <= o <= 0x206F) or o in (0xFE0F,)

def render_runs(text, size, color, fpath=FONT_BLACK, stroke=0, stroke_color=BLACK):
    """Texto con soporte de emoji a color. Devuelve RGBA ajustado."""
    runs, cur, emo = [], '', False
    for ch in text:
        e = is_emoji(ch)
        if ch == '️':
            continue
        if cur and e != emo:
            runs.append((cur, emo)); cur = ''
        cur += ch; emo = e
    if cur:
        runs.append((cur, emo))
    f = font(fpath, size)
    asc, desc = f.getmetrics()
    h = asc + desc + 2 * stroke
    parts = []
    for t, e in runs:
        if e:
            for ch in t:
                ef = font(FONT_EMOJI, 109)
                im = Image.new('RGBA', (140, 140), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((0, 0), ch, font=ef, embedded_color=True)
                im = im.crop(im.getbbox())
                s = int(size * 1.0)
                im = im.resize((int(im.width * s / im.height), s), Image.LANCZOS)
                canvas = Image.new('RGBA', (im.width + int(size * 0.15), h), (0, 0, 0, 0))
                canvas.paste(im, (int(size * 0.08), (h - s) // 2 + int(size * 0.05)), im)
                parts.append(canvas)
        else:
            w = int(f.getlength(t)) + 2 * stroke
            im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((stroke, stroke), t, font=f, fill=color, stroke_width=stroke, stroke_fill=stroke_color)
            parts.append(im)
    W_ = sum(p.width for p in parts)
    out = Image.new('RGBA', (W_, h), (0, 0, 0, 0))
    x = 0
    for p in parts:
        out.paste(p, (x, 0), p); x += p.width
    return out

def wrap(text, size, maxw, fpath=FONT_BLACK):
    if '\n' in text:
        return text.split('\n')
    f = font(fpath, size)
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if f.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines

def box_text(text, size, fg, bg, maxw=780, pad=(34, 20), radius=26, fpath=FONT_BLACK, line_gap=0.12):
    lines = wrap(text, size, maxw - 2 * pad[0], fpath)
    ims = [render_runs(l, size, fg, fpath) for l in lines]
    gap = int(size * line_gap)
    bw = max(i.width for i in ims) + 2 * pad[0]
    bh = sum(i.height for i in ims) + gap * (len(ims) - 1) + 2 * pad[1]
    out = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=radius, fill=bg + (255,))
    y = pad[1]
    for im in ims:
        out.paste(im, ((bw - im.width) // 2, y), im); y += im.height + gap
    return out

def pill(text, size, fg, bg, alpha=200, pad=(18, 8)):
    im = render_runs(text, size, fg, FONT_XB)
    out = Image.new('RGBA', (im.width + 2 * pad[0], im.height + 2 * pad[1]), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle([0, 0, out.width - 1, out.height - 1], radius=out.height // 2, fill=bg + (alpha,))
    out.paste(im, pad, im)
    return out

# ---------------------------------------------------------------- subtítulos palabra a palabra
def word_times(line, d0, dur):
    words = line.split()
    wts = [len(re.sub(r'[^\wáéíóúñü]', '', w, flags=re.I)) + 1.5 + (2.5 if re.search(r'[,:.!?]$', w) else 0) for w in words]
    tot, t, out = sum(wts), d0, []
    for w, k in zip(words, wts):
        dd = dur * k / tot
        out.append((re.sub(r'[,:.]$', '', w), t, t + dd)); t += dd
    return out

def chunks(wt, maxw=3, maxc=16):
    res, cur = [], []
    for w in wt:
        if cur and (len(cur) >= maxw or len(' '.join(x[0] for x in cur + [w])) > maxc):
            res.append(cur); cur = []
        cur.append(w)
        if re.search(r'[!?]$', w[0]) or w[0].endswith(':'):
            res.append(cur); cur = []
    if cur:
        res.append(cur)
    return res

_sub_cache = {}
def sub_img(words, active):
    k = (tuple(w[0] for w in words), active)
    if k in _sub_cache:
        return _sub_cache[k]
    size = 66
    parts = []
    for i, (w, _, _) in enumerate(words):
        parts.append(render_runs(w, size, YEL if i == active else WHITE, FONT_BLACK, stroke=9))
    sp = int(size * 0.28)
    out = Image.new('RGBA', (sum(p.width for p in parts) + sp * (len(parts) - 1), parts[0].height), (0, 0, 0, 0))
    x = 0
    for p in parts:
        out.paste(p, (x, 0), p); x += p.width + sp
    if out.width > 820:
        out = out.resize((820, int(out.height * 820 / out.width)), Image.LANCZOS)
    bg = Image.new('RGBA', (out.width + 44, out.height + 16), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle([0, 0, bg.width - 1, bg.height - 1], radius=24, fill=(0, 0, 0, 150))
    bg.paste(out, (22, 8), out)
    out = bg
    _sub_cache[k] = out
    return out

# ---------------------------------------------------------------- animación
def pop_scale(t, t0, d=0.2):
    x = (t - t0) / d
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return 0.6 + 0.48 * math.sin(x * math.pi * 0.75) / math.sin(math.pi * 0.75) * (1 - 0.1 * x)

def paste_center(base, img, cx, y, scale=1.0):
    if scale <= 0:
        return
    if abs(scale - 1) > 0.01:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    base.paste(img, (int(cx - img.width / 2), int(y - img.height / 2)), img)

# ---------------------------------------------------------------- render de una variante
def build_variant(hk, shots):
    hook = HOOKS[hk]
    seq = [(hk, hook['dur'])] + [(b[0], b[3]) for b in BODY]
    # 1) concat de planos
    lst, cuts, t = f'{TMP}/concat_{hk}.txt', [], 0.0
    with open(lst, 'w') as fh:
        for key, _ in seq:
            for f, d in shots[key]:
                fh.write(f"file '{f}'\n"); cuts.append(t); t += d
    total = t
    base = f'{TMP}/base_{hk}.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', base])
    # 2) tiempos de filas
    rows, t = [], 0.0
    for key, d in seq:
        rows.append((key, t, d)); t += d
    row_start = {k: s for k, s, _ in rows}
    # 3) audio
    vo_items = [(f'{VO}/{hook["vo"]}_t.wav', 0.08)] + [(f'{VO}/{b[0]}_t.wav', row_start[b[0]] + 0.05) for b in BODY]
    whoosh = f'{G}/audio/sfx_1489.mp3'; popsfx = f'{G}/audio/sfx_2357.mp3'; click = f'{G}/audio/sfx_1109.mp3'
    music = f'{G}/audio/music_821.mp3'
    tap_t = row_start['B6'] + 12 / FPS + 0.55
    inputs, filt, labels = [], [], []
    for i, (f, st) in enumerate(vo_items):
        inputs += ['-i', f]
        filt.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={int(st*1000)}|{int(st*1000)},volume=1.0[v{i}]')
        labels.append(f'[v{i}]')
    n = len(vo_items)
    filt.append(f'{"".join(labels)}amix=inputs={n}:normalize=0,pan=stereo|c0=c0|c1=c0[vo]')
    inputs += ['-i', music]; mi = n
    filt.append(f'[{mi}:a]aresample=48000,atrim=0:{total},volume=0.10,afade=t=in:d=0.3,afade=t=out:st={total-0.6}:d=0.6[mus]')
    sfx = []
    k = mi + 1
    for c in cuts[1:]:
        inputs += ['-i', whoosh]
        filt.append(f'[{k}:a]aresample=48000,atrim=0:0.6,volume=0.22,adelay={int(max(0,c-0.12)*1000)}|{int(max(0,c-0.12)*1000)}[s{k}]')
        sfx.append(f'[s{k}]'); k += 1
    for key, st, _ in rows:  # pop cuando aparece el texto de cada fila
        inputs += ['-i', popsfx]
        filt.append(f'[{k}:a]aresample=48000,volume=0.35,adelay={int((st+0.04)*1000)}|{int((st+0.04)*1000)}[s{k}]')
        sfx.append(f'[s{k}]'); k += 1
    inputs += ['-i', click]
    filt.append(f'[{k}:a]aresample=48000,atrim=0:0.5,volume=0.6,adelay={int(tap_t*1000)}|{int(tap_t*1000)}[s{k}]')
    sfx.append(f'[s{k}]'); k += 1
    filt.append(f'{"".join(sfx)}amix=inputs={len(sfx)}:normalize=0[sfx]')
    filt.append(f'[vo][mus][sfx]amix=inputs=3:normalize=0,atrim=0:{total},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]')
    audio = f'{TMP}/audio_{hk}.m4a'
    run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]', '-c:a', 'aac', '-b:a', '192k', audio])

    # 4) overlays
    els = []  # (img, cx, cy, t0, t1, pop)
    CX = 520  # centro dentro de zona segura (140 px libres a la derecha)
    if hk == 'HA':
        els.append((box_text(hook['text'], 76, BLACK, WHITE, maxw=820), CX, 420, 0.0, hook['dur'], False))
    else:
        els.append((box_text(hook['text'], 76, BLACK, WHITE, maxw=820), CX, 420, 0.0, hook['dur'], False))
        three = render_runs('3', 330, YEL, FONT_BLACK, stroke=12, stroke_color=NAVY)
        els.append((three, 830, 640, 0.12, hook['dur'], True))
    for vo, line, txt, d in BODY:
        st = row_start[vo]
        if txt:
            els.append((box_text(txt, 66, NAVY, WHITE, maxw=760), CX, 360, st, st + d, True))
    st6 = row_start['B6']
    cta0 = st6 + shots['B6'][0][1]
    els.append((box_text('LLÉVALA HOY', 96, WHITE, NAVY, maxw=800, pad=(40, 22)), CX, 360, cta0, total, True))
    els.append((box_text('Pagas al recibir', 64, NAVY, YEL, maxw=760), CX, 492, cta0 + 0.15, total, True))
    els.append((pill('Pago contraentrega · Envío gratis 🚚', 40, WHITE, TEAL, alpha=235, pad=(26, 12)), CX, 598, cta0 + 0.3, total, True))
    ia_label = pill('Recreación con IA', 26, WHITE, (0, 0, 0), alpha=140)

    # subtítulos
    subs = []
    lines = [(hook['line'], f'{VO}/{hook["vo"]}_t.wav', 0.08)] + [(b[1], f'{VO}/{b[0]}_t.wav', row_start[b[0]] + 0.05) for b in BODY]
    for line, f, st in lines:
        wt = word_times(line, st, dur_of(f))
        for ch in chunks(wt):
            subs.append(ch)

    btn = json.load(open(f'{SCR}/btn.json'))
    out = f'{A}/GEO_TOFU_A1_02_{hk}_DEMO_v1.mp4'
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', base, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', out],
                           stdin=subprocess.PIPE)
    fsz = W * H * 3
    fi = 0
    while True:
        raw = dec.stdout.read(fsz)
        if len(raw) < fsz:
            break
        t = fi / FPS
        im = Image.frombytes('RGB', (W, H), raw)
        for img, cx, cy, t0, t1, pop in els:
            if t0 <= t < t1:
                paste_center(im, img, cx, cy, pop_scale(t, t0) if pop else 1.0)
        # tap en el botón de la landing
        if tap_t - 0.05 <= t < tap_t + 0.45:
            p = (t - tap_t + 0.05) / 0.5
            d = ImageDraw.Draw(im, 'RGBA')
            r = 40 + 70 * p
            bx, by = btn['btnCenterX'], btn['btnCenterY'] - 90 * W / 390  # frame final mostrado = sc_00
            d.ellipse([bx - r, by - r, bx + r, by + r], outline=(255, 255, 255, int(255 * (1 - p))), width=10)
            d.ellipse([bx - 34, by - 34, bx + 34, by + 34], fill=(255, 255, 255, int(170 * (1 - p * 0.6))))
        # subtítulo activo
        for ch in subs:
            if ch[0][1] <= t < ch[-1][2] + 0.05:
                act = max([i for i, w in enumerate(ch) if w[1] <= t] or [0])
                paste_center(im, sub_img(ch, act), CX, 1130, pop_scale(t, ch[0][1], 0.12))
                break
        im.paste(ia_label, (60, 1215), ia_label)
        enc.stdin.write(im.tobytes())
        fi += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print(out, f'{total:.2f}s', fi, 'frames')
    return out

if __name__ == '__main__':
    shots = build_shots()
    for hk in sys.argv[1:] or ['HA', 'HB']:
        build_variant(hk, shots)
