#!/usr/bin/env python3
"""A1-06: hooks nuevos C (abrazo) y D (la piedra de mamá) para la versión con CTA alterno K2 Navidad.
K4 (principal) sigue con HA (v8) y HB (v5) del brief."""
import sys, importlib.util, os
AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('b106', f'{AQUI}/build_a106.py'); m = importlib.util.module_from_spec(spec)
args = sys.argv[1:]; sys.argv = ['x']; spec.loader.exec_module(m)
B, k2 = m.B, m.k2
k2['version'] = 1
def vd(key): return B.dur_of(f'{m.VO}/{key}_t.wav') + 0.12
k2['hooks']['HC'] = dict(vo='HC', dur=vd('HC'), subs=False, text=('POV: te abrazan', 'y no pegas los brazos 🙌'),
                         line='POV: te abrazan... y ya no tienes que pegar los brazos.')
k2['hooks']['HD'] = dict(vo='HD', dur=vd('HD'), subs=False, text=('POV: le robaste', 'la piedra a tu mamá 🤫'),
                         line='POV: le sacaste la piedra a tu mamá del baño.')
shots = m.build_shots(k2)
k = lambda n: f'{m.HF}/{n}_0.mp4'
shots['HC'] = [B.shot(m.TMP, 's_hc2', k('k_j_abrazo'), k2['hooks']['HC']['dur'], z0=1.0, z1=1.03, framed=0.78) + ([(250, 700, 960, 1500)],)]
if os.path.exists(k('k_j_robo')):
    shots['HD'] = [B.shot(m.TMP, 's_hd', k('k_j_robo'), k2['hooks']['HD']['dur'], z0=1.0, z1=1.04)]
for hk in args or ['HC', 'HD']:
    if hk in shots: B.build(k2, hk, shots)
    else: print('falta el clip de', hk)
