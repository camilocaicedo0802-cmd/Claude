#!/usr/bin/env python3
"""GEO-TOFU-A1-04 · Street interview (voz principal hombre). Voces nativas de WAN 3.0; etiqueta real en tomas de producto."""
import os, sys, subprocess
G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
sys.path.insert(0, G)
import builder as B
A = f'{G}/a104'; TMP = f'{A}/tmp'; os.makedirs(TMP, exist_ok=True)
HF = f'{G}/hf'
cfg = dict(
    id='GEO_TOFU_A1_04', fmt='STREET', version=1, tmp=TMP, out_dir=A, vo_dir=TMP, min_face=50, hook_text_until=3.0,
    hooks={  # texto del hook = voz -> solo texto (sin subtítulo)
        'HA': dict(vo=None, clip_audio=True, dur=3.4, subs=False, text=('¿Cómo se usa la', 'piedra de alumbre?'),
                   line='Pregunta rápida: ¿usted sabe cómo se usa la piedra de alumbre?'),
        'HB': dict(vo=None, clip_audio=True, dur=3.8, subs=False, text=('Le preguntamos a', '5 personas en Bogotá'),
                   line='Le preguntamos a cinco personas y casi nadie acertó.',
                   extras=[dict(type='text', text='0/5', size=210, x=820, y=640, t0=0.15)]),
    },
    body=[
        dict(key='B1', clip_audio=True, dur=2.85, line='¿Seca? Uno se la frota y ya.', icon='❌'),
        dict(key='B2', clip_audio=True, dur=3.25, line='Ay, yo me mojo la axila primero.', icon='❌'),
        dict(key='B3', clip_audio=True, dur=2.6, line='Ni idea, mi abuela la usaba.', icon='❌'),
        dict(key='B4', clip_audio=True, dur=2.75, line='Por eso dicen que no sirve. Mire.', icon='👇'),
        dict(key='B5', clip_audio=True, dur=3.45, line='Se moja la piedra, no la axila.'),
        dict(key='B6', clip_audio=True, dur=2.5, line='Y se pasa por la piel limpia.'),
        dict(key='B7', clip_audio=True, dur=2.18, line='¡Ahhh, con razón!', icon='😂'),
        dict(key='B8', clip_audio=True, dur=4.5, line='Te la enviamos gratis a toda Colombia, y la pagas al recibir.'),
    ],
    cta=dict(row='B8', l1='ENVÍO GRATIS', l2='A TODA COLOMBIA', pill='Pagas al recibir 🚚'),
)

def wav_from(src, ss, dur, out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{ss}', '-t', f'{dur}', '-i', src, '-vn', '-ac', '1', '-ar', '48000',
                    '-af', f'apad=whole_dur={dur}', out], check=True)

def build_shots():
    T = TMP; ec, ec_box = B.endcard(T)
    w = lambda n: f'{HF}/{n}_0.mp4'
    fx = lambda n: f'{HF}/fixed/{n}_0.mp4'
    s = {
     'HA': [B.shot(T, 'ha', w('w_ha'), 3.4, ss=0.15, z0=1.0, z1=1.05, audio=True)],
     'HB': [B.shot(T, 'hb', w('w_hb'), 3.8, ss=0.05, z0=1.0, z1=1.04, audio=True)],
     'B1': [B.shot(T, 'b1', w('w_i1'), 2.85, ss=0.0, z0=1.0, z1=1.05, audio=True)],
     'B2': [B.shot(T, 'b2', w('w_i2'), 3.25, ss=0.0, z0=1.0, z1=1.05, audio=True)],
     'B3': [B.shot(T, 'b3', w('w_i3'), 2.6, ss=0.15, z0=1.0, z1=1.05, audio=True) + ([B.protect((320, 340, 700, 800))],)],
     'B4': [B.shot(T, 'b4', fx('w_p1'), 2.75, ss=0.0, z0=1.0, z1=1.05, audio=True)],
     'B5': [B.shot(T, 'b5', fx('w_p1'), 3.45, ss=3.2, z0=1.05, z1=1.12, audio=True)],
     'B6': [B.shot(T, 'b6', fx('k_brazo'), 2.5, ss=0.2, z0=1.0, z1=1.06) + ([],)],
     'B7': [B.shot(T, 'b7', w('w_i2'), 2.18, ss=4.85, z0=1.05, z1=1.1, audio=True)],
     'B8': [B.shot(T, 'b8a', w('k_map'), 2.6, ss=0.0, z0=1.0, z1=1.04) + ([],),
            B.shot(T, 'b8b', ec, 1.9, still=True, z0=1.0, z1=1.04) + ([ec_box],)],
    }
    # voz del presentador (clip WAN de la demostración) sobre el primer plano del antebrazo y el cierre
    wav_from(w('w_p2'), 0.35, 2.5, f'{T}/b6.wav')
    wav_from(w('w_p2'), 3.55, 2.6, f'{T}/b8a.wav')
    wav_from(w('w_p2'), 6.15, 1.9, f'{T}/b8b.wav')
    return s

if __name__ == '__main__':
    shots = build_shots()
    for hk in sys.argv[1:] or ['HA', 'HB']:
        B.build(cfg, hk, shots)
