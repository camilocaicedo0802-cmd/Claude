import sys, os, json, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T, core as C
plan = json.load(open(C.ROOT + 'edit/int_plan.json'))
k = [i for i, s in enumerate(T.SHOTS) if 'before' in s][0]
s = T.SHOTS[k]
r = C.make_reader(s['src'], plan[str(k)])
after = r.at(s['src_in'])
before = cv2.imread(T.PH + 'before.png')
g1 = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY); g2 = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
sift = cv2.SIFT_create(6000)
k1, d1 = sift.detectAndCompute(g1, None); k2, d2 = sift.detectAndCompute(g2, None)
m = cv2.BFMatcher().knnMatch(d1, d2, k=2)
good = [a for a, b in m if a.distance < 0.72 * b.distance]
src = np.float32([k1[g.queryIdx].pt for g in good]); dst = np.float32([k2[g.trainIdx].pt for g in good])
print('matches', len(good))
Ms, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=12)
Hh, inh = cv2.findHomography(src, dst, cv2.RANSAC, 12)
print('similarity inliers', int(inl.sum()), Ms.round(3).tolist())
print('homography inliers', int(inh.sum()))
H, W = after.shape[:2]
ws = cv2.warpAffine(before, Ms, (W, H), borderMode=cv2.BORDER_REFLECT)
wh = cv2.warpPerspective(before, Hh, (W, H), borderMode=cv2.BORDER_REFLECT)
cv2.imwrite(T.PH + 'before_sim.png', ws); cv2.imwrite(T.PH + 'before_hom.png', wh)
cv2.imwrite(T.PH + 'after_ref.png', after)
def sm(x): return cv2.resize(x, (360, 640))
blend = lambda a, b: cv2.addWeighted(sm(a), 0.5, sm(b), 0.5, 0)
cv2.imwrite(C.ROOT + 'sheets/align.jpg', np.hstack([sm(before), sm(after), blend(ws, after), blend(wh, after)]))
