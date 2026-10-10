---
name: editar-reel-beleza
description: Edita un vídeo en crudo de Beleza (persona hablando a cámara) y lo convierte en un Reel vertical 1080×1920 con Remotion. Corta silencios, mantiene el audio original, añade títulos grandes y recursos visuales animados según lo que se dice, hace zoom solo en frases clave dichas con la voz alta y añade música de fondo y efectos de sonido propios. Úsala cuando el usuario pase un vídeo en crudo para editar, pida "edita este vídeo" o "otro día del reto", o quiera aplicar el estilo de marca a un nuevo vídeo.
---

# Editar un Reel de Beleza

El estilo vive en `editor/estilo.md`. **Léelo entero antes de empezar.** La sección 10 (correcciones del usuario) manda sobre todo lo demás. Cuando el usuario corrija algo y le guste, añádelo allí como nueva regla numerada.

## 0. Entorno (una vez por sesión)
- Node ≥ 20, ffmpeg y Python 3. Whisper en un venv: `python3 -m venv <venv> && <venv>/bin/pip install faster-whisper numpy`.
- El modelo de Whisper se descarga de `huggingface.co`, que debe estar permitido en el acceso a red del entorno.
- Dependencias del proyecto: `cd editor && npm ci`. Si Remotion no puede descargar su Chrome, `remotion.config.ts` ya usa el Chromium local cuando existe.
- La fuente **TAN Pearl** es comercial y no está en el repositorio: pide el `.otf` y cópialo en `editor/public/fonts/TAN-Pearl-Regular.otf`.

## 1. Conseguir el vídeo
- Los archivos de más de 30 MB no se pueden subir al chat. Pide un enlace de Google Drive con "Cualquier persona con el enlace" y descárgalo en su propia carpeta: `curl -L -o crudo/video/crudo.mp4 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`.
- Comprueba resolución, fps y duración con `ffprobe`. Si es 4K vertical y la persona sale en plano general, recorta sin escalar para dejar un plano medio. Ajusta `RECORTE` en `scripts/preparar.py` para que la cara quede al ~43 % de altura y actualiza `CARA` en `Footage.tsx`.

## 2. Transcribir
`<venv>/bin/python -I editor/scripts/transcribir.py crudo/video/crudo.mp4 editor/scripts/transcripcion.json`
- Revisa las palabras de baja confianza y los nombres propios (p. ej. "Luma Body") y confírmalos con el usuario.
- Transcribe siempre desde el **audio del propio vídeo**: un audio suelto puede ir desfasado.

## 3. Cortar silencios y generar el vídeo editado
`python3 editor/scripts/preparar.py crudo/video/crudo.mp4 editor/scripts/transcripcion.json`
- Corta los silencios de más de 0,3 s (−35 dB, 0,08 s de margen) a fotograma exacto. Genera `public/crudo/editado.mp4` con el **audio original** y `src/data/edit.json`, con las palabras ya reasignadas a la nueva línea de tiempo y su volumen (`db`).
- Con `--sin-video` solo regenera los datos.
- **Nunca** recortes audio por tramo dentro de Remotion: `<Audio trimBefore>` dentro de `<Sequence>` repetía el inicio en cada corte.
- Verifica la sincronía: correlaciona el audio de `editado.mp4` con el original en cada tramo; el error debe ser menor de un fotograma.

## 4. Escribir los gráficos (`editor/src/components/Beats.tsx`)
Cada "beat" nace de una frase concreta, anclada con `at("frase")`. El anclaje acepta alternativas como `"3|tres semanas"`, porque Whisper alterna cifras y letras. Si una frase no existe, el render falla a propósito.
- **Títulos grandes:** TAN Pearl (o Glacial Bold en las cifras), en Marfil o Durazno. Van en el componente `Top`, con la base en y = 580, encima de la cabeza.
- **Recursos de apoyo:** listas, tarjetas, etiquetas y contadores en Glacial Indifference. Van en el componente `Bottom`, entre y = 1180 y 1560, sobre las piernas y fuera de la interfaz de Reels.
- **Nada a menos de ~100 px de la cara.** No hay subtítulos.
- La animación debe expresar el significado: un número que cuenta, una lista que se va marcando, una palabra tachada que da paso a otra, etapas que se encienden…
- **Cuando la persona señala un hueco**, el gráfico nace allí (p. ej. el calendario 3D de `public/graficos/calendario_base.png`). Mantén la cámara fija mientras señala.
- Para preparar una imagen nueva con fondo blanco usa `scripts/calendario.py` como base: quita el fondo y permite redibujar las partes que se animan.

## 5. Cámara (`editor/src/components/Footage.tsx`)
- Plano fijo. Zoom suave 1,0 → 1,12 solo en `FRASES_CLAVE` cuyo pico de volumen supere en ≥ 3,5 dB la mediana, con al menos 4 s entre zooms.
- Transiciones de tema sin zoom: destello Durazno + desenfoque breve.
- Actualiza `FRASES_CLAVE`, `TRANSICIONES` y `SIN_ZOOM` para cada vídeo.

## 6. Música y efectos de sonido
- `<venv>/bin/python -I editor/scripts/audio_marca.py` sintetiza en `public/audio/` la música (con la duración del vídeo editado) y 13 efectos. Son propios, así que no hay problemas de derechos en Instagram.
- En `editor/src/components/Sonido.tsx` cada efecto se ancla con `at()` al mismo instante que su animación. Elige el tipo según lo que hace el gráfico (ver `estilo.md` §10.14). Úsalos solo en los momentos importantes, varía los tipos y no los apiles.
- Verifica la mezcla restando la voz original del render: la voz debe quedar con ganancia 1 y desfase 0, la música ~16 dB por debajo y ningún efecto por encima de la voz.

## 6b. Organización por días y lecciones del día 2
- **Cada día va en su carpeta y no se toca lo entregado:** `src/dia2/` (composición `Dia2`, con su `timing.ts`, `Footage.tsx`, `Beats.tsx`, `Sonido.tsx`, `Objetos3D.tsx` y `data/edit.json`), `public/dia2/` (vídeo editado, fragmentos de apoyo y `audio/`) y `scripts/dia2/`. El día 1 sigue siendo la composición `Borrador`. Para un día nuevo copia `src/dia2` → `src/diaN` y regístralo en `Root.tsx`.
- **Crudos a 59,94 fps (DJI Osmo Pocket 3, HEVC 10 bits):** pásalos antes a 30 fps CFR con `scripts/dia2/convertir.sh`; `preparar.py` corta por número de fotograma a 30 fps. Si el crudo ya es 1080×1920, **no recortes** (habría que escalar): la cara queda al ~40 % de alto y los títulos, con base en y = 550, siguen quedando sobre la cabeza.
- **Tomas repetidas:** lista en `TOMAS` solo los tramos buenos (fuera intentos fallidos, frases que se reinician y el "listo, chao"). Si Whisper funde una frase repetida en una palabra larga, retranscribe ese tramo suelto y corrige los tiempos en `CORRECCIONES`.
- **Corte de audio exacto:** `aselect` corta por bloques del flujo de audio (con PCM el error se acumula hasta ~50 ms); pon `asetnsamples=n=16:p=0` antes de `aselect`. Comprueba siempre la sincronía tramo a tramo.
- **Toma de apoyo:** solo fragmentos cortos (≈1 s cada uno) que entran en la palabra que los nombra, con flash blanco y sonido de obturador; nada de títulos arriba durante el apoyo (la cabeza de la otra persona está allí), solo la etiqueta abajo.
- **Objetos 3D:** se modelan con three.js en `Objetos3D.tsx` (`@remotion/three`, acabado clay mate con la paleta de marca) y se animan según la frase (el pin cae y se clava, la cinta se desenrolla, el lápiz escribe, el candado se cierra). Van a los lados de la cabeza (x < 360 o x > 740). Canva genera buenas referencias, pero desde aquí solo deja descargar miniaturas de 200 px. Para renderizar WebGL en este entorno: `--gl=swangle --concurrency=2` (con 4 pestañas WebGL el render se queda colgado sin error; vigila que el contador de fotogramas avance).

## 6c. Rutinas con voz en off (días 4, 5 y 6)
- La voz en off llega en un audio aparte; el audio del crudo suele ser charla de detrás de cámaras. Si no llega, pídela.
- `scripts/rutinas/preparar_voz.py <diaN> <voz.m4a>` (añade sus `TOMAS`), `scripts/rutinas/montar.py <diaN> <crudo30.mp4> <yunet.onnx>` (añade su `PLAN`: frase → segundo del crudo; evita los momentos en que mira a cámara) y `scripts/rutinas/audio.py <diaN>`.
- Si el crudo no tiene un plano con el fondo vacío, no lo añadas a `FONDO`: la silueta sale por color. Revisa las cajas de la cabeza dibujándolas sobre `apoyo.mp4`.
- Si la cabeza se mueve mucho dentro de cada toma (ella en el centro, plano general), usa la maqueta de columnas del día 6 (`src/dia6/Maqueta.tsx`) en vez de `Laterales`.
- Render con 3D: `scripts/render_trozos.sh <Composición> out/<salida>.mp4 450 16` (reanudable: si cambias solo un tramo, borra ese `out/trozos_<Composición>/pNNN.mp4` y vuelve a lanzarlo).
- Mide la voz en off (`ffmpeg -af ebur128`): si no ronda −16 LUFS, ajusta `musica`/`musicaCierre` y el volumen de los efectos de `Rutina` en la misma proporción (nunca normalices la voz).
- Si hay varios crudos o se quiere variar el ritmo (cámara lenta, timelapse, pantalla partida) usa `scripts/dia7/montar.py` como base, y `src/dia7/Base7.tsx` para reencuadres, etalonaje por momento y cortinas.
- Si la cabeza está pegada al borde superior, el título va en la franja baja (`TituloBajo` del día 7).
- Si el render a CRF 16 pasa de 100 MB, recodifica a 2 pasadas (≈ 7,5 Mbps de vídeo + copia del audio) para el repositorio.

## 6d. Día 9 (rutina integrada) — herramientas nuevas
- Si en la voz en off Whisper funde la toma repetida con la buena (tiempos adelantados hasta 1 s o una palabra duplicada en el borde de una toma descartada), transcribe la voz YA LIMPIA (`public/<dia>/voz.wav`) y aplica sus tiempos con `scripts/dia9/retiempos.py` (adelanta al final del silencio los inicios que caen en una pausa).
- `scripts/dia9/montar.py` añade a las tomas: `"congela"` (fotograma congelado para la pizarra de análisis), `"splitv"` (pantalla partida vertical, 540 px de cada momento sin escalar) y los mosaicos 2×2 de zonas en archivos aparte (`mosaico_intro.mp4`, `mosaico_cierre.mp4`), que en Remotion se abren hacia las esquinas.
- `src/dia9/Base9.tsx`: el "escenario" (toma + gráficos colocados) se encoge a una tarjeta de capítulo con el título en el margen (nunca toca la cara) y hace barridos con desenfoque horizontal (filtro SVG) en los cortes que se indiquen.
- `src/dia9/Maqueta9.tsx`: como la del día 6 pero prueba el otro lado de la cabeza antes de bajar por debajo de ella (no tapa la acción).
- La pizarra (`Pizarra` en `src/dia9/Graficos.tsx`) dibuja sobre el congelado en coordenadas de la toma: mide antes los puntos (fotograma a 540×960 con rejilla de 100 px) y deja ≥ 100 px con la cara.
- Música propia por día: `scripts/dia9/audio_dia9.py` cambia tonalidad, tempo y figura (mismos timbres y limpieza para la voz).

## 6e. Día 10 (a cámara, cierre del reto) — herramientas nuevas
- `scripts/dia10/preparar.py`: igual que el del día 8 (tomas en el orden que se quiera, vídeo por fotogramas y audio a muestra exacta). Si Whisper funde una frase repetida en una palabra de varios segundos, transcribe `public/<dia>/editado.mp4` y aplica sus tiempos con `scripts/dia10/retiempos.py`.
- `scripts/dia10/caras.py`: caja de la cara con YuNet sobre el vídeo editado (a cámara se ve siempre). El modelo se descarga de `huggingface.co/opencv/face_detection_yunet` (raw.githubusercontent.com está bloqueado).
- B-roll de otro día: `scripts/dia10/apoyos.py` corta fragmentos cortos de otro crudo ya pasado a 30 fps.
- `src/dia10/Dia10.tsx`: panel lateral (la toma se desliza y la cara se recalcula con el mismo desplazamiento y zoom), ventana con forma de texto (máscara SVG) y cámara de móvil con fotos. Los dígitos 3D salen de `three/examples/fonts/helvetiker_bold.typeface.json` con `TextGeometry`.
- **Render que se cuelga sin error** (un tramo pasa de 15 min y el registro se queda en "Rendered N/…"): con `--log=verbose` aparece "Cannot decode … falling back to <OffthreadVideo>". El Chromium del entorno no decodifica H.264, así que Remotion pide cada fotograma al servidor y alguna petición no vuelve. Solución del día 10: el vídeo en VP9 sin audio (`ffmpeg -an -c:v libvpx-vp9 -crf 15 -b:v 0 -row-mt 1`, `muted`) y la voz original aparte en WAV a muestra exacta (`preparar.py --solo-audio`); comprueba el desfase (0 ms) antes de renderizar.
- Para matar un render no uses `pkill -f` con el nombre del script: también mata la propia orden. Busca los PID con `ps -eo pid,args`.
- Si un objeto 3D compartido sale pequeño en su columna, dale un lienzo más grande que la columna (el tamaño en píxeles crece con el alto del lienzo) en vez de escalarlo con CSS.

## 7. Revisar y entregar
- `cd editor && npm run lint`.
- Para revisar: `npx remotion render <Composición> out/borrador.mp4 --concurrency=4` (añade `--gl=swangle` si hay objetos 3D). Saca fotogramas en cada beat (hojas de contacto con ffmpeg) y comprueba que nada tapa la cara, que los textos no se cortan y que el gráfico aparece en su palabra.
- Para la versión final: `npx remotion render <Composición> out/final_alta_calidad.mp4 --crf=16 --audio-bitrate=320k` (+ `--gl=swangle --concurrency=2` si hay 3D).
- Para que el usuario lo revise en el chat, envía una copia de menos de 30 MB (x264 en 2 pasadas a ~3,4 Mbps). La final de alta calidad se entrega por el repositorio (< 100 MB) en `entregas/`.
- Explica cada decisión citando la frase que la provoca.
