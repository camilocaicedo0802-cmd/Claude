#!/usr/bin/env python3
"""Etiqueta real sobre una imagen fija, al doble de resolución (borra la zona y pega la etiqueta de la landing).
uso: fix_still.py entrada.png salida.png [--flip]   -> imprime la caja del producto (x0,y0,x1,y1) en la salida"""
import sys, cv2, numpy as np
G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
sys.argv, args = sys.argv[:1], sys.argv[1:]
sys.path.insert(0, G)
import label_fix as F
src, dst = args[0], args[1]
im = cv2.imread(src)
q = F.sift_quad(im)
if q is None:
    sys.exit('sin detección de la etiqueta')
big = cv2.resize(im, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
F.WIPE = True; F.TUBE = True; F.FLIP = '--flip' in args
out = F.composite(big.copy(), q * 2, 1.0)
cv2.imwrite(dst, out)
x, y, w, h = cv2.boundingRect((q * 2).astype(np.int32))
print(f'{dst} {out.shape[1]}x{out.shape[0]} etiqueta {x},{y},{x+w},{y+h}')
