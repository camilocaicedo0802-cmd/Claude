#!/bin/bash
# render all overlay frames with P parallel workers
R=$(dirname "$0"); P=${1:-3}
N=$(python3 -c "import json,math;print(math.ceil(json.load(open('$R/timeline.json'))['duration']*30))")
rm -rf $R/ovl; mkdir -p $R/ovl
step=$(( (N + P - 1) / P ))
for i in $(seq 0 $((P-1))); do s=$((i*step)); e=$(( s+step < N ? s+step : N )); node $R/render_overlay3.cjs $R/timeline.json $R/ovl $s $e & done
wait; ls $R/ovl | wc -l
