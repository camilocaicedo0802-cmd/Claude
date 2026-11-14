# Máscara "solo persona" (sin silla) = SAM2 (separa persona/silla) x RVM (borde fino de pelo y ropa).
# uso: person_masks.py <sam2_dir> <rvm.torchscript> <face_landmarker.task> <jobs.json> [VID]
# Escribe public/mascaras/<toma>/p_XXXXX.png (alfa 0-255, 1080x1920).
import sys, os, json, re, subprocess, time
import numpy as np, torch, cv2
import torch.nn.functional as TF
from PIL import Image
from transformers import Sam2Model
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

SAM_DIR, RVM_PATH, LM_PATH, JOBS = sys.argv[1:5]
VID = sys.argv[5] if len(sys.argv) > 5 else 'v8'
root = '/home/user/Claude/video-remotion'
W, H = 1080, 1920
WARM = 12
torch.set_num_threads(4)
sam = Sam2Model.from_pretrained(SAM_DIR).eval()
rvm = torch.jit.load(RVM_PATH).eval()
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=LM_PATH), running_mode=vision.RunningMode.IMAGE, num_faces=1))
faces = json.loads(re.search(r'= (\{.*\});', open(f'{root}/src/{VID}/faces.ts').read()).group(1))
KCH = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
LAPTOP = {'4848': (760, 1800)}
MEAN = np.array([0.485, 0.456, 0.406], np.float32); STD = np.array([0.229, 0.224, 0.225], np.float32)


def embed(fr):
    a = cv2.resize(fr, (1024, 1024), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
    px = torch.from_numpy(((a - MEAN) / STD).transpose(2, 0, 1)).float()[None]
    with torch.no_grad():
        return sam.get_image_embeddings(px)


def sam_mask(emb, pts, neg=()):
    allp = list(pts) + list(neg)
    ip = torch.tensor([[[[x * 1024 / W, y * 1024 / H] for x, y in allp]]]).float()
    il = torch.tensor([[[1] * len(pts) + [0] * len(neg)]], dtype=torch.long)
    with torch.no_grad():
        out = sam(image_embeddings=emb, input_points=ip, input_labels=il, multimask_output=True)
    k = int(out.iou_scores[0, 0].argmax())
    lo = TF.interpolate(out.pred_masks[0, :, k:k + 1], size=(H, W), mode='bilinear', align_corners=False)[0, 0]
    return (lo > 0).numpy().astype(np.uint8)


def clean(m):
    # se queda con la persona (componente mayor + piezas grandes) y tapa agujeros pequeños
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        big = st[1:, cv2.CC_STAT_AREA].max()
        keep = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 0.03 * big]
        m = np.isin(lab, keep).astype(np.uint8)
    inv = 1 - m
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, 4)
    for i in range(1, n):
        x, y, w, h, area = st[i]
        touches = x == 0 or y == 0 or x + w >= W or y + h >= H
        if not touches and area < 6000:
            m[lab == i] = 1
    return m


def face_pts(fr, seg, prev):
    small = cv2.resize(fr, (540, 960), interpolation=cv2.INTER_AREA)
    r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(small)))
    if r.face_landmarks:
        L = r.face_landmarks[0]
        xs = np.array([p.x for p in L]) * W; ys = np.array([p.y for p in L]) * H
        cx, cy, chin, fh = xs.mean(), ys.mean(), ys.max(), ys.max() - ys.min()
        return (cx, cy, chin, fh)
    if prev is not None:
        return prev
    x0, y0, x1, y1 = faces[str(seg)]
    return ((x0 + x1) / 2, (y0 + y1) / 2 + 40, y1, (y1 - y0) * 0.7)


jobs = json.load(open(JOBS))
for job in jobs:
    take, a, b, seg = job['take'], job['a'], job['b'], job['seg']
    s = max(0, a - WARM)
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{s/30+0.001:.4f}', '-i', f'{root}/public/clips/{VID}_{take}.mp4',
                          '-frames:v', str(b - s + 2), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    out = f'{root}/public/mascaras/{take}'
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    rec = [None] * 4
    alphas, sams, laps = {}, {}, {}
    prev = None
    for k, fr in enumerate(frames):
        f = s + k
        with torch.no_grad():
            src = torch.from_numpy(fr).permute(2, 0, 1).float().unsqueeze(0) / 255
            _, pha, *rec = rvm(src, *rec, 0.25)
        if f < a - 1:
            continue
        alphas[f] = pha[0, 0].numpy()
        prev = face_pts(fr, seg, prev)
        cx, cy, chin, fh = prev
        pts = [(cx, cy), (cx, min(H - 20, chin + 220)), (cx, min(H - 20, chin + 520))]
        emb = embed(fr)
        m1 = clean(sam_mask(emb, pts))
        # lo que RVM ve como primer plano y SAM no = silla -> puntos negativos y segunda pasada
        chair = ((alphas[f] > 0.5) & (cv2.dilate(m1, KCH) == 0)).astype(np.uint8)
        chair[int(min(H, chin + 700)):] = 0
        n, lab, st, _ = cv2.connectedComponentsWithStats(chair, 8)
        neg = []
        for j in sorted(range(1, n), key=lambda j: -st[j, cv2.CC_STAT_AREA])[:3]:
            if st[j, cv2.CC_STAT_AREA] < 2500: break
            dt = cv2.distanceTransform((lab == j).astype(np.uint8), cv2.DIST_L2, 5)
            yy, xx = np.unravel_index(dt.argmax(), dt.shape)
            neg.append((float(xx), float(yy)))
        if neg:
            m2 = clean(sam_mask(emb, pts, neg))
            m1 = m2 if m2.sum() > 0.8 * m1.sum() else m1
        # agujeros cerrados que RVM ve como cuerpo (micrófono de solapa, reflejos): se rellenan
        inv = (1 - m1).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(inv, 4)
        for j in range(1, n):
            x, y, w, h, area = st[j]
            if x == 0 or y == 0 or x + w >= W or y + h >= H or area > 40000:
                continue
            hole = lab == j
            if alphas[f][hole].mean() > 0.5:
                m1[hole] = 1
        sams[f] = m1
        if take in LAPTOP:
            # el portátil va delante de la persona: se recorta como objeto aparte y se suma (sin mordisco rectangular)
            lap = sam_mask(emb, [LAPTOP[take]])
            lap[:int(H * 0.62)] = 0
            laps[f] = lap
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    kin = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    kisl = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    uni = {f: np.maximum(m, laps[f]) if f in laps else m for f, m in sams.items()}
    gate = {f: cv2.GaussianBlur(cv2.dilate(u, ker).astype(np.float32), (0, 0), 2.0) for f, u in uni.items()}
    inter = {f: cv2.GaussianBlur(cv2.erode(u, kin).astype(np.float32), (0, 0), 4.0) for f, u in uni.items()}
    lapb = {f: cv2.GaussianBlur(l.astype(np.float32), (0, 0), 1.2) for f, l in laps.items()}
    fs = sorted(sams)
    def avg(d, i):
        nb = [d[g] for g in fs[max(0, i - 1):i + 2] if g in d]
        return np.mean(nb, axis=0) if nb else None
    for i, f in enumerate(fs):
        if f < a or f > b:
            continue
        ar = np.clip((alphas[f] - 0.12) / 0.88, 0, 1)
        # interior: manda SAM (ropa oscura que RVM duda); borde: manda RVM (pelo, orejas); fuera de SAM: nada (silla)
        al = np.maximum(ar, avg(inter, i)) * np.clip(avg(gate, i) * 1.15, 0, 1)
        al = np.clip((al - 0.03) / 0.97, 0, 1)
        if laps:
            al = np.maximum(al, avg(lapb, i))
        # sin islas sueltas (restos de silla/fondo)
        n, lab, st, _ = cv2.connectedComponentsWithStats((al > 0.5).astype(np.uint8), 8)
        if n > 1:
            big = st[1:, cv2.CC_STAT_AREA].max()
            keep = np.isin(lab, [j for j in range(1, n) if st[j, cv2.CC_STAT_AREA] >= 0.03 * big]).astype(np.uint8)
            al = al * cv2.GaussianBlur(cv2.dilate(keep, kisl).astype(np.float32), (0, 0), 2.0)
        Image.fromarray((al * 255).astype(np.uint8)).save(f'{out}/p_{f:05d}.png', optimize=True)
    print(take, a, b, f'{len(fs)} fotogramas en {time.time()-t0:.0f}s', flush=True)
print('PERSON_DONE')
