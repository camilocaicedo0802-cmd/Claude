# Rollins Pass — la montaña siempre cobró

Documental de 19:31 para YouTube, en español, sobre Rollins Pass (Colorado): el camino de peaje de John Rollins (1873),
David Moffat y su Denver, Northwestern and Pacific, la vía "provisional" por encima de la Divisoria Continental
(1903–1904) con el bucle de Riflesight Notch, la pendiente del 4 % y la estación de Corona a casi 11.700 pies; los
inviernos de la "Colina" (cobertizos, quitanieves rotativas, trenes atrapados, aludes de 1917 y 1922); la ruina de
Moffat (1911) y la quiebra (1913); el túnel Moffat pagado por el estado (1922–1928), el túnel de prueba que hoy lleva
agua del río Fraser a Denver (1936), el atajo de Dotsero (1934), el California Zephyr, el contrato de 2025 y el camino
de tierra de hoy con el túnel Needle's Eye cerrado.

El montaje está hecho por código: `edit/timeline.py` define los 279 planos anclados a las palabras de la locución
(`data/words.json`), y el motor (`edit/engine.py`, `gfx*.py`, `maps.py`, `render.py`) compone cada fotograma a
1920×1080 y 30 fps. No hay medios en el repositorio: solo código y datos ligeros.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor, `timeline.py` del episodio y `gfx12.py`, con los diagramas de este episodio: el corte de la montaña sobre el relieve real a lo largo del túnel (`rp_profile.json`, Mapzen) con la vía por encima y el túnel por debajo (2.400 pies más abajo); la pendiente del 2 % frente al 4 % con locomotoras de refuerzo; el bucle de Riflesight Notch; el cobertizo de nieve (techo, nieve que se cuela, vigas aplastadas, incendio de 1918); la quitanieves rotativa; el tren atrapado (días, -20 °C, carbón); los veranos y los inviernos del dinero; el túnel de prueba (8 pies, 21 pies al día, 10,5 pies con agua); el agua del Fraser cruzando la Divisoria hasta Denver y la señal de 20 mph. `maps.py` añade los mapas `rp_*`; `rp_grade.json` es la antigua vía sobre el paso (sacada de los caminos "Moffat Road" del USGS) y `rp_routes.json` las rutas ferroviarias (red del USGS). `audio.py` tiene los efectos de este episodio y `score.py` la banda sonora original (`SCORE_SEED=71`). |
| `tools/` | Búsqueda y descarga (Unsplash, Library of Congress, Flickr, Wikimedia, Mixkit con `mk.py` y `mklic.py`), créditos y entrega; `usgs.py` (consultas ArcGIS paginadas a GeoJSON), `grade.py`, `rails.py`, `profile.py` y `pancrop.py` (recortes de la panorámica de Corona de 1909). |
| `data/` | Transcripción, guion, material usado, mapa de música y capas del mapa (`map/`: vías, carreteras y senderos de The National Map, arroyos y lagos del NHD, red ferroviaria 1:1M; coordenadas redondeadas a 5 decimales). |
| `entrega/` | Descripción de YouTube y créditos completos. |

## Material y licencias

- Fotos: Flickr con CC BY 2.0 (Sheila McClune, Bradley Gordon, jda, Loco Steve, Roy Luck, Rick, Robert Rynerson, vxla,
  James St. John, Toronto History, NOAA Photo Library), CC BY 4.0 (Jeff Ruane) o marca de dominio público (Donner
  Summit Historical Society); Library of Congress (panorámica de Corona de 1909, vistas de la "Moffat Road", Denver,
  Calvin Coolidge, HABS; se descartaron las que tenían derechos "no evaluados").
- Wikimedia Commons limitó las descargas (HTTP 429) durante toda la sesión: no se usó nada de allí. Moffat aparece con
  una tarjeta tipográfica en lugar de retrato.
- Video: clips de Mixkit, todos con la *Stock Video Free License* (`mklic.py` revisó 1.397 resultados: 661 libres).
- Música: banda sonora original sintetizada.
- Mapas: relieve Mapzen/Tilezen; USGS (The National Map, NHD, GNIS); Natural Earth.

## Nota sobre la locución

En el capítulo de hoy la voz dice "los condados del lado oeste, Boulder y Gilpin"; el guion dice "lado este", que es
lo correcto. En pantalla, Boulder y Gilpin aparecen en el lado este, "en contra".

## Regenerar

```bash
python3 tools/fetch_tiles.py assets/map 8:-112.8,36.6,-101.6,42.8 12:-105.98,39.62,-104.80,40.12 14:-105.80,39.84,-105.58,39.97
python3 tools/natural_earth.py assets/map rp -127,23,-65,51
# capas USGS en assets/map/rp/ (ver data/map/ y tools/usgs.py); luego tools/grade.py, tools/rails.py, tools/profile.py
SCORE_SEED=71 python3 edit/score.py assets/score 68.0 142.7 147.0 117.9 137.2 131.2 117.4 124.7 197.5
python3 edit/audio.py out/mix.wav
python3 edit/render.py out/video_noaudio.mp4 --workers 4
bash tools/terminar.sh PID_RENDER Rollins_Pass 35145
```
