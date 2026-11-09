import sys, os
from PIL import Image
from rembg import new_session, remove
s = new_session('isnet-general-use')
root, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
for i in range(a, b):
    out = f'{root}/masks/{i:04d}.png'
    if os.path.exists(out): continue
    remove(Image.open(f'{root}/frames/{i:04d}.jpg').convert('RGB'), session=s, only_mask=True).save(out)
print('done', a, b)
