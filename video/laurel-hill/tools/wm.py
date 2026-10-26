"""Polite Wikimedia Commons helper: search files, fetch info, download thumbs (retries on 429)."""
import json, os, sys, time, urllib.parse, urllib.request, re, html

UA = "LaurelHillDoc/1.0 (https://github.com/camilocaicedo0802-cmd; camilocaicedo0802@gmail.com) python-urllib"
API = "https://commons.wikimedia.org/w/api.php"

def get(url, binary=False, tries=8):
    delay = 4
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                return data if binary else data.decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503, 502):
                ra = e.headers.get("retry-after")
                time.sleep(max(delay, int(ra) if ra and ra.isdigit() else 0))
                delay = min(delay * 2, 60)
                continue
            raise
        except Exception:
            time.sleep(delay); delay = min(delay * 2, 60)
    raise RuntimeError("failed " + url)

def api(params, host=API):
    params = dict(params, format="json", maxlag="5")
    return json.loads(get(host + "?" + urllib.parse.urlencode(params)))

def clean(s):
    return html.unescape(re.sub("<[^>]+>", "", s or "")).strip()

def search(q, limit=20, width=1920):
    d = api({"action": "query", "generator": "search", "gsrsearch": q, "gsrnamespace": 6,
             "gsrlimit": limit, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime",
             "iiurlwidth": width, "iiextmetadatafilter": "LicenseShortName|Artist|DateTimeOriginal|ImageDescription"})
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]
        if not ii.get("mime", "").startswith("image/") or ii["mime"] == "image/svg+xml" and False:
            continue
        m = ii.get("extmetadata", {})
        out.append({"title": p["title"], "w": ii["width"], "h": ii["height"], "mime": ii["mime"],
                    "thumb": ii.get("thumburl", ii["url"]), "url": ii["url"],
                    "license": clean(m.get("LicenseShortName", {}).get("value")),
                    "artist": clean(m.get("Artist", {}).get("value"))[:80],
                    "date": clean(m.get("DateTimeOriginal", {}).get("value"))[:40],
                    "desc": clean(m.get("ImageDescription", {}).get("value"))[:160]})
    return out

def info(titles, width=1920):
    d = api({"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
             "iiprop": "url|size|extmetadata|mime", "iiurlwidth": width,
             "iiextmetadatafilter": "LicenseShortName|Artist|DateTimeOriginal"})
    res = {}
    for p in d.get("query", {}).get("pages", {}).values():
        if "imageinfo" not in p: continue
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        res[p["title"]] = {"thumb": ii.get("thumburl", ii["url"]), "url": ii["url"], "w": ii["width"], "h": ii["height"],
                           "license": clean(m.get("LicenseShortName", {}).get("value")),
                           "artist": clean(m.get("Artist", {}).get("value"))[:80]}
    return res

def download(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    data = get(url, binary=True)
    with open(path, "wb") as f:
        f.write(data)
    time.sleep(1)
    return path

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "search":
        for q in sys.argv[2:]:
            print("##", q)
            for r in search(q):
                print(f"  {r['w']}x{r['h']} [{r['license']}] {r['title'][5:90]} | {r['date']} | {r['desc'][:90]}")
            time.sleep(2)

def search_video(q, limit=20):
    d = api({"action": "query", "generator": "search", "gsrsearch": "filetype:video " + q, "gsrnamespace": 6,
             "gsrlimit": limit, "prop": "imageinfo|videoinfo", "viprop": "url|size|mime|extmetadata|derivatives",
             "viextmetadatafilter": "LicenseShortName|Artist|ImageDescription", "iiurlwidth": 480, "iiprop": "url"})
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        vi = (p.get("videoinfo") or [{}])[0]
        m = vi.get("extmetadata", {})
        ders = vi.get("derivatives", [])
        out.append({"title": p["title"], "w": vi.get("width"), "h": vi.get("height"), "dur": vi.get("duration"),
                    "url": vi.get("url"), "mime": vi.get("mime"),
                    "thumb": (p.get("imageinfo") or [{}])[0].get("thumburl"),
                    "license": clean(m.get("LicenseShortName", {}).get("value")),
                    "artist": clean(m.get("Artist", {}).get("value"))[:80],
                    "desc": clean(m.get("ImageDescription", {}).get("value"))[:140],
                    "derivs": [(x.get("width"), x.get("height"), x.get("src")) for x in ders if x.get("type", "").startswith("video/webm")]})
    return out
