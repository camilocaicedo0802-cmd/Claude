"""Render mid frames of selected shots: python sel.py OUT.jpg kind|t1,t2,..."""
import sys
sys.path.insert(0, '.')
from PIL import Image, ImageDraw, ImageFont
import render
shots = render.build(1130.37)
arg = sys.argv[2]
if arg == "maps":
    pick = [i for i, s in enumerate(shots) if type(s.base).__name__ == "MapScene"]
elif arg == "custom":
    pick = [i for i, s in enumerate(shots) if type(s.base).__name__ in ("Custom", "Split", "Framed")]
else:
    ts = [float(x) for x in arg.split(",")]
    pick = sorted({max(i for i, s in enumerate(shots) if s.start <= t) for t in ts})
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
tiles = []
for i in pick:
    s = shots[i]
    T = s.start + (s.end - s.start) * float(sys.argv[3] if len(sys.argv) > 3 else 0.7)
    fr = render.frame_at(shots, T, int(T * 30), set())
    im = Image.fromarray(fr).resize((480, 270))
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 120, 22], fill=(0, 0, 0)); d.text((3, 2), f"{i} {s.start:.1f}", fill=(255, 220, 0), font=font)
    tiles.append(im)
cols = 4
rows = (len(tiles) + cols - 1) // cols
sh = Image.new('RGB', (480 * cols, 270 * rows))
for j, t in enumerate(tiles):
    sh.paste(t, ((j % cols) * 480, (j // cols) * 270))
sh.save(sys.argv[1], quality=80)
print(len(tiles))
