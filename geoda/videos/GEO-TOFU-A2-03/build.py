#!/usr/bin/env python3
"""GEO-TOFU-A2-03 · 'Testimonio' (RECREACIÓN con creadora IA, Daniela) · ~30 s · CTA principal K6 Envío a toda Colombia
+ alterno K2 Navidad. El brief: si se hace con IA deja de ser testimonio -> se presenta como 'mi rutina' (primera persona,
sin prometer tiempos ni resultados: 'para mí', 'cada piel es distinta') y al publicar se activa la etiqueta de IA.
Ángulo A2: NO PUBLICAR hasta que Alberto confirme el registro sanitario; nunca la axila de cerca; sin 'blanquear'.
Voz: Gemini TTS Callirrhoe (todas con gemini-3.1-flash-tts-preview; B1 y B9 regrabadas con el mismo modelo).
Habla a cámara (HA, HC, B1, B2, B3): Wan 2.7 con la voz como audio_url -> los labios siguen la voz. El resto, voz en off.
Versiones: HA y HB del brief con K6; HC y HD nuevos con K2. En el HB el hook ya dice 'me rasuraba, me ardía': sin B1."""
import os, sys, copy
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a203'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'
XMAS = f'{G}/a202/tmp/xmas_ec_bow.mp4'   # cierre de Navidad del A2-02 (producto real + moño)

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

base = dict(
    id='GEO_TOFU_A2_03', fmt='TEST', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_821.mp3', music_vol=0.09,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Mi rutina para que mis', 'axilas luzcan parejas'),
                   line='Esta es mi rutina para que mis axilas luzcan parejas.'),
        'HB': dict(vo='HB', dur=vd('HB'), subs=False, text=('Me rasuraba, me ardía', 'y se veía peor'),
                   line='Me rasuraba, me ardía y se veía peor. Esto fue lo que cambié.', sfx=[(1.2, f'{AU}/sfx_thud.wav', 0.5)]),
        # hooks nuevos para el CTA alterno (Navidad): escenas distintas al cuerpo y a los otros hooks
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('Mi regalo de Navidad:', 'no esconder más los brazos'),
                   line='Mi regalo de Navidad para mí: dejar de esconder los brazos.'),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('Esto es lo que hay', 'en mi baño ahora'),
                   line='Esto es lo que hay en mi baño ahora.'),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Yo me rasuraba, a la carrera, y me ardía.'),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Y encima me echaba desodorante con perfume.'),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Cambié tres cosas.', big='3'),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Uno: rasurada sin afán.', big='1'),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Dos: descubrí una piedra mineral sin perfume y la cambié por el desodorante.', big='2', icon_x=210, big_y=370, big_size=230,
             sfx=[(2.6, f'{AU}/splash_1180.mp3', 0.3)]),
        dict(key='B6', vo='B6', dur=vd('B6'), line='Tres: hidratante en la noche.', big='3'),
        dict(key='B7', vo='B7', dur=vd('B7'), line='Ahora, para mí, se ven más parejas.'),
        dict(key='B8', vo='B8', dur=vd('B8'), line='Cada piel es distinta, pero esta es mi rutina.'),
        dict(key='B9', vo='B9', dur=vd('B9', 0.5), line='Se llama GEODA, y te la enviamos gratis a toda Colombia. La pagas al recibir.'),
    ],
    cta=dict(row='B9', delay=0.2, l1='ENVÍO GRATIS A TODA COLOMBIA', l2='La pagas al recibir', pill='Llega a tu casa 🚚'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'TEST_K2'
k2['body'][-1] = dict(key='B9', vo='B9k2', dur=vd('B9k2', 0.4), line='Se llama GEODA: una piedra que sí se usa todos los días. Regálala esta Navidad: paga dos, lleva tres.')
k2['cta'] = dict(row='B9', delay=0.2, l1='REGALO DE NAVIDAD', l2='Paga 2 lleva 3')
hb = copy.deepcopy(base); hb['body'] = [r for r in hb['body'] if r['key'] != 'B1']   # nada se repite entre hook y cuerpo

def build_shots(cfg):
    T = TMP; w = lambda n: f'{HF}/{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    d.setdefault('B1', 3.36)
    b5 = 2.5   # B5: Daniela con la piedra a contraluz / se moja (kit)
    b9 = ([B.shot(T, f's_b9nav_{d["B9"]:.2f}', XMAS, d['B9'], z0=1.0, z1=1.12, fx=0.5, fy=0.62) + ([(320, 940, 880, 1620)],)]
          if cfg['fmt'].endswith('K2') else
          [B.shot(T, f's_b9map_{d["B9"]:.2f}', f'{T}/cta_mapa.mp4', d['B9'], z0=1.0, z1=1.08, fx=0.5, fy=0.6) + ([(630, 940, 910, 1580)],)])
    return {
        # habla a cámara (Wan 2.7, labios con la voz): el clip arranca con la frase
        'HA': [B.shot(T, f's_ha_{d["HA"]:.2f}', w('w_ha'), d['HA'], z0=1.0, z1=1.10, fy=0.6) + ([(280, 800, 780, 1300)],)],
        'HB': [B.shot(T, f's_hb2_{d["HB"]:.2f}', f'{T}/hb_slow.mp4', d['HB'], z0=1.0, z1=1.18, fx=0.55, fy=0.7) + ([(150, 900, 1000, 1500)],)],   # caída real (2,55-4,6 s) en cámara lenta interpolada
        'HC': [B.shot(T, f's_hc_{d["HC"]:.2f}', w('w_hc'), d['HC'], z0=1.0, z1=1.10, fy=0.6) + ([(300, 740, 780, 1300)],)],
        'HD': [B.shot(T, f's_hd_{d["HD"]:.2f}', w('k_d_hd'), d['HD'], z0=1.0, z1=1.06)],
        'B1': [B.shot(T, f's_b1_{d["B1"]:.2f}', w('w_b1'), d['B1'], z0=1.0, z1=1.04) + ([(260, 240, 820, 840)],)],
        'B2': [B.shot(T, f's_b2_{d["B2"]:.2f}', w('w_b2'), d['B2'], z0=1.0, z1=1.04) + ([(280, 280, 840, 880), (120, 420, 440, 1080)],)],
        'B3': [B.shot(T, f's_b3_{d["B3"]:.2f}', w('w_b3'), d['B3'], z0=1.0, z1=1.04) + ([(280, 280, 840, 880), (80, 700, 460, 1120)],)],
        'B4': [B.shot(T, f's_b4_{d["B4"]:.2f}', w('k_d_b4'), d['B4'], z0=1.0, z1=1.04)],
        'B5': [B.shot(T, 's_b5a', w('k_d_b5'), b5, z0=1.0, z1=1.04) + ([(320, 360, 880, 980), (40, 520, 420, 1180)],),
               B.shot(T, f's_b5b_{d["B5"]:.2f}', f'{KIT}/broll/k_grifo_m_0.mp4', d['B5'] - b5, ss=0.3, z0=1.0, z1=1.06) + ([(260, 540, 840, 1500)],)],
        'B6': [B.shot(T, f's_b6_{d["B6"]:.2f}', w('k_d_b6'), d['B6'], z0=1.0, z1=1.04) + ([(280, 260, 780, 780)],)],
        'B7': [B.shot(T, f's_b7_{d["B7"]:.2f}', w('k_d_b7'), d['B7'], z0=1.0, z1=1.05) + ([(360, 360, 660, 660)],)],
        'B8': [B.shot(T, f's_b8_{d["B8"]:.2f}', f'{KIT}/broll/k_tapa_0.mp4', d['B8'], z0=1.0, z1=1.08) + ([(300, 520, 780, 1460)],)],
        'B9': b9,
    }

if __name__ == '__main__':
    plan = {'HA': base, 'HB': hb, 'HC': k2, 'HD': k2}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; B.build(cfg, hk, build_shots(cfg))
