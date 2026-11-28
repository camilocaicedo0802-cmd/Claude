#!/usr/bin/env python3
"""GEO-TOFU-A3-02 · Claymation (stop-motion IA) · ~26-28 s · CTA principal K3 'Llévala hoy' + alterno K2 Navidad.
Narradora (M) Gemini TTS gemini-3.1-flash-tts-preview (completo; cuota del 3.8 agotada), voz Achernar, una toma (la 3: las
anteriores decían mal "GEODA"); en K3 se pegó el "Se llama GEODA" de la frase K2 (misma toma). La piedra (personaje, sin boca)
habla con voz Puck (gemini-3.8-flash-tts). Set y personajes de plastilina desde una imagen de referencia (cl_ref) para que todo
sea igual; B1-B2 y B3 se animan desde esa misma imagen (sin imágenes nuevas). Producto real al final.
Versiones: HA y HB (hooks del brief) con K3; HC y HD (hooks nuevos) con K2."""
import os, sys, copy, subprocess
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a302'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
CTA_K3 = f'{G}/a208/tmp/m8_cta_k3.mp4'     # producto real + botón Comprar (A2-08, 6,4 s)
XMAS = f'{G}/a202/tmp/xmas_ec_bow.mp4'     # GEODA real con moño junto al árbol (A2-02)

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

base = dict(
    id='GEO_TOFU_A3_02', fmt='CLAY', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_821.mp3', music_vol=0.09,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('El frasco que', 'siempre se acaba'),
                   line='Frasco, frasco, frasco... y la piedra ahí.', sfx=[(0.3, f'{AU}/sfx_thud.wav', 0.4), (1.1, f'{AU}/sfx_thud.wav', 0.4), (1.9, f'{AU}/sfx_thud.wav', 0.4)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('Una piedra vs.', 'una fila de frascos'),
                   line='Mientras los frascos se acaban, la piedra sigue.', sfx=[(0.4, f'{AU}/sfx_tap.wav', 0.4), (0.9, f'{AU}/sfx_tap.wav', 0.4), (1.4, f'{AU}/sfx_tap.wav', 0.4)]),
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Regala algo que', 'no se acaba 🎁'),
                   line='Este diciembre, regala algo que no se acaba.', sfx=[(0.5, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('La piedra que le ganó', 'a una fila de frascos'),
                   line='La piedra que le ganó a una fila de frascos.', sfx=[(0.3, f'{AU}/sfx_chime.wav', 0.3)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Lunes. Frasco nuevo.', head='Lunes', sfx=[(0.2, f'{AU}/sfx_glint.wav', 0.3)]),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Unas semanas después...', head='Se acabó 😢'),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Frasco nuevo. Otra vez.', head='Otra vez...', sfx=[(1.0, f'{AU}/sfx_thud.wav', 0.4)]),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Y otra vez.', head='Y otra vez', sfx=[(0.3, f'{AU}/sfx_thud.wav', 0.4)]),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Mientras tanto, la piedra... ahí.', head='La piedra, ahí 😌'),
        dict(key='B6', vo='B6', dur=vd('B6'), line='¿Qué? Yo te duro un año.', head='1 piedra dura 1 año', sfx=[(1.9, f'{AU}/sfx_glint.wav', 0.35)]),
        dict(key='B7', vo='B7', dur=vd('B7'), line='Una piedra. Cero frascos.', head='1 piedra · 0 frascos'),
        dict(key='B8', vo='K3', dur=vd('K3', 0.5), line='Se llama GEODA. Pruébala: pídela hoy, y la pagas cuando te llegue.',
             sfx=[(1.8, f'{AU}/sfx_tap.wav', 0.5), (3.4, f'{AU}/sfx_tap.wav', 0.5)]),
    ],
    cta=dict(row='B8', delay=0.2, l1='LLÉVALA HOY', l2='Pagas al recibir'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'CLAY_K2'
k2['body'][-1] = dict(key='B8', vo='K2', dur=vd('K2', 0.5), line='Se llama GEODA: una piedra que sí se usa todos los días. Regálala esta Navidad: paga dos, lleva tres.')
k2['cta'] = dict(row='B8', delay=0.2, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3')

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    cta = ([B.shot(T, f's32_b8nav_{d["B8"]:.2f}', XMAS, d['B8'], z0=1.0, z1=1.12, fx=0.5, fy=0.62) + ([(320, 940, 880, 1620)],)]
           if cfg['fmt'].endswith('K2') else
           [B.shot(T, f's32_b8k3_{d["B8"]:.2f}', CTA_K3, d['B8'], z0=1.0, z1=1.12, fx=0.5, fy=0.62) + ([(259, 940, 801, 1620), (300, 720, 780, 860)],)])
    clay = dict(stopmo=True)
    return {
        'HA': [B.shot(T, f's32_ha_{d["HA"]:.2f}', k('k_cl_ha'), d['HA'], z0=1.0, z1=1.15, **clay) + ([(350, 560, 760, 900), (100, 900, 900, 1500)],)],
        'HB': [B.shot(T, f's32_hb_{d["HB"]:.2f}', k('k_cl_hb'), d['HB'], ss=0.3, z0=1.0, z1=1.15, fy=0.6, **clay) + ([(0, 760, 1080, 1100)],)],
        'HC': [B.shot(T, f's32_hc_{d["HC"]:.2f}', k('k_cl_hc'), d['HC'], z0=1.0, z1=1.05, **clay) + ([(130, 600, 900, 1300)],)],
        'HD': [B.shot(T, f's32_hd_{d["HD"]:.2f}', k('k_cl_hd'), d['HD'], ss=0.2, z0=1.0, z1=1.05, **clay) + ([(150, 820, 900, 1500)],)],
        'B1': [B.shot(T, f's32_b1_{d["B1"]:.2f}', k('k_cl_b12'), d['B1'], ss=0.0, z0=1.0, z1=1.04, **clay) + ([(180, 720, 820, 1180)],)],
        'B2': [B.shot(T, f's32_b2_{d["B2"]:.2f}', k('k_cl_b12'), d['B2'], ss=2.4, z0=1.04, z1=1.12, fy=0.45, **clay) + ([(180, 720, 820, 1180)],)],
        'B3': [B.shot(T, f's32_b3_{d["B3"]:.2f}', k('k_cl_b3'), d['B3'], ss=1.0, speed=1.25, z0=1.0, z1=1.04, **clay) + ([(180, 720, 820, 1500)],)],
        'B4': [B.shot(T, f's32_b4_{d["B4"]:.2f}', k('k_cl_b3'), d['B4'], ss=2.6, speed=1.4, z0=1.06, z1=1.1, **clay) + ([(180, 720, 820, 1500)],)],
        'B5': [B.shot(T, f's32_b5_{d["B5"]:.2f}', k('k_cl_b56'), d['B5'], ss=0.0, z0=1.0, z1=1.05, **clay) + ([(400, 560, 900, 1200)],)],
        'B6': [B.shot(T, f's32_b6_{d["B6"]:.2f}', k('k_cl_b56'), d['B6'], ss=2.2, speed=1.05, z0=1.05, z1=1.14, fy=0.5, **clay) + ([(250, 600, 900, 1200)],)],
        'B7': [B.shot(T, f's32_b7r_{d["B7"]:.2f}', f'{G}/a301/tmp/m31_rebote.mp4', d['B7'], z0=1.0, z1=1.04) + ([(300, 760, 780, 1460)],)],   # GEODA real (recorte) cae en la cama: el texto queda arriba, lejos de la piedra
        'B8': cta,
    }

if __name__ == '__main__':
    plan = {'HA': base, 'HB': base, 'HC': k2, 'HD': k2}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; print(hk, 'dur %.1f' % (cfg['hooks'][hk]['dur'] + sum(r['dur'] for r in cfg['body'])))
        B.build(cfg, hk, build_shots(cfg))
