# West Home Improvement · Reel 3 — recorrido del baño completo (Félix y Peter)

**v3 (ajustes del cliente):**
- **Inicio:** ahora abre afuera de la casa con Peter y Félix, en la toma IMG_9039: "Hey Tulsa, we have another beautiful West
  Home Improvement bathroom we just completed. Let's check it out."
  - Arriba van el título FULL BATHROOM TRANSFORMATION y la píldora TULSA, OK; los subtítulos son palabra a palabra.
  - Después, con un whip, entra Félix en el baño con el hook THEY ONLY WANTED A NEW SHOWER….
- **Clip quitado:** el del cuarto morado ("Are you ready to see something nice?" y la caminata por la puerta, IMG_9009).
  Del montaje del reveal se pasa directo a "There was a big wall here".
- **Cámara lenta real:** las tomas de 60 fps de "The shower is the masterpiece" y la ducha final van a media velocidad.
- **Recortes:** BiRefNet-portrait en todos los planos con persona, igual que el reel 2 v3.
- **Sonido:** los subtítulos entran sin sonido; los efectos quedan en títulos, gráficos y transiciones.
- **Duración:** 45,7 s. La tabla de abajo es de la v1.

Reel vertical de 43,5 s (1080×1920, 30 fps). Sin guion: la historia se armó con los mejores fragmentos de las
explicaciones (transcritas palabra por palabra y cortadas en los silencios; `chunks.json` tiene cada frase con su tiempo).

| Tiempo | Voz | Imagen | Texto |
| --- | --- | --- | --- |
| 0–4,7 | Initially the customers had the idea only remodel the shower area, but… | Félix a cámara desde el primer cuadro → ducha terminada en "the shower area" → Félix | Hook: THEY ONLY WANTED A NEW SHOWER… (en los primeros 2,3 s el hook reemplaza a los subtítulos: Félix camina hacia la cámara y no hay espacio libre) |
| 4,7–9,8 | I mean this space needs a lot of work, so I gave them some suggestions and we ended up doing | Félix (cortes con punch-in) → baño | |
| 9,8–11,5 | the whole thing | Montaje de 3 planos al ritmo (drop de la música) | THE WHOLE THING |
| 11,5–14,3 | Are you ready to see something nice? | Félix y Peter → entran por la puerta (speed ramp) | |
| 14,3–18,5 | There was a big wall here, so it was really narrow to get into the shower | Félix señalando | BIG WALL |
| 18,5–22,1 | We demoed the whole thing out to make a really open space | Baño abierto | BIG WALL tachado → OPEN SPACE |
| 22,1–28,5 | With a new custom vanity countertop to match the tile. All the fixtures are completely new | Vanity, puertas, mesón, grifería negra con agua, regadera | |
| 28,5–30,2 | The shower is the masterpiece | Ducha completa | THE SHOWER IS THE MASTERPIECE |
| 30,2–37,7 | Classic subway tile, but make it look great like a luxury bathroom, custom niche, a nice glass custom door | Azulejo, Félix en la ducha, nicho, puerta de vidrio | |
| 37,7–42,0 | Alright Felix, we did it again — Yes sir. / You already know, call West Home Improvement | Afuera: choque de manos; los dos en el porche | |
| 42,0–43,5 | | Ducha terminada | Logo (espacio para el CTA escrito) |

- Subtítulos dinámicos con palabras clave en naranja; todos los textos detrás de las personas (recorte por cuadro) y los
  subtítulos se acomodan solos para no chocar con las personas ni con los títulos (`layout` en `overlays.py`).
- SFX solo de la librería del cliente (`video/sfx-library`): teclado en cada texto, golpes y pops en palabras clave,
  whooshes en transiciones. Música original de 104 BPM (ElevenLabs Music v2.5 vía Higgsfield), extendida al compás.
- No se usaron fotos del "antes": las dos de la carpeta (IMG_8311/8312) son de otro baño (ventana y azulejo distintos).
