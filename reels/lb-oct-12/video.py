#!/usr/bin/env python3
"""Render the picture of reel LB-OCT-12: grade, transitions (mask, cover, dissolve) and text.

Usage:
    python video.py --raw <dir with c1 c2 c345 c6 c78> --fonts <dir> --model <selfie_multiclass.tflite>
                    --out video_noaudio.mp4 [--frames 0:300] [--stills 120,400]

Needs ffmpeg, numpy, opencv, pillow and mediapipe (only for the person-mask transitions).
"""
import argparse
import os
import subprocess
import sys

import cv2
import numpy as np

import edl
import text

W, H, FPS = edl.W, edl.H, edl.FPS

# Shared look: warm, soft, slightly lifted blacks; then per-scene exposure/white-balance fixes.
LOOK = ("colorbalance=rs=0.035:bs=-0.045:rm=0.03:bm=-0.035:rh=0.015:bh=-0.03,"
        "eq=contrast=0.94:saturation=0.9,"
        "curves=all='0/0.035 0.25/0.255 0.75/0.745 1/0.965'")
GRADES = {
    "entry": "eq=gamma=1.04",
    "kitchen": "eq=gamma=1.05:saturation=0.97",
    "hall": "eq=gamma=1.08",
    "room": "eq=gamma=1.12:brightness=0.01",
    "dark": "eq=gamma=1.32:brightness=0.03:contrast=0.97,colorbalance=rm=0.02:bm=-0.02",
    "closet": "eq=gamma=1.03",
    "bath": "colorbalance=rs=0.02:bs=-0.035:rm=0.015:bm=-0.03,eq=gamma=1.02",
}


def ffmpeg_shot_cmd(path, shot, seek, native):
    vf = [GRADES[shot["grade"]], LOOK]
    fps = 60 if shot.get("ramp") else FPS
    vf.append(f"fps={fps}")
    if not native:
        vf.append(f"scale={W}:{H}:flags=lanczos:in_color_matrix=bt709,unsharp=5:5:0.3:5:5:0")
    vf.append("format=rgb24")
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{seek:.4f}", "-i", path, "-map", "0:v:0",
           "-vf", ",".join(vf), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    return cmd, fps


class ShotReader:
    """Sequential frame source for one shot; frame j is the shot's j-th output frame."""

    def __init__(self, raw_dir, shot, first=0):
        self.shot = shot
        self.native = "zoom" in shot
        path = os.path.join(raw_dir, shot["src"])
        self.seek = shot["times"][first]
        cmd, self.fps = ffmpeg_shot_cmd(path, shot, self.seek, self.native)
        if self.native:
            probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0", path], capture_output=True, text=True)
            self.w, self.h = map(int, probe.stdout.strip().split(","))
        else:
            self.w, self.h = W, H
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        self.index, self.frame = -1, None

    def _read(self):
        n = self.w * self.h * 3
        buf = self.proc.stdout.read(n)
        if len(buf) < n:
            return False
        self.frame = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
        self.index += 1
        return True

    def get(self, j):
        want = int(round((self.shot["times"][j] - self.seek) * self.fps))
        while self.index < want:
            if not self._read():
                break
        img = self.frame
        if self.native:
            img = self._zoom(img, j)
        return img

    def _zoom(self, img, j):
        z0, z1, cx, cy = self.shot["zoom"]
        n = len(self.shot["times"])
        p = j / max(1, n - 1)
        z = z0 + (z1 - z0) * (p * p * (3 - 2 * p))
        cw, ch = self.w / z, self.h / z
        x0 = min(max(cx * self.w - cw / 2, 0), self.w - cw)
        y0 = min(max(cy * self.h - ch / 2, 0), self.h - ch)
        m = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
        out = cv2.warpAffine(img, m, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        blur = cv2.GaussianBlur(out, (0, 0), 1.6)
        return cv2.addWeighted(out, 1.45, blur, -0.45, 0)

    def close(self):
        if self.proc.poll() is None:
            self.proc.kill()
        self.proc.wait()


class PersonMask:
    """Person probability maps from MediaPipe's multiclass selfie segmenter."""

    def __init__(self, model):
        import mediapipe as mp
        from mediapipe.tasks import python as mpt
        from mediapipe.tasks.python import vision
        self.mp = mp
        opts = vision.ImageSegmenterOptions(base_options=mpt.BaseOptions(model_asset_path=model),
                                            output_confidence_masks=True)
        self.seg = vision.ImageSegmenter.create_from_options(opts)

    def __call__(self, rgb_small):
        res = self.seg.segment(self.mp.Image(image_format=self.mp.ImageFormat.SRGB,
                                             data=np.ascontiguousarray(rgb_small)))
        return np.clip(1.0 - np.squeeze(res.confidence_masks[0].numpy_view()), 0, 1).astype(np.float32)


class MaskReveal:
    """Reveals the incoming shot behind the person's trailing (right) edge as she crosses the lens."""

    SW, SH = 270, 480

    def __init__(self, segmenter, frames):
        self.seg = segmenter
        self.frames = frames
        self.edge = np.full(self.SH, float(self.SW))
        self.started = None

    def alpha(self, k, outgoing):
        small = cv2.resize(outgoing, (self.SW, self.SH), interpolation=cv2.INTER_AREA)
        p = cv2.GaussianBlur(self.seg(small), (0, 0), 1.2)
        body = p > 0.5
        cover = body.mean()
        if self.started is None and (cover > 0.45 or k >= self.frames // 3):
            self.started = k
        if self.started is not None:
            rows = np.where(body.any(axis=1))[0]
            if cover < 0.02 or len(rows) == 0:
                e = np.full(self.SH, -40.0)
            else:
                right = np.full(self.SH, np.nan)
                for y in rows:
                    right[y] = np.nonzero(body[y])[0][-1]
                valid = ~np.isnan(right)
                e = np.interp(np.arange(self.SH), np.nonzero(valid)[0], right[valid])
                e = cv2.GaussianBlur(e.reshape(-1, 1), (1, 0), 10).ravel() + 4
            self.edge = np.minimum(self.edge, e)
        xs = np.arange(self.SW, dtype=np.float32)[None, :]
        reveal = (xs > self.edge[:, None]).astype(np.float32)
        reveal = cv2.GaussianBlur(reveal, (0, 0), 5)
        a = reveal * (1.0 - p)
        if self.started is not None:
            a *= min(1.0, (k - self.started + 1) / 4.0)
        tail = (k - (self.frames - 5)) / 4.0  # make sure the new shot owns the frame at the end
        if tail > 0:
            a = a + (1 - a) * smooth(min(1.0, tail))
        return cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def render(args):
    shots, total = edl.build_timeline()
    f0, f1 = 0, total
    if args.frames:
        a, b = args.frames.split(":")
        f0, f1 = int(a), min(int(b), total)
    stills = set(int(s) for s in args.stills.split(",")) if args.stills else set()
    overlay = text.Overlay(args.fonts, shots, total)
    if args.only:
        return render_stills(args, shots, overlay)
    segmenter = PersonMask(args.model) if any(s.get("in_kind") == "mask" for s in shots) else None

    enc = None
    if args.out:
        enc = subprocess.Popen([
            "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
            "-r", str(FPS), "-i", "-",
            "-vf", "noise=c0s=5:c0f=t+u,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
            "-c:v", "libx264", "-preset", "veryfast" if args.fast else "slow", "-crf", str(args.crf), "-profile:v", "high",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-movflags", "+faststart", args.out], stdin=subprocess.PIPE)

    readers, reveals = {}, {}
    for f in range(f0, f1):
        active = [s for s in shots if s["start"] <= f < s["start"] + len(s["times"])]
        imgs = []
        for s in active:
            if s["id"] not in readers:
                readers[s["id"]] = ShotReader(args.raw, s, f - s["start"])
            imgs.append(readers[s["id"]].get(f - s["start"]).astype(np.float32))
        if len(active) == 1:
            frame = imgs[0]
        else:
            a_shot, b_shot = active
            k = f - b_shot["start"]
            n = b_shot["in_frames"]
            if b_shot["in_kind"] == "mask":
                if b_shot["id"] not in reveals:
                    reveals[b_shot["id"]] = MaskReveal(segmenter, n)
                alpha = reveals[b_shot["id"]].alpha(k, imgs[0].astype(np.uint8))
            else:
                alpha = smooth((k + 1) / (n + 1))
            frame = imgs[0] * (1 - alpha) + imgs[1] * alpha
        for s in list(readers):
            shot = next(x for x in shots if x["id"] == s)
            if f >= shot["start"] + len(shot["times"]) - 1:
                readers.pop(s).close()
        fade = (f - (total - edl.END_FADE)) / edl.END_FADE
        if fade > 0:
            frame = frame * (1 - 0.85 * smooth(fade))
        frame = overlay.apply(frame, f / FPS)
        out = np.clip(frame + 0.5, 0, 255).astype(np.uint8)
        if f in stills:
            cv2.imwrite(os.path.join(args.still_dir, f"f{f:05d}.png"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
        if enc:
            enc.stdin.write(out.tobytes())
        if f % 60 == 0:
            print(f"frame {f}/{total}", file=sys.stderr, flush=True)
    for r in readers.values():
        r.close()
    if enc:
        enc.stdin.close()
        enc.wait()
    if segmenter:
        segmenter.seg.close()


def render_stills(args, shots, overlay):
    """Quick look at single frames (mask transitions are previewed as dissolves)."""
    for f in sorted(int(x) for x in args.stills.split(",")):
        active = [s for s in shots if s["start"] <= f < s["start"] + len(s["times"])]
        imgs = []
        for s in active:
            r = ShotReader(args.raw, s, f - s["start"])
            imgs.append(r.get(f - s["start"]).astype(np.float32))
            r.close()
        frame = imgs[0]
        if len(imgs) == 2:
            a = smooth((f - active[1]["start"] + 1) / (active[1]["in_frames"] + 1))
            frame = imgs[0] * (1 - a) + imgs[1] * a
        out = np.clip(overlay.apply(frame, f / FPS) + 0.5, 0, 255).astype(np.uint8)
        cv2.imwrite(os.path.join(args.still_dir, f"f{f:05d}.png"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out")
    ap.add_argument("--crf", type=int, default=17)
    ap.add_argument("--fast", action="store_true", help="quick preview encode")
    ap.add_argument("--frames", help="render only f0:f1")
    ap.add_argument("--stills", help="comma separated frame numbers to save as PNG")
    ap.add_argument("--still-dir", default=".")
    ap.add_argument("--only", action="store_true", help="render just the --stills frames")
    render(ap.parse_args())


if __name__ == "__main__":
    main()
