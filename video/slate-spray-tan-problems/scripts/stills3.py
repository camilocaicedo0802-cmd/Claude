import sys, os, importlib.util, cv2, numpy as np
W, R, out = sys.argv[1], sys.argv[2], sys.argv[3]
times = [float(x) for x in sys.argv[4:]]
sys.argv = ["compose3.py", W, R, "/dev/null"]
spec = importlib.util.spec_from_file_location("compose", os.path.join(os.path.dirname(__file__), "compose3.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
tiles = []
for t in times:
    f = int(round(t * 30))
    img = C.overlay(C.finish(C.render(f), f), f)
    tiles.append(cv2.resize(img, (360, 640), interpolation=cv2.INTER_AREA))
    cv2.putText(tiles[-1], f"{t:.2f}", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
cols = 6
rows = [np.hstack(tiles[i:i + cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[i:i + cols]))) for i in range(0, len(tiles), cols)]
cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
