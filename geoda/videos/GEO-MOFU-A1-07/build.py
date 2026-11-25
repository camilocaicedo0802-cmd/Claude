#!/usr/bin/env python3
"""GEO-MOFU-A1-07 · Faceless / motion graphics '3 errores' · ~35 s · CTA K7 '1 piedra te dura 1 año'.
Narradora en off (Valeria, Zephyr). Todo animado (mg.py): fondo con burbujas que suben, producto = recorte real.
B9 = video real del producto (kit k_tapa). Sin rótulo IA. Ningún texto tapa la piedra ni la etiqueta (cajas por escena)."""
import os, sys
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a107'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
AU = f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

cfg = dict(
    id='GEO_MOFU_A1_07', fmt='MOTION', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_821.mp3', music_vol=0.10,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=True, text=('3 errores que hacen', 'que la piedra “no sirva”'),
                   line='Estos tres errores hacen que la piedra de alumbre no te funcione.',
                   sfx=[(0.40, f'{AU}/sfx_thud.wav', 0.55), (0.90, f'{AU}/sfx_thud.wav', 0.55), (1.40, f'{AU}/sfx_thud.wav', 0.6), (1.45, f'{AU}/sfx_error.wav', 0.25)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=True, text=('Si te pasa esto,', 'la estás usando mal'),
                   line='Si la piedra no te funcionó, seguro cometiste uno de estos errores.',
                   sfx=[(0.0, f'{AU}/sfx_alarma.wav', 0.16)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1', 0.15), line='Error número uno: usarla seca.',
             sfx=[(0.0, f'{AU}/sfx_error.wav', 0.25), (0.15, f'{AU}/sfx_scratch.wav', 0.30)]),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Seca no suelta nada. Se moja la piedra, no la axila.',
             sfx=[(0.35, f'{AU}/sfx_drip.wav', 0.4), (0.91, f'{AU}/sfx_drip.wav', 0.4), (1.47, f'{AU}/sfx_drip.wav', 0.4), (2.03, f'{AU}/sfx_drip.wav', 0.4)]),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Error número dos: saltarte días.', sfx=[(0.0, f'{AU}/sfx_error.wav', 0.25)]),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Hay quien cuenta que si la deja uno o dos días, vuelve el olor.',
             sfx=[(0.35, f'{AU}/sfx_type.wav', 0.25)]),
        dict(key='B5', vo='B5', dur=vd('B5', 0.13), line='La constancia es lo que hace que funcione.', sfx=[(1.2, f'{AU}/sfx_chime.wav', 0.3)]),
        dict(key='B6', vo='B6', dur=vd('B6'), line='Error número tres, el peor: guardarla mojada en la ducha.',
             sfx=[(0.0, f'{AU}/amb_ducha.wav', 0.3), (0.0, f'{AU}/sfx_error.wav', 0.25)]),
        dict(key='B7', vo='B7', dur=vd('B7', 0.17), line='Ahí se agrieta y se daña.', sfx=[(0.3, f'{AU}/sfx_crack.wav', 0.7)]),
        dict(key='B8', vo='B8', dur=vd('B8'), line='Lo correcto: mojar, aplicar, secar y guardar.'),
        dict(key='B9', vo='B9', dur=vd('B9', 0.17), line='Así la piedra trabaja y te rinde.', sfx=[(0.1, f'{AU}/sfx_glint.wav', 0.3)]),
        dict(key='B10', vo='B10', dur=vd('B10'), line='Y si aun así no te funciona, tienes catorce días de garantía.',
             sfx=[(0.40, f'{AU}/sfx_thud.wav', 0.6)]),
        dict(key='B11', vo='B11', dur=vd('B11', 0.43), line='Una piedra te dura un año. Haz la cuenta de cuántos frascos te ahorras.',
             sfx=[(0.45, f'{AU}/sfx_1489.mp3', 0.15)]),
    ],
    cta=dict(row='B11', delay=0.2, l1='1 PIEDRA = 1 AÑO', l2='Ahorra vs. desodorante'),
)

# zonas que ningún texto tapa (producto, etiqueta, calendario, tarjetas, sellos) en coordenadas 1080x1920
BOX = {
    'HA': [(40, 800, 1040, 1780)],
    'HB': [(380, 560, 700, 840), (300, 1030, 780, 1570)],
    'B1': [(200, 480, 880, 640), (0, 1035, 1080, 1460)],
    'B2': [(255, 840, 825, 1500)],
    'B3': [(320, 265, 760, 415), (90, 660, 990, 1310)],
    'B4': [(70, 880, 1000, 1400)],
    'B5': [(90, 660, 990, 1310)],
    'B6': [(290, 890, 790, 1510), (120, 480, 540, 640), (590, 240, 910, 450)],
    'B7': [(180, 690, 900, 1310), (720, 300, 960, 540)],
    'B8': [(90, 570, 990, 1350)],
    'B9': [(300, 520, 780, 1460)],
    'B10': [(320, 420, 760, 860), (290, 1050, 790, 1630)],
    'B11': [(10, 800, 1000, 1560)],
}

def build_shots(cfg):
    T = TMP
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    sh = {}
    for k in d:
        src = f'{KIT}/broll/k_tapa_0.mp4' if k == 'B9' else f'{T}/mg_{k.lower()}.mp4'
        z1 = 1.06 if k == 'B9' else 1.04
        sh[k] = [B.shot(T, f's_{k.lower()}_{d[k]:.2f}', src, d[k], z0=1.0, z1=z1) + (BOX[k],)]
    return sh

if __name__ == '__main__':
    shots = build_shots(cfg)
    for hk in sys.argv[1:] or ['HA', 'HB']:
        B.build(cfg, hk, shots)
