# Slate · "Spray tan problems? We've got solutions!" (reel 3)

Reel vertical 1080×1920 a 30 fps, de unos 56 s, en formato "Problem vs. Solution", con el mismo estilo que el
reel de referencia: tarjetas de B-roll redondeadas con borde luminoso (problema arriba, solución abajo),
textos palabra por palabra en Poppins + Playfair Display Italic y efectos de sonido suaves.

Todo se monta por código: `edit/render.py` compone cada fotograma con Python (Pillow, NumPy, OpenCV) y lo
codifica con ffmpeg; `edit/audio.py` hace la mezcla. Aquí está solo el código y las listas de tomas: los
medios (crudo, B-roll, fotos de stock, fuentes) no se suben al repositorio.

## Versión 2 (cambios pedidos)

- **Nada encima de la cara:** la tarjeta del problema es más compacta (448×280, de y=75 a y=355) y se quitó el
  acercamiento de las respuestas, que subía la cabeza. En las tomas donde ella queda más alta, el A-roll baja
  lo justo (0–45 px, `HEAD_TOP` en `timeline.py`). Se comprobó en todos los fotogramas: con tarjeta visible,
  queda un margen mínimo de 21 px entre el halo de la tarjeta y lo más alto de su cabeza.
- **Música suave de fondo:** pista instrumental original generada con ElevenLabs Music (vía Higgsfield),
  pop suave con guitarra, piano eléctrico y glockenspiel, ~100 BPM. Va a unos −27 LUFS bajo la voz (≈12 dB por
  debajo), con ducking automático, y algo más presente en el gancho y el final.

## Estructura del video

| Bloque | Pregunta (voz fuera de cámara) | Respuesta (presentadora) | Tarjeta problema | Tarjeta solución |
| --- | --- | --- | --- | --- |
| Gancho | — | — | Aplicación de spray tan a pantalla completa + "SPRAY TAN Problems? WE'VE GOT Solutions!" | |
| P1 | Pale or dull skin | A custom spray tan | Foto "antes" del banco (Spray tan 3) | Aplicación (Spray Tan 1) |
| P2 | Need color ASAP? | We have a rapid formula just for that | Reloj (Unsplash) | Aplicación (Spray tan 3) |
| P3 | Dry or patchy skin | Exfoliate 24 hours before your appointment | Piel seca (Unsplash) | Cepillado en seco (Unsplash) |
| P4 | Tan fading unevenly | Moisturize daily | Línea de bronceado (Unsplash) | Crema en la pierna (Unsplash) |
| P5 | Tan sticking to hands and feet | We have barrier cream in the room for that before your appointment | Manos → pies (Unsplash) | Técnica con el frasco en la cabina (Spray tan 2, consulta) |
| P6 | Going on vacation | Book your spray tan 1–2 days before your trip | Maleta (Unsplash) | Agenda (Unsplash) |
| P7 | Wedding or special event | Book 1–2 days before, follow the prep instructions, custom shade | Novia (Unsplash) | Llegada al salón → cepillos → aplicación |
| P8 | Not sure which shade or solution is right for you? | Every client gets a personalized spray tan consultation | Mujer pensando (Unsplash) | Consulta (Spray tan 2) |
| Cierre | — | Every skin tone… / Your spray tan should be too / If you relate… / Come see us at Slate… | Tonos de piel (Unsplash) → resultados del banco → fachada y recepción de Slate (carpeta del salón) | |

En P7 la presentadora dijo una frase distinta al guion ("Make sure you book your appointment one to two days
before your wedding and follow the prep instructions that we send you and we'll do a custom shade for you");
en pantalla queda "Book 1–2 days before" y luego "Proper prep + custom shade".

## Archivos

- `edit/edl_src.py`: tramos del crudo (archivo, entrada, salida) y dónde empieza cada pregunta/respuesta.
- `edit/snap.py`: ajusta los cortes al habla real a partir de la energía del audio.
- `edit/engine.py`: primitivas (curvas, textos, tarjetas, píldoras PROBLEM/SOLUTION, estrellas, color, lectores).
- `edit/timeline.py`: la edición completa (tarjetas, textos anclados a palabras, efectos).
- `edit/render.py`: `video salida.mp4` o `stills carpeta t1 t2…` para revisar fotogramas.
- `edit/audio.py`: voz igualada por fase (la voz que pregunta venía 2–8 dB más fuerte), limpieza, −14 LUFS y efectos.
- `edit/sfx.py`: síntesis de los efectos (pop, swish, whoosh, chime, sparkle, ding): originales, sin derechos de terceros.
- `credits.tsv`: fotos de Unsplash usadas (licencia Unsplash).

## Cómo regenerar

Requiere Python 3 con `numpy scipy pillow opencv-python-headless faster-whisper` y ffmpeg con libx264.
Las rutas de medios se resuelven desde la carpeta de trabajo (`proj/` con `mezz/`, `work/`, `sfx/`, `fonts/`
y, al lado, `dl/` y `stock/`).

```bash
python3 edit/sfx.py sfx
python3 edit/snap.py .
python3 edit/audio.py work/mix.wav
python3 edit/render.py video work/video.mp4
ffmpeg -i work/video.mp4 -i work/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest final.mp4
```
