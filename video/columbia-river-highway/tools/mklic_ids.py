import json, os, re, sys, time
sys.path.insert(0, "/home/user/cr/tools")
import mk
db = "/home/user/cr/work/mixkit.json"
d = mk.load(db)
for k in sys.argv[1:]:
    e = d.get(k)
    if not e:
        print(k, "NOT IN DB"); continue
    if not e.get("license"):
        s = mk.get(f"{mk.SITE}/free-stock-video/{e['slug']}/")
        lic = re.findall(r'data-license="(video\w+)"', s or "")
        e["license"] = lic[0] if lic else None
        time.sleep(1.0)
    print(k, e["license"], e.get("title", "")[:50], flush=True)
mk.save(db, d)
