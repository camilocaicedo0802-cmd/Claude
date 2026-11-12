"""Person masks for every talking-head mezzanine (for the background defocus).

usage: python3 talk_masks.py <scratch> <work>
writes <work>/talk/<id>_mask.npy  (frames x 720 x 405, uint8, temporally smoothed)
"""
import sys, os, json, time
S, W = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(S, "mp"))
import numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

opts = vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=os.path.join(S, "models", "selfie_multiclass_256x256.tflite")),
    output_confidence_masks=True, output_category_mask=False)
seg = vision.ImageSegmenter.create_from_options(opts)
F = json.load(open(os.path.join(W, "talk_faces.json")))
for vid in sorted(F):
    dst = os.path.join(W, "talk", vid + "_mask.npy")
    if os.path.exists(dst):
        continue
    t0 = time.time()
    cap = cv2.VideoCapture(F[vid]["file"])
    out, prev = [], None
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        small = cv2.resize(fr, (540, 960), interpolation=cv2.INTER_AREA)
        res = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(small, cv2.COLOR_BGR2RGB)))
        m = 1.0 - np.squeeze(res.confidence_masks[0].numpy_view()).astype(np.float32)   # 1 - background
        m = cv2.resize(m, (405, 720), interpolation=cv2.INTER_AREA)
        prev = m if prev is None else prev * 0.45 + m * 0.55        # temporal smoothing against flicker
        out.append(np.clip(prev * 255 + 0.5, 0, 255).astype(np.uint8))
    np.save(dst, np.stack(out))
    print(vid, len(out), f"{time.time() - t0:.1f}s", flush=True)
os._exit(0)   # skip mediapipe's noisy shutdown
