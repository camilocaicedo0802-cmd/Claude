# Kinzua Bridge — el puente que cayó igual

Documental de 18:33 para YouTube, en español, sobre el viaducto de Kinzua (McKean County, Pennsylvania): el puente
de hierro de 1882 que pidió Thomas L. Kane y diseñó Octave Chanute, levantado en 94 días; su sustitución por uno de
acero en 1900, que conservó los pedestales y los pernos de anclaje de 1882 (algunos alargados con manguitos); el
chatarrero que lo salvó en 1959, el parque estatal, la inspección de 2002 que avisó de cómo podía caer, la
reparación torre por torre de 2003 y el tornado F1 del 21 de julio de 2003 que tumbó 11 de las 20 torres; el informe
de diciembre de 2003 (pernos partidos, manguitos con grietas de fatiga bajo las arandelas) y el Kinzua Sky Walk.

El montaje está hecho por código: `edit/timeline.py` define los 233 planos anclados a las palabras de la locución
(`data/words.json`), y el motor (`edit/engine.py`, `gfx*.py`, `maps.py`, `render.py`) compone cada fotograma a
1920×1080 y 30 fps. No hay medios en el repositorio: solo código y datos ligeros.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor, `timeline.py` del episodio y `gfx10.py`, con los diagramas de este episodio: el viaducto en alzado sobre el perfil real del valle (`kz_profile.json`, del relieve Mapzen), con su construcción en 1882, el cambio de hierro a acero en 1900, la base de 1882 resaltada, la reparación torre por torre, la caída de 2003 (el centro primero, tres torres colgadas de los rieles) y el Sky Walk; la columna Phoenix y el barril; la silla en el viento; una torre de frente con viento, tirón y balanceo; el perno de anclaje en corte (1882, alargado, manguito, perno partido, manguito roto, arandela que tapa la grieta, los anclajes de 2011); el clip y la fatiga; el anemómetro de 94 mph; la escala F; los informes de 2002 y 2003 (recreaciones). `maps.py` añade los mapas `kz_*` y la capa `funnel` (tornado). `audio.py` tiene los efectos de este episodio y `score.py` la banda sonora original (`SCORE_SEED=43`). |
| `tools/` | Búsqueda y descarga (Unsplash, Library of Congress, Flickr, Wikimedia con `wmpick.py`, Mixkit con `mk.py` y `mklic.py`), créditos y entrega. |
| `data/` | Transcripción, guion, material usado, mapa de música y capas del mapa local (`map/`: arroyos del USGS NHD, carreteras de The National Map). |
| `entrega/` | Descripción de YouTube y créditos completos. |

## Material y licencias

- Fotos: Flickr con CC BY 2.0 (daveynin, Sean-Franc Strang, Nicholas_T, Andy Arthur, Random Retail, Steve
  Snodgrass, Sumner Caughey, Mike McBey) o marca de dominio público (David Schnell); Wikimedia Commons (HAER PA-7,
  dominio público); Library of Congress (sin restricciones conocidas; se descartó una foto de Chanute con derechos
  "no evaluados").
- Video: clips de Mixkit, todos con la *Stock Video Free License*; `tools/mklic.py` revisó la licencia de los 643
  resultados (269 libres, 374 restringidos).
- Música: banda sonora original sintetizada.
- Mapas: relieve Mapzen/Tilezen; Kinzua Creek y carreteras del USGS; Natural Earth. Trayectoria del tornado aproximada.

## Regenerar

```bash
python3 tools/fetch_tiles.py assets/map 4:-100,30,12,56 6:-126,24,-66,50 8:-81.5,39.6,-73.5,43.2 12:-79.0,41.55,-78.35,41.90 14:-78.612,41.748,-78.565,41.771
python3 tools/natural_earth.py assets/map kz -127,23,-65,51
# capas USGS del valle en assets/map/kz/ (ver data/map/)
SCORE_SEED=43 python3 edit/score.py assets/score 66.9 123.4 122.0 141.3 138.3 129.7 129.4 135.6 137.2
python3 edit/audio.py out/mix.wav
python3 edit/render.py out/video_noaudio.mp4 --workers 4
bash tools/terminar.sh PID_RENDER Kinzua_Bridge 33376
```
