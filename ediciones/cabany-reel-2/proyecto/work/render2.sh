#!/bin/bash
cd "$(dirname "$0")"
OUT=${1:-../out_frames}
for k in 0 1 2; do
  ../../venv/bin/python -c "import reel2; reel2.render_worker($k, 3, '$OUT')" > render2_$k.log 2>&1 &
done
wait
echo ALLDONE
