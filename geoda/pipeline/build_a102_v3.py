#!/usr/bin/env python3
"""GEO-TOFU-A1-02 v3 · Demo de producto con el guion del brief corregido ('Esto parece un cristal').
Narrador hombre (una sola toma, misma voz en todo el video). Sin precios. CTA K3 Llévala hoy.
Hook A: foto real a contraluz con destellos y giro. Hook B: frasco genérico tachado -> cae GEODA real.
Planos de producto con la etiqueta nativa buena (sin etiqueta sobrepuesta). Video a x1.05 (24 s del brief)."""
import os, sys
G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
sys.path.insert(0, G)
import builder as B
A = f'{G}/a102'; TMP = f'{A}/tmp3'; os.makedirs(TMP, exist_ok=True)
HF, VO, AU = f'{G}/hf', f'{A}/vo3', f'{G}/audio'
SPEED = 1.05

def vd(k):
    return B.dur_of(f'{VO}/{k}_t.wav') + 0.12

LAND = 1.7
cfg = dict(
    id='GEO_TOFU_A1_02', fmt='DEMO', version=3, tmp=TMP, out_dir=A, vo_dir=VO,
    ai_label=False,                      # demo de producto: el brief no pide rótulo IA aquí
    hook_text_until=3.0 * SPEED, speed=SPEED, music=f'{AU}/music_821.mp3',
    hooks={  # texto del hook = voz -> sin subtítulo
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Esto parece un cristal,', 'pero es un desodorante'),
                   line='Esto parece un cristal... pero es un desodorante.',
                   sfx=[(0.32, f'{AU}/sfx_glint.wav', 0.35), (1.15, f'{AU}/sfx_glint.wav', 0.3), (2.05, f'{AU}/sfx_glint.wav', 0.3)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('El desodorante que', 'NO viene en frasco'),
                   line='¿Sabías que existe un desodorante que no viene en frasco?',
                   sfx=[(0.26, f'{AU}/sfx_error.wav', 0.55), (1.30, f'{AU}/sfx_thud.wav', 0.8)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Es piedra de alumbre: un mineral que se usa como desodorante.', icon='🪨', sub_y=1190),
        dict(key='B2', vo='B2', dur=vd('B2'), line='No tiene perfume y no es líquido.'),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Pero hay un truco que casi nadie sabe.', icon='👇'),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Uno: se moja la piedra, no la axila.', big='1'),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Dos: la pasas por la axila limpia.', big='2', icon_x=800),
        dict(key='B6', vo='B6', dur=vd('B6'), line='Tres: la secas y la guardas lejos de la ducha. Así no se agrieta.', big='3'),
        dict(key='B7', vo='B7', dur=vd('B7'), line='Se llama GEODA. Pruébala: pídela hoy y la pagas cuando te llegue.',
             sfx=[(0.85, f'{AU}/sfx_1109.mp3', 0.6)]),
    ],
    cta=dict(row='B7', delay=LAND, l1='LLÉVALA HOY', l2='Pagas al recibir'),
)

P = B.protect
def build_shots(cfg):
    T = TMP; ec, ec_box = f'{HF}/fixed/endcard_bano_real.png', (259, 960, 801, 1600)
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    lab_ha, lab_hb = (300, 560, 760, 1450), (150, 560, 940, 1640)
    s = {
     # cajas directas (sin márgenes de cara): piedra + etiqueta del producto
     'HA': [B.shot(T, 's_ha', f'{T}/ha.mp4', d['HA']) + ([(330, 560, 760, 1300)],)],
     'HB': [B.shot(T, 's_hb', f'{T}/hb.mp4', d['HB']) + ([(170, 560, 930, 1620)],)],
     'B1': [B.shot(T, 's_b1', f'{T}/b1.mp4', d['B1']) + ([(330, 440, 860, 1130)],)],
     'B2': [B.shot(T, 's_b2', f'{HF}/k_huele_0.mp4', d['B2'], ss=0.05, speed=1.24, z0=1.0, z1=1.04)],
     'B3': [B.shot(T, 's_b3', f'{HF}/k_tapa_0.mp4', d['B3'], ss=0.2, z0=1.0, z1=1.14, fx=0.5, fy=0.45)],
     'B4': [B.shot(T, 's_b4', f'{HF}/fixed/k_grifo_m_0.mp4', d['B4'], ss=0.0, z0=1.0, z1=1.05)],
     'B5': [B.shot(T, 's_b5', f'{HF}/fixed/m_aplicar2_still2x.png', d['B5'], still=True, z0=1.0, z1=1.06) + ([(330, 330, 620, 720), (690, 960, 860, 1260)],)],
     'B6': [B.shot(T, 's_b6a', f'{HF}/fixed/k_tres_0.mp4', 1.53, ss=0.3, speed=0.8, z0=1.0, z1=1.04),
            B.shot(T, 's_b6b', f'{HF}/fixed/k_toalla_0.mp4', d['B6'] - 1.53, ss=0.0, speed=0.6, z0=1.0, z1=1.05)],
     'B7': [B.shot(T, 's_b7a', f'{T}/land.mp4', LAND) + ([],),
            B.shot(T, f's_b7b_{d["B7"]:.2f}', ec, d['B7'] - LAND, still=True, z0=1.0, z1=1.05) + ([ec_box],)],
    }
    return s

if __name__ == '__main__':
    shots = build_shots(cfg)
    for hk in sys.argv[1:] or ['HA', 'HB']:
        B.build(cfg, hk, shots)
