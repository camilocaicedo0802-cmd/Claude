#!/usr/bin/env python3
"""Transcode the curated portfolio videos into web-ready files.

Usage:
    python3 scripts/media/build_media.py --raw <folder with original Drive files>

For every entry in media/selection.json it writes, under media/out/:
    videos/<slug>.mp4    H.264 + AAC, max 1280px on the long side, faststart
    videos/<slug>.webm   VP9 + Opus fallback, only with --webm-full (doubles the size)
    previews/<slug>.mp4  6 s muted loop for hover / autoplay previews (+ .webm)
    posters/<slug>.webp  poster frame
and builds the showreel montage (videos/showreel.mp4) from real cuts of those clips.
A media/out/manifest.json with the final dimensions, duration and sizes is written
at the end; the websites read it at build time.

Originals missing from --raw are downloaded from the public Drive folders.
Requires ffmpeg/ffprobe on PATH.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEDIA = os.path.join(ROOT, "media")
OUT = os.path.join(MEDIA, "out")
LONG_SIDE = 1280
PREVIEW_SECONDS = 6


def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr[-2000:])
        raise RuntimeError("command failed: " + " ".join(cmd[:6]))
    return res.stdout


def probe(path):
    data = json.loads(run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,width,height:stream_tags=rotate",
        "-of", "json", path,
    ]))
    video = next(s for s in data["streams"] if s["codec_type"] == "video")
    return {
        "w": video["width"],
        "h": video["height"],
        "duration": float(data["format"]["duration"]),
        "audio": any(s["codec_type"] == "audio" for s in data["streams"]),
    }


def source_path(raw_dir, drive_id):
    path = os.path.join(raw_dir, drive_id + ".mp4")
    if not os.path.exists(path):
        url = f"https://drive.usercontent.google.com/download?id={drive_id}&export=download&confirm=t"
        run(["curl", "-sSL", "--retry", "3", "-o", path, url])
    return path


def fit_filter(w, h, long_side):
    # Scale so the long side is at most long_side, keep even dimensions.
    if h >= w:
        return f"scale=-2:'min({long_side},ih)'"
    return f"scale='min({long_side},iw)':-2"


def webm_from(mp4_path, webm_path, crf, audio):
    """VP9 fallback encoded from the web MP4 (already scaled and trimmed)."""
    if os.path.exists(webm_path):
        return
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", mp4_path, "-c:v", "libvpx-vp9", "-crf", str(crf), "-b:v", "0",
           "-row-mt", "1", "-deadline", "good", "-cpu-used", "4", "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "libopus", "-b:a", "96k"] if audio else ["-an"]
    run(cmd + [webm_path])


def build_video(item, raw_dir, webm_full=False):
    slug = item["slug"]
    src = source_path(raw_dir, item["driveId"])
    info = probe(src)
    dur = info["duration"]
    video_out = os.path.join(OUT, "videos", slug + ".mp4")
    preview_out = os.path.join(OUT, "previews", slug + ".mp4")
    poster_out = os.path.join(OUT, "posters", slug + ".webp")
    vf = fit_filter(info["w"], info["h"], LONG_SIDE) + ",fps='min(30,source_fps)',format=yuv420p"

    if not os.path.exists(video_out):
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf,
               "-c:v", "libx264", "-preset", "slow", "-crf", "25",
               "-maxrate", "1800k", "-bufsize", "3600k", "-profile:v", "high",
               "-movflags", "+faststart"]
        cmd += ["-c:a", "aac", "-b:a", "112k", "-ac", "2"] if info["audio"] else ["-an"]
        run(cmd + [video_out])

    if not os.path.exists(preview_out):
        length = min(PREVIEW_SECONDS, dur)
        start = max(0.0, min(item.get("previewAt", 0) * dur, dur - length))
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.2f}", "-t", f"{length:.2f}", "-i", src,
             "-vf", fit_filter(info["w"], info["h"], 640) + ",fps='min(30,source_fps)',format=yuv420p",
             "-c:v", "libx264", "-preset", "slow", "-crf", "30", "-an", "-movflags", "+faststart",
             preview_out])

    if not os.path.exists(poster_out):
        at = min(item.get("posterAt", 0.1) * dur, max(dur - 0.1, 0))
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", src, "-frames:v", "1",
             "-vf", fit_filter(info["w"], info["h"], LONG_SIDE), "-c:v", "libwebp", "-quality", "78",
             poster_out])

    final = probe(video_out)
    full_webm = video_out[:-4] + ".webm"
    if webm_full:
        webm_from(video_out, full_webm, 33, final["audio"])
    webm_from(preview_out, preview_out[:-4] + ".webm", 40, False)
    return slug, {
        "driveId": item["driveId"],
        "width": final["w"],
        "height": final["h"],
        "duration": round(final["duration"], 2),
        "audio": final["audio"],
        "bytes": os.path.getsize(video_out),
        "webm": os.path.exists(full_webm),
        "webmBytes": os.path.getsize(full_webm) if os.path.exists(full_webm) else 0,
        "previewBytes": os.path.getsize(preview_out),
    }


def build_showreel(cfg, selection, raw_dir):
    out = os.path.join(OUT, "videos", cfg["slug"] + ".mp4")
    poster = os.path.join(OUT, "posters", cfg["slug"] + ".webp")
    preview = os.path.join(OUT, "previews", cfg["slug"] + ".mp4")
    by_slug = {v["slug"]: v for v in selection}
    fade = cfg.get("transition", 0.25)
    W, H = 720, 1280
    if not os.path.exists(out):
        with tempfile.TemporaryDirectory() as tmp:
            parts = []
            for i, seg in enumerate(cfg["segments"]):
                src = source_path(raw_dir, by_slug[seg["slug"]]["driveId"])
                info = probe(src)
                part = os.path.join(tmp, f"{i:02d}.mp4")
                d = seg["dur"]
                vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                      f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x080808,fps=30,format=yuv420p,"
                      f"fade=t=in:st=0:d={fade},fade=t=out:st={d - fade:.2f}:d={fade}")
                af = f"afade=t=in:st=0:d={fade},afade=t=out:st={d - fade:.2f}:d={fade},aresample=44100"
                cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(seg["start"]), "-t", str(d), "-i", src]
                if not info["audio"]:
                    cmd += ["-f", "lavfi", "-t", str(d), "-i", "anullsrc=r=44100:cl=stereo"]
                cmd += ["-vf", vf, "-af", af, "-map", "0:v", "-map", "0:a" if info["audio"] else "1:a",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-ac", "2",
                        "-b:a", "192k", "-shortest", part]
                run(cmd)
                parts.append(part)
            listing = os.path.join(tmp, "list.txt")
            with open(listing, "w") as fh:
                fh.write("".join(f"file '{p}'\n" for p in parts))
            run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", listing,
                 "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-maxrate", "2200k",
                 "-bufsize", "4400k", "-profile:v", "high", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out])
    if not os.path.exists(poster):
        run(["ffmpeg", "-v", "error", "-y", "-ss", "1.2", "-i", out, "-frames:v", "1",
             "-c:v", "libwebp", "-quality", "80", poster])
    if not os.path.exists(preview):
        run(["ffmpeg", "-v", "error", "-y", "-i", out, "-vf", "scale=-2:640,format=yuv420p",
             "-c:v", "libx264", "-preset", "slow", "-crf", "30", "-an", "-movflags", "+faststart", preview])
    webm_from(out, out[:-4] + ".webm", 32, True)
    webm_from(preview, preview[:-4] + ".webm", 40, False)
    info = probe(out)
    return cfg["slug"], {
        "width": info["w"], "height": info["h"], "duration": round(info["duration"], 2),
        "audio": True, "bytes": os.path.getsize(out), "webm": True, "webmBytes": os.path.getsize(out[:-4] + ".webm"),
        "previewBytes": os.path.getsize(preview),
        "segments": [s["slug"] for s in cfg["segments"]],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, help="folder with original files named <driveId>.mp4")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--webm-full", action="store_true", help="also encode full-length VP9 fallbacks")
    args = parser.parse_args()
    os.makedirs(args.raw, exist_ok=True)
    for sub in ("videos", "previews", "posters"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    selection = json.load(open(os.path.join(MEDIA, "selection.json")))
    manifest = {}
    with ThreadPoolExecutor(args.jobs) as pool:
        for slug, data in pool.map(lambda v: build_video(v, args.raw, args.webm_full), selection["videos"]):
            manifest[slug] = data
            print(f"ok {slug}: {data['width']}x{data['height']} {data['duration']}s {data['bytes'] // 1024} KB")
    slug, data = build_showreel(selection["showreel"], selection["videos"], args.raw)
    manifest[slug] = data
    print(f"ok {slug}: {data['duration']}s {data['bytes'] // 1024} KB")
    with open(os.path.join(OUT, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)
    total = sum(v["bytes"] + v["webmBytes"] + v["previewBytes"] for v in manifest.values())
    print(f"total {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
