#!/usr/bin/env python3
"""Prueba rápida del montaje en una sesión nueva (sin IA, sin costo): hook + 1 fila + CTA con recursos del kit.
uso: python3 geoda/pipeline/smoke_test.py   -> <trabajo>/smoke/GEO_TEST_A0_00_HA_DEMO_v1.mp4 (~7 s)"""
import os, sys, subprocess
G = os.environ.get('GEODA_WORK') or open(os.path.expanduser('~/.geoda_work')).read().strip()
sys.path.insert(0, G)
import builder as B
A = f'{G}/smoke'; T = f'{A}/tmp'; VO = f'{A}/vo'
for d in (T, VO): os.makedirs(d, exist_ok=True)
for k, d in (('HA', 2.6), ('B1', 2.4)):   # voz de prueba: tono suave (no se gasta cuota de voz)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'sine=frequency=220:duration={d}', '-af', 'volume=0.05',
                    '-ar', '24000', '-ac', '1', f'{VO}/{k}_t.wav'], check=True)
cfg = dict(id='GEO_TEST_A0_00', fmt='DEMO', version=1, tmp=T, out_dir=A, vo_dir=VO, ai_label=True,
           hooks={'HA': dict(vo='HA', dur=2.7, subs=False, text=('Prueba del montaje', 'GEODA listo'), line='Prueba del montaje.')},
           body=[dict(key='B1', vo='B1', dur=2.5, line='Se moja la piedra, no la axila.', big='1'),
                 dict(key='B2', vo='B1', dur=2.0, line='Llévala hoy.')],
           cta=dict(row='B2', l1='LLÉVALA HOY', l2='Pagas al recibir'))
K = f'{G}/kit'
shots = {'HA': [B.shot(T, 'ha', f'{K}/broll/k_tapa_0.mp4', 2.7, z0=1.0, z1=1.06) + ([(300, 300, 860, 1500)],)],
         'B1': [B.shot(T, 'b1', f'{K}/broll/k_grifo2_0.mp4', 2.5, z0=1.0, z1=1.05)],
         'B2': [B.shot(T, 'b2', f'{K}/producto/endcard_bano_anim.mp4', 2.0) + ([(259, 960, 801, 1600)],)]}
print(B.build(cfg, 'HA', shots))
