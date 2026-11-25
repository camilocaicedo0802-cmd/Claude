#!/usr/bin/env python3
"""GEO-TOFU-A1-04 · Street interview (voz principal hombre). Voces nativas de WAN 3.0; etiqueta real en tomas de producto."""
import os, sys, subprocess
import os
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
A = f'{G}/a104'; TMP = f'{A}/tmp'; os.makedirs(TMP, exist_ok=True)
HF = f'{G}/hf'
cfg = dict(
    id='GEO_TOFU_A1_04', fmt='STREET', version=4, ai_label=False, tmp=TMP, out_dir=A, vo_dir=TMP, min_face=50, hook_text_until=3.6,  # 3,6 s del montaje = 3,0 s del video final a x1.2
    speed=1.2,  # pedido de Camilo: todo el video a x1.2
    hooks={  # texto del hook = voz -> solo texto (sin subtítulo)
        'HA': dict(vo=None, clip_audio=True, dur=3.3, subs=False, text=('¿Cómo se usa la', 'piedra de alumbre?'),
                   line='Pregunta rápida: ¿usted sabe cómo se usa la piedra de alumbre?'),
        'HB': dict(vo=None, clip_audio=True, dur=3.8, subs=False, text=('Le preguntamos a', '5 personas en Bogotá'),
                   line='Le preguntamos a cinco personas y casi nadie acertó.',
                   extras=[dict(type='text', text='0/5', size=190, x=735, y=660, t0=0.15)]),
    },
    body=[
        dict(key='B1', clip_audio=True, dur=2.85, line='¿Seca? Uno se la frota y ya.', icon='❌'),
        dict(key='B2', clip_audio=True, dur=3.25, line='Ay, yo me mojo la axila primero.', icon='❌'),
        dict(key='B3', clip_audio=True, dur=2.6, line='Ni idea, mi abuela la usaba.', icon='❌'),
        dict(key='B4', clip_audio=True, dur=3.18, line='Es un desodorante mineral, y casi todos lo usan mal. Mire.', icon='👇'),   # brief corregido
        dict(key='B5', clip_audio=True, dur=2.19, line='Se moja la piedra, no la axila.'),
        dict(key='B6', clip_audio=True, dur=2.04, line='Y se pasa por la piel limpia.'),
        dict(key='B7', clip_audio=True, dur=2.18, line='¡Ahhh, con razón!', icon='😂'),
        dict(key='B8', clip_audio=True, dur=5.05, line='Se llama GEODA, y te la enviamos gratis a toda Colombia. La pagas al recibir.'),   # brief corregido
    ],
    cta=dict(row='B8', l1='ENVÍO GRATIS', l2='A TODA COLOMBIA'),   # + 'Pago contraentrega · Envío gratis' (cierre del brief)
)

def wav_from(src, ss, dur, out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{ss}', '-t', f'{dur}', '-i', src, '-vn', '-ac', '1', '-ar', '48000',
                    '-af', f'apad=whole_dur={dur}', out], check=True)

def build_shots():
    T = TMP
    ec, ec_box = f'{HF}/fixed/endcard_bano_real.png', (259, 960, 801, 1600)   # producto REAL de la landing en un baño
    w = lambda n: f'{HF}/{n}_0.mp4'
    fx = lambda n: f'{HF}/fixed/{n}_0.mp4'
    s = {
     # plano completo de la entrevista: el presentador le hace la pregunta a la señora con el micrófono (los dos en cuadro)
     'HA': [B.shot(T, 'ha', w('w_ha2'), 3.3, ss=0.50, z0=1.0, z1=1.04, audio=True)],
     'HB': [B.shot(T, 'hb', w('w_hb'), 3.8, ss=0.05, z0=1.0, z1=1.04, audio=True)],
     'B1': [B.shot(T, 'b1', w('w_i1'), 2.85, ss=0.0, z0=1.0, z1=1.05, audio=True)],
     'B2': [B.shot(T, 'b2', w('w_i2'), 3.25, ss=0.0, z0=1.0, z1=1.05, audio=True)],
     'B3': [B.shot(T, 'b3', w('w_i3'), 2.6, ss=0.15, z0=1.0, z1=1.05, audio=True) + ([B.protect((320, 340, 700, 800))],)],
     # frases nuevas del brief en un solo clip del presentador (verificadas); etiqueta original del clip
     'B4': [B.shot(T, 'b4', w('w_p3'), 3.18, ss=0.22, z0=1.0, z1=1.05, audio=True)],
     # gotas solo en la punta de la piedra (el tubo y la etiqueta quedan secos); etiqueta original de la imagen, sin capa
     'B5': [B.shot(T, 'b5', w('k_gota'), 2.19, ss=0.0, speed=1.0, z0=1.0, z1=1.06) + ([],)],
     # piedra hacia abajo sobre el antebrazo -> etiqueta real invertida (label_fix --flip --tube); solo el tramo de frente
     'B6': [B.shot(T, 'b6', fx('k_brazo2_flip'), 2.04, ss=0.0, z0=1.0, z1=1.06) + ([],)],   # sin residuo: la piedra no deja marca
     'B7': [B.shot(T, 'b7', w('w_i2'), 2.18, ss=4.85, z0=1.05, z1=1.1, audio=True)],
     'B8': [B.shot(T, 'b8a', w('k_map'), 2.6, ss=0.0, z0=1.0, z1=1.04) + ([],),
            B.shot(T, 'b8b', f'{HF}/fixed/endcard_bano_anim.mp4', 2.45, ss=0.0, z0=1.0, z1=1.04) + ([ec_box],)],   # cierre animado
    }
    # voz del presentador (clip WAN de la demostración) sobre el primer plano del antebrazo y el cierre
    P3 = w('w_p3')   # frases verificadas: 0,22-3,40 / 3,65-5,84 / 6,20-8,24 / 8,56-13,61
    wav_from(P3, 3.65, 2.19, f'{T}/b5.wav')
    wav_from(P3, 6.20, 2.04, f'{T}/b6.wav')
    wav_from(P3, 8.56, 2.6, f'{T}/b8a.wav')
    wav_from(P3, 11.16, 2.45, f'{T}/b8b.wav')
    return s

if __name__ == '__main__':
    shots = build_shots()
    for hk in sys.argv[1:] or ['HA', 'HB']:
        B.build(cfg, hk, shots)
