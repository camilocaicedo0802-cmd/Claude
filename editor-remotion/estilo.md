# estilo.md — Guía de estilo de edición

Extraída del vídeo de referencia `referencia/referencia.mp4`, **solo del vídeo final
de la derecha** (la tarjeta "$70 Ads"; se ignoran la tarjeta "Raw", el fondo gris y el
texto "DM me ADS"). Recorte analizado: `crop=356:633:265:308` → `referencia/final_derecha.mp4`.

Método: 872 fotogramas (30 fps, 29,07 s) extraídos con ffmpeg, hojas de contacto a 2 fps y
fotograma a fotograma en cada animación, detección de cortes por diferencia entre
fotogramas, curva de zoom por emparejado de puntos (ORB), medición de cajas de texto y
colores por píxel, transcripción con Whisper (tiempos por palabra) y análisis del canal
lateral del audio (L−R) para aislar efectos y música de la voz.

Todas las medidas en píxeles están **convertidas a 1080 × 1920**. Lo que no se puede medir
con certeza va marcado con **[SUPOSICIÓN]**.

---

## 1. Formato

| Parámetro | Referencia | Nuestro proyecto |
| --- | --- | --- |
| Lienzo | 9:16 vertical | 1080 × 1920 |
| Fotogramas por segundo | 30 | 60 (animaciones definidas en segundos) |
| Duración | 29 s (fragmento) | la que pida el guion |

## 2. Ritmo de cortes

- 8 cortes en 29 s → **un plano nuevo cada 3,6 s de media** (mín. 0,8 s, máx. 5,9 s).
- Tiempos de corte: 3,57 · 7,07 · 8,60 · 12,33 · 14,50 · 19,40 · 25,30 · 28,30 s.
- Tipos de plano: **busto parlante** (71 % del tiempo) y **escena de motion graphics a
  pantalla completa** (29 %: 7,07–8,60 s y 14,50–19,40 s).
- Los cortes dentro del busto parlante son *jump cuts* que quitan silencios; el encuadre
  cambia de escala entre un plano y el siguiente (1,00× ↔ 1,22×) para que no se note el salto.
- Nunca pasan más de **1,5 s sin que cambie algo en pantalla** (palabra nueva, destacado,
  icono, zoom o corte).
- No hay silencios: la voz encadena frase con frase (huecos < 0,35 s).

## 3. Zooms y movimiento de cámara

No hay zoom lento continuo. El movimiento es un **golpe de zoom al empezar el plano**, que
frena solo y luego queda quieto:

| Plano | Escala inicial → final | Duración | Curva |
| --- | --- | --- | --- |
| 0,00 s (arranque) | 1,34× → 1,00× (aleja) | 0,6 s | salida suave (ease-out) |
| 3,57 s | ≥ 1,28× → 1,00× (aleja) | 0,9 s | salida suave |
| 8,60 s | 1,00× → 1,22× (acerca) | 0,7 s | salida suave |
| 19,40 s | 1,25× → 1,00× (aleja) | 0,6 s | salida suave, luego deriva −1 %/s |
| 12,33 · 25,30 · 28,30 s | sin zoom (corte seco) | — | — |

- Cada golpe de zoom lleva **desenfoque de movimiento** en sus primeros 4–6 fotogramas y un
  whoosh (ver §11).
- Al entrar una palabra destacada grande el plano se acerca un **+5 %** en 0,1 s
  **[SUPOSICIÓN: medido a ojo, por debajo del error del método]**.
- En las escenas de motion graphics: entrada con zoom 3× → 1× en 0,3 s y después deriva lenta
  +3 % hasta el final de la escena.

## 4. Subtítulos (texto normal)

| Parámetro | Valor |
| --- | --- |
| Fuente | **Helvetica Neue Light** (peso 300) [SUPOSICIÓN: podría ser Neue Haas Grotesk; mismas formas] |
| Tamaño | **70 px** (altura de ascendentes ≈ 52 px; 3,6 % del alto) |
| Interletraje | **−0,05 em** (muy apretado) |
| Caja | minúsculas; mayúscula solo al inicio de frase; sin punto final ni comas |
| Color | blanco `#FFFFFF` |
| Textura | resplandor blanco suave (desenfoque ≈ 14 px, opacidad ≈ 45 %) + sombra negra difusa (desenfoque ≈ 24 px, opacidad ≈ 55 %). Sin contorno ni caja de fondo |
| Posición | centrado en horizontal (x = 540); centro vertical entre **y = 1015 y 1090** (53–57 % del alto), a la altura del pecho, nunca tapando la cara |
| Palabras por bloque | **1 a 4** (media 2,4). Una sola línea |
| Duración del bloque | 0,4–1,2 s |
| Sincronía | cada palabra aparece cuando se pronuncia (desfase medido +0,05 a +0,15 s respecto a Whisper) |

**Animación de entrada, palabra a palabra:** la palabra nueva aparece 12 px por encima de su
sitio, ligeramente inclinada (≈ −3°), y baja a su posición en **0,1 s** (3 fotogramas a
30 fps) con salida suave. Sin fundido largo (opacidad 0 → 1 en 2 fotogramas). Las palabras
anteriores del bloque no se mueven.

**Salida:** el bloque desaparece de golpe (corte, 0 fotogramas) cuando empieza el siguiente.

**No se subtitula todo:** las muletillas se omiten ("some of the", "in the world", "use
this" no aparecen). Se muestra solo lo que lleva significado.

## 5. Palabra / frase destacada

Aparece en el **29 % del tiempo** (7 destacados en 29 s ≈ uno cada 4 s): TECHNIQUE · THE
FRAMEWORK · AI · HOW THEY ARE · MANAGING · 80% OF THE WORK (+ rótulos de los gráficos).

| Parámetro | Valor |
| --- | --- |
| Fuente | **Helvetica Neue Bold** (700). Cursiva (Bold Italic) en los destacados que rematan un bloque de varias líneas (TECHNIQUE, THE FRAMEWORK); recta en los que van solos (HOW THEY ARE, MANAGING, 80% OF THE WORK, AI) |
| Caja | MAYÚSCULAS |
| Tamaño | **90–115 px** (altura de mayúscula 65–85 px); la línea ocupa entre el 47 % y el 73 % del ancho. Una palabra corta va más grande (TECHNIQUE 110 px, AI 120 px); una frase, más pequeña (THE FRAMEWORK 90 px) |
| Interletraje | −0,04 em |
| Relleno | degradado **horizontal**: naranja `#E4844B` (0 %) → `#E7B776` (40 %) → dorado claro `#EDCC8E` (62 %) → naranja `#EB9D61` (100 %). Ligero oscurecido vertical (−8 % de luminosidad abajo) |
| Textura | resplandor naranja `#E8873A` (desenfoque ≈ 28 px, opacidad ≈ 55 %) + sombra negra hacia abajo (desplazamiento 6 px, desenfoque 12 px, opacidad 60 %). Detrás, una mancha oscura difusa que apaga el fondo ≈ 25 % para que el texto resalte |
| Entrada | palabra a palabra; cada una entra con **escala 1,10 → 1,00 en 0,12 s** (pop) |
| Efecto sobre la línea anterior | la línea normal que estaba en pantalla **se atenúa a ≈ 50 % de opacidad** y el destacado se coloca justo debajo, pisándole la parte baja |

### Bloque apilado (título de 3 líneas)

Usado en el gancho (0,2–3,5 s) y en 3,7–5,5 s:

```
This is a                ← línea normal, 70 px, atenuada al 50 %, y ≈ 1002
TECHNIQUE                ← destacado 110 px cursiva, y ≈ 1097
used by (top executives) ← línea normal 70 px + píldora, y ≈ 1178
```

- Alineado a la **izquierda** sobre un mismo borde (x ≈ 237); la 3.ª línea sangrada +33 px.
- Separación entre líneas ≈ 85–95 px (las líneas casi se tocan).
- El bloque entero ocupa de x = 237 a x = 860 (58 % del ancho) y queda quieto hasta el corte.
- Orden de aparición: línea 1 (0,13–0,33 s) → destacado (0,53 s) → "used by" (0,87–0,93 s) →
  icono 1 (0,93 s) → icono 2 (1,13 s) → píldora (1,27 s) → texto de la píldora (1,40–1,53 s).

### Píldora

- Cápsula con esquinas totalmente redondas que rodea 1–2 palabras: alto 62 px, margen
  horizontal 22 px.
- Entra como **cápsula negra opaca** (barrido de izquierda a derecha, 0,07 s); 0,13 s después
  aparecen las palabras dentro (misma caída que los subtítulos) y el relleno pasa a negro al
  55 % de opacidad con **borde de 2 px** color crema-naranja `#E9C9A0`.
- Texto interior: Helvetica Neue Light 66 px, blanco.

### Iconos junto al destacado

- Siluetas planas (dos ejecutivos) con relleno degradado naranja `#E8873A` → `#B4551F` y
  resplandor naranja. Tamaño ≈ 120 × 150 px.
- Colocados **encima y a la derecha** del destacado, parcialmente tapados por él.
- Entran uno a uno (separados 0,2 s) con pop de escala 0 → 1,15 → 1 en 0,2 s.

### Cita en negrita (frase textual)

Usada en 21,7–23,7 s ("Hey I need you to go do this / that's the 10%"):

- Helvetica Neue **Bold** 68 px, minúsculas, entre comillas tipográficas “ ”, blanco con el
  mismo resplandor; interlineado 1,0; dos líneas centradas; línea 1 ocupa el 83 % del ancho.
- La frase entera está en pantalla desde el principio **al 35 % de opacidad** y cada palabra
  pasa al 100 % cuando se pronuncia (efecto karaoke).

## 6. Textos en pantalla fijos

- **Marca de agua**: usuario (`@d4niel.hee`) centrado abajo, y ≈ 1830 (95 % del alto),
  Helvetica Neue Light 56 px, blanco al **30 % de opacidad**, visible todo el vídeo, también
  sobre los motion graphics.
- No hay titulares fijos, barras de progreso, emojis ni rótulos inferiores.

## 7. Motion graphics a pantalla completa

Dos escenas (1,5 s y 4,9 s) que sustituyen al busto mientras la voz sigue.

- **Fondo**: casi negro `#010000` con resplandor radial cálido en el centro
  (`#41150A` junto al objeto → `#230600` a media altura → negro en las esquinas).
- **Objeto central**: barra horizontal tipo cápsula (ancho 81 % del lienzo, alto ≈ 95 px,
  centro y ≈ 845) dividida en 3 tramos (10 | 80 | 10) por dos líneas verticales blancas de
  2 px que sobresalen 35 px por arriba y por abajo. Relleno degradado naranja
  `#C06A47` → `#DFAC71` → `#DE7E4C` → `#C36F45`; contorno blanco de 3 px con resplandor
  blanco (desenfoque ≈ 10 px). Números en blanco-crema, Helvetica Neue Light 56 px.
- **Construcción** (1.ª escena): la barra nace corta y se estira hasta su ancho en 0,25 s; un
  **brillo diagonal** la recorre de izquierda a derecha (0,5 s); los números aparecen uno a
  uno a los 0,13 · 0,23 · 0,43 s.
- **Rótulos** (2.ª escena): texto naranja `#E89864` en Helvetica Neue Bold 52 px con
  resplandor, palabra a palabra. Se conectan a la barra con **flechas blancas de 3 px que se
  dibujan** (trazo progresivo en 0,3 s, curva de un cuarto de círculo o recta, punta al
  final). Cada elemento entra cuando la voz lo nombra.
- Solo hay **un concepto por escena**; todo lo demás es fondo vacío.

## 8. B-roll

- **La referencia no usa b-roll de vídeo**: los únicos insertos son los motion graphics.
- Regla derivada para nuestros vídeos: el b-roll ocupa el papel de esos insertos — a
  pantalla completa, 1,5–5 s, con la voz debajo, entra y sale por corte seco o por la
  transición de luz (§9), y lleva subtítulos igual que el busto.

## 9. Transiciones

| Tipo | Dónde | Descripción |
| --- | --- | --- |
| Corte seco | 7,07 · 8,60 · 12,33 · 14,50 · 25,30 · 28,30 s | 0 fotogramas. Es la transición por defecto |
| **Anillo + fuga de luz naranja** | 3,40–3,77 s y 19,30–19,60 s | un anillo fino naranja crece desde el centro (0,13 s); después una fuga de luz naranja `#F08A2A` cubre el cuadro hasta ≈ 85 % de opacidad justo en el corte y se disuelve en 0,2 s sobre el plano nuevo, que entra con golpe de zoom. Total ≈ 0,35 s. Se usa para **cambiar de bloque temático**, 2 veces en 29 s |

No hay fundidos, cortinillas ni deslizamientos.

## 10. Color

- Busto: contraste suave, negros ligeramente levantados, saturación contenida, piel cálida;
  fondo desenfocado. **[SUPOSICIÓN: etalonado de cámara, no medible por separado]**
- Viñeta ligera (esquinas ≈ −12 % de luminosidad) **[SUPOSICIÓN]**.
- Acento único: **naranja → dorado**. No hay un segundo color de acento.
- Esquinas del vídeo redondeadas: pertenecen a la tarjeta del montaje, no al vídeo → no se copian.

## 11. Sonido

Niveles medidos: voz −17 dB RMS; música + efectos ≈ 20 dB por debajo de la voz.

**Voz**: limpia, seca, en primer plano, sin silencios.

**Música**: una sola pista instrumental ambiental y tonal (notas largas + pulso grave suave
cada ≈ 0,42 s) de principio a fin, muy baja. Durante la cita (21,5–27,5 s) la música pierde
los graves (filtro paso-alto) y vuelve entera a los 28,1 s **[SUPOSICIÓN: se deduce del
espectro, no identifico el tema]**.

**Efectos** (instantes detectados en el canal lateral):

| Momento | Efecto | Acompaña a |
| --- | --- | --- |
| 0,26–0,46 s | whoosh corto | golpe de zoom inicial |
| 1,8–2,2 s | brillo / destello agudo (+18 dB en agudos) | la píldora y el cierre del bloque de título |
| 3,6–3,8 s | whoosh fuerte de banda ancha (+21 dB) | transición anillo + fuga de luz |
| 7,19 s | golpe + whoosh | corte al motion graphic |
| 7,54 · 7,64 · 7,86 · 8,05 s | ticks cortos | aparición de cada número de la barra |
| 13,4–13,9 s | subida (riser) | anticipa el 2.º motion graphic |
| 14,66–14,90 s | whoosh + golpe grave | zoom de entrada al motion graphic |
| 15,16 · 15,76 · 16,49 · 16,92 · 17,98 · 18,65 s | ticks / pops | cada rótulo y cada flecha |
| 19,42–19,63 s | whoosh fuerte (+22 dB) | transición de luz de vuelta al busto |
| 20,8–26,1 s | ráfagas de tecleo muy bajas | textos que se escriben (cita y bloques) |

Reglas que se deducen:

1. **Todo elemento que entra suena**: transición → whoosh; destacado → golpe/whoosh corto;
   icono o número → pop/tick; texto → tecleo.
2. Los efectos van **por debajo de la voz** (nunca la tapan) y duran < 0,6 s, salvo risers.
3. El whoosh empieza 2–4 fotogramas antes del corte y su pico cae en el corte.

---

## 12. Adaptación a AgroKrack

Lo que cambia respecto a la referencia, por indicación del cliente.

### Paleta (tomada del logo `material/crudo/wa_imagen_105200.jpeg`)

| Uso | Color |
| --- | --- |
| Verde oscuro (trazo y texto del logo) | `#0B211D` |
| Verde (hoja / campo) | `#4BB54D` — vivo `#4DC351` |
| Naranja (arco) | `#DC8956` — vivo `#E69057` |
| Crema (fondo) | `#DED5C8` |

- **Destacados**: el degradado naranja → dorado de la referencia se rehace con el naranja del
  logo: `#E69057` → `#F2C48A` → `#F7DDB0` → `#E69057`. Resplandor `#E69057`.
- **Segundo acento (verde del logo)**: píldoras, iconos de "correcto", tramo activo de los
  gráficos y flechas. Degradado `#4DC351` → `#B6E86A`.
- **Fondo de motion graphics**: verde oscuro `#0B211D` con resplandor radial `#17402F`
  (en lugar del negro-marrón de la referencia).
- Texto normal: blanco, igual que la referencia.

### Tipografía

La referencia usa **Helvetica Neue** (Light / Bold / Bold Italic), que es de pago y no está en
este equipo. Sustitutas libres, elegidas comparando los trazos con la referencia:

| Uso | Referencia | En el proyecto | Archivo |
| --- | --- | --- | --- |
| Subtítulos, píldoras, marca de agua | Helvetica Neue Light | **Inter Display Light** (300), interletraje −0,05 em | `public/fonts/InterDisplay-Light.otf` |
| Destacados rectos, cita, rótulos | Helvetica Neue Bold | **TeX Gyre Heros Bold** (clon libre de Helvetica) | `public/fonts/texgyreheros-bold.otf` |
| Destacados en cursiva | Helvetica Neue Bold Italic | **TeX Gyre Heros Bold Italic** | `public/fonts/texgyreheros-bolditalic.otf` |

Si se aportan los archivos de Helvetica Neue, se cambian en un solo sitio (`src/fuentes.ts`).

### Posición y legibilidad del texto

- La regla de la referencia es "sobre el pecho, nunca sobre la cara". En la referencia eso cae
  en y = 1015–1090; aquí depende del plano: presentador en selfie **y ≈ 1390**, agrónomo en
  plano medio **y ≈ 1120–1190**, b-roll **y ≈ 1060**.
- El material es de exterior (arroz amarillo, cielo blanco, ropa clara) y no una camiseta
  oscura de estudio, así que la sombra del texto es más cerrada que en la referencia y la
  línea que se atenúa al entrar un destacado baja al **62 %** (no al 50 %).

### Sonido

- **Solo se usan efectos de la carpeta de Drive del cliente** (`material/sfx/`). Ninguno de
  Remotion ni de otra fuente.
- Los textos que se escriben usan los efectos de **tecleo** del pack.
- Música: de la carpeta de música del cliente.

### B-roll

- Se usa el b-roll propio del rodaje (arroz, cosechadora, grano). El pack genérico de
  recursos no tiene planos de agricultura.

### Cómo se traduce cada recurso de la referencia

| Recurso de la referencia | En los vídeos de AgroKrack |
| --- | --- |
| Bloque apilado con iconos y píldora ("This is a / TECHNIQUE / used by (top executives)") | Idea central del gancho y presentación de cada persona: línea normal + destacado en cursiva + píldora con el dato. Iconos en el verde del logo |
| Destacado suelto ("HOW THEY ARE", "80% OF THE WORK") | Una palabra clave por frase, recta, centrada, con la línea anterior atenuada encima |
| Barra 10 / 80 / 10 con flechas y rótulos | Gráfico propio del tema. Para listas (beneficios, pasos, razones): barra con un tramo por punto; cada tramo se rellena cuando la voz lo nombra y su rótulo se conecta con flecha. Fondo verde oscuro del logo |
| Cita en negrita con karaoke | Frases textuales o promesas ("lo que usted compra es lo que se lleva") |
| Anillo + fuga de luz naranja | Solo al cambiar de bloque (gancho → contexto, contexto → experto, final → logo). Máximo una cada 10–15 s |
| Golpe de zoom al empezar el plano | En cada corte a busto o b-roll: aleja 1,25–1,34× → 1× o acerca 0,86× → 1× en 0,5–0,8 s |
| Marca de agua con el usuario | "AgroKrack" abajo al 30 % (se cambia por el @ exacto en `src/estilo.ts`) |
| (no tiene cierre) | Cierre de 1,9 s con el logo sobre su crema |

### Ritmo objetivo

- Un plano o gráfico nuevo cada 2–3 s; ningún plano de más de 4,5 s sin corte ni cambio de escala.
- Un destacado cada 3–4 s como máximo. Si dos caen seguidos, el segundo pasa a texto normal.
- Las frases largas del busto se cubren con b-roll del propio rodaje en su segunda mitad.

### Masterizado

- Voz de cada toma limpiada (paso-alto 90 Hz, reducción de ruido suave, compresión) y nivelada a −15 LUFS.
- Mezcla final a **−14 LUFS** con limitador (pico < −1 dB). `scripts/exportar.sh` lo hace solo.

---

## 13. Correcciones aprobadas por el cliente

*(Aquí se añade cada corrección que guste, con fecha, para que quede fija en adelante.)*

— vacío por ahora —
