# estilo.md — Análisis de la referencia (@danushkmotion)

Fuente: `referencia/referencia.mp4` · 576×1024 · 29,97 fps · 18,26 s · AAC estéreo 44,1 kHz.
Material extraído: `referencia/frames/` (37 fotogramas, 2 por segundo), `referencia/cortes2/` (10 cambios de plano,
umbral de escena 0,08), `referencia/audio_ref.wav`, `referencia/palabras_ref.json` (transcripción con tiempos por palabra),
`referencia/espectro.png`, tiras de 15 fps en las transiciones (`referencia/m_*.png`).

Todas las medidas en px se dan **convertidas a 1080×1920** (factor ×1,875 respecto al original de 576×1024).

---

## 1. Estructura y ritmo de cortes

No hay cortes duros: es **un solo plano continuo de motion design**. Los "cortes" son transiciones animadas de 4 a 8 frames.

| # | Tiempo (s) | Composición | Entrada | Salida |
|---|-----------|-------------|---------|--------|
| 1 | 0,00–2,80 | Palabras sueltas → píldora "problem?" → la píldora **se transforma** en tarjeta vertical con silueta | blur-in por palabra | push-in + inclinación 3D + blur direccional (6 fr) |
| 2 | 2,80–4,07 | Tarjeta horizontal con foto recortada + nombre | escala desde rectángulo pequeño desenfocado (4 fr) | sube 110 px y crece ×1,05 (5 fr) |
| 3 | 4,07–10,81 | Misma tarjeta arriba + lista con conector vertical (5 ítems) | ítems uno a uno con la voz | barrido horizontal a la izquierda con motion blur (8 fr) |
| 4 | 10,81–12,75 | Texto solo "the allrounder" | blur-in por palabra | zoom-through (4 fr) |
| 5 | 12,75–13,91 | Foto recortada B/N a sangre inferior + píldora "JOHNY" + "can do everything" | zoom ×1,3→×1,0 desenfocado→nítido (4 fr) | barrido arriba-izquierda con blur (5 fr) |
| 6 | 13,91–16,65 | Píldora pequeña que crece → personaje emerge desde detrás de la píldora + "that's my job" | scaleX 0→1 (6 fr) + máscara (8 fr) | barrido a la izquierda con blur (6 fr) |
| 7 | 16,65–18,26 | Cierre tipográfico "let's make something good." | blur-in por palabra | — (último frame sostenido 0,8 s) |

- **Cambios de composición:** 6 en 18,26 s → **1 cada 2,6 s** de media (mín. 1,2 s, máx. 6,7 s).
- **Micro-eventos** (aparición de palabra, ítem, píldora, cambio de posición): **1 cada 0,25–0,5 s**. Nunca hay más de 0,6 s sin que algo se mueva.
- Las transiciones caen sobre el inicio de la frase siguiente de la voz (desfase 0 a −3 frames).
- Picos del detector de escena (ffmpeg `scene`): 2,80 (0,38) · 2,84 (0,56) · 4,07 · 10,81 · 12,75 · 13,91 · 16,65.

## 2. Texto en pantalla (kinetic typography — no hay subtítulos tradicionales)

- **No hay subtítulos abajo.** El texto ES la gráfica: vive en el tercio central/superior (y = 400–1150 px) o dentro de las tarjetas.
- **Fuente:** grotesca neo-sans, peso 700–800, **itálica** (inclinación ≈ 10–12°), tracking negativo ≈ −4 % (letras casi tocándose: "fixit all", "allrounder"). Equivalente: **Inter ExtraBold Italic (800)**.
- **Palabras por bloque:** 1 a 3 palabras por bloque. Estructura fija: **palabra pequeña de entrada + palabra grande clave** ("ever had / **problem?**", "one guy could / **fix it all**", "that's / **my job**", "let's make / **something** / good.").
- **Tamaños (a 1080 px de ancho):**
  - Palabra clave grande: 150–190 px de cuerpo (ancho de bloque 600–680 px = 55–63 % del ancho).
  - Palabra clave dentro de píldora: 110–130 px.
  - Palabras de entrada (pequeñas): 40–55 px, situadas encima y alineadas a la izquierda de la grande, solapando 10–15 px.
  - Texto secundario dentro de tarjeta ("not an editor"): 22–26 px.
  - Lista: 34 px, interlineado 70 px.
- **Colores de texto:**
  - Sobre fondo claro: palabra clave **#3E1D49** (morado casi negro); palabras de entrada **#816D85–#906F9D** (morado grisáceo claro).
  - Sobre tarjeta morada: **#FFFFFF** con degradado sutil a #E6E0E8 abajo.
- **Palabra destacada:** se invierte → texto blanco dentro de una **píldora morada** (#35193F→#4D3157, radio = alto/2, sombra suave). Ej.: "problem?", "JOHNY", "good.".
- **Animación de entrada por palabra (6 frames ≈ 0,2 s):** opacidad 0→1, desenfoque 10 px→0, desplazamiento x +20 px→0, escala 0,96→1. Curva ease-out expo. Cada palabra entra en el frame exacto en que se pronuncia.
- **Píldora:** nace como una cápsula vertical de 12×40 px (3 frames), se expande en horizontal hasta su ancho final en 6 frames con un ligero overshoot (≤3 %), y el texto se escribe dentro.
- **Salida:** nunca un fade simple; el texto sale con la cámara (barrido + motion blur).

## 3. Tarjetas y elementos gráficos

- **Fondo:** #F0F0F0 plano (muestreado) + **retícula de puntos** #E3E3E3, paso 30 px, diámetro 3 px, ocupando un área con margen de 120 px laterales y 215 px arriba/abajo (no llega a los bordes).
- **Arcos punteados:** 2–3 arcos de circunferencia grandes (radio 550–700 px) que entran por las esquinas; trazo 3,5 px, guion 15 px, hueco 11 px, color #8E8C91. Giran lentamente (≈ 12°/s) y aceleran en cada transición (≈ 90° en 8 frames).
- **Tarjeta morada:** degradado lineal 135° de #4D3157 (esquina superior izquierda) a #35193F (centro) a #5A2A6A (esquina inferior derecha), radio de esquina 26 px. Brillo especular diagonal blanco al 8–12 % que barre la tarjeta.
  - Tarjeta vertical: 800×1040 px. Tarjeta horizontal: 840×660 px. Píldora barra: 710×186 px.
- **Sombra:** `0 22px 55px rgba(20,8,26,0.28)` + sombra de contacto `0 6px 12px rgba(20,8,26,0.18)`.
- **Recortes fotográficos:** personas recortadas en **blanco y negro** de alto contraste (curva S), que **rompen el borde superior** de la tarjeta (la cabeza sale por encima). El texto grande queda **detrás** de la persona (capas: tarjeta → texto → persona) para dar profundidad.
- **Conectores:** línea vertical de 3 px #3E1D49 que baja desde la tarjeta + puntos de 14 px en cada ítem de la lista; la línea se dibuja (stroke-dashoffset) antes de cada ítem.
- **Elementos 2D/3D:** emoji/ilustración 3D sale desde detrás de la píldora (máscara en el borde superior); la tarjeta se deforma en 3D (rotateY ±25°, perspectiva 1200 px) en los push-in.

## 4. B-roll

- No hay b-roll a pantalla completa ni vídeo convencional. Todo el material visual (fotos, siluetas, personajes) va **dentro de tarjetas o recortado sobre el fondo blanco**.
- Fotos en B/N (saturación 0 %, contraste +25 %); el color lo aportan solo las tarjetas moradas.

## 5. Transiciones (catálogo medido)

| Tipo | Duración | Detalle |
|------|----------|---------|
| Morph de objeto compartido | 15 fr (0,5 s) | píldora → tarjeta horizontal → tarjeta vertical; ease-in-out cúbica |
| Push-in 3D | 6 fr | escala 1→1,6, rotateY 0→−20°, blur direccional 25 px, la siguiente tarjeta nace pequeña y desenfocada |
| Reposición | 5 fr | toda la composición sube 110 px; ease-out quint |
| Barrido horizontal | 6–8 fr | x 0→−1200 px con motion blur horizontal (≈ 40 px); arcos giran a la vez |
| Zoom-through | 4 fr | entrante escala 1,3→1,0 y blur 20→0 px |
| Crecimiento de píldora | 6 fr | scaleX 0→1 desde el centro |
| Revelado por máscara | 8 fr | objeto sube 150 px desde detrás del borde de la tarjeta |

Curvas: siempre **ease-out fuerte** (expo/quint) para entradas y **ease-in** rápido para salidas; nada lineal; rebote máximo 3 %.

## 6. Zooms y cámara

- Cámara virtual con micro-deriva constante: escala 1,00→1,04 durante cada composición (≈ 2 %/s).
- Zooms bruscos solo como transición (push-in ×1,6 en 6 frames). 1 zoom fuerte cada ~5 s; nunca dos seguidos en el mismo sentido.
- Parallax: fondo/retícula se mueve al 30 %, arcos al 60 %, tarjetas al 100 %, recortes al 115 %.

## 7. Color

| Uso | HEX muestreado | Nota |
|-----|----------------|------|
| Fondo | **#F0F0F0** | (el brief proponía #F5F5F5; se corrige al valor medido) |
| Puntos de retícula | #E3E3E3 | |
| Tarjeta base | **#35193F** | percentil 50 de los píxeles morados |
| Tarjeta luz | #4D3157 | esquina superior izquierda / brillo |
| Tarjeta acento | #5A2A6A | esquina inferior derecha (secundario; brief #714181) |
| Texto clave sobre blanco | **#3E1D49** | |
| Texto de entrada | #816D85 | |
| Arcos punteados | #8E8C91 | |
| Texto sobre tarjeta | #FFFFFF | |
| Negro de recortes | #161616 | |

Sin grano, sin viñeta, sin aberración. Fotos desaturadas al 100 %.

## 8. Sonido

- **Música:** groove electronic hip-hop / funky, **≈ 104 BPM** (beat cada 0,577 s, detectado con librosa), bombo y bajo marcados, hats con swing.
- La música hace **cortes de silencio total** (stops) en 4,0 · 6,5 · 7,6 · 10,4–10,6 · 15,5 s para que la voz y una gráfica "peguen"; regresa en el siguiente tiempo fuerte con un golpe grave.
- **Efectos:** transientes agudos (5–10 kHz) en casi cada aparición de palabra/ítem (clicks/pops, ~1 cada 0,4 s); whoosh en cada barrido; sub-impact (< 80 Hz) en 4,0, 8,5 y 11,0 s.
- **Mezcla:** integrado **−15 LUFS**; voz siempre delante (música ≈ −14 dB bajo la voz, efectos ≈ −8 dB).
- **Voz:** en off, conversacional, sin pausas largas (máx. 0,5 s entre frases).

---

## 9. Adaptación al proyecto (decisiones derivadas)

- Locución del cliente (`assets/voz.mp3`, 38,2 s) → recortar silencios a ≤ 0,25 s y acelerar ×1,15 (sin cambiar el tono) para quedar en **≈ 29–30 s**.
- Fuente: **Inter 800 Italic**, tracking −0,04 em.
- Paleta final: fondo #F0F0F0, tarjeta #35193F→#472052→#714181, texto #3E1D49 / #816D85, blanco #FFFFFF, negro #161616.
- Recursos de edición (timeline, curvas, ruedas de color, ondas, cámara 3D, móvil vertical) siempre dentro de tarjetas moradas o recortados con sombra, unidos por conectores punteados.
