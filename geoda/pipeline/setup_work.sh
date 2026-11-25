#!/bin/bash
# Prepara la carpeta de trabajo GEODA en una sesión nueva (sirve en cualquier chat/contenedor).
# uso: bash geoda/pipeline/setup_work.sh <carpeta_de_trabajo>      (ej. <scratchpad>/geoda)
# - Enlaza el código del repo (builder, label_fix, tools, montajes de referencia) y el kit de recursos reales.
# - Escribe ~/.geoda_work: así todos los scripts encuentran la carpeta sin variables de entorno.
set -e
W=${1:?falta la carpeta de trabajo}
R=$(cd "$(dirname "$0")/.." && pwd)          # .../geoda (repo)
mkdir -p "$W"/{a102,tools,hf/fixed,v2frames,labelfix,lab,stock}
ln -sf "$R/pipeline/builder.py" "$R/pipeline/label_fix.py" "$W/"
ln -sf "$R/pipeline/build_a102.py" "$W/a102/build_a102.py"
ln -sf "$R/pipeline/motion_v3.py" "$W/a102/motion_v3.py"
for f in "$R"/pipeline/tools/*.py; do ln -sf "$f" "$W/tools/"; done
cp -f "$R/pipeline/hf.sh" "$W/hf/hf.sh"; chmod +x "$W/hf/hf.sh"
ln -sfn "$R/kit" "$W/kit"
ln -sfn "$R/kit/audio" "$W/audio"
ln -sfn "$R/kit/screen" "$W/screen"
ln -sf "$R/kit/producto/producto_cut.png" "$R/kit/producto/mano.png" "$W/v2frames/"
ln -sf "$R/kit/producto/label_real.png" "$W/labelfix/label_real.png"
ln -sf "$R/kit/producto/endcard_bano_real.png" "$W/hf/fixed/"
for f in "$R"/kit/broll/*; do ln -sf "$f" "$W/hf/fixed/"; done
echo "$W" > ~/.geoda_work
# dependencias (normalmente ya están)
python3 -c "import cv2, numpy, PIL" 2>/dev/null || pip install -q opencv-python-headless numpy pillow
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg)
[ -f /usr/share/fonts/opentype/inter/InterDisplay-Black.otf ] || (apt-get update -qq && apt-get install -y -qq fonts-inter)
[ -f /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf ] || (apt-get update -qq && apt-get install -y -qq fonts-noto-color-emoji)
echo "GEODA listo en $W (código y kit enlazados desde $R)"
