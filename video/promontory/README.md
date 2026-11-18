# Promontory Summit — la vía que desmontaron con una fiesta

Documental de 18:16 para YouTube, en español, sobre Promontory Summit (Utah): la ley del ferrocarril del Pacífico de
1862, la carrera entre el Central Pacific y el Union Pacific (los trabajadores chinos en la Sierra Nevada, los terraplenes
paralelos, las diez millas en un día), el clavo de oro del 10 de mayo de 1869 y el telegrama «hecho», la vida en la
línea (Terrace, Kelton y las diligencias a Boise), el atajo de Lucin sobre el Gran Lago Salado (1902–1904) que dejó
vacía la vía vieja, la Segunda Guerra Mundial y la chatarra, la ceremonia del 8 de septiembre de 1942 en la que el
gobernador arrancó el último clavo, adónde fue el acero, el lago partido en dos y lo que queda hoy.

El montaje está hecho por código: `edit/timeline.py` define los 317 planos anclados a las palabras de la locución
(`data/words.json`), y el motor (`edit/engine.py`, `gfx*.py`, `maps.py`, `render.py`) compone cada fotograma a
1920×1080 y 30 fps. No hay medios en el repositorio: solo código y datos ligeros.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor, `timeline.py` del episodio y `gfx14.py`, con los diagramas de este episodio: el clavo de oro sobre el durmiente pulido (y el cambio por uno de hierro), la barra que levanta el clavo en 1942, el pago por milla, un pie al día en granito, los dos terraplenes paralelos, las diez millas en un día, «DONE» en morse, el perfil real de las dos líneas (por la loma de Promontory y por el lago, `pm_profile.json`, relieve Mapzen), el caballete y el relleno que se hundía, el tráfico de 1908, la chatarra, la vía que se levanta, la vida de Mary Ipsen y el lago partido en dos. `maps.py` añade los mapas `pm_*` (Estados Unidos, el Oeste, el norte de Utah con el Gran Lago Salado del NHD y la loma); `pm_route.json` tiene la línea vieja (caminos del USGS sobre la explanación), el atajo de Lucin (red ferroviaria del USGS), las rutas aproximadas de 1869 y el camino de diligencias a Boise. `audio.py` tiene los efectos de este episodio y `score.py` la banda sonora original (`SCORE_SEED=97`). |
| `tools/` | Búsqueda y descarga (Unsplash, Library of Congress, Flickr, NASA con `nasa.py`, Mixkit con `mk.py` y `mklic.py`), comprobación de derechos (`locrights.py`), créditos y entrega; `usgs.py`, `pm_routes.py` (trazados), `pm_profile.py` (perfil) y `terminar_lista.sh`. |
| `data/` | Transcripción, guion, material usado, mapa de música y capas del mapa (`map/`: carreteras y vías de The National Map, ríos y lagos del NHD; coordenadas redondeadas a 5 decimales). |
| `entrega/` | Descripción de YouTube y créditos completos. |

## Material y licencias

- Fotos históricas: Library of Congress (estereografías de Alfred A. Hart y A. J. Russell, la ceremonia de 1869, el
  caballete del atajo de Lucin (HAER), Pearl Harbor, FSA/OWI 1942, Carol M. Highsmith). Se descartaron las que tenían
  derechos «no evaluados» o sin indicar (una postal del atajo, la cuadrilla de 1869, el tren de Stanford y tres carteles
  de 1942).
- Flickr: marca de dominio público, «No known copyright restrictions» o US Government Work (BLM Utah, SMU Libraries,
  OSU, Donner Summit Historical Society, Architect of the Capitol) y CC BY 2.0 con atribución.
- NASA: el Gran Lago Salado desde la Estación Espacial (dominio público).
- Video: clips de Mixkit, todos con la *Stock Video Free License* (`mklic.py` revisó 600 resultados: 313 libres).
- Música: banda sonora original sintetizada.

## Disco

Para no tener dos copias del render, `render.py out/video_noaudio.txt` deja los trozos en `out/chunks` y escribe solo
su lista; `splice.py` lee esa lista directamente y `tools/terminar_lista.sh` borra los trozos después de las partes.

## Regenerar

```bash
python3 tools/fetch_tiles.py assets/map 7:-124.0,36.5,-109.5,47.5 10:-114.3,40.5,-111.6,42.1 13:-112.80,41.50,-112.30,41.72
python3 tools/natural_earth.py assets/map pm -127,23,-65,51
# capas USGS en assets/map/pm/ (ver data/map/ y tools/usgs.py); luego tools/pm_routes.py y tools/pm_profile.py
SCORE_SEED=97 python3 edit/score.py assets/score 63.6 129.8 125.4 130.4 143.3 112.4 143.9 127.9 131.9
python3 edit/audio.py out/mix.wav
python3 edit/render.py out/video_noaudio.txt --workers 4
PY=python3 bash tools/terminar_lista.sh PID_RENDER Promontory 32878
```
