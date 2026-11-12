#!/usr/bin/env bash
# Prepara las tomas a cámara: 30 fps, 2160x3840 H.264, etalonaje cálido y voz tratada (-16 LUFS).
set -euo pipefail
SRC=/home/user/media-in/raw
OUT=/home/user/Claude/slate-reel/public/raw
GRADE="colorbalance=rs=0.02:bs=-0.03:rm=0.04:gm=0.01:bm=-0.05:rh=0.02:bh=-0.03,eq=saturation=1.06:contrast=1.03:gamma=1.02,curves=master='0/0.02 0.5/0.52 0.92/0.9 1/0.95'"
AF="highpass=f=80,deesser=i=0.4,acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=2"
mkdir -p "$OUT"
for f in "$SRC"/*.MOV; do
  n=$(basename "$f" .MOV)
  m=$(ffmpeg -nostdin -hide_banner -i "$f" -vn -af "$AF,loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  ii=$(echo "$m" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
  read I TP LRA TH OFF <<<"$ii"
  ffmpeg -nostdin -v error -y -i "$f" \
    -vf "fps=30,scale=2160:3840:flags=lanczos,$GRADE,format=yuv420p" \
    -c:v libx264 -preset medium -crf 17 -g 15 \
    -af "$AF,loudnorm=I=-16:TP=-1.5:LRA=7:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$TH:offset=$OFF:linear=true,aresample=48000" \
    -c:a aac -b:a 192k -movflags +faststart "$OUT/$n.mp4"
  echo "$n listo (entrada $I LUFS)"
done
