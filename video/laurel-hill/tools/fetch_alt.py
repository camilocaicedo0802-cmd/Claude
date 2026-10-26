import sys, os, json, re, time, urllib.request, urllib.error
UA = "Mozilla/5.0 (X11; Linux x86_64) LaurelHillDoc/1.0 (camilocaicedo0802@gmail.com)"
OUT = sys.argv[1]
reg = json.load(open('registry.json'))
items = {v['id']: v['title'] for v in reg.values()}
items.update(json.load(open('extra_titles.json')))
src = json.load(open('sources.json'))
srcurls = json.load(open('srcurls.json'))
skip = {'c005', 'c017', 'c048', 'c056', 'c128', 'c033', 'c034', 'c035', 'c036', 'c041', 'c042', 'c046', 'c047'}

def get(url, binary=True):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        d = r.read()
    return d if binary else d.decode('utf-8', 'ignore')

def have(cid):
    return any(os.path.exists(os.path.join(OUT, cid + e)) for e in ('.jpg', '.jpeg', '.png', '.gif', '.JPG'))

def save(cid, data):
    if len(data) < 20000: raise RuntimeError('too small %d' % len(data))
    open(os.path.join(OUT, cid + '.jpg'), 'wb').write(data)

def iiif_loc(path_parts, width=1920):
    svc = ":".join(path_parts)
    for w in (f"{width},", "full"):
        try:
            return get(f"https://tile.loc.gov/image-services/iiif/{svc}/full/{w}/0/default.jpg")
        except Exception:
            pass
    raise RuntimeError('iiif fail ' + svc)

def loc_from_url(u):
    m = re.search(r'/(?:service|master)/pnp/(.+?)\.(jpg|tif)', u)
    if not m: raise RuntimeError('no loc path')
    parts = m.group(1).split('/')
    last = parts[-1]
    base = re.sub(r'[uvr]$', '', last)
    for suf in ('u', 'v', ''):
        try:
            return iiif_loc(['service', 'pnp'] + parts[:-1] + [base + suf])
        except Exception:
            continue
    return get(u.replace('http://', 'https://').replace('lcweb2.loc.gov', 'tile.loc.gov/storage-services').replace('memory.loc.gov', 'tile.loc.gov/storage-services').replace('cdn.loc.gov', 'tile.loc.gov/storage-services'))

def fsa(id_):
    a, b = id_[:4] + '000', id_[:5] + '00'
    for suf in ('u', 'v'):
        try:
            return iiif_loc(['service', 'pnp', 'fsa', a, b, id_ + suf])
        except Exception:
            continue
    raise RuntimeError('fsa fail')

def flickr(u):
    m = re.search(r'flickr\.com/photos/([^/]+)/(\d+)', u)
    user, pid = m.groups()
    for size in ('k', 'h', 'b', 'o', 'c'):
        try:
            h = get(f"https://www.flickr.com/photos/{user}/{pid}/sizes/{size}/", binary=False)
        except Exception:
            continue
        cands = re.findall(r'https://live\.staticflickr\.com/[^"\']+?_' + size + r'\.(?:jpg|png)', h)
        if cands:
            return get(cands[0])
    raise RuntimeError('flickr fail')

def dcommonwealth(u):
    h = get(u.replace('http://', 'https://'), binary=False)
    m = re.search(r'commonwealth:([a-z0-9]+)', h)
    ids = re.findall(r'commonwealth:([a-z0-9]{9})', h)
    for i in dict.fromkeys(ids):
        try:
            return get(f"https://iiif.digitalcommonwealth.org/iiif/2/commonwealth:{i}/full/1920,/0/default.jpg")
        except Exception:
            continue
    raise RuntimeError('dc fail')

done, todo = [], []
for cid, t in items.items():
    if cid in skip or have(cid): continue
    links = [l for l in src.get(t, []) if not re.search('wikimedia|wikipedia|wikidata|toolforge', l)]
    su = srcurls.get(cid, {})
    try:
        data = None
        if su.get('ids') and re.match(r'8[a-z]\d{5}', su['ids'][0]):
            data = fsa(su['ids'][0])
        elif any(re.search(r'/pnp/', u) for u in su.get('urls', [])):
            data = loc_from_url([u for u in su['urls'] if '/pnp/' in u][0])
        elif links and 'flickr.com' in links[0]:
            data = flickr(links[0])
        elif links and 'digitalcommonwealth' in links[0]:
            data = dcommonwealth(links[0])
        if data:
            save(cid, data); done.append(cid); print('ok', cid, len(data), flush=True)
        else:
            todo.append(cid); print('todo', cid, (links[:1] or [''])[0][:80], flush=True)
    except Exception as e:
        todo.append(cid); print('fail', cid, e, flush=True)
    time.sleep(0.8)
json.dump(todo, open('todo_commons.json', 'w'))
print('DONE', len(done), 'TODO', len(todo))
