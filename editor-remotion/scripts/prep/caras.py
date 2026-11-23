import cv2, json, numpy as np, os
E=json.load(open("material/edl.json"))
d=os.path.join(os.path.dirname(cv2.__file__),"data")
front=cv2.CascadeClassifier(d+"/haarcascade_frontalface_default.xml"); prof=cv2.CascadeClassifier(d+"/haarcascade_profileface.xml")
res={}
for o in E:
    cap=cv2.VideoCapture("material/"+o["src"]); W=cap.get(3); H=cap.get(4); pts=[]
    for (a,b) in o["keep"]:
        for t in np.arange(a,b,0.3):
            cap.set(cv2.CAP_PROP_POS_MSEC,t*1000); ok,fr=cap.read()
            if not ok: continue
            sc=960/fr.shape[1] if fr.shape[1]>960 else 1.0
            g=cv2.cvtColor(cv2.resize(fr,None,fx=sc,fy=sc),cv2.COLOR_BGR2GRAY); best=None
            for det,flip in ((front,False),(prof,False),(prof,True)):
                gg=cv2.flip(g,1) if flip else g
                for (x,y,w,h) in det.detectMultiScale(gg,1.1,6,minSize=(int(g.shape[1]*0.07),)*2):
                    if flip: x=g.shape[1]-x-w
                    if y+h/2>g.shape[0]*0.7: continue
                    if best is None or w*h>best[2]*best[3]: best=(x,y,w,h)
                if best is not None: break
            if best: x,y,w,h=best; pts.append(((x+w/2)/sc/W,(y+h/2)/sc/H,w/sc/W))
    cap.release()
    if pts:
        P=np.array(pts); res[o["id"]]=dict(cx=round(float(np.median(P[:,0])),4),cy=round(float(np.median(P[:,1])),4),w=round(float(np.median(P[:,2])),4),n=len(pts),cx_rng=[round(float(P[:,0].min()),3),round(float(P[:,0].max()),3)],cy_rng=[round(float(P[:,1].min()),3),round(float(P[:,1].max()),3)],W=int(W),H=int(H))
    print(o["id"],res.get(o["id"]),flush=True)
json.dump(res,open("material/caras.json","w"),indent=1)
