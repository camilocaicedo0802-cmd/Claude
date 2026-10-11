import sys
from PIL import Image, ImageDraw
out, frames = sys.argv[1], sys.argv[2:]
w, h = 360, 640
cols = min(6, len(frames))
rows = (len(frames) + cols - 1) // cols
s = Image.new('RGB', (w * cols, (h + 24) * rows), 'white')
d = ImageDraw.Draw(s)
for i, fr in enumerate(frames):
    im = Image.open(f'out/prev/f_{fr}.png').convert('RGB').resize((w, h))
    x, y = (i % cols) * w, (i // cols) * (h + 24)
    s.paste(im, (x, y))
    d.text((x + 6, y + h + 4), f'frame {fr}  ({int(fr)/30:.2f}s)', fill='black')
s.save(out, quality=85)
