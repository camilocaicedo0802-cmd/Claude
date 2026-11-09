import sys, json, subprocess, numpy as np, cv2
src, wj = sys.argv[1], sys.argv[2]
W, H, FPS = 270, 480, 15
raw = subprocess.run(["ffmpeg","-v","error","-i",src,"-vf",f"fps={FPS},scale={W}:{H}","-f","rawvideo","-pix_fmt","gray","-"],capture_output=True).stdout
fr = np.frombuffer(raw,np.uint8).reshape(-1,H,W).astype(np.float32)
# template-track the face (eyes+glasses) to follow head motion, then measure mouth-box change
ref = fr[int(2*FPS)]
fx0,fy0,fx1,fy1 = 115,135,195,180     # glasses/eyes box at 270x480
tmpl = ref[fy0:fy1, fx0:fx1]
act = []
prev = None
for f in fr:
    r = cv2.matchTemplate(f, tmpl, cv2.TM_CCOEFF_NORMED); _,mv,_,ml = cv2.minMaxLoc(r)
    dx, dy = ml[0]-fx0, ml[1]-fy0
    mx0,my0 = 135+dx, 178+dy
    m = f[my0:my0+22, mx0:mx0+42] if mv > 0.4 else None
    if m is None or m.shape != (22,42) or prev is None or prev.shape != (22,42): act.append(0.0)
    else: act.append(float(np.abs(m-prev).mean()))
    prev = m
act = np.array(act); act = np.convolve(act, np.ones(3)/3, 'same')
ws = json.load(open(wj)); ph=[]; cur=[]
for w in ws:
    if cur and w['s']-cur[-1]['e']>0.35: ph.append(cur); cur=[]
    cur.append(w)
if cur: ph.append(cur)
base = np.percentile(act, 30)
for p in ph:
    print(" ".join(f"{w['w']}[{w['s']:.1f}:{act[int(w['s']*FPS):int(w['e']*FPS)+1].mean()/max(base,1e-3):.1f}]" for w in p))
