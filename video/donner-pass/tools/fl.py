"""Flickr search (HTML page model) limited to licenses that allow commercial reuse, plus polite downloads.

usage: python fl.py search OUT.json "query 1" "query 2" ...   (appends to OUT.json)
       python fl.py get OUT.json DIR id1 id2 ...                (downloads largest size, writes DIR/f_<id>.jpg)
"""
import json, os, re, sys, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) DPDoc/1.0 (camilocaicedo0802@gmail.com)"
LIC = {4: "CC BY 2.0", 7: "No known copyright restrictions", 8: "United States Government Work", 9: "CC0 1.0",
       10: "Public Domain Mark", 11: "CC BY 4.0"}


def get(url, binary=False):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = r.read()
            return d if binary else d.decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(10 * (i + 1))
                continue
            raise
        except Exception:
            time.sleep(3 * (i + 1))
    raise RuntimeError("failed " + url)


def walk(o):
    if isinstance(o, dict):
        if "license" in o and "ownerNsid" in o:
            yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def search(q, page=1):
    url = "https://www.flickr.com/search/?" + urllib.parse.urlencode(
        {"text": q, "license": ",".join(map(str, LIC)), "page": page})
    h = get(url)
    m = re.search(r"modelExport:\s*(\{.*?\})\s*,\s*auth:", h, re.S)
    if not m:
        return []
    out = []
    for p in walk(json.loads(m.group(1))):
        if p.get("license") not in LIC:
            continue
        sizes = p.get("sizes", {}).get("data", {})
        best = max((s["data"] for s in sizes.values()), key=lambda s: s.get("width", 0) * s.get("height", 0), default={})
        out.append({"id": p["id"], "owner": p["ownerNsid"], "alias": p.get("pathAlias") or p["ownerNsid"],
                    "author": p.get("realname") or p.get("username"), "title": p.get("title", ""),
                    "license": LIC[p["license"]], "w": best.get("width"), "h": best.get("height"),
                    "thumb": "https:" + best.get("url", ""), "q": q})
    return out


def largest(alias, pid):
    for size in ("k", "h", "b", "c"):
        try:
            h = get(f"https://www.flickr.com/photos/{alias}/{pid}/sizes/{size}/")
        except Exception:
            continue
        c = re.findall(r"https://live\.staticflickr\.com/[^\"']+?_" + size + r"\.(?:jpg|png)", h)
        if c:
            return get(c[0], binary=True)
    raise RuntimeError("no size for " + pid)


if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]
    db = json.load(open(out)) if os.path.exists(out) else {}
    if cmd == "search":
        for q in sys.argv[3:]:
            for page in (1, 2):
                try:
                    res = search(q, page)
                except Exception as e:
                    print("ERR", q, e, flush=True)
                    break
                for r in res:
                    db.setdefault(r["id"], r)
                print(f"{q!r} p{page}: {len(res)}", flush=True)
                time.sleep(2)
        json.dump(db, open(out, "w"), ensure_ascii=False, indent=0)
    elif cmd == "get":
        d = sys.argv[3]
        os.makedirs(d, exist_ok=True)
        for pid in sys.argv[4:]:
            path = os.path.join(d, f"f_{pid}.jpg")
            if os.path.exists(path):
                continue
            r = db[pid]
            try:
                data = largest(r["alias"], pid)
                open(path, "wb").write(data)
                print("ok", pid, len(data), flush=True)
            except Exception as e:
                print("fail", pid, e, flush=True)
            time.sleep(float(os.environ.get("FL_SLEEP", "1.5")))
