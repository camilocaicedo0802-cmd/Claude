"""archive.org film fetcher: picks the best MP4 of each item, records title/license.

usage: python ia.py OUT_DIR REGISTRY.json id1 id2 ...
"""
import json, os, sys, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) CGDoc/1.0 (camilocaicedo0802@gmail.com)"
OK = ("publicdomain", "zero/1.0", "/by/")  # PD mark, CC0, CC BY (not BY-SA/NC/ND)


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = r.read()
    return d if binary else d.decode("utf-8", "ignore")


def pick(files):
    vids = [f for f in files if f["name"].lower().endswith((".mp4", ".mpeg", ".mpg")) and int(f.get("size", 0) or 0) > 0]
    if not vids:
        return None

    def score(f):
        n, size = f["name"].lower(), int(f["size"])
        try:
            res = int(f.get("width") or 0) * int(f.get("height") or 0)
        except ValueError:
            res = 0
        fmt = f.get("format", "").lower()
        ok = 0 if size > 2_500_000_000 else 1
        return (ok, res, "512kb" not in n, "mpeg2" in fmt, min(size, 2_000_000_000))
    return max(vids, key=score)


def main():
    out, reg_path, ids = sys.argv[1], sys.argv[2], sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    reg = json.load(open(reg_path)) if os.path.exists(reg_path) else {}
    for ident in ids:
        try:
            meta = json.loads(get(f"https://archive.org/metadata/{ident}"))
        except Exception as e:
            print("meta fail", ident, e, flush=True)
            continue
        md = meta.get("metadata", {})
        lic = md.get("licenseurl", "") or ""
        coll = md.get("collection", [])
        coll = coll if isinstance(coll, list) else [coll]
        pd_coll = any(c in ("prelinger", "prelinger_library", "universal_newsreels", "FedFlix", "home_movies") for c in coll)
        if not (any(k in lic for k in OK) and "by-sa" not in lic and "-nc" not in lic and "-nd" not in lic) and not (pd_coll and not lic):
            print("SKIP license", ident, lic, coll, flush=True)
            continue
        f = pick(meta.get("files", []))
        if not f:
            print("no mp4", ident, flush=True)
            continue
        dst = os.path.join(out, f"ia_{ident}.mp4")
        if not os.path.exists(dst):
            url = f"https://archive.org/download/{ident}/{urllib.parse.quote(f['name'])}"
            tmp = dst + ".part"
            for i in range(3):
                try:
                    data = get(url, binary=True)
                    open(tmp, "wb").write(data)
                    if f["name"].lower().endswith((".mpeg", ".mpg")):
                        import subprocess
                        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-vf", "scale=trunc(ih*dar/2)*2:ih,setsar=1",
                                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-f", "mp4", tmp + ".mp4"], check=True)
                        os.remove(tmp)
                        tmp = tmp + ".mp4"
                    os.replace(tmp, dst)
                    break
                except Exception as e:
                    print("retry", ident, e, flush=True)
                    time.sleep(5)
        reg[ident] = {"file": os.path.basename(dst), "title": md.get("title"), "year": md.get("year") or md.get("date"),
                      "license": lic or "public domain (" + ",".join(coll) + ")", "creator": md.get("creator"),
                      "src": f"https://archive.org/details/{ident}"}
        json.dump(reg, open(reg_path, "w"), indent=1, ensure_ascii=False)
        print("ok", ident, f["name"], int(f["size"]) // 1_000_000, "MB", lic, flush=True)


if __name__ == "__main__":
    main()
