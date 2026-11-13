#!/bin/bash
# Archivo único optimizado: 1080p H.264 High, 2 pasadas a 2400 kb/s (≈350 MB para 19 min), se abre en cualquier equipo.
# Por trozos de 90 s y reanudable (si se reinicia el contenedor, se vuelve a lanzar y sigue donde iba).
# usage: bash encode_optimizado.sh MAESTRO.mp4 SALIDA.mp4 CARPETA_TRABAJO
set -e
F="$(readlink -f "$1")"; O="$(readlink -f "$2")"; W="$3"
mkdir -p "$W/src" "$W/enc"; cd "$W"
if [ ! -f src/.done ]; then
  ffmpeg -v error -y -i "$F" -map 0:v -c copy -f segment -segment_time 90 -reset_timestamps 1 src/s_%03d.mp4
  touch src/.done
fi
enc_one() {
  s=$1; b=$(basename $s .mp4); [ -f enc/$b.mp4 ] && return 0
  X="-c:v libx264 -preset slow -b:v 2400k -maxrate 7M -bufsize 14M -pix_fmt yuv420p -threads 2"
  ffmpeg -v error -y -i $s $X -pass 1 -passlogfile p_$b -an -f null -
  ffmpeg -v error -y -i $s $X -pass 2 -passlogfile p_$b -an enc/$b.tmp.mp4
  mv enc/$b.tmp.mp4 enc/$b.mp4; rm -f p_$b*; echo "trozo $b ok"
}
export -f enc_one
ls src/s_*.mp4 | xargs -P 2 -I{} bash -c 'enc_one {}'
ls enc/s_*.mp4 | grep -v tmp | sed "s/^/file '/;s/$/'/" > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -i "$F" -map 0:v -map 1:a -c copy -movflags +faststart "$O"
echo DONE
