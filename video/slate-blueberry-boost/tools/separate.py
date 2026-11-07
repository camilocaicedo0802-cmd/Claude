# Source separation with HTDemucs, weights loaded from safetensors (no pickle).
import sys, json, torch, numpy as np, soundfile as sf
from safetensors.torch import load_file
from demucs.htdemucs import HTDemucs
from demucs.apply import apply_model
cfg_path, w_path, wav_in, out_prefix = sys.argv[1:5]
cfg = json.load(open(cfg_path))
kw = cfg["kwargs"]
model = HTDemucs(**kw)
sd = {k[len("state."):] if k.startswith("state.") else k: v for k, v in load_file(w_path).items()}
missing, unexpected = model.load_state_dict(sd, strict=True)
print("missing", len(missing), "unexpected", len(unexpected))
model.eval()
x, sr = sf.read(wav_in, dtype="float32", always_2d=True)
assert sr == kw["samplerate"], sr
wav = torch.from_numpy(x.T.copy())
ref = wav.mean(0); m, s = ref.mean(), ref.std()
with torch.no_grad():
    out = apply_model(model, ((wav - m) / s)[None], shifts=2, split=True, overlap=0.25, progress=False)[0]
out = out * s + m
for name, src in zip(kw["sources"], out):
    sf.write(f"{out_prefix}_{name}.wav", src.numpy().T, sr, subtype="FLOAT")
print("ok", kw["sources"])
