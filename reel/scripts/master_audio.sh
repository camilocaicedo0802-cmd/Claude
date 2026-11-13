#!/usr/bin/env bash
# Masteriza el audio del render a -13 LUFS / -1 dBTP (loudnorm en dos pasadas) sin recodificar el vídeo.
# Uso: bash scripts/master_audio.sh out/render.mp4 out/final.mp4
set -euo pipefail
IN="$1"; OUT="$2"; I=-13; TP=-1; LRA=9
J=$(ffmpeg -hide_banner -i "$IN" -af "loudnorm=I=$I:TP=$TP:LRA=$LRA:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
get() { echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i "$IN" -c:v copy \
  -af "loudnorm=I=$I:TP=$TP:LRA=$LRA:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true,aresample=48000" \
  -c:a aac -b:a 320k -movflags +faststart "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak:"
