# Kiowa Creek — la locomotora perdida

Documental de 17:42 para YouTube, en español, sobre la locomotora 51 del Kansas Pacific, que cayó a Kiowa Creek
(Bennett, Colorado) en la crecida del 21 de mayo de 1878: el ferrocarril que llegó a Denver (1869–1870), el arroyo
casi siempre seco, la noche del accidente, la primera búsqueda de 1878, la leyenda (1914–1982), la gran búsqueda
de 1989 con NUMA y los registros que encontró Lloyd Glasier: la máquina se desenterró de noche, se reconstruyó en
Kansas City en 1880 y siguió trabajando con el número 1026.

El montaje está hecho por código: `edit/timeline.py` define los 270 planos anclados a las palabras de la locución
(`data/words.json`), y el motor (`edit/engine.py`, `gfx*.py`, `maps.py`, `render.py`) compone cada fotograma a
1920×1080 y 30 fps. No hay medios en el repositorio: solo código y datos ligeros.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor, `timeline.py` del episodio y `gfx9.py`, con los diagramas de este episodio: el cruce del arroyo en corte (terraplén y puente de madera, crecida, hueco, caída del tren, rescate, pozo de 40 pies, arena que se baraja, magnetómetro), la crecida vista desde arriba, la manguera, los granos de arena que se licúan, la cabina de noche, la locomotora por partes, el periódico de 1914, el registro de locomotoras, la lectura del magnetómetro, el satélite, la reconstrucción (51 → 1026), las dos líneas de tiempo, la fusión de 1880 y la teoría del seguro. También `maps.py` con los mapas `kc_*` (Kiowa Creek trazado desde el NHD, nubes y sol), `audio.py` con los efectos de este episodio, `score.py` (banda sonora original, `SCORE_SEED=31`) y `thumbs_kc.py`. |
| `tools/` | Búsqueda y descarga (Unsplash, Library of Congress, Flickr, Wikimedia con `wmget.py`, Mixkit con `mk.py` y `mklic.py`, que comprueba la licencia de cada clip sin descargarlo), créditos y entrega. |
| `data/` | Transcripción, guion, material usado, mapa de música y capas del mapa local (`map/`: arroyos del USGS NHD, carreteras y vía de The National Map). |
| `entrega/` | Descripción de YouTube y créditos completos. |

## Material y licencias

- Fotos: Flickr con CC BY 2.0 (Boston Public Library, fotos de Alexander Gardner de 1867; James St. John; Lyn
  Lomasi; Grand Canyon NPS; Andrew Magill; born1945) o marca de dominio público; Wikimedia Commons (Kiowa Creek,
  Jeffrey Beall, CC BY 4.0); Library of Congress (estereografías de 1867 y Denver hacia 1875, sin restricciones
  conocidas: se descartó una foto con derechos "no evaluados" y las que no se pudieron verificar).
- Video: 33 clips de Mixkit, todos con la *Stock Video Free License*. La mayoría de los clips elegidos al principio
  tenían licencia restringida y se descartaron; `tools/mklic.py` revisó el catálogo para quedarse solo con los libres.
- Música: banda sonora original sintetizada.
- Mapas: relieve Mapzen/Tilezen; arroyos, vía y carreteras del USGS; Natural Earth. Trazados aproximados.
- El periódico de 1914, el registro de locomotoras, la vista desde la cabina y los diagramas son recreaciones.

## Regenerar

```bash
python3 tools/fetch_tiles.py assets/map 6:-126,24,-66,50 8:-105.6,36.6,-93.9,41.4 11:-105.3,38.8,-103.9,40.4 14:-104.62,39.68,-104.28,39.84
python3 tools/natural_earth.py assets/map kc -127,23,-65,51
# capas USGS del mapa local en assets/map/kc/ (ver data/map/)
SCORE_SEED=31 python3 edit/score.py assets/score 64.7 141.8 124.6 142.8 113.9 121.5 126.9 119.9 118.1
python3 edit/audio.py out/mix.wav
python3 edit/render.py out/video_noaudio.mp4 --workers 4
bash tools/terminar.sh PID_RENDER Kiowa_Creek 31848 211.9 216.2
```
