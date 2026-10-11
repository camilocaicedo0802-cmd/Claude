#!/usr/bin/env bash
# Render del vídeo + masterizado del audio (loudnorm 2 pasadas a -14 LUFS, pico real -1.5 dBTP).
# Uso: bash scripts/render.sh [salida.mp4]
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-out/cr7_final.mp4}"
RAW="out/cr7_raw.mp4"
mkdir -p out
npx remotion render CR7 "$RAW" --concurrency=4 --crf=18 --log=error
MEAS=$(ffmpeg -hide_banner -i "$RAW" -af loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
get() { echo "$MEAS" | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
ffmpeg -hide_banner -v error -y -i "$RAW" -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=7:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true,aresample=48000" \
  -c:a aac -b:a 256k -movflags +faststart "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tr -s ' '
echo "OK -> $OUT"
