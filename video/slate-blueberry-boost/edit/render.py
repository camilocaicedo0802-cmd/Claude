"""Render the reel. Usage:
  python render.py out.mp4                 -> full render (video only)
  python render.py --stills 0.5,5.6 dir    -> PNG stills at given times (for review)"""
import sys, os, json, time
import numpy as np, cv2
from engine import *
import timeline as TL

HERE = os.path.dirname(os.path.abspath(__file__))
VMAP = json.load(open(os.path.join(HERE, "voice_raw_map.json")))
WORDS = TL.load_words(os.path.join(HERE, "words.json"))
OVERLAYS = TL.build_overlays(WORDS)

def fr(t): return int(round(t * FPS))

def expand_shots():
    """Split talking-head shots at voice-piece boundaries so lips stay in sync."""
    out = []
    for s in TL.SHOTS:
        if s["kind"] != "t":
            out.append(dict(s)); continue
        ps = [p for p in VMAP if p["clip"] == s["clip"] and p["t1"] > s["t0"] and p["t0"] < s["t1"]]
        assert ps, s
        for i, p in enumerate(ps):
            a = s["t0"] if i == 0 else p["t0"]
            b = ps[i + 1]["t0"] if i + 1 < len(ps) else s["t1"]
            d = dict(s); d.update(t0=a, t1=b, path=TL.TH[s["clip"]], src=p["src0"] + (a - p["t0"]),
                                  zt0=s["t0"], zt1=s["t1"])
            out.append(d)
    return out

SHOTS = expand_shots()

class Renderer:
    def __init__(self):
        self.cur = None; self.reader = None

    def base(self, t, n_in_shot_hint=None):
        s = next(x for x in SHOTS if x["t0"] - 1e-6 <= t < x["t1"] - 1e-6) if t < SHOTS[-1]["t1"] else SHOTS[-1]
        if s["kind"] == "white":
            return np.full((H, W, 3), 0.985, np.float32)
        if self.cur is not s:
            if self.reader: self.reader.close()
            nfr = fr(s["t1"]) - fr(s["t0"]) + 2
            grade = TL.GRADE_T if s["kind"] == "t" else TL.GRADE_B
            self.reader = ShotReader(s["path"], s["src"], nfr, grade); self.cur = s
        img = self.reader.read()
        zt0, zt1 = s.get("zt0", s["t0"]), s.get("zt1", s["t1"])
        u = (t - zt0) / max(1e-3, zt1 - zt0)
        z = s["z0"] + (s["z1"] - s["z0"]) * u
        v = view(img, z, s["cx"], s["cy"])
        return v.astype(np.float32) / 255.0

    def frame(self, t):
        f = self.base(t)
        for o in OVERLAYS:
            for l in o.layers(t):
                composite(f, l)
        return f

def to8(f): return (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == "__main__":
    if sys.argv[1] == "--stills":
        ts = [float(x) for x in sys.argv[2].split(",")]; od = sys.argv[3]; os.makedirs(od, exist_ok=True)
        for t in ts:
            r = Renderer()   # fresh reader per still (seek)
            s = next(x for x in SHOTS if x["t0"] - 1e-6 <= t < x["t1"]) if t < SHOTS[-1]["t1"] else SHOTS[-1]
            if s["kind"] != "white":
                # emulate reading up to t: start a reader at the exact source time
                s2 = dict(s); s2["src"] = s["src"] + (t - s["t0"]); s2["t0"] = t
                s2.setdefault("zt0", s["t0"]); s2.setdefault("zt1", s["t1"])
                r.cur = None
                SHOTS_BAK = list(SHOTS)
                idx = SHOTS.index(s); SHOTS[idx] = s2
                f = r.frame(t); SHOTS[:] = SHOTS_BAK
            else:
                f = r.frame(t)
            cv2.imwrite(f"{od}/s_{t:06.2f}.png", cv2.cvtColor(to8(f), cv2.COLOR_RGB2BGR))
            if r.reader: r.reader.close()
        sys.exit(0)
    out = sys.argv[1]
    t_start = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    t_end = float(sys.argv[3]) if len(sys.argv) > 3 else TL.END
    n0, n1 = fr(t_start), fr(t_end)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "15",
                            "-pix_fmt", "yuv420p", "-x264-params", "keyint=60", out], stdin=subprocess.PIPE)
    r = Renderer(); t0 = time.time()
    for n in range(n0, n1):
        t = n / FPS
        enc.stdin.write(to8(r.frame(t)).tobytes())
        if n % 60 == 0:
            print(f"frame {n}/{n1}  {t:.1f}s  {(n - n0 + 1) / (time.time() - t0):.1f} fps", flush=True)
    enc.stdin.close(); enc.wait()
    if r.reader: r.reader.close()
    print("done", out)
