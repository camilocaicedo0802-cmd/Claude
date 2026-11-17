"""Busca clips en Mixkit (licencia gratuita, uso comercial) por palabras clave.
Guarda id, título y orientación aproximada, y descarga miniaturas.
Uso: python3 -I mixkit_search.py <salida_dir> kw1 kw2 ..."""
import json, os, re, subprocess, sys, html
out = sys.argv[1]
os.makedirs(f"{out}/thumbs", exist_ok=True)
db_path = f"{out}/mixkit.json"
db = json.load(open(db_path)) if os.path.exists(db_path) else {}
UA = "Mozilla/5.0 (X11; Linux x86_64)"
item_re = re.compile(r'data-item-grid--video-player-item-id-value="(\d+)".*?<img src="([^"]+)"[^>]*alt="([^"]*)"', re.S)
for kw in sys.argv[2:]:
    for page in (1, 2):
        url = f"https://mixkit.co/free-stock-video/{kw}/" + (f"?page={page}" if page > 1 else "")
        h = subprocess.run(["curl", "-s", "-L", "--max-time", "30", "-A", UA, url], capture_output=True, text=True).stdout
        found = item_re.findall(h)
        for vid, thumb, title in found:
            e = db.setdefault(vid, {"id": vid, "title": html.unescape(title).strip(), "thumb": thumb, "kws": []})
            if kw not in e["kws"]:
                e["kws"].append(kw)
        print(f"{kw} p{page}: {len(found)} clips", flush=True)
        if len(found) < 20:
            break
json.dump(db, open(db_path, "w"), indent=1, ensure_ascii=False)
todo = [e for e in db.values() if not os.path.exists(f"{out}/thumbs/{e['id']}.jpg")]
from concurrent.futures import ThreadPoolExecutor
def dl(e):
    subprocess.run(["curl", "-s", "--max-time", "30", "-o", f"{out}/thumbs/{e['id']}.jpg", e["thumb"]])
with ThreadPoolExecutor(8) as ex:
    list(ex.map(dl, todo))
print("total clips en base:", len(db))
