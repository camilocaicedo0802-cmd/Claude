# estilo.md — Guía de estilo extraída de `referencia.mp4`

Referencia: 31,0 s · 576x1024 · 30 fps (se escala ×1,875 a 1080x1920).
Todas las medidas están convertidas a **1080x1920** salvo que se indique otra cosa.
Lo que no se puede medir directamente está marcado con **[SUPOSICIÓN]**.

Material de análisis en `analisis/`: `frames_2fps/` (62 fotogramas), `frames_cortes/` (14 cambios de plano),
`sheets/` (hojas de contacto), `trans/` (transiciones a 30 fps), `crops/` (tipografías), `stems/` (separación Demucs),
`audio_extraido/` (música limpia y SFX), `whisper_ref/` (transcripción con tiempos por palabra).

---

## 1. Ritmo de cortes

| Tramo | Duración media de plano | Detalle |
|---|---|---|
| Intro 0,00–1,60 s | **0,25–0,27 s (8 fotogramas)** | 6 planos seguidos: 0,03 · 0,30 · 0,53 · 0,80 · 1,03 · 1,27 s |
| Cuerpo 1,60–26,20 s | **1,5–2,7 s por escena** | Cortes en 1,60 · 3,43 · 4,87 · 6,43 · 7,57 · 9,27 · 11,57 · 13,03 · 15,77 · 18,27 · 19,00 · 20,20 · 24,10 · 26,20 |
| Cierre 26,20–31,00 s | 4,8 s (una escena larga que evoluciona) | Último corte a **negro puro en 30,93 s** (2 fotogramas negros) |

- Total: ~22 planos en 31 s → **1 plano cada 1,4 s** de media.
- **Regla:** cada frase de la locución = 1 escena. Si la frase dura más de 2,5 s, la escena cambia de encuadre por dentro (*whip* o nuevo elemento).
- Nunca hay más de **~2,7 s** sin un cambio visual fuerte (corte, *whip*, objeto nuevo o palabra destacada).
- El vídeo termina **0 s después** de la última palabra (sin cola ni CTA).

## 2. Dos "modos" visuales que se alternan

| | Modo OSCURO (cinemático) | Modo BLANCO (estudio / motion graphics) |
|---|---|---|
| Uso | Contexto / problema / drama (0–1,6 s, 3,4–7,6 s) | Explicación, datos, giro, resultado (resto) |
| Fondo | Fotos fotorrealistas generadas con IA [SUPOSICIÓN], gradación cálida desaturada: media RGB ≈ `#3E3932`, luma 41–88/255, viñeta fuerte, negros levantados | Blanco `#FFFFFF`–`#FCFCFC` liso |
| Texto | Blanco `#FFFFFF` (≈`#E7E6E9` tras el *glow*), resplandor blanco-azulado | Negro `#000000`; palabra aún no dicha en gris `#858585` |
| Movimiento | Empuje de cámara lento (escala 1,00→1,05 por plano) [SUPOSICIÓN en el %] | Objetos 3D flotando/girando, retículas, puntos, tarjetas UI |

Proporción en la referencia: **~25 % oscuro / ~75 % blanco**. Se alternan para crear contraste (oscuro→blanco = "golpe").

## 3. Subtítulos (tipografía cinética)

No son subtítulos clásicos: son **bloques tipográficos compuestos** ("lockups") que se construyen palabra a palabra sincronizados con la voz.

### 3.1 Fuentes
| Rol | Fuente en la referencia | Réplica usada en el proyecto |
|---|---|---|
| Palabras normales | Helvetica Neue Bold [SUPOSICIÓN] | **FreeSans Bold** (clon de Helvetica), interletrado **−0,08 em**, interlineado **0,80** |
| Palabra destacada (modo blanco y oscuro) | Serif tipo Times Bold Italic **condensada al ~70 %** y engrosada [SUPOSICIÓN] | **Tinos Bold Italic**, `scaleX 0,70`, interletrado **−0,03 em**, trazo extra **0,012 em**, MAYÚSCULAS |
| Palabra destacada secundaria (minúsculas, p. ej. "Demaciados", "decisión", "locura") | La misma serif itálica, sin condensar | Tinos Bold Italic sin `scaleX` |
| Cifras/hero en modo oscuro ("1997") | Grotesca Black | FreeSans Bold + trazo 0,035 em (efecto Black) |
| Rótulos manuscritos (polaroids) | Rotulador mayúsculas | **Permanent Marker** |
| Interfaz (diálogo UI) | Helvetica Bold | FreeSans Bold |

### 3.2 Tamaños (medidos)
| Elemento | Altura medida | Tamaño de fuente equivalente |
|---|---|---|
| Línea pequeña sans ("Apple", "esa misma", "al borde") | 43–47 px (con ascendentes/descendentes) | **46–50 px** |
| Línea pequeña sans grande ("Empezo a", "Steave Jobs") | 64–71 px | **66–72 px** |
| Palabra grande sans ("estaba") | 116 px (asc. + x) · ancho 527 px | **~160 px** |
| Destacada serif ("EMPRESA", "ENFOCARSE") | altura de mayúscula 111–129 px · ancho 628–669 px (**58–62 % del ancho**) | **170–195 px** |
| Hero oscuro "1997" | 216 px de alto · 574 px de ancho (53 %) | **~300 px** |
| Palabra suelta sobre foto B&N ("decisión") | 99 px | **~110 px** |
| Pila 1 palabra/línea ("y / nadie / sabia / que / hacer") | 5 líneas en 351 px | **~78 px**, interlineado 0,90 |

Regla práctica: **la palabra destacada mide entre 3,5× y 4× la línea pequeña** y ocupa **55–62 %** del ancho.

### 3.3 Composición del bloque
- 3 líneas escalonadas: **línea 1 pequeña alineada a la izquierda del destacado (+15 px)** → **línea 2 destacada** → **línea 3 pequeña alineada a la derecha del destacado**.
- Interlineado negativo: las líneas pequeñas **se solapan 5–10 px** con la destacada.
- Posición vertical:
  - Modo blanco: **bloque en el tercio superior, y = 320–620 px** (17–32 % de la altura); el objeto/gráfico va debajo, centrado en **y ≈ 960 px (50 %)**.
  - Modo oscuro: **bloque centrado, y = 830–1100 px** (43–57 %).
  - Foto B&N: palabra suelta sobre el pecho del sujeto, **y ≈ 1075 px (56 %)**, con mancha oscura radial detrás (Ø ~500 px, negro 60 %) para legibilidad.
- Centro horizontal: el bloque centrado en x = 540 px (margen mínimo **≥ 140 px** a cada lado).

### 3.4 Palabras por bloque
- Bloque normal: **3–5 palabras** (máx. 6).
- Momentos de tensión: **1–2 palabras por pantalla** (escena B&N: "y tomó" / "una" / "decisión" / "parecía" / "una locura").
- **El texto en pantalla NO es la transcripción literal**: se eliminan muletillas y relleno ("de la quiebra", "intentar", "a veces crecer" no aparecen). Frases enteras se sustituyen por un gráfico (p. ej. "Eliminar casi todo" → diálogo UI "Eliminar 'Productos'").
- **1 palabra destacada por bloque**, siempre el sustantivo/verbo con más carga (MILLONES, PRODUCTOS, VENDERLE, ENFOCARSE, EMPRESA, ENTENDIERON, HACER MÁS, QUÉ ELIMINAR).
- La referencia omite tildes ("sabia", "despues", "MAS"); **en este proyecto se escriben con tildes correctas** (decisión propia, no es parte del estilo).

### 3.5 Animación de entrada (palabra a palabra)
- Cada palabra **empieza a entrar 4–6 fotogramas (0,13–0,2 s) antes** de que se pronuncie.
- Estado inicial: opacidad 0, desenfoque **8–10 px**, escala 0,92 → al terminar: opacidad 1, desenfoque 0, escala 1. Duración **6–8 fotogramas** con *ease-out* fuerte (`bezier(0.16, 1, 0.3, 1)`).
- Mientras entra, la palabra se ve **gris `#858585`/`#BDBDBD`** (opacidad parcial) y se oscurece a negro en **~0,4 s** (12 fotogramas). Ese "gris → negro" es la firma visual del karaoke.
- **Palabra destacada:** revelado **letra a letra de izquierda a derecha** (cada letra: gris + desenfoque → negro nítido), desfase **1–1,5 fotogramas por letra**, total **10–14 fotogramas**. En modo oscuro entra además con desenfoque de movimiento horizontal (~20 px) y parpadeo de *glow* 2–3 fotogramas.
- Pila vertical ("y / nadie / sabia…"): cada línea aparece al decirse, sin desplazamiento.
- Salida: el bloque **no sale solo**; se va con la transición de escena (zoom + desenfoque).

### 3.6 Texturas del texto
- Modo blanco: texto plano, sin sombra.
- Modo oscuro: **glow blanco-azulado** (`text-shadow` 0 0 18 px `rgba(190,215,255,0.85)` + 0 0 40 px `rgba(160,190,255,0.45)`) [SUPOSICIÓN en los valores exactos], relleno con textura (ruido/escarcha que cambia cada fotograma) y aberración cromática azul en el borde derecho.
- Palabra sobre foto B&N: blanco con halo blanco 0 0 24 px y mancha oscura radial detrás.

## 4. Textos en pantalla que no son subtítulos
- **Etiqueta de personaje:** nombre en sans Bold 72 px ("Steave Jobs") + subtítulo sans Regular 30 px **curvado en arco** ("Fundador de Apple") + logo pequeño + **flecha a mano** (trazo negro 3 px, curva en "S") apuntando a la cabeza.
- **Rótulos manuscritos** en el borde inferior de cada polaroid: "POWERBOOK (1997)", 30–34 px, rotados con la foto (−8° a +12°).
- **Interfaz falsa:** diálogo tipo macOS: fondo `#262626`, radio **~55 px**, 765x439 px; título "Eliminar “Productos”" blanco 54 px; cuerpo blanco 26 px; botones "Cancelar" texto `#3C9398` y "Eliminar" texto `#B5121B` sobre fondo `#3A0A0F`; cursor de flecha blanco con borde negro.
- **Tarjetas de e-commerce:** fondo `#C0C0C0`, foto del producto, nombre, "★ 3.0 (1k Review)", precio, botones "Add to chart" (blanco) y "Buy now" (negro). Al "eliminarse" se tiñen de rojo (`rgb(172,98,108)` → `#E00000` al 70 %) y tiemblan.
- **Pregunta suelta centrada:** "¿El Resultado?" sans Bold 64 px gris oscuro `#333333`, sola en blanco, 0,73 s.

## 5. B-roll y objetos

### 5.1 Modo oscuro
- Fotografías fotorrealistas (IA [SUPOSICIÓN]) de época, contexto del relato: calles de los 90, oficina con gráfica de pérdidas "$708M", periódico "Apple Posts $708 Million Loss", almacén de cajas, ejecutivo derrotado.
- Encuadre vertical a sangre, **empuje lento de 1,00 → 1,05** durante el plano [SUPOSICIÓN en el %], viñeta y grano.

### 5.2 Modo blanco (motion graphics)
- **Objetos 3D recortados en escala de grises** (botón con logo, globo terráqueo, reloj de arena, manzana, cerebro, círculos negros). Solo 1–2 acentos de color por objeto (manzana roja, latón del reloj de arena).
- **Sombra larga y suave abajo a la derecha:** desplazamiento (**+40 px, +60 px**), desenfoque **50–60 px**, negro al **35–45 %** (luz desde arriba a la izquierda).
- **Copias desenfocadas en primer plano** del mismo objeto en las esquinas (desenfoque 12–25 px, recortadas por el borde) → profundidad de campo.
- **Formas negras desenfocadas** (hojas/aspas) en esquina superior derecha e inferior izquierda, desenfoque ~20 px, negro 85 %, rotación lenta.
- **Retícula de boceto:** líneas grises `#C8C8C8` de 1–2 px, rejilla 5x5 de ~700x700 px con cruces "+" en las intersecciones y bordes que se desvanecen (máscara radial).
- **Arcos negros gruesos** (8–12 px) que cruzan el encuadre, parcialmente desenfocados.
- **Bokeh gris** `#DEDEDE`: círculos de 20–80 px con desenfoque, flotando.
- **Anillo discontinuo** alrededor de objetos circulares, girando **~30°/s**.
- **Polaroids** con marco crema envejecido, cinta adhesiva semitransparente en las esquinas, apiladas con rotaciones distintas, cayendo una a una cada ~0,5 s.
- **Personaje recortado** (sin fondo) con sombra grande y retícula detrás.
- **Foto de archivo en B&N con trama de semitono** (puntos visibles, contraste alto).
- **Animación semántica**: los objetos *hacen* lo que dice la frase (el logo se agrieta en "al borde"; las tarjetas se ponen rojas en "eliminar"; los puntos se apagan y desaparecen en "qué eliminar").

### 5.3 Entrada de objetos
- Escala **0,3 → 1,0** con rebote (*spring*, sobreimpulso ~6 %), rotación inicial de −20° a 0°, desenfoque de movimiento en los primeros 3–4 fotogramas. Duración **8–12 fotogramas**.
- Después, movimiento continuo: flotación ±10 px, rotación lenta 2–5°/s.
- Elementos múltiples (puntos, tarjetas, polaroids) con **desfase de 2–4 fotogramas** entre sí.

## 6. Transiciones

| Tipo | Cuándo | Valores |
|---|---|---|
| **Zoom-blur de salida + corte seco** (principal, ~10 veces) | Entre escenas | La escena saliente escala **1,00 → 1,12–1,20** en **4–5 fotogramas** con desenfoque de movimiento creciente (0 → 25 px) y a veces desplazamiento. Corte seco. |
| **Entrada desenfocada** | Inicio de cada escena | La escena entrante empieza con desenfoque **15–20 px** y escala 1,08 → nitidez y 1,00 en **4–6 fotogramas**; o el objeto principal entra desde escala 0,3 con desenfoque de movimiento. |
| **Destello blanco** | Fotograma 0 del vídeo | Blanco al 100 % → 0 % en **5 fotogramas** mientras "1997" entra deslizando desde la izquierda con desenfoque. |
| **Whip pan dentro de la escena** | Frases largas (22,17 s) | La cámara se desplaza rápido (~600 px) con desenfoque direccional 6 fotogramas y se reencuadra. |
| **Cortes secos rítmicos** | Intro | Cada 8 fotogramas, sin efecto, con el texto fijo encima. |
| **Corte a negro** | Final | Negro puro 2 fotogramas. |

## 7. Zooms y cámara
- **Empuje continuo** en todas las escenas: escala 1,00 → 1,04–1,08 a lo largo de la escena (`ease-in-out`) [SUPOSICIÓN en el %].
- **Punch-in** de 1,00 → 1,15 en 4–5 fotogramas justo antes de cada corte (es la mitad de salida de la transición).
- Personaje recortado: entra con zoom 1,25 → 1,00 desenfocado y sigue empujando hasta ~1,10.

## 8. Color
| Uso | Valor |
|---|---|
| Fondo blanco | `#FFFFFF` (centro) / `#FCFCFC` |
| Texto principal (blanco) | `#000000` |
| Palabra entrando / aún no activa | `#858585` → `#BDBDBD` (≈ negro al 48 % → 25 %) |
| Objetos 3D | Escala de grises: `#2E2E2E` (botón), `#5A5A5A` (manzana), `#DEDEDE` (bokeh) |
| Acentos | Rojo manzana/alerta `#C8102E`, rojo botón `#B5121B`, verde azulado `#3C9398`, latón `#B07A3A` [SUPOSICIÓN en el latón] |
| Interfaz | Diálogo `#262626`, tarjeta `#C0C0C0` |
| Modo oscuro | Media `#3E3932`; sombras `#211D19`; altas luces cálidas; texto `#FFFFFF` con glow `#BED7FF` |
| Foto de archivo | B&N, contraste alto, semitono |

Paleta global: **blanco y negro dominantes + 1 acento rojo**. El color solo aparece en las fotos oscuras (cálidas) y en acentos puntuales.

## 9. Sonido

### 9.1 Música
- Canción: **"Timeless" — The Weeknd & Playboi Carti** (identificada con Shazam en 2 fragmentos distintos), versión instrumental de fondo.
- Tempo **120 BPM exactos** (pulso 0,500 s, compás 2,000 s, medido por autocorrelación).
- Estructura en la referencia: **intro suave 0–7,15 s** (sintetizador agudo ~2,6 kHz, sin bajo) → **entra el bajo y la batería completa en 7,15 s**, justo en el giro del relato ("Entonces volvió Steve Jobs").
- Nivel: voz −21,5 LUFS · música −22,9 LUFS → **música solo 1,4 LU por debajo de la voz** en el cuerpo; en la intro, **4–6 dB por debajo**. **Sin ducking** (mezcla fuerte, estilo TikTok). Mezcla final −18 LUFS integrados.
- Archivo limpio (sin voz ni SFX): `analisis/audio_extraido/musica_timeless_limpia.wav` (los SFX se reemplazaron por el mismo fragmento ±1–2 compases).

### 9.2 Efectos de sonido (catálogo extraído en `analisis/audio_extraido/sfx/`)
| SFX | Momento en la referencia | Qué acompaña | Cómo se usa |
|---|---|---|---|
| `flash_click_1/2/3` (clic seco de obturador/flash, 0,2 s, brillo 2–4 kHz) | 0,07 · 0,26 · 0,53 · 0,84 · 1,14 s | Cada corte rápido de la intro | 1 por corte rápido / aparición de foto |
| `boom_ring` / `boom_ring_2` (golpe grave 60–500 Hz + campanilla aguda ~5,5 kHz, 1,2 s) | 1,68 s y 20,20 s | Paso oscuro→blanco con objeto protagonista (logo); revelado clave | En los 2–3 revelados más importantes |
| `glass_crack` (estallido de banda ancha + chisporroteo agudo, 0,45 s) | 2,85 s | El logo se agrieta ("al borde") | Golpe / rotura / impacto negativo |
| `riser` (subida de ruido con armónicos 8–10 kHz, 1,5 s) | 6,30–7,80 s | Tensión antes del giro y del drop musical | Antes del giro principal |
| `ui_beep` (pitido de interfaz, dos tonos ~1,3 y ~2,6 kHz, 1,3 s) | 11,55 s | Aparece el diálogo "Eliminar" | Elementos de interfaz / notificaciones |
| `photo_paper` (golpe medio de papel/foto, 0,7 s) | 17,30 s | Caen las polaroids | Fotos/tarjetas que caen |
| `pops` (serie de "pops" tonales, 1,7 s) | 25,35–27,05 s | Aparecen y se apagan los puntos | Elementos múltiples que aparecen/desaparecen |
- [SUPOSICIÓN] Las descripciones de cada SFX salen del espectrograma, no de una escucha.
- Las ráfagas que caen cada ~2,0 s (8,65 · 10,65 · 12,67… s) son la **palmada de la canción**, no SFX.
- Densidad: **~1 SFX cada 2–3 s**, siempre pegado a un evento visual (corte rápido, revelado, objeto que cambia).
- Nivel de los SFX: picos de **−20 a −24 dBFS** en la mezcla (≈ al nivel de la voz en los golpes, 6–10 dB por debajo en clics/pops).

### 9.3 Voz
- Locución masculina en español, ~3,1 palabras/s, pausas de 0,1–0,4 s entre frases. Nivel −21,5 LUFS (pico −1,9 dBFS).

## 10. Plantilla de escena (resumen operativo)
1. Frase de la locución → 1 escena de 1,5–2,7 s.
2. Elegir modo: OSCURO (contexto/problema) o BLANCO (explicación/giro/resultado).
3. Objeto protagonista centrado (y ≈ 50 %), con sombra abajo a la derecha, copia desenfocada en una esquina y decorado (retícula/arcos/bokeh/formas desenfocadas).
4. Bloque tipográfico de 3 líneas en el tercio superior: pequeña–DESTACADA–pequeña, palabra a palabra, gris → negro.
5. El objeto reacciona a la frase (animación semántica).
6. SFX pegado al evento principal.
7. Salida con punch-in + desenfoque de 4–5 fotogramas y corte seco.

---

## 11. Correcciones aprobadas por el usuario
_(Se irán añadiendo aquí las correcciones que el usuario apruebe para que se mantengan en futuras ediciones.)_
