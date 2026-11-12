# Slate · "Spray tan problems? We've got solutions!"

Reel vertical (1080×1920, 30 fps, ~59 s) en formato **Problema vs. Solución** para Slate (organic spray tans & facials).
Esta carpeta guarda el proyecto de edición reproducible: decisiones, línea de tiempo y scripts. Los videos en
bruto, el b-roll y los recursos se descargan de Drive y no se suben al repositorio.

## Estructura (v2: la persona hablando es la toma principal)

El talking head (video en bruto) está en pantalla de principio a fin, con lip-sync exacto: mientras la voz fuera
de cámara pregunta se la ve escuchando, y cuando responde se la ve hablando (con punch-in). Las imágenes de apoyo
viven en tarjetas, nunca reemplazan a la persona:

| Momento | Pantalla |
| --- | --- |
| Hook (0–2.6 s) | Toma de aplicación del spray + "SPRAY TAN PROBLEMS?" / *we've got* **solutions!** |
| Pregunta | Baja la **tarjeta superior** con el visual del problema y el texto del problema, sincronizado palabra a palabra |
| Respuesta | Sube la **tarjeta inferior** con el visual de la solución y el texto de la solución; ella queda al centro hablando |
| Cambio de problema | Las tarjetas salen, punch-in sobre ella + whoosh, entra el siguiente problema |
| Cierre (~12 s) | Ella a cámara con subtítulos; tres polaroids de resultados ("every skin tone…"), tarjeta con la fachada de Slate y la recepción |

| # | Problema (tarjeta superior) | Solución (tarjeta inferior) | Visual de solución |
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

- Tipografías de las referencias de Slate: **SF Pro Display Bold** (titulares), **Nyght Serif Medium Italic** en
  dorado para la palabra clave de cada solución, **Shadows Into Light** para "✕ problem #n" / "solution ✓".
- Encuadre del talking head por detección de cara (misma posición en todas las tomas), zoom más abierto en las
  preguntas y punch-in en las respuestas; cortes de una sola vez por pausa.
- Tarjetas con esquinas redondeadas, borde blanco fino y sombra suave; texto animado palabra por palabra,
  ✕/✓ dibujados a mano y destellos; polaroids con flash en el cierre.
- Sonido: whoosh por cambio de problema, pop al aparecer cada problema, swoosh al subir la solución, campanita
  al dibujarse el ✓ (sin pisar la primera palabra de la respuesta), obturador en las polaroids. Los SFX y la
  música bajan automáticamente bajo la voz. Loudness -14 LUFS / -1 dBTP.
- Música: "Million Dollar Baby" (instrumental), arrancando en un golpe fuerte; cortes en el pulso (92 BPM).
- Color: una sola corrección para todas las tomas de ella (consistencia), y balance/exposición por clip hacia un
  neutro cálido común para el apoyo; viñeta y grano finos.

## Archivos

```
scripts/edl.py           línea de tiempo: voces, textos sincronizados por palabra, pulso de la música
scripts/talk_prep.py     tomas del crudo por frase (con pre/post-roll) + seguimiento de cara
scripts/assets.py        visuales de apoyo: clip/foto, punto de entrada y encuadre para cada tarjeta
scripts/layout.py        cuadro a cuadro: qué toma y tiempo de origen (lip-sync), zoom, tarjetas y animación
scripts/compose2.py      compositor (talking head + tarjetas + polaroids + transición del hook, color, grano)
scripts/mix.py           limpieza de voz, ducking de música, SFX, loudness
render/overlay2.html     tipografía animada (Chromium → PNG transparentes), anclada a las tarjetas
render/render_overlay2.cjs, render/render_all2.sh
```

Orden de render: `edl.py` → `talk_prep.py` → `assets.py` → `layout.py` → `render_all2.sh` → `compose2.py` →
`mix.py` → mux con ffmpeg. `talk_prep.py` usa OpenCV 4 (el detector Haar ya no viene en OpenCV 5).

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
