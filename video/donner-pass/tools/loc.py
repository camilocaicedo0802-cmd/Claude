"""Library of Congress photo search (unrestricted items only) + IIIF download.

usage: python loc.py search DB.json "q1" "q2" ...
       python loc.py get DB.json OUT_DIR id1 id2 ...
"""
import json, os, re, sys, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) DPDoc/1.0 (camilocaicedo0802@gmail.com)"


def get(url, binary=False):
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = r.read()
            return d if binary else d.decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(30 * (i + 1))
                continue
            raise
        except Exception:
            time.sleep(5)
    raise RuntimeError("failed " + url)


def thumb_url(svc):
    if svc.startswith("service:pnp:"):
        return "https://tile.loc.gov/storage-services/" + svc.replace(":", "/") + "r.jpg"
    return f"https://tile.loc.gov/image-services/iiif/{svc}/full/320,/0/default.jpg"


def head_size(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return int(r.headers.get("Content-Length") or 0)
    except Exception:
        return -1


def get_pnp(svc, p):
    """Prints & Photographs: master TIFF when it is a sane size, else the 1024px service JPEG."""
    from PIL import Image
    import io
    path = svc.replace(":", "/")
    tif = "https://tile.loc.gov/storage-services/" + path.replace("service/", "master/", 1) + "u.tif"
    n = head_size(tif)
    if 0 < n < 150_000_000:
        try:
            im = Image.open(io.BytesIO(get(tif, True)))
            im = im.convert("RGB") if im.mode not in ("RGB", "L") else im
            im.thumbnail((2600, 2600))
            im.convert("RGB").save(p, quality=92)
            return "tif"
        except Exception as e:
            print("tif fail", svc, e, flush=True)
    data = get("https://tile.loc.gov/storage-services/" + path + "v.jpg", True)
    open(p, "wb").write(data)
    return "v"


def search(q, n=40):
    url = "https://www.loc.gov/photos/?" + urllib.parse.urlencode({"q": q, "fo": "json", "c": n, "at": "results"})
    d = json.loads(get(url))
    out = []
    for r in d.get("results", []):
        if not r.get("unrestricted"):
            continue
        res = r.get("resources") or [{}]
        img = res[0].get("image") or ""
        m = re.search(r"iiif/(service:[^/]+)/", img)
        if m:
            svc = m.group(1)
        else:
            m2 = re.search(r"storage-services/(service/pnp/[^#?]+?)(?:_\d+px|[a-z])?\.(?:jpg|gif|png)", img)
            if not m2:
                continue
            svc = m2.group(1).replace("/", ":")
        lid = svc.split(":")[-1]
        out.append({"id": lid, "svc": svc, "title": r.get("title", "")[:200], "date": r.get("date"),
                    "url": r.get("url"), "q": q, "thumb": thumb_url(svc)})
    return out


if __name__ == "__main__":
    cmd, dbp = sys.argv[1], sys.argv[2]
    db = json.load(open(dbp)) if os.path.exists(dbp) else {}
    if cmd == "search":
        for q in sys.argv[3:]:
            try:
                res = search(q)
            except Exception as e:
                print("ERR", q, e, flush=True)
                continue
            for r in res:
                db.setdefault(r["id"], r)
            print(f"{q!r}: {len(res)}", flush=True)
            json.dump(db, open(dbp, "w"), indent=0, ensure_ascii=False)
            time.sleep(3)
    elif cmd == "get":
        out = sys.argv[3]
        for lid in sys.argv[4:]:
            p = os.path.join(out, f"l_{lid}.jpg")
            if os.path.exists(p):
                continue
            svc = db[lid]["svc"]
            if svc.startswith("service:pnp:"):
                try:
                    print("ok", lid, get_pnp(svc, p), flush=True)
                except Exception as e:
                    print("fail", lid, e, flush=True)
                time.sleep(1)
                continue
            for size in ("2400,", "1600,", "full"):
                try:
                    data = get(f"https://tile.loc.gov/image-services/iiif/{svc}/full/{size}/0/default.jpg", True)
                    if len(data) > 30000:
                        open(p, "wb").write(data)
                        print("ok", lid, len(data), flush=True)
                        break
                except Exception as e:
                    print("retry", lid, size, e, flush=True)
            time.sleep(2)
