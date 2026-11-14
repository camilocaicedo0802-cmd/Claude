# Estilo · Referente Grow (`referencia_grow/referente_grow.mp4`)

Análisis del video de referencia (20,2 s, 720×1280, 30 fps, AAC 44,1 kHz).
Material extraído con ffmpeg en `referencia_grow/`: `frames2fps/` (40 fotogramas, 2 por segundo), `cortes/` (16 fotogramas en cada cambio de plano, umbral de escena 0,25), `audio.wav` y la separación voz / música+SFX en `sep/htdemucs/audio/` (Demucs).
Las medidas en px están **pasadas a 1080×1920** (×1,5 sobre el original). Lo marcado con **[SUPOSICIÓN]** no se puede medir con certeza.

---

## 1. Estructura y ritmo de cortes

Cambios de plano detectados (s): 0,07 · 0,93 · 1,60 · 2,20 · 2,80 · 4,30 · 5,73 · 7,63 · 10,80 · 11,40 · 13,33 · 15,57 · 16,53.

| Tramo (s) | Duración | Plano | Texto en pantalla |
|---|---|---|---|
| 0,00–0,93 | 0,93 | Persona sentada de cuerpo entero en **estudio de color liso** (rojo, ciclorama con viñeta) | Gancho palabra a palabra **alrededor de la cabeza**: «hay / algo / que / nadie / me dijo.» |
| 0,93–1,60 | 0,67 | **Avatar 3D** tipo Pixar de la persona con portátil, **fondo blanco** | «cuando» pequeño + «COMENCÉ» gigante condensado gris **detrás del avatar** |
| 1,60–2,20 | 0,60 | **Lámina de color a pantalla completa** (rojo) sin persona | «EDITAR» / «VIDEOS» gigantes, blancos con resplandor |
| 2,20–2,80 | 0,60 | Persona pequeña en **escenario oscuro con foco cenital** (círculo de luz en el suelo) | «cómo» pequeño + «COLOCAR» gigante rojo **detrás de la persona** |
| 2,80–4,30 | 1,50 | Plano medio de la persona trabajando en su escritorio (fondo naranja, softbox) | Subtítulo de 2 líneas a la izquierda: «subtítulos» (blanco) / «automáticos» (azul claro) |
| 4,30–5,73 | 1,43 | **Estudio blanco 3D** con la palabra «SUBTITULOS» repetida en **letras 3D extruidas que vuelan** alrededor; cámara orbitando | (las propias letras 3D) |
| 5,73–7,63 | 1,90 | **Buscador de Google** sobre gris #343434, la caja de búsqueda **curvada en 3D**; se escribe la marca y salen sugerencias | (la interfaz) |
| 7,63–16,53 | 8,90 | **Grabación de pantalla** de la herramienta con zooms que siguen al cursor; cortes internos en 10,80 · 11,40 · 13,33 · 15,57 | (la interfaz) |
| 16,53–20,20 | 3,67 | Plano medio en el escritorio, **imagen oscurecida ≈ −40 %** | **Una palabra cada vez**, centrada |

- **Primeros 7,6 s: un plano cada 0,6–1,9 s (media 1,1 s)**; después, un bloque largo de demostración (8,9 s) y un cierre hablado (3,7 s).
- La voz es continua (voz en off); los planos cambian sobre la voz, no esperan a pausas.
- Cada escena es un **lugar distinto** (estudio rojo, blanco, escenario oscuro, despacho, estudio 3D, interfaz).

## 2. Subtítulos

Hay **tres familias de texto**:

### 2.1 Palabras del gancho alrededor de la cabeza (0–0,93 s)
| Parámetro | Valor |
|---|---|
| Fuente | Grotesca negrita tipo **Helvetica Neue Bold** — [SUPOSICIÓN] alternativa libre: **Inter Bold** |
| Caja | minúsculas, interletrado −0,03 em |
| Tamaños | «hay» ≈ 110 px · «algo» ≈ 130 px · «que» ≈ 60 px · «nadie» ≈ 100 px · «me dijo.» ≈ 125 px |
| Posición | Dispersas alrededor de la cabeza: «hay» arriba-izquierda (centro x 406, y 470), «algo» debajo, a la izquierda y **detrás de la cabeza** (la cabeza tapa parte de la «o»), «que» pequeño a la derecha de la cabeza, «nadie» a la derecha (x 882, y 663), «me dijo.» sobre el pecho (x 608, y 982) |
| Color | Blanco #FFFFFF |
| Textura | **Resplandor blanco** suave en todas; **muy fuerte en la última** («me dijo.»): halo ≈ 30–40 px |
| Animación | Una palabra por sílaba tónica: aparece en **3–4 fotogramas** con fundido + desenfoque (las primeras se ven rosadas/transparentes al entrar); «me dijo.» entra de golpe con el destello |
| Entrada del plano | f0–1 fondo vacío · **f2–5 silueta blanca de la persona** (máscara en blanco puro) · f6–7 fondo vacío · f8 aparece la persona. Al final, **destello blanco** (f28–29) que funde al plano siguiente |

### 2.2 Subtítulo de dos líneas (2,80–4,30 s)
| Parámetro | Valor |
|---|---|
| Fuente | Helvetica Neue Bold [SUPOSICIÓN] → Inter Bold |
| Tamaño | ≈ 60 px (alto de «subtítulos» 56 px con ascendentes) |
| Posición | **A la izquierda del sujeto**, centro de la 1.ª línea x 352, y 896; 2.ª línea desplazada **+110 px a la derecha**, y 959 |
| Colores | 1.ª línea blanco; **2.ª línea azul claro #7FC7D8** |
| Palabras por bloque | 1 por línea, 2 líneas |
| Animación | Cada palabra entra con fundido + desenfoque en 3–4 fotogramas y una pequeña revelación de izquierda a derecha |
| Sombra | Sombra suave oscura, sin caja |

### 2.3 Una palabra cada vez (16,53–20,2 s)
| Parámetro | Valor |
|---|---|
| Fuente | Helvetica Neue Bold [SUPOSICIÓN] → Inter Bold |
| Tamaño | **Variable según la importancia**: palabras de relleno 45–55 px («y», «te», «el», «solo») · normales 70 px («Captions», «comenta») · destacadas **95–110 px** («quieres», «esta», «"si"») |
| Posición | **Centro** de la pantalla (x ≈ 520, y ≈ 940–960) |
| Color | Blanco; algunas destacadas con un **tinte azul claro** («esta») |
| Palabras por bloque | **1** (a veces 2 apiladas: «esta / herramienta») |
| Animación | La palabra nueva aparece en el centro; la anterior **sube y se desvanece** (se ven las dos superpuestas 2–3 fotogramas, «tú» encima de «quieres») |
| Fondo | Video oscurecido ≈ −40 % para que mande el texto |

## 3. Títulos gigantes condensados

| Parámetro | Valor |
|---|---|
| Fuente | Sans **ultracondensada** en MAYÚSCULAS. «COMENCÉ» y «COLOCAR»: cada letra ≈ 0,27 × su altura (súper estrecha); «EDITAR»: ≈ 0,52 × altura — [SUPOSICIÓN] **League Gothic** (eje de anchura) para las súper estrechas y **Anton** para «EDITAR VIDEOS» |
| Tamaños | «COMENCÉ» alto 435 px (≈ 70 % del ancho, 750 px) · «COLOCAR» alto 400 px (ancho 717) · «EDITAR» alto 262 px (ancho 822) |
| Acompañante | Palabra pequeña en minúsculas encima, alineada a la izquierda del bloque: «cuando», «cómo» (≈ 50–55 px, Helvetica Bold) |
| Profundidad | **Detrás de la persona / avatar** (la cabeza tapa el centro de la palabra) |
| Colores | Gris oscuro **#4E4A4B** sobre fondo blanco · **rojo #DE0004 con resplandor rojo** sobre escenario oscuro · **blanco con resplandor blanco** sobre lámina roja |
| Animación | La pequeña entra primero (fundido con desenfoque, o **giro 3D** con desenfoque de movimiento en «cuando»: entra girando desde arriba a la izquierda en 5 fotogramas); la gigante aparece **de golpe** 4–8 fotogramas después |
| Lámina «EDITAR VIDEOS» | Fondo rojo **#AF0003** con centro más claro (degradado radial); palabras en 2 líneas que entran **de golpe** una tras otra (0,23 s de separación), con ligera perspectiva y empuje de cámara (escala +3 %) |

## 4. Otros textos y motion graphics
- **Palabras 3D voladoras** (4,30–5,73 s): la palabra clave («SUBTITULOS») repetida 40–60 veces en **letras 3D extruidas gris metálico**, a distintas profundidades y giros, con desenfoque de movimiento; **la cámara orbita ≈ 90°** alrededor de la persona sentada en el centro; fondo estudio blanco #E8EDF1 con suelo infinito.
- **Buscador** (5,73–7,63 s): fondo gris **#343434**, logo «Google» blanco centrado arriba (y ≈ 330), caja de búsqueda blanca redondeada (radio ≈ 24 px), **curvada y en perspectiva** (como una pantalla doblada que gira hacia la cámara); se escribe la marca letra a letra y se despliegan 8–9 sugerencias con iconos.
- **Grabación de pantalla** (7,63–16,53 s): interfaz real de la herramienta sobre blanco; **zooms de 1,5–2,5×** que siguen al cursor (menús, paletas de color, plantillas), cortes cada 1–3 s.

## 5. B-roll
- No usa B-roll de stock: cada escena es un **escenario distinto** de la misma persona (IA) o una **grabación de pantalla** del producto.
- Al adaptarlo: escenarios = **recorte de la persona** sobre fondos generados (estudio de color, escenario con foco, estudio blanco 3D); demostración = **grabación de pantalla** o maqueta de interfaz; B-roll de stock solo en frases que lo pidan.

## 6. Transiciones
| Tipo | Dónde | Detalle |
|---|---|---|
| **Corte seco** | La mayoría | Sin efecto, sobre la voz |
| **Destello blanco** | Gancho → avatar (0,93 s) | 2 fotogramas a blanco y el plano nuevo aparece desde blanco (fundido 8 fotogramas) |
| **Silueta blanca** | Arranque | La persona aparece primero como silueta blanca 4 fotogramas |
| Golpe de zoom con whoosh | 4,30 (estudio 3D), 7,63 y 10,0 (grabación de pantalla) | Corte con whoosh fuerte |

## 7. Zooms y movimiento
- Empuje lento constante en los planos (escala +3–5 % por plano).
- Escenario con foco y estudio 3D: **cámara orbitando / acercándose**.
- Grabación de pantalla: **zoom 1,5–2,5× al punto de interés** con desplazamiento suave (≈ 10 fotogramas).

## 8. Color
- Paleta muy saturada por escena: rojo #AF0003–#DE0004, naranja del despacho, azul noche del escenario, blanco del estudio 3D, gris #343434 de la interfaz; acento secundario azul claro #7FC7D8.
- Último tramo oscurecido ≈ −40 %.
- **Adaptación a la marca (estilo.md §10.1 y §10.4)**: los rojos pasan a los **morados del logo** (#B701FC / #9601FD / #7600FC), el azul claro a **lavanda #C7A6FF**; **no se etaloniza** el material grabado (los colores van en fondos y textos).

## 9. Sonido
| Pista | Sonoridad |
|---|---|
| Mezcla final | **−14,6 LUFS** |
| Voz | −15,2 LUFS |
| Música + SFX | **−24,5 LUFS (≈ 9 dB por debajo de la voz)** |

- **Música**: base trap/hip-hop **≈ 140 BPM** (medio tiempo 70), energía constante (−22 dB RMS muy estable, muy comprimida). **Corte en seco de la música de 13,70 a 14,45 s** (silencio bajo la voz) y vuelve con un golpe de bajo.
- **SFX identificados** (correlación cruzada de la pista sin voz contra el paquete de SFX del cliente, `referencia_grow/sfx_match.json`):

| Tiempo (s) | Momento | SFX | Archivo del paquete | Coincidencia |
|---|---|---|---|---|
| 0,09 | Arranque (silueta blanca) | Clic | `clicks/Lighter Double Click 01.wav` / `clicks/Mouse Click 02.wav` | 0,33 / 0,25 |
| 4,3–4,5 | Corte al estudio 3D | Whoosh | [SUPOSICIÓN] `pack1/Woosh Effect 4.wav` | débil |
| 7,55 | Entra la grabación de pantalla | Whoosh corto | **`pack1/VS_Short Whoosh 3.mp3`** (+ `VS_Short Whoosh 2`) | **0,47** |
| 9,97 | Golpe fuerte en la demostración | Whoosh | **`whoosh/Woosh Effect 10.wav`** | **0,53** |
| 13,62 | Antes del corte de música | Whoosh | **`whoosh/Woosh Effect 8.wav`** | 0,42 |
| 14,57 | Vuelve la música | Golpe de bajo | `pack1/Deep Bass Hit 2.wav` | 0,33 |
| 17,45 | Cierre | Golpe sub | `pack1/Sub Bass Hit.wav` | 0,36 |

- **Textos con sonido de tecleo** (indicación del cliente): cada palabra/título que entra suena con `Escribir teclado.mp3` / `Type Digital SFX.wav` / `Tecla.mp3` (cortos, −14 dB respecto a la voz).
