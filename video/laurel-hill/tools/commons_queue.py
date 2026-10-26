import json, os, sys, time, urllib.request, urllib.error
UA = "LaurelHillDoc/1.0 (https://github.com/camilocaicedo0802-cmd; camilocaicedo0802@gmail.com) python-urllib"
ROOT = sys.argv[1]
q = json.load(open('commons_queue.json'))
for it in q:
    ext = os.path.splitext(it['url'].split('?')[0])[1].lower()
    d = os.path.join(ROOT, 'img' if it.get('img') else 'vid')
    p = os.path.join(d, it['name'] + (ext if not it.get('img') else ('.jpg' if ext in ('.jpg', '.jpeg') else ext)))
    if os.path.exists(p) and os.path.getsize(p) > 10000: continue
    while True:
        try:
            req = urllib.request.Request(it['url'], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=300) as r, open(p + '.part', 'wb') as f:
                while True:
                    b = r.read(1 << 20)
                    if not b: break
                    f.write(b)
                    time.sleep(0.35)  # keep well under 25 Mbps
            os.rename(p + '.part', p)
            print('ok', it['name'], flush=True)
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                ra = int(e.headers.get('retry-after') or 60)
                print('429', it['name'], ra, time.strftime('%H:%M:%S'), flush=True)
                time.sleep(ra + 5)
                continue
            print('HTTP', e.code, it['name'], flush=True); break
        except Exception as e:
            print('err', it['name'], e, flush=True); time.sleep(30); break
    time.sleep(2)
print('ALLDONE', flush=True)
