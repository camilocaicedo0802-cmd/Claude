# Diccionario de datos

Consulta: 27 de octubre de 2026. Todas las cifras son públicas o de vidIQ. Ninguna es una métrica privada (CTR, retención, ingresos).

## `videos.csv`

| Columna | Significado |
|---|---|
| `handle` | Canal (sin @) |
| `tab` | `long` (video) o `short` (Short) |
| `id`, `url` | Identificador y enlace del video |
| `title` | Título **original**. Los canales en español y vietnamita se descargaron con su idioma; YouTube muestra traducciones a otros públicos |
| `title_en` | Título traducido que YouTube muestra en inglés, solo en canales no angloparlantes |
| `date` | Fecha de publicación |
| `date_src` | `vidiq` o `yt-dlp` = exacta; `approx` = deducida de "hace X días/meses" (±1 mes en lo reciente, varios meses en videos de más de un año); vacío = sin fecha |
| `age_days` | Días desde la publicación hasta el 27-oct-2026 |
| `duration` | Segundos |
| `views` | Vistas a la fecha de consulta |
| `views_src` | `vidiq`/`yt-dlp` = exactas; `rounded` = de la lista pública, redondeadas (±15 % en 296 videos verificados). Un 0 con `rounded` significa dato ausente |
| `likes`, `comments` | Solo con datos exactos |
| `like_rate` | Likes ÷ vistas × 100 |
| `comment_rate` | Comentarios por cada 1.000 vistas |
| `chapters` | Número de capítulos (solo con datos de yt-dlp) |
| `neigh_median` | Mediana de vistas de los 10 videos publicados alrededor (5 antes y 5 después), en el mismo formato |
| `multiple` | `views ÷ neigh_median`. Es el indicador principal de rendimiento relativo |
| `chan_median` | Mediana de vistas de todo el canal en ese formato |
| `views_per_day` | `views ÷ age_days`. Sirve para comparar videos recientes; favorece a los muy recientes que aún están en su pico |
| `thumb` | Enlace a la miniatura pública |
| `desc_first_line` | Primera línea de la descripción |

## `canales.csv`

Una fila por canal. Columnas no obvias:

- `video_mas_antiguo_con_fecha_exacta`: el video más antiguo **entre los que tienen fecha exacta**. No siempre es el primer video del canal.
- `subidas_por_semana_90d`: publicaciones (videos y Shorts) de los últimos 90 días ÷ 12,86 semanas. En Squire Explains, que tiene 4 semanas de vida, el ritmo real es de ~9 por semana.
- `pct_vistas_top10pct_videos`: porcentaje de todas las vistas que suma el 10 % de videos con más vistas. Mide cuánto depende el canal de unos pocos éxitos.
- `pistas_audio_doblaje`: número de pistas de audio en los videos revisados. Es una muestra, no todos los videos.
- `fecha_1k_subs`, `fecha_10k_subs`: primer día del historial de vidIQ con al menos ese número de suscriptores.

Las medianas excluyen los videos con 0 vistas por dato ausente.

## `hitos_crecimiento.csv`

Hitos extraídos del historial diario de vidIQ. La columna `video_asociado` relaciona un salto de crecimiento con los videos publicados justo antes. **Esa relación es una hipótesis por coincidencia de fechas, no una causa demostrada.**

## `crudos-2026-10-27.tar.gz`

- `flatdate/`: listas de yt-dlp con fechas aproximadas.
- `flatorig/`: listas con títulos en idioma original (Te Lo Pinto Fácil, Estrictamente, Lịch Sử Ngoại Truyện).
- `full/`: metadatos por video de yt-dlp (incluye capítulos y pistas de audio).
- `vidiq/`: respuestas de `vidiq_get_videos_by_ids` y el historial diario de Te Lo Pinto Fácil.

Los historiales diarios de los demás canales se consultaron, pero solo se guardaron sus hitos.
