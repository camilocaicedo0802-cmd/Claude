#!/usr/bin/env python3
"""Reemplaza la etiqueta generada por IA con la etiqueta REAL de la landing, cuadro a cuadro.
- Detección: SIFT entre la etiqueta real y el cuadro (el logo GEODA suele salir bien) -> homografía.
- Seguimiento: flujo óptico (LK) para los cuadros donde la detección falla o con un cuadrilátero inicial manual.
- Composición: etiqueta real con la luz/sombra del tubo original, borde suave, dedos (piel) por delante.
uso: label_fix.py entrada.mp4 salida.mp4 [--quad x0,y0,x1,y1,x2,y2,x3,y3 --qt t] [--roi x0,y0,x1,y1]
"""
import sys, os, subprocess, json, argparse
import numpy as np, cv2

G = '/tmp/claude-0/-home-user-Claude/89fb9332-1428-5876-823c-b89791e99771/scratchpad/geoda'
LAB = cv2.imread(f'{G}/labelfix/label_real.png')
LH, LW = LAB.shape[:2]
LCORN = np.float32([[0, 0], [LW, 0], [LW, LH], [0, LH]])
SIFT = cv2.SIFT_create(nfeatures=4000)
KL, DL = SIFT.detectAndCompute(cv2.cvtColor(LAB, cv2.COLOR_BGR2GRAY), None)
BF = cv2.BFMatcher()
LAB_WHITE = float(np.percentile(cv2.cvtColor(LAB, cv2.COLOR_BGR2GRAY), 90))
_l = cv2.cvtColor(LAB, cv2.COLOR_BGR2GRAY).astype(np.float32)
_sat = cv2.cvtColor(LAB, cv2.COLOR_BGR2HSV)[..., 1].astype(np.float32) / 255
LAB_A = np.clip(np.maximum((LAB_WHITE - 12 - _l) / (LAB_WHITE - 90), _sat * 2.2 - 0.25), 0, 1)   # 1 en letras/logo, 0 en el blanco
LAB_A = cv2.GaussianBlur(LAB_A, (0, 0), 0.6)
_e = 8  # el recorte de la foto trae sombra del tubo en los bordes: no se pinta
_ramp = np.clip(np.minimum.outer(np.minimum(np.arange(LH), np.arange(LH)[::-1]), np.minimum(np.arange(LW), np.arange(LW)[::-1])) / _e, 0, 1)
LAB_A = (LAB_A * _ramp).astype(np.float32)

def read_frames(path):
    w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height',
                                    '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip().split(','))
    fps = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', path],
                         capture_output=True, text=True).stdout.strip()
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    return [np.frombuffer(raw[i*w*h*3:(i+1)*w*h*3], np.uint8).reshape(h, w, 3).copy() for i in range(n)], fps, w, h

def valid_quad(q, w, h):
    q = q.reshape(4, 2)
    if not cv2.isContourConvex(q.astype(np.float32)):
        return False
    area = cv2.contourArea(q.astype(np.float32))
    if area < 30 * 30 or area > 0.35 * w * h:
        return False
    e = [np.linalg.norm(q[i] - q[(i + 1) % 4]) for i in range(4)]
    if min(e) < 15 or max(e) / min(e) > 3.0:
        return False
    return True

def sift_quad(frame, roi=None):
    g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ox = oy = 0; sc = 1.0
    if roi is not None:
        x0, y0, x1, y1 = [int(v) for v in roi]
        x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(g.shape[1], x1), min(g.shape[0], y1)
        if x1 - x0 < 20 or y1 - y0 < 20:
            return None
        g = g[y0:y1, x0:x1]; ox, oy = x0, y0
        sc = max(1.0, 500.0 / max(g.shape))
        if sc > 1:
            g = cv2.resize(g, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    kf, df = SIFT.detectAndCompute(g, None)
    if df is None or len(kf) < 8:
        return None
    m = BF.knnMatch(DL, df, k=2)
    good = [a for a, b in (x for x in m if len(x) == 2) if a.distance < 0.75 * b.distance]
    if len(good) < 10:
        return None
    src = np.float32([KL[a.queryIdx].pt for a in good]).reshape(-1, 1, 2)
    dst = np.float32([kf[a.trainIdx].pt for a in good]).reshape(-1, 1, 2) / sc + np.float32([ox, oy])
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 4.0)
    if H is None or mask.sum() < 12:
        return None
    q = cv2.perspectiveTransform(LCORN.reshape(-1, 1, 2), H).reshape(4, 2)
    return q if valid_quad(q, frame.shape[1], frame.shape[0]) else None

def lk_step(prev, nxt, q):
    """Mueve el cuadrilátero q de prev a nxt con flujo óptico sobre el producto."""
    g0 = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY); g1 = cv2.cvtColor(nxt, cv2.COLOR_BGR2GRAY)
    c = q.mean(0); big = (q - c) * 1.35 + c
    mask = np.zeros_like(g0); cv2.fillConvexPoly(mask, big.astype(np.int32), 255)
    p0 = cv2.goodFeaturesToTrack(g0, 200, 0.01, 4, mask=mask)
    if p0 is None or len(p0) < 6:
        return q
    p1, st, _ = cv2.calcOpticalFlowPyrLK(g0, g1, p0, None, winSize=(21, 21), maxLevel=3)
    ok = st.reshape(-1) == 1
    if ok.sum() < 6:
        return q
    M, inl = cv2.estimateAffinePartial2D(p0[ok], p1[ok], method=cv2.RANSAC, ransacReprojThreshold=3.0)
    if M is None:
        return q
    return cv2.transform(q.reshape(-1, 1, 2), M).reshape(4, 2)

def pair_motion(f0, f1, q):
    """Movimiento del tubo entre dos cuadros (similaridad 3x3) con flujo óptico ida y vuelta sobre la zona de la etiqueta."""
    g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY); g1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)
    c = q.mean(0); big = (q - c) * 1.12 + c
    mask = np.zeros_like(g0); cv2.fillConvexPoly(mask, big.astype(np.int32), 255)
    p0 = cv2.goodFeaturesToTrack(g0, 400, 0.003, 3, mask=mask)
    if p0 is None or len(p0) < 8:
        return None
    lk = dict(winSize=(21, 21), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 0.01))
    p1, st, _ = cv2.calcOpticalFlowPyrLK(g0, g1, p0, None, **lk)
    pb, st2, _ = cv2.calcOpticalFlowPyrLK(g1, g0, p1, None, **lk)
    ok = (st.reshape(-1) == 1) & (st2.reshape(-1) == 1) & (np.linalg.norm((p0 - pb).reshape(-1, 2), axis=1) < 0.4)
    if ok.sum() < 8:
        return None
    model = os.environ.get('LF_MODEL', 'aff')  # afín completa: sigue mejor la inclinación del tubo
    if model == 'homo':
        Hm, inl = cv2.findHomography(p0[ok], p1[ok], cv2.RANSAC, 0.8)
        if Hm is None or inl is None or inl.sum() < 10:
            return None
        return Hm.astype(np.float64)
    est = cv2.estimateAffine2D if model == 'aff' else cv2.estimateAffinePartial2D
    M, inl = est(p0[ok], p1[ok], method=cv2.RANSAC, ransacReprojThreshold=0.8, maxIters=4000, confidence=0.999)
    if M is None or inl is None or inl.sum() < 8:
        return None
    return np.vstack([M, [0, 0, 1]]).astype(np.float64)

def apply_h(Hm, q):
    return cv2.perspectiveTransform(q.reshape(-1, 1, 2).astype(np.float64), Hm).reshape(4, 2).astype(np.float32)

def lock_to_tube(frames, det, rough, sigma=12.0):
    """Etiqueta fija al tubo: el movimiento cuadro a cuadro sale del flujo óptico (sin temblor) y las detecciones SIFT
    solo corrigen la deriva lenta (promedio gaussiano en el tiempo, sin valores atípicos)."""
    n = len(frames)
    A = [np.eye(3)] * n; brk = [False] * n
    for i in range(1, n):
        M = pair_motion(frames[i - 1], frames[i], rough[i - 1])
        if M is None:  # sin puntos: movimiento de la estimación gruesa
            M2, _ = cv2.estimateAffinePartial2D(rough[i - 1].reshape(-1, 1, 2), rough[i].reshape(-1, 1, 2))
            M = np.vstack([M2, [0, 0, 1]]) if M2 is not None else np.eye(3); brk[i] = True
        A[i] = M
    anchors = [i for i in range(n) if det[i] is not None]
    r = anchors[len(anchors) // 2]
    C = [None] * n; C[r] = np.eye(3)
    for i in range(r + 1, n):
        C[i] = A[i] @ C[i - 1]
    for i in range(r - 1, -1, -1):
        C[i] = np.linalg.inv(A[i + 1]) @ C[i + 1]
    R = {i: apply_h(np.linalg.inv(C[i]), det[i]) for i in anchors}
    dev = {}
    for i in anchors:  # atípicos frente a la mediana local (±15 cuadros): la deriva lenta no cuenta como error
        near = [R[j] for j in anchors if abs(j - i) <= 15]
        dev[i] = float(np.abs(R[i] - np.median(np.array(near), axis=0)).max())
    mad = np.median(list(dev.values()))
    keep = [i for i in anchors if dev[i] <= max(3.0, 3.0 * mad)] or anchors
    kt = np.array(keep, np.float64); KR = np.array([R[i] for i in keep], np.float64)
    out = []
    for t in range(n):
        wgt = np.exp(-0.5 * ((kt - t) / sigma) ** 2) + 1e-9
        Rt = (KR * wgt[:, None, None]).sum(0) / wgt.sum()
        out.append(apply_h(C[t], Rt))
    return np.array(out, np.float32), sum(brk), len(keep)

MOTION = 0.0

def tube_mask(roi, L, sat, qm, skin):
    """Silueta del tubo blanco dentro del recorte: claro y poco saturado, letras rellenadas, componente bajo la etiqueta."""
    inq = qm > 0
    ref = np.percentile(L[inq], 85) if inq.any() else 220
    white = (L > ref * 0.62) & (sat < 0.22) & (skin == 0)
    white = white.astype(np.uint8) * 255
    bw = max(5, int(np.sqrt(inq.sum()) * 0.12) | 1)
    white = cv2.morphologyEx(white, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (bw, bw)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(white)
    if n <= 1:
        return np.ones(L.shape, np.float32)
    cnt = np.bincount(lab[inq].ravel(), minlength=n); cnt[0] = 0
    m = (lab == int(cnt.argmax())).astype(np.uint8) * 255
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(m, cs, -1, 255, cv2.FILLED)   # rellenar huecos (letras)
    m = cv2.erode(m, np.ones((3, 3), np.uint8), iterations=2)
    return cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 1.2)
FLIP = False   # etiqueta invertida 180° (stick boca abajo: piedra hacia abajo)
TUBE = False   # recortar la etiqueta a la silueta blanca del tubo (no se sale por los bordes cuando el stick gira)
WIPE = False   # borrar TODA la zona de la etiqueta (no solo las letras): para etiquetas pequeñas donde quedan restos de la IA
BLANK = False  # solo borrar el texto de la IA (tubo sin etiqueta) cuando no se puede pegar perfecta

def composite(frame, q, strength=1.0):
    if strength <= 0.01:
        return frame
    h, w = frame.shape[:2]
    if FLIP:
        q = np.roll(q.reshape(4, 2), 2, axis=0)
    Hm = cv2.getPerspectiveTransform(LCORN, q.astype(np.float32))
    x, y, bw, bh = cv2.boundingRect(q.astype(np.int32))
    pad = 30
    x0, y0, x1, y1 = max(0, x - pad), max(0, y - pad), min(w, x + bw + pad), min(h, y + bh + pad)
    if x1 <= x0 or y1 <= y0:
        return frame
    T = np.float32([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]]) @ Hm
    rw, rh = x1 - x0, y1 - y0
    sc = min(1.0, max(bw, bh) * 1.3 / LW)
    if sc < 0.95:  # etiqueta pequeña: se reduce primero por área (como una foto real a esa distancia), luego se deforma
        sw, sh = max(8, int(LW * sc)), max(8, int(LH * sc))
        labs, laba = cv2.resize(LAB, (sw, sh), interpolation=cv2.INTER_AREA), cv2.resize(LAB_A, (sw, sh), interpolation=cv2.INTER_AREA)
        Ts = T @ np.float32([[LW / sw, 0, 0], [0, LH / sh, 0], [0, 0, 1]])
    else:
        labs, laba, Ts = LAB, LAB_A, T
    txt = cv2.warpPerspective(labs, Ts, (rw, rh), flags=cv2.INTER_CUBIC).astype(np.float32)
    ta = cv2.warpPerspective(laba, Ts, (rw, rh), flags=cv2.INTER_LINEAR)
    ta = np.clip(ta, 0, 1) ** (0.65 if sc >= 0.95 else 0.85)  # más contraste en letras pequeñas
    qm = cv2.warpPerspective(np.full((LH, LW), 255, np.uint8), T, (rw, rh))
    roi = frame[y0:y1, x0:x1]
    L = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).astype(np.float32)
    k = max(5, int(min(bw, bh) * 0.09) | 1)
    S = cv2.GaussianBlur(cv2.dilate(L, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))), (0, 0), max(2, k / 2))
    ycc = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
    skin = ((ycc[..., 1] > 135) & (ycc[..., 1] < 178) & (ycc[..., 2] > 80) & (ycc[..., 2] < 132) & (ycc[..., 0] > 50)).astype(np.uint8)
    # con luz cálida el tubo blanco cae en el rango de piel: piel = color lejos del tono propio del tubo y más saturado
    qin = cv2.warpPerspective(np.full((LH, LW), 255, np.uint8), np.float32([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]]) @ Hm, (x1 - x0, y1 - y0)) > 0
    if qin.any():
        lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB).astype(np.float32)
        Lq = lab[..., 0][qin]
        tref = np.median(lab[qin & (lab[..., 0] >= np.percentile(Lq, 60))], axis=0)
        cd = np.linalg.norm(lab[..., 1:] - tref[1:], axis=2)
        sat0 = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)[..., 1].astype(np.float32) / 255
        tsat = float(np.median(sat0[qin & (lab[..., 0] >= np.percentile(Lq, 60))]))
        skin = (skin.astype(bool) & ((cd > 9) | (sat0 > tsat + 0.12))).astype(np.uint8)
    skin = cv2.dilate(skin, np.ones((5, 5), np.uint8))
    # 1) borrar el texto deformado de la IA dentro de la zona de la etiqueta
    sat = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)[..., 1].astype(np.float32) / 255
    inner = cv2.erode(qm, np.ones((3, 3), np.uint8), iterations=max(1, int(min(bw, bh) * 0.02)))
    textmask = (((L < S * 0.86) | (sat > 0.20)) & (inner > 0) & (skin == 0)).astype(np.uint8) * 255
    textmask = cv2.dilate(textmask, np.ones((3, 3), np.uint8), iterations=3)
    clean = cv2.inpaint(roi, textmask, 5, cv2.INPAINT_TELEA).astype(np.float32)
    # 2) letras reales con la luz del tubo
    shade = np.clip(S / max(1.0, np.percentile(S[inner > 0], 80) if (inner > 0).any() else 255), 0.6, 1.1)
    lit = txt * shade[..., None]
    if MOTION > 0.6:  # desenfoque de movimiento aproximado
        lit = cv2.GaussianBlur(lit, (0, 0), MOTION); ta = cv2.GaussianBlur(ta, (0, 0), MOTION)
    a = ta * (1 - np.clip(cv2.GaussianBlur(skin.astype(np.float32), (0, 0), 2) * 1.3, 0, 1))
    em = cv2.GaussianBlur(textmask.astype(np.float32) / 255, (0, 0), 1.0)
    if WIPE:  # tubo limpio = luz del tubo (máximo local) con el tono del blanco del tubo
        kc = max(7, int(min(bw, bh) * 0.16) | 1)   # cierre mayor que las letras: queda la luz real del tubo
        clean = cv2.morphologyEx(roi, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kc, kc)))
        clean = cv2.GaussianBlur(clean, (0, 0), kc / 4).astype(np.float32)
        em = cv2.GaussianBlur(((inner > 0) & (skin == 0)).astype(np.float32), (0, 0), max(1.5, kc / 5))
    if TUBE:
        tm = tube_mask(roi, L, sat, qm, skin)
        em = em * tm; ta = ta * tm
    base = roi.astype(np.float32) * (1 - em[..., None] * strength) + clean * (em[..., None] * strength)
    if BLANK:
        frame[y0:y1, x0:x1] = np.clip(base, 0, 255).astype(np.uint8)
        return frame
    out = base * (1 - (a * strength)[..., None]) + lit * (a * strength)[..., None]
    frame[y0:y1, x0:x1] = np.clip(out, 0, 255).astype(np.uint8)
    return frame

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('dst')
    ap.add_argument('--quad', help='x0,y0,...,x3,y3 (TL,TR,BR,BL) en el cuadro --qt')
    ap.add_argument('--qt', type=float, default=0.0)
    ap.add_argument('--roi', help='x0,y0,x1,y1 zona del producto para la detección inicial')
    ap.add_argument('--nosift', action='store_true')
    ap.add_argument('--flip', action='store_true', help='pegar la etiqueta invertida 180° (piedra hacia abajo)')
    ap.add_argument('--tube', action='store_true', help='recortar la etiqueta a la silueta del tubo')
    ap.add_argument('--wipe', action='store_true', help='borrar toda la zona de la etiqueta antes de pegar la real')
    ap.add_argument('--blank', action='store_true', help='solo borrar el texto de la IA, sin pegar etiqueta')
    ap.add_argument('--nolock', action='store_true', help='sin fijar al tubo (solo suavizado)')
    ap.add_argument('--keys', help='t:x,y,lado;t:x,y,lado;... posiciones manuales (cuadrado) interpoladas')
    a = ap.parse_args()
    global FLIP, BLANK, TUBE, WIPE, MOTION
    FLIP, BLANK, TUBE, WIPE = a.flip, a.blank, a.tube, a.wipe
    frames, fps, w, h = read_frames(a.src)
    n = len(frames); num, den = map(int, fps.split('/')); fr = num / den
    if a.keys:  # modo manual por fotogramas clave (producto pequeño o logo ilegible para la detección)
        ks = sorted((float(t), [float(v) for v in xy.split(',')]) for t, xy in (k.split(':') for k in a.keys.split(';')))
        tt = np.array([k[0] for k in ks]); vv = np.array([k[1] for k in ks])
        Qs, speed = [], []
        for i in range(n):
            t = i / fr
            x, y, sd = (np.interp(t, tt, vv[:, j]) for j in range(3))
            Qs.append(np.float32([[x, y], [x + sd, y], [x + sd, y + sd], [x, y + sd]]))
        Qs = np.array(Qs)
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}', '-r', fps, '-i', '-',
                                '-i', a.src, '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14',
                                '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-shortest', a.dst], stdin=subprocess.PIPE)
        for i in range(n):
            v = np.linalg.norm(Qs[min(n - 1, i + 1)].mean(0) - Qs[max(0, i - 1)].mean(0)) / 2
            MOTION = min(2.0, v * 0.12)
            enc.stdin.write(composite(frames[i], Qs[i], 1.0).tobytes())
        enc.stdin.close(); enc.wait(); print('ok (claves)', a.dst); return
    det = [None] * n
    roi = [float(v) for v in a.roi.split(',')] if a.roi else None
    if not a.nosift:
        for i in range(n):
            if roi is None and i % 1 == 0:
                det[i] = sift_quad(frames[i])
            else:
                r = roi
                prev = next((det[j] for j in range(i - 1, max(-1, i - 8), -1) if det[j] is not None), None)
                if prev is not None:
                    x, y, bw, bh = cv2.boundingRect(prev.astype(np.int32)); r = (x - bw, y - bh, x + 2 * bw, y + 2 * bh)
                det[i] = sift_quad(frames[i], r)
    if a.quad:
        q = np.float32([float(v) for v in a.quad.split(',')]).reshape(4, 2)
        det[int(round(a.qt * fr))] = q
    anchors = [i for i in range(n) if det[i] is not None]
    print(f'{a.src}: {n} cuadros, detección en {len(anchors)}')
    if not anchors:
        sys.exit('sin detección: pasar --quad')
    # completar con seguimiento hacia adelante y hacia atrás desde cada ancla
    quads = [None] * n
    for i in anchors:
        quads[i] = det[i]
    for i in range(1, n):
        if quads[i] is None and quads[i - 1] is not None:
            quads[i] = lk_step(frames[i - 1], frames[i], quads[i - 1])
    for i in range(n - 2, -1, -1):
        if quads[i] is None and quads[i + 1] is not None:
            quads[i] = lk_step(frames[i + 1], frames[i], quads[i + 1])
    # segunda pasada: donde no hubo detección, buscar en una zona ampliada alrededor de la posición estimada
    if not a.nosift:
        extra = 0
        for i in range(n):
            if det[i] is None and quads[i] is not None:
                x, y, bw, bh = cv2.boundingRect(quads[i].astype(np.int32))
                d2 = sift_quad(frames[i], (x - bw, y - bh, x + 2 * bw, y + 2 * bh))
                if d2 is not None and np.abs(d2 - quads[i]).max() < max(bw, bh) * 0.6:
                    det[i] = d2; extra += 1
        if extra:
            anchors = [i for i in range(n) if det[i] is not None]
            print(f'  segunda pasada: +{extra} detecciones (total {len(anchors)})')
            quads = [det[i] if det[i] is not None else None for i in range(n)]
            for i in range(1, n):
                if quads[i] is None and quads[i - 1] is not None:
                    quads[i] = lk_step(frames[i - 1], frames[i], quads[i - 1])
            for i in range(n - 2, -1, -1):
                if quads[i] is None and quads[i + 1] is not None:
                    quads[i] = lk_step(frames[i + 1], frames[i], quads[i + 1])
    # estimación gruesa (mediana) -> etiqueta fija al tubo (flujo óptico + corrección lenta de la deriva)
    Q = np.array(quads, np.float32)
    k = 5
    Qs = np.array([np.median(Q[max(0, i - k // 2):i + k // 2 + 1], axis=0) for i in range(n)], np.float32)
    Qs = np.array([Qs[max(0, i - 1):i + 2].mean(0) for i in range(n)], np.float32)
    if len(anchors) >= 2 and not a.nolock:
        Qs, nbrk, nkeep = lock_to_tube(frames, det, Qs)
        print(f'  fija al tubo: {nkeep} anclas usadas, {nbrk} cuadros sin flujo')
    np.save(a.dst + '.quads.npy', Qs)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}', '-r', fps, '-i', '-',
                            '-i', a.src, '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14',
                            '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-shortest', a.dst], stdin=subprocess.PIPE)
    dist = [min((abs(i - j) for j in anchors), default=999) for i in range(n)]
    manual = a.quad is not None and len(anchors) <= 1
    for i in range(n):
        st = 1.0 if manual else float(np.clip((10 - dist[i]) / 6.0, 0, 1))
        v = np.linalg.norm(Qs[min(n - 1, i + 1)].mean(0) - Qs[max(0, i - 1)].mean(0)) / 2
        MOTION = min(2.0, v * 0.12)  # desenfoque de movimiento como el del clip
        enc.stdin.write(composite(frames[i], Qs[i], st).tobytes())
    enc.stdin.close(); enc.wait()
    json.dump({'anchors': len(anchors), 'n': n}, open(a.dst + '.json', 'w'))
    print('ok', a.dst)

if __name__ == '__main__':
    main()
