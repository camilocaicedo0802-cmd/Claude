import json, glob, os, statistics, datetime as dt, csv, sys, re
S = sys.argv[1]
TODAY = dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else dt.date.today()
def iso_dur(s):
    m = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', s or '')
    if not m: return None
    d, h, mi, se = (int(x or 0) for x in m.groups()); return d*86400 + h*3600 + mi*60 + se
exact = {}
for f in glob.glob(f"{S}/data/full/*.json"):
    try: d = json.loads(open(f).read().strip().splitlines()[0])
    except Exception: continue
    exact[d['id']] = dict(date=dt.datetime.strptime(d['upload_date'], '%Y%m%d').date() if d.get('upload_date') else None,
                          views=d.get('view_count'), likes=d.get('like_count'), comments=d.get('comment_count'),
                          duration=d.get('duration'), chapters=len(d.get('chapters') or []), desc=d.get('description') or '',
                          tags=d.get('tags') or [], src='yt-dlp')
for f in glob.glob(f"{S}/data/vidiq/mcp-vidIQ-vidiq_get_videos_by_ids-*.txt"):
    for v in json.load(open(f))['videos']:
        exact[v['id']] = dict(date=dt.date.fromisoformat(v['publishedAt'][:10]), views=v.get('viewCount'), likes=v.get('likeCount'),
                              comments=v.get('commentCount'), duration=iso_dur(v.get('duration')), chapters=None,
                              desc=v.get('description') or '', tags=v.get('tags') if isinstance(v.get('tags'), list) else [],
                              vph=v.get('vph'), src='vidiq')
orig = {}
for f in glob.glob(f"{S}/data/flatorig/*.json"):
    for e in json.load(open(f))['entries']: orig[e['id']] = e['title']
rows = []
for f in sorted(glob.glob(f"{S}/data/flatdate/*.json")):
    d = json.load(open(f))
    if not d: continue
    h, tab = os.path.basename(f)[:-5].rsplit('_', 1)
    for i, e in enumerate(d['entries']):
        x = exact.get(e['id'], {})
        date = x.get('date') or (dt.datetime.fromtimestamp(e['timestamp'], dt.UTC).date() if e.get('timestamp') else None)
        dur = x.get('duration') or e.get('duration')
        rows.append(dict(handle=h, tab='short' if tab == 'shorts' else 'long', pos=i, id=e['id'],
                         title=orig.get(e['id'], e['title']), title_en=e['title'] if e['id'] in orig else '',
                         date=date, date_src=x.get('src') or ('approx' if date else ''),
                         duration=dur, views=x.get('views') or e.get('view_count') or 0, views_src=x.get('src') or 'rounded',
                         likes=x.get('likes'), comments=x.get('comments'), chapters=x.get('chapters'),
                         url=f"https://www.youtube.com/watch?v={e['id']}", thumb=f"https://i.ytimg.com/vi/{e['id']}/hqdefault.jpg",
                         desc_first_line=(x.get('desc') or '').strip().split('\n')[0][:200]))
by = {}
for r in rows: by.setdefault((r['handle'], r['tab']), []).append(r)
for key, lst in by.items():
    lst.sort(key=lambda r: r['pos'])
    allmed = statistics.median([x['views'] for x in lst])
    for i, r in enumerate(lst):
        nb = [x['views'] for j, x in enumerate(lst) if j != i and abs(j - i) <= 5]
        med = statistics.median(nb) if nb else 0
        r['neigh_median'] = int(med); r['multiple'] = round(r['views'] / med, 2) if med else ''
        r['chan_median'] = int(allmed)
        r['age_days'] = (TODAY - r['date']).days if r['date'] else ''
        r['views_per_day'] = round(r['views'] / max(r['age_days'], 1)) if r['date'] else ''
        r['like_rate'] = round(r['likes'] / r['views'] * 100, 2) if r['likes'] and r['views'] else ''
        r['comment_rate'] = round(r['comments'] / r['views'] * 1000, 2) if r['comments'] and r['views'] else ''
cols = ['handle','tab','id','url','title','title_en','date','date_src','age_days','duration','views','views_src','likes','comments',
        'like_rate','comment_rate','chapters','neigh_median','multiple','chan_median','views_per_day','thumb','desc_first_line']
with open(f"{S}/data/videos.csv", 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore'); w.writeheader()
    for r in rows: w.writerow(r)
print(len(rows), 'rows;', sum(1 for r in rows if r['date_src'] in ('vidiq','yt-dlp')), 'with exact data')
