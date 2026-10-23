# VSL Luis · "Puntualidad y compromiso" + testimonio

Video vertical tipo VSL (1080×1920, 30 fps, 53 s), sobrio y fiel al video de referencia, armado con el material
de la carpeta de Drive <https://drive.google.com/drive/folders/166Jczofb7o8ZOH8N44OnZ3g5wmsoUItL>.

**Resultado:** [`VSL_Luis_final.mp4`](VSL_Luis_final.mp4)

## Estructura

| Tramo | Qué se ve |
| --- | --- |
| 0:00 – 0:33 · Pitch | Crudo horizontal en una franja central con negro arriba y abajo, como la referencia. Cortes que alternan plano abierto y cerrado. Subtítulos blancos en minúscula (renglón pequeño + renglón grande para el énfasis) **al lado de la cara**, sin taparla. "Más info en mi perfil" fijo en el negro de abajo. |
| 0:17 – 0:21 | "que tenía las views estancadas, no crecía para nada": **Recurso 2 y 3** (373 y 542 vistas) como B-roll dentro de la franja, con zoom lento hacia las vistas. |
| 0:21 – 0:24 | "ya pegamos un video por más de 300 mil vistas": **Recurso 1** (321 mil) con zoom lento hacia el contador. |
| 0:33 – 0:52 · Testimonio | El testimonio del cliente resumido a 19 s, en vertical a pantalla completa (como el cierre de la referencia), subtítulos sobre el pecho: "solo tengo palabras de agradecimiento" · "lo que hiciste con mi cuenta… 19, 20 días publicando y una total locura" · "mira lo que este muchacho ha logrado con mi cuenta, sabe lo que hace" · "100 por ciento recomendado" · "se vienen niveles, let's go". |
| 0:52 – 0:53 | Fundido a negro y "Más info en mi perfil" al centro. |

Cortes del pitch: se quitó el silencio inicial (0,7 s) y una pausa de 1,3 s después de "que comenzó" (queda escondida bajo el B-roll).

## Audio

- Voz del pitch limpiada (paso alto, reducción de ruido suave, presencia, compresión); voz del testimonio (micrófono de solapa) solo nivelada. Las dos quedan igualadas y el total a −14 LUFS.
- Música épica: **"The Storm Chasers"**, [OpenGameArt](https://opengameart.org/content/storm-chasers), licencia **CC0** (dominio público: uso comercial sin atribución). Va unos 12 dB debajo de la voz, baja sola cuando alguien habla y cierra con el fundido final.
- Sin efectos de sonido, para mantener el tono serio.

## Cómo regenerarlo

```bash
pip install numpy pillow                    # + ffmpeg en el PATH
bash videos/vsl-luis/build.sh               # descarga de Drive, corta, renderiza y mezcla (~3-4 min)
RETRACK=1 bash videos/vsl-luis/build.sh     # además vuelve a transcribir y a detectar la cara
                                            # (pip install faster-whisper "opencv-python-headless<5")
```

| Archivo | Para qué |
| --- | --- |
| `render.py` | Compone cada cuadro: franja, encuadres, B-roll, subtítulos, testimonio y CTA. Textos en `MAIN_CHUNKS` y `TESTI_CHUNKS`, B-roll en `BROLL`, tramos del testimonio en `T_CUTS`. |
| `audio.py` | Mezcla las dos voces con la música. |
| `transcribe.py`, `faces.py` | Transcripción palabra por palabra (Whisper) y cajas de la cara; su salida está en `data/`. |
| `build.sh` | Todo el proceso de punta a punta. Si cambias `T_CUTS`, cambia también `CUTS=` en este archivo y los totales de cuadros en `render.py`/`audio.py`. |

Para cambiar un subtítulo, edita su línea en `MAIN_CHUNKS` o `TESTI_CHUNKS` (`/` separa renglones, `^` marca el renglón grande). Cada palabra debe corresponder a una palabra dicha en `data/words.json` o `data/testi_words.json`.
