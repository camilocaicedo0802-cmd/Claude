# Road to Nowhere — la carretera a ninguna parte

Documental de 18:32 para YouTube, en español, sobre Lakeview Drive (la "Road to Nowhere") en Bryson City,
Carolina del Norte: el lago Fontana, la presa de 1942–1944, el acuerdo de 1943, la roca Anakeesta, el túnel
de 1970, los 28 cementerios de la orilla norte y el pago de 52 millones de dólares de 2010.

Todo el montaje está hecho por código: `edit/timeline.py` define los 242 planos anclados a las palabras de
la locución (`data/words.json`), y el motor (`edit/engine.py`, `gfx*.py`, `maps.py`, `render.py`) compone cada
fotograma a 1920×1080 y 30 fps. No hay medios en el repositorio: solo código y datos ligeros.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor, `timeline.py` del episodio, `gfx7.py` (diagramas de este episodio: el valle que se inunda, la presa frente a un edificio, el acuerdo de 1943, la roca Anakeesta, la carretera prometida milla a milla, el cheque y el fondo), `maps.py` con los mapas `rn_*`, `audio.py` (efectos de este episodio) y `score.py` (banda sonora original). |
| `tools/` | Herramientas de búsqueda y descarga (Unsplash, Library of Congress, Flickr, Wikimedia, Mixkit con `mk.py`), créditos y entrega. |
| `data/` | Transcripción (`words.json`, `retx.json`), guion, lista de material usado, mapa de música, créditos de lo usado (`credits_used.json`) y las capas del mapa local (`map/`). |
| `entrega/` | Descripción de YouTube y créditos completos para el comentario fijado. |

## Material y licencias

- Fotos: Flickr con CC BY 2.0, CC0, marca de dominio público o "sin restricciones conocidas" (créditos en
  `entrega/creditos_completos.txt`); Library of Congress (FSA/OWI, HABS/HAER, postales de 1948, Pearl Harbor);
  Unsplash (licencia Unsplash).
- Video: 17 clips de Mixkit, solo los marcados con la *Stock Video Free License* (`tools/mk.py` comprueba la
  licencia de cada clip y descarta los de licencia restringida).
- Música: banda sonora original sintetizada con `edit/score.py` (sin muestras de terceros).
- Mapas: relieve Mapzen/Tilezen; lago Fontana, ríos y arroyos del USGS National Hydrography Dataset; carreteras
  del USGS The National Map; límite del parque del National Park Service; Natural Earth. Los trazados de la
  antigua NC 288 y de la North Shore Road son aproximados.
- Los documentos en pantalla (acuerdo de 1943, aviso, carta de 1962, decisión de 2007, cheque de 2010) son
  recreaciones.

## Regenerar

```bash
bash tools/nuevo_proyecto.sh P voz.mp3 guion.pdf        # desde la skill; copia motor y herramientas
# material: tools/udl.py, tools/loc.py, tools/fl.py, tools/mk.py (ids en data/credits_used.json)
python3 tools/natural_earth.py assets/map rn -92,29,-74,41
python3 tools/fetch_tiles.py assets/map 7:-96,27,-70,43 10:-85.6,34.9,-82.2,36.4 13:-83.92,35.37,-83.38,35.59 14:-83.62,35.40,-83.42,35.50
# capas USGS/NPS del mapa local en assets/map/rn/ (ver data/map/)
python3 edit/score.py assets/score 72.6 112.5 142.8 143.9 114.6 137.7 159.0 127.2 113.4
python3 edit/audio.py out/mix.wav
python3 edit/render.py out/video_noaudio.mp4 --workers 4
bash tools/terminar.sh PID_RENDER Road_to_Nowhere 33374
```
