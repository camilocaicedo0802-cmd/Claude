import json, subprocess, sys
S = sys.argv[1]; OUT = sys.argv[2]
sys.path.insert(0, S)
tl = json.load(open(f'{S}/work/timeline.json'))
SEGS = [(5.73, 7.85), (8.60, 9.46), (25.76, 30.50), (13.42, 15.54), (33.62, 36.60), (44.72, 46.74), (56.76, 57.44)]
TR = [None, 'cut', 'whip', 'whip', 'punch', 'whip', 'punch']
SPEED = 1.033
total = tl['total']; starts = tl['starts']
keys = {k[2]: k[0] for k in tl['keys']}
fc = []
# voice: each segment with tiny fades, sped up, concatenated
for i, (a, b) in enumerate(SEGS):
    d = b - a
    fc.append(f'[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.02:.3f}:d=0.02,atempo={SPEED}[v{i}]')
fc.append(''.join(f'[v{i}]' for i in range(len(SEGS))) + f'concat=n={len(SEGS)}:v=0:a=1,highpass=f=80,'
          'acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-15:TP=-1.5:LRA=7,aresample=48000[voice]')
# music bed: soft, fade at end
fc.append(f'[1:a]atrim=0:{total:.3f},aresample=48000,volume=0.30,afade=t=out:st={total-1.0:.3f}:d=1.0[mus]')
sfx = []  # (input_idx, time, vol)
for i, t in enumerate(TR):
    if t in ('whip', 'punch'): sfx.append((2, starts[i] - 0.18, 0.55 if t == 'whip' else 0.35))
for w in ['beautiful', 'ceramic', 'Cecilia', 'gift bag', 'favorite']:
    sfx.append((3, keys[w], 0.35))
sfx.append((5, keys['one-of-a-kind'], 0.45))
sfx.append((4, keys['Get one'], 0.55))
labels = []
for j, (idx, t, vol) in enumerate(sfx):
    ms = max(0, int(t * 1000))
    fc.append(f'[{idx}:a]aresample=48000,adelay={ms}|{ms},volume={vol}[s{j}]'); labels.append(f'[s{j}]')
fc.append('[voice][mus]' + ''.join(labels) + f'amix=inputs={2+len(labels)}:normalize=0:duration=first,'
          f'alimiter=limit=0.95,apad,atrim=0:{total:.3f}[aout]')
open(f'{S}/work/mix_fc.txt', 'w').write(';\n'.join(fc))
cmd = ['ffmpeg', '-v', 'error', '-y', '-i', f'{S}/work/full48.wav', '-i', f'{S}/sfx/music.wav',
       '-i', f'{S}/sfx/whoosh.wav', '-i', f'{S}/sfx/pop.wav', '-i', f'{S}/sfx/ding.wav', '-i', f'{S}/sfx/sparkle.wav',
       '-filter_complex_script', f'{S}/work/mix_fc.txt', '-map', '[aout]', f'{S}/work/mix.wav']
subprocess.run(cmd, check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{S}/work/video_noaudio.mp4', '-i', f'{S}/work/mix.wav',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-movflags', '+faststart', OUT], check=True)
print('ok', sfx)
