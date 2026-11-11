# Slate · "Spray tan problems? We've got solutions!"

Reel vertical (1080×1920, 30 fps, ~60 s) en formato **Problema vs. Solución** para Slate (organic spray tans & facials).
Esta carpeta guarda el proyecto de edición reproducible: decisiones, línea de tiempo y scripts. Los videos en
bruto, el b-roll y los recursos se descargan de Drive y no se suben al repositorio.

## Estructura del video

| Bloque | Qué pasa |
| --- | --- |
| Hook (0–2.6 s) | Toma de aplicación del spray en cabina + "SPRAY TAN PROBLEMS?" / *we've got* **solutions!** con pop y destellos |
| 8 pares problema/solución | La voz que pregunta abre el problema a pantalla completa; cuando responde la otra voz, el problema sube a la mitad superior y la solución entra desde abajo |
| Cierre (~13 s) | Ella a cámara (lip-sync) + montaje de resultados de 3 clientas ("every skin tone…"), fachada de Slate, recepción y resultado final |

| # | Problema (arriba) | Solución (abajo) | Visual de solución |
| --- | --- | --- | --- |
| 1 | Pale or dull skin? | A custom *spray tan* | Misma clienta: antes (arriba) / después (abajo) |
| 2 | Need color ASAP? | *Rapid* tan formula | Aplicación con la pistola Slate |
| 3 | Dry or patchy skin? | *Exfoliate* 24 hours before | Exfoliación con cepillo |
| 4 | Tan fading unevenly? | *Moisturize* daily | Crema en la pierna |
| 5 | Tan sticking to hands & feet? | *Barrier cream* in the room | Técnica de Slate mostrando el producto |
| 6 | Going on vacation? | Book *1–2 days* before your trip | Clienta con el bronceado terminado |
| 7 | Wedding or special event? | Proper prep + *custom shade* | Clienta con vestido después del bronceado |
| 8 | Not sure which shade or solution is right for you? | *Personalized* consultation | Consulta real en cabina |

Se mantienen **las dos voces originales**: la que pregunta (fuera de cámara) y la que responde. En el par 7 se usó
lo que ella dijo realmente ("book your appointment one to two days before your wedding… and we'll do a custom
shade for you").

## Estilo

- Tipografías de las referencias de Slate: **SF Pro Display Bold** (titulares), **Nyght Serif Medium Italic** en
  dorado para la palabra clave de cada solución, **Shadows Into Light** para las etiquetas "problem #n" / "solution ✓".
- Animación de texto palabra por palabra sincronizada con cada voz (blur-in + subida), etiquetas con trazo dibujado
  (✕ coral para el problema, ✓ dorado para la solución) y estrellas que destellan.
- Transiciones: zoom con destello + light leak (entrada y cierre), whip horizontal/vertical con motion blur entre
  pares, panel de solución que sube con desenfoque de movimiento.
- Sonido: whoosh por transición, pop al aparecer cada problema, swoosh al subir la solución, campanita al dibujarse
  el ✓ (nunca encima de la primera palabra de la respuesta), obturador en las fotos de resultados y destello final.
  Los SFX y la música bajan automáticamente cuando hay voz.
- Música: "Million Dollar Baby" (instrumental), arrancando en un golpe fuerte; los cortes caen en el pulso (92 BPM).
- Color: balance de blancos y exposición por clip hacia un neutro cálido común, curva S suave, negros levemente
  levantados, viñeta y grano finos para unificar teléfono, cámara y stock.

## Archivos

```
scripts/edl.py           línea de tiempo: voces, textos sincronizados por palabra, pulso de la música
scripts/assets.py        qué clip/foto va en cada lugar, punto de entrada y encuadre; genera mezzanines
scripts/compose.py       compositor cuadro a cuadro (split, Ken Burns, transiciones, color, grano)
scripts/mix.py           limpieza de voz, ducking de música, SFX, loudness -14 LUFS / -1 dBTP
render/overlay.html      capa de tipografía animada (se renderiza con Chromium en PNG transparentes)
render/render_overlay.cjs, render/render_all.sh
```

Orden de render: `edl.py` → `assets.py` → `render_all.sh` → `compose.py` → `mix.py` → mux con ffmpeg.

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
| Tan fading unevenly? | Meg Sanchez — https://unsplash.com/photos/person-wearing-brown-sunday-hat-during-daytime-QKKBxetBH6s |
| Moisturize daily | Mina Rad — https://unsplash.com/photos/woman-applying-cream-to-leg-EM9VdLxwqPs |
| Going on vacation? | Marissa Grootes — https://unsplash.com/photos/open-suitcase-with-travel-essentials-and-hat-TVllFyGaLEA |
| Wedding or special event? | Gemali Martinez — https://unsplash.com/photos/a-person-in-a-white-dress-TjH8K0vKjcA |

Todo lo demás es material propio de Slate (videos en bruto, b-roll de bronceados y del salón, fotos antes/después).
