# Farmasi · Nutriplus Gummies (edición en Remotion)

Edición vertical **1080x1920 a 60 fps** de la toma UGC sobre las gomitas de sidra de manzana, con el estilo del vídeo de referencia (`referencia/referencia.mp4`). La guía de estilo con todos los valores medidos está en [`estilo.md`](estilo.md).

## Requisitos

- Node 22, ffmpeg 6, Python 3.13 con `faster-whisper`, `onnxruntime`, `librosa`, `opencv-python-headless<5`, `fonttools`.
- Skills oficiales de Remotion instaladas en `.claude/skills` (`npx skills add remotion-dev/skills`).

## Cómo se reproduce

Los medios pesados no están en Git: se descargan de las carpetas de Drive del cliente.

```bash
python3 scripts/descargar_drive.py material/lista_sfx.json public/sfx 6       # SFX del cliente
python3 scripts/descargar_drive.py material/lista_broll.json public/broll 6   # b-roll del cliente
python3 scripts/descargar_drive.py material/lista_musica.json public/musica 4 # música del cliente
python3 scripts/mixkit_buscar.py material/mixkit/resultados.json apple salad    # b-roll de Mixkit (licencia libre)
python3 scripts/transcribir.py public/crudo/toma_ugc.mov datos/transcripcion_ugc.json es large-v3
python3 scripts/recortar_persona.py public/proxy/ugc.mp4 public/matte/ugc_persona.webm 0.25
python3 scripts/preparar_edicion.py      # A-roll cortado, capa de persona y voz procesada
npm run dev                              # Remotion Studio
./scripts/render.sh out/farmasi.mp4      # render final
```

## Estructura

| Ruta | Qué es |
|---|---|
| `datos/guion_fuente.py` | Fragmentos de la toma que se conservan y palabras con tiempos (Whisper corregido) |
| `src/plan.ts` | El montaje como datos: bloques de subtítulos, cámara, escenas, superposiciones |
| `src/sonido.ts` | Todos los SFX sincronizados (solo de la carpeta del cliente) y la curva de la música |
| `src/componentes/` | A-roll con capa de persona, subtítulos, tarjetas de cristal, escenas y light leak |
| `scripts/` | Descarga, transcripción, recorte de persona (RVM), preparación, fotogramas de control y render |
