import csv, sys, statistics, collections
rows = list(csv.DictReader(open(sys.argv[1])))
for r in rows:
    r['views'] = int(r['views']); r['multiple'] = float(r['multiple']) if r['multiple'] else 0
    r['age'] = int(r['age_days']) if r['age_days'] else None
    r['vpd'] = int(r['views_per_day']) if r['views_per_day'] else 0
    r['dur'] = int(float(r['duration'])) if r['duration'] else 0
def mmss(s): return f"{s//60}:{s%60:02d}"
for h in sorted(set(r['handle'] for r in rows)):
    for tab in ("long","short"):
        L = [r for r in rows if r['handle']==h and r["tab"]==tab]
        if not L: continue
        print(f"\n######## {h} / {tab}  n={len(L)}  total={sum(r['views'] for r in L):,}  median={statistics.median([r['views'] for r in L]):,.0f}  mean={statistics.mean([r['views'] for r in L]):,.0f}")
        dated = [r for r in L if r['date']]
        if dated:
            print(f"  first visible upload ~{min(r['date'] for r in dated)}  latest {max(r['date'] for r in dated)}")
            for days in (30, 90):
                print(f"  uploads last {days}d: {sum(1 for r in dated if r['age'] is not None and r['age']<=days)}")
            bym = collections.OrderedDict()
            for r in sorted(dated, key=lambda r: r['date']):
                m = r['date'][:7]; bym.setdefault(m, []).append(r['views'])
            print("  by publish month (n uploads, median views):", " | ".join(f"{m}:{len(v)}/{statistics.median(v)/1000:.0f}k" for m,v in bym.items()))
            durs=[r['dur'] for r in L if r['dur']]
            if durs: print(f"  duration median {mmss(int(statistics.median(durs)))}  p25 {mmss(sorted(durs)[len(durs)//4])}  p75 {mmss(sorted(durs)[3*len(durs)//4])}")
        print("  TOP ABS:")
        for r in sorted(L, key=lambda r: -r['views'])[:8]:
            print(f"    {r['views']:>10,}  x{r['multiple']:<5} {r['date'] or '?':10} {mmss(r['dur']):>6}  {r['title'][:85]}  [{r['id']}]")
        print("  TOP RELATIVE (vs 10 neighbours):")
        for r in sorted(L, key=lambda r: -r['multiple'])[:8]:
            print(f"    x{r['multiple']:<6} {r['views']:>10,} {r['date'] or '?':10} {mmss(r['dur']):>6}  {r['title'][:85]}  [{r['id']}]")
        rec = [r for r in dated if r['age'] is not None and r['age']<=60]
        if rec:
            print("  TOP RECENT (<=60d, by views/day):")
            for r in sorted(rec, key=lambda r: -r['vpd'])[:5]:
                print(f"    {r['vpd']:>8,}/d {r['views']:>10,} {r['date']} {mmss(r['dur']):>6}  {r['title'][:85]}  [{r['id']}]")
