"""Talking-head mezzanines (one per voice segment, with pre/post roll) + per-frame face tracking.

usage: python3 talk_prep.py <work> <models_dir> [ids]
writes <work>/talk/<id>.mp4 (1620x2880, 30 fps) and <work>/talk_faces.json
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cv4"))
import cv2

W, MD = sys.argv[1], sys.argv[2]
only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
T = json.load(open(os.path.join(W, "timeline.json")))
OUT = os.path.join(W, "talk")
os.makedirs(OUT, exist_ok=True)
PRE, POST = 0.8, 1.0
TW, TH = 1620, 2880


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)


def prep(v):
    src = os.path.join(W, "raw", v["src"] + ".MOV")
    a = max(0.0, v["in"] - PRE)
    b = min(dur(src) - 0.05, v["out"] + POST)
    dst = os.path.join(OUT, v["id"] + ".mp4")
    if not os.path.exists(dst) or only:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", src, "-an",
                        "-vf", f"scale={TW}:{TH}:flags=lanczos,fps=30,setsar=1,format=yuv420p",
                        "-c:v", "libx264", "-crf", "10", "-preset", "fast", dst], check=True)
    return v["id"], a, b, dst


def faces(path):
    det = cv2.CascadeClassifier(os.path.join(MD, "haarcascade_frontalface_default.xml"))
    cap = cv2.VideoCapture(path)
    res = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        sm = cv2.resize(fr, (405, 720), interpolation=cv2.INTER_AREA)
        g = cv2.equalizeHist(cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY))
        fs = det.detectMultiScale(g, scaleFactor=1.08, minNeighbors=6, minSize=(60, 60))
        if len(fs):
            x, y, w, h = max(fs, key=lambda r: r[2] * r[3])
            res.append([round((x + w / 2) / 405, 4), round((y + h / 2) / 720, 4), round(w / 405, 4)])
        else:
            res.append(None)
    return res


EXTRA = [{"id": "H", "src": "IMG_7108", "in": 0.20, "out": 2.80, "kind": "h"}]   # silent hook shot of her
segs = [v for v in T["voice"] + EXTRA if not only or v["id"] in only]
with ThreadPoolExecutor(3) as ex:
    done = list(ex.map(prep, segs))
meta_path = os.path.join(W, "talk_faces.json")
meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
for vid, a, b, dst in done:
    fc = faces(dst)
    got = [f for f in fc if f]
    med = np.median(np.array(got), axis=0).round(4).tolist() if got else None
    meta[vid] = {"file": dst, "t0": a, "t1": b, "faces": fc, "median": med}
    miss = sum(1 for f in fc if f is None)
    print(vid, f"{a:.2f}-{b:.2f}", "frames", len(fc), "missing", miss, "median", med, flush=True)
json.dump(meta, open(meta_path, "w"))
