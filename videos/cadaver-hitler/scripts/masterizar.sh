#!/usr/bin/env bash
# Normaliza el audio del render a -14 LUFS / -1.5 dBTP (estándar de Reels/TikTok) sin recodificar el video.
set -euo pipefail
entrada="$1"; salida="${2:-${1%.mp4}-final.mp4}"
ffmpeg -v error -y -i "$entrada" -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k -movflags +faststart "$salida"
echo "$salida"
