#!/usr/bin/env python3
"""Turn the curated portfolio media into web-ready files.

Usage:
    python3 scripts/media/build_media.py --raw <folder with original Drive files>

For every video in media/selection.json it writes, under media/out/:
    videos/<slug>.mp4    H.264 + AAC, faststart, sized by duration so each file stays under ~12 MB
                         (an entry's "encode" object overrides long_side, crf, maxrate, audio, channels)
    videos/<slug>.webm   VP9 + Opus fallback, only with --webm-full (doubles the size)
    previews/<slug>.mp4  6 s muted loop for hover / autoplay previews (+ .webm)
    posters/<slug>.webp  poster frame
For every piece it writes pieces/<file>.webp (max 1600 px) and pieces/sm/<file>.webp (max 720 px),
and records the full-size dimensions in pieces.json.
A media/out/manifest.json with the final video dimensions, duration and sizes is written
at the end; the websites read both JSON files at build time.

Originals are looked up in --raw as <driveId> or <driveId>.mp4 and downloaded from the public
Drive folder when missing. Outputs that already exist are kept; delete a file to rebuild it.
Requires ffmpeg/ffprobe on PATH.
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEDIA = os.path.join(ROOT, "media")
OUT = os.path.join(MEDIA, "out")
PREVIEW_SECONDS = 6
# Upper bound per video file, so every clip fits static hosts with per-file limits.
MAX_VIDEO_BYTES = 11.5e6
# Files in media/out/pieces that do not come from selection.json (portrait for "Sobre mí").
KEEP_PIECES = {"retrato"}


def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr[-2000:])
        raise RuntimeError("command failed: " + " ".join(cmd[:6]))
    return res.stdout


def probe(path):
    data = json.loads(run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,width,height:stream_tags=rotate:stream_side_data=rotation",
        "-of", "json", path,
    ]))
    video = next(s for s in data["streams"] if s["codec_type"] == "video")
    w, h = video["width"], video["height"]
    rotation = int(video.get("tags", {}).get("rotate", 0))
    for side in video.get("side_data_list", []):
        rotation = int(side.get("rotation", rotation))
    if abs(rotation) % 180 == 90:  # ffmpeg auto-rotates, so filters see the swapped size
        w, h = h, w
    return {
        "w": w,
        "h": h,
        "duration": float(data["format"].get("duration") or 0) if data["format"].get("duration") != "N/A" else 0.0,
        "audio": any(s["codec_type"] == "audio" for s in data["streams"]),
    }


def source_path(raw_dir, drive_id):
    for name in (drive_id, drive_id + ".mp4"):
        path = os.path.join(raw_dir, name)
        if os.path.exists(path):
            return path
    path = os.path.join(raw_dir, drive_id)
    url = f"https://drive.usercontent.google.com/download?id={drive_id}&export=download&confirm=t"
    run(["curl", "-sSL", "--fail", "--retry", "3", "-o", path, url])
    return path


def fit_filter(w, h, long_side):
    # Scale so the long side is at most long_side, keep even dimensions.
    if h >= w:
        return f"scale=-2:'min({long_side},ih)'"
    return f"scale='min({long_side},iw)':-2"


def encode_settings(duration, high=False):
    """Videos over 40 s (talks, tutorials) get a smaller frame; every file stays under MAX_VIDEO_BYTES."""
    long_form = duration > 40 and not high
    audio_kbps = 80 if long_form else 112
    budget = int(MAX_VIDEO_BYTES * 8 / max(duration, 1) / 1000) - audio_kbps
    if long_form:
        return {"long_side": 960, "crf": 27, "maxrate": min(900, budget), "audio": audio_kbps, "channels": 2}
    return {"long_side": 1280, "crf": 25, "maxrate": min(1800, budget), "audio": audio_kbps, "channels": 2}


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
    cfg = encode_settings(dur, item.get("quality") == "high")
    # Per-video overrides, e.g. full-length YouTube episodes that cannot fit the per-file budget.
    cfg.update(item.get("encode", {}))
    vf = fit_filter(info["w"], info["h"], cfg["long_side"]) + ",fps='min(30,source_fps)',format=yuv420p"

    if not os.path.exists(video_out):
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf,
               "-c:v", "libx264", "-preset", "slow", "-crf", str(cfg["crf"]),
               "-maxrate", f"{cfg['maxrate']}k", "-bufsize", f"{cfg['maxrate'] * 2}k", "-profile:v", "high",
               "-movflags", "+faststart"]
        cmd += ["-c:a", "aac", "-b:a", f"{cfg['audio']}k", "-ac", str(cfg["channels"])] if info["audio"] else ["-an"]
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
             "-vf", fit_filter(info["w"], info["h"], 1280), "-c:v", "libwebp", "-quality", "78",
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


def build_piece(item, raw_dir):
    name = item["file"]
    full = os.path.join(OUT, "pieces", name + ".webp")
    small = os.path.join(OUT, "pieces", "sm", name + ".webp")
    if not (os.path.exists(full) and os.path.exists(small)):
        src = source_path(raw_dir, item["driveId"])
        info = probe(src)
        for path, side, quality in ((full, 1600, 82), (small, 720, 78)):
            run(["ffmpeg", "-v", "error", "-y", "-i", src, "-frames:v", "1",
                 "-vf", fit_filter(info["w"], info["h"], side), "-c:v", "libwebp", "-quality", str(quality), path])
    out = probe(full)
    return name, [out["w"], out["h"]]


def prune(folder, keep):
    """Remove outputs for media that left selection.json."""
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and name.split(".")[0] not in keep:
            os.remove(path)
            print("removed", os.path.relpath(path, OUT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, help="folder with original files named <driveId>")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--webm-full", action="store_true", help="also encode full-length VP9 fallbacks")
    args = parser.parse_args()
    os.makedirs(args.raw, exist_ok=True)
    for sub in ("videos", "previews", "posters", "pieces", "pieces/sm"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    selection = json.load(open(os.path.join(MEDIA, "selection.json")))

    slugs = {v["slug"] for v in selection["videos"]}
    for sub in ("videos", "previews", "posters"):
        prune(os.path.join(OUT, sub), slugs)
    files = {p["file"] for p in selection["pieces"]} | KEEP_PIECES
    prune(os.path.join(OUT, "pieces"), files)
    prune(os.path.join(OUT, "pieces", "sm"), files)

    manifest = {}
    with ThreadPoolExecutor(args.jobs) as pool:
        for slug, data in pool.map(lambda v: build_video(v, args.raw, args.webm_full), selection["videos"]):
            manifest[slug] = data
            print(f"ok {slug}: {data['width']}x{data['height']} {data['duration']}s {data['bytes'] // 1024} KB")
    with open(os.path.join(OUT, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)

    pieces_path = os.path.join(OUT, "pieces.json")
    previous = json.load(open(pieces_path)) if os.path.exists(pieces_path) else {}
    pieces = {k: v for k, v in previous.items() if k in KEEP_PIECES}
    with ThreadPoolExecutor(args.jobs) as pool:
        for name, size in pool.map(lambda p: build_piece(p, args.raw), selection["pieces"]):
            pieces[name] = size
    with open(pieces_path, "w") as fh:
        json.dump(pieces, fh, indent=1, ensure_ascii=False)
    print(f"ok {len(pieces)} pieces")

    total = sum(v["bytes"] + v["webmBytes"] + v["previewBytes"] for v in manifest.values())
    print(f"videos total {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
