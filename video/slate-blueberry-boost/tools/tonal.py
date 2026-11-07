import sys, librosa, numpy as np, soundfile as sf, scipy.ndimage as nd, scipy.signal as ss
src, t0, dur, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
thr = float(sys.argv[5]) if len(sys.argv) > 5 else 4.0
y, sr = sf.read(src, dtype='float32'); y = y.T
y = y[:, int(t0*sr):int((t0+dur)*sr)]
n_fft = 8192; hop = 256
Ds = [librosa.stft(c, n_fft=n_fft, hop_length=hop) for c in y]
M = np.abs(Ds[0]) + np.abs(Ds[1])
loc = nd.median_filter(M, size=(81, 1))           # local spectral floor
peak = (M > thr * loc) & (M == nd.maximum_filter(M, size=(5, 1)))
peak = nd.binary_dilation(peak, structure=np.ones((5, 1)))
mask = nd.uniform_filter(peak.astype(np.float32), size=(1, 9))  # temporal smoothing
mask = nd.binary_opening(mask > 0.5, structure=np.ones((1, 7))).astype(np.float32)  # need sustained partials
mask = nd.uniform_filter(mask, size=(3, 5))
outw = np.stack([librosa.istft(D * mask, hop_length=hop, length=y.shape[1]) for D in Ds])
sos = ss.butter(4, 500/(sr/2), 'high', output='sos'); outw = ss.sosfiltfilt(sos, outw, axis=1)
n = outw.shape[1]; f = np.ones(n); fi = int(0.004*sr); fo = int(0.15*sr)
f[:fi] = np.linspace(0, 1, fi); f[-fo:] = np.linspace(1, 0, fo)
outw *= f
pk = np.abs(outw).max(); outw = outw / pk * 0.89
sf.write(out, outw.T, sr, subtype='PCM_24'); print(out, 'peak_in_dB', 20*np.log10(pk))
