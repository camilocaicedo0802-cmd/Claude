#!/usr/bin/env python3
"""A1-03: hooks nuevos C (reunión) y D (ascensor) para la versión con CTA alterno K5 (cada versión arranca con un hook distinto).
K1 (principal) sigue con HA y HB del brief."""
import sys, importlib.util, os
AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('b103', f'{AQUI}/build_a103_v2.py'); m = importlib.util.module_from_spec(spec)
sys.argv = ['x']; spec.loader.exec_module(m)
B, P, vd, k5 = m.B, m.P, m.vd, m.k5
k5['version'] = 1
k5['hooks']['HC'] = dict(vo='HC', dur=vd('HC'), subs=False, text=('Pedro levantó la mano', 'y se acabó la reunión 😵'),
                         line='Pedro levantó la mano en la reunión... y se acabó la reunión.')
k5['hooks']['HD'] = dict(vo='HD', dur=vd('HD'), subs=False, text=('Pedro entra al ascensor', 'y todos se bajan 😂'),
                         line='Cuando Pedro entraba al ascensor, todos se bajaban en el siguiente piso.')
shots = m.build_shots(k5)
k = lambda n: f'{m.HF}/{n}_0.mp4'
shots['HC'] = [B.shot(m.TMP, 'hc', k('k_c3_hc'), k5['hooks']['HC']['dur'], ss=0.0, z0=1.0, z1=1.05, stopmo=True) + ([P((380, 740, 560, 910))],)]
shots['HD'] = [B.shot(m.TMP, 'hd', k('k_c3_hd'), k5['hooks']['HD']['dur'], ss=0.0, z0=1.0, z1=1.06, stopmo=True) + ([P((370, 1380, 560, 1520))],)]
for hk in sys.argv[1:] or ['HC', 'HD']:
    B.build(k5, hk, shots)
