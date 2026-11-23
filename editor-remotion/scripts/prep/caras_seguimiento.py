"""Sigue la cara en cada toma exportada (public/media/aroll) y guarda una trayectoria suavizada en src/data/caras.json.
El recorte vertical es muy cerrado, así que la cámara virtual tiene que acompañar a la cara."""
import cv2, json, numpy as np, os

d = os.path.join(os.path.dirname(cv2.__file__), "data")
front = cv2.CascadeClassifier(d + "/haarcascade_frontalface_default.xml")
prof = cv2.CascadeClassifier(d + "/haarcascade_profileface.xml")
edl = json.load(open("material/edl.json"))
caras = {}
med = lambda a, k=5: np.array([np.median(a[max(0, i - k // 2):i + k // 2 + 1]) for i in range(len(a))])
smooth = lambda a, k=5: np.convolve(np.pad(a, (k // 2, k // 2), mode="edge"), np.ones(k) / k, mode="valid")
for o in edl:
    sid = o["id"]
    if "testimonio" in sid:
        continue
    cap = cv2.VideoCapture(f"public/media/aroll/{sid}.mp4")
    W, H, n, fps = cap.get(3), cap.get(4), int(cap.get(7)), cap.get(5)
    pts = []
    for fi in range(0, n, 3):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ok, fr = cap.read()
        if not ok:
            break
        sc = 960 / fr.shape[1]
        g = cv2.cvtColor(cv2.resize(fr, None, fx=sc, fy=sc), cv2.COLOR_BGR2GRAY)
        best = None
        for det, flip in ((front, False), (prof, False), (prof, True)):
            gg = cv2.flip(g, 1) if flip else g
            for (x, y, w, h) in det.detectMultiScale(gg, 1.1, 6, minSize=(int(g.shape[1] * 0.1),) * 2):
                if flip:
                    x = g.shape[1] - x - w
                if y + h / 2 > g.shape[0] * 0.65 or w < g.shape[1] * 0.12:
                    continue
                if best is None or w * h > best[2] * best[3]:
                    best = (x, y, w, h)
            if best is not None:
                break
        if best:
            x, y, w, h = best
            pts.append((fi / fps, (x + w / 2) / sc / W, (y + h / 2) / sc / H, w / sc / W))
    cap.release()
    P = np.array(pts)
    ts = np.arange(0, n / fps, 0.25)
    cx = smooth(med(np.interp(ts, P[:, 0], P[:, 1])))
    cy = smooth(med(np.interp(ts, P[:, 0], P[:, 2])))
    caras[sid] = dict(cx=round(float(np.median(P[:, 1])), 4), cy=round(float(np.median(P[:, 2])), 4), w=round(float(np.median(P[:, 3])), 4), W=int(W), H=int(H),
                      track=[[round(float(t), 2), round(float(x), 4), round(float(y), 4)] for t, x, y in zip(ts, cx, cy)])
    print(sid, len(pts), "detecciones · cx", caras[sid]["cx"], "cy", caras[sid]["cy"], "ancho", caras[sid]["w"], flush=True)
json.dump(caras, open("src/data/caras.json", "w"), indent=1)
