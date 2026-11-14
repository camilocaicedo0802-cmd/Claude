# estilo.md — análisis del reel de referencia (Frank, "cambios a mitad de obra")

Fuente: `Video_referencia_Felix_Ramirez.mp4`. 720×1280, 30 fps, H.264 + AAC 44,1 kHz estéreo. Dura 52,75 s.
Método:
- Fotogramas a 2 fps (105) más los fotogramas en cada cambio de plano (`select=gt(scene,…)`), con umbral 0,25 para planos y 0,06 para jump cuts.
- Ventanas a 30 fps alrededor de cada animación.
- Audio transcrito con Whisper (faster-whisper medium, tiempos por palabra) y medido con EBU R128 y RMS en las pausas.

Los valores en px se dan a 1080×1920 (la referencia ×1,5). Lo marcado con [SUPOSICIÓN] no se puede medir con exactitud
en el archivo y es mi mejor lectura.

## 1. Formato y estructura

- **Formato:** entrevista POV. Una persona fuera de cámara (voz femenina) pregunta y su mano entra en primer plano gesticulando. El experto contesta a cámara en el lugar de obra.
- **Arranque:** a los 0,0 s ya está la pregunta con el nombre del experto ("Frank, ¿qué pasa cuando…?"). No hay intro ni logo.
- **Hilo:** pregunta → respuesta corta y contundente → contrapregunta corta ("¿Cómo así?", "¿Y siempre es así?") → explicación → regla/conclusión ("el error no es cambiar, es cambiar tarde") → CTA.
- **Contrapreguntas:** 3 en total, de 0,5 a 0,9 s cada una. Reinician la atención cada 10–15 s.
- **CTA final:** dura 5 s (47,8–52,6). Cierra con "comenta la palabra OBRA y te estaremos contactando". No hay logo ni tarjeta final: termina sobre el experto.

## 2. Ritmo de cortes

| Medida | Valor |
| --- | --- |
| Planos totales | 24 (≈ 1 corte cada 2,2 s) |
| Cortes en el A-roll (jump cuts) | 2,77 · 4,77 · 5,33 · 7,13 · 14,47 · 16,20 · 26,40 · 27,53 · 29,47 · 31,77 · 32,77 · 34,57 · 44,50 · 45,47 s |
| Duración de plano A-roll | 0,5–7,3 s; mediana 1,9 s |
| Bloques de B-roll | 2 bloques: 22,47–25,73 s (3 clips: 1,20 / 0,87 / 1,20 s) y 36,87–41,67 s (4 clips: 1,00 / 1,07 / 1,07 / 1,67 s) |
| Peso del B-roll | 8,1 s de 52,7 s (15 %) |
| Velocidad de habla | 3,25 palabras/s (171 palabras) |
| Pausas | Se cortan todas. Las que quedan entre frases son de 0,15–0,9 s (mediana 0,31 s), y las de más de 0,5 s llevan un SFX encima |

**Encuadre:**
- Alterna plano abierto (cuerpo entero, cabeza a ~30 % desde arriba) con punch-in de ~1,45× (cabeza a ~22 %, de cintura para arriba).
- El cambio es por corte seco en el jump cut (27,53 s abierto → cerrado), sin zoom animado.
- [SUPOSICIÓN] Hay estabilización digital leve, porque la mano POV tiembla y el fondo no.

## 3. Subtítulos

| Parámetro | Valor |
| --- | --- |
| Fuente | Sans neo-grotesca, peso medio/semibold, tipo SF Pro Display Semibold / Instagram Sans [SUPOSICIÓN: no se puede extraer el nombre del archivo] |
| Tamaño base | Altura de mayúscula ≈ 54 px (2,8 % del alto). Equivale a ~76 px de cuerpo |
| Tamaño de énfasis | La última línea del bloque va a 1,5–1,7× (≈ 120 px de cuerpo) |
| Palabra héroe (sola) | ≈ 2,2× (≈ 165 px de cuerpo; "nadie", "quiere", "escuchar") |
| Tracking / interlineado | Tracking ≈ −3 % [SUPOSICIÓN]; interlineado ≈ 0,95 (las líneas apiladas casi se tocan) |
| Color | Blanco #FFFFFF. Destacado amarillo **#F5E12A** (RGB 245,225,42, medido en "Obra") |
| Sombra | Negra suave, ~35 % de opacidad, desenfoque ~8 px, sin desplazamiento [SUPOSICIÓN]. Sin contorno ni caja |
| Posición | Centrado en X. Centro del bloque a **57 % del alto (y ≈ 1095 px)**, a la altura del pecho. La palabra héroe va a 26–30 % (y ≈ 500–580 px), por encima o detrás de la cabeza. El CTA va arriba, al 13–19 % (y ≈ 250–370 px) |
| Palabras por bloque | 1–3 (mediana 2). Ejemplos: "implica", "tiempo", "y dinero", "a los arquitectos", "a rediseñar" |
| Bloques apilados | En frases clave las líneas se van sumando debajo de la anterior, hasta 4: "¿Qué pasa / cuando el / cliente quiere", "cambiar algo / a mitad / de obra?", "¿Entonces / el error / no es / cambiar?" |
| Animación de entrada | Cada línea entra con fade 0→100 % en 5 fotogramas (0,17 s) más desenfoque 6→0 px [SUPOSICIÓN en el blur], sin desplazamiento. En el CTA la palabra clave se revela de izquierda a derecha en 0,15 s |
| Salida | Corte seco al entrar el siguiente bloque (a veces un fade de 0,1 s) |
| Palabra destacada | Va en la última línea, más grande y amarilla. Son conceptos clave: "de obra?", "arquitectura", "ingenierías", "dinero", "cambiar?", "tu obra", "tu casa", "Obra" (~1 cada 5–6 s) |
| Relación con la persona | Las palabras héroe quedan **detrás de la cabeza** (a los 4,8 s, "escuchar" se ve tapada por la cabeza de Frank) |
| Sincronía | Palabra a palabra: cada bloque entra en el inicio de su primera palabra (±1 fotograma) |

## 4. Objetos y textos en pantalla (motion graphics)

- **Iconos de concepto:** objetos de estilo 3D/emoji.
  - Reloj en insignia circular con borde dentado ("tiempo").
  - Billete con alas ("presupuesto").
  - Trabajadores con casco ("arquitectos y yo").
  - Grúa ("tu obra") y casa ("tu casa").
  - Tamaño: 100–130 px (9–12 % del ancho).
  - Posición: junto a la palabra o debajo de ella, a 120–200 px.
  - Entrada: pop de escala 0,6→1,0 en 0,2 s con un anillo de brillo blanco. Si hay varios, entran escalonados cada 0,13 s.
  - Salida: con el bloque de texto.
- **Gráfica:** una línea verde (#3EE03E) en zigzag ascendente con brillo, dibujada de izquierda a derecha en 0,35 s, en el cuadrante superior derecho (x 50–100 %, y 15–30 %), para "un aumento en el presupuesto".
- **Glow rojo de bordes:** viñeta roja (#E23B3B) en los cuatro bordes, ~12 % del ancho. Sube 0→60 % en 0,25 s, se mantiene ~0,8 s y sale por corte. Aparece en el momento negativo ("tumbar lo hecho, imagínate").
- **Nombre:** la primera palabra ("Frank") aparece como subtítulo normal cuando lo llaman.
- [SUPOSICIÓN] No hay lower thirds, barras ni marcos: todo el grafismo es texto, iconos y la línea.

## 5. B-roll

- Es material propio de obras: arquitecto con tableta, obrero con casco frente a un muro de ladrillo, dos personas en un andamio, planos CAD y render 3D en pantalla, cocina en construcción.
- Cada clip está ligado literalmente a lo que se dice ("todo detallado" → personas revisando la obra; "hacer cambios" → plano en CAD; "fase constructiva" → cocina en obra).
- Los subtítulos siguen en la misma posición (57 %) encima del B-roll.
- Los clips son de 0,9–1,7 s, sin speed ramps visibles, con leve movimiento de cámara en mano.

## 6. Transiciones y zooms

- **Corte seco:** ~90 % de las uniones.
- **Light leak / flash cálido:** una vez, al volver del B-roll al A-roll (41,65–42,0 s). El plano se calienta a naranja, se quema a blanco crema en 2 fotogramas y revela el A-roll con un lavado naranja que cae en ~0,3 s. Total ≈ 0,35 s.
- **Punch-in por corte:** 1,0 ↔ ~1,45×, en los jump cuts.
- No hay whips, glitch ni zooms animados.

## 7. Color

- **Look:** cálido y luminoso, de día. Blancos cremosos (paredes ~#E8DCC8), negros apenas levantados y contraste medio.
- **Saturación:** los naranjas (tubos, casco amarillo) un poco subidos (+10 %) [SUPOSICIÓN], con la piel natural y cálida.
- El B-roll de oficina tiene el mismo balance cálido. El render 3D se deja con su color.

## 8. Sonido

- **Música:** no hay cama musical. Las pausas entre frases miden −33 a −43 dB RMS, es decir, solo ambiente.
- **Voz:** limpia, al frente. Mezcla final a **−14,1 LUFS** integrados.
- **SFX:** suenan en las pausas que lo justifican, a unos −15/−19 dB RMS:
  - golpe grave/whoosh al cortar al punch-in (28,5–29,4 s);
  - whoosh/shimmer en el light leak (41,6–42,1 s);
  - golpe en "tumbar… imagínate" (con el glow rojo);
  - sonido de dinero en "dinero" y en "presupuesto" [SUPOSICIÓN sobre el tipo].
- Todo es sutil: ningún SFX tapa la voz.

## 9. Cómo lo aplico al reel de cocina (West Home / Félix)

- **Estructura:** la misma (pregunta POV con el nombre "Félix", respuesta, contrapreguntas cortas, regla/recomendación, CTA "comenta la palabra COCINA"), con un objetivo de 40–45 s.
- **Fuente:** se cambia por la de la marca, Poppins. SemiBold para la base (lo más parecido al peso medio de la referencia), Bold/ExtraBold para el énfasis y las palabras héroe. Tracking −3 %.
- **Color destacado:** el amarillo #F5E12A se cambia por el naranja de la marca (#FF4D00 → #FF7A3D en degradado).
- **Iconos:** los objetos 3D de la referencia son emojis, y en estos videos no se usan. Por eso los dibujo propios (insignias redondas con brillo) del tema: precio, mantenimiento, piedra natural, fábrica, patrones, sello, llama/calor, olla caliente, tienda/almacén, muestra pequeña vs losa completa y equipo con casco.
- **Comparaciones:** pantalla dividida granito vs cuarzo, barras de costo ($ vs $$) en lugar de la línea verde, y glow de advertencia (rojo) en "se puede dañar".
- **B-roll:** el crudo no trae B-roll, así que uso fotos de stock con licencia libre (Unsplash) de losas, cocinas y almacén, con movimiento de cámara, más planos de detalle de la isla de cuarzo del propio crudo.
- **Reglas de la marca que se mantienen:** textos siempre detrás de las personas, sin emojis, sin silencios y arrancando con la persona en pantalla.
