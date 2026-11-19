import os, sys, json
from PIL import Image, ImageDraw, ImageFont
P = "/home/user/cr"
fl = json.load(open(f"{P}/work/flickr.json"))
files = sorted(f for f in os.listdir(f"{P}/assets/img") if f.endswith(".jpg"))
order = lambda f: ({"f": 0, "l": 1, "w": 2, "u": 3}.get(f[0], 4), f)
files.sort(key=order)
font = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 13)
cols, tw, th = 10, 184, 120
per = 70
for si in range(0, len(files), per):
    chunk = files[si:si + per]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 34)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(chunk):
        try:
            im = Image.open(f"{P}/assets/img/{f}"); im.draft("RGB", (300, 300)); im = im.convert("RGB")
        except Exception:
            continue
        im.thumbnail((tw - 4, th - 4))
        x, y = (i % cols) * tw, (i // cols) * (th + 34)
        sheet.paste(im, (x + 2, y + 2))
        lab = f[:-4]
        sub = ""
        if f.startswith("f_"):
            r = fl.get(f[2:-4], {}); sub = (r.get("q") or "")[:22]
        d.text((x + 3, y + th), lab[:24], font=font, fill=(255, 220, 80))
        d.text((x + 3, y + th + 15), sub, font=font, fill=(160, 160, 160))
    sheet.save(f"{P}/work/sheets/all_{si // per}.jpg", quality=80)
    print(si // per, len(chunk))
