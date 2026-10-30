"""Frame renderer. Usage:
  python render.py frames t1 t2 ...        -> PNG stills (timeline seconds) for checking
  python render.py video OUT.mp4 [a b]     -> full render (or timeline range a..b seconds)
"""
import sys, os, math, subprocess, time
import multiprocessing as mp
import numpy as np, cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import (W, H, FPS, S, VideoReader, load_image, resolve, view_warp, grade, holo, look, tr_effect,
                  clamp01, ease_io, lerp)
import gfx as G
import edl

TR_OUT = {"whip": 0.15, "zoom": 0.2, "glitch": 0.12, "flash": 0.07, "fade": 0.25, "dip": 0.15, "redflash": 0.05}


class Renderer:
    def __init__(self):
        self.shots, self.ovs, self.sfx = edl.build()
        self.readers, self.gfx = {}, {}
        self.cur = 0

    def shot_index(self, t):
        sh = self.shots
        i = min(self.cur, len(sh) - 1)
        while i > 0 and t < sh[i]["t"]:
            i -= 1
        while i + 1 < len(sh) and t >= sh[i + 1]["t"]:
            i += 1
        self.cur = i
        return i

    def base(self, i, t):
        s = self.shots[i]
        dur = s["end"] - s["t"]
        tl = t - s["t"]
        u = clamp01(tl / dur)
        ue = 0.5 * u + 0.5 * ease_io(u)
        kind = s["kind"]
        if kind in ("video", "image"):
            if kind == "video":
                if i not in self.readers:
                    n = int(math.ceil(dur * FPS)) + 2
                    self.readers[i] = VideoReader(resolve(s["src"]), s["ss"], s["speed"], n, s["rev"])
                src = self.readers[i].get(int(round(tl * FPS)))
            else:
                src = load_image(resolve(s["src"]))
            z = lerp(s["z"][0], s["z"][1], ue)
            p = s["pan"]
            img = view_warp(src, z, lerp(p[0], p[2], ue), lerp(p[1], p[3], ue), lerp(s["rot"][0], s["rot"][1], ue))
            img = img.astype(np.float32) / 255
            if s.get("blur"):
                img = cv2.GaussianBlur(img, (0, 0), s["blur"])
            if s.get("holo"):
                img = holo(img, t) * s["dark"]
            else:
                img = grade(img, s["grade"], s["dark"])
        elif kind == "gfx":
            if i not in self.gfx:
                kw = dict(s["gkw"])
                if s["src"] == "LeakGrid":
                    kw["thumbs"] = edl.leak_thumbs()
                self.gfx[i] = getattr(G, s["src"])(dur, **kw)
            img = self.gfx[i].frame(tl).astype(np.float32)
            if s["grade"] != "raw":
                img = grade(img, s["grade"], s["dark"])
        else:
            img = np.zeros((H, W, 3), np.float32)
        return np.ascontiguousarray(img)

    def render(self, fi):
        t = fi / FPS
        i = self.shot_index(t)
        for k in [k for k in self.readers if k < i - 1 or k > i + 1]:
            self.readers.pop(k).close()
        for k in [k for k in self.gfx if k < i - 1]:
            self.gfx.pop(k)
        s = self.shots[i]
        f = self.base(i, t)
        for o in self.ovs:
            if o.active(t):
                o.draw(f, t)
        tl = t - s["t"]
        if s.get("tin"):
            kind, d = s["tin"]
            if tl < d:
                f = tr_effect(f, kind, 1 - tl / d, "in", fi)
        if i + 1 < len(self.shots) and self.shots[i + 1].get("tin"):
            kind, _ = self.shots[i + 1]["tin"]
            d = TR_OUT[kind]
            rem = s["end"] - t
            if rem < d:
                f = tr_effect(f, kind, 1 - rem / d, "out", fi)
        f = look(f, fi)
        if t < 0.35:
            f = f * (t / 0.35)
        if t > edl.END - 0.9:
            f = f * clamp01((edl.END - t) / 0.9)
        return f


def work(args):
    a, b, out, preset = args
    cv2.setNumThreads(1)
    R = Renderer()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", preset, "-crf", "17",
                          "-pix_fmt", "yuv420p", "-threads", "2", out], stdin=subprocess.PIPE)
    t0 = time.time()
    for fi in range(a, b):
        f = R.render(fi)
        p.stdin.write((np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if (fi - a) % 300 == 0:
            print(f"[{a}-{b}] {fi} {time.time() - t0:.0f}s", flush=True)
    p.stdin.close()
    p.wait()
    return out


def main():
    mode = sys.argv[1]
    if mode == "frames":
        R = Renderer()
        os.makedirs(S + "/work/frames", exist_ok=True)
        for ts in sys.argv[2:]:
            t = float(ts)
            fi = int(round(t * FPS))
            R.cur = 0
            f = R.render(fi)
            cv2.imwrite(S + f"/work/frames/f_{t:07.2f}.jpg", (f * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])
        return
    out = sys.argv[2]
    a = int(float(sys.argv[3]) * FPS) if len(sys.argv) > 3 else 0
    b = int(float(sys.argv[4]) * FPS) if len(sys.argv) > 4 else int(edl.END * FPS)
    preset = os.environ.get("PRESET", "medium")
    nproc = int(os.environ.get("NPROC", "4"))
    step = math.ceil((b - a) / nproc)
    parts = []
    for k in range(nproc):
        pa, pb = a + k * step, min(b, a + (k + 1) * step)
        if pa < pb:
            parts.append((pa, pb, S + f"/work/part_{k}.mp4", preset))
    t0 = time.time()
    with mp.Pool(len(parts)) as pool:
        files = pool.map(work, parts)
    lst = S + "/work/parts.txt"
    open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
    print("done", out, f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
