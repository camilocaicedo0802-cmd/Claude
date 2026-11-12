# SLATE · Spray Tan Problems? We've Got Solutions! (reel 9:16)

> **Versión 5 (vigente): línea minimalista + presets y sonidos de la librería de la clienta, `edit/mn2_*.py`.**
> Mismo corte, voces y tiempos que la v4 (`mn2_timeline.py` importa `mn_timeline.py`); cambian los textos, el
> sonido y dos elementos visuales. Los presets de texto de la librería (archivos de CapCut / DaVinci / After
> Effects) se leyeron y se **replicaron con sus valores numéricos** (curvas bezier, duraciones, desplazamientos,
> desenfoques, escalonado entre palabras):
> - **Gancho:** *Texto Elegancia Real* (línea pequeña palabra por palabra + cursiva grande que se revela de izquierda
>   a derecha con parpadeo y desenfoque).
> - **Problemas:** número grande + líneas Light / SemiBold con las curvas *Minimal slide / bounce* de CapCut.
> - **Soluciones:** *Dúo Cinemático* (palabra sans + cursiva rosada metida debajo; la sans queda encima para que se
>   lean las dos) y *Texto Elegante* (trazo de marcador detrás de los números grandes "24h" y "1-2 days").
> - **Cierre:** *Three Aesthetic Words* (filas que suben con desenfoque, contraste Light / Bold / cursiva).
> - **Fachada:** *SB Fade blanco elegante* ("COME SEE US AT" espaciado + "Slate" escrito a máquina). Por pedido de la
>   clienta se quitó la última línea del CTA ("we'll find the perfect tan for you."); con `CTA=short` sale la variante
>   que además termina el video en "come see us at Slate" (voz silenciada desde el "and", ~55.3 s).
> - **Subtítulos de la presentadora:** *Apple Texto Deslizante 2* (palabra que se desliza hacia arriba); las palabras
>   clave pasan a la cursiva del preset.
> - **Fuentes:** Poppins (la sans de la marca, en lugar de la Inter de los presets) + la cursiva de los presets
>   (Ocean Delight, de Blankids Studio; licencia por confirmar, alternativa libre: Great Vibes, OFL).
> - **Visual de la librería:** LUT "Calor Desvanecido" al 55 %, PNG "Degradado a negro subtítulos" bajo los textos de
>   los b-roll, film burn cálido en la entrada del cierre (alineado a su cuadro más brillante).
> - **Sonido de la librería** (`mn/sfx2`, wav 48 kHz): chasquido en el gancho, gota de agua en cada problema,
>   swoosh en cada solución, trazo de marcador, pop en los números, whoosh de título al cierre, obturador en el
>   sticker, teclas en la máquina de escribir y un brillo suave al final. Voz −15 LUFS, música −28.5 LUFS,
>   master −14 LUFS / −1.7 dBFS.
>
> ```bash
> python3 edit/mn2_render.py out/video_noaudio.mp4
> python3 edit/mn2_mix.py /ruta/mn/sfx2 /ruta/music.wav out/mix.wav
> CTA=short python3 edit/mn2_render.py out/video_noaudio_corto.mp4   # variante: termina en "come see us at Slate"
> CTA=short python3 edit/mn2_mix.py /ruta/mn/sfx2 /ruta/music.wav out/mix_corto.wav
> ```
>
> El material de la clienta (presets, SFX, LUT, PNG, film burn, fuentes) no se incluye en el repo.

> **Versión 4: nueva línea visual minimalista, `edit/mn_*.py`.** Rehecha desde cero con el brief nuevo
> de la clienta y las tres referencias nuevas (Reel_referencia_slate_1/2/3):
> - **Tipografía:** las mismas fuentes (Poppins + Playfair Display Italic), planas, sin brillo; solo una sombra
>   casi invisible para legibilidad. Tamaños que juegan entre sí (palabra clave grande + línea pequeña, números
>   grandes "24h", "1-2"), como la referencia 2.
> - **Estructura:** cada problema numerado ("1." + texto palabra por palabra con la voz que pregunta + fila de
>   progreso de 8 puntos, como el ranking de la referencia 1) sobre un b-roll del problema; la solución con la
>   presentadora y subtítulos de **una palabra** (referencias 1 y 3; las palabras clave pasan a Playfair cursiva),
>   y después un b-roll con la palabra clave entrando con un deslizamiento corto y un **subrayado** que se dibuja.
> - **Cierre:** frase que se construye sobre cuatro clientas, un momento **"sticker"** (la presentadora recortada
>   con borde blanco, referencia 3; recorte con rembg/u2net_human_seg), fachada SLATE y **fundido a negro**.
> - **Material de la clienta (Drive "material de edición", no incluido en el repo):** LUT "Calor Desvanecido" al
>   55 % (`lib/lut/`), sonidos de su librería (`lib/sfx` recortados en `mn/sfx`: swoosh, tecla, pop, subrayado de
>   marcador, sub-bass suave, obturador), degradado negro suave en la parte baja de los b-roll y la **zona
>   segura** (`Margen seguro.png`: x 50–1027, y 212–1547, x ≤ 920 bajo y 1117).
> - Transiciones: cortes limpios; solo dos zoom-blur muy suaves (al primer problema y al cierre).

> **Versión 2 (vigente): `edit/r3_*.py`.** Rehecha con la estructura de `Referencia_Reel_3_Slate`:
> la presentadora queda en pantalla todo el video; en cada problema entra **arriba a la derecha una tarjeta con
> la imagen del problema** (desde la derecha, con desenfoque de movimiento, y sale hacia arriba) y el texto del
> problema aparece **en el pecho, palabra por palabra**, en tipografía mixta (Poppins SemiBold pequeña +
> Playfair Display Italic grande y condensada, crema con sombra). En la respuesta entra **abajo una tarjeta con
> la solución** (desde la izquierda, con su nombre dentro: "Custom Spray Tan", "Rapid Tan", "Exfoliate 24h
> Before", "Moisturize Daily", "Barrier Cream", "Book 1-2 Days Before", "Proper Prep" → "Custom Shade",
> "Personalized Consultation"). Tarjetas con esquinas redondeadas, borde crema luminoso y sombra. Para el cierre,
> **destello de luz cálida (light leak)** a un plano más cerrado con subtítulos en la misma tipografía mixta.
> Los clips de las tarjetas se ralentizan solos si son más cortos que su tiempo en pantalla.
>
> ```bash
> python3 edit/r3_render.py out/video_noaudio.mp4
> python3 edit/r3_mix.py sfx /ruta/music.wav out/mix.wav
> ```
>
> La versión 1 (`ps_*.py`, descrita abajo) queda como referencia; la v2 reutiliza su voz y sus tiempos.

Reel vertical 1080×1920, 30 fps, ~59 s. Estilo "Problem vs. Solution" con la línea gráfica SLATE de los
reels anteriores (Oswald + EB Garamond Italic + subtítulos Poppins Bold con brillo, títulos con destello,
tarjeta final blanca). Sin emojis en pantalla.

## Las dos voces

En el material en crudo (IMG_7103/7106/7108/7110) una compañera **fuera de cámara** lee cada problema y la
presentadora responde. Se identificó quién habla en cada frase midiendo el movimiento de la boca en el video
(`tools/lipw.py`) y comparando el timbre con frases seguras de cada voz. **Se conservan las dos voces**:
cada problema suena con la voz original que pregunta y cada solución con la de la presentadora. Ambas se
igualan en nivel (±6 dB por frase) antes de mezclar.

Los cortes de voz (`edit/voice_edl.py`) se ajustaron al inicio real de cada palabra medido por energía:
las marcas de whisper llegan 0,1–0,3 s tarde y recortaban "Ex-foliate", "Moi-sturize", "Tan sticking"…

## Estructura

| | Problema (voz fuera de cámara) | Solución (presentadora) | Imagen |
| --- | --- | --- | --- |
| Hook | — | — | "SPRAY TAN PROBLEMS? / *we've got solutions!*" desde el primer cuadro sobre la nube dorada del spray |
| 1 | Pale or dull skin | A custom spray tan | antes → aplicación |
| 2 | Need color ASAP | We have a rapid formula just for that | antes → presentadora + aplicación rápida |
| 3 | Dry or patchy skin | Exfoliate 24 hours before your appointment | antes → presentadora + clienta llegando |
| 4 | Tan fading unevenly | Moisturize daily | presentadora escuchando → estante de lociones |
| 5 | Tan sticking to hands and feet | We have barrier cream in the room for that before your appointment | manos rociadas → presentadora + cabina |
| 6 | Going on vacation | Book your spray tan 1–2 days before your trip | resultado → presentadora + calendario (BOOK → TRIP, "1-2 DAYS") |
| 7 | Wedding or special event | …book 1–2 days before your wedding, follow the prep instructions… custom shade for you | resultado glam → presentadora, preparación, consulta, aplicación |
| 8 | Not sure which shade or solution is right for you? | Every client gets a personalized spray tan consultation | consulta (técnica con muestra y producto) |
| Cierre | — | Every skin tone, undertone, and glow goal is different. Your spray tan should be too. If you relate to any of this, come see us at Slate… | clientas distintas, presentadora, fachada SLATE, tarjeta "Let's find your perfect tan / SLATE TULSA" |

## Diferenciación visual

- **Problema:** tarjeta de vidrio esmerilado con etiqueta "PROBLEM" (icono "?" dibujado), texto en EB Garamond
  Italic que se escribe letra a letra, gradación algo más fría y plana.
- **Solución:** píldora cálida "SOLUTION" con estrella dibujada, título Oswald en color caramelo con destello,
  estrellitas que titilan, subtítulos palabra por palabra, gradación cálida.
- **Transiciones:** whip-pan problema→solución; zoom-blur solución→siguiente problema.
- **SFX:** pop en cada tarjeta de problema, whoosh en cada transición, "ting" corto en cada solución
  (no tapa la primera palabra), sparkle en hook y cierre, ding en la tarjeta final.

Todos los tiempos del montaje se calculan desde la voz (`voice_raw_map.json` + `words.json` alineadas con el
texto del guion), así que si se recorta la voz el montaje se reajusta solo.

## Render

```bash
export STDIR=/ruta/st PSDIR=/ruta/ps FONT_DIR=/ruta/fonts   # st/b = banco de b-roll, st/broll2 = salón, ps/raw = crudo
NOREFINE=1 python3 tools/assemble_voice.py edit /ruta/ps/talk edit/voice_raw.wav 0.05
python3 edit/ps_render.py out/video_noaudio.mp4
python3 edit/ps_mix.py /ruta/sfx /ruta/music.wav out/mix.wav
```

Música: original (ElevenLabs Music v2.5 vía Higgsfield), pop moderno y "cute", 120 BPM, ~12 LU bajo la voz.
