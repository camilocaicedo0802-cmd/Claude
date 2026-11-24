#!/usr/bin/env python3
"""GEO-TOFU-A1-03 · Claymation (voz de mujer narradora + vocecita de la piedra). Dos cierres: K5 (contraentrega) y K1 (Black Friday)."""
import os, sys, copy
G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
sys.path.insert(0, G)
import builder as B
A = f'{G}/a103'; TMP = f'{A}/tmp'; os.makedirs(TMP, exist_ok=True)
HF = f'{G}/hf'
base = dict(
    id='GEO_TOFU_A1_03', fmt='CLAY', version=1, tmp=TMP, out_dir=A, vo_dir=f'{A}/vo',
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{G}/audio/music_847.mp3',
    hooks={  # texto del hook = voz -> solo texto
        'HA': dict(vo='HA', dur=2.4, subs=False, text=('Esta piedra no', 'tenía la culpa 🪨'), line='Esta piedra no tenía la culpa.'),
        'HB': dict(vo='HB', dur=2.4, subs=False, text=('Pobre piedra:', 'siempre la culpan'), line='Todo el mundo culpa a la piedra...'),
    },
    body=[  # todos los titulares del guion repetían la voz -> solo subtítulos (+ íconos sin texto)
        dict(key='B1', vo='B1', dur=2.95, line='Pedro dijo que la piedra no servía.'),
        dict(key='B2', vo='B2', dur=1.8, line='Pero había un detalle.'),
        dict(key='B3', vo='B3', dur=1.4, line='¡Mójame, Pedro!'),
        dict(key='B4', vo='B4', dur=1.8, line='Segundo intento, con agua.', icon='💧'),
        dict(key='B5', vo='B5', dur=2.05, line='Pasada suave, piel limpia.'),
        dict(key='B6', vo='B6', dur=2.9, line='Y la nube de olor... se deshace.', icon='💨'),
        dict(key='B7', vo='B7', dur=2.35, line='Esta piedra nunca tuvo la culpa.'),
        dict(key='B8', vo='B8', dur=3.4, line='No pagas nada ahora: pagas cuando te llegue.'),
    ],
    cta=dict(row='B8', l1='PAGA CONTRAENTREGA', l2='Pagas cuando te llegue', pill='Envío gratis a toda Colombia 🚚'),
)
bf = copy.deepcopy(base); bf['fmt'] = 'CLAY_BF'
bf['body'][-1] = dict(key='B8', vo='B8bf', dur=4.9, line='¡Es Black Friday! Paga dos y lleva tres, y pagas cuando te llegue.')
bf['cta'] = dict(row='B8', l1='BLACK FRIDAY', l2='Paga 2 lleva 3', pill='Pagas cuando te llegue · Envío gratis 🚚')

def build_shots(card_dur):
    T = TMP; ec, ec_box = B.endcard(T)
    k = lambda n: f'{HF}/{n}_0.mp4'
    s = {
     'HA': [B.shot(T, 'ha', k('k_cha'), 2.4, ss=0.2, z0=1.0, z1=1.06, stopmo=True) + ([B.protect((240,90,390,300)), B.protect((645,690,855,900))],)],
     'HB': [B.shot(T, 'hb', k('k_chb'), 2.4, ss=0.2, z0=1.0, z1=1.06, stopmo=True) + ([B.protect((120,285,330,525)), B.protect((510,990,720,1200))],)],
     'B1': [B.shot(T, 'b1', k('k_cb1'), 2.95, ss=0.0, z0=1.0, z1=1.05, stopmo=True) + ([B.protect((270,330,480,570)), B.protect((690,615,795,750))],)],
     'B2': [B.shot(T, 'b2', k('k_cb2'), 1.8, ss=0.0, z0=1.0, z1=1.25, stopmo=True) + ([B.protect((240,390,930,840))],)],
     'B3': [B.shot(T, 'b3', k('k_cb3'), 1.4, ss=0.6, z0=1.0, z1=1.06, stopmo=True) + ([B.protect((270,420,840,840))],)],
     'B4': [B.shot(T, 'b4', k('k_cb4'), 1.8, ss=0.6, z0=1.0, z1=1.06, stopmo=True) + ([B.protect((180,225,480,540)), B.protect((585,1080,825,1350))],)],
     'B5': [B.shot(T, 'b5', k('k_cb5'), 2.05, ss=0.4, z0=1.0, z1=1.05, stopmo=True) + ([B.protect((405,450,600,690)), B.protect((690,570,825,690))],)],
     'B6': [B.shot(T, 'b6', k('k_cb6'), 2.9, ss=0.0, z0=1.0, z1=1.05, stopmo=True) + ([B.protect((165,405,390,660)), B.protect((705,1260,870,1410))],)],
     'B7': [B.shot(T, 'b7a', k('k_cb7'), 1.2, ss=1.3, z0=1.0, z1=1.05, stopmo=True) + ([B.protect((180,270,435,570)), B.protect((690,1140,930,1410))],),
            B.shot(T, 'b7b', k('k_mano'), 1.15, ss=0.2, z0=1.0, z1=1.06) + ([],)],          # corte a GEODA real
     'B8': [B.shot(T, f'b8_{card_dur}', ec, card_dur, still=True, z0=1.0, z1=1.05) + ([ec_box],)],
    }
    return s

if __name__ == '__main__':
    which = sys.argv[1:] or ['K5', 'BF']
    for w in which:
        cfg = base if w == 'K5' else bf
        shots = build_shots(cfg['body'][-1]['dur'])
        for hk in ['HA', 'HB']:
            B.build(cfg, hk, shots)
