# Caja de cabeza (con pelo) por segmento, en coordenadas 1080x1920 de la toma. Escribe src/caras.ts.
import json, re, subprocess, numpy as np, mediapipe as mp, os
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=mpt.BaseOptions(model_asset_path='/tmp/claude-0/-home-user-Claude/8ca66ad8-679a-5f1d-a671-bedcf5aab479/scratchpad/face_landmarker.task'), running_mode=vision.RunningMode.IMAGE, num_faces=1))
t = open(f'{root}/src/timeline.ts').read()
segs = json.loads(re.search(r'SEGMENTS: Segment\[\] = (\[.*?\]);', t, re.S).group(1))
W, H = 540, 960
out = {}
for s in segs:
    n = int(round((s['srcOut'] - s['srcIn']) * 30))
    raw = subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',f"{s['srcIn']:.3f}",'-i',f"{root}/public/clips/g4_{s['take']}.mp4",'-frames:v',str(n),'-vf',f'select=not(mod(n\\,3)),scale={W}:{H}','-vsync','vfr','-pix_fmt','rgb24','-f','rawvideo','-'],capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    bx = []
    for im in fr:
        r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(im)))
        if not r.face_landmarks: continue
        L = r.face_landmarks[0]; xs = [p.x for p in L]; ys = [p.y for p in L]; fh = max(ys) - min(ys)
        bx.append((min(xs)*1080, (min(ys)-0.35*fh)*1920, max(xs)*1080, max(ys)*1920))
    b = np.array(bx)
    out[s['idx']] = [round(float(v)) for v in (b[:,0].min(), b[:,1].min(), b[:,2].max(), b[:,3].max(), np.median((b[:,0]+b[:,2])/2), np.median((b[:,1]+b[:,3])/2))]
    print(s['idx'], s['take'], out[s['idx']], flush=True)
open(f'{root}/src/caras.ts','w').write('// Caja de cabeza+pelo por segmento: [x0, y0, x1, y1, centroX, centroY] (MediaPipe, 1080x1920).\nexport const CARAS: Record<number, number[]> = ' + json.dumps({int(k): v for k, v in out.items()}) + ';\n')
