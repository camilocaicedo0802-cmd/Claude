#!/usr/bin/env bash
# Downloads the fonts and music the edit uses and renders the emoji stickers.
# Usage: scripts/video-edit/matcha/fetch_assets.sh <assets_dir>
set -euo pipefail
A="${1:?assets dir}"
mkdir -p "$A/fonts" "$A/music" "$A/emoji" "$A/sfx"
UA="Mozilla/4.0"
font() {  # family-css-query  output-name
  url=$(curl -sS -A "$UA" "https://fonts.googleapis.com/css2?family=$1" | grep -oE "https://fonts.gstatic.com[^)]+" | head -1)
  curl -sS -o "$A/fonts/$2" "$url"
}
font "Montserrat:wght@900" Montserrat-Black.ttf
font "Montserrat:wght@800" Montserrat-ExtraBold.ttf
font "Anton" Anton.ttf
# "Funshine" from FreePD (public domain, CC0), mirrored on archive.org
curl -sSL -o "$A/music/Funshine.mp3" "https://archive.org/download/freepd/upbeat/Funshine.mp3"
# emoji stickers from the system Noto Color Emoji font
python3 - "$A/emoji" <<'PY'
import sys
from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
E = {"matcha": "🍵", "coffee": "☕", "herb": "🌿", "zap": "⚡", "sparkles": "✨", "greenheart": "💚",
     "x": "❌", "check": "✅", "fire": "🔥", "hearteyes": "😍", "dizzy": "😵‍💫", "eyes": "👀",
     "100": "💯", "relieved": "😌", "muscle": "💪", "starstruck": "🤩", "trophy": "🏆"}
for k, v in E.items():
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), v, font=f, embedded_color=True, anchor="mm")
    im.crop(im.getbbox()).save(f"{sys.argv[1]}/{k}.png")
PY
python3 "$(dirname "$0")/sfx.py" "$A/sfx"
