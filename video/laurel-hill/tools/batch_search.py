import sys, json, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm
qs = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
out_path = sys.argv[2]
res = json.load(open(out_path)) if os.path.exists(out_path) else {}
for q in qs:
    if q in res: continue
    try:
        res[q] = wm.search(q, limit=int(sys.argv[3]) if len(sys.argv) > 3 else 15, width=480)
    except Exception as e:
        print("ERR", q, e); continue
    json.dump(res, open(out_path, "w"), indent=0)
    print("##", q, flush=True)
    for i, r in enumerate(res[q]):
        print(f"  {i:2d} {r['w']}x{r['h']} [{r['license'][:14]}] {r['title'][5:95]} | {r['date'][:22]} | {r['desc'][:70]}".replace("\n", " "))
    time.sleep(1.5)
