# estilo.md — Guía de edición (referencia: "Reel_referencia_e_fashion.mp4")

> Fuente del análisis: **solo el panel derecho** (resultado final) del vídeo de referencia.
> Panel recortado en el original 716×1274 → `crop=424:754:224:256` (9:16), 29,85 s, 25 fps.
> Todas las medidas están convertidas a nuestro lienzo **1080×1920 a 30 fps** (factor ×2,547).
> Extracción: 60 fotogramas a 2 fps + 23 cambios de plano (`select=gt(scene,0.18)`), tiras a 4–25 fps
> en cada momento clave, muestreo de color por píxel, transcripción Whisper large-v3 con tiempos por palabra
> y análisis espectral del audio (bandas <70 Hz y >7 kHz).
> Lo que no se puede medir directamente está marcado con **[SUPOSICIÓN]**.

---

## 1. Ritmo y estructura

| Parámetro | Valor medido |
|---|---|
| Duración | 29,85 s, voz continua de 0,00 a 29,82 s (sin silencio inicial: el vídeo arranca con la primera palabra) |
| Velocidad de habla | 95 palabras / 29,8 s = **3,2 palabras/s** |
| Cambios de plano (corte, b-roll, punch-in o pantalla gráfica) | **14 en 30 s → 1 cada 2,1 s**. Duración de plano: mín. 1,1 s, máx. 3,6 s |
| Cambio de bloque de texto/gráfico | **cada 0,8–1,5 s** (nunca hay más de ~1,5 s sin un elemento nuevo en pantalla) |
| Tiempos de corte medidos | 0,04 · 1,24 (punch-in) · 2,40 (b-roll) · 3,68 (gráfico a pantalla completa) · 6,24 · 12,64 (b-roll) · 14,04 (b-roll) · 15,12 · 16,88 (punch-in) · 17,96 · 21,08 · 22,80 (punch-in) · 24,00 · 27,12 |
| Proporción de pantalla | ~70 % cabeza parlante, ~12 % b-roll a pantalla completa, ~8 % motion graphic a pantalla completa, ~10 % transiciones/punch-ins |
| Pausas | Silencios entre frases recortados a **0,12–0,24 s** (jump cuts sin respiraciones) |

Arco narrativo: gancho con la idea principal en los primeros 2 s → historia personal (b-roll) → problema
(b-roll emocional) → analogía → giro ("That's when the True Test begins") → conclusión/mensaje final.

## 2. Subtítulos (tipografía cinética, no subtítulo plano)

No hay una línea fija de subtítulos: **cada frase se convierte en un bloque tipográfico** compuesto por
palabras pequeñas de contexto + **1 palabra (o 2) destacada enorme**.

| Parámetro | Valor |
|---|---|
| Palabras por bloque | **2–7 (típico 4–6)**. Siempre **1 palabra destacada** (a veces 2: "All in", "Up Everyday", "motivation alone") |
| Fuente palabras pequeñas | Geométrica redondeada, peso Medium/SemiBold → equivalente Google: **Outfit 500–600** [SUPOSICIÓN: la original parece Gilroy/Lufga; Outfit es la más parecida al comparar renderizados] |
| Tamaño palabras pequeñas | **44–60 px**, blanco `#FFFFFF`, tracking −0,02 em |
| Fuente palabra destacada | La misma familia, peso Bold → **Outfit 700**, tracking **−0,04 em** |
| Tamaño palabra destacada | **135–280 px**. Regla: la palabra ocupa **≈60–65 % del ancho (650–700 px)**; palabras cortas ("All in", "Gym", "Test") se escalan hasta 280 px |
| Relación tamaños | pequeña ≈ **20–25 %** de la destacada |
| Color destacada (amarillo) | Degradado vertical **`#FFF34F` (arriba) → `#FCEB3F` → `#F6CD22` (abajo)** + resplandor `0 0 30px rgba(252,229,0,0.45)` |
| Color destacada alternativo (lima) | `#C6EF17` → `#D8F42F` con resplandor lima (usado en "Gym", "Test": momentos de energía/clímax) |
| Composición del bloque | Palabras pequeñas **encima** de la destacada, repartidas a izquierda y derecha ("Discipline ··· is the" / "Secret"), y a veces **debajo-derecha** ("would happen", "begins") |
| Posición vertical | Centro del bloque entre **50 % y 73 % de la altura (960–1400 px)**, típico **60 % (≈1150 px)**: sobre el pecho, debajo de la barbilla, nunca tapa la cara |
| Posición horizontal | Centrado; ocasionalmente desplazado a la derecha cuando el sujeto se mueve a la izquierda ("Gym", "Test") |
| Sincronía | **Palabra a palabra**: cada palabra pequeña aparece en el instante en que se pronuncia (tiempos Whisper); la destacada entra justo en su sílaba tónica |
| Animación de entrada (pequeñas) | Fade 0→1 + subida 20 px + desenfoque 6→0 px en **5 fotogramas** (≈170 ms) |
| Animación de entrada (destacada) | Sube desde +60 px con **blur de movimiento vertical 12→0 px**, escala 0,85→1,0 con resorte (sin rebote visible), **6–8 fotogramas** |
| Salida del bloque | Fade + blur 0→8 px en 4–6 fotogramas, o corte seco con el siguiente bloque/plano |
| Textura | Ninguna textura en la letra; solo degradado + glow. Sin contorno, sin caja de fondo |
| Subrayado de énfasis | Trazo rojo a mano alzada `#E5383B`, 6 px, dibujado de izquierda a derecha en 8 fotogramas ("hard", "Novelty wears off") |
| Mayúsculas | Frase en minúscula natural; destacadas con mayúscula inicial ("Secret", "Something", "Excitement") |

## 3. Textos en pantalla y motion graphics (objetos)

Todos los objetos UI comparten: esquinas muy redondeadas, sombras suaves, fondo oscuro translúcido tipo "glass",
acentos amarillo/naranja con glow.

1. **Barra de progreso con llama** (0,25–2,4 s, 21,5–22,6 s): píldora **≈780×90 px**, radio completo, fondo
   `rgba(40,32,24,0.80)` (`#3D3325`–`#524233` sobre vídeo); relleno degradado **`#FF9500` → `#FFAB00` → `#FFB700`**
   que crece de izquierda a derecha en ~1,2 s; emoji 🔥 en el extremo del relleno dentro de un círculo oscuro.
   Situada a **≈65 % de altura**, justo debajo de la palabra destacada.
2. **Píldora blanca conectada** ("long term success"): fondo `#FFFFFF`, texto `#111` Outfit 500 **≈40 px**, padding
   18×36 px, radio completo; unida a la barra con **3 puntos blancos de 8 px** en vertical. Texto escrito palabra a palabra.
3. **Etiquetas blancas apiladas** ("Face Challenge", "Get Tired", "Lose the initial Spark"): fondo blanco 95 %,
   texto `#111` **≈38 px**, padding 22×40, **radio 18 px**, sombra `0 8px 30px rgba(0,0,0,.35)`; aparecen con pop
   (escala 0,6→1,05→1, 8 fotogramas) **una por palabra clave**, en rejilla 2 + 1 a ancho completo, a **≈48 % de altura**.
4. **Panel calendario** (19,3–21 s): panel oscuro **≈860×190 px**, radio 28 px, fondo `rgba(20,16,14,0.78)`,
   días (`MON…SAT`, 22 px gris `#B5B5B5`) y números blancos 40 px que entran uno a uno (cada 4 fotogramas) deslizándose
   desde la derecha; los días "fallados" se marcan con **círculo rojo `#FE4348` de 64 px con glow rojo**.
   Debajo, frase blanca ("Novelty wears off") con subrayado rojo dibujado.
5. **Tarjetas glass con iconos** (24–27 s): panel oscuro radio 28 px, borde 1 px `rgba(255,255,255,.12)`,
   2 columnas con icono-app (cuadrado 70 px, radio 18 px) + texto pequeño 30 px + palabra en mayúsculas Outfit 700 40 px;
   **línea de luz amarilla `#FFC21A` de 3 px** bajo el panel con degradado que se desvanece en los extremos.
6. **Fotos tipo polaroid** (6,4–8,9 s): marcos blancos de 6 px, **≈280×380 px**, sin rotación, a **≈62 % de altura**,
   aparecen una por una (pop + flash blanco de 2 fotogramas); cuando entra la frase destacada se vuelven
   translúcidas (40 %) y desenfocadas detrás del texto.
7. **Gráfico de barra a pantalla completa** (3,68–6,2 s): fondo casi negro cálido **`#0F0F0A`–`#1A180D`**;
   barra vertical **`#FCE500`** con glow amarillo (`0 0 80px rgba(252,229,0,.6)`) que se llena de abajo arriba;
   avatar circular 70 px con borde blanco que sube con la barra; etiqueta "ON" (24 px) + "Motivation" (Outfit 500,
   110 px, blanco). A los 1,6 s la cámara virtual **se desplaza ~45 % a la izquierda** y aparece texto condensado.
8. **Texto condensado** (gráficos y b-roll): **Bebas Neue** para mayúsculas ("EARLY STAGES" 150 px,
   "TO GET ME THROUGH THE" 60 px; "WORKING" 260 px) y **Oswald 600** para minúsculas condensadas ("Didn't",
   "Feel like", "My Agency") [SUPOSICIÓN: equivalentes Google más cercanos]. Blanco `#F5F5F5`.
   Entrada **letra a letra / con glitch** (W·O·R·K·I·N·G aparece en ~10 fotogramas).
9. **Estela de luz amarilla**: curva neón amarilla (`#FFD21F`, 18 px, glow 40 px) que barre el plano de izquierda a
   derecha en ~0,6 s en b-rolls ("My Agency", "Workout").
10. **Texto detrás del sujeto** en b-roll ("My Agency", "Workout"): el titular se coloca en el tercio superior y la
    cabeza del sujeto lo tapa parcialmente (recorte/matte del sujeto).
11. **Orbe de luz**: círculo amarillo difuso (300–400 px, blur 60 px, 60 % opacidad) detrás del titular en el b-roll.

## 4. B-roll

| Parámetro | Valor |
|---|---|
| Cantidad | 3 b-rolls a pantalla completa en 30 s (2,40–3,68 · 12,64–14,04 · 14,04–15,12) + 2 fotos en tarjeta |
| Duración | **1,1–1,4 s** cada b-roll (cortos, de apoyo literal a lo que se dice) |
| Contenido | Ilustra literalmente la frase ("my agency" → oficina; "didn't feel like working" → persona agotada; "workout" → gimnasio) |
| Movimiento | Push-in lento continuo **1,00→1,08** durante el plano [SUPOSICIÓN: estimado entre fotogramas] |
| Texto encima | Siempre lleva titular condensado/blanco + estela o orbe amarillo |
| Grade | Mismo tono cálido que la cabeza parlante (ámbar/tungsteno) para que no salte |

## 5. Transiciones

| Tipo | Medida |
|---|---|
| Corte seco | La mayoría de cambios de frase |
| **Blur-in con zoom** (al volver a cabeza parlante) | El plano entrante empieza con desenfoque fuerte (~25 px) y escala 1,12, y se asienta a nitidez y escala 1,0 en **8 fotogramas** (≈280 ms) — 15,12 s, 21,08 s, 27,12 s |
| **Flash de exposición** | 3 fotogramas sobreexpuestos (+brillo, blur) al pasar de gráfico a cabeza (6,24 s) |
| **Whip/motion blur de arranque** | El vídeo empieza en movimiento con blur de movimiento horizontal (0,00–0,20 s) |
| Parpadeo (flicker) | 1 fotograma oscuro antes de cambiar de b-roll (15,0 s) |
| Paneo de cámara virtual | Desplazamiento lateral del gráfico completo (−45 % en 0,5 s, ease in-out) |

## 6. Zooms

| Tipo | Valor |
|---|---|
| **Punch-in** (jump cut de escala) | Corte instantáneo de escala **1,00 → 1,22–1,35** en la palabra clave (1,24 s "long term", 16,88 s "gets you to the Gym", 22,80 s "True Test"). Dura 1,1–1,2 s y vuelve a 1,0 con corte |
| Afecta a los gráficos | Sí: el punch-in escala también los textos/objetos en pantalla (se aplica al conjunto) |
| Frecuencia | 1 punch-in cada **~7 s** |
| Zoom lento | [SUPOSICIÓN] push-in muy suave 1,00→1,04 dentro de planos largos |

## 7. Color

| Parámetro | Valor |
|---|---|
| Look general | Cálido tungsteno/ámbar, contraste medio-alto, negros densos. Media RGB cabeza parlante **(72, 61, 49)** |
| Fondo | Ladrillo naranja/marrón desenfocado; plantas verdes oscuras |
| Degradado inferior | Oscurece desde **65 %** de la altura hasta negro casi total al **90 %** (luminancia 76 → 50 → 36 → 10 → 4) |
| Viñeta superior | Oscurece el **0–15 %** superior (luminancia ~15) |
| Acentos | Amarillo `#FCE500`/`#FCEB3F`, naranja `#FFAB00`, lima `#C6EF17` (clímax), rojo `#FE4348` (alerta/fallo), blanco puro |
| Fondos de gráficos | Negro cálido `#0F0F0A` |

## 8. Sonido

| Parámetro | Valor |
|---|---|
| Loudness integrado | **−12,5 LUFS** (voz muy presente, estilo redes) |
| Voz | RMS mediana −15,3 dBFS por palabra |
| Música | Cama ambiental/cinemática sin batería marcada, con una nota sostenida aguda (~1,44 kHz) presente todo el vídeo [SUPOSICIÓN: inferido del espectrograma]. Nivel en pausas −22 a −28 dBFS → **≈10–12 dB por debajo de la voz** |
| SFX — whoosh | En cada cambio a b-roll / gráfico / transición blur (picos >7 kHz en 2,27 · 3,53 · 12,40 · 14,00 · 15,00 s) |
| SFX — pop grave ("thud") | En cada etiqueta/tarjeta/foto que aparece (picos <70 Hz en 6,38 · 7,15 · 9,25 · 10,05 · 11,12 · 24,30 · 24,95 s) |
| SFX — impacto/boom suave | En palabras destacadas de clímax (8,40 "Something", 16,95 "Gym", 18,05 "All in") |
| SFX — riser / tono de carga | Durante el relleno de la barra de progreso (0,30–1,20 s, tono sostenido + armónicos) |
| SFX — tecleo | [SUPOSICIÓN] en textos que se escriben letra a letra |
| Densidad | ~22 golpes graves + ~25 transitorios agudos en 30 s → **≈1 SFX por segundo**, siempre a volumen bajo-medio (no tapan la voz) |

## 9. Reglas para replicarlo (resumen accionable)

1. Recortar silencios a ≤0,2 s; arrancar con la primera palabra.
2. Un elemento visual nuevo cada 0,8–1,5 s; un cambio de plano cada ~2 s.
3. Cada frase = bloque tipográfico de 2–7 palabras con 1 destacada amarilla gigante (Outfit 700, 135–280 px) y el resto blanco pequeño (Outfit 500, 44–60 px), sincronizado palabra a palabra, a ~60 % de altura.
4. Objetos UI glass oscuros con acentos amarillo/naranja y glow; etiquetas blancas para listas.
5. B-roll de 1,1–1,4 s, literal a la frase, con titular condensado y estela amarilla.
6. Punch-in 1,22–1,35 cada ~7 s en palabras clave; blur-in de 8 fotogramas al volver del b-roll.
7. Grade cálido + degradado negro inferior desde el 65 %.
8. SFX en cada aparición (pop grave en objetos, whoosh en cortes, tecleo en textos escritos, boom en clímax); música ~11 dB bajo la voz; master a −13 LUFS aprox.

---

## 10. Correcciones aprobadas por el usuario

_(Aquí se añaden las correcciones que el usuario confirme que le gustan, para que se mantengan en futuras ediciones.)_

- **Tipografía/colores:** usar las fuentes y colores del vídeo de referencia (no la identidad del portafolio).
- **Textos escritos:** usar SFX de tecleo ("typing") en los textos en pantalla.
- **Efectos de sonido:** usar los SFX de las carpetas del usuario en cada palabra/elemento destacado, b-roll y motion graphic, buscando un resultado dinámico pero premium y sin saturar.
- **Logo de la marca (actualizado en la ronda 2):** extraerlo del propio material y usarlo: el isotipo dentro de los
  elementos circulares de los gráficos (en lugar de fotos de personas) y el logotipo completo en el cierre. Si el
  material lo trae en baja resolución, vectorizarlo o reconstruirlo para que se vea nítido.

### Ronda 2 (correcciones sobre la versión 1)

- **Arranque directo:** el vídeo empieza en la frase de valor del producto, sin gags ni introducciones previas
  (aquí: "Esta es una silla de diseño único" sobre la silla sola). Si el corte pedido cae a mitad de palabra, se
  ajusta al inicio de frase más cercano y se compensa el volumen si la toma está más lejos del micro.
- **Muletillas fuera:** eliminar toda muletilla ("e", "eh", "este"…), aunque dure menos de 0,3 s. Verificarlo
  transcribiendo el fragmento con Whisper y un prompt que fuerce a escribir muletillas.
- **B-roll con criterio:** si no hay un b-roll que aporte, dejar al presentador hablando; no repetir el mismo plano
  de apoyo sin necesidad.
- **B-roll coherente con la marca:** solo planos del universo del cliente (fábrica, proyectos terminados,
  interiores, renders); nunca lifestyle ajeno al concepto (p. ej. un DJ con equipos de música).
- **Marcas mencionadas = logos flotando:** cuando se nombran clientes o marcas, mostrar sus logos oficiales en
  tarjetas blancas (radio 30 px, sombra suave) que salen desde detrás de la persona al nombrarlas y flotan a su
  alrededor (balanceo ±14 px y giro ±2,6°), con un rótulo "NUESTROS CLIENTES" y SFX pop + whoosh suave por logo.
