# Reel LB-OCT-12 · Rutina después del trabajo (ASMR)

- **Ángulo:** casos reales · **Objetivo:** conectar · **CTA:** comentar "rutina" · **Formato:** reel 9:16
- **Duración:** 56,7 s · 1080×1920 · 30 fps · H.264 + AAC 48 kHz estéreo
- **Fuentes:** TAN Pearl (frases principales) y Glacial Indifference Bold (mayúsculas espaciadas y "productividad.")

Este folder guarda el proyecto de edición reproducible (scripts). El video final y los clips en crudo
**no** se suben al repositorio porque es público: el reel se entrega aparte.

## Corte por cuerpo

| Cuerpo | Toma (clip · segundos) | Entrada / salida | Sonido ASMR |
| --- | --- | --- | --- |
| 1 | c1 1,95–4,6 y 7,25–11,15 (cámara lenta al pasar) | Llega a casa; al pasar frente a la cámara, **efecto máscara**: la cocina aparece detrás de ella | Clic suave del picaporte, pasos lentos y amortiguados, roce de la mochila, "fush" |
| 2 | c2 0,2–5,95 y 8,3–9,7 | Se sirve la bebida; pasa por el frente de la cámara y su cuerpo hace el corte al pasillo | Líquido cayendo en la taza, tintineo muy suave, sorbo, "fush" |
| 3 | c345 2,55–6,95 | Entra al pasillo en toma frontal → corte | Ambiente casi en silencio (viento suave muy bajo), pasos que se acercan, roce de la ropa |
| 4 | c345 10,55–17,85 | Entra a la habitación desde la toma posterior → corte | Pasos suaves, roce ligero de la ropa |
| 5 | c345 118,6–126,4 | Entra a la habitación (frontal) y al baño; cubre la cámara con el cabello | Clic de interruptor antiguo, agua corriendo muy suave, "fush" del cabello |
| 6 | c6 1,45–10,5 | Descubre la cámara al bajar la bata del perchero; la cubre al quitarse la camisa | **Tela de la bata** (sonido clave), roce del tejido de punto |
| 7 | c78 0,55–16,4 | Descubre la cámara al ponerse la bata; la cubre con el cabello | Seda/algodón al acomodarse, cabello, "fush" |
| 8 | c78 72,45–74,4 · 24–25,95 · 61,7–63,85 · 75,3–77,05 · 89,25–95,4 | Abre desde la pierna; microtomas del reto en el teléfono y del calendario impreso; masaje | Manos sobre la piel, yemas en la pantalla, hoja del calendario, zumbido muy bajo del masajeador |

## Texto

- **Parte 1** — "No todo tiene que ser productividad.": aparece lentamente (fundido con desenfoque, línea por
  línea) desde el segundo 0,7 y se va al terminar la escena de la cocina (cuerpos 1–2).
- **Parte 2** — "A veces hay que parar, respirar y dedicarte un momento.": entra al final del cuerpo 7 y
  desaparece lentamente al final del video (cuerpos 7–8).
- Entre los cuerpos 3 y 6 no hay texto: predominan la imagen y los sonidos.
- Estilo tomado de las portadas: ciruela `#48223D`, rosa `#BC5C5F`, crema `#FAEDCD`, destellos de 4 puntas
  y una bruma clara arriba para que el texto se lea sin tapar la acción.

## Audio

Mezcla a −18 LUFS integrados (pico −1,6 dBFS): íntima, no fuerte. Todo pasa por filtros de 24 dB/oct
(sin agudos estridentes ni metálicos), una compresión muy suave y una sala corta casi seca.
Entre acciones solo queda ruido rosa a ~−40 LUFS. Hay un pad ambiental mínimo (acordes lentos, sintetizado
aquí mismo) a −32 LUFS, por debajo del límite de −30 dB. El audio original de los clips no se usa:
tenía las indicaciones del equipo durante las tomas.

Efectos: previsualizaciones de [Mixkit](https://mixkit.co/free-sound-effects/) (licencia gratuita de
Mixkit, permite uso comercial en videos) con los IDs que aparecen en `audio.py`, más texturas
sintetizadas (tela, piel, zumbido, ruido rosa, pad) sincronizadas con el movimiento de cada toma.

## Cómo regenerarlo

Requisitos: ffmpeg, Python 3 con `numpy scipy opencv-python-headless pillow mediapipe`, el modelo
[`selfie_multiclass_256x256.tflite`](https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite)
(para el efecto máscara) y, en Linux, `libegl1`.

```bash
# raw/: los 5 clips de la carpeta de Drive renombrados c1 c2 c345 c6 c78 (ver edl.py)
# fonts/: TAN-Pearl-Regular.otf y GlacialIndifference-Bold.otf
# sfx/: previsualizaciones de Mixkit guardadas como <id>.mp3
python video.py --raw raw --fonts fonts --model selfie_multiclass_256x256.tflite --out video.mp4
python audio.py --raw raw --sfx sfx --out mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 19 -maxrate 6500k \
       -bufsize 13000k -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart LB-OCT-12_reel.mp4
```

`python edl.py` imprime la línea de tiempo. Para revisar cuadros sueltos sin renderizar todo:
`python video.py ... --only --stills 120,400 --still-dir .`
