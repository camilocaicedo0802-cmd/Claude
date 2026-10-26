import sys, os, json, time, re, urllib.request, urllib.error
UA = "LaurelHillDoc/1.0 (https://github.com/camilocaicedo0802-cmd; camilocaicedo0802@gmail.com) python-urllib"
OUT = sys.argv[1]
reg = json.load(open('registry.json'))
skip = {'c005', 'c017', 'c048', 'c056', 'c128'}
items = {v['id']: v['title'] for v in reg.values() if v['id'] not in skip}
items.update(json.load(open('extra_titles.json')))
meta = json.load(open('commons_meta.json'))
def fetch(url, path):
    while True:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            open(path, 'wb').write(data); return True
        except urllib.error.HTTPError as e:
            if e.code == 429:
                ra = int(e.headers.get('retry-after') or 10)
                print('429 wait', ra, flush=True); time.sleep(ra + 1); continue
            print('HTTP', e.code, url, flush=True); return False
        except Exception as e:
            print('err', e, flush=True); time.sleep(5)
for cid, t in items.items():
    m = meta.get(t)
    if not m: print('nometa', cid, t, flush=True); continue
    if m['w'] > 1920:
        url = re.sub(r'/\d+px-', '/1920px-', m['thumb'])
    else:
        url = m['url']
        if url.lower().endswith(('.tif', '.tiff')):
            url = re.sub(r'/\d+px-', f"/1280px-", m['thumb'])
    ext = os.path.splitext(url.split('?')[0])[1].lower() or '.jpg'
    if ext in ('.tif', '.tiff'): ext = '.jpg'
    p = os.path.join(OUT, f"{cid}{ext}")
    if any(os.path.exists(os.path.join(OUT, cid + e)) for e in ('.jpg', '.jpeg', '.png', '.gif', '.JPG')):
        continue
    ok = fetch(url, p)
    print('ok' if ok else 'FAIL', cid, url[-60:], flush=True)
    time.sleep(1.5)
print('done')
