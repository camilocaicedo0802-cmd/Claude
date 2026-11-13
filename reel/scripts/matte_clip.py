"""Recorta a la persona de un clip con BiRefNet (modelo ONNX de rembg) en CPU y guarda PNG RGBA por fotograma.
Se usa para poner texto DETRÁS de la persona: b-roll -> texto -> persona recortada.

Sesión de onnxruntime propia, sin arena de memoria: con la sesión por defecto el uso de RAM crece entre
fotogramas hasta que el sistema mata el proceso.
Uso: python3 -I matte_clip.py <video_proxy.mp4> <carpeta_salida> <fotograma_inicial> <fotograma_final>
(el modelo se descarga la primera vez con: python3 -c "from rembg import new_session; new_session('birefnet-general')")
"""
import gc
import os
import subprocess
import sys
import time

import numpy as np
import onnxruntime as ort
from PIL import Image

src, out, f0, f1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
MODEL = os.path.expanduser("~/.rembg/models/birefnet-general/birefnet-general.onnx")
os.makedirs(out, exist_ok=True)
W, H, S = 1080, 1920, 1024

opts = ort.SessionOptions()
opts.enable_cpu_mem_arena = False
opts.enable_mem_pattern = False
opts.intra_op_num_threads = 4
sess = ort.InferenceSession(MODEL, sess_options=opts, providers=["CPUExecutionProvider"])
mean = np.array([0.485, 0.456, 0.406], np.float32)
std = np.array([0.229, 0.224, 0.225], np.float32)

for n in range(f0, f1 + 1):
    dst = f"{out}/{n:04d}.png"
    if os.path.exists(dst):
        continue
    t = time.time()
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"select='eq(n\\,{n})'", "-vsync", "0",
                          "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
    x = np.asarray(Image.fromarray(fr).resize((S, S), Image.BILINEAR), np.float32) / 255.0
    x = ((x - mean) / std).transpose(2, 0, 1)[None]
    pred = sess.run(None, {"input_image": x})[0][0, 0]
    pred = 1 / (1 + np.exp(-pred))
    pred = (pred - pred.min()) / (pred.max() - pred.min() + 1e-8)
    alpha = np.asarray(Image.fromarray((pred * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS))
    Image.fromarray(np.dstack([fr, alpha]), "RGBA").save(dst, optimize=True)
    del x, pred, alpha, fr
    gc.collect()
    print(f"{n}: {time.time() - t:.1f}s", flush=True)
