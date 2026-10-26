import re, sys, traceback
sys.path.insert(0, '.')
import words as W
try:
    import timeline
    sh = timeline.build()
    sh.sort(key=lambda s: s.start)
    print("OK", len(sh))
    prev = None
    for s in sh:
        if prev and s.start - prev.start < 0.6:
            print(f"SHORT {prev.start:.2f}->{s.start:.2f} ({s.start - prev.start:.2f})")
        prev = s
except KeyError as e:
    m = re.search(r"near ([\d.]+)", str(e))
    print(e)
    if m:
        n = float(m.group(1))
        print(' '.join(f'{w[2].strip()}@{w[0]:.1f}' for w in W.WORDS if n - 4 <= w[0] < n + 9))
