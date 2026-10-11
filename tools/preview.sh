#!/usr/bin/env bash
# Uso: tools/preview.sh nombre f1 f2 f3 ...  → out/prev_nombre.jpg (hoja de contacto de los frames dados)
set -e
cd "$(dirname "$0")/.."
NAME=$1; shift
npx remotion bundle src/index.ts --out-dir=build >/dev/null 2>&1
mkdir -p out/prev
for fr in "$@"; do
  npx remotion still build Promo out/prev/f_$fr.png --frame=$fr --gl=swangle --log=error >/dev/null 2>&1 &
  while [ "$(jobs -r | wc -l)" -ge 4 ]; do sleep 0.5; done
done
wait
python3 -I tools/hoja.py out/prev_$NAME.jpg "$@"
