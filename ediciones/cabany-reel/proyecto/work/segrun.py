import sys, os
from PIL import Image
from rembg import new_session, remove
s = new_session('isnet-general-use')
a, b = int(sys.argv[1]), int(sys.argv[2])
for i in range(a, b):
    out = f'masks/{i:04d}.png'
    if os.path.exists(out): continue
    img = Image.open(f'frames/{i:04d}.jpg').convert('RGB')
    remove(img, session=s, only_mask=True).save(out)
print('done')
