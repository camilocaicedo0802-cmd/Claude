#!/bin/bash
# Encadena todo lo que va después del render, para no perder tiempo entre pasos:
# espera al render (por PID, no por nombre), mezcla final, 4 partes y archivo único optimizado.
# usage (desde la carpeta del proyecto, en segundo plano):
#   setsid nohup bash tools/terminar.sh PID_RENDER NOMBRE FRAMES [T0 T1 ...] > out/terminar.log 2>&1 < /dev/null &
#   FRAMES = round(duración_locución * 30); T0 T1 = tramos a re-renderizar (opcional)
set -e
PID=$1; NOMBRE=$2; FRAMES=$3; shift 3
while kill -0 "$PID" 2>/dev/null; do sleep 30; done
grep -q "wrote out/video_noaudio.mp4" out/render.log
n=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of csv=p=0 out/video_noaudio.mp4)
echo "fotogramas $n"; [ "$n" -eq "$FRAMES" ]
rm -rf out/chunks
${PY:-python} edit/splice.py out/video_noaudio.mp4 out/mix.wav "out/${NOMBRE}_final.mp4" "$@"
rm -rf out/splice
echo SPLICE_DONE
mkdir -p out/parts
${PY:-python} tools/split4.py "out/${NOMBRE}_final.mp4" out/parts "$NOMBRE"
echo PARTS_DONE
bash tools/encode_optimizado.sh "out/${NOMBRE}_final.mp4" "out/${NOMBRE}_1080p_optimizado.mp4" out/lite
rm -rf out/lite/src out/lite/enc
echo ALL_DONE
