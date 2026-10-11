# estilo.md — Análisis del vídeo de referencia (`referencia/referencia.mp4`)

Método: fotogramas extraídos con ffmpeg a 2 fps (41) + fotograma en cada cambio de plano (detección `scene` > 0,08 y diferencia de luma por fotograma), audio separado a WAV, beats/onsets medidos por bandas (kick 30–120 Hz, snare 1,5–5 kHz) y letra transcrita con Whisper (`small`, tiempos por palabra → `referencia/referencia_whisper.json`).
Todo lo que no se pudo medir directamente va marcado con **[SUPOSICIÓN]**.

---

## 1. Formato técnico

| Parámetro | Valor |
|---|---|
| Resolución | 720 × 1280 (vertical 9:16) — exportaremos a **1080 × 1920** |
| FPS | 30 |
| Duración | 20,60 s |
| Vídeo | H.264, ~1,4 Mbps |
| Audio | AAC 44,1 kHz estéreo, ~53 kbps |

## 2. Ritmo de cortes

**8 planos, 7 cortes, todos por corte seco (hard cut).** Duración media de plano: **2,58 s** (mín. 1,53 s, máx. 3,33 s).

| # | Entrada → salida | Duración | Diseño | Tamaño de plano | Movimiento de cámara |
|---|---|---|---|---|---|
| 1 | 0,00 → 2,33 | 2,33 s | ESPALDA (retrato grande) | General: camiseta entera sobre rejilla, girada ~15° | Cámara en mano, *push-in* + rotación leve; a 2,0 s acelera el acercamiento (diferencia de imagen ×3) |
| 2 | 2,33 → 5,33 | 3,00 s | ESPALDA | Detalle macro: boca/grillz + cadenas, llena el encuadre | Mano, paneo lento hacia abajo/derecha, ligeramente inclinado |
| 3 | 5,33 → 6,87 | 1,54 s | ESPALDA | Macro: cara (gorra, gafas, grillz) | Mano, deriva lenta (se aleja ligeramente) |
| 4 | 6,87 → 10,20 | 3,33 s | DELANTERO (logo "NATANAEL Cano") | Primer plano del pecho sobre rejilla | Paneo lateral: el texto se desplaza de centro a salir por la derecha→izquierda del encuadre |
| 5 | 10,20 → 13,20 | 3,00 s | ESPALDA | Macro: cara + cadenas, inclinado ~10–15° | Mano, deriva lenta |
| 6 | 13,20 → 14,73 | 1,53 s | ESPALDA | Macro: cara, encuadre algo más abierto (*jump cut* sobre el mismo diseño) | Casi fijo |
| 7 | 14,73 → 17,33 | 2,60 s | ESPALDA | General: camiseta entera, recta, sobre rejilla | Prácticamente estático (diferencia de imagen ~2, la más baja del vídeo) |
| 8 | 17,33 → 20,60 | 3,27 s | DELANTERO | General: camiseta entera, recta → termina girada | Mano, rotación lenta hacia el final |

- **Proporción de pantalla:** ESPALDA **14,0 s (68 %)** · DELANTERO **6,6 s (32 %)** → encaja con tu requisito (espalda protagonista).
- **Estructura:** general espalda → 2 macros espalda → delantero → 2 macros espalda → general espalda → general delantero (cierre).
- **Patrón de duraciones:** alterna planos largos (~3 s) y cortos (~1,5 s): 2,3 · 3,0 · **1,5** · 3,3 · 3,0 · **1,5** · 2,6 · 3,3.
- **Sincronía con la música:** 1 corte ≈ 1 frase de la letra (las frases duran ~2,5 s). Los cortes caen a **±0,1 s de un golpe fuerte** (snare/voz): 5,33↔5,29 · 6,87↔6,78 · 10,20↔10,09 · 13,20↔13,22 · 17,33↔17,43. No siguen una rejilla de compás estricta. [SUPOSICIÓN] el editor cortaba "a oído" en el acento de la frase, no a cuadrícula.

## 3. Subtítulos

- **No hay subtítulos.** Ninguno de los 41 fotogramas contiene texto superpuesto.
- La letra de la canción **no** se muestra en pantalla.
- Fuente / tamaño / posición / palabras por bloque / animación / palabra destacada: **no aplica (0 bloques)**.

## 4. Textos en pantalla

- **Ningún texto gráfico añadido.** Todo el "texto" que se ve es la propia estampa de la camiseta.
- Único elemento sobreimpreso: **marca de agua "LucifeR mx"** (cuenta del creador), sans-serif fina, ~14 px de alto sobre 1280, gris oscuro semitransparente (~40 % opacidad), centrada-derecha en **x ≈ 520–605 px, y ≈ 1195 px** (≈ 93 % de la altura), fija durante todo el vídeo. → **No la copiaremos** (es de otra marca). [SUPOSICIÓN] si tienes tu propio @ o logo podríamos poner uno equivalente en la misma posición.
- **Tipografía de la marca (impresa en la camiseta, la que tomaremos como guía si hace falta texto):**
  - "NATANAEL": sans-serif geométrica, mayúsculas, extra-bold, ancha, con textura plateada/cromada desgastada (*distressed*), las "A" sin travesaño.
  - "Cano": script/manuscrita fina, cursiva, plateada, solapada bajo la "EL".
  - [SUPOSICIÓN] equivalentes libres: *Michroma* / *Orbitron Black* / *Montserrat ExtraBold* con textura para la primera; *Mr Dafoe* / *Allison* para el script.

## 5. B-roll

- **No hay b-roll externo.** Los 8 planos son de la propia camiseta. El "b-roll" son los **planos macro del estampado** (planos 2, 3, 5, 6 = 9,1 s, 44 % del vídeo) que funcionan como detalle.
- Nunca aparece una persona vistiendo la camiseta: siempre **flat-lay** sobre el suelo.

## 6. Transiciones

- **0 transiciones**: todos los cambios son cortes secos (verificado fotograma a fotograma ±3 frames en cada corte: sin fundidos, flashes, desenfoques ni *whip* digital).
- La única sensación de "transición" es el **acelerón de cámara real** al final del plano 1 (1,9–2,3 s) justo antes de cortar al macro.
- Un *jump cut* (13,20 s) entre dos macros del mismo diseño con distinto encuadre.

## 7. Zooms y movimiento

- **Sin zoom digital detectable**: todo el movimiento es de cámara física (móvil en mano).
- Movimientos tipo: *push-in* (plano 1), paneo lento (2, 4), deriva/rotación lenta 5–15° (3, 5, 8), estático (6, 7).
- Encuadres a menudo **inclinados 10–20°** (holandés) en macros y en el plano inicial.
- [SUPOSICIÓN] Si tus tomas son más estáticas, simularé este movimiento en Remotion con un zoom digital suave (escala 1,00 → 1,06 por plano) y rotación de ±2°, nunca más.

## 8. Color

| Medida | Valor |
|---|---|
| Luminancia media | **35/255** (muy oscuro, *low-key*) |
| Negros (percentil 2) | 0–3 → **negros aplastados** |
| Mediana de luma | 4–10 en planos con camiseta (el negro domina el cuadro) |
| Altas luces (percentil 98) | **118–188** → no llegan a blanco puro (aspecto mate) |
| Dominante | **cálida**: R > G > B en ~+3 a +6 por canal (p. ej. RGB medio 34/32/29) |
| Viñeta | ninguna (centro 42,9 vs esquinas 44,6) |
| Saturación | baja salvo piel y oro |

**Paleta medida (hex):**
- Camiseta negra: `#060508`
- Suelo de piedra/cemento: `#837768`
- Plata del texto / brillos: `#C8C9CE`
- Cadenas/diamantes: `#B4B4AB`
- Oro de los tréboles: `#997D60`
- Piel del retrato: `#B49775`
- Rejilla metálica: negro ≈ `#0A0A0A`

**Escenario:** camiseta extendida sobre **2 paneles de rejilla metálica negra** (cuadrícula ~4 cm) apoyados en suelo de piedra beige-gris. Luz cenital suave, sin sombras duras.
→ Grading a aplicar: bajar exposición ~-0,5 EV, contraste alto con negros a 0, altas luces limitadas a ~200/255, temperatura ligeramente cálida (+5 en R, −3 en B), saturación −15 %. [SUPOSICIÓN] valores de corrección deducidos del resultado, no del proyecto original.

## 9. Sonido

- **Solo música**, sin voz en off, sin efectos (whoosh, clicks…). [SUPOSICIÓN] no se aprecian SFX en el análisis espectral.
- Canción: corrido tumbado / trap en español (letra: *"Que les moleste el brillo que yo cargo / Me vale verga, yo sigo brillando…"*). Tempo medido **~143,5 BPM** en la detección de golpes (~95,7 BPM en sensación ternaria; frase ≈ 2,5 s).
- Fragmento elegido: **8 frases seguidas** de la letra (≈ 20 s) — empieza en el inicio de una frase y termina al final de otra.
- Volumen: **-14,1 LUFS integrados**, LRA 0,5 LU (muy comprimido, nivel estándar de redes).
- Entrada: microfade de ~0,25 s. Salida: **corte seco** sin fade-out.
- La letra encaja con el producto ("brillo", "prendas en hielo bien adiamantado") → el tema refuerza los macros de diamantes/grillz.

## 10. Aplicación a mi vídeo (reglas que seguiré)

1. Duración objetivo **~20 s**, 8 ± 1 planos, cortes secos, media 2,5 s/plano, alternando largo (~3 s) y corto (~1,5 s).
2. **Espalda ≥ 65 % del tiempo**, delantero ~30 %. Abrir con plano general de la espalda; cerrar con plano general del delantero.
3. Cada corte en el **golpe fuerte más cercano** al inicio de frase de BOMBASTIK (±0,1 s).
4. Sin subtítulos ni rótulos (salvo que me pidas lo contrario); sin transiciones.
5. Grading oscuro/cálido según la tabla de color; exportación 1080×1920, 30 fps, -14 LUFS.
