"""Endurece el canal alfa de los recortes (elimina halos semitransparentes) y recorta al contenido."""
import sys
from PIL import Image
for path in sys.argv[1:]:
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A").point(lambda v: 0 if v < 100 else 255 if v > 180 else int((v - 100) * 255 / 80))
    im.putalpha(a)
    im = im.crop(a.getbbox())
    im.save(path)
    print(path, im.size)
