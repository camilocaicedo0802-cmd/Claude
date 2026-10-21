import numpy as np, onnxruntime as ort
from PIL import Image
_sess = None
def matte(img, w=384, h=672):
    """Person alpha (0..1 float32, img size) via MODNet."""
    global _sess
    if _sess is None:
        so = ort.SessionOptions(); so.intra_op_num_threads = 4
        _sess = ort.InferenceSession(f'{__file__.rsplit("/",1)[0]}/models/Xenova_modnet/onnx/model.onnx', so)
    x = np.asarray(img.convert('RGB').resize((w, h), Image.BILINEAR), np.float32) / 127.5 - 1
    x = x.transpose(2, 0, 1)[None]
    m = _sess.run(None, {_sess.get_inputs()[0].name: x})[0][0, 0]
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(img.size, Image.BILINEAR), np.float32) / 255
