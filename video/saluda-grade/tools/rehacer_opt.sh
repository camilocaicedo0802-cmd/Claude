#!/bin/bash
# Re-encode the optimized pieces whose frame count does not match their part (pass 1 and 2 with the same fps mode),
# then join them with the master's audio.
set -e
cd /home/user/sg/out/lite
X="-c:v libx264 -preset slow -b:v 2400k -maxrate 7M -bufsize 14M -pix_fmt yuv420p -threads 2 -fps_mode passthrough"
nf() { ffprobe -v error -count_packets -select_streams v:0 -show_entries stream=nb_read_packets -of csv=p=0 "$1"; }
redo() { b=$1; rm -f enc/$b.tmp.mp4 enc/$b.mp4 p_r_$b*
  ffmpeg -v error -y -i src/$b.mp4 $X -pass 1 -passlogfile p_r_$b -an -f null -
  ffmpeg -v error -y -i src/$b.mp4 $X -pass 2 -passlogfile p_r_$b -an enc/$b.tmp.mp4
  mv enc/$b.tmp.mp4 enc/$b.mp4; rm -f p_r_$b*; echo "rehecho $b"; }
redo s_000
while pgrep -f "enc_one src/s_003" >/dev/null; do sleep 15; done
for b in s_000 s_001 s_002 s_003; do
  a=$(nf src/$b.mp4); e=$( [ -f enc/$b.mp4 ] && nf enc/$b.mp4 || echo 0 ); echo "$b $a $e"
  [ "$a" = "$e" ] || redo $b
done
ls enc/s_*.mp4 | grep -v tmp | sed "s/^/file '/;s/$/'/" > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -i ../Saluda_Grade_final.mp4 -map 0:v -map 1:a -c copy -movflags +faststart ../Saluda_Grade_1080p_optimizado.mp4
rm -f p_s_00*
echo OPT_DONE
