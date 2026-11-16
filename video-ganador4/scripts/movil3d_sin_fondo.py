# Móvil 3D del cliente: fondo blanco fuera por fotograma (rembg isnet), color original, huecos rellenos (pieza maciza).
import subprocess, numpy as np, cv2, sys
from PIL import Image
from rembg import new_session, remove
s = new_session('isnet-general-use')
W, H = 1280, 960
raw = subprocess.run(['ffmpeg','-v','error','-i','/root/.claude/uploads/8ca66ad8-679a-5f1d-a671-bedcf5aab479/496d9d26-Celular_3d.mp4','-f','rawvideo','-pix_fmt','rgb24','-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
boxes = []
for i, f in enumerate(fr):
    al = np.array(remove(Image.fromarray(f), session=s, only_mask=True))
    m = (al > 128).astype(np.uint8)
    inv = 1 - m; k, lab, st, _ = cv2.connectedComponentsWithStats(inv, 4)
    for j in range(1, k):
        x, y, w, h, area = st[j]
        if x > 0 and y > 0 and x + w < W and y + h < H: m[lab == j] = 1
    # sin islas
    k, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if k > 1:
        big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); keep = (lab == big).astype(np.uint8)
        al = np.where(cv2.dilate(keep, np.ones((5,5),np.uint8)) > 0, al, 0)
    al = np.maximum(al, cv2.erode(m, np.ones((5,5),np.uint8)) * 255).astype(np.uint8)
    Image.fromarray(np.dstack([f, al])).save(f'/home/user/Claude/video-ganador4/public/cel3d/f_{i:03d}.png', optimize=True)
    ys, xs = np.where(al > 20); boxes.append((xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None)
    if i % 50 == 0: print(i, flush=True)
b = np.array([x for x in boxes if x is not None]); print('union bbox', b[:,0].min(), b[:,1].min(), b[:,2].max(), b[:,3].max(), 'n', len(fr))
print('CEL_DONE')
