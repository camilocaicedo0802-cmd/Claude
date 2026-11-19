"""CLAP (laion/clap-htsat-unfused) zero-shot mood/genre probabilities per track, averaged over 6 windows.
usage: python3 clap_rank.py out.json prompts.json files..."""
import sys, json, subprocess, numpy as np, torch
from transformers import ClapModel, ClapProcessor
torch.set_num_threads(4)
M = 'laion/clap-htsat-unfused'
m = ClapModel.from_pretrained(M).eval(); p = ClapProcessor.from_pretrained(M)
P = json.load(open(sys.argv[2])); names = list(P)
with torch.no_grad(): tf = m.get_text_features(**p(text=[P[k] for k in names], return_tensors='pt', padding=True))
tf = tf / tf.norm(dim=-1, keepdim=True)
out = {}
for f in sys.argv[3:]:
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.strip() or 0)
    prs = []
    for frac in (0.15, 0.3, 0.45, 0.6, 0.75, 0.9):
        a = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(dur * frac), '-t', '10', '-i', f, '-ac', '1', '-ar', '48000', '-f', 'f32le', '-'], capture_output=True).stdout
        x = np.frombuffer(a, np.float32).copy()
        if len(x) < 48000: continue
        with torch.no_grad(): af = m.get_audio_features(**p(audios=[x], sampling_rate=48000, return_tensors='pt'))
        af = af / af.norm(dim=-1, keepdim=True)
        prs.append(((af @ tf.T) * 100).softmax(-1)[0].numpy())
    pr = np.mean(prs, 0)
    out[f] = dict(dur=round(dur, 1), p={k: round(float(v), 3) for k, v in zip(names, pr)})
    print('.', end='', flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1); print()
