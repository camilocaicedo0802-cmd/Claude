#!/usr/bin/env python3
"""Contact sheet: sheet.py out.jpg file1 [file2 ...] [--n 8] [--w 200] [--t0 a --t1 b]
Each file -> one row of n frames evenly spaced (alpha shown over checkerboard). Labels with time."""
import sys, subprocess, json, numpy as np
from PIL import Image, ImageDraw, ImageFont
args = sys.argv[1:]
def opt(name, default, cast=float):
    if name in args:
        i = args.index(name); v = cast(args[i+1]); del args[i:i+2]; return v
    return default
n = opt('--n', 8, int); W = opt('--w', 200, int); t0 = opt('--t0', None); t1 = opt('--t1', None)
out = args[0]; files = args[1:]
font = ImageFont.truetype('/home/user/notas/fonts/Poppins-Medium.ttf', 14)
rows = []
for f in files:
    p = json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,codec_type:stream_tags=rotate:stream_side_data=rotation','-of','json',f],capture_output=True,text=True).stdout)
    dur = float(p['format'].get('duration', 1))
    a = t0 if t0 is not None else 0; b = min(t1, dur) if t1 is not None else dur
    tiles = []
    for i in range(n):
        t = a + (b - a) * (i + 0.5) / n
        r = subprocess.run(['ffmpeg','-v','error','-ss',f'{t:.3f}','-i',f,'-frames:v','1','-vf',f'scale={W}:-2','-pix_fmt','rgba','-f','image2pipe','-vcodec','png','-'],capture_output=True)
        try:
            from io import BytesIO
            im = Image.open(BytesIO(r.stdout)).convert('RGBA')
        except Exception:
            im = Image.new('RGBA', (W, W), (80, 0, 0, 255))
        bg = Image.new('RGBA', im.size, (255,255,255,255)); d = ImageDraw.Draw(bg)
        for y in range(0, im.size[1], 16):
            for x in range(0, im.size[0], 16):
                if (x//16 + y//16) % 2: d.rectangle([x,y,x+15,y+15], fill=(190,190,190,255))
        bg.alpha_composite(im)
        d = ImageDraw.Draw(bg); d.rectangle([0,0,70,18], fill=(0,0,0,255)); d.text((3,0), f'{t:.1f}s', font=font, fill=(255,255,0,255))
        tiles.append(bg.convert('RGB'))
    h = max(t.size[1] for t in tiles)
    row = Image.new('RGB', (W*n, h + 22), (20,20,20))
    for i, t in enumerate(tiles): row.paste(t, (i*W, 22))
    ImageDraw.Draw(row).text((4,2), f'{f.split("/")[-1]}  ({dur:.1f}s)', font=font, fill=(255,255,255))
    rows.append(row)
H = sum(r.size[1] for r in rows); sheet = Image.new('RGB', (W*n, H), (0,0,0)); y = 0
for r in rows: sheet.paste(r, (0, y)); y += r.size[1]
sheet.save(out, quality=85); print(out, sheet.size)
