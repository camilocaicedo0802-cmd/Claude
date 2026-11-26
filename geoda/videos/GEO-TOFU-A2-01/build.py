#!/usr/bin/env python3
"""GEO-TOFU-A2-01 · UGC con avatar IA (Laura, M) · ~28 s (x1.1) · CTA principal K5 Paga contraentrega + alterno K2 Navidad.
Ángulo A2 (axilas más parejas): primera persona, nunca 'blanquear'/'aclarar', nunca la axila de cerca, sin antes/después.
NO PUBLICAR hasta que Alberto confirme el alcance del registro sanitario (brief). Voz en off de Laura (Gemini TTS Aoede, mismo
modelo en todas las frases; HD, B2 y B8 regrabadas). Laura nunca habla a cámara.
Versiones: HA y HB del brief con K5; HC y HD nuevos con K2. En el HB el hook ya dice 'levantaba el brazo con miedo': sin B4."""
import os, sys, copy
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a201'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
CTA_NAV = f'{G}/a108/tmp/cta_navidad.mp4'   # cierre animado del A1-08 (producto real + etiqueta REGALO NAVIDAD + botón)
SPEED = 1.1

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

DOOR = 2.0
base = dict(
    id='GEO_TOFU_A2_01', fmt='UGC', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0 * SPEED, speed=SPEED, music=f'{AU}/music_847.mp3', music_vol=0.10,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=True, text=('Dejé el desodorante con perfume', 'y pasó esto 👇'),
                   line='Dejé el desodorante con perfume y mis axilas empezaron a lucir más parejas.', sfx=[(0.45, f'{AU}/sfx_thud.wav', 0.6)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=True, text=('Ya me pongo blusa sin mangas', 'sin pensarlo'),
                   line='Yo antes levantaba el brazo con miedo. Ya no.'),
        # hooks nuevos para el CTA alterno (Navidad): escenas distintas al cuerpo y a los otros hooks
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Esta blusa estuvo 2 años', 'escondida en el clóset'),
                   line='Esta blusa sin mangas estuvo dos años escondida en el clóset.', sfx=[(0.3, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('Nadie me cree cuando les', 'cuento qué me pongo'),
                   line='Nadie me cree cuando les cuento qué me pongo en las axilas.'),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Llevaba años con desodorante de perfume fuerte.'),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Rasurada, a la carrera, ardor, y ropa apretada todo el día.'),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Y mis axilas no se veían como yo quería.', head='Algo no me cuadraba'),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Levantaba el brazo con miedo.', head='Brazo pegado 😬', sfx=[(0.5, f'{AU}/sfx_shutter.wav', 0.5)]),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Entonces descubrí una piedra mineral que se usa como desodorante, sin perfume.',
             sfx=[(0.6, f'{AU}/sfx_glint.wav', 0.3)]),
        dict(key='B6', vo='B6', dur=vd('B6'), line='La mojo, la paso todos los días, y le sumé hidratante.', sfx=[(0.1, f'{AU}/splash_1180.mp3', 0.3)]),
        dict(key='B7', vo='B7', dur=vd('B7'), line='Con las semanas, yo las veo más parejas. A mí me funcionó.'),
        dict(key='B8', vo='B8', dur=vd('B8', 0.5), line='Se llama GEODA, y no pagas nada ahora: la pagas cuando te llegue a la casa.'),
    ],
    cta=dict(row='B8', delay=DOOR, l1='PAGA CONTRAENTREGA', l2='Pagas cuando te llegue', pill='Envío gratis a toda Colombia 🚚'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'UGC_K2'
k2['body'][-1] = dict(key='B8', vo='B8k2', dur=vd('B8k2', 0.4), line='Se llama GEODA: una piedra que sí se usa todos los días. Regálala esta Navidad: paga dos, lleva tres.',
                      sfx=[(1.6, f'{AU}/sfx_tap.wav', 0.5), (3.4, f'{AU}/sfx_tap.wav', 0.5)])
k2['cta'] = dict(row='B8', delay=0.2, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3')
hb = copy.deepcopy(base); hb['body'] = [r for r in hb['body'] if r['key'] != 'B4']   # nada se repite entre hook y cuerpo

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/k_{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    d.setdefault('B4', 1.6)
    k2v = cfg['fmt'].endswith('K2')
    r1, r2 = 2.3, 0.85    # B2: 'Rasurada, a la carrera' / 'ardor' / 'y ropa apretada todo el día'
    m1 = 2.2              # B6: 'La mojo, la paso todos los días' / 'y le sumé hidratante'
    b8 = ([B.shot(T, f's_b8nav_{d["B8"]:.2f}', CTA_NAV, d['B8'], z0=1.0, z1=1.09, fx=0.5, fy=0.62)
           + ([(259, 940, 801, 1620), (75, 500, 405, 930), (400, 720, 880, 880)],)] if k2v else
          [B.shot(T, 's_b8a', k('l_b8'), DOOR, ss=0.0, z0=1.0, z1=1.04) + ([(250, 460, 1080, 820)],),
           B.shot(T, f's_b8b_{d["B8"]:.2f}', f'{KIT}/producto/endcard_bano_anim.mp4', d['B8'] - DOOR, ss=0.5, z0=1.0, z1=1.08, fx=0.5, fy=0.62)
           + ([(259, 940, 801, 1620)],)])
    return {
        # hooks: plano abierto con la pared vacía arriba (título); cajas = cabezas (con pelo) en todo el plano
        'HA': [B.shot(T, f's_ha_{d["HA"]:.2f}', k('l_ha'), d['HA'], z0=1.0, z1=1.04) + ([(360, 820, 720, 1140)],)],
        'HB': [B.shot(T, f's_hb_{d["HB"]:.2f}', k('l_hb'), d['HB'], ss=0.3, z0=1.0, z1=1.06) + ([(300, 840, 780, 1250)],)],
        'HC': [B.shot(T, f's_hc_{d["HC"]:.2f}', k('l_hc'), d['HC'], ss=0.2, z0=1.0, z1=1.04) + ([(450, 920, 780, 1230)],)],
        'HD': [B.shot(T, f's_hd_{d["HD"]:.2f}', k('l_hd'), d['HD'], ss=0.2, z0=1.0, z1=1.04) + ([(0, 840, 1080, 1190)],)],
        'B1': [B.shot(T, f's_b1_{d["B1"]:.2f}', k('l_b1'), d['B1'], z0=1.0, z1=1.04) + ([(300, 240, 820, 880)],)],
        'B2': [B.shot(T, 's_b2a', k('l_b2a'), r1, ss=0.4, z0=1.0, z1=1.05),
               B.shot(T, 's_b2b', k('l_b2b'), r2, ss=0.2, z0=1.0, z1=1.04) + ([(380, 400, 840, 900)],),
               B.shot(T, f's_b2c_{d["B2"]:.2f}', k('l_b2c'), d['B2'] - r1 - r2, ss=0.0, z0=1.0, z1=1.04) + ([(380, 400, 780, 900)],)],
        'B3': [B.shot(T, f's_b3_{d["B3"]:.2f}', k('l_b3'), d['B3'], z0=1.0, z1=1.04) + ([(400, 420, 820, 900)],)],
        'B4': [B.shot(T, f's_b4_{d["B4"]:.2f}', k('l_b4'), d['B4'], ss=0.6, z0=1.0, z1=1.04) + ([(0, 600, 1080, 930)],)],
        'B5': [B.shot(T, f's_b5_{d["B5"]:.2f}', k('l_b5'), d['B5'], z0=1.0, z1=1.03) + ([(320, 360, 870, 990), (40, 480, 400, 1200)],)],
        'B6': [B.shot(T, 's_b6a', f'{KIT}/broll/k_grifo_m_0.mp4', m1, ss=0.3, z0=1.0, z1=1.06) + ([(260, 540, 840, 1500)],),
               B.shot(T, f's_b6b_{d["B6"]:.2f}', k('l_b6'), d['B6'] - m1, ss=0.6, z0=1.0, z1=1.04) + ([(260, 480, 740, 960)],)],
        'B7': [B.shot(T, f's_b7_{d["B7"]:.2f}', k('l_b7'), d['B7'], z0=1.0, z1=1.04) + ([(230, 360, 640, 720)],)],
        'B8': b8,
    }

if __name__ == '__main__':
    plan = {'HA': base, 'HB': hb, 'HC': k2, 'HD': k2}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; B.build(cfg, hk, build_shots(cfg))
