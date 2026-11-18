"""Lista las imágenes y películas que usa la edición (work/used.json) e imprime los tiempos de los capítulos.

usage (desde la carpeta edit/): python usados.py"""
import json, os, sys
sys.path.insert(0, ".")
import timeline
from gfx import BigText

shots = sorted(timeline.build(), key=lambda s: s.start)
imgs, vids = set(), set()


def walk(b):
    if hasattr(b, "path") and isinstance(getattr(b, "path"), str):
        (vids if type(b).__name__ == "Video" else imgs).add(os.path.basename(b.path))
    for k in ("bases", "parts"):
        for x in getattr(b, k, []) or []:
            walk(x[1] if isinstance(x, tuple) else x)


for s in shots:
    walk(s.base)
    for o in s.ov:
        if isinstance(o, BigText) and o.text.startswith("CAPÍTULO"):
            m, sec = divmod(int(s.start), 60)
            print("CAPÍTULO", f"{m}:{sec:02d}", [x.text for x in s.ov if isinstance(x, BigText)][1:2])
json.dump({"imgs": sorted(imgs), "vids": sorted(vids)}, open("../work/used.json", "w"))
print(len(imgs), "imágenes,", len(vids), "películas")
