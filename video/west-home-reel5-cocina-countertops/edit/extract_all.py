import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps
import pillow_heif; pillow_heif.register_heif_opener()
import timeline as T, core as C
# photos are prepared beforehand (photos/*.png at IWxIH)
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
