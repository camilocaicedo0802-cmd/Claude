"""Busca vídeos en Mixkit (licencia gratuita de uso comercial) y guarda resultados + miniaturas.
Uso: python3 scripts/mixkit_buscar.py <salida.json> termino1 termino2 ...
"""
import json, re, subprocess, sys, urllib.request
out, terms = sys.argv[1], sys.argv[2:]
res = {}
for t in terms:
    slug = t.strip().lower().replace(" ", "-")
    for page in ["", "?page=2"]:
        url = f"https://mixkit.co/free-stock-video/{slug}/{page}"
        try:
            html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf8", "ignore")
        except Exception as e:
            print("fallo", url, e); continue
        for m in re.finditer(r'/free-stock-video/([a-z0-9-]+)-(\d+)/', html):
            title, vid = m.group(1), m.group(2)
            if vid not in res:
                res[vid] = {"id": vid, "titulo": title.replace("-", " "), "termino": t,
                            "mp4_720": f"https://assets.mixkit.co/videos/{vid}/{vid}-720.mp4",
                            "mp4_360": f"https://assets.mixkit.co/videos/{vid}/{vid}-360.mp4",
                            "thumb": f"https://assets.mixkit.co/videos/{vid}/{vid}-thumb-360-0.jpg"}
json.dump(list(res.values()), open(out, "w"), ensure_ascii=False, indent=1)
print(len(res), "resultados")
