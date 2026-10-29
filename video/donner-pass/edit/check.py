import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline
from engine import IMG, VID
shots = timeline.build()
starts = [s.start for s in shots]
print("shots", len(shots))
srt = sorted(shots, key=lambda s: s.start)
bad = 0
for a, b in zip(srt, srt[1:]):
    d = b.start - a.start
    if d < 0.6:
        print(f"SHORT {a.start:8.2f} -> {b.start:8.2f} ({d:.2f}s)")
        bad += 1
print("last start", srt[-1].start)
src = open("timeline.py").read()
for f in sorted(set(re.findall(r'"([ufl]_[^"]+\.jpg)"', src))):
    if not os.path.exists(os.path.join(IMG, f)):
        print("MISSING IMG", f)
for f in sorted(set(re.findall(r'vid\("([^"]+)"', src))):
    if not os.path.exists(os.path.join(VID, f"ia_{f}.mp4")):
        print("MISSING VID", f)
