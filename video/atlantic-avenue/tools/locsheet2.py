import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
P, name = sys.argv[1], sys.argv[2]
qs = sys.argv[3:]
db = json.load(open(f"{P}/work/loc.json"))
UA = "Mozilla/5.0 DPDoc/1.0"
items = [r for q in qs for r in db.values() if r["q"] == q]
os.makedirs(f"{P}/work/locthumbs", exist_ok=True)
def th(r):
    p = f"{P}/work/locthumbs/{r['id']}.jpg"
    if not os.path.exists(p):
        for k in range(3):
            try:
                open(p, "wb").write(urllib.request.urlopen(urllib.request.Request(r["thumb"], headers={"User-Agent": UA}), timeout=40).read()); break
            except Exception:
                time.sleep(2)
    return p if os.path.exists(p) else None
with ThreadPoolExecutor(6) as ex:
    paths = list(ex.map(th, items))
f = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 13)
cells = [(r, p) for r, p in zip(items, paths) if p]
cols, tw, th_ = 8, 220, 150
for si in range(0, len(cells), 64):
    chunk = cells[si:si + 64]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th_ + 34)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (r, p) in enumerate(chunk):
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        im.thumbnail((tw - 6, th_ - 6))
        x, y = (i % cols) * tw, (i // cols) * (th_ + 34)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 4, y + th_), f"{r['id']} {str(r.get('date'))[:4]}", font=f, fill=(255, 220, 80))
        d.text((x + 4, y + th_ + 15), r["title"][:32], font=f, fill=(190, 190, 190))
    out = f"{P}/work/sheets/{name}_{si // 64}.jpg"
    sheet.save(out, quality=80)
    print(out, len(chunk))
