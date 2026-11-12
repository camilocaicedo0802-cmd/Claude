# Catalog media in a folder: probe + one thumbnail per file (3 frames for video), labeled sheets.
import subprocess, json, os, sys
from PIL import Image, ImageDraw, ImageFont
root = sys.argv[1]; tag = sys.argv[2]
outdir = f'/home/user/media-in/work/catalog/{tag}'; os.makedirs(outdir, exist_ok=True)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
items = []
for dp, dn, fn in os.walk(root):
    for f in sorted(fn):
        p = os.path.join(dp, f)
        ext = f.lower().rsplit('.',1)[-1]
        if ext not in ('mov','mp4','m4v','jpg','jpeg','png','heic','webp'): continue
        items.append(p)
items.sort()
cat = []
TW, TH = 180, 320
for i, p in enumerate(items):
    ext = p.lower().rsplit('.',1)[-1]
    info = {'id': f'{tag}{i:03d}', 'path': p}
    thumbs = []
    if ext in ('mov','mp4','m4v'):
        pr = json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,r_frame_rate,codec_type:stream_side_data=rotation','-of','json',p],capture_output=True,text=True).stdout or '{}')
        dur = float(pr.get('format',{}).get('duration',0) or 0)
        vs = [s for s in pr.get('streams',[]) if s.get('codec_type')=='video']
        if vs:
            s = vs[0]; rot = 0
            for sd in s.get('side_data_list',[]) or []:
                rot = sd.get('rotation', rot)
            w,h = s.get('width'), s.get('height')
            if abs(int(rot or 0)) == 90: w,h = h,w
            info.update(dur=round(dur,2), w=w, h=h, fps=s.get('r_frame_rate'))
        for k, frac in enumerate((0.15, 0.5, 0.85)):
            tp = f'{outdir}/{info["id"]}_{k}.jpg'
            subprocess.run(['ffmpeg','-v','error','-y','-ss',str(dur*frac),'-i',p,'-frames:v','1','-vf',f'scale={TW}:{TH}:force_original_aspect_ratio=decrease,pad={TW}:{TH}:(ow-iw)/2:(oh-ih)/2','-q:v','4',tp])
            if os.path.exists(tp): thumbs.append(tp)
    else:
        tp = f'{outdir}/{info["id"]}_0.jpg'
        subprocess.run(['ffmpeg','-v','error','-y','-i',p,'-frames:v','1','-vf',f'scale={TW}:{TH}:force_original_aspect_ratio=decrease,pad={TW}:{TH}:(ow-iw)/2:(oh-ih)/2','-q:v','4',tp])
        pr = json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','stream=width,height','-of','json',p],capture_output=True,text=True).stdout or '{}')
        ss = pr.get('streams',[{}])
        info.update(dur=0, w=ss[0].get('width') if ss else None, h=ss[0].get('height') if ss else None, image=True)
        if os.path.exists(tp): thumbs.append(tp)
    info['thumbs'] = thumbs
    cat.append(info)
json.dump(cat, open(f'{outdir}/catalog.json','w'), indent=1, ensure_ascii=False)
# sheets: each item = up to 3 thumbs side by side (video) ; 4 items per row, 3 rows per sheet
cellw, cellh = TW*3+6, TH+22
per_row, rows = 3, 3
for si in range(0, len(cat), per_row*rows):
    chunk = cat[si:si+per_row*rows]
    sheet = Image.new('RGB', (cellw*per_row, cellh*rows), 'black')
    d = ImageDraw.Draw(sheet)
    for j, it in enumerate(chunk):
        cx, cy = (j%per_row)*cellw, (j//per_row)*cellh
        for k, tp in enumerate(it['thumbs']):
            sheet.paste(Image.open(tp), (cx+k*(TW+2), cy+22))
        label = f"{it['id']} {it.get('dur',0)}s {it.get('w')}x{it.get('h')}"
        d.text((cx+4, cy+2), label, fill='yellow', font=font)
    sheet.save(f'{outdir}/sheet_{si//(per_row*rows):02d}.jpg', quality=80)
for it in cat: print(it['id'], it.get('dur'), it.get('w'), it.get('h'), it.get('fps'), os.path.relpath(it['path'], root))
