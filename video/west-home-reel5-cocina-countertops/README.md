# West Home Improvement · Reel 5 — "Opciones para tu cocina": granito vs cuarzo (Félix Ramírez)

Reel educativo vertical de 44,4 s (1080×1920, 30 fps) en formato entrevista POV: Samantha pregunta fuera de cámara y
Félix responde en la isla de la cocina. Está editado siguiendo `estilo.md`, que es el análisis medido del reel de
referencia.

| Tiempo | Voz | Imagen | Gráficos |
| --- | --- | --- | --- |
| 0–4,7 | Félix, ¿qué pasa si quiero remodelar mi cocina y no sé qué countertop elegir? | Félix desde el primer cuadro (abierto → punch-in) | Subtítulos palabra a palabra; COUNTERTOP como palabra héroe; icono cocina |
| 4,7–7,6 | Tenemos dos opciones, el granito o el cuarzo. | Félix → pantalla dividida granito/cuarzo | "2 opciones"; paneles que entran por lados opuestos con etiquetas |
| 7,6–9,9 | ¿Cuál es la diferencia entre los dos materiales? | Félix escuchando (punch-in) | |
| 9,9–13,7 | El granito puede ser un poco más económico, pero requiere mayor mantenimiento. | Félix → granito natural de cerca | Tarjeta COSTO ($ vs $$); icono spray |
| 13,7–18,2 | El cuarzo es un material fabricado, hay más variación en los patrones. | Cocina de cuarzo → tres franjas de patrones | Iconos fábrica y muestrario |
| 18,2–20,8 | Lo mejor de todo es que ya viene completamente sellado. | Félix (punch-in) | SELLADO héroe; icono escudo |
| 20,8–30,6 | El cuarzo resiste calor, pero no tanto como el granito, entonces tienes que ser cuidadoso… ollas calientes, no dejarlas encima de tu countertop porque se puede dañar. | Félix → pantalla dividida con barras de "resistencia al calor" → olla con vapor → ollas sobre la isla | Iconos llama/olla/advertencia; glow rojo de bordes en "se puede dañar" |
| 30,6–32,3 | ¿Qué opción me recomendarías tú? | Destello cálido (light leak) → Félix (punch-in) | |
| 32,3–39,5 | Hacemos un appointment y vamos a un distribuidor de materiales, porque no es lo mismo mirarla completo a mirar un sample pequeño. | Félix → pared de losas tipo showroom → losa completa que se encoge a una muestra | Iconos calendario/almacén |
| 39,5–44,4 | Y si quieres que mi equipo y yo te ayudemos, comenta la palabra cocina y nos pondremos en contacto contigo. | Félix | Tres iconos de equipo; CTA arriba: "comenta la palabra" + "COCINA" |

- **Selección:** del crudo (~90 s de habla) se quedaron 15 fragmentos. Los cortes caen en valles de energía (`tools/cuts.py`) y se verificaron re-transcribiendo la voz montada. `words_out.json` tiene los tiempos por palabra de la voz final (Whisper).
- **Subtítulos:** Cabinet Grotesk, de la carpeta de marca y lo más parecido a la neo-grotesca de la referencia. Blancos con halo oscuro suave y la palabra clave en naranja de marca. Cada palabra entra con fade + desenfoque en su tiempo exacto.
- **Personas:** todos los textos van detrás de Félix y de la mano de Samantha, con el recorte por cuadro U2-Net.
- **Iconos:** dibujados en código (`icons.py`), sin emojis.
- **B-roll:** fotos de Unsplash con licencia libre (créditos en `credits.json`). Las pantallas divididas, franjas, cuadrícula y la muestra que se encoge están hechas en `overlays.py`.
- **Audio:**
  - Sin cama musical, igual que la referencia.
  - SFX sutiles solo de la librería del cliente (`video/sfx-library`): tecleo muy bajo en los subtítulos, pops en los iconos, whooshes al entrar al B-roll y golpe grave en los punch-ins.
  - Mezcla final a −14,4 LUFS.
