#!/usr/bin/env bash
# Regenera public/media y public/audio desde las carpetas de Drive del proyecto (enlaces públicos).
# Requisitos: curl, ffmpeg, python3 con faster-whisper, numpy y opencv-python-headless<5.
# Uso: bash scripts/prepare_media.sh [carpeta_temporal]
set -euo pipefail
cd "$(dirname "$0")/.."
TMP="${1:-$(mktemp -d)}"
mkdir -p "$TMP/raw" public/media public/audio src/data
dl() { [ -s "$2" ] || curl -sSL --retry 4 -o "$2" "https://drive.usercontent.google.com/download?id=$1&export=download&confirm=t"; }

# 1. Material del proyecto (carpeta "VIDEO BASE" + b-rolls + fotos)
dl 1uERpjSEVFlNdtbOtvr_n_ZiDaADyKzZY "$TMP/raw/video_base.mov"
dl 1GT7oTsaPeApXpUQkIkK_d0Y_AlcmNafc "$TMP/raw/broll_1.mp4"
dl 1m0rWmcQjRdtIZcqAY0aRUkUR14iHU643 "$TMP/raw/broll_2.mp4"
i=1; for id in 1U4MQf4w1Xi-ddS6g6aOHR85QN5uUIlyD 1XXeTF5ooB2O3n8bfylzBM6fFoSljnttA 1oabq922H8JY5R83eGc0FhlBQ68fdjop7 \
  18RxQzM5csVAWQVRo6FDTUmdnkq3pEdFs 1VEZ8SJLRWlkLbCP-NDurw8UIN6Vx7-Vt 1DNIGwyq6HI7pbi4CataWaR-av-ou0gz_ 1lWZ6EV7PLUNI1epiBNAt5UsWjPKKbYDv; do
  dl "$id" "$TMP/raw/foto_macizo_$i.jpg"; i=$((i + 1)); done
# B-roll genérico de interiores (pack de b-roll) y música (PACK MÚSICA V2 / ANBR - Quantum)
dl 1hN65_hrtLMfgCpMdRH3zCdbMytOmH7oL "$TMP/raw/c187.mp4"
dl 1if9sTpoocnRe7YvjwLsvVu7bMUi_oPIG "$TMP/raw/c271.mp4"
dl 1N0L8W1OgraMGsXvDkAg9wXTZQZxqisB6 "$TMP/raw/anbr_quantum.wav"

# 2. Etalonaje (estilo.md §7): G2 para el presentador, G1 (más suave) para b-roll y fotos
G2="eq=brightness=-0.07:contrast=1.18:saturation=1.05:gamma=0.9,colorbalance=rs=0.07:gs=0.02:bs=-0.08:rm=0.06:gm=0.01:bm=-0.07:rh=0.02:gh=0.0:bh=-0.05,curves=master='0/0.02 0.25/0.18 0.5/0.47 0.8/0.82 1/0.96'"
G1="eq=brightness=-0.03:contrast=1.1:saturation=1.05:gamma=0.96,colorbalance=rs=0.04:bs=-0.05:rm=0.03:bm=-0.04:rh=0.02:bh=-0.03"
ffmpeg -v error -y -i "$TMP/raw/video_base.mov" -vf "fps=30,scale=1080:1920:flags=lanczos,$G2,format=yuv420p" -an -c:v libx264 -crf 16 -g 15 public/media/base.mp4
for b in 1 2; do ffmpeg -v error -y -i "$TMP/raw/broll_$b.mp4" -vf "fps=30,scale=1080:1920:flags=lanczos,$G1,format=yuv420p" -an -c:v libx264 -crf 16 -g 15 "public/media/broll$b.mp4"; done
for i in 1 2 3 4 5 6 7; do ffmpeg -v error -y -i "$TMP/raw/foto_macizo_$i.jpg" -vf "$G1" -q:v 2 "public/media/foto$i.jpg"; done
for c in c187 c271; do ffmpeg -v error -y -i "$TMP/raw/$c.mp4" -t 12 -vf "fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,$G1,format=yuv420p" -an -c:v libx264 -crf 17 -g 15 "public/media/$c.mp4"; done
# Recortes de la silla (plano en que él sale de cuadro) y avatar para el gráfico de barra
ffmpeg -v error -y -ss 7.0 -i public/media/base.mp4 -frames:v 1 "$TMP/chair.png"
ffmpeg -v error -y -i "$TMP/chair.png" -vf "crop=820:900:20:1020,scale=600:-1" -q:v 2 public/media/silla_completa.jpg
ffmpeg -v error -y -i "$TMP/chair.png" -vf "crop=480:600:380:1300,scale=600:-1" -q:v 2 public/media/silla_cuero.jpg
ffmpeg -v error -y -i "$TMP/chair.png" -vf "crop=420:540:520:1380,scale=600:-1" -q:v 2 public/media/silla_madera.jpg
ffmpeg -v error -y -ss 20 -i public/media/base.mp4 -frames:v 1 -vf "crop=300:300:575:830,scale=200:200" -q:v 2 public/media/avatar.jpg
# Música: ANBR - Quantum desde 24,4 s (inicio de sección), 70 s
ffmpeg -v error -y -ss 24.4 -t 70 -i "$TMP/raw/anbr_quantum.wav" -af "afade=t=in:d=0.3,aresample=48000" -ac 2 public/audio/musica.wav

# 3. Transcripción Whisper (tiempos por palabra) -> EDL -> voz editada
ffmpeg -v error -y -i "$TMP/raw/video_base.mov" -vn -ac 1 -ar 16000 "$TMP/base16k.wav"
python3 -I scripts/transcribe.py "$TMP/base16k.wav" "$TMP/base_words.json" es
python3 -I scripts/build_edl.py "$TMP/base16k.wav" "$TMP/base_words.json" src/data
python3 -I scripts/build_voice.py "$TMP/raw/video_base.mov" src/data/edl.json public/audio/voz.wav
python3 -I scripts/face_track.py "$TMP/raw/video_base.mov" "$TMP/faces_raw.json"
python3 -I scripts/attach_faces.py "$TMP/faces_raw.json" src/data/edl.json
echo "Listo: medios en public/media y public/audio."

# 4. Kit de SFX (carpetas SFX PACK 1 y 2 del usuario): recorte del silencio inicial, pico a -1 dBFS y fundido
mkdir -p public/sfx "$TMP/sfx"
sfx() { # id nombre duración_max [inicio]
  dl "$1" "$TMP/sfx/$2.src"
  ffmpeg -v error -y -ss "${4:-0}" -i "$TMP/sfx/$2.src" -af "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.005,atrim=0:$3,aresample=48000" -ac 2 "$TMP/sfx/$2.wav"
  local mx d; mx=$(ffmpeg -i "$TMP/sfx/$2.wav" -af volumedetect -f null - 2>&1 | awk '/max_volume/ {print $5}')
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/sfx/$2.wav")
  ffmpeg -v error -y -i "$TMP/sfx/$2.wav" -af "volume=$(python3 -c "print(-1.0-($mx))")dB,afade=t=out:st=$(python3 -c "print(max(0,$d-0.08))"):d=0.08" "public/sfx/$2.wav"
}
sfx 1G9iLND4bMoVG4DNeEV7BmhY5Mj4BEjn4 whoosh1 1.2
sfx 1GW2ufSLZwATEz4tLje-2TUruR6snqcTX whoosh2 1.2
sfx 1XK2Chi7U7KzDUtwBMVnLIQJqbrM52KX8 whoosh3 1.2
sfx 1-keG3Zw42OTxzZcI42Sz11oFYiwbZgkR swoosh1 0.4
sfx 1lGAHJGN0BDsVAVkzbFV0qbPIzYWJZF4s swoosh2 0.4
sfx 1P_HBk8TnT-ToXy5iNEJVr3QGWs9god_Z hitwhoosh 1.8
sfx 1TSs-NsfAlX7clS3o6qyV1nQl_kxy_5_G pop 0.6
sfx 1piIl2jcHsztXna_vs1UDhmGZPehKjaL_ click 0.3
sfx 1lga-8GtnK3-nLT2Ki7dEGjciU2xptw7C subhit 1.5
sfx 1wtqsjyylUMN2qf5WHp42GFgbXycWs62g boom 2.5
sfx 1p2uGxCHdt0znHJ028G5-i9oiAQ8l7Qqm cinebass 3.5
sfx 1pAm6oxdx1HnnGpNhNyyWOsYqzdnrU6qx riser 2.4
sfx 1vGMFLkJqJwnEQ8y33Ou1Cq1gj0G3BaI3 riser_long 4.0
sfx 1NL_wgSRgXharzFCwe4BnEWdOXh3jtxo- type_short 1.7
sfx 1lxrCRfhEmA9UTr02oO0u1aFE95mkpUWY keys 0.5
sfx 1ev7tNjj3-fJF1DFlDF94ONsDKZuVL8RD shutter 0.9
sfx 1Eiytr3PXiY4WEVwxoK_3xKiFVFcGh3qV flash 0.9
sfx 1JXlbYd53TZESJMHsJ713i8D4C5VKEf5M marker 1.2
sfx 1tZpn0uOEYexY-NHEaJqbW7LiKlPiJSWj typing 10 2.4
sfx 1VdFtzbpDejih-WtJFveWbXv9E2z9QLeF typing_digital 6
echo "SFX listos en public/sfx."
