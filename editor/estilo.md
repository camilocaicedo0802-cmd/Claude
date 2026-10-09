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

## 3. Subtítulos (palabra a palabra) — todo [SUPOSICIÓN]
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

## 11. Composición aplicada en el borrador (pendiente de tu visto bueno)
- Fuente 4K (2160×3840) recortada sin escalar a 1620×2880 (`crop=1620:2880:270:268`): plano medio con la cara al 43 % de altura.
- Zoom alterno por corte: 1,00× (plano medio) ↔ 1,22× (plano medio corto), origen en la cara (52 %, 43 %); empuje lento +2,5 % por plano; golpe +6 % en la palabra clave.
- Zonas: títulos y = 110–600 (pared, con velo Verde petróleo 62 %→0 en el tercio superior) · tarjetas y = 980–1360 (torso) · subtítulos desde y = 1390 (pantalón oscuro, zona segura de Reels).
- Cortes: silencios > 0,3 s a −35 dB con 0,08 s de margen · voz a −14 LUFS.
