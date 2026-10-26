# Laurel Hill · video para YouTube

Montaje del episodio *Laurel Hill* (locución de 18:13) hecho por código: Ken Burns sobre fotos de archivo,
mapas animados con relieve real, grafismos propios, películas de dominio público y música CC BY.
Este directorio guarda **solo el código y los datos ligeros**; los medios (≈1 GB) se descargan con los scripts.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor de render (`engine.py`, `gfx.py`, `gfx2.py`, `maps.py`), la edición plano a plano (`timeline.py`), el audio (`audio.py`) y utilidades de revisión (`check.py`, `stills.py`, `mids.py`). |
| `tools/` | Búsqueda y descarga de material libre (Wikimedia Commons, Library of Congress, Flickr, Internet Archive), transcripción con faster-whisper y descarga del relieve. |
| `data/` | Transcripción con tiempos por palabra, cortes de escena de las películas, registro y licencias de cada imagen, coordenadas. |
| `entrega/` | Descripción para YouTube con capítulos y créditos, créditos completos y lista de clips opcionales de Pixabay para una v2. |

## Licencias del material

Solo se usó material apto para monetizar: dominio público, CC0, licencia Unsplash y CC BY (con atribución en
`entrega/descripcion_youtube.txt`). Se descartó todo lo CC BY-SA, no comercial o con derechos reservados.
La música es de Kevin MacLeod (CC BY 4.0). Los efectos de sonido se sintetizan en `audio.py`.

## Cómo regenerar el video

Estructura esperada (junto a este README): `assets/{img,vid,music,fonts,map}`, `work/` y `out/`.

```bash
python -m venv venv && venv/bin/pip install faster-whisper opencv-python-headless pillow numpy scipy
mkdir -p work && cp data/words.json data/retx.json work/ && cp -r data/scenes work/
# medios: ver tools/ (fetch_alt.py, commons_queue.py, fetch_tiles.py) y data/unsplash_final.txt
venv/bin/python edit/check.py                      # valida la línea de tiempo
venv/bin/python edit/audio.py out/mix.wav          # voz + música con ducking + efectos
venv/bin/python edit/render.py out/video_noaudio.mp4 --workers 4
venv/bin/python edit/splice.py out/video_noaudio.mp4 out/mix.wav out/laurel_hill.mp4   # [T0 T1 ...] re-renderiza tramos
```

El render a 1080p30 tarda unos 60 min con 4 núcleos; `splice.py` codifica la entrega (x264 CRF 20, ≤10 Mbps,
audio a −14 LUFS) en trozos de 90 s que se pueden reanudar, y tarda unos 30 min más.
