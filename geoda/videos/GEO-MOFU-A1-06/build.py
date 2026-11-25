#!/usr/bin/env python3
"""GEO-MOFU-A1-06 · POV 'segunda oportunidad' · 30 s · CTA K4 Se agota rápido (+ alterno K2 Navidad, sin precio).
Voz en off de un narrador (una sola toma, Zubenelgenubi), planos en primera persona, nadie mueve los labios con la voz.
Producto real: lavamanos (recorte real) y estante con 3 unidades reales en el cierre."""
import os, sys, copy
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a106'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
K = f'{G}/kit' if os.path.isdir(f'{G}/kit') else None
GRIFO = f'{K}/broll/k_grifo_m_0.mp4' if K else f'{HF}/fixed/k_grifo_m_0.mp4'

base = dict(
    id='GEO_MOFU_A1_06', fmt='POV', version=5, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_847.mp3', music_vol=0.12,
    hooks={
        'HA': dict(vo='HA', dur=3.0, subs=True, text=('POV: por fin aprendiste', 'a usar la piedra'),
                   line='POV: le diste una segunda oportunidad.', sub_y=900, sub_cx=215, sub_scale=0.8, hook_slots=[360], sfx=[(1.95, f'{AU}/sfx_soplo.wav', 0.6)]),
        'HB': dict(vo='HB', dur=3.35, subs=True, text=('POV: tu mamá tenía razón', 'con la piedra'),
                   line='Mi mamá usaba esto y yo me reía.'),
    },
    body=[  # filas de ~3 s como el brief; la hora va en pantalla (la voz no la dice)
        dict(key='B1', vo='B1', dur=2.9, line='Le diste una segunda oportunidad.', sfx=[(0.0, f'{AU}/amb_ducha.wav', 0.35)]),
        dict(key='B2', vo='B2', dur=2.7, line='Esta vez, la mojas primero.', icon='💧', sub_y=905, sfx=[(0.1, f'{AU}/splash_1180.mp3', 0.35)]),
        dict(key='B3', vo='B3', dur=2.7, line='Piel limpia, pasadas suaves.'),
        dict(key='B4', vo='B4', dur=3.2, line='Camisa, y para la calle.', head='7:00 a. m.'),
        dict(key='B5', vo='B5', dur=2.6, line='Bus lleno.', head='8:00 a. m. 🚌', sfx=[(0.0, f'{AU}/amb_bus.wav', 0.5)]),
        dict(key='B6', vo='B6', dur=2.7, line='Reunión, brazos arriba en el tablero.', head='11:00 a. m.'),
        dict(key='B7', vo='B7', dur=2.9, line='Y a las seis... nada de qué preocuparte.', head='6:00 p. m. 😌'),
        dict(key='B8', vo='B8', dur=2.9, line='Tu mamá tenía razón. Solo había que usarla bien.'),
        dict(key='B9', vo='B9', dur=4.6, line='Este lote se está yendo rápido. Asegura la tuya antes de que se agote.'),
    ],
    cta=dict(row='B9', delay=0.25, l1='ÚLTIMAS UNIDADES DEL LOTE', l2='Asegura la tuya'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'POV_K2'
k2['body'][-1] = dict(key='B9', vo='B9k2', dur=6.9, line='Regala algo que sí se usa todos los días: GEODA. Paga dos, lleva tres, y reparte en Navidad.')
k2['cta'] = dict(row='B9', delay=0.25, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3')

def build_shots(cfg):
    T = TMP
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    k = lambda n: f'{HF}/{n}_0.mp4'
    return {
        # la persona siempre en video haciendo algo (regla de Camilo): nada de fotos fijas del avatar
        'HA': [B.shot(T, 's_ha3', k('k_j_cajon'), d['HA'], z0=1.0, z1=1.03) + ([(380, 460, 720, 1400)],)],   # pantalla completa
        'HB': [B.shot(T, 's_hb2', k('k_j_mama'), d['HB'], speed=0.9, z0=1.0, z1=1.04) + ([(140, 800, 650, 1460)],)],
        'B1': [B.shot(T, 's_b1', k('k_j_ducha'), d['B1'], z0=1.0, z1=1.05)],
        'B2': [B.shot(T, 's_b2', GRIFO, d['B2'], z0=1.0, z1=1.05)],
        # se aplica GEODA (tramo 0-1,5 s, etiqueta de frente, en cámara lenta interpolada)
        'B3': [B.shot(T, 's_b3p', k('k_j_pasadas'), d['B3'], z0=1.0, z1=1.05)],   # pasadas suaves: la piedra no deja residuo
        'B4': [B.shot(T, 's_b4', k('k_j_camisa'), d['B4'], speed=0.92, z0=1.0, z1=1.04)],
        'B5': [B.shot(T, 's_b5', k('k_j_bus'), d['B5'], z0=1.0, z1=1.04)],
        'B6': [B.shot(T, 's_b6', k('k_j_tablero'), d['B6'], z0=1.0, z1=1.04)],
        # llegada a casa: cuelga la chaqueta y estira el cuello con alivio, de espaldas (sin labios que no coincidan con la voz)
        'B7': [B.shot(T, 's_b7back', k('k_j_casa_back'), d['B7'], z0=1.0, z1=1.04)],
        'B8': [B.shot(T, f's_b8b_{d["B8"]:.2f}', f'{T}/b8_lavamanos_anim.mp4', d['B8'], z0=1.0, z1=1.14, fx=0.48, fy=0.65) + ([(361, 1030, 699, 1430)],)],   # animado
        'B9': [B.shot(T, f's_b9c_{d["B9"]:.2f}', f'{T}/cta_estante_anim.mp4', d['B9'], z0=1.0, z1=1.24, fx=0.52, fy=0.55) + ([(240, 806, 911, 1236)],)],   # animado
    }

if __name__ == '__main__':
    for cfg in ([base, k2] if len(sys.argv) < 2 else [base if sys.argv[1] == 'K4' else k2]):
        shots = build_shots(cfg)
        for hk in ['HA', 'HB']:
            B.build(cfg, hk, shots)
