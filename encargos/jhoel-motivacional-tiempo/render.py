"""Render Jhoel reel 2 ("El tiempo es lo que menos sobra"): one driving shot + top text + music.

Usage: python3 -I render2.py <scratchpad_dir> <music> <music_start_s> <out.mp4>
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = Path(sys.argv[1])
MUSIC = sys.argv[2]
MUSIC_START = float(sys.argv[3])
OUT = Path(sys.argv[4])

WORK = S / "work2"
WORK.mkdir(exist_ok=True)
CLIP = S / "clips" / "drive_6925.mov"   # Drive: B rols/auto/IMG_6925.mov (60 fps, HLG)
FONT = S / "fonts" / "SofiaSansCond-500.ttf"
W, H, FPS = 1080, 1920, 30
TOTAL = 9.2                              # same length as the reference
SPEED = 6.08 / TOTAL                     # stretch the whole 6.08 s take over the reel

LINES = ["El tiempo es lo que menos sobra", "Tienes que jubilarte a los 30", "para ver a tus hijos crecer"]
BASELINES = [389, 482, 575]              # reference positions scaled from 720x1280
LINE1_WIDTH = 830                        # reference first-line width (553px @720)

HLG = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable,"
       "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=contrast=1.06:saturation=1.08")
# Dark, cool, slightly desaturated look closer to the night reference.
GRADE = ("curves=all='0/0 0.5/0.30 1/0.76',eq=saturation=0.82,"
         "colorbalance=bs=0.07:bm=0.04:rh=-0.03,vignette=PI/4.5")
COVER = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"


def run(cmd):
    subprocess.run(cmd, check=True)


def font_for_width():
    size = 40
    while ImageFont.truetype(str(FONT), size + 1).getlength(LINES[0]) <= LINE1_WIDTH:
        size += 1
    return ImageFont.truetype(str(FONT), size)


def render_overlay(path):
    """Top gradient (for legibility over the light headliner) + text with a soft shadow."""
    font = font_for_width()
    text = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(text)
    for line, y in zip(LINES, BASELINES):
        d.text((W / 2, y), line, font=font, fill=255, anchor="ms")
    shadow = text.filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.6))
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(int(H * 0.45)):
        gd.line([(0, y), (W, y)], fill=int(255 * 0.55 * (1 - y / (H * 0.45))))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste((0, 0, 0, 255), (0, 0), grad)
    img.paste((0, 0, 0, 255), (0, 2), shadow)
    img.paste((255, 255, 255, 255), (0, 0), text)
    img.save(path)


def main():
    overlay = WORK / "overlay.png"
    render_overlay(overlay)
    n = round(TOTAL * FPS)
    vf = (f"[0:v]{HLG},{GRADE},setpts=(PTS-STARTPTS)/{SPEED:.5f},fps={FPS},{COVER},"
          f"unsharp=5:5:0.35:5:5:0,setsar=1[v];[v][1:v]overlay=0:0[vo];"
          f"[2:a]afade=t=in:d=0.08,afade=t=out:st={TOTAL - 0.6}:d=0.6,"
          f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(CLIP), "-loop", "1", "-i", str(overlay),
         "-ss", str(MUSIC_START), "-t", str(TOTAL), "-i", MUSIC,
         "-filter_complex", vf, "-map", "[vo]", "-map", "[a]", "-frames:v", str(n), "-t", str(TOTAL),
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
         "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-colorspace", "bt709", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)])
    print(OUT)


if __name__ == "__main__":
    main()
