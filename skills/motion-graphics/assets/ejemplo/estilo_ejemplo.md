# estilo.md — guía de estilo extraída de `referencia.mp4`

Fuente analizada: `referencia/referencia.mp4`. Dura 8.52 s, 576×1024 a 30 fps, con locución en español y música de fondo.
Todas las medidas están **convertidas a 1080×1920** (factor ×1.875) salvo que se indique lo contrario.
Lo que no se puede medir con certeza va marcado con **[SUPOSICIÓN]**.

Material de análisis: `referencia/frames_2fps/` (17 fotogramas), `referencia/frames_cortes/` (cambios de plano),
`referencia/audio_ref.wav`, separación de pistas con Demucs en `referencia/separado*/`, transcripción en `referencia/whisper_ref/`.

---

## 1. Estructura y ritmo de cortes

| Bloque | Tiempo | Duración | Contenido | Frase de la voz |
|---|---|---|---|---|
| E1 | 0.00–4.13 s | 4.13 s | Bombilla en círculo discontinuo → la cámara baja hasta la señal STOP | "Si tienes una idea, realízala. No le pongas un alto a tu creatividad." |
| E2 | 4.13–6.20 s | 2.07 s | Estatua griega pensativa + banda negra | "Si no salió bien, no importa." |
| E3 | 6.20–7.70 s | 1.50 s | La estatua se oscurece hasta ser silueta; un cerebro sustituye su cabeza | "Porque ya aprendiste algo." |
| Cierre | 7.70–8.25 s | 0.55 s | Tarjeta gris con el @usuario | — |
| Negro | 8.25–8.52 s | 0.27 s | Negro | — |

- **Cortes duros: 0.** Todo son transiciones animadas. El cambio más fuerte (iris) puntúa 0.234 en el detector de escena de ffmpeg, a los 7.70 s; el barrido de 4.4 s puntúa 0.071.
- **Escena nueva cada 1.5–4.1 s** (media 2.6 s).
- **Evento visual nuevo cada 0.2–0.5 s**: una palabra, un objeto, un movimiento de cámara o un trazo. Nunca pasan más de 0.6 s sin que algo cambie.
- **Una frase de voz = un "beat" visual.** Entre frases hay pausas de 0.4–0.6 s, que se aprovechan para mover la cámara.
- La cámara **nunca está quieta** (ver §6).

## 2. Subtítulos (sistema de dos niveles)

Los subtítulos no son una franja fija abajo: son **tipografía editorial colocada junto al objeto** del que habla la frase.

### 2.1 Línea guía (caligráfica)
- **Fuente:** caligráfica inclinada y conectada, de contraste fino. Sustituto libre elegido: **Parisienne** (Google Fonts), comparada lado a lado con la original y casi idéntica. [SUPOSICIÓN: la original no se puede identificar con exactitud]
- **Tamaño:** 56 px (altura de mayúscula ≈ 47 px). "Si tienes una idea" ocupa 394 px de ancho.
- **Color:** `#141414` sobre fondo claro y `#F0F0F0` sobre fondo oscuro.
- **Contenido:** de 3 a 6 palabras, la parte de la frase que lleva hasta la palabra clave ("Si tienes una idea", "no le pongas un alto a tu", "Si no salió bien").
- **Animación:** aparece **palabra a palabra, sincronizada con la voz**. Cada palabra entra en 6 frames (0.2 s): opacidad 0→1, desenfoque 8 px→0 y subida 12 px→0, con easing ease-out. Las palabras ya dichas se quedan en pantalla.
- **Variante E2:** revelado de izquierda a derecha con desenfoque de unos 10 px que se va limpiando, como una barrida suave.
- Las palabras quedan con pequeñas diferencias de línea base (±6 px), así que no forman una línea perfectamente recta.

### 2.2 Palabra destacada (palo seco negra)
- **Fuente:** grotesca muy gruesa con tracking apretado, tipo Helvetica Neue Heavy. Sustituto libre: **Archivo 800–900**, `letter-spacing: -0.03em`. [SUPOSICIÓN]
- **Tamaño:** 122–131 px. "realizala" ocupa 572 px de ancho y "creatividad" 806 px.
- **Color:** `#141414`.
- **Contenido:** 1–2 palabras, el concepto clave de la frase ("realizala", "creatividad", "no importa").
- **Animación:** entra **en el frame exacto en que se pronuncia**. El color pasa de gris claro `#B4B4B4` a `#141414` en 9 frames (0.3 s), sube 35 px→0 y la opacidad va de 0→1 en 3 frames. En E2 usa el revelado con desenfoque de izquierda a derecha (10 frames).
- **Composición:** la línea guía va **justo encima** de la palabra destacada, casi pegada (la línea base del guion queda 0.1 em por encima de la altura de mayúscula de la destacada). La alineación puede ser a la izquierda (el guion empieza donde empieza la destacada) o a la derecha (el guion termina donde termina la destacada), y se alterna entre bloques.
- **Posición:** el bloque de texto se coloca **encima del objeto** al que se refiere, alineado a la izquierda con un margen de 130–255 px. La altura depende de la cámara: al asentarse, el bloque queda entre el 13 % y el 30 % de la altura del cuadro.

### 2.3 Inversión final (sobre fondo negro)
- La jerarquía se invierte: **la guía va en palo seco blanca y pequeña** (Archivo 800, 52 px, "porque ya") y **la destacada en caligráfica blanca y grande** (Parisienne, 95–100 px, "aprendiste algo").
- Usa el mismo revelado con desenfoque de izquierda a derecha.

### 2.4 Lo que NO hay
- Subtítulos fijos abajo, cajas o fondos detrás del texto, contornos, emojis y mayúsculas sostenidas: todo va en minúsculas salvo la "S" inicial de las frases.

## 3. Textos en pantalla
- Solo existen los subtítulos de §2. No hay títulos, rótulos ni contadores.
- **Tarjeta de cierre:** fondo `#B6B6B6`, @usuario en Archivo 800 a 42 px, color `#141414`, centrado en horizontal y al 46 % de la altura.

## 4. B-roll (objetos)
- **No hay vídeo real.** El b-roll son **recortes fotográficos de objetos simbólicos** en escala de grises: bombilla (idea), señal STOP (freno), estatua griega pensativa (reflexión o fracaso) y cerebro (aprendizaje). **Un objeto por concepto.**
- **Tratamiento:** saturación 0, contraste alto, aspecto 3D realista y **sombra proyectada abajo a la derecha** (desplazamiento 18–24 px, desenfoque 30 px, opacidad 0.45).
- **Tamaño:** el objeto protagonista ocupa el 26–45 % del ancho (bombilla unos 280 px, STOP unos 470 px). La estatua ocupa el 75–100 % del ancho.
- **Entradas:** el objeto entra desde un borde con rotación. La bombilla entra desde la izquierda, gira de −35° a −8° y se desliza unos 560 px en 0.6 s con ease-out. La estatua entra desde abajo a la izquierda.
- **Sustitución simbólica:** un objeto se transforma en otro con significado (cabeza de la estatua → cerebro).

## 5. Motion graphics y transiciones

### Elementos gráficos
1. **Círculo discontinuo** alrededor del objeto protagonista: diámetro de unas 1.45× el objeto (≈ 390 px), trazo de 7 px en `#141414`, guiones de 22 px con huecos de 16 px. Va girando despacio. [SUPOSICIÓN: la velocidad de giro, unos 10°/s]
2. **Trazo curvo de pincel:** línea negra gruesa (20–26 px) con bordes difuminados y sombra, en forma de "S", que **serpentea entre los objetos y guía la vista** (une la bombilla con el STOP). Se dibuja según avanza la cámara.
3. **Banda negra horizontal** detrás de la estatua: ocupa el 8–25 % de la altura y crece con el zoom.
4. **Halo negro difuminado** (desenfoque de unos 60 px) detrás del cerebro y de la silueta.
5. **Marco rectangular fino** gris de 2 px, visible un instante durante el empuje de E3. [SUPOSICIÓN: es el borde de una capa]

### Transiciones
| Momento | Tipo | Duración | Detalle |
|---|---|---|---|
| E1→E2 (4.13 s) | **Empuje horizontal / whip** | 0.25 s | Todo el plano se desplaza hacia la derecha con desenfoque de movimiento y entra el siguiente |
| E2→E3 (5.9–6.3 s) | **Oscurecimiento y transformación** | 0.4 s | El brillo de la estatua baja al 8 % hasta quedar en silueta; el fondo pasa a negro y aparece el cerebro con halo; empuje de cámara hacia dentro |
| E3→cierre (7.70 s) | **Iris circular** | 4 frames | Círculo gris `#B6B6B6` con borde suave de unos 20 px que se expande desde el centro-abajo hasta cubrir el cuadro |
| Cierre→negro (8.25 s) | Corte a negro | 1 frame | — |

## 6. Zooms y cámara
- **E1:** tras la entrada de la bombilla, **desplazamiento vertical continuo hacia abajo de unos 535 px en 3.5 s** (ease-in-out, el tramo más rápido entre 1.0 y 2.5 s). La cámara viaja de un objeto al siguiente siguiendo el trazo curvo y la escala sube de 1.00 a 1.05.
- **E2:** zoom hacia dentro de **1.00 a 1.25 en 1.8 s** sobre la estatua, más una ligera subida.
- **E3:** empuje hacia dentro y subida (≈ 10 % de la altura en 1 s): el texto anterior sale por arriba del cuadro.
- **Deriva permanente:** el plano se mueve siempre de 5 a 15 px/s. El cuadro nunca está quieto.
- Todo con curvas de easing suaves, sin rebotes ni sacudidas.

## 7. Color y textura
- **Monocromo total.** No hay ningún color con saturación.
- Fondo papel `#E4E4E4` (228,228,228).
- Texto y objetos negros `#141414`.
- Escena oscura `#131314` (19,19,20).
- Texto sobre oscuro `#F0F0F0`.
- Tarjeta de cierre `#B6B6B6` (182).
- **Grano de película:** desviación de unos 6.7/255 en las escenas claras y unos 10/255 en las oscuras. Es animado y cambia en cada frame.
- **Viñeta** suave en los bordes. [SUPOSICIÓN: oscurece un 12–15 % en las esquinas]
- **Aberración cromática** leve, de 1 px, en los bordes del texto: se ven franjas cian y naranja en los recortes ampliados.
- Contraste alto en los objetos: punto negro casi 0 y blancos de 240–250.

## 8. Sonido
- **Voz:** seca, sin reverb, centrada (L = R exacto en los tramos de solo voz). Picos a −6 dBFS, RMS de la mezcla −21 dB. Frases cortas con pausas de 0.4–0.6 s.
- **Música:** cama tonal suave, tipo piano o pad [SUPOSICIÓN sobre el instrumento], en tonalidad Do menor / Fa menor según el croma (C, F, D#, G, G#) y a unos 59 BPM [estimado]. Suena **muy baja: unos −40 dB RMS, 18–20 dB por debajo de la voz**, continua y sin golpes rítmicos.
- **Efectos (SFX):** estéreo abierto, a la izquierda y derecha, con un efecto **por cada objeto nuevo, palabra fuerte o transición**:
  - 0.0–1.2 s: whoosh grave de entrada (entra la bombilla), pico unos −12 dB.
  - 3.4 s: golpe o pop corto al aparecer "creatividad".
  - 4.4 s: whoosh de transición (empuje horizontal).
  - 6.4 s: whoosh suave al revelarse el cerebro.
  - 7.7 s: impacto o clic seco en el iris.
- Los efectos suenan a unos −10/−13 dB de pico, por encima de la música y sin tapar la voz.

## 9. Reglas para adaptar este estilo a vídeos más largos
- Mantener **una escena por idea u objeto, de 2 a 4 s**, enlazadas siempre con una transición del catálogo de §5 (nunca un corte seco).
- Por cada frase: línea guía en caligráfica palabra a palabra, más 1–2 palabras clave en Archivo negro sobre o junto al objeto que la simboliza.
- Alternar fondo claro (papel) y oscuro (negro) para marcar los cambios de tono. La inversión de la jerarquía tipográfica se reserva para el cierre emocional.
- Un SFX en cada entrada de objeto, palabra destacada y transición. La música, siempre de 18 a 20 dB por debajo de la voz.

---

## Correcciones aprobadas por el usuario
_(Aquí se añaden las correcciones que el usuario apruebe para que se mantengan en futuros vídeos.)_
- **2026-10-11 · Borrador v1 aprobado** («me gusta mucho el estilo»). Se mantiene como base para próximos vídeos con esta referencia:
  - escenas de 2–6 s que alternan papel y negro;
  - transiciones solo del catálogo de §5, más el zoom dentro de una pantalla;
  - subtítulos de dos niveles con la jerarquía invertida en las escenas oscuras;
  - recortes en B/N con sombra, más vectores monocromos (móvil, tarjeta, notificaciones) para lo que no existe en foto;
  - un SFX en cada objeto, palabra clave y transición;
  - música de la referencia en bucle, entre 14 y 18 dB bajo la voz;
  - mezcla final a −14 LUFS con el pico real ≤ −1 dBFS.
