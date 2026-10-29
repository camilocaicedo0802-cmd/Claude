#!/bin/bash
P=$1; n=$2
f=$P/assets/vid/ia_$n.mp4
out=$P/work/scenes/$n.txt
[ -s "$out" ] && exit 0
ffmpeg -v info -i "$f" -vf "scale=320:-2,select='gt(scene,0.32)',showinfo" -an -f null - 2>&1 | grep -o "pts_time:[0-9.]*" | cut -d: -f2 | tr '\n' ' ' > "$out.tmp" && mv "$out.tmp" "$out"
echo "$n $(wc -w < $out)"
