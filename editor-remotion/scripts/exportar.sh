#!/usr/bin/env bash
# Exporta el vídeo final: render de Remotion + masterizado del sonido a -14 LUFS con
# limitador (pico por debajo de -1 dB), que es el nivel que esperan Reels, TikTok y Shorts.
set -euo pipefail
cd "$(dirname "$0")/.."
COMP="${1:-SemillaCertificada}"
SALIDA="${2:-out/agrokrack_semilla_certificada.mp4}"
mkdir -p out
npx remotion render "$COMP" out/_render.mp4 --crf=17 --jpeg-quality=92 --concurrency=4 --audio-bitrate=320k --log=error
I=$(ffmpeg -hide_banner -nostats -i out/_render.mp4 -vn -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
G=$(python3 -c "print(round(-14.0 - ($I), 2))")
echo "Sonoridad del render: $I LUFS → ganancia $G dB"
ffmpeg -v error -y -i out/_render.mp4 -c:v copy \
  -af "volume=${G}dB,alimiter=limit=0.85:attack=3:release=60:level=disabled" \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$SALIDA"
ffmpeg -hide_banner -nostats -i "$SALIDA" -vn -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):" | tr -s ' ' | tr '\n' ' '
echo
ls -la "$SALIDA"
