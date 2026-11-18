#!/usr/bin/env bash
# Música de fondo: "ANBR - Quantum" (carpeta de música del cliente, PACK MÚSICA V2).
# Genera la pista normal y una versión sin graves para el tramo de la cita.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p material/musica public/musica
scripts/drive_dl.sh 1N0L8W1OgraMGsXvDkAg9wXTZQZxqisB6 material/musica/ANBR_-_Quantum.wav
M=material/musica/ANBR_-_Quantum.wav
[ -s "$M" ] || M=$(find material/musica -name "ANBR_-_Quantum.wav" | head -1)
ffmpeg -v error -y -i "$M" -c:a libmp3lame -b:a 192k -ar 48000 public/musica/quantum.mp3
ffmpeg -v error -y -i "$M" -af "highpass=f=650,highpass=f=650,lowpass=f=6000" -c:a libmp3lame -b:a 192k -ar 48000 public/musica/quantum_filtrada.mp3
ls -la public/musica
