#!/usr/bin/env python3
"""PLANTILLA de montaje de un video GEODA. Copiar a geoda/videos/<ID>/build.py y llenar.
Ejemplos reales: build_a101_v2.py (UGC voz en off), build_a102_v3.py (demo), build_a103_v2.py (clay),
build_a104.py (street con audio nativo WAN), build_a105.py (podcast con sincronía de labios).

Rutas:
  G            carpeta de trabajo (setup_work.sh)        -> G/hf (generados), G/kit (recursos reales del repo)
  AQUI         geoda/videos/<ID> en el repo               -> vo/*_t.wav (voces verificadas), motion.py, assets.json
  OUT          G/<id>                                     -> mp4 finales + tmp/
"""
import os, sys
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
ID, ETAPA, ANG, NN, FMT, VERSION = 'GEO_TOFU_A2_AxilasMasParejas_01', 'TOFU', 'A2', '01', 'UGC', 1   # <- llenar (ángulo con su nombre corto, ver LOTES.md)
OUT = f'{G}/{ID.lower()}'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, K, VO, AU = f'{G}/hf', f'{G}/kit', f'{AQUI}/vo', f'{G}/kit/audio'
SPEED = 1.0          # 1.05-1.2 si la voz deja el video largo (TOFU 21-39 s, MOFU 30-51, BOFU 18-24)

def vd(k):           # duración de la fila = voz verificada + 0,12 s
    return B.dur_of(f'{VO}/{k}_t.wav') + 0.12

cfg = dict(
    id=ID, fmt=FMT, version=VERSION, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50,                 # caras pequeñas también se protegen
    ai_label=False,              # sin rótulo 'Recreación con IA' (Camilo); la etiqueta IA se activa en la plataforma al publicar
    hook_text_until=3.0 * SPEED, speed=SPEED, music=f'{AU}/music_821.mp3',   # music_805 / 821 / 847
    hooks={
        # text=(línea blanca, línea amarilla grande). Si el texto dice lo mismo que la voz -> subs=False.
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Texto del hook A', 'segunda línea'), line='Frase exacta de la voz.',
                   sfx=[(0.0, f'{AU}/sfx_glint.wav', 0.3)]),           # (segundos desde el inicio de la fila, archivo, volumen)
        'HB': dict(vo='HB', dur=vd('HB'), subs=True, text=('Texto del hook B', 'segunda línea'), line='Frase exacta de la voz.'),
    },
    body=[  # una fila por frase del guion; sin titulares que repitan la voz (queda el subtítulo)
        dict(key='B1', vo='B1', dur=vd('B1'), line='Frase exacta.', icon='🪨'),        # icon: emoji grande a la derecha
        dict(key='B2', vo='B2', dur=vd('B2'), line='Uno: se moja la piedra, no la axila.', big='1'),  # número de paso
        dict(key='B3', vo='B3', dur=vd('B3'), line='Frase exacta.', sub_y=440),          # sub_y: fija el subtítulo (no tapar la piedra)
        dict(key='B4', vo='B4', dur=vd('B4'), line='Se llama GEODA, ...'),
    ],
    # CTA del brief (sin precios salvo que Camilo lo pida). delay: segundos dentro de la fila antes de la tarjeta.
    cta=dict(row='B4', delay=1.5, l1='PAGA CONTRAENTREGA', l2='Pagas cuando te llegue'),   # pill= opcional
)

def build_shots(cfg):
    T = TMP; ec, ec_box = f'{K}/producto/endcard_bano_anim.mp4', (259, 960, 801, 1600)   # producto real en el baño, ANIMADO
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    # B.shot(tmp, nombre, fuente, duración, ss=inicio, speed=, z0/z1=zoom, fx/fy=punto del zoom, still=foto, stopmo=12 fps)
    # + ([cajas],) opcional: zonas que ningún texto tapa (cara, piedra, etiqueta). Sin caja: detecta caras/etiqueta solo.
    # REGLA: NADA estático. Personas, fondos y producto siempre en video (Kling/WAN o animación propia); no usar still=True.
    # (Ojo: los montajes del A1-01 al A1-05 son anteriores a esta regla y tienen algunas fotos fijas de personas: no copiarlas.)
    return {
        'HA': [B.shot(T, 'ha', f'{K}/broll/k_tapa_0.mp4', d['HA'], z0=1.0, z1=1.08) + ([(300, 300, 860, 1500)],)],
        'HB': [B.shot(T, 'hb', f'{K}/broll/k_tapa_0.mp4', d['HB'], z0=1.0, z1=1.1)],
        'B1': [B.shot(T, 'b1', f'{K}/broll/k_grifo2_0.mp4', d['B1'], speed=0.8, z0=1.0, z1=1.05)],
        'B2': [B.shot(T, 'b2', f'{K}/broll/k_grifo_m_0.mp4', d['B2'])],
        'B3': [B.shot(T, 'b3', f'{K}/broll/k_toalla_0.mp4', d['B3'], speed=0.6)],
        'B4': [B.shot(T, 'b4a', f'{K}/broll/k_tres_0.mp4', 1.5),
               B.shot(T, 'b4b', ec, d['B4'] - 1.5, ss=0.0, z0=1.0, z1=1.05) + ([ec_box],)],
    }

if __name__ == '__main__':
    shots = build_shots(cfg)
    for hk in sys.argv[1:] or ['HA', 'HB']:
        B.build(cfg, hk, shots)    # -> OUT/GEO_..._HA_<FMT>_v<n>.mp4
