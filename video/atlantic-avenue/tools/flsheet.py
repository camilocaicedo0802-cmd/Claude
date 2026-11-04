import json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
P = sys.argv[1]
db = json.load(open(f"{P}/work/flickr.json"))
queries = sys.argv[2:]
UA = "Mozilla/5.0 DPDoc/1.0"
def thumb(r):
    p = f"{P}/work/flthumbs/{r['id']}.jpg"
    if os.path.exists(p): return p
    u = r["thumb"]
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA})
        open(p, "wb").write(urllib.request.urlopen(req, timeout=40).read())
    except Exception:
        return None
    return p
items = [r for q in queries for r in db.values() if r["q"] == q]
with ThreadPoolExecutor(8) as ex:
    paths = list(ex.map(thumb, items))
f = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 15)
LIC = {"CC BY 2.0": "BY", "Public Domain Mark": "PD", "No known copyright restrictions": "NKC", "CC BY 4.0": "BY4",
       "CC0 1.0": "CC0", "United States Government Work": "USG"}
cols, tw, th = 8, 230, 170
cells = [(r, p) for r, p in zip(items, paths) if p]
for si in range(0, len(cells), 48):
    chunk = cells[si:si + 48]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 40)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (r, p) in enumerate(chunk):
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        im.thumbnail((tw - 6, th - 6))
        x, y = (i % cols) * tw, (i // cols) * (th + 40)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 4, y + th), f"{r['id']} {LIC[r['license']]} {r['w']}", font=f, fill=(255, 220, 80))
        d.text((x + 4, y + th + 18), r["q"][:24], font=f, fill=(170, 170, 170))
    out = f"{P}/work/sheets/fl_{queries[0][:16].replace(chr(32), chr(95))}_{si // 48}.jpg"
    sheet.save(out, quality=82)
    print(out, len(chunk))
