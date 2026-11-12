# estilo.md — Guía de edición (referente: `Reel_referencia_slate_1.mp4`)

Valores medidos sobre el referente (720×1280, 29.97 fps, 58.05 s) y convertidos a nuestro
lienzo **1080×1920 a 30 fps** (factor ×1.5). Lo que no se pudo medir y es una deducción
va marcado con **[SUPOSICIÓN]**.

Método: 116 fotogramas a 2 fps + detección de cambios de plano (`scene`), tiras fotograma
a fotograma de cada animación, medición de píxeles (PIL/numpy), seguimiento del tamaño
de la cara (OpenCV) para medir zooms, transcripción Whisper con tiempos por palabra,
espectrogramas y correlación cruzada de cada SFX del pack contra el audio.

---

## 1. Formato y estructura

| Parámetro | Referente | Nuestro proyecto |
|---|---|---|
| Resolución | 720×1280 | 1080×1920 |
| FPS | 29.97 | 30 |
| Duración | 58.0 s | lo que dure la voz + 1.5 s de salida |
| Estructura | Hook (0–2.7 s) → lista numerada 1–7 con valoración → cierre con risa y fundido | Hook → 3 bloques del guion → CTA |
| Inicio | Sin intro: la persona ya habla en el fotograma 0 | Igual: voz o imagen fuerte en el fotograma 0 |
| Final | Fundido a negro de 1.7 s (56.0 → 57.7 s), audio baja de −16 dB a −41 dB en el mismo tramo | Igual |

## 2. Ritmo de cortes y encuadre

- **Tipo de plano**: plano medio corto fijo (cabeza + pecho). Ancho de cara = **32 % del ancho
  del cuadro** (115 px de 360). Ojos a **~19 % de la altura** desde arriba (cy ≈ 240/640).
- **Cortes duros** (cambio de toma): 2.90 s, 10.58 s, 22.39 s, 44.38 s → **4 cortes en 58 s**.
- **Cambios de encuadre** (cortes + punch-ins + vueltas): ~13 en 58 s → **un cambio cada 4.4 s
  de media**. Lo que mantiene el ritmo es el texto: **algo nuevo aparece en pantalla cada
  1.0–1.5 s**.
- **Zoom de arranque**: el vídeo empieza a **1.42×** y se asienta en **1.0×** en **0.6 s**
  (18 fotogramas, ease-out).
- **Punch-in de énfasis**: salto a **1.15–1.22×** en los momentos clave ("Diez", "Uy, diez",
  "Depende…", "Es más, yo le puedo dar la solución"). Duración del punch-in: **1.0–3.0 s**;
  la vuelta a 1.0× es un corte seco. Entrada: corte seco o rampa de ≤ 6 fotogramas.
- **Push-in lento** antes de un corte: 1.0 → 1.18× en ~0.6 s (2.1–2.7 s) y 1.0 → 1.08× en
  ~1 s (54.3–55.2 s).
- No hay b-roll en el referente: todo es la persona a cámara. **[SUPOSICIÓN]** el b-roll que
  añadimos (lo pide el brief) usa el mismo ritmo: planos de **1.0–2.0 s**, corte seco o
  transición suave, nunca más de 2.5 s seguidos.

## 3. Subtítulos (frases habladas)

| Parámetro | Valor |
|---|---|
| Fuente | Grotesca neo, peso Medium. Equivalente usado: **Inter Display Medium (500)** [SUPOSICIÓN: el original parece SF Pro Display, la fuente de las apps de edición de iOS; Inter Display es la alternativa abierta más parecida] |
| Tamaño | Altura ascendente–descendente 35 px @720 → **cuerpo 54 px @1080** |
| Tracking | **−0.04 em** (letras muy juntas) |
| Color | **#FFFFFF** puro |
| Textura / contorno | **Ninguno**: sin caja, sin contorno. Sombra muy suave para legibilidad [SUPOSICIÓN: `0 2px 8px rgba(0,0,0,.25)`] |
| Posición | **Centrado en X**; centro vertical a **57 % de la altura** (y ≈ 1095 px @1920) — a la altura del pecho, nunca sobre la cara |
| Palabras por bloque | **1–4 palabras**, media **1.7**, máx. ~14 caracteres. Corta en comas y pausas ("No, no," / "no puedo," / "Eso no es tan" / "grave.") |
| Mayúsculas | Frase normal (sentence case), conserva la puntuación hablada (comas, puntos, "…") |
| Animación | **Ninguna**: el bloque cambia en seco en el fotograma en que empieza la primera palabra del bloque siguiente |
| Convivencia | Mientras hay un título/gráfico en pantalla, **no hay subtítulo** (el texto del gráfico sustituye a la frase) |

### Palabra destacada
- Una sola por frase y solo en el hook ("**Cita**" en "en una primera Cita").
- Fuente: **serif itálica condensada**. Equivalente usado: **Instrument Serif Italic**
  [SUPOSICIÓN: la más parecida de 5 candidatas comparadas].
- Color **#FCF210** (amarillo). Tamaño: 124 px de alto @720 → **cuerpo ~235 px @1080**
  (≈ 4.3× el subtítulo).
- Va **debajo** de la línea anterior, solapándola ligeramente, acompañada de un emoji
  (❤️) a la derecha. **En nuestro vídeo: sin emojis** (indicación del cliente) → se sustituye
  por un destello dibujado (✦) en vectorial.
- Entrada: opacidad 0 → 1 + desenfoque 10 px → 0 + escala 0.9 → 1 + subida de 20 px, en
  **4 fotogramas** (133 ms). Se queda hasta el corte.

## 4. Textos en pantalla (títulos de lista / motion graphics)

### Título de hook (palabras en cascada)
- Las palabras del título aparecen **una a una al ritmo de la voz**, cada una en una posición
  distinta formando una **diagonal descendente izquierda → derecha** ("Ranking" arriba-izq.,
  "de" centro, "redflags" abajo-der.).
- Cada palabra entra con **fundido + desenfoque en 3–4 fotogramas** y se queda.
- La palabra clave va en **color de acento + peso Bold** y lleva un **icono** que entra
  **2 fotogramas antes** con un pop de escala (0 → 1.1 → 1).
- Tamaño del hook: "Ranking" 47 px de alto @720 → **cuerpo ~74 px @1080**.

### Ítem numerado ("1. Mal aliento")
- **Número**: Inter Display **Black (900)**, altura de cifra 50 px @720 → **cuerpo ~104 px**,
  tracking −0.04 em, blanco. El punto es cuadrado.
- **Etiqueta**: Inter Display Medium, **cuerpo ~64 px**, interlineado **1.0** (baseline a
  baseline 63 px), máximo 2 líneas, alineada a la izquierda, a **25 px** a la derecha del
  número. El número queda centrado verticalmente respecto al bloque de 2 líneas.
- Posición: bloque con el borde superior al **50 %** de la altura (y ≈ 970 px), centrado
  ópticamente en X (centro del bloque a ~56 % del ancho).
- **Secuencia de entrada** (medida fotograma a fotograma):
  1. f0 — el número aparece **en seco, centrado** en X.
  2. f8 → f16 — el número **se desliza a la izquierda** ~150 px (ease-out, 8 fotogramas)
     para dejar sitio a la etiqueta.
  3. f17 — **línea 1** de la etiqueta: opacidad 0 → 1 + blur 12 px → 0 + desplazamiento
     x +20 px → 0 en **6 fotogramas**.
  4. f20 — **línea 2**, igual, con **3 fotogramas de retraso**.
  5. f28 — **barra de valoración**: opacidad + blur 8 px → 0 en **6 fotogramas**.
- **Salida**: todo el grupo a opacidad 0 + blur 8 px en **6 fotogramas**, en seco al terminar
  la idea.
- **Duración en pantalla**: 3.0–4.0 s por ítem.

### Barra de valoración (objeto gráfico recurrente)
- Píldora translúcida tipo vidrio: **795×72 px @1080** (x de 13 % a 87 %), radio completo,
  relleno blanco ~25 % + borde blanco ~40 %, desenfoque de fondo [SUPOSICIÓN: `backdrop-filter: blur(12px)`].
- Centro vertical a **64 %** de la altura (y ≈ 1230 px).
- 10 círculos **Ø ~56 px**, paso **77 px**, con número blanco Inter SemiBold ~24 px.
- Degradado de color medido: 1–2 `#54A949` · 3–4 `#BAD54F` · 5–6 `#F2E041` · 7–8 `#F79A2D` ·
  9 `#ED7417` · 10 `#F73734`.
- **Puntero**: triángulo blanco ▼ de ~21 px sobre la píldora; se desliza de valor en valor
  (0.13–0.2 s por paso, ease-in-out) hasta la nota final, sincronizado con la palabra
  hablada ("Diez", "un siete").

### Halo de color en los bordes ("glow")
- Cuando el puntero llega a la nota final, los **4 bordes del cuadro se tiñen del color de
  esa nota** (rojo para 10, naranja para 7–8, amarillo para 5–6).
- Forma: viñeta interior, ~**18 % del ancho** de profundidad, opacidad máx. ~55 %.
- Tiempo: entra en **4 fotogramas**, se mantiene **0.6–0.9 s**, sale en **~10 fotogramas**.
- Va **acompañado de un punch-in de 1.2×** cuando la nota es 10.

## 5. B-roll

- El referente **no usa b-roll** (todo es a cámara). El brief del cliente sí lo pide.
- Reglas aplicadas [SUPOSICIÓN, coherente con el ritmo del referente]:
  - Cada b-roll **1.0–2.0 s**, a pantalla completa, reencuadrado a 9:16.
  - Movimiento interno lento: **escala 1.00 → 1.06** a lo largo del plano (Ken Burns sutil).
  - El b-roll ilustra **literalmente** lo que dice la voz (aplicación cuando se habla de
    spray tan, resultado cuando se habla del color/desarrollo).
  - Los subtítulos y gráficos siguen encima del b-roll con la misma posición.

## 6. Transiciones

- Entre tomas: **corte seco** (4 de 4 cortes del referente).
- Entre encuadres: **punch-in** seco o rampa ≤ 6 fotogramas.
- Textos: entrada/salida con **blur + fundido de 4–6 fotogramas**; nunca deslizamientos
  largos, rebotes ni giros.
- Cierre: **fundido a negro de 1.7 s**.
- Ajuste por manual de marca (spa, "transiciones suaves y sutiles"): donde se pase de la
  persona a un b-roll se permite un **fundido cruzado de 6 fotogramas** con blur 6 px →
  0 [SUPOSICIÓN: no existe en el referente; se añade para el tono premium].

## 7. Color

- Etalonaje **cálido / melocotón**: media RGB del cuadro ≈ (158, 130, 104); R − B ≈ +54.
- Negros a ~10/255 (no levantados), altas luces a ~234/255 (sin quemar, roll-off suave).
- Saturación moderada; piel luminosa. Ligero bloom en las luces (lámpara) [SUPOSICIÓN].
- Sin viñeta fija (bordes izq./der. a 163/206 de luminancia vs. 182 en el centro).
- Paleta de grafismos (la del referente, por indicación del cliente): blanco `#FFFFFF`,
  amarillo de acento `#FCF210`, escala verde→rojo de la barra (ver §4).
- Nuestro material (iPhone, luz de día fría): se calienta con un ajuste ligero
  (temperatura +, sombras sin levantar) para acercarlo a esa media.

## 8. Sonido

### Niveles
- **Voz**: −18.5 dBFS RMS de media, picos a −9.8 dBFS. Limpia, seca, sin reverb.
- **Música**: cama continua de principio a fin, a **−36 a −40 dBFS RMS** en los silencios
  → **~18–22 dB por debajo de la voz**. Tímbrica cálida (centroide espectral 750–900 Hz),
  notas sostenidas, sin percusión brillante [SUPOSICIÓN: piano/pads tipo lo-fi suave].
  No está en los packs de SFX.
- **SFX**: ~8–10 dB por debajo de la voz [SUPOSICIÓN: deducido de la correlación ≈ 0.4 con
  la voz encima]. Nunca tapan una palabra.
- Final: música y voz bajan juntas a −41 dB en el fundido de 1.7 s.

### Qué SFX usa y cuándo (identificados en el pack con correlación cruzada)
| SFX (archivo del pack 1) | Dónde aparece en el referente | Función → regla |
|---|---|---|
| `Swoosh 01 - 04.wav` / `Swoosh 01 - 05.wav` | 5.7, 17.5, 24.6, 30.2, 39.0, 46.4, 51.1 s (r = 0.37–0.42, confirmado en espectrograma: barrido de ruido 2–12 kHz) | **Cada vez que salta el halo de color / punch-in** → swoosh corto (0.21–0.30 s) |
| `Pop up SFX.mp3` | 3.7, 13.4, 23.5, 30.3, 39.3 s (r = 0.27–0.40) | **Entrada de un texto/etiqueta o llegada del puntero a la nota** → pop |
| `Sub Bass Drop 3.wav` | 0.75 s (r = 0.30, plantilla de 2 s, z = 34) | **Palabra clave + icono del hook** → golpe grave suave, una sola vez |
| `Tecla.mp3` | 21.8, 29.7 s (r ≈ 0.30) [SUPOSICIÓN: confianza media] | **Pasos del puntero** / microacentos → tic suave |
| `CENSORED SOUND EFFECT.mp3` | 54.4–55.3 s (r = 0.99, coincidencia exacta) | Pitido de censura en el remate → no aplica a nuestro guion |
| `Resaltador highlighter Sound Effect.m4a` | 4.0 s (tramo largo, z = 27) [SUPOSICIÓN: confianza media] | **Aparición de la barra** → trazo suave |

- No hay risers, booms ni impactos cinematográficos (el pack 2 completo dio 0 coincidencias).
- Densidad: **~1 SFX cada 4–5 s**, siempre ligado a un movimiento gráfico. Nunca SFX en un
  corte "normal" de plano.

## 9. Adaptación a la marca SLATE (manual de branding + guía del cliente)

- **Tipografías y colores del grafismo = los del referente** (indicación explícita del
  cliente). Del manual se usa: el **logotipo SLATE** (recuadro + letras) en el cierre y la
  sensación general clean / premium.
- Paleta del manual (referencia, no se usa en textos): salvia `#7F9369`, salvia claro
  `#9DB37F`, marrón `#6B3E22`, beige `#E7C9A8`, blanco, azul noche `#152A36`.
- **Nada tapa la cara** de quien habla: todo texto/gráfico se coloca por debajo de la
  barbilla o en zonas sin rostro, calculado con detección de cara por toma.
- **Sin emojis** en pantalla (se sustituyen por iconos vectoriales finos).
- Menos es más: **máx. 2 elementos gráficos** a la vez en pantalla.

---

## 10. Correcciones aprobadas por el cliente

> Aquí se añaden, con fecha, las correcciones que el cliente apruebe, para que se queden
> como regla en las próximas ediciones.
