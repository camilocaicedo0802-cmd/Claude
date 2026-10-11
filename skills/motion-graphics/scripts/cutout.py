#!/usr/bin/env python3
"""
Recorta el fondo de fotos con BiRefNet (ONNX, licencia MIT) y aplica el tratamiento de color de la referencia.

Uso:
  python3 cutout.py entrada.jpg salida.png                    # recorte a color
  python3 cutout.py entrada.jpg salida.png --mono             # escala de grises + autocontraste
  python3 cutout.py entrada.jpg salida.png --mono --gamma 0.9 --contrast 1.15
  python3 cutout.py carpeta_in/ carpeta_out/ --mono           # lote
  python3 cutout.py entrada.jpg salida.png --tint "#1E3A8A"   # duotono hacia un color de la paleta
  --lite  usa BiRefNet_lite (más rápido, algo menos fino)

El modelo se descarga una vez a ~/.cache/motion-graphics/ desde Hugging Face (onnx-community).
"""
import argparse
import os
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageEnhance, ImageOps

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "motion-graphics")
URLS = {
    "full": "https://huggingface.co/onnx-community/BiRefNet-ONNX/resolve/main/onnx/model.onnx",
    "lite": "https://huggingface.co/onnx-community/BiRefNet_lite-ONNX/resolve/main/onnx/model.onnx",
}
_sess = None


def model_path(lite):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, "birefnet_lite.onnx" if lite else "birefnet.onnx")
    if not os.path.exists(p):
        print(f"Descargando BiRefNet{' lite' if lite else ''} (~{220 if lite else 970} MB)…", file=sys.stderr)
        urllib.request.urlretrieve(URLS["lite" if lite else "full"], p + ".part")
        os.replace(p + ".part", p)
    return p


def mask_for(img, lite=False):
    global _sess
    import onnxruntime as ort

    if _sess is None:
        so = ort.SessionOptions()
        so.intra_op_num_threads = os.cpu_count() or 4
        _sess = ort.InferenceSession(model_path(lite), so, providers=["CPUExecutionProvider"])
    name = _sess.get_inputs()[0].name
    size = _sess.get_inputs()[0].shape[-1] if isinstance(_sess.get_inputs()[0].shape[-1], int) else 1024
    x = np.asarray(img.convert("RGB").resize((size, size), Image.BILINEAR), dtype=np.float32) / 255.0
    x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
    y = _sess.run(None, {name: x})[0][0, 0]
    if y.min() < 0 or y.max() > 1:
        y = 1 / (1 + np.exp(-y))
    return Image.fromarray((np.clip(y, 0, 1) * 255).astype(np.uint8)).resize(img.size, Image.BICUBIC)


def treat(img, a):
    rgb = img.convert("RGB")
    if a.mono or a.tint:
        g = ImageOps.autocontrast(ImageOps.grayscale(rgb), cutoff=0.5)
        if a.gamma != 1.0:
            g = g.point([int(255 * ((i / 255) ** a.gamma)) for i in range(256)])
        if a.tint:
            c = tuple(int(a.tint.lstrip("#")[i: i + 2], 16) for i in (0, 2, 4))
            rgb = ImageOps.colorize(g, black=c, white=(245, 245, 245))
        else:
            rgb = Image.merge("RGB", (g, g, g))
    if a.contrast != 1.0:
        rgb = ImageEnhance.Contrast(rgb).enhance(a.contrast)
    if a.saturation != 1.0:
        rgb = ImageEnhance.Color(rgb).enhance(a.saturation)
    return rgb


def process(src, dst, a):
    img = ImageOps.exif_transpose(Image.open(src))
    rgb = treat(img, a)
    if a.keep_bg:
        rgb.save(dst)
        print(dst, rgb.size)
        return
    m = np.asarray(mask_for(img, a.lite)).astype(np.float32) / 255
    m = np.clip((m - 0.08) / 0.84, 0, 1)  # endurece el borde y elimina halo
    out = rgb.convert("RGBA")
    out.putalpha(Image.fromarray((m * 255).astype(np.uint8)))
    bbox = out.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if bbox:
        p = 8
        out = out.crop((max(0, bbox[0] - p), max(0, bbox[1] - p), min(out.width, bbox[2] + p), min(out.height, bbox[3] + p)))
    out.save(dst, optimize=True)
    print(dst, out.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--mono", action="store_true")
    ap.add_argument("--tint", default=None, help="duotono: color hex para las sombras")
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--contrast", type=float, default=1.0)
    ap.add_argument("--saturation", type=float, default=1.0)
    ap.add_argument("--keep-bg", action="store_true", help="solo tratamiento de color, sin recortar")
    ap.add_argument("--lite", action="store_true")
    a = ap.parse_args()
    if os.path.isdir(a.src):
        os.makedirs(a.dst, exist_ok=True)
        for f in sorted(os.listdir(a.src)):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                process(os.path.join(a.src, f), os.path.join(a.dst, os.path.splitext(f)[0] + ".png"), a)
    else:
        process(a.src, a.dst, a)


if __name__ == "__main__":
    main()
