#!/usr/bin/env bash
# Prepara el entorno y el proyecto Remotion.
#   bash setup.sh <carpeta_proyecto> [--width 1080 --height 1920 --fps 30] [--no-demucs] [--no-template]
# - Comprueba Node ≥18, ffmpeg, Python 3 e instala lo que falte (pip): whisper, librosa, soundfile,
#   onnxruntime, rapidocr-onnxruntime, pillow, numpy y demucs (torch CPU).
# - Crea el proyecto Remotion (plantilla en blanco) si no existe, instala @remotion/{media,captions,paths,fonts}
#   y las skills oficiales de Remotion (npx skills add remotion-dev/skills).
# - Copia la plantilla de componentes de esta skill a src/ y escribe dimensiones/fps en src/theme.ts.
set -uo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJ="${1:?uso: setup.sh <carpeta_proyecto> [opciones]}"; shift || true
WIDTH=1080; HEIGHT=1920; FPS=30; DEMUCS=1; TEMPLATE=1
while [ $# -gt 0 ]; do
  case "$1" in
    --width) WIDTH="$2"; shift 2;; --height) HEIGHT="$2"; shift 2;; --fps) FPS="$2"; shift 2;;
    --no-demucs) DEMUCS=0; shift;; --no-template) TEMPLATE=0; shift;; *) shift;;
  esac
done
ok(){ printf "  \033[32m✓\033[0m %s\n" "$*"; }; warn(){ printf "  \033[33m!\033[0m %s\n" "$*"; }
PIP="pip3 install -q"; $PIP --help >/dev/null 2>&1 && pip3 install --help | grep -q break-system-packages && PIP="pip3 install -q --break-system-packages"

echo "1) Herramientas"
if command -v node >/dev/null; then ok "node $(node -v)"; else
  warn "node no encontrado: instálalo (https://nodejs.org) o con tu gestor de paquetes"; fi
if command -v ffmpeg >/dev/null; then ok "$(ffmpeg -version | head -1 | cut -d' ' -f1-3)"; else
  (command -v apt-get >/dev/null && sudo -n apt-get install -y ffmpeg >/dev/null 2>&1 || command -v brew >/dev/null && brew install ffmpeg >/dev/null 2>&1) \
  && ok "ffmpeg instalado" || warn "instala ffmpeg manualmente"; fi
python3 -c "import torch" 2>/dev/null || $PIP --index-url https://download.pytorch.org/whl/cpu torch >/dev/null 2>&1 || $PIP torch >/dev/null 2>&1
for mod in "whisper:openai-whisper" "librosa:librosa" "soundfile:soundfile" "onnxruntime:onnxruntime" "rapidocr_onnxruntime:rapidocr-onnxruntime" "PIL:pillow" "numpy:numpy"; do
  m="${mod%%:*}"; p="${mod##*:}"
  python3 -c "import $m" 2>/dev/null && ok "python: $p" || { $PIP "$p" >/dev/null 2>&1 && ok "python: $p (instalado)" || warn "no se pudo instalar $p"; }
done
if [ "$DEMUCS" = 1 ]; then python3 -c "import demucs" 2>/dev/null && ok "python: demucs" || { $PIP demucs >/dev/null 2>&1 && ok "python: demucs (instalado)" || warn "demucs no instalado"; }; fi
command -v whisper >/dev/null && ok "whisper CLI" || warn "whisper CLI no está en PATH (se puede usar como módulo de Python)"

echo "2) Proyecto Remotion en $PROJ"
if [ ! -f "$PROJ/package.json" ]; then
  mkdir -p "$(dirname "$PROJ")"
  (cd "$(dirname "$PROJ")" && npx --yes create-video@latest --yes --blank --no-tailwind "$(basename "$PROJ")" >/dev/null 2>&1) && { ok "proyecto creado"; CREATED=1; } || warn "create-video falló"
else ok "ya existe"; fi
cd "$PROJ" || exit 1
npm i --no-audit --no-fund >/dev/null 2>&1
npx remotion add @remotion/media @remotion/captions @remotion/paths @remotion/fonts >/dev/null 2>&1 && ok "paquetes @remotion añadidos" || warn "npx remotion add falló"
if [ ! -d .claude/skills/remotion-best-practices ]; then
  npx --yes skills add remotion-dev/skills -a claude-code -y --copy >/dev/null 2>&1 && ok "skills oficiales de Remotion instaladas" || warn "no se pudieron instalar las skills oficiales"
else ok "skills oficiales ya instaladas"; fi

if [ "$TEMPLATE" = 1 ]; then
  echo "3) Plantilla de componentes"
  # Proyecto recién creado (andamiaje en blanco): se sustituye todo src/ por la plantilla.
  # Proyecto con trabajo previo: se añaden los archivos que falten sin sobrescribir nada.
  if [ "${CREATED:-0}" = 1 ] || grep -q "./Composition" src/Root.tsx 2>/dev/null; then
    cp -r "$SKILL_DIR/assets/remotion-template/src/." src/
  else
    cp -rn "$SKILL_DIR/assets/remotion-template/src/." src/
    warn "proyecto existente: no se sobrescribió ningún archivo de src/"
  fi
  mkdir -p scripts public/fonts public/img public/sfx public/audio public/fx
  cp "$SKILL_DIR/assets/remotion-template/scripts/stills.mjs" scripts/
  rm -f src/Composition.tsx
  sed -i.bak -e "s/export const W = [0-9]*;/export const W = $WIDTH;/" -e "s/export const H = [0-9]*;/export const H = $HEIGHT;/" -e "s/export const FPS = [0-9]*;/export const FPS = $FPS;/" src/theme.ts && rm -f src/theme.ts.bak
  python3 "$SKILL_DIR/scripts/make_grain.py" public/fx "$WIDTH" "$HEIGHT" >/dev/null && ok "texturas de grano"
  for f in "Archivo:800" "Parisienne:400"; do
    n="$(echo "$f" | sed 's/:/-/; s/ /_/g').ttf"
    [ -f "public/fonts/$n" ] || python3 "$SKILL_DIR/scripts/font_match.py" --download "$f" --dest public/fonts >/dev/null 2>&1
  done
  ok "fuentes por defecto en public/fonts (cámbialas tras identificar las de la referencia)"
  ok "plantilla copiada (src/, scripts/stills.mjs) · $WIDTH×$HEIGHT @ $FPS fps"
fi
echo "4) Prueba de render"
if npx tsc --noEmit >/tmp/mg_tsc.log 2>&1; then ok "TypeScript compila"; else warn "TypeScript con errores:"; head -15 /tmp/mg_tsc.log; fi
echo "Listo."
