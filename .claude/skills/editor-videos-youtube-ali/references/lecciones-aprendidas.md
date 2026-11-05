# Lecciones aprendidas en este chat

Errores reales de los cinco episodios (Laurel Hill, I-80 Wyoming, Cumberland Gap, Donner Pass, Atlantic
Avenue) y cómo se resolvieron. Agrupados por fase.

## Pedidos y comunicación

- Ali escribe "okay, envíame el video cuando esté listo" y "¿ya está listo el video?" varias veces mientras
  se renderiza: responde con porcentaje y minutos restantes, y envía solo, sin esperar otro mensaje.
- Cuando adjunta locución y guion con "el siguiente video", no hagas preguntas: arranca con el mismo
  proceso. Pregunta solo lo que bloquea (las pistas de música).
- Si un adjunto no llega ("no space left on device"), libera disco y pídele que lo vuelva a subir.
- Si la locución no coincide con el guion en algún tramo, cúbrelo visualmente y avísale para que lo regrabe.

## Material y derechos

- Un reclamo de copyright llegó en uno de los videos: se dejó la música de Kevin MacLeod y se pasó a la
  Biblioteca de audio de YouTube (o a música original). Las películas de Prelinger también pueden recibir
  reclamos: en Atlantic Avenue no se usaron.
- "Unrestricted" en la API de la LoC no significa libre de derechos: lee `rights_advisory`. Una foto de la
  colección Vergara ("Publication may be restricted") se quitó y su tramo se re-renderizó.
- No intentes esquivar protecciones de sitios (Pixabay, Mixkit, cambiar el user-agent de Flickr para
  evitar el bloqueo). Si una fuente se bloquea, usa otra legítima o pídele el material a Ali.
- Wikimedia devolvía 429 constantemente: tamaños estándar, respetar `Retry-After`, máximo 2 descargas.
  Flickr: `FL_SLEEP=10` entre descargas.
- No pongas datos personales (correo) en el user-agent de las herramientas ni en el código del repositorio.
- Una foto de stock tenía el logotipo "TWA" en una tapa de alcantarilla: se cambió. Busca marcas.
- La película del NPS sobre Cumberland Gap tenía música con derechos: descartada aunque la imagen fuera PD.

## Transcripción y sincronía

- El modelo `medium` tarda ≈16–20 min; `small` va más rápido cuando hay prisa.
- Palabras que no se encuentran: números partidos ("2.300", "20.000"), nombres mal transcritos ("Booth" →
  "Wood"), palabras con tilde distinta. Usa la primera parte del número o una palabra vecina, y amplía la
  ventana de búsqueda (`words.at` busca desde `near - 4.0`).
- Si una zona sale mal, se retranscribe y se guarda en `work/retx.json`; `words.py` reemplaza solo ese tramo.

## Selección de imágenes

- Los ids de Unsplash leídos de las hojas confunden I/l/1 y O/0: `res()` en `timeline.py` los corrige
  comparando con los archivos en disco.
- Revisa que cada imagen cuente lo que dice la voz en ese segundo. Se cambiaron: una montaña seca puesta
  como "avalancha", maquinaria oscura puesta como "el tren de 1952 atrapado en la nieve", un campamento
  de California que no correspondía, una foto de Hanna que era otra carretera, una valla de fauna que no era
  la de la historia.
- Fotos de visitantes o de archivo muy oscuras: linterna más amplia o cambiar la foto.
- Primeros planos de desconocidos (visitantes en fotos de Flickr): evítalos; personas reconocibles solo si
  son los protagonistas públicos de la historia.
- Si no hay retrato libre de una persona, tarjeta tipográfica con su nombre; nunca su nombre sobre otra cara.
- Estereografías: recortar la mitad izquierda sin el cartón (`stereo_crop.py`).
- Películas anamórficas 352×480: pasar a píxel cuadrado. Clips con marcas de tiempo de VHS: recortar con zoom.
- Escaneos girados: comprobar la orientación (uno quedó al revés después de girarlo 90°).

## Montaje y gráficos

- Textos cortados arriba en fotos enmarcadas: `y=0.065`, `maxw` 0.85–0.9.
- Leyenda de `fr()` y `LowerThird` a la vez se pisan: quitar la leyenda.
- Texto amarillo sobre mapas antiguos o planos claros: `Darken(0.35–0.4)`.
- Sello rojo sobre ladrillo rojo: no se lee; usar amarillo.
- Etiquetas de mapas cortadas en los bordes: moverlas hacia dentro o cambiar el lado (`side`).
- Cámara de mapa saliéndose del mapa base (bordes negros): limitar zoom mínimo y centro (hecho para `aa_`).
- Puntos fuera del mapa base (Jamaica, en Queens, no entraba en el mapa de la ciudad): cortar la ruta en el
  borde y poner la etiqueta "HACIA QUEENS" dentro.
- Diagramas: etiquetas superpuestas (reducir alcance), objetos fuera de cuadro (locomotora que entraba
  tarde), formas mal dibujadas (techo del cobertizo que no seguía la pendiente), elementos tapados por el
  orden de dibujo (barracones bajo la nieve), gráficos pequeños o vacíos (acercar y llenar), linterna demasiado
  oscura (subir `r` y `amb`), relleno de tierra sobre la bóveda que quedaba negro (polígono mal ordenado).
- Diagramas que tocan datos (cifras, fechas): copiar las cifras exactas del guion, con su conversión métrica.
- `aa_poly` con puntos NaN da avisos: el filtro ya está en `gfx2.py`.

## Audio

- Ali pidió dos veces bajar música y efectos: niveles de `audio-y-musica.md`; no los subas por tu cuenta.
- La primera banda sonora sintética tenía ruido agudo por aliasing: tablas de onda con armónicos limitados.
- `audio.py` necesita `s.end` en cada plano para colocar efectos: se asigna en `build_sfx`.

## Render, codificación y entrega

- Un `filter_complex` que leía dos veces el mismo máster hizo crecer ffmpeg a 14 GB: `splice.py` codifica
  ahora por trozos de 90 s con memoria constante y re-renderiza solo los tramos cambiados.
- El contenedor se reinició y mató procesos: todo lo largo con `setsid nohup`, y las codificaciones por
  trozos reanudables.
- Esperas que nunca terminaban: `pgrep -f "patrón"` encontraba el propio comando de espera (o el shell
  que lanzó el proceso). Espera por PID (`while kill -0 PID`) o con el patrón entre corchetes (`[r]ender`).
- Una espera con `grep "wrote"` terminó antes de tiempo porque `splice.py` escribe "wrote seg0": usa un
  patrón exacto del archivo final.
- `pkill -f` mató su propia shell: matar por PID.
- Disco lleno en medio de un episodio (los adjuntos de Ali no llegaron): borrar trozos tras unirlos,
  `out/splice/`, partes ya enviadas, películas de episodios entregados. `rm -rf $VAR/…` está bloqueado por
  seguridad: rutas absolutas literales.
- `renice` solo afecta al hilo principal: para bajar la prioridad de x265 hay que recorrer `/proc/PID/task/*`.
- Dos codificaciones a la vez en 4 núcleos se ralentizan mutuamente: prioriza la que Ali espera.
- Descripción de más de 5.000 caracteres: versión compacta. Créditos de más de 10.000: Unsplash en una línea.
- `SendUserFile` hasta 400 MiB; Drive no sirve para archivos grandes; partes binarias no gustaron: partes mp4.
