# Entrega

## Qué se entrega en cada episodio

1. **4 partes mp4 en máxima calidad** (`split4.py`): el máster de `splice.py` (≈1,4 GB, x264 CRF 20,
   ≤10 Mbps, AAC 192k, −14 LUFS) cortado en fotogramas clave en 4 trozos de ≈350 MiB, cada uno reproducible.
   Envíalas con un solo `SendUserFile` (`display: "attach"`), con los tramos en el pie: "0:00–4:46, …".
2. **Archivo único optimizado** (`encode_optimizado.sh`): 1080p H.264 High, 2 pasadas a 2400 kb/s,
   ≈350 MB. Se abre en cualquier equipo y YouTube lo acepta. Es el que Ali pidió como "resolución optimizada".
3. **HEVC** (`encode_hevc.sh`, solo si pide "el video completo en la más alta resolución" en un archivo):
   1080p H.265 a 2620 kb/s, `-tag:v hvc1`, ≈380 MiB. Más nítido a igual tamaño; algunos Windows necesitan la
   extensión HEVC (VLC siempre lo abre).
4. **Para YouTube** (`SendUserFile` aparte): `miniatura_1.jpg`, `miniatura_2.jpg`, `descripcion_youtube.txt`,
   `creditos_completos.txt`.

Orden: primero las 4 partes y los textos (en cuanto termina la mezcla final), después el archivo único.

## Límites que hay que respetar

- `SendUserFile` admite hasta 400 MiB por archivo: por eso las partes y el archivo optimizado.
- No hay forma de subir el video a su Google Drive: el conector de Drive solo acepta contenido dentro de la
  llamada (no sirve para 1 GB) y la carpeta compartida no era visible para la cuenta conectada. Se le
  explicó. No ofrezcas subirlo a otros servicios (WeTransfer, GitHub LFS…) por iniciativa propia; una vez
  se empezó a subir a GitHub y Ali lo interrumpió: no lo retomes sin preguntar.
- Partes binarias `.001 .002…` (se unen con `copy /b` o `cat`) funcionan, pero Ali prefirió partes que se
  reproducen solas ("cada una en formato mp4"): usa `split4.py`.
- Descripción de YouTube: máximo 5.000 caracteres. Comentario fijado: máximo 10.000 caracteres.

## Verificación antes de enviar

```bash
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,nb_frames -of compact ARCHIVO
ffmpeg -nostats -i ARCHIVO -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1      # −14.0 LUFS
ffmpeg -v error -i PARTE -t 3 -f null - ; ffmpeg -v error -sseof -3 -i PARTE -f null -   # sin errores
ffmpeg -ss T -i OPTIMIZADO -ss T -i MAESTRO -frames:v 1 -lavfi '[0:v][1:v]psnr' -f null -  # > 30 dB
```
Saca también un fotograma del tramo re-renderizado para confirmar que entró el cambio.

## Descripción para YouTube (`entrega/descripcion_youtube.txt`)

```
TÍTULOS SUGERIDOS
- (3 títulos con gancho: el misterio, la cifra, la paradoja)

===== DESCRIPCIÓN (pegar en YouTube) =====
(párrafo 1: la escena del gancho, en presente)
(párrafo 2: de qué va la historia y las dos preguntas)
(párrafo 3: la pregunta a la audiencia del final del guion: "Cuéntanos en los comentarios…")

CAPÍTULOS
0:00 …
(una línea por tarjeta de capítulo, con el tiempo de la tarjeta)

CRÉDITOS
Música: …
Fotografías CC BY: autores, licencia con enlace, "vía Flickr".
Dominio público: Library of Congress (colecciones), NPS, National Archives, Prelinger…
Fotos adicionales: Unsplash (licencia Unsplash). Mapas: … Gráficos y efectos: creación propia.
Recreaciones: (documentos, planos o chats dibujados)
Lista completa de créditos con enlaces: ver comentario fijado.

#Lugar #Estado #Tema #HistoriaDeEstadosUnidos
```
Revisa los datos del texto contra el guion (fechas, cifras, quién hizo qué).

## Créditos completos (`entrega/creditos_completos.txt`)

```bash
cd edit && $PY ../tools/usados.py && cd ..
$PY tools/creditos.py "NOMBRE DEL EPISODIO" "Línea de música"
```
Agrupa Flickr por autor con sus ids, lista cada ítem de la LoC con fecha y enlace, y pone a todos los
autores de Unsplash en una línea. Debe quedar por debajo de 10.000 caracteres (Cumberland pasó de 13.000 y
hubo que acortarlo).

## Miniaturas (`edit/thumbs.py`, 1280×720)

Dos opciones distintas, con la foto más fuerte del episodio y 2–4 palabras enormes en Bebas:
- Blanco + amarillo con contorno negro, una caja amarilla con texto negro, viñeta.
- Ejemplos que se hicieron: "LA BORRARON / A PROPÓSITO" con una X roja sobre la carretera; "40 AÑOS PARA
  BORRAR UNA CARRETERA" sobre el diagrama; "NADIE LO FIRMÓ / ABIERTO A MANO" con linterna en el túnel;
  "MILES DE NOMBRES / NI UNO DE ELLOS" en pantalla partida antes y hoy; "NUEVA YORK LO PERDIÓ / UN TÚNEL
  DE 1844"; "ARRIBA: LA CALLE / ABAJO: 1844" con un círculo rojo sobre la alcantarilla.
- Etiquetas honestas: si la foto no es del año que dice el texto, no pongas el año (se cambió "1867" por
  "ENTONCES"). El círculo rojo tiene que rodear de verdad lo que señala.

## Mensaje final a Ali

Breve, en español: qué se envió (con tamaños y tramos), que se revisó, de dónde sale el material (y que no
hay nada con riesgo de reclamo), qué falta si algo falta, y que el código quedó en el repositorio.
