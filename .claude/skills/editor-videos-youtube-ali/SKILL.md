---
name: editor-videos-youtube-ali
description: Editor de videos YouTube de Ali. Convierte una locución (mp3) y un guion (PDF) en un documental completo para YouTube en español, al estilo de los episodios Laurel Hill, I-80 Wyoming, Cumberland Gap, Donner Pass y Atlantic Avenue. Hace Ken Burns sobre fotos de archivo y de stock sin copyright, mapas animados con relieve real, diagramas propios, textos en pantalla sincronizados palabra a palabra, música baja bajo la voz y efectos de sonido. Entrega el video en 4 partes mp4 y en un archivo único optimizado, con miniaturas, descripción con capítulos y créditos. Úsala siempre que Ali (o cualquier usuario) adjunte una locución y un guion y pida "el siguiente video", "una edición parecida", "mismo proceso", "un video para YouTube que retenga la atención", o pida bajar imágenes de stock sin copyright, bajar la música para que no opaque al narrador, partes en mp4, la versión optimizada, miniaturas, descripción o créditos de uno de estos documentales; también para cambiar la música de un episodio ya hecho.
---

# Editor videos YouTube Ali

Documentales de 18–19 minutos para YouTube, narrados en español, sobre lugares e infraestructuras de
Estados Unidos (túneles, pasos de montaña, carreteras). Todo se monta por código: un motor en Python
compone cada fotograma (1920×1080, 30 fps) a partir de una línea de tiempo anclada a las palabras de la
locución, y ffmpeg codifica la entrega. El motor, las herramientas y las fuentes están en `scripts/` y
`assets/`; las instrucciones finas, en `references/`.

## Quién es Ali y qué espera (preferencias fijas)

- **Idioma:** escribe en español y espera respuestas en español, cortas, con el estado del trabajo y un
  tiempo estimado. Sus mensajes típicos son "okay, envíame el video cuando esté listo" o "¿ya está listo el
  video?": responde con el porcentaje y el tiempo que falta, y envía los archivos en cuanto estén, sin
  esperar a que pregunte otra vez.
- **El encargo de siempre:** "edición parecida a la anterior, mismo proceso, baja las imágenes del stock,
  sin copyright, que retenga la atención del espectador, bájale un poco a la música y sonidos para que no
  opaque la voz del narrador". El video dura exactamente lo que dura la locución.
- **Retención:** dinámico y fluido; los primeros 4–5 minutos, con más ritmo. Un cambio de plano cada
  2,5–5 s, textos con palabras clave resaltadas y mapas o diagramas cada pocos planos.
- **Monetización sin reclamos:** solo material que se pueda monetizar: dominio público, CC0, licencia
  Unsplash, "No known copyright restrictions" y CC BY con atribución. Nunca CC BY-SA, NC, ND ni material sin
  licencia clara. Hubo un reclamo de copyright en uno de los videos: desde entonces **la música sale de la
  Biblioteca de audio de YouTube Studio** (ver más abajo) y se evitan las películas de archivo.
- **Entregas:** 4 partes mp4 en máxima calidad (cada una por debajo de 400 MiB) + un archivo único
  optimizado H.264 1080p de unos 350 MB; si pide "la más alta resolución en un solo archivo", además la
  versión HEVC. Siempre: 2 miniaturas, descripción con títulos, capítulos y créditos, y créditos completos
  para el comentario fijado.
- **Nunca** pedirle contraseñas ni subir sus archivos a servicios externos por iniciativa propia.

## Flujo de trabajo

Usa una tarea por fase (transcribir · material · montaje · audio/render/entrega) y avisa a Ali al terminar
cada una. Las fases largas (render, codificación) van en segundo plano con `setsid nohup`, y se esperan por
PID (`while kill -0 PID`), nunca con `pgrep -f` sobre un patrón que aparece en el propio comando de espera.

1. **Proyecto.** `bash scripts/herramientas/nuevo_proyecto.sh PROYECTO voz.mp3 guion.pdf` crea
   `edit/ tools/ work/ out/ entrega/ assets/{img,vid,map,score,yt,fonts}`, copia el motor y extrae el guion.
   Anota la duración exacta de la locución: es el `TOTAL` de todo lo demás.
2. **Transcripción.** faster-whisper `medium` (o `small` si va lento) con los nombres propios del guion en el
   prompt → `work/words.json`. Coteja con el guion: si la locución dice algo que no está en el guion (pasó
   en Laurel Hill), avisa a Ali y cúbrelo en pantalla. Detalle: `references/flujo-detallado.md`.
3. **Material.** Busca en paralelo: Unsplash (con un subagente que usa el MCP de Unsplash), Library of
   Congress, Flickr con licencias libres, Wikimedia Commons (solo PD/CC0/CC BY) y datos abiertos para mapas.
   Revisa todo en hojas de contacto antes de elegir. Licencias y comprobaciones: `references/material-y-licencias.md`.
4. **Mapas y diagramas.** Mapas base con relieve real (teselas Mapzen + Natural Earth; calles reales con
   datos abiertos cuando es una ciudad) y diagramas propios del episodio en un `gfxN.py` nuevo.
   Ver `references/montaje-y-retencion.md`.
5. **Montaje.** `edit/timeline.py`: un `add(t, base, overlays, transición)` por plano, anclado con
   `w("palabra", segundo_aprox)`. Estructura fija: gancho → dos preguntas → título → capítulos con tarjeta →
   CTA de suscripción donde lo pida el guion → conclusión que responde las preguntas → CTA de comentarios.
   Valida con `check.py`, revisa todos los planos con `mids.py` y corrige antes de renderizar.
6. **Música y audio.** Pide a Ali 9 pistas de la Biblioteca de audio de YouTube (una por capítulo) en cuanto
   empiece el proyecto; si no llegan, compone una banda sonora original con `score.py`. Mezcla con
   `audio.py`: música baja y con ducking bajo la voz, efectos sintetizados aún más bajos.
   Niveles exactos: `references/audio-y-musica.md`.
7. **Render y entrega.** `render.py --workers 4` (≈1 h), luego `terminar.sh` encadena la mezcla final
   (`splice.py`, voz a −14 LUFS), las 4 partes y el archivo optimizado. Verifica cada archivo y envíalo con
   `SendUserFile`. Ver `references/entrega.md`.
8. **Guardar.** Copia código y datos ligeros (sin medios) a `video/<episodio>/` del repositorio, con un
   README, y haz commit y push en la rama de trabajo.

## Música: la regla actual

1. Al empezar cada episodio, pide a Ali que descargue de **YouTube Studio → Biblioteca de audio → Música**,
   filtrando por **Atribución no obligatoria**, 9 pistas de al menos 2–3 minutos, con una tabla de capítulo,
   género y ánimo (en `references/audio-y-musica.md` está la tabla que se le mandó para Atlantic Avenue).
   Desde aquí no se puede entrar a su cuenta de YouTube.
2. Mientras tanto avanza con todo lo demás; la música solo hace falta en la mezcla.
3. Si las pistas no llegan cuando la imagen está lista, usa `score.py` (música original sintetizada nota a
   nota: no puede recibir reclamos) y dile que se cambia en unos 30 minutos si después manda las pistas.
4. No vuelvas a usar música de Kevin MacLeod: es CC BY pero recibe reclamos automáticos de Content ID.

## Controles de calidad que no se saltan

- `check.py` sin anclas perdidas ni archivos faltantes; ningún plano de menos de 0,6 s.
- Hojas de `mids.py` revisadas plano a plano (el fotograma central de cada plano) y mapas revisados con
  `sel.py maps`: textos cortados, etiquetas superpuestas, mapas con bordes negros, imágenes que no
  corresponden a lo que dice la voz, marcas comerciales visibles, fotos al revés.
- Mezcla medida: voz integrada −14 LUFS en el archivo final; pista de música alrededor de −33/−34 LUFS
  y efectos alrededor de −35/−36 LUFS (medidos en los stems antes de normalizar).
- Archivos finales comprobados con ffprobe (duración = locución, 1920×1080, audio presente), decodificación
  sin errores al inicio y al final de cada parte, y PSNR del archivo optimizado frente al máster (> 30 dB).

Las correcciones concretas que se hicieron en este chat (y por qué) están en
`references/lecciones-aprendidas.md`. Léelo antes de montar un episodio nuevo: casi todos los errores
fueron de revisión visual y son fáciles de repetir.

## Referencias

| Archivo | Cuándo leerlo |
| --- | --- |
| `references/flujo-detallado.md` | Comandos exactos de cada fase, en orden, con rutas y parámetros. |
| `references/material-y-licencias.md` | Antes de buscar o elegir material: fuentes, licencias aceptadas, comprobaciones de derechos, límites de cada sitio. |
| `references/montaje-y-retencion.md` | Antes de escribir `timeline.py`: estructura del video, recursos del motor (bases, overlays, transiciones, mapas, diagramas) y reglas de diseño. |
| `references/audio-y-musica.md` | Antes de mezclar: pedido de pistas a Ali, `score.py`, efectos y niveles. |
| `references/entrega.md` | Al codificar y enviar: partes, archivo optimizado, HEVC, descripción, créditos, miniaturas, repositorio. |
| `references/lecciones-aprendidas.md` | Siempre, antes de empezar: lista de errores y correcciones de este chat. |

## Scripts incluidos

- `scripts/motor/`: el motor completo de la última versión (Atlantic Avenue). `engine.py`, `gfx.py`–`gfx6.py`
  (bases, overlays y diagramas de todos los episodios), `maps.py`, `render.py`, `splice.py`, `audio.py`,
  `score.py`, `check.py`, `mids.py`, `sel.py`, `stills.py`, `words.py`, `thumbs.py` y `timeline.py` como
  ejemplo completo de un episodio (244 planos).
- `scripts/herramientas/`: `nuevo_proyecto.sh`, `transcribe.py`, `udl.py` (descargas de Unsplash), `loc.py`
  y `locq.py`, `fl.py` y `flsheet.py`, `wm.py`, `ia.py`, `usq.py`, `scenes.sh`, `filmsheet.py`,
  `fetch_tiles.py`, `natural_earth.py`, `stereo_crop.py`, `usados.py`, `creditos.py`.
- `scripts/entrega/`: `split4.py`, `encode_optimizado.sh`, `encode_hevc.sh`, `terminar.sh`.
- `assets/fonts/`: Bebas Neue, Playfair Display, Poppins, JetBrains Mono, Special Elite y Oswald
  (licencias OFL/Apache, libres para uso comercial).

Dependencias: Python 3 con `numpy scipy pillow opencv-python-headless faster-whisper`, ffmpeg con
libx264 y libx265, `pdftotext` (poppler-utils). 4 núcleos y unos 15 GB libres por episodio.
