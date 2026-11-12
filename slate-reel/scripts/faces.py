import cv2, json, sys, glob, os, subprocess, numpy as np
casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
out = {}
for f in sorted(glob.glob('/home/user/media-in/raw/*.MOV')):
    name = os.path.basename(f)
    # decode at 5 fps, 540x960 (autorotated)
    cmd = ['ffmpeg','-v','error','-i',f,'-vf','fps=5,scale=540:960','-f','rawvideo','-pix_fmt','bgr24','-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw)//(540*960*3)
    frames = np.frombuffer(raw, np.uint8)[:n*540*960*3].reshape(n,960,540,3)
    res = []
    for i, fr in enumerate(frames):
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        fs = casc.detectMultiScale(g, 1.08, 5, minSize=(14,14))
        if len(fs):
            x,y,w,h = max(fs, key=lambda r: r[2]*r[3])
            res.append([round(i/5,2), int(x+w/2)*4, int(y+h/2)*4, int(w)*4])  # in 2160x3840 coords
        else:
            res.append([round(i/5,2), None, None, None])
    out[name] = res
    print(name, ' '.join(f"{r[0]}:{r[1]},{r[2]},{r[3]}" for r in res[::3]))
json.dump(out, open('/home/user/media-in/work/faces.json','w'))
