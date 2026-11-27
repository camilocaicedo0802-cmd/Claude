#!/usr/bin/env python3
"""GEO-MOFU-A3-08 · Podcast 'ranking de desodorantes' (modelado de un reel de referencia) · CTA principal K5 contraentrega + alterno K2 Navidad.
Presentadora (M, ~34) en set de podcast; voz NATIVA de WAN 3.0 (voz y labios salen juntos): 3 tomas, la 2 y la 3 igualadas en tono
a la 1 con rubberband (formantes conservados, no cambia los tiempos). Cada frase usa sus propios tramos del clip; las pausas
de más de 0,3 s se cortan con salto alternando plano abierto y acercamiento (como el original). Tarjetas X/10 (tarjetas.py)
compuestas sobre cada plano ya encuadrado. Sin marcas de la competencia: aerosol, barra y roll-on genéricos.
Versiones: HA (abre con la primera nota) y HB con K5; HC y HD (hooks nuevos) con K2. En el HA se quita la fila B1 (es el hook)."""
import os, sys, subprocess, copy
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G); sys.path.insert(0, f'{G}/tools')
import builder as B
from pauses import segments
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from tarjetas import componer
A = f'{G}/a308'; T = f'{A}/tmp'; os.makedirs(T, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
T1, T2, T3 = f'{HF}/wr_t1_0.mp4', f'{HF}/wr_t2_0.mp4', f'{HF}/wr_t3_0.mp4'
PITCH = {T2: 225.4 / 242.4, T3: 225.4 / 213.3}   # tono de cada toma igualado al de la toma 1
SPEED = float(os.environ.get('A308_SPEED', '1.2'))
# (toma, inicio, fin, texto) medidos por energía y verificados transcribiendo cada tramo solo
LINES = {
 'HB': (T3, 0.28, 5.53, 'Le puse nota a todos los desodorantes que he usado. Solo uno sacó diez.'),
 'HC': (T3, 6.13, 10.74, 'Desodorantes, del peor al mejor. El último te va a sorprender.'),
 'HD': (T3, 11.52, 16.26, 'Probé de todo para el olor de las axilas. Esta es mi nota sincera.'),
 'B1': (T1, 0.73, 4.31, '¿Desodorante en aerosol con perfume? Cuatro de diez.'),
 'B2': (T1, 4.49, 10.46, 'Huele rico al principio, pero a mí el perfume solo me tapaba el olor, y a media tarde volvía.'),
 'B3': (T1, 10.73, 13.13, 'Y el frasco se me acababa en semanas.'),
 'B4': (T1, 13.58, 16.61, '¿Desodorante en barra? Cinco de diez.'),
 'B5': (T1, 17.19, 21.02, 'Es práctico, pero a mí me dejaba rayas blancas en la ropa negra.'),
 'B6': (T1, 21.53, 23.57, '¿Roll-on? Seis de diez.'),
 'B7': (T1, 23.98, 29.66, 'Funciona, pero me quedaba húmedo y tardaba en secar. Y en la mañana, con afán, no.'),
 'B8': (T2, 1.14, 4.06, '¿Piedra de alumbre GEODA? Diez de diez.'),
 'B9': (T2, 4.51, 10.66, 'Es una piedra mineral sin perfume: ataca la bacteria que causa el olor, no lo tapa.'),
 'B10': (T2, 11.02, 15.45, 'Se moja la piedra, no la axila, y no me mancha la ropa.'),
 'B11': (T2, 16.05, 18.77, 'Y una sola piedra te dura un año.'),
 'B12': (T2, 19.37, 23.25, 'Y si en catorce días no te funciona, te devuelven la plata.'),
 'K5': (T2, 23.57, 29.64, 'Si ves el botón aquí abajo, pídela hoy: la pagas cuando te llegue y el envío es gratis.'),
 'K2': (T3, 16.74, 23.51, 'Si ves el botón aquí abajo, aprovecha: paga dos, lleva tres, y regala GEODA esta Navidad.'),
}
LINES['HA'] = LINES['B1']
# tarjetas en el tiempo de cada toma: (inicio, fin, producto, nota, momento de la nota, entra con animación)
EV = {
 T1: [(0.73, 13.45, 'aerosol', '4/10', 3.33), (13.58, 21.45, 'barra', '5/10', 15.54), (21.53, 30.1, 'rollon', '6/10', 22.55)],
 T2: [(1.14, 23.50, 'geoda', '10/10', 2.97), (23.50, 30.1, 'geoda', 'cta', None, False)],
 T3: [(16.74, 24.1, 'geoda', 'cta_regalo', None)],
}
FACE = (330, 560, 760, 1000)   # cabeza con pelo en el plano abierto
PAD, MAXGAP = 0.06, 0.30
_segs = {}

def subsegs(clip, a0, a1):
    if clip not in _segs: _segs[clip] = segments(clip, 0.08, 0.05)
    ss = [(max(a0, s0), min(a1, s1)) for s0, s1 in _segs[clip] if s1 > a0 and s0 < a1]
    out = []
    for s0, s1 in ss:
        if out and s0 - out[-1][1] < MAXGAP: out[-1][1] = s1
        else: out.append([s0, s1])
    out = [[max(0, s0 - PAD), s1 + PAD] for s0, s1 in out]
    for i in range(1, len(out)):   # sin solaparse
        if out[i][0] < out[i - 1][1]: m = (out[i][0] + out[i - 1][1]) / 2; out[i - 1][1] = m; out[i][0] = m
    return out

def row(key, k, flip=0, src=None, extra=0.0, box=None):
    clip, a0, a1, text = LINES[k]; parts = subsegs(clip, a0, a1)
    shots = []; total = 0.0
    for i, (s0, s1) in enumerate(parts):
        d = s1 - s0 + (extra if i == len(parts) - 1 else 0.0)
        close = (i + flip) % 2 == 1
        o = dict(z0=1.12, z1=1.15, fx=0.47, fy=0.40) if close else dict(z0=1.0, z1=1.03, fx=0.47, fy=0.45)
        name = f'p_{key}_{k}_{i}' + ('c' if close else 'w')
        sh, dd = B.shot(T, name, clip, d, ss=s0, **o)
        ev = [(e[0] - s0, e[1] - s0, *e[2:4], (e[4] - s0) if len(e) > 4 and e[4] is not None else None, *(e[5:] or [True]))
              for e in EV.get(clip, []) if e[1] > s0 and e[0] < s0 + d]
        out = sh.replace('.mp4', '_c.mp4')
        if ev and (not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(sh)): componer(sh, out, ev)
        shots.append((out if ev else sh, dd, box if box is not None else [FACE] if not close else [(260, 480, 800, 1010)]))
        total += d
    w = shots[0][0].replace('.mp4', '.wav')   # voz de toda la fila (tramos pegados), tono igualado
    fl = ';'.join(f'[0:a]atrim={s0:.3f}:{s1:.3f},asetpts=PTS-STARTPTS[a{i}]' for i, (s0, s1) in enumerate(parts))
    cat = ''.join(f'[a{i}]' for i in range(len(parts))) + f'concat=n={len(parts)}:v=0:a=1'
    af = ((f',rubberband=pitch={PITCH[clip]:.4f}:formant=preserved' if clip in PITCH else '')
          + ',highpass=f=90,alimiter=limit=0.6:attack=1:release=40:level=false' + f',apad=whole_dur={total:.3f}')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', clip, '-filter_complex', f'{fl};{cat}{af}[out]', '-map', '[out]', '-ac', '1', '-ar', '48000', w], check=True)
    words = B.word_times(text, 0.0, total)
    return shots, total, words

def plan(cta):
    keys = {'HA': 'HA', 'HB': 'HB', 'HC': 'HC', 'HD': 'HD', **{f'B{i}': f'B{i}' for i in range(1, 13)}, 'B13': cta}
    shots, meta = {}, {}
    for n, (key, k) in enumerate(keys.items()):
        sh, d, wd = row(key, k, flip=n % 2 if key.startswith('B') else 0)
        shots[key] = sh; meta[key] = (d, wd)
    return shots, meta

def cfg_for(meta, cta):
    def r(key, **kw):
        d, wd = meta[key]
        return dict(key=key, clip_audio=True, dur=d, words=wd, line=' '.join(w for w, _, _ in wd), **kw)
    hooks = {
        'HA': r('HA', subs=False, text=('Califiqué cada', 'desodorante que usé 👇')),
        'HB': r('HB', subs=False, text=('Solo uno sacó', '10 de 10 👇')),
        'HC': r('HC', subs=False, text=('Desodorantes: del peor', 'al mejor 👇')),
        'HD': r('HD', subs=False, text=('Mi nota sincera a', 'cada desodorante')),
    }
    for h in hooks.values():
        h.pop('key')
        h['hook_slots'] = [B.SAFE_TOP + 4 + B.hook_block(*h['text']).height // 2]   # v2 (Camilo): título pegado arriba (borde superior de la zona segura)
    body = [r(f'B{i}', sub_y=520) for i in range(1, 13)] + [r('B13', sub_y=520)]
    ctad = (dict(row='B13', delay=0.3, l1='PÍDELA HOY', l2='La pagas cuando te llegue', pill='Envío gratis a toda Colombia 🚚') if cta == 'K5'
            else dict(row='B13', delay=0.3, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3'))
    return dict(id='GEO_MOFU_A3_08', fmt='PODCAST' if cta == 'K5' else 'PODCAST_K2', version=2, tmp=T, out_dir=A, vo_dir=T,
                min_face=50, hook_text_until=3.0 * SPEED, speed=SPEED, ai_label=False, cut_sfx=True, cut_sfx_vol=0.08,
                music=f'{AU}/music_805.mp3', music_vol=0.05, hooks=hooks, body=body, cta=ctad)

if __name__ == '__main__':
    want = sys.argv[1:] or ['HA', 'HB', 'HC', 'HD']
    for cta, hks in (('K5', ['HA', 'HB']), ('K2', ['HC', 'HD'])):
        hks = [h for h in hks if h in want]
        if not hks: continue
        shots, meta = plan(cta); cfg = cfg_for(meta, cta)
        for hk in hks:
            c = copy.deepcopy(cfg)
            if hk == 'HA': c['body'] = [x for x in c['body'] if x['key'] != 'B1']   # el hook A ya es la primera nota
            print(hk, 'duración sin acelerar: %.1f s' % (meta[hk][0] + sum(x['dur'] for x in c['body'])))
            B.build(c, hk, shots)
