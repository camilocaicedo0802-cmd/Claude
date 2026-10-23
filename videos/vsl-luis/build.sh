#!/usr/bin/env bash
# Build the VSL from the Drive folders (pitch take, screenshots, client testimonial, music) end to end.
#   bash videos/vsl-luis/build.sh            -> videos/vsl-luis/VSL_Luis_final.mp4
# Downloads go to videos/vsl-luis/work/ (gitignored). Needs ffmpeg, python3, numpy, pillow, and the
# Coolvetica font (not redistributable): put Coolvetica-Rg.otf in work/assets/fonts/ or pass FONT=<path>.
# Re-transcribing or re-detecting faces is optional: data/*.json are already in the repo.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work"
ASSETS="$WORK/assets"
mkdir -p "$WORK" "$ASSETS/fonts"

drive() { [ -s "$2" ] || curl -sSL --fail --retry 3 -o "$2" "https://drive.usercontent.google.com/download?id=$1&export=download&confirm=t"; }
# Material: Drive folder 166Jczofb7o8ZOH8N44OnZ3g5wmsoUItL
drive 1zql3XkjH5ZqXgx4FI9rwOXdGK8R-lJgZ "$WORK/crudo.mp4"            # crudo 2 (para editar).mp4
drive 1nbXPSvQixy2uuIMpGgV7ariApw2EhK1b "$WORK/testimonio.mov"       # Testimonio.MOV
drive 1mG0-S5kaaRTkHcvc_PVhd3Y-j059Qzl0 "$ASSETS/recurso1.jpeg"      # Recurso 1 (321 mil)
drive 1XqKYSKKOFRApPdEg1GCXDq8zfU75awjx "$ASSETS/recurso23.jpeg"     # Recurso dos y tres (373 / 542)
# Music: Drive folder 1knl3Lxp6aeBAySatN1SK5jPGHL7Uy2Ar > emocional > "Música Épica Sin Copyright.m4a"
drive 1g9f-g1pRqmvusC5t75h-iRz53QsfpIif "$WORK/musica_epica.m4a"

FONT_DST="$ASSETS/fonts/Coolvetica-Rg.otf"
if [ -n "${FONT:-}" ]; then cp "$FONT" "$FONT_DST"; fi
[ -s "$FONT_DST" ] || { echo "Missing $FONT_DST (Coolvetica Regular). Pass FONT=/path/Coolvetica_Rg.otf" >&2; exit 1; }

# cut <input> <video prefilter> <out video> <out audio> <first:last frame at 30 fps>...
# Keeps the listed excerpts, each with 15 ms audio fades so the joins don't click.
cut() {
  local src=$1 pre=$2 outv=$3 outa=$4; shift 4
  local fv="" fa="" cat="" i=0 splits=""
  for c in "$@"; do
    local a=${c%:*} b=${c#*:}
    fv+="[f$i]trim=start_frame=$a:end_frame=$b,setpts=PTS-STARTPTS[v$i];"
    fa+="[0:a:0]atrim=start=$(python3 -c "print($a/30)"):end=$(python3 -c "print($b/30)"),asetpts=PTS-STARTPTS,afade=t=in:d=0.015,areverse,afade=t=in:d=0.015,areverse[a$i];"
    cat+="[v$i][a$i]"; splits+="[f$i]"; i=$((i + 1))
  done
  ffmpeg -v error -y -i "$src" -filter_complex "[0:v]${pre}fps=30,format=yuv420p,split=$i$splits;$fv$fa${cat}concat=n=$i:v=1:a=1[v][a]" \
    -map "[v]" -c:v libx264 -crf 12 -preset fast "$outv" -map "[a]" -ac 2 -ar 48000 "$outa"
}
# Same frame lists as CUTS_F / T_CUTS_F in render.py.
# Pitch: drops the leading silence, a pause after "un momento", the false start "que comenzó…" and "hermano".
cut "$WORK/crudo.mp4" "" "$WORK/mezz.mp4" "$WORK/voice_raw.wav" 21:430 442:494 581:886 915:1042
# Testimonial: "solo tengo palabras de agradecimiento" / "lo que hiciste con mi cuenta y llevamos 20 días
# publicando y una total locura" / "mira lo que este muchacho ha logrado con mi cuenta, sabe lo que hace" /
# "y sin duda alguna 100% recomendado" (drops "¿qué? 19,", "o sea" and the hesitation pauses)
cut "$WORK/testimonio.mov" "scale=1080:1920,setsar=1," "$WORK/testi.mp4" "$WORK/testi_voice.wav" \
  34:103 213:275 306:345 358:404 1434:1454 1461:1489 1502:1546 1565:1595 1607:1716

if [ "${RETRACK:-0}" = 1 ]; then
  ffmpeg -v error -y -i "$WORK/crudo.mp4" -vn -ac 1 -ar 16000 "$WORK/audio16k.wav"
  python3 "$HERE/transcribe.py" "$WORK/audio16k.wav" medium "$HERE/data/words.json"
  ffmpeg -v error -y -i "$WORK/testimonio.mov" -map 0:a:0 -ac 1 -ar 16000 "$WORK/testi16k.wav"
  python3 "$HERE/transcribe.py" "$WORK/testi16k.wav" medium "$HERE/data/testi_words.json"
  python3 "$HERE/faces.py" "$WORK/crudo.mp4" "$HERE/data/faces.json"
fi
cp "$HERE/data/words.json" "$HERE/data/faces.json" "$HERE/data/testi_words.json" "$WORK/"

python3 "$HERE/render.py" --work "$WORK" --assets "$ASSETS" --out "$WORK/video_noaudio.mp4"
python3 "$HERE/audio.py" --work "$WORK" --music "$WORK/musica_epica.m4a" --music-start 15.85 --out "$WORK/mix.wav"
ffmpeg -v error -y -i "$WORK/video_noaudio.mp4" -i "$WORK/mix.wav" -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart "$HERE/VSL_Luis_final.mp4"
echo "-> $HERE/VSL_Luis_final.mp4"
