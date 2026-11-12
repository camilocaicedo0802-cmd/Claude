#!/usr/bin/env bash
# Recorta y etaloniza los b-roll elegidos. Formato: nombre|archivo origen|inicio|duración
set -euo pipefail
B1=/home/user/media-in/broll1; B2=/home/user/media-in/broll2
OUT=/home/user/Claude/slate-reel/public/broll
GRADE="colorbalance=rs=0.02:bs=-0.03:rm=0.04:gm=0.01:bm=-0.05:rh=0.02:bh=-0.03,eq=saturation=1.06:contrast=1.03:gamma=1.02,curves=master='0/0.02 0.5/0.52 0.92/0.9 1/0.95'"
mkdir -p "$OUT"
while IFS='|' read -r name src ss dur; do
  [ -z "$name" ] && continue
  ffmpeg -nostdin -v error -y -ss "$ss" -t "$dur" -i "$src" -an \
    -vf "fps=30,scale=1440:2560:force_original_aspect_ratio=increase:flags=lanczos,crop=1440:2560,$GRADE,format=yuv420p" \
    -c:v libx264 -preset medium -crf 17 -g 15 -movflags +faststart "$OUT/$name.mp4"
  echo "$name ok"
done <<LIST
hook_spray_face|$B1/Spray tan 3/Videos/Proceso/MVI_4551.MP4|0.0|3.0
spray_abs|$B1/Spray tan 2/Videos/Proceso/IMG_1965.MOV|0.5|3.0
xmas_arms_up|$B1/Spray tan 3/Videos/Proceso/MVI_4548.MP4|3.0|3.0
newyear_result|$B1/Spray Tan 1/spray tan 1 - B roll despues/IMG_4149.MOV|0.3|3.0
book_slate_gun|$B1/Spray Tan 1/spray tan 1 - B roll proceso/IMG_4102.MOV|0.0|3.0
develop_tanline|$B1/Spray Tan 1/spray tan 1 - B roll despues/IMG_4123.mov|2.0|3.0
result_strap|$B1/Spray tan 3/Videos/Después/IMG_2209.MOV|5.6|2.0
result_smile_tanline|$B1/Spray Tan 1/spray tan 1 - B roll despues/IMG_4122.mov|5.0|2.0
result_glow_face|$B1/Spray tan 3/Videos/Después/IMG_2211.MOV|5.2|2.0
endcard_reception|$B2/IMG_0798.MOV|0.0|3.5
LIST
ls -la "$OUT"
