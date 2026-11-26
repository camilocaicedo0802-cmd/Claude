#!/usr/bin/env python3
"""GEO-BOFU-A1-09 · Demo de producto (solo manos, voz en off H) · ~20 s · CTA principal K5 paga contraentrega + alterno K2 Navidad.
Narrador en off (Gemini TTS Orus, una sola toma). Nadie habla a cámara; ninguna cara (manos y torso).
Estructura: HOOK → PROBLEMA (B1, reloj 3 p. m.) → PRODUCTO (B2, foto real en la mano) → SOLUCIÓN (B3 mojar/aplicar/secar + B4) → CTA (B5).
Versiones: HA y HB con K5; HC y HD (hooks nuevos) con K2. Sin rótulo IA. Ningún texto tapa la piedra ni la etiqueta.
Tramos descartados: HA desde 1,35 s (se usa 0,1-1,35 de ida y vuelta) y la aplicación desde 1,3 s (Kling dejó rastro blanco en la piel: la piedra no deja residuo)."""
import os, sys, copy
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a109'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
XMAS = f'{G}/a202/tmp/xmas_ec_bow.mp4'   # producto real con moño junto al árbol (A2-02)

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

base = dict(
    id='GEO_BOFU_A1_09', fmt='DEMO', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_821.mp3', music_vol=0.10,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Si tu piedra no funcionó,', 'te faltó un paso 👇'),
                   line='Si tu piedra no te funcionó, te faltó un paso.',
                   extras=[dict(type='stamp', text='SECA', x=235, y=1120, t0=0.35, size=96)],
                   sfx=[(0.05, f'{AU}/sfx_scratch.wav', 0.3), (0.35, f'{AU}/sfx_thud.wav', 0.6)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('¡No la botes!', 'Solo la estabas usando mal'),
                   line='No la botes. Solo la estabas usando mal.', sfx=[(0.1, f'{AU}/sfx_error.wav', 0.22)]),
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Antes de regalar la piedra,', 'mira cómo se usa 🎁'),
                   line='Antes de regalar una piedra de alumbre, mira cómo se usa.', sfx=[(0.5, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('El paso que casi todos', 'se saltan con la piedra 👇'),
                   line='El paso que casi todos se saltan con la piedra de alumbre.', sfx=[(0.4, f'{AU}/sfx_glint.wav', 0.3)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Seca, la piedra no suelta nada, y a media tarde vuelve el olor.', sfx=[(0.0, f'{AU}/sfx_clock.wav', 0.3)]),
        dict(key='B2', vo='B2', dur=vd('B2'), line='GEODA es piedra de alumbre natural, sin perfume.', sfx=[(0.3, f'{AU}/sfx_glint.wav', 0.3)]),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Mójala, pásala por la axila limpia y déjala secar.',
             sfx=[(0.1, f'{AU}/splash_1180.mp3', 0.3), (2.1, f'{AU}/sfx_soplo.wav', 0.25)]),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Así sí neutraliza el olor.', sfx=[(0.7, f'{AU}/sfx_tap.wav', 0.35)]),
        dict(key='B5', vo='B5', dur=vd('B5', 0.4), line='Pídela hoy: no pagas nada ahora, la pagas cuando te llegue. Y tienes catorce días de garantía.'),
    ],
    cta=dict(row='B5', delay=0.2, l1='PÍDELA HOY', l2='La pagas cuando te llegue', pill='Garantía 14 días ✅'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'DEMO_K2'
k2['body'][-1] = dict(key='B5', vo='B5k2', dur=vd('B5k2', 0.5), line='Regálalas esta Navidad: paga dos, lleva tres, y las pagas cuando te lleguen.')
k2['cta'] = dict(row='B5', delay=0.2, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3')

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    a1, a2 = 1.0, 1.1   # B3: 'mójala' / 'pásala por la axila limpia' / 'déjala secar'
    dom = 2.3           # B5: domicilio (manos) y luego el cierre con el producto real
    if cfg['fmt'].endswith('K2'):
        cta = [B.shot(T, f's9_b5nav_{d["B5"]:.2f}', XMAS, d['B5'], z0=1.0, z1=1.12, fx=0.5, fy=0.62) + ([(320, 940, 880, 1620)],)]
    else:
        cta = [B.shot(T, 's9_b5dom', k('k_a9_dom'), dom, ss=1.2, z0=1.0, z1=1.05) + ([(380, 520, 1080, 1520)],),
               B.shot(T, f's9_b5ec_{d["B5"]:.2f}', f'{KIT}/producto/endcard_bano_anim.mp4', d['B5'] - dom, z0=1.0, z1=1.06, fx=0.5, fy=0.62)
               + ([(259, 940, 801, 1620)],)]
    return {
        'HA': [B.shot(T, f's9_ha2_{d["HA"]:.2f}', f'{T}/ha_vaiven.mp4', d['HA'], ss=0.0, speed=0.92, z0=1.0, z1=1.05) + ([(300, 600, 820, 1320)],)],   # 0,1-1,35 s ida y vuelta (sin rastro en la piel)
        'HB': [B.shot(T, f's9_hb2_{d["HB"]:.2f}', k('k_a9_hb'), d['HB'], ss=1.4, speed=1.15, z0=1.0, z1=1.04) + ([(380, 760, 820, 1260)],)],
        'HC': [B.shot(T, f's9_hc_{d["HC"]:.2f}', k('k_a9_hc'), d['HC'], ss=0.0, z0=1.0, z1=1.06) + ([(330, 840, 720, 1420)],)],
        'HD': [B.shot(T, f's9_hd_{d["HD"]:.2f}', k('k_a9_hd2'), d['HD'], ss=0.0, z0=1.0, z1=1.06, fy=0.65) + ([(230, 680, 940, 1560)],)],
        'B1': [B.shot(T, f's9_b1_{d["B1"]:.2f}', k('k_a9_b1'), d['B1'], ss=0.0, z0=1.0, z1=1.04) + ([(380, 40, 840, 440)],)],
        'B2': [B.shot(T, f's9_b2_{d["B2"]:.2f}', k('k_a9_b2'), d['B2'], ss=0.0, z0=1.0, z1=1.03, framed=0.8) + ([(300, 640, 820, 1520)],)],
        'B3': [B.shot(T, 's9_b3a', f'{KIT}/broll/k_grifo_m_0.mp4', a1, ss=0.3, z0=1.0, z1=1.05) + ([(350, 560, 960, 1560)],),
               B.shot(T, 's9_b3b', k('k_a9_apl'), a2, ss=0.1, z0=1.0, z1=1.04) + ([(400, 760, 720, 1460), (0, 0, 260, 400)],),
               B.shot(T, f's9_b3c_{d["B3"]:.2f}', f'{KIT}/broll/k_toalla_0.mp4', d['B3'] - a1 - a2, ss=0.8, z0=1.0, z1=1.04)],
        'B4': [B.shot(T, f's9_b4_{d["B4"]:.2f}', f'{KIT}/broll/k_tapa_0.mp4', d['B4'], ss=0.2, z0=1.0, z1=1.06) + ([(300, 520, 780, 1460)],)],
        'B5': cta,
    }

def vaiven():   # HA: tramo limpio 0,1-1,35 s del clip de Kling, de ida y vuelta (2,54 s)
    out = f'{TMP}/ha_vaiven.mp4'
    if not os.path.exists(out):
        import subprocess
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.1', '-t', '1.25', '-i', f'{HF}/k_a9_ha_0.mp4', '-filter_complex',
                        '[0:v]split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0,setpts=PTS-STARTPTS', '-an', '-c:v', 'libx264',
                        '-crf', '14', '-pix_fmt', 'yuv420p', out], check=True)

if __name__ == '__main__':
    vaiven()
    plan = {'HA': base, 'HB': base, 'HC': k2, 'HD': k2}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; B.build(cfg, hk, build_shots(cfg))
