#!/usr/bin/env python3
"""GEO-BOFU-A1-10 · UGC con avatar IA (Sara, M) · ~23 s a 1,15x · CTA principal K7 '1 piedra = 1 año' + alterno K3 'Pruébala hoy'.
Voz en off de Sara (Gemini TTS Despina, una sola toma). Sara nunca habla a cámara: labios cerrados en todos los tramos usados
(revisado cuadro a cuadro: se descartan B1 desde 3,1 s y B4 antes de 3,3 s porque abre la boca).
Estructura: HOOK → PROBLEMA (B1 oficina + reloj) → PRODUCTO (B2) → SOLUCIÓN (B3 mojar/aplicar + B4 llega tranquila) → CTA (B5).
Versiones: HA y HB con K7; HC y HD (hooks nuevos) con K3. Todo el video a 1,15x (BOFU 18-24 s). Sin rótulo IA.
Encuadre FR: cabeza en el centro y pared vacía arriba (siempre pantalla completa: HA, HB y HD con zoom anclado arriba que baja la cabeza; el HC se regeneró con la cabeza a media altura)."""
import os, sys, copy
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a110'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
MG_ANIO = f'{G}/a107/tmp/mg_b11.mp4'   # GEODA real junto a frascos genéricos tachados (A1-07)
SPEED = 1.15

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

base = dict(
    id='GEO_BOFU_A1_10', fmt='UGC', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO, speed=SPEED,
    min_face=50, ai_label=False, hook_text_until=3.0 * SPEED, music=f'{AU}/music_805.mp3', music_vol=0.10,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Pensé que la piedra', 'era puro cuento…'),
                   line='Pensé que la piedra era puro cuento, hasta que la usé bien.', sfx=[(1.4, f'{AU}/sfx_glint.wav', 0.3)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('Mi hermana se burló de', 'cómo me ponía la piedra 😬'),
                   line='Mi hermana se burló de cómo me ponía la piedra.'),
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Lo único que hago', 'cada mañana ✅'),
                   line='Esto es lo único que hago cada mañana y ya no me preocupo por el olor.', sfx=[(3.0, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('La piedra de la abuela', 'sí funciona 👇'),
                   line='La piedra de la abuela sí funciona, si la usas bien.'),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Me la pasaba seca, rapidito, y a media tarde ya sentía olor.', sfx=[(1.7, f'{AU}/sfx_clock.wav', 0.3)]),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Es GEODA: piedra de alumbre natural, sin perfume.', sub_y=1190, sub_cx=620,   # abajo a la derecha: arriba rozaba el pelo y a la izquierda está la piedra
             sfx=[(0.3, f'{AU}/sfx_glint.wav', 0.3)]),
        # B3 partida en dos filas (misma toma de voz cortada en la pausa de 'mojo,'): el subtítulo de la aplicación va fijo abajo a la derecha,
        # lejos de la cara y de la piedra
        dict(key='B3a', vo='B3a', dur=vd('B3a'), line='Ahora la mojo,', sfx=[(0.1, f'{AU}/splash_1180.mp3', 0.3)]),
        dict(key='B3b', vo='B3b', dur=vd('B3b'), line='la paso por la axila limpia y la dejo secar.', sub_y=1190, sub_cx=620),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Y llego a la noche tranquila.'),
        dict(key='B5', vo='B5', dur=vd('B5', 0.4), line='Una piedra te dura un año: haz la cuenta de cuántos frascos te ahorras. Y si en catorce días no te funciona, te devolvemos tu dinero.',
             sfx=[(0.45, f'{AU}/sfx_1489.mp3', 0.15)]),
    ],
    cta=dict(row='B5', delay=0.2, l1='1 PIEDRA = 1 AÑO', l2='Garantía de 14 días'),
)
k3 = copy.deepcopy(base); k3['fmt'] = 'UGC_K3'
k3['body'][-1] = dict(key='B5', vo='B5k3', dur=vd('B5k3', 0.5), line='Se llama GEODA. Pruébala: pídela hoy y la pagas cuando te llegue.')
k3['cta'] = dict(row='B5', delay=0.2, l1='PRUÉBALA HOY', l2='La pagas cuando te llegue')

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    c1, c2 = 1.7, 1.6                     # B1: Sara (0-1,7) / reloj de pared (inserto) / Sara baja el brazo (1,7-3,1 a 0,8x)
    if cfg['fmt'].endswith('K3'):
        cta = [B.shot(T, f's10_b5ec_{d["B5"]:.2f}', f'{KIT}/producto/endcard_bano_anim.mp4', d['B5'], z0=1.0, z1=1.08, fx=0.5, fy=0.62) + ([(259, 940, 801, 1620)],)]
    else:
        e = d['B5'] - 4.4
        cta = [B.shot(T, 's10_b5anio', MG_ANIO, 4.4, z0=1.0, z1=1.03) + ([(10, 800, 1000, 1560)],),
               B.shot(T, f's10_b5ec_{e:.2f}', f'{KIT}/producto/endcard_bano_anim.mp4', e, z0=1.0, z1=1.06, fx=0.5, fy=0.62) + ([(259, 940, 801, 1620)],)]
    return {
        'HA': [B.shot(T, f's10_ha3_{d["HA"]:.2f}', k('k_s_ha'), d['HA'], ss=0.1, z0=1.10, z1=1.12, fy=0.0) + ([(362, 666, 917, 1277), (52, 910, 318, 1332)],)],
        'HB': [B.shot(T, f's10_hb3_{d["HB"]:.2f}', k('k_s_hb'), d['HB'], ss=0.0, z0=1.13, z1=1.15, fy=0.0) + ([(174, 593, 836, 1311), (37, 730, 379, 1117), (722, 1231, 1064, 1801)],)],
        'HC': [B.shot(T, f's10_hc3_{d["HC"]:.2f}', k('k_s_hc2'), d['HC'], ss=0.0, z0=1.06, z1=1.09, fy=0.0) + ([(250, 540, 700, 1000), (700, 1150, 920, 1480), (380, 600, 760, 1300)],)],
        'HD': [B.shot(T, f's10_hd3_{d["HD"]:.2f}', k('k_s_hd'), d['HD'], ss=0.0, z0=1.12, z1=1.14, fy=0.0) + ([(136, 633, 969, 1300), (404, 1243, 788, 1639)],)],
        'B1': [B.shot(T, 's10_b1a', k('k_s_b1'), c1, ss=0.0, z0=1.0, z1=1.04) + ([(280, 360, 760, 860)],),
               B.shot(T, 's10_b1reloj', k('k_a9_b1'), c2, ss=0.5, z0=2.5, z1=2.65, fx=0.62, fy=0.08),
               B.shot(T, f's10_b1b_{d["B1"]:.2f}', k('k_s_b1'), d['B1'] - c1 - c2, ss=c1, speed=0.8, z0=1.04, z1=1.07) + ([(280, 360, 760, 860)],)],
        'B2': [B.shot(T, f's10_b2_{d["B2"]:.2f}', k('k_s_b2'), d['B2'], ss=0.0, z0=1.0, z1=1.03) + ([(330, 500, 880, 1150), (60, 780, 500, 1350)],)],
        'B3a': [B.shot(T, f's10_b3a_{d["B3a"]:.2f}', f'{KIT}/broll/k_grifo_m_0.mp4', d['B3a'], ss=0.3, z0=1.0, z1=1.05) + ([(350, 560, 960, 1560)],)],
        'B3b': [B.shot(T, f's10_b3b_{d["B3b"]:.2f}', k('k_s_b3b'), d['B3b'], ss=0.1, z0=1.0, z1=1.03) + ([(280, 360, 830, 1000), (40, 700, 440, 1420)],)],
        'B4': [B.shot(T, f's10_b4_{d["B4"]:.2f}', k('k_s_b4'), d['B4'], ss=3.3, speed=0.94, z0=1.0, z1=1.04) + ([(380, 420, 840, 960)],)],
        'B5': cta,
    }

if __name__ == '__main__':
    plan = {'HA': base, 'HB': base, 'HC': k3, 'HD': k3}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; B.build(cfg, hk, build_shots(cfg))
