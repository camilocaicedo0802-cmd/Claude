#!/usr/bin/env bash
# Descarga clips de Mixkit en la mayor resolución disponible (2160 > 1080 > 720).
# Uso: mixkit_download.sh <dir_salida> id1 id2 ...
out="$1"; shift
for id in "$@"; do
  [ -s "$out/$id.mp4" ] && continue
  for q in 2160 1080 720; do
    url="https://assets.mixkit.co/videos/$id/$id-$q.mp4"
    code=$(curl -s -o /dev/null -w "%{http_code}" -r 0-10 --max-time 20 "$url")
    if [ "$code" = "206" ] || [ "$code" = "200" ]; then
      curl -s --max-time 600 -o "$out/$id.mp4" "$url" && echo "$id $q" && break
    fi
  done
done
