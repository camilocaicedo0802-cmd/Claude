# Church Hill — el tren enterrado de Richmond

Documental de 18:39 para YouTube, en español, sobre el túnel de Church Hill en Richmond, Virginia: la obra de
1872–1873 en arcilla azul bajo el barrio de St. John's, el hundimiento de enero de 1873, el abandono en 1902, el
derrumbe del 2 de octubre de 1925 que dejó dentro la locomotora 231, diez vagones y al menos dos jornaleros, el
veredicto del jurado, el sellado con arena en 1926 y los intentos fallidos de sacar el tren.

El montaje está hecho por código: `edit/timeline.py` define los 264 planos anclados a las palabras de la locución
(`data/words.json`), y el motor (`edit/engine.py`, `gfx*.py`, `maps.py`, `render.py`) compone cada fotograma a
1920×1080 y 30 fps. No hay medios en el repositorio: solo código y datos ligeros.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `edit/` | Motor, `timeline.py` del episodio y `gfx8.py`, con los diagramas de este episodio: la colina en corte (obra, hundimiento de 1873, derrumbe de 1925, rescate, sellado y estado actual), la plastilina, la huida a oscuras, el ataúd, la lista de la compañía, el veredicto y las razones del sellado. También `maps.py` con los mapas `rc_*` (calles reales de Church Hill y la ruta del carbón), `audio.py` con los efectos de este episodio y `score.py` (banda sonora original, `SCORE_SEED=25`). |
| `tools/` | Búsqueda y descarga (Unsplash, Library of Congress con conversión de TIFF de 16 bits, Flickr, Wikimedia, Mixkit con comprobación de licencia), créditos y entrega. |
| `data/` | Transcripción, guion, material usado, mapa de música y créditos de lo usado (`credits_used.json`). |
| `entrega/` | Descripción de YouTube y créditos completos. |

## Material y licencias

- Fotos: Flickr con CC BY 2.0 o "sin restricciones conocidas" (VCU Libraries, Library of Virginia); Library of
  Congress (1865, St. John's Church, litografía de 1876, HABS/HAER, FSA). Se descartaron cuatro imágenes de la
  LoC: dos con el aviso "Publication may be restricted" y dos sin fecha ni derechos evaluados.
- Video: 18 clips de Mixkit, todos con la *Stock Video Free License*.
- Las fotos de dominio público del rescate de 1925 en Wikimedia Commons no se pudieron descargar (límite de
  peticiones del servidor). Si se consiguen, `timeline.py` las usa automáticamente con `pick("w_00.jpg", …)`.
- Música: banda sonora original sintetizada.
- Mapas: relieve Mapzen/Tilezen; calles, vías y río del USGS; Natural Earth.

## Regenerar

```bash
python3 tools/fetch_tiles.py assets/map 9:-82.8,36.5,-75.8,39.2 16:-77.4400,37.5180,-77.4000,37.5440
python3 tools/natural_earth.py assets/map rc -83,36.4,-75.6,39.4
SCORE_SEED=25 python3 edit/score.py assets/score 65.3 135.7 132.8 126.0 164.8 131.9 122.0 138.3 113.3
python3 edit/audio.py out/mix.wav
python3 edit/render.py out/video_noaudio.mp4 --workers 4
bash tools/terminar.sh PID_RENDER Church_Hill_Richmond 33567 50.4 52.2 79.9 87.7 621.8 624.6
```
