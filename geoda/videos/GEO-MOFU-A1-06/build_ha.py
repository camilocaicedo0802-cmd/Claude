#!/usr/bin/env python3
"""A1-06 hook A sin repetir 'le diste una segunda oportunidad' (v4): el hook ya la dice, así que en la variante HA el plano de
la ducha va sin voz (1,8 s con sonido de ducha) y se alargan lavamanos y cierre para no bajar de 30 s (MOFU)."""
import sys, copy, importlib.util, os
AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('b106', f'{AQUI}/build_a106.py'); m = importlib.util.module_from_spec(spec)
sys.argv = ['x']; spec.loader.exec_module(m)
def ha_cfg(cfg, extra_cierre):
    c = copy.deepcopy(cfg); c['version'] = 4
    for r in c['body']:
        if r['key'] == 'B1':
            r.update(vo='SIL', dur=1.8, line='', subs=False)
        if r['key'] == 'B8':
            r['dur'] = 3.2
        if r['key'] == 'B9':
            r['dur'] += extra_cierre
    return c
for cfg, extra in ((m.base, 0.6), (m.k2, 0.0)):
    c = ha_cfg(cfg, extra)
    m.B.build(c, 'HA', m.build_shots(c))
