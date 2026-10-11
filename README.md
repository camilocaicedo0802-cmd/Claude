# Claude · editor de vídeo con Remotion

Vídeo vertical 1080×1920 a 30 fps hecho con Remotion, que imita el estilo de `referencia/referencia.mp4` aplicado a la locución `video/public/audio/voz.mp3`.

- **`estilo.md`**: guía de estilo con valores medidos de la referencia. Las correcciones aprobadas se añaden al final.
- **`video/`**: proyecto Remotion (skills oficiales en `video/.claude/skills`).
  - `src/Main.tsx`: línea de tiempo (escenas, transiciones, voz, música y SFX).
  - `src/scenes/`: una escena por archivo. `src/components/`: subtítulos, cámara, recortes, motion graphics.
  - `src/data/captions.ts`: subtítulos palabra a palabra (Whisper). `src/data/sfx.ts`: mapa de efectos de sonido.
- **`transcripcion/voz.json`**: salida de Whisper con tiempos por palabra.
- **`assets/tools/`**: scripts de recorte de fondo (`cutout.py`), audio (`audio_build.py`) y subtítulos (`captions_build.py`).
- **`render/`**: borradores renderizados.
- **`CREDITOS.md`**: licencias de fotos, audio, fuentes y modelos.

## Comandos
```bash
cd video
npm i
npx remotion studio                                   # vista previa interactiva
npx remotion render Main out/video.mp4 --crf=18       # render final
# limitador de audio (pico real ≤ -1 dBFS) sin recodificar el vídeo:
ffmpeg -i out/video.mp4 -c:v copy -af "alimiter=limit=0.85:attack=2:release=60:level=disabled" -c:a aac -b:a 192k -movflags +faststart ../render/video.mp4
OUT_DIR=/tmp/stills node scripts/stills.mjs 1 5 10    # fotogramas sueltos para revisar
```
