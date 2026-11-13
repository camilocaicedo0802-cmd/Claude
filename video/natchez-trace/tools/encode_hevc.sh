#!/bin/bash
# Archivo único en HEVC (H.265) 1080p a ≈2620 kb/s: más nítido a igual tamaño, por debajo de 400 MiB para ~19 min.
# Algunos Windows necesitan la extensión HEVC (VLC lo abre siempre). Por trozos y reanudable.
# usage: bash encode_hevc.sh MAESTRO.mp4 SALIDA.mp4 CARPETA_TRABAJO
set -e
F="$(readlink -f "$1")"; O="$(readlink -f "$2")"; W="$3"
mkdir -p "$W/src" "$W/enc"; cd "$W"
if [ ! -f src/.done ]; then
  ffmpeg -v error -y -i "$F" -map 0:v -c copy -f segment -segment_time 90 -reset_timestamps 1 src/s_%03d.mp4
  touch src/.done
fi
enc_one() {
  s=$1; b=$(basename $s .mp4); [ -f enc/$b.mp4 ] && return 0
  X="-c:v libx265 -preset medium -b:v 2620k -maxrate 8M -bufsize 16M -pix_fmt yuv420p -tag:v hvc1"
  ffmpeg -v error -y -i $s $X -x265-params pass=1:stats=$b.log:log-level=error -an -f null -
  ffmpeg -v error -y -i $s $X -x265-params pass=2:stats=$b.log:log-level=error -an enc/$b.tmp.mp4
  mv enc/$b.tmp.mp4 enc/$b.mp4; rm -f $b.log*; echo "trozo $b ok"
}
export -f enc_one
ls src/s_*.mp4 | xargs -P 2 -I{} bash -c 'enc_one {}'
ls enc/s_*.mp4 | grep -v tmp | sed "s/^/file '/;s/$/'/" > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -i "$F" -map 0:v -map 1:a -c copy -movflags +faststart "$O"
echo DONE
