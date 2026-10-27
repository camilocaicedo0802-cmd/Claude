"""Genera el ranking preliminar de videos por canal (Markdown) a partir de datos/videos.csv.

Uso: python3 ranking_videos.py datos/videos.csv > 03-ranking-videos.md
Categorías: absolutos (más vistas), relativos (múltiplo sobre la mediana de los 10 videos vecinos),
recientes (vistas por día, publicados hace 60 días o menos).
"""
import csv, sys

NAMES = {'ThePaintExplainer': 'The Paint Explainer', 'SimplePaintOfficial': 'Simple Paint', 'TeloPintoFacil': 'Te Lo Pinto Fácil',
         'SomeGuyWhoKnowsStuff': 'Some Guy Who Knows Stuff', 'thecrookedexplainer': 'The Crooked Explainer',
         'estrictamente': 'Estrictamente', 'lichsungoaitruyen': 'Lịch Sử Ngoại Truyện', 'SquireExplains': 'Squire Explains'}
ORDER = list(NAMES)
rows = list(csv.DictReader(open(sys.argv[1])))
for r in rows:
    r['views'] = int(r['views']); r['mult'] = float(r['multiple'] or 0); r['vpd'] = int(r['views_per_day'] or 0)
    r['age'] = int(r['age_days']) if r['age_days'] else None

def mmss(s):
    s = int(float(s or 0)); return f"{s // 60}:{s % 60:02d}"

def fmt(n): return f"{n:,}".replace(',', '.')

def table(sel, cols):
    out = ["| # | Título | Fecha | Duración | Vistas | Mediana vecinos | Múltiplo | Vistas/día |", "|---|---|---|---|---|---|---|---|"]
    for k, r in enumerate(sel, 1):
        date = r['date'] + ('' if r['date_src'] in ('vidiq', 'yt-dlp') else ' (aprox.)')
        views = fmt(r['views']) + ('' if r['views_src'] in ('vidiq', 'yt-dlp') else ' (redondeado)')
        title = r['title'].replace('|', '/')
        if r['title_en']: title += f" <br>_EN: {r['title_en'].replace('|', '/')}_"
        out.append(f"| {k} | [{title}]({r['url']}) | {date} | {mmss(r['duration'])} | {views} | {fmt(int(r['neigh_median']))} | ×{str(r['mult']).replace('.', ',')} | {fmt(r['vpd'])} |")
    return "\n".join(out)

print("# Ranking preliminar de videos por canal\n")
print("Generado desde `datos/videos.csv` (consulta del 27-oct-2026). **Múltiplo** = vistas del video ÷ mediana de los 10 videos "
      "publicados alrededor (5 antes y 5 después) en el mismo formato. Es un indicador de rendimiento relativo, no de CTR ni retención, "
      "que son privados. \"(aprox.)\" = fecha deducida de \"hace X meses\"; \"(redondeado)\" = vistas de la lista pública (±15 % en la muestra verificada).\n")
for h in ORDER:
    for tab, label in (('long', 'videos largos'), ('short', 'Shorts')):
        L = [r for r in rows if r['handle'] == h and r['tab'] == tab and r['views'] > 0]
        if len(L) < 4: continue
        print(f"\n## {NAMES[h]} — {label} ({len(L)} analizados)\n")
        print("### Éxitos absolutos\n"); print(table(sorted(L, key=lambda r: -r['views'])[:5], None))
        print("\n### Éxitos relativos\n"); print(table(sorted(L, key=lambda r: -r['mult'])[:5], None))
        rec = [r for r in L if r['age'] is not None and r['age'] <= 60]
        if rec:
            print("\n### Éxitos recientes (≤ 60 días, por vistas/día)\n"); print(table(sorted(rec, key=lambda r: -r['vpd'])[:3], None))
        low = [r for r in L if r['date_src'] in ('vidiq', 'yt-dlp')]
        if low:
            print("\n### Contraste: peor rendimiento relativo con datos exactos\n"); print(table(sorted(low, key=lambda r: r['mult'])[:3], None))
