#!/bin/bash
cd "$(dirname "$0")"
OUT=${1:-../out_frames}
for k in 0 1 2 3; do
  ../venv/bin/python -c "import reel; reel.render_worker($k, 4, '$OUT')" > ../work/render_$k.log 2>&1 &
done
wait
echo ALLDONE
