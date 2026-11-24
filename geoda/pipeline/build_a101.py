#!/usr/bin/env python3
"""GEO-TOFU-A1-01 · UGC con avatar IA (voz y avatar hombre). Montaje con builder.py."""
import os, sys
G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
sys.path.insert(0, G)
import builder as B

A = f'{G}/a101'; TMP = f'{A}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, S = f'{G}/hf', f'{G}/stock'

cfg = dict(
    id='GEO_TOFU_A1_01', fmt='UGC', version=1, tmp=TMP, out_dir=A, vo_dir=f'{A}/vo_m',
    min_face=50, ai_label=False, hook_text_until=3.0,
    hooks={
        # texto y voz dicen lo mismo -> solo texto del hook (sin subtítulo)
        'HA': dict(vo='HA', dur=3.0, subs=False, text=('¿La botaste porque', 'no te sirvió?'),
                   line='Si botaste la piedra de alumbre porque no te sirvió, escúchame un segundo.'),
        'HB': dict(vo='HB', dur=2.5, subs=True, text=('El error #1 con', 'la piedra de alumbre'),
                   line='Casi todo el mundo se pone la piedra al revés.',
                   extras=[dict(type='bigx', x=800, y=1420, size=220, t0=0.05)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=2.4, line='Yo también la boté. Pensé que era puro cuento.'),            # titular repetía la voz
        dict(key='B2', vo='B2', dur=2.35, line='Hasta que alguien me mostró qué estaba haciendo mal.', head='El error: ¿lo adivinas?'),
        dict(key='B3', vo='B3', dur=2.1, line='La usaba seca. Así no suelta nada.', icon='❌'),
        dict(key='B4', vo='B4', dur=2.15, line='Se moja la piedra, no la axila.', icon='✅'),
        dict(key='B5', vo='B5', dur=2.45, line='Y la pasas por la axila limpia, con calma.'),
        dict(key='B6', vo='B6', dur=2.85, line='Después la secas y la guardas fuera de la ducha.'),
        dict(key='B7', vo='B7', dur=3.85, line='Con eso dejé de sentir olor a media tarde. Era yo, no la piedra.'),
        dict(key='B8', vo='B8', dur=3.4, line='No pagas nada ahora: pagas cuando te llegue.'),
    ],
    cta=dict(row='B8', l1='PAGA CONTRAENTREGA', l2='Pagas cuando te llegue', pill='Envío gratis a toda Colombia 🚚'),
    sfx={'HB': [(0.05, f'{G}/audio/sfx_2357.mp3', 0.45)]},
)

def build_shots():
    T = TMP
    ec, ec_box = B.endcard(T)
    s = {}
    s['HA'] = [B.shot(T, 'ha', f'{HF}/m_caneca_0.mp4', 3.0, ss=0.0, speed=0.55, z0=1.0, z1=1.06)]
    s['HB'] = [B.shot(T, 'hb', f'{HF}/m_xfrente_0.mp4', 2.5, ss=0.0, z0=1.0, z1=1.04, framed=0.7)]
    # el stick sale pequeño y su etiqueta no queda perfecta -> encuadre más cerrado arriba, sin el producto
    s['B1'] = [B.shot(T, 'b1', f'{HF}/m_tina_0.mp4', 2.4, ss=0.0, z0=1.34, z1=1.38, fx=0.5, fy=0.0)]
    # primer plano nuevo (imagen con referencia del producto + Kling) con la etiqueta real; mentón protegido arriba
    s['B2'] = [B.shot(T, 'b2', f'{HF}/fixed/k_error_0.mp4', 2.35, ss=0.0, speed=0.93, z0=1.0, z1=1.05) + ([B.protect((300, 0, 800, 170))],)]
    # piedra seca frotada en la axila; solo el tramo antes de que el tubo se mueva rápido (etiqueta real, --tube --wipe)
    s['B3'] = [B.shot(T, 'b3', f'{HF}/fixed/k_seca_0.mp4', 2.1, ss=0.0, speed=0.55, z0=1.0, z1=1.05) + ([],)]
    # gotas solo en la punta de la piedra (el tubo queda seco), mano de hombre; etiqueta real
    s['B4'] = [B.shot(T, 'b4', f'{HF}/fixed/k_grifo_m_0.mp4', 2.15, ss=0.0, z0=1.0, z1=1.08) + ([],)]
    # imagen fija: zona de la etiqueta borrada completa y etiqueta real pegada al doble de resolución
    s['B5'] = [B.shot(T, 'b5', f'{HF}/fixed/m_aplicar2_still2x.png', 2.45, still=True, z0=1.0, z1=1.1)]
    s['B6'] = [B.shot(T, 'b6a', f'{S}/hi_35928.mp4', 0.75, ss=5.0, z0=1.0, z1=1.06, fx=0.55) + ([],),
               B.shot(T, 'b6b', f'{HF}/k_toalla_0.mp4', 2.1, ss=0.0, speed=0.76, z0=1.0, z1=1.06) + ([],)]  # solo 0-1,6 s: después la etiqueta gira
    s['B7'] = [B.shot(T, 'b7', f'{HF}/m_oficina_0.mp4', 3.85, ss=0.0, z0=1.0, z1=1.04)]
    s['B8'] = [B.shot(T, 'b8a', f'{S}/hi_42130.mp4', 1.4, ss=0.3, z0=1.0, z1=1.06) + ([],),
               B.shot(T, 'b8b', ec, 2.0, still=True, z0=1.0, z1=1.04) + ([ec_box],)]
    return s

if __name__ == '__main__':
    shots = build_shots()
    for hk in sys.argv[1:] or ['HA', 'HB']:
        B.build(cfg, hk, shots)
