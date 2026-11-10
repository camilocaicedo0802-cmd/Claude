# Proclama del Pacífico · edición de dos notas periodísticas (prueba)

Dos reels verticales (1080×1920, 30 fps, H.264 + AAC) editados por código con los
recursos de marca de Proclama del Pacífico (cortinillas, rótulo de nombre, logo animado, cierre "Síguenos").
Los videos no se guardan en el repositorio: aquí está todo lo necesario para volver a generarlos.

| Nota | Archivo entregado | Duración | Formato |
| --- | --- | --- | --- |
| 1 · Colombia rompe récord de masacres en la última década | `Nota1_Record_masacres_Colombia_vertical_v3.mp4` | 1:51 | Guion completo en pantalla + gráficos de datos · audio −16 LUFS |
| 2 · Compactadores y obras en Santander de Quilichao | `Nota2_Compactadores_Santander_vertical.mp4` | 2:26 | Reportaje con entrevistas, subtítulos y rótulos · audio −14 LUFS |

## Nota 1 · Récord de masacres (Indepaz)

- **Sin locución**: el material no traía voz, así que el guion ("Video 1" a "Video 6") va completo en pantalla,
  palabra por palabra, con las cifras clave en caja roja (estilo del titular de los reels de Proclama).
- **Titular** de apertura con el diseño de `Ejemplo Reels.jpg` (Roboto Black, franja roja, web debajo).
- **Gráficos animados** con los datos del guion y de la nota web:
  - contadores 97 masacres / 376 personas asesinadas (1 de enero al 9 de octubre de 2026);
  - curva del acumulado mensual de 2026 (14, 9, 14, 13, 10, 9, 9, 9, 7 y 3 casos) frente a los totales de
    2021 (96) y 2022 (94), con la insignia "récord desde 2016";
  - mapa de Colombia (Natural Earth, dominio público) con Cauca (14 masacres, al menos 68 víctimas) y Antioquia;
  - lista de los tres factores que señalan los investigadores;
  - contadores desde 2016 (791 masacres, cerca de 2.900 víctimas).
- **Censura** de palabras sensibles en pantalla (una letra cambiada por `*`): masacre(s), asesinadas/os,
  asesinatos, crímenes, armado(s), ilícitas, ataques y violencia. La lista está en `edit/n1.py` (`lib.CENSOR`)
  y se cambia en una línea si el medio marca otras palabras en rojo.
- **Verificación**: todas las cifras coinciden entre guion, nota web e Indepaz; el corte se rotula como
  "9 de octubre de 2026" (no noviembre), como pide la nota. La suma mensual da 97.
- **Videos de apoyo de Facebook** con crédito en pantalla ("Imágenes de referencia · Video: Cauca Al Día",
  "Tv Norte Noticias", "Cajamarca Real", "Denuncias Ciudadanas Cali"): son ataques recientes en el Cauca, no
  masacres, y así se evita confundir al público. El texto quemado del video de Cajamarca Real se desenfoca.
  Se silenció el audio de los videos que traían groserías ("Tv Norte Noticias", primeros segundos), locución de
  otro medio ("Cajamarca Real") o posible música ("Denuncias Ciudadanas Cali"); solo queda el ambiente.
- **Cierre**: pregunta del guion al público + "Déjanos tu opinión en los comentarios" + cierre "Síguenos".

## Nota 2 · Compactadores, hospital y Calle 5 (Santander de Quilichao)

Material grabado el 2 de julio de 2026 (9 entrevistas, 71 clips de cámara DJI y 110 de iPhone).
La historia sale de las entrevistas:

1. **Compactadores**: la Gobernación, con Emcaservicios, entrega 4 compactadores: 2 para Santander de
   Quilichao (25 y 17 yardas), 1 para Caloto y 1 para Inzá. Hablan el gobernador Octavio Guzmán (solo la
   primera pregunta de ese archivo, como indica su nombre), Jorge Macías (Emcaservicios), el alcalde Luis
   Eduardo Grijalba y el alcalde de Inzá, Delio Hernán Trujillo.
2. **Hospital Francisco de Paula Santander**: primer pabellón; habla la secretaria de Salud, Carolina Camargo.
3. **Calle 5**: el gobernador revisa la obra con el contratista (archivo "Gobernador del Cauca").

Quedaron fuera, por duración y para no desviar la nota: Leonel Barrera (repite la idea de los retrasos),
el alcalde de Caloto, Edgar Gómez y las preguntas políticas (presidente electo, oposición, frigorífico).
Los clips `IMG_2211`–`IMG_2213` son otra pieza (explicador sobre desobediencia civil) y no se usaron.

- Subtítulos corregidos a mano (Whisper decía "Enquilichao", "en caservicios", "recibios sólidos") y alineados
  palabra por palabra con `edit/subs.py`.
- Rótulo de nombre de Proclama (`Rotulo_Nombre_PC_2026.mov`) con nombre en Roboto Black y cargo en Roboto Light,
  como en los parámetros de CapCut del medio.
- Video HDR del iPhone (HLG) convertido a SDR con tonemapping "hable".
- Cada respuesta de entrevista normalizada a −16 LUFS; la música baja sola bajo las voces.

## Música

Original, sintetizada nota a nota en `edit/music.py` (sin samples ni pistas de terceros: no puede recibir
reclamos de derechos).

- **Nota 1**: suspenso grave en re menor (drone, latido suave filtrado, cuerdas oscuras en trémolo, notas
  graves de piano y golpes graves en las cifras). Primera versión con un arpegio que entraba hacia el segundo
  25–30; se quitó porque le restaba seriedad, y la música quedó unos 4 dB más baja (master a −16 LUFS).
- **Nota 2**: fondo informativo sobrio (pads, pulso grave y piano espaciado, sin arpegios ni platillos),
  que baja solo debajo de las entrevistas (cada respuesta normalizada a −16 LUFS; master a −14 LUFS).

Si Proclama tiene su propia librería de música, se cambia en la mezcla sin volver a renderizar el video.

## Cómo volver a generarlas

```bash
# 1) material: Drive (públicos) y Facebook
bash tools/dl.sh datos/inventario_drive_nota2.tsv /home/user/notas/raw/n2
bash tools/dl.sh datos/recursos_proclama.tsv /home/user/notas/raw/pc
# 2) transcripción (faster-whisper medium)
python3 tools/transcribe.py medium salida/ audio/*.wav
# 3) video, música y mezcla
python3 edit/n1.py && python3 edit/music.py n1 out/n1_plan.json n1_music.wav
python3 edit/mix.py out/n1_plan.json n1_music.wav n1_mix.wav --music-lufs -21 --target -16
python3 edit/n2.py && python3 edit/music.py n2 out/n2_plan.json n2_music.wav
python3 edit/mix.py out/n2_plan.json n2_music.wav n2_mix.wav --music-lufs -21 --target -14
# 4) unir: ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k salida.mp4
```

`edit/stills.py n1 4 20 33` genera hojas de revisión con fotogramas de cualquier instante.

Dependencias: Python 3 con `numpy scipy pillow opencv-python-headless faster-whisper yt-dlp`, ffmpeg con
libx264 y zscale; fuentes Roboto y Poppins (Google Fonts, licencia OFL/Apache).
