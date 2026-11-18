"""Genera entrega/creditos_completos.txt a partir de work/used.json y de los registros de cada fuente.
Cabe en un comentario fijado de YouTube (límite 10.000 caracteres): los autores de Unsplash van en una sola línea.

usage (desde la carpeta del proyecto): python tools/creditos.py "NOMBRE DEL EPISODIO" "Línea de música" ["línea extra" …]
ej.: python tools/creditos.py "ATLANTIC AVENUE" "Banda sonora original compuesta y sintetizada para este video." \
       "  · Calles y límites de los distritos: NYC Open Data" "Los planos y el permiso que aparecen en pantalla son recreaciones ilustrativas."
Las líneas extra se añaden al final (datos de mapas propios del episodio, aviso de recreaciones…).
"""
import collections, json, os, sys

titulo, musica = sys.argv[1], sys.argv[2]
used = json.load(open("work/used.json"))
load = lambda p: json.load(open(p)) if os.path.exists(p) else {}
U = {r["id"]: r for r in (json.load(open("work/unsplash.json")) if os.path.exists("work/unsplash.json") else [])}
F, L, FI = load("work/flickr.json"), load("work/loc.json"), load("work/films.json")
uid = lambda f: f[2:-4]
out = [f"CRÉDITOS COMPLETOS — {titulo}", "=" * 40, "", "MÚSICA — " + musica]
by = collections.defaultdict(list)
for f in used["imgs"]:
    if f.startswith("f_") and uid(f) in F:
        r = F[uid(f)]
        by[(r["author"], r["alias"], r["license"])].append(r)
if by:
    out += ["", "FOTOGRAFÍAS DE FLICKR"]
    for (a, alias, lic), rs in sorted(by.items(), key=lambda x: -len(x[1])):
        titles = sorted({r["title"] or "sin título" for r in rs})
        out.append(f"  · {a} — «{' / '.join(titles)[:90]}» — {lic} — https://www.flickr.com/photos/{alias}/ (fotos {', '.join(r['id'] for r in rs)})")
loc = [f for f in used["imgs"] if f.startswith("l_")]
if loc:
    out += ["", "LIBRARY OF CONGRESS — Prints & Photographs Division (dominio público / sin restricciones conocidas)"]
    fsa = [f for f in loc if ":fsa" in L[uid(f).replace("_L", "")].get("svc", "")]
    if fsa:
        out.append("  · Farm Security Administration / Office of War Information, 1939–1942 (" + str(len(fsa)) +
                   " fotos: " + ", ".join(uid(f) for f in fsa) + ") — https://www.loc.gov/pictures/collection/fsa/")
    seen = set()
    for f in loc:
        if f in fsa:
            continue
        r = L[uid(f).replace("_L", "")]
        if r["url"] in seen:
            continue
        seen.add(r["url"])
        d = f" ({str(r.get('date'))[:4]})" if r.get("date") else ""
        svc = r.get("svc", "")
        tag = (" — Carol M. Highsmith Archive" if ":highsm:" in svc else " — HABS/HAER (Servicio de Parques Nacionales)" if "habshaer" in svc else
               " — Farm Security Administration / Office of War Information" if ":fsa" in svc else
               " — estereografía" if ":stereo:" in svc else "")
        t = r["title"] if len(r["title"]) <= 95 else r["title"][:92].rstrip() + "…"
        out.append(f"  · «{t}»{d}{tag} — {r['url']}")
MK = load("work/mixkit.json")
films = [v for v in used.get("vids", []) if not v.startswith("mk_")]
if films:
    out += ["", "PELÍCULAS DE DOMINIO PÚBLICO (Internet Archive)"]
    for v in films:
        r = FI[v[3:-4]]
        out.append(f"  · «{r['title']}» ({r.get('year') or 's. f.'}) — {r['license']} — {r['src']}")
clips = [v for v in used.get("vids", []) if v.startswith("mk_")]
if clips:
    out += ["", "CLIPS DE VIDEO — Mixkit (Mixkit Stock Video Free License: https://mixkit.co/license/#videoFree)"]
    out.append("  · " + "; ".join((MK[v[3:-4]].get("title") or "").replace(" - Free Stock Video", "").strip() + f" (#{v[3:-4]})" for v in clips) + ".")
names = sorted({(U[uid(f)]["author"] or U[uid(f)]["username"]) for f in used["imgs"] if f.startswith("u_") and uid(f) in U}, key=str.lower)
if names:
    out += ["", "FOTOGRAFÍAS DE UNSPLASH (licencia Unsplash: https://unsplash.com/license)", "  " + ", ".join(names) + "."]
out += ["", "MAPAS Y DATOS", "  · Relieve: Mapzen / Tilezen Terrain Tiles (Amazon Open Data) — datos SRTM, USGS y otros",
        "  · Ríos, lagos, costas y límites: Natural Earth (dominio público)",
        "", "GRÁFICOS, ANIMACIONES Y EFECTOS DE SONIDO: creación propia."] + sys.argv[3:]
txt = "\n".join(out) + "\n"
os.makedirs("entrega", exist_ok=True)
open("entrega/creditos_completos.txt", "w").write(txt)
print(len(txt), "caracteres", "(OK)" if len(txt) <= 10000 else "(PASA DEL LÍMITE DE 10.000: acortar)")
