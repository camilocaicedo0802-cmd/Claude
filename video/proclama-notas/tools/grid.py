#!/usr/bin/env python3
"""grid.py out.jpg cols frames_per_clip tile_w file... : each clip a cell of k frames + label (name, dur)."""
import sys, subprocess, json, os
from io import BytesIO
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
out, cols, k, W = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); files = sys.argv[5:]
font = ImageFont.truetype('/home/user/notas/fonts/Poppins-Medium.ttf', 12)
def dur(f):
    r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',f],capture_output=True,text=True)
    try: return float(json.loads(r.stdout)['format']['duration'])
    except Exception: return 0
def frame(a):
    f, t = a
    r = subprocess.run(['ffmpeg','-v','error','-ss',f'{t:.2f}','-i',f,'-frames:v','1','-vf',f'scale={W}:{int(W*16/9)}:force_original_aspect_ratio=decrease,pad={W}:{int(W*16/9)}:(ow-iw)/2:(oh-ih)/2','-f','image2pipe','-vcodec','png','-'],capture_output=True)
    try: return Image.open(BytesIO(r.stdout)).convert('RGB')
    except Exception: return Image.new('RGB',(W,int(W*16/9)),(90,0,0))
H = int(W*16/9)
with Pool(4) as p:
    ds = p.map(dur, files)
    jobs = [(f, d*(i+0.5)/k) for f, d in zip(files, ds) for i in range(k)]
    ims = p.map(frame, jobs)
rows = (len(files)+cols-1)//cols; cw = W*k+6; ch = H+16
sheet = Image.new('RGB', (cols*cw, rows*ch), (15,15,15)); d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    x, y = (i%cols)*cw, (i//cols)*ch
    for j in range(k): sheet.paste(ims[i*k+j], (x+j*W, y+16))
    name = os.path.basename(f).replace('DJI_20260702','D').replace('.MP4','').replace('.MOV','')
    d.text((x+2, y), f'{name} {ds[i]:.0f}s', font=font, fill=(255,255,0))
sheet.save(out, quality=82); print(out, sheet.size)
