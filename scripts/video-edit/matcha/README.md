# Edición: Té Matcha · Laboratorios Outlet

Re-edición del UGC `IMG_3040.MOV` (Drive, carpeta *tOMA mATCHA*). Resultado: [`media/edits/matcha-outlet-editado.mp4`](../../../media/edits/matcha-outlet-editado.mp4), 1080×1920, 30 fps, 43,4 s, audio a -14 LUFS.

## Qué se hizo

| Elemento | Detalle |
| --- | --- |
| Subtítulos viejos | Estaban quemados en las filas 205-262 del original. El encuadre nunca muestra nada por encima de la fila 300, así que desaparecen sin borrones. |
| Subtítulos nuevos | Montserrat Black, de 1 a 3 palabras, cada palabra entra con un pop al decirla. Las palabras clave van en caja lima con texto negro. |
| Zooms | Cada plano hace un empuje lento centrado en la cara (seguimiento con OpenCV) y hay 18 punch-ins en palabras de énfasis. Tres de ellos van hacia la lata o el polvo. El zoom se limita para que la cabeza nunca baje de la fila 1130, así la franja inferior queda libre para los textos. |
| Transiciones | En los 10 cortes: whip pan, zoom blur, giro, flash y glitch RGB. |
| B-roll | Primer plano del polvo de matcha (seg. 5,3) e inserto cinético "HOJA COMPLETA" (seg. 8,4). La foto de la lata va en la tarjeta final. |
| Motion graphics | Gancho "6 RAZONES", "RAZÓN #N" mientras ella dice el ordinal, etiqueta por sección, emojis animados, sacudida de cámara en "me dejan como…", logo de marca y tarjeta final con CTA. |
| Regla de composición | Ningún elemento gráfico toca la cabeza, el rostro ni el producto (la lata, cerrada o abierta). Cada elemento busca, durante todo su tiempo en pantalla, una posición libre de la elipse de la cabeza y de la caja de la lata; si un emoji no cabe en ningún lado, se omite. `--check` lo verifica frame por frame. |
| Audio | Voz con filtro pasa altos, EQ de presencia y compresión. Música que baja sola bajo la voz y sube en la tarjeta final. SFX sintetizados sincronizados con cada animación. |

## Licencias de los recursos

- Música: "Funshine" de [FreePD](https://archive.org/details/freepd), dominio público (CC0). No requiere atribución.
- Fuentes: Montserrat y Anton (Google Fonts, SIL OFL).
- Emojis: Noto Color Emoji (SIL OFL).
- Efectos de sonido: generados por código en `sfx.py`.

## Cómo regenerarlo

Requisitos: ffmpeg, Python 3 con `numpy pillow scipy librosa "opencv-contrib-python-headless<5"`. Solo para volver a transcribir hace falta también `faster-whisper`.

```bash
W=scripts/video-edit/matcha
A=/tmp/matcha-assets                 # fuentes, música, emojis y SFX (no se versionan)
SRC=media/raw/IMG_3040.MOV           # el original de Drive (media/raw está en .gitignore)

$W/fetch_assets.sh $A
# opcional, ya están en el repo:
#   python3 $W/facetrack.py $SRC $W/faces.json      # cara por frame
#   python3 $W/cantrack.py $SRC $W/cans.json        # lata por frame (SIFT + correlación)
#   ffmpeg -i $SRC -vn -ac 1 -ar 16000 voice.wav && python3 $W/transcribe.py voice.wav words_raw.json
python3 $W/render.py $W $A $SRC /dev/null --check             # 0 contactos con cabeza/rostro/lata
python3 $W/render.py $W $A $SRC /tmp/video_noaudio.mp4        # ~3 min en 4 núcleos
python3 $W/mix_audio.py $W $A $SRC $A/music/Funshine.mp3 /tmp/mix.wav
ffmpeg -i /tmp/video_noaudio.mp4 -i /tmp/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
       -movflags +faststart media/edits/matcha-outlet-editado.mp4
```

Para revisar frames sueltos sin renderizar todo: `python3 $W/render.py $W $A $SRC /tmp/prev --frames 90,300,1290`.

Todo lo creativo está en la sección **EDIT TIMELINE** de `render.py`: cortes y transiciones, zooms, B-roll, secciones, emojis, palabras clave y la hoja de SFX. `words.json` es la transcripción corregida a mano ("helado" → "la hoja", "Vente, muestra" → "Ven, te muestro").
