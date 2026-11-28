#!/usr/bin/env python3
"""GEO-BOFU-A2-07 · UGC con avatar IA (Mariana, la del diario A2-05) · ~18-24 s · CTA principal K8 Combo para regalar + alterno K2 Navidad.
Voz en off de Mariana: Gemini TTS gemini-3.8-flash-tts (versión completa, regla 47), voz Callirrhoe, una sola toma expresiva.
Mariana nunca habla a cámara: labios cerrados en todos los tramos usados. Sin precios. Productos = recorte REAL (mg207.py, cierre del A2-06).
Ángulo A2: NO PUBLICAR hasta que Alberto confirme el registro sanitario.
Versiones: HA y HB (hooks del brief) con K8; HC y HD (hooks nuevos) con K2. Nada se repite entre hook y cuerpo:
HA y HD quitan B1 (las blusas sin mangas), HB quita B3 (paga 2 lleva 3)."""
import os, sys, copy, subprocess
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a207'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
CTA3 = f'{G}/a206/tmp/m6_cta3.mp4'            # tres GEODA reales, dos con moño, botón Comprar (A2-06)
CTA_NAV = f'{G}/a108/tmp/cta_navidad.mp4'     # producto real + etiqueta REGALO NAVIDAD + Comprar (A1-08, 7,8 s)
DOM = f'{HF}/k_a9_dom_0.mp4'                  # domicilio: manos reciben la caja con GEODA (A1-09)

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

base = dict(
    id='GEO_BOFU_A2_07', fmt='UGC', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_805.mp3', music_vol=0.08,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('La blusa sin mangas', 'te está esperando'),
                   line='Yo ya la saqué del clóset. Tú, ¿qué esperas?', sfx=[(0.15, f'{AU}/sfx_1489.mp3', 0.3)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('Paga 2, lleva 3: una para ti', 'y dos para tus amigas'),
                   line='Paga dos, lleva tres: una para ti y dos para tus amigas.',
                   sfx=[(0.47, f'{AU}/sfx_2357.mp3', 0.5), (0.97, f'{AU}/sfx_2357.mp3', 0.5), (1.47, f'{AU}/sfx_2357.mp3', 0.5)]),
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('¿Ya sabes qué regalarle', 'a tus amigas? 🎁'),
                   line='¿Ya sabes qué regalarle a tus amigas esta Navidad? Yo sí.', sfx=[(0.3, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('Este diciembre vuelvo a', 'las blusas sin mangas'),
                   line='Este diciembre vuelvo a las blusas sin mangas... y no voy sola.'),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Yo ya saqué las blusas sin mangas del clóset.', head='Las saqué 💃'),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Mi secreto es esta piedra, sin perfume.', sub_y=1190, sub_cx=380),   # selfie cerca: subtítulo en el pecho, lejos del pelo y de la piedra
        dict(key='B3', vo='B3', dur=vd('B3'), line='Paga dos, lleva tres: una para ti y dos para tus amigas.', head='Paga 2 lleva 3'),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Pagas cuando te llegue, y tienes catorce días de garantía.', head='Contraentrega + 14 días ✅'),
        dict(key='B5', vo='B5', dur=vd('B5', 0.3), line='¿Qué esperas?'),
        dict(key='B6', vo='B6', dur=vd('B6', 0.5), line='Paga dos y lleva tres: una para ti y dos para regalar. ¡Pídelo hoy!',
             sfx=[(2.2, f'{AU}/sfx_tap.wav', 0.5), (3.6, f'{AU}/sfx_tap.wav', 0.5)]),
    ],
    cta=dict(row='B6', delay=0.2, l1='PAGA 2 LLEVA 3', l2='Una para ti y dos para regalar'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'UGC_K2'
k2['body'][-1] = dict(key='B6', vo='B6k2', dur=vd('B6k2', 0.5), line='Regala algo que sí se usa todos los días: GEODA. Paga dos, lleva tres, y reparte en Navidad.',
                      sfx=[(1.6, f'{AU}/sfx_tap.wav', 0.5), (3.4, f'{AU}/sfx_tap.wav', 0.5)])
k2['cta'] = dict(row='B6', delay=0.2, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3')
def sin(cfg, *keys):
    c = copy.deepcopy(cfg); c['body'] = [r for r in c['body'] if r['key'] not in keys]; return c

def local(name, dur):
    out = f'{TMP}/m7_{name}.mp4'
    if not os.path.exists(out) or B.dur_of(out) < dur:
        subprocess.run([sys.executable, f'{AQUI}/mg207.py', name, f'{dur + 0.3:.2f}'], check=True)
    return out

def vaiven(src, a, b, out):   # tramo a-b de ida y vuelta (sonrisas con la boca cerrada)
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(b - a), '-i', src, '-filter_complex',
                        '[0:v]split[x][y];[y]reverse[r];[x][r]concat=n=2:v=1:a=0,setpts=PTS-STARTPTS', '-an', '-c:v', 'libx264',
                        '-crf', '14', '-pix_fmt', 'yuv420p', out], check=True)
    return out

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    for kk, v in (('B1', 2.33), ('B3', 3.77)): d.setdefault(kk, v)
    hd = vaiven(k('k_mj_hd'), 0.0, 1.2, f'{T}/hd_vaiven.mp4')
    cta = ([B.shot(T, f's7_b6nav_{d["B6"]:.2f}', CTA_NAV, d['B6'], z0=1.0, z1=1.09, fx=0.5, fy=0.62) + ([(259, 940, 801, 1620), (75, 500, 405, 930), (400, 720, 880, 880)],)]
           if cfg['fmt'].endswith('K2') else
           [B.shot(T, f's7_b6k8_{d["B6"]:.2f}', CTA3, d['B6'], z0=1.0, z1=1.03) + ([(100, 820, 980, 1470), (300, 630, 780, 770)],)])
    return {
        'HA': [B.shot(T, f's7_ha_{d["HA"]:.2f}', k('k_mj_ha'), d['HA'], ss=0.0, speed=0.6, z0=1.0, z1=1.04) + ([(330, 600, 760, 1150)],)],   # antes de la carcajada
        'HB': [B.shot(T, f's7_hb_{d["HB"]:.2f}', local('palma', 4.0), d['HB'], z0=1.0, z1=1.02) + ([(300, 640, 900, 1260)],)],
        'HC': [B.shot(T, f's7_hc_{d["HC"]:.2f}', k('k_mj_hc'), d['HC'], ss=0.0, z0=1.0, z1=1.04) + ([(380, 560, 720, 940), (600, 1000, 820, 1450)],)],
        'HD': [B.shot(T, f's7_hd_{d["HD"]:.2f}', hd, d['HD'], speed=0.53, z0=1.0, z1=1.05) + ([(0, 560, 1080, 1150)],)],
        'B1': [B.shot(T, f's7_b1_{d["B1"]:.2f}', k('k_mj_b1'), d['B1'], ss=0.0, z0=1.0, z1=1.04) + ([(300, 520, 720, 960)],)],
        'B2': [B.shot(T, f's7_b2_{d["B2"]:.2f}', k('k_mj_b2'), d['B2'], ss=1.0, z0=1.0, z1=1.04) + ([(180, 480, 760, 1150), (620, 900, 900, 1450)],)],
        'B3': [B.shot(T, f's7_b3_{d["B3"]:.2f}', local('abanico', 4.1), d['B3'], z0=1.0, z1=1.0) + ([(180, 780, 900, 1400)],)],
        'B4': [B.shot(T, f's7_b4_{d["B4"]:.2f}', DOM, d['B4'], ss=1.2, z0=1.0, z1=1.05) + ([(380, 520, 1080, 1520)],)],
        'B5': [B.shot(T, f's7_b5_{d["B5"]:.2f}', k('k_mj_b5'), d['B5'], ss=0.0, z0=1.0, z1=1.06) + ([(420, 560, 660, 800)],)],
        'B6': cta,
    }

if __name__ == '__main__':
    plan = {'HA': sin(base, 'B1'), 'HB': sin(base, 'B3'), 'HC': k2, 'HD': sin(k2, 'B1')}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; print(hk, 'dur %.1f' % (cfg['hooks'][hk]['dur'] + sum(r['dur'] for r in cfg['body'])))
        B.build(cfg, hk, build_shots(cfg))
