import sys, numpy as np, scipy.io.wavfile as wf
src, dst = sys.argv[1], sys.argv[2]
sr, a = wf.read(src); a = a.astype(np.float32) / 32768
if a.ndim == 2: a = a.mean(1)
k = int(0.02 * sr); env = np.sqrt(np.convolve(a ** 2, np.ones(k) / k, 'same'))
quiet = env < 10 ** (-40 / 20); n = len(a); keep = int(0.11 * sr)
runs = []; j = 0
while j < n:
    if quiet[j]:
        s = j
        while j < n and quiet[j]: j += 1
        if j - s > int(0.30 * sr): runs.append((s, j))
    else: j += 1
out = []; pos = 0
for s, e in runs:
    if s == 0: pos = max(0, e - int(0.05 * sr)); continue
    if e >= n: out.append(a[pos:s + keep]); pos = n; break
    out.append(a[pos:s + keep]); pos = e - keep
if pos < n: out.append(a[pos:])
xf = int(0.006 * sr); res = out[0]
for seg in out[1:]:
    res = np.concatenate([res[:-xf], res[-xf:] * np.linspace(1, 0, xf) + seg[:xf] * np.linspace(0, 1, xf), seg[xf:]])
wf.write(dst, sr, (res * 32767).astype(np.int16)); print('runs', len(runs), len(a) / sr, '->', len(res) / sr)
