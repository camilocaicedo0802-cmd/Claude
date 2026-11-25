#!/usr/bin/env python3
"""A1-06: hooks nuevos C (abrazo) y D (la piedra de mamá) para la versión con CTA alterno K2 Navidad.
K4 (principal) sigue con HA (v8) y HB (v5) del brief."""
import sys, importlib.util, os
AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('b106', f'{AQUI}/build_a106.py'); m = importlib.util.module_from_spec(spec)
args = sys.argv[1:]; sys.argv = ['x']; spec.loader.exec_module(m)
B, k2 = m.B, m.k2
k2['version'] = 2
def vd(key): return B.dur_of(f'{m.VO}/{key}_t.wav') + 0.12
k2['hooks']['HC'] = dict(vo='HC', dur=vd('HC'), subs=False, text=('POV: te abrazan', 'y no pegas los brazos 🙌'),
                         line='POV: te abrazan... y ya no tienes que pegar los brazos.', hook_slots=[1090, 1060])
k2['hooks']['HD'] = dict(vo='HD', dur=vd('HD'), subs=False, text=('POV: le robaste', 'la piedra a mamá 🤫'),
                         line='POV: le sacaste la piedra a tu mamá del baño.', hook_cx=360, hook_maxw=620, hook_slots=[380, 360, 400])
shots = m.build_shots(k2)
k = lambda n: f'{m.HF}/{n}_0.mp4'
shots['HC'] = [B.shot(m.TMP, 's_hc3', k('k_j_abrazo'), k2['hooks']['HC']['dur'], z0=1.0, z1=1.03) + ([(260, 150, 680, 700), (460, 400, 1040, 900)],)]   # pantalla completa
if os.path.exists(k('k_j_robo')):
    shots['HD'] = [B.shot(m.TMP, 's_hd3', k('k_j_robo'), k2['hooks']['HD']['dur'], z0=1.0, z1=1.03) + ([(700, 330, 980, 640), (230, 580, 600, 1320)],)]   # pantalla completa
for hk in args or ['HC', 'HD']:
    if hk in shots: B.build(k2, hk, shots)
    else: print('falta el clip de', hk)
