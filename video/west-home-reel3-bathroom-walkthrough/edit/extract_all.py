import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps
import pillow_heif; pillow_heif.register_heif_opener()
import timeline as T, core as C
# photos
for out, name in T.PHOTOS.items():
    dst = T.PH + out
    if os.path.exists(dst):
        continue
    im = ImageOps.exif_transpose(Image.open(T.F(name))).convert('RGB')
    w, h = im.size; tw = int(h * 9 / 16)
    if tw <= w:
        im = im.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h))
    else:
        th = int(w * 16 / 9); im = im.crop((0, (h - th) // 2, w, (h - th) // 2 + th))
    im.resize((C.IW, C.IH), Image.LANCZOS).save(dst)
    print('photo', dst)
jobs, plan = [], {}
for i, s in enumerate(T.SHOTS):
    if C.is_still(s['src']):
        plan[i] = None; continue
    f, _ = C.srcmap(s)
    a = max(0.0, min(f(s['t0']), f(s['t1'])) - 0.12)
    b = max(f(s['t0']), f(s['t1'])) + 0.2
    jobs.append((s['src'], a, b)); plan[i] = (s['src'], a, b)
json.dump(plan, open(C.ROOT + 'edit/int_plan.json', 'w'), indent=1)
with ThreadPoolExecutor(4) as ex:
    for p in ex.map(lambda j: C.extract(*j), jobs):
        print(p, flush=True)
print('DONE')
