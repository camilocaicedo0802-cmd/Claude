"""Download chosen Wikimedia files from a saved search listing (work/wm_list.json), politely, at <= 2560 px.
usage: python -I wmpick.py OUTDIR REGISTRY.json LIST.json "substring|name" ..."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm
out, regp, listp = sys.argv[1], sys.argv[2], sys.argv[3]
reg = json.load(open(regp)) if os.path.exists(regp) else {}
listing = json.load(open(listp))
allres = {}
for res in listing.values():
    for r in res:
        allres.setdefault(r["title"], r)
for spec in sys.argv[4:]:
    sub, name = spec.split("|")
    fn = os.path.join(out, f"w_{name}.jpg")
    if os.path.exists(fn):
        continue
    hits = [r for t, r in allres.items() if sub.lower() in t.lower()]
    if not hits:
        print("NOT FOUND", spec, flush=True); continue
    r = hits[0]
    lic = r["license"] or ""
    if "SA" in lic or "NC" in lic or "ND" in lic or "GFDL" in lic:
        print("SKIP license", lic, r["title"], flush=True); continue
    info = wm.info([r["title"]], 2560)
    meta = info[0] if isinstance(info, list) and info else (list(info.values())[0] if isinstance(info, dict) and info else {})
    src = meta.get("thumb") or r.get("url")
    if r.get("w", 0) and r["w"] <= 2560 and not r["url"].lower().endswith((".tif", ".tiff")):
        src = r["url"]
    try:
        data = wm.get(src, binary=True)
    except Exception as e:
        print("FAIL", spec, e, flush=True); continue
    open(fn, "wb").write(data)
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(fn).convert("RGB"); im.thumbnail((2600, 2600)); im.save(fn, quality=92)
    reg[f"w_{name}.jpg"] = {"title": r["title"], "license": lic, "artist": r["artist"], "date": r.get("date"), "url": r["url"],
                           "page": "https://commons.wikimedia.org/wiki/" + r["title"].replace(" ", "_")}
    json.dump(reg, open(regp, "w"), ensure_ascii=False, indent=1)
    print("OK", name, lic, r["title"][:80], flush=True)
    time.sleep(5)
