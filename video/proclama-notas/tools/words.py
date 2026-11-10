#!/usr/bin/env python3
"""words.py transcript.json t0 t1 -> palabras con tiempos"""
import json, sys
d = json.load(open(sys.argv[1])); a, b = float(sys.argv[2]), float(sys.argv[3])
out = []
for s in d['segments']:
    for w in s['words']:
        if a <= w['s'] <= b:
            out.append(f"{w['w'].strip()}[{w['s']:.2f}]")
print(' '.join(out))
