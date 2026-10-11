#!/usr/bin/env python3
"""
Control de fidelidad: compara el vídeo generado con la referencia en las mismas métricas de edición.

  python3 compare.py referencia.mp4 render/borrador.mp4 qa/

Produce qa/comparacion.md (tabla referencia vs borrador con alertas) y qa/lado_a_lado.jpg
(fotogramas a la misma posición relativa: referencia arriba, borrador abajo).
Las métricas de ritmo se comparan por proporción (cortes/min, mediana de plano), no por tiempo absoluto,
porque el vídeo nuevo dura lo que dure su locución.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_reference import camera_motion, color_stats, detect_cuts, grain_and_vignette, loudness, probe, read_frames, shots_from_cuts, zoom_samples  # noqa: E402


def metrics(path):
    info = probe(path)
    gray = read_frames(path, 128)
    fps = len(gray) / info["duration"]
    cuts, soft, _, pd = detect_cuts(gray, fps)
    shots = shots_from_cuts(cuts, info["duration"])
    g192 = read_frames(path, 192)
    pans, _ = camera_motion(g192, len(g192) / info["duration"], 1080 / 192)
    zs = [z for _, z in zoom_samples(read_frames(path, 160), len(g192) / info["duration"], every=0.5)]
    rgb = read_frames(path, 96, fps=4, gray=False)
    col = color_stats(rgb)
    full = read_frames(path, 540, fps=1, gray=False)
    gv = [grain_and_vignette(f) for f in full[:12]]
    durs = np.array([s["dur"] for s in shots])
    themes = [color_stats(rgb[int(s["start"] * 4): max(int(s["start"] * 4) + 1, int(s["end"] * 4))])["tema"] for s in shots]
    m = {
        "duracion_s": round(info["duration"], 2),
        "formato": f"{info['width']}x{info['height']} @{info['fps']}",
        "cortes_por_min": round(60 * len(cuts) / info["duration"], 1),
        "transiciones_suaves_por_min": round(60 * len(soft) / info["duration"], 1),
        "plano_mediana_s": round(float(np.median(durs)), 2),
        "tiempo_con_cambio_%": round(100 * float((pd > 0.004).mean()), 1),
        "camara_vel_mediana_px_s": round(float(np.median(np.hypot(pans[:, 0], pans[:, 1]))), 1),
        "zoom_medio_abs_por_s": round(float(np.mean(np.abs(zs))), 4) if zs else 0.0,
        "luminancia": col["luminancia_media"],
        "saturacion": col["saturacion_media"],
        "monocromo": col["monocromo"],
        "alternancias_claro_oscuro_por_min": round(60 * sum(1 for a, b in zip(themes, themes[1:]) if a != b) / info["duration"], 1),
        "grano": float(np.median([g for g, _ in gv])),
        "vineta": float(np.median([v for _, v in gv])),
        "paleta": " ".join(p["hex"] for p in col["paleta"][:5]),
    }
    if info["has_audio"]:
        m.update({k: v for k, v in loudness(path).items()})
    return m


def side_by_side(ref, out, dst, n=10):
    ir, io = probe(ref), probe(out)
    tw = 150
    th_r = int(tw * ir["height"] / ir["width"])
    th_o = int(tw * io["height"] / io["width"])
    S = Image.new("RGB", (n * tw, th_r + th_o + 40), "white")
    d = ImageDraw.Draw(S)
    for k in range(n):
        p = (k + 0.5) / n
        for row, (path, info, th, y) in enumerate([(ref, ir, th_r, 20), (out, io, th_o, th_r + 40)]):
            tmp = f"/tmp/_cmp_{row}_{k}.jpg"
            os.system(f'ffmpeg -v error -y -ss {p * info["duration"]:.2f} -i "{path}" -frames:v 1 -q:v 3 {tmp}')
            if os.path.exists(tmp):
                S.paste(Image.open(tmp).convert("RGB").resize((tw, th)), (k * tw, y))
    d.text((4, 4), "REFERENCIA", fill="red")
    d.text((4, th_r + 24), "BORRADOR", fill="blue")
    S.save(dst, quality=85)


def main():
    ref, out, qa = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(qa, exist_ok=True)
    mr, mo = metrics(ref), metrics(out)
    L = ["# Comparación referencia vs borrador\n", "| métrica | referencia | borrador | nota |", "|---|---|---|---|"]
    # umbrales: diferencias absolutas para dB, relativas (>50 %) con suelo mínimo para el resto
    ABS = {"lufs_integrado": 3.0, "pico_real_dbfs": 1.5, "lra": 4.0, "luminancia": 0.15, "saturacion": 0.08, "vineta": 0.08}
    FLOOR = {"cortes_por_min": 5, "transiciones_suaves_por_min": 3, "plano_mediana_s": 0.5, "tiempo_con_cambio_%": 15, "camara_vel_mediana_px_s": 15, "zoom_medio_abs_por_s": 0.02, "alternancias_claro_oscuro_por_min": 3, "grano": 2}
    for k in mr:
        a, b = mr[k], mo.get(k)
        note = ""
        if isinstance(a, bool) or isinstance(b, bool):
            note = "⚠ distinto" if a != b else ""
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and k != "duracion_s":
            if k in ABS:
                note = f"⚠ Δ {b - a:+.2f}" if abs(b - a) > ABS[k] else ""
            elif max(abs(a), abs(b)) > FLOOR.get(k, 0) and abs(b - a) / (max(abs(a), abs(b)) + 1e-9) > 0.5:
                note = f"⚠ ×{(b / a) if a else float('inf'):.2f}"
        L.append(f"| {k} | {a} | {b} | {note} |")
    L.append("\nRevisa cada ⚠: o se justifica por el contenido nuevo, o es una desviación de estilo a corregir.")
    open(os.path.join(qa, "comparacion.md"), "w").write("\n".join(L) + "\n")
    side_by_side(ref, out, os.path.join(qa, "lado_a_lado.jpg"))
    print("\n".join(L))
    print(f"\nHoja: {os.path.join(qa, 'lado_a_lado.jpg')}")


if __name__ == "__main__":
    main()
