# Reel Cabany 2 · "Te muestro cómo buscar tu próxima cabaña"

Video vertical (1080×1920, 30 fps, 33 s) editado desde `Video_crudo_Cabany.MOV`. Sigue el estilo de `Video_de_referencia_Cabany.mp4`, con los colores de la marca: textos blancos y resaltes en verde.

- `cabany_reel_2.mp4`: video final (H.264 + AAC 48 kHz, −14 LUFS).
- `portada.jpg`: cuadro de muestra.
- `proyecto/work/`: el código que genera el video cuadro por cuadro.

## Limpieza del video en crudo

El crudo traía texto quemado que se eliminó así:

| Qué | Dónde | Cómo se quitó |
| --- | --- | --- |
| Letras cortadas de subtítulos ("TU", "S", "M", "T", "P", "C", "L", "A"), amarillas o blancas con borde negro | Borde derecho, en casi todo el video | En las tomas de ella, la cámara está fija: se reemplazan solo los píxeles de esas letras por un "fondo limpio" (mediana de los cuadros sin texto). Ella nunca se toca, gracias a su recorte. En las grabaciones de pantalla, las letras se rellenan con inpainting. |
| "WWWcabanypanama.com" escrito encima de la página | Inicio de la web, 8.3–10.9 s | Se cubre con el fondo blanco de la página. En su lugar aparece una píldora de vidrio donde se escribe "cabanypanama.com". |
| "www.cabanypanama.com." con línea guía | Sobre la cabeza, en la última toma (26.4–29.3 s) | Se reemplaza por el fondo limpio de esa toma. |
| Destellos naranjas entre tomas y el centro de control de iOS | 2.5 s, 7.6 s y 22.4–23.7 s | Quedan tapados por destellos blancos y zooms propios, o se saltan esos cuadros. |

## Tipografía y efectos (de la referencia)

- **Tipografía:** Urbanist (Google Fonts, licencia OFL). Es una geométrica con "a" y "g" de un solo piso, la más parecida a la de la referencia (tipo Sofia Pro / Gilroy).
  - **Black 900:** palabras gigantes.
  - **Light 300 y Light Italic:** palabras delgadas.
  - **ExtraBold 800:** palabras blancas pesadas.
  - **SemiBold:** píldoras.
- **Palabra gigante:** degradado verde luminoso (#F1FFC4 → #B5F05A → #5FC23C) con textura holográfica tipo mármol (bandas menta y amarillo), brillo superior, resplandor verde y sombra suave. Va detrás de la cabeza de ella, recortada con su silueta.
  - **Entrada:** sube con desenfoque de movimiento, o entra de lado como un latigazo.
  - **Mientras está en pantalla:** crece despacio.
  - **Salida:** se desenfoca. Las palabras de una serie ("mira" / "esto") se reemplazan en el mismo lugar.
- **Palabra delgada blanca** encima de la gigante ("te muestro cómo", "si estás pensando en").
- **Palabra blanca pesada** abajo a la derecha, delante de ella ("a Chiriquí", "tu próximo viaje", "este tutorial").
- **Palabras sueltas a la altura del pecho**, en blanco regular o itálica delgada.
- **Píldoras de vidrio esmerilado** con borde claro ("Alojamientos publicados", "Súper sencillo", "cabanypanama.com").
- **Íconos de línea doble blanca** que se dibujan solos y salen con un glitch: cabaña, montaña, lupa, guardar y compartir.
- **Notificación tipo iOS:** "Viaje a Chiriquí".
- **Cierre:** tarjeta de marca de vidrio sobre la última toma desenfocada.

## Edición

- **Tomas de ella:** acercamiento lento continuo y un golpe de zoom en cada frase.
- **"Paso 1":** pantalla de título con el fondo desenfocado.
- **Recorrido de la página (sin subtítulos):**
  - el teléfono 3D entra volando y gira en perspectiva;
  - acercamientos y resaltados en lima sobre la búsqueda, la habitación luxury Canyon y el botón Reservar;
  - tarjetas de cabañas y fotos que salen del teléfono;
  - chips de Capacidad, Precios, Disponibles, Te gusta, Fechas, Detalles y Disponibilidad;
  - toque en "Reservar" y "¡Reserva lista!".
- **Toma del celular en la mano:** zoom y abanico de fotos.
- **Transiciones:** destellos, desenfoque de zoom y latigazos.
- **Marca de agua:** logo pequeño y URL arriba a la derecha, como en el reel anterior.

## Audio

- **Voz:** la del crudo, nivelada.
- **Música:** original y sintetizada, a 130 BPM. Tiene intro, un redoble con riser y el cambio de ritmo justo en "paso 1". En la toma final baja a una parte suave y cierra con un acorde.
- **Efectos:** sintetizados, del mismo tipo que la referencia:
  - swoosh en cada palabra gigante;
  - destello con "ding" agudo cuando se dibujan los íconos;
  - riser antes del cambio de ritmo y del cierre, con impactos;
  - notificación de dos tonos;
  - clics de teclado mientras se escribe la URL;
  - pops en chips y píldoras;
  - obturador en las fotos, clic en el toque y campanita de "reserva lista".

## Regenerar

Misma estructura que `../cabany-reel/`. Este proyecto usa la carpeta `ROOT` con:

```
frames/0000.jpg…   ffmpeg -i Video_crudo_Cabany.MOV -q:v 2 -start_number 0 frames/%04d.jpg
masks/             segrun_p2.py ROOT 0 232 y ROOT 766 934 (rembg isnet-general-use)
fonts/Urbanist-*.ttf, fonts/Montserrat-*.ttf, fonts/InterTight-*.ttf
site/img/*.webp, brand/logo-*.png
work/              estos scripts + words.json
```

```bash
./work/render2.sh ../out_frames
```

```bash
cd work && python audio2.py --fresh
```

```bash
ffmpeg -framerate 30 -i out_frames/%05d.jpg -i work/mix.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 48000 -c:a aac -b:a 256k -movflags +faststart cabany_reel_2.mp4
```
