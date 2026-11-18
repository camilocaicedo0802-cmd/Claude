"""Search Wikimedia Commons and download chosen files politely (one at a time, standard thumb width, Retry-After).
usage: python -I wmget.py OUTDIR REGISTRY.json "query|substring|name" ..."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm
out, regp = sys.argv[1], sys.argv[2]
reg = json.load(open(regp)) if os.path.exists(regp) else {}
for spec in sys.argv[3:]:
    q, sub, name = spec.split("|")
    fn = os.path.join(out, f"w_{name}.jpg")
    if os.path.exists(fn):
        continue
    res = [r for r in wm.search(q, 30, 2560) if sub.lower() in r["title"].lower()]
    if not res:
        print("NOT FOUND", spec, flush=True); time.sleep(3); continue
    r = res[0]
    lic = r["license"] or ""
    if "SA" in lic or "NC" in lic or "ND" in lic:
        print("SKIP license", lic, r["title"], flush=True); continue
    src = r["thumb"] if r["w"] > 2560 else r["url"]
    try:
        data = wm.get(src, binary=True)
    except Exception as e:
        print("FAIL", spec, e, flush=True); continue
    open(fn, "wb").write(data)
    if src.lower().endswith((".png", ".tif", ".tiff", ".gif")):
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        im = Image.open(fn).convert("RGB"); im.thumbnail((2600, 2600)); im.save(fn, quality=92)
    reg[f"w_{name}.jpg"] = {"title": r["title"], "license": lic, "artist": r["artist"], "date": r["date"], "url": r["url"],
                           "page": "https://commons.wikimedia.org/wiki/" + r["title"].replace(" ", "_")}
    json.dump(reg, open(regp, "w"), ensure_ascii=False, indent=1)
    print("OK", name, lic, r["title"][:80], flush=True)
    time.sleep(4)
