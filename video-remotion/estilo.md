# estilo.md — Guía de edición (referencia: "Video de referencia Glow")

Fuente del análisis: `referencia/referencia.mp4` (720×1280, 24 fps, 30,0 s, AAC 44,1 kHz estéreo).
Material extraído: `referencia/frames_2fps/` (60 fotogramas), `referencia/frames_cortes/` (cambios de plano),
`referencia/audio.wav`, separación voz/fondo con Demucs en `referencia/sep/`, transcripción por palabra en
`referencia/ref_words.json`.

Todas las medidas están convertidas a **nuestro lienzo: 1080×1920 px, 30 fps** (factor ×1,5 respecto a la referencia).
Lo que no se puede medir con certeza va marcado con **[SUPOSICIÓN]**.

---

## 1. Formato y ritmo general

| Parámetro | Valor |
|---|---|
| Duración | 30 s (85 palabras habladas → **2,9 palabras/s**) |
| Pausas de voz | Ninguna mayor de 0,25 s: todas las pausas se cortan (jump cuts) |
| Escenas distintas | 14 en 30 s → **una escena nueva cada 2,1 s** de media |
| Cambio visual (corte, zoom, texto, overlay) | **cada 0,8–1,5 s**; nunca más de 2,5 s sin que algo cambie |
| Plano más largo sin corte | 3,4 s (17,83 → 21,25), y aun así lleva un "golpe" de mano a cámara en 18,6 s |
| Escena más corta | 0,1–0,4 s (micro-cortes de la transición del móvil, 11,79 → 12,12) |

### Mapa de la referencia (para copiar la estructura)

| Tiempo | Qué pasa | Recurso |
|---|---|---|
| 0,00–2,92 | Gancho. Plano general en escritorio rojo. Título 2 líneas "no te quedarás / viendo este video" → "porque tengo / el pelo rojo" | Zoom-in animado 1,0→1,9 s, título palabra a palabra, música corta en seco en 2,05 s |
| 2,92–4,21 | Plano general desde otro ángulo | Subtítulo pequeño |
| 4,21–6,21 | **B-roll**: detrás de cámaras (equipo, cámara, luces) | Título "match / perfecto" (blanco / rojo) |
| 6,21–8,38 | Primer plano hablando | Subtítulo pequeño, salto de encuadre (punch-in) |
| 8,38–10,40 | Plano medio + **overlay HUD** (esquinas de visor, arcos, números) con eco/estela | SFX digitales (pitidos agudos) |
| 10,40–11,79 | El video se encoge dentro de un **móvil sostenido por una mano**; la mano lo retira | Barrido con desenfoque de movimiento + flash blanco 6 fotogramas |
| 11,79–13,60 | **Collage** de miniaturas de video + persona en B/N | Título "y tú aún / sigues aquí" (blanco / rojo) |
| 13,60–13,70 | Transición desenfoque (defocus) | Whoosh |
| 13,70–16,00 | Nueva localización (césped) | Título 3 líneas "creamos / videos / publicitarios" (cromado / rojo / cromado) **detrás de la cabeza** |
| 16,00–16,40 | Transición zoom radial con desenfoque | Whoosh + golpe de bajo |
| 16,40–17,83 | **Composición surrealista**: recortes gigantes de la misma persona mirando el móvil alrededor del set pequeño | Título "que la gente / termina / de ver" en perspectiva |
| 17,83–21,25 | Contrapicado con laptop en primer término; mano a cámara en 18,6 s | Subtítulo pequeño; riser 20,0→21,2 |
| 21,25–23,29 | Mano tapa el lente (transición práctica), lámpara vuela, flash blanco | Golpe + whoosh |
| 23,29–26,54 | **Motion graphic** fondo negro con cuadrícula: ventanas tipo macOS con recortes B/N de ojos y boca; título "CEREBRO"; nota escribiéndose "Captar la atención con videos que venden" | SFX teclado (confirmado) |
| 26,54–28,62 | Fondo blanco, recorte de la persona sentada sobre una cabeza gigante; **logo** + "podemos hacerlo / para / tu / marca" palabra a palabra | Golpe en el corte |
| 28,62–30,00 | Plano final (playa), título gigante "CONTA / CTANOS" (rojo / cromado) con estela | Golpe + whoosh |

---

## 2. Subtítulos (texto pequeño, sincronizado palabra a palabra)

| Parámetro | Valor |
|---|---|
| Fuente | **Outfit SemiBold (600)** — [SUPOSICIÓN] la original parece Gilroy SemiBold; Outfit es la alternativa libre más parecida (comparada contra 20 fuentes en `scratchpad/fontcmp_sub.jpg`) |
| Tamaño | **36 px** (en la referencia 24 px sobre 720) |
| Interletrado | −0,02 em |
| Color | Blanco cálido **#FFF5F4** |
| Sombra | `0 2px 8px rgba(0,0,0,0.45)` — sin caja ni contorno |
| Posición | Centrado horizontal; **centro vertical en y = 950 px (49,5 % de la altura)**, a la altura del pecho |
| Palabras por bloque | **1–4 (media 2)**; se corta el bloque en comas y puntos ("Si no," / "porque rompimos" / "el patrón.") |
| Mayúsculas | Como se habla (minúscula salvo inicio de frase y números: "El 96%") |
| Números | En cifra: "96%", "3 segundos" |
| Animación de entrada | Aparece el bloque entero en el inicio de su primera palabra: opacidad 0→1 y escala 0,92→1 en **4 fotogramas** [SUPOSICIÓN: a 24 fps no se distingue entre 3 y 5 fotogramas] |
| Animación de salida | Corte seco al siguiente bloque |
| Palabra activa | No cambia de color en el subtítulo pequeño. El énfasis va en los **títulos grandes** (sección 3) |
| Convivencia con títulos | **Mientras hay un título grande en pantalla, el subtítulo pequeño se oculta** (no se duplica el texto) |

---

## 3. Títulos / palabras destacadas (texto grande)

Aparecen en el **25–35 % del tiempo total** (8 apariciones en 30 s, una cada ~3,5 s), siempre sobre la frase clave.

| Parámetro | Valor |
|---|---|
| Fuente | **Outfit ExtraBold (800)** en minúsculas; **Outfit Black (900)** en MAYÚSCULAS ("CEREBRO", "CONTACTANOS") — [SUPOSICIÓN] original ≈ Gilroy ExtraBold/Black |
| Interletrado | **−0,05 em** (muy apretado) |
| Interlineado | **0,88** (líneas casi pegadas) |
| Tamaños medidos | Gancho línea 1: **60 px** · títulos normales: **105–130 px** · palabra central destacada ("videos", "termina"): **150–165 px** · cierre MAYÚSCULAS: **225 px** |
| Ancho | 40–72 % del ancho de pantalla (430–780 px) |
| Líneas | 2 o 3. Se puede partir una palabra en dos líneas si queda más gráfico ("CONTA / CTANOS") |
| Combinación de color | Siempre **dos tonos alternos**: blanco + rojo, o cromado + rojo + cromado. La palabra clave va en rojo |
| Posición | En el aire libre del encuadre: **tercio superior (y = 420–700 px)** sobre la cabeza, o **a la altura del pecho/escritorio (y = 1000–1300 px)**. Nunca tapa ojos ni boca |
| Profundidad | En 1 de cada 3 títulos el texto va **detrás de la persona** (recorte del sujeto por encima del texto) |
| Perspectiva | Ocasional: inclinación 3D `rotateX 18–25°` ("termina de ver") |

### Texturas de los títulos
- **Blanco con resplandor**: relleno #FFFFFF + glow blanco `0 0 14px rgba(255,255,255,0.55)` + `0 0 40px rgba(255,255,255,0.25)`.
- **Rojo**: relleno **#D32425**, sombra interior/exterior roja oscura `0 3px 0 #8E1410` y halo `0 0 18px rgba(211,36,37,0.45)`.
- **Cromado/plateado**: degradado vertical `#F5F5F5 → #9C9C9C (55 %) → #E6E6E6`, borde 1 px #FFFFFF al 40 %, ligera desenfoque de 0,5 px.
- **Rojo oscuro de cierre** (MAYÚSCULAS): #A6150F con brillo superior #D32425.

### Animación de los títulos
- **Palabra a palabra**, sincronizada con el inicio de cada palabra hablada (Whisper).
- Entrada de cada palabra: desenfoque 18 px→0, opacidad 0→1, escala 1,25→1 y desplazamiento 40 px→0 en **6 fotogramas**, curva `Easing.bezier(0.16, 1, 0.3, 1)`; estela de movimiento (motion blur) en la dirección de entrada.
- Mientras está en pantalla: deriva lenta escala 1,00→1,04.
- Salida: desenfoque 0→16 px + opacidad 1→0 en **5 fotogramas**, o corte seco si cambia la escena.
- Cada palabra destacada que entra lleva **SFX** (sección 8).

---

## 4. Otros textos en pantalla
- **Nota tipo macOS** (motion graphic): ventana gris oscuro #1E1E1E al 92 %, radio 18 px, tres puntos rojo/amarillo/verde (#FF5F57 / #FEBC2E / #28C840), barra de herramientas con iconos grises, texto Outfit Medium 30 px blanco que se **escribe letra a letra** (≈ 18 caracteres/s) con cursor; fecha en gris #8A8A8A 18 px.
- **Etiquetas HUD**: números de coordenadas tipo `-79.1913972` en monoespaciada blanca al 50 %, 18 px.
- **Cierre de marca**: logo centrado arriba (y ≈ 520 px, ancho ≈ 330 px) y frase en Outfit Medium 34 px gris #4A4A4A, **palabras sueltas apareciendo en posiciones distintas** ("podemos hacerlo" / "para" / "tu" / "marca"), una cada 0,25 s.

---

## 5. B-roll y motion graphics
Proporción: **≈ 55 % hablando a cámara / 45 % B-roll + motion graphics**. Nunca más de **4 s seguidos** de busto parlante sin recurso.

| Tipo | Duración | Cómo se ve |
|---|---|---|
| Detrás de cámaras real | 2,0 s | Equipo, cámara de cine, luces; título encima |
| Móvil sostenido por una mano | 1,4 s | El video sigue reproduciéndose dentro de la pantalla del teléfono (marco negro, esquinas 60 px) |
| Collage de miniaturas | 1,8 s | Cuadrícula de 6–9 videos/fotos que se desplazan en paralaje; persona protagonista en **B/N** delante |
| Composición surrealista | 1,4 s | La persona repetida en recortes gigantes alrededor del set |
| Motion graphic "cerebro" | 3,25 s | Fondo **#0B0B0B** + cuadrícula gris #2A2A2A (celdas de 90 px, líneas de 1 px) + cuadrados sueltos #3A3A3A; ventanas con foto **B/N** de ojos/boca, borde blanco 8 px, sombra `0 20px 50px rgba(0,0,0,0.6)`, flotando en paralaje (±20 px) |
| Recorte sobre fondo blanco | 2,1 s | Fondo **#F2F2F2**, persona recortada con sombra suave, logo y palabras sueltas |
| Overlay HUD | 1,0 s | Esquinas de visor (corchetes de 40 px, línea 2 px blanca al 60 %), arcos de círculo de 600 px, números; eco/estela de 3 copias al 30 % |

Regla: el B-roll **ilustra literalmente la frase** que se está diciendo (pelo rojo → plano del pelo, "set" → detrás de cámaras, "hace scroll" → móvil, "cerebro" → gráfico de cerebro/ojos).

---

## 6. Transiciones (por orden de frecuencia)
1. **Corte seco / jump cut** — 60 % de los cambios.
2. **Punch-in**: alternar encuadre abierto (escala 1,0) y cerrado (escala 1,35–1,5) entre tomas consecutivas del mismo plano.
3. **Flash blanco**: 4–6 fotogramas, opacidad 0→1→0 (11,5 s y 23,0 s).
4. **Desenfoque (defocus) dissolve**: desenfoque 0→30 px→0 en 6 fotogramas (13,6 s).
5. **Zoom radial con desenfoque**: escala 1→1,6 + desenfoque radial en 8–10 fotogramas (16,0 s).
6. **Barrido con desenfoque de movimiento** (whip/smear) horizontal en 4 fotogramas (10,4 s).
7. **Transición práctica con la mano** al lente (18,6 s y 21,3 s) — necesita grabarse; si no existe, se sustituye por un *wipe* con desenfoque.
8. **Eco/estela** (3 copias desplazadas al 30 %) durante el HUD.

Cada transición que no es corte seco lleva **whoosh** (o riser + golpe si es un cambio de bloque).

---

## 7. Zooms y movimiento
- **Zoom-in animado del gancho**: escala 1,00→1,45 entre 1,0 y 1,9 s, curva `Easing.bezier(0.65, 0, 0.35, 1)`.
- **Deriva lenta en planos hablados**: escala +4 % a lo largo del plano (1,00→1,04) [SUPOSICIÓN: puede ser movimiento de cámara real].
- **Punch-in** en el corte entre frases: ver transición 2.
- Textos y ventanas siempre en movimiento suave (deriva de 10–20 px o escala +4 %); nada queda totalmente quieto.

---

## 8. Sonido

### Niveles (medidos con EBU R128 sobre las pistas separadas)
| Pista | Sonoridad |
|---|---|
| Voz | **−14,5 LUFS** |
| Música + SFX | **−23,4 LUFS** (≈ **9 dB por debajo de la voz**) |
| Mezcla final | **−14,0 LUFS integrado** |

### Música [SUPOSICIÓN en estilo]
- 0–7 s: base de hip-hop/trap con bombo marcado, **≈ 94 BPM** (golpes cada 0,64 s).
- **Corte en seco de la música 0,1 s en 2,05 s**, justo después del remate del gancho ("…pelo rojo").
- 7–30 s: sección melódica con sintetizadores/pads, más suave, sin bombo marcado.
- La música no se nota bajo la voz; sube solo en transiciones.

### Efectos de sonido detectados
Comparé los 140 SFX del paquete de Drive contra la pista sin voz (correlación cruzada, `referencia/sfx_match_novox.json`).
**Confirmado** = coincidencia clara; **probable** = mismo tipo de sonido y momento, coincidencia débil.

| Tiempo | Evento visual | SFX | Archivo del paquete |
|---|---|---|---|
| 0,9–1,0 | Entra el título del gancho | Whoosh corto | `VS_Short Whoosh 2.mp3` / `VS_Short Whoosh 6.mp3` / `SWHOOSH.mp3` (probable, 0,38–0,43) |
| 2,05 | Remate del gancho | Corte de música (silencio) | — |
| 4,2–6,4 | B-roll + "match perfecto" | Whooshes cortos en cada palabra | `VS_Short Whoosh 2.mp3`, `Standard Swoosh.wav` (probable, 0,37–0,40) |
| 9,4–11,0 | Overlay HUD | Pitidos digitales agudos + barrido ascendente | `Type Digital SFX.wav` / `8-bit Game digital typing.wav` [SUPOSICIÓN] |
| 11,5–11,8 | Flash blanco del móvil | Golpe + whoosh | `Woosh Effect 5.wav` + `Sub Bass Hit.wav` [SUPOSICIÓN] |
| 13,6 | Transición desenfoque | Whoosh | `Woosh Effect 8.wav` (probable, 0,31) |
| 15,4 | Entra "videos" | Pop | `Pop up SFX.mp3` (probable, 0,21) |
| 16,1 | Zoom radial | Golpe de bajo | `Sub Bass Hit.wav` (probable, 0,28) |
| 18,6 | Mano a cámara | Whoosh / chasquido | `MA_CineTransitions_TumblingRocksWhoosh2_004.wav` / `Camera Flash.mp3` (probable, 0,33–0,37) |
| 20,0–21,2 | Antes de tapar el lente | **Riser** | `RISER.mp3` (probable, 0,34) |
| 21,1–21,3 | Mano tapa el lente | Golpe de bajo | `Sub Bass Hit.wav` (probable, 0,27) |
| 23,3 | Corte a "CEREBRO" | Golpe | `Sub Bass Hit.wav` [SUPOSICIÓN] |
| 24,5–26,0 | Nota escribiéndose | **Teclado** | **`Escribir teclado.mp3` (confirmado, 0,52)** + `Tecla.mp3` (0,43) |
| 26,5 | Corte a fondo blanco | Golpe | `Sub Bass Hit.wav` [SUPOSICIÓN] |
| 28,6–29,0 | "CONTACTANOS" | Golpe + whoosh | `VS_Short Whoosh 4.mp3` (probable, 0,36) |

Reglas de SFX:
- **Cada palabra destacada que entra = whoosh corto** (−12 dB respecto a la voz).
- **Cada cambio de bloque/escena con transición = whoosh + golpe de bajo** (golpe −10 dB).
- **Antes de un momento fuerte = riser de 1,2 s** que termina justo en el corte.
- **Texto que se escribe = teclado**; **UI/HUD = sonidos digitales**.
- Máximo **1 SFX cada 0,5 s**; nunca dos whooshes encima.

---

## 9. Color
> ⚠️ **Sustituido por §10.1**: los acentos van en el blanco y los morados del logo, no en rojo. Lo de abajo describe la referencia original.

| Elemento | Valor |
|---|---|
| Rojo principal (títulos, acentos) | **#D32425** |
| Rojo oscuro (MAYÚSCULAS, sombras de texto) | **#A6150F** / **#8E1410** |
| Rojo del set (escritorio, laptop) | #9D2B2C |
| Blanco texto | #FFFFFF (títulos) / #FFF5F4 (subtítulos) |
| Negro motion graphics | #0B0B0B |
| Gris cuadrícula | #2A2A2A / #3A3A3A |
| Fondo claro de cierre | #F2F2F2 |
| Cromado | #F5F5F5 → #9C9C9C → #E6E6E6 |

**Etalonaje medido** (medias por zona de luminancia):
- Sombras cálidas y algo levantadas: RGB ≈ (33, 29, 22), nunca negro puro.
- Medios ligeramente verdosos/neutros: ≈ (110, 115, 95).
- Altas luces frías y suaves: ≈ (215, 220, 200), sin quemar.
- Saturación general media-baja (~30/255) **salvo el rojo, que va muy saturado** → look "rojo selectivo" cinematográfico.
- Las escenas de motion graphics y collage usan la persona en **blanco y negro** para que solo destaque el rojo.

---

## 10. Registro de correcciones del usuario
*(Cada corrección que apruebes se añade aquí y se aplica a los siguientes videos. **Estas reglas mandan sobre las secciones anteriores.**)*

### 10.1 Color: se usan los colores del logo, no el rojo de la referencia (13/11/2026)
- **Nada en rojo.** Los acentos (palabra destacada, tachados, HUD, cursor, botones) usan **el blanco y los morados de la "W" del logo GROW**.
- Valores medidos sobre el PNG del logo:

| Uso | Valor |
|---|---|
| Blanco | **#FFFFFF** (subtítulos #FFF5F4) |
| Morado claro (parte alta de la W) | **#B701FC** |
| Morado medio | **#9601FD** |
| Morado profundo (parte baja de la W) | **#7600FC** |
| Degradado de acento (como la W) | `linear-gradient(180deg, #B701FC 0%, #9601FD 50%, #7600FC 100%)` |
| Sombra de texto morado | #3D0080 (desplazada 3 px hacia abajo) |
| Halo morado | rgba(150, 1, 253, 0.5), desenfoque 16–22 px |

- La palabra destacada de cada título va con **el degradado vertical de la W** (relleno con `background-clip: text`), no en color plano.
- Se mantienen de la referencia: negro #0B0B0B y grises de cuadrícula para motion graphics, y el cromado, que pasa a ser blanco plateado (#FFFFFF → #ECECEC → #BDBDBD → #F4F4F4).
- Las escenas en blanco y negro siguen igual; ahora lo único con color en ellas es el morado.
