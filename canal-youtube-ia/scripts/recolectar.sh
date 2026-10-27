#!/bin/bash
# Recolecta las listas públicas de videos y Shorts de cada canal con yt-dlp.
# Uso: BASE=/ruta/de/trabajo ./recolectar.sh @Canal1 @Canal2 ...
# Requiere yt-dlp (pip install yt-dlp). Una sola petición por pestaña: no dispara el límite de YouTube.
# Los metadatos exactos por video (fecha, vistas, likes, comentarios) se piden después en lotes de 50
# con vidiq_get_videos_by_ids (5 créditos por lote), porque pedir video a video desde yt-dlp
# provoca "HTTP 429" y "Sign in to confirm you're not a bot" desde IPs de centros de datos.
set -u
BASE=${BASE:-./trabajo}
mkdir -p "$BASE/data/flatdate" "$BASE/data/flatorig"
for h in "$@"; do
  h=${h#@}
  for tab in videos shorts; do
    yt-dlp --flat-playlist -J --extractor-args "youtubetab:approximate_date" \
      "https://www.youtube.com/@$h/$tab" > "$BASE/data/flatdate/${h}_${tab}.json" 2> "$BASE/data/flatdate/${h}_${tab}.err"
    sleep 3
  done
done
# Canales que no publican en inglés: repetir con títulos originales, p. ej.
#   yt-dlp --flat-playlist -J --extractor-args "youtube:lang=es;youtubetab:approximate_date" URL > flatorig/<canal>_videos.json
