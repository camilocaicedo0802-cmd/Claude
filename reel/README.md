# Reel Macizo · Remotion

Edición vertical (1080×1920, 30 fps) del vídeo de Macizo siguiendo el estilo del reel de referencia.
La guía de estilo con valores medidos está en [`estilo.md`](estilo.md); las correcciones aprobadas se añaden
al final de ese archivo para que se mantengan.

## Requisitos

- Node 22, ffmpeg, Python 3 con `faster-whisper`, `numpy`, `librosa` (solo análisis) y `opencv-python-headless<5`.
- Skills oficiales de Remotion: `npx skills add remotion-dev/skills` (ya instaladas en `.agents/skills`).

## Preparar los medios

Los medios pesados no están en git. Para regenerarlos desde las carpetas de Drive:

```bash
bash scripts/prepare_media.sh
```

Esto descarga el VIDEO BASE, b-rolls, fotos, clips de interiores y la música; aplica el etalonaje cálido,
transcribe con Whisper large-v3 (tiempos por palabra), construye el EDL (`src/data/edl.json`) y la pista de voz
editada (`public/audio/voz.wav`), y detecta la cara para encuadrar los punch-ins.

## Previsualizar y renderizar

```bash
npm run dev
```

```bash
npx remotion render Reel out/reel_macizo.mp4 --codec=h264 --crf=18 --audio-bitrate=320k
```

## Dónde se edita cada cosa

| Qué | Archivo |
| --- | --- |
| Cortes de la voz (silencios, repeticiones eliminadas) | `scripts/build_edl.py` (`CONTENT_CUTS`) |
| Bloques de subtítulos, b-roll, punch-ins, transiciones y SFX | `src/timeline.ts` |
| Colores y tipografías | `src/theme.ts` |
| Objetos de motion graphics | `src/components/Graphics.tsx` |
| Subtítulos cinéticos palabra a palabra | `src/components/Captions.tsx` |
| Encuadre del presentador | `src/components/TalkingHead.tsx` |
| Mezcla (voz, música, SFX) | `src/components/AudioLayer.tsx` |
