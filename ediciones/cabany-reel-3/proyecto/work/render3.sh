#!/bin/bash
cd "$(dirname "$0")"
OUT=${1:-../out_frames}
for k in 0 1 2 3; do
  ../../venv/bin/python -c "import reel3; reel3.render_worker($k, 4, '$OUT')" > render3_$k.log 2>&1 &
done
wait
echo ALLDONE
