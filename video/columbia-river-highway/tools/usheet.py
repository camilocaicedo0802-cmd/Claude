import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
P = "/home/user/cr"
rows = [l.rstrip("\n").split("\t") for l in open(f"{P}/work/unsplash_cands.tsv") if l.strip()]
def th(r):
    p = f"{P}/work/uthumbs/{r[0]}.jpg"
    if not os.path.exists(p):
        u = r[1] + ("&" if "?" in r[1] else "?") + "w=320&fm=jpg&q=70"
        subprocess.run(["curl", "-sS", "-L", "--fail", "-m", "40", "-o", p, u])
    return p if os.path.exists(p) else None
with ThreadPoolExecutor(8) as ex:
    paths = list(ex.map(th, rows))
f = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 13)
cells = [(r, p) for r, p in zip(rows, paths) if p]
cols, tw, th_ = 8, 230, 160
for si in range(0, len(cells), 56):
    chunk = cells[si:si + 56]
    nr = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, nr * (th_ + 40)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (r, p) in enumerate(chunk):
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        im.thumbnail((tw - 6, th_ - 6))
        x, y = (i % cols) * tw, (i // cols) * (th_ + 40)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 4, y + th_), r[0], font=f, fill=(255, 220, 80))
        d.text((x + 4, y + th_ + 17), r[2][:28], font=f, fill=(170, 170, 170))
    out = f"{P}/work/sheets/us_{si // 56}.jpg"
    sheet.save(out, quality=82); print(out, len(chunk))
