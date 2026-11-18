# Ridge Route — la carretera que nadie usa

Documental de 18:52 para YouTube, en español, sobre la Ridge Route de California: el muro de montañas entre Los Ángeles
y el valle de San Joaquín, Fort Tejon y sus camellos, el préstamo de 1910, la crecida de 1914 que llevó la carretera a
las crestas, las 697 curvas, el control de velocidad por tarjeta, los radiadores y los frenos, las posadas de las
cumbres, Swede's Cut, la carretera del cañón de 1933 (US 99), los bonos que se pagaron hasta 1965, la Interstate 5 de
1970, la US 99 hundida bajo Pyramid Lake, el acueducto, Harrison Scott y la carretera de hoy.

El montaje está hecho por código: `edit/timeline.py` define los 229 planos anclados a las palabras de la locución
(`data/words.json`), y el motor (`edit/engine.py`, `gfx*.py`, `maps.py`, `render.py`) compone cada fotograma a
1920×1080 y 30 fps. No hay medios en el repositorio: solo código y datos ligeros.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor, `timeline.py` del episodio y `gfx13.py`, con los diagramas de este episodio: el volante de las 697 curvas, el corte de la montaña (la crecida de 1914, la carretera en la cresta, los cortes de la autopista), la carretera que rodea los cerros, la tarjeta de control de velocidad (recreación), el radiador que hierve y los frenos traseros, el perfil real con las posadas (`rr_profile.json`, relieve Mapzen), Swede's Cut, la deuda (18 años de uso, 50 de pagos), las tres carreteras en capas y la presa que hunde la US 99. `maps.py` añade los mapas `rr_*`; `rr_route.json` tiene la Ridge Route (USGS + camino 8N04 del Servicio Forestal), la I-5, la US 99 aproximada por el cañón del Piru y un acueducto esquemático. `audio.py` tiene los efectos de este episodio y `score.py` la banda sonora original (`SCORE_SEED=83`). |
| `tools/` | Búsqueda y descarga (Unsplash, Library of Congress, Flickr, Wikimedia, Mixkit con `mk.py` y `mklic.py`), créditos y entrega; `usgs.py`, `rr_grade.py` (trazado), `rr_profile.py` (perfil). |
| `data/` | Transcripción, guion, material usado, mapa de música y capas del mapa (`map/`: carreteras de The National Map, caminos del Servicio Forestal, ríos y lagos del NHD; coordenadas redondeadas a 5 decimales). |
| `entrega/` | Descripción de YouTube y créditos completos. |

## Material y licencias

- Fotos: Flickr con marca de dominio público (Shutter Theory: Swede's Cut; Mjr Kool: US 99 en 1939), CC0 (The Fun
  Chronicles) o CC BY 2.0 (Craig Howell, Curtis Palmer, Terry Whalebone, Don O'Brien, Clotee Allochuku-Albritton,
  Damian Gadal, Jon Evans); Library of Congress (sin restricciones conocidas; se descartaron una postal de la Ridge Route
  y dos fotos de Los Ángeles con derechos "no evaluados" o sin indicar); Freepik vía Magnific (licencia gratuita con
  atribución; la cuenta gratuita permitió 10 descargas al día); Unsplash.
- Se quitaron seis fotos de Flickr etiquetadas "Ridge Route" que en realidad eran de Arizona y del Gran Cañón.
- Wikimedia Commons limitó las descargas (HTTP 429) toda la sesión: no se usó nada de allí.
- Video: clips de Mixkit, todos con la *Stock Video Free License*.
- Música: banda sonora original sintetizada.

## Regenerar

```bash
python3 tools/fetch_tiles.py assets/map 8:-121.6,33.4,-116.4,36.6 11:-119.2,34.25,-118.3,35.15 13:-118.95,34.45,-118.55,34.95
python3 tools/natural_earth.py assets/map rr -127,23,-65,51
# capas USGS / USFS en assets/map/rr/ (ver data/map/ y tools/usgs.py); luego tools/rr_grade.py y tools/rr_profile.py
SCORE_SEED=83 python3 edit/score.py assets/score 74.2 128.6 123.0 130.0 118.2 134.3 113.1 144.0 166.3
python3 edit/audio.py out/mix.wav
python3 edit/render.py out/video_noaudio.mp4 --workers 4
bash tools/terminar.sh PID_RENDER Ridge_Route 33951
```
