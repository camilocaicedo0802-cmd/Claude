# Slate · "Spray tan problems? We've got solutions!"

Reel vertical (1080×1920, 30 fps, ~59 s) en formato **Problema vs. Solución** para Slate (organic spray tans & facials).
Esta carpeta guarda el proyecto de edición reproducible: decisiones, línea de tiempo y scripts. Los videos en
bruto, el b-roll y los recursos se descargan de Drive y no se suben al repositorio.

## Estructura (v3: minimalista, la persona hablando es la toma principal)

El talking head (video en bruto) está en pantalla del primer al último cuadro, también en el hook, con lip-sync
exacto: mientras la voz fuera de cámara pregunta se la ve escuchando, y cuando responde se la ve hablando. **Nada se
pone encima de su cara ni de su cabeza**: el encuadre (por detección de cara) deja libres una banda arriba para el
texto y un espacio bajo el mentón para la tarjeta. La pared de fondo va desenfocada (segmentación de persona, efecto
retrato) para quitar el texto impreso y el ruido visual.

| Momento | Pantalla |
| --- | --- |
| Hook (0–2.6 s) | Ella a cámara; arriba "SPRAY TAN PROBLEMS?", sobre la camiseta *we've got* **solutions!** |
| Pregunta | Arriba, sobre la pared desenfocada: etiqueta "problem #n" + el problema, palabra por palabra con la voz |
| Respuesta | Abajo, bajo el mentón: una sola tarjeta con el visual de la solución; el texto de la solución va debajo de la tarjeta para no tapar la imagen |
| Cierre (~12 s) | Ella a cámara con subtítulos arriba; tres miniaturas de resultados que entran con "every skin tone / undertone / glow goal"; fachada de Slate y recepción en la tarjeta |

| # | Problema (texto arriba) | Solución (texto abajo) | Visual de la tarjeta |
| --- | --- | --- | --- |
| 1 | Pale or dull skin? | A custom *spray tan* | Misma clienta: antes / después |
| 2 | Need color ASAP? | *Rapid* tan formula | Aplicación con la pistola Slate |
| 3 | Dry or patchy skin? | *Exfoliate* 24 hours before | Exfoliación (cepillo, luego exfoliante en la mano) |
| 4 | Tan fading unevenly? | *Moisturize* daily | Crema en la pierna |
| 5 | Tan sticking to hands & feet? | *Barrier cream* in the room | Técnica de Slate mostrando el producto |
| 6 | Going on vacation? | Book *1–2 days* before your trip | Clienta con el bronceado terminado |
| 7 | Wedding or special event? | Proper prep + *custom shade* | Clienta en vestido, luego aplicación |
| 8 | Not sure which shade or solution is right for you? | *Personalized* consultation | Consulta real en cabina |

Se mantienen **las dos voces originales**. En el par 7 se usó lo que ella dijo realmente ("book your appointment
one to two days before your wedding… and we'll do a custom shade for you").

## Estilo

- Tipografías de las referencias de Slate: **SF Pro Display Bold** (titulares), **Nyght Serif Medium Italic** para la
  palabra clave (dorado sobre oscuro, bronce sobre la pared clara), **Shadows Into Light** para "problem #n" /
  "solution".
- Minimalista: un solo bloque de texto por zona, sin estrellas, sin bordes, sin destellos ni light leaks; textos que
  entran con un fade + desenfoque suave, tarjeta de esquinas redondeadas con sombra muy ligera.
- Encuadre del talking head igual en todas las tomas; un corte por pausa, con un punch-in suave al cambiar de problema.
- Sonido discreto: pop suave al aparecer el problema, swoosh corto al entrar la solución, campanita baja al terminar
  la pregunta, whoosh leve entre problemas. Música y efectos bajan solos bajo la voz. -14 LUFS / -1 dBTP.
- Música: "Million Dollar Baby" (instrumental), arrancando en un golpe fuerte; cortes en el pulso (92 BPM).
- Color: una sola corrección para todas las tomas de ella (algo menos saturada, natural), y balance/exposición por
  clip hacia un neutro cálido común para el apoyo; grano muy fino.

## Archivos

```
scripts/edl.py           línea de tiempo: voces, textos sincronizados por palabra, pulso de la música
scripts/talk_prep.py     tomas del crudo por frase (con pre/post-roll) + seguimiento de cara (incluye la toma del hook)
scripts/talk_masks.py    máscaras de persona (MediaPipe) para desenfocar solo la pared
scripts/assets.py        visuales de apoyo: clip/foto, punto de entrada y encuadre para cada tarjeta
scripts/layout3.py       cuadro a cuadro: qué toma y tiempo de origen (lip-sync), zoom y tarjetas
scripts/compose3.py      compositor (talking head + fondo desenfocado + tarjetas, color, grano)
scripts/mix.py           limpieza de voz, ducking de música, SFX, loudness
render/overlay3.html     tipografía animada (Chromium → PNG transparentes)
render/render_overlay3.cjs, render/render_all3.sh
```

Orden de render: `edl.py` → `talk_prep.py` → `talk_masks.py` → `assets.py` → `layout3.py` → `render_all3.sh` →
`compose3.py` → `mix.py` → mux con ffmpeg. `talk_prep.py` usa OpenCV 4 (el detector Haar ya no viene en OpenCV 5);
`talk_masks.py` usa MediaPipe con el modelo `selfie_multiclass_256x256.tflite`.

Las fuentes no se incluyen en el repositorio (licencias): vienen de la carpeta de Drive *FUENTES PRO ELEGANTES* y
van en `render/fonts/` (`SFPRODISPLAYBOLD.OTF`, `SFPRODISPLAYMEDIUM.OTF`, `NyghtSerif-MediumItalic.ttf`,
`ShadowsIntoLight-Regular.ttf`). `timeline.json` es la línea de tiempo final que generó `edl.py`.

Se exportan dos versiones: con música y sin música (voces + efectos), por si se prefiere añadir el audio desde
Instagram/TikTok. La pista es una canción comercial: en cuentas de empresa puede quedar silenciada o bloqueada, y
en ese caso conviene publicar la versión sin música y elegir el audio dentro de la app.

## Fotos de stock (Unsplash, licencia Unsplash)

| Uso | Foto |
| --- | --- |
| Need color ASAP? | Raghavendra Mithare — https://unsplash.com/photos/a-pink-alarm-clock-with-a-daisy-face-5nHU_OUi2Z0 |
| Dry or patchy skin? | Alexander Grey — https://unsplash.com/photos/persons-palm-in-close-up-photography-tWTFjznQlBA |
| Exfoliate | Megan Dujardin — https://unsplash.com/photos/a-woman-with-a-ring-on-her-finger-LB_OWger9XE |
| Exfoliate (2) | Anita Austvika — https://unsplash.com/photos/a-person-making-a-dough-Z75dEgdKCS0 |
| Tan fading unevenly? | Meg Sanchez — https://unsplash.com/photos/person-wearing-brown-sunday-hat-during-daytime-QKKBxetBH6s |
| Moisturize daily | Mina Rad — https://unsplash.com/photos/woman-applying-cream-to-leg-EM9VdLxwqPs |
| Going on vacation? | Marissa Grootes — https://unsplash.com/photos/open-suitcase-with-travel-essentials-and-hat-TVllFyGaLEA |
| Wedding or special event? | Gemali Martinez — https://unsplash.com/photos/a-person-in-a-white-dress-TjH8K0vKjcA |

Todo lo demás es material propio de Slate (videos en bruto, b-roll de bronceados y del salón, fotos antes/después).
