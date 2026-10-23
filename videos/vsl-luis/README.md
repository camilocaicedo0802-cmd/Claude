# VSL Luis · "Puntualidad y compromiso" + testimonio

Video vertical tipo VSL (1080×1920, 30 fps, 45 s), sobrio y fiel al video de referencia, armado con el material
de la carpeta de Drive <https://drive.google.com/drive/folders/166Jczofb7o8ZOH8N44OnZ3g5wmsoUItL>.

**Resultado:** [`VSL_Luis_final.mp4`](VSL_Luis_final.mp4)

## Estructura

| Tramo | Qué se ve |
| --- | --- |
| 0:00 – 0:30 · Pitch | Crudo horizontal en una franja central con negro arriba y abajo, como la referencia. Cortes que alternan plano abierto y cerrado. Subtítulos blancos en Coolvetica (renglón pequeño + renglón grande de énfasis) **al lado de la cara**, sin taparla y a 180 px del borde izquierdo, para que no se corten en celulares altos. |
| 0:15 – 0:19 | "que tenía las views estancadas, no crecía para nada": **Recurso 2 y 3** separados, completos, sin esquinas redondeadas y con un acercamiento leve (3 %). |
| 0:19 – 0:22 | "ya pegamos un video por más de 300 mil vistas": **Recurso 1** completo (321 mil), mismo tratamiento. |
| 0:30 – 0:45 · Testimonio | Testimonio del cliente resumido a 15 s, recortado **1:1** (sin la zona desenfocada de la esquina) en el mismo marco negro, con los subtítulos debajo: "solo tengo palabras de agradecimiento, lo que hiciste con mi cuenta y llevamos 20 días publicando y una total locura. Mira lo que este muchacho ha logrado con mi cuenta, sabe lo que hace y sin duda alguna **100% recomendado**". Cierra en "100% recomendado" y funde a negro. |

Cortes sin titubeos ni muletillas: en el pitch se quitaron el silencio inicial, una pausa después de "un momento", el arranque en falso "que comenzó…" y "hermano"; en el testimonio, "¿qué? 19,", "o sea", las pausas de duda y el final ("pero creo que…", "let's go"). Los cortes se verificaron volviendo a transcribir el audio editado.

## Audio

- Voz del pitch limpiada (paso alto, reducción de ruido suave, presencia, compresión); voz del testimonio (micrófono de solapa) solo nivelada. Las dos quedan igualadas y el total a −14 LUFS.
- Música: **"Música Épica Sin Copyright"** de la carpeta de pistas (Drive `1knl3Lxp6aeBAySatN1SK5jPGHL7Uy2Ar` › emocional), desde el segundo 15,85: su pausa cae bajo "a otro nivel" y su golpe fuerte entra justo con el testimonio. Va 12–14 dB debajo de la voz y baja sola cuando alguien habla.

## Cómo regenerarlo

```bash
pip install numpy pillow                                        # + ffmpeg en el PATH
FONT=/ruta/Coolvetica_Rg.otf bash videos/vsl-luis/build.sh      # descarga de Drive, corta, renderiza y mezcla (~3 min)
RETRACK=1 bash videos/vsl-luis/build.sh                         # además vuelve a transcribir y a detectar la cara
                                                                # (pip install faster-whisper "opencv-python-headless<5")
```

La fuente Coolvetica no está en el repo (su licencia no permite redistribuir el archivo): pásala con `FONT=` o déjala en `work/assets/fonts/Coolvetica-Rg.otf`.

| Archivo | Para qué |
| --- | --- |
| `render.py` | Compone cada cuadro: franja, encuadres, B-roll, subtítulos y testimonio 1:1. Tramos en `CUTS_F` y `T_CUTS_F`, textos en `MAIN_CHUNKS` y `TESTI_CHUNKS`, encuadres en `FRAMING`. |
| `audio.py` | Mezcla las dos voces con la música (toma las duraciones de `render.py`). |
| `transcribe.py`, `faces.py` | Transcripción palabra por palabra (Whisper) y cajas de la cara; su salida está en `data/`. |
| `build.sh` | Todo el proceso de punta a punta. Si cambias un tramo, cámbialo también en la llamada a `cut` de este archivo. |

Para cambiar un subtítulo, edita su línea en `MAIN_CHUNKS` o `TESTI_CHUNKS` (`/` separa renglones, `^` marca el renglón grande, `{n}` hace que una palabra en pantalla reemplace n palabras dichas, como `100%{3}` por "100 por ciento"). Cada palabra debe corresponder a una palabra dicha que quede dentro de los cortes.
