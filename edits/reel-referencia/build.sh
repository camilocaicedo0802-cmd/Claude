#!/bin/bash
# Usage: build.sh <scratchpad>
set -e
S=$1; cd $S; mkdir -p work/seg
# common look: soft filmic curve, slightly reduced saturation, gentle warm
LOOK="curves=all='0/0.025 0.25/0.235 0.5/0.5 0.75/0.77 1/0.975',eq=saturation=0.92,colorbalance=rs=0.015:bs=-0.015:rh=0.01:bh=-0.01"
declare -A G
G[v1]="colorchannelmixer=rr=0.95:gg=0.99:bb=1.10,eq=gamma=1.02"
G[v2]="eq=gamma=1.28:brightness=0.015:contrast=1.04,colorchannelmixer=rr=1.0:gg=0.96:bb=1.0"
G[v3]="colorchannelmixer=rr=0.98:bb=1.04,eq=gamma=1.04"
G[v4]="colorchannelmixer=rr=1.05:gg=0.93:bb=1.06,eq=gamma=1.30:brightness=0.01"
# name clip start frames extra
SEGS=(
"s1 v1 6.000 172 none"
"s2 v2 1.000 43 fadein"
"s3 v2 3.500 20 none"
"s4 v3 1.000 33 none"
"s5 v3 4.250 17 none"
"s6 v3 5.400 16 none"
"s7 v4 14.000 22 none"
"s8 v4 15.367 49 none"
)
for spec in "${SEGS[@]}"; do
  set -- $spec
  X=""; [ "$5" = fadein ] && X=",fade=t=in:st=0:d=0.2"
  ffmpeg -hide_banner -loglevel error -y -ss $3 -i dl/$2.mov -an \
    -vf "fps=30,scale=1080:1920:flags=lanczos,${G[$2]},$LOOK,format=yuv420p,setpts=PTS-STARTPTS$X" \
    -frames:v $4 -c:v libx264 -preset slow -crf 14 -r 30 work/seg/$1.mp4
  echo "$1 $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 work/seg/$1.mp4)"
done
printf "file '%s'\n" $S/work/seg/s{1..8}.mp4 > work/seg/list.txt
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i work/seg/list.txt -i work/ref.mp4 -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 30 -c:a copy -movflags +faststart -t 12.4 out/video_final.mp4
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,duration out/video_final.mp4
