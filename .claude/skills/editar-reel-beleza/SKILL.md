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

## 7. Revisar y entregar
- `cd editor && npm run lint`.
- Para revisar: `npx remotion render Borrador out/borrador.mp4 --concurrency=4`. Saca fotogramas en cada beat (hojas de contacto con ffmpeg) y comprueba que nada tapa la cara, que los textos no se cortan y que el gráfico aparece en su palabra.
- Para la versión final: `npx remotion render Borrador out/final_alta_calidad.mp4 --crf=16 --audio-bitrate=320k`.
- Para que el usuario lo revise en el chat, envía una copia de menos de 30 MB (x264 en 2 pasadas a ~3,4 Mbps). La final de alta calidad se entrega por el repositorio (< 100 MB) en `entregas/`.
- Explica cada decisión citando la frase que la provoca.
