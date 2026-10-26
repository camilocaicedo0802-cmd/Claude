"""Download 480px thumbs for chosen search results and tile into labeled contact sheets.
usage: preview.py picks.txt outprefix   (picks lines: <json file>|<query>|<idx,idx,...>)"""
import sys, os, json, time, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm
from PIL import Image, ImageDraw, ImageFont
picks, prefix = sys.argv[1], sys.argv[2]
cache = {}
items = []
for line in open(picks):
    line = line.strip()
    if not line or line.startswith('#'): continue
    f, q, idxs = line.split('|')
    if f not in cache: cache[f] = json.load(open(f))
    rs = cache[f][q]
    for i in [int(x) for x in idxs.split(',')]:
        if i < len(rs): items.append(rs[i])
os.makedirs('thumbs', exist_ok=True)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
tiles = []
reg = json.load(open('registry.json')) if os.path.exists('registry.json') else {}
for r in items:
    key = r['title']
    if key not in reg:
        reg[key] = {"id": f"c{len(reg):03d}", **{k: r.get(k) for k in ('title','license','artist','w','h','url','thumb')}}
    cid = reg[key]['id']
    p = f"thumbs/{cid}.jpg"
    if not os.path.exists(p):
        try:
            data = wm.get(r['thumb'], binary=True)
            Image.open(io.BytesIO(data)).convert('RGB').save(p, quality=85)
        except Exception as e:
            print('fail', key, e); continue
        time.sleep(0.4)
    im = Image.open(p); im.thumbnail((360, 240))
    tile = Image.new('RGB', (360, 270), (20, 20, 20)); tile.paste(im, ((360 - im.width) // 2, (240 - im.height) // 2))
    d = ImageDraw.Draw(tile); d.text((4, 244), f"{cid} {r['license'][:12]} {key[5:30]}", fill=(255, 220, 0), font=font)
    tiles.append(tile)
json.dump(reg, open('registry.json', 'w'), indent=0)
for s in range(0, len(tiles), 24):
    sheet = Image.new('RGB', (360 * 6, 270 * 4), (0, 0, 0))
    for k, t in enumerate(tiles[s:s + 24]):
        sheet.paste(t, ((k % 6) * 360, (k // 6) * 270))
    sheet.save(f"{prefix}_{s // 24}.jpg", quality=80)
    print(f"{prefix}_{s // 24}.jpg")
