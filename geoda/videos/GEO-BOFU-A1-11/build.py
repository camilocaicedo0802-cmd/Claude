#!/usr/bin/env python3
"""GEO-BOFU-A1-11 · Faceless / motion graphics · ~23 s · CTA principal K6 envío gratis a toda Colombia + alterno K1 Black Friday.
Narrador en off (H, Gemini TTS Iapetus, una sola toma; B5 regrabada con la misma voz y modelo). Todo animado (mg11.py), producto = recorte real.
Estructura: HOOK → PROBLEMA (B1) → PRODUCTO (B2) → SOLUCIÓN (B3 4 pasos + B4 garantía) → CTA (B5).
Versiones: HA y HB con K6 (mapa de Colombia); HC y HD (hooks nuevos de Black Friday) con K1. Sin rótulo IA. Ningún texto tapa la piedra ni la etiqueta."""
import os, sys, copy, json, subprocess
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a111'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
AU = f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
CTA_MAPA = f'{G}/a203/tmp/cta_mapa.mp4'     # mapa de Colombia + pines + camión + producto real (A2-03)
CTA_BF = f'{G}/a108/tmp/cta_bf.mp4'         # producto real + etiqueta BLACK FRIDAY + botón Comprar (A1-08)

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

TAPS = [(1.6, f'{AU}/sfx_tap.wav', 0.5), (3.4, f'{AU}/sfx_tap.wav', 0.5)]
base = dict(
    id='GEO_BOFU_A1_11', fmt='MOTION', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_847.mp3', music_vol=0.10,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('¿Tu piedra “no sirve”?', 'No compres otro desodorante'),
                   line='¿Tu piedra no sirve? No compres otro desodorante todavía.',
                   sfx=[(0.85, f'{AU}/sfx_thud.wav', 0.7), (0.9, f'{AU}/sfx_error.wav', 0.2)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('La piedra no te falló:', 'te la pusiste mal ✅'),
                   line='La piedra no te falló: te la pusiste mal.',
                   sfx=[(0.1, f'{AU}/sfx_error.wav', 0.22), (1.25, f'{AU}/sfx_chime.wav', 0.35)]),
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Black Friday para los que', 'dicen que la piedra no sirve'),
                   line='Black Friday para los que dicen que la piedra no sirve.',
                   sfx=[(0.42, f'{AU}/sfx_thud.wav', 0.6), (0.5, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('Si vas a probar la piedra,', 'que sea este Black Friday 🎁'),
                   line='Si vas a probar la piedra, que sea este Black Friday.',
                   sfx=[(0.45, f'{AU}/sfx_tap.wav', 0.4), (0.9, f'{AU}/sfx_tap.wav', 0.4), (1.35, f'{AU}/sfx_tap.wav', 0.4), (1.8, f'{AU}/sfx_chime.wav', 0.35)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Si la usas seca o la guardas mojada, no neutraliza el olor y se agrieta.',
             sfx=[(0.05, f'{AU}/sfx_scratch.wav', 0.3), (1.9, f'{AU}/amb_ducha.wav', 0.25), (3.6, f'{AU}/sfx_crack.wav', 0.7)]),
        dict(key='B2', vo='B2', dur=vd('B2'), line='GEODA es piedra de alumbre natural, sin perfume.', sfx=[(0.3, f'{AU}/sfx_glint.wav', 0.3)]),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Mójala, aplícala, déjala secar y guárdala seca.',
             sfx=[(0.05, f'{AU}/sfx_drip.wav', 0.4), (0.75, f'{AU}/sfx_tap.wav', 0.35), (1.55, f'{AU}/sfx_soplo.wav', 0.3), (2.3, f'{AU}/sfx_tap.wav', 0.35)]),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Y si en catorce días no te funciona, te devolvemos tu dinero.', sfx=[(0.4, f'{AU}/sfx_thud.wav', 0.6)]),
        dict(key='B5', vo='B5', dur=vd('B5', 0.45), line='Te la enviamos gratis a toda Colombia y la pagas al recibir.'),
    ],
    cta=dict(row='B5', delay=0.2, l1='ENVÍO GRATIS A TODA COLOMBIA', l2='La pagas al recibir', pill='Llega a tu casa 🚚'),
)
k1 = copy.deepcopy(base); k1['fmt'] = 'MOTION_K1'
k1['body'][-1] = dict(key='B5', vo='B5k1', dur=vd('B5k1', 0.5), line='Por Black Friday: paga dos, lleva tres, y las pagas cuando te lleguen.', sfx=TAPS)
k1['cta'] = dict(row='B5', delay=0.2, l1='BLACK FRIDAY', l2='Paga 2 lleva 3')

# zonas que ningún texto tapa (producto, etiqueta, señales, sellos, calendario), coordenadas 1080x1920
BOX = {
    'HA': [(40, 690, 1040, 1500)], 'HB': [(200, 710, 980, 1500)], 'HC': [(200, 800, 980, 1520)], 'HD': [(60, 740, 960, 1530)],
    'B1a': [(0, 1000, 1080, 1460)], 'B1b': [(560, 230, 920, 460), (220, 880, 880, 1520)], 'B1c': [(180, 690, 900, 1310), (720, 300, 960, 540)],
    'B2': [(200, 740, 880, 1520)], 'B3': [(90, 570, 990, 1350)], 'B4': [(320, 420, 760, 860), (290, 1050, 790, 1630)],
}

def scenes(cfg):
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    return d

def render_mg():
    d = scenes(base); need = {k.lower(): d[k] for k in ['HA', 'HB', 'HC', 'HD', 'B1', 'B2', 'B3', 'B4']}
    todo = {k: v for k, v in need.items() if not os.path.exists(f'{TMP}/mg_11_{k}.mp4')
            or abs(B.dur_of(f'{TMP}/mg_11_{k}.mp4') - v) > 0.05}
    if todo:
        jf = f'{TMP}/durs.json'; json.dump(todo, open(jf, 'w'))
        subprocess.run([sys.executable, f'{AQUI}/mg11.py', 'todas', jf], check=True, cwd=AQUI)

def build_shots(cfg):
    T = TMP; d = scenes(cfg); m = lambda k: f'{T}/mg_11_{k}.mp4'
    b1 = d['B1']; a, b = round(b1 * 0.38, 2), round(b1 * 0.70, 2)
    if cfg['fmt'].endswith('K1'):
        cta = [B.shot(T, f's_b5bf_{d["B5"]:.2f}', CTA_BF, d['B5'], z0=1.0, z1=1.09, fx=0.5, fy=0.62)
               + ([(259, 940, 801, 1620), (75, 500, 405, 930), (400, 720, 880, 880)],)]
    else:
        cta = [B.shot(T, f's_b5map_{d["B5"]:.2f}', CTA_MAPA, d['B5'], z0=1.0, z1=1.08, fx=0.5, fy=0.6) + ([(630, 940, 910, 1580)],)]
    sh = {k: [B.shot(T, f's11_{k.lower()}_{d[k]:.2f}', m(k.lower()), d[k], z0=1.0, z1=1.04) + (BOX[k],)] for k in ['HA', 'HB', 'HC', 'HD', 'B2', 'B3', 'B4']}
    sh['B1'] = [B.shot(T, 's11_b1a', m('b1'), a, ss=0.0, z0=1.0, z1=1.03) + (BOX['B1a'],),
                B.shot(T, 's11_b1b', m('b1'), b - a, ss=a, z0=1.0, z1=1.03) + (BOX['B1b'],),
                B.shot(T, f's11_b1c_{b1:.2f}', m('b1'), b1 - b, ss=b, z0=1.0, z1=1.05) + (BOX['B1c'],)]
    sh['B5'] = cta
    return sh

if __name__ == '__main__':
    render_mg()
    plan = {'HA': base, 'HB': base, 'HC': k1, 'HD': k1}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; B.build(cfg, hk, build_shots(cfg))
