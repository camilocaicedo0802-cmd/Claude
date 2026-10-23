# VSL Luis · "Puntualidad y compromiso"

Video vertical tipo VSL (1080×1920, 30 fps, 34 s) armado a partir del crudo horizontal de la carpeta de Drive
<https://drive.google.com/drive/folders/166Jczofb7o8ZOH8N44OnZ3g5wmsoUItL>, siguiendo el estilo del video de referencia.

**Resultado:** [`VSL_Luis_final.mp4`](VSL_Luis_final.mp4)

## Qué tiene el video

| Momento | Qué pasa en pantalla |
| --- | --- |
| Todo el video | Crudo horizontal en una franja central con negro arriba y abajo, como la referencia. Pastilla amarilla fija **"Más info en mi perfil"** en el negro de abajo, con latido y brillo. |
| Subtítulos | Palabra por palabra, apilados **a la izquierda de la cara** (nunca la tapan; la posición sale de un detector de rostro). Palabras clave en Anton grande: amarillo, rojo (negativo) o verde (crecimiento), algunas en caja amarilla. |
| "puntualidad / compromiso" | Stickers ⏰ 🤝 y zoom de golpe. |
| "un editor de video que no tiene nada de eso" | Ventana de "Exportando video… 99 %" atascada en el negro de arriba + etiqueta "ENTREGA ATRASADA". |
| "que tenía las views estancadas, no crecía para nada" | **Recurso 2 y 3** (373 y 542 vistas) entran como tarjetas, círculo rojo en las vistas, título "¿CUENTA ESTANCADA?" y se ponen grises. |
| "ya pegamos un video por más de 300 mil vistas" | Riser + golpe + flash: **Recurso 1** con brillo verde, contador 0 → 321.000 "VISTAS EN UN SOLO VIDEO", confeti y círculo verde en "321 mil". |
| "crecimiento / impacto / 15 días / crece / a otro nivel" | Zooms y sacudidas, stickers 📈 💥 🚀 🔥 y un calendario "15 DÍAS". |
| Cierre (1,6 s) | El video se oscurece y el CTA "Más info en mi perfil" pasa al centro. |

Cortes: se quitó el silencio inicial (0,7 s) y una pausa de 1,3 s después de "que comenzó" (el corte queda escondido bajo las tarjetas).

## Audio

- Voz limpiada (paso alto, reducción de ruido suave, presencia, compresión) y normalizada a −14 LUFS.
- Música épica: **"The Storm Chasers"**, [OpenGameArt](https://opengameart.org/content/storm-chasers), licencia **CC0** (dominio público: uso comercial sin atribución). Va unos 12 dB debajo de la voz y baja sola cuando él habla.
- Efectos (whoosh, pop, riser, golpes, buzz, ticks del contador) sintetizados en `audio.py`, sin muestras de terceros.

## Cómo regenerarlo

```bash
pip install numpy pillow                    # + ffmpeg en el PATH
bash videos/vsl-luis/build.sh               # descarga de Drive, corta, renderiza y mezcla
RETRACK=1 bash videos/vsl-luis/build.sh     # además vuelve a transcribir y a detectar la cara
                                            # (pip install faster-whisper "opencv-python-headless<5")
```

| Archivo | Para qué |
| --- | --- |
| `render.py` | Compone cada cuadro: franja, zooms, subtítulos, stickers, tarjetas, contador y CTA. Los textos y tiempos están en `CHUNKS`, `build_timeline()` y `draw_cards()`. |
| `audio.py` | Sintetiza los efectos y mezcla voz + música + efectos. |
| `transcribe.py`, `faces.py` | Transcripción palabra por palabra (Whisper) y cajas de la cara; su salida está en `data/`. |
| `build.sh` | Todo el proceso de punta a punta. |

Para cambiar un subtítulo, edita su línea en `CHUNKS` (`/` separa renglones; al final `*` amarillo, `#` caja amarilla, `!` rojo, `+` verde). Cada palabra debe corresponder a una palabra dicha en `data/words.json`.
