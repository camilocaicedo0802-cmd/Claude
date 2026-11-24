#!/usr/bin/env bash
# Control de calidad del render: formato, sonoridad, picos, negros y hoja de contacto.
set -e
V="${1:-out/farmasi.mp4}"
echo "== Formato"; ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate,channels -of default=nw=1 "$V"
echo "== Sonoridad (objetivo ≈ −14 LUFS, pico < −1 dBTP)"; ffmpeg -v info -nostats -i "$V" -af ebur128=peak=true -f null - 2>&1 | grep -A12 "Summary" | grep -E "I:|LRA:|Peak:"
echo "== Fotogramas negros (>0,1 s)"; ffmpeg -v info -nostats -i "$V" -vf "blackdetect=d=0.1:pix_th=0.06" -an -f null - 2>&1 | grep -o "black_start.*" || echo "ninguno"
mkdir -p out/control && ffmpeg -v error -y -i "$V" -vf "fps=2,scale=180:-1,drawtext=text='%{pts\:hms}':x=3:y=3:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.7,tile=13x6:padding=2" -frames:v 1 out/control/hoja.jpg && echo "hoja: out/control/hoja.jpg"
