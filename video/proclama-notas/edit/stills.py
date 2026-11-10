"""stills.py modulo t1 t2 ... -> hoja de revisión out/<modulo>_stills.jpg"""
import importlib
import sys
sys.path.insert(0, '/home/user/notas/edit')
from lib import ROOT, contact, still  # noqa: E402
from PIL import ImageDraw  # noqa: E402
mod = importlib.import_module(sys.argv[1])
ts = [float(x) for x in sys.argv[2:]]
ims = []
for t in ts:
    im = still(mod.shots, mod.overlays, t, scale=0.36)
    ImageDraw.Draw(im).text((8, 8), f'{t:.1f}s', fill=(255, 255, 0))
    ims.append(im)
out = f'{ROOT}/out/{sys.argv[1]}_stills.jpg'
contact(ims, out, cols=min(6, len(ims)))
print(out)
