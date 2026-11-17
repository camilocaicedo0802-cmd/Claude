"""Métodos de recorte de personas (alfa) para el primer plano."""
import numpy as np
import onnxruntime as ort

ROOT = "/home/user/Claude/video-editor/.models"
_sess = {}


def sess(path):
    if path not in _sess:
        so = ort.SessionOptions()
        so.intra_op_num_threads = 4
        # sin arena ni patrón de memoria: BiRefNet llegaba a 14 GB reservados entre fotogramas
        so.enable_cpu_mem_arena = False
        so.enable_mem_pattern = False
        _sess[path] = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
    return _sess[path]


def resize(img, w, h):
    """Bilineal separable (img HxW o HxWxC, float32)."""
    H, W = img.shape[:2]
    yi = np.linspace(0, H - 1, h); xi = np.linspace(0, W - 1, w)
    y0 = np.floor(yi).astype(int); y1 = np.minimum(y0 + 1, H - 1); wy = (yi - y0)
    x0 = np.floor(xi).astype(int); x1 = np.minimum(x0 + 1, W - 1); wx = (xi - x0)
    if img.ndim == 2:
        a = img[y0][:, x0] * (1 - wx) + img[y0][:, x1] * wx
        b = img[y1][:, x0] * (1 - wx) + img[y1][:, x1] * wx
        return (a * (1 - wy)[:, None] + b * wy[:, None]).astype(np.float32)
    a = img[y0][:, x0] * (1 - wx)[None, :, None] + img[y0][:, x1] * wx[None, :, None]
    b = img[y1][:, x0] * (1 - wx)[None, :, None] + img[y1][:, x1] * wx[None, :, None]
    return (a * (1 - wy)[:, None, None] + b * wy[:, None, None]).astype(np.float32)


def modnet(rgb, w=512, h=896):
    """rgb float32 0-1 HxWx3 -> alfa HxW."""
    x = resize(rgb, w, h)
    x = ((x - 0.5) / 0.5).transpose(2, 0, 1)[None].astype(np.float32)
    m = sess(f"{ROOT}/modnet/model.onnx").run(None, {"input": x})[0][0, 0]
    return resize(m, rgb.shape[1], rgb.shape[0])


def birefnet(rgb, model="birefnet/lite.onnx", size=1024):
    s = sess(f"{ROOT}/{model}")
    inp = s.get_inputs()[0]
    x = resize(rgb, size, size)
    x = ((x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32))
    x = x.transpose(2, 0, 1)[None]
    if "float16" in inp.type:
        x = x.astype(np.float16)
    out = s.run(None, {inp.name: x.astype(np.float16 if "float16" in inp.type else np.float32)})[-1]
    m = np.asarray(out, np.float32).reshape(size, size)
    if m.min() < 0 or m.max() > 1:
        m = 1 / (1 + np.exp(-m))
    return resize(m, rgb.shape[1], rgb.shape[0])


def box(img, r):
    """Filtro de caja de radio r con sumas acumuladas."""
    c = np.cumsum(np.cumsum(np.pad(img, ((1, 0), (1, 0))), 0), 1)
    H, W = img.shape
    y0 = np.clip(np.arange(H) - r, 0, H); y1 = np.clip(np.arange(H) + r + 1, 0, H)
    x0 = np.clip(np.arange(W) - r, 0, W); x1 = np.clip(np.arange(W) + r + 1, 0, W)
    s = c[y1][:, x1] - c[y0][:, x1] - c[y1][:, x0] + c[y0][:, x0]
    n = (y1 - y0)[:, None] * (x1 - x0)[None, :]
    return s / n


def guided(alpha, rgb, r=10, eps=2e-3):
    """Filtro guiado (He et al.) con la luminancia como guía: pega el borde del alfa
    a los contornos reales de la imagen (pelo, orejas)."""
    I = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]).astype(np.float64)
    p = alpha.astype(np.float64)
    mI = box(I, r); mp = box(p, r)
    cov = box(I * p, r) - mI * mp
    var = box(I * I, r) - mI * mI
    a = cov / (var + eps); b = mp - a * mI
    q = box(a, r) * I + box(b, r)
    return np.clip(q, 0, 1).astype(np.float32)


def fill_holes(alpha, thr=0.5):
    """Rellena huecos cerrados dentro de la silueta (relleno por inundación desde el borde)."""
    from scipy.ndimage import binary_fill_holes
    solid = binary_fill_holes(alpha > thr)
    return np.maximum(alpha, solid.astype(np.float32) * (alpha > 0.02))
