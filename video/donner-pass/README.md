# Donner Pass · video para YouTube

Montaje del episodio *Donner Pass: el túnel que nadie firmó* (locución de 18:50) con el mismo motor que *Laurel Hill*,
*I-80 Wyoming* y *Cumberland Gap*: Ken Burns sobre las estereografías del Central Pacific de la década de 1860, fotos
actuales del túnel 6, mapas animados con relieve real de la Sierra Nevada (y un mapa del Pacífico de Cantón a
California), diagramas propios (el túnel atacado por cuatro frentes, el barreno a mano, la nieve frente a una casa,
los cobertizos de nieve, la nómina de la compañía), películas de dominio público y música CC BY. Aquí solo se guardan
el código y los datos ligeros; los medios se descargan con los scripts de `tools/`.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor (`engine.py`, `gfx.py` a `gfx4.py`), diagramas de este episodio (`gfx5.py`: linterna en el túnel, nieve anual frente a una casa, la expedición Donner, el túnel 6 en planta, frentes, pozo y encuentro, el barreno a mano, avance por día, salarios, el pasillo de nieve, las 44 tormentas, el cobertizo, el libro de nómina y el «ni un solo trabajador chino» de 1869), mapas (`maps.py`, con cuatro mapas base), la edición plano a plano (`timeline.py`), el audio (`audio.py`), la codificación final (`splice.py`), las miniaturas (`thumbs.py`) y utilidades de revisión (`check.py`, `mids.py`, `sel.py`). |
| `tools/` | Transcripción, búsqueda y descarga en Flickr (solo licencias libres), Library of Congress (incluidas las estereografías, recortadas a una sola imagen), Internet Archive, Unsplash, detección de cortes, hojas de contacto y descarga de teselas de relieve. |
| `data/` | Transcripción con tiempos por palabra, guion, cortes de escena y el registro de cada imagen y película usada. |
| `entrega/` | Descripción para YouTube con capítulos y créditos, y los créditos completos con enlaces (caben en un comentario fijado). |

## Audio

La música va 1 dB por debajo de la de *Cumberland Gap* y los efectos se mantienen igual de bajos, con la voz a −14 LUFS
en la mezcla final.

## Licencias del material

Solo material apto para monetizar: dominio público o sin restricciones conocidas (Library of Congress, Carol M.
Highsmith, HAER, Donner Summit Historical Society, Marty Bernard, SMU Libraries, Prelinger), licencia Unsplash y
CC BY 2.0 con atribución. Nada CC BY-SA, no comercial ni con derechos reservados. Música de Kevin MacLeod (CC BY 4.0).
Efectos de sonido sintetizados.

## Cómo regenerar el video

Estructura esperada (junto a este README): `assets/{img,vid,music,fonts,map}`, `work/` y `out/`.

```bash
mkdir -p work && cp data/words.json work/ && cp -r data/scenes work/
venv/bin/python edit/check.py
venv/bin/python edit/audio.py out/mix.wav
venv/bin/python edit/render.py out/video_noaudio.mp4 --workers 4 --total 1130.06
venv/bin/python edit/splice.py out/video_noaudio.mp4 out/mix.wav out/donner_pass.mp4
```
