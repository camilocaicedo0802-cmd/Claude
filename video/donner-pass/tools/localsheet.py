import glob, os, sys
from PIL import Image, ImageDraw, ImageFont
P, pattern, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
files = sorted(glob.glob(f"{P}/assets/img/{pattern}"))
f = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 15)
cols, tw, th = 8, 230, 150
for si in range(0, len(files), 64):
    chunk = files[si:si + 64]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, p in enumerate(chunk):
        try:
            im = Image.open(p); im.draft("RGB", (tw * 2, th * 2)); im = im.convert("RGB")
        except Exception:
            continue
        im.thumbnail((tw - 6, th - 6))
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 4, y + th), os.path.basename(p)[:-4], font=f, fill=(255, 220, 80))
    out = f"{P}/work/sheets/{prefix}_{si // 64}.jpg"
    sheet.save(out, quality=80)
    print(out, len(chunk))
