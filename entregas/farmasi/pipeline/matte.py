import numpy as np, onnxruntime as ort, time
from PIL import Image
_s = {}
def sess(name):
    if name not in _s:
        o = ort.SessionOptions(); o.intra_op_num_threads = 4; o.enable_cpu_mem_arena = False
        _s[name] = ort.InferenceSession(f"models/{name}.onnx", o)
    return _s[name]
def modnet(img):
    w, h = img.size
    nw, nh = 512, int(round(512 * h / w / 32)) * 32
    x = np.asarray(img.convert("RGB").resize((nw, nh), Image.BILINEAR), np.float32) / 255
    x = ((x - 0.5) / 0.5).transpose(2, 0, 1)[None]
    a = sess("modnet").run(None, {"input": x})[0][0, 0]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
def birefnet(img):
    w, h = img.size
    x = np.asarray(img.convert("RGB").resize((1024, 1024), Image.BILINEAR), np.float32) / 255
    x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).astype(np.float32).transpose(2, 0, 1)[None]
    a = sess("birefnet_lite").run(None, {"input_image": x})[0][0, 0]
    a = 1 / (1 + np.exp(-a)) if a.min() < 0 or a.max() > 1 else a
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
