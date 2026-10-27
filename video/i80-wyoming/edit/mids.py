import sys, time, traceback
sys.path.insert(0, '.')
from PIL import Image, ImageDraw, ImageFont
import render
shots = render.build(1126.37)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
tiles = []
errs = 0
for i, s in enumerate(shots):
    T = s.start + (s.end - s.start) * 0.62
    try:
        fr = render.frame_at(shots, T, int(T * 30), set())
        im = Image.fromarray(fr).resize((320, 180))
    except Exception as e:
        errs += 1
        print('ERR shot', i, round(s.start, 2), type(s.base).__name__, repr(e)[:200])
        traceback.print_exc(limit=3)
        im = Image.new('RGB', (320, 180), (120, 0, 0))
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 92, 18], fill=(0, 0, 0)); d.text((3, 2), f"{i} {s.start:.1f}", fill=(255, 220, 0), font=font)
    tiles.append(im)
    s.base.close()
for k in range(0, len(tiles), 48):
    sh = Image.new('RGB', (320 * 8, 180 * 6))
    for j, t in enumerate(tiles[k:k + 48]):
        sh.paste(t, ((j % 8) * 320, (j // 8) * 180))
    sh.save(f"{sys.argv[1]}/mid_{k // 48}.jpg", quality=78)
print('errors', errs, 'shots', len(shots))
