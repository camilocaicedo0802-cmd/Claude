#!/usr/bin/env python3
"""A1-06 hook A (v5): 'le diste una segunda oportunidad' solo en el hook y SIN el plano de la ducha (Camilo: quitar la toma que
no dice nada). Para no bajar de 30 s (MOFU) se alargan 0,2-0,3 s los planos con acción y el cierre."""
import sys, copy, importlib.util, os
AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('b106', f'{AQUI}/build_a106.py'); m = importlib.util.module_from_spec(spec)
sys.argv = ['x']; spec.loader.exec_module(m)
EXTRA = {'B4': 0.2, 'B5': 0.3, 'B6': 0.3, 'B7': 0.2, 'B8': 0.5}
def ha_cfg(cfg, extra_cierre):
    c = copy.deepcopy(cfg); c['version'] = 9
    for r in c['body']:
        r['dur'] += EXTRA.get(r['key'], 0.0)
        if r['key'] == 'B9':
            r['dur'] += extra_cierre
    shots = m.build_shots(c)                                         # planos con las duraciones nuevas
    c['body'] = [r for r in c['body'] if r['key'] != 'B1']          # fuera la ducha
    return c, shots
for cfg, extra in ((m.base, 1.2), (m.k2, 0.0)):
    c, shots = ha_cfg(cfg, extra)
    m.B.build(c, 'HA', shots)
