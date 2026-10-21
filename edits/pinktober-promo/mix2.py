import json, subprocess, sys
S = sys.argv[1]; OUT = sys.argv[2]
tl = json.load(open(f'{S}/work/timeline.json'))
END = tl['end_t']; TOTAL = 15.0
VO_IN, VO_OUT = 0.48, 14.28          # "Dance for a cause ... survivors and thrivers"
fc = [
    f'[0:a]atrim={VO_IN}:{VO_OUT},asetpts=PTS-STARTPTS,afade=t=out:st={VO_OUT-VO_IN-0.05:.3f}:d=0.05,'
    'highpass=f=90,equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-18dB:ratio=3:attack=4:release=60,'
    'loudnorm=I=-15:TP=-1.5:LRA=6,aresample=48000,asplit=2[vo][key]',
    '[1:a]aresample=48000,volume=0.9[mus0]',
    # duck the music under the voice, release into the end card
    '[mus0][key]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=280:makeup=1[mus]',
]
sfx = []
for t, tr in zip(tl['cuts'], tl['trans']):
    if tr == 'whip': sfx.append((2, t - 0.14, 0.32))
    if tr == 'glitch': sfx.append((2, t - 0.10, 0.22))
sfx += [(3, tl['pinktober'], 0.55), (3, END, 0.7), (4, END - 1.0, 0.35), (5, END + 0.75, 0.6)]
labels = []
for j, (idx, t, vol) in enumerate(sfx):
    ms = max(0, int(t * 1000))
    fc.append(f'[{idx}:a]aresample=48000,adelay={ms}|{ms},volume={vol}[s{j}]'); labels.append(f'[s{j}]')
fc.append('[vo]apad[vop];[vop][mus]' + ''.join(labels) + f'amix=inputs={2+len(labels)}:normalize=0:duration=longest,'
          f'atrim=0:{TOTAL},alimiter=limit=0.94,loudnorm=I=-14:TP=-1:LRA=9,aresample=48000[aout]')
open(f'{S}/work/mix2_fc.txt', 'w').write(';\n'.join(fc))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{S}/raw/vo.m4a', '-i', f'{S}/sfx/music.wav', '-i', f'{S}/sfx/whoosh.wav',
                '-i', f'{S}/sfx/boom.wav', '-i', f'{S}/sfx/riser.wav', '-i', f'{S}/sfx/sparkle.wav',
                '-filter_complex_script', f'{S}/work/mix2_fc.txt', '-map', '[aout]', '-t', str(TOTAL), f'{S}/work/mix2.wav'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{S}/work/v2_noaudio.mp4', '-i', f'{S}/work/mix2.wav', '-map', '0:v', '-map', '1:a',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', str(TOTAL), OUT], check=True)
print('sfx', sfx)
