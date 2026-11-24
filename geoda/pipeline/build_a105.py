#!/usr/bin/env python3
"""GEO-MOFU-A1-05 · Podcast (host hombre + invitada mujer; la invitada es la voz principal).
Voces nativas de WAN 3.0: un clip largo por personaje (misma voz en todo el video). Etiqueta real en todas las tomas."""
import os, sys, json, subprocess, re
G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
sys.path.insert(0, G); sys.path.insert(0, f'{G}/tools')
import builder as B
from lines import line_spans
A = f'{G}/a105'; T = f'{A}/tmp'; os.makedirs(T, exist_ok=True)
HF, S, AU = f'{G}/hf', f'{G}/stock', f'{G}/audio'
HOST, G1, G2 = f'{HF}/fixed/w_host_0.mp4', f'{HF}/fixed/w_g1_0.mp4', f'{HF}/fixed/w_g2_0.mp4'
WORDS = {HOST: f'{A}/w_host.words.json', G1: f'{A}/w_g1.words.json', G2: f'{A}/w_g2.words.json'}
STARTS = {HOST: '¿Por qué|En serio|A ver|¿Y entonces|¿Y uno|¿Y si', G1: 'El problema|porque el|El olor|El perfume',
          G2: 'Error uno|Error dos|No, no|Tienes 14|No pagas'}

def spans(clip):
    W = json.load(open(WORDS[clip])); sp = line_spans(clip, WORDS[clip], STARTS[clip].split('|'))
    out = []
    for a0, a1 in sp:
        last = max((w for w in W if a0 - 0.01 <= w['s'] < a1), key=lambda w: w['s'])
        out.append((a0, min(a1, last['e'] + 0.15)))
    return out, W
SP = {c: spans(c) for c in (HOST, G1, G2)}
def seg(clip, i):
    return SP[clip][0][i]
def words(clip, a0, a1):
    return [(w['w'], w['s'] - a0, w['e'] - a0) for w in SP[clip][1] if a0 - 0.01 <= w['s'] < a1]

PITCH = {G2: 1.035}   # la parte 2 de la invitada sale un poco más grave: se empareja con la parte 1 (timbre conservado)
def wav(name, clip, a0, d):
    af = (f'rubberband=pitch={PITCH[clip]}:formant=preserved,' if clip in PITCH else '') + f'apad=whole_dur={d:.3f}'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a0:.3f}', '-t', f'{d:.3f}', '-i', clip, '-vn', '-ac', '1', '-ar', '48000',
                    '-af', af, f'{T}/{name}.wav'], check=True)

# fila = (clave, clip de voz, índice de frase, [tomas]); toma: (nombre, tipo, fuente, duración o None=resto, opciones)
#   'sync' = el mismo clip y tramo de la voz (labios sincronizados); 'vid' = otro video; 'still' = imagen fija
ROWS = {
 'HA':  (HOST, 0, [('ha', 'sync', HOST, None, dict(z0=1.0, z1=1.04, shake=(0.0, 0.35, 16)))]),
 'HB':  (G1, 0, [('hb', 'sync', G1, None, dict(z0=1.0, z1=1.04))]),
 'B1':  (HOST, 1, [('b1', 'sync', HOST, None, dict(z0=1.0, z1=1.04))]),
 'B2':  (G1, 1, [('b2', 'vid', G1, None, dict(ss='a0', speed=0.88, z0=1.0, z1=1.04))]),   # sin el giro del stick al bajarlo
 'B3':  (HOST, 2, [('b3', 'vid', f'{HF}/k_set_0.mp4', None, dict(ss=0.45, z0=1.0, z1=1.05))]),  # plano general
 'B4':  (G1, 2, [('b4', 'vid', f'{T}/ins_gota.mp4', None, dict(ss=0.0))]),
 'B5':  (G1, 3, [('b5a', 'still', f'{HF}/p_mesa_0.png', 2.4, dict(z0=1.0, z1=1.06)), ('b5b', 'sync', G1, None, dict(z0=1.04, z1=1.07))]),
 'B6':  (HOST, 3, [('b6', 'sync', HOST, None, dict(z0=1.0, z1=1.04))]),
 'B7':  (G2, 0, [('b7a', 'sync', G2, 0.9, dict(z0=1.0, z1=1.03)), ('b7b', 'vid', f'{HF}/fixed/k_grifo2_0.mp4', None, dict(ss=0.6, z0=1.0, z1=1.05))]),
 'B8':  (G2, 1, [('b8', 'vid', f'{T}/ins_cal.mp4', None, dict(ss=0.0))]),
 'B9':  (HOST, 4, [('b9', 'sync', HOST, None, dict(z0=1.0, z1=1.04))]),
 'B10': (G2, 2, [('b10', 'sync', G2, None, dict(z0=1.0, z1=1.04))]),
 'B11': (HOST, 5, [('b11', 'sync', HOST, None, dict(z0=1.34, z1=1.38, fx=0.5, fy=0.15))]),  # encuadre cerrado: no se ve el stick al dejarlo
 'B12': (G2, 3, [('b12a', 'sync', G2, 0.57, dict(z0=1.0, z1=1.02)),
                 ('b12b', 'vid', HOST, None, dict(ss=15.75, speed=0.77, z0=1.0, z1=1.04))]),    # el host con el stick frente a él
 'B13': (G2, 4, [('b13a', 'vid', f'{S}/hi_42130.mp4', 1.3, dict(ss=0.3, z0=1.0, z1=1.06)),
                 ('b13b', 'still', f'{HF}/fixed/p_bano_2x.png', None, dict(z0=1.0, z1=1.05))]),
}
LINES = {'HA': '¿Por qué tanta gente dice que la piedra de alumbre no sirve?', 'HB': 'El problema casi nunca es la piedra.'}
EC_BOX = (290, 790, 900, 1530)   # producto + tapa en la tarjeta final (no se tapa)

def build_shots():
    shots, rowmeta = {}, {}
    for key, (clip, i, items) in ROWS.items():
        a0, a1 = seg(clip, i); d = a1 - a0
        fixed = sum(x[3] for x in items if x[3]); rest = d - fixed
        lst, t = [], 0.0
        for name, kind, src, dd, o in items:
            dd = dd or rest
            o = dict(o)
            if kind == 'sync':
                sh = B.shot(T, name, src, dd, ss=a0 + t, **o)
            elif kind == 'still':
                sh = B.shot(T, name, src, dd, still=True, **o)
            else:
                if o.get('ss') == 'a0': o['ss'] = a0 + t
                sh = B.shot(T, name, src, dd, **o)
            wav(name, clip, a0 + t, dd)
            obst = None
            if name == 'b13b': obst = [EC_BOX]
            if src.endswith(('ins_gota.mp4', 'ins_cal.mp4')) or 'k_grifo2' in src or 'p_mesa' in src or 'hi_42130' in src: obst = obst or []
            lst.append(sh + ((obst,) if obst is not None else ())); t += dd
        shots[key] = lst; rowmeta[key] = (d, words(clip, a0, a1))
    return shots, rowmeta

WH = f'{AU}/sfx_1489.mp3'
def cfg_for(meta):
    def row(key, **kw):
        d, wd = meta[key]
        return dict(key=key, clip_audio=True, dur=d, words=wd, line=' '.join(w for w, _, _ in wd), **kw)
    hooks = {
        'HA': dict(row('HA', subs=False, text=('“La piedra no sirve”:', '¿mito?'),
                       extras=[dict(type='stamp', text='MITO', size=120, angle=-14, x=760, y=1240, t0=0.06, t1=meta['HA'][0])]),
                   ),
        'HB': dict(row('HB', subs=True, text=('Lo que nadie explica', 'del alumbre'),
                       extras=[dict(type='text', text='?', size=230, color=(255, 214, 0), stroke=12, stroke_color=(16, 42, 67),
                                    x=300, y=770, t0=0.1, t1=meta['HB'][0])])),
    }
    for h in hooks.values():
        h.pop('key')
    body = [row('B1'), row('B2'), row('B3', icon='👀'), row('B4', sfx=[(-0.1, WH, 0.18)]), row('B5', sfx=[(-0.1, WH, 0.18)]),
            row('B6'), row('B7', sfx=[(0.8, f'{AU}/splash_1311.mp3', 0.25)]), row('B8', sfx=[(-0.1, WH, 0.18)]), row('B9'), row('B10'),
            row('B11'), row('B12'), row('B13', sfx=[(-0.1, WH, 0.18)])]
    return dict(id='GEO_MOFU_A1_05', fmt='PODCAST', version=1, tmp=T, out_dir=A, vo_dir=T, min_face=50, hook_text_until=3.0,
                hook_slots=[250, 300, 360, 420, 470, 560, 700, 860, 1000], cut_sfx=False, music_vol=0.07,
                hooks=hooks, body=body,
                cta=dict(row='B13', l1='PAGA CONTRAENTREGA', l2='Pagas cuando te llegue', pill='Envío gratis a toda Colombia 🚚'),
                sfx={'HA': [(0.02, f'{AU}/sfx_2357.mp3', 0.6)]})

if __name__ == '__main__':
    shots, meta = build_shots()
    cfg = cfg_for(meta)
    for hk in sys.argv[1:] or ['HA', 'HB']:
        B.build(cfg, hk, shots)
