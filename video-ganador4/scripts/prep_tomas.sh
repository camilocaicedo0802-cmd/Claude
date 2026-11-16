#!/bin/bash
# Proxies 1080x1920 sin ajuste de color + transcripción Whisper (palabra a palabra) + alineación forzada.
# uso: scripts/prep_tomas.sh 4846 4863 4843
S=/tmp/claude-0/-home-user-Claude/8ca66ad8-679a-5f1d-a671-bedcf5aab479/scratchpad
P=/home/user/Claude/video-ganador4
for n in "$@"; do
  out=$P/public/clips/g4_$n.mp4
  [ -s $out ] || ffmpeg -nostdin -v error -y -i $S/wt/files/IMG_$n.MOV -vf "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p" -c:v libx264 -preset medium -crf 17 -g 15 -c:a aac -b:a 192k -ar 48000 $out
  echo "proxy $n ok"
done
for n in "$@"; do
  HF_HOME=$S/hf $S/venv/bin/python -I $S/scripts/tx_words.py $P/public/clips/g4_$n.mp4 $P/transcripciones/g4_$n.json medium 2>&1 | grep -v Warning | cut -c1-400
  TORCH_HOME=$S/torch $S/venv/bin/python -I $S/scripts/align.py $P/public/clips/g4_$n.mp4 $P/transcripciones/g4_$n.json $P/transcripciones/g4_${n}_alineado.json '{}' 2>&1 | grep -v Warn
  echo "tx $n ok"
done
echo ALLDONE
