#!/usr/bin/env bash
# Masteriza el audio del render (limitador + objetivo de sonoridad) sin recodificar el vídeo,
# y crea una copia ligera para enviar/previsualizar si el original supera ~30 MB.
#   bash finalize.sh video/out/video.mp4 render/video_v1.mp4 [-14]
set -euo pipefail
IN="$1"; OUT="$2"; TARGET="${3:--14}"
mkdir -p "$(dirname "$OUT")"
I=$(ffmpeg -i "$IN" -af ebur128 -f null - 2>&1 | awk '/Summary/{s=1} s&&/I:/{print $2; exit}')
GAIN=$(python3 -c "print(round(${TARGET} - (${I}), 2))")
ffmpeg -v error -y -i "$IN" -c:v copy \
  -af "volume=${GAIN}dB,alimiter=limit=0.85:attack=2:release=60:level=disabled" \
  -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "Sonoridad antes: ${I} LUFS · ganancia aplicada: ${GAIN} dB"
ffmpeg -i "$OUT" -af "ebur128=peak=true" -f null - 2>&1 | awk '/Summary/{s=1} s&&/I:|Peak:/{print "  "$0}'
SIZE=$(stat -c %s "$OUT")
if [ "$SIZE" -gt 30000000 ]; then
  PREV="${OUT%.mp4}_preview.mp4"
  ffmpeg -v error -y -i "$OUT" -c:v libx264 -crf 25 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart "$PREV"
  echo "Copia ligera: $PREV ($(du -h "$PREV" | cut -f1))"
fi
ls -la "$OUT"
