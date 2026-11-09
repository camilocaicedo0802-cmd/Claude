"""Contact sheets of downloaded Unsplash photos grouped by query: python usq.py PROJECT NAME [q1 q2 ...]"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
P, name, qs = sys.argv[1], sys.argv[2], sys.argv[3:]
reg = json.load(open(f"{P}/work/unsplash.json"))
if qs:
    reg = [r for q in qs for r in reg if r["query"] == q]
f = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 14)
cells = [(r, f"{P}/assets/img/u_{r['id']}.jpg") for r in reg if os.path.exists(f"{P}/assets/img/u_{r['id']}.jpg")]
cols, tw, th = 8, 230, 150
os.makedirs(f"{P}/work/ush", exist_ok=True)
for si in range(0, len(cells), 64):
    chunk = cells[si:si + 64]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 36)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (r, p) in enumerate(chunk):
        tp = f"{P}/work/ush/{r['id']}.jpg"
        if not os.path.exists(tp):
            im = Image.open(p).convert("RGB"); im.thumbnail((tw - 6, th - 6)); im.save(tp, quality=80)
        im = Image.open(tp)
        x, y = (i % cols) * tw, (i // cols) * (th + 36)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 4, y + th), r["id"], font=f, fill=(255, 220, 80))
        d.text((x + 4, y + th + 16), r["query"][:28], font=f, fill=(170, 170, 170))
    out = f"{P}/work/sheets/us_{name}_{si // 64}.jpg"
    sheet.save(out, quality=80)
    print(out, len(chunk))
