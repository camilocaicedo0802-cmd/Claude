#!/usr/bin/env bash
# YA NO SE USA (el cliente pidió la voz original sin procesar). Se conserva como referencia.
# Masterizaba el render de Remotion: sonoridad a -10,5 LUFS (igual que la referencia),
# picos verdaderos <= -1 dBTP (loudnorm en dos pasadas). El vídeo se copia sin recodificar.
# Uso: scripts/master.sh <entrada.mp4> <salida.mp4>
set -euo pipefail
in="$1"; out="$2"
pre="volume=3dB,alimiter=limit=0.708:attack=2:release=60:level=false"
stats=$(ffmpeg -hide_banner -i "$in" -af $pre,loudnorm=I=-10.5:TP=-1.0:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
get() { echo "$stats" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i "$in" -c:v copy -af "$pre,loudnorm=I=-10.5:TP=-1.0:LRA=9:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true,aresample=48000" -c:a aac -b:a 320k -movflags +faststart "$out"
ffmpeg -hide_banner -i "$out" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:|LRA:)" | head -3
