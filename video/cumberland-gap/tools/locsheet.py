import json, os, sys, time, urllib.request
from PIL import Image, ImageDraw, ImageFont
P = sys.argv[1]
db = json.load(open(f"{P}/work/loc.json"))
UA = "Mozilla/5.0 CGDoc/1.0 (camilocaicedo0802@gmail.com)"
items = list(db.values())
f = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 14)
cells = []
for r in items:
    p = f"{P}/work/locthumbs/{r['id']}.jpg"
    if not os.path.exists(p) and os.environ.get("FETCH"):
        try:
            open(p, "wb").write(urllib.request.urlopen(urllib.request.Request(r["thumb"], headers={"User-Agent": UA}), timeout=40).read())
            time.sleep(0.4)
        except Exception as e:
            continue
    if os.path.exists(p):
        cells.append((r, p))
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
        d.text((x + 4, y + th), r["id"], font=f, fill=(255, 220, 80))
        d.text((x + 4, y + th + 16), r["title"][:30], font=f, fill=(190, 190, 190))
        d.text((x + 4, y + th + 32), r["title"][30:60], font=f, fill=(190, 190, 190))
    out = f"{P}/work/sheets/loc_{si // 56}.jpg"
    sheet.save(out, quality=82)
    print(out, len(chunk))
