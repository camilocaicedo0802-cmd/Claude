# estilo.md · Guía de edición

Fuente: `referencia/referencia.mp4` (25,49 s · 720x1280 · 30 fps · AAC 48 kHz estéreo).
Todos los valores están convertidos al lienzo del proyecto: **1080x1920 a 60 fps** (1 fotograma = 16,7 ms).
Lo que no se pudo medir directamente lleva **[SUPOSICIÓN]**.

> **Qué se copia y qué no.** La referencia es una pieza de portafolio de *Mohmd.Visuals*: un fondo plateado con dos tarjetas, "raw" (crudo) y "result" (editado). **Solo se imita la tarjeta "result"**, que es la edición. No se copian el fondo plateado, las etiquetas raw/result, la firma "Mohmd.Visuals" ni la marca de agua "MV" del pie del vídeo.
> La tarjeta "result" mide 368x654 px dentro del vídeo; se recortó (`referencia/result_crop.mp4`) y se reescaló ×2,935 para medir en 1080x1920.

---

## 1. Estructura y ritmo

| Tramo (s) | Tipo de plano | Qué pasa |
|---|---|---|
| 0,00–3,07 | Plano hablando (PH) | Zoom de salida inicial, palabra gigante detrás de la cabeza, tarjeta UI "Medical Practice" |
| 3,10–7,55 | PH | 3 reencuadres; tarjeta con gráfica "Grow"; palabras gigantes |
| 7,60–9,60 | B-roll a pantalla completa | Médico con paciente, zoom de salida lento, tipografía encima |
| 9,60–9,83 | Transición light leak | Destello naranja → blanco → arcoíris |
| 9,83–16,13 | PH | Gancho del problema; 6 cambios de encuadre |
| 16,13–19,53 | Motion graphic a pantalla completa | Fondo azul claro, tarjetas de servicio apiladas, titulares condensados |
| 19,53–22,33 | PH | Palabra gigante y tres iconos en cristal |
| 22,33–23,50 | Motion graphic | Reloj de arena 3D + palabras sueltas |
| 23,50–25,49 | Motion graphic | Radar con avatar + iconos de personas |

- **Reparto del tiempo:** PH 64 % (16,3 s) · motion graphic a pantalla completa 25 % (6,4 s) · b-roll 8 % (2,0 s) · transición 1 %.
- **Cambios de escena "grandes"** (cambia el tipo de imagen): 6 en 25,5 s → **uno cada 4,2 s** de media (en 7,60 / 9,83 / 16,13 / 19,53 / 22,33 / 23,50 s).
- **Cambios de encuadre dentro del PH** (punch, empuje o reencuadre): **uno cada 1,0–1,5 s**, siempre al empezar una frase.
- **Algo nuevo en pantalla cada 0,5–1,0 s** (palabra, bloque, tarjeta, icono o encuadre). Nunca hay más de 1,5 s sin un cambio visual.
- **Solapes de UI sobre el PH:** 3 en 25 s (tarjeta clínica 0,67–3,1 s; gráfica 4,5–6,3 s; iconos 21,3–22,3 s) → **uno cada ~8 s**, de 1,0 a 2,4 s cada uno.
- **Silencios:** la voz no tiene huecos mayores de 0,36 s (el hueco más largo, 9,58–9,84 s, coincide con la transición light leak). Los silencios se recortan.

## 2. Movimiento de cámara en el plano hablando

Medido con detección de cara (ancho de la cara en px sobre 1080):

| Movimiento | Valores | Cuándo |
|---|---|---|
| Zoom de salida de apertura | escala **1,32 → 1,00** en **36 f (0,6 s)**, ease-out | Fotograma 0 del vídeo |
| Zoom de salida tras transición | escala **1,15 → 1,00** en **24–30 f (0,4–0,5 s)**, ease-out | Al volver al PH desde b-roll/MG/light leak |
| Punch-in | **+8 % a +12 %** en **4–6 f**, ease-out, con desenfoque de movimiento | Inicio de frase (p. ej. 3,30 s, 6,60 s, 14,0 s) |
| Empuje lento | **+10 %** en **60 f (1 s)**, lineal | Durante frases largas (1,4–2,4 s) |
| Reencuadre vertical | el sujeto baja **+130–140 px** (y sube escala +12–28 %) en **18 f (0,3 s)**, y vuelve después | Para dejar sitio a la palabra gigante encima de la cabeza (4,7 s, 12,8 s, 20,1 s) |
| B-roll | escala **1,35 → 1,00** durante todo el clip (2 s), lineal | Ken Burns de salida |

Nunca hay un PH estático más de ~1 s.

## 3. Subtítulos

### 3.1 Tipografías [SUPOSICIÓN: la referencia usa Helvetica Neue + una condensada tipo Druk/Tusker Grotesk, que son de pago]

| Uso | En la referencia (aspecto) | Fuente en el proyecto | Peso |
|---|---|---|---|
| Subtítulo normal | Grotesca neutra tipo Helvetica Neue, minúsculas | **Inter Tight** | 400 |
| Palabra destacada en línea | La misma grotesca, MAYÚSCULAS, negrita ancha | **Inter Tight** | 800 |
| Palabra gigante / titular | Grotesca ultracondensada, MAYÚSCULAS, interletra apretada | **League Gothic, ancho 75 %** | 400 (+ trazo 1,5 px del mismo color para engordar) |
| Palabra destacada en MG ("want", "wait") | Grotesca negrita cursiva | **Inter Tight** | 800 italic |
| Textos de UI (tarjetas) | Grotesca neutra | **Inter Tight** | 500 / 700 |

Comparativa: `referencia/tipos/` y las pruebas de fuentes. League Gothic al 75 % mide 733 px frente a ~780 px de la referencia en "MORE IMPORTANT" a la misma altura → se compensa con `letter-spacing: -0.01em` y un trazo de 1,5 px.

### 3.2 Tamaños y posición (lienzo 1080x1920)

| Elemento | Tamaño | Posición |
|---|---|---|
| Subtítulo normal | **80 px** (≈ 465 px de ancho para "that's a great"), interletra -0,02 em | Centrado; **línea en y ≈ 830–880 px** (altura del pecho, 44–46 % de la pantalla). **No va abajo.** |
| Destacado en línea (cian) | **84 px**, Inter Tight 800, MAYÚSCULAS | Justo debajo del subtítulo, interlineado **0,95** (las líneas casi se tocan), y ≈ 950 px |
| Palabra gigante delante (blanca/roja) | altura de mayúscula **170–185 px** (≈ font-size 235 px), ancho 700–780 px | Centrada, y ≈ 880–1060 px, sobre el pecho |
| Palabra gigante **detrás de la cabeza** (cian) | altura de mayúscula **300–420 px**, llena el **88–92 %** del ancho (márgenes ≈ 50 px) | y ≈ 180–600 px; **la cabeza del sujeto queda delante** (recorte del sujeto) |
| Palabras de contexto con la gigante detrás | **60 px**, Inter Tight 400 | Arriba, y ≈ 190–230 px, **partidas a izquierda y derecha de la cabeza** ("mostly · · · through") |
| Titular en MG | altura de mayúscula **145–180 px** | Centrado, y ≈ 450–600 px |
| Palabra cursiva en MG ("want") | **100 px** | Alineada a izq./der., junto al objeto 3D |
| Palabras pequeñas en MG | **48 px**, Inter Tight 400, gris oscuro | Encima de la palabra cursiva |

Márgenes de seguridad: ≥ 60 px a los lados; nada importante por debajo de y = 1650 px.

### 3.3 Palabras por bloque

- Cada bloque = **2–4 palabras pequeñas + 1 destacada (1–3 palabras)**. Media: **4–5 palabras en pantalla**.
- **Cada bloque tiene exactamente una palabra destacada.** Duración del bloque: 0,8–2,0 s (media 1,3 s).
- Mayúsculas y minúsculas originales en el subtítulo normal (minúscula salvo inicio de frase); la destacada siempre en MAYÚSCULAS.
- No se subtitula una palabra que ya está escrita en un gráfico al mismo tiempo (p. ej. "medical practice" lo dice la tarjeta UI).

### 3.4 Tres estilos de destacado (se alternan)

1. **Cian en línea** (≈ 25 % de los bloques): Inter Tight 800, `#1FADD9`→`#28BCEE`. Ej.: "PLACE TO BE", "REFERRALS", "IS VALUABLE".
2. **Gigante detrás de la cabeza** (≈ 45 %): League Gothic, degradado vertical **`#68D8F8` (arriba) → `#3D7BA6` (abajo)**, resplandor `0 0 24px rgba(80,170,210,0.35)`. Ej.: "SUCCESSFUL", "REFERRALS", "DECIDE", "PURPOSE", "CONTROL", "HAPPEN", "CAPACITY", "SERVICE". Puede llevar emojis 3D a los lados (🏆 en "SUCCESSFUL").
3. **Gigante delante, tecleada letra a letra** (≈ 20 %): League Gothic blanco `#F3F4F9`. Ej.: "MORE IMPORTANT", "DECIDE".
   - Variante **alerta** para palabras negativas ("PROBLEM"): primero rojo **`#EC011A`** con resplandor `0 0 28px rgba(236,1,26,0.8)`, a los 0,3 s pasa a blanco; dos **"!" rojas `#EB2C35`** a los lados, rotadas −12° y +15°, que entran con pop.
4. (B-roll) **Blanca gigante + píldora cian** cruzándola: píldora `#0FB2EF`, radio 999 px, texto blanco Inter Tight 500 de 56 px, padding 8×26 px, rotación −3°.

### 3.5 Animación de entrada (60 fps)

| Elemento | Animación | Duración | Sincronía con la voz |
|---|---|---|---|
| Palabra pequeña | opacidad 0→1, desenfoque 8→0 px, y −12→0 px, escala 1,06→1 | **8 f** (0,13 s), ease-out | Aparece **3–6 f antes** de que se pronuncie |
| Destacado cian en línea | igual + escala 1,15→1 | **8–10 f** | **6–12 f antes** |
| Gigante detrás | letra a letra de izquierda a derecha: opacidad 0→1, desenfoque 14→0, y +30→0; retardo de **1,5 f por letra** | total **15–18 f** | Empieza **20–25 f (0,35–0,4 s) antes** y termina al pronunciarse |
| Gigante tecleada | máquina de escribir: **1 letra cada 2,6 f**, cada letra de gris 40 % a blanco 100 % en 6 f | dura lo que dura la palabra hablada | Empieza **9 f antes** |
| "!" de alerta | pop: escala 0→1,2→1 con rotación | 10 f | Con la primera letra |
| Salida del bloque | opacidad 1→0 y desenfoque 0→6 px | **6 f** | Al empezar el bloque siguiente (sin solape) |

## 4. Textos en pantalla y motion graphics

### 4.1 Paleta (muestreada en píxeles)

| Token | Hex | Uso |
|---|---|---|
| cian-texto | `#1FADD9` (claro `#28BCEE`) | Destacado en línea |
| cian-gigante | `#68D8F8` → `#3D7BA6` | Degradado de la palabra detrás |
| cian-MG | `#65CEF8` → `#3AA0CD` | Titulares en fondos azul claro |
| cian-píldora | `#0FB2EF` | Píldoras, iconos de personas (`#1EB4EA`) |
| rojo-alerta | `#EC011A` / `#EB2C35` | "PROBLEM" y "!" |
| blanco-texto | `#F3F4F9` | Subtítulos y gigantes blancas |
| navy-tarjeta | `#0B3350` → `#021725` | Fondo de tarjetas oscuras (gráfica) |
| navy-cabecera | `#1D3E8A` | Cabecera de la tarjeta clínica |
| verde-ok | `#22C55E` | Check "Fully Booked", flecha de tendencia |
| fondo-MG | esquinas `#8BCEFA` (sup-der) y `#83C3EB` (inf-izq); diagonal blanca `#F8F9FE`→`#F3F9FC` | Fondo de los motion graphics |
| gris-texto-MG | `#2B2B2B` [SUPOSICIÓN] | Palabras pequeñas sobre fondo claro |

### 4.2 Componentes

- **Tarjeta UI de cristal (glassmorphism)** sobre el PH, a la altura del pecho (centro y ≈ 1050 px, ancho ≈ 640 px, alto ≈ 360 px): fondo `rgba(30,60,110,0.55)` + `backdrop-filter: blur(12px)`, borde 2 px `rgba(255,255,255,0.35)`, radio 28 px, sombra `0 20px 60px rgba(0,0,0,0.45)`. Lleva **fotografía** del tema, **cabecera** con icono + título en mayúsculas (Inter Tight 600, 34 px, interletra 0,04 em) y **2 widgets satélite** en cristal (cuadrado 150×150 con icono + contador animado; chip con icono + check verde).
  - Entrada: opacidad 0→1, escala 0,85→1, y +80→0, desenfoque 16→0 en **22 f** (0,37 s), ease-out. Los widgets entran **8 f** después, uno tras otro.
  - **Contador animado:** p. ej. 224+ → 300+ en 60 f (1 s), con flecha verde.
- **Tarjeta de gráfica oscura** (≈ 690×420 px, centro y ≈ 1160 px): degradado navy, radio 36 px, borde 1 px `rgba(120,200,255,0.3)`, 3 líneas de cuadrícula horizontales `rgba(120,200,255,0.25)`, curva `#2EC4F2` de 4 px con resplandor `0 0 10px #2EC4F2`, **dibujada en 60 f** (ease-in-out); título blanco Inter Tight 500 de 60 px arriba a la izquierda. Entrada: de transparente a sólida en 20 f.
- **Fila de 3 iconos en cristal** (≈ 210×210 px, radio 30 px, cristal oscuro, icono cian degradado + 2 líneas de texto en mayúsculas de 26 px). Entran **escalonados 6 f** con pop (escala 0,7→1,05→1). Encima, el destacado cian en línea.
- **Pila de tarjetas (MG a pantalla completa):** 3 tarjetas blancas tipo app (foto + etiqueta "● In Demand" verde + título negrita + subtítulo gris + fila de 3 iconos), la central delante (≈ 330×520 px) y dos detrás desplazadas ±230 px y escaladas 0,85. Entran con desenfoque 20→0 y escala 0,9→1 en 20 f; el titular condensado está **detrás** de la pila (arriba) y otro titular debajo.
- **Objeto 3D aislado** (reloj de arena) sobre fondo MG, rotación oscilante ±8° y ligera inclinación 3D, entrada con desenfoque 20→0 y opacidad en 16 f. Palabras clave en cursiva cian **entran deslizándose** en horizontal (±300 px → 0 en 10 f con desenfoque de movimiento).
- **Radar:** avatar circular del presentador (160 px, borde blanco 4 px), 3 anillos blancos 2 px `rgba(255,255,255,0.85)` de radios 180/260/340 px que se expanden desde 0; 6 iconos de persona cian aparecen **escalonados 5 f** con pop en las órbitas; el avatar late (resplandor cian). Titular arriba y abajo.
- **Emoji / objeto 3D decorativo** junto a la palabra gigante (🏆): pop con rotación ±15°, 12 f, entra 0,3 s después de la palabra.

## 5. B-roll

- **Proporción:** 8 % del tiempo en la referencia (1 clip de 2,0 s), más 25 % de motion graphics a pantalla completa. Para mantener la atención: **un recurso a pantalla completa (b-roll o MG) cada ~4 s**.
- **Contenido:** ilustra **literalmente** la frase (habla de pacientes y confianza → médico hablando con paciente). Estética de stock limpia: luz cálida, interior premium, poca profundidad de campo.
- **Tratamiento:** pantalla completa, Ken Burns de salida 1,35→1,00, tipografía encima (pequeña blanca + gigante blanca + píldora cian). La voz sigue debajo.
- **Duración:** 1,5–2,5 s por clip.

## 6. Transiciones

| Transición | Valores | Cuándo |
|---|---|---|
| **Corte con desenfoque** (la más usada) | Sale: desenfoque 0→20 px + escala 1→1,08 en **6 f**. Entra: desenfoque 20→0 + escala 1,10→1,00 en **12–16 f**, ease-out | PH ↔ motion graphic (16,13 / 19,53 / 22,33 s) |
| **Light leak + flash** | **18 f** en total: destello rojo-naranja (f 0–4) → blanco puro (f 6–8) → fuga arcoíris (f 9–14) → blanco (f 15–16) → plano nuevo con restos de prisma | **Una sola vez**, en el giro del guion ("but there's one problem") |
| **Punch-in** | corte + escala +8–12 % en 4–6 f | Entre frases dentro del PH |
| Corte seco | — | B-roll → tipografía (7,60 s) |

## 7. Zooms (resumen)

Ver §2. Regla: **cada frase empieza con un cambio de escala o de posición**; alternar ancho (1,00) y cerrado (1,10–1,15); tras cada transición, zoom de salida de 1,15 a 1,00.

## 8. Color

Medido comparando "raw" y "result" en 5 instantes:

| Parámetro | Raw | Result | Ajuste aplicado |
|---|---|---|---|
| Contraste (desv. luma) | 0,200 | 0,236 | **+18 %** |
| Saturación media | 0,24 | 0,37 | **+55 %** |
| Negros (percentil 5) | 0,063 | 0,045 | negros más profundos |
| Altas luces (percentil 95) | 0,71 | 0,79 | **+11 %** |
| Fondo (ventana/ciudad) RGB | 0,49 / 0,51 / 0,57 | 0,48 / 0,56 / 0,66 | **G +0,05, B +0,09**: sombras y fondo hacia **cian-teal**; la piel se mantiene cálida |

Look: frío/cian en fondos, piel cálida, contraste medio-alto, nítido. Motion graphics en blanco + azul cielo.

## 9. Sonido

- **Voz:** protagonista, limpia, a **−14 LUFS** integrados [SUPOSICIÓN], sin huecos > 0,35 s.
- **Música:** electrónica corporativa/tech ambiental, **~115 BPM**, pads de sintetizador + sub-bajo + percusión mínima; **−14 a −16 dB por debajo de la voz**, con ducking bajo la voz; sin drops agresivos. [SUPOSICIÓN: estimación por escucha automática]
- **Efectos (≈ 0,7 por segundo; 17 en 25 s):**

| Momento | Efecto | Nivel frente a la voz |
|---|---|---|
| Entra una tarjeta UI | whoosh suave / pop | más bajo (−10 dB) |
| Aparece un widget o chip | pop de burbuja / clic de UI | más bajo |
| Cambia un contador | tic | más bajo |
| Aparece la gráfica y se dibuja | subida digital (riser corto) | más bajo |
| Palabra destacada gigante | impacto grave (sub hit / punch) | parecido |
| "PROBLEM" | pop de alerta / impacto | parecido |
| Transición a b-roll o MG | whoosh / swoosh | más bajo |
| Entrada de la pila de tarjetas | pop múltiple / obturador | parecido |
| Cambio de tarjeta | swipe | más bajo |
| Iconos en cristal | golpe digital / brillo | más bajo |
| Reloj de arena | whoosh de cristal / metálico | parecido |
| Radar | campanita digital / pop de nodo | más bajo |

- **Reglas:** (1) cada elemento UI que aparece lleva su pop/clic; (2) cada palabra gigante lleva impacto o whoosh; (3) cada cambio de escena lleva whoosh; (4) los subtítulos normales **no** llevan sonido.
- **Regla del cliente:** **los textos llevan SFX de tecleo (typing)** sincronizados con la aparición letra a letra o palabra a palabra. **Solo se usan SFX de la carpeta del cliente.**

---

## Reglas aprendidas (correcciones del cliente)

*Aquí se añaden las correcciones que el cliente apruebe, para que se mantengan en las siguientes ediciones.*

- **Sonido:** usar **solo** los SFX de la carpeta enviada por el cliente; nunca efectos propios.
- **Textos:** usar los SFX de *typing* **solo en los textos grandes e importantes** (corrección sobre la v4): las palabras gigantes detrás de la cabeza y los titulares condensados de los motion graphics. Una tecla mecánica cada 2 letras (cada 3 f a 60 fps), sincronizada con la aparición letra a letra, vol. 0,38. Los subtítulos y los destacados cian en línea van **sin** tecleo.
- **Colores y tipografías (actualizado en la v6, sustituye a la regla anterior de usar las de la referencia):** el contenido es para mujeres, así que la tipografía es **más delicada** (ni cursiva ni de adorno) y el acento es **morado lila** en lugar de cian. La *estructura* de la referencia se mantiene: tamaños, posiciones, animaciones y jerarquía.
  - **Textos:** Jost. Subtítulo 300, 80 px, interletra −0,02 em. Destacado en línea 500, MAYÚSCULAS, 84 px, interletra +0,04 em. Chips y tarjetas 400/500.
  - **Palabras gigantes y titulares:** Sofia Sans Extra Condensed. Peso 400 detrás de la cabeza, con degradado `#E4D4FF` → `#9D6FEA`, trazo de 1 px y brillo lila. Peso 300 en los motion graphics, con degradado `#B892F5` → `#7E4FDC`.
  - **Lila:** destacado sobre vídeo `#B794F6` (claro `#D2B8FF`); píldoras `#9B6BF2`; curvas y barras `#C4A5FF` / `#9B6BF2`; tarjetas oscuras en morado profundo `#2E1C52` → `#150B2A`; fondo de los motion graphics en lavanda (esquinas `#DCCBFF` / `#CFBDF7`, centro `#FBF8FF`). Los iconos 3D azules (flechas) se tiñen con `hue-rotate(48deg)`.
- **Rostro luminoso:** la cara no debe verse oscura. Curva de gamma en la capa de la persona (exponente 0,74, amplitud 1,04) y más suave en el fondo (0,88 / 1,02), con contraste ×1,02–1,03 y saturación ×1,05. Levanta sombras y medios tonos sin quemar altas luces.
- **Estilo UGC, más sencillo** (corrección sobre la v1). Del estilo de la referencia se mantienen la tipografía, los colores y los subtítulos palabra a palabra, pero el montaje debe parecer contenido de creador, no un anuncio producido:
  - **Plano hablando ≥ 85 % del tiempo.** Nada de motion graphics a pantalla completa (buscadores, objetos 3D, gráficas grandes, tarjeta de cierre).
  - **B-roll solo con las tomas propias del creador** (producto en mano, gomita en la palma), 1,5–2 s, **corte seco** y escala 1,06→1,00. Sin stock de cine.
  - **Subtítulos:** casi todo en estilo **cian en línea** (§3.4-1). Como mucho **2 palabras gigantes detrás de la cabeza** por vídeo (gancho y tema central). Sin palabras tecleadas gigantes.
  - **Como mucho 1 superposición informativa** pequeña (p. ej. tarjeta con curva), a la altura del pecho.
  - **Iconos 3D:** 2 como máximo en todo el vídeo.
  - **Cámara:** apertura 1,12→1,00 en 0,5 s; en cada corte de salto, alternar escala 1,00 / 1,07 de golpe (4 f). Sin reencuadres grandes.
  - **Transiciones:** cortes secos. Sin light leak ni desenfoques de corte.
  - **Color natural:** contraste ×1,05, saturación ×1,08, sin virado cian ni viñeta.
  - **Sonido:** tecleo solo en los textos grandes (ver regla de "Textos"), swoosh suave (0,2) en los cortes a b-roll y pop en la superposición. Sin impactos graves, risers ni film burn.
- **Excepción: la parte explicativa de salud lleva apoyo visual** (corrección sobre la v2). Cuando el creador explica un tema técnico o de salud (aquí, la glucosa), ese tramo sí lleva:
  - **B-roll e imágenes de salud cada 1,0–1,6 s**: comida con glucómetro, azúcar, medición en el dedo, glóbulos en la sangre. Se buscan en bancos con licencia comercial (Unsplash, Mixkit) y se anotan en `public/img/CREDITOS.txt`.
  - **Datos reales, con fuente y prudencia**: cada dato lleva su fuente en un pie de 25 px (p. ej. "pico 1–2 h", "2–3 h para normalizarse*", estudio del vinagre con "puede"). Las gráficas llevan "Gráfico ilustrativo. No sustituye el consejo médico."
  - **Motion graphics de la referencia** (fondo azul claro §4.1, titulares condensados cian letra a letra, tarjetas blancas, chips cian), con entrada de desenfoque 18→0 en 12 f y whoosh. Dentro del motion graphic, las palabras dichas las pinta la propia escena, sincronizadas.
  - **Chips y tarjetas de cristal** sobre el b-roll para explicar (p. ej. "Carbohidratos → Glucosa", barra de tiempo 0–3 h con contador).
  - Fuera de ese tramo se mantienen las reglas UGC.
- **El vídeo nunca termina en seco: debe cerrar la idea** (corrección sobre la v3).
  - Después de la última palabra se deja **≥ 0,8 s de la acción natural** del creador (aquí, echándose las gomitas en la mano). La voz se funde en 0,6 s.
  - Se termina con un **plano de producto de 1,2–1,5 s** y una píldora cian sencilla con el nombre del producto (y la marca en pequeño), colocada en una zona limpia sin tapar la etiqueta.
  - La música **sube un poco al terminar la voz** (0,12 → 0,20) y **se funde en el último segundo**.
- **Legibilidad sobre b-roll claro:** degradado oscuro suave detrás de los subtítulos (transparente → 38 % de negro entre el 66 % y el 76 % de la altura → transparente) en todas las imágenes y b-roll.
