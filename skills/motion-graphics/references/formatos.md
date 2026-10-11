# Catálogo de formatos de referencia

Clasifica la referencia con un formato principal y, si es híbrida, uno secundario («70 % editorial, 30 % persona a cámara»). Cada ficha dice qué medir con más cuidado, cómo construirlo con la plantilla y qué hacer si falta material.

## Índice

1. Editorial / collage de motion graphics
2. Persona a cámara con subtítulos dinámicos
3. Voz en off con b-roll (documental o «faceless»)
4. Tipografía cinética (solo texto)
5. Edición rápida al ritmo de la música
6. Tutorial / grabación de pantalla
7. Clip de pódcast / entrevista
8. Producto / promo / anuncio
9. Listado / ranking / «top N»
10. Carrusel de fotos / slideshow

---

## 1. Editorial / collage de motion graphics

**Señales:**
- fondo de color plano o papel;
- objetos recortados con sombra;
- formas gráficas (círculos, trazos, bandas);
- tipografía mixta (caligráfica + palo seco);
- cámara que viaja por un «mundo» y pocos cortes duros;
- transiciones animadas (empuje, iris, oscurecimiento con transformación).

**Medir con cuidado:**
- tamaños relativos de los objetos;
- recorrido de la cámara (px/s y zoom);
- la relación guía/palabra clave del texto;
- el catálogo exacto de transiciones;
- el grano.

**Construir:**
- `Camera` sobre un mundo alto (coordenadas > 1920) con varios objetos y un `BrushPath` que los une;
- `Cutout` con sombra;
- `DashedCircle` u otras formas;
- `EditorialBlock` colocado junto al objeto;
- transiciones `Push`, `Iris` u oscurecimiento propio dentro de la escena (bajar el brillo del objeto + fondo oscuro + objeto simbólico nuevo).

**Ejemplo completo:** `assets/ejemplo/`.

**Material:** fotos de Openverse recortadas con `cutout.py`; lo que no exista en foto, en vectorial.

## 2. Persona a cámara con subtítulos dinámicos (talking head)

**Señales:**
- una persona hablando ocupa el plano;
- cortes de salto (jump cuts) cada 1–4 s;
- golpes de zoom (1.0 → 1.15 → 1.3) en los cortes;
- subtítulos grandes, centrados o en el tercio inferior, de 1–4 palabras, a menudo en mayúsculas, con contorno y palabra activa en color;
- emojis o iconos ocasionales;
- b-roll de 1–2 s tapando cortes.

**Medir:**
- frecuencia de cortes y de golpes de zoom;
- escalas de zoom;
- `texto.posicion_vertical`, `alto_caja`, mayúsculas, color de acento y contorno;
- cuántas palabras por página;
- proporción de b-roll sobre A-roll;
- SFX en cada golpe (pop, whoosh, ding).

**Construir:**
- Pasa el metraje por `scripts/jumpcut.py` (quita silencios) y transcribe el archivo resultante.
- `ARoll` con `punches` en cada corte (alterna escalas medidas).
- `WordPop` o `KaraokePage` según el OCR.
- Cortes de b-roll con `Cutout` o `Video` a sangre durante 1–2 s.

**Si el usuario no tiene metraje de sí mismo:** dilo y ofrece dos alternativas:
- (a) formato 3 (voz en off + b-roll) con los mismos subtítulos y ritmo;
- (b) un avatar o figura recortada estática animada con los golpes de zoom.

No cambies de formato sin preguntar.

## 3. Voz en off con b-roll (documental, «faceless»)

**Señales:**
- clips o fotos a sangre que cambian cada 1.5–4 s;
- movimiento Ken Burns (zoom/pan lento);
- subtítulos en el tercio inferior o centrados;
- música notable;
- a veces mapas, fechas o textos de lugar.

**Medir:**
- mediana de plano;
- velocidad y dirección del Ken Burns;
- tipo de imagen (archivo, stock, IA);
- etalonaje (saturación, tinte, contraste, grano);
- tipo de subtítulo;
- `musica_bajo_voz_db`;
- transiciones (corte, fundido, destello).

**Construir:**
- `Img` o `Video` a sangre (`objectFit: cover`) dentro de una `Camera` con zoom lento;
- `ColorGrade` + `Grain` + `Vignette` para igualar el etalonaje;
- `KaraokePage` o `WordPop`;
- cortes en las pausas de la voz.

**Material:** `find_images.py` (fotos). Para vídeo de stock, pide al usuario los clips o usa fotos con Ken Burns y dilo.

## 4. Tipografía cinética (solo texto)

**Señales:**
- el texto es el protagonista y ocupa el cuadro;
- palabras que entran con escala, rotación o máscara;
- cambios de fuente o color por palabra clave;
- fondos planos que cambian de color en los acentos.

**Medir:**
- jerarquía tipográfica (cuántos tamaños y fuentes);
- palabras por pantalla;
- dirección de las entradas;
- duración de las animaciones en frames;
- paleta de fondos;
- si el fondo cambia en cada frase.

**Construir:** escenas que son bloques de texto. `EditorialBlock` con `reveal` `pop` / `rise` / `wipe` / `typewriter`, o un componente nuevo por palabra con `interpolate` sobre `scale`, `rotate` y `translate`. Fondos con un `div` de color animado.

## 5. Edición rápida al ritmo de la música (fan edit, montaje, «aesthetic»)

**Señales:**
- cortes cada 0.2–0.8 s alineados con los golpes de la música;
- destellos, sacudidas, zoom con desenfoque, RGB split;
- poco o ningún texto;
- música protagonista.

**Medir:**
- `tempo_bpm_estimado` y onsets;
- `cortes_por_min`;
- qué cortes coinciden con golpes (`cortes_con_sfx_%` sobre la pista completa);
- efectos por corte.

**Construir:**
- calcula los beats con librosa (`beat_track`) sobre la música y pon un corte o efecto en cada beat (o cada 2);
- transiciones `Flash`, `ZoomIn` y sacudida (`translate` con ruido).

**Material:** necesita clips. Si no los hay, collage de fotos con el mismo ritmo.

## 6. Tutorial / grabación de pantalla

**Señales:**
- captura de pantalla o app;
- zoom hacia la zona activa;
- cursor resaltado;
- recuadros, flechas y números de paso;
- voz explicativa;
- subtítulos sobrios.

**Medir:**
- nivel de zoom y duración;
- estilo de las llamadas de atención (color, grosor, radio);
- marco o dispositivo alrededor de la captura;
- ritmo de los pasos.

**Construir:**
- `ARoll` con la grabación y `punches` hacia `x`/`y` de la zona activa;
- recuadros y flechas con SVG (`evolvePath` para dibujarlas);
- `Phone` u otro marco si la referencia muestra dispositivo.

## 7. Clip de pódcast / entrevista

**Señales:**
- uno o dos hablantes, a veces en pantalla dividida;
- subtítulos grandes palabra a palabra;
- barra de título o nombre;
- forma de onda;
- logo del pódcast.

**Medir:**
- disposición (dividido arriba/abajo, cambio de plano por quien habla);
- subtítulos;
- barra de título;
- color de acento.

**Construir:**
- `ARoll` (uno o dos);
- `WordPop`;
- forma de onda con `@remotion/media-utils` (`visualizeAudio`) si aparece;
- cambio de plano en los turnos (silencios entre hablantes).

## 8. Producto / promo / anuncio

**Señales:**
- producto como héroe con giros, zooms y fondos de color;
- textos de beneficio cortos;
- precio o oferta;
- CTA final;
- ritmo muy marcado con la música.

**Medir:**
- estructura (problema → producto → beneficios → prueba → CTA) y duración de cada parte;
- tipografía de los beneficios;
- tratamiento del producto (sombra, reflejo, rotación);
- CTA.

**Construir:** `Cutout` del producto (`cutout.py` sin `--mono`) con rotación y escala animadas, textos con `EditorialBlock` o un componente propio y la tarjeta CTA como escena final.

## 9. Listado / ranking / «top N»

**Señales:**
- números grandes («#3»);
- una tarjeta o escena por elemento con estructura repetida;
- barra de progreso o contador.

**Medir:**
- plantilla de cada elemento (número, título, imagen, dato);
- transición entre elementos;
- duración por elemento.

**Construir:** una escena-plantilla parametrizada que se instancia por elemento. Este es el caso válido para generar escenas con un bucle: se controlan juntas.

## 10. Carrusel de fotos / slideshow

**Señales:**
- fotos que se suceden con fundidos o empujes;
- Ken Burns;
- texto superpuesto mínimo;
- música.

**Medir:** duración por foto, tipo y duración de la transición, dirección del movimiento y etalonaje.

**Construir:** `Img` a sangre + `Camera` (zoom lento) + `FadeIn` / `Push` entre fotos.

---

## Formatos híbridos y desconocidos

Si la referencia no encaja, no la fuerces: describe sus componentes (fondo, protagonista, texto, transición, cámara, sonido) con las métricas y construye cada componente con la plantilla, o con uno nuevo si no existe. Lo que manda siempre son las medidas y lo que se ve en los fotogramas.
