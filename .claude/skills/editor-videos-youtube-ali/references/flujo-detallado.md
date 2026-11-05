# Flujo detallado, fase por fase

Comandos tal como se usaron en los episodios de este chat. `P` es la carpeta del proyecto y `PY` el Python
del entorno virtual (`venv/bin/python`). Todo lo largo va en segundo plano con
`setsid nohup … > log 2>&1 < /dev/null &` para que sobreviva si se corta la conversación.

## Índice
1. Preparar el proyecto
2. Transcribir y cotejar con el guion
3. Buscar y descargar material
4. Hojas de contacto y selección
5. Mapas base
6. Diagramas del episodio
7. Escribir y revisar `timeline.py`
8. Audio
9. Render
10. Mezcla final, partes y archivo optimizado
11. Guardar en el repositorio
12. Disco y procesos

## 1. Preparar el proyecto

```bash
python3 -m venv venv && venv/bin/pip install numpy scipy pillow opencv-python-headless faster-whisper
bash SKILL/scripts/herramientas/nuevo_proyecto.sh $P voz.mp3 guion.pdf
```
- La locución llega como `*.mp3.mpeg`: se copia tal cual como `work/voz.mp3`.
- `work/guion.txt` sale de `pdftotext -layout`. Léelo entero: de ahí salen los capítulos, los nombres
  propios para la transcripción y la lista de imágenes que hacen falta.
- Ajusta `TOTAL` (duración de la locución) en `edit/timeline.py`, `edit/audio.py`, y el valor por
  defecto de `--total` en `render.py`, `mids.py`, `sel.py` y `check.py`.

## 2. Transcribir y cotejar

```bash
echo "Atlantic Avenue, Brooklyn, Long Island Rail Road, Walt Whitman, Bob Diamond, …" > work/nombres.txt
setsid nohup $PY tools/transcribe.py work/voz.mp3 work/words_raw.json medium work/nombres.txt > work/transcribe.log 2>&1 &
# ≈16–20 min con el modelo medium en 4 núcleos; "small" tarda la mitad y basta si va justo de tiempo
cp work/words_raw.json work/words.json
```
- Lista los segmentos con su tiempo (`start`, `text`) y compáralos con el guion: así salen los tiempos de
  cada capítulo y se detectan frases que la locución dice distinto. En Laurel Hill la locución decía una
  frase que no estaba en el guion: se cubrió en pantalla y se avisó a Ali.
- Los números grandes se transcriben partidos ("2.300" → "2", ".300"): ancla con la primera palabra.
- Si una zona sale mal transcrita, se puede retranscribir y guardar en `work/retx.json`
  (`{"t0-t1": [{"w":…,"s":…,"e":…}]}`); `words.py` reemplaza solo ese tramo.

## 3. Buscar y descargar material

En paralelo, mientras corre la transcripción:

- **Unsplash** (MCP de Unsplash): lanza un subagente con la lista de consultas (40–50, unas 6 fotos por
  consulta, horizontales, sin Unsplash+ ni logos). Escribe lotes TSV
  `id<TAB>url_raw<TAB>consulta<TAB>autor<TAB>usuario<TAB>alt` y los pasa por
  `$PY tools/udl.py $P < lote.tsv`, que descarga a `assets/img/u_<id>.jpg` y registra en `work/unsplash.json`.
- **Library of Congress:** `$PY tools/loc.py search work/loc.json "consulta 1" "consulta 2" …` (lento: deja
  que termine) y `$PY tools/loc.py get work/loc.json assets/img id1 id2 …` → `assets/img/l_<id>.jpg`.
- **Flickr (solo licencias libres):** `$PY tools/fl.py search work/flickr.json "consulta" …` y
  `FL_SLEEP=10 $PY tools/fl.py get work/flickr.json assets/img id1 id2 …` → `f_<id>.jpg`.
- **Wikimedia Commons:** `$PY -I tools/wm.py search "consulta"`; filtra por licencia (acepta PD, CC0,
  CC BY; descarta CC BY-SA, que es la mayoría).
- **Internet Archive (películas):** `$PY tools/ia.py assets/vid work/films.json identificador …` y
  `bash tools/scenes.sh $P nombre` para los cortes de escena. Úsalo poco o nada (ver licencias).
- **Datos abiertos para mapas de ciudad:** NYC Open Data por la API de Socrata, p. ej. calles
  `https://data.cityofnewyork.us/resource/inkn-q76z.geojson` con `$where=within_box(the_geom, lat_n, lon_w, lat_s, lon_e)`,
  `$limit=50000`, y límites de distritos `gthc-hcne` (costa) y `wh2p-dxnf` (con agua).

## 4. Hojas de contacto y selección

```bash
$PY -I tools/usq.py $P todo                       # Unsplash agrupado por consulta → work/sheets/us_*.jpg
$PY -I tools/locq.py $P a "consulta 1" "consulta 2"  # LoC por consultas → work/sheets/lq_a_*.jpg
$PY -I tools/flsheet.py $P "consulta 1" …         # Flickr con licencia y tamaño
$PY tools/filmsheet.py $P nombre 40               # fotogramas de una película
```
- Mira las hojas (son imágenes) y apunta los ids. Los ids de Unsplash se leen mal (I/l/1, O/0):
  `timeline.res()` los corrige buscando el archivo parecido en disco.
- Las estereografías (`l_1s…`) traen dos fotos y el cartón: `$PY tools/stereo_crop.py assets/img`
  crea `l_<id>_L.jpg` con solo la foto izquierda.
- Para cada imagen elegida, comprueba que lo que muestra es lo que dice la voz en ese momento.

## 5. Mapas base

```bash
$PY tools/natural_earth.py assets/map dp -125,32,-110,45   # capas Natural Earth + carreteras de la zona → roads_dp.geojson
$PY tools/fetch_tiles.py assets/map 10:-74.9,40.3,-70.5,42.85 12:-74.10,40.60,-73.82,40.80 15:-74.008,40.676,-73.970,40.700
```
- Las capas de Natural Earth (estados, lagos, ríos, costa, carreteras) se bajan una vez y sirven para todos
  los episodios. El archivo de carreteras se elige por el prefijo del nombre del mapa: si creas un prefijo
  nuevo, añádelo en `BaseMap._draw_vectors` y en la capa `road` de `MapScene` (`maps.py`).
- En `edit/maps.py` añade las coordenadas a `COORDS` y un caso en `basemap(nombre)`:
  `BaseMap(nombre, zoom, (lon0, lat0, lon1, lat1), exageración, elev_min, elev_max, lat_centro, tz=zoom_teselas)`.
  Con `tz` menor que `zoom` se reutilizan teselas gruesas reescaladas (ciudades planas).
- El mapa base se cachea en `assets/map/base_<nombre>.png`: bórralo si cambias el estilo.
- Ancho mínimo útil: el mapa base debe medir más que 1920×1080 al zoom de cámara usado (la cámara de
  `MapScene` se mantiene dentro del mapa para los mapas `aa_`; aplica el mismo recorte a mapas nuevos).
- Vista previa: `cd edit && $PY sel.py ../work/maps.jpg maps 0.85`.

## 6. Diagramas del episodio

Crea `edit/gfxN.py` con funciones `f(t, dur, **kw) -> imagen RGB 1920×1080` (fondo `background("dark_grid", t)`,
`label()`, `fill_poly()`, `aa_poly()`, `partial_line()`) y úsalas con `cus(f, …)` o
`warp(f, t_inicio, velocidad, …)` para mostrar solo una fase de la animación. Prueba cada diagrama con
fotogramas sueltos en una hoja antes de meterlo en la línea de tiempo (ver `montaje-y-retencion.md`).

## 7. `timeline.py`

- Parte del `timeline.py` de ejemplo (Atlantic Avenue): copia los helpers y reescribe `build()`.
- Valida y revisa:
```bash
cd edit
$PY check.py            # planos, anclas perdidas ([anchor] … not found), archivos faltantes
$PY mids.py ../work/mids  # un fotograma por plano, hojas de 48 → work/mids/mid_*.jpg (≈1,5 min)
$PY sel.py ../work/x.jpg 385,520,756 0.5   # planos concretos (tiempos) en el punto 0.5 de su duración
```
- Corrige todo lo que se vea mal antes de renderizar: un render cuesta una hora.

## 8. Audio

```bash
$PY edit/score.py assets/score L1 L2 … L9       # solo si no hay pistas de YouTube Studio
# work/music.json: [[inicio, fin, "score/cue_1.wav" o "yt/pista.mp3", desplazamiento, ganancia_dB], …]
$PY edit/audio.py out/mix.wav                    # ≈2 min; escribe también out/mix_music.wav y out/mix_sfx.wav
for f in out/mix.wav out/mix_music.wav out/mix_sfx.wav; do ffmpeg -nostats -i $f -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1; done
```
Ganancia de cada pista: `-27.5 - LUFS_de_la_pista` (medida con ebur128). Detalle en `audio-y-musica.md`.

## 9. Render

```bash
setsid nohup $PY edit/render.py out/video_noaudio.mp4 --workers 4 > out/render.log 2>&1 < /dev/null &
pgrep -f "python edit/[r]ender.py" | head -1    # anota el PID principal
```
- ≈55–60 min para 19 min de video con 4 núcleos (más si otra codificación compite por la CPU; baja su
  prioridad con `renice -n 19` sobre todos sus hilos, `/proc/PID/task/*`).
- Los trozos van a `out/chunks/part_XX.mp4` y se unen al final.

## 10. Mezcla final, partes y archivo optimizado

```bash
setsid nohup bash tools/terminar.sh PID_RENDER Nombre_Episodio FOTOGRAMAS [T0 T1 …] > out/terminar.log 2>&1 < /dev/null &
until grep -q PARTS_DONE out/terminar.log; do sleep 60; done   # en segundo plano
```
- `FOTOGRAMAS = round(TOTAL * 30)`. `T0 T1` son tramos a re-renderizar con cambios hechos después de
  lanzar el render (p. ej. una foto que hubo que cambiar).
- `splice.py` codifica en trozos de 90 s (x264 CRF 20, tune grain, maxrate 10M) y normaliza el audio en
  dos pasadas a −14 LUFS, pico −1,5 dBTP. Tarda ≈25 min.
- `split4.py` corta en 4 partes reproducibles (sin recodificar) de ≈350 MiB.
- `encode_optimizado.sh` hace el archivo único H.264 de ≈350 MB en ≈30 min.

## 11. Repositorio

Copia a `video/<episodio>/`: `edit/*.py`, `tools/*`, `data/` (words.json, guion.txt, used.json, music.json,
films.json, scenes/, credits_used.json) y `entrega/` (descripción y créditos), más un README con qué hay,
licencias y cómo regenerar. Sin medios (`.gitignore`: assets/ work/ out/ venv/ chunks/ *.mp4 *.wav).
Commit con mensaje en inglés, push con `git push -u origin <rama>`.

## 12. Disco y procesos

- Un episodio ocupa ≈15 GB en su punto máximo (render de 4 GB + trozos de 4 GB + máster de 1,4 GB +
  partes de 1,4 GB). Antes de renderizar comprueba `df -h /` y libera: trozos del render tras unirlos,
  `out/splice/`, partes ya enviadas, películas descargadas de episodios ya entregados.
- `rm -rf $VAR/...` lo bloquea la comprobación de seguridad: usa rutas absolutas literales.
- Si el contenedor se reinicia, los procesos en segundo plano mueren: las codificaciones por trozos se
  relanzan y siguen donde iban; vuelve a poner las esperas.
