#!/usr/bin/env python3
"""
Busca imágenes con licencia reutilizable (Openverse: Flickr, Wikimedia Commons, etc.) y genera una hoja de contactos.

  search "hourglass" cand/hourglass [--n 20] [--license commercial,modification]
      -> cand/hourglass/{00.jpg…, sheet.png, results.json}
  get cand/hourglass 3 7 --out assets/raw --name reloj
      -> descarga a tamaño completo los resultados 3 y 7 y añade sus créditos a assets/raw/credits.json
  credits assets/raw/credits.json
      -> imprime la tabla de créditos en Markdown (para CREDITOS.md y la descripción del vídeo)

Límites anónimos de Openverse: ~20 peticiones/min y 200/día. Las imágenes se descargan del host original.
Wikimedia exige un User-Agent descriptivo y limita ráfagas (HTTP 429): el script espera y reintenta.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse

UA = "MotionGraphicsSkill/1.0 (video editing; image reuse with attribution)"


def curl(url, out=None, tries=4):
    for k in range(tries):
        args = ["curl", "-sS", "-L", "--max-time", "90", "-A", UA, "-w", "%{http_code}"]
        if out:
            args += ["-o", out]
        r = subprocess.run(args + [url], capture_output=True)
        code = r.stdout[-3:].decode(errors="ignore") if r.stdout else "000"
        if code == "200":
            return r.stdout[:-3] if not out else True
        wait = 6 * (k + 1) if code == "429" else 2 ** (k + 1)
        print(f"  HTTP {code} en {url[:70]}… reintento en {wait}s", file=sys.stderr)
        time.sleep(wait)
    return None


def small(u):
    if "staticflickr" in u:
        b, ext = u.rsplit(".", 1)
        for suf in ("_b", "_c", "_z", "_o", "_h", "_k"):
            if b.endswith(suf):
                b = b[: -len(suf)]
        return f"{b}_n.{ext}"
    if "upload.wikimedia.org" in u and "/thumb/" not in u:
        parts = u.split("/commons/")
        if len(parts) == 2:
            fn = parts[1].rsplit("/", 1)[-1]
            return f"{parts[0]}/commons/thumb/{parts[1]}/320px-{fn}"
    return u


def sheet(d, files, cols=5, size=260):
    from PIL import Image, ImageDraw

    rows = max(1, (len(files) + cols - 1) // cols)
    S = Image.new("RGB", (cols * size, rows * (size + 22)), "white")
    dr = ImageDraw.Draw(S)
    for i, f in enumerate(files):
        x, y = (i % cols) * size, (i // cols) * (size + 22)
        dr.text((x + 4, y + 4), f"{i:02d}", fill="red")
        try:
            im = Image.open(f).convert("RGB")
            im.thumbnail((size - 6, size - 6))
            S.paste(im, (x, y + 20))
        except Exception:  # noqa: BLE001
            dr.text((x + 30, y + 100), "sin miniatura", fill="gray")
    S.save(os.path.join(d, "sheet.png"))


def cmd_search(a):
    os.makedirs(a.outdir, exist_ok=True)
    q = urllib.parse.urlencode({"q": a.query, "page_size": a.n, "license_type": a.license, "mature": "false"})
    raw = curl(f"https://api.openverse.org/v1/images/?{q}")
    if not raw:
        sys.exit("Openverse no responde")
    res = [r for r in json.loads(raw)["results"] if r.get("url")]
    json.dump(res, open(os.path.join(a.outdir, "results.json"), "w"), indent=1, ensure_ascii=False)
    files = []
    for i, r in enumerate(res):
        f = os.path.join(a.outdir, f"{i:02d}.jpg")
        if not curl(small(r["url"]), f, tries=2):
            curl(r["url"], f, tries=2)
        files.append(f)
        print(f"{i:02d} {(r.get('title') or '')[:55]:55s} {r['source']:10s} {r['license']:6s} {r.get('width')}x{r.get('height')}")
        time.sleep(0.3)
    sheet(a.outdir, files)
    print(f"Hoja de contactos: {os.path.join(a.outdir, 'sheet.png')}")


def cmd_get(a):
    res = json.load(open(os.path.join(a.cand, "results.json")))
    os.makedirs(a.out, exist_ok=True)
    cpath = os.path.join(a.out, "credits.json")
    credits = json.load(open(cpath)) if os.path.exists(cpath) else []
    for k, idx in enumerate(a.idx):
        r = res[idx]
        ext = os.path.splitext(urllib.parse.urlparse(r["url"]).path)[1] or ".jpg"
        name = f"{a.name}{'' if len(a.idx) == 1 else '_' + str(k + 1)}{ext}"
        dst = os.path.join(a.out, name)
        ok = curl(r["url"], dst)
        print(dst, "ok" if ok else "FALLO")
        credits.append({"file": name, "title": r.get("title"), "creator": r.get("creator"), "license": f"CC {r['license'].upper()} {r.get('license_version') or ''}".strip() if r["license"] not in ("cc0", "pdm") else r["license"].upper(), "source": r.get("foreign_landing_url"), "url": r["url"]})
        time.sleep(1)
    json.dump(credits, open(cpath, "w"), indent=1, ensure_ascii=False)


def cmd_credits(a):
    cr = json.load(open(a.path))
    print("| Archivo | Título | Autor | Licencia | Fuente |\n|---|---|---|---|---|")
    for c in cr:
        print(f"| {c['file']} | {c.get('title')} | {c.get('creator')} | {c['license']} | {c.get('source')} |")
    authors = sorted({c.get("creator") for c in cr if c.get("creator") and c["license"] not in ("CC0", "PDM")})
    if authors:
        print(f"\nPara la descripción: «Imágenes: {', '.join(authors)} (Creative Commons)»")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("search")
    p.add_argument("query")
    p.add_argument("outdir")
    p.add_argument("--n", type=int, default=20)
    p.add_argument("--license", default="commercial,modification")
    p = sp.add_parser("get")
    p.add_argument("cand")
    p.add_argument("idx", type=int, nargs="+")
    p.add_argument("--out", required=True)
    p.add_argument("--name", required=True)
    p = sp.add_parser("credits")
    p.add_argument("path")
    a = ap.parse_args()
    {"search": cmd_search, "get": cmd_get, "credits": cmd_credits}[a.cmd](a)


if __name__ == "__main__":
    main()
