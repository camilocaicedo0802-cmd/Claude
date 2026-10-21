import numpy as np, subprocess, sys
def load(p, sr=22050):
    return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(sr),'-f','s16le','-'],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def onset_env(x, sr=22050, hop=512):
    n = 2048; w = np.hanning(n)
    frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * w
    S = np.abs(np.fft.rfft(frames, axis=1))
    S = np.log1p(100 * S)
    flux = np.maximum(0, np.diff(S, axis=0)).sum(1)
    return flux - np.convolve(flux, np.ones(16)/16, 'same'), sr / hop
def tempo(env, fps, lo=80, hi=200):
    e = env - env.mean(); ac = np.correlate(e, e, 'full')[len(e)-1:]; ac /= ac[0] + 1e-9
    lags = np.arange(len(ac)); bpm = 60 * fps / np.maximum(lags, 1)
    m = (bpm >= lo) & (bpm <= hi)
    i = np.argmax(np.where(m, ac, -1)); return bpm[i], ac[i]
for p in sys.argv[1:]:
    x = load(p); win = 10
    out = []
    for t0 in range(0, max(1, int(len(x)/22050) - win + 1), 5):
        seg = x[t0*22050:(t0+win)*22050]
        env, fps = onset_env(seg); b, s = tempo(env, fps)
        out.append((t0, round(b), round(s, 2), round(20*np.log10(np.sqrt(np.mean(seg**2))+1e-9), 1)))
    best = max(out, key=lambda r: r[2])
    print(p.split('/')[-1][:12], 'best window', best, '| all strengths', [r[2] for r in out])
