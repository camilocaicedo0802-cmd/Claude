# Prueba de edición · Audi A3 · Mecatrónica DSG

Video vertical 9:16 (1080×1920, 30 fps, 53,6 s) editado a partir del material compartido en Drive: el "Lienzo" (`LienzoAudi`) y 16 clips de apoyo (`IMG_6302`–`IMG_6318`).
El estilo sigue la referencia `Referencia_video_automotriz.mp4` (ver [`ANALISIS_REFERENCIA.md`](ANALISIS_REFERENCIA.md)), pero con la paleta **rojo, negro y blanco** y la tipografía **Poppins**.

## Estructura del video

| Tiempo | Bloque | Qué pasa |
|---|---|---|
| 0,0–3,2 s | **Hook** | "¿La transmisión de tu Audi está fallando?": tipeo letra por letra y "FALLANDO?" en rojo biselado con glitch. "Ven, acompáñame" con punch-in. |
| 3,2–12,8 s | Contexto | "ESTE / AUDI A3" con estela y la pastilla DSG; etiqueta de ubicación Hidalgo / Tizayuca sobre el auto; escena oscura con tarjetas "TRANSMISIÓN DSG / MECATRÓNICA". |
| 12,8–30,4 s | Diagnóstico | Collage con los códigos **P17BF** y **P189C** (X roja); impacto "BAJA PRESIÓN DE ACEITE"; tarjetas 3D "HIDRÁULICA / TARJETA ELECTRÓNICA"; punch-in en "daño". |
| 30,4–46,1 s | Proceso | PASO 01 Desmontaje · PASO 02 Clonar (barra de progreso interactiva vieja → nueva, "MISMOS VALORES") · PASO 03 Aceite · PASO 04 Instalación · PASO 05 Ajustes. |
| 46,1–51,0 s | **CTA** | "Si tienes un Audi con problemas en la transmisión… MÁNDANOS UN MENSAJE". |
| 51,0–53,6 s | **Cierre** | El Audi en cámara lenta, la etiqueta "AUDI A3 · DSG REPARADA", el botón "ESCRÍBENOS" y la línea Diagnóstico · Mecatrónica · Programación. |

### Decisiones de guion
- El Lienzo dura 77 s y el máximo es 60 s. Se quitaron las pausas y dos tramos:
  - "Huasca de Ocampo fue catalogado como el primer pueblo mágico…": es un dato ajeno a la reparación.
  - "Por aquí te voy a dejar la presión inadecuada / correcta…": promete mostrar valores de presión que no vienen en el material. Si el taller los comparte, este tramo (Lienzo 63,8–70,1 s) se puede volver a meter con una gráfica de antes/después.
- La transcripción se hizo con Whisper y se corrigió a mano ("tu Audi", "Audi" en el CTA).

## Audio
- **Voz**: cortada en 7 tramos sobre los silencios, con fundidos de 8 ms y realce de presencia.
- **Música**: beat phonk/trap **original, sintetizado en el script** (`scripts/audio_mix.py`), así que no tiene copyright. Va a 140 BPM en La menor, con cencerro, 808, clap y hats. Entra en el primer corte, como en la referencia, se corta antes de "BAJA PRESIÓN" y se filtra en el CTA. Se atenúa ~14 dB bajo la voz (ducking).
- **SFX** sintetizados de los mismos tipos y en los mismos momentos que la referencia: whoosh en cada transición, pops en títulos, clics de tipeo, impactos y booms en las palabras de golpe, glitch, error en los códigos, datos y ding en la clonación, riser y stamp en el cierre.
- Master a −14 LUFS y pico de −1,5 dBTP.

## Cómo regenerarlo
1. Descargar el material del Drive en `media/raw/` (no se versiona).
2. `scripts/proxy.sh`: convierte el HDR (HLG, HEVC 10 bits) del iPhone a SDR Rec.709 con tone-mapping *hable*.
3. `scripts/transcribe.py`: transcripción con tiempos por palabra (faster-whisper, modelo medium).
4. `scripts/build_edl.py`: genera `remotion/src/edl.json` con los cortes, las escenas, los títulos, los subtítulos y los SFX.
5. `cd remotion && npm install && npm run render`: render del video sin audio. Las fuentes de Poppins salen de `@fontsource/poppins`; se copian a `public/fonts/` y los proxies van en `public/`.
6. `scripts/audio_mix.py` + ffmpeg (`loudnorm`): mezcla y masterizado. Al final se unen video y audio.
