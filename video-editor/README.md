# Editor de vídeo vertical (Remotion)

Edición vertical 1080×1920 a 30 fps del anuncio de **305 Media Club**, con el estilo medido de `referencia.mp4` (ver [`estilo.md`](estilo.md)).

## Requisitos

- Node 22, ffmpeg 6, Python 3.13 con `faster-whisper`, `torch`/`torchaudio` (CPU), `onnxruntime`, `fonttools`, `scipy`.
- Material (no se sube a git): `assets_in/` (bruto, referencia, carpetas de Drive del cliente) y `public/fonts/` (SF Pro Display del cliente).

## Flujo

```bash
python3 -I scripts/transcribe.py <audio> <salida.json>           # Whisper large-v3 con tiempos por palabra
python3 -I scripts/align_words.py <audio> analysis/segments.json analysis/segments_aligned.json  # alineación forzada MMS_FA
python3 -I scripts/prepare_clips.py                              # tomas: color, voz y recorte de la persona (MODNet)
python3 -I scripts/prepare_broll.py                              # b-roll de Mixkit recortado a 4:5 y 9:16
python3 -I scripts/build_edl.py                                  # genera src/data/edl.json (línea de tiempo en fotogramas)
npx remotion studio                                              # vista previa
npx remotion render Main out/final.mp4 --codec=h264 --crf=16 --audio-bitrate=320k
```

## Estructura

| Archivo | Qué hace |
|---|---|
| `src/Main.tsx` | Orden de capas: toma → lo que va detrás de la persona → persona recortada → textos delante |
| `src/components/Highlight.tsx` | Palabras destacadas con la textura de la referencia (vídeo posterizado a dos rojos o grises dentro de las letras + glitch por franjas) y kicker tecleado |
| `src/components/Overlays.tsx` | Subtítulos palabra a palabra, tarjetas de b-roll, monedas de neón, montaje, destello de luz, transiciones de desenfoque |
| `src/components/SoundTrack.tsx` | Voz, voz en off, música con automatización de volumen y SFX |
| `scripts/build_edl.py` | Todas las decisiones de montaje (tiempos, posiciones, SFX, música) |
| `scripts/shear_font.py` | Genera los estilos de SF Pro que faltaban (Black/Light rectas, Italic) |
