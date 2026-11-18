"""Check the Mixkit license of every item in a DB (page badge), politely; no downloads.
usage: python -I mklic.py DB.json [term ...]"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mk
db = sys.argv[1]
terms = set(sys.argv[2:])
d = mk.load(db)
todo = [k for k, e in d.items() if not e.get("license") and e.get("slug") and (not terms or terms & set(e.get("terms", [])))]
print("to check", len(todo), flush=True)
for i, k in enumerate(todo):
    e = d[k]
    s = mk.get(f"{mk.SITE}/free-stock-video/{e['slug']}/")
    lic = re.findall(r'data-license="(video\w+)"', s or "")
    e["license"] = lic[0] if lic else None
    if i % 20 == 0:
        mk.save(db, d)
    print(k, e["license"], e.get("title", "")[:50], flush=True)
    time.sleep(1.0)
mk.save(db, d)
