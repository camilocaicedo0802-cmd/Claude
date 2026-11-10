# SLATE · Spray Tan Problems? We've Got Solutions! (reel 9:16)

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
