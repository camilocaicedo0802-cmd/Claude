#!/usr/bin/env python3
"""Genera 8 texturas de grano (gris medio ± ruido) a media resolución para el componente <Grain>.
Uso: python3 make_grain.py public/fx [ancho alto] [sigma]"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

out = sys.argv[1] if len(sys.argv) > 1 else "public/fx"
w = int(sys.argv[2]) // 2 if len(sys.argv) > 2 else 540
h = int(sys.argv[3]) // 2 if len(sys.argv) > 3 else 960
sigma = float(sys.argv[4]) if len(sys.argv) > 4 else 46
os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(11)
for i in range(8):
    n = rng.normal(128, sigma, (h, w)).clip(0, 255).astype(np.uint8)
    Image.fromarray(n, "L").filter(ImageFilter.GaussianBlur(0.45)).save(os.path.join(out, f"grain_{i}.png"), optimize=True)
print(out)
