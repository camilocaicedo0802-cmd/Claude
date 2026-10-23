#!/usr/bin/env bash
# Build the VSL from the Drive folder (pitch take, screenshots and client testimonial) end to end.
#   bash videos/vsl-luis/build.sh            -> videos/vsl-luis/VSL_Luis_final.mp4
# Downloads go to videos/vsl-luis/work/ (gitignored). Needs ffmpeg, python3, numpy, pillow.
# Re-transcribing or re-detecting faces is optional: data/*.json are already in the repo.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work"
ASSETS="$WORK/assets"
mkdir -p "$WORK" "$ASSETS/fonts"

drive() { [ -s "$2" ] || curl -sSL --fail --retry 3 -o "$2" "https://drive.usercontent.google.com/download?id=$1&export=download&confirm=t"; }
# Drive folder 166Jczofb7o8ZOH8N44OnZ3g5wmsoUItL
drive 1zql3XkjH5ZqXgx4FI9rwOXdGK8R-lJgZ "$WORK/crudo.mp4"            # crudo 2 (para editar).mp4
drive 1nbXPSvQixy2uuIMpGgV7ariApw2EhK1b "$WORK/testimonio.mov"       # Testimonio.MOV
drive 1mG0-S5kaaRTkHcvc_PVhd3Y-j059Qzl0 "$ASSETS/recurso1.jpeg"      # Recurso 1 (321 mil)
drive 1XqKYSKKOFRApPdEg1GCXDq8zfU75awjx "$ASSETS/recurso23.jpeg"     # Recurso dos y tres (373 / 542)

GF=https://raw.githubusercontent.com/google/fonts/main/ofl
for w in SemiBold ExtraBold; do
  [ -s "$ASSETS/fonts/Poppins-$w.ttf" ] || curl -sSL --fail -o "$ASSETS/fonts/Poppins-$w.ttf" "$GF/poppins/Poppins-$w.ttf"
done

# "The Storm Chasers" — OpenGameArt, CC0 (public domain): https://opengameart.org/content/storm-chasers
[ -s "$WORK/storm.mp3" ] || curl -sSL --fail -o "$WORK/storm.mp3" "https://opengameart.org/sites/default/files/the_storm_chasers.mp3"

# Pitch: keep raw 0.70–17.98 s and 19.25–34.73 s (drops the leading silence and a 1.3 s pause).
ffmpeg -v error -y -i "$WORK/crudo.mp4" -filter_complex \
  "[0:v]trim=0.70:17.98,setpts=PTS-STARTPTS[a];[0:v]trim=19.25:34.73,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,fps=30,format=yuv420p[v];
   [0:a]atrim=0.70:17.98,asetpts=PTS-STARTPTS,afade=t=out:st=17.26:d=0.02[x];[0:a]atrim=19.25:34.73,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.02[y];[x][y]concat=n=2:v=0:a=1[aud]" \
  -map "[v]" -c:v libx264 -crf 12 -preset fast -an "$WORK/mezz.mp4" \
  -map "[aud]" -ac 2 -ar 48000 "$WORK/voice_raw.wav"

# Testimonial, condensed to five excerpts (frame numbers at 30 fps; same list as T_CUTS in render.py):
# "solo tengo palabras de agradecimiento" / "lo que hiciste con mi cuenta ... una total locura" /
# "mira lo que este muchacho ha logrado ... sabe lo que hace" / "100 por ciento recomendado" / "se vienen niveles, let's go"
CUTS="34:103 213:404 1434:1595 1608:1701 1824:1886"
fv=""; fa=""; cat=""; i=0
for c in $CUTS; do
  a=${c%:*}; b=${c#*:}
  fv+="[f$i]trim=start_frame=$a:end_frame=$b,setpts=PTS-STARTPTS[v$i];"
  fa+="[0:a:0]atrim=start=$(python3 -c "print($a/30)"):end=$(python3 -c "print($b/30)"),asetpts=PTS-STARTPTS,afade=t=in:d=0.015,areverse,afade=t=in:d=0.015,areverse[a$i];"
  cat+="[v$i][a$i]"; i=$((i + 1))
done
splits=$(for j in $(seq 0 $((i - 1))); do printf "[f%d]" "$j"; done)
ffmpeg -v error -y -i "$WORK/testimonio.mov" -filter_complex \
  "[0:v]fps=30,scale=1080:1920,setsar=1,split=$i$splits;$fv$fa${cat}concat=n=$i:v=1:a=1[v][a]" \
  -map "[v]" -c:v libx264 -crf 12 -preset fast -pix_fmt yuv420p "$WORK/testi.mp4" \
  -map "[a]" -ac 2 -ar 48000 "$WORK/testi_voice.wav"

if [ "${RETRACK:-0}" = 1 ]; then
  ffmpeg -v error -y -i "$WORK/crudo.mp4" -vn -ac 1 -ar 16000 "$WORK/audio16k.wav"
  python3 "$HERE/transcribe.py" "$WORK/audio16k.wav" medium "$HERE/data/words.json"
  ffmpeg -v error -y -i "$WORK/testimonio.mov" -map 0:a:0 -ac 1 -ar 16000 "$WORK/testi16k.wav"
  python3 "$HERE/transcribe.py" "$WORK/testi16k.wav" medium "$HERE/data/testi_words.json"
  python3 "$HERE/faces.py" "$WORK/crudo.mp4" "$HERE/data/faces.json"
fi
cp "$HERE/data/words.json" "$HERE/data/faces.json" "$HERE/data/testi_words.json" "$WORK/"

python3 "$HERE/render.py" --work "$WORK" --assets "$ASSETS" --out "$WORK/video_noaudio.mp4"
python3 "$HERE/audio.py" --work "$WORK" --music "$WORK/storm.mp3" --music-start 12.5 --out "$WORK/mix.wav"
ffmpeg -v error -y -i "$WORK/video_noaudio.mp4" -i "$WORK/mix.wav" -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart "$HERE/VSL_Luis_final.mp4"
echo "-> $HERE/VSL_Luis_final.mp4"
