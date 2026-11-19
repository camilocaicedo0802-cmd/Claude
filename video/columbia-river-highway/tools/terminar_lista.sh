#!/bin/bash
# Like terminar.sh, for a render written as a chunk list (render.py out/video_noaudio.txt): no concatenated copy on disk.
# usage: setsid nohup bash tools/terminar_lista.sh PID_RENDER NOMBRE FRAMES > out/terminar.log 2>&1 < /dev/null &
set -e
PID=$1; NOMBRE=$2; FRAMES=$3; shift 3
while kill -0 "$PID" 2>/dev/null; do sleep 30; done
grep -q "wrote out/video_noaudio.txt" out/render.log
n=0; for c in $(sed -n "s/^file '\(.*\)'$/\1/p" out/video_noaudio.txt); do
  k=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of csv=p=0 "$c"); n=$((n + k)); done
echo "fotogramas $n"; [ "$n" -eq "$FRAMES" ]
${PY:-python} edit/splice.py out/video_noaudio.txt out/mix.wav "out/${NOMBRE}_final.mp4" "$@"
rm -rf out/splice
echo SPLICE_DONE
mkdir -p out/parts
${PY:-python} tools/split4.py "out/${NOMBRE}_final.mp4" out/parts "$NOMBRE"
echo PARTS_DONE
rm -rf out/chunks
bash tools/encode_optimizado.sh "out/${NOMBRE}_final.mp4" "out/${NOMBRE}_1080p_optimizado.mp4" out/lite
rm -rf out/lite/src out/lite/enc
echo ALL_DONE
