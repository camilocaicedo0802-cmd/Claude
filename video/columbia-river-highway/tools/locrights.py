import json, subprocess, sys, time
db = json.load(open("/home/user/cr/work/loc.json"))
for lid in sys.argv[1:]:
    r = db.get(lid)
    if not r:
        print(lid, "NOT IN DB"); continue
    for k in range(3):
        p = subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0 (X11; Linux x86_64) DPDoc/1.0", r["url"] + "?fo=json"], capture_output=True, text=True)
        try:
            d = json.loads(p.stdout); break
        except Exception:
            d = None; time.sleep(8)
    if d is None:
        print(lid, "ERR", p.stdout[:80].replace("\n", " "), flush=True); continue
    it = d.get("item", {})
    ra = it.get("rights_advisory") or it.get("rights") or d.get("rights")
    print(lid, "|", str(ra)[:140], "|", r["title"][:60], flush=True)
    time.sleep(3)
