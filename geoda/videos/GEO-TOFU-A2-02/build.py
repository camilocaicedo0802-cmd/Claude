#!/usr/bin/env python3
"""GEO-TOFU-A2-02 · Estilo Pixar (3D) · ~30 s (x1,12) · CTA principal K2 Navidad + alterno K3 Llévala hoy.
Ángulo A2: personajes estilizados, sin antes/después, frascos genéricos sin marca, nunca 'blanquear'/'aclarar'.
NO PUBLICAR hasta que Alberto confirme el alcance del registro sanitario (brief).
Voces (Gemini TTS, mismo modelo en todas): narrador Charon, frasco Fenrir, Geo Puck, Valentina Leda.
Labios: Geo no tiene boca (voz en off); Valentina habla en voz en off (no mueve la boca); el único que mueve la boca es el
frasco en B2, que es quien grita '¡Más fragancia!'. Producto REAL: B7 (clip real del kit) y el cierre.
Versiones: HA y HB del brief con K2; HC y HD nuevos con K3."""
import os, sys, copy
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a202'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
SPEED = 1.12

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

base = dict(
    id='GEO_TOFU_A2_02', fmt='PIXAR', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0 * SPEED, speed=SPEED, music=f'{AU}/music_805.mp3', music_vol=0.11,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Tu axila vive en una', 'guerra de perfumes'),
                   line='Tu axila vive en una guerra de perfumes. Y lo sabe.', sfx=[(0.1, f'{AU}/sfx_thud.wav', 0.5), (0.7, f'{AU}/sfx_thud.wav', 0.4)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('Lo que tus axilas te dirían', 'si hablaran'),
                   line='Si tus axilas hablaran, te dirían esto.'),
        # hooks nuevos para el CTA alterno (Llévala hoy): escenas distintas al cuerpo y a los otros hooks
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Los frascos de tu baño tienen', 'un secreto'),
                   line='Los frascos de tu baño tienen un secreto que no quieren que sepas.'),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('Alerta en el baño:', 'llegó alguien sin olor'),
                   line='Alerta en el baño: llegó alguien que no huele a nada.', sfx=[(0.2, f'{AU}/sfx_error.wav', 0.25)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Valentina se echaba perfume encima de perfume.', head='Perfume x3'),
        dict(key='B2', vo='B2', dur=vd('B2'), line='¡Más fragancia, más fragancia!', sub_y=520),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Y ella seguía con los brazos pegados al cuerpo.', head='Brazos pegados 😬'),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Hasta que, al fondo del cajón, encontró a alguien distinto.', head='¿Y tú quién eres?',
             sfx=[(0.3, f'{AU}/sfx_glint.wav', 0.35)]),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Soy una piedra mineral. Yo no tapo con perfume, yo neutralizo.', sub_y=420),
        dict(key='B6', vo='B6', dur=vd('B6'), line='Un poco de agua, cada mañana.', icon='💧', sub_y=480, sfx=[(0.1, f'{AU}/sfx_drip.wav', 0.4), (0.6, f'{AU}/sfx_drip.wav', 0.35)]),
        dict(key='B7', vo='B7', dur=vd('B7'), line='Desde que dejé el perfume, mis axilas lucen más parejas.'),
        dict(key='B8', vo='B8', dur=vd('B8', 0.4), line='Se llama GEODA: una piedra que sí se usa todos los días. Regálala esta Navidad: paga dos, lleva tres.'),
    ],
    cta=dict(row='B8', delay=0.2, l1='REGALO DE NAVIDAD', l2='Paga 2 lleva 3'),
)
k3 = copy.deepcopy(base); k3['fmt'] = 'PIXAR_K3'
k3['body'][-1] = dict(key='B8', vo='B8k3', dur=vd('B8k3', 0.5), line='Se llama GEODA. Pruébala: pídela hoy y la pagas cuando te llegue.')
k3['cta'] = dict(row='B8', delay=0.2, l1='PÍDELA HOY', l2='La pagas cuando te llegue')

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/k_{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    p7 = 2.25   # B7: Valentina en el parque / GEODA real
    b8 = ([B.shot(T, f's_b8k3_{d["B8"]:.2f}', f'{KIT}/producto/endcard_bano_anim.mp4', d['B8'], ss=0.5, z0=1.0, z1=1.14, fx=0.5, fy=0.62)
           + ([(259, 940, 801, 1620)],)] if cfg['fmt'].endswith('K3') else
          [B.shot(T, f's_b8nav2_{d["B8"]:.2f}', f'{T}/xmas_ec_bow.mp4', d['B8'], z0=1.0, z1=1.12, fx=0.5, fy=0.62) + ([(320, 940, 880, 1620)],)])
    return {
        # hooks: el tercio de arriba vacío (título); cajas = caras de los personajes en todo el plano
        'HA': [B.shot(T, f's_ha_{d["HA"]:.2f}', k('p_ha'), d['HA'], z0=1.0, z1=1.04) + ([(0, 880, 1080, 1420)],)],
        'HB': [B.shot(T, f's_hb_{d["HB"]:.2f}', k('p_hb2'), d['HB'], z0=1.0, z1=1.05) + ([(280, 540, 780, 1080)],)],
        'HC': [B.shot(T, f's_hc_{d["HC"]:.2f}', k('p_hc'), d['HC'], z0=1.0, z1=1.05) + ([(0, 1080, 780, 1500)],)],
        'HD': [B.shot(T, f's_hd_{d["HD"]:.2f}', k('p_hd'), d['HD'], z0=1.0, z1=1.06) + ([(0, 1280, 920, 1720)],)],
        'B1': [B.shot(T, f's_b1_{d["B1"]:.2f}', k('p_b1'), d['B1'], z0=1.0, z1=1.04) + ([(180, 0, 720, 580)],)],
        'B2': [B.shot(T, f's_b2_{d["B2"]:.2f}', k('p_b2'), d['B2'], z0=1.0, z1=1.05) + ([(140, 700, 940, 1500)],)],
        'B3': [B.shot(T, f's_b3_{d["B3"]:.2f}', k('p_b3'), d['B3'], speed=0.85, z0=1.0, z1=1.04) + ([(0, 120, 1080, 820)],)],
        'B4': [B.shot(T, f's_b4_{d["B4"]:.2f}', k('p_b4'), d['B4'], z0=1.0, z1=1.05) + ([(220, 740, 740, 1140)],)],
        'B5': [B.shot(T, f's_b5_{d["B5"]:.2f}', k('p_b5'), d['B5'], speed=0.92, z0=1.0, z1=1.10) + ([(130, 880, 960, 1660), (0, 400, 1080, 740)],)],
        'B6': [B.shot(T, f's_b6_{d["B6"]:.2f}', k('p_b6'), d['B6'], z0=1.0, z1=1.05) + ([(130, 930, 920, 1560)],)],
        'B7': [B.shot(T, 's_b7a', k('p_b7'), p7, ss=0.0, z0=1.0, z1=1.04) + ([(230, 360, 720, 780)],),
               B.shot(T, f's_b7b_{d["B7"]:.2f}', f'{KIT}/broll/k_tapa_0.mp4', d['B7'] - p7, ss=0.3, z0=1.0, z1=1.12) + ([(300, 520, 780, 1460)],)],
        'B8': b8,
    }

if __name__ == '__main__':
    plan = {'HA': base, 'HB': base, 'HC': k3, 'HD': k3}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; B.build(cfg, hk, build_shots(cfg))
