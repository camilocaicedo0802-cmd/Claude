#!/bin/bash
# usage: dl.sh list.tsv outdir  (tsv: id mime size title) ; downloads with 3 parallel jobs, skips complete files
LIST=$1; OUT=$2; mkdir -p "$OUT"
dl_one() {
  id=$1; size=$2; title=$3; OUT=$4
  ext="${title##*.}"; case "$title" in *.*) ;; *) ext=mp4;; esac
  safe=$(echo "$title" | tr ' /,' '___' | tr -cd '[:alnum:]_.-' )
  case "$safe" in *.*) ;; *) safe="$safe.$ext";; esac
  f="$OUT/$safe"
  if [ -f "$f" ] && [ "$(stat -c%s "$f")" = "$size" ]; then return; fi
  for i in 1 2 3 4; do
    curl -sSL --fail -o "$f.part" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t" && mv "$f.part" "$f" && break
    sleep $((2**i))
  done
  echo "$(date +%T) $safe $(stat -c%s "$f" 2>/dev/null)"
}
export -f dl_one
while IFS=$'\t' read -r id mime size title; do printf '%s\0%s\0%s\0%s\0' "$id" "$size" "$title" "$OUT"; done < "$LIST" | xargs -0 -n4 -P3 bash -c 'dl_one "$@"' _
echo DONE
