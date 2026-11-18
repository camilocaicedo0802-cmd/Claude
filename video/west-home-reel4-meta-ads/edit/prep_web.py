"""v3: crop the dated stock bathrooms (Unsplash, free licence) to 9:16 plates for the before section.

usage: python3 prep_web.py   — reads WEB below, writes photos/<plate>.png at 1620x2880 (room for push-ins)."""
import os, sys
from PIL import Image, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T

SRC = T.ROOT + 'stock_v3/'
# plate -> (stock file, horizontal centre of the 9:16 crop as a fraction of the width)
WEB = T.WEB_V3

for plate, (name, fx) in WEB.items():
    im = ImageOps.exif_transpose(Image.open(SRC + name)).convert('RGB')
    w, h = im.size
    tw = int(round(h * 9 / 16))
    if tw <= w:
        x0 = int(round(min(max(fx * w - tw / 2, 0), w - tw)))
        im = im.crop((x0, 0, x0 + tw, h))
    else:
        th = int(round(w * 16 / 9)); y0 = (h - th) // 2
        im = im.crop((0, y0, w, y0 + th))
    im.resize((1620, 2880), Image.LANCZOS).save(T.PH + plate)
    print(plate, name, (w, h), '->', im.size)
