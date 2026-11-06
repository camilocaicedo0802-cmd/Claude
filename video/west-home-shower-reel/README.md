# West Home Improvement · Reel de duchas (Tulsa)

Reel vertical de 32,6 s (1080×1920, 30 fps) editado por código con el estilo del reel de referencia de la casa:
textos que entran con desenfoque y suben, subtítulos palabra por palabra (palabras clave en negrita o en naranja),
texto detrás de las personas, una tarjeta flotante con un adelanto en el hook, una píldora de vidrio con el logo,
transiciones whip, zoom y giro sincronizadas con el beat, speed ramps y sonidos en cada texto y cada corte.

Solo están aquí el código y los datos livianos. Los videos originales están en las carpetas de Drive del cliente y
el render final se entregó por el chat.

## Identidad usada (carpeta de branding)

- Tipografía: **Poppins** (Black/ExtraBold para títulos, Regular/Bold para subtítulos). Cabinet Grotesk se probó y se descartó.
- Color: naranja de marca `#FF4D00` con degradado a `#FF7A3D`; blanco; azul marino `#13293A` como reserva.
- Logo: `WEST HOME/PNG/Recurso 7@4x.png` (blanco) para el cierre y el isotipo `Recurso 3@4x.png` en la píldora.
- Etiqueta naranja con texto blanco, como en la portada de Facebook ("HOME REMODELING & IMPROVEMENT").

## Archivos

| Archivo | Qué hace |
| --- | --- |
| `edit/timeline.py` | Cortes: tomas de Félix sincronizadas, B-roll, velocidades, zooms, transiciones. Beat = 0,035 + 0,6·k s (100 BPM). |
| `edit/overlays.py` | Todos los textos y gráficos, anclados a las palabras de `words.json` (transcripción de las tomas). |
| `edit/gfx.py` | Render de texto, sombras, glow, píldora de vidrio, subtítulos. |
| `edit/core.py` | Lectura de clips, remapeo de tiempo (speed ramps), color, desenfoques. |
| `edit/render.py` | Compositor por fotograma (`--from/--to` para partes, `--stills` para revisar). |
| `edit/audio.py` | Voz (limpieza, EQ, compresión, −17 LUFS por toma), música empalmada al compás con ducking, SFX sintetizados, máster −14 LUFS. |
| `edit/extract_all.py` | Extrae de los originales 4K solo los tramos usados. |

## Rehacer

```bash
python3 edit/extract_all.py
python3 edit/render.py out/seg0.mp4 --from 0 --to 8.2     # y así hasta 32.6, en paralelo
python3 edit/audio.py
```

Las rutas de `core.ROOT` apuntan a la carpeta de trabajo de la sesión; cámbialas si mueves el proyecto.
Requiere Python con `numpy scipy opencv-python-headless pillow pyloudnorm onnxruntime` y ffmpeg; el modelo
`u2net_human_seg.onnx` (rembg) para recortar a las personas.

Música: pista instrumental original generada con ElevenLabs Music v2.5 (Higgsfield), 100 BPM.
