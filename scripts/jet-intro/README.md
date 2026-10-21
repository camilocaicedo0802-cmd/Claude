# Intro "Vuelo en jet privado"

Edición de 29 s (1920×1080, 30 fps) a partir del video en crudo *Vuelo en jet privado.mov* (38 min), con el ritmo y los efectos del video de referencia (*Construyendo en París*).

Resultado: [`media/edits/jet-privado-intro.mp4`](../../media/edits/jet-privado-intro.mp4)

## Estructura (sincronizada a 130 BPM)

| Tiempo | Bloque | Qué pasa |
| --- | --- | --- |
| 0:00–2:8 | Flash montage B/N | 12 cortes de medio beat (yates, Cuatro Torres, rooftop, jet, Lamborghini…) con punch-zoom y blur de movimiento; termina en flash blanco |
| 2:8–7:4 | Vlog | Selfie en el jet, hablando a cámara con jump cuts, Lamborghini; parpadeo en negativo antes del drop |
| 7:4–10:2 | **Drop + título** | Impacto, shake, "VUELO EN / JET PRIVADO" con efecto máquina de escribir, flashes en negativo y destello dorado |
| 10:2–17:5 | Viaje | Lamborghini, terminal privada, caminata a la pista, embarque, cabina, ventanilla sobre las nubes. Gradación teal-orange, light leaks, aberración RGB |
| 17:5–19:4 | "LET'S DO IT" | Plano en negativo con el texto y su copia invertida, como en la referencia |
| 19:4–25:9 | Atardecer / noche | Rooftop sobre Madrid, cena, puerto con yates, palmeras, compras. Gradación dorada |
| 25:9–29:1 | Cierre | "JET PRIVADO" con tracking animado y glow, fade a negro |

## Música

"Waka Floka Type" de [Mixkit](https://mixkit.co/free-stock-music/hip-hop/) (licencia Mixkit Stock Music Free License: uso comercial y en YouTube sin atribución). El drop de la pista (14.786 s) cae justo en el título. Los whooshes, el impacto del drop y los clicks de máquina de escribir se sintetizan en `audio.py`.

## Regenerar

Requiere Python 3 con `numpy`, `opencv-python-headless`, `pillow`, y ffmpeg.

```
work/raw/raw.mov            # video en crudo
work/music/364.mp3          # https://assets.mixkit.co/music/364/364.mp3
work/fonts2/Syncopate.ttf   # Google Fonts, Syncopate 700
work/fonts2/Playfair.ttf    # Google Fonts, Playfair Display
```

```bash
python3 render.py --preview   # pasada rápida a 960×540
python3 render.py             # 1080p
python3 audio.py 29.0667      # música + SFX -> work/mix.wav
ffmpeg -i work/video_noaudio.mp4 -i work/mix.wav -c:v copy -c:a aac -b:a 320k -shortest jet-privado-intro.mp4
```

`JET_WORKDIR` cambia la carpeta de trabajo. Los cortes se editan en `edl.py` (segundo de origen, duración en beats, look, velocidad y efectos).
