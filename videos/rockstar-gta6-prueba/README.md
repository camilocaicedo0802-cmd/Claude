# Prueba de video: "Rockstar / GTA 6" (estilo documental)

Prueba de 3:46 con los primeros minutos de la narración *NARRACIÓN DE ROCKSTAR GAME (ACTUALIZADO)*. Imita el estilo del video de referencia ("El Hombre que Hizo Desaparecer 1 Billón de Dólares en 36 Minutos"):

- **Cortes rápidos**: unos 110 planos en 3:46, entre 1,5 y 2,5 s cada uno.
- **Tipografía cinética**: Poppins Bold Italic en blanco con resplandor y palabras clave en rojo. Cada palabra entra justo cuando la dice la voz, sincronizada con la transcripción de Whisper.
- **Rótulos**: fecha en caja roja ("18 SEPT. 2022", "17 SEPT. 2013"…), ubicaciones en versalitas y nombres en letra script roja ("Arion Kurtaj", "Rockstar Games").
- **Look**: viñeta fuerte, aberración cromática en los bordes, desenfoque de lente en las esquinas, grano y parpadeo leve.
- **Transiciones**: whip pan, zoom, glitch, flash y fundido. Cada una lleva su efecto de sonido.
- **Gráficos animados propios**:
  - alerta de seguridad
  - logo de Rockstar con glitch
  - "LAPSUS$"
  - chat interno
  - cuadrícula de 90 videos filtrados con contador
  - contador de años 2014→2026
  - contador de $1.000.000.000
  - gráfica de $744 millones
  - expediente "Project Americas" con sello CLASIFICADO
  - mapa de América que se reduce a Florida (Leonida)
  - gráfica "ESTANCADO"
  - retrato holográfico
- **Audio**:
  - voz procesada (filtro pasa-altos, compresor y presencia)
  - música de Kevin MacLeod que baja automáticamente cuando habla la voz
  - unos 80 efectos de sonido
  - normalización a −14 LUFS, el nivel que usa YouTube

Las fuentes y licencias están en [`CREDITOS.md`](CREDITOS.md), con el texto listo para pegar en la descripción de YouTube.

## Cómo se genera

El video se arma con código (Python + ffmpeg + OpenCV), sin editor visual. Todo el montaje vive en `engine/edl.py`: cada plano, texto y efecto de sonido está escrito con el segundo exacto de la narración.

| Archivo | Qué hace |
| --- | --- |
| `engine/transcribe.py` | Transcribe la voz con faster-whisper y guarda los tiempos de cada palabra |
| `engine/coverr_search.py`, `coverr_dl.py` | Busca y descarga clips gratuitos de Coverr (descarta los Premium y los hechos con IA) |
| `engine/commons_get.py`, `svg2png.js` | Descarga imágenes y logos de Wikimedia Commons y convierte los SVG a PNG |
| `engine/mixkit_sfx.py` | Lista los efectos de sonido de Mixkit por categoría |
| `engine/core.py` | Lectura de video, Ken Burns, etalonaje, texto con resplandor, look global, transiciones, alineado con la transcripción |
| `engine/overlays.py` | Texto cinético, rótulo de fecha, etiquetas, logos, sellos, contadores |
| `engine/gfx.py` | Gráficos animados generados por código |
| `engine/edl.py` | El guion de montaje |
| `engine/render.py` | Renderiza en paralelo (4 procesos) a H.264 1080p30 |
| `engine/mix.py` | Mezcla voz, música con ducking y efectos, y normaliza el volumen |

```bash
export VIDEO_WORKDIR=/ruta/a/workdir
```

```bash
export VO_FILE=/ruta/a/narracion.mp3
```

```bash
python3 engine/render.py frames 21.4 74.6 125.8
```

```bash
python3 engine/render.py video $VIDEO_WORKDIR/work/video.mp4
```

```bash
python3 engine/mix.py $VIDEO_WORKDIR/work/mix.wav
```

```bash
ffmpeg -i $VIDEO_WORKDIR/work/video.mp4 -i $VIDEO_WORKDIR/work/mix.wav -c:v copy -c:a aac -b:a 320k -shortest final.mp4
```

Los recursos descargados (unos 1,2 GB) y el video final no se guardan en git porque pesan demasiado.
