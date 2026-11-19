"""Wikimedia contact sheet: python3 -I wmsheet.py NAME q1 q2 ... -> work/sheets/wm_NAME_k.jpg, listing in work/wm_list.json"""
import json, os, sys, time
sys.path.insert(0, "/home/user/cr/tools")
import wm
from PIL import Image, ImageDraw, ImageFont
P = "/home/user/cr"
name, qs = sys.argv[1], sys.argv[2:]
lp = f"{P}/work/wm_list.json"
lst = json.load(open(lp)) if os.path.exists(lp) else {}
cells = []
for q in qs:
    try:
        res = wm.search(q, 30, 300)
    except Exception as e:
        print("ERR", q, e); continue
    for r in res:
        lic = r["license"] or ""
        if any(x in lic for x in ("SA", "NC", "ND", "GFDL")) or not lic:
            continue
        k = str(len(lst)) if r["title"] not in [v["title"] for v in lst.values()] else [k for k, v in lst.items() if v["title"] == r["title"]][0]
        lst[k] = r
        p = f"{P}/work/wmthumbs/{k}.jpg"
        if not os.path.exists(p):
            try:
                open(p, "wb").write(wm.get(r["thumb"], binary=True)); time.sleep(0.6)
            except Exception as e:
                print("thumb fail", k, e); continue
        if k not in [c[0] for c in cells]:
            cells.append((k, r))
    json.dump(lst, open(lp, "w"), ensure_ascii=False, indent=0)
    time.sleep(1.5)
f = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 13)
cols, tw, th = 8, 230, 170
for si in range(0, len(cells), 48):
    chunk = cells[si:si + 48]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 40)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (k, r) in enumerate(chunk):
        try:
            im = Image.open(f"{P}/work/wmthumbs/{k}.jpg").convert("RGB")
        except Exception:
            continue
        im.thumbnail((tw - 6, th - 6))
        x, y = (i % cols) * tw, (i // cols) * (th + 40)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 4, y + th), f"w{k} {r['license'][:10]} {r['w']}", font=f, fill=(255, 220, 80))
        d.text((x + 4, y + th + 17), r["title"][5:36], font=f, fill=(170, 170, 170))
    out = f"{P}/work/sheets/wm_{name}_{si // 48}.jpg"
    sheet.save(out, quality=82); print(out, len(chunk))
