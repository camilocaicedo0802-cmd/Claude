#!/usr/bin/env bash
# Render robusto de composiciones con objetos 3D (WebGL por software): por tramos de fotogramas, reiniciando el
# navegador en cada tramo y reintentando si se cuelga (con muchas escenas 3D seguidas swiftshader acaba bloqueándose).
# Es REANUDABLE: cada tramo terminado queda en out/trozos_<Composición>/ y no se repite si se relanza
# (p. ej. tras un reinicio del contenedor). El audio se renderiza aparte y se une al final sin recodificar el vídeo.
# Uso: scripts/render_trozos.sh <Composición> <salida.mp4> [tramo=450] [crf=16]
set -uo pipefail
comp=$1; out=$2; tramo=${3:-450}; crf=${4:-16}
cd "$(dirname "$0")/.."
dir="out/trozos_$comp"; mkdir -p "$dir"
total=$(npx remotion compositions 2>/dev/null | awk -v c="$comp" '$1==c {print $4}')
[ -z "$total" ] && { echo "No encuentro $comp"; exit 1; }
echo "$comp: $total fotogramas en tramos de $tramo"
rm -rf "$dir/bundle"
npx remotion bundle --out-dir="$dir/bundle" --log=error > /dev/null 2>&1
i=0; : > "$dir/lista.txt"
for ((a=0; a<total; a+=tramo)); do
  b=$((a+tramo-1)); [ $b -ge $total ] && b=$((total-1))
  parte=$(printf "%s/p%03d.mp4" "$dir" $i)
  if [ -f "$parte" ] && [ "$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$parte" 2>/dev/null)" = "$((b-a+1))" ]; then
    echo "tramo $a-$b ya estaba"
  else
    for intento in 1 2 3; do
      timeout 900 npx remotion render "$dir/bundle" "$comp" "$parte.tmp.mp4" --frames=$a-$b --muted --gl=swangle --concurrency=2 --timeout=60000 --crf=$crf --log=error && mv "$parte.tmp.mp4" "$parte" && break
      echo "tramo $a-$b: reintento $intento"; ps -C chrome -o pid= | xargs -r kill -9
    done
    [ -f "$parte" ] || { echo "tramo $a-$b falló"; exit 1; }
    echo "tramo $a-$b listo"
  fi
  echo "file '$(realpath "$parte")'" >> "$dir/lista.txt"
  i=$((i+1))
done
npx remotion render "$dir/bundle" "$comp" "$dir/audio.wav" --codec=wav --log=error
ffmpeg -v error -y -f concat -safe 0 -i "$dir/lista.txt" -i "$dir/audio.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart "$out"
echo "listo $out"
