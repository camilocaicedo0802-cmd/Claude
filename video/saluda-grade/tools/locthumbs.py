import json, os, sys, time
sys.path.insert(0, "/home/user/sg/tools")
import loc
qs = set(sys.argv[1:])
d = json.load(open("/home/user/sg/work/loc.json"))
for r in d.values():
    if qs and r["q"] not in qs:
        continue
    p = f"/home/user/sg/work/locthumbs/{r['id']}.jpg"
    if os.path.exists(p) or not r.get("thumb"):
        continue
    try:
        b = loc.get(r["thumb"], binary=True)
        if b:
            open(p, "wb").write(b)
    except Exception as e:
        print("ERR", r["id"], e, flush=True)
    time.sleep(0.8)
print("done", flush=True)
