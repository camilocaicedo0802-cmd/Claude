#!/bin/bash
# qa.sh final.mp4 outdir : mid-frame of every shot + probe
F=$1; O=$2; mkdir -p $O; rm -f $O/s_*.png
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,sample_rate,channels -of compact $F
for t in $(python3 -c "
import sys; sys.path.insert(0,'$3')
import os; os.environ.setdefault('DRIVE','')
import timeline as T
print(' '.join(f'{(s[\"t0\"]+s[\"t1\"])/2:.2f}' for s in T.SHOTS))"); do
  ffmpeg -v error -y -ss $t -i $F -frames:v 1 $O/s_$(printf %06.2f $t).png
done
