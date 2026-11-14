"""Re-fetch LoC panoramas at full width and save 16:9-ish crops: python3 pancrop.py id:x0frac:x1frac:name ..."""
import io, sys
sys.path.insert(0, "/home/user/rp/tools")
import loc
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS = None
db = __import__("json").load(open("/home/user/rp/work/loc.json"))
cache = {}
for spec in sys.argv[1:]:
    lid, a, b, name = spec.split(":")
    if lid not in cache:
        svc = db[lid]["svc"].replace(":", "/")
        tif = "https://tile.loc.gov/storage-services/" + svc.replace("service/", "master/", 1) + "u.tif"
        im = Image.open(io.BytesIO(loc.get(tif, True)))
        if im.mode.startswith("I;16") or im.mode in ("I", "F"):
            arr = np.asarray(im).astype(np.float32)
            lo, hi = np.percentile(arr, 0.5), np.percentile(arr, 99.5)
            im = Image.fromarray(np.clip((arr - lo) / max(hi - lo, 1) * 255, 0, 255).astype(np.uint8))
        cache[lid] = im.convert("RGB")
    im = cache[lid]
    w, h = im.size
    c = im.crop((int(float(a) * w), 0, int(float(b) * w), h))
    c.thumbnail((2600, 2600))
    c.save(f"/home/user/rp/assets/img/l_{name}.jpg", quality=92)
    print(name, im.size, c.size, flush=True)
