# Análisis de la referencia (solo la parte "After")

Archivo analizado: `Referencia_video_automotriz.mp4` · 720×1280 · 29,97 fps · 20,02 s · 600 fotogramas.
El video es una vitrina "Before / After": el panel **After** (≈376×668 px dentro del cuadro) es el anuncio terminado.
Se revisaron los 600 fotogramas del panel After uno por uno (hojas de contacto fotograma a fotograma), con detección de cortes por cambio de escena y análisis espectral del audio.

> El anuncio en sí dura **0,00–17,75 s (fotogramas 0–532)**. De 17,78 s al final (533–599) es la tarjeta blanca del editor ("DM ME 'ADS' TO SCALE YOUR BUSINESS"), que no forma parte del anuncio.

## 1. Ritmo y estructura

- **15 planos en 17,75 s → un plano cada ~1,2 s.** Nunca hay más de 1,8 s sin un cambio visual (corte, escena gráfica o título nuevo).
- Cada corte cae en una pausa de la voz o en una palabra clave; el título de esa palabra entra en el mismo fotograma del corte.
- Estructura: **Hook** (nombre + pregunta) → presentación del auto → lista de servicios con escenas gráficas → problema (en rojo) → proceso → resultado ("LOOKING BRAND NEW").

| Fotogramas | Tiempo | Plano / escena | Texto y animación |
|---|---|---|---|
| 0–9 | 0,00–0,33 | Habla a cámara, plano medio | "Chris!" amarillo, heavy italic con glow (pop) |
| 10–36 | 0,33–1,23 | Mismo plano, push-in lento | "WHAT DOES / THIS CAR NEED?" letra por letra (~1 letra por fotograma, cada letra entra con desenfoque y escala) |
| 37–41 | 1,23–1,37 | Mismo plano | Subtítulo pequeño "This" |
| 42–67 | 1,40–2,24 | **Corte** a plano general (entra el beat) | "BEAUTIFUL" gigante entra grande y desenfocado con estela y se asienta en 2–3 fotogramas; "This" pequeño encima; pastilla negra "G80" entra desde la derecha (45–47) |
| 68–84 | 2,27–2,80 | Corte a otro ángulo | Subtítulo en minúsculas, palabra por palabra ("needs a nice") |
| 85–138 | 2,84–4,60 | **Escena gráfica oscura** (degradado negro → amarillo) | Tarjeta de video redondeada entra con zoom-blur (85–87); etiqueta en caja "INTERIOR and EXTERIOR"; segunda tarjeta desliza desde la derecha (108); segunda línea más grande "DEEP CLEANING" (119–121) |
| 139–187 | 4,64–6,24 | **Escena clara** (blanco → amarillo) con tarjeta y corchetes en las esquinas | Subtítulos dentro de la tarjeta, palabra por palabra |
| 188–209 | 6,27–6,97 | **Tarjetas 3D flotantes** en perspectiva sobre fondo oscuro | Etiqueta "DEEP VACUUM" (pop en 189, asienta en 190) |
| 210–263 | 7,01–8,78 | **Collage** de tarjetas que se desplaza verticalmente | Etiqueta roja "Smear marks" + X roja gigante + resplandor rojo (problema) desde 221 |
| 264–309 | 8,81–10,31 | Plano caminando junto al auto | "AS YOU CAN SEE / ON THE EXTERIOR" palabra por palabra |
| 310–354 | 10,34–11,81 | Macro del neumático | "THE WHEELS ARE VERY" → **"CAKED / UP"** rojo biselado, golpe escalonado (335–339) |
| 355–370 | 11,85–12,35 | Plano general | "SO WE'RE GOING TO DO" |
| 371–401 | 12,38–13,38 | Escena oscura con tarjeta | Etiqueta "A DEEP WHEEL / CLEANING" |
| 402–423 | 13,41–14,11 | Plano caminando | "WE'RE ALSO GOING TO DO A" |
| 424–457 | 14,15–15,25 | Macro de espuma | "CONTACT / WASH" (palabra pequeña sobre palabra grande) |
| 458–507 | 15,28–16,92 | Secado | "AND / DRY", luego "MAKE SURE THIS PAINT'S" |
| 508–532 | 16,95–17,75 | Plano final del auto | "LOOKING / BRAND NEW" |

## 2. Tipografía y texturas

Hay siete estilos de texto, siempre en mayúsculas salvo los subtítulos pequeños:

1. **Título principal**: sans muy pesada, cursiva, interletrado apretado. Relleno con degradado vertical (claro arriba → color abajo), glow del color de acento, extrusión dura de 2–4 px hacia abajo y sombra suave. Ejemplos: "BEAUTIFUL", "WHAT DOES THIS CAR NEED?".
2. **Palabra de impacto**: color negativo (rojo) biselado con borde claro, capas de extrusión oscuras y resplandor rojo. Primero entra la palabra pequeña y 3 fotogramas después la grande ("CAKED / UP").
3. **Etiqueta en caja**: caja del color de acento con brillo exterior; la palabra de unión va más pequeña ("INTERIOR *and* EXTERIOR"). La segunda línea es más grande y hace crecer la caja.
4. **Subtítulos minimalistas**: blanco, bold, 2 líneas de 2–4 palabras, al centro del cuadro. Cada palabra entra tenue o gris, con un desplazamiento de 10–20 px y algo de desenfoque, y en ~4 fotogramas queda en blanco sólido.
5. **Wide / extendida**: palabra pequeña encima de una grande, blanca y metálica con sombra ("CONTACT WASH", "AND DRY", "LOOKING BRAND NEW").
6. **Etiqueta de problema**: pastilla roja con texto blanco sobre una X roja gigante y un resplandor radial rojo ("Smear marks").
7. **Pastilla de dato**: pastilla negra con texto blanco ("G80").

## 3. Transiciones y movimiento

- **Zoom-blur de entrada** (la principal): el plano nuevo entra escalado a ~1,3–1,5× con desenfoque fuerte y brillo alto, y se asienta en 2–3 fotogramas. Se usa en todas las entradas a escenas gráficas (85, 139, 188, 371).
- **Cortes secos en el beat** entre planos de cámara, con push-in suave dentro del plano.
- **Tarjetas** que entran deslizando desde fuera de cuadro con rebote (overshoot), deriva lenta (flotan) y rotación 3D.
- **Títulos**: escala de grande a normal con estela (ghosting), letra por letra, palabra por palabra y golpe escalonado.
- Marca de agua tenue del editor al pie.

## 4. Color

- El material está saturado y contrastado; el verde del BMW resalta.
- Acento positivo en amarillo, sobre fondos degradados negro → amarillo o blanco → amarillo con viñeta.
- **Negativo / problema en rojo** ("Smear marks", "CAKED UP").

## 5. Audio

- Voz en off continua, sin pausas muertas (las pausas se cortan).
- **Beat hip-hop/trap con sub-bajo que entra en el primer corte (~1,38 s).** Antes solo están la voz y el hook.
- **Hueco corto del bajo (~9,95–10,3 s) justo antes de "CAKED UP"**: silencio de tensión y luego el golpe.
- **SFX**: transitorios en las transiciones y en las entradas de título (1,38 · 2,96 · 3,63 · 4,80 · 7,07 · 10,44 · 12,44 · 14,20 · 15,28 · 16,95 s). Por su forma espectral corresponden a *whoosh* en las transiciones, *pops* y clics en las entradas de texto y un golpe en la palabra de impacto. Al final solo queda la música, con hi-hats marcados.
- Nota: los SFX están mezclados bajo la voz, así que se identificaron por tipo y por tiempo, no se extrajeron.

## 6. Cómo se traduce a la paleta pedida (rojo, negro, blanco)

| En la referencia | En la prueba |
|---|---|
| Amarillo de acento (glow, cajas, degradados) | Rojo `#FF1F12` → `#C40000` |
| Fondo negro → amarillo | Negro → rojo |
| Fondo blanco → amarillo | Blanco → rojo |
| Texto amarillo con degradado | Blanco con degradado a rojo suave + glow rojo + extrusión |
| Rojo para el problema | Rojo biselado ("FALLANDO?", "BAJA PRESIÓN", "UN MENSAJE") |
| Fuente heavy italic / wide | Poppins 800–900 (normal y cursiva) |
