# Reel Cabany · Tour de cabanypanama.com

Video vertical (1080×1920, 30 fps, 44 s) editado a partir del video en crudo.

- **Recorrido de la página:** sigue el estilo del lado derecho del primer reel de referencia.
- **Tomas donde ella habla y toda la tipografía (versión 2):** siguen el segundo reel de referencia ("how's going editors").

- `cabany_reel.mp4`: video final (H.264 + AAC 48 kHz, −14 LUFS para Instagram/TikTok).
- `portada.jpg`: cuadro de muestra.
- `proyecto/work/`: el código que genera el video cuadro por cuadro.

## Qué tiene

| Tiempo | Escena | Efectos |
| --- | --- | --- |
| 0:00–0:02 | Gancho: "En todo grupo de amigos o familia" | Título apilado sobre la cabeza ("grupo" en itálica pesada con degradado lima), aro de luz que pasa detrás de ella, palabra "FAMILIA" en mayúsculas |
| 0:02–0:05 | Teléfono 3D con un chat de grupo ("¿Y quién reserva la cabaña?") | Destello desenfocado, burbujas con pop |
| 0:05–0:07 | Vuelta a cámara | Destello desenfocado, íconos 3D en rombo (calendario, lupa, casa, cama) y subtítulos de una palabra |
| 0:07–0:12 | Toma de pie, con dos encuadres en corte | Títulos apilados "y hoy te voy a / ahorrar / horas y horas" y "para que esa / tarea / sea mucho", ícono de reloj de arena, "BÚSQUEDA" |
| 0:12–0:13 | Pared de cabañas reales del sitio | Alejamiento hasta la cuadrícula con "sencilla" en lima, riser hacia el cambio de ritmo |
| 0:13–0:38 | Tour 3D de la página | El teléfono entra volando y gira en perspectiva, con acercamientos y resaltados sobre cada paso (ver abajo) |
| 0:38–0:42 | Selfie final | Flash blanco, título "En cuestión de / minutos", aro de luz, "RESERVA / LISTA" con ícono de check y cierre "sin / complicaciones" |
| 0:42–0:44 | Cierre de marca | Barrido circular lima → verde, logo, lema y URL |

Pasos del tour: resultado de Google, inicio con categorías (Cabañas, Casas, Premium, Piscinas, Buen Wifi, Naturaleza), filtros, tarjetas de cabañas que salen del teléfono, Luxury Canyon Suites (resaltado, toque y tarjeta que sale en 3D), "tu favorita" con corazón, fotos en abanico, amenidades con check, fechas (10 → 13 dic), 2 huéspedes, total $85.60 USD con contador, botón Reservar y "¡Reserva lista!" con confeti.

- **Colores:** verde #023B28 (theme-color del sitio), lima #A9E93A, lima del logo #86CB2C y crema #F8F5F2. Los logos son los oficiales de `cabanypanama.com/brand/`.
- **Tipografía:** Inter Tight, la grotesca apretada más parecida a la de la segunda referencia. Va en negrita, itálica pesada con degradado y mayúsculas. Se usa en títulos, subtítulos, chips y cierre. Montserrat queda solo en las tarjetas que imitan el sitio.
- **Efectos de texto:** las palabras entran con parpadeo, y las de color aparecen primero como fantasma. Los títulos apilados van sobre la cabeza y los subtítulos de una palabra a la altura del pecho. Al salir, los títulos se desenfocan.
- **Subtítulos solo en las tomas de ella:** en las partes del celular (chat y recorrido de la página) no hay subtítulos, para que la pantalla se vea limpia. Ahí solo quedan los chips y los resaltados.
- Marcas de agua sutiles: logo pequeño y `cabanypanama.com` arriba a la derecha, al 55–62 % de opacidad. El logo cambia entre la versión blanca y la verde según el fondo para que siempre se lea sin estorbar.
- Audio:
  - Voz original nivelada para que se oiga pareja.
  - Música original de unos 114 BPM, sintetizada aquí, sin muestras de terceros. Tiene intro, un riser con redoble y el cambio de ritmo justo cuando entra el tour. Al final pasa a una parte suave y cierra con un acorde.
  - Efectos sintetizados del mismo tipo que las referencias. En las tomas de ella hay un "ting" cuando entra cada título, un destello sonoro en las palabras de color, un barrido brillante con el aro de luz, pops suaves en los íconos y whooshes en los destellos. En el recorrido hay whooshes, pops y dings en los chips, clics en los toques, obturador en las fotos, riser e impactos.

## Regenerar

Los scripts esperan esta estructura en una carpeta de trabajo (`ROOT`), con `work/` adentro:

```
ROOT/
  raw.mov                  video en crudo
  frames/0000.jpg…         ffmpeg -i raw.mov -q:v 2 -start_number 0 frames/%04d.jpg
  masks/0226.png…0381.png  python segrun.py 226 382   (rembg, modelo isnet-general-use)
  site/img/*.webp          fotos del sitio (site2.js con Playwright + descarga)
  brand/logo-white.png, brand/logo-green.png
  fonts/Montserrat-{500..900}.ttf, fonts/InterTight-{600..900}[Italic].ttf
  masks/0026–0061, 1176–1211  python segrun2.py (recortes para el aro de luz)
  work/                    estos scripts + raw_words.json (transcripción con tiempos)
```

```bash
pip install numpy opencv-python-headless pillow scipy rembg[cpu]
```

```bash
./work/render_all.sh ../out_frames
```

```bash
ffmpeg -v error -y -i raw.mov -vn -ac 1 -ar 44100 work/voice.wav
```

```bash
cd work && python audio.py --fresh
```

```bash
ffmpeg -framerate 30 -i out_frames/%05d.jpg -i work/mix.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 48000 -c:a aac -b:a 256k -movflags +faststart cabany_reel.mp4
```

Todo el montaje (tiempos, cámaras del teléfono, chips y subtítulos del recorrido) está en `reel.py`. Cada escena es una función `scN(t)` y las transiciones están en `frame(t)`. Los títulos de las tomas de ella están en `STACKS` y `CHUNKS`. El sistema tipográfico (Inter Tight, degradados, parpadeo, íconos en rombo y aro de luz) está en `typo.py`.
