#!/usr/bin/env bash
# Render final 1080x1920 @ 60 fps (H.264, AAC 320k)
# Uso: scripts/render.sh [salida.mp4] [composición]   (por defecto: out/farmasi.mp4 Farmasi)
set -e
cd "$(dirname "$0")/.."
npx remotion render "${2:-Farmasi}" "${1:-out/farmasi.mp4}" --codec=h264 --crf=16 --audio-bitrate=320k --concurrency=4 --gl=swangle --log=error
rm -rf /tmp/remotion-webpack-bundle-* 2>/dev/null || true  # el bundle copia todo public/: no dejarlo en /tmp
