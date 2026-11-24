#!/usr/bin/env python3
"""Clip del host: desde que el stick queda quieto en la mesa, se borra la etiqueta inventada por la IA
(franja celeste) y se pega la etiqueta real con las proporciones del producto, siguiendo el leve desplazamiento."""
import sys, subprocess, numpy as np, cv2
G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
sys.argv = sys.argv[:1]; sys.path.insert(0, G)
import label_fix as F
src, dst = f'{G}/hf/orig/w_host_0.mp4', f'{G}/hf/fixed/w_host_0.mp4'
frames, fps, w, h = F.read_frames(src)
num, den = map(int, fps.split('/')); fr = num / den
i_ref = int(round(16.5 * fr)); i0 = int(round(float(sys.argv[1]) * fr)) if len(sys.argv) > 1 else int(round(15.0 * fr))
box = (390, 1060, 475, 1200)
gref = cv2.cvtColor(frames[i_ref][box[1]:box[3], box[0]:box[2]], cv2.COLOR_BGR2GRAY).astype(np.float32)
wipe = np.float32([[405, 1081], [457, 1081], [457, 1172], [405, 1172]])   # todo el cuerpo con texto de la IA
lab = np.float32([[403, 1085], [459, 1085], [459, 1139], [403, 1139]])     # etiqueta real (52 % del cuerpo, 94 % del ancho)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}', '-r', fps, '-i', '-',
                        '-i', src, '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14',
                        '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-shortest', dst], stdin=subprocess.PIPE)
sm = np.zeros(2)
def no_cyan(f):
    """Borra la franja celeste de la etiqueta inventada (asoma por el borde del stick en la mano)."""
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 0] > 75) & (hsv[..., 0] < 105) & (hsv[..., 1] > 40) & (hsv[..., 2] > 110)).astype(np.uint8)
    m[:600] = 0
    if m.sum() < 5:
        return f
    m = cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2) * 255
    return cv2.inpaint(f, m, 6, cv2.INPAINT_TELEA)

for i, f in enumerate(frames):
    if i < i0:
        f = no_cyan(f)
    if i >= i0:
        g = cv2.cvtColor(f[box[1]:box[3], box[0]:box[2]], cv2.COLOR_BGR2GRAY).astype(np.float32)
        (dx, dy), _ = cv2.phaseCorrelate(gref, g)
        sm = np.array([dx, dy]) if i == i0 else 0.7 * sm + 0.3 * np.array([dx, dy])
        o = np.float32(sm)
        F.BLANK, F.WIPE, F.TUBE = True, True, True
        f = F.composite(f.copy(), wipe + o, 1.0)          # 1) tubo limpio
        F.BLANK, F.WIPE = False, False
        f = F.composite(f, lab + o, 1.0)                  # 2) etiqueta real
    enc.stdin.write(np.ascontiguousarray(f).tobytes())
enc.stdin.close(); enc.wait(); print('ok', dst)
