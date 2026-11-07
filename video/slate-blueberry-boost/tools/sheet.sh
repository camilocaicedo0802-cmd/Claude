#!/bin/bash
# sheet.sh input out.png  -> 6x2 grid of 12 frames evenly spaced, with timestamps
in="$1"; out="$2"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
n=12; step=$(python3 -c "print(max(0.2,$d/$n))")
ffmpeg -v error -y -i "$in" -vf "fps=1/$step,scale=160:284,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{pts\:hms}':x=3:y=3:fontsize=13:fontcolor=yellow:box=1:boxcolor=black,tile=6x2" -frames:v 1 "$out"
