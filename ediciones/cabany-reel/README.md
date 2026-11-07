# Reel Cabany · Tour de cabanypanama.com

Video vertical (1080×1920, 30 fps, 44 s) editado a partir del video en crudo, con el estilo del lado derecho del reel de referencia.

- `cabany_reel.mp4`: video final (H.264 + AAC 48 kHz, −14 LUFS para Instagram/TikTok).
- `portada.jpg`: cuadro de muestra.
- `proyecto/work/`: el código que genera el video cuadro por cuadro.

## Qué tiene

| Tiempo | Escena | Efectos |
| --- | --- | --- |
| 0:00–0:02 | Gancho: "En todo grupo de amigos o familia" | Zoom de corte, etiqueta de marca que entra desde la izquierda |
| 0:02–0:05 | Teléfono 3D con un chat de grupo ("¿Y quién reserva la cabaña?") | Transición de empuje, burbujas con pop |
| 0:05–0:07 | Vuelta a cámara | Transición con desenfoque de zoom, chips "Reservar" y "Buscar dónde quedarse" |
| 0:07–0:10 | Recorte de la toma de pie sobre fondo verde de marca | Etiqueta "Horas y horas de búsqueda" que gira en 3D y se tacha |
| 0:10–0:12 | Pared de cabañas reales del sitio | Alejamiento hasta formar la cuadrícula, riser hacia el cambio de ritmo |
| 0:12–0:38 | Tour 3D de la página | El teléfono entra volando y gira en perspectiva, con acercamientos y resaltados sobre cada paso (ver abajo) |
| 0:38–0:42 | Selfie final | Flash blanco, zooms de corte |
| 0:42–0:44 | Cierre de marca | Barrido circular lima → verde, logo, lema y URL |

Pasos del tour: resultado de Google, inicio con categorías (Cabañas, Casas, Premium, Piscinas, Buen Wifi, Naturaleza), filtros, tarjetas de cabañas que salen del teléfono, Luxury Canyon Suites (resaltado, toque y tarjeta que sale en 3D), "tu favorita" con corazón, fotos en abanico, amenidades con check, fechas (10 → 13 dic), 2 huéspedes, total $85.60 USD con contador, botón Reservar y "¡Reserva lista!" con confeti.

- Colores: verde #023B28 (theme-color del sitio), lima #A9E93A, lima del logo #86CB2C y crema #F8F5F2. Tipografía Montserrat (la del sitio) y logos oficiales de `cabanypanama.com/brand/`.
- Subtítulos palabra por palabra, con la frase clave en grande y en lima, igual que la referencia.
- Marcas de agua sutiles: logo pequeño y `cabanypanama.com` arriba a la derecha, al 55–62 % de opacidad. El logo cambia entre la versión blanca y la verde según el fondo para que siempre se lea sin estorbar.
- Audio:
  - Voz original nivelada para que se oiga pareja.
  - Música original de unos 114 BPM, sintetizada aquí, sin muestras de terceros. Tiene intro, un riser con redoble y el cambio de ritmo justo cuando entra el tour. Al final pasa a una parte suave y cierra con un acorde.
  - Efectos sintetizados del mismo tipo que la referencia: whooshes en cada transición, pops y dings en los chips, clics en los toques, obturador en las fotos, riser, impactos y destellos.

## Regenerar

Los scripts esperan esta estructura en una carpeta de trabajo (`ROOT`), con `work/` adentro:

```
ROOT/
  raw.mov                  video en crudo
  frames/0000.jpg…         ffmpeg -i raw.mov -q:v 2 -start_number 0 frames/%04d.jpg
  masks/0226.png…0381.png  python segrun.py 226 382   (rembg, modelo isnet-general-use)
  site/img/*.webp          fotos del sitio (site2.js con Playwright + descarga)
  brand/logo-white.png, brand/logo-green.png
  fonts/Montserrat-{500..900}.ttf
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

Todo el montaje (tiempos, cámaras del teléfono, chips, subtítulos) está en `reel.py`. Cada escena es una función `scN(t)` y las transiciones están en `frame(t)`.
