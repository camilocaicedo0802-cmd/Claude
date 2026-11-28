#!/usr/bin/env python3
"""GEO-BOFU-A2-08 · Unboxing (solo manos, POV) · ~19-23 s · CTA principal K3 'Llévala hoy' + alterno K2 Navidad.
Voz en off de Valentina: Gemini TTS gemini-3.8-flash-tts (regla 47), voz Autonoe, una sola toma (la 1; las tomas 2-3
pronunciaban mal "GEODA" y no se pueden mezclar: otro tono). Sin caras, solo manos. Producto real (recorte) en la cama y el cierre.
Ángulo A2: NO PUBLICAR hasta que Alberto confirme el registro sanitario.
Versiones: HA y HB (hooks del brief) con K3; HC y HD (hooks nuevos) con K2. HA quita B1 (es el mismo texto del hook).
La frase "Lo que llega en esta caja reemplazó mi desodorante" (hook D) va en el cuerpo de A y B (fila X) para que lleguen a 18 s."""
import os, sys, copy, subprocess
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a208'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
CTA_NAV = f'{G}/a108/tmp/cta_navidad.mp4'     # producto real + etiqueta REGALO NAVIDAD + Comprar (A1-08, 7,8 s)

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

base = dict(
    id='GEO_BOFU_A2_08', fmt='UNBOX', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_821.mp3', music_vol=0.07,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Me llegó GEODA y', 'la pagué al recibir 💵'),
                   line='Me llegó, y la pagué cuando el domiciliario me la entregó.', sfx=[(0.2, f'{AU}/sfx_1109.mp3', 0.25)]),
        'HB': dict(vo='HB', dur=vd('HB', 0.25), subs=False, text=('Abre conmigo', 'mi piedra GEODA 📦'),
                   line='Ven, la abrimos juntas.', sfx=[(0.05, f'{AU}/sfx_scratch.wav', 0.45)]),
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Unboxing de mi regalo', 'de Navidad 🎁'),
                   line='Unboxing de mi regalo de Navidad... para mí misma.', sfx=[(1.2, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('Lo que llega en esta caja', 'reemplazó mi desodorante'),
                   line='Lo que llega en esta caja reemplazó mi desodorante.', sfx=[(0.4, f'{AU}/sfx_thud.wav', 0.4)]),
    },
    body=[
        dict(key='B1', vo='HA', dur=vd('HA'), line='Me llegó, y la pagué cuando el domiciliario me la entregó.', head='Pagué al recibir 💵'),
        dict(key='X', vo='HD', dur=vd('HD'), line='Lo que llega en esta caja reemplazó mi desodorante.'),
        dict(key='B2', vo='B2', dur=vd('B2', 0.25), line='Abramos.', head='📦', sfx=[(0.1, f'{AU}/sfx_scratch.wav', 0.35)]),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Ahí está: la piedra GEODA.', head='La piedra 🪨', sfx=[(1.1, f'{AU}/sfx_glint.wav', 0.3)]),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Primera vez: la mojo... y la paso.', head='Primera aplicación 💧', sfx=[(0.1, f'{AU}/splash_1180.mp3', 0.3)]),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Pedí el paga dos, lleva tres, así que tengo para regalar.', head='3 piedras',
             sfx=[(0.1, f'{AU}/sfx_2357.mp3', 0.4), (0.5, f'{AU}/sfx_2357.mp3', 0.4), (0.9, f'{AU}/sfx_2357.mp3', 0.4)]),
        dict(key='B6', vo='B6', dur=vd('B6', 0.6), line='Llévala hoy: pídela ya, y la pagas cuando te llegue a la puerta.',
             sfx=[(1.8, f'{AU}/sfx_tap.wav', 0.5), (3.4, f'{AU}/sfx_tap.wav', 0.5)]),
    ],
    cta=dict(row='B6', delay=0.2, l1='LLÉVALA HOY', l2='Pagas al recibir'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'UNBOX_K2'
k2['body'][-1] = dict(key='B6', vo='B6k2', dur=vd('B6k2', 0.5), line='Regala algo que sí se usa todos los días: GEODA. Paga dos, lleva tres, y reparte en Navidad.',
                      sfx=[(1.6, f'{AU}/sfx_tap.wav', 0.5), (3.4, f'{AU}/sfx_tap.wav', 0.5)])
k2['cta'] = dict(row='B6', delay=0.2, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3')
def sin(cfg, *keys):
    c = copy.deepcopy(cfg); c['body'] = [r for r in c['body'] if r['key'] not in keys]; return c

def local(name, dur):
    out = f'{TMP}/m8_{name}.mp4'
    if not os.path.exists(out) or B.dur_of(out) < dur:
        subprocess.run([sys.executable, f'{AQUI}/mg208.py', name, f'{dur + 0.3:.2f}'], check=True)
    return out

def vaiven(src, a, b, out):
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(b - a), '-i', src, '-filter_complex',
                        '[0:v]split[x][y];[y]reverse[r];[x][r]concat=n=2:v=1:a=0,setpts=PTS-STARTPTS', '-an', '-c:v', 'libx264',
                        '-crf', '14', '-pix_fmt', 'yuv420p', out], check=True)
    return out

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    for kk, v in (('B1', 3.20), ('X', 3.21)): d.setdefault(kk, v)
    entrega = vaiven(k('k_u_ha'), 0.0, 1.3, f'{T}/entrega_vaiven.mp4')   # después de 1,3 s la caja queda flotando
    g = 1.2
    cta = ([B.shot(T, f's8_b6nav_{d["B6"]:.2f}', CTA_NAV, d['B6'], z0=1.0, z1=1.09, fx=0.5, fy=0.62) + ([(259, 940, 801, 1620), (75, 500, 405, 930), (400, 720, 880, 880)],)]
           if cfg['fmt'].endswith('K2') else
           [B.shot(T, f's8_b6k3_{d["B6"]:.2f}', local('cta_k3', 5.6), d['B6'], z0=1.0, z1=1.14, fx=0.5, fy=0.62) + ([(259, 940, 801, 1620), (300, 720, 780, 860)],)])
    return {
        'HA': [B.shot(T, f's8_ha_{d["HA"]:.2f}', entrega, d['HA'], speed=0.85, z0=1.0, z1=1.12) + ([(0, 700, 1080, 1560)],)],
        'HB': [B.shot(T, f's8_hb_{d["HB"]:.2f}', k('k_u_hb'), d['HB'], ss=0.2, z0=1.0, z1=1.06, fx=0.6, fy=0.6) + ([(500, 760, 1080, 1300)],)],
        'HC': [B.shot(T, f's8_hc_{d["HC"]:.2f}', k('k_u_hc'), d['HC'], ss=0.3, z0=1.0, z1=1.05) + ([(380, 760, 1000, 1400)],)],
        'HD': [B.shot(T, f's8_hd_{d["HD"]:.2f}', k('k_u_hd'), d['HD'], ss=1.4, z0=1.0, z1=1.08) + ([(180, 780, 1000, 1500)],)],
        'B1': [B.shot(T, f's8_b1_{d["B1"]:.2f}', entrega, d['B1'], speed=0.85, z0=1.06, z1=1.1) + ([(0, 700, 1080, 1560)],)],
        'X': [B.shot(T, f's8_x_{d["X"]:.2f}', k('k_u_hd'), d['X'], ss=1.4, z0=1.04, z1=1.12) + ([(180, 780, 1000, 1500)],)],
        'B2': [B.shot(T, f's8_b2_{d["B2"]:.2f}', k('k_u_b2'), d['B2'], ss=1.8, z0=1.0, z1=1.05) + ([(150, 700, 1000, 1500)],)],
        'B3': [B.shot(T, f's8_b3_{d["B3"]:.2f}', k('k_u_b3'), d['B3'], ss=0.0, z0=1.0, z1=1.05) + ([(300, 360, 820, 1260)],)],
        'B4': [B.shot(T, 's8_b4a', f'{KIT}/broll/k_grifo_m_0.mp4', g, ss=0.3, z0=1.0, z1=1.05) + ([(350, 560, 960, 1560)],),
               B.shot(T, f's8_b4b_{d["B4"]:.2f}', f'{KIT}/broll/k_grifo2_0.mp4', d['B4'] - g, ss=0.2, z0=1.0, z1=1.05) + ([(350, 560, 960, 1560)],)],
        'B5': [B.shot(T, f's8_b5_{d["B5"]:.2f}', local('cama', 4.0), d['B5'], z0=1.0, z1=1.0) + ([(150, 800, 930, 1420)],)],
        'B6': cta,
    }

if __name__ == '__main__':
    plan = {'HA': sin(base, 'B1'), 'HB': base, 'HC': sin(k2, 'X'), 'HD': sin(k2, 'X')}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; print(hk, 'dur %.1f' % (cfg['hooks'][hk]['dur'] + sum(r['dur'] for r in cfg['body'])))
        B.build(cfg, hk, build_shots(cfg))
