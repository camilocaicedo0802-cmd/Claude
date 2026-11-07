import sys, os
from PIL import Image
from rembg import new_session, remove
s = new_session('isnet-general-use')
for a, b in [(26, 62), (1176, 1212)]:
    for i in range(a, b):
        out = f'masks/{i:04d}.png'
        if os.path.exists(out): continue
        remove(Image.open(f'frames/{i:04d}.jpg').convert('RGB'), session=s, only_mask=True).save(out)
print('done')
