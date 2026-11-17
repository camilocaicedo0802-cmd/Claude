# estilo.md — Guía de estilo extraída de `referencia.mp4`

Fuente: `referencia.mp4` · 1080×1920 · 30 fps · 39,2 s · H.264 + AAC 44,1 kHz estéreo.
Método: 78 fotogramas a 2 fps + 19 fotogramas en cambios de plano (umbral de escena 0,25) + tiras a 30 fps en los momentos clave + transcripción Whisper large-v3 con tiempos por palabra + espectrograma y correlación de audio contra la carpeta de SFX.
Todas las coordenadas en píxeles sobre el lienzo de 1080×1920. Todo lo que no se puede medir directamente está marcado con **[SUPOSICIÓN]**.

---

## 1. Estructura y ritmo

| Tramo | Tiempo | Qué ocurre |
|---|---|---|
| Gancho hablado | 0,00–15,40 s | Presentador a cámara, subtítulos palabra a palabra, 3 palabras destacadas gigantes, 1 efecto neón, 2 tarjetas de foto |
| Montaje b-roll | 15,47–39,2 s | Detrás de cámaras, solo música, sin subtítulos, cortes al beat |

### Cortes medidos (s)
`0,00 · 1,97* · 2,87 · 12,13 · 15,47 · 17,03 · 19,03 · 20,53 · 22,00 · 23,00 · 25,03 · 27,00 · 29,00 · 31,03 · 32,53 · 34,03 · 35,03 · 36,53 · 38,03`
(*1,97 = entra el texto "PARA/GRABAR", no es corte de plano.)

- **Parte hablada**: plano medio-largo 0,00–2,87 s; plano general 2,87–12,13 s (9,3 s sin cortar, el ritmo lo sostienen los textos y gráficos); reencuadre a primer plano (punch-in ≈ 1,35×) en 12,13 s.
- **Regla de la parte hablada**: nunca pasan más de **~1,5 s** sin un evento visual nuevo (bloque de subtítulo, palabra destacada, icono, tarjeta, zoom o corte).
- **Montaje**: duración por plano **1,0 / 1,5 / 2,0 s** (media 1,7 s). Música a **120 BPM** (golpe cada 0,50 s); los 15 cortes caen a **≤ 0,07 s (≤ 2 fotogramas)** de un golpe → **se corta siempre al beat, cada 2, 3 o 4 tiempos**.
- La voz termina (15,2 s) y en 0,2 s entra la música a plena potencia con un destello de luz: el cambio de bloque se marca con **sonido + destello**, no con silencio.

---

## 2. Subtítulos (palabra a palabra)

| Parámetro | Valor |
|---|---|
| Fuente | **SF Pro Display Italic** (peso 400), la familia de la referencia (archivos del cliente). La cursiva regular no venía en el paquete: se genera inclinando 12° la Regular (`scripts/shear_font.py`), que es exactamente como Apple construye sus cursivas (todas las del paquete son oblicuas de −12°). Superpuesta sobre "para empezar" coincide letra a letra con interletraje 0 |
| Tamaño | **57 px** con SF Pro (medido: "para empezar" = 330 px de ancho) |
| Caja | minúsculas, tal cual se dice; sin puntuación |
| Color | **#FFFFFF**, 100 % opacidad |
| Textura | ninguna; solo sombra suave `0 2px 6px rgba(0,0,0,0.35)` **[SUPOSICIÓN]** (se intuye un halo oscuro mínimo) |
| Posición | centrado horizontal (x = 540), **centro vertical en y = 1228 px (64 % de la altura)**, igual en plano general y en primer plano |
| Palabras por bloque | **1–3** (media 2): "estamos" · "aquí listos" · "para" · "en este" · "nuevo lugar" · "que tenemos" · "para atender" · "cafecito" · "en la mañana" · "viene un cliente" · "west palm beach" · "el otro viene de" |
| Cambio de bloque | **corte seco**, sin animación de entrada ni de salida; el bloque nuevo aparece en el fotograma en que empieza su primera palabra (tiempo Whisper) |
| Palabra activa | no hay resaltado de color dentro del bloque; la "palabra destacada" se resuelve con los textos gigantes (§3) |
| Cuándo se ocultan | mientras hay una palabra destacada gigante en pantalla y en el montaje sin voz |

---

## 3. Palabras destacadas (textos gigantes) — **mismas texturas que la referencia**

Siempre son una pareja: **línea pequeña (kicker)** + **palabra grande**. Duración en pantalla: **1,0–1,3 s**. Frecuencia: 3 en 15 s (≈ una cada 2,5 s en el gancho).

| Momento | Kicker | Palabra | Posición |
|---|---|---|---|
| 0,25–1,75 s | "BUENOS" | "DÍAS" rojo | bloque alineado a la izquierda en x = 160; kicker y = 690–732; palabra y = 740–980 |
| 1,97–2,87 s | "PARA" | "GRABAR" blanco | kicker a la derecha (x = 560–830, y = 555–635); palabra a sangre, más ancha que el lienzo (1180 px), y = 690–880 |
| 4,85–5,75 s | "A NUESTROS" | "CLIENTES" rojo **detrás del presentador** | centrado; kicker y = 470–505; palabra y = 510–655 (a la altura de la cabeza) |

### Kicker
- **SF Pro Display Light** (300). "BUENOS" recto a **60 px** (Light recta derivada enderezando la Light Italic −12°); "PARA" y "A NUESTROS" en **Light Italic** (archivo original) a **100–113 px**.
- Mayúsculas, #FFFFFF, interletraje 0.
- Entrada: **3 fotogramas**, desliza **+40 px desde la izquierda** con opacidad 0→1 y desenfoque de movimiento 8→0 px.

### Palabra grande
- **SF Pro Display Black** (900), MAYÚSCULAS, interletraje **−0,055 em**, interlineado 0,9. La Black recta no venía en el paquete: se deriva enderezando la Black Italic (−12°); superpuesta sobre "CLIENTES" coincide letra a letra.
- Tamaño según ancho del bloque: **206 px** ("CLIENTES", 920 px de ancho), **341 px** ("DÍAS", 765 px), **~300 px** ("GRABAR", 1180 px, se sale del encuadre a propósito).
- **Textura ROJA** ("DÍAS", "CLIENTES"):
  - Color base **#E10000** (medido sobre pared blanca: RGB 225,0,0).
  - Dentro de las letras, el **vídeo del plano desplazado y posterizado a dos rojos**: claro **#FD4040** (253,64,64) y oscuro **#D70000** (215,0,0). Se ven siluetas del propio plano (camiseta, vaso) dentro de las letras.
  - **Glitch por bandas**: 3–6 franjas horizontales de 12–40 px de alto desplazadas ±6–18 px en X, que cambian cada 2–3 fotogramas (bordes con muescas rectangulares en la "S").
- **Textura BLANCA** ("GRABAR"): letras rellenas con el **vídeo en escala de grises aclarado** (blanco a gris claro #CFCFCF), con el mismo glitch por bandas.
- **Entrada**: aparición en 1–2 fotogramas con escala 1,08→1,00 (rojo) o **zoom-blur desde 1,25× con desenfoque 20→0 px en 4 fotogramas** (blanco).
- **Salida**: fundido 1,0→0,35 en 6 fotogramas y desaparece (en 1,50 s "DÍAS" se ve rosa translúcido) o con la transición de desenfoque del plano.
- **Detrás del sujeto**: "CLIENTES" queda tapado por la cabeza del presentador (recorte/matte del sujeto). Usarlo cuando la palabra coincide con la cabeza.

---

## 4. Motion graphics y elementos

1. **Neón verde trazado sobre objeto** (6,30–7,40 s, "cafecito en la mañana"):
   - Icono de línea (cohete) dibujado sobre la camiseta + el objeto que sostiene (el vaso) relleno de luz.
   - Color: núcleo **#9CFC8D**, brillo **#39FF14** (medido: mediana 134,222,114; p90 156,252,141). Grosor de trazo ≈ 8 px, halo `drop-shadow` 0 0 12 px y 0 0 28 px.
   - Entrada: trazo que se dibuja en 6–8 fotogramas; el icono sigue al sujeto (tracking) durante ~1,1 s; salida por fundido 4 fotogramas.
2. **Tarjetas de foto** (b-roll en ventana) para lugares nombrados ("West Palm Beach" 9,50–10,60 s; "Miami Beach" 11,30–12,10 s):
   - Foto real del lugar, vertical, **≈ 450–480 × 620–750 px**, **radio de esquina 36 px**, sin marco; bordes con ligero halo translúcido (efecto cristal).
   - Colocación: arriba, al lado de la cabeza (una a la derecha x ≈ 484–932, otra a la izquierda x ≈ 157–641), y ≈ 210–840. **Detrás del sujeto** (la mano y el vaso pasan por delante).
   - Entrada: fundido + desenfoque 12→0 px en ~12 fotogramas; salida: fundido 6 fotogramas o corte con la transición.
   - Sincronía: aparece 0,25 s antes de que se diga el nombre y dura lo que dura la frase.
3. **B-roll a pantalla completa** (montaje final): planos de detrás de cámaras del propio rodaje, cámara en mano con movimiento, 1,0–2,0 s cada uno, cortados al beat.

---

## 5. Transiciones

| Tipo | Dónde | Valores |
|---|---|---|
| **Desenfoque (blur)** | 2,87 s y 12,13 s | Plano saliente: desenfoque gaussiano 0→18 px en los **últimos 4 fotogramas** (con zoom 1,00→1,04). Plano entrante: empieza a 18 px y se enfoca a 0 en **6 fotogramas** |
| **Destello de luz (light leak)** | 15,40 s (entrada del montaje) | Destello **magenta/rosa (#FF4FD8 → blanco)** desde la esquina inferior izquierda; sube en 3 fotogramas, sobreexpone 2–3 y se va en 8 |
| **Corte seco al beat** | todo el montaje | sin efecto |
| **Punch-in** | 12,13 s | reencuadre ≈ 1,35× junto con el desenfoque |

---

## 6. Zooms y movimiento de cámara

- Parte hablada: **sin zoom continuo** en los planos largos; el dinamismo lo dan cortes de reencuadre (1,00× → 1,35×) en cambios de frase.
- En el plano general (2,87–12,13 s) se percibe un empuje lento [SUPOSICIÓN: ~1,00→1,05× en 9 s].
- B-roll: el movimiento lo pone la cámara en mano; no hay zooms digitales añadidos [SUPOSICIÓN].

---

## 7. Color

| Medida | Gancho (0–15 s) | Montaje (15–39 s) |
|---|---|---|
| Luminancia media | 0,45 | 0,55 |
| Percentil 5 / 99 | 0,00 / 0,98 | 0,00 / 0,98 |
| Blancos (RGB medio en luces > 0,75) | 0,85 / 0,84 / 0,81 | 0,87 / 0,84 / 0,82 |
| Sombras (RGB medio < 0,25) | 0,08 / 0,07 / 0,08 | 0,08 / 0,08 / 0,08 |

- **Contraste alto**: negros recortados a 0 (camiseta negra sin detalle), blancos a 0,98.
- **Blancos cálidos** (R > G > B, diferencia ≈ +0,04 R sobre B); sombras neutras con un toque magenta mínimo.
- Saturación natural en el montaje (media 0,25); interior luminoso high-key.
- Corrección a aplicar al bruto: contraste +12 %, negros −4 %, temperatura ligeramente cálida, saturación +5 % [valores exactos de la gradación del editor: SUPOSICIÓN; los objetivos medibles son los de la tabla].

---

## 8. Sonido

| Capa | Valores |
|---|---|
| Sonoridad total | **−10,5 LUFS integrados** (RMS gancho −12 dBFS; montaje −6,7 dBFS) |
| Voz | protagonista en el gancho; limpia, sin reverb |
| Música | 120 BPM; **muy baja o ausente bajo la voz** [SUPOSICIÓN: se intuye un colchón tonal a ~525 y ~840 Hz, ≈ −25 dB bajo la voz]; **entra a plena potencia en 15,40 s** con el destello |
| SFX | ver tabla |

### Mapa de SFX de la referencia
Ningún archivo de la carpeta coincide bit a bit con los SFX de la referencia: se compararon los **147 SFX únicos** de la carpeta completa (442 archivos con duplicados) y la correlación de forma de onda con ventana ≥ 1 s es < 0,26 (una copia exacta da > 0,8). Por espectro, los eventos son de estos tipos y los archivos más parecidos de la carpeta son:

| Tiempo ref. | Evento visual | Tipo de sonido | Archivo de la carpeta más parecido (por espectro) |
|---|---|---|---|
| 0,00–0,30 s | arranque + "BUENOS/DÍAS" | golpe de subgrave | `Sub Bass Hit.wav` / `Deep Bass Hit 1.wav` [SUPOSICIÓN] |
| 1,70–2,00 s | entra "PARA/GRABAR" | whoosh de aire | `SWHOOSH.mp3`, `Woosh Effect 2.wav` (z = 3,5) |
| 2,60–2,87 s | transición de desenfoque | whoosh corto | `Woosh Effect 5.wav` / `VS_Short Whoosh 3.mp3` |
| 4,45 s | entra "A NUESTROS/CLIENTES" | pop + swoosh corto | `Pop up SFX.mp3` (0,70), `Swoosh 01 - 05.wav` |
| 5,70–6,20 s | sale "CLIENTES" / entra neón | whoosh + golpe de grave (pico en 6,00 s) | `SWHOOSH.mp3` (z = 3,9) + `Cine SFX/BASS DROP (10).wav` (0,585 en ventana de 0,3 s) |
| 9,50 / 11,30 s | tarjetas de foto | swoosh suave | `Swoosh 01 - 03.wav`, `Loud Whip.mp3` (bajo) |
| 11,90–12,13 s | transición de desenfoque + punch-in | whoosh | `VS_Short Whoosh 4.mp3` |
| 15,40 s | destello + montaje | subida/impacto (va con la música) | `Sharp Riser.wav` → `Boom 2.mp3` |

### Reglas de SFX (para la edición)
- **Solo archivos de la carpeta del cliente.**
- Cada palabra destacada gigante: **whoosh** al entrar (−14 dB) + **golpe de grave** si es la primera o la más importante del bloque (−10 dB).
- **Textos de pantalla (kickers, rótulos, datos): SFX de tecleo** (`Type Digital SFX.wav`, `Efecto type de letras.wav`, `Escribir teclado.mp3`, `Tecla.mp3`), una pulsación cada 2 fotogramas mientras se escribe, −16 dB.
- Tarjetas/b-roll en ventana: `Pop up SFX.mp3` o swoosh suave (−16 dB).
- Transiciones de desenfoque: whoosh corto (−12 dB).
- Máximo **1 SFX "fuerte" cada 2 s** para no saturar; los SFX nunca tapan la voz (ducking de 3 dB en la música, no en la voz).

---

## 9. Correcciones del cliente (se añaden aquí cuando me corrijas algo que te guste)

_(vacío por ahora)_
