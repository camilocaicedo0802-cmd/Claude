#!/usr/bin/env python3
"""GEO-TOFU-A3-04 · Estilo Pixar (3D) · ~27-29 s · CTA principal K2 Navidad + alterno K3 Llévala hoy.
Voces (regla 47, Gemini TTS gemini-3.8-flash-tts, una toma por personaje): narradora Erinome (M), labial Laomedeia,
celular Fenrir, Geo Puck (mismo Geo y misma voz del A2-02).
Labios (regla 45): ningún personaje habla con la boca en movimiento. Geo no tiene boca; el labial y el celular dicen su
frase en planos donde solo tienen ojos o la boca cerrada (el celular tose con los ojos apretados).
Costo optimizado: 8 imágenes + 8 clips Kling nuevos (bolso, celular, tos, Geo rodando, Geo con gafas, hooks C y D);
reutiliza Geo bajo el grifo (A2-02), GEODA boca abajo sin gotear (A3-03) y los cierres K2 (A2-02) y K3 (A2-08).
Compliance: frascos genéricos sin marca; sin precios.
Versiones: HA y HB (hooks del brief) con K2; HC y HD (hooks nuevos) con K3. En HA se quita B1 (repite el hook)."""
import os, sys, copy, subprocess
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a304'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
XMAS = f'{G}/a202/tmp/xmas_ec_bow.mp4'
CTA_K3 = f'{G}/a208/tmp/m8_cta_k3.mp4'
BOCA = f'{G}/a303/tmp/m33_boca_abajo.mp4'

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

SPL = f'{AU}/splash_1198.mp3'
base = dict(
    id='GEO_TOFU_A3_04', fmt='PIXAR', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_805.mp3', music_vol=0.10,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Otra vez se te regó', 'el desodorante en el bolso'),
                   line='Otra vez se regó el desodorante en el bolso.', sfx=[(1.0, SPL, 0.5)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('Lo que tu desodorante', 'le hace a tu bolso'),
                   line='Esto es lo que pasa dentro de tu bolso.', sfx=[(0.1, f'{AU}/sfx_alarma.wav', 0.18)]),
        # hooks nuevos para el CTA alterno (Llévala hoy): escenas distintas al cuerpo y a los otros hooks
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('¿Y si tu desodorante', 'nunca se regara?'),
                   line='¿Y si tu desodorante nunca se regara?', sfx=[(0.4, f'{AU}/sfx_glint.wav', 0.35)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('En tu bolso hay', 'una guerra 💥'),
                   line='Dentro de tu bolso hay una guerra... y el frasco siempre gana.', sfx=[(1.0, SPL, 0.35)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Otra vez se regó el frasco en el bolso.', icon='😱', sfx=[(1.4, SPL, 0.45)]),
        dict(key='B2', vo='B2', dur=vd('B2'), line='¡Otra vez no!'),   # sin titular: repetiría el subtítulo
        # B3: la tos (sin palabras) no lleva subtítulo; 'Y todo huele a perfume' con tiempos medidos (+0,05 s de entrada de la voz)
        dict(key='B3', vo='B3', dur=vd('B3'), line='¡Y todo huele a perfume!', icon='😷',
             words=[('¡Y', 1.54, 1.70), ('todo', 1.87, 2.10), ('huele', 2.10, 2.37), ('a', 2.43, 2.60), ('perfume!', 2.80, 3.32)]),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Hasta que llegó una vecina nueva al bolso.', head='¿Y esa quién es?',
             sfx=[(1.0, f'{AU}/sfx_thud.wav', 0.4)]),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Soy una piedra mineral. A mí no se me riega nada.', head='No me riego 😎',
             sfx=[(0.2, f'{AU}/sfx_glint.wav', 0.3)]),
        dict(key='B6', vo='B6', dur=vd('B6'), line='En el baño de la oficina, un poquito de agua, y lista.', icon='💧',
             sfx=[(0.1, f'{AU}/sfx_drip.wav', 0.4), (0.6, f'{AU}/sfx_drip.wav', 0.35)]),
        dict(key='B7', vo='B7', dur=vd('B7'), line='Un desodorante sin perfume que no se riega.', head='No se riega ✅'),
        dict(key='B8', vo='K2', dur=vd('K2', 0.5), line='Se llama GEODA: una piedra que sí se usa todos los días. Regálala esta Navidad: paga dos, lleva tres.'),
    ],
    cta=dict(row='B8', delay=0.2, l1='REGALO DE NAVIDAD', l2='Paga 2 lleva 3'),
)
ha = copy.deepcopy(base); ha['body'] = [r for r in ha['body'] if r['key'] != 'B1']   # B1 repite el hook A
k3 = copy.deepcopy(base); k3['fmt'] = 'PIXAR_K3'
k3['body'][-1] = dict(key='B8', vo='K3', dur=vd('K3', 0.5), line='Se llama GEODA. Pruébala: pídela hoy, y la pagas cuando te llegue.')
k3['cta'] = dict(row='B8', delay=0.2, l1='PÍDELA HOY', l2='La pagas cuando te llegue')

def vaiven_hd():
    """Hook D: el frasco-general levanta el puño (0-2,3 s; después Kling deforma la cara) y lo baja (mismo tramo al revés)."""
    out = f'{TMP}/hd_vaiven.mp4'
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-t', '2.3', '-i', f'{HF}/k_p4_hd_0.mp4', '-filter_complex',
                        '[0:v]split[x][y];[y]trim=1.2:2.3,setpts=PTS-STARTPTS,reverse[r];[x][r]concat=n=2:v=1:a=0,setpts=PTS-STARTPTS',
                        '-an', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', out], check=True)
    return out

def build_shots(cfg, hk):
    T = TMP; k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    d.setdefault('B1', vd('B1'))   # en HA no se usa (B1 repite el hook)
    CH = (150, 760, 1000, 1420)   # labial + celular en el bolso
    if cfg['fmt'].endswith('K3'):
        b8 = [B.shot(T, f's34_b8k3_{d["B8"]:.2f}', CTA_K3, d['B8'], z0=1.0, z1=1.12, fx=0.5, fy=0.62) + ([(259, 940, 801, 1620), (300, 720, 780, 860)],)]
    else:
        b8 = [B.shot(T, f's34_b8nav_{d["B8"]:.2f}', XMAS, d['B8'], z0=1.0, z1=1.12, fx=0.5, fy=0.62) + ([(320, 940, 880, 1620)],)]
    return {
        'HA': [B.shot(T, f's34_ha_{d["HA"]:.2f}', k('k_p4_bolso'), d['HA'], ss=0.3, speed=0.8, z0=1.0, z1=1.08, fy=0.6) + ([CH],)],
        'HB': [B.shot(T, f's34_hb_{d["HB"]:.2f}', k('k_p4_cel'), d['HB'], ss=0.8, z0=1.0, z1=1.08, fy=0.6) + ([(250, 740, 960, 1520)],)],
        'HC': [B.shot(T, f's34_hc_{d["HC"]:.2f}', k('k_p4_hc'), d['HC'], ss=2.0, z0=1.0, z1=1.06, fy=0.55) + ([(150, 640, 920, 1900)],)],
        'HD': [B.shot(T, f's34_hd_{d["HD"]:.2f}', vaiven_hd(), d['HD'], speed=0.92, z0=1.0, z1=1.08, fy=0.55) + ([(420, 600, 820, 1300), (0, 1300, 900, 1760)],)],
        'B1': [B.shot(T, f's34_b1_{d["B1"]:.2f}', k('k_p4_bolso'), d['B1'], ss=0.0, z0=1.02, z1=1.1, fy=0.6) + ([CH],)],
        # B2: punch-in al labial (tramo 2,3-4 s: solo ojos / labios cerrados, no habla con la boca)
        'B2': [B.shot(T, f's34_b2_{d["B2"]:.2f}', k('k_p4_bolso'), d['B2'], ss=2.3, z0=1.75, z1=1.95, fx=0.46, fy=0.5) + ([(200, 640, 900, 1460)],)],
        'B3': [B.shot(T, f's34_b3_{d["B3"]:.2f}', k('k_p4_tos'), d['B3'], ss=0.0, speed=0.92, z0=1.0, z1=1.1, fx=0.6, fy=0.55) + ([(150, 600, 1000, 1400)],)],
        'B4': [B.shot(T, f's34_b4_{d["B4"]:.2f}', k('k_p4_rueda2'), d['B4'], ss=0.6, z0=1.0, z1=1.06, fy=0.6) + ([(80, 520, 460, 900), (60, 1100, 1040, 1760)],)],
        'B5': [B.shot(T, f's34_b5_{d["B5"]:.2f}', k('k_p4_gafas'), d['B5'], ss=1.0, speed=0.93, z0=1.0, z1=1.12, fx=0.5, fy=0.58) + ([(100, 720, 1000, 1500)],)],
        'B6': [B.shot(T, f's34_b6_{d["B6"]:.2f}', k('k_p_b6'), d['B6'], ss=0.0, speed=0.95, z0=1.0, z1=1.08) + ([(140, 700, 930, 1560)],)],
        'B7': [B.shot(T, f's34_b7_{d["B7"]:.2f}', BOCA, d['B7'], ss=0.3, speed=0.9, z0=1.0, z1=1.25, fy=0.3) + ([(380, 590, 1000, 1600)],)],   # GEODA (el frasco genérico sí puede quedar bajo el texto)
        'B8': b8,
    }

if __name__ == '__main__':
    plan = {'HA': ha, 'HB': base, 'HC': k3, 'HD': k3}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; print(hk, 'dur %.1f' % (cfg['hooks'][hk]['dur'] + sum(r['dur'] for r in cfg['body'])))
        B.build(cfg, hk, build_shots(cfg, hk))
