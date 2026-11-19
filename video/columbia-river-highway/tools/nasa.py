"""NASA Image and Video Library (images-api.nasa.gov): search + thumbs + original download. NASA imagery is public domain
(not copyrighted in the US); credit "NASA" / crew.
usage: python nasa.py search DB.json THUMBDIR "q1" ...   |   python nasa.py get DB.json OUTDIR id1 ...
"""
import json, os, sys, time, urllib.parse, urllib.request
UA = "Mozilla/5.0 DocResearch/1.0"
def get(u, binary=False):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=90) as r:
                d = r.read()
            return d if binary else d.decode("utf-8", "ignore")
        except Exception as e:
            time.sleep(4 * (i + 1))
    raise RuntimeError(u)
cmd, dbp, out = sys.argv[1], sys.argv[2], sys.argv[3]
db = json.load(open(dbp)) if os.path.exists(dbp) else {}
if cmd == "search":
    for q in sys.argv[4:]:
        d = json.loads(get("https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": q, "media_type": "image"})))
        n = 0
        for it in d["collection"]["items"][:60]:
            m = it["data"][0]; nid = m["nasa_id"]
            if nid in db: continue
            th = next((l["href"] for l in it.get("links", []) if l.get("rel") == "preview"), None)
            db[nid] = {"id": nid, "title": m.get("title", ""), "desc": (m.get("description") or "")[:400], "date": m.get("date_created", "")[:10],
                       "center": m.get("center"), "q": q, "thumb": th, "credit": m.get("photographer") or m.get("secondary_creator") or "NASA"}
            if th:
                p = os.path.join(out, nid + ".jpg")
                if not os.path.exists(p):
                    try: open(p, "wb").write(get(th.replace(" ", "%20"), True))
                    except Exception: pass
            n += 1
        print(q, n, flush=True)
        json.dump(db, open(dbp, "w"), indent=0, ensure_ascii=False)
else:
    for nid in sys.argv[4:]:
        p = os.path.join(out, f"n_{nid}.jpg")
        if os.path.exists(p): continue
        assets = json.loads(get(f"https://images-api.nasa.gov/asset/{urllib.parse.quote(nid)}"))["collection"]["items"]
        hs = [a["href"] for a in assets if a["href"].lower().endswith((".jpg", ".jpeg"))]
        pick = next((h for h in hs if "~orig" in h), None) or next((h for h in hs if "~large" in h), None) or hs[0]
        open(p, "wb").write(get(pick.replace(" ", "%20").replace("http://", "https://"), True))
        print("ok", nid, os.path.getsize(p), flush=True)
