#!/usr/bin/env python3
"""GEO-TOFU-A3-01 · Comparación piedra vs frasco · ~32-36 s · CTA principal K7 '1 piedra = 1 año' + alterno K2 Navidad.
Narrador en off (Andrés, H): Gemini TTS gemini-3.1-flash-tts-preview (modelo completo, no lite: la cuota diaria del 3.8 estaba
agotada), voz Enceladus, una sola toma expresiva. En el cierre de Navidad el modelo dijo mal "GEODA": se usa el "Se llama GEODA"
de la frase K7 (misma toma) pegado al resto de la frase.
Optimización de costos: solo 3 escenas nuevas (hooks A, C y D); el resto reutiliza clips de A1-02, A1-07, A1-09, A2-02, A2-06,
A2-08 y del kit, y dos animaciones locales (mg301.py).
Versiones: HA y HB (hooks del brief) con K7; HC y HD (hooks nuevos) con K2. HA quita B1 (el bolso ya es el hook)."""
import os, sys, copy, subprocess
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a301'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
MG_ANIO = f'{G}/a107/tmp/mg_b11.mp4'          # GEODA real + frascos genéricos tachados (A1-07)
XMAS = f'{G}/a202/tmp/xmas_ec_bow.mp4'        # GEODA real con moño junto al árbol (A2-02)

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

base = dict(
    id='GEO_TOFU_A3_01', fmt='COMP', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_847.mp3', music_vol=0.08,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Tu desodorante se riega,', 'se acaba y huele a perfume'),
                   line='Tu desodorante se riega, se acaba y huele a perfume. ¿Y si no tuviera que ser así?', sfx=[(0.2, f'{AU}/sfx_drip.wav', 0.4)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('Esto que parece un cristal', 'es un desodorante'),
                   line='Esto que parece un cristal... es un desodorante. Te explico.',
                   extras=[dict(type='stamp', text='?', x=860, y=700, t0=0.4, size=200, angle=8)], sfx=[(0.4, f'{AU}/sfx_glint.wav', 0.3)]),
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('¿Un regalo que sí se usa', 'todos los días? 🎁'),
                   line='¿Buscas un regalo que sí se use todos los días? Mira esto.', sfx=[(0.5, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('Hice la cuenta de cuántos', 'frascos compro al año'),
                   line='Hice la cuenta de cuántos frascos de desodorante compro al año.', sfx=[(0.2, f'{AU}/sfx_type.wav', 0.35)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='El frasco se riega en el bolso.', head='Se riega 😩', sfx=[(0.3, f'{AU}/sfx_drip.wav', 0.4)]),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Se acaba en unas semanas... y vuelves a comprar.', head='Se acaba', sfx=[(0.2, f'{AU}/sfx_soplo.wav', 0.25)]),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Y huele a perfume encima de tu olor.', head='Perfume encima'),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Existe otra opción: una piedra mineral que se usa como desodorante.', head='Una piedra mineral 🪨',
             sfx=[(0.3, f'{AU}/sfx_glint.wav', 0.35)]),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Se moja, se pasa por la axila limpia, y listo. Sin perfume.', head='Mojar y pasar 💧',
             sfx=[(0.1, f'{AU}/sfx_drip.wav', 0.4)]),
        dict(key='B6', vo='B6', dur=vd('B6'), line='No se riega, y una piedra te dura un año.', head='No se riega · 1 piedra = 1 año',
             sfx=[(0.55, f'{AU}/sfx_thud.wav', 0.5)]),
        dict(key='B7', vo='B7', dur=vd('B7', 0.4), line='Se llama GEODA. Toca el link y haz la cuenta de cuánto te ahorras.', sfx=[(0.45, f'{AU}/sfx_1489.mp3', 0.15)]),
    ],
    cta=dict(row='B7', delay=0.2, l1='1 PIEDRA = 1 AÑO', l2='Ahorra vs. desodorante'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'COMP_K2'
k2['body'][-1] = dict(key='B7', vo='B7k2', dur=vd('B7k2', 0.5), line='Se llama GEODA: una piedra que sí se usa todos los días. Regálala esta Navidad: paga dos, lleva tres.')
k2['cta'] = dict(row='B7', delay=0.2, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3')
def sin(cfg, *keys):
    c = copy.deepcopy(cfg); c['body'] = [r for r in c['body'] if r['key'] not in keys]; return c

def local(name, dur):
    out = f'{TMP}/m31_{name}.mp4'
    if not os.path.exists(out) or B.dur_of(out) < dur:
        subprocess.run([sys.executable, f'{AQUI}/mg301.py', name, f'{dur + 0.3:.2f}'], check=True)
    return out

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    d.setdefault('B1', 2.70)
    rev = f'{T}/tapa_rev.mp4'
    if not os.path.exists(rev):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{KIT}/broll/k_tapa_0.mp4', '-vf', 'reverse', '-an', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', rev], check=True)
    r1 = 2.6; g = 2.0
    cta = ([B.shot(T, f's31_b7nav_{d["B7"]:.2f}', XMAS, d['B7'], z0=1.0, z1=1.12, fx=0.5, fy=0.62) + ([(320, 940, 880, 1620)],)]
           if cfg['fmt'].endswith('K2') else
           [B.shot(T, f's31_b7anio_{d["B7"]:.2f}', MG_ANIO, d['B7'], speed=0.88, z0=1.0, z1=1.04) + ([(10, 800, 1000, 1560)],)])
    return {
        'HA': [B.shot(T, f's31_ha_{d["HA"]:.2f}', k('k_a3_ha'), d['HA'], speed=0.68, z0=1.0, z1=1.06) + ([(100, 620, 1080, 1560)],)],
        'HB': [B.shot(T, f's31_hb_{d["HB"]:.2f}', k('k_macro'), d['HB'], ss=0.3, speed=0.95, z0=1.0, z1=1.06) + ([(250, 900, 820, 1700)],)],
        'HC': [B.shot(T, f's31_hc_{d["HC"]:.2f}', k('k_a3_hc'), d['HC'], speed=0.6, z0=1.0, z1=1.05) + ([(130, 760, 560, 1300), (500, 760, 900, 1150)],)],
        'HD': [B.shot(T, f's31_hd_{d["HD"]:.2f}', k('k_a3_hd'), d['HD'], ss=0.5, z0=1.0, z1=1.05) + ([(0, 560, 1080, 840)],)],
        'B1': [B.shot(T, f's31_b1_{d["B1"]:.2f}', k('k_a3_ha'), d['B1'], ss=2.3, z0=1.04, z1=1.1) + ([(100, 400, 1080, 1560)],)],
        'B2': [B.shot(T, f's31_b2_{d["B2"]:.2f}', k('k_c_b3'), d['B2'], ss=1.2, z0=1.0, z1=1.22, fy=0.5)],
        'B3': [B.shot(T, f's31_b3_{d["B3"]:.2f}', local('nubes', 3.3), d['B3'], z0=1.0, z1=1.0) + ([(180, 600, 920, 1300)],)],
        'B4': [B.shot(T, 's31_b4a', rev, r1, ss=0.0, z0=1.0, z1=1.12) + ([(280, 520, 820, 1500)],),
               B.shot(T, f's31_b4b_{d["B4"]:.2f}', k('k_a9_b2'), d['B4'] - r1, ss=0.0, z0=1.0, z1=1.04) + ([(330, 330, 820, 1400)],)],
        'B5': [B.shot(T, 's31_b5a', f'{KIT}/broll/k_grifo_m_0.mp4', g, ss=0.3, z0=1.0, z1=1.05) + ([(350, 560, 960, 1560)],),
               B.shot(T, f's31_b5b_{d["B5"]:.2f}', f'{KIT}/broll/k_brazo_seco_flip_0.mp4', d['B5'] - g, ss=0.2, z0=1.0, z1=1.06) + ([(300, 640, 920, 1400)],)],
        'B6': [B.shot(T, f's31_b6_{d["B6"]:.2f}', local('rebote', 3.8), d['B6'], z0=1.0, z1=1.0) + ([(300, 760, 780, 1460)],)],
        'B7': cta,
    }

if __name__ == '__main__':
    plan = {'HA': sin(base, 'B1'), 'HB': base, 'HC': k2, 'HD': k2}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; print(hk, 'dur %.1f' % (cfg['hooks'][hk]['dur'] + sum(r['dur'] for r in cfg['body'])))
        B.build(cfg, hk, build_shots(cfg))
