import numpy as np


def stabilize(seq, radius=2, sigma=22.0, passes=1):
    """Motion-aware temporal denoise of an alpha sequence (list/array of HxW uint8 or float).
    Neighbours that differ little from the current frame (noise/flicker) are averaged in;
    neighbours that differ a lot (real motion) get ~zero weight, so moving edges don't ghost."""
    a = np.asarray(seq, np.float32)
    for _ in range(passes):
        out = np.empty_like(a)
        n = len(a)
        for t in range(n):
            acc = a[t].copy()
            wsum = np.ones_like(acc)
            for k in range(-radius, radius + 1):
                if k == 0 or not (0 <= t + k < n):
                    continue
                d = a[t + k] - a[t]
                w = np.exp(-(d / sigma) ** 2) * (0.6 if abs(k) == 2 else 1.0)
                acc += w * a[t + k]
                wsum += w
            out[t] = acc / wsum
        a = out
    return np.clip(a + 0.5, 0, 255).astype(np.uint8)
