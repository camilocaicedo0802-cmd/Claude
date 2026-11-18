"""Contact sheet of LoC search results for the given queries: python locq.py PROJECT NAME q1 q2 ..."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
P, name, qs = sys.argv[1], sys.argv[2], sys.argv[3:]
db = json.load(open(f"{P}/work/loc.json"))
f = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 14)
cells = [(r, f"{P}/work/locthumbs/{r['id']}.jpg") for q in qs for r in db.values() if r["q"] == q]
cells = [c for c in cells if os.path.exists(c[1])]
cols, tw, th = 8, 230, 160
for si in range(0, len(cells), 56):
    chunk = cells[si:si + 56]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 52)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (r, p) in enumerate(chunk):
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        im.thumbnail((tw - 6, th - 6))
        x, y = (i % cols) * tw, (i // cols) * (th + 52)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 4, y + th), f"{r['id']} {str(r.get('date') or '')[:4]}", font=f, fill=(255, 220, 80))
        d.text((x + 4, y + th + 16), r["title"][:30], font=f, fill=(190, 190, 190))
        d.text((x + 4, y + th + 32), r["title"][30:60], font=f, fill=(190, 190, 190))
    out = f"{P}/work/sheets/lq_{name}_{si // 56}.jpg"
    sheet.save(out, quality=80)
    print(out, len(chunk))
