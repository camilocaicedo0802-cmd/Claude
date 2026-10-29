import sys, time
sys.path.insert(0, '.')
from PIL import Image
import render
times = [float(x) for x in sys.argv[2:]]
shots = render.build(1093.25)
cache = set()
t0 = time.time()
for T in times:
    fr = render.frame_at(shots, T, int(T * 30), cache)
    Image.fromarray(fr).resize((960, 540)).save(f"{sys.argv[1]}/s_{T:07.2f}.jpg", quality=82)
print('per frame', (time.time() - t0) / len(times))
