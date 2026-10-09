#!/usr/bin/env bash
# Día 2: el crudo (DJI Osmo Pocket 3) es HEVC 10 bits a 59,94 fps. Se pasa a 30 fps CFR 8 bits
# para cortar a fotograma exacto, y de la toma de apoyo se sacan tres fragmentos cortos (perfil, frente, espalda).
# Uso: scripts/dia2/convertir.sh <crudo.mp4> <apoyo.mp4> <carpeta_salida>
set -euo pipefail
crudo=$1; apoyo=$2; out=$3; pub="$(dirname "$0")/../../public/dia2"
mkdir -p "$out" "$pub"
ffmpeg -v error -y -i "$crudo" -map 0:v:0 -map 0:a:0 -vf fps=30 -c:v libx264 -preset fast -crf 14 -pix_fmt yuv420p -g 30 -c:a pcm_s16le "$out/crudo30.mov"
# Fragmentos de apoyo (segundos de la toma): pose estable, sin girar ni mover el pelo
corta() { ffmpeg -v error -y -ss "$2" -t "$3" -i "$apoyo" -map 0:v:0 -vf fps=30 -an -c:v libx264 -preset slow -crf 15 -pix_fmt yuv420p -movflags +faststart "$pub/apoyo_$1.mp4"; }
corta perfil 16.45 1.6
corta frente 3.30 1.6
corta espalda 13.40 2.0
