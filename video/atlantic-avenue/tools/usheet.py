import json, os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
P = sys.argv[1]
reg = json.load(open(f"{P}/work/unsplash.json"))
reg.sort(key=lambda r: r["query"])
os.makedirs(f"{P}/work/uthumbs", exist_ok=True)
def th(r):
    p = f"{P}/work/uthumbs/{r['id']}.jpg"
    if not os.path.exists(p):
        try:
            im = Image.open(r["file"]); im.draft("RGB", (400, 400)); im = im.convert("RGB"); im.thumbnail((214, 144)); im.save(p, quality=80)
        except Exception:
            return None
    return p
with ThreadPoolExecutor(4) as ex:
    paths = list(ex.map(th, reg))
f = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 12)
cells = [(r, p) for r, p in zip(reg, paths) if p]
cols, tw, th_ = 9, 220, 150
per = 81
for si in range(0, len(cells), per):
    chunk = cells[si:si + per]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th_ + 30)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (r, p) in enumerate(chunk):
        im = Image.open(p)
        x, y = (i % cols) * tw, (i // cols) * (th_ + 30)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 4, y + th_ - 4), r["id"], font=f, fill=(255, 220, 80))
        d.text((x + 4, y + th_ + 10), r["query"][:30], font=f, fill=(180, 180, 180))
    out = f"{P}/work/sheets/u_{si // per}.jpg"
    sheet.save(out, quality=78)
    print(out, len(chunk))
