#!/usr/bin/env bash
# Render final 1080x1920 @ 60 fps (H.264, AAC 320k)
set -e
cd "$(dirname "$0")/.."
npx remotion render Farmasi "${1:-out/farmasi.mp4}" --codec=h264 --crf=16 --audio-bitrate=320k --concurrency=4 --gl=swangle --log=error
