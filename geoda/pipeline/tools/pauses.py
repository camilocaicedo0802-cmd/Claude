#!/usr/bin/env python3
"""Tramos de voz de un clip (pausas reales por energía). uso: pauses.py clip.mp4 [min_pausa]"""
import sys, numpy as np
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lines import envelope
def segments(src, min_gap=0.12, min_seg=0.12):
    db, hop = envelope(src)
    db = np.convolve(db, np.ones(3) / 3, 'same')
    floor = np.percentile(db, 10); top = np.percentile(db, 97)
    thr = floor + 0.30 * (top - floor)
    on = db > thr
    segs, i, n = [], 0, len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]: j += 1
            segs.append([i * hop, j * hop]); i = j
        else:
            i += 1
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < min_gap:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return [(round(a, 2), round(b, 2)) for a, b in merged if b - a >= min_seg]
if __name__ == '__main__':
    for a, b in segments(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 0.12):
        print(f'{a:6.2f}-{b:6.2f} ({b-a:.2f})')
