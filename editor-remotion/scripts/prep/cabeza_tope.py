"""Borde superior de la cabeza en cada recorte con transparencia (public/media/fg/*.webm).

La opción B (formato horizontal) hace que la cabeza sobresalga por encima de la ventana una cantidad fija;
para eso necesita saber, fotograma a fotograma, a qué altura del plano original está la coronilla.
Salida: src/data/cabeza.json → { toma: [[t_local, y (0–1 de la altura del plano)], …] }
"""
import json
import subprocess

import numpy as np

FG = json.load(open("src/data/fg.json"))
CARAS = json.load(open("src/data/caras.json"))
SRC_W, SRC_H = 3840, 2160
OUT_W = 320


def alpha_frames(path, w, h):
    oh = int(round(h * OUT_W / w / 2) * 2)
    cmd = ["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", path, "-vf", f"alphaextract,scale={OUT_W}:{oh}", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, oh, OUT_W), oh


def face_x(track, t, default):
    if not track:
        return default
    ts = [k[0] for k in track]
    return float(np.interp(t, ts, [k[1] for k in track]))


out = {}
for seg_id, fg in FG.items():
    frames, oh = alpha_frames("public/" + fg["file"], fg["w"], fg["h"])
    cara = CARAS[seg_id]
    fps = 24.0
    ys = []
    for i, a in enumerate(frames):
        t = fg["from_"] + i / fps
        # Solo se mira una franja alrededor de la cara, para que una mano levantada no cuente como cabeza.
        cx = (face_x(cara.get("track"), t, cara["cx"]) * SRC_W - fg["x"]) / fg["w"] * OUT_W
        half = cara["w"] * SRC_W / fg["w"] * OUT_W * 0.42
        band = a[:, max(0, int(cx - half)) : min(OUT_W, int(cx + half))]
        rows = np.where((band > 110).sum(axis=1) >= 3)[0]
        y = rows[0] if len(rows) else np.nan
        ys.append((fg["y"] + y / oh * fg["h"]) / SRC_H)
    ys = np.array(ys, float)
    idx = np.arange(len(ys))
    ok = ~np.isnan(ys)
    ys = np.interp(idx, idx[ok], ys[ok])
    # Mediana de 5 + media móvil de ≈0,5 s: movimiento de cámara suave, sin temblor.
    pad = np.pad(ys, 2, mode="edge")
    ys = np.array([np.median(pad[i : i + 5]) for i in range(len(ys))])
    k = 13
    pad = np.pad(ys, k // 2, mode="edge")
    ys = np.convolve(pad, np.ones(k) / k, mode="valid")
    step = 3  # una clave cada 0,125 s
    out[seg_id] = [[round(fg["from_"] + i / fps, 3), round(float(ys[i]), 4)] for i in list(range(0, len(ys), step)) + [len(ys) - 1]]
    print(seg_id, len(frames), "fotogramas · coronilla y =", round(float(ys.min()), 3), "–", round(float(ys.max()), 3), "· cara y =", cara["cy"])

json.dump(out, open("src/data/cabeza.json", "w"), indent=1)
