#!/usr/bin/env python3
"""GEO-TOFU-A1-03 v2 · Claymation con el guion del brief corregido (Pedro probó todos los desodorantes; la abuela le da la piedra).
Narradora mujer (una sola toma de voz, misma voz en todo el video) + vocecita de la piedra. Sin precios.
CTA principal K1 Black Friday (sin precio) + alterno K5 Paga contraentrega. Video a x1.15 (ritmo del brief, 27 s)."""
import os, sys, copy
import os  # carpeta de trabajo: GEODA_WORK o ~/.geoda_work (la crea setup_work.sh)
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
A = f'{G}/a103'; TMP = f'{A}/tmp2'; os.makedirs(TMP, exist_ok=True)
HF, VO = f'{G}/hf', f'{A}/vo2'
SPEED = 1.15

def vd(k):
    return B.dur_of(f'{VO}/{k}_t.wav') + 0.12

base = dict(
    id='GEO_TOFU_A1_03', fmt='CLAY', version=2, tmp=TMP, out_dir=A, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0 * SPEED, speed=SPEED, music=f'{G}/audio/music_847.mp3',
    hooks={
        # texto del hook = voz -> sin subtítulo
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Pedro probó todos los desodorantes', 'y seguía oliendo'),
                   line='Pedro probó todos los desodorantes y seguía oliendo.'),
        'HB': dict(vo='HB', dur=vd('HB'), subs=True, text=('Lo que nadie le dijo a Pedro', 'sobre su olor'),
                   line='A Pedro nadie le había dicho esto.'),
    },
    body=[  # titulares que repetían la voz -> solo subtítulos e íconos
        dict(key='B1', vo='B1', dur=vd('B1'), line='Pedro olía a perfume y a sudor, al tiempo.', icon='😩'),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Frasco tras frasco, el olor volvía.'),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Hasta que su abuela le dio esto.', head='¿Una piedra? 🪨'),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Una piedra mineral sin perfume. Pedro la frotó seca y nada.', icon='❌'),
        dict(key='B5', vo='B5', dur=vd('B5') + 0.25, line='¡Mójame, Pedro!'),
        dict(key='B6', vo='B6', dur=vd('B6'), line='Con agua, sobre la piel limpia, la nube se deshace.', icon='💨'),
        dict(key='B7', vo='B7', dur=vd('B7'), line='El problema nunca fue la piedra. Era cómo la usaba.'),
        dict(key='B8', vo='B8bf', dur=vd('B8bf'), line='Se llama GEODA, y por Black Friday: paga dos y lleva tres. Pagas cuando te llegue.'),
    ],
    cta=dict(row='B8', l1='BLACK FRIDAY', l2='Paga 2 lleva 3'),   # sin precio (pedido de Camilo) + 'Pago contraentrega · Envío gratis'
)
k5 = copy.deepcopy(base); k5['fmt'] = 'CLAY_K5'
k5['body'][-1] = dict(key='B8', vo='B8', dur=vd('B8'), line='Se llama GEODA, y no pagas nada ahora: la pagas cuando te llegue.')
k5['cta'] = dict(row='B8', l1='PAGA CONTRAENTREGA', l2='Pagas cuando te llegue')

P = B.protect
def build_shots(cfg):
    T = TMP; ec, ec_box = f'{HF}/fixed/endcard_bano_real.png', (259, 960, 801, 1600)
    k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    s = {
     'HA': [B.shot(T, 'ha', k('k_c2_ha'), d['HA'], ss=0.0, z0=1.0, z1=1.06, stopmo=True) + ([P((440, 690, 650, 960))],)],
     'HB': [B.shot(T, 'hb', f'{HF}/c2_hb_0.png', d['HB'], still=True, z0=1.0, z1=1.07, stopmo=True) + ([P((255, 780, 490, 1040)), (290, 480, 475, 765)],)],
     'B1': [B.shot(T, 'b1', f'{HF}/c2_b1_0.png', d['B1'], still=True, z0=1.0, z1=1.08, stopmo=True) + ([P((350, 740, 600, 1050))],)],
     'B2': [B.shot(T, 'b2', k('k_c2_b2'), d['B2'], ss=0.0, z0=1.0, z1=1.05, stopmo=True) + ([P((540, 560, 770, 890))],)],
     'B3': [B.shot(T, 'b3', k('k_c2_b3'), d['B3'], ss=0.0, z0=1.0, z1=1.05, stopmo=True) + ([P((130, 950, 330, 1150)), P((510, 1000, 670, 1200)), P((710, 830, 935, 1100))],)],
     'B4': [B.shot(T, 'b4', k('k_c2_b4'), d['B4'], ss=0.0, speed=0.62, z0=1.0, z1=1.05, stopmo=True) + ([P((225, 800, 455, 1090)), P((600, 1240, 840, 1480))],)],
     'B5': [B.shot(T, 'b5', k('k_cb3'), d['B5'], ss=0.6, z0=1.0, z1=1.06, stopmo=True) + ([P((270, 420, 840, 840))],)],
     'B6': [B.shot(T, 'b6a', k('k_cb4'), 1.9, ss=0.6, z0=1.0, z1=1.06, stopmo=True) + ([P((180, 225, 480, 540)), P((585, 1080, 825, 1350))],),
            B.shot(T, 'b6b', k('k_cb6'), d['B6'] - 1.9, ss=0.0, z0=1.0, z1=1.05, stopmo=True) + ([P((165, 405, 390, 660)), P((705, 1260, 870, 1410))],)],
     'B7': [B.shot(T, 'b7a', k('k_cb7'), 1.5, ss=1.3, z0=1.0, z1=1.05, stopmo=True) + ([P((180, 270, 435, 570)), P((690, 1140, 930, 1410))],),
            B.shot(T, 'b7b', f'{G}/v2frames/mano.png', d['B7'] - 1.5, still=True, z0=1.0, z1=1.06) + ([],)],   # GEODA real 2 s
     'B8': [B.shot(T, f'b8_{d["B8"]:.2f}', ec, d['B8'], still=True, z0=1.0, z1=1.06) + ([ec_box],)],
    }
    return s

if __name__ == '__main__':
    for cfg in ([base, k5] if len(sys.argv) < 2 else [base if sys.argv[1] == 'K1' else k5]):
        shots = build_shots(cfg)
        for hk in ['HA', 'HB']:
            B.build(cfg, hk, shots)
