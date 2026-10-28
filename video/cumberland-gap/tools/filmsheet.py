import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
P, name, n = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 40
path = f"{P}/assets/vid/ia_{name}.mp4"
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout)
f = ImageFont.truetype(f"{P}/assets/fonts/Poppins-SemiBold.ttf", 16)
cols, tw, th = 8, 230, 172
rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 20)), (20, 20, 20))
d = ImageDraw.Draw(sheet)
for i in range(n):
    t = dur * (i + 0.5) / n
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-vf", f"scale={tw-6}:{th-6}:force_original_aspect_ratio=decrease", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    if not raw:
        continue
    import io
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    x, y = (i % cols) * tw, (i // cols) * (th + 20)
    sheet.paste(im, (x + 3, y + 3))
    d.text((x + 4, y + th - 2), f"{t:6.1f}s", font=f, fill=(255, 220, 80))
out = f"{P}/work/sheets/film_{name[:30]}.jpg"
sheet.save(out, quality=80)
print(out, round(dur, 1))
