# Montaje y retención

## Índice
1. Estructura del video
2. Ritmo y textos en pantalla
3. Recursos del motor
4. Mapas
5. Diagramas propios
6. Reglas de diseño que salieron de las revisiones
7. Estructuras usadas en cada episodio

## 1. Estructura del video

Los guiones de Ali siguen siempre el mismo esquema, y el montaje lo acompaña:

1. **Gancho (0:00–~1:05).** Arranca dentro de la escena (linterna en un túnel oscuro, carretera cerrada por
   el viento) con imágenes fuertes, un mapa que sitúa el lugar y cifras animadas. Termina con las **dos
   preguntas** del guion, cada una en su tarjeta (`q1`, `q2`: fondo oscuro, transición `glitch`, palabra
   clave resaltada).
2. **Título (~1:05).** Tarjeta con el nombre del lugar en Bebas amarillo, subtítulo en serif cursiva y la
   insignia "CAPÍTULO 1 · …", con transición `flash`.
3. **Capítulos** (6–8), cada uno abierto con `chapter(n, título, fondo, gradación, años)` y `tr="flash"`.
   Los años del capítulo van en la tarjeta.
4. **CTA de suscripción** donde el guion lo dice ("a ti te basta un clic…"): `FnOverlay(G2.subscribe)` sobre
   un plano oscuro durante toda la frase.
5. **Conclusión:** vuelve la pregunta 1 (`q1`) y se responde con frases cortas y grandes.
6. **CTA de comentarios al final:** `FnOverlay(G4.comments, line1=…, line2=…, cta=…)` con la pregunta que
   hace el guion, hasta el último segundo.

Los capítulos de la descripción de YouTube salen de los tiempos de estas tarjetas (`tools/usados.py` los
imprime).

## 2. Ritmo y textos en pantalla

- Un plano cada 2,5–5 s; en los primeros 4–5 minutos más corto y con más transiciones.
- Cada plano empieza en una palabra de la locución: `add(w("palabra", segundo_aprox) - 0.2, …)`.
  `w()` busca la palabra cerca de ese segundo; si no la encuentra, lo avisa en `check.py` y usa el
  segundo aproximado.
- Texto en pantalla en casi todos los planos, nunca la frase entera: la idea clave, con 1–2 palabras
  resaltadas (`rich(texto, ("palabra",), …)`), títulos grandes (`big`), cifras que cuentan (`Counter`),
  sellos (`Stamp`), fechas y lugares (`Badge`), nombres (`LowerThird`) y leyendas de archivo (`Caption`).
- Las cifras del guion se muestran con su conversión: "21 PIES · ≈ 6,5 M", "6 MPH · ≈ 10 KM/H".
- Alterna: archivo (gradación `archival`, textura ARCH) → stock moderno (CLEAN) → mapa → diagrama (GFX).
  Evita dos diagramas o dos mapas seguidos si hay foto que lo cuente.
- Movimiento siempre: Ken Burns (`in`, `out`, `l`, `r`, `up`, `down`, `punch`), linterna sobre fotos de
  túneles (`torch`), sacudida cuando la voz dice golpes o explosiones (`post=postshake(n)`).

## 3. Recursos del motor

**Bases** (`gfx.py`): `Still` (vía `kb(ruta, movimiento, gradación)`), `Framed` (vía `fr(ruta, leyenda)`: foto
enmarcada sobre fondo difuminado, para archivo y fotos pequeñas), `Video` (vía `vid(nombre, segundo, dur)`, siempre
dentro de una escena), `Solid("black")`, `Custom` (vía `cus(fn, …)` o `warp(fn, a, b, …)`), `Split([bases], labels=[…])`
y `Seq`.

**Gradaciones:** `doc`, `cold`, `warm`, `faded`, `dark`, `night`, `bw`, `archival`, `sepia`, `cold_bw`, `none`.
**Texturas:** ARCH (grano + polvo + parpadeo), FILM, CLEAN, GFX, DARK.
**Transiciones:** `fade`, `black`, `flash`, `whip_l`, `whip_r`, `zoom`, `glitch` (cada una lleva su efecto
de sonido automático en `audio.py`).

**Overlays:** `Badge(texto, t0, t1)`, `Caption(texto, sub, t0)`, `LowerThird(nombre, rol, t0)`,
`BigText` (vía `big(texto, t0, y, tamaño, color, anim)` con anim `up`/`pop`/`zoom`/`type`), `Rich` (vía
`rich(texto, resaltadas, t0, step, y, size, maxw, red=…)`), `Counter(v0, v1, formato, etiqueta, t0, dur, pos, tamaño)`,
`Stamp(texto, t0, color, pos, ángulo, tamaño)`, `Callout(px, py, lx, ly, texto, t0)`, `Flash(t0, dur, color, pico)`,
`Darken(k)`, `FnOverlay(función, **kw)`.

**Helpers de `timeline.py`:** `w`, `res` (corrige ids de Unsplash mal leídos), `kb`, `fr`, `cus`, `warp`,
`chapter`, `question`, `rich`, `big`, `torch`, `postshake`, `mp`, `q1`/`q2` dentro de `build()`.

## 4. Mapas

- `MapScene(nombre_mapa, cámaras=[(t, lon, lat, zoom), …], capas=[…])` vía `mp()`. Zoom 1 = un píxel del mapa
  base por píxel de pantalla; la cámara interpola el zoom de forma geométrica.
- Capas: `route` (path, draw, color, width, smooth, dash, traffic, speed), `rail`, `road` (carreteras de
  Natural Earth unidas con `road_chain`), `band`, `poly`, `pin` (at, label, side l/r/t/b, box, size),
  `label` (at, text, size, box, color), `state`, `xmark`, `gate`, `marker`. Cada capa tiene `t0` (y `t1`
  opcional) para aparecer al ritmo de la voz.
- Tipos de mapa que funcionaron: país (z6) para situar, región (z9–10) para rutas, local (z11–14) con
  relieve exagerado para pasos de montaña, y en ciudad, calles reales de datos abiertos (z14–17).
- Animación típica: aparece la etiqueta del lugar → se dibuja la ruta (draw 1,5–3 s) → pin con caja
  amarilla en el punto clave → etiqueta con la cifra (millas, pies) en amarillo.

## 5. Diagramas propios

Cada episodio tiene su módulo (`gfx2.py` Laurel Hill, `gfx3.py` I-80, `gfx4.py` Cumberland, `gfx5.py` Donner,
`gfx6.py` Atlantic Avenue) y se pueden reutilizar. Ejemplos que funcionaron bien para retener:

- **Corte de la montaña o de la calle** con el túnel dentro, que se excava, se tapia o se recorre
  (`gfx5.tunnel6`, `gfx6.cut_cover`, `gfx6.avenue_profile`, `gfx6.descent`).
- **Escala humana:** nieve frente a una casa de dos pisos (`snow_depth`), personas en un hueco de 60 cm.
- **Procesos paso a paso:** barreno a mano → pólvora → mecha → explosión (`hand_drill`), zanja → muros →
  bóveda → calle encima (`cut_cover`).
- **Documentos recreados** con la línea clave resaltada y sellos (`permit`, `payroll`, `document`, `blueprint`).
- **Tableros y cronologías:** `rumor_board` (tarjetas con chinchetas e hilo rojo), `timeline`, `calendar`,
  `countdown`, `london` (1844 frente a 1863).
- **Contadores grandes sobre foto** (`counter_people`, `Counter`).

Antes de usarlos en la línea de tiempo, renderiza 4–8 fotogramas de cada uno en una hoja y revísala.

## 6. Reglas de diseño que salieron de las revisiones

- Texto sobre fotos enmarcadas (`fr`): arriba en `y=0.065` con `maxw` 0.85–0.9 para que quepa en una línea;
  en `y=0.1` se cortaba.
- No pongas a la vez la leyenda de `fr()` y un `LowerThird`: se pisan. Con `LowerThird`, `fr(ruta)` sin leyenda.
- Texto sobre fondos claros (mapas antiguos, planos, cielos): añade `Darken(0.35–0.4)`.
- Sellos rojos sobre ladrillo rojo no se leen: usa amarillo.
- Etiquetas de diagramas: no las pongas en la misma altura que el título ni en el borde; un texto largo
  centrado sobre un objeto pegado al borde se corta: ánclalo a la izquierda o a la derecha.
- Mapas: que la cámara nunca muestre fuera del mapa base (bordes negros); que ningún punto o etiqueta
  caiga fuera del mapa (en Atlantic, Jamaica quedaba fuera del mapa de la ciudad).
- Objetos animados (trenes, camiones) dentro del encuadre en el centro del plano, no saliendo o entrando.
- Imagen = lo que dice la voz: una avalancha debe ser una avalancha, no una montaña seca; un tren de 1952
  en la nieve, no maquinaria. Revisa los fotogramas de las películas en la escena exacta.
- Fotos muy oscuras: sube la linterna (`r` y `amb`) o cámbialas; un plano casi negro se ve como error.
- Gráficos demasiado pequeños o vacíos: acércalos (zoom de foco) y llena el cuadro.
- Grabados o escaneos girados: revisa la orientación (uno quedó al revés tras girarlo 90°).

## 7. Estructuras usadas en cada episodio

| Episodio | Duración | Capítulos (inicio) |
| --- | --- | --- |
| Laurel Hill | 18:13 | Intro · título 1:05 · La autopista del futuro 1:09 · Cuatro carriles, una puerta 3:54 · Más viejo que la autopista 6:35 · El túnel que nadie miraba 10:38 · Los nuevos inquilinos 11:33 · Cómo está hoy 15:39 · Conclusión 17:10 |
| I-80 Wyoming | 18:46 | Intro · título 1:25 · Dos mapas 1:28 · La pelea 3:55 · Cuatro días 5:30 · La nieve que viaja 8:31 · La firma 10:59 · Vallas y barreras 13:08 · Hoy 14:42 · Conclusión 17:26 |
| Cumberland Gap | 18:50 | 0:00 · 0:59 · 4:12 · 6:19 · 8:22 · 10:55 · 14:40 · 16:49 · 17:58 |
| Donner Pass | 18:50 | 0:00 · 1:07 · 3:04 · 5:03 · 7:42 · 11:03 · 13:04 · 15:55 · 17:38 |
| Atlantic Avenue | 19:05 | 0:00 · 1:06 · 3:27 · 6:44 · 8:23 · 10:40 · 12:59 · 16:22 · 17:36 |

`scripts/motor/timeline.py` es Atlantic Avenue completo (244 planos): sirve de plantilla.
