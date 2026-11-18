#!/usr/bin/env bash
# Descarga un archivo público de Google Drive por ID.  Uso: drive_dl.sh <id> <destino>
set -euo pipefail
id="$1"; out="$2"
if [ -s "$out" ]; then echo "ya existe: $out"; exit 0; fi
tmp="$out.part"
for intento in 1 2 3 4; do
  if curl -sS -L --fail --retry 3 -o "$tmp" \
      "https://drive.usercontent.google.com/download?id=${id}&export=download&confirm=t"; then
    # Si Drive devolvió una página HTML (aviso/cuota) no es el archivo real.
    if head -c 200 "$tmp" | grep -qi '<!DOCTYPE html\|<html'; then
      echo "intento $intento: Drive devolvió HTML para $id" >&2
    else
      mv "$tmp" "$out"; echo "ok: $out ($(stat -c%s "$out") bytes)"; exit 0
    fi
  fi
  sleep $((intento * 3))
done
echo "FALLO: $id -> $out" >&2; rm -f "$tmp"; exit 1
