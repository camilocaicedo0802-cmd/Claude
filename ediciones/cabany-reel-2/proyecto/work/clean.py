"""Remove burned-in text from the raw Cabany clip (corrected raw: only the two URL overlays remain):
 - cut-off yellow/white subtitle letters on the right edge (all shots)
 - 'WWWcabanypanama.com' typing overlay on the home page (8.3-10.9 s)
 - 'www.cabanypanama.com.' typing overlay above the head in the last shot (26.4-29.3 s)
The camera is static in every talking shot, so text over the background is replaced by a
median 'clean plate' of the same shot; inside screen recordings it is inpainted."""
import functools, os
import numpy as np, cv2
from lib import ROOT

SHOTS = {  # name: (first, last) frame, frames used for the clean plate
    'door': (0, 79, list(range(0, 80, 2))),
    'balcony': (80, 230, list(range(82, 230, 3))),
    'selfie': (768, 932, list(range(768, 791)) + list(range(882, 933, 2))),
}
REGIONS = {  # (x0, y0, x1, y1) areas that carry burned-in text
    'door': [(930, 820, 1080, 1760)],
    'balcony': [(930, 820, 1080, 1760)],
    'selfie': [(930, 820, 1080, 1760), (0, 300, 1080, 545)],
}
def shot_of(i):
    for k, (a, b, _) in SHOTS.items():
        if a <= i <= b: return k
    return None

def _has_text(bgr):
    b = bgr[..., 0].astype(int); g = bgr[..., 1].astype(int); r = bgr[..., 2].astype(int)
    yel = (r > 185) & (g > 165) & (b < 120)
    wht = ((r > 215) & (g > 215) & (b > 215)).astype(np.uint8)
    blk = ((r < 60) & (g < 60) & (b < 60)).astype(np.uint8)
    wt = wht & cv2.dilate(blk, np.ones((9, 9), np.uint8))
    s = (yel | wt.astype(bool))[900:1700, 960:].sum()
    return s > 60

@functools.lru_cache(maxsize=4)
def plate(name):
    a, b, use = SHOTS[name]
    frames = [(i, cv2.imread(f'{ROOT}/frames/{i:04d}.jpg')) for i in use]
    clean = [f for i, f in frames if not _has_text(f)]
    if len(clean) < 5: clean = [f for _, f in frames]
    return np.median(np.stack(clean), axis=0).astype(np.uint8)  # BGR

@functools.lru_cache(maxsize=4)
def feather(name):
    m = np.zeros((1920, 1080), np.float32)
    for x0, y0, x1, y1 in REGIONS[name]:
        m[y0:y1, x0:x1] = 1
    return cv2.GaussianBlur(m, (0, 0), 14)

def person_mask(i):
    p = f'{ROOT}/masks/{i:04d}.png'
    if not os.path.exists(p): return None
    m = (cv2.imread(p, 0) > 140).astype(np.float32)
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    return cv2.GaussianBlur(m, (0, 0), 2)

def clean_talking(i, rgb):
    name = shot_of(i)
    if not name: return rgb
    pl = cv2.cvtColor(plate(name), cv2.COLOR_BGR2RGB).astype(np.float32)
    f = rgb.astype(np.float32)
    r = rgb[..., 0].astype(int); g = rgb[..., 1].astype(int); b = rgb[..., 2].astype(int)
    yel = ((r > 185) & (g > 165) & (b < 120)).astype(np.uint8)
    # white letters with a black outline (the other half of the stray subtitles)
    wht = ((r > 215) & (g > 215) & (b > 215)).astype(np.uint8)
    blk = ((r < 60) & (g < 60) & (b < 60)).astype(np.uint8)
    wtxt = wht & cv2.dilate(blk, np.ones((9, 9), np.uint8))
    txt = yel | wtxt
    txt[:] = 0          # corrected raw: no stray subtitle letters on the edge any more
    txt[:, :960] = 0; txt[:900] = 0; txt[1700:] = 0
    tm = cv2.dilate(txt, np.ones((33, 33), np.uint8)).astype(np.float32)
    if name == 'selfie' and 788 <= i <= 884:   # typed URL + leader line above the head
        d = (np.abs(f - pl).max(-1) > 18).astype(np.uint8)
        reg = np.zeros_like(d); reg[330:560, :] = 1
        tm = np.maximum(tm, cv2.dilate(d * reg, np.ones((13, 13), np.uint8)).astype(np.float32))
        tm[360:610, 110:270] = 1.0
    if tm.max() == 0: return rgb
    w = cv2.GaussianBlur(tm, (0, 0), 4)
    pm = person_mask(i)
    if pm is not None: w = w * (1 - pm)
    w = w[..., None]
    out = (f * (1 - w) + pl * w).clip(0, 255).astype(np.uint8)
    r = out[..., 0].astype(int); g = out[..., 1].astype(int); b = out[..., 2].astype(int)
    yel = ((r > 185) & (g > 165) & (b < 120)).astype(np.uint8); yel[:, :880] = 0
    if yel.sum() > 15:
        out = cv2.inpaint(out, cv2.dilate(yel, np.ones((17, 17), np.uint8)), 7, cv2.INPAINT_TELEA)
    return out

def clean_screen(i, rgb):
    out = rgb
    if 246 <= i <= 327:  # 'WWWcabanypanama.com' overlay on the home page
        x0, y0, x1, y1 = 150, 588, 935, 686
        reg = out[y0:y1, x0:x1]
        lum = reg.mean(-1)
        if np.percentile(lum, 60) > 235 and (lum < 120).mean() < 0.25:
            out = out.copy(); out[y0:y1, x0:x1] = np.uint8(255)
    b = out[..., 2].astype(int); g = out[..., 1].astype(int); r = out[..., 0].astype(int)
    yel = ((r > 185) & (g > 165) & (b < 120)).astype(np.uint8)
    yel[:, :1000] = 0; yel[:950] = 0; yel[1600:] = 0
    if yel.sum() > 25:
        mk = cv2.dilate(yel, np.ones((17, 17), np.uint8))
        out = cv2.inpaint(np.ascontiguousarray(out), mk, 7, cv2.INPAINT_TELEA)
    return out
