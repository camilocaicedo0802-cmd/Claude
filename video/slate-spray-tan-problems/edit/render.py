# Render del reel: compone cada fotograma y lo envía a ffmpeg (x264 de alta calidad).
#   python3 render.py video out.mp4 [--from T] [--to T]
#   python3 render.py stills carpeta t1 t2 ...      (fotogramas sueltos para revisar)
import sys, os, subprocess, time
sys.path.insert(0, os.path.dirname(__file__))
import timeline as TL
from engine import *

class ARoll:
    def __init__(self):
        self.cur = None; self.reader = None; self.frame_t = None

    def frame(self, t):
        s, z = TL.zoom_at(t)
        if self.cur is not s or self.reader is None or (self.frame_t is not None and t < self.frame_t):
            if self.reader: self.reader.close()
            self.cur = s
            start = s["a"] + max(0.0, t - s["t0"])
            self.reader = Reader(os.path.join(PROJ, "mezz", s["src"] + ".mov"), start, s["t1"] - t + 0.3 + (TL.TAIL if s is TL.spans[-1] else 0), W, H)
        self.frame_t = t
        img = grade(self.reader.next(), LUT_AROLL, 1.03)
        ax, ay = TL.ANCHOR[s["src"]]
        dy = TL.shift_of(s)
        if abs(z - 1) > 1e-3 or dy > 0:
            M = np.array([[z, 0, ax * (1 - z)], [0, z, ay * (1 - z) + dy]], np.float32)
            img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return img

def compose(t, aroll):
    if t < TL.HOOK:
        img = TL.HOOK_L.draw_base(t)
    else:
        img = aroll.frame(t).copy()
    for L in TL.layers:
        L.draw(img, t)
    # destello suave en el corte del gancho al primer bloque
    if TL.HOOK <= t < TL.HOOK + 0.14:
        a = 0.45 * (1 - (t - TL.HOOK) / 0.14)
        img[:] = (img.astype(np.float32) * (1 - a) + 255 * a).astype(np.uint8)
    return img

def video(out, t_from=0.0, t_to=None):
    t_to = t_to or TL.TOTAL
    n0, n1 = int(round(t_from * FPS)), int(round(t_to * FPS))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ar = ARoll(); t0 = time.time()
    for n in range(n0, n1):
        t = n / FPS
        enc.stdin.write(compose(t, ar).tobytes())
        if n % 60 == 0:
            el = time.time() - t0; done = n - n0 + 1
            print(f"frame {n}/{n1} t={t:5.2f}s  {done / el:4.1f} fps  eta {(n1 - n) / max(done / el, 0.01):4.0f}s", flush=True)
    enc.stdin.close(); enc.wait()
    print("ok", out, time.time() - t0)

def stills(folder, ts):
    os.makedirs(folder, exist_ok=True)
    from PIL import Image
    for t in ts:
        ar = ARoll()
        # avanzar capas de video: las tarjetas abren su lector en el primer fotograma que dibujan
        img = compose(t, ar)
        Image.fromarray(img).save(os.path.join(folder, f"s_{t:06.2f}.png"))
        for L in TL.layers:
            if hasattr(L, "readers"):
                for r in L.readers.values(): r.close()
                L.readers = {}
        if TL.HOOK_L.r: TL.HOOK_L.r.close(); TL.HOOK_L.r = None
    print("ok", len(ts))

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "video":
        a = sys.argv[2:]
        tf = float(a[a.index("--from") + 1]) if "--from" in a else 0.0
        tt = float(a[a.index("--to") + 1]) if "--to" in a else None
        video(a[0], tf, tt)
    else:
        stills(sys.argv[2], [float(x) for x in sys.argv[3:]])
