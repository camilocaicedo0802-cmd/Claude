# estilo.md — guía de estilo extraída del vídeo de referencia

Fuente: `material/referencia/referencia.mp4` (720×1280, 30 fps, 23,55 s). El vídeo es una comparación
«Raw Video / Final Video»; todo lo que sigue describe **solo el panel «Final Video»** (recorte
402×712 px dentro del archivo, proporción 9:16).

Cómo se midió: 47 fotogramas a 2 fps + 36 fotogramas alrededor de cada cambio de plano, los 703
fotogramas del panel final revisados en tiras, transcripción con Whisper (tiempos por palabra),
análisis de píxeles (color, cajas de texto), estimación de zoom por emparejamiento de puntos y
análisis de audio (espectrograma, silencios, comparación con la librería de SFX).

Todas las medidas en píxeles están **convertidas a 1080×1920**. Los tiempos van en milisegundos y,
entre paréntesis, en fotogramas a 60 fps. Lo que no pude medir y deduje va marcado con **[SUPOSICIÓN]**.

---

## 1. Ritmo

| Dato | Valor |
| --- | --- |
| Duración | 23,4 s |
| Velocidad de locución | 71 palabras en 23,4 s = **3,03 palabras/s** (182 ppm) |
| Pausas entre frases | 100–280 ms (respiraciones cortadas); 480 ms solo cuando hay transición encima |
| Material base | **1 sola toma** de busto parlante; no hay cortes de montaje entre tomas distintas |
| Evento visual nuevo | cada **1,0–1,8 s** (bloque de texto, gráfico o transición); nunca pasan más de 2 s sin cambio |
| Transiciones con efecto | 4 en 23,4 s (≈ 1 cada 5,8 s): 3,13 s · 4,40 s · 8,10 s · 20,43 s |
| Cortes secos | 2: entrada al b-roll (6,20 s) y salida (8,27 s) |
| Bloques de texto | 11 en 23,4 s; cada uno dura **1,1–1,9 s** |

Mapa del vídeo (segundos):

| t | Qué pasa |
| --- | --- |
| 0,00–0,90 | Abre en primer plano (zoom 1,42) y se aleja a 1,0. Texto «If the **Prospects** have to meet you» |
| 1,64–2,82 | «to **Understand** your value» + icono de avión de papel en neón |
| 3,13–3,27 | Transición de desenfoque |
| 3,10–4,24 | «your **Content** is failing» + tachado rojo a mano |
| 4,40–4,67 | Transición de barras verticales con destello blanco |
| 4,72–6,02 | Texto **detrás** de la persona, arriba: «You know **content** matters» |
| 6,20–8,27 | B-roll (misma persona, rodeada de cámaras) con aro de enfoque, texto arriba y globo tecleado |
| 8,10–8,27 | Glitch + corte seco de vuelta |
| 8,38–10,18 | «even if **You record** you are unsure» + visor REC (9,0–14,6 s) |
| 10,2–14,6 | Dos tarjetas rojas de alerta con texto tecleado |
| 14,70–16,32 | «we take it off **Your plate**» |
| 16,93–20,4 | Fichas con icono 3D: PLAN · SHOOT · SCRIPT → EDIT · POST (una por palabra dicha) |
| 20,43–20,73 | Transición de barras verticales |
| 20,8–22,4 | Píldora verde con avatar y «value…» tecleado |
| 22,44–23,22 | «working **together.**» |

---

## 2. Subtítulos

### 2.1 Tipografía

- **Familia:** grotesca neo-suiza de tracking muy cerrado (las letras casi se tocan).
  **[SUPOSICIÓN]** Helvetica Now Display / Neue Haas Grotesk. Sustituto libre usado en el proyecto:
  **Inter Tight** (Google Fonts).
- **Palabra clave:** peso 700, `letter-spacing: -0.045em`, `line-height: 0.86`.
- **Palabras secundarias:** peso 500–600, `letter-spacing: -0.035em`.
- Sin mayúsculas sostenidas: la palabra clave va con **Inicial Mayúscula**; las secundarias en minúscula.

### 2.2 Tamaños (a 1080 px de ancho)

| Nivel | Tamaño | Medido en |
| --- | --- | --- |
| Palabra clave | **150–185 px** (se ajusta para ocupar 650–910 px de ancho, 60–85 % del cuadro) | «Prospects» 741×144 px · «Content» 688×140 · «Your plate» 819×157 |
| Secundarias pequeñas | **46–50 px** (≈ 0,30 × palabra clave) | «If the», «have to», «meet you» (altura de caja 28–30 px) |
| Secundarias medianas | **85–95 px** (≈ 0,55 × palabra clave) | «your value», «is failing», «you out» |
| Palabra clave detrás del sujeto | **≈ 265 px** (1,65 × la normal) | «content» 950×191 px |

### 2.3 Color y textura

| Elemento | Valor |
| --- | --- |
| Lima de la palabra clave | **#DFFF4F** (mediana medida #E0FF57; núcleo #E9FF6D) |
| Resplandor de la palabra clave | mismo lima, desenfoque ≈ 28 px, opacidad ≈ 55 % + sombra negra suave 0/4/24 px al 60 % |
| Secundarias | **#FFFFFF**, con sombra negra suave (sin trazo, sin caja de fondo) |
| Secundaria «apagada» (última línea) | gris **#C4C3B8** al ≈ 75 % |
| Lima sobre plano oscuro del b-roll | el mismo lima al ≈ 70 % de opacidad (se ve oliva) |
| Rojo del tachado y del punto REC | **#C6001B** (tachado) · **#D4002A** (punto) |

Sin contorno, sin caja, sin fondo. La legibilidad la dan el resplandor, la sombra y que el plano es oscuro.

### 2.4 Posición

- **Bloque centrado en horizontal.** Centro vertical de la palabra clave en **y ≈ 1045–1090 px (55–57 %)**,
  sobre el pecho, nunca sobre la cara.
- Composición en 3 filas pegadas (interlineado negativo):
  1. fila pequeña arriba: primeras palabras a la **izquierda** y, si hay más, otras a la **derecha**;
  2. palabra clave;
  3. fila pequeña o mediana abajo, alineada al **borde derecho** de la palabra clave.
- Variante «arriba»: cuando el plano tiene la cara en el centro (b-roll) o el texto va detrás del
  sujeto, el bloque sube a **y ≈ 150–400 px (8–21 %)**.
- Margen lateral mínimo: 60 px.

### 2.5 Palabras por bloque y qué se destaca

- **4–7 palabras por bloque** (media 5,3). Una frase = un bloque.
- **1 palabra clave por bloque** (a veces 2 palabras juntas: «You record», «Your plate»): el sustantivo
  o verbo que carga el sentido.
- Se **omiten muletillas y conectores** («but», «And», «That's why», «everything for you»): el
  subtítulo resume, no transcribe literal.
- Las enumeraciones no van como subtítulo: cada elemento se convierte en un gráfico (ficha con icono).

### 2.6 Animación (sincronía palabra a palabra)

| Evento | Valor |
| --- | --- |
| Entrada de palabra pequeña | aparece en el instante en que se pronuncia (±33 ms); fundido 0→100 % + desenfoque 6→0 px en **100 ms (6 f)**, sin desplazamiento |
| Entrada de palabra clave | **130 ms (8 f)**: escala 1,08→1,00, opacidad 50→100 %, desenfoque 8→0 px; el resplandor termina de encenderse 100 ms después |
| Entrada de palabra mediana | barrido de izquierda a derecha con degradado de opacidad, **130 ms (8 f)** por palabra |
| Permanencia | las palabras ya dichas **se quedan** hasta que termina el bloque |
| Salida del bloque | **corte seco** (0 f) al empezar el siguiente, o tapada por la transición |
| Adelanto de gráficos | fichas/tarjetas entran 0–100 ms **antes** de la palabra que ilustran |

---

## 3. Textos en pantalla y motion graphics (además de los subtítulos)

Todos comparten lenguaje: **vidrio oscuro** (degradado radial + borde de 1 px + esquinas redondeadas)
en **rojo vino** para problemas/dolor y **verde** para la solución/CTA.

### 3.1 Tarjeta de alerta (problema)
- Rectángulo 675×127 px, radio 26 px, centrado; tarjeta 1 en y ≈ 1089 px, tarjeta 2 en y ≈ 1284 px.
- Fondo: degradado radial rojo vino (#8A0015 en el centro inferior → #0A0204 en los bordes),
  borde 1 px blanco al 18 %.
- Icono 3D a la izquierda (≈ 52 px): triángulo de advertencia rojo; billete con alas.
- Texto: sans geométrica ancha, **peso 300**, 44 px, blanco al 92 %. **[SUPOSICIÓN]** Clash Display Light;
  sustituto libre: **Sora 300**.
- Animación: la tarjeta entra con fundido + subida de 8 px en **133 ms (8 f)**; el texto se **teclea
  palabra a palabra**: cada palabra nace 20 px por encima y al 30 % y cae a su sitio en 100 ms (6 f).
- Las tarjetas se apilan (la 2.ª entra debajo sin quitar la 1.ª) y salen juntas por corte seco.

### 3.2 Fichas con icono 3D (enumeración)
- Fichas cuadradas ≈ 317×337 px, radio 28 px, fila en y ≈ 1284 px (67 %), separación 12 px, margen 24 px.
- Fondo rojo vino translúcido (se ve el vídeo detrás), borde 1 px claro.
- Icono 3D realista ≈ 55 % del ancho; debajo, etiqueta en MAYÚSCULAS peso 300, 40 px, blanco al 85 %.
- Animación: aparece **sobreexpuesta** (brillo ≈ 2,5× y escala 1,15) y se asienta a escala 1,0 en
  **100 ms (6 f)**. Una ficha por palabra dicha. Máximo 3 por fila; al llegar la 4.ª se limpia la fila.

### 3.3 Píldora verde (solución / CTA)
- Círculo con la cara del orador (Ø ≈ 100 px) + píldora 673×122 px, radio 30 px, y ≈ 1154 px (60 %).
- Fondo: degradado radial verde (#5F8F1E → negro), borde 1 px.
- Texto: **serif itálica** de alto contraste, 72 px, blanco con resplandor.
  **[SUPOSICIÓN]** PP Editorial New Italic; sustituto libre: **Instrument Serif Italic**.
- Se **teclea letra a letra**: 1 letra cada **67 ms (4 f)** ≈ 15 caracteres/s.

### 3.4 Visor REC
- Cuatro esquinas en L, trazo blanco 3 px, brazos ≈ 89×81 px, a 75 px del borde lateral y en
  y ≈ 127 px y y ≈ 1788 px. Arriba a la izquierda: punto rojo Ø 14 px + «REC» bold 30 px blanco.
  Cruz «+» fina abajo a la derecha.
- Se mantiene 5,6 s (toda la sección «grabarte»): marca visualmente un capítulo.

### 3.5 Otros recursos
- **Tachado a mano** sobre la palabra clave: trazo rojo #C6001B, grosor ≈ 15 px, ligeramente inclinado,
  se dibuja de izquierda a derecha en **400 ms (24 f)**.
- **Icono de trazo neón** (avión de papel): mismo lima con resplandor, entra volando en curva desde
  abajo, girando, en **330 ms (20 f)** y se posa a la izquierda de la última línea.
- **Texto detrás del sujeto**: la palabra clave gigante queda tapada parcialmente por la cabeza.
- **Aro de enfoque**: círculo crema (#F4E6C8) de 4 px con resplandor, Ø final ≈ 640 px, centrado en la
  cara; entra grande (≈ 1,5×) y se cierra acompañando el zoom.
- **Globo tecleado**: píldora rosa-rojo translúcida ≈ 250×65 px junto a la cabeza, texto 30 px que se
  teclea palabra a palabra («Please turn it off…»).
- **Punto rojo** de grabación pegado a la esquina superior derecha de «You record».

Densidad: **nunca hay más de 2 recursos gráficos a la vez** además del subtítulo, y cuando entra una
tarjeta o ficha el subtítulo grande desaparece (no compiten).

---

## 4. B-roll

- **1 inserto en 23,4 s** (6,20–8,27 s = 2,07 s, 9 % de la duración).
- No es stock: es la **misma persona escenificando el problema** (agobiada, rodeada de cámaras).
- Entra por corte seco con zoom de 1,87 → 1,0 en 1,2 s; sale con glitch.
- Mientras dura, el texto sube al tercio superior y se añade el aro de enfoque.
- Regla: el b-roll ilustra **literalmente** lo que se está diciendo en ese momento y dura una frase.

---

## 5. Transiciones

| # | Tipo | Tiempo | Valores |
| --- | --- | --- | --- |
| 1 | **Desenfoque** | 3,10–3,27 s | 167 ms (10 f). Desenfoque gaussiano 0→≈20 px→0 con zoom 1,0→1,1. El texto nuevo aparece ya dentro del desenfoque |
| 2 | **Barras verticales + destello** | 4,40–4,67 s | 280 ms (17 f). ≈ 50 barras blancas verticales (barra ≈ 11 px, hueco ≈ 10 px) que suben de 0 a 100 % en 133 ms hasta casi blanco total y bajan en 150 ms sobre el plano nuevo, que llega desenfocado |
| 3 | **Corte seco con zoom** | 6,20 s | 0 f; el plano nuevo entra a 1,87× y se aleja |
| 4 | **Glitch** | 8,10–8,27 s | 167 ms (10 f). Separación RGB y ondulación ±15 px sobre el texto, brillo −40 %, y corte seco. El primer texto del bloque siguiente se adelanta 100 ms |
| 5 | **Barras verticales + destello** | 20,43–20,73 s | 300 ms (18 f), igual que la 2 |

Regla: las transiciones con efecto marcan **cambio de idea** (problema → agitación → solución → CTA),
no cada frase.

---

## 6. Zooms y movimiento de cámara

| Momento | Valor |
| --- | --- |
| Apertura | **1,42 → 1,00 en 900 ms**, desaceleración exponencial (1,42 · 1,33 · 1,16 · 1,06 · 1,02 · 1,00 cada 200 ms) |
| Énfasis en palabra clave | salto **1,00 → 1,16 en 250 ms** al decir «Understand», luego deriva hasta 1,24 en 1 s |
| Empuje lento | **1,00 → 1,20 en 1,5 s** (≈ +13 %/s) durante el texto detrás del sujeto |
| Entrada de b-roll | **1,87 → 1,00 en 1,2 s** |
| Resto | 1,00 ± 0,05; deriva ≤ 3 %/s. Nunca hay un plano completamente quieto más de 2 s |

El punto de anclaje del zoom es la cara (los ojos se mantienen en y ≈ 22–30 %).

---

## 7. Color

- Imagen **oscura y contrastada**: mediana de luminancia 5 %, percentil 95 al 50 %; el tercio
  inferior es prácticamente negro (2 %).
- Diferencia medida entre el panel «Raw» y el «Final»: altas luces +20 % (p95 0,42 → 0,50),
  medios del sujeto +22 %, saturación +5 %, negros iguales. Es decir: **contraste suave +10–15 %,
  sujeto un poco más luminoso, sin viraje de color fuerte**.
- Viñeta natural del propio plano; no se aprecia viñeta añadida. **[SUPOSICIÓN]**
- Acentos de color solo en gráficos: lima #DFFF4F, rojo vino #8A0015 / #C6001B, verde #5F8F1E, crema #F4E6C8.

---

## 8. Sonido

### 8.1 Música
- El archivo **no tiene música**: en las pausas el nivel cae a −70 dBFS (silencio digital). La pista
  solo lleva voz + SFX; la música se añadiría al publicar.
- Para nuestras ediciones: música de la carpeta del cliente a **−22 dB bajo la voz**, bajando 4 dB más
  cuando entra un testimonio. **[SUPOSICIÓN]** (no hay música en la referencia con la que medir).

### 8.2 Voz
- −18 dBFS RMS de media, muy comprimida y presente. Respiraciones y silencios recortados a 100–280 ms.

### 8.3 SFX (medido por comparación con la librería del cliente)

| t (s) | Evento visual | Sonido | Coincidencia en la carpeta |
| --- | --- | --- | --- |
| 0,1–0,5 | Apertura / zoom | whoosh corto | `Swoosh 01 - 03.wav`, `Swoosh 01 - 06.wav` — probable |
| 1,95 | Palabra clave + salto de zoom | golpe grave corto | **[SUPOSICIÓN]** `Sub Bass Hit.wav` |
| 3,17 | Transición de desenfoque | **obturador de cámara** | `Camera Flash.mp3` / `Camera Shutter.wav` — **confirmado** |
| 4,45–5,0 | Barras + destello | whoosh + golpe grave (el sonido más fuerte: −8 dBFS frente a −18 de la voz) | `Woosh Effect 3.wav` + boom — probable |
| 7,8 | Fin del globo tecleado | clic / notificación | `Mouse Click 04.wav`, `snapchat-notification-sound.mp3` — probable |
| 10,4 · 12,1 | Tarjetas con texto tecleado | teclas | `Escribir teclado.mp3`, `Mechanical Keyboard Click 13.wav`, `Tecla.mp3` — probable |
| 13,65 | Fin de la sección «problema» | caída de subgrave | `Sub Bass Drop 2.wav` / `Boom 2.mp3` — probable |
| 16,5 | Antes de las fichas | clic doble | `Lighter Double Click 02.wav` — probable |
| 17,1 · 17,7 · 18,3 · 19,0 · 19,4 | Cada ficha (PLAN…POST) | pop con cuerpo grave, uno por ficha | `Mouse Click 01/02/04.wav`, `Mechanical Keyboard Click 05/19.wav` — probable |
| 18,66 | Ficha EDIT | clic de obturador | `camera-shutter-click-1133.wav` — probable |
| 20,58 | Barras + destello | whoosh + golpe grave | igual que 4,45 |
| 22,47 | «together.» | clic | `Mechanical Keyboard Click 17.wav` — probable |

### 8.4 Reglas de sonido
1. **Cada elemento gráfico que entra suena** (clic/pop); cada **transición** lleva whoosh, y las dos
   grandes (barras) además un golpe grave.
2. **Todo texto tecleado lleva teclas** sincronizadas con cada palabra/letra.
3. El cambio de cámara «a foto» (desenfoque) lleva **obturador**.
4. Las palabras pequeñas del subtítulo **no** suenan; solo la palabra clave cuando coincide con un salto de zoom.
5. Los SFX van por debajo de la voz (−6 a −12 dB) salvo los dos golpes de transición.
6. **Solo se usan SFX de la carpeta del cliente** (`material/drive/SFX`). Nunca de otra fuente.

---

## 9. Reglas del cliente (se aplican siempre)

- Formato de entrega: **vertical 1080×1920 a 60 fps**.
- Colores y tipografías: **los de la referencia** (apartados 2 y 3).
- En los textos que se escriben en pantalla, **SFX de tecleo**.
- SFX **únicamente** de la carpeta enviada. Música: de la carpeta de música enviada.
- Dinámico pero premium, **sin saturar** (máximo 2 recursos gráficos a la vez, ver 3.5).

## 10. Formato «clase horizontal» (decisión de montaje, no viene de la referencia)

El cliente graba en horizontal (16:9) y propone como formato el reel de Instagram
`DeU3534pDWp`: lienzo vertical oscuro, título arriba y el vídeo horizontal en el centro.
La referencia de edición es a pantalla completa, así que se combinan así:

| Elemento | Valor |
| --- | --- |
| Gancho y frase de cierre mirando a cámara | **pantalla completa** (recorte vertical que sigue la cara), subtítulos centrados en y ≈ 1150 px |
| Resto | **ventana** 1024×640 px en (28, 446), radio 32 px, borde 1 px blanco al 12 %; zoom base 1,6 sobre el plano original |
| Titular de capítulo | y ≈ 246–420 px: antetítulo Sora 25 px en mayúsculas espaciadas + titular Inter Tight 700 de 86 px, **tecleado** a 20 caracteres/s |
| Zona de subtítulos y gráficos | bajo la ventana, centro en y ≈ 1312 px (queda libre el margen inferior de Instagram) |
| Testimonio | tarjeta vertical 800×940 px con chip «Testimonio» y rótulo de nombre; subtítulos debajo |
| Cambio de formato | siempre tapado por una transición de barras o por un encogimiento de 340 ms |
| Fondo | #060606 con dos resplandores radiales muy tenues (lima y vino) |
| Frase del guion sin grabar | se escribe en tarjeta verde con serif itálica, tecleada palabra a palabra sobre b-roll |
| Música | 22 dB por debajo de la voz; el arranque de la batería coincide con el inicio de la solución |
| Inicios de frase | sobre la rejilla de 0,25 s de la música (120 BPM) |

## 11. Correcciones aprobadas

_(Aquí se añade cada corrección que el cliente dé por buena, con fecha, para que se mantenga en las
siguientes ediciones.)_
