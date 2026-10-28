"""Render the timeline to video in parallel chunks.

usage: python render.py OUT.mp4 [--workers 4] [--from S --to S] [--preview]"""
import argparse
import math
import os
import subprocess
import sys
import time
from multiprocessing import Process

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import FPS, H, W, texture  # noqa: E402
from gfx import transition  # noqa: E402


class Shot:
    def __init__(self, start, base, ov=(), tr=None, td=0.0, tex=None, post=None, name=""):
        self.start, self.base, self.ov, self.tr, self.td = start, base, list(ov), tr, td
        self.tex = tex or {}
        self.post = post
        self.name = name
        self.ready = False

    def setup(self, dur):
        self.dur = dur
        self.base.setup(dur)
        self.ready = True

    def render(self, t, fi):
        fr = self.base.frame(t)
        if fr.shape[:2] != (H, W):
            import cv2
            fr = cv2.resize(fr, (W, H))
        fr = np.ascontiguousarray(fr)
        if not fr.flags.writeable:
            fr = fr.copy()
        for o in self.ov:
            o.draw(fr, t, self.dur)
        if self.post:
            fr = self.post(fr, t, self.dur)
        tex = dict(grain=5.0, vignette=0.85, dust=0.0, flicker=0.0)
        tex.update(self.tex)
        return texture().apply(fr, fi, **tex)


def build(total):
    import timeline
    shots = timeline.build()
    shots.sort(key=lambda s: s.start)
    for i, s in enumerate(shots):
        end = shots[i + 1].start if i + 1 < len(shots) else total
        s.end = end
    return shots


def frame_at(shots, T, fi, cache):
    # binary search
    lo, hi = 0, len(shots) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if shots[mid].start <= T:
            lo = mid
        else:
            hi = mid - 1
    i = lo

    def rend(j, tt):
        s = shots[j]
        if not s.ready:
            s.setup(s.end - s.start)
            cache.add(j)
        return s.render(tt - s.start, fi)

    s = shots[i]
    if i > 0 and s.tr and s.td > 0 and T < s.start + s.td / 2:
        a = rend(i - 1, T)
        b = rend(i, max(T, s.start))
        k = (T - (s.start - s.td / 2)) / s.td
        return transition(s.tr, a, b, k)
    if i + 1 < len(shots):
        n = shots[i + 1]
        if n.tr and n.td > 0 and T >= n.start - n.td / 2:
            a = rend(i, T)
            b = rend(i + 1, n.start)
            k = (T - (n.start - n.td / 2)) / n.td
            return transition(n.tr, a, b, k)
    return rend(i, T)


def worker(out, f0, f1, total, preview):
    shots = build(total)
    ow, oh = (W // 2, H // 2) if preview else (W, H)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast" if preview else "medium", "-crf", "23" if preview else "18",
           "-pix_fmt", "yuv420p", "-g", "60", "-threads", "2", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    cache = set()
    t0 = time.time()
    for fi in range(f0, f1):
        T = fi / FPS
        fr = frame_at(shots, T, fi, cache)
        if preview:
            import cv2
            fr = cv2.resize(fr, (ow, oh), interpolation=cv2.INTER_AREA)
        p.stdin.write(np.ascontiguousarray(fr).tobytes())
        # close finished shots
        for j in list(cache):
            if shots[j].end + 1.0 < T:
                shots[j].base.close()
                cache.discard(j)
        if (fi - f0) % 300 == 0:
            el = time.time() - t0
            print(f"[{os.path.basename(out)}] {fi - f0}/{f1 - f0} frames, {el:.0f}s", flush=True)
    p.stdin.close()
    p.wait()
    for j in cache:
        shots[j].base.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--from", dest="t_from", type=float, default=0.0)
    ap.add_argument("--to", dest="t_to", type=float, default=None)
    ap.add_argument("--total", type=float, default=1130.37)
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    t_to = a.t_to if a.t_to is not None else a.total
    f0, f1 = int(round(a.t_from * FPS)), int(round(t_to * FPS))
    n = max(1, a.workers)
    step = math.ceil((f1 - f0) / n)
    parts, procs = [], []
    tmpdir = os.path.join(os.path.dirname(os.path.abspath(a.out)), "chunks")
    os.makedirs(tmpdir, exist_ok=True)
    for k in range(n):
        s, e = f0 + k * step, min(f1, f0 + (k + 1) * step)
        if s >= e:
            continue
        part = os.path.join(tmpdir, f"part_{k:02d}.mp4")
        parts.append(part)
        pr = Process(target=worker, args=(part, s, e, a.total, a.preview))
        pr.start()
        procs.append(pr)
    for pr in procs:
        pr.join()
    lst = os.path.join(tmpdir, "list.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", a.out], check=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
