S="${1:-$(dirname "$0")/..}"; cd "$S/../../media/raw"
VF="zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=contrast=1.06:brightness=0.025:saturation=1.12,fps=30"
for f in LienzoAudi.mov IMG_63*.MOV; do
  o="$S/remotion/public/${f%.*}.mp4"
  [ -s "$o" ] && continue
  ffmpeg -v error -y -i "$f" -vf "$VF" -c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k -ar 48000 "$o" && echo "ok $f"
done
echo PROXIES_DONE
