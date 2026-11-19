# Columbia River Highway — nueve días en un túnel

Documental de 17:57 para YouTube, en español, sobre la vieja carretera de la garganta del río Columbia (Oregón): el sueño
de Sam Hill y del ingeniero Samuel Lancaster, la Axenstrasse junto al lago de Lucerna, la carretera colgada del
acantilado, el túnel de las cinco ventanas de Mitchell Point (1915), los túneles gemelos de Mosier y los dos hombres que
pasaron nueve días dentro durante la nevada de noviembre de 1921, el tráfico de la US 30, el entierro de los túneles
(1948–1966), la Interstate 84, el plan de 1987, la reapertura de los gemelos (2000), Oneonta tras el incendio de 2017 y
el nuevo túnel de Mitchell Point (2025).

El montaje está hecho por código: `edit/timeline.py` define los 308 planos anclados a las palabras de la locución
(`data/words.json`), y el motor (`edit/engine.py`, `gfx*.py`, `maps.py`, `render.py`) compone cada fotograma a
1920×1080 y 30 fps. No hay medios en el repositorio: solo código y datos ligeros.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor, `timeline.py` del episodio y `gfx16.py`, con los diagramas de este episodio: la garganta en corte (ferrocarril abajo, carretera colgada, la autopista de la orilla y el acantilado recortado en 1966), el túnel con ventanas visto desde el río (1915 y 2025), la regla de Lancaster, los hombres con banderas, el auto de 1915 frente al camión de 1930, los túneles rellenos, excavados y reforzados, la inscripción (recreación), los nueve días, el viento del este, los precios de Mosier, el tejado contra las rocas y la línea del tiempo. `maps.py` añade los mapas `cr_*` (Estados Unidos, región, garganta, tramo oeste, tramo este y Suiza); `cr_route.json` tiene la carretera Troutdale–The Dalles trazada sobre las carreteras del USGS, separada en tramos que siguen siendo carretera y tramos bajo la I-84, y la propia I-84. `audio.py` tiene los efectos de este episodio y `score.py` la banda sonora original (`SCORE_SEED=109`). |
| `tools/` | Búsqueda y descarga (Unsplash, Library of Congress, Flickr, Wikimedia, Mixkit con `mk.py`, `mklic.py` y `mklic_ids.py`), comprobación de derechos (`locrights.py`), hojas de contacto, créditos y entrega; `usgs.py`, `cr_routes.py`, `terminar_cr.sh` y `rehacer_opt.sh`. |
| `data/` | Transcripción, guion, material usado, mapa de música, notas del material y capas del mapa (`map/`: carreteras, vías y ríos del USGS; coordenadas redondeadas a 5 decimales). |
| `entrega/` | Descripción de YouTube y créditos completos. |

## Material y licencias

- Fotos históricas: Library of Congress (HAER, Bain News Service, National Photo Company, FSA/OWI, Photochrom, Carol M.
  Highsmith). Se descartaron las que tenían derechos «no evaluados», sin indicar o restringidos (entre ellas las
  postales Detroit Publishing de Mitchell Point y de la garganta).
- Flickr: Oregon Department of Transportation y otros autores con CC BY 2.0; U.S. Forest Service (Pacific Northwest)
  y otros con marca de dominio público o «No known copyright restrictions».
- Video: clips de Mixkit, todos con la *Stock Video Free License*.
- Música: banda sonora original sintetizada.
- Wikimedia Commons respondió con 429 durante toda la sesión, así que no se usó ninguna imagen de allí.

## Disco

`render.py out/video_noaudio.txt` deja los trozos en `out/chunks` y escribe solo su lista (`RENDER_CRF=19`);
`splice.py` con `RM_CHUNKS=1` borra cada trozo en cuanto se han codificado todas sus piezas, y `tools/terminar_cr.sh`
corta las 4 partes, guarda el audio del máster, borra el máster y codifica el archivo optimizado a partir de las partes.

## Regenerar

```bash
python3 tools/fetch_tiles.py assets/map 10:-123.2,45.1,-120.4,46.1 11:-122.45,45.45,-121.05,45.80 13:-122.34,45.49,-122.00,45.63 13:-121.68,45.63,-121.26,45.74 9:5.8,45.7,10.6,47.9
# capas USGS en assets/map/cr/ (ver data/map/ y tools/usgs.py); luego tools/cr_routes.py
SCORE_SEED=109 python3 edit/score.py assets/score 61.7 118.7 170.2 177.8 106.8 113.8 118.2 108.5 112.4
python3 edit/audio.py out/mix.wav
RENDER_CRF=19 python3 edit/render.py out/video_noaudio.txt --workers 4
PY=python3 bash tools/terminar_cr.sh PID_RENDER Columbia_River_Highway 32305
```
