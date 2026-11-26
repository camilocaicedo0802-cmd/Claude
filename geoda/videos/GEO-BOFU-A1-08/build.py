#!/usr/bin/env python3
"""GEO-BOFU-A1-08 · UGC con avatar IA (Mateo, H) · ~21 s · CTA principal K1 Black Friday (sin precio) + alterno K2 Navidad.
Voz en off de Mateo (Gemini TTS Fenrir, una sola toma; B5 y B6 regrabadas con la misma voz). Mateo nunca habla a cámara.
Versiones (un hook distinto por versión): HA y HB del brief con K1; HC y HD nuevos con K2.
En el HA el hook ya dice 'si en 14 días no te funciona, te devolvemos tu dinero': se quita el plano del calendario (B2)."""
import os, sys, copy
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = f'{G}/a108'; TMP = f'{OUT}/tmp'; os.makedirs(TMP, exist_ok=True)
HF, AU = f'{G}/hf', f'{G}/audio'
VO = f'{AQUI}/vo' if os.path.isdir(f'{AQUI}/vo') else f'{OUT}/vo'
KIT = f'{G}/kit' if os.path.isdir(f'{G}/kit') else '/home/user/Claude/geoda/kit'

def vd(k, extra=0.0):
    return round(B.dur_of(f'{VO}/{k}_t.wav') + 0.12 + extra, 2)

TAPS = [(1.6, f'{AU}/sfx_tap.wav', 0.5), (3.4, f'{AU}/sfx_tap.wav', 0.5)]   # toques al botón Comprar (clip del cierre arranca 0,2 s antes)
base = dict(
    id='GEO_BOFU_A1_08', fmt='UGC', version=1, tmp=TMP, out_dir=OUT, vo_dir=VO,
    min_face=50, ai_label=False, hook_text_until=3.0, music=f'{AU}/music_805.mp3', music_vol=0.10,
    hooks={
        'HA': dict(vo='HA', dur=vd('HA'), subs=False, text=('Si en 14 días no te funciona,', 'te devolvemos la plata'),
                   line='Dale otra oportunidad a la piedra: si en catorce días no te funciona, te devolvemos tu dinero.',
                   extras=[dict(type='stamp', text='14 DÍAS', x=790, y=1080, t0=0.35, size=110)],
                   sfx=[(0.35, f'{AU}/sfx_thud.wav', 0.7)]),
        'HB': dict(vo='HB', dur=vd('HB'), subs=True, text=('Dale otra oportunidad', 'a la piedra, sin riesgo'),
                   line='Ya sabes usarla. Ahora pruébala sin riesgo.', sfx=[(0.35, f'{AU}/sfx_glint.wav', 0.3)]),
        # hooks nuevos para el CTA alterno (Navidad): escenas distintas al cuerpo y a los otros hooks
        'HC': dict(vo='HC', dur=vd('HC'), subs=False, text=('¿Te regalaron la piedra', 'y no te funcionó? 🎁'),
                   line='¿Te regalaron la piedra y no te funcionó? Dale otra oportunidad.', sfx=[(0.6, f'{AU}/sfx_glint.wav', 0.3)]),
        'HD': dict(vo='HD', dur=vd('HD'), subs=False, text=('Antes de botar la piedra', 'a la basura, escúchame 👇'),
                   line='Antes de botar la piedra a la basura, escúchame.', sfx=[(0.1, f'{AU}/sfx_error.wav', 0.25)]),
    },
    body=[
        dict(key='B1', vo='B1', dur=vd('B1'), line='Ya sabes el truco: mojar, aplicar, secar.', sfx=[(0.3, f'{AU}/splash_1180.mp3', 0.3)]),
        dict(key='B2', vo='B2', dur=vd('B2'), line='Si en catorce días no te funciona, te devolvemos tu dinero.', head='✅ Garantía 14 días'),
        dict(key='B3', vo='B3', dur=vd('B3'), line='Y no pagas nada por adelantado.', head='Pagas al recibir 📦'),
        dict(key='B4', vo='B4', dur=vd('B4'), line='Paga dos y lleva tres.'),
        dict(key='B5', vo='B5', dur=vd('B5'), line='Una para ti, y dos de repuesto, o para regalar.'),
        dict(key='B6', vo='B6', dur=vd('B6', 0.48), line='Es Black Friday en GEODA: paga dos y lleva tres, y pagas cuando te llegue.', sfx=TAPS),
    ],
    cta=dict(row='B6', delay=0.2, l1='BLACK FRIDAY', l2='Paga 2 lleva 3'),
)
k2 = copy.deepcopy(base); k2['fmt'] = 'UGC_K2'
k2['body'][-1] = dict(key='B6', vo='B6k2', dur=vd('B6k2', 0.5), line='Regala algo que sí se usa todos los días: GEODA. Paga dos, lleva tres, y reparte en Navidad.', sfx=TAPS)
k2['cta'] = dict(row='B6', delay=0.2, l1='REGALA GEODA EN NAVIDAD', l2='Paga 2 lleva 3')
ha = copy.deepcopy(base); ha['body'] = [r for r in ha['body'] if r['key'] != 'B2']   # nada se repite entre hook y cuerpo

def build_shots(cfg):
    T = TMP; k = lambda n: f'{HF}/k_{n}_0.mp4'
    d = {r['key']: r['dur'] for r in [dict(key=h, **cfg['hooks'][h]) for h in cfg['hooks']] + cfg['body']}
    d.setdefault('B2', 3.03)   # el HA no lleva B2 (no se usa)
    cta = 'cta_navidad' if cfg['fmt'].endswith('K2') else 'cta_bf'
    a1, a2 = 1.85, 0.90   # cortes en 'mojar' / 'aplicar' / 'secar'
    return {
        'HA': [B.shot(T, f's_ha_{d["HA"]:.2f}', k('m_ha'), d['HA'], z0=1.0, z1=1.05)],
        'HB': [B.shot(T, f's_hb_{d["HB"]:.2f}', k('m_hb'), d['HB'], ss=0.3, speed=1.25, z0=1.0, z1=1.04)],
        'HC': [B.shot(T, f's_hc_{d["HC"]:.2f}', k('m_hc'), d['HC'], ss=0.4, speed=1.2, z0=1.0, z1=1.04)],
        'HD': [B.shot(T, f's_hd_{d["HD"]:.2f}', k('m_hd'), d['HD'], ss=0.0, speed=1.3, z0=1.0, z1=1.06)],
        # montaje de 3 cortes: agua en la punta de la piedra (kit) / Mateo la pasa (solo 0,1-1,0 s: piel limpia) / se seca (kit)
        'B1': [B.shot(T, 's_b1a', f'{KIT}/broll/k_grifo_m_0.mp4', a1, ss=0.3, z0=1.0, z1=1.06),
               B.shot(T, 's_b1b', k('m_apl'), a2, ss=0.1, z0=1.04, z1=1.08),
               B.shot(T, f's_b1c_{d["B1"]:.2f}', f'{KIT}/broll/k_toalla_0.mp4', d['B1'] - a1 - a2, ss=0.8, z0=1.0, z1=1.04)],
        'B2': [B.shot(T, f's_b2_{d["B2"]:.2f}', k('m_cal'), d['B2'], ss=0.5, z0=1.0, z1=1.04) + ([(600, 580, 1080, 1520)],)],
        'B3': [B.shot(T, f's_b3_{d["B3"]:.2f}', k('m_door'), d['B3'], ss=0.0, z0=1.0, z1=1.04)],
        'B4': [B.shot(T, f's_b4_{d["B4"]:.2f}', k('m_tres'), d['B4'], ss=0.0, z0=1.0, z1=1.03) + ([(100, 800, 980, 1800)],)],
        'B5': [B.shot(T, f's_b5_{d["B5"]:.2f}', k('m_amigos'), d['B5'], ss=0.0, z0=1.0, z1=1.04)],
        'B6': [B.shot(T, f's_b6_{cta}_{d["B6"]:.2f}', f'{T}/{cta}.mp4', d['B6'], z0=1.0, z1=1.09, fx=0.5, fy=0.62)
               + ([(259, 940, 801, 1620), (75, 500, 405, 930), (400, 720, 880, 880)],)],
    }

if __name__ == '__main__':
    plan = {'HA': ha, 'HB': base, 'HC': k2, 'HD': k2}
    for hk in sys.argv[1:] or list(plan):
        cfg = plan[hk]; B.build(cfg, hk, build_shots(cfg))
