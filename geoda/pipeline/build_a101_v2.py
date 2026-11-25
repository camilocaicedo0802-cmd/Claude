#!/usr/bin/env python3
"""GEO-TOFU-A1-01 v2 · UGC con avatar IA (MUJER) con el guion del brief corregido ('olor a media tarde').
Narradora: una sola toma de voz (misma voz en todo el video), la avatar nunca mueve los labios (voz en off tipo storytime).
Rótulo 'Recreación con IA'. Sin precios. CTA K5 Paga contraentrega. Video a x1.15."""
import os, sys
import os  # carpeta de trabajo: GEODA_WORK o ~/.geoda_work (la crea setup_work.sh)
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
A = f'{G}/a101'; TMP = f'{A}/tmp2'; os.makedirs(TMP, exist_ok=True)
HF, VO, AU = f'{G}/hf', f'{A}/vo2', f'{G}/audio'
SPEED = 1.15

def vd(k):
    return B.dur_of(f'{VO}/{k}_t.wav') + 0.12

DOOR = 2.0
cfg = dict(
    id='GEO_TOFU_A1_01', fmt='UGC', version=3, tmp=TMP, out_dir=A, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0 * SPEED, speed=SPEED, music=f'{AU}/music_805.mp3',
    hooks={
        # texto del hook = voz -> sin subtítulo; reloj gigante 3:00 p. m. desde el fotograma 1
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Si a media tarde ya hueles, aunque', 'te eches desodorante, mira esto 👇'),
                   line='Si a media tarde ya sientes olor, aunque te hayas echado desodorante, escúchame.',
                   hook_slots=[1030],
                   extras=[dict(type='img', path=f'{TMP}/clock_sticker.png', x=250, y=560, t0=0.0, pop=False)],
                   sfx=[(0.0, f'{AU}/sfx_glint.wav', 0.25)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=True, text=('El error #1 por el que tu', "desodorante 'no sirve'"),
                   line='Esto es lo que casi todo el mundo hace mal con el desodorante.',
                   sfx=[(0.30, f'{AU}/sfx_thud.wav', 0.9), (0.33, f'{AU}/sfx_error.wav', 0.55)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Me echaba desodorante a las siete y a las tres ya sentía olor.',
             sfx=[(0.0, f'{AU}/sfx_clock.wav', 0.45)]),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Y le echaba más perfume encima. Peor.', icon='❌'),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Hasta que entendí algo: el olor no es el sudor.'),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Son las bacterias de la piel. El perfume solo lo tapa.'),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Ahí descubrí una piedra mineral que se usa como desodorante, sin perfume.', sub_y=440,
             sfx=[(0.55, f'{AU}/sfx_glint.wav', 0.3), (1.75, f'{AU}/sfx_glint.wav', 0.25)]),
        dict(key='B6', vo='B6', dur=vd('B6'), line='Pero ojo: casi todos la usan mal. Se moja la piedra, no la axila.', sub_y=905),
        dict(key='B7', vo='B7', dur=vd('B7'), line='Mojada, sobre la axila limpia. Desde ahí dejé de sentir olor a media tarde.', icon='✅'),
        dict(key='B8', vo='B8', dur=vd('B8'), line='Se llama GEODA, y no pagas nada ahora: la pagas cuando te llegue a la casa.'),
    ],
    cta=dict(row='B8', delay=DOOR, l1='PAGA CONTRAENTREGA', l2='Pagas cuando te llegue', pill='Envío gratis a toda Colombia 🚚'),
)

def build_shots(cfg):
    T = TMP; ec, ec_box = f'{HF}/fixed/endcard_bano_real.png', (259, 960, 801, 1600)
    k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    s = {
     # se huele la blusa y mira el reloj (antes de que voltee la cara, 3,7 s del clip)
     'HA': [B.shot(T, 's_ha', k('k_f_huele'), d['HA'], ss=0.0, speed=0.75, z0=1.0, z1=1.05) + ([(440, 330, 860, 880)],)],
     'HB': [B.shot(T, 's_hb', f'{T}/hb.mp4', d['HB']) + ([(240, 760, 860, 1400)],)],
     'B1': [B.shot(T, 's_b1', f'{T}/b1.mp4', d['B1']) + ([(220, 500, 820, 1330)],)],
     'B2': [B.shot(T, 's_b2', k('k_f_perfume'), d['B2'], ss=0.0, z0=1.0, z1=1.05)],
     # mira a cámara: zoom rápido (golpe) y luego quieto
     'B3': [B.shot(T, 's_b3a', k('k_f_mira'), 0.30, ss=0.0, z0=1.0, z1=1.22, fx=0.5, fy=0.38),
            B.shot(T, 's_b3b', k('k_f_mira'), d['B3'] - 0.30, ss=0.30, z0=1.22, z1=1.28, fx=0.5, fy=0.38)],
     'B4': [B.shot(T, 's_b4', f'{T}/b4.mp4', d['B4']) + ([(150, 950, 930, 1550)],)],
     'B5': [B.shot(T, 's_b5', f'{T}/b5.mp4', d['B5']) + ([(300, 500, 780, 1450)],)],
     'B6': [B.shot(T, 's_b6', f'{HF}/fixed/k_grifo2_0.mp4', d['B6'], ss=0.0, speed=0.64, z0=1.0, z1=1.06)],
     'B7': [B.shot(T, 's_b7a', f'{HF}/f_aplica_0.png', 2.3, still=True, z0=1.0, z1=1.06),
            B.shot(T, 's_b7b', k('k_f_sonrie'), d['B7'] - 2.3, ss=0.3, z0=1.0, z1=1.04)],
     'B8': [B.shot(T, 's_b8a', k('k_f_puerta'), DOOR, ss=0.6, z0=1.0, z1=1.05),
            B.shot(T, f's_b8b_{d["B8"]:.2f}', ec, d['B8'] - DOOR, still=True, z0=1.0, z1=1.05) + ([ec_box],)],
    }
    return s

if __name__ == '__main__':
    shots = build_shots(cfg)
    for hk in sys.argv[1:] or ['HA', 'HB']:
        B.build(cfg, hk, shots)
