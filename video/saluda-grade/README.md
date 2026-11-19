# Saluda Grade — la vía que mandaba cada tren contra la tierra

Documental de 18:32 para YouTube, en español, sobre la pendiente de Saluda (Carolina del Norte): el escarpe de la Blue
Ridge entre Asheville y Spartanburg, el trazado del capitán Charles Pearson por el cañón del Pacolet (casi un 5 %), los
presos que la construyeron en 1877–1878, los frenos a mano y los trenes partidos en trozos, el accidente de Lewis
Tunstall la noche del 17 de junio de 1890, las vías de escape con el cambio siempre hacia la tierra, el pueblo de
veraneo y el Carolina Special, el cierre de 2001, la vía tapada con tierra en 2003, el huracán Helene (2024) y el
sendero Inman–Zirconia.

El montaje está hecho por código: `edit/timeline.py` define los 286 planos anclados a las palabras de la locución
(`data/words.json`), y el motor (`edit/engine.py`, `gfx*.py`, `maps.py`, `render.py`) compone cada fotograma a
1920×1080 y 30 fps. No hay medios en el repositorio: solo código y datos ligeros.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor, `timeline.py` del episodio y `gfx15.py`, con los diagramas de este episodio: la pendiente de Saluda frente al 1 % y al 2 %, el perfil real Asheville–Spartanburg con el escarpe (`sg_profile.json`, relieve Mapzen), la rampa a un segundo piso, las dos opciones (rodeos o el cañón), el guardafrenos sobre los techos, el tren subido en trozos, el tren desbocado con el velocímetro sobre el perfil real Saluda–Melrose, la vía de escape con el guardagujas (cambio cerrado, silbato, vía libre, contra la tierra y la vía tapada en 2003), el sistema de tiempo de Melrose, la lápida (recreación), el huracán y la regla al revés. `maps.py` añade los mapas `sg_*`; `sg_route.json` tiene la línea Asheville–Spartanburg (red ferroviaria FRA/USGS), el tramo Saluda–Melrose y el río Pacolet (NHD). `audio.py` tiene los efectos de este episodio y `score.py` la banda sonora original (`SCORE_SEED=103`). |
| `tools/` | Búsqueda y descarga (Unsplash, Library of Congress, Flickr, Mixkit con `mk.py` y `mklic.py`), comprobación de derechos (`locrights.py`), créditos y entrega; `usgs.py`, `sg_routes.py`, `sg_profile.py` y `terminar_sg.sh`. |
| `data/` | Transcripción, guion, material usado, mapa de música, foto de Freepik y capas del mapa (`map/`: vías, carreteras y ríos del USGS; coordenadas redondeadas a 5 decimales). |
| `entrega/` | Descripción de YouTube y créditos completos. |

## Material y licencias

- Fotos históricas: Library of Congress (cuadrillas de presos, accidentes ferroviarios de la National Photo Company,
  Asheville en 1894, Hendersonville, FSA/OWI, Carol M. Highsmith). Se descartaron las que tenían derechos «no
  evaluados», sin indicar o restringidos (Paul Rudolph, David Seymour).
- Flickr: marca de dominio público o «No known copyright restrictions» (State Archives of North Carolina, UNC
  Libraries, Cornell University Library, Marty Bernard) y CC BY 2.0 / 4.0 con atribución.
- Freepik vía Magnific: una foto con licencia gratuita y atribución (aleksandarlittlewolf).
- Video: clips de Mixkit, todos con la *Stock Video Free License*.
- Música: banda sonora original sintetizada.

## Disco

`render.py out/video_noaudio.txt` deja los trozos en `out/chunks` y escribe solo su lista (`RENDER_CRF=19`);
`splice.py` con `RM_CHUNKS=1` borra cada trozo en cuanto se han codificado todas sus piezas, y `tools/terminar_sg.sh`
codifica el archivo optimizado a partir de las 4 partes, sin otra copia del máster.

## Regenerar

```bash
python3 tools/fetch_tiles.py assets/map 8:-85.5,33.5,-79.0,37.0 11:-83.2,34.75,-81.6,35.75 14:-82.42,35.17,-82.26,35.25
python3 tools/natural_earth.py assets/map sg -127,23,-65,51
# capas USGS en assets/map/sg/ (ver data/map/ y tools/usgs.py); luego tools/sg_routes.py y tools/sg_profile.py
SCORE_SEED=103 python3 edit/score.py assets/score 65.3 136.0 105.2 114.1 164.3 148.7 116.2 131.2 142.5
python3 edit/audio.py out/mix.wav
RENDER_CRF=19 python3 edit/render.py out/video_noaudio.txt --workers 4
PY=python3 bash tools/terminar_sg.sh PID_RENDER Saluda_Grade 33373
```
