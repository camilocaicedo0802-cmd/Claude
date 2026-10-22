# Intro "Vuelo en jet privado"

Edición de 29 s (1920×1080, 30 fps) a partir del video en crudo *Vuelo en jet privado.mov* (38 min) y cuatro tomas extra de iPhone, con el ritmo y los efectos del video de referencia (*Construyendo en París*).

Resultado: [`media/edits/jet-privado-intro.mp4`](../../media/edits/jet-privado-intro.mp4)

## Música y sincronización

Myke Towers, "Pauta y Flow", tramo 1:04.3–1:33.3. La canción va a 80.5 BPM (1 pulso = 0.7454 s); los cortes se miden en medios pulsos (0.3727 s). El bajo vuelve en 1:11.712 (entrada del coro) y cae exactamente en el corte al título (7.47 s del video).

La canción tiene derechos de autor: no se incluye en el repositorio y, al subir el video a YouTube o Instagram, la plataforma puede reclamarlo (Content ID).

## Estructura

| Tiempo | Bloque | Qué pasa |
| --- | --- | --- |
| 0:00–2:2 | Flash montage B/N | 12 cortes de 1/16 (yates, Cuatro Torres, subida al jet, ventanilla, Lamborghini, primera clase…) con punch-zoom y blur de movimiento; termina en flash blanco |
| 2:2–7:5 | Vlog | Selfie en primera clase, hablando en el jet privado con jump cuts, Lamborghini; parpadeo en negativo antes del drop |
| 7:5–10:4 | **Drop + título** | Entra el bajo: shake, "VUELO EN / JET PRIVADO" letra a letra, flashes en negativo y destello dorado |
| 10:4–17:9 | Lambo + jet | El protagonista en el Lamborghini, terminal privada, camino a la escalerilla, bajada del jet, caminata junto al avión y subida al auto, cabina, ventanilla sobre las nubes |
| 17:9–19:8 | "LET'S DO IT" | Plano en negativo con el texto y su copia invertida, como en la referencia |
| 19:8–25:7 | Primera clase / atardecer / noche | Rooftop, suite de primera clase, cena a bordo, cena en Madrid, puerto con yates, compras |
| 25:7–29:1 | Cierre | "JET PRIVADO" con tracking animado y glow, fade a negro |

Las tomas verticales (las del crudo y las de iPhone) se recortan a 16:9 para llenar el cuadro; las de iPhone vienen en HDR (HLG) y se convierten a SDR con `zscale` + `tonemap`. Los whooshes, el impacto del drop y los clicks de máquina de escribir se sintetizan en `audio.py`.

## Regenerar

Requiere Python 3 con `numpy`, `opencv-python-headless`, `pillow`, y ffmpeg con `zscale`.

```
work/raw/raw.mov                 # video en crudo
work/newclips/IMG_8829.MOV ...   # tomas extra (IMG_8829, IMG_8967, IMG_9018)
work/music2/pauta.mp3            # la canción
work/fonts2/Syncopate.ttf        # Google Fonts, Syncopate 700
work/fonts2/Playfair.ttf         # Google Fonts, Playfair Display
```

```bash
python3 render.py --preview   # pasada rápida a 960×540
python3 render.py             # 1080p
python3 audio.py 29.0667      # música + SFX -> work/mix.wav
ffmpeg -i work/video_noaudio.mp4 -i work/mix.wav -c:v copy -c:a aac -b:a 320k -shortest jet-privado-intro.mp4
```

`JET_WORKDIR` cambia la carpeta de trabajo. Los cortes se editan en `edl.py` (origen, duración en medios pulsos, look, velocidad, recorte vertical y efectos).
