"""Render the Jhoel 'Motivacional Texto' reel: 9 B-roll shots + TikTok-style text + music.

Usage: python3 -I render.py <scratchpad_dir> <music_wav> <music_start_s> <out.mp4> [timing]
timing: 'beat' (cuts snapped to the provisional song's beats) or 'ref' (exact reference cuts).
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = Path(sys.argv[1])
MUSIC = sys.argv[2]
MUSIC_START = float(sys.argv[3])
OUT = Path(sys.argv[4])
TIMING = sys.argv[5] if len(sys.argv) > 5 else "beat"

CLIPS = S / "clips"
WORK = S / "work"
WORK.mkdir(exist_ok=True)
FONT = S / "fonts" / "TikTokSans-700.ttf"
W, H, FPS = 1080, 1920, 30
TOTAL = 12.4

# Cut points (seconds). 'ref' = cuts measured in the reference video;
# 'beat' = same cuts snapped to the beat grid of the provisional track.
CUTS = {
    "ref": [0, 1.8, 3.7, 5.333, 7.067, 8.167, 9.2, 10.3, 11.333, TOTAL],
    "beat": [0, 1.827, 3.824, 5.333, 7.330, 8.328, 9.327, 10.325, 11.324, TOTAL],
}[TIMING]

HLG = (
    "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable,"
    "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=contrast=1.06:saturation=1.08"
)
SDR = "format=yuv420p,eq=contrast=1.04:saturation=1.04"
COVER = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"

# (clip, in-point s, is_hlg, framing filter)
SHOTS = [
    ("gym_6502", 1.9, True, COVER),            # curl, dramatic side light
    ("gym_5956", 7.0, True, COVER),            # lat pulldown, shirtless back
    ("gym_8724", 0.4, True, COVER),            # silhouette vs skyline ("Sabes por qué?")
    ("paraca_5950", 0.0, False,                # skydive freefall: the drop
     f"crop=608:1080:541:0,scale={W}:{H}:flags=lanczos"),
    ("run_C0294", 0.4, False, COVER),          # running toward camera, trees
    ("avio_selfie2", 0.25, False, COVER),      # cockpit selfie over the city
    ("run_atardecer", 0.2, True, COVER),       # running on the bridge, dramatic sky
    ("avio_despegue", 37.3, True, COVER),      # takeoff: side window, ground dropping away
    ("run_C0292", 2.6, False, COVER),          # running past camera
]

TEXTS = [
    # (start, end, lines, baselines at 1080x1920)
    (0, CUTS[2], ["Los haters saben quién eres, pero tú no los", "conoces a ellos."], [953, 991]),
    (CUTS[2], CUTS[3], ["Sabes por qué?"], [991]),
    (CUTS[3], TOTAL, ["tú has hecho algo increíble y ellos", "no han hecho nada."], [973, 1009]),
]
FONT_SIZE = 32  # matches the reference line width (447px @720 -> ~670px @1080)


def run(cmd):
    subprocess.run(cmd, check=True)


def frame_index(t):
    return round(t * FPS)


def render_shots():
    parts = []
    for k, (name, t_in, hlg, framing) in enumerate(SHOTS):
        n = frame_index(CUTS[k + 1]) - frame_index(CUTS[k])
        out = WORK / f"shot{k}.mp4"
        vf = ",".join([HLG if hlg else SDR, framing, f"fps={FPS}",
                       "unsharp=5:5:0.35:5:5:0", "setsar=1"])
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(t_in), "-i", str(CLIPS / f"{name}.mov"),
             "-vf", vf, "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium",
             "-crf", "12", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
             "-color_trc", "bt709", "-colorspace", "bt709", "-r", str(FPS), str(out)])
        parts.append(out)
    concat = WORK / "concat.txt"
    concat.write_text("".join(f"file '{p}'\n" for p in parts))
    base = WORK / "base.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
         "-c", "copy", str(base)])
    return base


def render_text(lines, baselines, path):
    font = ImageFont.truetype(str(FONT), FONT_SIZE)
    text = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(text)
    for line, y in zip(lines, baselines):
        d.text((W / 2, y), line, font=font, fill=255, anchor="ms")
    # Soft, faint drop shadow like TikTok's classic text.
    shadow = text.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.45))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste((0, 0, 0, 255), (0, 1), shadow)
    img.paste((255, 255, 255, 255), (0, 0), text)
    img.save(path)


def finish(base):
    inputs = ["-i", str(base)]
    chain, last = [], "0:v"
    for k, (t0, t1, lines, baselines) in enumerate(TEXTS):
        png = WORK / f"text{k}.png"
        render_text(lines, baselines, png)
        inputs += ["-loop", "1", "-t", str(TOTAL), "-i", str(png)]
        tag = f"v{k}"
        chain.append(f"[{last}][{k + 1}:v]overlay=0:0:enable='gte(t,{t0})*lt(t,{t1})'[{tag}]")
        last = tag
    a = len(TEXTS) + 1
    inputs += ["-ss", str(MUSIC_START), "-t", str(TOTAL), "-i", MUSIC]
    chain.append(f"[{a}:a]afade=t=in:d=0.08,afade=t=out:st={TOTAL - 0.45}:d=0.45,"
                 "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain),
         "-map", f"[{last}]", "-map", "[a]", "-t", str(TOTAL),
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
         "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-colorspace", "bt709", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)])


if __name__ == "__main__":
    finish(render_shots())
    print(json.dumps({"out": str(OUT), "timing": TIMING, "cuts": CUTS}))
