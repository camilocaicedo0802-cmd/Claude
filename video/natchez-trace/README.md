# Natchez Trace — el camino sin prisa

Documental de 19:54 para YouTube, en español, sobre el Natchez Trace y la Natchez Trace Parkway: la senda de
bisontes y pueblos nativos entre el Mississippi y las salinas de Nashville; los Kaintucks que bajaban en balsa por el
Ohio y el Mississippi y volvían a pie; el camino del Gobierno (1801–1810), las posadas ("stands"), los salteadores y
el tráfico de esclavos; Andrew Jackson, "Old Hickory", volviendo a pie en 1813; el vapor *New Orleans* (1811–1812)
y el abandono; el camino hundido en el loess; la idea de Jeff Busby, el parque nacional de 1938 y sus reglas (sin
camiones, carteles ni gasolineras, 50 mph); los 67 años de obra hasta 2005, el puente de doble arco de 1994 y los
cortes de 2026.

El montaje está hecho por código: `edit/timeline.py` define los 245 planos anclados a las palabras de la locución
(`data/words.json`), y el motor (`edit/engine.py`, `gfx*.py`, `maps.py`, `render.py`) compone cada fotograma a
1920×1080 y 30 fps. No hay medios en el repositorio: solo código y datos ligeros.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor, `timeline.py` del episodio y `gfx11.py`, con los diagramas de este episodio: la balsa río abajo y la vuelta a pie contra la corriente, la cinta de correr al revés, el corte del camino hundido a lo largo del tiempo, el menú de una posada, las barras de tiempos (10 días frente a 9 horas), el indicador de combustible, las reglas del parque, el parque visto desde arriba con su franja de bosque, la construcción a trozos (1939–2005), el puente de doble arco montado desde arriba, la arcilla que se hincha y se encoge y las dos líneas de tiempo (67 años de obra, 21 completa). `maps.py` añade los mapas `nt_*` y el trazado real de la Parkway (`nt_route.json`, línea central sacada del límite del parque del NPS, con los mileposts reescalados a 444 millas). `audio.py` tiene los efectos de este episodio y `score.py` la banda sonora original (`SCORE_SEED=57`). |
| `tools/` | Búsqueda y descarga (Unsplash, Library of Congress, Flickr, Wikimedia con `wmpick.py`, Mixkit con `mk.py` y `mklic.py`), créditos y entrega. |
| `data/` | Transcripción, guion, material usado, mapa de música y el límite del parque (`map/natr.geojson`, NPS Land Resources Division). |
| `entrega/` | Descripción de YouTube y créditos completos. |

## Material y licencias

- Fotos: Flickr con CC BY 2.0 (James Case, Natalie Maynor, Pratap Sankar, Shawn Rossi, The_Gut, Ron Cogswell, Stuart
  Seeger, Brent Moore), CC0 (Gary Todd) o marca de dominio público (amanderson2); Library of Congress (Carol M.
  Highsmith, retratos, grabados y litografías sin restricciones conocidas; se descartaron las que tenían derechos
  "no evaluados"); Wikimedia Commons (NPS, Highsmith, levantamiento de James Wilkinson, Billmeguire CC0).
- Video: clips de Mixkit, todos con la *Stock Video Free License*.
- Música: banda sonora original sintetizada.
- Mapas: relieve Mapzen/Tilezen; límite del parque del NPS; Natural Earth. Rutas históricas aproximadas.

## Nota sobre 2026

La locución dice que el tramo de 24 millas del centro de Mississippi sigue cerrado hasta mediados de 2027. Según el
NPS, ese tramo (MP 135–159.5) reabrió el 30 de octubre de 2026 y desde el 2 de noviembre está cerrado otro más corto
(MP 159.5–165) hasta mediados de 2027. En pantalla solo se pone "24 MILLAS EN OBRAS", sin fecha.

## Regenerar

```bash
python3 tools/fetch_tiles.py assets/map 4:-100,30,12,56 6:-126,24,-66,50 8:-92.6,30.6,-85.4,37.0 11:-91.5,31.45,-90.9,32.0
python3 tools/natural_earth.py assets/map nt -127,23,-65,51
# límite del parque del NPS en assets/map/nt/natr.geojson (ver data/map/)
SCORE_SEED=57 python3 edit/score.py assets/score 74.4 141.5 138.5 140.3 137.4 140.1 144.9 133.0 156.4
python3 edit/audio.py out/mix.wav
python3 edit/render.py out/video_noaudio.mp4 --workers 4
bash tools/terminar.sh PID_RENDER Natchez_Trace 35817
```
