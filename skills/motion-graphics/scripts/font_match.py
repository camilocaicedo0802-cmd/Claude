#!/usr/bin/env python3
"""
Compara un recorte de texto de la referencia con tipografías candidatas de Google Fonts.

  python3 font_match.py --crop recorte.png --text "creatividad" --category grotesk-heavy --out fuentes.png
  python3 font_match.py --crop recorte.png --text "aprendiste algo" --families "Parisienne,Great Vibes,Allura" --out f.png
  python3 font_match.py --list            # ver categorías

Descarga los TTF (API CSS de Google Fonts) a ~/.cache/motion-graphics/fonts y genera una hoja:
el recorte original arriba y debajo la misma palabra en cada candidata, a una altura similar.
Elige la que más se parezca en forma de letras (a, g, t, y, R), contraste del trazo, anchura y espaciado.
Luego descarga la fuente para Remotion con:  python3 font_match.py --download "Archivo:800" --dest video/public/fonts
"""
import argparse
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "motion-graphics", "fonts")
CATEGORIES = {
    "grotesk-heavy": ["Archivo:800", "Archivo:900", "Inter:900", "Inter Tight:900", "Roboto:900", "Work Sans:900", "Public Sans:900", "Figtree:900", "Schibsted Grotesk:900", "Archivo Black:400", "Manrope:800", "Plus Jakarta Sans:800"],
    "grotesk": ["Inter:600", "Roboto:500", "Archivo:600", "Work Sans:600", "DM Sans:600", "Figtree:600", "Manrope:600", "IBM Plex Sans:600", "Helvetica-like: Arimo:700", "Instrument Sans:600"],
    "geometric": ["Montserrat:800", "Poppins:700", "Poppins:800", "Outfit:700", "Urbanist:800", "Sora:700", "Lexend:700", "Kumbh Sans:800", "Red Hat Display:800", "Gilroy-like: Plus Jakarta Sans:800"],
    "condensed": ["Bebas Neue:400", "Anton:400", "Oswald:700", "League Gothic:400", "Barlow Condensed:800", "Archivo Narrow:700", "Big Shoulders Display:800", "Antonio:700", "Fjalla One:400", "Teko:600"],
    "rounded": ["Nunito:900", "Quicksand:700", "Varela Round:400", "M PLUS Rounded 1c:800", "Baloo 2:800", "Fredoka:600", "Comfortaa:700"],
    "serif-display": ["Playfair Display:800", "DM Serif Display:400", "Bodoni Moda:700", "Cormorant Garamond:700", "Libre Caslon Display:400", "Abril Fatface:400", "Prata:400", "Fraunces:800", "Instrument Serif:400", "Gloock:400"],
    "serif-text": ["Lora:600", "Merriweather:700", "EB Garamond:600", "Source Serif 4:700", "Crimson Pro:700", "Libre Baskerville:700"],
    "script": ["Parisienne:400", "Great Vibes:400", "Allura:400", "Alex Brush:400", "Pinyon Script:400", "Italianno:400", "Arizonia:400", "Rouge Script:400", "Sacramento:400", "Monsieur La Doulaise:400", "Mrs Saint Delafield:400", "Ephesis:400", "Birthstone:400", "Tangerine:400"],
    "handwriting": ["Caveat:700", "Kalam:700", "Patrick Hand:400", "Gochi Hand:400", "Shadows Into Light:400", "Permanent Marker:400", "Rock Salt:400", "Reenie Beanie:400", "Indie Flower:400", "Nanum Pen Script:400"],
    "brush-marker": ["Permanent Marker:400", "Marck Script:400", "Kaushan Script:400", "Yellowtail:400", "Satisfy:400", "Dancing Script:700", "Pacifico:400", "Lobster:400", "Courgette:400"],
    "mono": ["JetBrains Mono:700", "Space Mono:700", "IBM Plex Mono:600", "Roboto Mono:700", "DM Mono:500", "Courier Prime:700"],
    "impact-meme": ["Anton:400", "Oswald:700", "Bebas Neue:400", "Archivo Black:400", "Rubik:900", "Titan One:400", "Luckiest Guy:400", "Bangers:400"],
}


def parse(spec):
    spec = spec.split(": ")[-1]
    fam, _, w = spec.partition(":")
    return fam.strip(), int(w or 400)


def fetch(family, weight):
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, f"{family.replace(' ', '_')}-{weight}.ttf")
    if os.path.exists(fn):
        return fn
    url = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}:wght@{weight}"
    css = subprocess.run(["curl", "-sS", url], capture_output=True, text=True).stdout
    if "src:" not in css:
        css = subprocess.run(["curl", "-sS", f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}"], capture_output=True, text=True).stdout
    m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css)
    if not m:
        return None
    subprocess.run(["curl", "-sS", "-o", fn, m.group(1)], check=False)
    return fn if os.path.exists(fn) and os.path.getsize(fn) > 1000 else None


def render(fontfile, text, height, color=(20, 20, 20), bg=(235, 235, 235)):
    size = height
    for _ in range(6):
        f = ImageFont.truetype(fontfile, size)
        x0, y0, x1, y1 = f.getbbox(text)
        if y1 - y0 <= 0:
            break
        size = max(8, int(size * height / (y1 - y0)))
    f = ImageFont.truetype(fontfile, size)
    x0, y0, x1, y1 = f.getbbox(text)
    im = Image.new("RGB", (x1 - x0 + 20, y1 - y0 + 20), bg)
    ImageDraw.Draw(im).text((10 - x0, 10 - y0), text, font=f, fill=color)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crop")
    ap.add_argument("--text")
    ap.add_argument("--category", default=None)
    ap.add_argument("--families", default=None, help="lista 'Familia:peso,Familia:peso'")
    ap.add_argument("--out", default="fuentes.png")
    ap.add_argument("--dark", action="store_true", help="texto claro sobre fondo oscuro")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--download", default=None, help="'Familia:peso' a descargar como TTF")
    ap.add_argument("--dest", default=".")
    a = ap.parse_args()
    if a.list:
        for k, v in CATEGORIES.items():
            print(f"{k:14s} {', '.join(v)}")
        return
    if a.download:
        fam, w = parse(a.download)
        f = fetch(fam, w)
        if not f:
            sys.exit("No se encontró en Google Fonts")
        os.makedirs(a.dest, exist_ok=True)
        dst = os.path.join(a.dest, os.path.basename(f))
        open(dst, "wb").write(open(f, "rb").read())
        print(dst)
        return
    cands = [parse(s) for s in (a.families.split(",") if a.families else CATEGORIES[a.category])]
    crop = Image.open(a.crop).convert("RGB")
    target_h = max(40, min(160, crop.height))
    if crop.height != target_h:
        crop = crop.resize((int(crop.width * target_h / crop.height), target_h))
    rows = [("REFERENCIA", crop)]
    fg, bg = ((240, 240, 240), (20, 20, 20)) if a.dark else ((20, 20, 20), (235, 235, 235))
    for fam, w in cands:
        f = fetch(fam, w)
        if not f:
            print(f"  (no disponible) {fam}:{w}", file=sys.stderr)
            continue
        try:
            rows.append((f"{fam} {w}", render(f, a.text, int(target_h * 0.8), fg, bg)))
        except Exception as e:  # noqa: BLE001
            print(f"  (error) {fam}: {e}", file=sys.stderr)
    W = max(r[1].width for r in rows) + 260
    H = sum(r[1].height + 10 for r in rows)
    S = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(S)
    y = 0
    for label, im in rows:
        S.paste(im, (0, y))
        d.text((im.width + 12, y + im.height // 2 - 6), label, fill="red")
        y += im.height + 10
    S.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
