"""Edit decision list: drop the '3, 2, 1' count-in and tighten every pause (jump cuts)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = []
for s in json.load(open(f'{ROOT}/raw/words.json')):
    for w in s['words']:
        W.append([w['w'].strip(), w['s'], w['e']])
W = W[3:]                                   # drop "3, 2, 1."
SIL = [(5.854, 6.188), (7.398, 7.677), (8.727, 9.057), (9.275, 9.471), (11.162, 11.591), (13.225, 13.509),
       (14.306, 14.661), (16.985, 17.389), (21.556, 21.851), (25.378, 25.755), (26.118, 26.406), (27.619, 27.846)]
KEEP = 0.07                                 # silence kept on each side of a jump cut
out = []
start = 1.94
for a_, b_ in SIL:
    out.append([start, a_ + KEEP]); start = b_ - KEEP
out.append([start, 34.45])
SEGS = out
OUT0 = []
t = 0.0
for a, b in SEGS:
    OUT0.append(t); t += b - a
DUR_EDIT = t

def raw_of(t):
    """output time -> raw time"""
    for (a, b), o in zip(SEGS, OUT0):
        if t < o + (b - a): return a + (t - o)
    return SEGS[-1][1]

def out_of(r):
    """raw time -> output time (clamped into kept segments)"""
    for (a, b), o in zip(SEGS, OUT0):
        if r <= b: return o + max(0.0, r - a)
    return DUR_EDIT

CUTS = OUT0[1:]                             # output times of jump cuts
WORDS = [(w[0], out_of(w[1]), out_of(w[2])) for w in W]

if __name__ == '__main__':
    print('segments', len(SEGS), 'duration', round(DUR_EDIT, 2))
    for (a, b), o in zip(SEGS, OUT0): print(f'  out {o:6.2f}  raw {a:6.2f}-{b:6.2f}')
    for i, (w, s, e) in enumerate(WORDS): print(f'{i}:{w}[{s:.2f}]', end=' ')
    print()
