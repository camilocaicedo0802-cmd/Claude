import sys, os
from PIL import Image
from rembg import new_session, remove
s = new_session('u2net_human_seg')
root, k, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
for i in range(k, 865, n):
    out = f'{root}/masks/{i:04d}.png'
    if os.path.exists(out): continue
    im = Image.open(f'{root}/frames/{i:04d}.jpg').convert('RGB').resize((720, 1280), Image.BILINEAR)
    remove(im, session=s, only_mask=True).save(out)
print('done', k)
