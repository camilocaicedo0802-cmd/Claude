#!/usr/bin/env python3
"""GEO-TOFU-A3-03 · Demo de producto (macro) · ~21-23 s · CTA principal K5 Paga contraentrega + alterno K2 Navidad.
Narrador en off Daniel (H): Gemini TTS gemini-3.8-flash-tts, voz Alnilam, una sola toma expresiva (regla 47).
Costo optimizado: 2 imágenes nuevas + 3 clips (cristal macro, aerosol que rocía hacia cámara y hook de Navidad); el resto reutiliza
clips ya pagados (A2-06, A1-09, A2-08, A2-02 y kit) y dos animaciones locales (mg303.py: bacterias y piedra boca abajo).
Compliance: sin "un solo ingrediente" (pendiente); "ayuda a neutralizar el olor" (permitido); sin precios.
Versiones: HA y HB (hooks del brief) con K5; HC y HD (hooks nuevos) con K2."""
import os, sys, copy, subprocess
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a303'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
XMAS = f'{G}/a202/tmp/xmas_ec_bow.mp4'

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

base = dict(
    id='GEO_TOFU_A3_03', fmt='DEMO', version=2, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_847.mp3', music_vol=0.08,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA', 0.2), subs=False, text=('¿Qué es esto?', 'Pista: va en tu axila 👇'),
                   line='¿Qué crees que es esto? Pista: va en tu axila.', sfx=[(0.3, f'{AU}/sfx_glint.wav', 0.35)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('Llevas años echándote', 'perfume en la axila'),
                   line='Llevas años echándote perfume en la axila. ¿Para qué?', sfx=[(0.2, f'{AU}/sfx_soplo.wav', 0.4)]),
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Regala algo que', 'nadie espera 🎁'),
                   line='Este diciembre, regala algo que nadie espera: una piedra.', sfx=[(0.5, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD', 0.2), subs=False, text=('Cabe en tu mano', 'y te dura un año'),
                   line='Cabe en tu mano... y te dura un año.'),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='La mayoría tapamos el olor con perfume.', head='Tapar con perfume', sfx=[(0.1, f'{AU}/sfx_soplo.wav', 0.3)]),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Pero el olor viene de las bacterias, no del sudor.', head='El olor = bacterias'),
        dict(key='B3', vo='B3', dur=vd('B3', 0.3), line='Esto es piedra de alumbre: un mineral.', head='Piedra de alumbre 🪨', sfx=[(0.3, f'{AU}/sfx_glint.wav', 0.35)]),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Sin perfume, y sin líquido que se riegue.', head='Sin perfume · sin líquido'),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Unas gotas de agua, y se pasa por la axila limpia.', head='Mojar y pasar 💧', sfx=[(0.1, f'{AU}/sfx_drip.wav', 0.4)]),
        dict(key='B6', vo='B6', dur=vd('B6', 0.3), line='Ayuda a neutralizar el olor, sin taparlo.', head='Neutraliza, no tapa ✅'),
        dict(key='B7', vo='K5', dur=vd('K5', 0.5), line='Se llama GEODA, y no pagas nada ahora: la pagas cuando te llegue a la casa.'),
    ],
    cta=dict(row='B7', delay=0.2, l1='PAGA CONTRAENTREGA', l2='Pagas cuando te llegue'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'DEMO_K2'
k2['body'][-1] = dict(key='B7', vo='K2', dur=vd('K2', 0.5), line='Se llama GEODA: una piedra que sí se usa todos los días. Regálala esta Navidad: paga dos, lleva tres.')
k2['cta'] = dict(row='B7', delay=0.2, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3')

def local(name, dur):
    out = f'{TMP}/m33_{name}.mp4'
    if not os.path.exists(out) or B.dur_of(out) < dur:
        subprocess.run([sys.executable, f'{AQUI}/mg303.py', name, f'{dur + 0.3:.2f}'], check=True)
    return out

def axila():
    out = f'{TMP}/axila_vaiven.mp4'
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.1', '-t', '0.72', '-i', f'{HF}/k_a9_apl_0.mp4', '-filter_complex',
                        '[0:v]split[x][y];[y]reverse[r];[x][r]concat=n=2:v=1:a=0,setpts=PTS-STARTPTS', '-an', '-c:v', 'libx264',
                        '-crf', '14', '-pix_fmt', 'yuv420p', out], check=True)
    return out

def build_shots(cfg, hk):
    T = TMP; k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    g, dom = 1.1, 2.2
    if cfg['fmt'].endswith('K2'):
        cta = [B.shot(T, f's33_b7nav_{d["B7"]:.2f}', XMAS, d['B7'], z0=1.0, z1=1.12, fx=0.5, fy=0.62) + ([(320, 940, 880, 1620)],)]
    else:
        cta = [B.shot(T, 's33_b7dom', k('k_a9_dom'), dom, ss=1.2, z0=1.0, z1=1.06) + ([(380, 520, 1080, 1520)],),
               B.shot(T, f's33_b7ec_{d["B7"]:.2f}', f'{KIT}/producto/endcard_bano_anim.mp4', d['B7'] - dom, z0=1.0, z1=1.08, fx=0.5, fy=0.62) + ([(259, 940, 801, 1620)],)]
    # en la versión A el hook ya es el cristal: B3 muestra la piedra GEODA real a contraluz
    # B3 responde al hook A ('¿qué es esto?'): el mismo cristal, otro tramo del giro
    b3 = [B.shot(T, f's33_b3_{d["B3"]:.2f}', k('k_d3_cr'), d['B3'], ss=2.4, z0=1.04, z1=1.14)]
    # B1: el aerosol que rocía; en la versión B el hook ya es ese clip -> otro aerosol (mano que presiona)
    b1 = ([B.shot(T, f's33_b1p_{d["B1"]:.2f}', k('k_c_b3'), d['B1'], ss=0.0, z0=1.0, z1=1.08)] if hk == 'HB' else
          [B.shot(T, f's33_b1s_{d["B1"]:.2f}', k('k_d3_spray'), d['B1'], ss=2.6, z0=1.06, z1=1.16, fy=0.45)])
    return {
        'HA': [B.shot(T, f's33_ha_{d["HA"]:.2f}', k('k_d3_cr'), d['HA'], ss=0.0, z0=1.0, z1=1.08)],
        'HB': [B.shot(T, f's33_hb_{d["HB"]:.2f}', k('k_d3_spray'), d['HB'], ss=1.7, z0=1.0, z1=1.15, fy=0.45) + ([(300, 560, 780, 1300)],)],
        'HC': [B.shot(T, f's33_hc_{d["HC"]:.2f}', k('k_d3_hc'), d['HC'], ss=0.0, z0=1.0, z1=1.06) + ([(300, 900, 860, 1700)],)],
        'HD': [B.shot(T, f's33_hd_{d["HD"]:.2f}', f'{KIT}/broll/k_tapa_0.mp4', d['HD'], ss=0.3, z0=1.0, z1=1.1) + ([(300, 520, 780, 1460)],)],
        'B1': b1,
        'B2': [B.shot(T, f's33_b2_{d["B2"]:.2f}', local('bacterias', 2.6), d['B2'], z0=1.0, z1=1.14) + ([(160, 640, 920, 1380)],)],
        'B3': b3,
        'B4': [B.shot(T, f's33_b4_{d["B4"]:.2f}', local('boca_abajo', 2.7), d['B4'], z0=1.0, z1=1.14) + ([(80, 560, 1000, 1480)],)],
        'B5': [B.shot(T, 's33_b5a', f'{KIT}/broll/k_grifo_m_0.mp4', g, ss=0.3, z0=1.0, z1=1.05) + ([(350, 560, 960, 1560)],),
               # v2 (Camilo): 'se pasa por la axila' -> GEODA pasando por la axila en plano cercano (A1-09, solo 0,1-0,82 s de ida y vuelta: desde 0,9 s Kling pinta una mancha blanca)
               B.shot(T, f's33_b5ax2_{d["B5"]:.2f}', axila(), d['B5'] - g, z0=1.02, z1=1.1, fx=0.4, fy=0.6) + ([(330, 760, 900, 1500)],)],
        'B6': [B.shot(T, f's33_b6_{d["B6"]:.2f}', k('k_u_b3'), d['B6'], ss=0.0, z0=1.0, z1=1.06) + ([(300, 360, 820, 1260)],)],
        'B7': cta,
    }

if __name__ == '__main__':
    plan = {'HA': base, 'HB': base, 'HC': k2, 'HD': k2}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; print(hk, 'dur %.1f' % (cfg['hooks'][hk]['dur'] + sum(r['dur'] for r in cfg['body'])))
        B.build(cfg, hk, build_shots(cfg, hk))
