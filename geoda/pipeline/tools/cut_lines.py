#!/usr/bin/env python3
"""Corta cada frase de una narración y recorta las pausas internas a máx. MAXGAP (brief: cero tiempo muerto > 0,3 s).
uso: cut_lines.py narracion.wav outdir 'KEY:a-b,KEY:a-b,...'  -> KEY_t.wav"""
import sys, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pauses import segments
src, outdir, spec = sys.argv[1], sys.argv[2], sys.argv[3]
MAXGAP, PAD = 0.18, 0.06
segs = segments(src, 0.08, 0.05)
for item in spec.split(','):
    key, rng = item.split(':'); a, b = map(float, rng.split('-'))
    inner = [(max(a, s0), min(b, s1)) for s0, s1 in segs if s1 > a and s0 < b]
    parts, last = [], None
    for k, (s0, s1) in enumerate(inner):
        x0 = s0 - PAD if k == 0 else max(s0 - MAXGAP / 2, last)
        x1 = s1 + (PAD if k == len(inner) - 1 else MAXGAP / 2)
        parts.append((x0, x1)); last = x1
    flt = ''.join(f'[0:a]atrim={x0:.3f}:{x1:.3f},asetpts=PTS-STARTPTS[p{k}];' for k, (x0, x1) in enumerate(parts))
    flt += ''.join(f'[p{k}]' for k in range(len(parts))) + f'concat=n={len(parts)}:v=0:a=1,aresample=48000[o]'
    out = f'{outdir}/{key}_t.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', flt, '-map', '[o]', '-ac', '1', out], check=True)
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
    print(f'{key}: {b - a:.2f}s -> {d:.2f}s ({len(parts)} tramos)')
