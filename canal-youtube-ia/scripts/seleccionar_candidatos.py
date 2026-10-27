import csv, sys, os
S = sys.argv[1]
rows = list(csv.DictReader(open(f"{S}/data/videos.csv")))
for r in rows:
    r['views'] = int(r['views']); r['multiple'] = float(r['multiple'] or 0); r['vpd'] = int(r['views_per_day'] or 0)
    r['age'] = int(r['age_days']) if r['age_days'] else 9999
LANG = {'TeloPintoFacil': 'es', 'estrictamente': 'es', 'lichsungoaitruyen': 'vi'}
ALL = {'SquireExplains', 'thecrookedexplainer'}
pick = {}
for h in sorted(set(r['handle'] for r in rows)):
    for tab in ('videos', 'shorts'):
        L = [r for r in rows if r['handle'] == h and r['tab'] == tab]
        if not L: continue
        if h in ALL:
            sel = L
        elif tab == 'shorts':
            sel = sorted(L, key=lambda r: -r['views'])[:6]
        else:
            sel = (sorted(L, key=lambda r: -r['views'])[:12] + sorted(L, key=lambda r: -r['multiple'])[:12]
                   + sorted([r for r in L if r['age'] <= 60], key=lambda r: -r['vpd'])[:6]
                   + sorted(L, key=lambda r: r['pos'] if 'pos' in r else 0)[:0])
        for r in sel: pick[r['id']] = (h, LANG.get(h, 'en'))
done = {os.path.basename(f)[:-5] for f in os.listdir(f"{S}/data/full") if f.endswith('.json') and os.path.getsize(f"{S}/data/full/{f}") > 0}
todo = [(i, h, l) for i, (h, l) in pick.items() if i not in done]
for i, h, l in todo: print(h, l, i)
print(f"selected {len(pick)}, todo {len(todo)}", file=sys.stderr)
