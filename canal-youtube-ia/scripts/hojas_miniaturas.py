import csv, sys, os, io, urllib.request, time
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]
rows = list(csv.DictReader(open(f"{S}/data/videos.csv")))
for r in rows:
    r['views'] = int(r['views']); r['multiple'] = float(r['multiple'] or 0); r['vpd'] = int(r['views_per_day'] or 0)
os.makedirs(f"{S}/data/thumbs", exist_ok=True); os.makedirs(f"{S}/data/sheets", exist_ok=True)
def get(vid):
    p = f"{S}/data/thumbs/{vid}.jpg"
    if not os.path.exists(p):
        for name in ('maxresdefault', 'hqdefault'):
            try:
                data = urllib.request.urlopen(f"https://i.ytimg.com/vi/{vid}/{name}.jpg", timeout=20).read()
                if len(data) > 2000: open(p, 'wb').write(data); break
            except Exception: pass
        time.sleep(0.3)
    return Image.open(p).convert('RGB') if os.path.exists(p) else None
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
except Exception: font = ImageFont.load_default()
for h in sorted(set(r['handle'] for r in rows)):
    for tab in ('long', 'short'):
        L = [r for r in rows if r['handle'] == h and r['tab'] == tab]
        if len(L) < 3: continue
        pick = []
        for r in sorted(L, key=lambda r: -r['views'])[:6] + sorted(L, key=lambda r: -r['multiple'])[:6] + sorted(L, key=lambda r: -r['vpd'])[:4]:
            if r not in pick: pick.append(r)
        # add 4 low performers (bottom by multiple, dated) for contrast
        low = [r for r in sorted(L, key=lambda r: r['multiple']) if r not in pick and r['views'] > 0][:4]
        pick = pick[:12] + low
        W, H = (480, 270) if tab == 'long' else (270, 480)
        cols = 4 if tab == 'long' else 8
        rows_n = (len(pick) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * W, rows_n * (H + 40)), 'white')
        d = ImageDraw.Draw(sheet)
        for k, r in enumerate(pick):
            im = get(r['id'])
            x, y = (k % cols) * W, (k // cols) * (H + 40)
            if im:
                im = im.resize((W, H)) if tab == 'long' else im.resize((W, int(im.height * W / im.width))).crop((0, 0, W, H))
                sheet.paste(im, (x, y))
            tag = 'LOW ' if r in low else ''
            d.text((x + 4, y + H + 2), f"{tag}#{k+1} {r['views']:,} x{r['multiple']}", fill='red' if tag else 'black', font=font)
            d.text((x + 4, y + H + 20), r['title'][:52], fill='black', font=font)
        out = f"{S}/data/sheets/{h}_{tab}.jpg"
        sheet.save(out, quality=82); print(out, len(pick))
