#!/usr/bin/env bash
# Descarga un fondo generado (PNG) y lo guarda como JPG en public/fondos/<nombre>.jpg
# Uso: bash scripts/bajar-fondo.sh <nombre> <url>
set -euo pipefail
tmp=$(mktemp --suffix=.png)
curl -sS -o "$tmp" "$2"
ffmpeg -v error -y -i "$tmp" -q:v 3 "public/fondos/$1.jpg"
rm -f "$tmp"
echo "public/fondos/$1.jpg"
