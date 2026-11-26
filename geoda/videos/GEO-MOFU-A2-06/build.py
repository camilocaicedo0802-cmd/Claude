#!/usr/bin/env python3
"""GEO-MOFU-A2-06 · Comparación piedra vs frasco · ~32 s · CTA principal K8 Combo para regalar (Paga 2 lleva 3) + alterno K1 Black Friday.
Natalia (M, ~32, Bogotá), voz en off Gemini TTS Aoede (una sola toma); labios cerrados donde sale. Frasco = aerosol genérico
SIN marca ni texto (compliance: no nombrar ni mostrar marcas; del frasco solo cosas verificables o 'me pasaba').
NO PUBLICAR hasta que Alberto confirme el registro sanitario (ángulo A2).
Versiones: HA y HB con K8; HC y HD (hooks nuevos) con K1. HB del brief repetía B1+B2 palabra por palabra: su voz pasa a
'Frasco contra piedra. Te muestro la diferencia.' En el HA se quita la fila B7 ('Por eso yo cambié', ya está en el hook).
Piezas locales (mg206.py): VS del hook B, calendario de 12 meses (B4) y cierre con tres GEODA reales, dos con moño (B10)."""
import os, sys, copy, subprocess
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a206'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
CTA_BF = f'{G}/a108/tmp/cta_bf.mp4'

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

base = dict(
    id='GEO_MOFU_A2_06', fmt='COMP', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_847.mp3', music_vol=0.09,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Por qué cambié el frasco', 'perfumado por una piedra'),
                   line='Mi axila no quería más perfume. Por eso cambié.', sfx=[(0.05, f'{AU}/sfx_soplo.wav', 0.35)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('Frasco con fragancia', 'vs. una piedra mineral'),
                   line='Frasco contra piedra. Te muestro la diferencia.', sfx=[(0.42, f'{AU}/sfx_thud.wav', 0.7)]),
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Este Black Friday cambié', 'el frasco por una piedra'),
                   line='Este Black Friday cambié el frasco por una piedra. Te cuento por qué.'),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('Lo que nadie te dice', 'del desodorante en frasco 👇'),
                   line='Lo que nadie te dice del desodorante en frasco.'),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='De un lado, un frasco con fragancia.', head='Frasco: fragancia'),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Del otro, una piedra mineral sin perfume.', head='Piedra: sin perfume', sub_y=470),
        dict(key='B3', vo='B3', dur=vd('B3'), line='El frasco se acaba en semanas.', head='Se acaba', sfx=[(0.05, f'{AU}/sfx_soplo.wav', 0.2)]),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Una piedra te dura un año si la cuidas.', head='1 piedra = 1 año', sub_y=470, sub_cx=380, sub_scale=0.9),
        dict(key='B5', vo='B5', dur=vd('B5'), line='El de barra me dejaba rayas blancas en la ropa negra.', head='Rayas blancas'),
        dict(key='B6', vo='B6', dur=vd('B6'), line='La piedra se moja, se pasa y listo.', head='Mojar y listo', sub_y=470,
             sfx=[(0.1, f'{AU}/splash_1180.mp3', 0.3)]),
        dict(key='B7', vo='B7', dur=vd('B7'), line='Por eso yo cambié.', head='Por eso cambié', sfx=[(0.55, f'{AU}/sfx_thud.wav', 0.5)]),
        dict(key='B8', vo='B8', dur=vd('B8'), line='Y con el tiempo, mis axilas lucen más parejas. Experiencia mía.', head='Lucen más parejas (mi experiencia)'),
        dict(key='B9', vo='B9', dur=vd('B9'), line='Piedra GEODA, con catorce días de garantía.', head='14 días de garantía ✅', sub_y=470),
        dict(key='B10', vo='B10', dur=vd('B10', 0.5), line='Paga dos y lleva tres: una para ti y dos para regalar. Pídelo hoy.',
             sfx=[(2.2, f'{AU}/sfx_tap.wav', 0.5), (3.6, f'{AU}/sfx_tap.wav', 0.5)]),
    ],
    cta=dict(row='B10', delay=0.2, l1='PAGA 2 LLEVA 3', l2='Una para ti y dos para regalar'),
)
k1 = copy.deepcopy(base); k1['fmt'] = 'COMP_K1'
k1['body'][-1] = dict(key='B10', vo='B10k1', dur=vd('B10k1', 0.5), line='Es Black Friday en GEODA: paga dos y lleva tres, y pagas cuando te llegue.',
                      sfx=[(1.6, f'{AU}/sfx_tap.wav', 0.5), (3.4, f'{AU}/sfx_tap.wav', 0.5)])
k1['cta'] = dict(row='B10', delay=0.2, l1='BLACK FRIDAY', l2='Paga 2 lleva 3')
ha = copy.deepcopy(base); ha['body'] = [r for r in ha['body'] if r['key'] != 'B7']   # nada se repite entre hook y cuerpo

def mg(name, dur):
    out = f'{TMP}/m6_{name}.mp4'
    if not os.path.exists(out) or B.dur_of(out) < dur:
        subprocess.run([sys.executable, f'{AQUI}/mg206.py', name, f'{dur + 0.3:.2f}'], check=True)
    return out

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    d.setdefault('B7', 1.03)
    if cfg['fmt'].endswith('K1'):
        cta = [B.shot(T, f's6_b10bf_{d["B10"]:.2f}', CTA_BF, d['B10'], z0=1.0, z1=1.09, fx=0.5, fy=0.62) + ([(259, 940, 801, 1620), (75, 500, 405, 930), (400, 720, 880, 880)],)]
    else:
        cta = [B.shot(T, f's6_b10k8_{d["B10"]:.2f}', mg('cta3', 5.1), d['B10'], z0=1.0, z1=1.04) + ([(100, 820, 980, 1470), (300, 630, 780, 770)],)]
    return {
        'HA': [B.shot(T, f's6_ha_{d["HA"]:.2f}', k('k_c_ha'), d['HA'], z0=1.0, z1=1.2, fx=0.55, fy=0.72) + ([(200, 700, 860, 1620)],)],
        'HB': [B.shot(T, f's6_hb_{d["HB"]:.2f}', mg('vs', 3.2), d['HB'], z0=1.0, z1=1.0) + ([(560, 650, 1020, 1300), (150, 520, 420, 1450), (420, 495, 660, 735)],)],
        'HC': [B.shot(T, f's6_hc_{d["HC"]:.2f}', k('k_c_hc'), d['HC'], speed=1.15, z0=1.0, z1=1.18, fx=0.55, fy=0.6) + ([(480, 660, 760, 1330)],)],
        'HD': [B.shot(T, f's6_hd_{d["HD"]:.2f}', k('k_n_hd'), d['HD'], z0=1.0, z1=1.03) + ([(250, 520, 820, 1150), (40, 900, 300, 1500), (650, 1000, 980, 1450)],)],
        'B1': [B.shot(T, f's6_b1_{d["B1"]:.2f}', k('k_c_b1'), d['B1'], z0=1.0, z1=1.24, fy=0.55)],
        'B2': [B.shot(T, f's6_b2_{d["B2"]:.2f}', k('k_c_b2'), d['B2'], z0=1.0, z1=1.22, fx=0.45, fy=0.6) + ([(300, 700, 1000, 1560)],)],
        'B3': [B.shot(T, f's6_b3_{d["B3"]:.2f}', k('k_c_b3'), d['B3'], ss=1.2, z0=1.0, z1=1.16, fy=0.5)],
        'B4': [B.shot(T, f's6_b4_{d["B4"]:.2f}', mg('cal', 2.9), d['B4'], z0=1.0, z1=1.0) + ([(300, 700, 1000, 1560), (660, 450, 940, 730)],)],
        'B5': [B.shot(T, f's6_b5_{d["B5"]:.2f}', k('k_c_b5'), d['B5'], z0=1.0, z1=1.04)],
        'B6': [B.shot(T, f's6_b6_{d["B6"]:.2f}', f'{KIT}/broll/k_grifo2_0.mp4', d['B6'], ss=0.2, z0=1.0, z1=1.06) + ([(350, 560, 960, 1560)],)],
        'B7': [B.shot(T, f's6_b7_{d["B7"]:.2f}', k('k_n_b7'), d['B7'], ss=0.3, speed=1.5, z0=1.0, z1=1.03) + ([(280, 380, 740, 860)],)],
        'B8': [B.shot(T, f's6_b8_{d["B8"]:.2f}', k('k_n_b8'), d['B8'], z0=1.0, z1=1.04) + ([(430, 480, 650, 720)],)],
        'B9': [B.shot(T, f's6_b9_{d["B9"]:.2f}', f'{KIT}/broll/k_tapa_0.mp4', d['B9'], ss=0.0, z0=1.0, z1=1.12) + ([(300, 520, 780, 1460)],)],
        'B10': cta,
    }

if __name__ == '__main__':
    plan = {'HA': ha, 'HB': base, 'HC': k1, 'HD': k1}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; B.build(cfg, hk, build_shots(cfg))
