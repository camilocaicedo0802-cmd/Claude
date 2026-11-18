#!/usr/bin/env bash
# Convierte el material en crudo a 1080x1920, 60 fps constantes, SDR, GOP corto (búsqueda exacta en Remotion).
set -euo pipefail
cd "$(dirname "$0")/.."
enc() { # entrada salida [filtros extra] [opciones de entrada]
  local in="$1" out="$2" vf="${3:-}"; shift; shift; shift || true
  ffmpeg -v error -y "$@" -i "material/crudo/$in.mp4" -an \
    -vf "${vf}scale=1080:1920:flags=lanczos,fps=60,format=yuv420p" \
    -c:v libx264 -preset medium -crf 16 -g 12 -bf 0 -movflags +faststart \
    -color_primaries bt709 -color_trc bt709 -colorspace bt709 "public/clips/$out.mp4"
  echo "ok public/clips/$out.mp4 $(ffprobe -v error -show_entries format=duration -of csv=p=0 public/clips/$out.mp4)s"
}
enc toma1_agro   presentador_gancho   ""
enc wa_105147_0  presentador_contexto ""
enc wa_105147_1  agronomo_presentacion ""
enc wa_105147_2  agronomo_beneficio1  ""
enc wa_105147_3  agronomo_beneficio2  ""
enc wa_105147_4  agronomo_beneficio3  ""
enc wa_105147_5  agronomo_amtec       ""
enc broll_agro   broll_mano_arroz     ""
enc wa_105200_1  broll_grano          ""
# Cosechadora grabada a 120 fps → cámara lenta al 50 % (tramo 5–17 s del original).
enc wa_105200_0  broll_cosechadora_lenta "setpts=2.0*PTS," -ss 5 -t 12
