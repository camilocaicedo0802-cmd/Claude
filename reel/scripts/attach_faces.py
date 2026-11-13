"""Añade a cada segmento del EDL la posición mediana de la cara (para encuadrar punch-ins).
Uso: python3 attach_faces.py <faces_raw.json> <edl.json>
"""
import json, sys
import numpy as np
F = [f for f in json.load(open(sys.argv[1])) if f["x"] is not None]
E = json.load(open(sys.argv[2]))
for s in E["segments"]:
    c = [f for f in F if s["srcIn"] - 0.2 <= f["t"] <= s["srcOut"] + 0.2]
    if not c:
        c = sorted(F, key=lambda f: abs(f["t"] - (s["srcIn"] + s["srcOut"]) / 2))[:5]
    xs, ys, ss = (np.array([f[k] for f in c]) for k in ("x", "y", "s"))
    keep = (abs(xs - np.median(xs)) < 0.12) & (abs(ys - np.median(ys)) < 0.12)
    if not keep.any():
        keep = np.ones_like(xs, dtype=bool)
    vals = [float(np.median(a[keep])) for a in (xs, ys, ss)]
    if any(np.isnan(v) for v in vals):  # sin detecciones fiables: centro del plano sentado
        vals = [0.62, 0.51, 0.09]
    s["faceX"], s["faceY"], s["faceS"] = (round(v, 3) for v in vals)
json.dump(E, open(sys.argv[2], "w"), indent=1)
print("caras añadidas a", len(E["segments"]), "segmentos")
