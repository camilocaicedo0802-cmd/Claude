"""Recorta el fondo con BiRefNet (ONNX) y aplica el tratamiento monocromo de estilo.md.
Uso: python3 cutout.py entrada.jpg salida.png [--keep-bg]"""
import sys, numpy as np, onnxruntime as ort
from PIL import Image, ImageOps, ImageFilter

MODEL = "/home/user/models/birefnet.onnx"
_sess = None

def mask_for(img):
    global _sess
    if _sess is None:
        so = ort.SessionOptions(); so.intra_op_num_threads = 4
        _sess = ort.InferenceSession(MODEL, so, providers=["CPUExecutionProvider"])
    x = np.asarray(img.convert("RGB").resize((1024, 1024), Image.BILINEAR), dtype=np.float32) / 255.0
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    y = _sess.run(None, {"input_image": x})[0][0, 0]
    if y.min() < 0 or y.max() > 1:
        y = 1 / (1 + np.exp(-y))
    m = Image.fromarray((np.clip(y, 0, 1) * 255).astype(np.uint8)).resize(img.size, Image.BICUBIC)
    return m

def mono(img, cutoff=0.5, gamma=1.0):
    g = ImageOps.grayscale(img.convert("RGB"))
    g = ImageOps.autocontrast(g, cutoff=cutoff)
    if gamma != 1.0:
        lut = [int(255 * ((i / 255) ** gamma)) for i in range(256)]
        g = g.point(lut)
    return g

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    gamma = float(next((a.split("=")[1] for a in sys.argv if a.startswith("--gamma=")), "1.0"))
    img = Image.open(src); img = ImageOps.exif_transpose(img)
    m = mask_for(img)
    g = mono(img, gamma=gamma)
    # limpia halo: endurece levemente la máscara
    ma = np.asarray(m).astype(np.float32) / 255
    ma = np.clip((ma - 0.08) / 0.84, 0, 1)
    out = Image.merge("RGBA", (g, g, g, Image.fromarray((ma * 255).astype(np.uint8))))
    bbox = out.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if bbox:
        pad = 8
        bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(out.width, bbox[2] + pad), min(out.height, bbox[3] + pad))
        out = out.crop(bbox)
    out.save(dst, optimize=True)
    print(dst, out.size)
