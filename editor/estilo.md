# estilo.md — guía de edición (Beleza · Drena Oil)

Fuente: análisis de `referencia.mp4` (29,70 s · 576×1024 · 30 fps · AAC estéreo 44,1 kHz) con ffmpeg:
59 fotogramas a 2 fps, 9 cortes detectados, silencedetect, EBU R128 y RMS por ventanas.
Todo lo que no se pudo medir está marcado **[SUPOSICIÓN]**. Tiempos de textos: ±0,25 s (muestreo a 2 fps).
Medidas en px de la referencia (576 px de ancho); entre paréntesis, su equivalente en 1080×1920 (×1,875).

> **Límite del análisis:** no he podido transcribir el audio (Whisper no puede descargar su modelo en este entorno), así que no sé qué palabras dice la persona en cada plano. Los textos en pantalla sí los he leído de los fotogramas.

## 0. Hallazgo importante: la referencia NO lleva subtítulos continuos
No hay subtítulos palabra a palabra. En su lugar usa **textos en pantalla puntuales** (gancho, URL, contador 3-2-1, precio) y un rótulo de cierre. Los valores de subtítulos de la sección 3 son por tanto **[SUPOSICIÓN]** diseñados con tu marca, no copiados de la referencia.

## 1. Formato
| Parámetro | Valor |
|---|---|
| Lienzo de salida | 1080×1920, 30 fps, H.264 |
| Plano | Una sola persona, a cámara, plano medio-pecho, fondo liso con degradado cálido |
| Estructura | Gancho 0–2,2 s · URL 3,2–5,1 s · título 5,7–8,7 s · contador 3→2→1 de 9,5 a 21,7 s · precio 24,25–25,67 s · cierre 25,67–29,7 s |

## 2. Ritmo de cortes
- Cortes en: **2,17 · 5,13 · 6,27 · 8,73 · 11,97 · 13,43 · 17,00 · 21,70 · 25,67 s** (9 cortes en 29,7 s).
- Duración de plano: mín **1,13 s**, máx **4,70 s**, mediana **≈2,97 s** (≈1 corte cada 3 s en la parte hablada).
- Tipo: **jump cut** sin transición (corte seco). El cierre (25,67 s) es corte seco a imagen oscurecida.
- Reencuadre en cada corte: alterna **1,00× ↔ ~1,15–1,20×** (punch-in) [SUPOSICIÓN: estimado a ojo en pares antes/después; sin interpolación, el zoom salta de golpe].
- Pausas: no hay pausas > 0,35 s dentro del discurso (única: 1,78–2,12 s, justo en el primer corte). El audio de voz está cortado "al hueso".
- **Regla para tu vídeo:** cortar todo silencio > 0,3 s (tu petición) y forzar un reencuadre 1,0× ↔ 1,15× en cada corte; objetivo 1 corte cada 2,5–3,5 s.

## 3. Subtítulos (palabra a palabra) — ANULADO por §10.9 (se conserva como referencia)
| Parámetro | Valor propuesto |
|---|---|
| Fuente | Glacial Indifference Bold (cuerpo/funcional según manual) |
| Tamaño | 78 px |
| Color base | Marfil `#F5F0EC` con sombra `0 4px 22px rgba(69,89,90,.55)` |
| Palabra activa | Texto Durazno `#FAEDCD` sobre píldora Verde petróleo `#45595A`, radio 18 px, padding 6×18 px |
| Palabras por bloque | 2–3 (máx. 2 líneas, máx. 22 caracteres por línea) |
| Posición | Centrado horizontal, centro del bloque en y = 1280 px (67 % de alto), margen lateral ≥ 90 px |
| Animación de entrada | Bloque: fade+subida 12 px en 4 fotogramas · palabra activa: pop de escala 0,9→1,0 con `spring` (damping 14) en ≈5 fotogramas |
| Sincronía | Cambio de palabra activa en `word.start` de Whisper; el bloque cambia cuando se acaban sus palabras |
| Zona a evitar | Franja y 1500–1620 px (precio/CTA) y esquinas de la marca de agua |

## 4. Textos en pantalla (esto sí es de la referencia)
Color original: amarillo `#F4E517` (medio medido rgb 244,229,20), sin caja ni sombra visible. Tipografía: sans geométrica de peso muy alto, mayúsculas [SUPOSICIÓN sobre la familia exacta].

| # | Texto | Tiempo | Posición (ref → 1080×1920) | Tamaño | Animación |
|---|---|---|---|---|---|
| 1 | `TÓNICO` / `DE ROSAS` (2 líneas, izq.) | 0,75–2,17 s | x 79–369 px (148 px de margen izq.), y 742–855 → y ≈ 1390–1600 | altura de mayúscula 38–48 px (≈ 71–90) → fuente ≈ 100–125 px | Palabra por palabra, la 2ª entra ≈0,4 s después (aparece con fundido ≈ 3–4 fotogramas) |
| 2 | `www.lulabeauty.co` | 3,25–5,13 s | x 100–473, y 788–821 → y ≈ 1478–1540, alineado a la izquierda | altura de mayúscula 34 (≈ 64) → fuente ≈ 62 px, peso medio | **Máquina de escribir** con cursor `|` fijo; ≈ 10 caracteres/s |
| 3 | `3 RAZONES` (arriba izq.) + `PARA` (a la derecha, debajo) + `A MAR LO` (abajo) | 5,75–8,73 s | `3 RAZONES`: x 54–497, y 104–155 → y ≈ 195–290 · `PARA`: x 336–495, y 169–207 · `A MAR LO`: x 66–525, y 700–769 → y ≈ 1310–1440 | `3 RAZONES` fuente ≈ 135 px · `A MAR LO` ≈ 180 px | Palabra por palabra, ≈ 0,5 s entre palabras; se mantiene hasta el corte |
| 3b | `Tanto como nosotras` (naranja, tipografía manuscrita) | ≈7,8–8,73 s | x 226–510, y 788–809 → y ≈ 1480–1517 | altura ≈ 22 (≈ 41) | Fundido; color naranja `~#F28A1E` [SUPOSICIÓN del tono exacto] |
| 4 | Contador `3.` → `2.` → `1.` | `3.` ≈9,5–11,97 · `2.` 11,97–17,00 · `1.` 17,00–21,70 s | x 69–129, y 176–229 → esquina sup. izq., y ≈ 330–430 | altura de mayúscula 54 (≈ 101) → fuente ≈ 140 px | Cambia en el **mismo fotograma del corte**; sin animación visible |
| 5 | Píldora de precio `$25.800` | 24,25–29,7 s (queda atenuada en el cierre) | x 160–293, y 768–829 → píldora ≈ 250×116 px, y ≈ 1440–1555, x ≈ 300–550 | texto morado oscuro bold sobre fondo amarillo, radio ≈ 15 px | Pop-in; **dos flechas diagonales** moradas apuntan al producto recortado a la derecha |
| 6 | Cierre: icono Instagram + `@LULABEAUTY.CO` | 25,67–29,7 s | icono centrado (x 50 %, y 48 % → y ≈ 920) · handle debajo (y 56,5 % → y ≈ 1085) | handle ≈ 30 px, mayúsculas condensadas | El icono pasa de blanco → degradado Instagram → blanco en ≈ 1 s (bucle) |
| 7 | Marca de agua (icono IG + `@LULABEAUTY.CO` minúsculo) | ≈2,5–25,67 s | Alterna esquina sup. dcha. (x ≈ 90 %, y ≈ 15 %) y abajo-izq. (x ≈ 8 %, y ≈ 62 %) según no choque con el contador | icono ≈ 26 px, handle ≈ 11 px, opacidad ≈ 70 % | Estática |

## 5. B-roll y recursos gráficos
- **Sin b-roll.** Todo el vídeo es la misma toma de la persona.
- Recorte del producto (tónico de rosas) superpuesto: **0,75–2,17 s** y **24,25–29,7 s**, abajo a la derecha: x ≈ 68–94 %, y ≈ 59–95 % (≈ 175 px de ancho × 690 px de alto en 1080×1920). Entrada: aparece con ligero fundido/rebote.
- El producto real se sostiene en mano en casi todos los planos.

## 6. Transiciones
- Solo corte seco. **No hay** fundidos entre planos, ni whips, ni glitch.
- Único efecto de transición: cierre a imagen oscurecida (corte seco en 25,67 s).

## 7. Color
- Referencia: fondo degradado gris-azulado arriba → resplandor cálido naranja-melocotón abajo-izquierda; piel natural; sin LUT visible [SUPOSICIÓN: sin corrección fuerte].
- Cierre: capa negra al ≈ 65–70 % de opacidad sobre el último plano [SUPOSICIÓN del porcentaje].
- Texto: amarillo único `#F4E517` + naranja manuscrito para la frase de apoyo + morado para el precio.

## 8. Sonido
- **Sin cama musical**: el suelo de ruido en las pausas es ≈ −33 dBFS (sala).
- Voz: RMS típico −14 a −20 dBFS; integrado **−13,7 LUFS**, LRA **3,6 LU**, pico **0,1 dBFS** (muy limitado/comprimido).
- El audio termina en **27,85 s**; el vídeo sigue mudo hasta 29,7 s.
- Hay un evento sonoro de **26,04 a 27,10 s** (pico ≈ 0 dBFS) justo tras el corte de cierre [SUPOSICIÓN: efecto/jingle de cierre; no he podido escucharlo].
- No hay evidencia medible de efectos en los cortes [SUPOSICIÓN: ninguno].
- **Regla para tu vídeo:** normalizar la voz a ≈ −14 LUFS, pico máx. −1 dBTP; sin música salvo que lo pidas.

## 9. Identidad de marca (OBLIGATORIA, prevalece sobre la referencia)
Paleta: Durazno suave `#FAEDCD` · Marfil cálido `#F5F0EC` · Verde salvia `#6D8B74` · Verde petróleo `#45595A`.
Tipografías: **TAN Pearl** (marca, portadas, frases muy cortas de alto impacto; nunca en textos largos, precios ni instrucciones) y **Glacial Indifference** (cuerpo, descripciones, precios, botones, instrucciones).
Escala: Titular = TAN Pearl o Glacial Bold, máx. 3–7 palabras · Subtítulo = Glacial Semibold, una idea por bloque · Cuerpo = Glacial Regular · Precio/CTA = Glacial Bold. Máx. 2 familias por pieza.
Sustitutos del manual: Cormorant Garamond / Bodoni Moda (editorial), Montserrat / Poppins / Arial (funcional).
**Estado de las fuentes:** Glacial Indifference Regular y Bold instaladas (npm `typeface-glacial-indifference`; no incluye Semibold, uso Bold). **TAN Pearl instalada** (`public/fonts/TAN-Pearl-Regular.otf`, solo peso Regular); Cormorant Garamond queda como respaldo.

### Traducción de la referencia a tu marca
| En la referencia | En tu vídeo |
|---|---|
| Amarillo `#F4E517` en textos grandes | Gancho/título: TAN Pearl en Marfil `#F5F0EC` con sombra petróleo; contador `3.`/`2.`/`1.`: Glacial Bold en Durazno `#FAEDCD` |
| Frase naranja manuscrita | Glacial Regular en Durazno `#FAEDCD` (sin fuente manuscrita: no está en tu manual) |
| Píldora amarilla + texto morado | Píldora Durazno `#FAEDCD` + texto Petróleo `#45595A`, Glacial Bold; flechas en Salvia `#6D8B74` |
| Cierre negro al 65–70 % | **No se usa** (ver sección 10) |
| Recorte del tónico de rosas | Recorte de **Drena Oil** (foto enviada: Beleza · aceite corporal drenante y recuperador · árnica, romero, caléndula, almendras), quitando el fondo |
| URL `www.lulabeauty.co` y `@LULABEAUTY.CO` | **No se usa** (ver sección 10) |

## 10. Correcciones del usuario (se acumulan aquí, paso 4)
Estas reglas mandan sobre todo lo anterior.

1. **Sin URL, sin marca de agua de usuario y sin cierre/rótulo final.** Se eliminan las filas 2, 6 y 7 de la sección 4.
2. **Textos dinámicos según lo que se dice.** Nada de textos fijos de plantilla: cada texto en pantalla sale de la transcripción (ideas clave, beneficios, ingredientes, números, preguntas, llamadas a la acción que diga la persona).
3. **Animación según el significado.** Cada texto o efecto se elige por lo que se está diciendo en ese momento (p. ej. un ingrediente → aparece con su nombre; un número o lista → contador; un beneficio → palabra grande; una pregunta → texto que entra con pausa). Ser analítico: justificar cada elemento con la frase que lo provoca.
4. **Vídeo dinámico:** sin tramos de > 3 s sin algún cambio visual (corte, zoom, texto o animación).
5. **Audio original del vídeo**, sin normalizar ni procesar; los cortes se hacen con ffmpeg en un único archivo ya editado (nunca recortes de audio por tramo dentro de Remotion: repetían el inicio).
6. **Cuando la persona señala un hueco, ahí va un gráfico animado** que nazca de su dedo. Para el calendario: el calendario 3D de marca (`public/graficos/calendario_base.png`, agujas animadas), no una cuadrícula de días.
7. **Títulos grandes pegados a la cabeza:** anclados por abajo a y ≈ 605 px (≈ 40–80 px por encima de la cabeza), no arriba del todo.
8. ~~Más transiciones y zoom~~ → sustituida por la regla 12 (se veía saturado).
9. **Sin subtítulos.** Solo títulos grandes (arriba, base en y = 580) y recursos visuales de apoyo. La sección 3 queda anulada.
10. **Recursos de apoyo abajo:** tarjetas, listas y etiquetas ancladas por abajo, entre y = 1180 y 1560 (sobre el pantalón, fuera de la interfaz de Reels), nunca a la altura del pecho.
11. **Entrega en alta calidad:** render final H.264 CRF 16 desde el recorte 4K.
12. **Zoom solo en lo importante dicho con la voz alta:** frase clave del guion cuyo pico de volumen supera en ≥ 3,5 dB la mediana de la voz (lo mide `scripts/preparar.py`, campo `db`); zoom suave 1,0 → 1,12 (entra 10 fotogramas, se mantiene la frase, sale 15), mínimo 4 s entre zooms; nunca mientras señala. El resto del vídeo, plano fijo. Transiciones de tema sin zoom: destello Durazno 22 % + desenfoque 8 px.
13. **Nada cerca de la cara:** zona libre entre y ≈ 620 y 1180 y ≥ 100 px alrededor de la cabeza; los gráficos que acompañan un gesto (p. ej. el calendario) van en el hueco señalado pero a esa distancia.
14. **Música y efectos de sonido** (`scripts/audio_marca.py`, sintetizados: propios, sin derechos de terceros):
    - Música de fondo cálida tipo belleza/bienestar (Fa mayor, 84 BPM: pad + piano eléctrico en arpegio + bajo suave + percusión ligera), sin graves < 70 Hz y con hueco en 1–3 kHz para la voz; ~16 dB bajo la voz (volumen 0,1 ≈ −32 LUFS), sube a 0,2 al acabar de hablar.
    - Efectos variados según lo que hace el gráfico, solo en los momentos importantes y nunca encima de otro: blips (contadores), impacto suave (cifra o cierre clave), whoosh (títulos grandes), swish (títulos secundarios), pop (etiquetas), marimba ascendente (escalones/progreso), tic-tac (relojes/temporizadores), tecleo (texto que se escribe letra a letra), tarjeta (tarjetas que entran), tachado (palabra que se tacha), brillo (palabra clave positiva), campanita (logro) y subida (antes del momento final).
    - Ningún efecto por encima del nivel de la voz (impactos a 0,22).
15. **Solo las tomas buenas** (aprobado en el día 2): fuera intentos fallidos, frases que se reinician y despedidas fuera de guion ("listo, chao"); cuando hay varias tomas de la misma frase, la completa y correcta.
16. **Toma de apoyo en fragmentos cortos** (aprobado en el día 2): ≈1 s por idea, entrando en la palabra que la nombra, con flash + obturador y etiqueta abajo; sin títulos arriba mientras se ve el apoyo.
17. **Objetos 3D de marca según lo que se dice** (aprobado en el día 2): modelados con three.js (acabado clay mate, paleta Beleza), a los lados de la cabeza (x < 360 o x > 740) y con una animación que exprese la frase (el pin se clava, la cinta se desenrolla, el lápiz escribe, el candado se cierra). Si el guion indica un elemento (p. ej. carpeta "Día 1"), se puede rotular aunque no se diga.

## 11. Composición aplicada en el borrador (pendiente de tu visto bueno)
- Fuente 4K (2160×3840) recortada sin escalar a 1620×2880 (`crop=1620:2880:270:268`): plano medio con la cara al 43 % de altura.
- Plano fijo 1,0×; zoom 1,12× solo en frases clave con la voz alta (regla 12), origen en la cara (52 %, 43 %).
- Zonas: títulos con base en y = 605 (pared, con velo Verde petróleo 62 %→0 en el tercio superior) · recursos de apoyo con base en y = 1560 (pantalón oscuro, zona segura de Reels) · sin subtítulos.
- Cortes: silencios > 0,3 s a −35 dB con 0,08 s de margen, a fotograma exacto · audio original sin normalizar.

## 12. Composición aplicada en el día 2 · "Punto de partida" (aprobada)
- Crudo 1080×1920 a 59,94 fps (DJI Osmo Pocket 3): convertido a 30 fps y **sin recorte** (recortar obligaría a escalar). Cara a ~50 % · 40 %; títulos con base en y = 550 para que los trazos descendentes de TAN Pearl no bajen de y = 580.
- Tomas: solo las buenas (fuera los dos intentos fallidos de "usa un fondo neutro", el reinicio de "algo muy importante…" y el "listo, chao"); 2:25 de crudo → 47 s.
- Toma de apoyo: tres fragmentos de ≈1 s (perfil, frente, espalda) en las palabras "de perfil", "de frente" y "una de espalda", con visor, flash y obturador.
- Objetos 3D propios (three.js) a los lados de la cabeza, cada uno nacido de su frase: pin (punto de partida), celular-cámara (foto), cinta métrica (medidas), libreta (anota), calendario del día 1 (21 días) y carpeta "Día 1" con candado (son personales).

## 13. Composición aplicada en el día 3 · "Preparación y uso seguro"
- Crudo 1080×1920 a 59,94 fps, 5:22 → 1:19 con solo las tomas buenas (fuera la charla inicial sobre las hojas, el "antes de empezar… cosas no", los intentos de "tercero/tres", "o no veo", los "quinto" incompletos y el "listo/gracias").
- Estructura por pasos: número en círculo Durazno + idea en TAN Pearl (1 revisa tu piel · 2 piel seca → aceite · 3 más baja · 4 prueba · 5 movimiento · apaga y limpia), con destello en cada paso.
- Objetos 3D propios (sin calendario): lupa (revisar la piel), frasco Drena Oil que vierte gotas (aceite), gota de agua con señal de prohibido (no uses agua), perilla de intensidad que sube y baja de nivel, flechas abajo y en círculo (movimiento) y botón de encendido que se apaga con brillos (apagar y limpiar).

## 14. Composición aplicada en el día 6 · "Piernas y apariencia de la celulitis"
- Rutina con voz en off (como los días 4 y 5) sobre su propio crudo de 9 min (1080×1920 a 59,94 fps → 30 fps). El audio del crudo es solo charla de detrás de cámaras: no se usa.
- Voz en off: 2:06 → 1:32 con solo la toma buena (fuera el primer "Ahora vamos a repetir la misma secuencia en el muslo izquierdo. Tres minutos de barridos y tres…", que se corta y se repite entero) y silencios > 0,3 s.
- Tomas del crudo por frase (`scripts/rutinas/montar.py`, PLAN "dia6"): aceite en las manos y en los muslos, coge el equipo, barridos y círculos en el muslo derecho, baja la intensidad en el equipo ("recuerda verificar la intensidad… baja la intensidad de succión"), muslo izquierdo de pie y sobre el banco, cada glúteo de perfil, enseña el equipo ("terminamos") y masaje con las manos. Fuera los momentos en que mira a cámara o habla con quien graba.
- Cabeza: YuNet y, si no se ve la cara, silueta por color (la cortina es clara y poco saturada; no hay plano vacío) con una franja de 120 px, para que no entren hombros y brazos al agacharse.
- Maqueta propia (`src/dia6/Maqueta.tsx`): columnas pegadas a los bordes, debajo del título y hasta y = 1480; si una columna es estrecha el elemento se reduce hasta el 80 % y, si no cabe, se retira lo más antiguo (nunca lo último que se ha dicho).
- Objeto 3D conductor: mapa de piernas y glúteos (`Piernas3D`), el mismo todo el vídeo. "Muslos y glúteos" → se encienden y gira; en cada zona se enciende esa parte en salvia con su movimiento (líneas de luz que suben = barridos; anillo con una bola que gira = círculos); "evita pasar sobre la rodilla o la ingle" → cruces en esos puntos; glúteos de espaldas; al terminar, todo encendido.
- Resto: tarjeta de minutos por zona, frasco Drena Oil que vierte ("aplica aceite generosamente"), flecha que sube ("hacia la parte alta del muslo", "de abajo hacia arriba"), flecha en círculo ("círculos amplios"), perilla de intensidad que baja ("baja la intensidad de succión"; "una mayor intensidad no significa mejores resultados"), resumen que cuenta hasta 15 min y lista que se marca en "la técnica, el movimiento y la constancia". Sin calendario 3D.
- Mezcla: la voz en off llegó más baja (−25,2 LUFS frente a ≈ −16) y no se normaliza (§10.5); música y efectos bajan ×0,35 (≈ −9 dB). Medido sobre el render: voz con ganancia 1,0 y desfase 0, música 16,5 dB por debajo y ningún efecto por encima de la voz.
- Entrega: render CRF 16 por tramos y, para que quepa en el repositorio (< 100 MB), x264 a 2 pasadas a 7,5 Mbps + AAC 320 kbps (90 MB); copia ligera de 28,8 MB.

## 15. Composición aplicada en el día 7 · "Piernas ligeras"
- Voz en off limpia (1:19 → 1:02; sin repeticiones, solo silencios > 0,3 s) sobre **dos crudos** (cuarto con pared y puerta; uno de 7 min y otro de 3 min). Composición `Dia7`, montaje en `scripts/dia7/montar.py`.
- Pedido: que no sea monótono y se diferencie de los días anteriores sin perder la secuencia. Cambios de lenguaje:
  - **Título en la franja baja** (la cabeza está casi en el borde superior y no cabe encima): entra letra a letra con el kicker en píldora Durazno y a los ~2,4 s se recoge en una píldora pequeña en la columna lateral.
  - **Cortinas** diagonales Salvia/Durazno/Marfil en los cambios de zona (en vez de destello + desenfoque).
  - **Anillo de la rutina** con los 5 tramos del cuadro (1·4·4·3·3 min) en vez de la tarjeta de minutos.
  - **Ritmo del montaje según la frase:** timelapse ×2 en "trabajamos 4 minutos", cámara lenta (desde el original a 60 fps) en "lentos y continuos", la toma a ×3 en "no necesitas hacerlo rápido" y vuelta al ritmo normal en "necesitas mantener el movimiento", pantalla partida en "ambas pantorrillas", reencuadres lentos hacia la pierna.
  - **Etalonaje por momento:** "cansada" apagada y fría con viñeta que se calienta en "pero no quieres abandonar el hábito"; el descanso, cálido con viñeta suave.
  - **3D nuevos:** pluma ("piernas ligeras"), batería que se recarga ("cansada" → "no quieres abandonar"), almohada que se hunde ("apoyadas sobre una almohada") y sello "Día 7 cumplido" (cuadro: "marca el día cumplido"); racha de 7 días que se completa en "cumpliste".
  - **2D nuevos:** elección silla/cama, chips "ascendentes · lentos · continuos", palabra tachada "rápido" → "mantén el movimiento", insignia de velocidad ×2/×3.
- Maqueta: columnas a los lados de la cabeza (`bajoCabeza`: si no cabe al lado, siguen por debajo); tomas sin cabeza (tumbada, pantalla partida) marcadas como tales; YuNet descarta detecciones por debajo de la mitad del cuadro (falsos positivos).
- Intensidad: "suave" (perilla al nivel 1) y "Calor: opcional", nunca "calor máximo" (cuadro del día 7).
- Mezcla: voz a −25,6 LUFS sin tocar; música y efectos ×0,35.

## 16. Composición aplicada en el día 8 · "Evaluación del Día 10"
- A cámara (sentada, camiseta blanca), crudo 1080×1920 a 59,94 fps → 30 fps, sin recorte. 3:01 → 0:50 con solo las tomas buenas (`scripts/dia8/preparar.py`): fuera los dos primeros intentos de "vuelve a calificar…" y "…la sensación de la piel" (se corrige), "Toña", el arranque "vas a tomarte las mismas", la primera toma de "revisa si aparecieron moretones…" (repetida mejor) y el intento a medias de 125–129 s. Del final de la primera toma se conserva "de lo contrario puedes seguir con la rutina el resto de estos 10 días", que va detrás de la segunda: por eso el montaje es por tramos (no `select`, que conserva el orden del crudo), con audio a muestra exacta (sincronía 0 ms en todos los tramos).
- Lenguaje nuevo frente a los días anteriores: título que sube desde una línea invisible con un subrayado de pincel Durazno (cifras en Glacial Bold), transición en círculo (iris) entre secciones, tarjeta "Evaluación Día 10" con los 4 pasos (sensaciones, fotografías, piel, constancia) que se van marcando, confeti de marca en "¡Felicitaciones!".
- Recursos según la frase: calendario 3D de marca nuevo cuyas hojas pasan 7·8·9 hasta el 10 y se marca (cuadro: "marca el Día 10"); lupa ("vamos a revisar"); escala del 1 al 5 de pesadez, suavidad e inflamación con un cursor que la recorre sin fijar nota; cámara 3D del día 2 y lista "igual que el día 1" (misma ropa, luz, distancia y postura, del cuadro); **polaroids** de frente, costado, espalda y el otro costado que caen con flash y obturador en cada palabra (fotogramas del crudo 2 del día 7, con la piel sin enrojecer; el otro costado es el costado reflejado); fragmentos de ≈1 s de las piernas con una lupa y "¿Moretones?" / "¿Irritación?"; botón de pausa 3D ("suspender"); tarro de crema 3D que se abre ("o por una crema más suave"); fragmento del equipo en la pantorrilla ("puedes seguir con la rutina") y camino de 21 días con 10 hechos y 11 por delante (cuadro: "muestra los días pendientes"); tarjeta No/Sí ("perfección", "cambios rápidos" tachados → "adaptarte a una rutina"); lista "según: constancia, manejo del producto, tus sensaciones".
- Zoom 1,12 solo en frases clave dichas más alto ("felicitaciones, llegaste", "puedas adaptarte", "tus objetivos"; regla 12).
- Mezcla: voz a −29,2 LUFS sin tocar; música y efectos ×0,15 (música ≈ 16 dB bajo la voz).


## 17. Composición aplicada en el día 9 · "Rutina integrada"
- Rutina con voz en off (como los días 4–7) sobre su propio crudo de 10:25 (1080×1920 a 59,94 fps → 30 fps; mismo set de cortina del día 6). El audio del crudo no se usa.
- Voz en off: 1:53 → 1:09 con solo las tomas buenas (fuera la primera toma de "Aplica el aceite únicamente en la zona…", con una pausa a mitad de frase, y la primera toma de los brazos, que vacila en "sobre el… codo" y se repite entera con "articulaciones") y silencios > 0,3 s. Tiempos por palabra sacados de la voz ya limpia (`scripts/dia9/retiempos.py`).
- Tomas por frase (`scripts/dia9/montar.py`, 26 tomas, ≈ 2,7 s de media): fuera los momentos en que mira a cámara o habla con quien graba. Primeros planos del crudo (cámara en mano, sin cara) como apoyo: el aceite en la palma ("aplica el aceite"), los muslos (pizarra de líneas) y la mano por la ingle ("bajando por la ingle").
- Pedido: que no sea monótono y se diferencie de los días anteriores sin perder la secuencia. Lenguaje nuevo:
  - **Mosaico 2×2 de las cuatro zonas** (piernas, abdomen, glúteos, brazos) al empezar, con su rótulo en "diferentes zonas", que se abre hacia las esquinas en "una sola rutina"; vuelve en el cierre ("para trabajar diferentes zonas") con un ✓ en cada celda.
  - **Tarjeta de capítulo** en cada zona: la toma se encoge a una tarjeta con esquinas redondeadas sobre Marfil y arriba entra el capítulo (número en círculo Salvia, kicker con los minutos, título TAN Pearl Petróleo que se revela tras un bloque Durazno) y la barra de los 5 tramos del cuadro (1·6·4·3·1 min) que se llena. En el cierre los minutos cuentan hasta 15 y se llenan todos los tramos. Después queda una píldora pequeña con el paso y 5 puntos.
  - **Pizarra de análisis sobre fotogramas congelados** (flash + obturador, esquinas de visor y foco): líneas que suben por el muslo ("divide la zona en líneas"), prohibido sobre el ombligo ("evita pasar directamente sobre el ombligo") y ✕ en codo y axila con la franja segura "del codo al hombro" ("no pasar sobre las articulaciones"; cuadro: "evitando axila y articulaciones").
  - **Barridos** (desenfoque horizontal) en 6 cortes dentro de una zona; reencuadres lentos hacia el muslo, el abdomen y la cintura.
  - **Pantalla partida vertical** en "haz círculos amplios alternando ambos lados": un lado y el otro a la vez, con círculos que giran y el lado activo que alterna en "alternando", "ambos" y "lados".
  - **Notas claras** (Marfil con borde Durazno y ✓ Salvia) en vez de las tarjetas oscuras de los días anteriores; ruta del arrastre (espalda → cintura → ingle) e interruptor manos/equipo.
  - **3D nuevos** (sin calendario, a petición): rompecabezas de las 4 zonas que encaja en "una sola rutina", gota que cae y se extiende solo dentro del anillo de la zona con el equipo que se desliza ("únicamente en la zona… deslizamiento"), reloj de arena que se da la vuelta en "3 minutos" (piernas y glúteos), chevrones que se encienden de abajo arriba ("líneas ascendentes desde la parte baja"), maniquí de torso (abdomen y laterales se encienden, prohibido en el ombligo, bola que da círculos amplios alrededor del ombligo y estelas desde la espalda hacia la ingle), medidor de intensidad (aguja en la zona baja; en "dolorosa" se tacha la zona alta), espiral que pasa de círculos a barridos ascendentes, reloj de tarjetas 00 → 30 ("30 segundos") y medalla de 15 min.
- Del cuadro, aunque la voz no lo dice: "Al terminar: apaga y limpia el equipo" en el cierre.
- Música propia del día 9 (Re mayor, 92 BPM, arpegio sincopado tipo marimba; mismos timbres y limpieza para la voz). Mezcla: voz a −25,8 LUFS sin tocar; música y efectos ×0,34.
- Entrega: render CRF 16 por tramos (107 MB) y, para el repositorio (< 100 MB), x264 a 2 pasadas a 10 Mbps + copia del audio (90 MB); copia ligera de 28 MB. Mezcla medida sobre el render: voz con ganancia 1,0 y desfase 0, música y efectos 17 dB por debajo y ningún efecto por encima de la voz.

## 18. Composición aplicada en el día 10 · "Día 21 y continuidad" (último del reto)
- A cámara (sentada, camiseta blanca; mismo set del día 8), crudo 1080×1920 a 59,94 fps → 30 fps, sin recorte. 2:10 → 1:03 con solo las tomas buenas (`scripts/dia10/preparar.py`, sincronía 0 ms en los 21 tramos): fuera el primer "Felicitaciones, llegaste al día 21" (lo repite y la segunda enlaza con "y más allá…"), el "y lo más importante, revisando cómo se va a…" que se corta y se repite entero, las esperas en silencio con voces de fondo ("Antonia", "¡María Antonia!"), un "y ya está" casi inaudible y el primer "ahora cuéntanos". Whisper fundía las repeticiones en palabras de varios segundos: los tiempos salen de transcribir el vídeo ya editado (`scripts/dia10/retiempos.py`).
- En la grabación dice "aumentando la presión" donde el guion dice "dos o tres veces por semana": el audio no se toca y no se rotula la presión; del cuadro se muestran los 2–3 días por semana y "respetando las indicaciones del producto".
- Pedido: que no sea monótono y se diferencie de los días anteriores sin perder la secuencia. Lenguaje nuevo:
  - **Títulos pegatina**: TAN Pearl Petróleo sobre una pegatina Durazno con borde Marfil, que se pega con un golpe (escala y giro); el kicker en una etiqueta Petróleo inclinada al revés. Siempre por encima de la zona de la cara.
  - **Ventana con forma de 21**: el vídeo se abre a través de un 21 que crece (inicio) y los cambios de bloque grandes (registro, testimonio) se cierran y se abren con él.
  - **Panel lateral**: en medidas, comparación y continuidad la toma se desliza 190 px y entra un panel Marfil (filo Durazno) con su título y su contenido; en la comparación entra por el otro lado. La cara sigue entera y lejos del panel.
  - **Cámara de móvil** para las 4 fotos ("de frente, de costado, de espalda y luego del otro costado"): fragmentos cortos con cuadrícula, "IGUAL QUE EL DÍA 1", disparador, miniaturas de las fotos ya hechas, destello y obturador (fotos del día 8).
  - **Montaje rápido de la rutina** como b-roll en "debes seguir repitiendo esta misma rutina de aquí en adelante": piernas, abdomen, glúteos y brazos del crudo del día 9 (≈0,9 s cada uno, con barrido entre ellos y la zona encendida abajo).
  - **Mensajes de chat** que suben en "cuéntanos vía WhatsApp… cuáles fueron tus resultados" (con los puntos de escribiendo).
  - **2D nuevos**: anillo de 21 días que se completa en "pudiste hacer de esto una rutina", lista del registro final (medidas · fotos), ficha de medidas Día 1 / Día 21 que se va escribiendo, Día 1 y Día 21 lado a lado con "sin filtros · sin retoques" (siluetas: nunca fotos de "antes y después"), notas tipo etiqueta.
  - **3D nuevos** (sin calendario, a petición): globos metálicos "21" que suben y estallan en estrellas ("día 21", "gran logro", "una rutina"), móvil en trípode que dispara ("te vas a tomar las fotos en las mismas posiciones"), maniquí con cinta métrica que se enrolla en cintura y cadera con chinchetas en los mismos puntos, corazón que late ("no puedes frustrarte") y se multiplica ("puede motivar a otras mujeres"), semana con L·X·V marcados, frasco Drena Oil ("instrucciones del producto"), espejo de mano ("cómo se va comportando tu piel") y globo de diálogo que escribe ("cuéntanos").
- Zoom 1,12 solo en frases clave dichas más alto (regla 12), nunca con panel, cámara de móvil o montaje.
- Música propia del día 10 (Sol mayor, 96 BPM, campanas suaves; mismos timbres y limpieza para la voz). Voz original a −28,9 LUFS sin tocar; música y efectos ×0,19 (medido sobre el render: voz con ganancia 1,0 y desfase 0, música y efectos 15,8 dB por debajo y ningún efecto por encima de la voz).
- Render: el vídeo como secuencia de JPEG + voz en WAV (con el MP4 se colgaba y con VP9 daba fotogramas negros), en tramos de 100 fotogramas con reintento a los 5 min (los cuelgues del 3D por software fueron frecuentes); 0 fotogramas negros. Entrega: CRF 16 (75 MB) → 2 pasadas a 10 Mbps para el repositorio (82 MB) y copia ligera de 27 MB.
