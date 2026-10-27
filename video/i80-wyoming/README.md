# I-80 Wyoming · video para YouTube

Montaje del episodio *I-80 Wyoming* (locución de 18:46) hecho por código con el mismo motor que *Laurel Hill*:
Ken Burns sobre fotos, mapas animados con relieve real de Wyoming, diagramas propios de la nieve que viaja con
el viento, películas de dominio público y música CC BY. Aquí solo se guardan el código y los datos ligeros; los
medios (≈3 GB) se descargan con los scripts de `tools/`.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor (`engine.py`, `gfx.py`, `gfx2.py`), diagramas de este episodio (`gfx3.py`: nieve, vallas, flujo de viento alrededor de Elk Mountain, cuenta atrás, fila de camiones), mapas (`maps.py`, con la I-80 y la US 30 de Natural Earth), la edición plano a plano (`timeline.py`), el audio (`audio.py`), la codificación final por trozos (`splice.py`), las miniaturas (`thumbs.py`) y utilidades de revisión. |
| `tools/` | Transcripción (`transcribe.py`), búsqueda y descarga de Flickr con licencias libres (`fl.py`), Library of Congress (`loc.py`), películas de Internet Archive (`ia.py`), detección de cortes (`scenes.sh`) y hojas de contacto. |
| `data/` | Transcripción con tiempos por palabra, cortes de escena, y el registro de autor y licencia de cada imagen y película usada. |
| `entrega/` | Descripción para YouTube con capítulos y créditos, y los créditos completos con enlaces. |

## Licencias del material

Solo material apto para monetizar: dominio público (Carol M. Highsmith/Library of Congress, FHWA, Prelinger,
Universal Newsreel, USFWS, USGS, Smithsonian), CC0, licencia Unsplash y CC BY 2.0/4.0 con atribución. Nada CC BY-SA,
no comercial ni con derechos reservados. Música de Kevin MacLeod (CC BY 4.0). Efectos de sonido sintetizados.

## Cómo regenerar el video

Estructura esperada (junto a este README): `assets/{img,vid,music,fonts,map}`, `work/` y `out/`.

```bash
mkdir -p work && cp data/words.json work/ && cp -r data/scenes work/
venv/bin/python edit/check.py                          # valida anclas, archivos y duración de planos
venv/bin/python edit/audio.py out/mix.wav              # voz + música con ducking + viento, radio, barreras
venv/bin/python edit/render.py out/video_noaudio.mp4 --workers 4 --total 1126.37
venv/bin/python edit/splice.py out/video_noaudio.mp4 out/mix.wav out/i80_wyoming.mp4   # [T0 T1 ...] re-renderiza tramos
```

El render a 1080p30 tarda unos 60 min con 4 núcleos y la codificación final unos 30 min más.
