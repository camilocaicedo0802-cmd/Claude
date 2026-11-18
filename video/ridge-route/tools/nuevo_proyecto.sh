#!/bin/bash
# Crea la carpeta de un episodio nuevo con el motor, las herramientas y las fuentes de la skill.
# usage: bash nuevo_proyecto.sh CARPETA_PROYECTO LOCUCION.mp3 GUION.pdf [CARPETA_MUSICA]
set -e
SKILL="$(cd "$(dirname "$0")/../.." && pwd)"
P="$1"; VOZ="$2"; GUION="$3"; MUSICA="${4:-}"
mkdir -p "$P"/{edit,tools,work,out,entrega,assets/img,assets/vid,assets/map,assets/score,assets/yt}
cp "$SKILL"/scripts/motor/*.py "$P/edit/"
cp "$SKILL"/scripts/herramientas/* "$SKILL"/scripts/entrega/* "$P/tools/"
cp -r "$SKILL/assets/fonts" "$P/assets/fonts"
[ -n "$MUSICA" ] && ln -sfn "$MUSICA" "$P/assets/music"
cp "$VOZ" "$P/work/voz.mp3"
pdftotext -layout "$GUION" "$P/work/guion.txt"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$P/work/voz.mp3" | awk '{printf "duración de la locución: %.2f s\n", $1}'
echo "proyecto listo en $P"
