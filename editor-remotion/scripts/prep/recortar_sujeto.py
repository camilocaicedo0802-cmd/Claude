"""Genera, para los momentos de «texto detrás del sujeto», una capa del sujeto recortado con transparencia
(WebM VP9 con alfa) a partir de la toma ya exportada. Modelo: MODNet (Apache-2.0) en CPU con onnxruntime.

uso: python recortar_sujeto.py   (lee MOMENTOS y escribe public/media/fg/*.webm + src/data/fg.json)
"""
import json, subprocess, os, sys, numpy as np, cv2, onnxruntime as ort

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")  # raíz del proyecto
sess = ort.InferenceSession(os.path.join(ROOT, "material/matting/modnet.onnx"), providers=["CPUExecutionProvider"])
caras = json.load(open(os.path.join(ROOT, "src/data/caras.json")))

# id de la toma, inicio y fin (s, tiempo local de la toma). El inicio debe ser múltiplo de 1/12 s para casar fotogramas.
MOMENTOS = [
    ("s01_hook", 0.0, 2.5),
    ("s05_decisiones", 0.0, 2.5),
    ("s06_bits", 3.5, 6.25),
    ("s10_conflicto", 2.0, 3.74),
    ("s13_repitas", 0.0, 1.92),
]
FPS = 24

def matte(img, ref=512):
    h, w = img.shape[:2]
    s = ref / min(h, w)
    nh, nw = int(round(h * s / 32)) * 32, int(round(w * s / 32)) * 32
    x = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)[:, :, ::-1].astype(np.float32) / 255.0
    x = ((x - 0.5) / 0.5).transpose(2, 0, 1)[None]
    m = sess.run(None, {"input": x})[0][0, 0]
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
    return np.clip((m - 0.08) / 0.84, 0, 1)

out = {}
os.makedirs(os.path.join(ROOT, "public/media/fg"), exist_ok=True)
for sid, a, b in MOMENTOS:
    src = os.path.join(ROOT, f"public/media/aroll/{sid}.mp4")
    cap = cv2.VideoCapture(src)
    W, H = int(cap.get(3)), int(cap.get(4))
    fx = caras[sid]["cx"]
    x0 = int(max(0, (fx - 0.27) * W)) // 2 * 2
    x1 = int(min(W, (fx + 0.27) * W)) // 2 * 2
    y0, y1 = 0, int(H * 0.64) // 2 * 2
    cw, ch = x1 - x0, y1 - y0
    f0, f1 = int(round(a * FPS)), int(round(b * FPS))
    dst = os.path.join(ROOT, f"public/media/fg/{sid}.webm")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{cw}x{ch}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "20", "-b:v", "0", "-auto-alt-ref", "0", "-g", "12", "-row-mt", "1", "-cpu-used", "4", "-an", dst], stdin=subprocess.PIPE)
    cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
    prev = None
    n = 0
    for fi in range(f0, f1):
        ok, fr = cap.read()
        if not ok:
            break
        crop = fr[y0:y1, x0:x1]
        m = matte(crop)
        # suavizado temporal ligero para que el borde no vibre
        if prev is not None:
            m = 0.7 * m + 0.3 * prev
        prev = m
        rgba = np.dstack([crop[:, :, ::-1], (m * 255).astype(np.uint8)])
        enc.stdin.write(rgba.tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    cap.release()
    out[sid] = dict(file=f"media/fg/{sid}.webm", from_=a, to=a + n / FPS, x=x0, y=y0, w=cw, h=ch)
    print(sid, n, "fotogramas", cw, "x", ch, os.path.getsize(dst) // 1000, "KB", flush=True)
json.dump(out, open(os.path.join(ROOT, "src/data/fg.json"), "w"), indent=1)
