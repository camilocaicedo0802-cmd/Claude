#!/usr/bin/env bash
# Render robusto de composiciones con objetos 3D (WebGL por software): por tramos de fotogramas, reiniciando el
# navegador en cada tramo y reintentando si se cuelga (con muchas escenas 3D seguidas swiftshader acaba bloqueándose).
# El audio se renderiza aparte y se une al final sin recodificar el vídeo.
# Uso: scripts/render_trozos.sh <Composición> <salida.mp4> [tramo=450] [crf=16]
set -uo pipefail
comp=$1; out=$2; tramo=${3:-450}; crf=${4:-16}
cd "$(dirname "$0")/.."
tmp=$(mktemp -d)
total=$(npx remotion compositions 2>/dev/null | awk -v c="$comp" '$1==c {print $4}')
[ -z "$total" ] && { echo "No encuentro $comp"; exit 1; }
echo "$comp: $total fotogramas en tramos de $tramo"
npx remotion bundle --out-dir="$tmp/bundle" --log=error > /dev/null 2>&1
i=0; : > "$tmp/lista.txt"
for ((a=0; a<total; a+=tramo)); do
  b=$((a+tramo-1)); [ $b -ge $total ] && b=$((total-1))
  parte=$(printf "%s/p%03d.mp4" "$tmp" $i)
  for intento in 1 2 3; do
    timeout 900 npx remotion render "$tmp/bundle" "$comp" "$parte" --frames=$a-$b --muted --gl=swangle --concurrency=2 --timeout=60000 --crf=$crf --log=error && break
    echo "tramo $a-$b: reintento $intento"; ps -C chrome -o pid= | xargs -r kill -9
  done
  [ -f "$parte" ] || { echo "tramo $a-$b falló"; exit 1; }
  echo "file '$parte'" >> "$tmp/lista.txt"; echo "tramo $a-$b listo"
  i=$((i+1))
done
npx remotion render "$tmp/bundle" "$comp" "$tmp/audio.wav" --codec=wav --log=error
ffmpeg -v error -y -f concat -safe 0 -i "$tmp/lista.txt" -i "$tmp/audio.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart "$out"
echo "listo $out"
rm -r "$tmp"
