"""Mixkit stock video: search, contact sheets from the 360p previews, and licensed downloads.

Only items whose page declares the "Stock Video Free License" (data-license="videoFree") are downloaded.

usage: python mk.py search DB.json "term 1" "term 2" ...      # appends results (id, slug, title, preview) to DB
       python mk.py sheet DB.json OUTDIR [term ...]           # 3-frame contact sheets per term from 360p previews
       python mk.py get DB.json VIDDIR id1 id2 ...            # checks license, downloads 1080p, keeps a 1080p30 copy
"""
import json, os, re, subprocess, sys, time, urllib.request

UA = "DocResearchBot/1.0"
SITE = "https://mixkit.co"


def get(url, binary=False):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = r.read()
            return d if binary else d.decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(5 * (i + 1))
        except Exception:
            time.sleep(5 * (i + 1))
    return None


def load(db):
    return json.load(open(db)) if os.path.exists(db) else {}


def save(db, d):
    json.dump(d, open(db, "w"), ensure_ascii=False, indent=1)


def search(db, terms, pages=2):
    d = load(db)
    for term in terms:
        slug = re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
        n = 0
        for p in range(1, pages + 1):
            url = f"{SITE}/free-stock-video/discover/{slug}/" + (f"?page={p}" if p > 1 else "")
            s = get(url)
            if not s:
                break
            items = re.findall(r'/free-stock-video/([a-z0-9-]+)-(\d+)/', s)
            prevs = re.findall(r'https://assets\.mixkit\.co/[^"\s]*?/(\d+)(?:/\d+)?/\1-(?:video-)?360\.mp4', s)
            purls = {m.group(1): m.group(0) for m in re.finditer(
                r'https://assets\.mixkit\.co/(?:videos|active_storage/video_items)/(\d+)/(?:\d+/)?\1-(?:video-)?360\.mp4', s)}
            seen = set()
            for sl, vid in items:
                if vid in seen:
                    continue
                seen.add(vid)
                e = d.setdefault(vid, {"id": vid, "slug": f"{sl}-{vid}", "title": sl.replace("-", " "), "terms": []})
                if purls.get(vid):
                    e["preview"] = purls[vid]
                if term not in e["terms"]:
                    e["terms"].append(term)
                n += 1
            time.sleep(1.0)
        print(f"{term}: {n}", flush=True)
        save(db, d)


def sheet(db, outdir, terms):
    from PIL import Image, ImageDraw, ImageFont
    d = load(db)
    os.makedirs(outdir, exist_ok=True)
    pv = os.path.join(outdir, "previews")
    os.makedirs(pv, exist_ok=True)
    terms = terms or sorted({t for e in d.values() for t in e["terms"]})
    try:
        fnt = ImageFont.truetype(os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "JetBrainsMono.ttf"), 15)
    except Exception:
        fnt = ImageFont.load_default()
    for term in terms:
        es = [e for e in d.values() if term in e["terms"] and e.get("preview")]
        if not es:
            continue
        cells = []
        for e in es[:24]:
            mp4 = os.path.join(pv, e["id"] + ".mp4")
            if not os.path.exists(mp4):
                b = get(e["preview"], True)
                if not b:
                    continue
                open(mp4, "wb").write(b)
            try:
                dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4],
                                           capture_output=True, text=True).stdout.strip())
            except ValueError:
                continue
            e["dur"] = round(dur, 1)
            frames = []
            for k in (0.1, 0.5, 0.9):
                r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{dur * k:.2f}", "-i", mp4, "-frames:v", "1",
                                    "-vf", "scale=224:126:force_original_aspect_ratio=increase,crop=224:126", "-f", "rawvideo",
                                    "-pix_fmt", "rgb24", "-"], capture_output=True)
                if len(r.stdout) == 224 * 126 * 3:
                    frames.append(Image.frombytes("RGB", (224, 126), r.stdout))
            if frames:
                cells.append((e, frames))
        if not cells:
            continue
        cw, ch = 3 * 224 + 8, 126 + 24
        cols = 2
        rows = (len(cells) + cols - 1) // cols
        im = Image.new("RGB", (cols * (cw + 10) + 10, rows * (ch + 10) + 10), (20, 20, 20))
        dr = ImageDraw.Draw(im)
        for i, (e, frames) in enumerate(cells):
            x, y = 10 + (i % cols) * (cw + 10), 10 + (i // cols) * (ch + 10)
            for j, f in enumerate(frames):
                im.paste(f, (x + j * 228, y))
            dr.text((x, y + 128), f"{e['id']} {e.get('dur', '?')}s {e['title'][:52]}", fill=(255, 230, 80), font=fnt)
        slug = re.sub(r"[^a-z0-9]+", "_", term.lower())
        im.save(os.path.join(outdir, f"mk_{slug}.jpg"), quality=82)
        print("sheet", term, len(cells), flush=True)
    save(db, d)


def get_items(db, viddir, ids, maxdur=30.0):
    d = load(db)
    os.makedirs(viddir, exist_ok=True)
    for vid in ids:
        e = d.get(vid) or {"id": vid, "slug": None, "terms": []}
        out = os.path.join(viddir, f"mk_{vid}.mp4")
        if os.path.exists(out):
            print("have", vid)
            continue
        page_url = f"{SITE}/free-stock-video/{e['slug']}/" if e.get("slug") else None
        s = get(page_url) if page_url else None
        if not s:
            print("FAIL page", vid)
            continue
        lic = re.findall(r'data-license="(video\w+)"', s)
        # the item's own license badge comes first on its page
        e["license"] = lic[0] if lic else None
        if e["license"] != "videoFree":
            print("SKIP license", vid, e["license"])
            d[vid] = e
            continue
        t = re.search(r"<title>([^<|]+)", s)
        e["title"] = t.group(1).strip() if t else e.get("title")
        e["page"] = page_url
        src = None
        for res in ("1080", "720"):
            m = re.search(rf'https://assets\.mixkit\.co/(?:videos|active_storage/video_items)/{vid}/(?:\d+/)?{vid}-(?:video-)?{res}\.mp4', s)
            cand = m.group(0) if m else f"https://assets.mixkit.co/videos/{vid}/{vid}-{res}.mp4"
            r = subprocess.run(["curl", "-sI", "-A", UA, cand], capture_output=True, text=True).stdout
            if " 200" in r.split("\n\n")[-2 if r.count("HTTP/") > 1 else 0] or "content-type: video" in r.lower():
                src = cand
                break
        if not src:
            print("FAIL src", vid)
            continue
        tmp = out + ".src.mp4"
        subprocess.run(["curl", "-sS", "-L", "--fail", "-A", UA, "-o", tmp, src], check=False)
        if not os.path.exists(tmp) or os.path.getsize(tmp) < 100_000:
            print("FAIL dl", vid)
            continue
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-t", str(maxdur), "-an",
                        "-vf", "fps=30,scale=1920:1080:force_original_aspect_ratio=increase:flags=bicubic,crop=1920:1080",
                        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out], check=False)
        os.remove(tmp)
        e["src"], e["file"] = src, out
        d[vid] = e
        save(db, d)
        print("OK", vid, e["title"], flush=True)
    save(db, d)


if __name__ == "__main__":
    cmd, db = sys.argv[1], sys.argv[2]
    if cmd == "search":
        search(db, sys.argv[3:])
    elif cmd == "sheet":
        sheet(db, sys.argv[3], sys.argv[4:])
    elif cmd == "get":
        get_items(db, sys.argv[3], sys.argv[4:])
