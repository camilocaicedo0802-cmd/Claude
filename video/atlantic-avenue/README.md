# Atlantic Avenue · video para YouTube

Montaje del episodio *Atlantic Avenue: el túnel que Nueva York perdió* (locución de 19:05) con el mismo motor que los
episodios anteriores: fotos del interior del túnel y de las visitas de Bob Diamond, grabados y fotos de la Library of
Congress, mapas de Brooklyn calle por calle con los datos abiertos de la ciudad, la ruta a Boston por Long Island y
diagramas propios. Aquí solo se guardan el código y los datos ligeros; los medios se descargan con los scripts de
`tools/`.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor (`engine.py`, `gfx.py` a `gfx5.py`), diagramas de este episodio (`gfx6.py`: la calle de 1840 con el tren y el jinete de la bandera roja, la caja sobre la locomotora, la frenada, la zanja y la bóveda en sección, el túnel a lo largo de la avenida —abierto, tapiado, con una sola puerta, el escaneo detrás de la pared de Hicks Street y hoy—, la bajada por la alcantarilla, el plano con el círculo, el tablero de rumores, el permiso, 1844 frente a 1863 y la radio), mapas (`maps.py`, con mapas base de calles de Nueva York), la edición plano a plano (`timeline.py`), la banda sonora original (`score.py`), el audio (`audio.py`), la codificación final (`splice.py`), las miniaturas (`thumbs.py`) y utilidades de revisión (`check.py`, `mids.py`, `sel.py`). |
| `tools/` | Transcripción, búsqueda y descarga en Flickr (solo licencias libres), Library of Congress, Wikimedia Commons, Unsplash, hojas de contacto y descarga de teselas de relieve. |
| `data/` | Transcripción con tiempos por palabra, guion, plan de música y el registro de cada imagen usada. |
| `entrega/` | Descripción para YouTube con capítulos y créditos, y los créditos completos con enlaces. |

## Música y derechos

Para evitar reclamos de Content ID, este episodio no usa música de terceros ni películas de archivo: la banda sonora
es original, sintetizada nota a nota por `score.py` (nueve piezas, una por capítulo). `audio.py` lee el plan de
`data/music.json`, así que se puede cambiar por pistas de la Biblioteca de audio de YouTube sin tocar la imagen.
Las fotos son de dominio público (Library of Congress), CC BY 2.0 con atribución (Flickr) o con licencia Unsplash.

## Cómo regenerar el video

Estructura esperada (junto a este README): `assets/{img,music,fonts,map,score}`, `work/` y `out/`.

```bash
mkdir -p work && cp data/words.json data/music.json work/
venv/bin/python edit/check.py
venv/bin/python edit/score.py assets/score 67.6 142.0 197.9 100.5 138.6 140.1 204.7 75.1 89.7
venv/bin/python edit/audio.py out/mix.wav
venv/bin/python edit/render.py out/video_noaudio.mp4 --workers 4 --total 1145.23
venv/bin/python edit/splice.py out/video_noaudio.mp4 out/mix.wav out/atlantic_avenue.mp4
```
