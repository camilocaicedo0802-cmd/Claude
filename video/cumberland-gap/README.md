# Cumberland Gap · video para YouTube

Montaje del episodio *Cumberland Gap* (locución de 18:50) con el mismo motor que *Laurel Hill* e *I-80 Wyoming*:
Ken Burns sobre fotos y grabados, mapas animados con relieve real de los Apalaches, diagramas propios del paso
(los dos caminos uno encima del otro, el túnel piloto, las dos cuadrillas, la carretera que se borra), películas de
dominio público y música CC BY. Aquí solo se guardan el código y los datos ligeros; los medios se descargan con
los scripts de `tools/`.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor (`engine.py`, `gfx.py`, `gfx2.py`, `gfx3.py`), diagramas de este episodio (`gfx4.py`: la muesca en la muralla, el corte del paso, el corte transversal con la carretera, el túnel y el sendero, calendario, cronología, costes, escolta de carga peligrosa), mapas (`maps.py`, con cuatro mapas base del este de EE. UU. al paso), la edición plano a plano (`timeline.py`), el audio (`audio.py`), la codificación final (`splice.py`), las miniaturas (`thumbs.py`) y utilidades de revisión (`check.py`, `mids.py`, `sel.py`). |
| `tools/` | Transcripción, búsqueda y descarga en Flickr (solo licencias libres), Library of Congress, Internet Archive, Unsplash, detección de cortes, hojas de contacto y descarga de teselas de relieve. |
| `data/` | Transcripción con tiempos por palabra, guion, cortes de escena y el registro de cada imagen y película usada. |
| `entrega/` | Descripción para YouTube con capítulos y créditos, y los créditos completos con enlaces. |

## Audio

La música va unos 4 dB por debajo de la del episodio anterior (pista de música a −33 LUFS frente a −29,5) y los
efectos otros 4 dB más bajos, con la voz a −14 LUFS en la mezcla final.

## Licencias del material

Solo material apto para monetizar: dominio público (Library of Congress, Carol M. Highsmith, National Park Service,
National Archives, Prelinger), licencia Unsplash y CC BY 2.0 con atribución. Nada CC BY-SA, no comercial ni con
derechos reservados. Música de Kevin MacLeod (CC BY 4.0). Efectos de sonido sintetizados.

## Cómo regenerar el video

Estructura esperada (junto a este README): `assets/{img,vid,music,fonts,map}`, `work/` y `out/`.

```bash
mkdir -p work && cp data/words.json work/ && cp -r data/scenes work/
venv/bin/python edit/check.py
venv/bin/python edit/audio.py out/mix.wav
venv/bin/python edit/render.py out/video_noaudio.mp4 --workers 4 --total 1130.37
venv/bin/python edit/splice.py out/video_noaudio.mp4 out/mix.wav out/cumberland_gap.mp4
```
