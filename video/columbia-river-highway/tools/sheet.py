"""Contact sheets: python sheet.py OUT_PREFIX COLS item... where item = path|label ; writes OUT_PREFIX_N.jpg (30 per sheet)."""
import sys
from PIL import Image, ImageDraw, ImageFont
out, cols = sys.argv[1], int(sys.argv[2])
items = [a.split("|", 1) for a in sys.argv[3:]]
W, H = 360, 230
f = ImageFont.truetype("/home/user/pm/assets/fonts/JetBrainsMono.ttf", 15)
per = cols * 6
for s in range(0, len(items), per):
    chunk = items[s:s + per]
    rows = (len(chunk) + cols - 1) // cols
    sh = Image.new("RGB", (cols * W, rows * H), (20, 20, 20))
    d = ImageDraw.Draw(sh)
    for i, (p, lab) in enumerate(chunk):
        try:
            im = Image.open(p).convert("RGB"); im.thumbnail((W - 6, H - 26))
            sh.paste(im, ((i % cols) * W + 3, (i // cols) * H + 3))
        except Exception:
            pass
        d.text(((i % cols) * W + 4, (i // cols) * H + H - 22), lab[:44], fill=(255, 230, 80), font=f)
    sh.save(f"{out}_{s // per + 1}.jpg", quality=80)
    print(f"{out}_{s // per + 1}.jpg")
