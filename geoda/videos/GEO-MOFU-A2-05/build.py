#!/usr/bin/env python3
"""GEO-MOFU-A2-05 · Diario de 14 días (selfie) · ~41 s · CTA principal K1 Black Friday (sin precio) + alterno K2 Navidad.
Mariana (M, ~26, Cali), la misma persona y la misma voz los 14 días: voz en off Gemini TTS Callirrhoe (una sola toma).
Ella nunca habla a cámara: labios cerrados en todos los tramos usados (revisado cuadro a cuadro).
Compliance A2: sin fotos de la axila, sensaciones y no resultados medidos, 'para mí' en primera persona, sin antes/después.
NO PUBLICAR hasta que Alberto confirme el registro sanitario (regla del ángulo A2).
Versiones: HA y HB (hooks del brief) con K1; HC y HD (hooks nuevos) con K2. En el HB se quita la fila B1 ('Día uno' repetido).
Selfies del cuerpo con zoom anclado abajo (la cara sube): el 'DÍA X' y el subtítulo van bajo la barbilla, nunca sobre cara o pelo."""
import os, sys, copy, subprocess
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a205'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
SELLO = f'{G}/a107/tmp/mg_b10.mp4'                                   # sello 14 días + producto real (A1-07)
CTA_BF, CTA_NAV = f'{G}/a108/tmp/cta_bf.mp4', f'{G}/a108/tmp/cta_navidad.mp4'   # producto real + etiqueta + botón Comprar (A1-08)

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

SY = 1190   # subtítulo fijo bajo la barbilla en las selfies
TAPS = [(1.6, f'{AU}/sfx_tap.wav', 0.5), (3.4, f'{AU}/sfx_tap.wav', 0.5)]
base = dict(
    id='GEO_MOFU_A2_05', fmt='DIARIO', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_821.mp3', music_vol=0.09,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Mi diario de 14 días', 'sin perfume en las axilas'),
                   line='Catorce días usando solo la piedra. Te cuento cómo me fue.',
                   extras=[dict(type='stamp', text='0/14', x=845, y=612, t0=0.3, size=82)], sfx=[(0.3, f'{AU}/sfx_thud.wav', 0.6)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('14 días solo con piedra:', 'mi diario 👇'),
                   line='Día uno. Voy a usar solo esto por catorce días.', sfx=[(0.1, f'{AU}/sfx_scratch.wav', 0.35)]),
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Me regalaron la piedra', 'y me puse un reto 🎁'),
                   line='Me regalaron una piedra de alumbre y me puse un reto: catorce días sin perfume.', sfx=[(0.5, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('Mi hermana me retó:', '14 días solo con piedra'),
                   line='Mi hermana me retó: catorce días usando solo la piedra. Este es mi diario.'),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Día uno. Solo piedra, cero perfume.', head='DÍA 1', sub_y=SY, sub_cx=420, sub_scale=0.9),   # la piedra está a la derecha
        dict(key='B2', vo='B2', dur=vd('B2'), line='La mojo, la paso, la seco.', head='Mojar · Pasar · Secar', sub_y=470,
             sfx=[(0.1, f'{AU}/splash_1180.mp3', 0.3)]),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Día tres. Se siente raro no oler a perfume.', head='DÍA 3 · raro 🤔', sub_y=SY),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Pero no huelo mal. Huelo a piel.', head='Huelo a piel', sub_y=SY),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Día siete. Ya ni me acuerdo del frasco.', head='DÍA 7', sub_y=SY),
        dict(key='B6', vo='B6', dur=vd('B6'), line='Hoy elegí camiseta en vez de mangas largas.', head='Camiseta ✅', sub_y=SY),
        dict(key='B7', vo='B7', dur=vd('B7'), line='Día diez. Calor, y sigo tranquila.', head='DÍA 10 ☀️', sub_y=SY),
        dict(key='B8', vo='B8', dur=vd('B8'), line='Día doce. ¿Por qué no empecé antes?', head='DÍA 12', sub_y=SY),
        dict(key='B9', vo='B9', dur=vd('B9'), line='Y lo que más me gustó... te lo cuento al final.', head='Lo mejor, al final 👀', sub_y=SY,
             sfx=[(1.3, f'{AU}/sfx_1489.mp3', 0.2)]),
        dict(key='B10', vo='B10', dur=vd('B10', 0.35), line='Día catorce.', head='DÍA 14 🎉', sub_y=470, sfx=[(0.15, f'{AU}/sfx_scratch.wav', 0.3), (0.6, f'{AU}/sfx_chime.wav', 0.3)]),
        dict(key='B11', vo='B11', dur=vd('B11'), line='Saqué la blusa sin mangas.', head='La blusa volvió', sub_y=SY),
        dict(key='B12', vo='B12', dur=vd('B12'), line='Lo mejor: para mí, mis axilas lucen más parejas.', head='Para mí: más parejas', sub_y=SY),
        dict(key='B13', vo='B13', dur=vd('B13'), line='Y si no te funciona en catorce días, te devuelven la plata.', sfx=[(0.4, f'{AU}/sfx_thud.wav', 0.6)]),
        dict(key='B14', vo='B14', dur=vd('B14', 0.5), line='Es Black Friday en GEODA: paga dos y lleva tres, y pagas cuando te llegue.', sfx=TAPS),
    ],
    cta=dict(row='B14', delay=0.2, l1='BLACK FRIDAY', l2='Paga 2 lleva 3'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'DIARIO_K2'
k2['body'][-1] = dict(key='B14', vo='B14k2', dur=vd('B14k2', 0.5), line='Regala algo que sí se usa todos los días: GEODA. Paga dos, lleva tres, y reparte en Navidad.', sfx=TAPS)
k2['cta'] = dict(row='B14', delay=0.2, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3')
hb = copy.deepcopy(base); hb['body'] = [r for r in hb['body'] if r['key'] != 'B1']   # nada se repite entre hook y cuerpo

def vaiven(src, a, b, out):   # tramo a-b de ida y vuelta (labios cerrados todo el tiempo)
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(b - a), '-i', src, '-filter_complex',
                        '[0:v]split[x][y];[y]reverse[r];[x][r]concat=n=2:v=1:a=0,setpts=PTS-STARTPTS', '-an', '-c:v', 'libx264',
                        '-crf', '14', '-pix_fmt', 'yuv420p', out], check=True)
    return out

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    d.setdefault('B1', 2.70)
    if not os.path.exists(f'{T}/cal14.mp4'):
        subprocess.run([sys.executable, f'{AQUI}/cal14.py', '2.0'], check=True)
    b8 = vaiven(k('k_d_b8'), 0.0, 1.1, f'{T}/b8_vaiven.mp4')
    cta = (B.shot(T, f's5_b14nav_{d["B14"]:.2f}', CTA_NAV, d['B14'], z0=1.0, z1=1.09, fx=0.5, fy=0.62) if cfg['fmt'].endswith('K2') else
           B.shot(T, f's5_b14bf_{d["B14"]:.2f}', CTA_BF, d['B14'], z0=1.0, z1=1.09, fx=0.5, fy=0.62))
    up = dict(fy=1.0)   # selfies: zoom anclado abajo, la cara sube y queda espacio bajo la barbilla
    return {
        'HA': [B.shot(T, f's5_ha2_{d["HA"]:.2f}', k('k_d_ha2'), d['HA'], ss=0.0, z0=1.0, z1=1.08, fy=0.6) + ([(300, 620, 930, 1380), (700, 960, 920, 1320)],)],
        'HB': [B.shot(T, f's5_hb_{d["HB"]:.2f}', k('k_d_hb'), d['HB'], ss=0.0, speed=0.8, z0=1.0, z1=1.04) + ([(0, 520, 1080, 1260)],)],
        'HC': [B.shot(T, f's5_hc_{d["HC"]:.2f}', k('k_d_hc2'), d['HC'], ss=0.0, speed=0.72, z0=1.0, z1=1.03) + ([(250, 540, 900, 1260), (680, 960, 1020, 1460)],)],
        'HD': [B.shot(T, f's5_hd_{d["HD"]:.2f}', k('k_d_hd'), d['HD'], ss=0.0, z0=1.12, z1=1.14, fy=0.0) + ([(100, 540, 1080, 1560)],)],
        'B1': [B.shot(T, f's5_b1_{d["B1"]:.2f}', k('k_d_b1'), d['B1'], z0=1.1, z1=1.12, **up) + ([(200, 0, 960, 950), (640, 820, 900, 1300)],)],
        'B2': [B.shot(T, f's5_b2_{d["B2"]:.2f}', f'{KIT}/broll/k_grifo_m_0.mp4', d['B2'], ss=0.3, z0=1.0, z1=1.06) + ([(350, 560, 960, 1560)],)],
        'B3': [B.shot(T, f's5_b3_{d["B3"]:.2f}', k('k_d_b3'), d['B3'], z0=1.1, z1=1.12, **up) + ([(40, 0, 980, 940)],)],
        'B4': [B.shot(T, f's5_b4_{d["B4"]:.2f}', k('k_d_b4'), d['B4'], z0=1.14, z1=1.16, **up) + ([(150, 0, 1000, 990)],)],
        'B5': [B.shot(T, f's5_b5_{d["B5"]:.2f}', k('k_d_b5'), d['B5'], z0=1.12, z1=1.14, **up) + ([(200, 0, 900, 950)],)],
        'B6': [B.shot(T, f's5_b6_{d["B6"]:.2f}', k('k_d_b6'), d['B6'], ss=1.8, z0=1.0, z1=1.03) + ([(380, 150, 720, 540)],)],
        'B7': [B.shot(T, f's5_b7_{d["B7"]:.2f}', k('k_d_b7'), d['B7'], z0=1.18, z1=1.2, **up) + ([(200, 0, 1000, 1020)],)],
        'B8': [B.shot(T, f's5_b8_{d["B8"]:.2f}', b8, d['B8'], speed=0.87, z0=1.1, z1=1.12, **up) + ([(200, 0, 980, 950)],)],
        'B9': [B.shot(T, f's5_b9_{d["B9"]:.2f}', k('k_d_b9'), d['B9'], ss=2.7, z0=1.1, z1=1.12, **up) + ([(200, 0, 900, 910)],)],
        'B10': [B.shot(T, f's5_b10_{d["B10"]:.2f}', f'{T}/cal14.mp4', d['B10'], z0=1.0, z1=1.02) + ([(60, 540, 1020, 1360)],)],
        'B11': [B.shot(T, f's5_b11_{d["B11"]:.2f}', k('k_d_b11'), d['B11'], ss=0.0, z0=1.0, z1=1.04) + ([(360, 100, 760, 620)],)],
        'B12': [B.shot(T, f's5_b12_{d["B12"]:.2f}', k('k_d_b12'), d['B12'], ss=0.0, z0=1.0, z1=1.03) + ([(360, 700, 720, 920)],)],
        'B13': [B.shot(T, f's5_b13_{d["B13"]:.2f}', SELLO, d['B13'], z0=1.0, z1=1.04) + ([(320, 420, 760, 860), (290, 1050, 790, 1630)],)],
        'B14': [cta + ([(259, 940, 801, 1620), (75, 500, 405, 930), (400, 720, 880, 880)],)],
    }

if __name__ == '__main__':
    plan = {'HA': base, 'HB': hb, 'HC': k2, 'HD': k2}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; B.build(cfg, hk, build_shots(cfg))
