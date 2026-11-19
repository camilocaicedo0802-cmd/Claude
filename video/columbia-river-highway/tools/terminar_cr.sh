#!/bin/bash
# Low-disk finishing chain: render chunks -> splice (deleting each chunk once used) -> 4 parts -> optimized file encoded
# from the parts themselves (no extra copy of the master; the master is removed once the parts exist).
# usage: PY=python3 setsid nohup bash tools/terminar_cr.sh PID_RENDER NOMBRE FRAMES > out/terminar.log 2>&1 < /dev/null &
set -e
PID=$1; NOMBRE=$2; FRAMES=$3; shift 3
while kill -0 "$PID" 2>/dev/null; do sleep 30; done
grep -q "wrote out/video_noaudio.txt" out/render.log
n=0; for c in $(sed -n "s/^file '\(.*\)'$/\1/p" out/video_noaudio.txt); do
  k=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of csv=p=0 "$c"); n=$((n + k)); done
echo "fotogramas $n"; [ "$n" -eq "$FRAMES" ]
RM_CHUNKS=1 ${PY:-python} edit/splice.py out/video_noaudio.txt out/mix.wav "out/${NOMBRE}_final.mp4" "$@"
rm -rf out/splice out/chunks
echo SPLICE_DONE
mkdir -p out/parts
${PY:-python} tools/split4.py "out/${NOMBRE}_final.mp4" out/parts "$NOMBRE"
echo PARTS_DONE
mkdir -p out/lite/src
i=0; for p in out/parts/*.mp4; do ln -sf "$(readlink -f "$p")" "out/lite/src/s_00$i.mp4"; i=$((i + 1)); done
touch out/lite/src/.done
ffmpeg -v error -y -i "out/${NOMBRE}_final.mp4" -map 0:a -c copy out/audio.m4a   # the master's audio, so the master can go
rm -f "out/${NOMBRE}_final.mp4"
bash tools/encode_optimizado.sh out/audio.m4a "out/${NOMBRE}_1080p_optimizado.mp4" out/lite
rm -rf out/lite/src out/lite/enc
echo ALL_DONE
