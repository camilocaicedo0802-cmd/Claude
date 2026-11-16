# estilo.md — Ganador 4 · «Los 3 problemas de las redes»

Referente: **vídeo de la derecha («Our edit»)** de `referencia/referencia_lado_a_lado.mp4` (Haniarteq).
Se recortó la pantalla del teléfono derecho (368×654 px en x=262, y=316 del original 720×1280; la maqueta no se mueve en todo el clip) y se reescaló a 540×960 → `referencia/referencia.mp4` (31,7 s, 29,97 fps).
Todas las medidas de este documento están **pasadas a 1080×1920** (×2 sobre el recorte). Proyecto: **1080×1920 a 60 fps**.

Material del análisis (`referencia/`): `frames/2fps/` (63 fotogramas con tiempo), `frames/cambios/` (cambios de plano), `detalle/*.jpg` (tiras a 10 fps de cada recurso), `hoja_1/2.jpg`, `referencia.wav`, `sep/` (voz y fondo separados con Demucs), `transcripcion_ref.json`, `caras_10fps.json` (tamaño de cara = zoom), `sfx_eventos.json` / `sfx_match.json` (efectos contra el pack del cliente).

Lo que no se pudo medir y se ha deducido va marcado **[SUPOSICIÓN]**.

---

## 1. Ritmo y estructura

| Dato | Valor |
|---|---|
| Duración | 31,7 s |
| Velocidad de habla | 120 palabras en 31,2 s = **3,85 palabras/s**; pausas internas ≤ 0,3 s, entre frases 0,3–0,7 s |
| Planos (cortes/transiciones) | 0,00 · 4,20–4,60 (desenfoque) · 5,405 · 8,04 · 12,55 (rayas) · 18,45 · 20,92 · 25,69 (marco) · 27,03 → **9 planos, media 3,5 s** (mín. 1,3 s, máx. 5,9 s) |
| Bloques de texto | **21 bloques** en 31,7 s → uno cada **1,5 s** |
| Pantalla sin texto | < 5 % del tiempo (solo 0,0–0,15 s y los fotogramas de transición) |
| Recursos grandes (motion graphics) | 4: lingote de oro (0,2–1,6 s), lienzo con tarjeta (8,0–12,5 s), caja resaltada (11,8–12,5 s), marco «caja central» (25,7–27,0 s) |
| B-roll a pantalla completa | **0** (todo es la persona + gráficos) |

Mapa del referente:

| Tiempo | Plano | Texto | Recurso |
|---|---|---|---|
| 0,00–1,60 | medio (cara 290 px) | There is a / **Golden rule** / in social media | arranque desenfocado → enfoque; lingotes de oro + ondas |
| 1,80–4,20 | medio | you / **make** · people's / **eyes** · **move** (arriba, a los lados de la cabeza) | — |
| 4,20–4,60 | transición desenfoque + zoom 0,90 | — | whoosh |
| 4,60–5,40 | medio-abierto (cara 260 px) | you · will · lose / **their attention** (morado en nuestro caso) | — |
| 5,40–8,04 | medio (cara 290 px) | Right now · looking → **Captions** / under · my · chin | golpe grave + whoosh en el corte |
| 8,04–12,55 | abierto → **lienzo**: el vídeo se encoge a una tarjeta sobre papel cuadriculado | so in the / **next scene** · the / **main subject** / should · also · be · where / **the captions** / were | swooshes suaves; caja resaltada en 11,8 |
| 12,55 | transición de **rayas verticales** | — | clic + golpe grave |
| 12,60–18,45 | medio-abierto (260 px) | If · you · scatter / **elements** / across the screen · the · have · to make an / **Effort** · keep · what / **you're saying** | swooshes en palabras grandes |
| 18,45–20,92 | **primer plano** (cara 364 px) | and · that · makes / **your videos** · **uncomfortable** (letra a letra) / to · watch | tecla (escritura) |
| 20,92–25,69 | abierto 250 px → **empuje** a 300 px en 0,6 s → deriva hasta 270 px | so · remember · for · next · you're / **recording** · or / **editing** / a video · Keep · all · the / **elements** | — |
| 25,69–27,03 | igual, con **marco «caja central»** | inside · this / **middle box** | clic de mechero en la aparición |
| 27,03–31,70 | medio-cerrado (cara 320 px) | Watch · video · to see / **exactly** · making · move · the · entire / **time** | — |

## 2. Subtítulos (palabra a palabra)

Son un único sistema de texto (no hay subtítulo «normal» aparte): **bloques de 2–3 líneas que se construyen palabra a palabra** sobre el pecho, más un modo de **palabra suelta** para los tramos de enlace.

| Elemento | Valor |
|---|---|
| Fuente palabras pequeñas | grotesca de trazo fino-regular, tipo SF Pro Display / Inter **400** [SUPOSICIÓN de familia] |
| Fuente palabra grande | la misma familia en **700–800**, interletraje −2 % |
| Fuente adorno | serif cursiva con mayúscula de rasgo (la «T» de «There») solo en la primera palabra del gancho [SUPOSICIÓN: Playfair/Bodoni Italic] |
| Tamaño pequeñas | altura de mayúscula 44 px → **≈ 60 px** de cuerpo |
| Tamaño grande | altura de mayúscula 100 px → **≈ 136 px** (gancho «Golden rule»); 124 px («their attention»); 130 px («elements») |
| Tamaño bloque superior | «make» ≈ **160 px**, «eyes»/«move» ≈ 115 px, «you»/«people's» ≈ 60 px |
| Colores | pequeñas **blanco #FFFFFF** (algunas en gris 70 % mientras no se dicen); grande blanco o **acento** (en el referente naranja degradado #DF7D47 → #DB673B) |
| Sombra / brillo | sombra oscura suave `0 4px 14px rgba(0,0,0,.45)`; la palabra de acento lleva halo de su color `0 0 18px` al 55 % |
| Textura | ninguna (relleno liso; el naranja trae un degradado vertical leve) |
| Palabras por bloque | **3–7** (media 4,9); **1 palabra grande** (o 2 juntas) por bloque |
| Disposición | línea pequeña **justificada al ancho de la grande** (palabras repartidas con huecos de 40–90 px), justo encima (interlineado 0,95); a veces una tercera línea pequeña debajo, desplazada 60–150 px a la derecha («in social media») |
| Posición | centro del bloque en **x = 540 ± 50**, **y = 1000–1180 px** (52–61 % del alto), sobre el pecho, nunca en la cara; bloque superior en **y = 400–660 px** a los lados de la cabeza (columna izquierda x 10–360, derecha x 700–980), con letras que se salen del borde |
| Profundidad | las palabras grandes pasan **por detrás del micrófono y de las manos** (el objeto en primer plano las tapa) |
| Modo palabra suelta | una palabra pequeña (60 px) en el centro del pecho (y ≈ 1080) que cambia con cada palabra dicha: «keep», «what», «for», «next», «Watch», «video», «making», «move» |
| Sincronía | cada palabra aparece **0,05–0,15 s antes** de pronunciarse |

Animación (a 60 fps):
- **Entrada de palabra**: 8 fotogramas — opacidad 0→1, desenfoque 10→0 px, subida 8→0 px, escala 0,96→1, curva ease-out.
- **Palabra larga de acento** («uncomfortable»): se escribe **letra a letra**, ~2,8 fotogramas por letra (13 letras en 0,6 s), al ritmo de la voz.
- **Vida**: el bloque deriva 1→1,03 de escala mientras está en pantalla [SUPOSICIÓN: valor medido a ojo].
- **Salida**: todo el bloque a la vez, 6–8 fotogramas — opacidad 1→0 y desenfoque 0→12 px; empieza 0,05 s antes del siguiente bloque.

## 3. Textos en pantalla (no subtítulos)

Etiquetas del lienzo (8,0–12,5 s): texto vertical diminuto (≈ 16 px, mayúsculas, gris #6E6E80, interletraje +20 %) en los laterales de la tarjeta («NICKSON STUDIO», «DESIGNLAB 400», números «22», «11») y triángulos ▲ de 10 px como marcas de registro. Es decoración tipo maqueta de diseño.

## 4. B-roll y motion graphics

No hay B-roll de vídeo. Los recursos son gráficos sobre la persona:

1. **Objeto 3D del gancho** (0,2–1,6 s): lingote de oro renderizado en 3D; uno pequeño cae por arriba a la derecha (junto a la lámpara, ~70 px de ancho) y otro grande entra por abajo a la izquierda (~220×340 px, girado 15°), con **2–3 ondas concéntricas** doradas (trazo 3 px, radio 40→160 px, se apagan en 0,6 s).
2. **Lienzo con tarjeta** (8,04–12,55 s): el vídeo se encoge **1 → 0,74** en 0,45 s (ease-out) a una tarjeta de esquinas redondeadas (radio 32 px) con borde/halo melocotón #F3B9A6 (6 px + halo 24 px), sobre fondo lavanda **#D8D8E6** con cuadrícula fina [SUPOSICIÓN: celda 48 px, línea #C9C9DB], etiquetas verticales y marcas ▲ (§3). Dura 4,5 s.
3. **Caja resaltada** (11,76 s): rectángulo de trazo 3 px + relleno al 25 % del color de acento alrededor de la frase («the captions»), entra en 0,2 s.
4. **Marco «caja central»** (25,69–27,03 s): paneles de color de acento alrededor de un hueco central (≈ 92 % del ancho × 68 % del alto, arriba en el 15 %), con **escalones** que se desplazan; entra con **parpadeo** (1 fotograma encendido, 1 apagado, encendido), primero al 70 % de opacidad en tono oscuro y al final a tono pleno al 100 %. Ilustra literalmente lo que dice («keep all the elements inside this middle box»).

## 5. Transiciones

| Tipo | Dónde | Valores |
|---|---|---|
| Corte seco con cambio de zoom | 5,405 · 18,45 · 20,92 · 27,03 | 0 fotogramas; el encuadre cambia ×1,12–×1,40 |
| Desenfoque de lente | 0,0–0,3 (arranque) y 4,20–4,60 | desenfoque 0→18→0 px en 0,4 s + zoom 1→0,90; whoosh |
| Encogerse a tarjeta | 8,04 | escala 1→0,74 en 0,45 s, ease-out cúbico |
| Rayas verticales | 12,55 | 6 fotogramas a 60 fps: barras blancas/negras de 8 px que barren el plano |
| Marco que parpadea | 25,69 | ver §4.4 |

## 6. Zooms y movimiento

Medido con el alto de la cara (MediaPipe) cada 0,1 s:

| Nivel | Alto de cara | Escala relativa |
|---|---|---|
| Abierto / medio-abierto | 250–260 px | **1,00** |
| Medio | 290 px | **1,12** |
| Medio-cerrado | 320 px | **1,23** |
| Primer plano | 364 px | **1,40** |

- El zoom **cambia en cada corte** (nunca dos planos seguidos con la misma escala).
- **Empuje animado**: 20,92–21,60 s, de 1,00 a 1,20 en 0,6 s (ease-in-out).
- **Deriva**: dentro del plano, −7 % de escala en 5 s (21,6–26,5 s) [SUPOSICIÓN: puede ser estabilización].
- Encuadre siempre centrado en la persona; la cabeza ocupa el tercio superior (centro de la cara en y ≈ 520–620 px).

## 7. Color

- Look de la referencia: clave baja, dominante verde (cortina) con luz cálida de lámpara y relleno verde-cian en el pecho; negros profundos, viñeta suave en esquinas [SUPOSICIÓN: ~25 %].
- Colores medidos: acento naranja **#DF7D47 / #DB673B** (texto), marco final **#E25A2A**, lienzo **#D8D8E6**, borde de tarjeta **#D2B0A9**.

## 8. Sonido

| Pista | Medida |
|---|---|
| Mezcla final | **−14,8 LUFS**, pico 0,0 dBFS, LRA 3,7 LU |
| Voz (separada) | −15,0 LUFS |
| Fondo (música + efectos) | **−26,8 LUFS** integrado (11,8 LU bajo la voz), LRA 17,2 LU |
| Música | cama suave casi **sin graves** (energía < 150 Hz ≈ 5 %), dominan los medios; ≈ −33 dB RMS de 2 a 18 s; **baja ~12 dB a partir de 18,5 s** y casi desaparece en la segunda mitad [SUPOSICIÓN: fundido]; tempo ≈ 123 BPM (o 61,5) [SUPOSICIÓN] |

Efectos detectados y su equivalente en el **pack del cliente** (correlación local; ≥ 0,35 = coincidencia clara, menor = [SUPOSICIÓN] por tipo de sonido):

| Tiempo | Evento | SFX del pack | Corr. |
|---|---|---|---|
| 0,31 | entrada del lingote | `whoosh/VS_Short Whoosh 2.mp3` | 0,39 |
| 0,39 | golpe del lingote | `cine/Impact Normal.mp3` | 0,37 |
| 0,58 | segundo lingote | `whoosh/Woosh Effect 10.wav` | 0,44 |
| 4,60 | transición desenfoque | `whoosh/Woosh Effect 7.wav` (o `pack1/Woosh Effect 3.wav`) | 0,32 |
| 5,62 | corte «Right now» | `pack1/Sub Bass Hit.wav` | 0,45 |
| 5,72 | corte «Right now» | `whoosh/Woosh Effect 10.wav` | 0,50 |
| 6,64 | «Captions» | `general/camera-shutter-click-1133.wav` | 0,30 [SUPOSICIÓN] |
| 8,05–11,8 | encogerse a tarjeta y palabras del lienzo | `whoosh/Swoosh 01 - 07.wav` / `pack1/Swoosh 01 - 03.wav` | 0,16–0,25 [SUPOSICIÓN] |
| 12,64 | rayas | `clicks/Mouse Click 02.wav` + `cine/BASS DROP (16).wav` | 0,16–0,19 [SUPOSICIÓN] |
| 13,9–17,0 | palabras grandes | `pack1/Swoosh 01 - 03/05.wav` | 0,17–0,22 [SUPOSICIÓN] |
| 19,83 | «uncomfortable» letra a letra | `pack1/Tecla.mp3` | 0,20 [SUPOSICIÓN] |
| 20,90 | corte | `pack1/Swoosh 01 - 03.wav` | 0,33 |
| 25,83 | marco «caja central» | `clicks/Lighter Double Click 01.wav` | 0,37 |

Patrón: **whoosh + golpe grave** en los cortes fuertes y en el objeto 3D; **swoosh suave** (−6 dB respecto a los whoosh) en las palabras grandes; **clic** en las apariciones gráficas; **tecleo** en el texto escrito letra a letra. Nivel de los efectos: picos 6–10 dB por debajo de la voz.

---

## 9. Reglas del cliente que se mantienen (de los ganadores 1–3)

Estas correcciones del cliente mandan sobre el referente:
1. **Colores del logo GROW en vez del naranja**: acento morado liso **#B701FC** (con halo morado), morado medio #9601FD y profundo #7600FC para gráficos; blanco #FFFFFF. Letras **lisas, sin texturas** (sin cromado ni volumen); solo sombra/halo suave para leerse.
2. **Nada tapa la cara**; los textos van en el pecho o a los lados/encima de la cabeza; **labios siempre sincronizados**.
3. **Sin ajuste de color**: se usa el color de cámara (la luz violeta del set combina con el morado).
4. **B-roll sin repetir** entre ganadores.
5. **Recorte de persona** (si se usa): solo la persona, silueta completa y limpia, sin silla (método SAM2 + RVM del ganador 3).
6. **Música ≈ 12 LU por debajo de la voz** (cama discreta), mezcla final −14 LUFS.
7. **Efectos de sonido: únicamente del pack del cliente** (carpetas de Drive enviadas), **tecleo en los textos**. Música: de su carpeta de música.

## 10. Registro de correcciones del usuario (este vídeo)

### 10.1 Decisiones del cliente antes de editar (16/11/2026)
- **Perfiles desordenados**: con **maqueta** (no hay grabaciones reales).
- **Perfil bien hecho**: se usa la grabación de **@growmarketingpro_** (`ig_grow.mp4`); para este caso el cliente autoriza repetirla.
- **B-roll de cliente mirando el móvil**: el que envió el cliente (`Cliente_mirando_celular.mp4`).
- **Música**: **ANBR – Quantum** (PACK MÚSICA V2 de su carpeta).
- **Guion**: fuera «porque eso es lo que está realizando» y «Déjalo ahí» (toma 4863).
- **Objetos 3D**: en lugar del lingote de oro, la **animación del móvil 3D** y los **logos 3D de Instagram, Facebook y TikTok** que envió el cliente, **sin fondo** y con los logos **animados**.
