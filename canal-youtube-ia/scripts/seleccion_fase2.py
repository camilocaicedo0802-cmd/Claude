"""Selecciona los videos de la fase 2 por canal y calcula los suscriptores al publicar (interpolados).

Uso: python3 seleccion_fase2.py datos/videos.csv datos/suscriptores_series.csv > datos/videos_fase2.csv
"""
import csv, sys, datetime as dt, bisect

rows = [r for r in csv.DictReader(open(sys.argv[1])) if int(r['views']) > 0]
series = {}
for r in csv.DictReader(open(sys.argv[2])):
    series.setdefault(r['handle'], []).append((dt.date.fromisoformat(r['fecha']), int(r['suscriptores'])))
for v in series.values(): v.sort()

def subs_at(h, d):
    s = series.get(h)
    if not s or not d: return ''
    d = dt.date.fromisoformat(d)
    xs = [x for x, _ in s]
    i = bisect.bisect_left(xs, d)
    if i == 0: return s[0][1]
    if i >= len(s): return s[-1][1]
    (x0, y0), (x1, y1) = s[i - 1], s[i]
    return round(y0 + (y1 - y0) * (d - x0).days / max((x1 - x0).days, 1))

for r in rows:
    r['views'] = int(r['views']); r['mult'] = float(r['multiple'] or 0); r['vpd'] = int(r['views_per_day'] or 0)
    r['age'] = int(r['age_days']) if r['age_days'] else None
    r['subs_pub'] = subs_at(r['handle'], r['date']) if r['date_src'] in ('vidiq', 'yt-dlp') else ''
    r['views_per_sub'] = round(r['views'] / max(r['subs_pub'], 1), 1) if r['subs_pub'] != '' else ''

out = []
for h in sorted(set(r['handle'] for r in rows)):
    for tab in ('long', 'short'):
        if (h, tab) == ('TeloPintoFacil', 'short'): continue  # formato abandonado por el canal (mediana 10 k)
        L = [r for r in rows if r['handle'] == h and r['tab'] == tab]
        if len(L) < 4: continue
        n = 5 if tab == 'long' else 3
        cats = {}
        def add(sel, cat):
            for r in sel: cats.setdefault(r['id'], (r, []))[1].append(cat)
        add(sorted(L, key=lambda r: -r['views'])[:n], 'absoluto')
        add(sorted(L, key=lambda r: -r['mult'])[:n], 'relativo')
        add(sorted([r for r in L if r['age'] is not None and r['age'] <= 60], key=lambda r: -r['vpd'])[:3], 'reciente')
        small = [r for r in L if r['views_per_sub'] != '' and r['subs_pub'] != '' and r['subs_pub'] < 20000]
        add(sorted(small, key=lambda r: -r['views_per_sub'])[:3], 'canal_pequeno')
        add(sorted([r for r in L if r['date_src'] in ('vidiq', 'yt-dlp')], key=lambda r: r['mult'])[:2], 'contraste')
        for r, c in cats.values(): out.append((r, c))

cols = ['handle', 'tab', 'categorias', 'id', 'url', 'title', 'title_en', 'date', 'duration', 'views', 'neigh_median', 'multiple',
        'views_per_day', 'subs_pub', 'views_per_sub', 'likes', 'comments', 'thumb']
w = csv.DictWriter(sys.stdout, fieldnames=cols, extrasaction='ignore'); w.writeheader()
for r, c in out:
    r = dict(r); r['categorias'] = '+'.join(c); w.writerow(r)
