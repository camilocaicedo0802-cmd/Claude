import librosa, numpy as np, sys
base = sys.argv[1]
for stem in ["drums","other","bass","vocals"]:
    y, sr = librosa.load(f"{base}/{stem}.wav", sr=22050, mono=True)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
    db = 20*np.log10(np.maximum(rms,1e-9))
    print(f"== {stem}: overall RMS dBFS {20*np.log10(np.sqrt(np.mean(y**2))+1e-9):.1f}, peak {20*np.log10(np.max(np.abs(y))+1e-9):.1f}")
    on = librosa.onset.onset_detect(y=y, sr=sr, hop_length=512, backtrack=False, units='time', delta=0.12 if stem!='vocals' else 0.3)
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512)
    times = librosa.frames_to_time(np.arange(len(env)), sr=sr, hop_length=512)
    out=[]
    for t in on:
        i = np.argmin(np.abs(times-t))
        # spectral centroid near onset
        seg = y[int(t*sr):int((t+0.15)*sr)]
        if len(seg)<256: continue
        c = librosa.feature.spectral_centroid(y=seg, sr=sr).mean()
        lvl = 20*np.log10(np.sqrt(np.mean(seg**2))+1e-9)
        out.append(f"{t:.2f}s(c{int(c)}Hz,{lvl:.0f}dB)")
    if stem!='vocals': print(" ".join(out))
y, sr = librosa.load(f"{base}/bass.wav", sr=22050)
o, sr2 = librosa.load(f"{base}/other.wav", sr=22050)
d, _ = librosa.load(f"{base}/drums.wav", sr=22050)
m = y+o+d
tempo, beats = librosa.beat.beat_track(y=m, sr=sr, units='time')
print("tempo music (no vocals):", tempo, "beats:", np.round(beats,2))
chroma = librosa.feature.chroma_cqt(y=y+o, sr=sr).mean(axis=1)
names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
print("chroma rank:", [names[i] for i in np.argsort(chroma)[::-1][:6]])
